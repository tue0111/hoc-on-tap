# -*- coding: utf-8 -*-
"""V3 full extract for ONE course (plan 6.2). Read-only on source files, no page cap.
usage: python scripts/v3_extract_course.py --course <course_id>
"""
from __future__ import annotations
import argparse, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval import courses as C
from retrieval.config import AUTHORITY_BY_ROLE, CONTENT_ROLE_AUTHORITY, INVENTORY, NORMALIZED, SOURCE_OVERRIDES, SOURCE_ROOT, THIN_CHARS_PER_PAGE
from retrieval.textutil import content_hash, nfc, sha256_file
from scripts.phase2_extract import extract_pdf, load_overrides

EXTRACT_VERSION = "3.0.0"

# spec 7.2, first match wins. each: (rule, regex, chapter_group, topic_fn, part_fn)
RULES = [
    ("kttc2", re.compile(r"KTTC2-C(\d+)-CD(\d+\.\d+)", re.I), lambda m: (m[1], m[2], None)),
    ("ktcp", re.compile(r"KTCP-C(\d+)-CD(\d+(?:\.\d+)+)", re.I), lambda m: (m[1], m[2], None)),
    ("chuong_chude_p", re.compile(r"CHUONG\s*(\d+)\s*CHU\s*DE\s*(\d+)\s*P\s*(\d+)", re.I), lambda m: (m[1], f"{m[1]}.{m[2]}", f"P{m[3]}")),
    ("chuong_chude", re.compile(r"CHUONG\s*(\d+)\s*CHU\s*DE\s*(\d+)", re.I), lambda m: (m[1], f"{m[1]}.{m[2]}", None)),
    ("ktnh", re.compile(r"KTNH_C(\d+)_CD(\d+\.\d+)(?:.*?[-_]\s*Video\s*(\d+))?", re.I), lambda m: (m[1], m[2], f"Video {m[3]}" if m[3] else None)),
    ("script_ch_cd", re.compile(r"Script_Ch(\d+)[_-]\s*CD\s*(\d+\.\d+)(?:_P(\d+))?", re.I), lambda m: (m[1], m[2], f"P{m[3]}" if m[3] else None)),
    ("script_ch_clip", re.compile(r"Script_Ch(\d+)_Cli[pP]\s*(\d+)", re.I), lambda m: (m[1], f"clip {m[2]}", None)),
    ("tltk", re.compile(r"TLTK_.*CD\s*(\d+)\.(\d+)", re.I), lambda m: (m[1], f"{m[1]}.{m[2]}", "reference")),
    ("kdnv", re.compile(r"KDV?NV-C(\d+)-CD(\d+\.\d+)", re.I), lambda m: (m[1], m[2], None)),
    ("chuong_chude_vn", re.compile(r"Chuong(\d+)-Chu\s*de\s*(\d+\.\d+)", re.I), lambda m: (m[1], m[2], None)),
    ("lkd", re.compile(r"LKD-C(\d+)-\s*CD\.?\s*(\d+\.\d+)", re.I), lambda m: (m[1], m[2], None)),
    ("nlkt", re.compile(r"NLKT-C(\d+)-CD(\d+\.\d+)", re.I), lambda m: (m[1], m[2], None)),
    ("chuong", re.compile(r"(?:Slide\s*)?(?:Chương|chương|Chuong)\s*(\d+)", re.I), lambda m: (m[1], None, None)),
]


def parse_name(filename: str, rec: dict) -> dict:
    stem = Path(filename).stem
    for rule, rx, fn in RULES:
        m = rx.search(stem)
        if m:
            ch, topic, part = fn(m)
            return {"chapter": int(ch), "topic": topic, "part": part, "parse_rule": rule}
    return {"chapter": rec.get("apparent_chapter"), "topic": rec.get("apparent_topic_code"), "part": None,
            "parse_rule": "inventory_apparent" if rec.get("apparent_chapter") is not None else "none"}


def extract_docx(path: Path) -> dict:
    import docx

    try:
        d = docx.Document(str(path))
        parts = []
        # paragraphs and tables in document order
        from docx.table import Table
        from docx.text.paragraph import Paragraph

        body = d.element.body
        tcount = 0
        for child in body.iterchildren():
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "p":
                t = Paragraph(child, d).text
                if t.strip():
                    parts.append(t)
            elif tag == "tbl":
                tcount += 1
                tbl = Table(child, d)
                rows = [" | ".join(c.text.strip().replace("\n", " ") for c in r.cells) for r in tbl.rows]
                parts.append(f"[TABLE {tcount}]\n" + "\n".join(rows))
        text = nfc("\n".join(parts))
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"docx: {e}", "pages": [], "page_count": None, "char_count": 0, "outline": []}
    pages, i, n = [], 0, 1
    while i < len(text) or n == 1:
        seg = text[i:i + 3000]
        pages.append({"page": n, "text": seg, "char_count": len(seg.strip())})
        i += 3000; n += 1
        if i >= len(text):
            break
    return {"ok": True, "pages": pages, "page_count": len(pages), "char_count": sum(p["char_count"] for p in pages),
            "outline": [], "synthetic_pages": True}


def extract_text(path: Path) -> dict:
    text = nfc(path.read_text(encoding="utf-8", errors="replace"))
    pages, n = [], 1
    for i in range(0, max(len(text), 1), 3000):
        seg = text[i:i + 3000]
        pages.append({"page": n, "text": seg, "char_count": len(seg.strip())}); n += 1
    return {"ok": True, "pages": pages, "page_count": len(pages), "char_count": sum(p["char_count"] for p in pages),
            "outline": [], "synthetic_pages": True}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--course", required=True)
    cid = ap.parse_args().course
    reg = C.get_course(cid) or sys.exit(f"unknown course {cid}")
    paths = C.partition_paths(cid)
    NORMALIZED.mkdir(parents=True, exist_ok=True)
    from scripts.v3_inventory import active_records
    inv = active_records(json.loads(Path(INVENTORY).read_text(encoding="utf-8")))
    ov = load_overrides()
    tmp = set()
    ovdoc = json.loads(json.dumps(__import__("yaml").safe_load(SOURCE_OVERRIDES.read_text(encoding="utf-8"))))
    tmp = set(ovdoc.get("tmp_artifacts_not_curriculum") or [])
    recs = [r for r in inv if r.get("course_id") == cid and r["source_id"] not in tmp and "/tmp/" not in r["relative_path"]]
    docs, pages_out, cov = [], [], []
    for rec in recs:
        rel, sid = rec["relative_path"], rec["source_id"]
        path = SOURCE_ROOT / rel
        o = ov.get(sid) or {}
        role = o.get("content_role") or rec.get("source_role") or "unknown"
        authority = CONTENT_ROLE_AUTHORITY.get(role) or AUTHORITY_BY_ROLE.get(rec.get("source_role") or "unknown", 8)
        if "reference" in str(parse_name(rec["filename"], rec).get("part")):
            authority = 6
        learner = role == "learner_material"
        combined = "combined" in str(role)
        ext = (rec.get("extension") or path.suffix).lower()
        print("EXTRACT", sid, rel, flush=True)
        if ext == ".pdf": e = extract_pdf(path)
        elif ext == ".docx": e = extract_docx(path)
        elif ext in (".txt", ".md"): e = extract_text(path)
        elif ext == ".pptx" and not learner:
            e = {"ok": False, "error": "pptx extractor not wired (non-learner pptx)", "pages": [], "page_count": None, "char_count": 0, "outline": []}
        else:
            e = {"ok": False, "error": f"skipped {ext}" + (" (learner_material)" if learner else ""), "skipped": True, "pages": [], "page_count": None, "char_count": 0, "outline": []}
        pc, cc = e.get("page_count") or 0, e.get("char_count") or 0
        cpp = cc / pc if pc else 0
        thin = cpp < THIN_CHARS_PER_PAGE
        pq = "skipped" if e.get("skipped") else ("error" if not e.get("ok") else ("thin" if thin else "ok"))
        pn = parse_name(rec["filename"], rec)
        unit = "_nguon" in rel.split("/")
        full = "\n\n".join(f"----- PAGE {p['page']} -----\n{p['text']}" for p in e.get("pages") or [])
        doc = {
            "document_id": f"doc-{sid}", "source_id": sid, "course_id": cid, "course_name": reg["name"],
            "course_code": None, "course_codes": reg.get("codes") or [],
            "source_file": rec["filename"], "relative_path": rel, "source_type": rec.get("source_role") or "unknown",
            "content_role": role, "authority": authority, "chapter": pn["chapter"], "section": None, "topic": pn["topic"],
            "part": pn["part"], "parse_rule": pn["parse_rule"], "unit_script": unit,
            "page_start": 1 if pc else None, "page_end": pc or None, "page_count": pc, "text": full, "char_count": cc,
            "chars_per_page": round(cpp, 1), "parse_quality": pq, "extract_ok": bool(e.get("ok")), "extract_error": e.get("error"),
            "synthetic_pages": bool(e.get("synthetic_pages")),
            "content_hash": content_hash(full), "source_sha256": rec.get("sha256") or sha256_file(path),
            "combined_duplicate": combined, "learner_material": learner,
            "index_include": (not combined) and (not learner) and bool(e.get("ok")) and cc > 0,
            "dup_group": None, "outline": e.get("outline") or [],
            "provenance": {"extract_version": EXTRACT_VERSION, "extracted_at": datetime.now(timezone.utc).isoformat(),
                           "tool": "pdfplumber+pypdf" if ext == ".pdf" else ext, "page_cap": None},
        }
        docs.append(doc)
        for p in e.get("pages") or []:
            pages_out.append({"document_id": doc["document_id"], "source_id": sid, "course_id": cid, "relative_path": rel,
                              "source_file": rec["filename"], "source_type": doc["source_type"], "authority": authority,
                              "chapter": pn["chapter"], "topic": pn["topic"], "page": p["page"], "text": p["text"],
                              "char_count": p["char_count"], "combined_duplicate": combined, "index_include": doc["index_include"],
                              "unit_script": unit, "parse_quality": "thin" if p["char_count"] < THIN_CHARS_PER_PAGE else pq})
        cov.append({"source_id": sid, "relative_path": rel, "page_count": pc, "char_count": cc, "chars_per_page": round(cpp, 1),
                    "parse_quality": pq, "parse_rule": pn["parse_rule"], "chapter": pn["chapter"], "topic": pn["topic"],
                    "unit_script": unit, "index_include": doc["index_include"], "combined_duplicate": combined})
    with paths["documents"].open("w", encoding="utf-8") as f:
        for d in docs: f.write(json.dumps(d, ensure_ascii=False) + "\n")
    with paths["pages"].open("w", encoding="utf-8") as f:
        for p in pages_out: f.write(json.dumps(p, ensure_ascii=False) + "\n")
    # page-count verification against pypdf
    from pypdf import PdfReader
    mism = []
    for d in docs:
        if d["relative_path"].lower().endswith(".pdf") and d["extract_ok"]:
            if len(PdfReader(str(SOURCE_ROOT / d["relative_path"])).pages) != d["page_count"]:
                mism.append(d["source_id"])
    unparsed = [d["relative_path"] for d in docs if d["unit_script"] and d["chapter"] is None]
    summary = {"extract_version": EXTRACT_VERSION, "course_id": cid, "document_count": len(docs), "page_count": len(pages_out),
               "total_chars": sum(d["char_count"] for d in docs), "indexed_documents": sum(d["index_include"] for d in docs),
               "thin_documents": [d["source_id"] for d in docs if d["parse_quality"] == "thin"],
               "errors": [d["source_id"] for d in docs if d["parse_quality"] == "error"],
               "skipped": [d["source_id"] for d in docs if d["parse_quality"] == "skipped"],
               "page_count_mismatch": mism, "UNPARSED": unparsed, "coverage": cov}
    paths["coverage"].write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print("DONE docs", len(docs), "pages", len(pages_out), "chars", summary["total_chars"], "errors", summary["errors"],
          "mismatch", mism, "UNPARSED", unparsed, "thin", summary["thin_documents"], flush=True)


if __name__ == "__main__":
    main()
