# -*- coding: utf-8 -*-
"""V3 partition build for one course (plan 6.6): chunk (unchanged pages_to_units) + index 3.0.0."""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval import courses as C
from retrieval.chunking import pages_to_units
from retrieval.concepts import map_text_course
from retrieval.config import CHUNKING_VERSION, SYSTEM
from retrieval.index import build_index
from retrieval.textutil import content_hash, nfc
from scripts.v3_dedupe import norm_tokens, shingles


def jacc(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--course", required=True)
    cid = ap.parse_args().course
    p = C.partition_paths(cid)
    docs = {}
    for l in p["documents"].open(encoding="utf-8"):
        d = json.loads(l); docs[d["document_id"]] = d
    by_doc = {}
    for l in p["pages"].open(encoding="utf-8"):
        pg = json.loads(l); by_doc.setdefault(pg["document_id"], []).append(pg)
    chunks = []
    for doc_id, pages in by_doc.items():
        doc = docs[doc_id]
        if not doc.get("index_include"):
            continue
        pages.sort(key=lambda x: x["page"])
        for i, u in enumerate(pages_to_units(pages), start=1):
            if len(u["text"]) < 80:
                continue
            maps = map_text_course(u["text"], cid)
            chunks.append({
                "chunk_id": f"chk-{doc['source_id']}-{i:04d}", "parent_id": f"par-{doc['source_id']}", "document_id": doc_id,
                "source_id": doc["source_id"], "course_id": cid, "course_name": doc["course_name"], "course_code": doc.get("course_code"),
                "source_file": doc["source_file"], "relative_path": doc["relative_path"], "source_type": doc["source_type"],
                "content_role": doc.get("content_role"), "authority": doc["authority"], "chapter": doc.get("chapter"),
                "topic": doc.get("topic"), "unit_script": doc.get("unit_script"), "section": u.get("heading") or doc.get("topic"),
                "page_start": u["page_start"], "page_end": u["page_end"],
                "page_range": f"{u['page_start']}-{u['page_end']}" if u["page_start"] else None,
                "text": u["text"], "char_count": len(u["text"]), "concept_ids": [m["concept_id"] for m in maps], "concept_map": maps,
                "parse_quality": doc.get("parse_quality"), "content_hash": content_hash(u["text"]), "dup_group": None,
                "chunking_version": CHUNKING_VERSION,
                "provenance": {"source_sha256": doc.get("source_sha256"), "document_id": doc_id},
            })
    # chunk-level dedupe for mid-band chapters (spec 7.3)
    rep = SYSTEM / "reports" / "v3" / f"{cid}_dedupe.json"
    groups = 0
    if rep.exists():
        dd = json.loads(rep.read_text(encoding="utf-8"))
        for pr in dd["pairs"]:
            if pr["decision"] != "both_indexed_chunk_dedupe":
                continue
            ups = [c for c in chunks if c["source_id"] == pr["upper"]]
            lows = [c for c in chunks if c["source_id"] in set(pr["lowers"])]
            ls = [(c, set(shingles(norm_tokens(c["text"])))) for c in lows]
            for u in ups:
                su = set(shingles(norm_tokens(u["text"])))
                best = max(((jacc(su, s), c) for c, s in ls), key=lambda x: x[0], default=(0, None))
                if best[0] >= 0.6:
                    g = best[1]["dup_group"] or f"dg-{cid}-{groups + 1:04d}"
                    if not best[1]["dup_group"]: groups += 1
                    best[1]["dup_group"] = g; u["dup_group"] = g
    p["chunks"].parent.mkdir(parents=True, exist_ok=True)
    with p["chunks"].open("w", encoding="utf-8") as f:
        for c in chunks: f.write(json.dumps(c, ensure_ascii=False) + "\n")
    meta = {"chunking_version": CHUNKING_VERSION, "chunk_count": len(chunks), "course_id": cid, "dup_groups": groups,
            "by_source_type": {}}
    for c in chunks: meta["by_source_type"][c["source_type"]] = meta["by_source_type"].get(c["source_type"], 0) + 1
    p["chunks_meta"].write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    ctv = hashlib.sha256(p["concepts"].read_bytes()).hexdigest()[:12] if p["concepts"].exists() else None
    res = build_index(p["chunks"], p["index_dir"], meta_extra={"course_id": cid, "index_version": "3.0.0",
                      "extract_version": "3.0.0", "concept_table_version": ctv})
    # checks
    indexed = [d for d in docs.values() if d.get("index_include")]
    have = {c["source_id"] for c in chunks}
    missing = [d["source_id"] for d in indexed if d["source_id"] not in have]
    inv = {r["sha256"] for r in json.loads((SYSTEM / "inventory" / "files.json").read_text(encoding="utf-8"))}
    bad_hash = [h for h in res["meta"]["source_hashes"] if h not in inv]
    print("chunks", len(chunks), "vocab", res["meta"]["vocab_size"], "dup_groups", groups, "docs_without_chunk", missing, "hash_not_in_inventory", bad_hash)
    if not chunks or missing or bad_hash: sys.exit(1)


if __name__ == "__main__":
    main()
