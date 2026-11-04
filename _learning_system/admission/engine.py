# -*- coding: utf-8 -*-
"""Phase 6 admission gate. ADMIT | HOLD | REJECT. Observation-only. No mastery."""
from __future__ import annotations
import uuid

from admission.clustering import independent_peers
from admission.deduplication import find_duplicate
from admission.policy import FORBIDDEN_INFERENCE, HINT_BAD, INDEPENDENT, POLICY_VERSION


def _codes(*xs) -> list[str]:
    return [x for x in xs if x]


def _provenance_ok(c: dict) -> bool:
    if not c.get("source_session_id") and not c.get("diagnostic_result_ref"):
        return False
    if not c.get("concept_id"):
        return False
    if not (c.get("observation") or "").strip():
        return False
    return True


def _curriculum_ok(c: dict) -> bool:
    refs = c.get("curriculum_evidence_refs") or []
    return bool(refs) or bool(c.get("diagnostic_result_ref"))


def decide_admission(candidate: dict, prior: list[dict] | None = None, cluster_mates: list[dict] | None = None) -> dict:
    c = candidate or {}
    prior = list(prior or [])
    mates = list(cluster_mates or [])
    existing = prior + mates

    dup = find_duplicate(c, existing)
    strength = (c.get("evidence_strength") or "WEAK").upper()
    outcome = c.get("outcome") or "INCONCLUSIVE"
    support = c.get("support_level") or "INDEPENDENT"
    indep = c.get("independence")
    hint = c.get("hint_level") or "NO_HINT"
    dim = c.get("dimension")
    peers = independent_peers(c, existing)
    same_outcome_peers = [p for p in peers if p.get("outcome") == outcome]
    contradicting = [p for p in peers if p.get("outcome") in {"CORRECT", "INCORRECT"} and p.get("outcome") != outcome]

    decision = "HOLD"
    reasons = []
    conf = "LOW"

    if not _provenance_ok(c):
        decision, reasons, conf = "REJECT", ["SOURCE_UNCERTAIN"], "HIGH"
    elif dup:
        decision, reasons, conf = "REJECT", ["DUPLICATE_EVIDENCE"], "HIGH"
    elif support == "SELF_REPORTED" or (c.get("learner_event_type") == "SELF_REPORT"):
        decision, reasons, conf = "REJECT", ["SELF_REPORT_ONLY"], "HIGH"
    elif c.get("mechanical_only") and dim == "CONCEPTUAL":
        decision, reasons, conf = "REJECT", ["MECHANICAL_ONLY"], "HIGH"
    elif c.get("mechanical_only") and outcome == "INCORRECT" and dim in {None, "PROCEDURAL"}:
        decision, reasons, conf = "REJECT", ["MECHANICAL_ONLY", "TEMPORARY_CONTEXT"], "HIGH"
    elif (c.get("diagnosis_status") == "INCONCLUSIVE" or outcome == "INCONCLUSIVE") and not c.get("explicit_false_rule"):
        decision, reasons, conf = "HOLD", ["DIAGNOSIS_INCONCLUSIVE", "INSUFFICIENT_REPETITION"], "LOW"
    elif strength == "WEAK" and not c.get("explicit_false_rule"):
        decision, reasons, conf = "HOLD", ["LOW_PARSE_CONFIDENCE", "INSUFFICIENT_REPETITION"], "LOW"
    elif indep == "SAME_TASK_RETRY":
        decision, reasons, conf = "REJECT", ["SAME_TASK_RETRY"], "HIGH"
    elif hint in HINT_BAD or support in {"GUIDED", "COPIED", "HINTED"}:
        # Not independent knowledge evidence. Keep as HOLD only if we want the guided attempt later.
        if outcome == "CORRECT":
            decision, reasons, conf = "REJECT", ["HINT_CONTAMINATED"], "HIGH"
        else:
            decision, reasons, conf = "HOLD", ["HINT_CONTAMINATED", "INSUFFICIENT_REPETITION"], "LOW"
    elif c.get("wrong_reason_with_correct_result"):
        # Split: do not admit flattened "correct". Conceptual incorrect may HOLD/ADMIT as observation if strong.
        if dim == "CONCEPTUAL" and (c.get("explicit_false_rule") or strength == "STRONG"):
            decision, reasons, conf = "ADMIT", ["SPLIT_DIMENSIONS", "STRONG_DIRECT_EVIDENCE"], "MEDIUM"
        elif dim in {"APPLICATION", "PROCEDURAL"} and outcome == "CORRECT":
            decision, reasons, conf = "HOLD", ["SPLIT_DIMENSIONS", "INSUFFICIENT_REPETITION"], "LOW"
        else:
            decision, reasons, conf = "HOLD", ["SPLIT_DIMENSIONS"], "LOW"
    elif outcome == "INCORRECT" and c.get("explicit_false_rule") and strength == "STRONG" and indep in INDEPENDENT | {None, "INDEPENDENT_TASK"}:
        decision, reasons, conf = "ADMIT", ["STRONG_DIRECT_EVIDENCE"], "MEDIUM"
        if _curriculum_ok(c):
            reasons.append("CURRICULUM_GROUNDED")
    elif outcome == "CORRECT" and support == "INDEPENDENT" and hint in {"NO_HINT", "LIGHT_HINT"} and indep in INDEPENDENT:
        if dim == "TRANSFER" or strength == "STRONG" or len(same_outcome_peers) >= 1:
            decision, reasons, conf = "ADMIT", ["POSITIVE_INDEPENDENT_EVIDENCE"], "HIGH" if dim == "TRANSFER" or len(same_outcome_peers) >= 1 else "MEDIUM"
            if dim == "TRANSFER":
                reasons.append("TRANSFER_EVIDENCE")
            if _curriculum_ok(c):
                reasons.append("CURRICULUM_GROUNDED")
        else:
            # first ordinary independent success still an observation worth admitting if unhinted and grounded
            if _curriculum_ok(c) and strength in {"STRONG", "MEDIUM"}:
                decision, reasons, conf = "ADMIT", ["POSITIVE_INDEPENDENT_EVIDENCE", "CURRICULUM_GROUNDED"], "MEDIUM"
            else:
                decision, reasons, conf = "HOLD", ["INSUFFICIENT_REPETITION"], "LOW"
    elif outcome == "INCORRECT" and indep in INDEPENDENT:
        if len(same_outcome_peers) >= 1:
            decision, reasons, conf = "ADMIT", ["REPEATED_INDEPENDENT_EVIDENCE"], "HIGH"
            if _curriculum_ok(c):
                reasons.append("CURRICULUM_GROUNDED")
        elif c.get("explicit_false_rule") and strength == "STRONG":
            decision, reasons, conf = "ADMIT", ["STRONG_DIRECT_EVIDENCE"], "MEDIUM"
        else:
            decision, reasons, conf = "HOLD", ["INSUFFICIENT_REPETITION", "TEMPORARY_CONTEXT"], "LOW"
    elif indep == "SAME_PATTERN_NEAR_TRANSFER" and outcome == "INCORRECT":
        if len(same_outcome_peers) >= 1:
            decision, reasons, conf = "ADMIT", ["REPEATED_INDEPENDENT_EVIDENCE"], "MEDIUM"
        else:
            decision, reasons, conf = "HOLD", ["INSUFFICIENT_REPETITION"], "LOW"
    else:
        decision, reasons, conf = "HOLD", ["INSUFFICIENT_REPETITION"], "LOW"

    if contradicting and decision == "ADMIT":
        reasons = list(dict.fromkeys(reasons + ["CONTRADICTORY_EVIDENCE"]))
        # still ADMIT this observation; do not overwrite the other
        conf = "MEDIUM" if conf == "HIGH" else conf

    if decision == "ADMIT" and not _curriculum_ok(c) and "CURRICULUM_GROUNDED" not in reasons:
        # still allow STRONG explicit rule with session provenance
        if "STRONG_DIRECT_EVIDENCE" not in reasons:
            decision, reasons, conf = "HOLD", ["SOURCE_UNCERTAIN"], "LOW"

    return {
        "decision_id": f"adm-{uuid.uuid4().hex[:12]}",
        "candidate_id": c.get("candidate_id"),
        "decision": decision,
        "reason_codes": list(dict.fromkeys(_codes(*reasons))),
        "concept_id": c.get("concept_id"),
        "dimension": dim,
        "evidence_quality": strength,
        "independence": indep,
        "contradictions": [
            {"candidate_id": p.get("candidate_id"), "relation": "contradicts", "outcome": p.get("outcome")}
            for p in contradicting
        ],
        "duplicate_of": [dup] if dup else [],
        "admission_scope": "OBSERVATION_ONLY",
        "confidence_band": conf,
        "policy_version": POLICY_VERSION,
        "stored_artifact_id": None,
        "observation": c.get("observation"),
        "do_not_infer": list(FORBIDDEN_INFERENCE),
    }


def baseline_store_all(candidate: dict, **_k) -> dict:
    d = decide_admission(candidate, prior=[], cluster_mates=[])
    d["decision"] = "ADMIT"
    d["reason_codes"] = ["BASELINE_A_STORE_EVERY_DIAGNOSIS"]
    d["confidence_band"] = "LOW"
    d["baseline"] = "A"
    return d


def baseline_repeat_only(candidate: dict, prior=None, cluster_mates=None, **_k) -> dict:
    """Count any prior same concept, including retries — ignores quality."""
    existing = list(prior or []) + list(cluster_mates or [])
    n = sum(1 for e in existing if e.get("concept_id") == candidate.get("concept_id"))
    d = decide_admission(candidate, prior=prior, cluster_mates=cluster_mates)
    if n >= 1:
        d["decision"] = "ADMIT"
        d["reason_codes"] = ["BASELINE_B_REPEAT_IGNORING_QUALITY"]
    else:
        d["decision"] = "HOLD"
        d["reason_codes"] = ["BASELINE_B_FIRST"]
    d["baseline"] = "B"
    return d
