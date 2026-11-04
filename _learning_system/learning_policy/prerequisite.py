# -*- coding: utf-8 -*-
"""Conservative prerequisite backfill. Graph edge is not a gap."""
from __future__ import annotations

from learning_policy.priority import NLKT_CORE
from retrieval.concepts import prerequisite_concepts

JOURNALISH = {"journal_entry", "procedure", "classification"}
# Valuation/recall tasks do not require the Nợ/Có mechanism even if the concept is KTTC1.
NO_NOCO_TASKS = {"calculation", "recall", "definition", "explanation"}
JOURNAL_CONCEPTS = {"tien-va-tuong-duong-tien", "no-phai-thu", "hang-ton-kho"}


def task_needs_noco(task_type: str | None, concepts: list[str]) -> bool:
    t = (task_type or "").lower()
    if t in NO_NOCO_TASKS:
        return False
    if t in JOURNALISH:
        return True
    return bool(set(concepts or []) & JOURNAL_CONCEPTS)


def relevant_prereqs(concepts: list[str], course: str | None) -> list[str]:
    ids = list(concepts or [])
    pr = prerequisite_concepts(ids, course)
    return [p for p in pr if p in NLKT_CORE]


def should_backfill(
    *,
    allow: bool,
    course: str | None,
    task_type: str | None,
    current_concepts: list[str],
    prereq_id: str,
    prereq_state: str | None,
    current_state: str | None,
    diagnostic: dict | None,
) -> str:
    """Return BACKFILL | VERIFY | NO."""
    if not allow:
        return "NO"
    if course != "ke-toan-tai-chinh-1":
        return "NO"
    if not task_needs_noco(task_type, current_concepts):
        return "NO"
    if prereq_id not in NLKT_CORE:
        return "NO"
    rc = (diagnostic or {}).get("root_cause") or {}
    if rc.get("prerequisite_gap") and rc.get("prerequisite_confirmed") == "confirmed":
        return "BACKFILL"
    if prereq_state not in {"CONCERN", "TENTATIVE_CONCERN"}:
        return "NO"
    # Bottleneck: current insufficient, prereq concern.
    if current_state in {None, "INSUFFICIENT_EVIDENCE"} and prereq_state == "CONCERN":
        return "BACKFILL"
    # Both concern: do not auto-blame NLKT.
    if current_state in {"CONCERN", "TENTATIVE_CONCERN", "MIXED"}:
        return "VERIFY"
    return "NO"
