# -*- coding: utf-8 -*-
"""Write evals/v3/he-thong-thong-tin-ke-toan-1_retrieval.jsonl (plan 6.7) BEFORE any tuning.
Refuses to overwrite an existing file (frozen once its first run is recorded)."""
import json, sys
from pathlib import Path

SYS = Path(__file__).resolve().parents[2]
CID = "he-thong-thong-tin-ke-toan-1"
OUT = SYS / "evals" / "v3" / f"{CID}_retrieval.jsonl"
OTHERS = ["nguyen-ly-ke-toan", "ke-toan-tai-chinh-1", "ke-toan-tai-chinh-2", "ke-toan-chi-phi", "kiem-toan-1",
          "ke-toan-ngan-hang", "ngan-hang-thuong-mai", "tai-chinh-doanh-nghiep-1", "thi-truong-tai-chinh",
          "tai-chinh-hanh-chinh-su-nghiep", "luat-kinh-doanh", "kinh-doanh-va-nghiep-vu",
          "ke-toan-thue-1", "ke-toan-tai-chinh-3", "ke-toan-hanh-chinh-su-nghiep"]

ROWS = [
    # id, category, question, expected_chapter, must_include, mode
    ("ht-d01", "direct", "Hệ thống thông tin kế toán 1: hệ thống thông tin kế toán gồm những thành phần nào?", 1, ["src-0344"], None),
    ("ht-d02", "direct", "HTTTKT1: các nhóm hàm Excel thường dùng trong kế toán gồm những nhóm nào?", 2, ["src-0355"], None),
    ("ht-d03", "direct", "HTTTKT1: dữ liệu kế toán được tổ chức trên sheet BDMTK và sheet SOKTMAY như thế nào?", 2, ["src-0353"], None),
    ("ht-d04", "direct", "HTTTKT1: thao tác kết chuyển số liệu kế toán cho hoạt động sản xuất trên bảng tính làm thế nào?", 2, ["src-0354"], None),
    ("ht-d05", "direct", "Hệ thống thông tin kế toán 1: cách lập sổ nhật ký thu tiền trên Excel?", 3, ["src-0365"], None),
    ("ht-d06", "direct", "HTTTKT1: sổ nhật ký mua hàng dùng để theo dõi gì và lập ra sao?", 3, ["src-0363"], None),
    ("ht-d07", "direct", "HTTTKT1: những nghiệp vụ nào được ghi vào sổ nhật ký chung?", 3, ["src-0364"], None),
    ("ht-d08", "direct", "HTTTKT1: lập thẻ tính giá thành sản phẩm bằng hàm DSUM như thế nào?", 4, ["src-0377"], None),
    ("ht-d09", "direct", "Hệ thống thông tin kế toán 1: lập sổ cái tài khoản tổng hợp trên bảng tính thế nào?", 4, ["src-0378"], None),
    ("ht-d10", "direct", "HTTTKT1: sổ chi phí sản xuất kinh doanh dùng để làm gì?", 4, ["src-0379"], None),
    ("ht-d11", "direct", "HTTTKT1: bảng cân đối số phát sinh các tài khoản tổng hợp lập bằng công thức nào?", 5, ["src-0392"], None),
    ("ht-d12", "direct", "HTTTKT1: bảng tổng hợp chi tiết công nợ phải thu, phải trả lập thế nào?", 5, ["src-0390"], None),
    ("ht-d13", "direct", "Hệ thống thông tin kế toán 1: lập bảng cân đối kế toán trên bảng tính Excel như thế nào?", 6, ["src-0402"], None),
    ("ht-d14", "direct", "HTTTKT1: lập báo cáo lưu chuyển tiền tệ theo phương pháp trực tiếp trên bảng tính ra sao?", 6, ["src-0401"], None),
    ("ht-s01", "source_bound", "Theo chương 3 của Hệ thống thông tin kế toán 1, có những sổ nhật ký nào?", 3, ["src-0363", "src-0364", "src-0365"], "source_bound"),
    ("ht-s02", "source_bound", "Đề thi mẫu HTTTKT1 gồm những câu hỏi nào?", None, ["src-0405"], "source_bound"),
    ("ht-s03", "source_bound", "Hướng dẫn ôn tập HTTTKT1 yêu cầu học những gì?", None, ["src-0406"], "source_bound"),
    ("ht-i01", "insufficient", "Hệ thống thông tin kế toán 1: quy trình kiểm toán gồm những giai đoạn nào?", None, [], None),
    ("ht-i02", "insufficient", "HTTTKT1: lãi suất tái chiết khấu của ngân hàng trung ương là gì?", None, [], None),
    ("ht-i03", "insufficient", "Trong HTTTKT1, hợp đồng thương mại vô hiệu khi nào?", None, [], None),
    ("ht-c01", "collision", "Chương 1 của Hệ thống thông tin kế toán 1 nói về gì?", 1, [], None),
    ("ht-c02", "collision", "Chương 6 của HTTTKT1 nói về gì?", 6, [], None),
    ("ht-a01", "account", "HTTTKT1: tài khoản 621 được theo dõi trên sổ nào?", None, ["src-0379"], None),
    ("ht-a02", "account", "HTTTKT1: TK 6279 được phân bổ thế nào khi kết chuyển?", None, ["src-0354"], None),
]


def main():
    if OUT.exists():
        sys.exit(f"refuse: {OUT} exists (frozen after first run)")
    with OUT.open("w", encoding="utf-8") as f:
        for i, cat, q, ch, must, mode in ROWS:
            f.write(json.dumps({"id": i, "course": CID, "category": cat, "question": q, "expected_course": CID,
                                "expected_chapter": ch, "expected_concepts": [], "expected_source_types": [],
                                "must_include_source_ids": must, "must_not_include_courses": OTHERS,
                                "expected_coverage": "insufficient" if cat == "insufficient" else "sufficient",
                                "mode": mode}, ensure_ascii=False) + "\n")
    print("wrote", len(ROWS), "rows ->", OUT)


if __name__ == "__main__":
    main()
