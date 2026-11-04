# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mastery.baselines import baseline_latest, baseline_majority, baseline_net, system_d
from mastery.estimator import DIM_KEYS, recompute
from mastery.transitions import diff_transitions

CASES = (_SYS / "evals" / "state_cases.jsonl")
LONG = (_SYS / "evals" / "state_longitudinal.jsonl")
NAT = (_SYS / "evals" / "state_naturalistic.jsonl")
OUT = (_SYS / "reports" / "learner_state_benchmark_raw.json")


def load(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def dim_state(snap, concept, dim):
    c = (snap.get("concepts") or {}).get(concept)
    if not c:
        return "INSUFFICIENT_EVIDENCE", None
    st = (c.get("dimensions") or {}).get(DIM_KEYS[dim.upper()]) or {}
    return st.get("state") or "INSUFFICIENT_EVIDENCE", st


def eval_case(case, mode="D"):
    gold = case["gold"]
    concept = gold["concept_id"]
    dim = gold["dimension"]
    ev = case.get("evidence") or []
    if mode == "A":
        pred = baseline_latest(ev).get("state")
        st = None
        snap = recompute(ev)
    elif mode == "B":
        pred = baseline_majority(ev).get("state")
        st = None
        snap = recompute(ev)
    elif mode == "C":
        pred = baseline_net(ev).get("state")
        st = None
        snap = recompute(ev)
    else:
        snap = recompute(ev)
        pred, st = dim_state(snap, concept, dim)
    gold_s = gold["state"]
    ok = pred == gold_s
    leak_dim = False
    if gold.get("other_dims_insufficient") and mode == "D":
        c = (snap.get("concepts") or {}).get(concept) or {}
        for k, v in (c.get("dimensions") or {}).items():
            if k != DIM_KEYS[dim.upper()] and v.get("state") not in {None, "INSUFFICIENT_EVIDENCE"}:
                leak_dim = True
    leak_con = False
    if gold.get("no_other_concepts") and mode == "D":
        keys = set((snap.get("concepts") or {}).keys())
        leak_con = bool(keys - {concept})
    false_sup = pred == "SUPPORTED" and gold_s != "SUPPORTED"
    false_con = pred == "CONCERN" and gold_s != "CONCERN"
    absence_fail = pred in {"CONCERN", "TENTATIVE_CONCERN"} and gold_s == "INSUFFICIENT_EVIDENCE"
    hist = True
    if gold_s in {"SUPPORTED", "RECOVERY_SIGNAL"} and case.get("category") in {"recovery_completed", "recovery_signal"} and mode == "D" and st:
        hist = len(st.get("negative_evidence_refs") or []) >= 2
    snap2 = recompute(ev)
    recompute_eq = json.dumps(snap.get("concepts"), sort_keys=True) == json.dumps(snap2.get("concepts"), sort_keys=True)
    forbidden = any(k in snap for k in ("overall_mastery", "learner_score", "accounting_mastery_percent"))
    prov = True
    if mode == "D" and st and pred != "INSUFFICIENT_EVIDENCE":
        prov = bool((st.get("positive_evidence_refs") or []) or (st.get("negative_evidence_refs") or []))
    fail = None
    if leak_dim:
        fail = "DIMENSION_LEAKAGE"
    elif leak_con:
        fail = "CONCEPT_LEAKAGE"
    elif absence_fail:
        fail = "ABSENCE_EQUALS_FAILURE"
    elif false_sup:
        fail = "FALSE_SUPPORTED"
    elif false_con:
        fail = "FALSE_CONCERN"
    elif not hist:
        fail = "HISTORY_ERASURE"
    elif not recompute_eq:
        fail = "STATE_NOT_RECOMPUTABLE"
    elif not ok:
        fail = "wrong_state"
    return {
        "id": case["id"],
        "category": case.get("category"),
        "mode": mode,
        "passed": fail is None,
        "fail_class": fail,
        "pred": pred,
        "gold": gold_s,
        "false_supported": false_sup,
        "false_concern": false_con,
        "dim_leak": leak_dim,
        "concept_leak": leak_con,
        "history_ok": hist,
        "recompute_eq": recompute_eq,
        "provenance_ok": prov,
        "forbidden": forbidden,
        "invalid_inputs": (snap.get("invalid_input_count") or 0) if mode == "D" else 0,
    }


def summarize(rows):
    n = len(rows)
    ins = [r for r in rows if r["gold"] == "INSUFFICIENT_EVIDENCE"]
    rec = [r for r in rows if r["category"] in {"recovery_signal"}]
    rec_ok = sum(1 for r in rec if r["pred"] == "RECOVERY_SIGNAL")
    return {
        "n": n,
        "pass": sum(1 for r in rows if r["passed"]),
        "pass_rate": round(sum(1 for r in rows if r["passed"]) / n, 4) if n else 0,
        "state_classification": round(sum(1 for r in rows if r["pred"] == r["gold"]) / n, 4) if n else 0,
        "false_supported_rate": round(sum(1 for r in rows if r["false_supported"]) / n, 4) if n else 0,
        "false_concern_rate": round(sum(1 for r in rows if r["false_concern"]) / n, 4) if n else 0,
        "insufficient_accuracy": round(sum(1 for r in ins if r["pred"] == "INSUFFICIENT_EVIDENCE") / len(ins), 4) if ins else 1.0,
        "dimension_leakage": round(sum(1 for r in rows if r["dim_leak"]) / n, 4) if n else 0,
        "cross_concept_leakage": round(sum(1 for r in rows if r["concept_leak"]) / n, 4) if n else 0,
        "recovery_signal_accuracy": round(rec_ok / len(rec), 4) if rec else None,
        "history_preservation": round(sum(1 for r in rows if r["history_ok"]) / n, 4) if n else 0,
        "full_recompute_equivalence": round(sum(1 for r in rows if r["recompute_eq"]) / n, 4) if n else 0,
        "provenance_completeness": round(sum(1 for r in rows if r["provenance_ok"]) / n, 4) if n else 0,
        "fail_classes": dict(Counter(r["fail_class"] for r in rows if r["fail_class"])),
    }


def eval_long(seq):
    acc = []
    prev = None
    step_ok = []
    trans_ok = []
    for i, step in enumerate(seq["steps"]):
        acc.extend(step.get("add") or [])
        snap = recompute(acc)
        if "gold_by_dim" in step:
            ok = True
            for d, g in step["gold_by_dim"].items():
                pred, _ = dim_state(snap, seq["concept_id"], d)
                if pred != g:
                    ok = False
            step_ok.append(ok)
        else:
            pred, _ = dim_state(snap, seq["concept_id"], seq["dimension"])
            step_ok.append(pred == step["gold"])
            if prev is not None and i > 0:
                tr = diff_transitions(prev, snap)
                expected_change = prev_pred != step["gold"] if False else True
            prev_pred = dim_state(snap, seq["concept_id"], seq.get("dimension") or "APPLICATION")[0]
        prev = snap
        trans_ok.append(True)
    return {"id": seq["id"], "category": seq["category"], "passed": all(step_ok), "steps_ok": step_ok}


def main():
    cases = load(CASES)
    print("CASES", len(cases), flush=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "metrics": {}, "rows": {}}
    for mode in ("A", "B", "C", "D"):
        rows = [eval_case(c, mode) for c in cases]
        m = summarize(rows)
        by = defaultdict(lambda: {"n": 0, "pass": 0})
        for r in rows:
            by[r["category"]]["n"] += 1
            by[r["category"]]["pass"] += int(r["passed"])
        m["by_category"] = {k: {**v, "rate": round(v["pass"] / v["n"], 4)} for k, v in by.items()}
        payload["metrics"][mode] = m
        if mode == "D":
            payload["rows"]["D"] = rows
        print(mode, json.dumps(m, ensure_ascii=False), flush=True)

    longs = load(LONG)
    lrows = [eval_long(s) for s in longs]
    payload["longitudinal"] = {
        "n": len(lrows),
        "pass": sum(1 for r in lrows if r["passed"]),
        "pass_rate": round(sum(1 for r in lrows if r["passed"]) / len(lrows), 4),
        "fail": [r["id"] for r in lrows if not r["passed"]],
        "by_category": dict(Counter(r["category"] for r in lrows if r["passed"])),
    }
    print("LONG", json.dumps(payload["longitudinal"], ensure_ascii=False), flush=True)

    nats = load(NAT)
    nrows = [eval_case(c, "D") for c in nats]
    payload["naturalistic"] = summarize(nrows)
    print("NAT", json.dumps(payload["naturalistic"], ensure_ascii=False), flush=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
