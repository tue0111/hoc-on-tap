# -*- coding: utf-8 -*-
"""V3 concept table validator (plan spec 7.4). usage: --course C. Exit 0 on pass."""
from __future__ import annotations
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval import courses as C
from retrieval.config import CONCEPT_REGISTRY, SYSTEM
from retrieval.textutil import fold

PREFIX = {"ke-toan-tai-chinh-2": "kttc2", "ke-toan-chi-phi": "ktcp", "kiem-toan-1": "kt1", "ke-toan-ngan-hang": "ktnh",
          "ngan-hang-thuong-mai": "nhtm", "tai-chinh-doanh-nghiep-1": "tcdn1", "thi-truong-tai-chinh": "tttc",
          "tai-chinh-hanh-chinh-su-nghiep": "hcsn", "luat-kinh-doanh": "lkd", "kinh-doanh-va-nghiep-vu": "kdnv"}
T = lambda s: fold(re.sub(r"\s+", " ", s or ""))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--course", required=True)
    cid = ap.parse_args().course
    errs = []
    p = C.partition_paths(cid)
    doc = yaml.safe_load(p["concepts"].read_text(encoding="utf-8"))
    pages = [json.loads(l) for l in p["pages"].open(encoding="utf-8")]
    ptxt = {}
    for pg in pages: ptxt[(pg["source_id"], pg["page"])] = T(pg["text"])
    alltxt = list(ptxt.values())
    core = {c["concept_id"] for c in yaml.safe_load(CONCEPT_REGISTRY.read_text(encoding="utf-8"))["concepts"]}
    other = set()
    for f in (SYSTEM / "curriculum" / "concepts").glob("*.yaml"):
        if f.stem != cid:
            other |= {c["concept_id"] for c in (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("concepts") or []}
    if doc.get("course_id") != cid: errs.append("course_id mismatch")
    pre = PREFIX.get(cid)
    if doc.get("id_prefix") != pre: errs.append(f"id_prefix {doc.get('id_prefix')} != {pre}")
    ids = [c["concept_id"] for c in doc["concepts"]]
    for i, n in Counter(ids).items():
        if n > 1: errs.append(f"duplicate id {i}")
    for i in ids:
        if i in core or i in other: errs.append(f"id collides with another registry: {i}")
        if not i.startswith(pre + "-"): errs.append(f"bad prefix {i}")
    if not 15 <= len(ids) <= 40: errs.append(f"concept count {len(ids)} outside 15-40")
    seen_alias = {}
    for c in doc["concepts"]:
        cn = c["concept_id"]
        for k in ("canonical_name", "aliases", "chapter", "evidence_status"):
            if k not in c: errs.append(f"{cn}: missing {k}")
        names = [c["canonical_name"]] + list(c.get("aliases") or [])
        for n in names:
            fn = T(n)
            if not any(fn in t for t in alltxt): errs.append(f"{cn}: '{n}' not found in course text")
        for a in c.get("aliases") or []:
            fa = T(a)
            if len(fa) < 6 and not (a.isupper() and any(fa in t for t in alltxt)): errs.append(f"{cn}: alias too short '{a}'")
            if fa in seen_alias and seen_alias[fa] != cn: errs.append(f"alias '{a}' shared by {cn} and {seen_alias[fa]}")
            seen_alias[fa] = cn
        if c.get("same_as") and c["same_as"] not in core: errs.append(f"{cn}: same_as {c['same_as']} not in core registry")
        for r in c.get("source_refs") or []:
            t = ptxt.get((r["source_id"], r["page"]))
            if t is None or not any(T(n) in t for n in names): errs.append(f"{cn}: source_ref {r} does not contain name/alias")
        if c.get("evidence_status") not in ("OBSERVED", "INFERRED", "UNKNOWN"): errs.append(f"{cn}: bad evidence_status")
    for a, tgt in (doc.get("account_map") or {}).items():
        if tgt not in ids: errs.append(f"account_map {a} -> unknown {tgt}")
    for e in doc.get("edges") or []:
        t = ptxt.get((e.get("source_id"), e.get("page")))
        if t is None or T(e.get("quote")) not in t: errs.append(f"edge quote not found: {e}")
        for k in ("from", "to"):
            if e.get(k) not in ids: errs.append(f"edge {k} unknown: {e}")
    print("VALIDATOR", "PASS" if not errs else "FAIL", len(ids), "concepts")
    for e in errs: print(" -", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
