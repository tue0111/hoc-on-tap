# -*- coding: utf-8 -*-
"""Build source_registry.yaml from inventory/files.json with authority ranks."""
from __future__ import annotations
import json
from pathlib import Path

INV = Path(r"D:\Hoc\_learning_system\inventory\files.json")
OUT = Path(r"D:\Hoc\_learning_system\curriculum\source_registry.yaml")

RANK = {
    "syllabus": 1,
    "lecture_slide": 2,
    "lecture_note": 2,
    "textbook": 3,
    "exercise": 4,
    "solution": 4,
    "exam": 5,
    "quiz": 5,
    "assignment": 5,
    "reference": 6,
    "spreadsheet": 6,
    "summary": 6,
    "unknown": None,
}

# Content-informed reclassifications (still INFERRED unless filename was already strong)
PROMOTE_TEXTBOOK = {
    "Kế toán tài chính 1/KTTC 1.pdf",
    "Nguyên lý kế toán/Nguyên Lý Kế Toán.pdf",
    "Ngân hàng thương mại/Ngân hàng Thương Mại.pdf",
    "Tài chính doanh nghiệp 1/Tài Chính Doanh NGhiệp.pdf",
    "Tài chính hành chính sự nghiệp/Hành chính và sự nghiệp.pdf",
}
PROMOTE_EXAM = {
    "Kế toán tài chính 2/Đề 2.pdf",
}


def yaml_escape(s: str) -> str:
    if s is None:
        return "null"
    s = str(s)
    if any(c in s for c in ":{}[]#&*!|>'\"%@`") or s == "" or s.lower() in {"true", "false", "null"}:
        return json.dumps(s, ensure_ascii=False)
    return s


def main():
    records = json.loads(INV.read_text(encoding="utf-8"))
    lines = [
        "registry_id: source-registry",
        'version: "0.1.0"',
        "layer: curriculum",
        "source_root: D:/Hoc",
        "generated_from: inventory/files.json",
        "notes:",
        "  - Roles start from filename heuristics; some combined PDFs promoted after size+name+extract inspection.",
        "  - authority_rank is a retrieval prior, not a merge license.",
        "  - tmp/render/proxy files remain unknown artifacts and must not be treated as lecturer materials.",
        "sources:",
    ]
    for rec in records:
        rel = rec["relative_path"]
        role = rec["source_role"]
        conf = rec["classification_confidence"]
        ev = rec["classification_evidence_status"]
        reason = rec["classification_reason"]
        notes = list(rec.get("notes") or [])
        if rel.replace("\\", "/") in PROMOTE_TEXTBOOK and role in {"unknown", "textbook"}:
            role = "textbook"
            conf = "low"
            ev = "INFERRED"
            reason = "large combined PDF named after the course; treated as textbook/course-pack pending deeper TOC confirmation"
            notes.append("promoted_to_textbook_in_source_registry")
        if rel.replace("\\", "/") in PROMOTE_EXAM and role == "unknown":
            role = "exam"
            conf = "medium"
            ev = "OBSERVED"
            reason = "filename is Đề N (exam booklet token)"
            notes.append("promoted_to_exam_in_source_registry")
        rank = RANK.get(role)
        lines.append(f"  - source_id: {rec['source_id']}")
        lines.append(f"    relative_path: {yaml_escape(rel)}")
        lines.append(f"    filename: {yaml_escape(rec['filename'])}")
        lines.append(f"    course_id: {rec.get('course_id') or 'null'}")
        lines.append(f"    course_folder: {yaml_escape(rec.get('course_folder'))}")
        lines.append(f"    source_role: {role}")
        lines.append(f"    classification_confidence: {conf}")
        lines.append(f"    classification_evidence_status: {ev}")
        lines.append(f"    classification_reason: {yaml_escape(reason)}")
        lines.append(f"    authority_rank: {rank if rank is not None else 'null'}")
        lines.append(f"    extension: {yaml_escape(rec.get('extension'))}")
        lines.append(f"    size_bytes: {rec.get('size_bytes')}")
        lines.append(f"    page_count: {rec.get('page_count')}")
        lines.append(f"    parseability: {yaml_escape(rec.get('parseability'))}")
        lines.append(f"    extract_ok: {str(rec.get('extract_ok')).lower()}")
        lines.append(f"    extract_char_count: {rec.get('extract_char_count')}")
        lines.append(f"    likely_scanned: {str(rec.get('likely_scanned')).lower()}")
        lines.append(f"    apparent_chapter: {rec.get('apparent_chapter')}")
        lines.append(f"    apparent_topic_code: {yaml_escape(rec.get('apparent_topic_code')) if rec.get('apparent_topic_code') else 'null'}")
        year = rec.get("apparent_academic_year")
        lines.append(f"    academic_year_in_filename: {year if year else 'null'}")
        codes = rec.get("course_code_in_filename") or []
        if codes:
            lines.append("    course_code_in_filename:")
            for c in codes:
                lines.append(f"      - {c}")
        else:
            lines.append("    course_code_in_filename: []")
        dups = rec.get("exact_duplicate_paths") or []
        lines.append(f"    exact_duplicate_paths: {json.dumps(dups, ensure_ascii=False)}")
        if notes:
            lines.append("    notes:")
            for n in notes:
                lines.append(f"      - {yaml_escape(n)}")
        else:
            lines.append("    notes: []")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", OUT, "sources", len(records))


if __name__ == "__main__":
    main()
