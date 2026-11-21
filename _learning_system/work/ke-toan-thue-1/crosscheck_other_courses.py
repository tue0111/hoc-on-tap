# -*- coding: utf-8 -*-
"""Informational, writes only work/ke-toan-thue-1/crosscheck.json: does making ke-toan-thue-1
retrieval-tier (in memory) change any row of the other retrieval courses' frozen evals?"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from retrieval import courses as C
import v3_eval_course as E
rows = []
for c in C.load_registry()["courses"]:
    if c["tier"] == "retrieval" and c["id"] not in C.PSEUDO:
        p = ROOT / "evals" / "v3" / f"{c['id']}_retrieval.jsonl"
        if p.exists(): rows += [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
key = lambda x: (x["pass"], x["coverage"], tuple(x["top_sources"]), tuple(x["top_chapters"]))
before = {r["id"]: E.run_row(r) for r in rows}
for c in C.load_registry()["courses"]:
    if c["id"] == "ke-toan-thue-1": c["tier"] = "retrieval"
after = {r["id"]: E.run_row(r) for r in rows}
diff = [{"id": i, "before": [before[i]["pass"], before[i]["coverage"], before[i]["unknowns"]],
         "after": [after[i]["pass"], after[i]["coverage"], after[i]["unknowns"]]}
        for i in before if key(before[i]) != key(after[i]) or before[i]["unknowns"] != after[i]["unknowns"]]
out = {"rows_checked": len(rows), "diff_count": len(diff), "diff": diff}
(Path(__file__).parent / "crosscheck.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False)[:3000])
