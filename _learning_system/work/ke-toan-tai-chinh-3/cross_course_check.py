# Informational, writes only work/ke-toan-tai-chinh-3/cross_course_check.json.
# Re-runs every course eval that has a W6b-A reference (reports/v3/<X>_eval_w6bA.json) twice:
# (a) registry as on disk, (b) with ke-toan-tai-chinh-3 set to tier retrieval in memory.
# Differences between (a) and (b) are the effect of promoting KTTC3; differences between the
# reference and (a) come from other parallel W6b sessions' new indexes (rival coverage).
import json, sys
from pathlib import Path
SYS = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(SYS))
from retrieval import courses as C
from retrieval import partition as P
from retrieval import concepts as K
import scripts.v3_eval_course as E
CID = "ke-toan-tai-chinh-3"
refs = sorted((SYS / "reports" / "v3").glob("*_eval_w6bA.json"))

def run_all():
    out = {}
    for ref in refs:
        cid = ref.name.replace("_eval_w6bA.json", "")
        rows = [json.loads(l) for l in (SYS / "evals" / "v3" / f"{cid}_retrieval.jsonl").open(encoding="utf-8") if l.strip()]
        out[cid] = {r["id"]: (lambda x: {"pass": x["pass"], "coverage": x["coverage"], "top": x["top_sources"]})(E.run_row(r)) for r in rows}
    return out

def set_tier(t):
    for c in C.load_registry()["courses"]:
        if c["id"] == CID: c["tier"] = t
    P.clear_cache()

set_tier("catalog"); a = run_all()
set_tier("retrieval"); b = run_all()
report = {}
for ref in refs:
    cid = ref.name.replace("_eval_w6bA.json", "")
    w = {x["id"]: x for x in json.loads(ref.read_text(encoding="utf-8"))["results"]}
    diffs = []
    for rid in a[cid]:
        wa = w.get(rid, {})
        d = {}
        if wa and (wa.get("pass"), wa.get("coverage")) != (a[cid][rid]["pass"], a[cid][rid]["coverage"]): d["ref_vs_disk"] = [wa.get("pass"), wa.get("coverage"), a[cid][rid]["pass"], a[cid][rid]["coverage"]]
        if a[cid][rid] != b[cid][rid]: d["kttc3_effect"] = [a[cid][rid], b[cid][rid]]
        if d: diffs.append({"id": rid, **d})
    report[cid] = {"rows": len(a[cid]), "diffs": diffs}
    print(cid, len(a[cid]), "diffs", [(x["id"], list(x)[1:]) for x in diffs])
(SYS / "work" / CID / "cross_course_check.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
