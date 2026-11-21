# -*- coding: utf-8 -*-
"""V3 partition retrieval (plan 4.3). Used only for non-core courses.

The legacy core path in retrieve.py is untouched; this module is reached through
`resolve_extended_scope` before any legacy logic.
"""
from __future__ import annotations
import re
import uuid
from datetime import datetime, timezone

import numpy as np

from retrieval import courses as C
from retrieval.config import HYBRID_WEIGHTS, PREREQ_TOP_K, TOP_K_DEFAULT
from retrieval.textutil import fold, tokenize

_CACHE: dict = {}


def _core_cue_hit(question: str) -> bool:
    from retrieval.analyze import KTTC1_CUES, NLKT_CUES, _any

    q = fold(question)
    return _any(q, NLKT_CUES) or _any(q, KTTC1_CUES)


def resolve_extended_scope(question: str, filters: dict | None = None) -> dict | None:
    """Return {"course_id", "tier"} for a non-core course target, else None (legacy path)."""
    filters = filters or {}
    cid = C.normalize_course(filters.get("course_id")) if filters.get("course_id") else None
    if cid:
        if C.is_core(cid):
            return None
        return {"course_id": cid, "tier": C.tier(cid)}
    if filters.get("course_id"):
        return None  # unknown label such as "cross_course": legacy behaviour
    # Learner notes are a pseudo-partition: route only on an explicit learner cue.
    # It must win even when the note itself mentions a core or retrieval course.
    pseudo_hits = C.detect_courses(question, include_pseudo=True)
    if "learner-notes" in pseudo_hits:
        return {"course_id": "learner-notes", "tier": C.tier("learner-notes")}
    if _core_cue_hit(question):
        return None
    from retrieval.external import CUES, active
    if active() and CUES.search(fold(question)):
        return {"course_id": "external", "tier": C.tier("external")}
    hits = C.detect_courses(question)
    if len(hits) > 1:
        # A leading course label identifies the requested scope; later mentions
        # can name the topic being asked about. Do not resolve arbitrary comparisons.
        leading = re.sub(r"^\s*(?:môn\s+)?", "", fold(question))
        first = hits[0]
        if any(C._cue_re(cue).match(leading) for cue in (C.get_course(first) or {}).get("cues", [])):
            return {"course_id": first, "tier": C.tier(first)}
    if len(hits) == 1:
        return {"course_id": hits[0], "tier": C.tier(hits[0])}
    return None


def get_partition_index(course_id: str):
    if course_id not in _CACHE:
        from retrieval.index import Index

        p = C.partition_paths(course_id)
        _CACHE[course_id] = Index(chunks_path=p["chunks"], index_dir=p["index_dir"])
    return _CACHE[course_id]


def clear_cache() -> None:
    _CACHE.clear()


def _retrieval_courses() -> list[str]:
    return [c["id"] for c in C.load_registry()["courses"]
            if c.get("tier") == "retrieval" and c["id"] not in C.PSEUDO]


def topic_owner_suggestions(question: str, pkg: dict) -> list[dict]:
    """Additive hints for the legacy path: which retrieval-tier course teaches this topic."""
    from retrieval.concepts import detect_course_concepts, load_course_concepts

    out = []
    ambiguous = C.detect_courses(question)
    if len(ambiguous) > 1:
        out.append({"type": "ambiguous_courses", "course_ids": ambiguous})
    if pkg.get("coverage") == "sufficient" and _core_cue_hit(question):
        return out
    for cid in _retrieval_courses():
        hits = detect_course_concepts(question, cid)
        if not hits:
            continue
        by_id = {c["concept_id"]: c for c in load_course_concepts(cid).get("concepts") or []}
        chapters = sorted({by_id[h].get("chapter") for h in hits if h in by_id and by_id[h].get("chapter") is not None})
        out.append({"type": "topic_owner", "course_id": cid, "course_name": C.course_name(cid),
                    "concept_ids": hits, "chapters": chapters})
    return out


def _strip_course_cues(question: str, course_id: str) -> str:
    q = fold(question)
    for cue in sorted((C.get_course(course_id) or {}).get("cues") or [], key=len, reverse=True):
        q = q.replace(fold(cue), " ")
    q = q.replace(fold(C.course_name(course_id)), " ")
    return q


def _core_registry_owners(question: str, course_id: str) -> list[str]:
    """Explanatory only: courses owning a core-registry concept named in the question."""
    import yaml
    from retrieval.config import CONCEPT_REGISTRY

    q = _strip_course_cues(question, course_id)
    out = []
    for c in (yaml.safe_load(CONCEPT_REGISTRY.read_text(encoding="utf-8")) or {}).get("concepts") or []:
        owners = [x for x in (c.get("courses") or []) if x != course_id]
        if not owners or course_id in (c.get("courses") or []):
            continue
        names = [c.get("canonical_name") or ""] + [a for a in (c.get("aliases") or []) if isinstance(a, str)]
        if any(len(fold(n)) >= 6 and fold(n) in q for n in names):
            out += [o for o in owners if o not in out]
    return out


_QWORDS = frozenset(tokenize("gì nào sao thế như bao nhiêu khi gồm những ra làm được tính hạch toán cách"))
_REQUEST_PHRASES = re.compile(r"\b(?:hướng dẫn|giải thích|trình bày|cho biết)\b", re.I)


def _evidence_tokens(text: str) -> list[str]:
    # Remove request verbs as phrases, preserving individual domain words such
    # as 'hướng' and 'dẫn' elsewhere. Apply identically to query and evidence.
    return [t for t in tokenize(_REQUEST_PHRASES.sub(' ', text)) if t not in _QWORDS]


def _content_tokens(question: str, course_id: str) -> list[str]:
    return _evidence_tokens(_strip_course_cues(question, course_id))


def _bigram_cov(qt: list[str], texts: list[str]) -> float:
    qb = set(zip(qt, qt[1:]))
    if not qb:
        return 1.0
    bb = set()
    for t in texts:
        tk = _evidence_tokens(t)
        bb |= set(zip(tk, tk[1:]))
    return len(qb & bb) / len(qb)


def _rival_coverage(question: str, course_id: str, qt: list[str]) -> list[tuple[str, float]]:
    """Bigram coverage of the BM25 top-5 in every OTHER indexed course (core courses included)."""
    from retrieval.retrieve import get_index

    out = []
    core = get_index()
    for cc in ("nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"):
        if cc == course_id:
            continue
        m = np.array([c["course_id"] == cc for c in core.chunks])
        sc = np.where(m, core.bm25(qt), -1.0)
        top = [core.chunks[i]["text"] for i in np.argsort(-sc)[:5] if sc[i] > 0]
        out.append((cc, _bigram_cov(qt, top)))
    # Catalog controls serving, not availability of indexed comparison evidence.
    # Failed course gates must not remove their corpus from off-outline checks.
    indexed_courses = [c["id"] for c in C.load_registry()["courses"]
                       if c["id"] not in C.PSEUDO and not C.is_core(c["id"])
                       and (C.partition_paths(c["id"])["index_dir"] / "meta.json").is_file()]
    for rc in indexed_courses:
        if rc == course_id:
            continue
        ix = get_partition_index(rc)
        sc = ix.bm25(qt)
        top = [ix.chunks[i]["text"] for i in np.argsort(-sc)[:5] if sc[i] > 0]
        out.append((rc, _bigram_cov(qt, top)))
    return out


def _oov_terms(question: str, course_id: str, idx) -> list[str]:
    """Explanatory only: content terms of the question absent from this course's corpus."""
    return [t for t in _content_tokens(question, course_id) if t not in idx.idf]


def _empty_package(question, course_id, tier, analysis, unknowns, coverage="insufficient"):
    return {
        "package_id": f"pkg-{uuid.uuid4().hex[:12]}",
        "request_id": f"req-{uuid.uuid4().hex[:12]}",
        "layer": "curriculum",
        "query": question,
        "system": "hybrid",
        "mode": analysis.get("mode"),
        "current_course": course_id,
        "intent": analysis.get("intent"),
        "detected_concepts": analysis.get("detected_concepts") or [],
        "chapter": analysis.get("chapter"),
        "items": [],
        "evidence": [],
        "prerequisite_concepts": [],
        "prerequisite_evidence": [],
        "conflicts": [],
        "coverage": coverage,
        "unknowns": unknowns,
        "analysis": analysis,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "partition": course_id,
        "tier": tier,
        "index_version": "3.0.0",
    }


def retrieve_partition(question: str, ext: dict, filters: dict | None = None, top_k: int | None = None,
                       system: str = "hybrid") -> dict:
    from retrieval.analyze import PREREQ_CUES, SOURCE_BOUND_CUES, _any, analyze_question
    from retrieval.concepts import detect_course_concepts
    from retrieval.retrieve import (_authority_score, _concept_score, _metadata_score, _minmax, _to_item)

    filters = dict(filters or {})
    course_id, tier = ext["course_id"], ext["tier"]
    if course_id == "external":
        from retrieval.external import retrieve_external
        return retrieve_external(question, ext, filters, top_k)
    base = analyze_question(question, {k: v for k, v in filters.items() if k != "course_id"})
    q = fold(question)
    mode = filters.get("mode") or ("source_bound" if _any(q, SOURCE_BOUND_CUES) else "current_course")
    analysis = dict(base)
    analysis.update({"course_scope": course_id, "mode": mode,
                     "detected_concepts": [] if tier == "catalog" or course_id in C.PSEUDO else detect_course_concepts(question, course_id)})

    if tier != "retrieval":
        return _empty_package(question, course_id, tier, analysis, ["course_not_indexed"])

    idx = get_partition_index(course_id)
    chunks = idx.chunks
    qtoks = tokenize(question)
    # A2: course-specific lexical cue removal, never concept/prerequisite scoring.
    lexical_qtoks = (tokenize(_strip_course_cues(question, course_id))
                    if (C.get_course(course_id) or {}).get("retrieval", {}).get("strip_course_cues", False)
                    else qtoks)
    bm = _minmax(idx.bm25(lexical_qtoks))
    tf = _minmax(idx.tfidf_cosine(lexical_qtoks))
    cs = _concept_score(chunks, analysis["detected_concepts"])
    ms = _metadata_score(chunks, analysis)
    au = _authority_score(chunks)
    w = HYBRID_WEIGHTS
    hybrid = w["bm25"] * bm + w["tfidf"] * tf + w["concept"] * cs + w["metadata"] * ms + w["authority"] * au

    mask = np.ones(len(chunks), dtype=bool)
    chapter = analysis.get("chapter")
    if mode == "source_bound":
        if chapter is not None:
            mask &= np.array([c.get("chapter") == chapter for c in chunks])
        if analysis.get("source_type"):
            mask &= np.array([c.get("source_type") == analysis["source_type"] for c in chunks])
    hybrid = np.where(mask, hybrid, -1.0)

    k = top_k or TOP_K_DEFAULT
    picked, seen_groups = [], set()
    for i in np.argsort(-hybrid):
        if hybrid[i] < 0:
            continue
        g = chunks[i].get("dup_group")
        if g and g in seen_groups:
            continue
        if g:
            seen_groups.add(g)
        picked.append((int(i), float(hybrid[i])))
        if len(picked) >= k:
            break
    items = [_to_item(chunks[i], sc, analysis) for i, sc in picked]

    if course_id == "learner-notes":
        pkg = _empty_package(question, course_id, tier, analysis, ["not_curriculum_source"], "learner_material")
        pkg.update({"items": items, "evidence": items, "layer": "learner_notes"})
        return pkg

    prereq_items, prereq_ids = [], []
    reg = C.get_course(course_id) or {}
    if _any(q, PREREQ_CUES) and reg.get("explicit_prerequisites"):
        for pc in reg["explicit_prerequisites"]:
            pidx = None
            if C.is_core(pc):
                from retrieval.retrieve import get_index

                pidx = get_index()
            elif C.tier(pc) == "retrieval":
                pidx = get_partition_index(pc)
            if pidx is None:
                continue
            pm = np.array([c["course_id"] == pc for c in pidx.chunks])
            ps = np.where(pm, pidx.bm25(qtoks), -1.0)
            for i in np.argsort(-ps):
                if ps[i] <= 0:
                    break
                prereq_items.append(_to_item(pidx.chunks[i], float(ps[i]), analysis))
                if len(prereq_items) >= PREREQ_TOP_K:
                    break
            prereq_ids.append(pc)

    unknowns = []
    if not items:
        coverage = "insufficient"
    else:
        top = items[0]["relevance_score"]
        coverage = "sufficient" if top >= 0.15 else "partial"
        if top < 0.08:
            coverage = "insufficient"

    if not analysis["detected_concepts"]:
        from retrieval.concepts import detect_course_concepts as dcc

        # Owner repair authorized 2026-10-12. A requested course name is scope,
        # not subject evidence. Preserve source/chapter-bound queries; when a
        # term is absent from the corpus, the A1 evidence branch below owns the
        # decision and explanations (including indexed catalog rivals).
        owner_query = _strip_course_cues(question, course_id)
        owner_eligible = (analysis.get("chapter") is None and mode != "source_bound"
                          and not _oov_terms(question, course_id, idx))
        owners = ([oc for oc in _retrieval_courses() if oc != course_id and dcc(owner_query, oc)]
                  if owner_eligible else [])
        if owners:
            # W6b review B2 (2026-11-21, trial by the independent reviewer, re-verified on all frozen evals):
            # keep the answer (no refusal) only when this course's own top-5 covers every content bigram AND beats
            # each owner's coverage by >= 0.25. The owner is still listed in unknowns as a pointer.
            _qt = _content_tokens(question, course_id)
            _own = _bigram_cov(_qt, [it["text"] for it in items[:5]]) if items else 0.0
            _peer = dict(_rival_coverage(question, course_id, _qt))
            _specific_local = len(_qt) >= 2 and _own == 1 and all(_own - _peer.get(o, 1) >= 0.25 for o in owners)
            if not _specific_local:
                coverage = "insufficient"
            unknowns += [f"topic_in_other_course:{o}" for o in owners]
        # Amendment 4.3a/4.3b (design model, 2026-10-11). Min-max hybrid scores cannot express
        # "off-outline". For a free question (no chapter, not source_bound) that matches no
        # concept of this course:
        #   - always: coverage capped at "partial" + unknown "no_course_concept_match"
        #   - a content term absent from this course's whole corpus -> insufficient
        #   - another indexed course explains the question clearly better (query-bigram
        #     coverage of its top-5 >= 0.75 and >= this course + 0.25) -> insufficient
        # Thresholds fixed a priori; re-validated on all frozen course evals at checkpoint G3x.
        if analysis.get("chapter") is None and mode != "source_bound":
            if coverage == "sufficient":
                coverage = "partial"
            unknowns.append("no_course_concept_match")
            oov = _oov_terms(question, course_id, idx)
            if oov:
                coverage = "insufficient"
                unknowns += [f"term_not_in_course_corpus:{t}" for t in oov]
            qt = _content_tokens(question, course_id)
            mine = _bigram_cov(qt, [it["text"] for it in items[:5]])
            for rid, rcov in _rival_coverage(question, course_id, qt):
                if rcov >= 0.75 and rcov >= mine + 0.25:
                    coverage = "insufficient"
                    if f"topic_in_other_course:{rid}" not in unknowns:
                        unknowns.append(f"topic_in_other_course:{rid}")
            for o in _core_registry_owners(question, course_id):
                if f"topic_in_other_course:{o}" not in unknowns:
                    unknowns.append(f"topic_owner_hint:{o}")
    if coverage == "insufficient" and "insufficient_curriculum_evidence" not in unknowns:
        unknowns.append("insufficient_curriculum_evidence")

    pkg = _empty_package(question, course_id, tier, analysis, unknowns, coverage)
    pkg.update({"items": items, "evidence": items, "prerequisite_evidence": prereq_items,
                "prerequisite_concepts": prereq_ids})
    return pkg


def external_notes(pkg: dict) -> list[dict]:
    from retrieval.external import notes
    return notes(pkg)
