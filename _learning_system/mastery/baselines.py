# -*- coding: utf-8 -*-
"""Naive aggregations that Phase 7 must beat."""
from __future__ import annotations

from mastery.estimator import INDEPENDENT, classify_dimension, empty_dimension


def _ind(events):
    return [e for e in events if e.get("independence") in INDEPENDENT]


def baseline_latest(events: list[dict]) -> dict:
    usable = _ind(events)
    if not usable:
        return empty_dimension()
    usable = sorted(usable, key=lambda e: e.get("observed_at") or e.get("timestamp") or "")
    last = usable[-1]
    if last.get("outcome") == "CORRECT":
        st = "SUPPORTED"
    elif last.get("outcome") == "INCORRECT":
        st = "CONCERN"
    else:
        return empty_dimension()
    return {**empty_dimension(), "state": st, "confidence_band": "HIGH", "rationale_codes": ["BASELINE_A_LATEST"]}


def baseline_majority(events: list[dict]) -> dict:
    usable = [e for e in _ind(events) if e.get("outcome") in {"CORRECT", "INCORRECT"}]
    if not usable:
        return empty_dimension()
    pos = sum(1 for e in usable if e.get("outcome") == "CORRECT")
    neg = len(usable) - pos
    if pos > neg:
        st = "SUPPORTED"
    elif neg > pos:
        st = "CONCERN"
    else:
        st = "MIXED"
    return {**empty_dimension(), "state": st, "confidence_band": "MEDIUM", "rationale_codes": ["BASELINE_B_MAJORITY"]}


def baseline_net(events: list[dict]) -> dict:
    usable = [e for e in _ind(events) if e.get("outcome") in {"CORRECT", "INCORRECT"}]
    if not usable:
        return empty_dimension()
    net = sum(1 if e.get("outcome") == "CORRECT" else -1 for e in usable)
    if net >= 2:
        st = "SUPPORTED"
    elif net <= -2:
        st = "CONCERN"
    elif net > 0:
        st = "TENTATIVELY_SUPPORTED"
    elif net < 0:
        st = "TENTATIVE_CONCERN"
    else:
        st = "MIXED"
    return {**empty_dimension(), "state": st, "confidence_band": "LOW", "rationale_codes": ["BASELINE_C_NET"]}


def system_d(events: list[dict]) -> dict:
    return classify_dimension(events)
