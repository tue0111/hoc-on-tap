# -*- coding: utf-8 -*-
"""Run scripts/v3_validate_concepts.py for this course.
The shared validator's PREFIX table predates W6b and has no entry for the new course
(PREFIX.get() -> None -> TypeError). Phase B may not edit shared scripts, so the prefix is
added IN MEMORY only; every other check runs unchanged. Phase C should add
"he-thong-thong-tin-ke-toan-1": "httt1" to PREFIX in the script.
"""
import sys
from pathlib import Path

SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
import scripts.v3_validate_concepts as V  # noqa: E402

V.PREFIX["he-thong-thong-tin-ke-toan-1"] = "httt1"
sys.argv = ["v3_validate_concepts.py", "--course", "he-thong-thong-tin-ke-toan-1"]
V.main()
