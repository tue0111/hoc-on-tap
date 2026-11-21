# -*- coding: utf-8 -*-
"""Write evals/v3/ke-toan-thue-1_retrieval.jsonl (playbook 6.7) BEFORE any tuning. Refuses to overwrite."""
import json, sys
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evals" / "v3" / "ke-toan-thue-1_retrieval.jsonl"
if OUT.exists(): sys.exit("eval exists: frozen, not rewriting")
C = "ke-toan-thue-1"
reg = yaml.safe_load((ROOT / "curriculum" / "course_registry.yaml").read_text(encoding="utf-8"))
others = [c["id"] for c in reg["courses"] if c["id"] not in (C, "learner-notes", "external")]
rows = []
def row(i, cat, q, ch=None, must=(), mode=None, cov="sufficient"):
    rows.append({"id": i, "course": C, "category": cat, "question": q, "expected_course": C, "expected_chapter": ch,
                 "expected_concepts": [], "expected_source_types": [], "must_include_source_ids": list(must),
                 "must_not_include_courses": others, "expected_coverage": cov, "mode": mode})
row("th-d01", "direct", "Kế toán thuế 1: Luật quản lý thuế có vai trò gì và nguyên tắc quản lý thuế gồm những gì?", 1, ["src-0492"])
row("th-d02", "direct", "Kế toán thuế 1: số liệu kế toán và số liệu tính thuế giống và khác nhau ở điểm nào?", 1, ["src-0494"])
row("th-d03", "direct", "Kế toán thuế 1: dùng phần mềm HTKK để lập tờ khai thuế như thế nào?", 1, ["src-0496"])
row("th-d04", "direct", "Kế toán thuế 1: xác định số thuế nhập khẩu phải nộp của doanh nghiệp như thế nào?", 2, ["src-0502"])
row("th-d05", "direct", "Kế toán thuế 1: hạch toán thuế nhập khẩu phải nộp khi nhập khẩu hàng hóa ghi sổ thế nào?", 2, ["src-0504"])
row("th-d06", "direct", "Kế toán thuế 1: đối tượng chịu thuế tiêu thụ đặc biệt gồm những hàng hóa, dịch vụ nào?", 3, ["src-0510"])
row("th-d07", "direct", "Kế toán thuế 1: chứng từ và cách hạch toán thuế tiêu thụ đặc biệt phải nộp khi bán hàng chịu thuế?", 3, ["src-0514"])
row("th-d08", "direct", "Kế toán thuế 1: đối tượng chịu thuế bảo vệ môi trường gồm những loại hàng hóa nào?", 4, ["src-0520"])
row("th-d09", "direct", "Kế toán thuế 1: tính thuế GTGT theo phương pháp khấu trừ và phương pháp trực tiếp khác nhau thế nào?", 5, ["src-0532"])
row("th-d10", "direct", "Kế toán thuế 1: trình bày thuế GTGT trên báo cáo tài chính và lập tờ khai thuế GTGT như thế nào?", 5, ["src-0536"])
row("th-s01", "source_bound", "Theo chương 2 của Kế toán thuế 1, kế toán thuế xuất khẩu nhập khẩu gồm những chủ đề nào?", 2,
    ["src-0500", "src-0502", "src-0504", "src-0506", "src-0508"], "source_bound")
row("th-s02", "source_bound", "Đề thi mẫu Kế toán thuế 1 gồm những dạng câu hỏi nào?", None, ["src-0541"], "source_bound")
row("th-s03", "source_bound", "Hướng dẫn học tập môn Kế toán thuế 1 yêu cầu chuẩn bị và học những gì?", None, ["src-0542"], "source_bound")
row("th-i01", "insufficient", "WACC trong Kế toán thuế 1 được tính như thế nào?", cov="insufficient")
row("th-i02", "insufficient", "Kế toán thuế 1 hướng dẫn xử lý chênh lệch tỷ giá hối đoái cuối kỳ thế nào?", cov="insufficient")
row("th-i03", "insufficient", "Kế toán thuế 1: khi nào kiểm toán viên đưa ra ý kiến kiểm toán ngoại trừ?", cov="insufficient")
row("th-c01", "collision", "Chương 1 của Kế toán thuế 1 nói về gì?", 1)
row("th-c02", "collision", "Chương 3 của Kế toán thuế 1 nói về gì?", 3)
row("th-a01", "account", "Kế toán thuế 1: tài khoản 3333 dùng để hạch toán gì?", None, ["src-0504", "src-0506"])
row("th-a02", "account", "Kế toán thuế 1: TK 3332 phản ánh nội dung gì?", None, ["src-0514", "src-0516"])
with OUT.open("w", encoding="utf-8") as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + "\n")
print("wrote", OUT, len(rows))
