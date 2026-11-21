# -*- coding: utf-8 -*-
"""W6b: learner added HTTTKT1 Chương 4 scripts 4.1-4.3 and renamed the 3 old scripts to script_4.4..4.6 (2026-11-21).

- Renames are matched by sha256 (identical bytes). Rows src-0377..0379 are W6b rows not yet published, so the
  path is updated in place with `renamed_from`; source_id is kept so the frozen eval still points at them.
- New files are appended as next src ids, same classification rules as w6b_append_inventory.py.
Refuses anything outside 'Hệ thống thông tin kế toán 1/Chương 4/'.
"""
import hashlib, json, re, sys, unicodedata
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml
from retrieval.config import SYSTEM, SOURCE_ROOT
from scripts.v3_refresh import listing, compare, classify_source, append_records, read_json, write_json
from scripts.build_inventory import COURSE_IDS
from scripts.v3_extract_learner_notes import extract_one
from scripts.v3_extract_course import parse_name

PREFIX = "Hệ thống thông tin kế toán 1/Chương 4/"
# Fixed allowlists, matched on the FULL relative_path (not basename), so e.g. 'Chương 4/extra/script_4.1.pdf' is refused.
# Anything else in the delta stops the script before any write.
NEW_ALLOW = {PREFIX + "script_4.1.pdf", PREFIX + "script_4.2.pdf", PREFIX + "script_4.3.pdf"}
# source_id -> (old full path, new full path). The source_id binds each rename to its row.
RENAME_ALLOW = {
    "src-0379": (PREFIX + "script.pdf", PREFIX + "script_4.4.pdf"),
    "src-0377": (PREFIX + "script (1).pdf", PREFIX + "script_4.5.pdf"),
    "src-0378": (PREFIX + "script (2).pdf", PREFIX + "script_4.6.pdf"),
}


def check_new(rel):
    """Full relative_path must be one of the approved new files; otherwise SystemExit."""
    if rel not in NEW_ALLOW:
        raise SystemExit("STOP: new file not in allowlist: " + rel)


def check_rename(old, new_rel):
    """Rename must match the approved (old, new) full-path pair for this exact source_id."""
    if RENAME_ALLOW.get(old["source_id"]) != (old["relative_path"], new_rel):
        raise SystemExit("STOP: rename not in allowlist: %s -> %s (%s)" % (old["relative_path"], new_rel, old["source_id"]))
    if "added_in_w6b" not in old.get("notes", []):
        raise SystemExit("STOP: rename of a published (pre-W6b) row needs supersedes handling: " + old["source_id"])


def check_topic_page1(rel, x):
    """New file: extraction must succeed and page 1 must contain a line 'Chủ đề N' matching the 4.N in the filename."""
    if not x.get("ok") or not x.get("pages"):
        raise SystemExit("STOP: extraction failed for " + rel + ": " + str(x.get("error")))
    m = re.fullmatch(r"script_4\.(\d+)", PurePosixPath(rel).stem)
    if not m:
        raise SystemExit("STOP: filename does not match script_4.N: " + rel)
    text = unicodedata.normalize("NFC", x["pages"][0].get("text", ""))
    if not re.search(r"(?m)^\s*Chủ đề\s+" + m.group(1) + r"(?![.\d])", text):
        raise SystemExit("STOP: page 1 has no line 'Chủ đề " + m.group(1) + "' for " + rel)


def main(apply):
    inv_p, ov_p = SYSTEM / "inventory/files.json", SYSTEM / "curriculum/source_registry_overrides.yaml"
    inv = read_json(inv_p)
    rows = [r for r in listing(SOURCE_ROOT) if r["relative_path"].split("/")[0] in COURSE_IDS]
    delta = compare(rows, inv)
    if delta["CHANGED"] or any(not r["relative_path"].startswith(PREFIX) for r in delta["NEW"] + delta["MISSING"]):
        raise SystemExit("STOP: unexpected delta " + json.dumps(delta, ensure_ascii=False)[:800])
    sha = {r["relative_path"]: hashlib.sha256((SOURCE_ROOT / r["relative_path"]).read_bytes()).hexdigest() for r in delta["NEW"]}
    missing = {r["sha256"]: r for r in delta["MISSING"]}
    renames, new = [], []
    for r in delta["NEW"]:
        old = missing.pop(sha[r["relative_path"]], None)
        (renames if old else new).append((r, old))
    if missing:
        raise SystemExit("STOP: MISSING without identical renamed file: " + str([m["relative_path"] for m in missing.values()]))
    for r, old in renames:
        check_rename(old, r["relative_path"])
        print("RENAME", old["source_id"], old["relative_path"].split("/")[-1], "->", r["relative_path"].split("/")[-1])
    for r, _ in new:
        check_new(r["relative_path"])
    staged = []
    for r, _ in new:
        rel = r["relative_path"]; src = SOURCE_ROOT / rel; ext = PurePosixPath(rel).suffix.lower()
        x = extract_one(src, ext)
        check_topic_page1(rel, x)
        c = classify_source(rel, (x.get("pages") or [{}])[0].get("text", "") if x.get("ok") else "")
        if ext == ".pdf" and c["source_role"] == "unknown" and "script" in rel.lower():
            c = {**c, "source_role": "lecture_note", "classification_reason": c["classification_reason"] + "; W6b: 'script' in PDF filename -> lecture_note"}
        stem = PurePosixPath(rel).stem  # script_4.1 -> topic 4.1 (OBSERVED from learner-chosen filename + page 1)
        topic = stem.split("_", 1)[1] if "_" in stem else None
        staged.append({**r, "sha256": sha[rel], **c, "apparent_chapter": 4, "apparent_topic_code": topic})
        print("NEW", rel.split("/")[-1], c["source_role"], topic)
    if not apply:
        return
    by_id = {x["source_id"]: x for x in inv}
    ov = yaml.safe_load(ov_p.read_text(encoding="utf-8")); ovid = {o["source_id"]: o for o in ov["overrides"]}
    for r, old in renames:
        row = by_id[old["source_id"]]
        row["renamed_from"] = row["relative_path"]
        row["relative_path"] = r["relative_path"]; row["filename"] = PurePosixPath(r["relative_path"]).name
        row["notes"] = row["notes"] + ["renamed_by_learner_2026-11-21"]
        if old["source_id"] in ovid:
            ovid[old["source_id"]]["relative_path"] = r["relative_path"]
    new_inv = append_records(inv, staged)
    for row in new_inv[len(inv):]:
        row["notes"] = row["notes"] + ["added_in_w6b", "learner_supplied_missing_topic"]
        ov["overrides"].append({"source_id": row["source_id"], "relative_path": row["relative_path"],
                                "content_role": row["source_role"], "partition": row["partition"],
                                "evidence_status": "OBSERVED", "note": "W6b: learner-supplied script for Chương 4 topic " + str(row.get("apparent_topic_code"))})
        print("APPENDED", row["source_id"], row["filename"])
    write_json(inv_p, new_inv)
    ov_p.write_text(yaml.safe_dump(ov, allow_unicode=True, sort_keys=False), encoding="utf-8")


if __name__ == "__main__":
    main("--apply" in sys.argv)
