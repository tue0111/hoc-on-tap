# -*- coding: utf-8 -*-
"""Extract every learner-material source into the isolated learner-notes corpus."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval import courses as C
from retrieval.config import INVENTORY, SOURCE_OVERRIDES, SOURCE_ROOT, SYSTEM, THIN_CHARS_PER_PAGE
from retrieval.textutil import content_hash, fold, nfc, sha256_file
from scripts.phase2_extract import extract_pdf
from scripts.v3_extract_course import extract_docx, extract_text, parse_name

EXTRACT_VERSION = "3.0.0"
PARTITION_ID = "learner-notes"
PARTITION_FIELD = "learner_notes"


def load_source_rules() -> tuple[dict, set[str]]:
    doc = yaml.safe_load(SOURCE_OVERRIDES.read_text(encoding="utf-8")) or {}
    overrides = {row["source_id"]: row for row in doc.get("overrides") or [] if row.get("source_id")}
    return overrides, set(doc.get("tmp_artifacts_not_curriculum") or [])


def is_learner_source(rec: dict, overrides: dict) -> bool:
    override = overrides.get(rec["source_id"]) or {}
    if override.get("content_role") == "learner_material":
        return True
    rel = fold(rec.get("relative_path") or "")
    return "claude outputs" in rel or "nguyen duc tue" in rel or "nguyenductue" in rel.replace(" ", "")


def selected_records() -> list[dict]:
    from scripts.v3_inventory import active_records
    inventory = active_records(json.loads(Path(INVENTORY).read_text(encoding="utf-8")))
    overrides, tmp = load_source_rules()
    return [
        rec
        for rec in inventory
        if rec["source_id"] not in tmp
        and "/tmp/" not in rec["relative_path"].replace("\\", "/").lower()
        and is_learner_source(rec, overrides)
    ]


def verify_sources(records: list[dict]) -> list[dict]:
    checks = []
    for rec in records:
        path = SOURCE_ROOT / rec["relative_path"]
        exists = path.is_file()
        size = path.stat().st_size if exists else None
        digest = sha256_file(path) if exists else None
        checks.append(
            {
                "source_id": rec["source_id"],
                "relative_path": rec["relative_path"],
                "exists": exists,
                "size_ok": exists and size == rec.get("size_bytes"),
                "sha_ok": exists and digest == rec.get("sha256"),
            }
        )
    return checks


def extract_pptx(path: Path) -> dict:
    from pptx import Presentation

    try:
        deck = Presentation(str(path))
        pages = []
        for number, slide in enumerate(deck.slides, start=1):
            parts = []
            seen = set()
            title_shape = slide.shapes.title
            if title_shape is not None and title_shape.has_text_frame:
                title = nfc(title_shape.text).strip()
                if title:
                    parts.append(title)
                    seen.add(title)
            table_no = 0
            for shape in slide.shapes:
                if getattr(shape, "has_text_frame", False):
                    text = nfc(shape.text).strip()
                    if text and text not in seen:
                        parts.append(text)
                        seen.add(text)
                if getattr(shape, "has_table", False):
                    table_no += 1
                    rows = [" | ".join(nfc(cell.text).strip().replace("\n", " ") for cell in row.cells) for row in shape.table.rows]
                    table = f"[TABLE {table_no}]\n" + "\n".join(rows)
                    if table not in seen:
                        parts.append(table)
                        seen.add(table)
            text = nfc("\n".join(parts))
            pages.append({"page": number, "text": text, "char_count": len(text.strip())})
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": f"pptx: {exc}", "pages": [], "page_count": None, "char_count": 0, "outline": []}
    return {
        "ok": True,
        "pages": pages,
        "page_count": len(pages),
        "char_count": sum(page["char_count"] for page in pages),
        "outline": [],
    }


def extract_one(path: Path, extension: str) -> dict:
    if extension == ".pdf":
        return extract_pdf(path)
    if extension == ".docx":
        return extract_docx(path)
    if extension == ".pptx":
        return extract_pptx(path)
    if extension in {".txt", ".md"}:
        return extract_text(path)
    return {"ok": False, "error": f"unsupported learner extension {extension}", "pages": [], "page_count": None, "char_count": 0, "outline": []}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()

    records = selected_records()
    checks = verify_sources(records)
    bad = [row for row in checks if not (row["exists"] and row["size_ok"] and row["sha_ok"])]
    for row in checks:
        print(
            row["source_id"],
            f"exists={row['exists']}",
            f"size_ok={row['size_ok']}",
            f"sha_ok={row['sha_ok']}",
            row["relative_path"],
        )
    print("CHECK", f"count={len(checks)}", f"bad={len(bad)}")
    if not records or bad:
        raise SystemExit(1)
    if args.check_only:
        return

    docs = []
    pages_out = []
    for rec in records:
        source_id = rec["source_id"]
        relative_path = rec["relative_path"]
        path = SOURCE_ROOT / relative_path
        extension = (rec.get("extension") or path.suffix).lower()
        print("EXTRACT", source_id, relative_path, flush=True)
        extracted = extract_one(path, extension)
        page_count = extracted.get("page_count") or 0
        char_count = extracted.get("char_count") or 0
        chars_per_page = char_count / page_count if page_count else 0
        parse_quality = "error" if not extracted.get("ok") else ("thin" if chars_per_page < THIN_CHARS_PER_PAGE else "ok")
        parsed = parse_name(rec["filename"], rec)
        course = C.get_course(rec.get("course_id")) or {}
        full_text = "\n\n".join(f"----- PAGE {page['page']} -----\n{page['text']}" for page in extracted.get("pages") or [])
        document_id = f"doc-ln-{source_id}"
        doc = {
            "document_id": document_id,
            "source_id": source_id,
            "course_id": rec.get("course_id"),
            "course_name": course.get("name") or rec.get("course_folder"),
            "course_code": None,
            "course_codes": course.get("codes") or [],
            "partition": PARTITION_FIELD,
            "source_file": rec["filename"],
            "relative_path": relative_path,
            "source_type": rec.get("source_role") or "unknown",
            "content_role": "learner_material",
            "authority": 7,
            "chapter": parsed["chapter"],
            "section": None,
            "topic": parsed["topic"],
            "part": parsed["part"],
            "parse_rule": parsed["parse_rule"],
            "page_start": 1 if page_count else None,
            "page_end": page_count or None,
            "page_count": page_count,
            "text": full_text,
            "char_count": char_count,
            "chars_per_page": round(chars_per_page, 1),
            "parse_quality": parse_quality,
            "extract_ok": bool(extracted.get("ok")),
            "extract_error": extracted.get("error"),
            "synthetic_pages": bool(extracted.get("synthetic_pages")),
            "content_hash": content_hash(full_text),
            "source_sha256": rec["sha256"],
            "combined_duplicate": False,
            "learner_material": True,
            "index_include": bool(extracted.get("ok")) and char_count > 0,
            "dup_group": None,
            "outline": extracted.get("outline") or [],
            "provenance": {
                "extract_version": EXTRACT_VERSION,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "tool": "python-pptx" if extension == ".pptx" else ("pdfplumber+pypdf" if extension == ".pdf" else extension),
                "page_cap": None,
            },
        }
        docs.append(doc)
        for page in extracted.get("pages") or []:
            pages_out.append(
                {
                    "document_id": document_id,
                    "source_id": source_id,
                    "course_id": rec.get("course_id"),
                    "partition": PARTITION_FIELD,
                    "relative_path": relative_path,
                    "source_file": rec["filename"],
                    "source_type": doc["source_type"],
                    "content_role": "learner_material",
                    "authority": 7,
                    "chapter": parsed["chapter"],
                    "topic": parsed["topic"],
                    "page": page["page"],
                    "text": page["text"],
                    "char_count": page["char_count"],
                    "combined_duplicate": False,
                    "learner_material": True,
                    "index_include": doc["index_include"],
                    "parse_quality": "thin" if page["char_count"] < THIN_CHARS_PER_PAGE else parse_quality,
                }
            )

    normalized = SYSTEM / "data" / "normalized"
    normalized.mkdir(parents=True, exist_ok=True)
    documents_path = normalized / f"{PARTITION_ID}.documents.jsonl"
    pages_path = normalized / f"{PARTITION_ID}.pages.jsonl"
    with documents_path.open("w", encoding="utf-8") as handle:
        for doc in docs:
            handle.write(json.dumps(doc, ensure_ascii=False) + "\n")
    with pages_path.open("w", encoding="utf-8") as handle:
        for page in pages_out:
            handle.write(json.dumps(page, ensure_ascii=False) + "\n")

    from pypdf import PdfReader

    mismatches = []
    for doc in docs:
        source = SOURCE_ROOT / doc["relative_path"]
        if source.suffix.lower() == ".pdf" and doc["extract_ok"]:
            if len(PdfReader(str(source)).pages) != doc["page_count"]:
                mismatches.append(doc["source_id"])
    summary = {
        "extract_version": EXTRACT_VERSION,
        "partition": PARTITION_ID,
        "document_count": len(docs),
        "page_count": len(pages_out),
        "total_chars": sum(doc["char_count"] for doc in docs),
        "indexed_documents": sum(doc["index_include"] for doc in docs),
        "thin_documents": [doc["source_id"] for doc in docs if doc["parse_quality"] == "thin"],
        "errors": [doc["source_id"] for doc in docs if doc["parse_quality"] == "error"],
        "page_count_mismatch": mismatches,
        "source_ids": [doc["source_id"] for doc in docs],
        "coverage": "learner_material",
        "unknowns": ["not_curriculum_source"],
    }
    (normalized / f"{PARTITION_ID}.coverage.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        "DONE",
        "docs", len(docs),
        "pages", len(pages_out),
        "chars", summary["total_chars"],
        "errors", summary["errors"],
        "mismatch", mismatches,
        "thin", summary["thin_documents"],
        flush=True,
    )
    if summary["errors"] or mismatches:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
