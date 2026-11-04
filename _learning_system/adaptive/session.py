# -*- coding: utf-8 -*-
"""AdaptiveLearningSession factory. persist_to_learner_state is always false."""
from __future__ import annotations
import uuid


HYP_FOR = {
    "conceptual_failure": "H-concept",
    "arithmetic_error": "H-arith",
    "formula_selection_error": "H-formula",
    "classification_error": "H-class",
    "journal_entry_error": "H-acct",
    "prerequisite_gap": "H-noco",
    "recall_failure": "H-recall",
    "terminology_confusion": "H-term",
    "procedural_error": "H-proc",
    "interpretation_error": "H-interp",
    "transfer_failure": "H-xfer",
    "unknown": "H-unknown",
}


def _records_from_diag(diag: dict) -> list[dict]:
    considered = diag.get("hypotheses_considered") or []
    remaining = set((diag.get("session") or {}).get("remaining_hypotheses") or [])
    rejected = set((diag.get("session") or {}).get("eliminated_hypotheses") or [])
    rows = []
    seen = set()
    for h in considered:
        if not isinstance(h, dict):
            continue
        hid = h.get("hypothesis_id") or HYP_FOR.get(h.get("error_type") or "", "H-x")
        seen.add(hid)
        state = "REJECTED" if hid in rejected else ("ACTIVE" if hid in remaining or not remaining else "UNRESOLVED")
        if diag.get("primary_error_code") == h.get("error_type") and diag.get("status") == "DIAGNOSED":
            if (diag.get("confidence") or "") == "high":
                state = "SUPPORTED"
        rows.append(
            {
                "hypothesis_id": hid,
                "error_type": h.get("error_type"),
                "concept_id": h.get("concept_id"),
                "state": state,
                "history": [{"from": None, "to": state, "event_id": "start", "reason": "initial diagnosis"}],
            }
        )
    primary = diag.get("primary_error_code")
    if primary and HYP_FOR.get(primary) not in seen:
        hid = HYP_FOR.get(primary, "H-x")
        rows.append(
            {
                "hypothesis_id": hid,
                "error_type": primary,
                "concept_id": diag.get("target_concept"),
                "state": "ACTIVE",
                "history": [{"from": None, "to": "ACTIVE", "event_id": "start", "reason": "seeded from primary"}],
            }
        )
    if not rows:
        for et in ("conceptual_failure", "arithmetic_error", "prerequisite_gap", "classification_error"):
            rows.append(
                {
                    "hypothesis_id": HYP_FOR[et],
                    "error_type": et,
                    "concept_id": diag.get("target_concept"),
                    "state": "UNRESOLVED",
                    "history": [{"from": None, "to": "UNRESOLVED", "event_id": "start", "reason": "seeded under uncertainty"}],
                }
            )
    return rows


def new_session(diag: dict, dec: dict, request: dict) -> dict:
    ctx = request.get("session_context") or request.get("course_context") or {}
    recs = _records_from_diag(diag)
    open_h = [r["hypothesis_id"] for r in recs if r["state"] in {"ACTIVE", "SUPPORTED", "UNRESOLVED", "WEAKENED"}]
    pending = None
    qs = diag.get("diagnostic_questions") or []
    if qs:
        pending = qs[0].get("text") if isinstance(qs[0], dict) else str(qs[0])
    if not pending and (dec.get("decision") or {}).get("action_type") == "VERIFY_MORE":
        pending = (dec.get("decision") or {}).get("preview")
    return {
        "session_id": f"asess-{uuid.uuid4().hex[:12]}",
        "course_context": {
            "course_id": ctx.get("course_id") or diag.get("course_id"),
            "chapter": ctx.get("chapter"),
            "topic": ctx.get("topic"),
        },
        "current_task": {
            "question": request.get("question") or "",
            "initial_response": request.get("learner_response") or "",
            "initial_work": request.get("work_shown") or "",
        },
        "evidence_history": [],
        "diagnostic_history": [diag],
        "decision_history": [dec],
        "current_diagnosis": diag,
        "current_decision": dec,
        "open_hypotheses": open_h,
        "resolved_hypotheses": [r["hypothesis_id"] for r in recs if r["state"] in {"REJECTED", "CONFIRMED"}],
        "hypothesis_records": recs,
        "diagnosis_transitions": [],
        "decision_transitions": [],
        "status": "NEED_MORE_EVIDENCE" if (dec.get("decision") or {}).get("action_type") == "VERIFY_MORE" else "ACTIVE",
        "resolution_kind": None,
        "discriminator_count": 1 if pending and (dec.get("decision") or {}).get("action_type") == "VERIFY_MORE" else 0,
        "pending_question": pending,
        "rediagnose_count": 0,
        "redecide_count": 0,
        "adapted_override": None,
        "persistence": False,
        "persist_to_learner_state": False,
    }
