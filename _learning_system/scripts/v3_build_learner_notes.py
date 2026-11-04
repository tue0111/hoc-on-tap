# -*- coding: utf-8 -*-
"""Build the isolated learner-notes chunks/index and assert curriculum isolation."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval import courses as C
from retrieval.chunking import pages_to_units
from retrieval.config import CHUNKING_VERSION, SYSTEM
from retrieval.index import build_index
from retrieval.textutil import content_hash

PARTITION_ID = "learner-notes"
PARTITION_FIELD = "learner_notes"


def main() -> None:
    paths = C.partition_paths(PARTITION_ID)
    docs = {}
    with paths["documents"].open(encoding="utf-8") as handle:
        for line in handle:
            doc = json.loads(line)
            docs[doc["document_id"]] = doc
    by_doc = {}
    with paths["pages"].open(encoding="utf-8") as handle:
        for line in handle:
            page = json.loads(line)
            by_doc.setdefault(page["document_id"], []).append(page)

    chunks = []
    for document_id, pages in by_doc.items():
        doc = docs[document_id]
        if not doc.get("index_include"):
            continue
        pages.sort(key=lambda row: row["page"])
        for number, unit in enumerate(pages_to_units(pages), start=1):
            if len(unit["text"]) < 80:
                continue
            chunks.append(
                {
                    "chunk_id": f"chk-ln-{doc['source_id']}-{number:04d}",
                    "parent_id": f"par-ln-{doc['source_id']}",
                    "document_id": document_id,
                    "source_id": doc["source_id"],
                    "course_id": doc["course_id"],
                    "course_name": doc["course_name"],
                    "course_code": doc.get("course_code"),
                    "partition": PARTITION_FIELD,
                    "source_file": doc["source_file"],
                    "relative_path": doc["relative_path"],
                    "source_type": doc["source_type"],
                    "content_role": "learner_material",
                    "authority": 7,
                    "chapter": doc.get("chapter"),
                    "topic": doc.get("topic"),
                    "section": unit.get("heading") or doc.get("topic"),
                    "page_start": unit["page_start"],
                    "page_end": unit["page_end"],
                    "page_range": f"{unit['page_start']}-{unit['page_end']}" if unit["page_start"] else None,
                    "text": unit["text"],
                    "char_count": len(unit["text"]),
                    "concept_ids": [],
                    "concept_map": [],
                    "parse_quality": doc.get("parse_quality"),
                    "content_hash": content_hash(unit["text"]),
                    "dup_group": None,
                    "chunking_version": CHUNKING_VERSION,
                    "provenance": {"source_sha256": doc.get("source_sha256"), "document_id": document_id},
                }
            )

    paths["chunks"].parent.mkdir(parents=True, exist_ok=True)
    with paths["chunks"].open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    meta = {
        "chunking_version": CHUNKING_VERSION,
        "chunk_count": len(chunks),
        "partition": PARTITION_FIELD,
        "by_course": {},
        "by_source_type": {},
    }
    for chunk in chunks:
        cid = chunk["course_id"]
        source_type = chunk["source_type"]
        meta["by_course"][cid] = meta["by_course"].get(cid, 0) + 1
        meta["by_source_type"][source_type] = meta["by_source_type"].get(source_type, 0) + 1
    paths["chunks_meta"].write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    result = build_index(
        paths["chunks"],
        paths["index_dir"],
        meta_extra={
            "partition": PARTITION_FIELD,
            "index_version": "3.0.0",
            "extract_version": "3.0.0",
            "concept_table_version": None,
        },
    )

    indexed = [doc for doc in docs.values() if doc.get("index_include")]
    represented = {chunk["source_id"] for chunk in chunks}
    missing = [doc["source_id"] for doc in indexed if doc["source_id"] not in represented]
    inventory = json.loads((SYSTEM / "inventory" / "files.json").read_text(encoding="utf-8"))
    known_hashes = {row["sha256"] for row in inventory}
    bad_hashes = [digest for digest in result["meta"]["source_hashes"] if digest not in known_hashes]

    contamination = []
    for chunk_file in sorted((SYSTEM / "data" / "chunks").glob("*.chunks.jsonl")):
        if chunk_file == paths["chunks"]:
            continue
        with chunk_file.open(encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                chunk = json.loads(line)
                if chunk.get("content_role") == "learner_material" or chunk.get("partition") == PARTITION_FIELD:
                    contamination.append(f"{chunk_file.name}:{line_no}:{chunk.get('source_id')}")

    print(
        "chunks", len(chunks),
        "vocab", result["meta"]["vocab_size"],
        "docs_without_chunk", missing,
        "hash_not_in_inventory", bad_hashes,
        "course_partition_contamination", contamination,
    )
    if not chunks or missing or bad_hashes or contamination:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
