# -*- coding: utf-8 -*-
"""Phase 0–1: inventory + conservative text extraction. Read-only on D:\\Hoc sources."""
from __future__ import annotations

import hashlib
import json
import re
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
from pypdf import PdfReader
from docx import Document as DocxDocument

ROOT = Path(r"D:\Hoc")
OUT = ROOT / "_learning_system"
INV = OUT / "inventory"
EXT = OUT / "extracts"
SKIP_ROOT_NAME = "_learning_system"

COURSE_IDS = {
    "Kinh doanh và nghiệp vụ": "kinh-doanh-va-nghiep-vu",
    "Kiểm toán 1": "kiem-toan-1",
    "Kế toán chi phí": "ke-toan-chi-phi",
    "Kế toán ngân hàng": "ke-toan-ngan-hang",
    "Kế toán tài chính 1": "ke-toan-tai-chinh-1",
    "Kế toán tài chính 2": "ke-toan-tai-chinh-2",
    "Luật kinh doanh": "luat-kinh-doanh",
    "Nguyên lý kế toán": "nguyen-ly-ke-toan",
    "Ngân hàng thương mại": "ngan-hang-thuong-mai",
    "Thị trường tài chính": "thi-truong-tai-chinh",
    "Tài chính doanh nghiệp 1": "tai-chinh-doanh-nghiep-1",
    "Tài chính hành chính sự nghiệp": "tai-chinh-hanh-chinh-su-nghiep",
}

ARTIFACT_PATH_RE = re.compile(
    r"(^|/)(tmp|pdfs|render|final_render|redo_docx_proxy|render_proxy)(/|$)",
    re.I,
)
YEAR_RE = re.compile(r"\b((?:19|20)\d{2})\b")
COURSE_CODE_RE = re.compile(r"\b([A-Z]{3,5}\d{4})\b")
CHAPTER_RE = re.compile(
    r"(?i)(?:chương|chuong)\s*(\d+)|(?:^|[_\-\s])c(\d+)(?:[_\-\s.]|$)|"
    r"(?:cd|chude|chủ đề)\s*(\d+(?:\.\d+)?)"
)


def rel_posix(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(rel: str, name: str, ext: str) -> dict:
    n = name.lower()
    r = rel.lower()
    notes = []

    if ARTIFACT_PATH_RE.search(rel.replace("\\", "/")) or re.search(
        r"preview|proxy", n
    ):
        return {
            "source_role": "unknown",
            "confidence": "low",
            "reason": "path/name matches generated render/tmp/proxy artifact",
            "evidence_status": "OBSERVED",
        }

    if ext in {".xlsx", ".xls", ".xlsm", ".csv"}:
        return {
            "source_role": "spreadsheet",
            "confidence": "high",
            "reason": "spreadsheet extension",
            "evidence_status": "OBSERVED",
        }

    # Combined exam+solution
    if re.search(r"dapan|đáp án|dap an|lời giải|loi giai", n) and re.search(
        r"dethi|đề thi|de thi|exam", n
    ):
        return {
            "source_role": "exam",
            "confidence": "medium",
            "reason": "filename contains both exam and answer tokens; primary role=exam, also contains solutions",
            "evidence_status": "OBSERVED",
        }

    if re.search(r"dapan|đáp án|dap an|lời giải|loi giai", n):
        return {
            "source_role": "solution",
            "confidence": "medium",
            "reason": "filename contains answer/solution token",
            "evidence_status": "OBSERVED",
        }

    if re.search(r"dethi|đề thi|de thi|\bexam\b", n):
        return {
            "source_role": "exam",
            "confidence": "medium",
            "reason": "filename contains exam token",
            "evidence_status": "OBSERVED",
        }

    if re.search(r"quiz|trắc nghiệm|trac nghiem", n):
        return {
            "source_role": "quiz",
            "confidence": "medium",
            "reason": "filename contains quiz token",
            "evidence_status": "OBSERVED",
        }

    if re.search(r"thảo luận|thao luan|bài tập lớn|bai tap lon|\bbtl\b|assignment", r):
        return {
            "source_role": "assignment",
            "confidence": "medium",
            "reason": "path/filename contains assignment/discussion token",
            "evidence_status": "OBSERVED",
        }

    if re.search(r"bài tập|bai tap|\bexercise\b", n):
        return {
            "source_role": "exercise",
            "confidence": "medium",
            "reason": "filename contains exercise token",
            "evidence_status": "OBSERVED",
        }

    if re.search(
        r"syllabus|đề cương|de cuong|giới thiệu môn|gioi thieu mon|"
        r"gioithieumonhoc|script giới thiệu|script gioi thieu",
        n,
    ):
        return {
            "source_role": "syllabus",
            "confidence": "medium",
            "reason": "filename contains course-intro/syllabus token",
            "evidence_status": "OBSERVED",
        }

    if re.search(r"hướng dẫn học tập|huong dan hoc tap|huongdanhoc", n):
        return {
            "source_role": "syllabus",
            "confidence": "medium",
            "reason": "filename is a course study-guide / learning-instruction document",
            "evidence_status": "OBSERVED",
        }

    if n.startswith("slide ") or n.startswith("slide") and "chương" in n or n.startswith("slide chương") or n.startswith("slide chuong"):
        return {
            "source_role": "lecture_slide",
            "confidence": "medium",
            "reason": "filename starts with Slide + chapter/course token",
            "evidence_status": "OBSERVED",
        }

    if n.lower().startswith("slide"):
        return {
            "source_role": "lecture_slide",
            "confidence": "medium",
            "reason": "filename starts with Slide",
            "evidence_status": "OBSERVED",
        }

    if ext == ".pptx":
        return {
            "source_role": "lecture_slide",
            "confidence": "low",
            "reason": "pptx extension only; content role not confirmed",
            "evidence_status": "INFERRED",
        }

    if re.search(r"sổ tay|so tay|so_tay", n):
        return {
            "source_role": "summary",
            "confidence": "low",
            "reason": "handbook/sổ tay token; could be exam summary or reference",
            "evidence_status": "INFERRED",
        }

    if re.search(r"ôn tập|on tap|ontap|hướng dẫn ôn|huong dan on|tài liệu hướng dẫn|tailieuhuongdan", n):
        return {
            "source_role": "summary",
            "confidence": "medium",
            "reason": "filename contains review/ôn tập token",
            "evidence_status": "OBSERVED",
        }

    if re.search(r"bảng hệ thống tài khoản|he thong tai khoan|chart of accounts", n):
        return {
            "source_role": "reference",
            "confidence": "medium",
            "reason": "filename is an account-system table / chart of accounts",
            "evidence_status": "OBSERVED",
        }

    # Chapter-topic lecture units (NLKT-C1-CD1.1, LKD-C2-CD.2.1, KDNV-C3-...)
    if re.search(r"(?i)(nlkt|lkd|kdnv|kdvnv)-c\d+", n):
        return {
            "source_role": "lecture_note",
            "confidence": "medium",
            "reason": "filename matches course-chapter-topic lecture-unit pattern",
            "evidence_status": "OBSERVED",
        }

    if re.match(r"(?i)^chương\s*\d+", n) or re.match(r"(?i)^chuong\s*\d+", n):
        return {
            "source_role": "lecture_note",
            "confidence": "low",
            "reason": "filename is 'Chương N' only; could be notes, slides-export, or textbook chapter",
            "evidence_status": "INFERRED",
        }

    # Large combined document named after the course folder
    return {
        "source_role": "unknown",
        "confidence": "low",
        "reason": "no reliable filename signal; needs content inspection",
        "evidence_status": "UNKNOWN",
        "notes": notes,
    }


def parse_chapter_topic(name: str) -> dict:
    out = {
        "chapter": None,
        "topic_code": None,
        "raw_match": None,
        "evidence_status": "UNKNOWN",
    }
    m = re.search(r"(?i)(?:chương|chuong)\s*(\d+)", name)
    if m:
        out["chapter"] = int(m.group(1))
        out["raw_match"] = m.group(0)
        out["evidence_status"] = "OBSERVED"
    m2 = re.search(r"(?i)(?:^|[_\-\s])c(\d+)(?:[_\-\s.]|$)", name)
    if out["chapter"] is None and m2:
        out["chapter"] = int(m2.group(1))
        out["raw_match"] = m2.group(0)
        out["evidence_status"] = "OBSERVED"
    m3 = re.search(r"(?i)(?:cd|chủ đề|chude)[.\s]*(\d+(?:\.\d+)?)", name)
    if m3:
        out["topic_code"] = m3.group(1)
        out["raw_match"] = (out["raw_match"] or "") + "|" + m3.group(0)
        out["evidence_status"] = "OBSERVED"
    return out


def flatten_outline(items, depth=0, acc=None):
    if acc is None:
        acc = []
    if not items:
        return acc
    for item in items:
        if isinstance(item, list):
            flatten_outline(item, depth + 1, acc)
        else:
            title = getattr(item, "title", None) or str(item)
            acc.append({"depth": depth, "title": title})
    return acc


def extract_pdf(path: Path, max_pages: int) -> dict:
    result = {
        "ok": False,
        "page_count": None,
        "pages_extracted": 0,
        "char_count": 0,
        "likely_scanned": None,
        "outline": [],
        "metadata": {},
        "text": "",
        "error": None,
    }
    try:
        reader = PdfReader(str(path))
        result["page_count"] = len(reader.pages)
        meta = reader.metadata
        if meta:
            result["metadata"] = {
                k: (str(v) if v is not None else None)
                for k, v in {
                    "title": meta.title,
                    "author": meta.author,
                    "subject": meta.subject,
                    "creator": meta.creator,
                    "producer": meta.producer,
                }.items()
            }
        try:
            result["outline"] = flatten_outline(reader.outline)
        except Exception as e:
            result["outline_error"] = str(e)
    except Exception as e:
        result["error"] = f"pypdf: {e}"

    texts = []
    try:
        with pdfplumber.open(str(path)) as doc:
            if result["page_count"] is None:
                result["page_count"] = len(doc.pages)
            n = min(len(doc.pages), max_pages)
            for i in range(n):
                t = doc.pages[i].extract_text() or ""
                texts.append(f"\n\n----- PAGE {i+1} -----\n{t}")
            result["pages_extracted"] = n
        result["text"] = "".join(texts).strip()
        result["char_count"] = len(result["text"])
        extracted_any = bool(re.sub(r"[\s\-]+", "", result["text"]))
        result["likely_scanned"] = (not extracted_any) and (result["page_count"] or 0) > 0
        result["ok"] = True
    except Exception as e:
        result["error"] = (result["error"] + " | " if result["error"] else "") + f"pdfplumber: {e}"
        result["traceback"] = traceback.format_exc()
    return result


def extract_docx(path: Path) -> dict:
    result = {
        "ok": False,
        "page_count": None,
        "paragraphs": 0,
        "char_count": 0,
        "likely_scanned": False,
        "outline": [],
        "metadata": {},
        "text": "",
        "error": None,
    }
    try:
        doc = DocxDocument(str(path))
        paras = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
        result["paragraphs"] = len(paras)
        result["text"] = "\n".join(paras)
        result["char_count"] = len(result["text"])
        result["outline"] = [
            {"depth": 0, "title": p.text.strip()}
            for p in doc.paragraphs
            if p.style and p.style.name and p.style.name.startswith("Heading") and p.text.strip()
        ]
        core = doc.core_properties
        result["metadata"] = {
            "title": core.title,
            "author": core.author,
            "subject": core.subject,
        }
        result["ok"] = True
    except Exception as e:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
    return result


def page_budget(rel: str, name: str, size: int, role: str) -> int:
    n = name.lower()
    if ARTIFACT_PATH_RE.search(rel.replace("\\", "/")):
        return 0
    if role in {"syllabus", "exam", "solution", "summary"}:
        return 30
    if "chương 0" in n or n.startswith("chuong 0") or "-c0-" in n:
        return 25
    if size < 400_000:
        return 15
    if size < 2_000_000:
        return 8
    return 6


def main() -> None:
    INV.mkdir(parents=True, exist_ok=True)
    EXT.mkdir(parents=True, exist_ok=True)

    files = [
        p
        for p in ROOT.rglob("*")
        if p.is_file() and SKIP_ROOT_NAME not in p.relative_to(ROOT).parts
    ]
    files.sort(key=lambda p: rel_posix(p).lower())

    records = []
    hash_groups: dict[str, list[str]] = defaultdict(list)
    name_groups: dict[str, list[str]] = defaultdict(list)

    for i, p in enumerate(files, start=1):
        rel = rel_posix(p)
        parts = p.relative_to(ROOT).parts
        course_folder = parts[0] if parts else None
        course_id = COURSE_IDS.get(course_folder)
        ext = p.suffix.lower()
        cls = classify(rel, p.name, ext)
        ch = parse_chapter_topic(p.name)
        digest = sha256_file(p)
        year_tokens = YEAR_RE.findall(p.name)
        # ACCO2310 is a course code, not a year; keep only 4-digit years
        year_tokens = [y for y in year_tokens if not re.search(rf"[A-Z]{{3,5}}{y}", p.name)]
        codes = COURSE_CODE_RE.findall(p.name)

        rec = {
            "source_id": f"src-{i:04d}",
            "relative_path": rel,
            "filename": p.name,
            "extension": ext,
            "size_bytes": p.stat().st_size,
            "last_write_time": datetime.fromtimestamp(p.stat().st_mtime).isoformat(timespec="seconds"),
            "course_folder": course_folder,
            "course_id": course_id,
            "source_role": cls["source_role"],
            "classification_confidence": cls["confidence"],
            "classification_reason": cls["reason"],
            "classification_evidence_status": cls["evidence_status"],
            "apparent_chapter": ch["chapter"],
            "apparent_topic_code": ch["topic_code"],
            "apparent_academic_year": year_tokens[0] if year_tokens else None,
            "academic_year_evidence_status": "OBSERVED" if year_tokens else "UNKNOWN",
            "academic_semester": None,
            "semester_evidence_status": "UNKNOWN",
            "course_code_in_filename": codes,
            "sha256": digest,
            "parseability": {
                ".pdf": "pdf_text_layer_unknown_until_open",
                ".docx": "text_extractable",
                ".pptx": "pptx_not_extracted_this_phase_library_missing",
                ".xlsx": "structured",
            }.get(ext, "unknown_extension"),
            "notes": [],
        }
        if rec["course_id"] is None:
            rec["notes"].append("course_id UNKNOWN: top-level folder not in known course map")
        if rec["source_role"] == "exam" and re.search(r"dapan|đáp án", p.name, re.I):
            rec["notes"].append("filename also contains solution/answer token")
        records.append(rec)
        hash_groups[digest].append(rel)
        name_groups[p.name].append(rel)

    for rec in records:
        peers = [x for x in hash_groups[rec["sha256"]] if x != rec["relative_path"]]
        rec["exact_duplicate_paths"] = peers
        rec["exact_duplicate_count"] = len(peers) + 1
        same_name = [x for x in name_groups[rec["filename"]] if x != rec["relative_path"]]
        rec["same_filename_other_paths"] = same_name
        if same_name:
            rec["notes"].append(
                f"same filename appears in {len(same_name)+1} locations (not necessarily content-duplicate)"
            )

    # size-near duplicates (same name + size within 2%)
    for rec in records:
        rec["near_duplicate_signals"] = []
        for other in records:
            if other["source_id"] == rec["source_id"]:
                continue
            if other["filename"] != rec["filename"]:
                continue
            a, b = rec["size_bytes"], other["size_bytes"]
            if a and abs(a - b) / max(a, b) <= 0.02:
                rec["near_duplicate_signals"].append(
                    {
                        "path": other["relative_path"],
                        "size_bytes": b,
                        "signal": "same_filename_size_within_2pct",
                    }
                )

    # --- extraction ---
    extract_index = []
    for rec in records:
        p = ROOT / rec["relative_path"]
        role = rec["source_role"]
        budget = page_budget(rec["relative_path"], rec["filename"], rec["size_bytes"], role)
        ext = rec["extension"]
        course_id = rec["course_id"] or "_unassigned"
        stem = re.sub(r"[^\w\-.]+", "_", rec["filename"], flags=re.U)
        out_dir = EXT / course_id
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{rec['source_id']}__{stem}.extract.md"

        extracted = None
        skipped = None
        if ext == ".pdf":
            if budget <= 0:
                skipped = "skipped_tmp_or_artifact"
            else:
                extracted = extract_pdf(p, budget)
        elif ext == ".docx":
            extracted = extract_docx(p)
        elif ext == ".pptx":
            skipped = "python-pptx not installed; not extracted"
            rec["parseability"] = "pptx_library_missing"
        else:
            skipped = f"no extractor for {ext}"

        header_lines = [
            f"# extract {rec['source_id']}",
            f"relative_path: {rec['relative_path']}",
            f"course_id: {course_id}",
            f"source_role: {role}",
            f"filename: {rec['filename']}",
        ]

        if extracted:
            rec["page_count"] = extracted.get("page_count")
            rec["extract_char_count"] = extracted.get("char_count")
            rec["likely_scanned"] = extracted.get("likely_scanned")
            rec["extract_ok"] = extracted.get("ok")
            rec["pdf_outline_titles"] = [x["title"] for x in extracted.get("outline") or []][:80]
            rec["pdf_metadata"] = extracted.get("metadata") or {}
            if extracted.get("error"):
                rec["extract_error"] = extracted["error"]
                rec["parseability"] = "extract_error"
            elif extracted.get("likely_scanned"):
                rec["parseability"] = "likely_scanned_or_empty_text_layer"
            elif ext == ".pdf":
                rec["parseability"] = "pdf_text_layer_present"
            header_lines += [
                f"page_count: {extracted.get('page_count')}",
                f"pages_extracted: {extracted.get('pages_extracted')}",
                f"char_count: {extracted.get('char_count')}",
                f"likely_scanned: {extracted.get('likely_scanned')}",
                f"extract_ok: {extracted.get('ok')}",
                f"error: {extracted.get('error')}",
                "outline:",
            ]
            for item in extracted.get("outline") or []:
                header_lines.append(f"  - depth={item['depth']} | {item['title']}")
            body = extracted.get("text") or ""
            out_path.write_text("\n".join(header_lines) + "\n\n## TEXT\n" + body, encoding="utf-8")
            extract_index.append(
                {
                    "source_id": rec["source_id"],
                    "extract_path": str(out_path.relative_to(OUT)).replace("\\", "/"),
                    "ok": extracted.get("ok"),
                    "char_count": extracted.get("char_count"),
                    "page_count": extracted.get("page_count"),
                    "outline_count": len(extracted.get("outline") or []),
                    "likely_scanned": extracted.get("likely_scanned"),
                    "error": extracted.get("error"),
                }
            )
        else:
            rec["extract_ok"] = False
            rec["extract_skip_reason"] = skipped
            header_lines.append(f"skipped: {skipped}")
            out_path.write_text("\n".join(header_lines) + "\n", encoding="utf-8")
            extract_index.append(
                {
                    "source_id": rec["source_id"],
                    "extract_path": str(out_path.relative_to(OUT)).replace("\\", "/"),
                    "ok": False,
                    "skipped": skipped,
                }
            )

        print(f"[{rec['source_id']}] {rec['relative_path']} role={role} ok={rec.get('extract_ok')} chars={rec.get('extract_char_count')}", flush=True)

    # post-pass: promote unknown large combined docs named like the course
    for rec in records:
        if rec["source_role"] != "unknown":
            continue
        name = rec["filename"].lower()
        folder = (rec["course_folder"] or "").lower()
        if rec["extension"] == ".pdf" and rec["size_bytes"] >= 2_000_000:
            # if filename is essentially the course name
            compact_name = re.sub(r"[^a-z0-9àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", "", name)
            compact_folder = re.sub(r"[^a-z0-9àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+", "", folder)
            if compact_folder and compact_folder in compact_name:
                rec["source_role"] = "textbook"
                rec["classification_confidence"] = "low"
                rec["classification_reason"] = "large PDF whose filename matches course folder; content role not fully confirmed"
                rec["classification_evidence_status"] = "INFERRED"
                rec["notes"].append("promoted unknown -> textbook by size+name heuristic")

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(ROOT),
        "file_count": len(records),
        "by_extension": {},
        "by_role": {},
        "by_course": {},
        "exact_duplicate_groups": [],
        "parse_errors": [],
        "likely_scanned": [],
    }
    for rec in records:
        summary["by_extension"][rec["extension"]] = summary["by_extension"].get(rec["extension"], 0) + 1
        summary["by_role"][rec["source_role"]] = summary["by_role"].get(rec["source_role"], 0) + 1
        key = rec["course_id"] or rec["course_folder"]
        summary["by_course"][key] = summary["by_course"].get(key, 0) + 1
        if rec.get("extract_error"):
            summary["parse_errors"].append(
                {"source_id": rec["source_id"], "path": rec["relative_path"], "error": rec["extract_error"]}
            )
        if rec.get("likely_scanned"):
            summary["likely_scanned"].append(rec["relative_path"])

    seen_hash = set()
    for digest, paths in hash_groups.items():
        if len(paths) > 1 and digest not in seen_hash:
            seen_hash.add(digest)
            summary["exact_duplicate_groups"].append({"sha256": digest, "paths": paths})

    (INV / "files.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    (INV / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (EXT / "index.json").write_text(json.dumps(extract_index, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE", len(records), "files", flush=True)
    print("SUMMARY", json.dumps(summary, ensure_ascii=False)[:4000], flush=True)


if __name__ == "__main__":
    main()
