# -*- coding: utf-8 -*-
"""Phase 8 policy eval: controlled, baselines, longitudinal, closed-loop, naturalistic, adversarial, e2e."""
from __future__ import annotations
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))

from admission.engine import decide_admission
from decision.action_taxonomy import FORBIDDEN
from learning_policy.engine import baseline_lowest, baseline_prereq_first, baseline_static, choose
from mastery.estimator import recompute

ROOT = Path(r"D:\Hoc\_learning_system")
CASES = ROOT / "evals" / "learning_policy_cases.jsonl"
LONG = ROOT / "evals" / "learning_policy_longitudinal.jsonl"
NAT = ROOT / "evals" / "learning_policy_naturalistic.jsonl"
ADV = ROOT / "evals" / "learning_policy_adversarial.jsonl"
E2E = ROOT / "evals" / "learning_policy_e2e.jsonl"
OUT = ROOT / "reports" / "learning_policy_benchmark_raw.json"

SRS_KEYS = {"next_review_date", "interval_days", "ease_factor", "forgetting_probability", "review_due"}
MASTER_WORDS = ("mastered", "mastery forever", "đã thành thạo vĩnh viễn", "weak student", "strong student")
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


def _act(out):
    return (out.get("action") or {}).get("type")


def _reason(out):
    return ((out.get("action") or {}).get("reason") or "") + " " + ((out.get("action") or {}).get("goal") or "")


def flatten(obj, acc=None):
    acc = acc if acc is not None else set()
    if isinstance(obj, dict):
        acc.update(obj.keys())
        for v in obj.values():
            flatten(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            flatten(v, acc)
    return acc


def eval_one(case, mode="D"):
    req = case["request"]
    gold = case["gold"]
    if mode == "A":
        out = baseline_lowest(req)
    elif mode == "B":
        out = baseline_prereq_first(req)
    elif mode == "C":
        out = baseline_static(req)
    else:
        out = choose(req)
    pred_status = out.get("status")
    pred_act = _act(out)
    tgt = out.get("target") or {}
    pred_c = tgt.get("concept_id")
    pred_d = tgt.get("dimension")
    pred_pr = bool(tgt.get("is_prerequisite"))
    status_ok = pred_status == gold.get("status")
    act_ok = pred_act == gold.get("action_type")
    concept_ok = gold.get("concept_id") in {None, pred_c}
    dim_ok = gold.get("dimension") in {None, pred_d}
    pr_ok = pred_pr == bool(gold.get("is_prerequisite"))
    keys = flatten(out)
    srs = bool(keys & SRS_KEYS)
    mastered = any(w in _reason(out).lower() for w in MASTER_WORDS)
    broad = pred_act in FORBIDDEN or any((r.get("action") in FORBIDDEN) is False and False for r in [])
    if pred_act in FORBIDDEN:
        broad = True
    persist = bool(out.get("persistence"))
    backfill = pred_act == "PREREQUISITE_MICRO_BACKFILL" or pred_pr
    false_pr = bool(gold.get("must_not_backfill")) and backfill
    mech_wrong = bool(gold.get("must_not_mechanism")) and pred_act == "MECHANISM_EXPLANATION"
    insuff = False
    st = ((out.get("state_basis") or {}).get("state") or "")
    if st == "INSUFFICIENT_EVIDENCE" and pred_act in TEACHING - {"PREREQUISITE_MICRO_BACKFILL"}:
        insuff = True
    # UNKNOWN-as-failure: teaching the current concept from missing evidence
    if gold.get("status") == "VERIFY_MORE" and gold.get("action_type") == "VERIFY_MORE" and pred_act in TEACHING:
        insuff = True
    irrel = False
    current = set((req.get("current_context") or {}).get("current_concepts") or [])
    if pred_act in TEACHING and pred_c and pred_c not in current and not pred_pr:
        irrel = True
    if pred_act in TEACHING and gold.get("status") in {"CONTINUE", "NO_ACTION"} and mode == "D":
        irrel = True
    rec_ok = True
    if gold.get("recovery") or case.get("category") == "recovery":
        rec_ok = pred_act in {"APPLICATION_PRACTICE", "PROCEDURE_REHEARSAL", "RECALL_REFRESH"} and pred_act not in FORBIDDEN
        blob = _reason(out).lower()
        if pred_act in {"MECHANISM_EXPLANATION", "PREREQUISITE_MICRO_BACKFILL"}:
            rec_ok = False
        if "review entire" in blob or "full study plan" in blob:
            rec_ok = False
    override_ok = True
    if case.get("id", "").startswith("advp-01") or "CURRENT_DIAGNOSTIC_OVERRIDE" in (out.get("priority_reason_codes") or []):
        if case.get("id", "").startswith("advp-01"):
            override_ok = pred_act == "MECHANISM_EXPLANATION" and not (gold.get("status") == "CONTINUE")
    minimal = not (gold.get("status") in {"CONTINUE", "NO_ACTION", "VERIFY_MORE"} and pred_act in TEACHING)
    if gold.get("action_type") in TEACHING:
        minimal = pred_act not in FORBIDDEN
    fail = None
    if persist:
        fail = "PERSISTENCE_TRUE"
    elif srs:
        fail = "SRS_FIELD"
    elif mastered:
        fail = "SUPPORTED_EQUALS_MASTERED"
    elif broad:
        fail = "BROAD_REVIEW_OVERREACH"
    elif false_pr:
        fail = "FALSE_PREREQUISITE_BACKFILL"
    elif mech_wrong:
        fail = "WRONG_DIMENSION_TREATMENT"
    elif insuff:
        fail = "UNKNOWN_EQUALS_WEAK"
    elif not rec_ok:
        fail = "RECOVERY_RESET_TO_FULL_REVIEW"
    elif not status_ok or not act_ok:
        fail = "wrong_action"
    elif not concept_ok:
        fail = "wrong_concept"
    elif not dim_ok:
        fail = "wrong_dimension"
    ok = fail is None
    return {
        "id": case.get("id"),
        "category": case.get("category"),
        "mode": mode,
        "passed": ok,
        "fail_class": fail,
        "pred_status": pred_status,
        "gold_status": gold.get("status"),
        "pred_action": pred_act,
        "gold_action": gold.get("action_type"),
        "pred_concept": pred_c,
        "gold_concept": gold.get("concept_id"),
        "pred_dim": pred_d,
        "gold_dim": gold.get("dimension"),
        "pred_prereq": pred_pr,
        "gold_prereq": bool(gold.get("is_prerequisite")),
        "status_ok": status_ok,
        "action_ok": act_ok,
        "concept_ok": concept_ok,
        "dim_ok": dim_ok,
        "false_prereq": false_pr,
        "irrelevant": irrel,
        "unknown_as_weak": insuff,
        "supported_as_mastered": mastered,
        "recovery_ok": rec_ok,
        "minimal_ok": minimal,
        "override_ok": override_ok,
        "persistence": persist,
        "srs": srs,
        "codes": out.get("priority_reason_codes"),
    }


def summarize(rows):
    n = len(rows)
    if not n:
        return {"n": 0, "pass": 0, "pass_rate": 0}
    back_g = [r for r in rows if r["gold_prereq"] or r["gold_action"] == "PREREQUISITE_MICRO_BACKFILL"]
    back_p = [r for r in rows if r["pred_prereq"] or r["pred_action"] == "PREREQUISITE_MICRO_BACKFILL"]
    tp = sum(1 for r in back_p if r["gold_prereq"] or r["gold_action"] == "PREREQUISITE_MICRO_BACKFILL")
    rec = [r for r in rows if r["category"] in {"recovery", "recovery_loop"} or (r.get("id") or "").startswith("pol-recov")]
    ovr = [r for r in rows if (r.get("id") or "").startswith("advp-01") or r["category"] == "override"]
    return {
        "n": n,
        "pass": sum(1 for r in rows if r["passed"]),
        "pass_rate": round(sum(1 for r in rows if r["passed"]) / n, 4),
        "next_action_accuracy": round(sum(1 for r in rows if r["action_ok"] and r["status_ok"]) / n, 4),
        "target_concept_accuracy": round(sum(1 for r in rows if r["concept_ok"]) / n, 4),
        "target_dimension_accuracy": round(sum(1 for r in rows if r["dim_ok"]) / n, 4),
        "prerequisite_backfill_precision": round(tp / len(back_p), 4) if back_p else 1.0,
        "false_prerequisite_backfill": round(sum(1 for r in rows if r["false_prereq"]) / n, 4),
        "irrelevant_remediation": round(sum(1 for r in rows if r["irrelevant"]) / n, 4),
        "unknown_as_failure": round(sum(1 for r in rows if r["unknown_as_weak"]) / n, 4),
        "supported_as_mastered": round(sum(1 for r in rows if r["supported_as_mastered"]) / n, 4),
        "recovery_handling": round(sum(1 for r in rec if r["recovery_ok"] and r["passed"]) / len(rec), 4) if rec else 1.0,
        "minimal_intervention": round(sum(1 for r in rows if r["minimal_ok"]) / n, 4),
        "current_diagnostic_override": round(sum(1 for r in ovr if r["override_ok"] and r["passed"]) / len(ovr), 4) if ovr else None,
        "continue_correctness": round(
            sum(1 for r in rows if r["gold_status"] != "CONTINUE" or r["pred_status"] == "CONTINUE")
            / max(1, sum(1 for r in rows if r["gold_status"] == "CONTINUE")),
            4,
        )
        if any(r["gold_status"] == "CONTINUE" for r in rows)
        else 1.0,
        "verify_more_correctness": round(
            sum(1 for r in rows if r["gold_status"] != "VERIFY_MORE" or r["pred_status"] == "VERIFY_MORE")
            / max(1, sum(1 for r in rows if r["gold_status"] == "VERIFY_MORE")),
            4,
        )
        if any(r["gold_status"] == "VERIFY_MORE" for r in rows)
        else 1.0,
        "fail_classes": dict(Counter(r["fail_class"] for r in rows if r["fail_class"])),
    }


def cand(tag, concept, dim, outcome, i, course="ke-toan-tai-chinh-1"):
    ts = f"2026-01-{(i % 27) + 1:02d}T0{(i % 9)}:00:00+00:00"
    return {
        "candidate_id": f"{tag}-c{i}",
        "learner_event_type": "DIAGNOSTIC_ANSWER",
        "course_id": course,
        "concept_id": concept,
        "dimension": dim,
        "observation": f"{tag} {concept} {dim} {outcome} item {i} independent task.",
        "outcome": outcome,
        "support_level": "INDEPENDENT",
        "independence": "INDEPENDENT_TASK",
        "hint_level": "NO_HINT",
        "source_session_id": f"{tag}-sess-{i}",
        "source_task_id": f"{tag}-task-{i}",
        "curriculum_evidence_refs": [{"source_id": "src-0062"}],
        "diagnostic_result_ref": f"{tag}-diag-{i}",
        "decision_ref": f"{tag}-dec-{i}",
        "lineage_ids": [f"{tag}-diag-{i}"],
        "evidence_strength": "STRONG",
        "explicit_false_rule": outcome == "INCORRECT",
        "mechanical_only": False,
        "wrong_reason_with_correct_result": False,
        "diagnosis_status": "DIAGNOSED",
        "error_type": "classification_error" if outcome == "INCORRECT" else "none",
        "timestamp": ts,
        "observed_at": ts,
        "artifact_id": f"{tag}-art-{i}",
    }


def admit_all(candidates, prior=None):
    prior = list(prior or [])
    admitted = []
    decisions = []
    for c in candidates:
        d = decide_admission(c, prior=prior)
        decisions.append(d.get("decision"))
        if d.get("decision") == "ADMIT":
            admitted.append(c)
        prior.append(c)
    return admitted, decisions, prior


def closed_loop_recovery(i):
    htk = "hang-ton-kho"
    ctx = {"course_id": "ke-toan-tai-chinh-1", "chapter": 3, "task_type": "application", "current_concepts": [htk]}
    tag = f"clrec-{i:02d}"
    neg = [cand(tag, htk, "APPLICATION", "INCORRECT", 1), cand(tag, htk, "APPLICATION", "INCORRECT", 2)]
    adm, decs, prior = admit_all(neg)
    snap = recompute(adm)
    a1 = choose({"current_context": ctx, "learner_state": snap, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    pos1, d2, prior = admit_all([cand(tag, htk, "APPLICATION", "CORRECT", 3)], prior=prior)
    adm2 = adm + pos1
    snap2 = recompute(adm2)
    a2 = choose({"current_context": ctx, "learner_state": snap2, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    pos2, d3, prior = admit_all([cand(tag, htk, "APPLICATION", "CORRECT", 4)], prior=prior)
    adm3 = adm2 + pos2
    snap3 = recompute(adm3)
    a3 = choose({"current_context": ctx, "learner_state": snap3, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    st1 = ((snap.get("concepts") or {}).get(htk) or {}).get("dimensions", {}).get("application", {}).get("state")
    st2 = ((snap2.get("concepts") or {}).get(htk) or {}).get("dimensions", {}).get("application", {}).get("state")
    st3 = ((snap3.get("concepts") or {}).get(htk) or {}).get("dimensions", {}).get("application", {}).get("state")
    ok = (
        st1 == "CONCERN"
        and _act(a1) == "APPLICATION_PRACTICE"
        and st2 == "RECOVERY_SIGNAL"
        and _act(a2) == "APPLICATION_PRACTICE"
        and st3 == "SUPPORTED"
        and a3.get("status") == "CONTINUE"
        and "mastered" not in _reason(a3).lower()
        and all(x == "ADMIT" for x in decs + d2 + d3)
        and a1.get("persistence") is False
    )
    return {"id": tag, "category": "recovery_loop", "passed": ok, "states": [st1, st2, st3], "actions": [_act(a1), _act(a2), _act(a3)], "admissions": decs + d2 + d3}


def closed_loop_supported(i):
    fifo = "pp-tinh-gia-xuat-kho"
    ctx = {"course_id": "ke-toan-tai-chinh-1", "chapter": 3, "task_type": "calculation", "current_concepts": [fifo]}
    tag = f"clsup-{i:02d}"
    adm, decs, prior = admit_all([cand(tag, fifo, "APPLICATION", "CORRECT", 1), cand(tag, fifo, "APPLICATION", "CORRECT", 2)])
    snap = recompute(adm)
    a1 = choose({"current_context": ctx, "learner_state": snap, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    a2 = choose({"current_context": ctx, "learner_state": snap, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    st = ((snap.get("concepts") or {}).get(fifo) or {}).get("dimensions", {}).get("application", {}).get("state")
    ok = st == "SUPPORTED" and a1.get("status") == "CONTINUE" and a2.get("status") == "CONTINUE" and "mastered" not in _reason(a1).lower()
    return {"id": tag, "category": "stay_supported", "passed": ok, "states": [st], "actions": [_act(a1), _act(a2)], "admissions": decs}


def closed_loop_gather(i):
    cash = "tien-va-tuong-duong-tien"
    ctx = {"course_id": "ke-toan-tai-chinh-1", "chapter": 2, "task_type": "application", "current_concepts": [cash]}
    tag = f"clins-{i:02d}"
    snap0 = recompute([])
    a0 = choose({"current_context": ctx, "learner_state": snap0, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    adm, decs, prior = admit_all([cand(tag, cash, "APPLICATION", "CORRECT", 1)])
    snap1 = recompute(adm)
    a1 = choose({"current_context": ctx, "learner_state": snap1, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    st1 = ((snap1.get("concepts") or {}).get(cash) or {}).get("dimensions", {}).get("application", {}).get("state")
    ok = a0.get("status") == "VERIFY_MORE" and _act(a0) == "VERIFY_MORE" and st1 == "TENTATIVELY_SUPPORTED" and a1.get("status") == "CONTINUE"
    return {"id": tag, "category": "gather_then_continue", "passed": ok, "states": ["INSUFFICIENT_EVIDENCE", st1], "actions": [_act(a0), _act(a1)], "admissions": decs}


def closed_loop_prereq(i):
    htk, noco = "hang-ton-kho", "no-co"
    ctx = {"course_id": "ke-toan-tai-chinh-1", "chapter": 3, "task_type": "journal_entry", "current_concepts": [htk]}
    tag = f"clpre-{i:02d}"
    adm, decs, prior = admit_all([cand(tag, noco, "CONCEPTUAL", "INCORRECT", 1, course="nguyen-ly-ke-toan"), cand(tag, noco, "CONCEPTUAL", "INCORRECT", 2, course="nguyen-ly-ke-toan")])
    snap = recompute(adm)
    a1 = choose({"current_context": ctx, "learner_state": snap, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    pos, d2, prior = admit_all(
        [cand(tag, noco, "CONCEPTUAL", "CORRECT", 3, course="nguyen-ly-ke-toan"), cand(tag, noco, "CONCEPTUAL", "CORRECT", 4, course="nguyen-ly-ke-toan")],
        prior=prior,
    )
    snap2 = recompute(adm + pos)
    a2 = choose({"current_context": ctx, "learner_state": snap2, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    ok = (
        _act(a1) == "PREREQUISITE_MICRO_BACKFILL"
        and (a1.get("target") or {}).get("concept_id") == noco
        and a2.get("status") == "VERIFY_MORE"
        and _act(a2) != "PREREQUISITE_MICRO_BACKFILL"
    )
    return {"id": tag, "category": "prereq_then_current", "passed": ok, "actions": [_act(a1), _act(a2)], "admissions": decs + d2}


def eval_long_snapshots(seq):
    ok_steps = []
    for step in seq.get("steps") or []:
        out = choose(step["request"])
        g = step["gold"]
        ok_steps.append(out.get("status") == g.get("status") and _act(out) == g.get("action_type") and (out.get("target") or {}).get("concept_id") == g.get("concept_id"))
    return {"id": seq["id"], "category": seq.get("category"), "passed": all(ok_steps), "steps_ok": ok_steps}


def run_e2e(case):
    from adaptive.controller import ingest, start, summary
    from diagnostic.engine import diagnose
    from decision.engine import decide
    from retrieval.retrieve import retrieve

    q = case["question"]
    course = case["course"]
    ch = case.get("chapter")
    pkg = retrieve(q, filters={"course_id": course, "chapter": ch})
    diag = diagnose(
        {
            "question": q,
            "learner_response": case.get("response") or "",
            "work_shown": case.get("work") or "",
            "course_context": {"course_id": course, "chapter": ch},
        },
        followup_response=None,
        allow_question=True,
    )
    dec = decide({"diagnostic_result": diag, "session_context": {"course_id": course, "chapter": ch}, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True}})
    sess = start(
        {
            "question": q,
            "learner_response": case.get("response") or "",
            "work_shown": case.get("work") or "",
            "course_context": {"course_id": course, "chapter": ch},
        }
    )
    ingest(sess, case.get("followup") or case.get("response") or "")
    summ = summary(sess)
    live_diag = sess.get("current_diagnosis") or diag
    outcome = "INCORRECT" if (live_diag.get("primary_error_code") not in {None, "none", "unknown", "no_error"}) else "CORRECT"
    concept = live_diag.get("target_concept") or ((pkg.get("detected_concepts") or [None])[0])
    c = cand(case["id"], concept or "hang-ton-kho", "APPLICATION", outcome, 1, course=course)
    c["observation"] = (case.get("response") or "")[:200]
    c["error_type"] = live_diag.get("primary_error_code")
    c["curriculum_evidence_refs"] = (live_diag.get("curriculum_sources") or [{"source_id": "src-0062"}])[:1]
    c["diagnostic_result_ref"] = live_diag.get("diagnostic_id") or f"{case['id']}-diag"
    c["lineage_ids"] = [c["diagnostic_result_ref"]]
    adm, decs, _ = admit_all([c])
    snap = recompute(adm)
    nxt = choose(
        {
            "current_context": {"course_id": course, "chapter": ch, "task_type": "application", "current_concepts": [concept] if concept else []},
            "learner_state": snap,
            "current_diagnostic_result": live_diag,
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        }
    )
    keys = flatten(nxt)
    gold_status = case.get("gold_next_status") or ["CONTINUE", "VERIFY_MORE", "ACTION_SELECTED", "NO_ACTION"]
    traceable = bool((nxt.get("state_basis") or {}).get("state") or (nxt.get("priority_reason_codes")))
    grounded = bool(pkg.get("items") or pkg.get("coverage") in {"partial", "sufficient", "insufficient"})
    persist_ok = nxt.get("persistence") is False and sess.get("persist_to_learner_state") is False
    no_srs = not (keys & SRS_KEYS)
    status_ok = nxt.get("status") in gold_status
    # artifact continuity
    chain_ok = all(
        [
            isinstance(pkg, dict),
            isinstance(diag, dict),
            isinstance(dec, dict),
            isinstance(sess, dict),
            isinstance(summ, dict),
            isinstance(nxt, dict),
        ]
    )
    fail = None
    if not persist_ok:
        fail = "PERSISTENCE_TRUE"
    elif not no_srs:
        fail = "SRS_FIELD"
    elif not chain_ok:
        fail = "CHAIN_BREAK"
    elif not status_ok:
        fail = "wrong_next_status"
    return {
        "id": case["id"],
        "passed": fail is None,
        "fail_class": fail,
        "retrieve_items": len(pkg.get("items") or []),
        "diag": live_diag.get("primary_error_code"),
        "gold_diag": case.get("gold_diag"),
        "dec4": ((dec.get("decision") or {}).get("action_type")),
        "gold_dec4": case.get("gold_dec4"),
        "adapt_status": sess.get("status"),
        "admission": (decs[0] if decs else None),
        "next_status": nxt.get("status"),
        "next_action": _act(nxt),
        "next_concept": (nxt.get("target") or {}).get("concept_id"),
        "traceable": traceable,
        "grounded": grounded,
        "persistence_ok": persist_ok,
    }


def main():
    cases = load(CASES)
    print("CONTROLLED", len(cases), flush=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "metrics": {}, "rows": {}}
    for mode in ("A", "B", "C", "D"):
        rows = [eval_one(c, mode) for c in cases]
        m = summarize(rows)
        by = defaultdict(lambda: {"n": 0, "pass": 0})
        for r in rows:
            by[r["category"]]["n"] += 1
            by[r["category"]]["pass"] += int(r["passed"])
        m["by_category"] = {k: {**v, "rate": round(v["pass"] / v["n"], 4)} for k, v in by.items()}
        payload["metrics"][mode] = m
        if mode == "D":
            payload["rows"]["D"] = rows
            payload["fail_ids"] = [r["id"] for r in rows if not r["passed"]]
        print(mode, json.dumps(m, ensure_ascii=False), flush=True)

    longs = load(LONG)
    lrows = [eval_long_snapshots(s) for s in longs]
    payload["longitudinal_snapshots"] = {
        "n": len(lrows),
        "pass": sum(1 for r in lrows if r["passed"]),
        "pass_rate": round(sum(1 for r in lrows if r["passed"]) / len(lrows), 4),
        "fail": [r["id"] for r in lrows if not r["passed"]],
    }
    print("LONG_SNAP", json.dumps(payload["longitudinal_snapshots"], ensure_ascii=False), flush=True)

    closed = []
    for i in range(20):
        closed.append(closed_loop_recovery(i + 1))
    for i in range(20):
        closed.append(closed_loop_supported(i + 1))
    for i in range(20):
        closed.append(closed_loop_gather(i + 1))
    for i in range(20):
        closed.append(closed_loop_prereq(i + 1))
    payload["closed_loop"] = {
        "n": len(closed),
        "pass": sum(1 for r in closed if r["passed"]),
        "pass_rate": round(sum(1 for r in closed if r["passed"]) / len(closed), 4),
        "fail": [r["id"] for r in closed if not r["passed"]][:20],
        "by_category": {k: sum(1 for r in closed if r["category"] == k and r["passed"]) for k in {r["category"] for r in closed}},
        "rows": closed,
    }
    print("CLOSED", json.dumps({k: payload["closed_loop"][k] for k in ("n", "pass", "pass_rate", "fail", "by_category")}, ensure_ascii=False), flush=True)

    nats = load(NAT)
    nrows = [eval_one(c, "D") for c in nats]
    payload["naturalistic"] = summarize(nrows)
    payload["naturalistic"]["fail_ids"] = [r["id"] for r in nrows if not r["passed"]]
    print("NAT", json.dumps(payload["naturalistic"], ensure_ascii=False), flush=True)

    adv = load(ADV)
    arows = [eval_one(c, "D") for c in adv]
    payload["adversarial"] = summarize(arows)
    payload["adversarial"]["fail_ids"] = [r["id"] for r in arows if not r["passed"]]
    payload["adversarial"]["rows"] = arows
    print("ADV", json.dumps({k: payload["adversarial"][k] for k in payload["adversarial"] if k != "rows"}, ensure_ascii=False), flush=True)

    e2e = load(E2E)
    print("E2E", len(e2e), flush=True)
    erows = []
    for c in e2e:
        erows.append(run_e2e(c))
        print(" e2e", c["id"], erows[-1]["passed"], erows[-1].get("diag"), erows[-1].get("next_action"), flush=True)
    payload["e2e"] = {
        "n": len(erows),
        "pass": sum(1 for r in erows if r["passed"]),
        "pass_rate": round(sum(1 for r in erows if r["passed"]) / len(erows), 4) if erows else 0,
        "fail": [r["id"] for r in erows if not r["passed"]],
        "rows": erows,
    }
    print("E2E_SUM", json.dumps({k: payload["e2e"][k] for k in ("n", "pass", "pass_rate", "fail")}, ensure_ascii=False), flush=True)

    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
