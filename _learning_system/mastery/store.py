# -*- coding: utf-8 -*-
"""Read admitted evidence; write disposable derived snapshots."""
from __future__ import annotations
import json
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

from admission.store import ADMITTED, load_jsonl  # noqa: F401
from mastery.estimator import POLICY_VERSION, recompute
from mastery.transitions import diff_transitions

STATE_DIR = (_SYS / "learner" / "state")
CURRENT = STATE_DIR / "current_state.json"
TRANS = STATE_DIR / "state_transitions.jsonl"
META = STATE_DIR / "state_build_metadata.json"


def load_admitted(path: Path | None = None) -> list[dict]:
    return load_jsonl(path or ADMITTED)


def write_snapshot(snapshot: dict, old: dict | None = None, *, persist: bool = True) -> list[dict]:
    trans = diff_transitions(old, snapshot)
    if persist:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        CURRENT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
        if trans:
            with TRANS.open("a", encoding="utf-8") as f:
                for t in trans:
                    f.write(json.dumps(t, ensure_ascii=False) + "\n")
        META.write_text(
            json.dumps(
                {
                    "derivation_policy_version": POLICY_VERSION,
                    "derived_at": snapshot.get("derived_at"),
                    "concept_count": snapshot.get("concept_count"),
                    "invalid_input_count": snapshot.get("invalid_input_count"),
                    "source": snapshot.get("source"),
                    "note": "Derived state is disposable. Admitted evidence is durable.",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    return trans


def full_recompute(*, persist: bool = False, admitted: list[dict] | None = None) -> dict:
    ev = admitted if admitted is not None else load_admitted()
    old = None
    if persist and CURRENT.exists():
        old = json.loads(CURRENT.read_text(encoding="utf-8"))
    snap = recompute(ev)
    write_snapshot(snap, old, persist=persist)
    return snap
