# -*- coding: utf-8 -*-
"""Minimal discriminating diagnostic questions. No quiz marathon."""
from __future__ import annotations
import re

TEMPLATES = {
    ("H-noco", "H-acct"): {
        "id": "dq-noco-vs-acct",
        "text": "Chỉ trả lời hướng Nợ/Có, không cần số hiệu tài khoản: khi tiền mặt tăng, ghi Nợ hay ghi Có tài khoản tiền mặt?",
        "eliminates_if": {
            "nợ": ["H-noco"],
            "có": ["H-acct"],
            "ghi nợ": ["H-noco"],
            "ghi có": ["H-acct"],
        },
        "supports_if": {
            "có": ["H-noco"],
            "ghi có": ["H-noco"],
            "nợ": ["H-acct"],
        },
    },
    ("H-arith", "H-formula"): {
        "id": "dq-arith-vs-formula",
        "text": "Bạn đang dùng phương pháp giá xuất nào (FIFO, bình quân gia quyền, đích danh)? Tính lại đúng 50 đơn vị × đơn giá lô FIFO đầu tiên.",
        "eliminates_if": {
            "fifo": ["H-formula"],
            "bình quân": ["H-arith"],
        },
    },
    ("H-class", "H-noco"): {
        "id": "dq-class-vs-noco",
        "text": "Nghiệp vụ mua hàng hóa trả tiền mặt làm tăng khoản mục nào trên Bảng cân đối kế toán: hàng tồn kho hay chi phí?",
        "eliminates_if": {
            "hàng tồn kho": ["H-class"],
            "chi phí": ["H-noco"],
        },
    },
    ("H-class", "H-acct"): {
        "id": "dq-class-vs-acct",
        "text": "Đối tượng vừa mua là hàng hóa để bán hay chi phí kỳ này? Không cần định khoản.",
        "eliminates_if": {
            "hàng hóa": ["H-class"],
            "chi phí": ["H-acct"],
        },
    },
    ("H-unknown",): {
        "id": "dq-need-work",
        "text": "Hãy viết đúng một dòng: (1) đối tượng kế toán bị ảnh hưởng, (2) tăng hay giảm, (3) nếu có số liệu thì phép tính. Không cần giải thích lý thuyết.",
        "eliminates_if": {},
    },
}


def select_question(remaining: list[dict]) -> dict | None:
    ids = [h["hypothesis_id"] for h in remaining if h.get("testable", True)]
    if len(ids) <= 1:
        return None
    # pick pair template
    for key, tmpl in TEMPLATES.items():
        if set(key).issubset(set(ids)):
            return {"template_id": tmpl["id"], "text": tmpl["text"], "eliminates_if": tmpl.get("eliminates_if") or {}, "supports_if": tmpl.get("supports_if") or {}, "pair": list(key)}
    if any(h["hypothesis_id"] == "H-unknown" for h in remaining):
        tmpl = TEMPLATES[("H-unknown",)]
        return {"template_id": tmpl["id"], "text": tmpl["text"], "eliminates_if": {}, "supports_if": {}, "pair": ["H-unknown"]}
    if len(ids) >= 2:
        # generic discriminator — option letters must not match Vietnamese "có"
        return {
            "template_id": "dq-generic-split",
            "text": "Chỉ chọn một: (A) sai vì nhầm phép tính, (B) sai vì chọn sai đối tượng/tài khoản, (C) sai vì hiểu ngược Nợ/Có.",
            "eliminates_if": {
                "(a)": ["H-noco", "H-class", "H-acct", "H-concept"],
                "a.": ["H-noco", "H-class", "H-acct", "H-concept"],
                "nhầm phép tính": ["H-noco", "H-class", "H-acct", "H-concept"],
                "(b)": ["H-arith", "H-noco"],
                "b.": ["H-arith", "H-noco"],
                "chọn sai đối tượng": ["H-arith", "H-noco"],
                "(c)": ["H-arith", "H-class", "H-acct"],
                "c.": ["H-arith", "H-class", "H-acct"],
                "hiểu ngược": ["H-arith", "H-class", "H-acct"],
            },
            "supports_if": {},
            "pair": ids[:2],
        }
    return None


def _needle_hit(needle: str, text: str) -> bool:
    """Avoid 1-letter option keys matching inside Vietnamese words (có, chọn)."""
    n = (needle or "").strip().lower()
    f = text or ""
    if not n:
        return False
    if len(n) <= 2 and n.isalpha():
        return bool(re.search(rf"(^|[\s\(\[]){re.escape(n)}[\.\)\:\s]", f))
    return n in f


def apply_followup(remaining: list[dict], question_spec: dict, followup: str) -> tuple[list[dict], list[dict]]:
    f = (followup or "").lower()
    elim_ids = set()
    for needle, ids in (question_spec.get("eliminates_if") or {}).items():
        if _needle_hit(needle, f):
            elim_ids.update(ids)
    kept, rejected = [], []
    for h in remaining:
        if h["hypothesis_id"] in elim_ids:
            rejected.append(h)
        else:
            kept.append(h)
    if not kept and remaining:
        # followup didn't match; keep remaining
        return remaining, []
    return kept, rejected
