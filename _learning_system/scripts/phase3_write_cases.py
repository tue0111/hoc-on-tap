# -*- coding: utf-8 -*-
"""Controlled diagnostic cases from NLKT + KTTC1 curriculum only."""
from __future__ import annotations
import json
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

OUT = (_SYS / "evals" / "diagnostic_cases.jsonl")
OUT_MT = (_SYS / "evals" / "diagnostic_multiturn.jsonl")


def C(id, category, question, course, chapter, response, work, gold, multiturn=None):
    rec = {
        "id": id,
        "category": category,
        "input": {
            "question": question,
            "course_context": {"course_id": course, "chapter": chapter},
            "learner_response": response,
            "work_shown": work,
            "allowed_scope": ["nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"],
        },
        "gold": gold,
    }
    if multiturn:
        rec["multiturn"] = multiturn
        rec["input"]["followup_response"] = multiturn.get("followup_response")
    return rec


cases = []

# ---------- 15 NLKT current-concept ----------
nlkt = "nguyen-ly-ke-toan"
cases += [
    C("nlkt-01", "nlkt_current", "Phương trình kế toán trong Nguyên lý kế toán là gì?", nlkt, 2,
      "Tài sản = Doanh thu − Chi phí", "",
      {"target_concept": "phuong-trinh-ke-toan", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-02", "nlkt_current", "Bên Nợ của tài khoản tài sản phản ánh điều gì theo NLKT?", nlkt, 3,
      "Bên Nợ phản ánh giảm tài sản. Tăng tài sản ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "no-co", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-03", "nlkt_current", "Ghi sổ kép là gì trong Nguyên lý kế toán?", nlkt, 3,
      "Ghi sổ kép là ghi một nghiệp vụ vào đúng một tài khoản cho dễ đối chiếu.", "",
      {"target_concept": "ghi-so-kep", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-04", "nlkt_current", "Định khoản kế toán được hướng dẫn ở NLKT như thế nào?", nlkt, 3,
      "Định khoản chỉ cần ghi Có; bên Nợ tự cân bằng.", "",
      {"target_concept": "dinh-khoan", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-05", "nlkt_current", "Bút toán điều chỉnh trong Nguyên lý kế toán dùng để làm gì?", nlkt, 4,
      "Để sửa sai sót cộng nhầm trên sổ, không liên quan cơ sở dồn tích.", "",
      {"target_concept": "but-toan-dieu-chinh", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-06", "nlkt_current", "Kết chuyển để xác định kết quả kinh doanh trong NLKT?", nlkt, 4,
      "Kết chuyển là chuyển tiền mặt sang ngân hàng.", "",
      {"target_concept": "ket-chuyen", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-07", "nlkt_current", "Cơ sở dồn tích trong Nguyên lý kế toán?", nlkt, 2,
      "Chỉ ghi doanh thu khi thu được tiền mặt.", "",
      {"target_concept": "co-so-don-tich", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-08", "nlkt_current", "Bảng cân đối kế toán theo NLKT phản ánh những yếu tố nào?", nlkt, 2,
      "Chỉ có doanh thu và chi phí.", "",
      {"target_concept": "bang-can-doi-ke-toan", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-09", "nlkt_current", "Nguyên tắc phù hợp trong Nguyên lý kế toán?", nlkt, 2,
      "Phù hợp nghĩa là số dư Nợ phải bằng số dư Có trên mỗi tài khoản.", "",
      {"target_concept": "nguyen-tac-phu-hop", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-10", "nlkt_current", "Chứng từ kế toán theo môn Nguyên lý kế toán có vai trò gì?", nlkt, 5,
      "Chứng từ chỉ để lưu cho thuế, không phải căn cứ ghi sổ.", "",
      {"target_concept": "chung-tu-ke-toan", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-11", "nlkt_current", "Bản chất của kế toán theo ACCO1325?", nlkt, 1,
      "Kế toán là việc giữ tiền mặt trong két.", "",
      {"target_concept": "ke-toan-he-thong-thong-tin", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-12", "nlkt_current", "Các lĩnh vực kế toán được phân biệt thế nào trong Nguyên lý kế toán?", nlkt, 1,
      "Kế toán tài chính và kế toán quản trị là một, không khác nhau.", "",
      {"target_concept": "linh-vuc-ke-toan", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-13", "nlkt_current", "Báo cáo lưu chuyển tiền tệ trong NLKT phản ánh gì?", nlkt, 2,
      "Phản ánh khấu hao TSCĐ.", "",
      {"target_concept": "bao-cao-lctt", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-14", "nlkt_current", "Tài khoản kế toán kết cấu chữ T theo NLKT?", nlkt, 3,
      "Cột trái là Có, cột phải là Nợ.", "tăng tài sản ghi Có",
      {"target_concept": "tai-khoan-ke-toan", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("nlkt-15", "nlkt_current", "Chi phí trả trước theo NLKT được ghi nhận thế nào?", nlkt, 4,
      "Toàn bộ số tiền trả trước ghi hết vào chi phí ngay trong kỳ.", "",
      {"target_concept": "chi-phi-tra-truoc", "error_type": "conceptual_failure", "prerequisite_gap": False}),
]

# ---------- 20 KTTC1 current-concept (NOT NLKT blame) ----------
k1 = "ke-toan-tai-chinh-1"
cases += [
    C("kttc1-01", "kttc1_current", "Kế toán tiền mặt (TK 111) khi thu tiền bán hàng theo KTTC1?", k1, 2,
      "Nợ 112 / Có 511 vì em dùng nhầm tài khoản tiền gửi.", "sai tài khoản 112 thay vì 111",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "journal_entry_error", "prerequisite_gap": False}),
    C("kttc1-02", "kttc1_current", "Mua hàng hóa nhập kho, chưa trả tiền, định khoản KTTC1?", k1, 3,
      "Nợ 642 / Có 331. Ghi nhận chi phí ngay khi mua hàng hóa.", "ghi nhận vào chi phí, TK 642",
      {"target_concept": "hang-ton-kho", "error_type": "classification_error", "prerequisite_gap": False}),
    C("kttc1-03", "kttc1_current", "Các phương pháp tính giá xuất kho theo KTTC1? Tính giá xuất 50 sp, lô 1: 50@10, FIFO.", k1, 3,
      "FIFO nhưng em lấy bình quân (10+12)/2 = 11, xuất 50*11=550.", "",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "formula_selection_error", "prerequisite_gap": False}),
    C("kttc1-04", "kttc1_current", "Kê khai thường xuyên và kiểm kê định kỳ trong KTTC1 khác nhau chỗ nào?", k1, 3,
      "Hai phương pháp là một; kiểm kê định kỳ cũng ghi TK 156 liên tục.", "",
      {"target_concept": "kktx-kkdk", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("kttc1-05", "kttc1_current", "Phải thu khách hàng TK 131 khi bán chịu theo KTTC1?", k1, 2,
      "Nợ 138 / Có 511. Em chọn phải thu khác.", "",
      {"target_concept": "no-phai-thu", "error_type": "journal_entry_error", "prerequisite_gap": False}),
    C("kttc1-06", "kttc1_current", "Thông tư 200 trong KTTC1 dùng hệ thống tài khoản nào cho hàng hóa?", k1, 3,
      "TK 111. Không nhớ tài khoản hàng hóa.", "không nhớ số hiệu",
      {"target_concept": "hang-ton-kho", "error_type": "recall_failure", "prerequisite_gap": False}),
    C("kttc1-07", "kttc1_current", "Doanh thu bán hàng và thu nhập khác trong KTTC1 chương 1?", k1, 1,
      "Doanh thu và thu nhập là một, em nhầm thuật ngữ.", "",
      {"target_concept": "bao-cao-kqkd", "error_type": "terminology_confusion", "prerequisite_gap": False}),
    C("kttc1-08", "kttc1_current", "Công ty dịch vụ không có hàng hóa. Có dùng TK 156 như ví dụ bán hàng KTTC1 không?", k1, 3,
      "Có, công ty dịch vụ cũng dùng TK 156 giống ví dụ bán hàng.", "áp dụng giống ví dụ bán hàng",
      {"target_concept": "hang-ton-kho", "error_type": "transfer_failure", "prerequisite_gap": False}),
    C("kttc1-09", "kttc1_current", "Trình bày tiền trên Bảng cân đối kế toán theo KTTC1.", k1, 2,
      "Tiền chỉ hiện trên báo cáo KQKD vì là doanh thu.", "",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("kttc1-10", "kttc1_current", "Dự phòng phải thu khó đòi TK 2293 theo KTTC1?", k1, 2,
      "Nợ 131 / Có 2293 làm tăng phải thu.", "",
      {"target_concept": "no-phai-thu", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("kttc1-11", "kttc1_current", "Xuất kho hàng hóa theo FIFO, KTTC1. Lô 1 còn 40@10, xuất 40.", k1, 3,
      "FIFO, xuất 40*10 = 400 (đúng số) nhưng em nghĩ FIFO là lấy giá lô cuối.", "ra đúng số; kết quả đúng nhưng giải thích FIFO sai",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("kttc1-12", "kttc1_current", "Mua NVL nhập kho TK 152 theo KTTC1, trả tiền mặt.", k1, 3,
      "Nợ 627 / Có 111. Đưa vào chi phí sản xuất chung ngay.", "ghi nhận vào chi phí",
      {"target_concept": "hang-ton-kho", "error_type": "classification_error", "prerequisite_gap": False}),
    C("kttc1-13", "kttc1_current", "Tạm ứng TK 141 theo KTTC1 khi nhân viên lĩnh tạm ứng tiền mặt.", k1, 2,
      "Nợ 138 / Có 111.", "",
      {"target_concept": "no-phai-thu", "error_type": "journal_entry_error", "prerequisite_gap": False}),
    C("kttc1-14", "kttc1_current", "Hình thức nhật ký chung ở KTTC1 chương 1 bỏ bước nào nếu sai quy trình?", k1, 1,
      "Bỏ qua bút toán điều chỉnh rồi lên BCTC luôn.", "nhảy bước; bỏ qua bút toán điều chỉnh",
      {"target_concept": "so-sach-ke-toan", "error_type": "procedural_error", "prerequisite_gap": False}),
    C("kttc1-15", "kttc1_current", "Số dư Nợ TK 111 trên sổ KTTC1 nghĩa là gì?", k1, 2,
      "Số dư nợ là xấu, công ty đang lỗ.", "số dư nợ là xấu",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "interpretation_error", "prerequisite_gap": False}),
    C("kttc1-16", "kttc1_current", "Hàng gửi đi bán TK 157 theo KTTC1 có còn là hàng tồn kho không?", k1, 3,
      "Không, đã gửi đi thì ghi hết doanh thu, không còn HTK.", "",
      {"target_concept": "hang-ton-kho", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("kttc1-17", "kttc1_current", "Thuế GTGT được khấu trừ TK 133 khi mua hàng KTTC1?", k1, 2,
      "Nợ 156 / Có 111 gộp cả VAT vào giá hàng, không dùng 133.", "",
      {"target_concept": "no-phai-thu", "error_type": "classification_error", "prerequisite_gap": False}),
    C("kttc1-18", "kttc1_current", "Tương đương tiền theo KTTC1 gồm những khoản nào?", k1, 2,
      "Gồm cả khoản phải thu khách hàng 131.", "",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "conceptual_failure", "prerequisite_gap": False}),
    C("kttc1-19", "kttc1_current", "Kiểm kê phát hiện thiếu hàng TK 156 theo KTTC1.", k1, 3,
      "Nợ 111 / Có 156 như xuất bán thu tiền.", "",
      {"target_concept": "hang-ton-kho", "error_type": "journal_entry_error", "prerequisite_gap": False}),
    C("kttc1-20", "kttc1_current", "Bán hàng thu tiền mặt, giá vốn hàng xuất theo KTTC1 (kê khai thường xuyên).", k1, 3,
      "Chỉ Nợ 111 / Có 511, không ghi giá vốn. Hai bước đầu đúng, sai ở bước giá vốn.", "bước 1 đúng; sai ở bước giá vốn; nhảy bước",
      {"target_concept": "hang-ton-kho", "error_type": "procedural_error", "prerequisite_gap": False}),
]

# ---------- 15 KTTC1 errors caused by NLKT prerequisite ----------
# Must include explicit false Nợ/Có rule so the engine may confirm prerequisite_gap.
cases += [
    C("pre-01", "kttc1_prereq_nlkt", "Thu tiền mặt bán hàng, định khoản KTTC1 (TK 111, 511).", k1, 2,
      "Có 111 / Nợ 511 vì tăng tài sản ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-02", "kttc1_prereq_nlkt", "Mua hàng hóa nhập kho trả tiền mặt, định khoản KTTC1.", k1, 3,
      "Nợ 111 / Có 156 vì tăng tài sản ghi Có nên Có 156.", "tăng tài sản ghi Có",
      {"target_concept": "hang-ton-kho", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-03", "kttc1_prereq_nlkt", "Ứng trước cho nhân viên TK 141, xuất quỹ tiền mặt KTTC1.", k1, 2,
      "Có 141 / Nợ 111. Bên Nợ là giảm tài sản.", "nợ là giảm tài sản; tăng tài sản ghi Có",
      {"target_concept": "no-phai-thu", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-04", "kttc1_prereq_nlkt", "Gửi tiền mặt vào ngân hàng (111 → 112) theo KTTC1.", k1, 2,
      "Nợ 111 / Có 112 vì tài sản tăng bên Có.", "tài sản tăng bên Có",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-05", "kttc1_prereq_nlkt", "Xuất kho giá vốn, kê khai thường xuyên KTTC1: Nợ giá vốn / Có 156.", k1, 3,
      "Nợ 156 / Có 632 vì tăng tài sản ghi Có nên em đảo.", "tăng tài sản ghi Có",
      {"target_concept": "hang-ton-kho", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-06", "kttc1_prereq_nlkt", "Thu nợ phải thu bằng tiền mặt, KTTC1.", k1, 2,
      "Nợ 131 / Có 111. Tăng tiền ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "no-phai-thu", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-07", "kttc1_prereq_nlkt", "Mua hàng tồn kho chưa trả tiền (331) theo KTTC1.", k1, 3,
      "Có 156 / Nợ 331 vì tăng tài sản ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "hang-ton-kho", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-08", "kttc1_prereq_nlkt", "Rút tiền gửi ngân hàng về quỹ, KTTC1.", k1, 2,
      "Có 111 / Nợ 112. Tăng quỹ ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-09", "kttc1_prereq_nlkt", "Chi tiền mặt tạm ứng công tác phí, KTTC1.", k1, 2,
      "Có 141 / Nợ 111 vì bên Có phản ánh tăng tài sản.", "bên Có phản ánh tăng tài sản",
      {"target_concept": "no-phai-thu", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-10", "kttc1_prereq_nlkt", "Nhập kho thành phẩm 155 từ 154 theo KTTC1.", k1, 3,
      "Có 155 / Nợ 154. Tăng thành phẩm ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "hang-ton-kho", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-11", "kttc1_prereq_nlkt", "Bán chịu hàng hóa, ghi phải thu 131 và doanh thu KTTC1.", k1, 2,
      "Có 131 / Nợ 511 vì tăng tài sản ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "no-phai-thu", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-12", "kttc1_prereq_nlkt", "Chi tiền mặt mua hàng hóa nhập kho, KTTC1.", k1, 3,
      "Nợ 111 / Có 156. Em nghĩ tăng hàng thì ghi Có vì tăng tài sản ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "hang-ton-kho", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-13", "kttc1_prereq_nlkt", "Thu tiền gửi ngân hàng lãi, KTTC1 (111 hoặc 112).", k1, 2,
      "Có 112 / Nợ 515. Tăng TGNH ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-14", "kttc1_prereq_nlkt", "Xuất quỹ chi trả phải trả người bán, KTTC1.", k1, 2,
      "Nợ 111 / Có 331 vì giảm tiền phải ghi Nợ — nợ là giảm tài sản.", "nợ là giảm tài sản",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
    C("pre-15", "kttc1_prereq_nlkt", "Định khoản tăng quỹ tiền mặt khi rút 112, KTTC1.", k1, 2,
      "Có TK 111. Tăng tài sản ghi Có.", "tăng tài sản ghi Có",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co"}),
]

# ---------- 10 mechanical / arithmetic (NOT conceptual, NOT prereq) ----------
cases += [
    C("mech-01", "mechanical", "FIFO KTTC1: xuất 50 sp từ lô 50@10. Tính giá xuất.", k1, 3,
      "FIFO, 50 * 10 = 600. Tính nhầm phép nhân.", "FIFO; tính nhầm; 50 * 10 = 600",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-02", "mechanical", "Bình quân gia quyền KTTC1: tồn 100@10, nhập 100@20, xuất 50. Đơn giá?", k1, 3,
      "Bình quân gia quyền (10+20)/2 rồi 50*15. Đúng phương pháp; 100+200=250 nhầm tổng giá trị.", "bình quân gia quyền; cộng sai; 100+200=250",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-03", "mechanical", "FIFO KTTC1 xuất 40 từ lô 40@12.", k1, 3,
      "FIFO, 40*12. Em viết 480 thành 580 vì cộng sai.", "FIFO; cộng sai",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-04", "mechanical", "Tiền mặt tồn: quỹ 5.000.000 + thu 2.000.000 − chi 1.000.000. KTTC1.", k1, 2,
      "5.000.000+2.000.000-1.000.000=7.000.000. Cộng sai, đúng ra 6.000.000.", "cộng sai",
      {"target_concept": "tien-va-tuong-duong-tien", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-05", "mechanical", "Khấu hao đường thẳng NLKT: nguyên giá 120, 10 năm, không GTCL. Mức KH năm?", nlkt, 4,
      "120/10. Em ra 20 vì nhân sai, đúng ra 12.", "tính nhầm; nhân sai",
      {"target_concept": "khau-hao", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-06", "mechanical", "Phương trình kế toán NLKT: TS 100, Nợ phải trả 40, VCSH?", nlkt, 2,
      "100-40. Em viết VCSH=70 vì cộng sai.", "cộng sai",
      {"target_concept": "phuong-trinh-ke-toan", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-07", "mechanical", "FIFO KTTC1: xuất 10@8. Giá xuất?", k1, 3,
      "FIFO, 10*8=90. Nhân sai.", "FIFO; nhân sai; 10*8=90",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-08", "mechanical", "Bình quân liên hoàn KTTC1, đơn giá 12, xuất 5.", k1, 3,
      "Bình quân gia quyền, 5*12=50. Tính nhầm, đúng 60.", "bình quân gia quyền; tính nhầm",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-09", "mechanical", "Nợ TK 156: 80, Có TK 331: 80. Có cân không? KTTC1.", k1, 3,
      "Em cộng sai thành Nợ 90 / Có 80 dù biết Nợ phải bằng Có.", "cộng sai",
      {"target_concept": "hang-ton-kho", "error_type": "arithmetic_error", "prerequisite_gap": False}),
    C("mech-10", "mechanical", "FIFO KTTC1 lô 20@5, xuất 20.", k1, 3,
      "FIFO 20*5=90 vì nhân sai.", "FIFO; nhân sai; 20*5=90",
      {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "arithmetic_error", "prerequisite_gap": False}),
]

# ---------- 10 ambiguous / insufficient ----------
cases += [
    C("amb-01", "insufficient", "TSCĐ được ghi nhận như thế nào trong KTTC1?", k1, None,
      "Nợ 211 / Có 111.", "",
      {"target_concept": "tscd", "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-02", "insufficient", "WACC trong Kế toán tài chính 1 chương nào?", k1, None,
      "WACC = 10%.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-03", "insufficient", "IFRS 15 được giảng trong Nguyên lý kế toán như thế nào?", nlkt, None,
      "Doanh thu theo IFRS 15.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-04", "insufficient", "Định khoản nghiệp vụ vừa rồi giúp em với.", k1, 2,
      "Em không hiểu. Chưa hiểu đề.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-05", "insufficient", "Em làm sai câu kế toán.", k1, None,
      "", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-06", "insufficient", "CAPM có trong KTTC1 không?", k1, None,
      "Dùng CAPM để tính giá hàng tồn kho.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-07", "insufficient", "Kế toán vốn chủ sở hữu theo chương 3 KTTC1?", k1, 3,
      "Nợ 411 / Có 111.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-08", "insufficient", "Định mức chi phí sản xuất trong Nguyên lý kế toán ACCO1325?", nlkt, None,
      "Chi phí định mức 100.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-09", "insufficient", "Giúp em câu này.", k1, 2,
      "Không biết.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
    C("amb-10", "insufficient", "Em sai hết.", nlkt, 3,
      "Em không hiểu.", "",
      {"target_concept": None, "error_type": "unknown", "prerequisite_gap": False, "status": "INCONCLUSIVE"}),
]

# Contrastive pairs + multi-turn (20)
# Pair mechanical vs conceptual same surface number
cases.append(C(
    "mt-01", "mechanical",
    "FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?",
    k1, 3, "FIFO, 50*10=600.", "FIFO; tính nhầm; 50 * 10 = 600",
    {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "arithmetic_error", "prerequisite_gap": False, "pair": "fifo-50"},
    {"enabled": True, "followup_response": "A. Sai vì nhầm phép tính. FIFO."},
))
cases.append(C(
    "mt-02", "kttc1_current",
    "FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?",
    k1, 3, "Em lấy bình quân (10+12)/2 rồi nhân 50.", "(10 + 12)/2",
    {"target_concept": "pp-tinh-gia-xuat-kho", "error_type": "formula_selection_error", "prerequisite_gap": False, "pair": "fifo-50"},
    {"enabled": True, "followup_response": "Bình quân gia quyền."},
))
# Pair classification vs noco
cases.append(C(
    "mt-03", "kttc1_current",
    "Mua hàng hóa nhập kho trả tiền mặt, định khoản KTTC1?",
    k1, 3, "Nợ 642 / Có 111. Ghi nhận vào chi phí ngay khi mua hàng hóa.", "ghi nhận vào chi phí; 642",
    {"target_concept": "hang-ton-kho", "error_type": "classification_error", "prerequisite_gap": False, "pair": "mua-htk"},
    {"enabled": True, "followup_response": "Đó là chi phí kỳ này."},
))
cases.append(C(
    "mt-04", "kttc1_prereq_nlkt",
    "Mua hàng hóa nhập kho trả tiền mặt, định khoản KTTC1?",
    k1, 3, "Có 156 / Nợ 111 vì tăng tài sản ghi Có.", "tăng tài sản ghi Có",
    {"target_concept": "hang-ton-kho", "error_type": "prerequisite_gap", "prerequisite_gap": True, "prerequisite_concept_id": "no-co", "pair": "mua-htk"},
    {"enabled": True, "followup_response": "Tăng tiền mặt ghi Có."},
))
# more multiturn current
for i, src in enumerate([
    ("mt-05", "nlkt_current", "Ghi sổ kép là gì trong Nguyên lý kế toán?", nlkt, 3,
     "Chỉ ghi một tài khoản.", "", "ghi-so-kep", "conceptual_failure", False,
     "Em nghĩ một nghiệp vụ một tài khoản."),
    ("mt-06", "nlkt_current", "Bên Nợ tài khoản tài sản theo NLKT?", nlkt, 3,
     "Nợ là giảm. Tăng tài sản ghi Có.", "tăng tài sản ghi Có", "no-co", "conceptual_failure", False,
     "Tăng tiền mặt ghi Có."),
    ("mt-07", "kttc1_current", "Kê khai thường xuyên khác kiểm kê định kỳ KTTC1?", k1, 3,
     "Không khác.", "", "kktx-kkdk", "conceptual_failure", False,
     "B. Sai vì chọn sai đối tượng/tài khoản."),
    ("mt-08", "mechanical", "FIFO xuất 20@5 KTTC1.", k1, 3,
     "FIFO 20*5=90 nhân sai.", "FIFO; nhân sai; 20*5=90", "pp-tinh-gia-xuat-kho", "arithmetic_error", False,
     "A. Sai vì nhầm phép tính."),
    ("mt-09", "kttc1_prereq_nlkt", "Thu tiền mặt TK 111 KTTC1.", k1, 2,
     "Có 111 vì tăng tài sản ghi Có.", "tăng tài sản ghi Có", "tien-va-tuong-duong-tien", "prerequisite_gap", True,
     "Tăng tiền mặt ghi Có."),
    ("mt-10", "kttc1_current", "Thu tiền mặt TK 111, em ghi Nợ 112.", k1, 2,
     "Nợ 112 / Có 511. Nhầm tài khoản tiền gửi.", "sai 112 thay vì 111", "tien-va-tuong-duong-tien", "journal_entry_error", False,
     "Tăng tiền mặt ghi Nợ. Em chỉ nhầm 112."),
    ("mt-11", "nlkt_current", "Cơ sở dồn tích NLKT?", nlkt, 2,
     "Chỉ ghi khi có tiền.", "", "co-so-don-tich", "conceptual_failure", False,
     "B. Sai vì chọn sai đối tượng/tài khoản."),
    ("mt-12", "mechanical", "TS=80, NPT=30, VCSH NLKT?", nlkt, 2,
     "80-30=60 nhưng em viết 40 vì trừ sai.", "tính nhầm", "phuong-trinh-ke-toan", "arithmetic_error", False,
     "A. Sai vì nhầm phép tính."),
    ("mt-13", "kttc1_prereq_nlkt", "Xuất kho Có 156 KTTC1, em Nợ 156 vì tăng tài sản ghi Có.", k1, 3,
     "Nợ 156. Tăng tài sản ghi Có nên em loạn hướng.", "tăng tài sản ghi Có", "hang-ton-kho", "prerequisite_gap", True,
     "C. Sai vì hiểu ngược Nợ/Có."),
    ("mt-14", "insufficient", "Em sai câu KTTC1.", k1, None,
     "Không hiểu.", "", None, "unknown", False,
     "Vẫn không biết đối tượng."),
    ("mt-15", "kttc1_current", "Phải thu 131 hay 138 khi bán chịu KTTC1?", k1, 2,
     "Nợ 138.", "", "no-phai-thu", "journal_entry_error", False,
     "B. Sai vì chọn sai đối tượng/tài khoản."),
    ("mt-16", "nlkt_current", "Kết chuyển NLKT là gì?", nlkt, 4,
     "Chuyển tiền mặt sang NH.", "", "ket-chuyen", "conceptual_failure", False,
     "B. Sai vì chọn sai đối tượng/tài khoản."),
    ("mt-17", "mechanical", "FIFO 10@8 KTTC1.", k1, 3,
     "FIFO 10*8=90 nhân sai.", "FIFO; nhân sai; 10*8=90", "pp-tinh-gia-xuat-kho", "arithmetic_error", False,
     "A. Sai vì nhầm phép tính."),
    ("mt-18", "kttc1_prereq_nlkt", "Tăng quỹ khi rút 112, KTTC1.", k1, 2,
     "Có 111, tăng tài sản ghi Có.", "tăng tài sản ghi Có", "tien-va-tuong-duong-tien", "prerequisite_gap", True,
     "Tăng tiền mặt ghi Có."),
    ("mt-19", "kttc1_current", "Hàng gửi đi bán còn là HTK?", k1, 3,
     "Không còn HTK.", "", "hang-ton-kho", "conceptual_failure", False,
     "B. Sai vì chọn sai đối tượng/tài khoản."),
    ("mt-20", "insufficient", "IFRS 16 trong NLKT?", nlkt, None,
     "Thuê tài chính IFRS 16.", "", None, "unknown", False,
     "Vẫn theo IFRS."),
]):
    _id, cat, ques, course, ch, resp, work, tgt, et, pg, fu = src
    gold = {"target_concept": tgt, "error_type": et, "prerequisite_gap": pg}
    if pg:
        gold["prerequisite_concept_id"] = "no-co"
    if et == "unknown":
        gold["status"] = "INCONCLUSIVE"
    cases.append(C(_id, cat, ques, course, ch, resp, work, gold, {"enabled": True, "followup_response": fu}))

assert len(cases) >= 70, len(cases)
mt = [c for c in cases if c.get("multiturn", {}).get("enabled")]
assert len(mt) >= 20, len(mt)

OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")
OUT_MT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in mt), encoding="utf-8")
print("cases", len(cases), "multiturn", len(mt))
from collections import Counter
print(Counter(c["category"] for c in cases))
