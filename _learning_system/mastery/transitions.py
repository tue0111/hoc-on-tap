# -*- coding: utf-8 -*-
"""Append-only derived-state transitions. Evidence is never rewritten."""
from __future__ import annotations
from datetime import datetime, timezone

from mastery.estimator import DIM_KEYS, DIMS, POLICY_VERSION


def diff_transitions(old_snap: dict | None, new_snap: dict) -> list[dict]:
    old_c = (old_snap or {}).get("concepts") or {}
    new_c = new_snap.get("concepts") or {}
    rows = []
    ts = datetime.now(timezone.utc).isoformat()
    ids = set(old_c) | set(new_c)
    for cid in sorted(ids):
        for d in DIMS:
            key = DIM_KEYS[d]
            o = ((old_c.get(cid) or {}).get("dimensions") or {}).get(key) or {}
            n = ((new_c.get(cid) or {}).get("dimensions") or {}).get(key) or {}
            old_s = o.get("state")
            new_s = n.get("state") or "INSUFFICIENT_EVIDENCE"
            if old_s == new_s:
                continue
            refs = list(n.get("positive_evidence_refs") or []) + list(n.get("negative_evidence_refs") or [])
            rows.append(
                {
                    "concept_id": cid,
                    "dimension": d,
                    "old_state": old_s,
                    "new_state": new_s,
                    "trigger_evidence_refs": refs,
                    "policy_version": POLICY_VERSION,
                    "timestamp": ts,
                    "reason_codes": n.get("rationale_codes") or [],
                }
            )
    return rows
