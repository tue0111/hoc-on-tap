# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from retrieval.config import CHUNKS_DIR, INDEX_DIR, INDEX_VERSION, CHUNKING_VERSION, EXTRACT_VERSION
from retrieval.textutil import tokenize


def _load_chunks(path=None) -> list[dict]:
    path = Path(path) if path else CHUNKS_DIR / "nlkt_kttc1.chunks.jsonl"
    chunks = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def build_index(chunks_path=None, index_dir=None, meta_extra: dict | None = None) -> dict:
    INDEX_DIR_ = Path(index_dir) if index_dir else INDEX_DIR
    chunks = _load_chunks(chunks_path)
    tokenized = [tokenize(c["text"]) for c in chunks]
    df = Counter()
    for toks in tokenized:
        df.update(set(toks))
    vocab = {t: i for i, t in enumerate(sorted(df))}
    n = len(chunks)
    avgdl = sum(len(t) for t in tokenized) / max(n, 1)

    # sparse bm25 postings: term -> list[(chunk_idx, tf)]
    postings = defaultdict(list)
    tfs = []
    for i, toks in enumerate(tokenized):
        tf = Counter(toks)
        tfs.append(tf)
        for term, f in tf.items():
            postings[term].append((i, f))

    # tf-idf dense is too large if vocab huge; store as sparse lists
    idf = {}
    for t, dfi in df.items():
        idf[t] = math.log((n - dfi + 0.5) / (dfi + 0.5) + 1.0)

    # l2-normalized tf-idf vectors as dict[term]=weight per chunk
    tfidf_vecs = []
    for tf in tfs:
        vec = {}
        for t, f in tf.items():
            vec[t] = (1 + math.log(f)) * idf[t]
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        tfidf_vecs.append({t: v / norm for t, v in vec.items()})

    INDEX_DIR_.mkdir(parents=True, exist_ok=True)
    # store lightweight arrays
    meta = {
        "index_version": INDEX_VERSION,
        "chunking_version": CHUNKING_VERSION,
        "extract_version": EXTRACT_VERSION,
        "build_date": datetime.now(timezone.utc).isoformat(),
        "chunk_count": n,
        "vocab_size": len(vocab),
        "avgdl": avgdl,
        "k1": 1.5,
        "b": 0.75,
        "courses": sorted({c["course_id"] for c in chunks}),
        "source_hashes": sorted({c["provenance"]["source_sha256"] for c in chunks if c.get("provenance")}),
        "embedding": None,
        "lexical": "bm25",
        "semantic": "tfidf_cosine_numpy",
        "concept_registry_version": "0.1.0",
    }
    if meta_extra:
        meta.update(meta_extra)
    (INDEX_DIR_ / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    # persist bm25/tfidf as jsonl sidecar (chunk-aligned)
    side = []
    for i, c in enumerate(chunks):
        side.append(
            {
                "chunk_id": c["chunk_id"],
                "dl": len(tokenized[i]),
                "tf": tfs[i],
                "tfidf": tfidf_vecs[i],
            }
        )
    with (INDEX_DIR_ / "vectors.jsonl").open("w", encoding="utf-8") as f:
        for row in side:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    (INDEX_DIR_ / "idf.json").write_text(json.dumps(idf, ensure_ascii=False), encoding="utf-8")
    # copy chunk ids order
    (INDEX_DIR_ / "chunk_ids.json").write_text(
        json.dumps([c["chunk_id"] for c in chunks], ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"meta": meta, "chunks": chunks, "idf": idf, "vectors": side, "avgdl": avgdl}


class Index:
    def __init__(self, chunks_path=None, index_dir=None):
        d = Path(index_dir) if index_dir else INDEX_DIR
        self.meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        self.chunk_ids = json.loads((d / "chunk_ids.json").read_text(encoding="utf-8"))
        self.idf = json.loads((d / "idf.json").read_text(encoding="utf-8"))
        self.avgdl = self.meta["avgdl"]
        self.k1 = self.meta.get("k1", 1.5)
        self.b = self.meta.get("b", 0.75)
        self.chunks = _load_chunks(chunks_path)
        self.by_id = {c["chunk_id"]: c for c in self.chunks}
        self.vectors = []
        with (d / "vectors.jsonl").open(encoding="utf-8") as f:
            for line in f:
                self.vectors.append(json.loads(line))
        assert len(self.vectors) == len(self.chunks)

    def bm25(self, query_tokens: list[str]) -> np.ndarray:
        n = len(self.chunks)
        scores = np.zeros(n, dtype=np.float64)
        qtf = Counter(query_tokens)
        for term, qf in qtf.items():
            idf = self.idf.get(term)
            if not idf:
                continue
            for i, vec in enumerate(self.vectors):
                f = vec["tf"].get(term, 0)
                if not f:
                    continue
                dl = vec["dl"] or 1
                denom = f + self.k1 * (1 - self.b + self.b * dl / (self.avgdl or 1))
                scores[i] += idf * (f * (self.k1 + 1) / denom)
        return scores

    def tfidf_cosine(self, query_tokens: list[str]) -> np.ndarray:
        qtf = Counter(query_tokens)
        qvec = {}
        for t, f in qtf.items():
            if t in self.idf:
                qvec[t] = (1 + math_log(f)) * self.idf[t]
        qn = math.sqrt(sum(v * v for v in qvec.values())) or 1.0
        for t in list(qvec):
            qvec[t] /= qn
        n = len(self.chunks)
        scores = np.zeros(n, dtype=np.float64)
        for i, vec in enumerate(self.vectors):
            acc = 0.0
            tv = vec["tfidf"]
            # iterate smaller
            if len(qvec) < len(tv):
                for t, w in qvec.items():
                    acc += w * tv.get(t, 0.0)
            else:
                for t, w in tv.items():
                    acc += w * qvec.get(t, 0.0)
            scores[i] = acc
        return scores


def math_log(x: float) -> float:
    return math.log(x)
