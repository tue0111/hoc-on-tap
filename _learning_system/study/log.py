# -*- coding: utf-8 -*-
"""Append-only pilot audit. Instrumentation tests are tagged and not counted as real traffic."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

ROOT = _SYS
PILOT = ROOT / "pilot"
EVENTS = PILOT / "events" / "events.jsonl"
SESSIONS = PILOT / "sessions" / "sessions.jsonl"
FEEDBACK = PILOT / "feedback" / "feedback.jsonl"
CORRECTIONS = PILOT / "corrections" / "corrections.jsonl"
STATE = PILOT / "state.yaml"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def log_event(event: dict) -> dict:
    row = {"logged_at": _now(), **event}
    append_jsonl(EVENTS, row)
    return row


def log_session(session: dict) -> None:
    append_jsonl(SESSIONS, {"logged_at": _now(), **session})


def log_feedback(row: dict) -> None:
    rec = {"logged_at": _now(), **row}
    append_jsonl(FEEDBACK, rec)
    append_jsonl(CORRECTIONS, rec)


def is_real_traffic(kind: str | None) -> bool:
    return (kind or "real") == "real"
