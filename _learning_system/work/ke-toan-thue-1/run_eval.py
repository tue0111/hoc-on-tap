# -*- coding: utf-8 -*-
"""Run scripts/v3_eval_course.py for ke-toan-thue-1 while the registry still says tier `catalog`
(the tier switch is Pha C's job; course_registry.yaml must not be edited in Pha B).
The tier is set to `retrieval` IN MEMORY ONLY for this process. Other W6b courses stay catalog.
usage: run_eval.py <tag>"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from retrieval import courses as C
for c in C.load_registry()["courses"]:
    if c["id"] == "ke-toan-thue-1":
        c["tier"] = "retrieval"
assert C.tier("ke-toan-thue-1") == "retrieval"
import v3_eval_course as E
sys.argv = ["v3_eval_course.py", "--course", "ke-toan-thue-1", "--tag", sys.argv[1] if len(sys.argv) > 1 else ""]
E.main()
