# -*- coding: utf-8 -*-
from __future__ import annotations
import re

from retrieval.concepts import detect_query_concepts
from retrieval.textutil import fold

NLKT_CUES = [
    r"nguyên\s*lý\s*kế\s*toán",
    r"\bnlkt\b",
    r"acco\s*1325",
]
KTTC1_CUES = [
    r"kế\s*toán\s*tài\s*chính\s*1",
    r"\bkttc\s*1\b",
    r"acco\s*2310",
]
PREREQ_CUES = [
    r"từ nguyên lý",
    r"của nguyên lý",
    r"ở nguyên lý",
    r"nlkt",
    r"nợ/?có",
    r"ghi sổ kép",
    r"cần học trước",
    r"kiến thức nền",
    r"prereq",
    r"tiên quyết",
]
CROSS_CUES = [
    r"phát triển thành",
    r"khác nhau giữa",
    r"so sánh",
    r"ở nlkt.*kttc",
    r"từ nlkt sang",
    r"hai môn",
]
SOURCE_BOUND_CUES = [
    r"theo chương\s*\d+",
    r"trong chương\s*\d+",
    r"chương\s*\d+\s+của",
    r"theo slide",
    r"đề thi mẫu",
    r"hướng dẫn học tập",
]
INTENT_PATTERNS = [
    ("journal_entry", [r"định khoản", r"hạch toán", r"bút toán", r"nợ.{0,20}có"]),
    ("calculation", [r"tính", r"số tiền", r"giá xuất", r"khấu hao", r"bình quân"]),
    ("definition", [r"là gì", r"khái niệm", r"định nghĩa"]),
    ("comparison", [r"khác nhau", r"so sánh", r"phân biệt"]),
    ("prerequisite", PREREQ_CUES),
    ("cross_course", CROSS_CUES),
    ("source_lookup", SOURCE_BOUND_CUES),
    ("application", [r"vận dụng", r"trình bày trên", r"ghi nhận"]),
    ("explanation", [r"giải thích", r"như thế nào", r"vì sao", r"tại sao"]),
]


def _any(q: str, pats: list[str]) -> bool:
    return any(re.search(p, q, re.I) for p in pats)


def _chapter(q: str) -> int | None:
    m = re.search(r"chương\s*(\d+)", q, re.I)
    return int(m.group(1)) if m else None


def analyze_question(question: str, filters: dict | None = None) -> dict:
    filters = filters or {}
    q = fold(question)
    course = filters.get("course_id")
    hit_nlkt = _any(q, NLKT_CUES)
    hit_kttc = _any(q, KTTC1_CUES)
    if course:
        course_scope = course
    elif hit_nlkt and hit_kttc:
        course_scope = "cross_course"
    elif hit_kttc:
        course_scope = "ke-toan-tai-chinh-1"
    elif hit_nlkt:
        course_scope = "nguyen-ly-ke-toan"
    else:
        course_scope = "unknown"

    intent = "unknown"
    for name, pats in INTENT_PATTERNS:
        if _any(q, pats):
            intent = name
            break

    mode = "current_course"
    prereq_hit = intent == "prerequisite" or _any(q, PREREQ_CUES)
    # "from NLKT used in KTTC1" is prerequisite recovery, not a full cross-course dump.
    if prereq_hit and (hit_kttc or course_scope == "ke-toan-tai-chinh-1" or (hit_nlkt and hit_kttc)):
        mode = "prerequisite_recovery"
        course_scope = "ke-toan-tai-chinh-1" if (hit_kttc or not hit_nlkt) else course_scope
        if hit_kttc:
            course_scope = "ke-toan-tai-chinh-1"
    elif course_scope == "cross_course" or intent == "cross_course" or (hit_nlkt and hit_kttc):
        mode = "cross_course"
        course_scope = "cross_course"
    elif intent == "source_lookup" or _any(q, SOURCE_BOUND_CUES):
        mode = "source_bound"
        if course_scope == "unknown" and hit_kttc:
            course_scope = "ke-toan-tai-chinh-1"
        if course_scope == "unknown" and hit_nlkt:
            course_scope = "nguyen-ly-ke-toan"

    if filters.get("include_prerequisites") is True and mode == "current_course":
        if course_scope == "ke-toan-tai-chinh-1":
            mode = "prerequisite_recovery"

    if filters.get("include_prerequisites") is False and mode == "prerequisite_recovery":
        mode = "current_course"

    concepts = detect_query_concepts(question)
    chapter = filters.get("chapter")
    if chapter is None:
        chapter = _chapter(q)

    explicit = []
    if hit_nlkt:
        explicit.append("named_nlkt")
    if hit_kttc:
        explicit.append("named_kttc1")
    if chapter is not None:
        explicit.append(f"chapter_{chapter}")

    return {
        "question": question,
        "intent": intent,
        "course_scope": course_scope,
        "mode": mode,
        "detected_concepts": concepts,
        "chapter": chapter,
        "explicit_constraints": explicit,
        "source_type": filters.get("source_type"),
    }
