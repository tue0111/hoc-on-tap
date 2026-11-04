# -*- coding: utf-8 -*-
"""Incremental ingest of NEW files only. Does not rebuild Phase 2 NLKT/KTTC1 index."""
from __future__ import annotations
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
from pypdf import PdfReader

ROOT = Path(r"D:\Hoc")
SYS = ROOT / "_learning_system"
INV_PATH = SYS / "inventory" / "files.json"
DELTA_PATH = SYS / "inventory" / "delta_phase2_1.json"
EXT = SYS / "extracts"
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

CHAPTER_FN = re.compile(r"(?i)(?:chương|chuong)\s*(\d+)")
C_RE = re.compile(r"(?i)(?:^|[_\-\s])c(\d+)(?:[_\-\s.]|$)")
TOPIC_RE = re.compile(r"(?i)(?:cd|chủ đề|chude)[.\s_-]*(\d+(?:\.\d+)?)")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify(rel: str, name: str) -> dict:
    n = name.lower()
    r = rel.lower().replace("\\", "/")
    if "/_nguon/" in f"/{r}/" or r.split("/")[1:2] == ["_nguon"]:
        return {
            "source_role": "lecture_note",
            "confidence": "medium",
            "reason": "path _nguon + script/topic filename; unit script underlying chapter compilations",
            "evidence_status": "OBSERVED",
            "unit_script": True,
        }
    if re.search(r"đề thi|de thi|dethimau", n):
        return {"source_role": "exam", "confidence": "medium", "reason": "filename exam token", "evidence_status": "OBSERVED", "unit_script": False}
    if re.search(r"hướng dẫn ôn|huong dan on|ôn tập|on tap", n):
        return {"source_role": "summary", "confidence": "medium", "reason": "filename ôn tập token", "evidence_status": "OBSERVED", "unit_script": False}
    if CHAPTER_FN.match(n) or n.startswith("chương"):
        return {"source_role": "lecture_note", "confidence": "low", "reason": "filename Chương N", "evidence_status": "INFERRED", "unit_script": False}
    return {"source_role": "unknown", "confidence": "low", "reason": "no strong filename signal", "evidence_status": "UNKNOWN", "unit_script": False}


def chapter_of(name: str, rel: str) -> int | None:
    m = CHAPTER_FN.search(name)
    if m:
        return int(m.group(1))
    m = re.search(r"(?i)ch(\d+)", name)
    if m and "_nguon" in rel.replace("\\", "/"):
        return int(m.group(1))
    m = re.search(r"(?i)(?:^|[_\-\s.])c(\d+)(?:[_\-\s.]|$)", name)
    if m:
        return int(m.group(1))
    # CHUONG 5 / Script_Ch4
    m = re.search(r"(?i)chuong\s*(\d+)|script_ch(\d+)|ch(\d+)_cd|ch(\d+)-cd", name)
    if m:
        for g in m.groups():
            if g:
                return int(g)
    m = re.search(r"(?i)ch(\d+)", name)
    return int(m.group(1)) if m else None


def topic_of(name: str) -> str | None:
    m = TOPIC_RE.search(name)
    return m.group(1) if m else None


def light_extract(path: Path, max_pages: int) -> dict:
    out = {"ok": False, "page_count": None, "pages_extracted": 0, "char_count": 0, "text": "", "outline": [], "error": None, "title_line": None}
    try:
        reader = PdfReader(str(path))
        out["page_count"] = len(reader.pages)
        try:
            titles = []
            def walk(items, depth=0):
                if not items:
                    return
                for it in items:
                    if isinstance(it, list):
                        walk(it, depth + 1)
                    else:
                        titles.append(getattr(it, "title", None) or str(it))
            walk(reader.outline)
            out["outline"] = titles[:40]
        except Exception:
            pass
    except Exception as e:
        out["error"] = str(e)
        return out
    try:
        texts = []
        with pdfplumber.open(str(path)) as doc:
            n = min(len(doc.pages), max_pages)
            for i in range(n):
                t = doc.pages[i].extract_text() or ""
                texts.append(f"\n----- PAGE {i+1} -----\n{t}")
            out["pages_extracted"] = n
        body = "".join(texts)
        out["text"] = body
        out["char_count"] = len(body)
        out["ok"] = True
        for line in body.splitlines():
            s = line.strip()
            if s and not s.startswith("-----") and len(s) > 8:
                out["title_line"] = s[:180]
                break
    except Exception as e:
        out["error"] = (out.get("error") or "") + f" pdfplumber:{e}"
    return out


def is_canonical_new(rel: str, name: str) -> bool:
    r = rel.replace("\\", "/")
    if "/_nguon/" in f"/{r}/":
        return False
    n = name.lower()
    return bool(CHAPTER_FN.search(name) or re.search(r"đề thi|hướng dẫn ôn|ôn tập", n))


def main():
    inv = json.loads(INV_PATH.read_text(encoding="utf-8"))
    max_id = max(int(r["source_id"].split("-")[1]) for r in inv)
    delta = json.loads(DELTA_PATH.read_text(encoding="utf-8"))
    new_paths = delta["new"]
    existing = {r["relative_path"] for r in inv}
    added = []
    extracts_index = []
    next_id = max_id + 1
    for rel in new_paths:
        if rel in existing:
            continue
        path = ROOT / rel
        if not path.exists():
            continue
        parts = Path(rel).parts
        folder = parts[0]
        cid = COURSE_IDS.get(folder)
        name = path.name
        ext = path.suffix.lower()
        cls = classify(rel, name)
        ch = chapter_of(name, rel)
        topic = topic_of(name)
        rec = {
            "source_id": f"src-{next_id:04d}",
            "relative_path": rel,
            "filename": name,
            "extension": ext,
            "size_bytes": path.stat().st_size,
            "last_write_time": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            "course_folder": folder,
            "course_id": cid,
            "source_role": cls["source_role"],
            "classification_confidence": cls["confidence"],
            "classification_reason": cls["reason"],
            "classification_evidence_status": cls["evidence_status"],
            "apparent_chapter": ch,
            "apparent_topic_code": topic,
            "apparent_academic_year": None,
            "academic_year_evidence_status": "UNKNOWN",
            "academic_semester": None,
            "semester_evidence_status": "UNKNOWN",
            "course_code_in_filename": [],
            "sha256": sha256_file(path),
            "parseability": "pdf_text_layer_unknown_until_open" if ext == ".pdf" else "unknown",
            "notes": ["added_in_phase_2_1"],
            "unit_script": cls.get("unit_script", False),
            "phase": "2.1",
        }
        next_id += 1
        canonical = is_canonical_new(rel, name)
        rec["ingest_priority"] = "canonical" if canonical else "unit_script"
        if ext == ".pdf" and canonical:
            ex = light_extract(path, 12)
            rec["page_count"] = ex.get("page_count")
            rec["extract_char_count"] = ex.get("char_count")
            rec["extract_ok"] = ex.get("ok")
            rec["title_line"] = ex.get("title_line")
            rec["pdf_outline_titles"] = ex.get("outline") or []
            rec["parseability"] = "pdf_text_layer_present" if ex.get("ok") else "extract_error"
            out_dir = EXT / (cid or "_unassigned")
            out_dir.mkdir(parents=True, exist_ok=True)
            stem = re.sub(r"[^\w\-.]+", "_", name)
            ep = out_dir / f"{rec['source_id']}__{stem}.extract.md"
            header = [
                f"# extract {rec['source_id']}",
                f"relative_path: {rel}",
                f"course_id: {cid}",
                f"source_role: {rec['source_role']}",
                f"filename: {name}",
                f"phase: 2.1",
                f"page_count: {ex.get('page_count')}",
                f"pages_extracted: {ex.get('pages_extracted')}",
                f"char_count: {ex.get('char_count')}",
                "outline:",
            ]
            for t in ex.get("outline") or []:
                header.append(f"  - {t}")
            ep.write_text("\n".join(header) + "\n\n## TEXT\n" + (ex.get("text") or ""), encoding="utf-8")
            rec["extract_path"] = str(ep.relative_to(SYS)).replace("\\", "/")
            print("EXTRACT", rec["source_id"], rel, "pages", rec.get("page_count"), "title", rec.get("title_line"), flush=True)
        else:
            rec["extract_ok"] = False
            rec["extract_skip_reason"] = "unit_script_catalog_only" if rec.get("unit_script") else "not_canonical"
            print("CATALOG", rec["source_id"], rel, "ch", ch, rec["source_role"], flush=True)
        inv.append(rec)
        added.append(rec)

    INV_PATH.write_text(json.dumps(inv, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "phase": "2.1",
        "added": len(added),
        "new_source_id_range": [added[0]["source_id"], added[-1]["source_id"]] if added else [],
        "by_course": {},
        "canonical": [a["source_id"] for a in added if a.get("ingest_priority") == "canonical"],
        "unit_scripts": [a["source_id"] for a in added if a.get("unit_script")],
    }
    for a in added:
        k = a["course_id"] or a["course_folder"]
        summary["by_course"][k] = summary["by_course"].get(k, 0) + 1
    (SYS / "inventory" / "phase2_1_added.json").write_text(json.dumps({"summary": summary, "records": added}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ADDED", len(added), json.dumps(summary["by_course"], ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
