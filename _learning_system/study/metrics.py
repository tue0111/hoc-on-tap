# -*- coding: utf-8 -*-
"""Pilot counters. Synthetic/instrumentation traffic is excluded."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

from study.log import EVENTS, SESSIONS

HIGH = {
    "FALSE_LONG_TERM_MEMORY",
    "WRONG_CURRICULUM_SOURCE_PRESENTED_AS_FACT",
    "FALSE_PREREQUISITE_BACKFILL",
    "REPEATED_WRONG_DIAGNOSIS_AFTER_CORRECTION",
    "STATE_CORRUPTION",
    "PROVENANCE_LOSS",
    "CROSS_COURSE_CONTAMINATION",
    "SOURCE_INTEGRITY_CHANGE",
}


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def snapshot() -> dict:
    sess = [r for r in _load(SESSIONS) if r.get("counted_as_real") or r.get("kind") == "real"]
    ev = [r for r in _load(EVENTS) if r.get("counted_as_real")]
    high = [r for r in ev if r.get("severity") in HIGH or r.get("high_severity")]
    return {
        "meaningful_sessions": len({r.get("session_id") for r in sess if r.get("session_id")}),
        "substantive_turns": sum(int(r.get("substantive_turns") or 0) for r in sess)
        or sum(1 for r in ev if r.get("system_mode") in {"teach", "decision", "adapt", "feedback"}),
        "events_real": len(ev),
        "high_severity_open": len(high),
        "modes": dict(Counter(r.get("system_mode") for r in ev)),
        "corrections": dict(Counter(r.get("learner_correction") for r in ev if r.get("learner_correction"))),
    }
