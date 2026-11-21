"""In-memory overlay runner for the W6b phase-B session of ke-toan-hanh-chinh-su-nghiep.

Phase B may not edit shared files (course_registry.yaml, scripts/v3_validate_concepts.py).
This wrapper changes nothing on disk; inside this process only it
  * sets tier of COURSE to "retrieval" (so retrieve() routes to the partition, as it will after phase C1),
  * adds the id prefix "kthcsn" to the validator's PREFIX table (spec 7.4 list predates W6b).
usage: python work/ke-toan-hanh-chinh-su-nghiep/overlay_run.py <validate|eval> [script args...]
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
COURSE = "ke-toan-hanh-chinh-su-nghiep"

from retrieval import courses as C  # noqa: E402

reg = C.load_registry()  # cached dict; mutate in memory only
for c in reg["courses"]:
    if c["id"] == COURSE:
        c["tier"] = "retrieval"
C._by_id.cache_clear(); C._alias_map.cache_clear(); C._cue_table.cache_clear()
assert C.tier(COURSE) == "retrieval"

cmd, rest = sys.argv[1], sys.argv[2:]
if cmd == "validate":
    import scripts.v3_validate_concepts as V
    V.PREFIX[COURSE] = "kthcsn"
    sys.argv = ["v3_validate_concepts.py"] + rest
    V.main()
elif cmd == "eval":
    sys.argv = ["v3_eval_course.py"] + rest
    runpy.run_path(str(ROOT / "scripts" / "v3_eval_course.py"), run_name="__main__")
else:
    sys.exit(f"unknown cmd {cmd}")
