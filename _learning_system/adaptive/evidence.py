# -*- coding: utf-8 -*-
"""Typed evidence events + strength. Self-report is never STRONG."""
from __future__ import annotations
import re
import uuid

from diagnostic.signals import extract_signals
from retrieval.textutil import fold

EVENT_TYPES = (
    "DIAGNOSTIC_ANSWER",
    "RETRY_ANSWER",
    "WORKED_STEP",
    "EXPLANATION",
    "CALCULATION",
    "CLASSIFICATION_CHOICE",
    "JOURNAL_ENTRY",
    "CORRECTION",
    "SELF_REPORT",
    "NO_RESPONSE",
    "AMBIGUOUS_RESPONSE",
)

SELF_REPORT = re.compile(
    r"em hiểu rồi|hiểu rồi|ok\b|oke\b|được rồi|rõ rồi|chắc vậy|hình như đúng|em nghĩ vậy",
    re.I,
)
HEDGE = re.compile(r"không chắc|gì đó|nhỉ|hình như|chắc vậy|huh|cảm giác", re.I)
ARITH = re.compile(
    r"nhân .{0,12} ra\s*\d+|50\s*[x×*]\s*10\s*=\s*600|ra\s*600|tính thành\s*\d+|cộng sai|nhân nhầm|nhầm phép",
    re.I,
)
NOCO_FALSE = re.compile(
    r"tăng thì (ghi )?bên (phải|có)|tăng .{0,12} ghi có|tài sản tăng (thì )?(bên có|ghi có)|"
    r"bên phải vì tăng|tiền vào ghi có|tăng quỹ ghi có",
    re.I,
)
NOCO_TRUE = re.compile(
    r"(tiền mặt|tiền|quỹ) tăng.{0,12}(ghi )?nợ|tăng .{0,12} ghi nợ|ghi nợ khi tăng|"
    r"tăng thì ghi nợ|bên trái vì tăng",
    re.I,
)
CLASS_EXPENSE = re.compile(r"\b642\b|đưa vào chi phí|là chi phí|ghi chi phí|hàng hóa.{0,12}chi phí", re.I)
CLASS_ASSET = re.compile(r"hàng tồn kho|hàng hóa để bán|không phải chi phí|là tài sản", re.I)
FORMULA_BQ = re.compile(r"bình quân|gia quyền|lấy giữa|chia 2|trung bình", re.I)
FORMULA_FIFO = re.compile(r"\bfifo\b|lô đầu|nhập trước", re.I)
CORRECT_REASON = re.compile(
    r"fifo.{0,20}lô (đầu|cũ)|50\s*[x×*]\s*10\s*=\s*500|đúng ra 500|ghi nợ (tk )?111",
    re.I,
)
WRONG_REASON_OK_NUM = re.compile(r"lô cuối|lô mới nhất|fifo là lấy giá sau", re.I)


def new_event(
    content: str,
    event_type: str | None = None,
    order: int = 0,
    related_question: str | None = None,
    related_hypothesis: str | None = None,
) -> dict:
    text = content or ""
    et = event_type or infer_event_type(text)
    strength = strength_of(et, text)
    return {
        "event_id": f"ev-{uuid.uuid4().hex[:10]}",
        "event_type": et,
        "content": text,
        "task_context": None,
        "source": "learner",
        "order": order,
        "related_question": related_question,
        "related_hypothesis": related_hypothesis,
        "parse_confidence": strength,
        "strength": strength,
    }


def infer_event_type(text: str) -> str:
    t = fold(text or "")
    if not t.strip():
        return "NO_RESPONSE"
    if SELF_REPORT.search(t) and len(t.split()) <= 8:
        return "SELF_REPORT"
    if HEDGE.search(t) and len(t.split()) <= 10:
        return "AMBIGUOUS_RESPONSE"
    if re.search(r"nợ\s*\d{3}|có\s*\d{3}|tk\s*\d{3}", t):
        return "JOURNAL_ENTRY"
    if ARITH.search(t) or re.search(r"\d+\s*[x×*]\s*\d+", t):
        return "CALCULATION"
    if CLASS_EXPENSE.search(t) or CLASS_ASSET.search(t):
        return "CLASSIFICATION_CHOICE"
    if re.search(r"vì |bởi vì |em nghĩ", t):
        return "EXPLANATION"
    return "DIAGNOSTIC_ANSWER"


def strength_of(event_type: str, text: str) -> str:
    t = fold(text or "")
    if event_type in {"SELF_REPORT", "NO_RESPONSE", "AMBIGUOUS_RESPONSE"}:
        return "WEAK"
    if SELF_REPORT.search(t) and not ARITH.search(t) and not NOCO_FALSE.search(t):
        return "WEAK"
    if HEDGE.search(t) and not ARITH.search(t) and not NOCO_FALSE.search(t) and not CLASS_EXPENSE.search(t):
        return "WEAK"
    if NOCO_FALSE.search(t) or NOCO_TRUE.search(t) or ARITH.search(t) or CLASS_EXPENSE.search(t):
        return "STRONG"
    if FORMULA_BQ.search(t) or CLASS_ASSET.search(t) or CORRECT_REASON.search(t):
        return "STRONG"
    if re.search(r"nợ\s*\d{3}.+có\s*\d{3}", t):
        return "MEDIUM"
    if event_type in {"CALCULATION", "CLASSIFICATION_CHOICE", "JOURNAL_ENTRY", "CORRECTION", "WORKED_STEP"}:
        return "MEDIUM"
    return "MEDIUM"


def interpret(event: dict, question: str = "") -> dict:
    """Map one event onto error-type support / contradiction. Not a mastery score."""
    text = event.get("content") or ""
    et = event.get("event_type") or infer_event_type(text)
    strength = event.get("strength") or strength_of(et, text)
    sig = extract_signals(question, text, text)
    t = fold(text)

    suggested = None
    supports = []
    contradicts = []
    notes = []

    if et == "SELF_REPORT":
        notes.append("Self-report is weak and does not confirm a gap or mastery.")
        return {
            "suggested_error": None,
            "supports": [],
            "contradicts": [],
            "strength": "WEAK",
            "self_report": True,
            "notes": notes,
            "signals": {k: v for k, v in sig.items() if v},
            "irrelevant": True,
        }

    if et == "NO_RESPONSE":
        return {
            "suggested_error": None,
            "supports": [],
            "contradicts": [],
            "strength": "WEAK",
            "self_report": False,
            "notes": ["No content."],
            "signals": {},
            "irrelevant": True,
        }

    arith = bool(sig.get("arithmetic") or ARITH.search(t))
    noco_false = bool(sig.get("reversed_dc_rule") or NOCO_FALSE.search(t))
    noco_true = bool(NOCO_TRUE.search(t)) and not noco_false
    class_exp = bool(sig.get("classification_asset_expense") or CLASS_EXPENSE.search(t))
    class_ok = bool(CLASS_ASSET.search(t)) and not class_exp
    formula = bool(sig.get("formula_mismatch") or FORMULA_BQ.search(t))
    fifo_ok = bool(FORMULA_FIFO.search(t)) and not formula
    wrong_reason = bool(sig.get("correct_number_wrong_reason") or WRONG_REASON_OK_NUM.search(t))
    recall = bool(sig.get("recall"))
    term = bool(sig.get("terminology"))
    xfer = bool(sig.get("transfer"))
    proc = bool(sig.get("procedural_skip"))
    interp = bool(sig.get("interpretation"))
    acct = bool(sig.get("wrong_account"))

    if noco_false:
        suggested = "prerequisite_gap"
        supports.append("prerequisite_gap")
        contradicts.extend(["arithmetic_error", "classification_error"])
        notes.append("Explicit false Nợ/Có / asset-direction rule.")
    elif noco_true:
        contradicts.append("prerequisite_gap")
        notes.append("Learner stated a correct cash-increase → Nợ direction.")
        if class_exp:
            suggested = "classification_error"
            supports.append("classification_error")
        elif acct:
            suggested = "journal_entry_error"
            supports.append("journal_entry_error")
        elif arith:
            suggested = "arithmetic_error"
            supports.append("arithmetic_error")
            contradicts.append("conceptual_failure")
    elif formula:
        suggested = "formula_selection_error"
        supports.append("formula_selection_error")
        contradicts.extend(["arithmetic_error", "conceptual_failure"])
    elif arith:
        suggested = "arithmetic_error"
        supports.append("arithmetic_error")
        contradicts.extend(["conceptual_failure", "prerequisite_gap", "formula_selection_error"])
        notes.append("Computation slip with or without a named method.")
    elif class_exp:
        suggested = "classification_error"
        supports.append("classification_error")
        contradicts.extend(["prerequisite_gap", "arithmetic_error"])
    elif class_ok:
        contradicts.append("classification_error")
        notes.append("Object classified as inventory/asset, not expense.")
    elif wrong_reason:
        suggested = "conceptual_failure"
        supports.append("conceptual_failure")
        contradicts.append("arithmetic_error")
        notes.append("Number may be right; reasoning is wrong — not resolved.")
    elif recall:
        suggested = "recall_failure"
        supports.append("recall_failure")
    elif term:
        suggested = "terminology_confusion"
        supports.append("terminology_confusion")
    elif xfer:
        suggested = "transfer_failure"
        supports.append("transfer_failure")
    elif proc:
        suggested = "procedural_error"
        supports.append("procedural_error")
    elif interp:
        suggested = "interpretation_error"
        supports.append("interpretation_error")
    elif acct:
        suggested = "journal_entry_error"
        supports.append("journal_entry_error")
        contradicts.append("prerequisite_gap")
    elif CORRECT_REASON.search(t) and fifo_ok:
        contradicts.extend(["conceptual_failure", "arithmetic_error", "formula_selection_error"])
        notes.append("Correct method and figure on this item; session-local only.")
        suggested = "none"

    if HEDGE.search(t) and suggested is None:
        notes.append("Hedged; do not lock a diagnosis.")
        strength = "WEAK"

    return {
        "suggested_error": suggested,
        "supports": supports,
        "contradicts": contradicts,
        "strength": strength,
        "self_report": False,
        "notes": notes,
        "signals": {k: v for k, v in sig.items() if v},
        "irrelevant": suggested is None and not supports and not contradicts,
        "correct_on_item": suggested == "none",
        "unresolved_reasoning": bool(wrong_reason),
    }
