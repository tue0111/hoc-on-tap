# -*- coding: utf-8 -*-
"""Hypothesis state transitions. History is kept. Weak evidence does not confirm."""
from __future__ import annotations

from adaptive.session import HYP_FOR

RANK = {
    "UNRESOLVED": 0,
    "ACTIVE": 1,
    "WEAKENED": 2,
    "SUPPORTED": 3,
    "REJECTED": 4,
    "CONFIRMED": 5,
}


def _set_state(rec: dict, new_state: str, event_id: str, reason: str) -> bool:
    old = rec["state"]
    if old == new_state:
        return False
    rec["state"] = new_state
    rec.setdefault("history", []).append({"from": old, "to": new_state, "event_id": event_id, "reason": reason})
    return True


def apply_interpretation(session: dict, interp: dict, event: dict) -> list[dict]:
    """Update records. Returns list of {hypothesis_id, from, to}."""
    changes = []
    strength = interp.get("strength") or "WEAK"
    eid = event.get("event_id") or "ev"
    if interp.get("irrelevant") or interp.get("self_report"):
        return changes

    recs = session.get("hypothesis_records") or []
    by_err = {}
    for r in recs:
        by_err.setdefault(r.get("error_type"), []).append(r)

    def bump(error_type: str, target: str, reason: str):
        rows = by_err.get(error_type)
        if not rows:
            rec = {
                "hypothesis_id": HYP_FOR.get(error_type, f"H-{error_type}"),
                "error_type": error_type,
                "concept_id": (session.get("current_diagnosis") or {}).get("target_concept"),
                "state": "UNRESOLVED",
                "history": [],
            }
            recs.append(rec)
            by_err.setdefault(error_type, []).append(rec)
            rows = [rec]
        for rec in rows:
            if rec["state"] == "REJECTED" and target in {"SUPPORTED", "CONFIRMED"}:
                # revival allowed: new evidence > previous commitment
                pass
            elif rec["state"] == "CONFIRMED" and target == "REJECTED":
                pass
            old = rec["state"]
            if _set_state(rec, target, eid, reason):
                changes.append({"hypothesis_id": rec["hypothesis_id"], "from": old, "to": target, "error_type": error_type})

    for et in interp.get("supports") or []:
        if strength == "STRONG":
            bump(et, "CONFIRMED", "strong supporting evidence")
        elif strength == "MEDIUM":
            bump(et, "SUPPORTED", "medium supporting evidence")
        else:
            bump(et, "ACTIVE", "weak support; not confirmed")

    for et in interp.get("contradicts") or []:
        if strength == "STRONG":
            bump(et, "REJECTED", "strong contradicting evidence")
        elif strength == "MEDIUM":
            bump(et, "WEAKENED", "medium contradiction")
        else:
            bump(et, "WEAKENED", "weak contradiction")

    session["hypothesis_records"] = recs
    session["open_hypotheses"] = [r["hypothesis_id"] for r in recs if r["state"] in {"ACTIVE", "SUPPORTED", "UNRESOLVED", "WEAKENED"}]
    session["resolved_hypotheses"] = [r["hypothesis_id"] for r in recs if r["state"] in {"REJECTED", "CONFIRMED"}]
    return changes
