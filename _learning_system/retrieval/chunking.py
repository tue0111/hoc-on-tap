# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import re
from pathlib import Path

from retrieval.concepts import map_text
from retrieval.config import (
    CHUNKS_DIR,
    CHUNKING_VERSION,
    MAX_CHUNK_CHARS,
    MIN_CHUNK_CHARS,
    NORMALIZED,
    TARGET_CHUNK_CHARS,
)
from retrieval.textutil import content_hash, nfc

HEADING_RE = re.compile(
    r"(?i)^\s*(?:"
    r"chương\s*\d+|"
    r"chuong\s*\d+|"
    r"chủ đề\s*\d|"
    r"chu de\s*\d|"
    r"slide\s*\d+|"
    r"mục tiêu|"
    r"nội dung|"
    r"phần\s*\d+"
    r").{0,120}$"
)


def _heading_kind(line: str) -> str | None:
    s = line.strip()
    if not s or len(s) > 140:
        return None
    if HEADING_RE.match(s):
        return "heading"
    return None


def pages_to_units(pages: list[dict]) -> list[dict]:
    """Split each page into heading-bounded blocks, then pack to target size."""
    units = []
    current_heading = pages[0].get("topic") if pages else None
    buf = []
    buf_pages = []
    buf_chars = 0

    def flush():
        nonlocal buf, buf_pages, buf_chars
        if not buf:
            return
        text = nfc("\n".join(buf).strip())
        if not text:
            buf, buf_pages, buf_chars = [], [], 0
            return
        units.append(
            {
                "text": text,
                "heading": current_heading,
                "page_start": min(buf_pages) if buf_pages else None,
                "page_end": max(buf_pages) if buf_pages else None,
            }
        )
        buf, buf_pages, buf_chars = [], [], 0

    for p in pages:
        page_no = p["page"]
        raw = nfc(p.get("text") or "")
        if not raw.strip():
            continue
        lines = raw.splitlines()
        for line in lines:
            kind = _heading_kind(line)
            if kind and buf_chars >= MIN_CHUNK_CHARS:
                flush()
                current_heading = line.strip()
            candidate = line.rstrip()
            if not candidate:
                continue
            # keep definition with its following paragraph: only flush on size
            if buf_chars + len(candidate) + 1 > MAX_CHUNK_CHARS and buf_chars >= MIN_CHUNK_CHARS:
                flush()
            buf.append(candidate)
            buf_pages.append(page_no)
            buf_chars += len(candidate) + 1
            if buf_chars >= TARGET_CHUNK_CHARS and not candidate.endswith((",", ":", ";")):
                # don't split if line looks like a list start
                flush()
        # page boundary is a soft split if large enough
        if buf_chars >= TARGET_CHUNK_CHARS:
            flush()
    flush()
    return units


def build_chunks() -> list[dict]:
    pages_path = NORMALIZED / "nlkt_kttc1.pages.jsonl"
    docs_path = NORMALIZED / "nlkt_kttc1.documents.jsonl"
    docs = {}
    with docs_path.open(encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            docs[d["document_id"]] = d
    by_doc: dict[str, list] = {}
    with pages_path.open(encoding="utf-8") as f:
        for line in f:
            p = json.loads(line)
            by_doc.setdefault(p["document_id"], []).append(p)

    chunks = []
    n = 0
    for doc_id, pages in by_doc.items():
        pages.sort(key=lambda x: x["page"])
        doc = docs[doc_id]
        if not doc.get("index_include"):
            continue
        units = pages_to_units(pages)
        parent_id = f"par-{doc['source_id']}"
        for i, u in enumerate(units, start=1):
            if len(u["text"]) < 80:
                continue
            n += 1
            maps = map_text(u["text"])
            heading = u.get("heading") or doc.get("topic")
            chunk = {
                "chunk_id": f"chk-{doc['source_id']}-{i:04d}",
                "parent_id": parent_id,
                "document_id": doc_id,
                "source_id": doc["source_id"],
                "course_id": doc["course_id"],
                "course_name": doc["course_name"],
                "course_code": doc["course_code"],
                "source_file": doc["source_file"],
                "relative_path": doc["relative_path"],
                "source_type": doc["source_type"],
                "content_role": doc.get("content_role"),
                "authority": doc["authority"],
                "chapter": doc.get("chapter"),
                "topic": doc.get("topic"),
                "section": heading,
                "page_start": u["page_start"],
                "page_end": u["page_end"],
                "page_range": f"{u['page_start']}-{u['page_end']}" if u["page_start"] else None,
                "text": u["text"],
                "char_count": len(u["text"]),
                "concept_ids": [m["concept_id"] for m in maps],
                "concept_map": maps,
                "parse_quality": doc.get("parse_quality"),
                "content_hash": content_hash(u["text"]),
                "chunking_version": CHUNKING_VERSION,
                "provenance": {
                    "source_sha256": doc.get("source_sha256"),
                    "document_id": doc_id,
                },
            }
            chunks.append(chunk)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    out = CHUNKS_DIR / "nlkt_kttc1.chunks.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    meta = {
        "chunking_version": CHUNKING_VERSION,
        "chunk_count": len(chunks),
        "by_course": {},
        "by_source_type": {},
    }
    for c in chunks:
        meta["by_course"][c["course_id"]] = meta["by_course"].get(c["course_id"], 0) + 1
        meta["by_source_type"][c["source_type"]] = meta["by_source_type"].get(c["source_type"], 0) + 1
    (CHUNKS_DIR / "nlkt_kttc1.chunks.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return chunks
