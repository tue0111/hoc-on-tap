# -*- coding: utf-8 -*-
"""V3 course registry loader, cue detection and partition paths (plan 4.2 / 7.1).

Core course cues stay in analyze.py; this module only detects NON-core courses.
"""
from __future__ import annotations
import re
from functools import lru_cache

import yaml

from retrieval.config import SYSTEM
from retrieval.textutil import fold

REGISTRY_PATH = SYSTEM / "curriculum" / "course_registry.yaml"
# Non-course partitions that live in the registry; never produced by detect_courses
# unless explicitly requested (their routing is wired in Wave 3g / Wave 5).
PSEUDO = frozenset({"learner-notes", "external"})


@lru_cache(maxsize=1)
def load_registry() -> dict:
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def reload_registry() -> dict:
    load_registry.cache_clear()
    _by_id.cache_clear()
    _alias_map.cache_clear()
    _cue_table.cache_clear()  # W6b review m5: cue table must follow the reloaded registry
    return load_registry()


@lru_cache(maxsize=1)
def _by_id() -> dict:
    return {c["id"]: c for c in load_registry()["courses"]}


@lru_cache(maxsize=1)
def _alias_map() -> dict:
    m = {}
    for c in load_registry()["courses"]:
        m[fold(c["id"])] = c["id"]
        m[fold(c["name"])] = c["id"]
        for code in c.get("codes") or []:
            m[fold(code)] = c["id"]
    return m


def get_course(course_id: str) -> dict | None:
    return _by_id().get(course_id)


def course_name(course_id: str) -> str:
    c = get_course(course_id)
    return c["name"] if c else course_id


def normalize_course(id_or_alias: str | None) -> str | None:
    """Map id / official name / course code to a registry id; None if unknown."""
    if not id_or_alias:
        return None
    key = fold(str(id_or_alias)).strip()
    return _alias_map().get(key) or _alias_map().get(re.sub(r"\s+", "", key))


def tier(course_id: str) -> str:
    c = get_course(course_id)
    return c["tier"] if c else "catalog"


def is_core(course_id: str | None) -> bool:
    return bool(course_id) and tier(course_id) == "core"


def _cue_re(cue: str) -> re.Pattern:
    c = fold(cue)
    if len(c) <= 5 and " " not in c:
        return re.compile(r"(?<![0-9a-zà-ỹ])" + re.escape(c) + r"(?![0-9a-zà-ỹ])")
    return re.compile(re.escape(c))


@lru_cache(maxsize=1)
def _cue_table() -> list[tuple[str, list, list, list[str]]]:
    """(course id, label cues, topic cues, topic veto-after phrases).

    W6b G06: `cues` are LABEL cues (course name / code / abbreviation); `topic_cues` are
    business-topic or study-context phrases. `topic_veto_after` lists folded phrases; a topic
    cue match directly followed by one of them is dropped (e.g. 'học kế toán thuế' + 'tndn').
    """
    rows = []
    for c in load_registry()["courses"]:
        if c.get("tier") == "core":
            continue
        cues = sorted(c.get("cues") or [], key=lambda x: -len(x))  # longest first
        topics = sorted(c.get("topic_cues") or [], key=lambda x: -len(x))
        veto = [fold(v) for v in (c.get("topic_veto_after") or [])]
        rows.append((c["id"], [(x, _cue_re(x)) for x in cues], [(x, _cue_re(x)) for x in topics], veto))
    return rows


def _mask_nested(spans: list) -> list:
    """W6b: a match lying strictly inside a longer match of ANOTHER course is masked
    (e.g. "hành chính sự nghiệp" inside "kế toán hành chính sự nghiệp")."""
    return [s for s in spans
            if not any(o[2] != s[2] and o[0] <= s[0] and s[1] <= o[1] and (o[1] - o[0]) > (s[1] - s[0])
                       for o in spans)]


def detect_courses(question: str, include_pseudo: bool = False) -> list[str]:
    """Non-core course ids whose cues occur in the question, ordered by first position.

    W6b G06: explicit label cues win. If any non-pseudo course matches a label cue, topic cues
    are ignored entirely; topic cues are only used when no label matched.
    """
    q = fold(question)
    labels, topics = [], []  # (start, end, cid)
    for cid, lab, top, veto in _cue_table():
        if cid in PSEUDO and not include_pseudo:
            continue
        for _cue, rx in lab:
            labels += [(m.start(), m.end(), cid) for m in rx.finditer(q)]
        for _cue, rx in top:
            for m in rx.finditer(q):
                if veto and any(q[m.end():].lstrip().startswith(v) for v in veto):
                    continue
                topics.append((m.start(), m.end(), cid))
    kept = _mask_nested(labels)
    if not any(s[2] not in PSEUDO for s in kept):
        kept = _mask_nested(labels + topics)
    best = {}
    for start, _end, cid in kept:
        if cid not in best or start < best[cid]:
            best[cid] = start
    hits = sorted((start, cid) for cid, start in best.items())
    return [cid for _, cid in hits]


def partition_paths(course_id: str) -> dict:
    root = SYSTEM / load_registry().get("partition_root", "data/indexes/3.0.0")
    return {
        "documents": SYSTEM / "data" / "normalized" / f"{course_id}.documents.jsonl",
        "pages": SYSTEM / "data" / "normalized" / f"{course_id}.pages.jsonl",
        "coverage": SYSTEM / "data" / "normalized" / f"{course_id}.coverage.json",
        "chunks": SYSTEM / "data" / "chunks" / f"{course_id}.chunks.jsonl",
        "chunks_meta": SYSTEM / "data" / "chunks" / f"{course_id}.chunks.meta.json",
        "index_dir": root / course_id,
        "concepts": SYSTEM / "curriculum" / "concepts" / f"{course_id}.yaml",
    }
