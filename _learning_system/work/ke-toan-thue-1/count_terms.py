# -*- coding: utf-8 -*-
import json, re, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from retrieval.textutil import fold
T = lambda s: fold(re.sub(r"\s+", " ", s or ""))
pages = [json.loads(l) for l in open(Path(__file__).resolve().parents[2] / "data/normalized/ke-toan-thue-1.pages.jsonl", encoding="utf-8")]
for term in sys.argv[1:]:
    ft = T(term); hits = Counter()
    for p in pages:
        n = T(p["text"]).count(ft)
        if n: hits[(p["source_id"], p["page"])] += n
    tot = sum(hits.values())
    print(f"{tot:4d} {term!r} :", ", ".join(f"{s}p{pg}x{n}" for (s, pg), n in sorted(hits.items())[:8]))
