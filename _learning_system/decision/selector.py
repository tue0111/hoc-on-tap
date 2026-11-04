# -*- coding: utf-8 -*-
"""Guards: prerequisite, minimality, VERIFY_MORE, NO_INTERVENTION."""
from __future__ import annotations
import re

from decision.action_taxonomy import DEPTH, FORBIDDEN
from decision.policy import action_for, family, pick_causal_error


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

NO_GAP_PHRASES = (
    "chỉ sai chính tả",
    "nhầm đánh máy",
    "gõ nhầm",
    "sai dấu phẩy",
    "đáp án đúng",
    "câu trả lời đúng",
    "formatting only",
    "typo only",
)

SPECIFIC_SIGNALS = (
    "reversed_dc_rule",
    "reversed_journal",
    "arithmetic",
    "formula_mismatch",
    "recall",
    "terminology",
    "classification_asset_expense",
    "kktx_mix",
    "wrong_account",
    "procedural_skip",
    "interpretation",
    "transfer",
    "correct_number_wrong_reason",
)

HEDGES = re.compile(
    r"không chắc|cảm giác|cảm thấy|\bhuh\b|chứ nhỉ|\bnhỉ\b|được không|gì đó|hình như|"
    r"cũng được|cho nhanh|hoài|chưa hiểu đề|em sai hết|không hiểu câu",
    re.I,
)
COMPLETE_CLAIM = re.compile(
    r"( là |bằng|=|phản ánh|ghi nhận|nghĩa là|không liên quan|chỉ cần|chỉ ghi|chỉ có|gồm cả|không còn|chuyển tiền)",
    re.I,
)

STRUCTURED_ERRORS = {
    "recall_failure",
    "classification_error",
    "procedural_error",
    "formula_selection_error",
    "arithmetic_error",
    "interpretation_error",
    "transfer_failure",
    "terminology_confusion",
    "prerequisite_gap",
}


def _rc(diag: dict) -> dict:
    return diag.get("root_cause") or {}


def _signals(diag: dict) -> dict:
    return diag.get("signals") or {}


def prereq_confirmed(diag: dict) -> bool:
    rc = _rc(diag)
    if not rc.get("prerequisite_gap"):
        return False
    if rc.get("prerequisite_confirmed") != "confirmed":
        return False
    if not rc.get("prerequisite_concept_id"):
        return False
    return True


def looks_like_no_gap(diag: dict, observed: str) -> bool:
    if (diag.get("primary_error_code") in {"none", "no_error", "no_gap"}) or (
        _rc(diag).get("error_type") in {"none", "no_error", "no_gap"}
    ):
        return True
    blob = (observed or "").lower()
    if any(p in blob for p in NO_GAP_PHRASES):
        return True
    sig = _signals(diag)
    if sig.get("typo_only") or sig.get("formatting_only") or sig.get("correct_answer"):
        return True
    # Named taught method, a complete numeric answer, no error cue, not confusion.
    if (
        sig.get("method_named_ok")
        and not sig.get("arithmetic")
        and not sig.get("formula_mismatch")
        and not sig.get("no_answer")
        and not sig.get("confusion_only")
        and not sig.get("reversed_dc_rule")
        and diag.get("primary_error_code") in {None, "unknown"}
        and diag.get("status") in {"INCONCLUSIVE", "PARTIAL"}
    ):
        return True
    return False


def has_specific_signals(diag: dict) -> bool:
    sig = _signals(diag)
    return any(sig.get(k) for k in SPECIFIC_SIGNALS)


def thin_evidence(diag: dict) -> bool:
    """Vague/hedged free text without a specific error cue is not enough to teach."""
    if has_specific_signals(diag):
        return False
    primary = diag.get("primary_error_code") or _rc(diag).get("error_type")
    conf = (diag.get("confidence") or _rc(diag).get("confidence") or "").lower()
    if primary in STRUCTURED_ERRORS and diag.get("status") != "INCONCLUSIVE" and conf != "inconclusive":
        return False
    if diag.get("secondary_error_codes"):
        return False
    obs = (diag.get("observed_failure") or "").strip()
    if not obs:
        return True
    if HEDGES.search(obs):
        return True
    if "?" in obs or "？" in obs:
        return True
    words = obs.split()
    if len(words) <= 7 and not COMPLETE_CLAIM.search(obs):
        return True
    if primary in {"conceptual_failure", "journal_entry_error", "unknown"} and len(words) <= 8 and not COMPLETE_CLAIM.search(obs):
        return True
    return False


def unresolved_causal_fork(diag: dict) -> bool:
    """VERIFY_MORE when remaining hyps imply different causal families (e.g. class vs Nợ/Có)."""
    session = diag.get("session") or {}
    remaining = session.get("remaining_hypotheses") or []
    considered = {h.get("hypothesis_id"): h for h in (diag.get("hypotheses_considered") or []) if isinstance(h, dict)}
    if len(remaining) <= 1:
        return False
    families = set()
    for hid in remaining:
        h = considered.get(hid) or {}
        et = h.get("error_type")
        families.add(family(et))
    if "prereq" in families and "current" in families:
        # Unconfirmed mix of NLKT vs current-concept — do not pick yet.
        if not prereq_confirmed(diag):
            return True
    return False


def should_verify(diag: dict) -> bool:
    status = diag.get("status")
    conf = (diag.get("confidence") or _rc(diag).get("confidence") or "").lower()
    primary = diag.get("primary_error_code") or _rc(diag).get("error_type")
    if status == "INCONCLUSIVE" or conf == "inconclusive":
        return True
    if primary in {None, "unknown"}:
        return True
    if diag.get("retrieval_coverage") == "insufficient" and not (diag.get("curriculum_sources") or []):
        return True
    if unresolved_causal_fork(diag):
        return True
    # Unconfirmed prerequisite must not become a teaching backfill; verify or stay current.
    rc = _rc(diag)
    if rc.get("prerequisite_gap") and rc.get("prerequisite_confirmed") != "confirmed":
        return True
    return False


def select_gap_and_action(diag: dict, allow_prereq: bool) -> dict:
    """Return {error_type, action, is_prerequisite, concept_id, verify, no_intervention}."""
    observed = (diag.get("observed_failure") or "") + " " + str(_rc(diag).get("why") or "")
    if looks_like_no_gap(diag, observed):
        return {
            "error_type": "none",
            "action": "NO_INTERVENTION",
            "is_prerequisite": False,
            "concept_id": diag.get("target_concept"),
            "verify": False,
            "no_intervention": True,
            "reason": "No evidenced learning gap (correct, typo, or formatting-only).",
        }

    if thin_evidence(diag) and not looks_like_no_gap(diag, observed):
        return {
            "error_type": diag.get("primary_error_code") or "unknown",
            "action": "VERIFY_MORE",
            "is_prerequisite": False,
            "concept_id": diag.get("target_concept"),
            "verify": True,
            "no_intervention": False,
            "reason": "Observation is too thin or hedged to choose a teaching action; obtain one discriminating response.",
        }

    if should_verify(diag) and not looks_like_no_gap(diag, observed):
        # Exception: PARTIAL with a ranked non-unknown primary of one family → still treat.
        primary = diag.get("primary_error_code") or _rc(diag).get("error_type")
        conf = (diag.get("confidence") or _rc(diag).get("confidence") or "").lower()
        fork = unresolved_causal_fork(diag)
        unconfirmed_prereq = _rc(diag).get("prerequisite_gap") and _rc(diag).get("prerequisite_confirmed") != "confirmed"
        hard = (
            diag.get("status") == "INCONCLUSIVE"
            or conf == "inconclusive"
            or primary in {None, "unknown"}
            or fork
            or unconfirmed_prereq
            or (diag.get("retrieval_coverage") == "insufficient" and not (diag.get("curriculum_sources") or []))
        )
        if hard:
            return {
                "error_type": primary or "unknown",
                "action": "VERIFY_MORE",
                "is_prerequisite": False,
                "concept_id": diag.get("target_concept"),
                "verify": True,
                "no_intervention": False,
                "reason": "Cause unresolved or evidence insufficient; do not force a teaching action.",
            }

    primary = diag.get("primary_error_code") or _rc(diag).get("error_type")
    secondary = diag.get("secondary_error_codes") or []
    chosen_error = pick_causal_error(primary, secondary)
    # Journal as primary only if it really is the confirmed root (no upstream in play).
    if chosen_error == "journal_entry_error" and primary != "journal_entry_error":
        chosen_error = primary

    is_prereq = chosen_error == "prerequisite_gap" and prereq_confirmed(diag)
    if chosen_error == "prerequisite_gap" and not is_prereq:
        return {
            "error_type": primary or "unknown",
            "action": "VERIFY_MORE",
            "is_prerequisite": False,
            "concept_id": diag.get("target_concept"),
            "verify": True,
            "no_intervention": False,
            "reason": "Prerequisite gap is unconfirmed; will not send the learner back to NLKT.",
        }
    if is_prereq and not allow_prereq:
        return {
            "error_type": primary or "conceptual_failure",
            "action": "MECHANISM_EXPLANATION",
            "is_prerequisite": False,
            "concept_id": diag.get("target_concept"),
            "verify": False,
            "no_intervention": False,
            "reason": "Backfill disabled by constraint; stay on the current-concept manifestation.",
        }

    action = action_for(chosen_error)
    concept = diag.get("target_concept")
    if is_prereq:
        concept = _rc(diag).get("prerequisite_concept_id") or "no-co"
    return {
        "error_type": chosen_error,
        "action": action,
        "is_prerequisite": is_prereq,
        "concept_id": concept,
        "verify": action == "VERIFY_MORE",
        "no_intervention": action == "NO_INTERVENTION",
        "reason": None,
    }


def rejected_alternatives(action: str, error_type: str | None, is_prereq: bool) -> list[dict]:
    rows = []
    if action != "PREREQUISITE_MICRO_BACKFILL":
        rows.append(
            {
                "action": "PREREQUISITE_MICRO_BACKFILL",
                "reason_rejected": "No confirmed prerequisite_gap; graph existence is not evidence of a gap.",
            }
        )
    if action != "MECHANISM_EXPLANATION" and error_type in {
        "arithmetic_error",
        "recall_failure",
        "terminology_confusion",
        "classification_error",
    }:
        rows.append(
            {
                "action": "MECHANISM_EXPLANATION",
                "reason_rejected": "Re-teaching the model is broader than the confirmed failure layer.",
            }
        )
    if error_type == "classification_error" and action != "WORKED_EXAMPLE":
        rows.append(
            {
                "action": "WORKED_EXAMPLE",
                "reason_rejected": "Wrong journal line is the symptom; classification is the cause.",
            }
        )
    if error_type == "arithmetic_error":
        rows.append(
            {
                "action": "CONTRASTIVE_EXAMPLE",
                "reason_rejected": "Method was identified; the slip is mechanical.",
            }
        )
    if action != "PROCEDURE_REHEARSAL" and error_type == "journal_entry_error":
        rows.append(
            {
                "action": "PROCEDURE_REHEARSAL",
                "reason_rejected": "Account-object mix-up does not justify rehearsing the full journal procedure.",
            }
        )
    for forbidden in FORBIDDEN:
        rows.append({"action": forbidden, "reason_rejected": "Phase 4 forbids broad review and multi-gap bundles."})
    # unique by action, keep first
    seen = set()
    out = []
    for r in rows:
        if r["action"] in seen:
            continue
        seen.add(r["action"])
        out.append(r)
    return out[:8]


def do_not_do(action: str, is_prereq: bool, course: str | None) -> list[str]:
    items = [
        "Do not write mastery scores.",
        "Do not prescribe a full chapter or course review.",
        "Do not run multiple interventions at once.",
        "Do not start spaced repetition.",
    ]
    if not is_prereq:
        items.append("Do not send the learner back to NLKT.")
    else:
        items.append("Do not review all of NLKT; only the confirmed Nợ/Có rule.")
    if action == "MECHANICAL_CORRECTION":
        items.append("Do not re-teach FIFO/BQ or debit-credit.")
    if action == "VERIFY_MORE":
        items.append("Do not teach a guessed concept.")
    return items


def depth_for(action: str) -> str:
    return DEPTH.get(action, "SHORT")
