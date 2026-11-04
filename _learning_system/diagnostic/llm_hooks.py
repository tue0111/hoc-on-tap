# -*- coding: utf-8 -*-
"""Optional model reasoning slots. Phase 3 eval uses the deterministic engine.

Enabled only if DIAGNOSTIC_LLM=1. The workflow state machine must stay
in diagnostic.engine; this module must not mutate session status.
"""
from __future__ import annotations
import os

ENABLED = os.environ.get("DIAGNOSTIC_LLM", "").strip() in {"1", "true", "TRUE"}


def interpret_error(question: str, response: str, work: str) -> dict | None:
    if not ENABLED:
        return None
    return None


def propose_hypotheses(task, target, course, signals) -> list | None:
    if not ENABLED:
        return None
    return None


def propose_question(remaining: list) -> dict | None:
    if not ENABLED:
        return None
    return None
