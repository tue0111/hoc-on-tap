# -*- coding: utf-8 -*-
"""Phase 8 longitudinal policy. One next action. Does not write learner state."""
from __future__ import annotations
import uuid

from decision.action_taxonomy import FORBIDDEN
from decision.engine import decide as phase4_decide
from diagnostic.signals import normalize_course
from learning_policy.prerequisite import relevant_prereqs, should_backfill
from learning_policy.priority import (
    LAYER,
    NLKT_CORE,
    STATE_PRIORITY,
    action_for_state,
    depth_for_action,
    preferred_dim,
    relevant_dims,
)
from mastery.estimator import DIM_KEYS, DIMS, empty_dimension

POLICY_VERSION = "8.0.0"
DO_NOT = (
    "Do not treat SUPPORTED as mastered.",
    "Do not treat INSUFFICIENT_EVIDENCE as weakness.",
    "Do not schedule reviews or SRS.",
    "Do not output a multi-item study plan.",
    "Do not write learner state from this action.",
)


def _dim_state(snap: dict | None, concept: str, dim: str) -> dict:
    c = ((snap or {}).get("concepts") or {}).get(concept) or {}
    return (c.get("dimensions") or {}).get(DIM_KEYS.get(dim, dim.lower())) or empty_dimension()


def _error_type(diag: dict | None) -> str | None:
    if not diag:
        return None
    return diag.get("primary_error_code") or (diag.get("root_cause") or {}).get("error_type")


def _diag_conf(diag: dict | None) -> str:
    if not diag:
        return ""
    return (diag.get("confidence") or (diag.get("root_cause") or {}).get("confidence") or "").lower()


def _strong_diag(diag: dict | None) -> bool:
    if not diag:
        return False
    if diag.get("status") not in {"DIAGNOSED", "PARTIAL"}:
        return False
    et = _error_type(diag)
    if et in {None, "unknown", "none"}:
        return False
    return _diag_conf(diag) in {"high", "medium"}


def _item_success(diag: dict | None) -> bool:
    """Current item is evidenced correct. Does not erase history and is not mastery."""
    if not diag:
        return False
    if diag.get("status") not in {"DIAGNOSED", "PARTIAL"}:
        return False
    if _error_type(diag) not in {"none", "no_error", "no_gap"}:
        return False
    return _diag_conf(diag) in {"high", "medium"}


ERROR_DIM = {
    "recall_failure": "RECALL",
    "conceptual_failure": "CONCEPTUAL",
    "prerequisite_gap": "CONCEPTUAL",
    "terminology_confusion": "RECALL",
    "procedural_error": "PROCEDURAL",
    "classification_error": "APPLICATION",
    "journal_entry_error": "APPLICATION",
    "formula_selection_error": "APPLICATION",
    "arithmetic_error": "APPLICATION",
    "interpretation_error": "CONCEPTUAL",
    "transfer_failure": "TRANSFER",
}


def _pack(status, action_type, concept, dim, course, is_prereq, reason, goal, state_basis, codes, rejected, curriculum_basis=None):
    st = "VERIFY_MORE" if action_type == "VERIFY_MORE" else status
    if action_type == "CONTINUE":
        st = "CONTINUE"
        action_type = "NO_INTERVENTION"
    if action_type == "NO_ACTION":
        st = "NO_ACTION"
        action_type = "NO_INTERVENTION"
    return {
        "action_id": f"pol-{uuid.uuid4().hex[:12]}",
        "status": st if st in {"ACTION_SELECTED", "VERIFY_MORE", "CONTINUE", "NO_ACTION"} else "ACTION_SELECTED",
        "target": {
            "concept_id": concept,
            "dimension": dim,
            "course_id": course,
            "is_prerequisite": bool(is_prereq),
        },
        "action": {
            "type": action_type,
            "depth": depth_for_action(action_type, (state_basis or {}).get("state")),
            "reason": reason,
            "goal": goal,
        },
        "state_basis": state_basis or {},
        "curriculum_basis": list(curriculum_basis or []),
        "alternatives_rejected": rejected,
        "priority_reason_codes": codes,
        "persistence": False,
        "do_not_infer": list(DO_NOT),
        "policy_version": POLICY_VERSION,
    }


def choose(request: dict) -> dict:
    ctx = request.get("current_context") or {}
    course = normalize_course(ctx.get("course_id"))
    concepts = list(ctx.get("current_concepts") or [])
    task = ctx.get("task_type")
    req_dim = ctx.get("required_dimension")
    snap = request.get("learner_state")
    diag = request.get("current_diagnostic_result")
    allow = (request.get("constraints") or {}).get("allow_prerequisite_backfill", True)
    dims = relevant_dims(task, req_dim)
    rejected = []

    # --- current diagnosis overrides historical SUPPORTED when strong ---
    if _strong_diag(diag):
        et = _error_type(diag)
        tgt = diag.get("target_concept") or (concepts[0] if concepts else None)
        if et == "arithmetic_error":
            return _pack(
                "ACTION_SELECTED",
                "MECHANICAL_CORRECTION",
                tgt,
                "APPLICATION",
                course,
                False,
                "Current arithmetic slip is scoped mechanically; historical concept state is not overturned.",
                "Correct the computation only.",
                {"state": "n/a", "confidence_band": diag.get("confidence"), "provenance_refs": []},
                ["CURRENT_DIAGNOSTIC_OVERRIDE", "MECHANICAL_SCOPE"],
                [
                    {"action": "MECHANISM_EXPLANATION", "reason_rejected": "Typo/arithmetic is not a conceptual gap."},
                    {"action": "PREREQUISITE_MICRO_BACKFILL", "reason_rejected": "A computation slip is not an NLKT gap."},
                ],
            )
        p4 = phase4_decide({"diagnostic_result": diag, "session_context": {"course_id": course, "chapter": ctx.get("chapter")}, "constraints": {"max_actions": 1, "allow_prerequisite_backfill": allow}})
        act = (p4.get("decision") or {}).get("action_type") or "VERIFY_MORE"
        is_pr = bool((p4.get("primary_gap") or {}).get("is_prerequisite"))
        dim = ERROR_DIM.get(et or "", "APPLICATION")
        if is_pr:
            dim = "CONCEPTUAL"
        gap = p4.get("primary_gap") or {}
        return _pack(
            "VERIFY_MORE" if act == "VERIFY_MORE" else "ACTION_SELECTED",
            act,
            gap.get("concept_id") or tgt,
            dim,
            course,
            is_pr,
            "Strong current diagnostic evidence outranks historical derived state for this error.",
            (p4.get("decision") or {}).get("expected_learning_effect") or "Treat the confirmed current failure layer.",
            {
                "state": "CURRENT_DIAGNOSIS",
                "confidence_band": (diag.get("confidence") or "medium").upper() if isinstance(diag.get("confidence"), str) else "MEDIUM",
                "provenance_refs": [diag.get("diagnostic_id")] if diag.get("diagnostic_id") else [],
            },
            ["CURRENT_DIAGNOSTIC_OVERRIDE"],
            [{"action": "CONTINUE", "reason_rejected": "Live confirmed error is not skipped because history was SUPPORTED."}],
        )

    # Current correct item: do not full-review historical CONCERN; do not declare mastery.
    if _item_success(diag):
        cid = (concepts[0] if concepts else None) or diag.get("target_concept")
        dim = preferred_dim(dims) if dims else "APPLICATION"
        st = _dim_state(snap, cid, dim) if cid else empty_dimension()
        return _pack(
            "CONTINUE",
            "CONTINUE",
            cid,
            dim,
            course,
            False,
            "Current item is correct. Historical CONCERN is not a permanent weakness; this success is not mastery. Continue the task.",
            "Do not restart full review from one current success.",
            st,
            ["CURRENT_ITEM_SUCCESS", "NO_FULL_REVIEW", "NOT_MASTERY"],
            [
                {"action": "MECHANISM_EXPLANATION", "reason_rejected": "A current correct item does not justify re-teaching the mechanism."},
                {"action": "PREREQUISITE_MICRO_BACKFILL", "reason_rejected": "Do not backfill NLKT on a successful current item."},
            ],
        )

    if not concepts:
        return _pack("CONTINUE", "CONTINUE", None, None, course, False, "No current concept; continue the task to gather evidence.", "Do not invent a gap.", {}, ["NO_CURRENT_CONCEPT"], [])

    # Collect relevant needs
    needs = []
    for cid in concepts:
        for d in DIMS:
            if d not in dims:
                continue
            st = _dim_state(snap, cid, d)
            needs.append({"concept_id": cid, "dimension": d, "state": st.get("state"), "conf": st.get("confidence_band"), "st": st, "is_prereq": False})

    # Prerequisite bottleneck (not automatic)
    current_primary = concepts[0]
    focus_dim = preferred_dim(dims)
    current_app = _dim_state(snap, current_primary, focus_dim)
    for p in relevant_prereqs(concepts, course):
        pst = _dim_state(snap, p, "CONCEPTUAL")
        decision = should_backfill(
            allow=allow,
            course=course,
            task_type=task,
            current_concepts=concepts,
            prereq_id=p,
            prereq_state=pst.get("state"),
            current_state=current_app.get("state"),
            diagnostic=diag,
        )
        if decision == "BACKFILL":
            return _pack(
                "ACTION_SELECTED",
                "PREREQUISITE_MICRO_BACKFILL",
                p,
                "CONCEPTUAL",
                "nguyen-ly-ke-toan",
                True,
                "Curriculum-supported prerequisite is a bottleneck for this task (concern + necessity).",
                "Micro-backfill only the required NLKT mechanism.",
                pst,
                ["PREREQUISITE_BOTTLENECK", "CURRICULUM_EDGE"],
                [{"action": "APPLICATION_PRACTICE", "reason_rejected": "Current concept has insufficient evidence; upstream concern is the bottleneck."}],
                curriculum_basis=[{"concept_id": p, "relation": "prerequisite", "required_for": current_primary, "edge": "curriculum"}],
            )
        if decision == "VERIFY":
            return _pack(
                "VERIFY_MORE",
                "VERIFY_MORE",
                current_primary,
                focus_dim,
                course,
                False,
                "Both current-concept concern and NLKT concern exist; causal role is not confirmed.",
                "Discriminate current KTTC1 failure vs NLKT Nợ/Có before backfill.",
                current_app,
                ["PREREQUISITE_ROLE_UNCLEAR"],
                [{"action": "PREREQUISITE_MICRO_BACKFILL", "reason_rejected": "Do not auto-blame NLKT when the current concept also shows concern."}],
            )
        if pst.get("state") in {"CONCERN", "TENTATIVE_CONCERN"}:
            rejected.append({"action": "PREREQUISITE_MICRO_BACKFILL", "reason_rejected": f"{p} concern is not necessary for this task mechanism."})

    # Filter to actionable relevant needs
    treatable = [n for n in needs if n["state"] not in {"SUPPORTED", "TENTATIVELY_SUPPORTED"}]
    # INSUFFICIENT on irrelevant already excluded by dims
    if not treatable:
        all_ok = needs and all(n["state"] in {"SUPPORTED", "TENTATIVELY_SUPPORTED"} for n in needs)
        if all_ok:
            n0 = needs[0]
            return _pack(
                "CONTINUE",
                "CONTINUE",
                n0["concept_id"],
                n0["dimension"],
                course,
                False,
                "Relevant dimensions are SUPPORTED or TENTATIVELY_SUPPORTED. Continue the current task; this is not mastery.",
                "Gather more natural evidence without extra remediation.",
                n0["st"],
                ["CONTINUE_SUPPORTED_NOT_MASTERED"],
                [{"action": "MECHANISM_EXPLANATION", "reason_rejected": "Do not re-teach a currently supported dimension."}],
            )
        return _pack("CONTINUE", "CONTINUE", concepts[0], focus_dim, course, False, "No relevant gap for this task.", "Continue.", {}, ["NO_RELEVANT_GAP"], rejected)

    # INSUFFICIENT required → VERIFY_MORE not teach
    insuff = [n for n in treatable if n["state"] == "INSUFFICIENT_EVIDENCE"]
    others = [n for n in treatable if n["state"] != "INSUFFICIENT_EVIDENCE"]
    if insuff and not others:
        n0 = insuff[0]
        return _pack(
            "VERIFY_MORE",
            "VERIFY_MORE",
            n0["concept_id"],
            n0["dimension"],
            course,
            False,
            "Required concept/dimension has insufficient evidence; UNKNOWN is not weakness. Obtain evidence first.",
            "Lightweight diagnostic, not a review lesson.",
            n0["st"],
            ["INSUFFICIENT_NOT_FAILURE"],
            [{"action": "MECHANISM_EXPLANATION", "reason_rejected": "Do not teach a guessed gap from missing evidence."}],
        )

    pool = others or treatable
    pool.sort(key=lambda n: (STATE_PRIORITY.get(n["state"], 9), LAYER.get(n["dimension"], 9)))
    chosen = pool[0]
    act = action_for_state(chosen["dimension"], chosen["state"])
    codes = ["TASK_RELEVANT", "MINIMAL_LAYER", chosen["state"]]
    if chosen["state"] == "RECOVERY_SIGNAL":
        codes.append("RECOVERY_CONFIRMATION")
        reason = "RECOVERY_SIGNAL: confirm with a small independent task; do not restart full review."
        goal = "Independent confirmation in this dimension."
    elif chosen["state"] == "MIXED":
        reason = "MIXED evidence in a task-relevant dimension; verify rather than broad review."
        goal = "One discriminating item."
    elif chosen["state"] == "CONCERN":
        reason = f"Repeated evidence currently supports a problem in {chosen['dimension']} of {chosen['concept_id']}; patch that layer only."
        goal = "Minimal remediation of the confirmed failure layer."
    else:
        reason = f"{chosen['state']} on a relevant dimension; small verification."
        goal = "Targeted check, not chapter review."

    # Reject wrong-layer alternatives
    if chosen["dimension"] == "APPLICATION" and chosen["state"] == "CONCERN":
        rejected.append({"action": "MECHANISM_EXPLANATION", "reason_rejected": "Conceptual dimension is not the confirmed failure layer."})
    for a in FORBIDDEN:
        rejected.append({"action": a, "reason_rejected": "Out of Phase 8 scope."})

    status = "VERIFY_MORE" if act == "VERIFY_MORE" else "ACTION_SELECTED"
    return _pack(status, act, chosen["concept_id"], chosen["dimension"], course, False, reason, goal, chosen["st"], codes, rejected)


def baseline_lowest(request: dict) -> dict:
    snap = request.get("learner_state") or {}
    best = None
    for cid, c in (snap.get("concepts") or {}).items():
        for d in DIMS:
            st = (c.get("dimensions") or {}).get(DIM_KEYS[d]) or {}
            sc = STATE_PRIORITY.get(st.get("state"), 9)
            if best is None or sc < best[0]:
                best = (sc, cid, d, st)
    if not best or best[0] >= 5:
        return choose({**request, "current_diagnostic_result": None})
    cid, d, st = best[1], best[2], best[3]
    act = action_for_state(d, st.get("state"))
    if act == "CONTINUE":
        act = "MECHANISM_EXPLANATION"
    out = choose(request)
    actd = dict(out.get("action") or {})
    actd["type"] = act if act != "CONTINUE" else "MECHANISM_EXPLANATION"
    out["action"] = actd
    out["target"] = {"concept_id": cid, "dimension": d, "course_id": None, "is_prerequisite": cid in NLKT_CORE}
    out["status"] = "ACTION_SELECTED"
    out["baseline"] = "A"
    return out


def baseline_prereq_first(request: dict) -> dict:
    snap = request.get("learner_state") or {}
    for cid, c in (snap.get("concepts") or {}).items():
        if cid not in NLKT_CORE:
            continue
        st = (c.get("dimensions") or {}).get("conceptual") or {}
        if st.get("state") in {"CONCERN", "TENTATIVE_CONCERN"}:
            return _pack(
                "ACTION_SELECTED",
                "PREREQUISITE_MICRO_BACKFILL",
                cid,
                "CONCEPTUAL",
                "nguyen-ly-ke-toan",
                True,
                "Baseline B always remediates prerequisite first.",
                "Backfill",
                st,
                ["BASELINE_B"],
                [],
            )
    return choose(request)


def baseline_static(request: dict) -> dict:
    ctx = request.get("current_context") or {}
    concepts = ctx.get("current_concepts") or []
    cid = concepts[0] if concepts else None
    snap = request.get("learner_state")
    st = _dim_state(snap, cid or "", "APPLICATION")
    act = action_for_state("APPLICATION", st.get("state"))
    if act == "CONTINUE":
        act = "NO_INTERVENTION"
    return _pack(
        "ACTION_SELECTED" if act not in {"VERIFY_MORE", "NO_INTERVENTION", "CONTINUE"} else ("CONTINUE" if act in {"CONTINUE", "NO_INTERVENTION"} else "VERIFY_MORE"),
        act if act != "CONTINUE" else "NO_INTERVENTION",
        cid,
        "APPLICATION",
        ctx.get("course_id"),
        False,
        "Baseline C static map on current concept APPLICATION.",
        "Static",
        st,
        ["BASELINE_C"],
        [],
    )
