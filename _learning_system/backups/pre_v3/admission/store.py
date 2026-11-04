# -*- coding: utf-8 -*-
"""Append-only learner evidence store. ADMIT only writes active evidence."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path

from admission.policy import POLICY_VERSION

ROOT = Path(r"D:\Hoc\_learning_system\learner\evidence")
ADMITTED = ROOT / "admitted.jsonl"
HELD = ROOT / "held.jsonl"
LOG = ROOT / "admission_log.jsonl"
CONFLICTS = ROOT / "conflicts.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def write_decision(candidate: dict, decision: dict, *, persist: bool = True) -> dict:
    """If persist and ADMIT, append observation. Always log. Never edit past rows."""
    rec = {
        "operation": decision.get("decision"),
        "candidate_id": candidate.get("candidate_id"),
        "decision": decision.get("decision"),
        "timestamp": _now(),
        "policy_version": POLICY_VERSION,
        "evidence_refs": {
            "session": candidate.get("source_session_id"),
            "task": candidate.get("source_task_id"),
            "diagnostic": candidate.get("diagnostic_result_ref"),
            "decision": candidate.get("decision_ref"),
            "curriculum": candidate.get("curriculum_evidence_refs") or [],
        },
        "concept_id": candidate.get("concept_id"),
        "dimension": candidate.get("dimension"),
        "reason_codes": decision.get("reason_codes"),
    }
    artifact = None
    if persist:
        append_jsonl(LOG, rec)
        if decision.get("decision") == "ADMIT":
            artifact = {
                "artifact_id": f"lte-{candidate.get('candidate_id')}",
                "candidate_id": candidate.get("candidate_id"),
                "observation": candidate.get("observation"),
                "outcome": candidate.get("outcome"),
                "concept_id": candidate.get("concept_id"),
                "dimension": candidate.get("dimension"),
                "course_id": candidate.get("course_id"),
                "support_level": candidate.get("support_level"),
                "independence": candidate.get("independence"),
                "source_session_id": candidate.get("source_session_id"),
                "source_task_id": candidate.get("source_task_id"),
                "curriculum_evidence_refs": candidate.get("curriculum_evidence_refs") or [],
                "diagnostic_result_ref": candidate.get("diagnostic_result_ref"),
                "observed_at": candidate.get("observed_at") or candidate.get("timestamp"),
                "admission_scope": "OBSERVATION_ONLY",
                "policy_version": POLICY_VERSION,
                "admitted_at": rec["timestamp"],
            }
            append_jsonl(ADMITTED, artifact)
            decision = dict(decision)
            decision["stored_artifact_id"] = artifact["artifact_id"]
        elif decision.get("decision") == "HOLD":
            append_jsonl(HELD, {"candidate": candidate, "decision": decision, "held_at": rec["timestamp"]})
        if decision.get("contradictions"):
            append_jsonl(CONFLICTS, {"candidate_id": candidate.get("candidate_id"), "contradictions": decision.get("contradictions"), "logged_at": rec["timestamp"]})
    return decision
