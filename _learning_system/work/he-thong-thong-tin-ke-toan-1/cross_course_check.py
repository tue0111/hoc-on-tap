# -*- coding: utf-8 -*-
"""Read-only impact check for Phase C: re-run every frozen eval of the courses that are
`retrieval` in the registry, first with this course at its registry tier (catalog), then with
this course set to `retrieval` in memory. Reports row-level differences (pass / coverage / top-5).
Writes only work/he-thong-thong-tin-ke-toan-1/cross_course_check.json.
"""
import json, sys
from pathlib import Path

SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
from retrieval import courses as C  # noqa: E402
from scripts.v3_eval_course import run_row  # noqa: E402

CID = "he-thong-thong-tin-ke-toan-1"
targets = [c["id"] for c in C.load_registry()["courses"] if c.get("tier") == "retrieval" and c["id"] not in C.PSEUDO]


def run_all():
    out = {}
    for cid in targets:
        f = SYS / "evals" / "v3" / f"{cid}_retrieval.jsonl"
        if not f.exists():
            continue
        rows = [json.loads(l) for l in f.open(encoding="utf-8") if l.strip()]
        out[cid] = {r["id"]: {k: v for k, v in run_row(r).items() if k in ("pass", "coverage", "top_sources", "unknowns")} for r in rows}
    return out


before = run_all()
C.get_course(CID)["tier"] = "retrieval"
after = run_all()
diff = []
for cid in before:
    for rid, b in before[cid].items():
        a = after[cid][rid]
        if (a["pass"], a["coverage"], a["top_sources"]) != (b["pass"], b["coverage"], b["top_sources"]):
            diff.append({"course": cid, "id": rid, "before": b, "after": a})
res = {"courses_checked": list(before), "rows_checked": sum(len(v) for v in before.values()), "diffs": diff,
       "pass_flips": [d for d in diff if d["before"]["pass"] != d["after"]["pass"]]}
(SYS / "work" / CID / "cross_course_check.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
print("courses", len(before), "rows", res["rows_checked"], "diffs", len(diff), "pass_flips", len(res["pass_flips"]))
for d in diff: print(d["course"], d["id"], d["before"]["pass"], "->", d["after"]["pass"], d["before"]["coverage"], "->", d["after"]["coverage"], d["after"]["unknowns"])
