# -*- coding: utf-8 -*-
"""Cluster candidates by concept_id + dimension. No global weakness labels."""
from __future__ import annotations

from admission.policy import INDEPENDENT


def cluster_key(c: dict) -> tuple:
    return (c.get("concept_id") or "_", c.get("dimension") or "_")


def build_clusters(candidates: list[dict]) -> list[dict]:
    groups: dict[tuple, list] = {}
    for c in candidates:
        groups.setdefault(cluster_key(c), []).append(c)
    out = []
    for (concept, dim), rows in groups.items():
        indep_inc = sum(
            1
            for r in rows
            if r.get("outcome") == "INCORRECT" and (r.get("independence") in INDEPENDENT)
        )
        indep_cor = sum(
            1
            for r in rows
            if r.get("outcome") == "CORRECT" and (r.get("independence") in INDEPENDENT)
        )
        retries = sum(1 for r in rows if r.get("independence") == "SAME_TASK_RETRY")
        relations = []
        if indep_inc and indep_cor:
            relations.append({"type": "contradicts", "note": "Independent incorrect and independent correct coexist; keep both."})
        out.append(
            {
                "cluster_id": f"cl-{concept}-{dim}",
                "concept_id": concept,
                "dimension": dim,
                "candidate_ids": [r.get("candidate_id") for r in rows],
                "independent_incorrect": indep_inc,
                "independent_correct": indep_cor,
                "retry_count": retries,
                "relations": relations,
            }
        )
    return out


def independent_peers(candidate: dict, others: list[dict]) -> list[dict]:
    """Prior observations that count as independent of this candidate."""
    peers = []
    for o in others:
        if o.get("candidate_id") == candidate.get("candidate_id"):
            continue
        if o.get("concept_id") != candidate.get("concept_id"):
            continue
        if o.get("dimension") != candidate.get("dimension"):
            continue
        if o.get("independence") not in INDEPENDENT:
            continue
        if o.get("source_task_id") and o.get("source_task_id") == candidate.get("source_task_id"):
            continue
        if o.get("source_session_id") and o.get("source_session_id") == candidate.get("source_session_id") and o.get(
            "independence"
        ) == "SAME_TASK_RETRY":
            continue
        peers.append(o)
    return peers
