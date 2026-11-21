# -*- coding: utf-8 -*-
"""Run scripts/v3_eval_course.py for this course with its tier set to `retrieval` IN MEMORY only.
The registry file is not touched (W6b phase B); a catalog course would otherwise return
course_not_indexed for every row. Same approach as scripts/v3_r1_check.py (--candidates).
usage: run_eval.py <tag>   -> reports/v3/he-thong-thong-tin-ke-toan-1_eval<tag>.json/.md
"""
import sys
from pathlib import Path

SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
from retrieval import courses as C  # noqa: E402

CID = "he-thong-thong-tin-ke-toan-1"
C.get_course(CID)["tier"] = "retrieval"
import scripts.v3_eval_course as E  # noqa: E402

sys.argv = ["v3_eval_course.py", "--course", CID, "--tag", sys.argv[1] if len(sys.argv) > 1 else ""]
E.main()
