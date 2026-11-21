# -*- coding: utf-8 -*-
"""Supplementary dedupe evidence (spec 7.3 metric, read-only on documents).
v3_dedupe.py compares chapter docs vs _nguon unit scripts; this course has no _nguon folder,
so it yields 0 pairs. Here every pair of extracted docs in the same chapter (and the summary /
exam / Tailieuthamkhao vs the scripts) is scored with the SAME compare() (8-shingle cov/back).
Writes reports/v3/he-thong-thong-tin-ke-toan-1_dedupe_pairwise.json. Changes no document.
"""
import json, sys
from itertools import permutations
from pathlib import Path

SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
from scripts.v3_dedupe import compare  # noqa: E402
from retrieval import courses as C  # noqa: E402

CID = "he-thong-thong-tin-ke-toan-1"
docs = [json.loads(l) for l in C.partition_paths(CID)["documents"].open(encoding="utf-8")]
ok = [d for d in docs if d["extract_ok"] and d["char_count"] > 0]
pairs = []
for a, b in permutations(ok, 2):
    same_ch = a["chapter"] is not None and a["chapter"] == b["chapter"]
    if not same_ch and a["chapter"] is not None and b["chapter"] is not None:
        continue
    r = compare(a, [b]); r["scope"] = f"pair ch{a['chapter']}|ch{b['chapter']}"
    r["upper_path"] = a["relative_path"]; r["lower_path"] = b["relative_path"]
    pairs.append(r)
flag = [r for r in pairs if r["decision"] != "both_canonical"]
out = {"course_id": CID, "note": __doc__, "pairs_scored": len(pairs), "non_distinct": flag,
       "max_cov": max((r["cov"] for r in pairs), default=0),
       "pairs": sorted(pairs, key=lambda r: -r["cov"])[:40]}
(SYS / "reports" / "v3" / f"{CID}_dedupe_pairwise.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print("pairs", len(pairs), "non_distinct", [(r["upper"], r["lowers"], r["cov"], r["back"], r["decision"]) for r in flag])
for r in out["pairs"][:8]:
    print(r["upper"], r["lowers"], r["cov"], r["back"], r["decision"])
