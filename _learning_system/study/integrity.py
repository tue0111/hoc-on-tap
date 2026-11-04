# -*- coding: utf-8 -*-
"""Source integrity vs inventory hashes. Never writes under D:\\Hoc course folders."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

from retrieval.config import INVENTORY, SLICE_COURSE_IDS, SOURCE_ROOT

BLOCK = "SOURCE_INTEGRITY_BLOCK"


def sha256_file(path: Path, buf: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(buf)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def sha256_text(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inventory() -> list[dict]:
    return json.loads(INVENTORY.read_text(encoding="utf-8"))


def verify_sources(*, courses: tuple[str, ...] | None = None) -> dict:
    courses = tuple(courses or SLICE_COURSE_IDS)
    rows = [r for r in load_inventory() if r.get("course_id") in set(courses)]
    mismatches = []
    missing = []
    checked = []
    for r in rows:
        rel = r.get("relative_path") or ""
        path = SOURCE_ROOT / rel
        expected = (r.get("sha256") or "").lower()
        rec = {"source_id": r.get("source_id"), "relative_path": rel, "expected": expected}
        if not path.is_file():
            missing.append(rec)
            continue
        actual = sha256_file(path)
        rec["actual"] = actual
        rec["ok"] = actual.lower() == expected
        checked.append(rec)
        if not rec["ok"]:
            mismatches.append(rec)
    status = "OK" if not missing and not mismatches else BLOCK
    return {
        "status": status,
        "courses": list(courses),
        "inventory_rows": len(rows),
        "checked": len(checked),
        "missing": missing,
        "mismatches": mismatches,
        "ok": status == "OK",
    }
