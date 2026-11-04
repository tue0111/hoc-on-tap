# -*- coding: utf-8 -*-
"""Session-local diagnostic state. Never written to long-term learner mastery."""
from __future__ import annotations
import uuid


def new_session(
    *,
    target_concept: str | None,
    course_id: str | None,
    hypotheses: list,
    questions_asked: list | None = None,
    eliminated: list | None = None,
    remaining: list | None = None,
    diagnosis: dict | None = None,
    confidence: str | None = None,
) -> dict:
    return {
        "session_id": f"dsess-{uuid.uuid4().hex[:12]}",
        "target_concept": target_concept,
        "course_id": course_id,
        "hypotheses": hypotheses or [],
        "questions_asked": questions_asked or [],
        "learner_evidence": [],
        "eliminated_hypotheses": eliminated or [],
        "remaining_hypotheses": remaining or [],
        "diagnosis": diagnosis,
        "confidence": confidence,
        "persist_to_learner_state": False,
    }
