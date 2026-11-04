# -*- coding: utf-8 -*-
"""Error → action policy. Symptom class does not select the intervention."""

from decision.action_taxonomy import CAUSAL_RANK

# Map diagnosed ROOT CAUSE (not surface symptom) to one default action.
ERROR_TO_ACTION = {
    "recall_failure": "RECALL_REFRESH",
    "conceptual_failure": "MECHANISM_EXPLANATION",
    "classification_error": "CONTRASTIVE_EXAMPLE",
    "procedural_error": "PROCEDURE_REHEARSAL",
    "journal_entry_error": "WORKED_EXAMPLE",
    "formula_selection_error": "CONTRASTIVE_EXAMPLE",
    "arithmetic_error": "MECHANICAL_CORRECTION",
    "interpretation_error": "CONTRASTIVE_EXAMPLE",
    "transfer_failure": "APPLICATION_PRACTICE",
    "terminology_confusion": "TERMINOLOGY_CLARIFICATION",
    "prerequisite_gap": "PREREQUISITE_MICRO_BACKFILL",
    "source_conflict": "VERIFY_MORE",
    "unknown": "VERIFY_MORE",
    "none": "NO_INTERVENTION",
}

# If these two error types co-occur, treat the first (upstream).
UPSTREAM_WINS = (
    ("classification_error", "journal_entry_error"),
    ("conceptual_failure", "journal_entry_error"),
    ("prerequisite_gap", "journal_entry_error"),
    ("prerequisite_gap", "conceptual_failure"),
    ("arithmetic_error", "journal_entry_error"),
    ("formula_selection_error", "arithmetic_error"),
    ("classification_error", "procedural_error"),
)


def action_for(error_type: str | None) -> str:
    if not error_type:
        return "VERIFY_MORE"
    return ERROR_TO_ACTION.get(error_type, "VERIFY_MORE")


def pick_causal_error(primary: str | None, secondary: list | None) -> str | None:
    """Prefer the upstream confirmed cause over a downstream symptom label."""
    codes = [primary] + list(secondary or [])
    codes = [c for c in codes if c]
    if not codes:
        return primary
    for up, down in UPSTREAM_WINS:
        if up in codes and down in codes:
            return up
    return min(codes, key=lambda c: CAUSAL_RANK.get(c, 15))


def family(error_type: str | None) -> str:
    if error_type == "prerequisite_gap":
        return "prereq"
    if error_type in {"arithmetic_error"}:
        return "mechanical"
    if error_type in {"unknown", "none", None}:
        return "none"
    return "current"
