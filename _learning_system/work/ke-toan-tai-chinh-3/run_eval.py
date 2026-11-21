# Runs scripts/v3_eval_course.py unchanged for ke-toan-tai-chinh-3 with the course's tier set to
# "retrieval" IN MEMORY ONLY (course_registry.yaml is not modified; the tier switch is a Pha C step).
# usage: python work/ke-toan-tai-chinh-3/run_eval.py <tag>
import sys
from pathlib import Path
SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
from retrieval import courses as C
CID = "ke-toan-tai-chinh-3"
for c in C.load_registry()["courses"]:
    if c["id"] == CID:
        c["tier"] = "retrieval"
assert C.tier(CID) == "retrieval"
import scripts.v3_eval_course as E
sys.argv = ["v3_eval_course.py", "--course", CID, "--tag", sys.argv[1] if len(sys.argv) > 1 else ""]
E.main()
