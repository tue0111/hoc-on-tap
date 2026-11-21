# -*- coding: utf-8 -*-
"""W6b step A3: append NEW sources of the 4 new course folders to inventory (append-only).

Reuses v3_refresh.listing/compare/classify_source/append_records so rules are identical to Wave 6.
Differences, by design (see reports/v3/PLAN_W6B_MON_MOI.md):
- unsupported extensions (.xls/.xlsm) are inventoried with index_include: false instead of aborting;
- apparent_chapter is taken from the 'Chương N' folder (INFERRED), apparent_topic_code from parse_name.
Usage: python scripts/w6b_append_inventory.py --plan | --apply
"""
import argparse, hashlib, json, re, sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from retrieval.config import SYSTEM, SOURCE_ROOT
from scripts.v3_refresh import listing, compare, classify_source, append_records, guard, core_integrity, read_json, write_json
from scripts.v3_extract_course import parse_name
from scripts.v3_extract_learner_notes import extract_one

NEW_FOLDERS = {"Hệ thống thông tin kế toán 1", "Kế toán thuế 1", "Kế toán tài chính 3", "Kế toán hành chính sự nghiệp"}
SUPPORTED = {".pdf", ".docx", ".pptx", ".txt", ".md", ".xlsx"}


def folder_chapter(rel):
    for part in PurePosixPath(rel).parts[1:-1]:
        m = re.fullmatch(r"Chương\s+(\d+)", part)
        if m:
            return int(m[1])
        if part.casefold() == "chương mở đầu":
            return 0
    return None


def build():
    inv = read_json(SYSTEM / "inventory/files.json")
    from scripts.build_inventory import COURSE_IDS
    # D:\Hoc is now also a git repo with _grok_pack/README; only registered course folders are sources.
    rows = [r for r in listing(SOURCE_ROOT) if r["relative_path"].split("/")[0] in COURSE_IDS]
    delta = compare(rows, inv)
    others = [r for k in ("NEW", "CHANGED", "MISSING") for r in delta[k] if r["relative_path"].split("/")[0] not in NEW_FOLDERS]
    if others or delta["CHANGED"] or delta["MISSING"]:
        raise SystemExit("STOP: delta outside the 4 new folders: " + json.dumps(others[:5] + delta["CHANGED"][:3] + delta["MISSING"][:3], ensure_ascii=False))
    guard(delta)
    core_integrity()
    staged = []
    for e in delta["NEW"]:
        rel = e["relative_path"]
        src = SOURCE_ROOT / rel
        data = src.read_bytes()
        if len(data) != e["size_bytes"] or src.stat().st_mtime_ns != e["mtime_ns"]:
            raise SystemExit("STOP: source drift " + rel)
        ext = PurePosixPath(rel).suffix.lower()
        first = ""
        if ext in SUPPORTED:
            x = extract_one(src, ext)
            first = (x.get("pages") or [{}])[0].get("text", "") if x.get("ok") else ""
        c = classify_source(rel, first)
        if ext == ".pdf" and c["source_role"] == "unknown" and re.search(r"scri?pt?", PurePosixPath(rel).name, re.I):
            # lecturer video transcript ("Script"/"Scrip" in filename), same role as _nguon unit scripts
            c = {**c, "source_role": "lecture_note",
                 "classification_reason": c["classification_reason"] + "; W6b: 'script/scrip' in PDF filename -> lecture_note"}
        p = parse_name(PurePosixPath(rel).name, {})
        ch = p["chapter"] if p["chapter"] is not None else folder_chapter(rel)
        staged.append({**e, "sha256": hashlib.sha256(data).hexdigest(), **c,
                       "apparent_chapter": ch, "apparent_topic_code": p["topic"],
                       "w6b_unsupported_extension": ext not in SUPPORTED})
    return inv, staged


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true")
    g.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    inv, staged = build()
    out = SYSTEM / "work/w6b/inventory_plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    write_json(out, staged)
    summary = {}
    for s in staged:
        k = (s["course_id"], s["partition"], "unsupported" if s["w6b_unsupported_extension"] else "ok")
        summary[" | ".join(k)] = summary.get(" | ".join(k), 0) + 1
    print(json.dumps({"new": len(staged), "summary": summary, "plan": str(out)}, ensure_ascii=False, indent=1))
    if not a.apply:
        return
    new_inv = append_records(inv, [{k: v for k, v in s.items() if k != "w6b_unsupported_extension"} for s in staged])
    new_rows = new_inv[len(inv):]
    ov_path = SYSTEM / "curriculum/source_registry_overrides.yaml"
    ov = yaml.safe_load(ov_path.read_text(encoding="utf-8"))
    for row, s in zip(new_rows, staged):
        row["notes"] = row["notes"] + ["added_in_w6b"]
        entry = {"source_id": row["source_id"], "relative_path": row["relative_path"],
                 "content_role": row["source_role"], "partition": row["partition"],
                 "evidence_status": "INFERRED", "note": "W6b classification (Wave 6 rules); see work/w6b/inventory_plan.json"}
        if s["w6b_unsupported_extension"]:
            entry.update(index_include=False, exclusion_reason="unsupported_extension")
        ov.setdefault("overrides", []).append(entry)
    write_json(SYSTEM / "inventory/files.json", new_inv)
    ov_path.write_text(yaml.safe_dump(ov, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"APPLIED: {len(new_rows)} rows {new_rows[0]['source_id']}..{new_rows[-1]['source_id']}")


if __name__ == "__main__":
    main()
