# -*- coding: utf-8 -*-
"""Lexicographic priority. No calibrated numeric weights. No SRS."""

from decision.action_taxonomy import DEPTH

NLKT_CORE = {"no-co", "ghi-so-kep", "dinh-khoan", "tai-khoan-ke-toan", "phuong-trinh-ke-toan"}
KTTC1 = {"tien-va-tuong-duong-tien", "no-phai-thu", "hang-ton-kho", "pp-tinh-gia-xuat-kho", "kktx-kkdk"}

# Lower = treat first among relevant needs.
STATE_PRIORITY = {
    "CONCERN": 0,
    "TENTATIVE_CONCERN": 1,
    "RECOVERY_SIGNAL": 2,
    "MIXED": 3,
    "INSUFFICIENT_EVIDENCE": 4,
    "TENTATIVELY_SUPPORTED": 5,
    "SUPPORTED": 6,
}

# Lowest confirmed failure layer first (same concept).
LAYER = {
    "CONCEPTUAL": 0,
    "PROCEDURAL": 1,
    "APPLICATION": 2,
    "TRANSFER": 3,
    "RECALL": 4,
}

TASK_DIMS = {
    "recall": {"RECALL"},
    "definition": {"RECALL", "CONCEPTUAL"},
    "explanation": {"CONCEPTUAL"},
    "journal_entry": {"APPLICATION", "PROCEDURAL"},
    "procedure": {"PROCEDURAL"},
    "calculation": {"APPLICATION"},
    "application": {"APPLICATION"},
    "transfer": {"TRANSFER", "APPLICATION"},
    "classification": {"APPLICATION", "CONCEPTUAL"},
}

DIM_ACTION = {
    ("RECALL", "CONCERN"): "RECALL_REFRESH",
    ("CONCEPTUAL", "CONCERN"): "MECHANISM_EXPLANATION",
    ("PROCEDURAL", "CONCERN"): "PROCEDURE_REHEARSAL",
    ("APPLICATION", "CONCERN"): "APPLICATION_PRACTICE",
    ("TRANSFER", "CONCERN"): "APPLICATION_PRACTICE",
    ("RECALL", "TENTATIVE_CONCERN"): "VERIFY_MORE",
    ("CONCEPTUAL", "TENTATIVE_CONCERN"): "VERIFY_MORE",
    ("PROCEDURAL", "TENTATIVE_CONCERN"): "VERIFY_MORE",
    ("APPLICATION", "TENTATIVE_CONCERN"): "VERIFY_MORE",
    ("TRANSFER", "TENTATIVE_CONCERN"): "VERIFY_MORE",
    ("RECALL", "RECOVERY_SIGNAL"): "RECALL_REFRESH",
    ("CONCEPTUAL", "RECOVERY_SIGNAL"): "APPLICATION_PRACTICE",
    ("PROCEDURAL", "RECOVERY_SIGNAL"): "PROCEDURE_REHEARSAL",
    ("APPLICATION", "RECOVERY_SIGNAL"): "APPLICATION_PRACTICE",
    ("TRANSFER", "RECOVERY_SIGNAL"): "APPLICATION_PRACTICE",
    ("RECALL", "MIXED"): "VERIFY_MORE",
    ("CONCEPTUAL", "MIXED"): "VERIFY_MORE",
    ("PROCEDURAL", "MIXED"): "VERIFY_MORE",
    ("APPLICATION", "MIXED"): "VERIFY_MORE",
    ("TRANSFER", "MIXED"): "VERIFY_MORE",
}


def relevant_dims(task_type: str | None, required_dimension: str | None) -> set[str]:
    if required_dimension:
        return {required_dimension.upper()}
    return set(TASK_DIMS.get((task_type or "").lower()) or {"APPLICATION"})


def preferred_dim(dims: set[str], prefer: str | None = None) -> str:
    if prefer and prefer in dims:
        return prefer
    for d in ("APPLICATION", "PROCEDURAL", "CONCEPTUAL", "TRANSFER", "RECALL"):
        if d in dims:
            return d
    return "APPLICATION"


def action_for_state(dim: str, state: str) -> str:
    if state in {"SUPPORTED", "TENTATIVELY_SUPPORTED"}:
        return "CONTINUE"
    if state == "INSUFFICIENT_EVIDENCE":
        return "VERIFY_MORE"
    return DIM_ACTION.get((dim, state), "VERIFY_MORE")


def depth_for_action(action: str, state: str | None = None) -> str:
    if state in {"RECOVERY_SIGNAL", "TENTATIVE_CONCERN"}:
        return "MICRO"
    return DEPTH.get(action, "SHORT")
