# -*- coding: utf-8 -*-
"""V3 mechanical concept candidate harvest (plan 6.4). usage: --course C -> work/C/concept_candidates.json"""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval import courses as C
from retrieval.config import SYSTEM

PATS = [
    ("chuong", re.compile(r"^\s*(Chương|CHƯƠNG)\s*\d+\s*[:.\-]\s*(.+)$")),
    ("chude", re.compile(r"^\s*(Chủ đề|CHỦ ĐỀ)\s*\d+(\.\d+)*\s*[:.\-]\s*(.+)$")),
    ("phan", re.compile(r"^\s*PHẦN\s*\d+\s*[:.\-]\s*(.+)$")),
]
ACC = re.compile(r"(?:TK|tài khoản)\s*(\d{3,5})")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--course", required=True)
    cid = ap.parse_args().course
    p = C.partition_paths(cid)
    docs = [json.loads(l) for l in p["documents"].open(encoding="utf-8")]
    pages = [json.loads(l) for l in p["pages"].open(encoding="utf-8")]
    out = {"course_id": cid, "unit_titles": [], "heading_lines": [], "outline_titles": [], "accounts": []}
    for d in docs:
        if d["unit_script"] or d["topic"]:
            out["unit_titles"].append({"source_id": d["source_id"], "chapter": d["chapter"], "topic": d["topic"],
                                       "title_from_filename": re.sub(r"[_\-]+", " ", Path(d["source_file"]).stem), "page": 1})
        for o in d.get("outline") or []:
            out["outline_titles"].append({"source_id": d["source_id"], "title": o["title"], "page": o.get("page")})
    heads = defaultdict(lambda: {"count": 0, "refs": []})
    acc = defaultdict(lambda: {"count": 0, "refs": set()})
    for pg in pages:
        if not pg["index_include"] and pg.get("combined_duplicate") is False:
            pass
        for ln in pg["text"].splitlines():
            for kind, rx in PATS:
                m = rx.match(ln)
                if m:
                    k = (kind, ln.strip())
                    heads[k]["count"] += 1
                    if len(heads[k]["refs"]) < 3: heads[k]["refs"].append({"source_id": pg["source_id"], "page": pg["page"]})
        if pg["index_include"]:
            for a in ACC.findall(pg["text"]):
                acc[a]["count"] += 1; acc[a]["refs"].add((pg["source_id"], pg["page"]))
    out["heading_lines"] = [{"kind": k[0], "line": k[1], **v} for k, v in sorted(heads.items(), key=lambda x: -x[1]["count"])]
    out["accounts"] = [{"account": a, "count": v["count"], "refs": sorted(v["refs"])[:3]} for a, v in sorted(acc.items(), key=lambda x: -x[1]["count"])]
    w = SYSTEM / "work" / cid; w.mkdir(parents=True, exist_ok=True)
    (w / "concept_candidates.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("units", len(out["unit_titles"]), "headings", len(out["heading_lines"]), "outline", len(out["outline_titles"]), "accounts", len(out["accounts"]))


if __name__ == "__main__":
    main()
