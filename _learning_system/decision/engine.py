# -*- coding: utf-8 -*-
"""Level 5 decision engine. Session-local. Does not execute teaching. Does not write mastery."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from decision.action_taxonomy import EFFECT
from decision.preview import preview
from decision.selector import (
    depth_for,
    do_not_do,
    prereq_confirmed,
    rejected_alternatives,
    select_gap_and_action,
)
from diagnostic.signals import normalize_course

ALLOWED = {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"}
NLKT = "nguyen-ly-ke-toan"


def _band(diag: dict, action: str, verify: bool) -> str:
    conf = (diag.get("confidence") or (diag.get("root_cause") or {}).get("confidence") or "").lower()
    if action in {"VERIFY_MORE"}:
        return "LOW"
    if action == "NO_INTERVENTION":
        return "HIGH" if conf in {"high", "medium"} else "MEDIUM"
    if verify:
        return "LOW"
    if conf == "high" and (action != "PREREQUISITE_MICRO_BACKFILL" or prereq_confirmed(diag)):
        return "HIGH"
    if conf == "medium":
        return "MEDIUM"
    if conf == "low":
        return "MEDIUM" if action != "PREREQUISITE_MICRO_BACKFILL" else "LOW"
    return "MEDIUM"


def _status(action: str) -> str:
    if action == "VERIFY_MORE":
        return "VERIFY_MORE"
    if action == "NO_INTERVENTION":
        return "NO_INTERVENTION"
    return "DECIDED"


def _reason(sel: dict, diag: dict) -> str:
    if sel.get("reason"):
        return sel["reason"]
    et = sel["error_type"]
    act = sel["action"]
    parts = [
        f"Observed failure treated via Phase 3 root cause `{et}`.",
        f"Selected `{act}` because it patches that layer only.",
    ]
    if sel["is_prerequisite"]:
        parts.append("Prerequisite micro-backfill is allowed only because prerequisite_gap is confirmed with a sourced NLKT rule.")
    else:
        parts.append("NLKT backfill was not selected: no confirmed prerequisite_gap.")
    if et == "classification_error":
        parts.append("A contrastive object pair targets the cause; a journal drill would treat the symptom.")
    if et == "arithmetic_error":
        parts.append("Method identification is intact; only the computation is patched.")
    if et == "journal_entry_error":
        parts.append("Journal-entry error is the confirmed primary (not a classification or Nợ/Có gap).")
    return " ".join(parts)


def decide(request: dict | None = None, diagnostic_result: dict | None = None) -> dict:
    req = request or {}
    diag = diagnostic_result or req.get("diagnostic_result")
    if diag is None:
        # Convenience path: run Phase 3 then decide. Does not modify the diagnostic engine.
        from diagnostic.engine import diagnose

        ctx = req.get("session_context") or {}
        diag = diagnose(
            {
                "question": req.get("question") or "",
                "learner_response": req.get("learner_response") or "",
                "work_shown": req.get("work_shown") or "",
                "course_context": {
                    "course_id": ctx.get("course_id"),
                    "chapter": ctx.get("chapter"),
                    "topic": ctx.get("topic"),
                },
                "followup_response": req.get("followup_response"),
            },
            followup_response=req.get("followup_response"),
            allow_question=True,
        )

    constraints = req.get("constraints") or {}
    allow_prereq = constraints.get("allow_prerequisite_backfill", True)
    ctx = req.get("session_context") or {}

    course = normalize_course(diag.get("course_id") or ctx.get("course_id"))
    chapter = ctx.get("chapter")
    sources = list(diag.get("curriculum_sources") or diag.get("evidence") or [])
    grounded_ok = bool(sources) or diag.get("evidence_status") in {"OBSERVED", "UNKNOWN"}

    sel = select_gap_and_action(diag, allow_prereq=allow_prereq)
    action = sel["action"]

    # Curriculum grounding: teaching actions need sources. Otherwise VERIFY_MORE.
    if action in {
        "RECALL_REFRESH",
        "MECHANISM_EXPLANATION",
        "CONTRASTIVE_EXAMPLE",
        "WORKED_EXAMPLE",
        "PROCEDURE_REHEARSAL",
        "APPLICATION_PRACTICE",
        "PREREQUISITE_MICRO_BACKFILL",
        "TERMINOLOGY_CLARIFICATION",
        "MECHANICAL_CORRECTION",
    } and not sources:
        action = "VERIFY_MORE"
        sel["verify"] = True
        sel["reason"] = "Curriculum evidence is missing for the intervention target."
        grounded_ok = False

    status = _status(action)
    is_prereq = bool(sel["is_prerequisite"] and action == "PREREQUISITE_MICRO_BACKFILL")
    concept = sel.get("concept_id") or diag.get("target_concept")
    error_type = sel.get("error_type")
    if action == "VERIFY_MORE":
        error_type = error_type or "unknown"
        is_prereq = False
    if action == "NO_INTERVENTION":
        is_prereq = False

    prereq_course = NLKT if is_prereq else None
    # Current-concept-first: KTTC1 errors stay in KTTC1 unless confirmed NLKT gap.
    scope_course = course
    if is_prereq:
        scope_course = course  # error appeared here
    if scope_course not in ALLOWED and scope_course:
        # do not send intervention into KTTC2 etc.
        action = "VERIFY_MORE"
        status = "VERIFY_MORE"
        is_prereq = False
        prereq_course = None
        sel["reason"] = "Course is outside the NLKT+KTTC1 production slice."

    conf = _band(diag, action, sel.get("verify", False))
    reason = _reason(sel, diag)
    depth = depth_for(action)

    candidates = [
        {"action_type": action_for_safe(error_type), "note": "policy default for root cause"},
        {"action_type": "PREREQUISITE_MICRO_BACKFILL", "note": "only if confirmed NLKT gap"},
        {"action_type": "VERIFY_MORE", "note": "if cause unresolved"},
    ]

    result = {
        "decision_id": f"ldec-{uuid.uuid4().hex[:12]}",
        "diagnostic_id": diag.get("diagnostic_id"),
        "status": status,
        "primary_gap": {
            "error_type": error_type,
            "concept_id": concept,
            "course_id": (NLKT if is_prereq else course),
            "is_prerequisite": is_prereq,
        },
        "decision": {
            "action_type": action,
            "target_concept": concept,
            "reason": reason,
            "expected_learning_effect": EFFECT.get(action, ""),
            "depth": depth,
            "preview": preview(action, concept),
        },
        "scope": {
            "course": scope_course,
            "chapter": chapter if chapter is not None else None,
            "prerequisite_course": prereq_course,
        },
        "candidates": candidates,
        "evidence_refs": sources[:5],
        "alternatives_rejected": rejected_alternatives(action, error_type, is_prereq),
        "confidence_band": conf,
        "do_not_do": do_not_do(action, is_prereq, course),
        "persistence": False,
        "grounded": bool(sources) or action in {"VERIFY_MORE", "NO_INTERVENTION"},
        "unknowns": list(diag.get("unknowns") or []),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    if not grounded_ok and action not in {"VERIFY_MORE", "NO_INTERVENTION"}:
        result["unknowns"] = list(result["unknowns"]) + ["insufficient_curriculum_evidence"]
    return result


def action_for_safe(error_type: str | None) -> str:
    from decision.policy import action_for

    return action_for(error_type)


def baseline_review_topic(diag: dict) -> dict:
    """Baseline A: generic review the topic. Ignores root cause."""
    target = diag.get("target_concept")
    return {
        "decision_id": "ldec-baseA",
        "diagnostic_id": diag.get("diagnostic_id"),
        "status": "DECIDED",
        "primary_gap": {
            "error_type": diag.get("primary_error_code"),
            "concept_id": target,
            "course_id": diag.get("course_id"),
            "is_prerequisite": False,
        },
        "decision": {
            "action_type": "MECHANISM_EXPLANATION",
            "target_concept": target,
            "reason": "Baseline A always reviews the topic.",
            "expected_learning_effect": EFFECT["MECHANISM_EXPLANATION"],
            "depth": "NORMAL",
            "preview": "Review the topic.",
        },
        "scope": {"course": diag.get("course_id"), "chapter": None, "prerequisite_course": None},
        "evidence_refs": (diag.get("curriculum_sources") or [])[:3],
        "alternatives_rejected": [],
        "confidence_band": "LOW",
        "do_not_do": [],
        "persistence": False,
        "grounded": True,
        "baseline": "A",
    }


def baseline_static_lookup(diag: dict) -> dict:
    """Baseline B: static error-type → action, no guards."""
    from decision.policy import action_for

    et = diag.get("primary_error_code") or (diag.get("root_cause") or {}).get("error_type")
    action = action_for(et)
    rc = diag.get("root_cause") or {}
    is_prereq = bool(rc.get("prerequisite_gap"))  # unconfirmed still backfills — the point of the baseline
    target = rc.get("prerequisite_concept_id") if is_prereq else diag.get("target_concept")
    return {
        "decision_id": "ldec-baseB",
        "diagnostic_id": diag.get("diagnostic_id"),
        "status": "DECIDED" if action not in {"VERIFY_MORE", "NO_INTERVENTION"} else action,
        "primary_gap": {
            "error_type": et,
            "concept_id": target,
            "course_id": diag.get("course_id"),
            "is_prerequisite": is_prereq,
        },
        "decision": {
            "action_type": action,
            "target_concept": target,
            "reason": "Baseline B static lookup on primary_error_code.",
            "expected_learning_effect": EFFECT.get(action, ""),
            "depth": depth_for(action),
            "preview": preview(action, target),
        },
        "scope": {
            "course": diag.get("course_id"),
            "chapter": None,
            "prerequisite_course": NLKT if is_prereq else None,
        },
        "evidence_refs": (diag.get("curriculum_sources") or [])[:3],
        "alternatives_rejected": [],
        "confidence_band": "MEDIUM",
        "do_not_do": [],
        "persistence": False,
        "grounded": True,
        "baseline": "B",
    }
