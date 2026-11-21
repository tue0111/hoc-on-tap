# -*- coding: utf-8 -*-
"""Post-extract metadata for he-thong-thong-tin-ke-toan-1 (own normalized files only).
Script PDFs are named script.pdf / script (n).pdf, so the filename carries no topic.
Topic is taken from the first-page line "Chủ đề k: <title>" -> "<chapter>.<k>" (topic_rule
page1_chude_line). Chapter stays the inventory apparent_chapter. Idempotent; rerun after extract.
"""
import json, re, sys
from pathlib import Path

SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
from retrieval import courses as C  # noqa: E402

CID = "he-thong-thong-tin-ke-toan-1"
P = C.partition_paths(CID)
RX = re.compile(r"^\s*Chủ đề\s*(\d+)\s*:\s*(.+?)\s*$", re.M)
docs = [json.loads(l) for l in P["documents"].open(encoding="utf-8")]
topics = {}
for d in docs:
    if d["source_type"] != "lecture_note" or not d["extract_ok"] or d["chapter"] is None:
        continue
    first = d["text"].split("----- PAGE 2 -----")[0]
    m = RX.search(first)
    if m:
        d["topic"] = f"{d['chapter']}.{m[1]}"; d["topic_title"] = m[2]; d["topic_rule"] = "page1_chude_line"
    else:  # single-topic chapters (Ch0, Ch1): chapter title line
        m2 = re.search(r"^\s*Chương[^:\n]*:\s*(.+?)\s*$", first, re.M)
        d["topic"] = f"{d['chapter']}"; d["topic_title"] = m2[1] if m2 else None; d["topic_rule"] = "page1_chapter_line"
    topics[d["source_id"]] = (d["topic"], d["topic_title"])
with P["documents"].open("w", encoding="utf-8") as f:
    for d in docs: f.write(json.dumps(d, ensure_ascii=False) + "\n")
pages = [json.loads(l) for l in P["pages"].open(encoding="utf-8")]
for p in pages:
    if p["source_id"] in topics: p["topic"] = topics[p["source_id"]][0]
with P["pages"].open("w", encoding="utf-8") as f:
    for p in pages: f.write(json.dumps(p, ensure_ascii=False) + "\n")
for s, t in sorted(topics.items()): print(s, t)
