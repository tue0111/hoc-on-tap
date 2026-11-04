# -*- coding: utf-8 -*-
"""Read-only queries over derived state. No study-next planner."""
from __future__ import annotations

from mastery.estimator import DIM_KEYS, DIMS


def concept_state(snapshot: dict, concept_id: str) -> dict | None:
    return ((snapshot or {}).get("concepts") or {}).get(concept_id)


def dimensions_insufficient(snapshot: dict) -> list[dict]:
    out = []
    for cid, c in ((snapshot or {}).get("concepts") or {}).items():
        for d in DIMS:
            st = (c.get("dimensions") or {}).get(DIM_KEYS[d]) or {}
            if st.get("state") == "INSUFFICIENT_EVIDENCE":
                out.append({"concept_id": cid, "dimension": d, "state": st.get("state")})
    return out


def concepts_in_state(snapshot: dict, state: str) -> list[dict]:
    out = []
    for cid, c in ((snapshot or {}).get("concepts") or {}).items():
        for d in DIMS:
            st = (c.get("dimensions") or {}).get(DIM_KEYS[d]) or {}
            if st.get("state") == state:
                out.append({"concept_id": cid, "dimension": d, "state": state, "confidence_band": st.get("confidence_band")})
    return out


def concern(snapshot: dict) -> list[dict]:
    return concepts_in_state(snapshot, "CONCERN") + concepts_in_state(snapshot, "TENTATIVE_CONCERN")


def recovery(snapshot: dict) -> list[dict]:
    return concepts_in_state(snapshot, "RECOVERY_SIGNAL")


def changes(transitions: list[dict], since: str | None = None) -> list[dict]:
    if not since:
        return list(transitions or [])
    return [t for t in (transitions or []) if (t.get("timestamp") or "") >= since]
