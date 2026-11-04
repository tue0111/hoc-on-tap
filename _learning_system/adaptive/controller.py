# -*- coding: utf-8 -*-
"""Level 6 session controller. Reuses Phase 3 diagnose + Phase 4 decide. No mastery."""
from __future__ import annotations
import copy
import re

from adaptive.evidence import interpret, new_event
from adaptive.session import new_session
from adaptive.transition import (
    MAX_DISCRIMINATORS,
    diagnosis_materially_changed,
    should_rediagnose,
    should_redecide,
)
from adaptive.updater import apply_interpretation
from diagnostic.engine import diagnose
from diagnostic.questions import select_question
from decision.engine import decide

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


def _ctx(session: dict) -> dict:
    return session.get("course_context") or {}


def _diagnose_from_session(session: dict, latest: str) -> dict:
    task = session.get("current_task") or {}
    prior = [e.get("content") or "" for e in (session.get("evidence_history") or [])]
    work = "\n".join([task.get("initial_work") or "", task.get("initial_response") or "", *prior, latest])
    ctx = _ctx(session)
    return diagnose(
        {
            "question": task.get("question") or "",
            "learner_response": latest or task.get("initial_response") or "",
            "work_shown": work,
            "course_context": {"course_id": ctx.get("course_id"), "chapter": ctx.get("chapter"), "topic": ctx.get("topic")},
            "followup_response": latest,
        },
        followup_response=latest,
        allow_question=True,
    )


def _override_diag(diag: dict, interp: dict) -> tuple[dict, dict | None]:
    """NEW EVIDENCE > previous Phase 3 commitment when evidence is STRONG."""
    suggested = interp.get("suggested_error")
    primary = diag.get("primary_error_code")
    # A copied journal line must not erase a classification diagnosis.
    if suggested == "journal_entry_error" and primary == "classification_error" and interp.get("strength") != "STRONG":
        return diag, None
    if not suggested or interp.get("strength") != "STRONG":
        if interp.get("correct_on_item") and interp.get("strength") in {"STRONG", "MEDIUM"}:
            out = copy.deepcopy(diag)
            out["primary_error_code"] = "none"
            out["status"] = "DIAGNOSED"
            rc = dict(out.get("root_cause") or {})
            rc.update(
                {
                    "error_type": "none",
                    "prerequisite_gap": False,
                    "prerequisite_confirmed": "rejected",
                    "prerequisite_concept_id": None,
                    "confidence": "medium",
                    "why": "Item-level correct evidence; not long-term mastery.",
                }
            )
            out["root_cause"] = rc
            out["confidence"] = "medium"
            return out, {"from": diag.get("primary_error_code"), "to": "none", "reason": "correct item evidence"}
        return diag, None
    # Overdiagnosis recovery: conceptual/unknown/journal overwritten by strong specific evidence.
    allow = primary in {None, "unknown", "conceptual_failure", "journal_entry_error"} or suggested != primary
    if not allow and suggested == primary:
        # still upgrade prereq confirmation
        if suggested == "prerequisite_gap":
            allow = True
        else:
            return diag, None
    out = copy.deepcopy(diag)
    out["primary_error_code"] = suggested
    out["status"] = "DIAGNOSED"
    rc = dict(out.get("root_cause") or {})
    if suggested == "prerequisite_gap":
        rc.update(
            {
                "error_type": "prerequisite_gap",
                "prerequisite_gap": True,
                "prerequisite_confirmed": "confirmed",
                "prerequisite_concept_id": "no-co",
                "confidence": "high",
                "why": "Strong session evidence of a false Nợ/Có rule.",
            }
        )
        out["confidence"] = "high"
    elif suggested == "none":
        rc.update(
            {
                "error_type": "none",
                "prerequisite_gap": False,
                "prerequisite_confirmed": "rejected",
                "prerequisite_concept_id": None,
                "confidence": "medium",
                "why": "Item-level correct evidence; not mastery.",
            }
        )
        out["confidence"] = "medium"
    else:
        rc.update(
            {
                "error_type": suggested,
                "prerequisite_gap": False,
                "prerequisite_confirmed": "rejected",
                "prerequisite_concept_id": None,
                "confidence": "high" if interp.get("strength") == "STRONG" else "medium",
                "why": "Strong session evidence overrides the previous conceptual fallback.",
            }
        )
        out["confidence"] = rc["confidence"]
    if suggested in interp.get("contradicts") or False:
        pass
    if "prerequisite_gap" in (interp.get("contradicts") or []):
        rc["prerequisite_gap"] = False
        rc["prerequisite_confirmed"] = "rejected"
        rc["prerequisite_concept_id"] = None
    out["root_cause"] = rc
    return out, {"from": primary, "to": suggested, "reason": "; ".join(interp.get("notes") or ["strong evidence override"])}


def _decide(session: dict, diag: dict) -> dict:
    ctx = _ctx(session)
    return decide(
        {
            "diagnostic_result": diag,
            "session_context": {"course_id": ctx.get("course_id"), "chapter": ctx.get("chapter")},
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        }
    )


def _pending_from(diag: dict, dec: dict, session: dict) -> str | None:
    qs = diag.get("diagnostic_questions") or []
    if qs:
        return qs[0].get("text") if isinstance(qs[0], dict) else str(qs[0])
    recs = [h for h in (session.get("hypothesis_records") or []) if h.get("state") in {"ACTIVE", "SUPPORTED", "UNRESOLVED", "WEAKENED"}]
    if len(recs) >= 2:
        q = select_question(recs)
        if q:
            return q.get("text")
    if (dec.get("decision") or {}).get("action_type") == "VERIFY_MORE":
        return (dec.get("decision") or {}).get("preview")
    return None


def _refresh_status(session: dict, interp: dict | None = None) -> None:
    dec = session.get("current_decision") or {}
    diag = session.get("current_diagnosis") or {}
    action = (dec.get("decision") or {}).get("action_type")
    interp = interp or {}
    if session.get("discriminator_count", 0) >= MAX_DISCRIMINATORS and action == "VERIFY_MORE":
        session["status"] = "NEED_MORE_EVIDENCE"
        session["resolution_kind"] = "INCONCLUSIVE"
        session["pending_question"] = None
        return
    if interp.get("unresolved_reasoning"):
        session["status"] = "ACTIVE"
        session["resolution_kind"] = None
        return
    if interp.get("self_report"):
        return
    if interp.get("correct_on_item") and action in {None, "NO_INTERVENTION", "VERIFY_MORE"} or (
        interp.get("correct_on_item") and (diag.get("primary_error_code") in {"none", "unknown"})
    ):
        # Session-local gap on this item; not mastery.
        if not interp.get("unresolved_reasoning"):
            session["status"] = "RESOLVED"
            session["resolution_kind"] = "LEARNING_GAP_RESOLVED"
            session["pending_question"] = None
            return
    if action in TEACHING and diag.get("status") == "DIAGNOSED" and (diag.get("confidence") in {"high", "medium"}):
        confirmed = [r for r in (session.get("hypothesis_records") or []) if r.get("state") == "CONFIRMED"]
        if confirmed and not interp.get("unresolved_reasoning"):
            session["status"] = "RESOLVED"
            session["resolution_kind"] = "DIAGNOSIS_RESOLVED"
            session["pending_question"] = None
            return
    if action == "VERIFY_MORE":
        session["status"] = "NEED_MORE_EVIDENCE"
        session["resolution_kind"] = None
        return
    if action == "NO_INTERVENTION":
        session["status"] = "RESOLVED"
        session["resolution_kind"] = "LEARNING_GAP_RESOLVED"
        session["pending_question"] = None
        return
    session["status"] = "ACTIVE"


def start(request: dict) -> dict:
    ctx = request.get("session_context") or request.get("course_context") or {}
    diag = diagnose(
        {
            "question": request.get("question") or "",
            "learner_response": request.get("learner_response") or "",
            "work_shown": request.get("work_shown") or "",
            "course_context": ctx,
            "followup_response": request.get("followup_response"),
        },
        followup_response=request.get("followup_response"),
        allow_question=True,
    )
    dec = decide(
        {
            "diagnostic_result": diag,
            "session_context": {"course_id": ctx.get("course_id"), "chapter": ctx.get("chapter")},
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        }
    )
    req = dict(request)
    req["session_context"] = {"course_id": ctx.get("course_id"), "chapter": ctx.get("chapter"), "topic": ctx.get("topic")}
    session = new_session(diag, dec, req)
    _refresh_status(session)
    return session


def ingest(session: dict, content: str, event_type: str | None = None) -> dict:
    """Apply one evidence event. Mutates session. Returns a delta dict."""
    event = new_event(
        content,
        event_type=event_type,
        order=len(session.get("evidence_history") or []) + 1,
        related_question=session.get("pending_question"),
    )
    task = session.get("current_task") or {}
    interp = interpret(event, question=task.get("question") or "")
    # Retracted false direction + leftover wrong line → account/journal, not a concept lecture.
    if (
        "prerequisite_gap" in (interp.get("contradicts") or [])
        and not interp.get("suggested_error")
        and re.search(r"có\s*111|ghi có", (task.get("initial_response") or ""), re.I)
    ):
        interp = dict(interp)
        interp["suggested_error"] = "journal_entry_error"
        interp["supports"] = list(interp.get("supports") or []) + ["journal_entry_error"]
        interp["strength"] = "STRONG"
        interp["irrelevant"] = False
        interp["notes"] = list(interp.get("notes") or []) + ["Correct Nợ/Có stated; remaining issue is the recorded line."]
    event["strength"] = interp.get("strength") or event.get("strength")
    event["_interp"] = {k: interp.get(k) for k in ("suggested_error", "supports", "contradicts", "strength", "self_report", "correct_on_item", "unresolved_reasoning")}
    session.setdefault("evidence_history", []).append(event)

    # Contradictory STRONG evidence on Nợ/Có: do not average; stay unresolved.
    prereq_for = any(
        "prerequisite_gap" in (e.get("_interp") or {}).get("supports", []) and (e.get("_interp") or {}).get("strength") == "STRONG"
        for e in session["evidence_history"]
    )
    prereq_against = any(
        "prerequisite_gap" in (e.get("_interp") or {}).get("contradicts", []) and (e.get("_interp") or {}).get("strength") == "STRONG"
        for e in session["evidence_history"]
    )
    if prereq_for and prereq_against:
        interp = dict(interp)
        interp["suggested_error"] = None
        interp["strength"] = "WEAK"
        interp["notes"] = list(interp.get("notes") or []) + ["Contradictory Nợ/Có evidence; do not confirm a prerequisite gap."]
        interp["contradicts"] = list(interp.get("contradicts") or []) + ["prerequisite_gap"]
        interp["supports"] = [x for x in (interp.get("supports") or []) if x != "prerequisite_gap"]

    hyp_changes = apply_interpretation(session, interp, event)
    old_diag = session.get("current_diagnosis")
    old_dec = session.get("current_decision")
    rediag = should_rediagnose(session, event, interp)
    redec = False
    override_info = None
    new_diag = old_diag
    new_dec = old_dec

    if rediag:
        raw = _diagnose_from_session(session, event["content"])
        new_diag, override_info = _override_diag(raw, interp)
        session["rediagnose_count"] = int(session.get("rediagnose_count") or 0) + 1
        session["diagnostic_history"].append(new_diag)
        if override_info:
            session["adapted_override"] = override_info
        if diagnosis_materially_changed(old_diag, new_diag):
            session["diagnosis_transitions"].append(
                {
                    "from": (old_diag or {}).get("primary_error_code"),
                    "to": new_diag.get("primary_error_code"),
                    "event_id": event["event_id"],
                    "reason": (override_info or {}).get("reason") or "re-diagnosis from new evidence",
                }
            )
        session["current_diagnosis"] = new_diag
        redec = should_redecide(session, old_diag, new_diag, interp)
    else:
        redec = should_redecide(session, old_diag, old_diag, interp) and not interp.get("self_report")

    if redec:
        new_dec = _decide(session, session["current_diagnosis"])
        # Bound VERIFY_MORE loops.
        new_action = (new_dec.get("decision") or {}).get("action_type")
        old_action = (old_dec.get("decision") or {}).get("action_type") if old_dec else None
        if new_action == "VERIFY_MORE":
            session["discriminator_count"] = int(session.get("discriminator_count") or 0) + 1
            if int(session.get("discriminator_count") or 0) >= MAX_DISCRIMINATORS:
                session["status"] = "NEED_MORE_EVIDENCE"
                session["resolution_kind"] = "INCONCLUSIVE"
                session["pending_question"] = None
            else:
                session["pending_question"] = _pending_from(session["current_diagnosis"], new_dec, session)
        else:
            session["pending_question"] = None
        session["redecide_count"] = int(session.get("redecide_count") or 0) + 1
        session["decision_history"].append(new_dec)
        if old_action != new_action:
            session["decision_transitions"].append(
                {
                    "from": old_action,
                    "to": new_action,
                    "event_id": event["event_id"],
                    "reason": "decision updated after evidence",
                }
            )
        session["current_decision"] = new_dec

    _refresh_status(session, interp)
    return {
        "event": event,
        "interpretation": interp,
        "hypothesis_changes": hyp_changes,
        "rediagnosed": rediag,
        "redecided": redec,
        "status": session.get("status"),
        "resolution_kind": session.get("resolution_kind"),
        "persist_to_learner_state": False,
    }


def summary(session: dict) -> dict:
    diag = session.get("current_diagnosis") or {}
    dec = session.get("current_decision") or {}
    concepts = []
    for d in session.get("diagnostic_history") or []:
        c = d.get("target_concept")
        if c and c not in concepts:
            concepts.append(c)
    candidate = []
    if session.get("resolution_kind") == "DIAGNOSIS_RESOLVED":
        candidate.append(
            {
                "kind": "session_error_observation",
                "error_type": diag.get("primary_error_code"),
                "concept_id": diag.get("target_concept"),
                "note": "Candidate only. Not admitted to learner mastery.",
            }
        )
    return {
        "session_id": session.get("session_id"),
        "course": _ctx(session).get("course_id"),
        "concepts_tested": concepts,
        "observed_errors": [
            {"error_type": d.get("primary_error_code"), "concept_id": d.get("target_concept")}
            for d in (session.get("diagnostic_history") or [])
        ],
        "diagnoses": [
            {
                "primary": d.get("primary_error_code"),
                "status": d.get("status"),
                "prereq": (d.get("root_cause") or {}).get("prerequisite_gap"),
            }
            for d in (session.get("diagnostic_history") or [])
        ],
        "diagnosis_transitions": session.get("diagnosis_transitions") or [],
        "evidence_events": [
            {"event_type": e.get("event_type"), "strength": e.get("strength"), "content": (e.get("content") or "")[:200]}
            for e in (session.get("evidence_history") or [])
        ],
        "final_session_status": session.get("status"),
        "resolution_kind": session.get("resolution_kind"),
        "final_action": (dec.get("decision") or {}).get("action_type"),
        "candidate_long_term_evidence": candidate,
        "persistence": False,
    }
