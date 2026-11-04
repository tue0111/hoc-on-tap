# -*- coding: utf-8 -*-
"""Deterministic re-diagnosis / re-decision triggers. Not every message."""
from __future__ import annotations

MAX_DISCRIMINATORS = 3

ALWAYS_REDIAGNOSE = {"DIAGNOSTIC_ANSWER", "RETRY_ANSWER", "CORRECTION", "CALCULATION", "CLASSIFICATION_CHOICE", "JOURNAL_ENTRY", "EXPLANATION", "WORKED_STEP"}
NEVER_REDIAGNOSE = {"SELF_REPORT", "NO_RESPONSE"}


def should_rediagnose(session: dict, event: dict, interp: dict) -> bool:
    et = event.get("event_type")
    if et in NEVER_REDIAGNOSE or interp.get("self_report"):
        return False
    if interp.get("irrelevant") and et == "AMBIGUOUS_RESPONSE":
        return False
    action = ((session.get("current_decision") or {}).get("decision") or {}).get("action_type")
    if action == "VERIFY_MORE" and et in ALWAYS_REDIAGNOSE:
        return True
    if interp.get("strength") == "STRONG" and interp.get("suggested_error"):
        cur = (session.get("current_diagnosis") or {}).get("primary_error_code")
        if interp["suggested_error"] != cur:
            return True
        if interp["suggested_error"] == "prerequisite_gap":
            return True
    if "prerequisite_gap" in (interp.get("contradicts") or []) or "prerequisite_gap" in (interp.get("supports") or []):
        return True
    if interp.get("unresolved_reasoning"):
        return True
    if et in ALWAYS_REDIAGNOSE and interp.get("strength") in {"STRONG", "MEDIUM"}:
        return True
    n_since = 0
    for ev in reversed(session.get("evidence_history") or []):
        if ev.get("event_id") == event.get("event_id"):
            continue
        n_since += 1
        if n_since >= 2 and interp.get("strength") != "WEAK":
            return True
        break
    return False


def diagnosis_materially_changed(old: dict | None, new: dict | None) -> bool:
    if not old or not new:
        return True
    if (old.get("primary_error_code") or "") != (new.get("primary_error_code") or ""):
        return True
    orc = old.get("root_cause") or {}
    nrc = new.get("root_cause") or {}
    if bool(orc.get("prerequisite_gap")) != bool(nrc.get("prerequisite_gap")):
        return True
    if (orc.get("prerequisite_confirmed") or "") != (nrc.get("prerequisite_confirmed") or ""):
        return True
    if (old.get("status") or "") != (new.get("status") or ""):
        return True
    oc = (old.get("confidence") or "").lower()
    nc = (new.get("confidence") or "").lower()
    if {oc, nc} == {"high", "inconclusive"} or {oc, nc} == {"low", "high"}:
        return True
    return False


def should_redecide(session: dict, old_diag: dict | None, new_diag: dict | None, interp: dict) -> bool:
    if diagnosis_materially_changed(old_diag, new_diag):
        return True
    action = ((session.get("current_decision") or {}).get("decision") or {}).get("action_type")
    if action == "VERIFY_MORE" and new_diag and new_diag.get("primary_error_code") not in {None, "unknown"}:
        if new_diag.get("status") in {"DIAGNOSED", "PARTIAL"}:
            return True
    if interp.get("correct_on_item") and interp.get("strength") == "STRONG":
        return True
    if interp.get("unresolved_reasoning"):
        return True
    return False
