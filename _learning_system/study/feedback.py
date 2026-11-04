# -*- coding: utf-8 -*-
"""User correction capture. Disagreement is not proof the curriculum is wrong."""
from __future__ import annotations
import re

from retrieval.textutil import fold

# First matching rule wins. Explicit exclude is highest priority.
RULES = (
    (r"không muốn.{0,40}đánh giá|đừng (nhớ|lưu)|không dùng.{0,20}(đánh giá|ghi nhớ)|exclude from", "EXCLUDE_FROM_LONG_TERM_EVIDENCE"),
    (r"mày hiểu sai|hiểu sai rồi|hiểu nhầm câu", "MISUNDERSTOOD_QUERY"),
    (r"không,? ý (tao|tôi|mình|em) là", "MISUNDERSTOOD_QUERY"),
    (r"chỉ tính nhầm|tính nhầm|nhân nhầm|gõ nhầm|sai chính tả", "WRONG_DIAGNOSIS"),
    (r"thuộc chương khác|nhầm chương", "WRONG_SOURCE"),
    (r"giáo trình ghi khác|trong (bài giảng|giáo trình) khác", "WRONG_SOURCE"),
    (r"sai môn|nhầm môn|không phải kttc|không phải nlkt", "WRONG_COURSE"),
    (r"không cần quay lại (nlkt|nguyên lý)|đừng (kéo|quay).{0,12}nlkt", "OVERREACH"),
    (r"giải thích khó hiểu|giải thích rối|nói khó hiểu", "UNDER_EXPLANATION"),
    (r"nói dài quá|không cần giảng nhiều", "OVER_EXPLANATION"),
    (r"can thiệp sai|không phải cái đó", "WRONG_INTERVENTION"),
    (r"chẩn đoán sai|không phải lỗi đó", "WRONG_DIAGNOSIS"),
    (r"đúng rồi|đúng đó|ok đúng", "CORRECT"),
    (r"hữu ích|hay|dùng được", "USEFUL"),
)


def classify_feedback(text: str) -> str:
    t = fold(text or "")
    if not t.strip():
        return "UNKNOWN"
    for pat, code in RULES:
        if re.search(pat, t, re.I):
            return code
    return "UNKNOWN"


def is_exclude(code: str | None, text: str | None = None) -> bool:
    if code == "EXCLUDE_FROM_LONG_TERM_EVIDENCE":
        return True
    if text and classify_feedback(text) == "EXCLUDE_FROM_LONG_TERM_EVIDENCE":
        return True
    return False
