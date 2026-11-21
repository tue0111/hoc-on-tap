# -*- coding: utf-8 -*-
"""Writes curriculum/concepts/ke-toan-tai-chinh-3.yaml from the hand-written spec below.
source_refs are computed mechanically (first pages containing the canonical name or an alias,
own-topic documents first). Every string was checked against the extracted text."""
import json, re, sys
from pathlib import Path

SYS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SYS))
import yaml
from retrieval.textutil import fold

CID = "ke-toan-tai-chinh-3"
T = lambda s: fold(re.sub(r"\s+", " ", s or ""))
pages = [json.loads(l) for l in (SYS / "data/normalized" / f"{CID}.pages.jsonl").open(encoding="utf-8")]
docs = {json.loads(l)["source_id"]: json.loads(l) for l in (SYS / "data/normalized" / f"{CID}.documents.jsonl").open(encoding="utf-8")}

# (slug, canonical_name (exact heading text), aliases, chapter, topic, confidence)
SPEC = [
    ("gioi-thieu-mon-hoc", "GIỚI THIỆU MÔN HỌC", ["mục tiêu của môn học"], 0, None, "high"),
    # Chương 1: KẾ TOÁN NGOẠI TỆ VÀ KINH DOANH XUẤT NHẬP KHẨU
    ("tong-quan-ve-ngoai-te", "TỔNG QUAN VỀ NGOẠI TỆ", ["tỷ giá hối đoái", "đơn vị tiền tệ kế toán", "khoản mục tiền tệ có gốc ngoại tệ", "khoản mục phi tiền tệ"], 1, "1.1", "high"),
    ("ke-toan-giao-dich-phat-sinh-bang-ngoai-te", "KẾ TOÁN GIAO DỊCH PHÁT SINH BẰNG NGOẠI TỆ", ["giao dịch bằng ngoại tệ", "tỷ giá ghi sổ bình quân", "tỷ giá giao dịch thực tế"], 1, "1.2", "high"),
    ("ke-toan-danh-gia-chenh-lech-ty-gia-cuoi-ky", "KẾ TOÁN ĐÁNH GIÁ CHÊNH LỆCH TỶ GIÁ CUỐI KỲ", ["chênh lệch tỷ giá cuối kỳ", "đánh giá lại các khoản mục tiền tệ"], 1, "1.3", "high"),
    ("ke-toan-hoat-dong-nhap-khau-truc-tiep", "KẾ TOÁN HOẠT ĐỘNG NHẬP KHẨU TRỰC TIẾP", ["nhập khẩu trực tiếp"], 1, "1.4", "high"),
    ("ke-toan-hoat-dong-xuat-khau-truc-tiep", "KẾ TOÁN HOẠT ĐỘNG XUẤT KHẨU TRỰC TIẾP", ["xuất khẩu trực tiếp"], 1, "1.5", "high"),
    ("chenh-lech-ty-gia-hoi-doai", "chênh lệch tỷ giá hối đoái", ["chênh lệch tỷ giá"], 1, None, "medium"),
    # Chương 2: KẾ TOÁN BẤT ĐỘNG SẢN ĐẦU TƯ
    ("ke-toan-bat-dong-san-dau-tu", "KẾ TOÁN BẤT ĐỘNG SẢN ĐẦU TƯ", ["bất động sản đầu tư", "BĐS đầu tư", "BĐSĐT"], 2, None, "high"),
    ("tong-quan-ve-bat-dong-san-dau-tu", "Tổng quan về bất động sản đầu tư", ["bất động sản chủ sở hữu sử dụng", "đánh giá bất động sản đầu tư"], 2, "2.1", "high"),
    ("ke-toan-mua-sam-xay-dung-bat-dong-san-dau-tu", "Kế toán mua sắm, xây dựng bất động sản đầu tư", ["nguyên giá bất động sản đầu tư", "mua sắm, xây dựng"], 2, "2.2", "high"),
    ("ke-toan-khau-hao-cho-thue-nhuong-ban-bat-dong-san-dau-tu", "Kế toán khấu hao, cho thuê, nhượng bán bất động sản đầu tư", ["khấu hao bất động sản đầu tư", "nhượng bán bất động sản đầu tư", "khấu hao BĐSĐT"], 2, "2.3", "high"),
    ("ke-toan-sua-chua-nang-cap-bat-dong-san-dau-tu", "Kế toán sửa chữa, nâng cấp bất động sản đầu tư", ["nâng cấp bất động sản đầu tư", "sửa chữa, nâng cấp"], 2, "2.4", "high"),
    ("ke-toan-chuyen-doi-muc-dich-su-dung", "Kế toán chuyển đổi mục đích sử dụng", ["chuyển đổi mục đích sử dụng", "hàng hóa bất động sản"], 2, "2.5", "high"),
    ("trinh-bay-thong-tin-bds-dau-tru-tren-bctc", "Trình bày thông tin BĐS đầu trư trên BCTC", ["trình bày thông tin liên quan đến bất động sản đầu tư"], 2, "2.6", "high"),
    # Chương 3: KẾ TOÁN ĐẦU TƯ TÀI CHÍNH
    ("ke-toan-dau-tu-tai-chinh", "KẾ TOÁN ĐẦU TƯ TÀI CHÍNH", ["các khoản đầu tư tài chính"], 3, None, "high"),
    ("tong-quan-ve-dau-tu-tai-chinh", "TỔNG QUAN VỀ ĐẦU TƯ TÀI CHÍNH", ["quyền biểu quyết", "ảnh hưởng đáng kể"], 3, "3.1", "high"),
    ("ke-toan-chung-khoan-kinh-doanh", "KẾ TOÁN CHỨNG KHOÁN KINH DOANH", ["chứng khoán kinh doanh"], 3, "3.2", "high"),
    ("ke-toan-dau-tu-nam-giu-den-ngay-dao-han", "KẾ TOÁN ĐẦU TƯ NẮM GIỮ ĐẾN NGÀY ĐÁO HẠN", ["nắm giữ đến ngày đáo hạn"], 3, "3.3", "high"),
    ("ke-toan-dau-tu-von-vao-cac-cong-ty", "KẾ TOÁN ĐẦU TƯ VỐN VÀO CÁC CÔNG TY", ["đầu tư vào công ty con", "đầu tư vào công ty liên doanh", "công ty liên kết"], 3, "3.4", "high"),
    ("ke-toan-du-phong-ton-that-dau-tu-tai-chinh", "Kế toán dự phòng tổn thất đầu tư tài chính", ["dự phòng tổn thất đầu tư", "kế toán dự phòng đầu tư tài chính", "dự phòng giảm giá chứng khoán kinh doanh"], 3, "3.5", "high"),
    ("trinh-bay-thong-tin-tren-tai-chinh", "TRÌNH BÀY THÔNG TIN TRÊN TÀI CHÍNH", ["thông tin về các khoản đầu tư tài chính"], 3, "3.6", "medium"),
    # Chương 4: KẾ TOÁN THUẾ TNDN
    ("so-lieu-ke-toan-va-so-lieu-tinh-thue-tndn", "SỐ LIỆU KẾ TOÁN VÀ SỐ LIỆU TÍNH THUẾ TNDN", ["lợi nhuận kế toán trước thuế", "thu nhập chịu thuế", "thu nhập tính thuế"], 4, "4.1", "high"),
    ("ke-toan-thue-tndn-hien-hanh", "KẾ TOÁN THUẾ TNDN HIỆN HÀNH", ["chi phí thuế TNDN hiện hành"], 4, "4.2", "high"),
    ("phan-biet-chenh-lech-giua-so-lieu-ke-toan-va-so-lieu-tinh-thue-tndn", "PHÂN BIỆT CHÊNH LỆCH GIỮA SỐ LIỆU KẾ TOÁN VÀ SỐ LIỆU TÍNH THUẾ TNDN", ["chênh lệch tạm thời", "chênh lệch vĩnh viễn", "cơ sở tính thuế"], 4, "4.3", "high"),
    ("ke-toan-tai-san-thue-tn-hoan-lai", "KẾ TOÁN TÀI SẢN THUẾ TN HOÃN LẠI", ["tài sản thuế thu nhập hoãn lại", "tài sản thuế TN hoãn lại", "chênh lệch tạm thời được khấu trừ"], 4, "4.4", "high"),
    ("ke-toan-thue-tn-hoan-lai-phai-tra", "KẾ TOÁN THUẾ TN HOÃN LẠI PHẢI TRẢ", ["thuế thu nhập hoãn lại phải trả", "thuế TN hoãn lại phải trả", "chênh lệch tạm thời phải chịu thuế"], 4, "4.5", "high"),
    ("trinh-bay-thong-tin-tren-bao-cao-tai-chinh", "TRÌNH BÀY THÔNG TIN TRÊN BÁO CÁO TÀI CHÍNH", ["trình bày thông tin tài sản thuế TN hoãn lại"], 4, "4.6", "medium"),
    ("chi-phi-thue-tndn-hoan-lai", "chi phí thuế TNDN hoãn lại", [], 4, None, "medium"),
]

ACCOUNTS = {  # count >= 2 in indexed text (work/<C>/concept_candidates.json)
    "4131": "chenh-lech-ty-gia-hoi-doai", "413": "chenh-lech-ty-gia-hoi-doai",
    "1122": "ke-toan-giao-dich-phat-sinh-bang-ngoai-te", "1112": "ke-toan-giao-dich-phat-sinh-bang-ngoai-te",
    "217": "ke-toan-bat-dong-san-dau-tu", "2147": "ke-toan-khau-hao-cho-thue-nhuong-ban-bat-dong-san-dau-tu",
    "5117": "ke-toan-khau-hao-cho-thue-nhuong-ban-bat-dong-san-dau-tu", "1567": "ke-toan-chuyen-doi-muc-dich-su-dung",
    "121": "ke-toan-chung-khoan-kinh-doanh", "1211": "ke-toan-chung-khoan-kinh-doanh",
    "128": "ke-toan-dau-tu-nam-giu-den-ngay-dao-han", "1281": "ke-toan-dau-tu-nam-giu-den-ngay-dao-han", "1282": "ke-toan-dau-tu-nam-giu-den-ngay-dao-han",
    "221": "ke-toan-dau-tu-von-vao-cac-cong-ty", "222": "ke-toan-dau-tu-von-vao-cac-cong-ty", "228": "ke-toan-dau-tu-von-vao-cac-cong-ty", "2281": "ke-toan-dau-tu-von-vao-cac-cong-ty",
    "229": "ke-toan-du-phong-ton-that-dau-tu-tai-chinh", "2291": "ke-toan-du-phong-ton-that-dau-tu-tai-chinh",
    "8211": "ke-toan-thue-tndn-hien-hanh", "3334": "ke-toan-thue-tndn-hien-hanh",
    "243": "ke-toan-tai-san-thue-tn-hoan-lai", "347": "ke-toan-thue-tn-hoan-lai-phai-tra",
    "8212": "chi-phi-thue-tndn-hoan-lai",
}

# explicit sequence edges: quote taken verbatim from page 1 of the later topic's script
EDGES = [
    ("tong-quan-ve-bat-dong-san-dau-tu", "ke-toan-mua-sam-xay-dung-bat-dong-san-dau-tu", "bài học trước chúng ta đã hoàn thành chủ đề 2.1", "src-0558", 1),
    ("ke-toan-mua-sam-xay-dung-bat-dong-san-dau-tu", "ke-toan-khau-hao-cho-thue-nhuong-ban-bat-dong-san-dau-tu", "Ở chủ đề trước chúng ta đã học xong chủ đề 2.2", "src-0560", 1),
    ("ke-toan-khau-hao-cho-thue-nhuong-ban-bat-dong-san-dau-tu", "ke-toan-sua-chua-nang-cap-bat-dong-san-dau-tu", "ở bài học trước chúng ta đã hoàn thành chủ đề 2.3", "src-0562", 1),
    ("ke-toan-sua-chua-nang-cap-bat-dong-san-dau-tu", "ke-toan-chuyen-doi-muc-dich-su-dung", "bài học trước chúng ta đã hoàn thành chủ đề 2.4", "src-0564", 1),
    ("so-lieu-ke-toan-va-so-lieu-tinh-thue-tndn", "ke-toan-thue-tndn-hien-hanh", "Các anh chị đã tìm hiểu chủ đề 1 của chương 4", "src-0582", 1),
    ("phan-biet-chenh-lech-giua-so-lieu-ke-toan-va-so-lieu-tinh-thue-tndn", "ke-toan-tai-san-thue-tn-hoan-lai", "Các anh chị đã phân biệt được các khoản chênh lệch phát sinh giữa số liệu kế toán và số liệu tính thuế TNDN theo hai hướng tiếp cận", "src-0586", 1),
]

CONFLICTS = [
    {"type": "COURSE_CODE", "values": ["ACCO3310", "ACCO1335", "ACCO3301"],
     "refs": [{"source_id": "src-0592", "page": 1, "code": "ACCO3310"}, {"source_id": "src-0544", "page": 1, "code": "ACCO1335"},
              {"source_id": "src-0595", "page": 1, "code": "ACCO3301"}],
     "resolution": "not resolved; registry decision (official: UNKNOWN)"},
    {"type": "TITLE_VARIANT", "scope": "chapter 1 topic list",
     "values": ["scripts: 1.4 nhập khẩu trực tiếp, 1.5 xuất khẩu trực tiếp (5 chủ đề)",
                "hướng dẫn ôn tập: 1.4 'Kế toán xử lý chênh lệch tỷ giá giai đoạn trước hoạt động', 1.5 nhập khẩu, 1.6 xuất khẩu (6 chủ đề)"],
     "refs": [{"source_id": "src-0550", "page": 1}, {"source_id": "src-0595", "page": 2}],
     "resolution": "chapter/topic numbers follow the script filenames; no script exists for the ôn tập 1.4 topic"},
    {"type": "TITLE_VARIANT", "scope": "topic 4.2",
     "values": ["KẾ TOÁN THUẾ TNDN HIỆN HÀNH (script)", "Kế toán chi phí thuế thu nhập doanh nghiệp hiện hành (ôn tập)"],
     "refs": [{"source_id": "src-0582", "page": 1}, {"source_id": "src-0595", "page": 6}], "resolution": "script title used as canonical"},
    {"type": "TITLE_VARIANT", "scope": "topic 4.3",
     "values": ["PHÂN BIỆT CHÊNH LỆCH ... (script)", "Phân loại chênh lệch ... (ôn tập)"],
     "refs": [{"source_id": "src-0584", "page": 1}, {"source_id": "src-0595", "page": 6}], "resolution": "script title used as canonical"},
    {"type": "TITLE_VARIANT", "scope": "topic 3.5",
     "values": ["KẾ TOÁN DỰ PHÒNG ĐẦU TƯ TÀI CHÍNH (script 3.5)", "Kế toán dự phòng tổn thất đầu tư tài chính (script 3.1 + ôn tập)"],
     "refs": [{"source_id": "src-0576", "page": 1}, {"source_id": "src-0568", "page": 1}], "resolution": "both kept (canonical + alias)"},
]


def refs_for(names, chapter, topic):
    fn = [T(n) for n in names]
    hits = [(p["source_id"], p["page"]) for p in pages if any(f in T(p["text"]) for f in fn)]
    own = [h for h in hits if docs[h[0]].get("topic") == topic and docs[h[0]].get("chapter") == chapter] if topic else \
          [h for h in hits if docs[h[0]].get("chapter") == chapter]
    pick = (own + [h for h in hits if h not in own])[:2]
    return [{"source_id": s, "page": p} for s, p in pick]


def main():
    concepts = []
    for slug, name, aliases, ch, topic, conf in SPEC:
        refs = refs_for([name] + aliases, ch, topic)
        assert refs, slug
        concepts.append({"concept_id": f"kttc3-{slug}", "canonical_name": name, "aliases": aliases, "same_as": None,
                         "chapter": ch, "topic": topic, "source_refs": refs, "evidence_status": "OBSERVED", "confidence": conf})
    doc = {"course_id": CID, "version": "0.1.0", "id_prefix": "kttc3",
           "notes": ["W6b 2026-11-21. canonical_name = heading text (script page 1 'Chủ đề x.y: ...' or chapter heading); "
                     "two cross-topic terms (chenh-lech-ty-gia-hoi-doai, chi-phi-thue-tndn-hoan-lai) use a term that occurs >=3 times.",
                     "same_as: none. No core concept has an identical meaning (core khau-hao = TSCĐ depreciation; ktnh-* are bank-specific).",
                     "Chapter 4 aliases avoid the bare words 'thuế' / 'thuế TNDN' (shared with Kế toán thuế 1)."],
           "concepts": concepts,
           "account_map": {a: f"kttc3-{s}" for a, s in ACCOUNTS.items()},
           "edges": [{"from": f"kttc3-{a}", "to": f"kttc3-{b}", "type": "explicit_sequence", "quote": q, "source_id": s, "page": p}
                     for a, b, q, s, p in EDGES],
           "conflicts": CONFLICTS}
    out = SYS / "curriculum" / "concepts" / f"{CID}.yaml"
    out.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    print("wrote", out, len(concepts), "concepts", len(doc["account_map"]), "accounts", len(doc["edges"]), "edges")


if __name__ == "__main__":
    main()
