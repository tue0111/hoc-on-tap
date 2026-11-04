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

from adaptive.controller import ingest, start, summary
from diagnostic.engine import diagnose
from decision.engine import decide

CASES = (_SYS / "evals" / "adaptive_sessions.jsonl")
ADV = (_SYS / "evals" / "adaptive_adversarial.jsonl")
OUT = (_SYS / "reports" / "adaptive_benchmark_raw.json")
OUT_ADV = (_SYS / "reports" / "adaptive_adversarial_raw.json")


def load(path):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def run_c(case):
    inp = case["input"]
    t0 = time.perf_counter()
    sess = start(
        {
            "question": inp["question"],
            "learner_response": inp.get("learner_response") or "",
            "work_shown": inp.get("work_shown") or "",
            "course_context": inp.get("course_context") or {},
        }
    )
    initial = {
        "error": (sess.get("current_diagnosis") or {}).get("primary_error_code"),
        "action": ((sess.get("current_decision") or {}).get("decision") or {}).get("action_type"),
        "status": sess.get("status"),
    }
    deltas = []
    for ev in inp.get("events") or []:
        deltas.append(ingest(sess, ev.get("content") or "", event_type=ev.get("event_type")))
    dt = time.perf_counter() - t0
    return sess, initial, deltas, dt


def run_a(case):
    inp = case["input"]
    sess = start(
        {
            "question": inp["question"],
            "learner_response": inp.get("learner_response") or "",
            "work_shown": inp.get("work_shown") or "",
            "course_context": inp.get("course_context") or {},
        }
    )
    return sess


def run_b(case):
    """Always rerun diagnose+decide from the latest utterance only."""
    inp = case["input"]
    ctx = inp.get("course_context") or {}
    latest = (inp.get("events") or [{}])[-1].get("content") if inp.get("events") else inp.get("learner_response")
    diag = diagnose(
        {
            "question": inp["question"],
            "learner_response": latest or "",
            "work_shown": latest or "",
            "course_context": ctx,
        },
        followup_response=latest,
        allow_question=True,
    )
    dec = decide({"diagnostic_result": diag, "session_context": ctx, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    return diag, dec


def score(case, sess, initial, deltas):
    gold = case["gold"]
    diag = sess.get("current_diagnosis") or {}
    dec = sess.get("current_decision") or {}
    rc = diag.get("root_cause") or {}
    action = (dec.get("decision") or {}).get("action_type")
    err = diag.get("primary_error_code")
    prereq = bool(rc.get("prerequisite_gap") and rc.get("prerequisite_confirmed") == "confirmed")
    resolved = sess.get("status") == "RESOLVED"
    kind = sess.get("resolution_kind")

    action_ok = action == gold.get("final_action")
    if gold.get("allow_inconclusive") and action in {"VERIFY_MORE", "NO_INTERVENTION"}:
        action_ok = True
    if gold.get("allow_inconclusive") and sess.get("status") in {"NEED_MORE_EVIDENCE", "ABORTED"}:
        action_ok = action_ok or True

    err_ok = True
    if gold.get("final_error_type") and gold.get("final_error_type") != "unknown":
        err_ok = err == gold["final_error_type"]
        if gold.get("allow_inconclusive") and err in {None, "unknown"}:
            err_ok = True
    elif gold.get("final_error_type") == "unknown":
        err_ok = err in {None, "unknown", "conceptual_failure"} and action in {"VERIFY_MORE"} or gold.get("allow_inconclusive")

    trans_ok = True
    if gold.get("expect_transition"):
        trans_ok = (err != initial.get("error")) or (action != initial.get("action"))
        if gold.get("allow_inconclusive") and action == "VERIFY_MORE":
            trans_ok = True

    false_prereq = prereq and gold.get("must_not_confirm_prereq")
    missed_prereq = gold.get("expect_prereq") and not prereq
    premature = bool(gold.get("must_not_resolve")) and resolved and kind == "LEARNING_GAP_RESOLVED"
    if gold.get("must_not_resolve") and resolved and any(
        (e.get("event_type") == "SELF_REPORT") or (e.get("content") or "").lower().find("hiểu rồi") >= 0
        for e in (sess.get("evidence_history") or [])
    ):
        premature = True

    lock = gold.get("expect_transition") and not gold.get("allow_inconclusive") and err == initial.get("error") and err != gold.get("final_error_type")
    over_upd = (not gold.get("expect_transition")) and (err != initial.get("error")) and gold.get("must_not_resolve")
    under_upd = gold.get("expect_transition") and gold.get("final_error_type") not in {None, "unknown"} and err != gold.get("final_error_type")

    loop = int(sess.get("discriminator_count") or 0) > 3
    high = (dec.get("confidence_band") == "HIGH" or diag.get("confidence") == "high") and gold.get("allow_inconclusive")
    self_ow = premature and any("hiểu rồi" in (e.get("content") or "").lower() for e in (sess.get("evidence_history") or []))

    od = False
    od_ok = None
    if gold.get("overdiagnosis_recovery"):
        od = initial.get("error") in {"conceptual_failure", "unknown", None} or initial.get("action") == "VERIFY_MORE"
        od_ok = bool(od) and err_ok and action_ok and not false_prereq

    fail = None
    if false_prereq:
        fail = "FALSE_PREREQUISITE_CONFIRMATION"
    elif premature:
        fail = "PREMATURE_RESOLUTION"
    elif loop:
        fail = "VERIFY_MORE_LOOP"
    elif self_ow:
        fail = "SELF_REPORT_OVERWEIGHT"
    elif lock:
        fail = "BELIEF_LOCK_IN"
    elif under_upd and not gold.get("allow_inconclusive"):
        fail = "UNDER_UPDATE"
    elif not action_ok:
        fail = "wrong_action"
    elif not err_ok and not gold.get("allow_inconclusive"):
        fail = "wrong_error"

    passed = fail is None
    return {
        "id": case["id"],
        "category": case.get("category"),
        "passed": passed,
        "fail_class": fail,
        "initial_error": initial.get("error"),
        "initial_action": initial.get("action"),
        "final_error": err,
        "final_action": action,
        "gold_error": gold.get("final_error_type"),
        "gold_action": gold.get("final_action"),
        "action_ok": action_ok,
        "error_ok": err_ok,
        "transition_ok": trans_ok,
        "prereq": prereq,
        "false_prereq": false_prereq,
        "missed_prereq": missed_prereq,
        "resolved": resolved,
        "resolution_kind": kind,
        "premature": premature,
        "lock_in": lock,
        "over_update": over_upd,
        "under_update": under_upd,
        "loop": loop,
        "unsupported_high": bool(high),
        "self_report_overweight": self_ow,
        "overdiagnosis_recovery_case": bool(gold.get("overdiagnosis_recovery")),
        "overdiagnosis_recovered": od_ok,
        "rediagnose_count": sess.get("rediagnose_count"),
        "redecide_count": sess.get("redecide_count"),
        "discriminator_count": sess.get("discriminator_count"),
        "n_events": len(sess.get("evidence_history") or []),
        "status": sess.get("status"),
        "persist": sess.get("persist_to_learner_state"),
    }


def summarize(rows):
    n = len(rows)
    od = [r for r in rows if r.get("overdiagnosis_recovery_case")]
    od_ok = sum(1 for r in od if r.get("overdiagnosis_recovered"))
    trans_n = sum(1 for r in rows if r.get("transition_ok") is not None)
    return {
        "n": n,
        "pass": sum(1 for r in rows if r["passed"]),
        "pass_rate": round(sum(1 for r in rows if r["passed"]) / n, 4) if n else 0,
        "diagnosis_transition_accuracy": round(sum(1 for r in rows if r["error_ok"]) / n, 4) if n else 0,
        "decision_transition_accuracy": round(sum(1 for r in rows if r["action_ok"]) / n, 4) if n else 0,
        "false_prerequisite_confirmation_rate": round(sum(1 for r in rows if r["false_prereq"]) / n, 4) if n else 0,
        "belief_lock_in_rate": round(sum(1 for r in rows if r["lock_in"]) / n, 4) if n else 0,
        "premature_resolution_rate": round(sum(1 for r in rows if r["premature"]) / n, 4) if n else 0,
        "unsupported_high_rate": round(sum(1 for r in rows if r["unsupported_high"]) / n, 4) if n else 0,
        "verify_more_loop_rate": round(sum(1 for r in rows if r["loop"]) / n, 4) if n else 0,
        "overdiagnosis_recovery_rate": round(od_ok / len(od), 4) if od else None,
        "over_update_rate": round(sum(1 for r in rows if r["over_update"]) / n, 4) if n else 0,
        "under_update_rate": round(sum(1 for r in rows if r["under_update"]) / n, 4) if n else 0,
        "avg_events": round(sum(r["n_events"] for r in rows) / n, 3) if n else None,
        "avg_rediagnose": round(sum(r["rediagnose_count"] or 0 for r in rows) / n, 3) if n else None,
        "fail_classes": dict(Counter(r["fail_class"] for r in rows if r["fail_class"])),
        "persist_any": any(r.get("persist") for r in rows),
    }


def main():
    cases = load(CASES)
    print("SESSIONS", len(cases), flush=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "n": len(cases), "metrics": {}, "rows": {}}
    # A
    rows_a = []
    for c in cases:
        sess = run_a(c)
        initial = {
            "error": (sess.get("current_diagnosis") or {}).get("primary_error_code"),
            "action": ((sess.get("current_decision") or {}).get("decision") or {}).get("action_type"),
        }
        # freeze: score as if no ingest
        fake = dict(sess)
        rows_a.append(score(c, fake, initial, []))
    payload["metrics"]["A"] = summarize(rows_a)
    payload["rows"]["A"] = rows_a
    print("A", json.dumps(payload["metrics"]["A"], ensure_ascii=False), flush=True)

    rows_b = []
    for c in cases:
        diag, dec = run_b(c)
        wrap = {
            "current_diagnosis": diag,
            "current_decision": dec,
            "status": "ACTIVE",
            "resolution_kind": None,
            "evidence_history": c["input"].get("events") or [],
            "rediagnose_count": len(c["input"].get("events") or []),
            "redecide_count": len(c["input"].get("events") or []),
            "discriminator_count": 0,
            "persist_to_learner_state": False,
        }
        initial = {"error": "conceptual_failure", "action": "VERIFY_MORE"}
        rows_b.append(score(c, wrap, initial, []))
    payload["metrics"]["B"] = summarize(rows_b)
    payload["rows"]["B"] = rows_b
    print("B", json.dumps(payload["metrics"]["B"], ensure_ascii=False), flush=True)

    rows_c = []
    for c in cases:
        sess, initial, deltas, dt = run_c(c)
        row = score(c, sess, initial, deltas)
        row["latency_s"] = round(dt, 4)
        rows_c.append(row)
    payload["metrics"]["C"] = summarize(rows_c)
    payload["rows"]["C"] = rows_c
    by = defaultdict(lambda: {"n": 0, "pass": 0})
    for r in rows_c:
        by[r["category"]]["n"] += 1
        by[r["category"]]["pass"] += int(r["passed"])
    payload["metrics"]["C"]["by_category"] = {k: {**v, "rate": round(v["pass"] / v["n"], 4)} for k, v in by.items()}
    print("C", json.dumps(payload["metrics"]["C"], ensure_ascii=False), flush=True)

    adv = load(ADV)
    adv_rows = []
    for c in adv:
        sess, initial, deltas, dt = run_c(c)
        row = score(c, sess, initial, deltas)
        row["latency_s"] = round(dt, 4)
        adv_rows.append(row)
    adv_m = summarize(adv_rows)
    print("ADV", json.dumps(adv_m, ensure_ascii=False), flush=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_ADV.write_text(json.dumps({"metrics": adv_m, "rows": adv_rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
