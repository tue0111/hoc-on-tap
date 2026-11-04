# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))

from admission.engine import baseline_repeat_only, baseline_store_all, decide_admission

CASES = Path(r"D:\Hoc\_learning_system\evals\admission_cases.jsonl")
LONG = Path(r"D:\Hoc\_learning_system\evals\admission_longitudinal.jsonl")
NAT = Path(r"D:\Hoc\_learning_system\evals\admission_naturalistic.jsonl")
OUT = Path(r"D:\Hoc\_learning_system\reports\admission_benchmark_raw.json")


def load(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def eval_one(case, mode="C"):
    cand = case["candidate"]
    prior = case.get("prior") or []
    mates = case.get("cluster_mates") or []
    if mode == "A":
        pred = baseline_store_all(cand, prior=prior, cluster_mates=mates)
    elif mode == "B":
        pred = baseline_repeat_only(cand, prior=prior, cluster_mates=mates)
    else:
        pred = decide_admission(cand, prior=prior, cluster_mates=mates)
    gold = case["gold"]
    ok = pred.get("decision") == gold.get("decision")
    if gold.get("reason_contains") and gold["reason_contains"] not in (pred.get("reason_codes") or []):
        ok = False
    if gold.get("must_not_admit") and pred.get("decision") == "ADMIT":
        ok = False
    if gold.get("expect_contradiction") and not pred.get("contradictions"):
        ok = False
    false_adm = gold.get("must_not_admit") and pred.get("decision") == "ADMIT"
    one_off_false = case.get("category") == "one_off" and pred.get("decision") == "ADMIT"
    self_false = case.get("category") == "self_report" and pred.get("decision") == "ADMIT"
    hint_false = case.get("category") == "hinted" and pred.get("decision") == "ADMIT"
    dup_adm = case.get("category") == "duplicate" and pred.get("decision") == "ADMIT"
    prov = True
    if pred.get("decision") == "ADMIT":
        prov = bool(cand.get("source_session_id") or cand.get("diagnostic_result_ref"))
    return {
        "id": case["id"],
        "category": case.get("category"),
        "mode": mode,
        "passed": ok and not (pred.get("decision") == "ADMIT" and not prov),
        "pred": pred.get("decision"),
        "gold": gold.get("decision"),
        "reasons": pred.get("reason_codes"),
        "false_admit": false_adm,
        "one_off_false": one_off_false,
        "self_false": self_false,
        "hint_false": hint_false,
        "dup_inflate": dup_adm,
        "contradiction_kept": bool(pred.get("contradictions")) if gold.get("expect_contradiction") else None,
        "provenance_ok": prov,
        "dimension": pred.get("dimension") or cand.get("dimension"),
        "positive": cand.get("outcome") == "CORRECT" and pred.get("decision") == "ADMIT",
        "negative": cand.get("outcome") == "INCORRECT" and pred.get("decision") == "ADMIT",
    }


def summarize(rows):
    n = len(rows)
    admit_g = [r for r in rows if r["gold"] == "ADMIT"]
    hold_g = [r for r in rows if r["gold"] == "HOLD"]
    rep = [r for r in rows if r["category"] == "repeated_independent"]
    pos = [r for r in rows if r["category"] == "independent_success"]
    contra = [r for r in rows if r["contradiction_kept"] is not None]
    return {
        "n": n,
        "pass": sum(1 for r in rows if r["passed"]),
        "pass_rate": round(sum(1 for r in rows if r["passed"]) / n, 4) if n else 0,
        "admission_precision": round(
            sum(1 for r in rows if r["pred"] == "ADMIT" and r["gold"] == "ADMIT") / max(1, sum(1 for r in rows if r["pred"] == "ADMIT")),
            4,
        ),
        "admission_recall": round(sum(1 for r in admit_g if r["pred"] == "ADMIT") / len(admit_g), 4) if admit_g else 1.0,
        "false_admission_rate": round(sum(1 for r in rows if r["false_admit"] or (r["pred"] == "ADMIT" and r["gold"] != "ADMIT")) / n, 4) if n else 0,
        "one_off_false_admission_rate": round(sum(1 for r in rows if r["one_off_false"]) / max(1, sum(1 for r in rows if r["category"] == "one_off")), 4),
        "self_report_false_admission_rate": round(sum(1 for r in rows if r["self_false"]) / max(1, sum(1 for r in rows if r["category"] == "self_report")), 4),
        "hint_contaminated_false_admission_rate": round(sum(1 for r in rows if r["hint_false"]) / max(1, sum(1 for r in rows if r["category"] == "hinted")), 4),
        "duplicate_inflation_rate": round(sum(1 for r in rows if r["dup_inflate"]) / max(1, sum(1 for r in rows if r["category"] == "duplicate")), 4),
        "repeated_independent_recall": round(sum(1 for r in rep if r["pred"] == "ADMIT") / len(rep), 4) if rep else None,
        "positive_evidence_recall": round(sum(1 for r in pos if r["pred"] == "ADMIT") / len(pos), 4) if pos else None,
        "contradiction_preservation_rate": round(sum(1 for r in contra if r["contradiction_kept"]) / len(contra), 4) if contra else None,
        "hold_appropriateness": round(sum(1 for r in hold_g if r["pred"] == "HOLD") / len(hold_g), 4) if hold_g else None,
        "provenance_completeness": round(sum(1 for r in rows if r["provenance_ok"]) / n, 4) if n else 0,
        "admitted_positive": sum(1 for r in rows if r["positive"]),
        "admitted_negative": sum(1 for r in rows if r["negative"]),
        "fail_classes": dict(Counter(f"{r['category']}:{r['pred']}/{r['gold']}" for r in rows if not r["passed"])),
    }


def eval_long(seq):
    prior = []
    step_rows = []
    for i, step in enumerate(seq["steps"]):
        case = {"id": f"{seq['id']}-s{i+1}", "category": seq["category"], "candidate": step["candidate"], "prior": list(prior), "cluster_mates": [], "gold": step["gold"]}
        r = eval_one(case, "C")
        step_rows.append(r)
        if r["pred"] in {"ADMIT", "HOLD"}:
            prior.append(step["candidate"])
    return {"id": seq["id"], "category": seq["category"], "passed": all(x["passed"] for x in step_rows), "steps": step_rows}


def main():
    cases = load(CASES)
    print("CASES", len(cases), flush=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "metrics": {}, "rows": {}}
    for mode in ("A", "B", "C"):
        rows = [eval_one(c, mode) for c in cases]
        m = summarize(rows)
        by = defaultdict(lambda: {"n": 0, "pass": 0})
        for r in rows:
            by[r["category"]]["n"] += 1
            by[r["category"]]["pass"] += int(r["passed"])
        m["by_category"] = {k: {**v, "rate": round(v["pass"] / v["n"], 4)} for k, v in by.items()}
        payload["metrics"][mode] = m
        payload["rows"][mode] = rows
        print(mode, json.dumps(m, ensure_ascii=False), flush=True)

    longs = load(LONG)
    lrows = [eval_long(s) for s in longs]
    payload["longitudinal"] = {
        "n": len(lrows),
        "pass": sum(1 for r in lrows if r["passed"]),
        "pass_rate": round(sum(1 for r in lrows if r["passed"]) / len(lrows), 4),
        "by_category": dict(Counter(r["category"] for r in lrows if r["passed"])),
        "fail": [r["id"] for r in lrows if not r["passed"]],
    }
    print("LONG", json.dumps(payload["longitudinal"], ensure_ascii=False), flush=True)

    nats = load(NAT)
    nrows = [eval_one(c, "C") for c in nats]
    payload["naturalistic"] = {
        "n": len(nrows),
        "pass": sum(1 for r in nrows if r["passed"]),
        "pass_rate": round(sum(1 for r in nrows if r["passed"]) / len(nrows), 4),
        "false_admission_rate": round(sum(1 for r in nrows if r["pred"] == "ADMIT") / len(nrows), 4),
        "hold_or_reject_rate": round(sum(1 for r in nrows if r["pred"] in {"HOLD", "REJECT"}) / len(nrows), 4),
        "self_report_admits": sum(1 for r in nrows if r["self_false"]),
    }
    print("NAT", json.dumps(payload["naturalistic"], ensure_ascii=False), flush=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
