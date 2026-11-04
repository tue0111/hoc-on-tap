# -*- coding: utf-8 -*-
"""Deterministic error-signal extraction from learner text. No mastery."""
from __future__ import annotations
import re
from retrieval.textutil import fold

COURSE_MAP = {
    "acco2310": "ke-toan-tai-chinh-1",
    "kttc1": "ke-toan-tai-chinh-1",
    "kế toán tài chính 1": "ke-toan-tai-chinh-1",
    "ke-toan-tai-chinh-1": "ke-toan-tai-chinh-1",
    "acco1325": "nguyen-ly-ke-toan",
    "nlkt": "nguyen-ly-ke-toan",
    "nguyên lý kế toán": "nguyen-ly-ke-toan",
    "nguyen-ly-ke-toan": "nguyen-ly-ke-toan",
}

OUT_OF_SCOPE = [
    r"\bifrs\b",
    r"\bwacc\b",
    r"\bcapm\b",
    r"định mức chi phí",
    r"kiểm toán độc lập",
]


def normalize_course(cid: str | None) -> str | None:
    if not cid:
        return None
    return COURSE_MAP.get(fold(str(cid)), cid)


def extract_accounts(text: str) -> list[str]:
    return re.findall(r"\b(?:tk\s*)?(\d{3,4})\b", fold(text or ""))


def infer_task(question: str) -> str:
    q = fold(question or "")
    if re.search(r"định khoản|hạch toán|nợ\s*.*\s*có\s*tk|bút toán", q):
        return "journal_entry"
    if re.search(r"tính|giá xuất|fifo|bình quân|số tiền|khấu hao", q):
        return "calculation"
    if re.search(r"phân loại|phân biệt|kê khai|kiểm kê định kỳ", q):
        return "classification"
    if re.search(r"là gì|khái niệm|định nghĩa", q):
        return "definition"
    return "explanation"


def extract_signals(question: str, response: str, work: str) -> dict:
    blob = fold((response or "") + "\n" + (work or ""))
    q = fold(question or "")
    flags = {
        "no_answer": False,
        "confusion_only": False,
        "reversed_dc_rule": False,
        "reversed_journal": False,
        "wrong_account": False,
        "classification_asset_expense": False,
        "arithmetic": False,
        "formula_mismatch": False,
        "recall": False,
        "terminology": False,
        "transfer": False,
        "procedural_skip": False,
        "interpretation": False,
        "out_of_scope": False,
        "method_named_ok": False,
        "partial_steps": False,
        "correct_number_wrong_reason": False,
        "kktx_mix": False,
    }
    if not blob.strip() or re.search(r"không hiểu|chưa hiểu|không biết|không nhớ làm", blob):
        if not re.search(r"nợ tk|có tk|tk\s*\d{3}", blob):
            flags["no_answer"] = True
            flags["confusion_only"] = True
    if re.search(r"không nhớ|quên tài khoản|quên số hiệu", blob):
        flags["recall"] = True
    if re.search(
        r"tăng tài sản ghi có|tăng ts ghi có|tài sản tăng bên có|nợ là giảm tài sản|"
        r"bên có phản ánh tăng tài sản|tăng [^.\n]{0,16} ghi có|giảm tiền phải ghi nợ",
        blob,
    ):
        flags["reversed_dc_rule"] = True
    if re.search(r"em đảo nợ có|đảo định khoản|ghi ngược nợ có", blob):
        flags["reversed_journal"] = True
    if re.search(r"ghi nhận.{0,20}chi phí|hạch toán.{0,12}642|đưa vào chi phí ngay", blob) and re.search(
        r"mua hàng|hàng hóa|tồn kho|156|152", q + blob
    ):
        flags["classification_asset_expense"] = True
    if re.search(r"tính nhầm|nhân sai|cộng sai|nhầm số|50\s*\*\s*10\s*=\s*600|100\+200=.*=\s*250", blob):
        flags["arithmetic"] = True
    if re.search(r"fifo", q) and re.search(r"bình quân|gia quyền|\(10\s*\+\s*12\)\s*/\s*2", blob):
        flags["formula_mismatch"] = True
    if re.search(r"fifo|bình quân gia quyền|đích danh|kê khai thường xuyên", blob) and flags["arithmetic"]:
        flags["method_named_ok"] = True
    if re.search(r"fifo", blob) and not flags["formula_mismatch"]:
        flags["method_named_ok"] = True
    if re.search(r"doanh thu.{0,10}thu nhập|thu nhập.{0,10}doanh thu|nhầm thuật ngữ", blob):
        flags["terminology"] = True
    if re.search(r"công ty dịch vụ.{0,30}156|áp dụng giống ví dụ bán hàng", blob):
        flags["transfer"] = True
    if re.search(r"bỏ qua bút toán điều chỉnh|không kết chuyển|nhảy bước", blob):
        flags["procedural_skip"] = True
    if re.search(r"số dư nợ là xấu|nợ nghĩa là lỗ", blob):
        flags["interpretation"] = True
    if re.search(r"bước 1 đúng|hai bước đầu đúng|sai ở bước", blob):
        flags["partial_steps"] = True
    if re.search(r"ra đúng số|kết quả đúng nhưng", blob):
        flags["correct_number_wrong_reason"] = True
    if any(re.search(p, q + blob) for p in OUT_OF_SCOPE):
        flags["out_of_scope"] = True
    if re.search(r"tscđ|tài sản cố định", q) and ("kttc1" in q or "tài chính 1" in q or "acco2310" in q):
        flags["out_of_scope"] = True
    if re.search(r"vốn chủ sở hữu", q) and ("kttc1" in q or "tài chính 1" in q or "acco2310" in q or "chương 3 kttc1" in q):
        flags["out_of_scope"] = True
    # wrong account: different TK than question's object without reverse-rule
    q_acc = set(extract_accounts(question))
    r_acc = set(extract_accounts(response or ""))
    if q_acc and r_acc and not q_acc.intersection(r_acc):
        if not flags["reversed_dc_rule"]:
            flags["wrong_account"] = True
    if re.search(r"hai phương pháp là một|không khác nhau|không khác|cũng ghi tk 156 liên tục", blob):
        flags["kktx_mix"] = True
    if re.search(r"gộp cả vat|không dùng 133|vat vào giá hàng", blob):
        flags["classification_asset_expense"] = True
    if re.search(r"như xuất bán|nhầm tài khoản|dùng nhầm tài khoản|sai tài khoản|thay vì", blob):
        flags["wrong_account"] = True
    # Forced choice between two account numbers: response picks a proper subset.
    if len(q_acc) >= 2 and r_acc and r_acc < q_acc and not flags["reversed_dc_rule"]:
        flags["wrong_account"] = True
    return flags
