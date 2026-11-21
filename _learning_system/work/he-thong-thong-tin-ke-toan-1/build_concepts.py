# -*- coding: utf-8 -*-
"""Build curriculum/concepts/he-thong-thong-tin-ke-toan-1.yaml (plan 6.5, the judgment step).
Judgment is in SPEC below (canonical names copied from headings; aliases only strings seen in text).
The script only resolves source_refs pages (pages of the named sources that contain the name/alias)
and refuses to write if any name/alias is absent from the course text.
"""
import json, re, sys
from pathlib import Path

import yaml

SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
from retrieval import courses as C  # noqa: E402
from retrieval.textutil import fold  # noqa: E402

CID = "he-thong-thong-tin-ke-toan-1"
T = lambda s: fold(re.sub(r"\s+", " ", s or ""))

# (slug, canonical_name, aliases, chapter, topic, preferred sources, heading_source note)
SPEC = [
    ("chuong-mo-dau-gioi-thieu-mon-hoc", "Chương mở đầu: Giới thiệu môn học", [], 0, "0", ["src-0404"]),
    ("tong-quan-ve-he-thong-thong-tin-ke-toan", "Tổng quan về hệ thống thông tin kế toán",
     ["khái niệm hệ thống thông tin kế toán", "thành phần của HTTTKT"], 1, "1", ["src-0344", "src-0406"]),
    ("httt-ke-toan-duoi-tac-dong-cua-cntt", "HTTT Kế toán dưới tác động của CNTT",
     ["tác động CNTT", "hệ thống ERP", "PMKT chuyên dụng"], 1, "1", ["src-0344"]),
    ("nghe-nghiep-lien-quan-den-htttkt", "nghề nghiệp liên quan đến HTTTKT",
     ["hệ thống AIS", "hướng nghề nghiệp"], 1, "1", ["src-0344"]),
    ("to-chuc-du-lieu-ke-toan-tren-moi-truong-bang-tinh", "Tổ chức dữ liệu kế toán trên môi trường bảng tính",
     [], 2, None, ["src-0353", "src-0406"]),
    ("cac-ham-thuong-dung-trong-ke-toan", "Các hàm thường dùng trong kế toán",
     ["hàm thường dùng", "các hàm ứng dụng trong excel kế toán"], 2, "2.1", ["src-0355"]),
    ("nhom-ham-logic", "Nhóm hàm Logic", ["hàm điều kiện IF"], 2, "2.1", ["src-0355"]),
    ("nhom-ham-text", "Nhóm hàm Text", ["hàm LEFT"], 2, "2.1", ["src-0355"]),
    ("nhom-ham-statistics", "Nhóm hàm Statistics", ["SUMIF"], 2, "2.1", ["src-0355", "src-0392", "src-0402"]),
    ("nhom-ham-lookup", "Nhóm hàm Lookup", ["VLOOKUP"], 2, "2.1", ["src-0355", "src-0377", "src-0390"]),
    ("nhom-ham-database", "Nhóm hàm Database", ["DSUM", "vùng điều kiện"], 2, "2.1", ["src-0355", "src-0377", "src-0400"]),
    ("to-chuc-du-lieu-tren-moi-truong-bang-tinh", "Tổ chức dữ liệu trên môi trường bảng tính",
     ["tổ chức dữ liệu kế toán"], 2, "2.2", ["src-0353"]),
    ("sheet-bdmtk", "sheet BDMTK", ["BDMTK", "bảng danh mục tài khoản"], 2, "2.2", ["src-0353", "src-0392"]),
    ("sheet-soktmay", "sheet SOKTMAY", ["SOKTMAY", "sổ kế toán máy"], 2, "2.2", ["src-0353", "src-0378"]),
    ("ket-chuyen-so-lieu-ke-toan", "Kết chuyển số liệu kế toán",
     ["thao tác kết chuyển", "kết chuyển cho hoạt động sản xuất"], 2, "2.3", ["src-0354"]),
    ("ky-thuat-lap-cac-so-nhat-ky", "Kỹ thuật lập các sổ nhật ký", [], 3, None, ["src-0363", "src-0406"]),
    ("hinh-thuc-ke-toan-nhat-ky-chung", "hình thức kế toán Nhật ký chung",
     ["nhật ký đặc biệt"], 3, "3.1", ["src-0365", "src-0364"]),
    ("lap-nhat-ky-thu-tien-va-nhat-ky-chi-tien", "Lập nhật ký thu tiền và nhật ký chi tiền",
     ["nhật ký thu tiền", "nhật ký chi tiền"], 3, "3.1", ["src-0365"]),
    ("lap-nhat-ky-mua-hang-va-nhat-ky-ban-hang", "Lập nhật ký mua hàng và nhật ký bán hàng",
     ["nhật ký mua hàng", "nhật ký bán hàng"], 3, "3.2", ["src-0363"]),
    ("lap-nhat-ky-chung", "Lập nhật ký chung", ["sổ nhật ký chung", "mẫu sổ nhật ký chung"], 3, "3.3", ["src-0364"]),
    ("ky-thuat-lap-so-chi-tiet-va-so-cai-tai-khoan", "Kỹ thuật lập sổ chi tiết và sổ cái tài khoản",
     [], 4, None, ["src-0406"]),
    ("cac-so-chi-tiet-thanh-toan", "Các sổ chi tiết thanh toán", ["sổ chi tiết thanh toán"], 4, "4.1", ["src-0406"]),
    ("so-chi-tiet-tien-mat", "Sổ chi tiết tiền mặt", [], 4, "4.2", ["src-0406"]),
    ("so-chi-tiet-hang-ton-kho", "Sổ chi tiết hàng tồn kho", [], 4, "4.3", ["src-0406", "src-0376"]),
    ("so-chi-phi-san-xuat-kinh-doanh", "Sổ chi phí sản xuất kinh doanh", [], 4, "4.4", ["src-0379"]),
    ("the-tinh-gia-thanh-san-pham", "Thẻ tính giá thành sản phẩm", ["thẻ tính giá thành"], 4, "4.5", ["src-0377"]),
    ("so-cai-tai-khoan-tong-hop", "Sổ cái tài khoản tổng hợp", [], 4, "4.6", ["src-0406", "src-0378"]),
    ("ky-thuat-lap-cac-bang-tong-hop-chi-tiet", "Kỹ thuật lập các bảng tổng hợp chi tiết", [], 5, None, ["src-0406", "src-0388"]),
    ("bang-can-doi-so-phat-sinh-cac-tai-khoan-tong-hop", "Bảng cân đối số phát sinh các tài khoản tổng hợp",
     ["bảng cân đối số phát sinh"], 5, "5.1", ["src-0392"]),
    ("bang-tong-hop-chi-tiet-hang-ton-kho", "Bảng tổng hợp chi tiết hàng tồn kho", [], 5, "5.2", ["src-0388", "src-0389"]),
    ("bang-tong-hop-chi-tiet-cong-no", "Bảng tổng hợp chi tiết công nợ", [], 5, "5.3", ["src-0388", "src-0390"]),
    ("bang-tong-hop-chi-tiet-cac-tai-khoan-khac", "Bảng tổng hợp chi tiết các tài khoản khác", [], 5, "5.4", ["src-0392", "src-0391", "src-0388"]),
    ("lap-bao-cao-tai-chinh-tren-bang-tinh", "Lập báo cáo tài chính trên bảng tính", [], 6, None, ["src-0400", "src-0404"]),
    ("lap-bang-can-doi-ke-toan", "Lập bảng cân đối kế toán", [], 6, "6.1", ["src-0402"]),
    ("lap-bao-cao-ket-qua-hoat-dong-kinh-doanh", "Lập báo cáo kết quả hoạt động kinh doanh", [], 6, "6.2", ["src-0400"]),
    ("lap-bao-cao-luu-chuyen-tien-te", "Lập báo cáo lưu chuyển tiền tệ", [], 6, "6.3", ["src-0401"]),
]

ACCOUNTS = {  # account -> slug; only accounts with count >= 2 in the indexed text (concept_candidates.json)
    "621": "so-chi-phi-san-xuat-kinh-doanh",
    "154": "the-tinh-gia-thanh-san-pham",
    "6279": "ket-chuyen-so-lieu-ke-toan",
    "911": "ket-chuyen-so-lieu-ke-toan",
    "4212": "ket-chuyen-so-lieu-ke-toan",
    "5111": "lap-nhat-ky-thu-tien-va-nhat-ky-chi-tien",
    "1521": "lap-nhat-ky-mua-hang-va-nhat-ky-ban-hang",
    "331": "lap-nhat-ky-mua-hang-va-nhat-ky-ban-hang",
}

EDGES = []  # filled only with quotable explicit sequences (see EDGE_SPEC)
EDGE_SPEC = [
    # (from, to, quote, source_id, page)
    ("sheet-soktmay", "lap-nhat-ky-mua-hang-va-nhat-ky-ban-hang",
     "sổ Nhật ký mua hàng sẽ lấy dữ liệu từ sheet SOKTMAY", "src-0363", 3),
    ("sheet-soktmay", "lap-nhat-ky-chung", "sổ Nhật ký chung sẽ lấy dữ liệu từ sheet SOKTMAY", "src-0364", 3),
    ("lap-nhat-ky-chung", "so-cai-tai-khoan-tong-hop",
     "kế toán sử dụng sổ Nhật ký chung để ghi chép tất cả nghiệp vụ kinh tế phát sinh theo trình tự thời gian "
     "để làm cơ sở cho việc ghi vào Sổ cái của các tài khoản", "src-0365", 2),
]


def main():
    p = C.partition_paths(CID)
    pages = [json.loads(l) for l in p["pages"].open(encoding="utf-8")]
    ptxt = {(pg["source_id"], pg["page"]): T(pg["text"]) for pg in pages}
    alltxt = list(ptxt.values())
    errs, concepts = [], []
    for slug, name, aliases, ch, topic, srcs in SPEC:
        names = [name] + aliases
        for n in names:
            if not any(T(n) in t for t in alltxt): errs.append(f"{slug}: '{n}' not in text")
        refs = []
        for s in srcs:
            hit = sorted(pg for (sid, pg), t in ptxt.items() if sid == s and any(T(n) in t for n in names))
            if hit: refs.append({"source_id": s, "page": hit[0]})
        if not refs: errs.append(f"{slug}: no source_ref page found in {srcs}")
        concepts.append({"concept_id": f"httt1-{slug}", "canonical_name": name, "aliases": aliases, "same_as": None,
                         "chapter": ch, "topic": topic, "source_refs": refs, "evidence_status": "OBSERVED",
                         "confidence": "high" if refs and refs[0]["source_id"] == srcs[0] else "medium"})
    if errs:
        print("\n".join(errs)); sys.exit(1)
    doc = {"course_id": CID, "version": "0.1.0", "id_prefix": "httt1", "concepts": concepts,
           "account_map": {a: f"httt1-{s}" for a, s in ACCOUNTS.items()},
           "edges": [{"from": f"httt1-{a}", "to": f"httt1-{b}", "type": "explicit_sequence", "quote": q,
                      "source_id": s, "page": pg} for a, b, q, s, pg in EDGE_SPEC],
           "conflicts": [],
           "prerequisites_observed": [{
               "statement": "Môn học HTTTKT 1 là môn chuyên ngành; được học sau môn kế toán tài chính.",
               "source_id": "src-0404", "page": 2, "evidence_status": "OBSERVED",
               "family": "ke-toan-tai-chinh", "which_part": "UNKNOWN",
               "note": "Proposal only; registry not edited (W6b phase B). NLKT is not named in the text."}]}
    p["concepts"].write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("wrote", len(concepts), "concepts")


if __name__ == "__main__":
    main()
