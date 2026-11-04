# -*- coding: utf-8 -*-
"""User view vs debug view. No hypothesis IDs in the normal view."""
from __future__ import annotations

from decision.preview import preview

ERROR_PLAIN = {
    "arithmetic_error": "Chỗ này sai phép tính; phương pháp không bị bác.",
    "classification_error": "Đối tượng bị xếp nhầm nhóm so với giáo trình.",
    "conceptual_failure": "Cơ chế khái niệm chưa khớp phần đã dạy.",
    "journal_entry_error": "Bút toán/tài khoản chưa đúng đối tượng đã dạy.",
    "formula_selection_error": "Công thức/phương pháp tính giá chưa đúng phần đã dạy.",
    "procedural_error": "Thiếu hoặc đảo bước trong quy trình đã dạy.",
    "recall_failure": "Thiếu tên/số hiệu đã dạy, chưa chắc sai bản chất.",
    "terminology_confusion": "Hai thuật ngữ gần nghĩa đang bị trộn.",
    "prerequisite_gap": "Có thể thiếu một quy tắc Nợ/Có đã dạy ở NLKT — chỉ khi đã xác nhận.",
    "interpretation_error": "Đọc tình huống chưa khớp giáo trình.",
    "transfer_failure": "Áp sang tình huống mới chưa giữ đúng quy tắc đã dạy.",
    "none": "Trên câu này chưa thấy lỗ hổng học tập.",
    "unknown": "Chưa đủ căn cứ để kết luận lỗi.",
}

ACTION_PLAIN = {
    "RECALL_REFRESH": "Nhắc lại đúng một tên hoặc số hiệu đã dạy.",
    "MECHANISM_EXPLANATION": "Giải đúng một cơ chế đã dạy, không ôn cả chương.",
    "CONTRASTIVE_EXAMPLE": "Đặt cạnh hai trường hợp đã dạy để tách chỗ nhầm.",
    "WORKED_EXAMPLE": "Xem một bút toán/ví dụ đã dạy cho đúng đối tượng này.",
    "PROCEDURE_REHEARSAL": "Làm lại đúng chuỗi bước đã dạy bị bỏ.",
    "APPLICATION_PRACTICE": "Làm một tình huống cùng khái niệm, ngữ cảnh khác.",
    "PREREQUISITE_MICRO_BACKFILL": "Vá đúng một quy tắc Nợ/Có cần cho bài này — không ôn cả NLKT.",
    "TERMINOLOGY_CLARIFICATION": "Tách hai thuật ngữ theo cách giáo trình dùng.",
    "MECHANICAL_CORRECTION": "Sửa phép tính/sao chép; giữ phương pháp đã chọn đúng.",
    "VERIFY_MORE": "Cần một câu trả lời rõ hơn trước khi giảng.",
    "NO_INTERVENTION": "Không cần can thiệp thêm trên câu này.",
    "CONTINUE": "Tiếp tục bài hiện tại để lấy thêm bằng chứng.",
}

INTERNAL_NEEDLES = (
    "hypothesis_id",
    "h-concept",
    "h-arith",
    "evidencepackage",
    "policy_version",
    "primary_error_code",
    "state_machine",
)


def _src_line(it: dict) -> str:
    name = it.get("source") or it.get("relative_path") or it.get("source_id") or "nguồn"
    ch = it.get("chapter")
    pages = it.get("page_range")
    course = it.get("course_id") or ""
    bits = [str(x) for x in (course, f"ch.{ch}" if ch is not None else None, name, f"tr.{pages}" if pages else None) if x]
    return " · ".join(bits)


def format_teach(answer_obj: dict, *, debug: bool = False) -> dict:
    pkg = answer_obj.get("package") or {}
    items = pkg.get("items") or []
    coverage = pkg.get("coverage")
    if coverage == "insufficient":
        user = "Trong giáo trình NLKT/KTTC1 đang dùng, chưa đủ căn cứ để khẳng định điều này như một sự kiện đã dạy."
        if pkg.get("detected_concepts"):
            user += "\nKhái niệm nhận ra trong câu hỏi: " + ", ".join(pkg["detected_concepts"])
    else:
        snippet = ""
        if items:
            snippet = (items[0].get("excerpt") or "").replace("\n", " ").strip()
            if len(snippet) > 500:
                snippet = snippet[:500] + "…"
        srcs = "\n".join("- " + _src_line(it) for it in items[:3])
        user = (snippet or "Có đoạn giáo trình liên quan.") + ("\n\nNguồn:\n" + srcs if srcs else "")
        if pkg.get("conflicts"):
            user += "\n\nCác nguồn không được gộp thành một định nghĩa duy nhất."
    dbg = None
    if debug:
        dbg = {
            "mode": pkg.get("mode"),
            "course": pkg.get("current_course"),
            "coverage": coverage,
            "concepts": pkg.get("detected_concepts"),
            "items": [
                {"source_id": it.get("source_id"), "chapter": it.get("chapter"), "course_id": it.get("course_id")}
                for it in items[:5]
            ],
            "grounded": answer_obj.get("grounded"),
        }
    return {"user": user, "debug": dbg}


def format_decision(diag: dict, dec: dict | None, *, debug: bool = False) -> dict:
    et = (diag or {}).get("primary_error_code") or ((diag or {}).get("root_cause") or {}).get("error_type") or "unknown"
    act = ((dec or {}).get("decision") or {}).get("action_type") if dec else None
    concept = (diag or {}).get("target_concept")
    q = None
    qs = (diag or {}).get("diagnostic_questions") or []
    if qs:
        q = qs[0].get("text") if isinstance(qs[0], dict) else str(qs[0])
    elif act == "VERIFY_MORE":
        q = ((dec or {}).get("decision") or {}).get("preview")
    lines = [ERROR_PLAIN.get(et, ERROR_PLAIN["unknown"])]
    if act:
        lines.append("Việc nên làm tiếp: " + (ACTION_PLAIN.get(act) or preview(act, concept)))
    if q and act in {None, "VERIFY_MORE"}:
        lines.append("Câu hỏi: " + q)
    user = "\n".join(lines)
    dbg = None
    if debug:
        rc = (diag or {}).get("root_cause") or {}
        dbg = {
            "status": (diag or {}).get("status"),
            "primary_error_code": et,
            "confidence": (diag or {}).get("confidence"),
            "target_concept": concept,
            "prerequisite_gap": rc.get("prerequisite_gap"),
            "action_type": act,
            "decision_status": (dec or {}).get("status"),
            "sources": [
                {"source_id": s.get("source_id"), "path": s.get("relative_path")}
                for s in ((diag or {}).get("curriculum_sources") or [])[:4]
            ],
        }
    return {"user": user, "debug": dbg}


def format_next(action: dict, *, debug: bool = False) -> dict:
    act = (action.get("action") or {}).get("type")
    st = action.get("status")
    if st == "CONTINUE" or act in {"NO_INTERVENTION", "CONTINUE"}:
        user = "Tiếp tục bài hiện tại. Bằng chứng hiện có không kết luận đã thành thạo mãi."
    elif st == "VERIFY_MORE" or act == "VERIFY_MORE":
        user = "Cần thêm một câu trả lời rõ trước khi giảng. Thiếu bằng chứng không có nghĩa là yếu."
    elif st == "NO_ACTION":
        user = "Không có can thiệp nào được chứng minh cho nhiệm vụ hiện tại."
    else:
        user = "Việc nên làm tiếp: " + (ACTION_PLAIN.get(act) or act or "một bước nhỏ.")
        tgt = action.get("target") or {}
        if tgt.get("concept_id"):
            user += f"\nKhái niệm: {tgt.get('concept_id')}" + (f" ({tgt.get('dimension')})" if tgt.get("dimension") else "")
        if tgt.get("is_prerequisite"):
            user += "\nĐây là vá ngắn quy tắc nền cần cho bài hiện tại, không phải ôn cả môn trước."
    dbg = None
    if debug:
        dbg = {
            "status": st,
            "action": action.get("action"),
            "target": action.get("target"),
            "codes": action.get("priority_reason_codes"),
            "state_basis": action.get("state_basis"),
            "persistence": action.get("persistence"),
        }
    return {"user": user, "debug": dbg}


def leaks_internal(text: str) -> bool:
    t = (text or "").lower()
    return any(n in t for n in INTERNAL_NEEDLES)
