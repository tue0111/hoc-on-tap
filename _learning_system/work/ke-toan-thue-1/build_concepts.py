# -*- coding: utf-8 -*-
"""Build curriculum/concepts/ke-toan-thue-1.yaml (playbook 6.5, judgment step).

canonical_name = exact heading text (Chương / Chủ đề lines on script page 1, or a
"Slide N." heading line for cross-topic terms). Aliases are strings present in the
course text (checked by count_terms.py and the validator).
"""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "curriculum" / "concepts" / "ke-toan-thue-1.yaml"


def c(cid, name, aliases, ch, topic, refs, chapters=None, conf="high", same_as=None):
    d = {"concept_id": "thue1-" + cid, "canonical_name": name, "aliases": aliases, "same_as": same_as,
         "chapter": ch, "topic": topic}
    if chapters:
        d["chapters"] = chapters
    d.update({"source_refs": [{"source_id": s, "page": p} for s, p in refs], "evidence_status": "OBSERVED",
              "confidence": conf})
    return d


concepts = [
    # chapter 0 (DOCX script, src-0539)
    c("gioi-thieu-mon-hoc", "Giới thiệu môn học", [], 0, None, [("src-0539", 1)]),
    # chapter-level concepts (heading "Chương n: ..." on every script page 1)
    c("tong-quan-ve-ke-toan-thue", "Tổng quan về kế toán & thuế", ["tổng quan về kế toán và thuế"], 1, None,
      [("src-0498", 1), ("src-0492", 1)]),
    c("ke-toan-thue-xuat-khau-nhap-khau", "Kế toán thuế xuất khẩu – nhập khẩu",
      ["thuế xuất khẩu", "thuế nhập khẩu", "thuế XK"], 2, None, [("src-0500", 1), ("src-0504", 1)]),
    c("ke-toan-thue-tieu-thu-dac-biet", "Kế toán thuế Tiêu thụ đặc biệt", ["thuế tiêu thụ đặc biệt", "thuế TTĐB"], 3, None,
      [("src-0510", 1), ("src-0514", 1)]),
    # heading typo "mội trường" kept verbatim; correct spelling is an alias present in text
    c("ke-toan-thue-bao-ve-moi-truong", "Kế toán thuế Bảo vệ mội trường", ["thuế bảo vệ môi trường", "thuế BVMT"], 4, None,
      [("src-0520", 1), ("src-0524", 1)]),
    c("ke-toan-thue-gia-tri-gia-tang", "Kế toán thuế Giá trị gia tăng", ["thuế giá trị gia tăng", "thuế GTGT"], 5, None,
      [("src-0530", 1), ("src-0536", 1)]),
    # chapter 1 topics
    c("he-thong-cac-quy-dinh-ve-ke-toan-va-chinh-sach-thue", "Hệ thống các quy định về kế toán và chính sách thuế",
      ["văn bản pháp quy về kế toán", "mối quan hệ giữa kế toán và thuế"], 1, "1.1", [("src-0498", 1)]),
    c("gioi-thieu-he-thong-cac-quy-dinh-co-ban-cua-luat-quan-ly-thue",
      "Giới thiệu hệ thống các quy định cơ bản của Luật quản lý thuế", ["Luật quản lý thuế"], 1, "1.2", [("src-0492", 1)]),
    c("su-dung-so-lieu-ke-toan-de-lap-cac-bao-cao-thue", "Sử dụng số liệu kế toán để lập các báo cáo thuế",
      ["số liệu tính thuế"], 1, "1.3", [("src-0494", 1)]),
    c("su-dung-cac-cong-cu-de-lap-bao-cao-thue", "Sử dụng các công cụ để lập báo cáo thuế", ["phần mềm HTKK", "HTKK"], 1,
      "1.4", [("src-0496", 1)]),
    # chapter 2 topics
    c("cac-noi-dung-co-ban-lien-quan-den-thue-xk-nk", "Các nội dung cơ bản liên quan đến thuế XK – NK",
      ["Luật thuế xuất khẩu"], 2, "2.1", [("src-0500", 1)]),
    c("xac-dinh-nghia-vu-thue-xk-nk-tai-doanh-nghiep", "Xác định nghĩa vụ thuế XK - NK tại doanh nghiệp",
      ["nghĩa vụ thuế XK"], 2, "2.2", [("src-0502", 1)]),
    c("to-chuc-chung-tu-va-ghi-nhan-thue-xk-nk-tren-so-ke-toan", "Tổ chức chứng từ và ghi nhận thuế XK - NK trên sổ kế toán",
      ["ghi nhận thuế XK"], 2, "2.3", [("src-0504", 1)]),
    c("trinh-bay-va-lap-bao-cao-thue-xk-nk", "Trình bày và lập báo cáo thuế XK- NK", ["báo cáo thuế XK"], 2, "2.4",
      [("src-0506", 1)]),
    c("nhan-dien-rui-ro-va-co-hoi-ve-thue-xk-nk-tai-doanh-nghiep",
      "Nhận diện rủi ro và cơ hội về thuế XK - NK tại doanh nghiệp", ["rủi ro và cơ hội về thuế XK"], 2, "2.5",
      [("src-0508", 1)]),
    # chapter 3 topics
    c("cac-noi-dung-co-ban-lien-quan-den-thue-ttdb", "Các nội dung cơ bản liên quan đến thuế TTĐB",
      ["Luật thuế tiêu thụ đặc biệt"], 3, "3.1", [("src-0510", 1)]),
    c("xac-dinh-nghia-vu-thue-ttdb-tai-doanh-nghiep", "Xác định nghĩa vụ thuế TTĐB tại doanh nghiệp",
      ["nghĩa vụ thuế TTĐB"], 3, "3.2", [("src-0512", 1)]),
    c("to-chuc-chung-tu-va-ghi-nhan-thue-ttdb-tren-so-ke-toan", "Tổ chức chứng từ và ghi nhận thuế TTĐB trên sổ kế toán",
      ["ghi nhận thuế TTĐB"], 3, "3.3", [("src-0514", 1)]),
    c("trinh-bay-va-lap-bao-cao-thue-ttdb", "Trình bày và lập báo cáo thuế TTĐB", ["báo cáo thuế TTĐB"], 3, "3.4",
      [("src-0516", 1)]),
    c("nhan-dien-nhung-rui-ro-va-co-hoi-ve-thue-ttdb-tai-doanh-nghiep",
      "Nhận diện những rủi ro và cơ hội về thuế TTĐB tại doanh nghiệp", ["rủi ro và cơ hội về thuế TTĐB"], 3, "3.5",
      [("src-0518", 1)]),
    # chapter 4 topics
    c("cac-noi-dung-co-ban-lien-quan-den-thue-bvmt", "Các nội dung cơ bản liên quan đến thuế BVMT",
      ["Luật thuế bảo vệ môi trường"], 4, "4.1", [("src-0520", 1)]),
    c("xac-dinh-nghia-vu-thue-bvmt-tai-doanh-nghiep", "Xác định nghĩa vụ thuế BVMT tại doanh nghiệp",
      ["nghĩa vụ thuế BVMT"], 4, "4.2", [("src-0522", 1)]),
    c("to-chuc-chung-tu-va-ghi-nhan-thue-bvmt-tren-so-ke-toan", "Tổ chức chứng từ và ghi nhận thuế BVMT trên sổ kế toán",
      ["ghi nhận thuế BVMT"], 4, "4.3", [("src-0524", 1)]),
    c("trinh-bay-va-lap-bao-cao-thue-bvmt", "Trình bày và lập báo cáo thuế BVMT", ["báo cáo thuế BVMT"], 4, "4.4",
      [("src-0526", 1)]),
    c("nhan-dien-nhung-rui-ro-va-co-hoi-ve-thue-bvmt-tai-doanh-nghiep",
      "Nhận diện những rủi ro và cơ hội về thuế BVMT tại doanh nghiệp", ["rủi ro và cơ hội về thuế BVMT"], 4, "4.5",
      [("src-0528", 1)]),
    # chapter 5 topics
    c("cac-noi-dung-co-ban-lien-quan-den-thue-gtgt", "Các nội dung cơ bản liên quan đến thuế GTGT",
      ["Luật thuế giá trị gia tăng"], 5, "5.1", [("src-0530", 1)]),
    c("xac-dinh-nghia-vu-thue-gtgt-cua-doanh-nghiep", "Xác định nghĩa vụ thuế GTGT của doanh nghiệp",
      ["nghĩa vụ thuế GTGT", "phương pháp khấu trừ"], 5, "5.2", [("src-0532", 1)]),
    c("to-chuc-hoa-don-chung-tu", "Tổ chức hóa đơn, chứng từ", [], 5, "5.3", [("src-0534", 1)]),
    c("trinh-bay-va-lap-bao-cao-thue-gtgt", "Trình bày và lập báo cáo thuế GTGT", ["báo cáo thuế GTGT"], 5, "5.4",
      [("src-0536", 1)]),
    c("nhan-dien-rui-ro-va-co-hoi-ve-thue-gtgt", "Nhận diện rủi ro và cơ hội về thuế GTGT",
      ["rủi ro và cơ hội về thuế GTGT"], 5, "5.5", [("src-0538", 1)]),
    # cross-topic terms (>=3 occurrences; canonical from a "Slide N." heading line)
    c("hoan-thue", "Hoàn thuế", [], 1, "1.2", [("src-0492", 4)], chapters=[2, 5], conf="medium"),
    c("hoa-don-dien-tu", "Hóa đơn điện tử", [], 1, "1.2", [("src-0492", 5)], chapters=[5], conf="medium"),
    c("doi-tuong-khong-chiu-thue", "Đối tượng không chịu thuế", [], 2, "2.1",
      [("src-0500", 2), ("src-0510", 3), ("src-0520", 4)], chapters=[3, 4, 5], conf="medium"),
    c("tri-gia-tinh-thue", "trị giá tính thuế", [], 2, "2.1", [("src-0500", 4), ("src-0500", 5)], conf="medium"),
    c("to-khai-hai-quan", "Tờ khai hải quan", [], 2, "2.3", [("src-0504", 1)], chapters=[3], conf="medium"),
]

account_map = {
    "3333": "thue1-to-chuc-chung-tu-va-ghi-nhan-thue-xk-nk-tren-so-ke-toan",
    "3332": "thue1-to-chuc-chung-tu-va-ghi-nhan-thue-ttdb-tren-so-ke-toan",
    "3331": "thue1-ke-toan-thue-gia-tri-gia-tang",
    "1331": "thue1-ke-toan-thue-gia-tri-gia-tang",
}

doc = {"course_id": "ke-toan-thue-1", "version": "0.1.0", "id_prefix": "thue1", "concepts": concepts,
       "account_map": account_map, "edges": [], "conflicts": [],
       "notes": ["33381 (thuế BVMT) and 33311/33312 are 5-digit sub-accounts; course account regex matches 3-4 digits only, so they are not mapped.",
                 "Chương 4 heading spells 'Bảo vệ mội trường' (typo, verbatim); 'thuế bảo vệ môi trường' kept as alias.",
                 "Law/circular references are as taught (curriculum vintage); currency of regulations is handled by the external layer."]}
OUT.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
print("wrote", OUT, len(concepts), "concepts")
