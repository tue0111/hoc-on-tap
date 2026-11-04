# -*- coding: utf-8 -*-
"""Full-text extract NLKT + KTTC1. Read-only on D:\\Hoc sources. No page cap."""
from __future__ import annotations
import json
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pdfplumber
from pypdf import PdfReader

from retrieval.config import (
    COMBINED_SOURCE_IDS,
    EXTRACT_VERSION,
    INVENTORY,
    NORMALIZED,
    SLICE_COURSE_IDS,
    SOURCE_OVERRIDES,
    SOURCE_ROOT,
    SYSTEM,
    AUTHORITY_BY_ROLE,
    CONTENT_ROLE_AUTHORITY,
    COURSE_CODES,
    COURSE_NAMES,
    THIN_CHARS_PER_PAGE,
)
from retrieval.textutil import content_hash, nfc, sha256_file

try:
    import yaml
except ImportError:
    yaml = None


CHAPTER_FN_RE = re.compile(r"(?i)(?:chương|chuong)\s*(\d+)")
NLKT_CH_RE = re.compile(r"(?i)NLKT-C(\d+)")
TOPIC_RE = re.compile(r"(?i)(?:CD|chủ đề|chude)[.\s]*(\d+(?:\.\d+)?)")


def load_overrides() -> dict:
    out = {}
    p = SOURCE_OVERRIDES
    if not p.exists() or yaml is None:
        return out
    doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    for item in doc.get("overrides") or []:
        sid = item.get("source_id")
        if sid:
            out[sid] = item
    return out


def flatten_outline(items, acc=None, depth=0, reader=None):
    if acc is None:
        acc = []
    if not items:
        return acc
    for item in items:
        if isinstance(item, list):
            flatten_outline(item, acc, depth + 1, reader)
        else:
            title = getattr(item, "title", None) or str(item)
            page = None
            if reader is not None:
                try:
                    page = reader.get_destination_page_number(item)
                    if page is not None:
                        page = int(page) + 1
                except Exception:
                    page = None
            acc.append({"depth": depth, "title": nfc(title), "page": page})
    return acc


def chapter_from_filename(name: str) -> int | None:
    m = CHAPTER_FN_RE.search(name)
    if m:
        return int(m.group(1))
    m = NLKT_CH_RE.search(name)
    if m:
        return int(m.group(1))
    if re.search(r"(?i)gioi\s*thieu|chương\s*0|chuong\s*0|-c0-", name):
        return 0
    return None


def topic_from_filename(name: str) -> str | None:
    m = TOPIC_RE.search(name)
    return m.group(1) if m else None


def extract_pdf(path: Path) -> dict:
    result = {
        "ok": False,
        "page_count": None,
        "pages": [],
        "outline": [],
        "error": None,
        "char_count": 0,
    }
    try:
        reader = PdfReader(str(path))
        result["page_count"] = len(reader.pages)
        try:
            result["outline"] = flatten_outline(reader.outline, reader=reader)
        except Exception as e:
            result["outline_error"] = str(e)
    except Exception as e:
        result["error"] = f"pypdf: {e}"

    pages = []
    try:
        with pdfplumber.open(str(path)) as doc:
            if result["page_count"] is None:
                result["page_count"] = len(doc.pages)
            for i, pg in enumerate(doc.pages):
                t = pg.extract_text() or ""
                t = nfc(t)
                pages.append({"page": i + 1, "text": t, "char_count": len(t.strip())})
        result["pages"] = pages
        result["char_count"] = sum(p["char_count"] for p in pages)
        result["ok"] = True
    except Exception as e:
        result["error"] = (result.get("error") or "") + f" | pdfplumber: {e}"
        result["traceback"] = traceback.format_exc()
    return result


def main():
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    inv = json.loads(Path(INVENTORY).read_text(encoding="utf-8"))
    overrides = load_overrides()
    records = [r for r in inv if r.get("course_id") in SLICE_COURSE_IDS]
    docs = []
    pages_out = []
    coverage = []

    for rec in records:
        rel = rec["relative_path"]
        path = SOURCE_ROOT / rel
        sid = rec["source_id"]
        ov = overrides.get(sid) or {}
        role = ov.get("content_role") or rec.get("source_role") or "unknown"
        if role in CONTENT_ROLE_AUTHORITY:
            authority = CONTENT_ROLE_AUTHORITY[role]
        else:
            authority = AUTHORITY_BY_ROLE.get(rec.get("source_role") or "unknown", 8)
        combined = sid in COMBINED_SOURCE_IDS or "combined" in str(role)
        print(f"EXTRACT {sid} {rel}", flush=True)
        ext = rec.get("extension") or path.suffix.lower()
        extracted = None
        if ext == ".pdf":
            extracted = extract_pdf(path)
        else:
            extracted = {"ok": False, "error": f"no extractor for {ext}", "pages": [], "page_count": None, "char_count": 0, "outline": []}

        page_count = extracted.get("page_count") or 0
        char_count = extracted.get("char_count") or 0
        cpp = (char_count / page_count) if page_count else 0
        thin = cpp < THIN_CHARS_PER_PAGE
        parse_quality = "ok"
        if not extracted.get("ok"):
            parse_quality = "error"
        elif thin:
            parse_quality = "thin"
        elif char_count == 0:
            parse_quality = "empty"

        chapter = rec.get("apparent_chapter")
        if chapter is None:
            chapter = chapter_from_filename(rec["filename"])
        topic = rec.get("apparent_topic_code") or topic_from_filename(rec["filename"])
        file_hash = rec.get("sha256") or sha256_file(path)
        full_text = "\n\n".join(
            f"----- PAGE {p['page']} -----\n{p['text']}" for p in extracted.get("pages") or []
        )
        doc = {
            "document_id": f"doc-{sid}",
            "source_id": sid,
            "course_id": rec["course_id"],
            "course_name": COURSE_NAMES[rec["course_id"]],
            "course_code": COURSE_CODES[rec["course_id"]],
            "source_file": rec["filename"],
            "relative_path": rel.replace("\\", "/"),
            "source_type": rec.get("source_role") or "unknown",
            "content_role": role,
            "authority": authority,
            "chapter": chapter,
            "section": None,
            "topic": topic,
            "page_start": 1 if page_count else None,
            "page_end": page_count or None,
            "page_count": page_count,
            "text": full_text,
            "char_count": char_count,
            "chars_per_page": round(cpp, 1),
            "parse_quality": parse_quality,
            "text_coverage": "thin" if thin else ("full" if extracted.get("ok") else "none"),
            "extract_ok": bool(extracted.get("ok")),
            "extract_error": extracted.get("error"),
            "content_hash": content_hash(full_text),
            "source_sha256": file_hash,
            "combined_duplicate": combined,
            "index_include": (not combined) and bool(extracted.get("ok")) and char_count > 0,
            "outline": extracted.get("outline") or [],
            "provenance": {
                "extract_version": EXTRACT_VERSION,
                "extracted_at": datetime.now(timezone.utc).isoformat(),
                "tool": "pdfplumber+pypdf",
                "page_cap": None,
            },
        }
        docs.append(doc)
        for p in extracted.get("pages") or []:
            pages_out.append(
                {
                    "document_id": doc["document_id"],
                    "source_id": sid,
                    "course_id": rec["course_id"],
                    "relative_path": doc["relative_path"],
                    "source_file": rec["filename"],
                    "source_type": doc["source_type"],
                    "authority": authority,
                    "chapter": chapter,
                    "topic": topic,
                    "page": p["page"],
                    "text": p["text"],
                    "char_count": p["char_count"],
                    "combined_duplicate": combined,
                    "index_include": doc["index_include"],
                    "parse_quality": "thin" if p["char_count"] < THIN_CHARS_PER_PAGE else parse_quality,
                }
            )
        coverage.append(
            {
                "source_id": sid,
                "relative_path": rel,
                "course_id": rec["course_id"],
                "page_count": page_count,
                "char_count": char_count,
                "chars_per_page": round(cpp, 1),
                "parse_quality": parse_quality,
                "phase0_extract_chars": rec.get("extract_char_count"),
                "page_cap_removed": True,
                "index_include": doc["index_include"],
                "combined_duplicate": combined,
            }
        )

    docs_path = NORMALIZED / "nlkt_kttc1.documents.jsonl"
    pages_path = NORMALIZED / "nlkt_kttc1.pages.jsonl"
    cov_path = NORMALIZED / "nlkt_kttc1.coverage.json"
    with docs_path.open("w", encoding="utf-8") as f:
        for d in docs:
            slim = {k: v for k, v in d.items() if k != "text"}
            slim["text"] = d["text"]
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    with pages_path.open("w", encoding="utf-8") as f:
        for p in pages_out:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    summary = {
        "extract_version": EXTRACT_VERSION,
        "courses": list(SLICE_COURSE_IDS),
        "document_count": len(docs),
        "page_count": len(pages_out),
        "total_chars": sum(d["char_count"] for d in docs),
        "indexed_documents": sum(1 for d in docs if d["index_include"]),
        "thin_documents": [d["source_id"] for d in docs if d["parse_quality"] == "thin"],
        "errors": [d["source_id"] for d in docs if d["parse_quality"] == "error"],
        "combined_excluded_from_index": list(COMBINED_SOURCE_IDS),
        "coverage": coverage,
    }
    cov_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE docs", len(docs), "pages", len(pages_out), "chars", summary["total_chars"], flush=True)


if __name__ == "__main__":
    main()
