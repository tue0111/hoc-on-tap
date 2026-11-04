# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from diagnostic.engine import diagnose
from decision.engine import baseline_review_topic, baseline_static_lookup, decide

CASES = (_SYS / "evals" / "decision_cases.jsonl")
NAT = (_SYS / "evals" / "decision_naturalistic_shadow.jsonl")
OUT = (_SYS / "reports" / "decision_benchmark_raw.json")
OUT_NAT = (_SYS / "reports" / "decision_naturalistic_raw.json")

TEACHING = {
    "RECALL_REFRESH",
    "MECHANISM_EXPLANATION",
    "CONTRASTIVE_EXAMPLE",
    "WORKED_EXAMPLE",
    "PROCEDURE_REHEARSAL",
    "APPLICATION_PRACTICE",
    "PREREQUISITE_MICRO_BACKFILL",
    "TERMINOLOGY_CLARIFICATION",
    "MECHANICAL_CORRECTION",
}


def load(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def get_diag(case):
    inp = case["input"]
    if case.get("input_mode") == "injected" and inp.get("diagnostic_result"):
        return inp["diagnostic_result"]
    ctx = inp.get("course_context") or inp.get("session_context") or {}
    fu = inp.get("followup_response")
    return diagnose(
        {
            "question": inp.get("question") or "",
            "learner_response": inp.get("learner_response") or "",
            "work_shown": inp.get("work_shown") or "",
            "course_context": ctx,
            "followup_response": fu,
        },
        followup_response=fu,
        allow_question=True,
    )


def fail_class(gold, pred, diag) -> str | None:
    act = (pred.get("decision") or {}).get("action_type")
    gap = pred.get("primary_gap") or {}
    if gold.get("must_not_backfill") and act == "PREREQUISITE_MICRO_BACKFILL":
        return "FALSE_PREREQUISITE_BACKFILL"
    if gold.get("action_type") == "VERIFY_MORE" and act in TEACHING and (pred.get("confidence_band") == "HIGH"):
        return "INTERVENTION_WITH_UNCONFIRMED_DIAGNOSIS"
    if gold.get("action_type") == "NO_INTERVENTION" and act in TEACHING:
        return "UNNECESSARY_INTERVENTION"
    if gold.get("action_type") == "MECHANICAL_CORRECTION" and act in {"MECHANISM_EXPLANATION", "PREREQUISITE_MICRO_BACKFILL"}:
        return "BROAD_REVIEW_WHEN_MICRO_FIX_SUFFICIENT"
    if gold.get("error_type") in {"classification_error", "prerequisite_gap", "conceptual_failure"} and act == "WORKED_EXAMPLE" and gold.get("action_type") != "WORKED_EXAMPLE":
        return "TREATING_SYMPTOM_NOT_CAUSE"
    if gold.get("action_type") and act != gold["action_type"]:
        if gold.get("allow_verify_more") and act == "VERIFY_MORE":
            return None
        return "wrong_action"
    if gold.get("is_prerequisite") and not gap.get("is_prerequisite"):
        return "missed_prerequisite_backfill"
    if (not gold.get("is_prerequisite")) and gap.get("is_prerequisite"):
        return "FALSE_PREREQUISITE_BACKFILL"
    if gold.get("concept_id") and gap.get("concept_id") not in {gold["concept_id"], gold.get("prerequisite_concept_id")}:
        if gold.get("action_type") in {"VERIFY_MORE", "NO_INTERVENTION"}:
            return None
        return "wrong_primary_gap"
    return None


def eval_one(case, mode: str) -> dict:
    gold = case["gold"]
    t0 = time.perf_counter()
    diag = get_diag(case)
    if mode == "A":
        pred = baseline_review_topic(diag)
    elif mode == "B":
        pred = baseline_static_lookup(diag)
    else:
        req = {
            "diagnostic_result": diag,
            "session_context": case["input"].get("session_context") or case["input"].get("course_context") or {},
            "constraints": case["input"].get("constraints") or {"max_actions": 1, "allow_prerequisite_backfill": True},
        }
        pred = decide(req)
    dt = time.perf_counter() - t0
    fc = fail_class(gold, pred, diag)
    act = (pred.get("decision") or {}).get("action_type")
    gap = pred.get("primary_gap") or {}
    action_ok = act == gold.get("action_type") or (gold.get("allow_verify_more") and act == "VERIFY_MORE")
    gap_ok = True
    if gold.get("concept_id") and gold.get("action_type") not in {"VERIFY_MORE", "NO_INTERVENTION"}:
        gap_ok = gap.get("concept_id") in {gold.get("concept_id"), gold.get("prerequisite_concept_id")} or gap.get(
            "error_type"
        ) == gold.get("error_type")
    prereq_pred = bool(gap.get("is_prerequisite") or act == "PREREQUISITE_MICRO_BACKFILL")
    over = False
    if gold.get("action_type") in {"MECHANICAL_CORRECTION", "RECALL_REFRESH", "TERMINOLOGY_CLARIFICATION", "NO_INTERVENTION"} and act in {
        "MECHANISM_EXPLANATION",
        "PREREQUISITE_MICRO_BACKFILL",
        "PROCEDURE_REHEARSAL",
        "APPLICATION_PRACTICE",
    }:
        over = True
    if gold.get("must_not_backfill") and prereq_pred:
        over = True
    if (pred.get("decision") or {}).get("depth") == "NORMAL" and gold.get("depth") in {"MICRO", "SHORT"}:
        over = True
    under = gold.get("action_type") in TEACHING and act in {"VERIFY_MORE", "NO_INTERVENTION"} and not gold.get("allow_verify_more")
    grounded = bool(pred.get("grounded")) or act in {"VERIFY_MORE", "NO_INTERVENTION"}
    course = (pred.get("scope") or {}).get("course")
    contamin = course not in {None, "nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"}
    return {
        "id": case["id"],
        "category": case.get("category"),
        "mode": mode,
        "passed": fc is None and action_ok,
        "fail_class": fc,
        "action_ok": action_ok,
        "gap_ok": gap_ok,
        "pred_action": act,
        "gold_action": gold.get("action_type"),
        "pred_error": gap.get("error_type"),
        "gold_error": gold.get("error_type"),
        "prereq_pred": prereq_pred,
        "prereq_gold": bool(gold.get("is_prerequisite")),
        "over_treatment": over,
        "under_treatment": under,
        "grounded": grounded,
        "contamination": contamin,
        "status": pred.get("status"),
        "confidence": pred.get("confidence_band"),
        "diag_status": diag.get("status"),
        "diag_primary": diag.get("primary_error_code"),
        "diag_prereq": bool((diag.get("root_cause") or {}).get("prerequisite_gap")),
        "latency_s": round(dt, 4),
    }


def summarize(rows):
    n = len(rows)
    gp = [r for r in rows if r["prereq_pred"]]
    prec = (sum(1 for r in gp if r["prereq_gold"]) / len(gp)) if gp else 1.0
    gg = [r for r in rows if r["prereq_gold"]]
    rec = (sum(1 for r in gg if r["prereq_pred"]) / len(gg)) if gg else 1.0
    false_bf = sum(1 for r in rows if r["prereq_pred"] and not r["prereq_gold"]) / n if n else 0
    verify_g = [r for r in rows if r["gold_action"] == "VERIFY_MORE"]
    verify_ok = (sum(1 for r in verify_g if r["pred_action"] == "VERIFY_MORE") / len(verify_g)) if verify_g else 1.0
    none_g = [r for r in rows if r["gold_action"] == "NO_INTERVENTION"]
    none_ok = (sum(1 for r in none_g if r["pred_action"] == "NO_INTERVENTION") / len(none_g)) if none_g else 1.0
    gap_n = sum(1 for r in rows if r["gold_error"] not in {None, "unknown", "none"})
    gap_ok = sum(1 for r in rows if r["gold_error"] not in {None, "unknown", "none"} and r["gap_ok"])
    return {
        "n": n,
        "pass": sum(1 for r in rows if r["passed"]),
        "pass_rate": round(sum(1 for r in rows if r["passed"]) / n, 4) if n else 0,
        "primary_gap_accuracy": round(gap_ok / gap_n, 4) if gap_n else None,
        "action_accuracy": round(sum(1 for r in rows if r["action_ok"]) / n, 4) if n else 0,
        "prerequisite_backfill_precision": round(prec, 4),
        "prerequisite_backfill_recall": round(rec, 4),
        "false_prerequisite_backfill_rate": round(false_bf, 4),
        "over_treatment_rate": round(sum(1 for r in rows if r["over_treatment"]) / n, 4) if n else 0,
        "under_treatment_rate": round(sum(1 for r in rows if r["under_treatment"]) / n, 4) if n else 0,
        "verify_more_correctness": round(verify_ok, 4),
        "no_intervention_correctness": round(none_ok, 4),
        "decision_grounding_rate": round(sum(1 for r in rows if r["grounded"]) / n, 4) if n else 0,
        "wrong_course_intervention_rate": round(sum(1 for r in rows if r["contamination"]) / n, 4) if n else 0,
        "fail_classes": dict(Counter(r["fail_class"] for r in rows if r["fail_class"])),
        "latency_mean_s": round(sum(r["latency_s"] for r in rows) / n, 4) if n else None,
    }


def shadow_diag_metrics(rows):
    n = len(rows)
    diagnosed = sum(1 for r in rows if r["diag_status"] == "DIAGNOSED")
    inc = sum(1 for r in rows if r["diag_status"] == "INCONCLUSIVE")
    partial = sum(1 for r in rows if r["diag_status"] == "PARTIAL")
    false_prereq = sum(1 for r in rows if r["diag_prereq"] and not r["prereq_gold"])
    unsupported = sum(1 for r in rows if r["diag_status"] == "DIAGNOSED" and r["gold_action"] == "VERIFY_MORE" and r["confidence"] == "HIGH")
    return {
        "n": n,
        "diagnosis_rate": round(diagnosed / n, 4) if n else 0,
        "inconclusive_rate": round(inc / n, 4) if n else 0,
        "partial_rate": round(partial / n, 4) if n else 0,
        "false_prerequisite_gap_rate": round(false_prereq / n, 4) if n else 0,
        "unsupported_confident_decision_rate": round(unsupported / n, 4) if n else 0,
        "verify_more_rate": round(sum(1 for r in rows if r["pred_action"] == "VERIFY_MORE") / n, 4) if n else 0,
        "false_prerequisite_backfill_rate": round(sum(1 for r in rows if r["prereq_pred"] and not r["prereq_gold"]) / n, 4) if n else 0,
        "over_treatment_rate": round(sum(1 for r in rows if r["over_treatment"]) / n, 4) if n else 0,
        "action_accuracy_vs_gold": round(sum(1 for r in rows if r["action_ok"]) / n, 4) if n else 0,
        "fail_classes": dict(Counter(r["fail_class"] for r in rows if r["fail_class"])),
    }


def main():
    cases = load(CASES)
    print("CONTROLLED", len(cases), flush=True)
    all_rows = {}
    metrics = {}
    for mode in ("A", "B", "C"):
        print("MODE", mode, flush=True)
        rows = [eval_one(c, mode) for c in cases]
        all_rows[mode] = rows
        m = summarize(rows)
        by = defaultdict(lambda: {"n": 0, "pass": 0})
        for r in rows:
            by[r["category"]]["n"] += 1
            by[r["category"]]["pass"] += int(r["passed"])
        m["by_category"] = {k: {**v, "rate": round(v["pass"] / v["n"], 4)} for k, v in by.items()}
        metrics[mode] = m
        print(json.dumps(m, ensure_ascii=False), flush=True)

    nat = load(NAT)
    print("NATURALISTIC", len(nat), flush=True)
    nat_rows = [eval_one(c, "C") for c in nat]
    nat_m = shadow_diag_metrics(nat_rows)
    print("SHADOW", json.dumps(nat_m, ensure_ascii=False), flush=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_cases": len(cases),
        "metrics": metrics,
        "rows": {k: v for k, v in all_rows.items()},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_NAT.write_text(
        json.dumps({"generated_at": payload["generated_at"], "metrics": nat_m, "rows": nat_rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("WROTE", OUT)
    print("WROTE", OUT_NAT)


if __name__ == "__main__":
    main()
