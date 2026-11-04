# -*- coding: utf-8 -*-
"""Thin action preview. Not a lesson. Not Level 6 pedagogy."""

PREVIEWS = {
    "RECALL_REFRESH": "Nhắc lại đúng một tên/số hiệu đã dạy cho {concept} (không giải lại cả chương).",
    "MECHANISM_EXPLANATION": "Giải đúng một cơ chế đã dạy của {concept}, đúng phạm vi mục hiện tại.",
    "CONTRASTIVE_EXAMPLE": "Đặt cạnh nhau hai đối tượng/phương pháp đã dạy liên quan {concept} để tách chỗ nhầm.",
    "WORKED_EXAMPLE": "Một bút toán/ví dụ đã dạy cho đúng đối tượng {concept}; không ôn cả định khoản.",
    "PROCEDURE_REHEARSAL": "Làm lại đúng chuỗi bước đã dạy bị bỏ, chỉ cho {concept}.",
    "APPLICATION_PRACTICE": "Một tình huống cùng {concept} nhưng ngữ cảnh khác với ví dụ gốc trong giáo trình.",
    "PREREQUISITE_MICRO_BACKFILL": "Chỉ vá quy tắc Nợ/Có (tăng/giảm tài sản) đã dạy ở NLKT — không ôn cả chương NLKT.",
    "TERMINOLOGY_CLARIFICATION": "Phân biệt hai thuật ngữ gần nghĩa mà giáo trình tách, gắn với {concept}.",
    "MECHANICAL_CORRECTION": "Sửa đúng phép tính/sao chép số; giữ nguyên phương pháp {concept} đã chọn đúng.",
    "VERIFY_MORE": "Hỏi một câu phân biệt nguyên nhân trước khi dạy.",
    "NO_INTERVENTION": "Không can thiệp.",
}


def preview(action_type: str, concept_id: str | None) -> str:
    tmpl = PREVIEWS.get(action_type) or "Can thiệp hẹp cho {concept}."
    return tmpl.format(concept=concept_id or "khái niệm đã chẩn đoán")
