# -*- coding: utf-8 -*-
"""Duplicate lineage: same session/task/concept/dimension/observation must not inflate."""
from __future__ import annotations
from retrieval.textutil import fold


def fingerprint(c: dict) -> str:
    obs = fold((c.get("observation") or "")[:240])
    return "|".join(
        [
            str(c.get("source_session_id") or ""),
            str(c.get("source_task_id") or ""),
            str(c.get("concept_id") or ""),
            str(c.get("dimension") or ""),
            str(c.get("outcome") or ""),
            obs,
        ]
    )


def lineage_key(c: dict) -> set[str]:
    ids = set(c.get("lineage_ids") or [])
    for k in ("diagnostic_result_ref", "decision_ref", "adaptive_summary_ref", "candidate_id"):
        if c.get(k):
            ids.add(str(c[k]))
    return ids


def find_duplicate(candidate: dict, existing: list[dict]) -> str | None:
    fp = fingerprint(candidate)
    lin = lineage_key(candidate)
    for e in existing:
        if e.get("candidate_id") == candidate.get("candidate_id"):
            continue
        if fingerprint(e) == fp:
            return e.get("candidate_id") or e.get("stored_artifact_id")
        if lin and lineage_key(e) and lin & lineage_key(e):
            # same upstream artifact, same concept+dimension
            if (e.get("concept_id") == candidate.get("concept_id")) and (e.get("dimension") == candidate.get("dimension")):
                return e.get("candidate_id") or e.get("stored_artifact_id")
    return None
