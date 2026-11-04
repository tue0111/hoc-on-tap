# -*- coding: utf-8 -*-
"""Derive concept × dimension evidence state from admitted observations only.

Recomputable. No mastery score. No forgetting decay. No global learner label.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone

POLICY_VERSION = "7.0.0"
STATE_VERSION = "7.0.0"

DIMS = ("RECALL", "CONCEPTUAL", "PROCEDURAL", "APPLICATION", "TRANSFER")
DIM_KEYS = {d: d.lower() for d in DIMS}

INDEPENDENT = {"INDEPENDENT_TASK", "CROSS_CONTEXT_TRANSFER"}
SKIP_SUPPORT = {"SELF_REPORTED", "COPIED", "GUIDED", "HINTED"}
SKIP_HINT = {"DIRECT_HINT", "ANSWER_EXPOSED"}

FORBIDDEN_FIELDS = (
    "learner_score",
    "overall_mastery",
    "accounting_mastery_percent",
    "course_mastery_percent",
    "mastery",
)


def _ts(e: dict) -> str:
    return e.get("observed_at") or e.get("admitted_at") or e.get("timestamp") or ""


def _ref(e: dict) -> str:
    return e.get("artifact_id") or e.get("candidate_id") or e.get("diagnostic_result_ref") or ""


def _usable_independent(e: dict) -> bool:
    if e.get("independence") not in INDEPENDENT:
        return False
    if e.get("support_level") in SKIP_SUPPORT:
        return False
    if e.get("hint_level") in SKIP_HINT:
        return False
    if e.get("outcome") not in {"CORRECT", "INCORRECT"}:
        return False
    return True


def validate_row(e: dict) -> str | None:
    if not isinstance(e, dict):
        return "STATE_INPUT_INVALID"
    if not e.get("concept_id"):
        return "STATE_INPUT_INVALID"
    dim = (e.get("dimension") or "").upper()
    if dim not in DIMS:
        return "STATE_INPUT_INVALID"
    return None


def classify_dimension(events: list[dict]) -> dict:
    """events already filtered to one concept × one dimension."""
    invalid = []
    usable = []
    retries = []
    for e in events:
        err = validate_row({**e, "concept_id": e.get("concept_id") or "_", "dimension": e.get("dimension")})
        if err and not e.get("concept_id"):
            invalid.append(e)
            continue
        if e.get("independence") == "SAME_TASK_RETRY":
            retries.append(e)
            continue
        if _usable_independent(e):
            usable.append(e)
    usable.sort(key=_ts)
    pos = [e for e in usable if e.get("outcome") == "CORRECT"]
    neg = [e for e in usable if e.get("outcome") == "INCORRECT"]
    pos_refs = [_ref(e) for e in pos if _ref(e)]
    neg_refs = [_ref(e) for e in neg if _ref(e)]
    contradictions = []
    if pos and neg:
        contradictions.append(
            {
                "type": "same_dimension_opposite_outcomes",
                "positive_refs": pos_refs,
                "negative_refs": neg_refs,
            }
        )
    latest = _ts(usable[-1]) if usable else None
    latest_outcome = usable[-1].get("outcome") if usable else None
    n_pos, n_neg = len(pos), len(neg)

    last_neg_i = max((i for i, e in enumerate(usable) if e.get("outcome") == "INCORRECT"), default=-1)
    later_pos = [e for i, e in enumerate(usable) if i > last_neg_i and e.get("outcome") == "CORRECT"]
    earlier_neg = [e for i, e in enumerate(usable) if i < last_neg_i + 1 and e.get("outcome") == "INCORRECT"] if last_neg_i >= 0 else []

    if n_pos == 0 and n_neg == 0:
        state, conf, reasons = "INSUFFICIENT_EVIDENCE", "NONE", ["NO_INDEPENDENT_EVIDENCE"]
        if retries:
            reasons.append("RETRIES_DO_NOT_COUNT")
    elif n_pos >= 1 and n_neg >= 1:
        if latest_outcome == "CORRECT" and len(earlier_neg) >= 2:
            if len(later_pos) >= 2:
                state, conf, reasons = "SUPPORTED", "HIGH", ["RECOVERY_CONFIRMED", "REPEATED_LATER_POSITIVE"]
            else:
                state, conf, reasons = "RECOVERY_SIGNAL", "MEDIUM", ["RECOVERY_SIGNAL", "INSUFFICIENT_CONFIRMATION"]
        elif latest_outcome == "INCORRECT" and n_pos >= 1:
            state, conf, reasons = "MIXED", "MEDIUM", ["CONTRADICTION_SAME_DIMENSION", "LATEST_NEGATIVE"]
        else:
            state, conf, reasons = "MIXED", "MEDIUM", ["POSITIVE_AND_NEGATIVE"]
    elif n_neg == 0:
        if n_pos >= 2:
            state, conf, reasons = "SUPPORTED", "HIGH", ["REPEATED_INDEPENDENT_POSITIVE"]
        else:
            state, conf, reasons = "TENTATIVELY_SUPPORTED", "MEDIUM", ["SINGLE_INDEPENDENT_POSITIVE"]
    else:
        if n_neg >= 2:
            state, conf, reasons = "CONCERN", "HIGH", ["REPEATED_INDEPENDENT_NEGATIVE"]
        else:
            state, conf, reasons = "TENTATIVE_CONCERN", "MEDIUM", ["SINGLE_INDEPENDENT_NEGATIVE"]

    if state == "SUPPORTED" and conf == "LOW":
        state, conf = "TENTATIVELY_SUPPORTED", "MEDIUM"

    return {
        "state": state,
        "confidence_band": conf,
        "positive_evidence_refs": pos_refs,
        "negative_evidence_refs": neg_refs,
        "contradiction_refs": contradictions,
        "independent_observation_count": n_pos + n_neg,
        "latest_observation_at": latest or None,
        "latest_independent_outcome": latest_outcome,
        "rationale_codes": reasons,
        "_retry_count": len(retries),
        "_invalid": len(invalid),
    }


def empty_dimension() -> dict:
    return {
        "state": "INSUFFICIENT_EVIDENCE",
        "confidence_band": "NONE",
        "positive_evidence_refs": [],
        "negative_evidence_refs": [],
        "contradiction_refs": [],
        "independent_observation_count": 0,
        "latest_observation_at": None,
        "latest_independent_outcome": None,
        "rationale_codes": ["NO_INDEPENDENT_EVIDENCE"],
    }


def derive_concept(concept_id: str, events: list[dict]) -> dict:
    by_dim: dict[str, list] = {d: [] for d in DIMS}
    courses = []
    invalid = 0
    unused_retries = 0
    for e in events:
        err = validate_row(e)
        if err:
            invalid += 1
            continue
        dim = (e.get("dimension") or "").upper()
        by_dim[dim].append(e)
        cid = e.get("course_id")
        if cid and cid not in courses:
            courses.append(cid)
        if e.get("independence") == "SAME_TASK_RETRY":
            unused_retries += 1
    dimensions = {}
    pos = neg = 0
    latest = None
    refs = []
    for d in DIMS:
        st = classify_dimension(by_dim[d]) if by_dim[d] else empty_dimension()
        unused_retries += int(st.pop("_retry_count", 0) or 0)
        invalid += int(st.pop("_invalid", 0) or 0)
        dimensions[DIM_KEYS[d]] = st
        pos += len(st.get("positive_evidence_refs") or [])
        neg += len(st.get("negative_evidence_refs") or [])
        ts = st.get("latest_observation_at")
        if ts and (latest is None or ts > latest):
            latest = ts
        refs.extend(st.get("positive_evidence_refs") or [])
        refs.extend(st.get("negative_evidence_refs") or [])
    return {
        "concept_id": concept_id,
        "course_appearances": courses,
        "dimensions": dimensions,
        "last_updated_from_evidence": latest,
        "evidence_count": {"positive": pos, "negative": neg, "unused_retries": unused_retries, "invalid": invalid},
        "state_version": STATE_VERSION,
        "derivation_policy_version": POLICY_VERSION,
        "provenance_refs": [r for r in dict.fromkeys(refs) if r],
    }


def recompute(admitted: list[dict]) -> dict:
    """FULL_RECOMPUTE from admitted evidence. HOLD/REJECT must not be passed in."""
    invalid = []
    groups: dict[str, list] = defaultdict(list)
    seen_fp = set()
    for e in admitted or []:
        err = validate_row(e)
        if err:
            invalid.append({"record": e, "reason": err})
            continue
        fp = (
            e.get("artifact_id")
            or e.get("candidate_id")
            or (e.get("source_session_id"), e.get("source_task_id"), e.get("concept_id"), e.get("dimension"), e.get("outcome"), e.get("observation"))
        )
        if fp in seen_fp:
            continue
        seen_fp.add(fp)
        groups[e["concept_id"]].append(e)
    concepts = {cid: derive_concept(cid, evs) for cid, evs in sorted(groups.items())}
    snapshot = {
        "derived_at": datetime.now(timezone.utc).isoformat(),
        "derivation_policy_version": POLICY_VERSION,
        "state_version": STATE_VERSION,
        "source": "learner/evidence/admitted.jsonl",
        "concept_count": len(concepts),
        "invalid_input_count": len(invalid),
        "invalid_inputs": [{"reason": x["reason"], "candidate_id": (x["record"] or {}).get("candidate_id")} for x in invalid],
        "concepts": concepts,
        "coverage": coverage_view(concepts),
        "forbidden": list(FORBIDDEN_FIELDS),
        "note": "Evidence coverage only. Not a course grade or learner ability score.",
    }
    return snapshot


def coverage_view(concepts: dict) -> dict:
    counts = defaultdict(int)
    for c in concepts.values():
        for dim in (c.get("dimensions") or {}).values():
            counts[dim.get("state") or "INSUFFICIENT_EVIDENCE"] += 1
    return {
        "dimension_slot_counts": dict(counts),
        "note": "This is evidence coverage, not course mastery percentage.",
    }
