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

from diagnostic.engine import baseline_correction, diagnose

CASES = (_SYS / "evals" / "diagnostic_cases.jsonl")
OUT = (_SYS / "reports" / "diagnostic_benchmark_raw.json")


def load_cases():
    rows = []
    with CASES.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def fail_class(gold, pred) -> str | None:
    if gold.get("status") == "INCONCLUSIVE":
        if pred.get("status") != "INCONCLUSIVE":
            return "insufficient_evidence_not_detected"
        return None
    if pred.get("status") == "INCONCLUSIVE" and gold.get("error_type") != "unknown":
        return "premature_diagnosis" if False else "unsupported_diagnosis"
    rc = (pred.get("root_cause") or {})
    if gold.get("target_concept"):
        ids = pred.get("concept_ids") or []
        if pred.get("target_concept") != gold["target_concept"] and gold["target_concept"] not in ids:
            return "wrong_target_concept"
    if gold.get("prerequisite_gap") and not rc.get("prerequisite_gap"):
        return "missed_prerequisite_gap"
    if (not gold.get("prerequisite_gap")) and rc.get("prerequisite_gap"):
        return "false_prerequisite_gap"
    if gold.get("error_type") and pred.get("primary_error_code") != gold["error_type"]:
        if gold["error_type"] in {"classification_error", "prerequisite_gap", "conceptual_failure"} and pred.get(
            "primary_error_code"
        ) == "journal_entry_error":
            return "surface_symptom_only"
        return "wrong_root_cause"
    return None


def eval_one(case, mode: str) -> dict:
    req = case["input"]
    gold = case["gold"]
    t0 = time.perf_counter()
    if mode == "A":
        pred = baseline_correction(req)
    elif mode == "B":
        pred = diagnose(req, followup_response=None, allow_question=False)
    else:
        fu = None
        if case.get("multiturn", {}).get("enabled"):
            fu = case["multiturn"].get("followup_response")
        pred = diagnose(req, followup_response=fu, allow_question=True)
        # if still needs followup and we have one, apply
        if pred.get("needs_followup") and fu:
            pred = diagnose(req, followup_response=fu, allow_question=True)
    dt = time.perf_counter() - t0
    rc = pred.get("root_cause") or {}
    fc = fail_class(gold, pred)
    target_ok = True
    if gold.get("target_concept"):
        target_ok = pred.get("target_concept") == gold["target_concept"] or gold["target_concept"] in (
            pred.get("concept_ids") or []
        )
    root_ok = True
    if gold.get("status") == "INCONCLUSIVE":
        root_ok = pred.get("status") == "INCONCLUSIVE"
    else:
        root_ok = pred.get("primary_error_code") == gold.get("error_type")
    prereq_pred = bool(rc.get("prerequisite_gap"))
    prereq_gold = bool(gold.get("prerequisite_gap"))
    grounded = pred.get("evidence_status") in {"OBSERVED", "UNKNOWN"} and (
        pred.get("curriculum_sources") or pred.get("status") == "INCONCLUSIVE"
    )
    courses = {s.get("course_id") for s in (pred.get("curriculum_sources") or []) if s.get("course_id")}
    allowed = {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1", None}
    contamin = bool(courses - allowed)
    turns = 1 + (1 if pred.get("diagnostic_questions") else 0)
    return {
        "id": case["id"],
        "category": case["category"],
        "mode": mode,
        "passed": fc is None and target_ok and (root_ok or gold.get("status") == "INCONCLUSIVE"),
        "fail_class": fc,
        "target_ok": target_ok,
        "root_ok": root_ok,
        "prereq_pred": prereq_pred,
        "prereq_gold": prereq_gold,
        "status": pred.get("status"),
        "primary": pred.get("primary_error_code"),
        "pred_target": pred.get("target_concept"),
        "gold_target": gold.get("target_concept"),
        "gold_error": gold.get("error_type"),
        "grounded": grounded,
        "contamination": contamin,
        "turns": turns,
        "latency_s": round(dt, 4),
        "confidence": pred.get("confidence"),
        "question_asked": [x.get("text") for x in (pred.get("diagnostic_questions") or [])],
    }


def summarize(rows):
    n = len(rows)
    tgt_n = sum(1 for r in rows if r["gold_target"])
    tgt_ok = sum(1 for r in rows if r["gold_target"] and r["target_ok"])
    root_n = sum(1 for r in rows if r["gold_error"] != "unknown")
    root_ok = sum(1 for r in rows if r["gold_error"] != "unknown" and r["root_ok"])
    gp = [r for r in rows if r["prereq_pred"]]
    prec = (sum(1 for r in gp if r["prereq_gold"]) / len(gp)) if gp else 1.0
    gg = [r for r in rows if r["prereq_gold"]]
    rec = (sum(1 for r in gg if r["prereq_pred"]) / len(gg)) if gg else 1.0
    false_gap = sum(1 for r in rows if r["prereq_pred"] and not r["prereq_gold"]) / n if n else 0
    symptom = sum(1 for r in rows if r["fail_class"] == "surface_symptom_only") / n if n else 0
    grounded = sum(1 for r in rows if r["grounded"]) / n if n else 0
    insc = [r for r in rows if r["gold_error"] == "unknown"]
    insc_ok = (sum(1 for r in insc if r["status"] == "INCONCLUSIVE") / len(insc)) if insc else 1.0
    cont = sum(1 for r in rows if r["contamination"]) / n if n else 0
    premature = sum(1 for r in rows if r["fail_class"] == "premature_diagnosis") / n if n else 0
    mt = [r for r in rows if r["turns"] >= 2]
    asked = [r for r in rows if r.get("question_asked")]
    return {
        "n": n,
        "pass": sum(1 for r in rows if r["passed"]),
        "pass_rate": round(sum(1 for r in rows if r["passed"]) / n, 4) if n else 0,
        "n_with_diagnostic_question": len(asked),
        "target_concept_accuracy": round(tgt_ok / tgt_n, 4) if tgt_n else None,
        "root_cause_accuracy": round(root_ok / root_n, 4) if root_n else None,
        "prerequisite_gap_precision": round(prec, 4),
        "prerequisite_gap_recall": round(rec, 4),
        "false_prerequisite_gap_rate": round(false_gap, 4),
        "symptom_as_root_cause_rate": round(symptom, 4),
        "evidence_grounded_rate": round(grounded, 4),
        "inconclusive_detection": round(insc_ok, 4),
        "wrong_course_contamination": round(cont, 4),
        "premature_diagnosis_rate": round(premature, 4),
        "avg_turns": round(sum(r["turns"] for r in rows) / n, 3) if n else None,
        "fail_classes": dict(Counter(r["fail_class"] for r in rows if r["fail_class"])),
        "by_category": {},
        "latency_mean_s": round(sum(r["latency_s"] for r in rows) / n, 4) if n else None,
    }


def main():
    cases = load_cases()
    print("CASES", len(cases), flush=True)
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
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_cases": len(cases),
        "metrics": metrics,
        "rows": {k: v for k, v in all_rows.items()},
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
