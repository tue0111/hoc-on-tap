# -*- coding: utf-8 -*-
from __future__ import annotations
import uuid
from datetime import datetime, timezone

import numpy as np

from retrieval.analyze import analyze_question
from retrieval.concepts import prerequisite_concepts
from retrieval.config import HYBRID_WEIGHTS, PREREQ_TOP_K, TOP_K_DEFAULT
from retrieval.index import Index
from retrieval.textutil import tokenize

_INDEX: Index | None = None


def get_index() -> Index:
    global _INDEX
    if _INDEX is None:
        _INDEX = Index()
    return _INDEX


def _minmax(arr: np.ndarray) -> np.ndarray:
    mx = float(arr.max()) if len(arr) else 0.0
    mn = float(arr.min()) if len(arr) else 0.0
    if mx - mn < 1e-12:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)


def _mask(chunks: list[dict], analysis: dict, mode: str, for_prereq: bool = False) -> np.ndarray:
    n = len(chunks)
    m = np.ones(n, dtype=bool)
    scope = analysis["course_scope"]
    chapter = analysis.get("chapter")
    source_type = analysis.get("source_type")

    if for_prereq:
        # NLKT only
        m &= np.array([c["course_id"] == "nguyen-ly-ke-toan" for c in chunks])
        return m

    if mode == "current_course":
        if scope in {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"}:
            m &= np.array([c["course_id"] == scope for c in chunks])
        # unknown: do not filter course (ambiguous) — later contamination tests expect this
    elif mode == "source_bound":
        if scope in {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"}:
            m &= np.array([c["course_id"] == scope for c in chunks])
        if chapter is not None:
            m &= np.array([c.get("chapter") == chapter for c in chunks])
        if source_type:
            m &= np.array([c.get("source_type") == source_type for c in chunks])
    elif mode == "prerequisite_recovery":
        # main evidence stays in current course (KTTC1 default)
        current = scope if scope in {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"} else "ke-toan-tai-chinh-1"
        m &= np.array([c["course_id"] == current for c in chunks])
    elif mode == "cross_course":
        m &= np.array([c["course_id"] in {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"} for c in chunks])

    if source_type and mode != "cross_course":
        # apply only if not already applied
        if mode == "current_course":
            m &= np.array([c.get("source_type") == source_type for c in chunks])
    if chapter is not None and mode in {"current_course"}:
        # soft: don't hard-filter chapter in current_course unless source_bound
        pass
    return m


def _concept_score(chunks: list[dict], concepts: list[str]) -> np.ndarray:
    n = len(chunks)
    s = np.zeros(n, dtype=np.float64)
    if not concepts:
        return s
    cset = set(concepts)
    for i, ch in enumerate(chunks):
        hit = cset.intersection(ch.get("concept_ids") or [])
        if hit:
            s[i] = len(hit) / max(len(cset), 1)
    return s


def _metadata_score(chunks: list[dict], analysis: dict) -> np.ndarray:
    n = len(chunks)
    s = np.zeros(n, dtype=np.float64)
    chapter = analysis.get("chapter")
    concepts = set(analysis.get("detected_concepts") or [])
    for i, ch in enumerate(chunks):
        score = 0.0
        if chapter is not None and ch.get("chapter") == chapter:
            score += 0.6
        if concepts and concepts.intersection(ch.get("concept_ids") or []):
            score += 0.4
        # prefer lecture notes over combined/exam unless exam asked
        if analysis.get("intent") == "source_lookup" and analysis.get("source_type"):
            if ch.get("source_type") == analysis["source_type"]:
                score += 0.5
        s[i] = score
    return s


def _authority_score(chunks: list[dict]) -> np.ndarray:
    # lower rank is better (1 syllabus ... 8 unknown)
    n = len(chunks)
    s = np.zeros(n, dtype=np.float64)
    for i, ch in enumerate(chunks):
        rank = ch.get("authority") or 8
        s[i] = (9 - rank) / 8.0
        if ch.get("parse_quality") == "thin":
            s[i] *= 0.4
        if ch.get("source_type") == "lecture_slide":
            s[i] *= 0.55
        if ch.get("source_type") == "exam":
            s[i] *= 0.85  # exam is not theory authority
    return s


def _reason(ch: dict, analysis: dict, hybrid: float) -> str:
    bits = []
    if analysis.get("course_scope") == ch["course_id"]:
        bits.append("course_match")
    overlap = set(analysis.get("detected_concepts") or []).intersection(ch.get("concept_ids") or [])
    if overlap:
        bits.append("concept:" + ",".join(sorted(overlap)[:4]))
    if analysis.get("chapter") is not None and ch.get("chapter") == analysis["chapter"]:
        bits.append(f"chapter_{ch.get('chapter')}")
    bits.append(f"source_type={ch.get('source_type')}")
    bits.append(f"authority={ch.get('authority')}")
    bits.append(f"hybrid={hybrid:.3f}")
    return "; ".join(bits)


def _to_item(ch: dict, score: float, analysis: dict) -> dict:
    excerpt = ch["text"]
    if len(excerpt) > 1800:
        excerpt = excerpt[:1800] + "…"
    return {
        "item_id": ch["chunk_id"],
        "chunk_id": ch["chunk_id"],
        "source_id": ch["source_id"],
        "relative_path": ch["relative_path"],
        "course_id": ch["course_id"],
        "course_code": ch.get("course_code"),
        "chapter": ch.get("chapter"),
        "topic": ch.get("topic"),
        "section": ch.get("section"),
        "source_type": ch.get("source_type"),
        "authority": ch.get("authority"),
        "authority_rank": ch.get("authority"),
        "page_range": ch.get("page_range"),
        "locator": {
            "page": ch.get("page_start"),
            "heading": ch.get("section"),
            "char_start": None,
            "char_end": None,
        },
        "concept_ids": ch.get("concept_ids") or [],
        "relevance_score": round(float(score), 4),
        "reason_selected": _reason(ch, analysis, score),
        "text": excerpt,
        "excerpt": excerpt,
        "evidence_status": "OBSERVED",
        "confidence": "high" if score >= 0.45 else ("medium" if score >= 0.25 else "low"),
        "parse_quality": ch.get("parse_quality"),
        "source": ch.get("source_file"),
    }


def retrieve(question: str, filters: dict | None = None, top_k: int | None = None, system: str = "hybrid") -> dict:
    """system: naive | hybrid | hybrid_prereq"""
    from retrieval.partition import resolve_extended_scope, retrieve_partition, topic_owner_suggestions, external_notes

    ext = resolve_extended_scope(question, filters)
    if ext is not None:
        pkg = retrieve_partition(question, ext, filters, top_k, system)
        updates = external_notes(pkg)
        if updates:
            pkg.setdefault("v3", {})["regulation_updates"] = updates
        return pkg
    pkg = _retrieve_legacy(question, filters, top_k, system)
    pkg["other_course_suggestions"] = topic_owner_suggestions(question, pkg)  # additive key only
    updates = external_notes(pkg)
    if updates:
        pkg["regulation_updates"] = updates
    return pkg


def _retrieve_legacy(question: str, filters: dict | None = None, top_k: int | None = None, system: str = "hybrid") -> dict:
    filters = dict(filters or {})
    analysis = analyze_question(question, filters)
    if system == "hybrid_prereq" and analysis["mode"] == "current_course":
        if analysis["course_scope"] == "ke-toan-tai-chinh-1":
            analysis["mode"] = "prerequisite_recovery"
    if system == "naive":
        analysis_naive = dict(analysis)
        # naive: ignore course/chapter filters
        analysis_naive["mode"] = "cross_course"
        analysis_naive["course_scope"] = "cross_course"
        analysis_naive["chapter"] = None
        analysis = analysis_naive
        mode = "cross_course"
    else:
        mode = analysis["mode"]
        if filters.get("mode"):
            mode = filters["mode"]
            analysis["mode"] = mode

    idx = get_index()
    chunks = idx.chunks
    qtoks = tokenize(question)
    if system == "naive":
        scores = idx.tfidf_cosine(qtoks)
        mask = np.ones(len(chunks), dtype=bool)
        hybrid = _minmax(scores)
    else:
        bm = _minmax(idx.bm25(qtoks))
        tf = _minmax(idx.tfidf_cosine(qtoks))
        cs = _concept_score(chunks, analysis["detected_concepts"])
        ms = _metadata_score(chunks, analysis)
        au = _authority_score(chunks)
        w = HYBRID_WEIGHTS
        hybrid = w["bm25"] * bm + w["tfidf"] * tf + w["concept"] * cs + w["metadata"] * ms + w["authority"] * au
        mask = _mask(chunks, analysis, mode, for_prereq=False)

    hybrid = np.where(mask, hybrid, -1.0)
    k = top_k or TOP_K_DEFAULT
    order = np.argsort(-hybrid)
    picked = []
    for i in order:
        if hybrid[i] < 0:
            continue
        picked.append((int(i), float(hybrid[i])))
        if len(picked) >= k:
            break

    items = [_to_item(chunks[i], sc, analysis) for i, sc in picked]

    prereq_items = []
    prereq_concepts = []
    if system in {"hybrid", "hybrid_prereq"} and mode in {"prerequisite_recovery", "cross_course"}:
        current = analysis["course_scope"]
        if current == "cross_course":
            current = "ke-toan-tai-chinh-1"
        prereq_concepts = prerequisite_concepts(analysis["detected_concepts"], current)
        if mode == "prerequisite_recovery":
            for c in ("no-co", "tai-khoan-ke-toan", "ghi-so-kep", "dinh-khoan"):
                if c not in prereq_concepts:
                    prereq_concepts.append(c)
        if prereq_concepts and (mode == "prerequisite_recovery" or system == "hybrid_prereq"):
            pmask = _mask(chunks, analysis, mode, for_prereq=True)
            pcs = _concept_score(chunks, prereq_concepts)
            pbm = _minmax(idx.bm25(qtoks + prereq_concepts))
            pscore = 0.7 * pcs + 0.3 * pbm
            pscore = np.where(pmask, pscore, -1.0)
            porder = np.argsort(-pscore)
            for i in porder:
                if pscore[i] < 0:
                    continue
                # require concept hit for prereq evidence
                if not set(prereq_concepts).intersection(chunks[i].get("concept_ids") or []):
                    continue
                prereq_items.append(_to_item(chunks[i], float(pscore[i]), analysis))
                if len(prereq_items) >= PREREQ_TOP_K:
                    break

    # coverage
    if not items:
        coverage = "insufficient"
    elif analysis["course_scope"] in {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"}:
        same = sum(1 for it in items if it["course_id"] == analysis["course_scope"])
        coverage = "sufficient" if same >= 1 and items[0]["relevance_score"] >= 0.15 else "partial"
        if items[0]["relevance_score"] < 0.08:
            coverage = "insufficient"
    else:
        coverage = "partial" if items else "insufficient"

    unknowns = []
    # KTTC1 advertised chapters are 1–3 (overview, cash/receivables, inventory).
    # Incidental TSCĐ examples inside those scripts are not a TSCĐ chapter.
    qfold = question.lower()
    if analysis["course_scope"] == "ke-toan-tai-chinh-1" and mode in {"current_course", "source_bound"}:
        if "tscđ" in qfold or "tài sản cố định" in qfold or "tscd" in (analysis.get("detected_concepts") or []):
            coverage = "insufficient"
            unknowns.append("kttc1_has_no_tscd_chapter")
        if any(tok in qfold for tok in ("wacc", "capm", "ifrs 15", "ifrs15", "vốn chủ sở hữu", "định mức chi phí")):
            coverage = "insufficient"
            unknowns.append("topic_not_in_kttc1_outline")
    if analysis["course_scope"] == "nguyen-ly-ke-toan" and mode == "current_course":
        if any(tok in qfold for tok in ("ifrs", "wacc", "capm", "định mức chi phí")):
            coverage = "insufficient"
            unknowns.append("topic_not_in_nlkt_outline")

    conflicts = []
    # simple conflict: same concept, lecture_note vs exam wording not merged — flag if both present
    by_concept = {}
    for it in items:
        for cid in it.get("concept_ids") or []:
            by_concept.setdefault(cid, []).append(it)
    for cid, group in by_concept.items():
        types = {g["source_type"] for g in group}
        if "exam" in types and "lecture_note" in types:
            conflicts.append(
                {
                    "concept_id": cid,
                    "item_ids": [g["item_id"] for g in group],
                    "note": "SOURCE_CONFLICT: exam and lecture_note both retrieved; exam is not theory authority.",
                    "flag": "SOURCE_CONFLICT",
                }
            )

    if analysis["course_scope"] == "unknown":
        unknowns.append("course_scope_unresolved")
    if coverage == "insufficient" and "insufficient_curriculum_evidence" not in unknowns:
        unknowns.append("insufficient_curriculum_evidence")

    pkg = {
        "package_id": f"pkg-{uuid.uuid4().hex[:12]}",
        "request_id": f"req-{uuid.uuid4().hex[:12]}",
        "layer": "curriculum",
        "query": question,
        "system": system,
        "mode": mode,
        "current_course": analysis["course_scope"],
        "intent": analysis["intent"],
        "detected_concepts": analysis["detected_concepts"],
        "chapter": analysis.get("chapter"),
        "items": items,
        "evidence": items,
        "prerequisite_concepts": prereq_concepts,
        "prerequisite_evidence": prereq_items,
        "conflicts": conflicts,
        "coverage": coverage,
        "unknowns": unknowns,
        "analysis": analysis,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return pkg
