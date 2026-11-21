"""Build the audited concept table for ke-toan-hanh-chinh-su-nghiep (playbook 6.5).

Canonical names are copied verbatim from headings ("Chương n:" / "Chủ đề n.m:" lines of the
lecture scripts, src-0407..src-0485; chapter 0 from the docx script src-0487). Aliases are only
strings present in this course's extracted text. source_refs are computed: first pages that
contain the canonical name or an alias, preferring the topic's own script.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from retrieval.textutil import fold  # noqa: E402

COURSE = "ke-toan-hanh-chinh-su-nghiep"
PREFIX = "kthcsn"


def slug(v: str) -> str:
    v = v.replace("đ", "d").replace("Đ", "D")
    v = unicodedata.normalize("NFD", v)
    v = "".join(c for c in v if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", v.lower()).strip("-")


T = lambda s: fold(re.sub(r"\s+", " ", s or ""))

# (canonical, aliases, chapter, topic, preferred source ids, explicit id slug or None)
S = [
    ("Giới thiệu môn học", ["Chuẩn đầu ra của môn học"], 0, "0", ["src-0487"], None),
    ("Tổng quan về kế toán hành chính sự nghiệp", [], 1, "1", ["src-0407", "src-0489"], None),
    ("Tổ chức công tác kế toán", ["mô hình tổ chức công tác kế toán"], 1, "1.1", ["src-0407", "src-0409"], None),
    ("Tổ chức bộ máy kế toán", ["Kế toán trưởng"], 1, "1.2", ["src-0411"], None),
    ("Tổ chức hệ thống tài khoản kế toán", [], 1, "1.3", ["src-0413", "src-0415", "src-0417"], None),
    ("Tài khoản ngoài bảng", [], 1, "1.3", ["src-0413", "src-0417"], None),
    ("Chế độ kế toán hành chính sự nghiệp", [], 1, None, ["src-0434", "src-0459"], None),
    ("Kế toán vốn bằng tiền và các khoản thanh toán", [], 2, "2", ["src-0419", "src-0421"], None),
    ("Kế toán vốn bằng tiền", ["quỹ tiền mặt"], 2, "2.1", ["src-0419", "src-0421"], "ke-toan-von-bang-tien-chu-de"),
    ("Kế toán các khoản phải thu", ["Phải thu khách hàng"], 2, "2.2", ["src-0423", "src-0425"], None),
    ("Kế toán các khoản phải trả cho người lao động", ["Phải trả người lao động", "các khoản phải nộp theo lương"], 2, "2.3", ["src-0427", "src-0429"], None),
    ("Kế toán các khoản nộp nhà nước", ["Các khoản phải nộp nhà nước"], 2, "2.4", ["src-0431"], None),
    ("Kế toán Hàng tồn kho", [], 3, "3", ["src-0433", "src-0434", "src-0436"], None),
    ("Kế toán nguyên vật liệu, công cụ dụng cụ", ["Kế toán nguyên liệu, vật liệu"], 3, "3.1", ["src-0433", "src-0434"], None),
    ("Kế toán chi phí sản xuất kinh doanh, dịch vụ dở dang", [], 3, "3.2", ["src-0436"], None),
    ("Kế toán tài sản cố định và đầu tư xây dựng cơ bản", [], 4, "4", ["src-0439", "src-0441"], None),
    ("Những vấn đề chung về tài sản cố định", ["Tài sản cố định hữu hình", "Tài sản cố định vô hình"], 4, "4.1", ["src-0439"], None),
    ("Kế toán tài sản cố định của đơn vị", [], 4, "4.2", ["src-0441"], None),
    ("Kế toán khấu hao, hao mòn TSCĐ", ["hao mòn TSCĐ"], 4, "4.3", ["src-0443"], None),
    ("Kế toán đầu tư xây dựng cơ bản", [], 4, "4.4", ["src-0445", "src-0447"], "ke-toan-dau-tu-xay-dung-co-ban-chu-de"),
    ("Kế toán hoạt động hành chính sự nghiệp", ["Kế toán doanh thu, chi phí hoạt động hành chính sự nghiệp"], 5, "5", ["src-0449", "src-0489"], None),
    ("Kế toán doanh thu hành chính sự nghiệp", ["Doanh thu từ kinh phí NSNN cấp", "Doanh thu từ nhà tài trợ nước ngoài"], 5, "5.1", ["src-0449", "src-0451"], None),
    ("Kế toán chi phí hành chính sự nghiệp", ["Chi phí hoạt động không giao tự chủ", "Chi phí hoạt động giao tự chủ"], 5, "5.2", ["src-0453"], None),
    ("Kế toán hoạt động hành chính sự nghiệp khác", ["Thu nhập khác"], 5, "5.3", ["src-0455"], None),
    ("Kế toán hoạt động sản xuất kinh doanh, dịch vụ và hoạt động đầu tư tài chính", ["Kế toán doanh thu, chi phí hoạt động sản xuất kinh doanh, hoạt động đầu tư tài chính và hoạt động khác"], 6, "6", ["src-0457", "src-0459", "src-0489"], None),
    ("Những vấn đề chung về doanh thu chi phí hoạt động sản xuất kinh doanh", [], 6, "6.1", ["src-0457", "src-0459"], None),
    ("Kế toán doanh thu hoạt động sản xuất kinh doanh, dịch vụ", [], 6, "6.2", ["src-0461"], None),
    ("Kế toán chi phí hoạt động sản xuất kinh doanh, dịch vụ", ["Giá vốn hàng bán"], 6, "6.3", ["src-0463", "src-0465", "src-0467"], None),
    ("Kế toán doanh thu chi phí hoạt động đầu tư tài chính", ["Doanh thu tài chính", "Chi phí tài chính"], 6, "6.4", ["src-0469", "src-0471"], None),
    ("Kế toán xác định kết quả và phân phối kết quả hoạt động", [], 7, "7", ["src-0473", "src-0475"], None),
    ("Kế toán xác định kết quả hoạt động", [], 7, "7.1", ["src-0473"], None),
    ("Kế toán phân phối kết quả các hoạt động", ["Thặng dư (thâm hụt) lũy kế", "Các quỹ thuộc đơn vị", "Nguồn kinh phí mang sang năm sau"], 7, "7.2", ["src-0475", "src-0478"], None),
    ("Báo cáo kế toán", [], 8, "8", ["src-0479", "src-0483"], None),
    ("Báo cáo quyết toán", [], 8, "8.1", ["src-0479", "src-0481"], None),
    ("Báo cáo tài chính", ["Báo cáo tình hình tài chính", "Thuyết minh báo cáo tài chính"], 8, "8.2", ["src-0483", "src-0485"], None),
    ("Chuẩn mực kế toán công", [], None, None, ["src-0433", "src-0449", "src-0457"], None),
    ("rút dự toán", [], None, None, ["src-0419", "src-0449"], None),
]

ACCOUNTS = {
    "111": "ke-toan-von-bang-tien-chu-de", "112": "ke-toan-von-bang-tien-chu-de",
    "131": "ke-toan-cac-khoan-phai-thu", "137": "ke-toan-cac-khoan-phai-thu", "141": "ke-toan-cac-khoan-phai-thu",
    "334": "ke-toan-cac-khoan-phai-tra-cho-nguoi-lao-dong", "332": "ke-toan-cac-khoan-phai-tra-cho-nguoi-lao-dong",
    "353": "ke-toan-cac-khoan-phai-tra-cho-nguoi-lao-dong",
    "333": "ke-toan-cac-khoan-nop-nha-nuoc",
    "152": "ke-toan-nguyen-vat-lieu-cong-cu-dung-cu", "153": "ke-toan-nguyen-vat-lieu-cong-cu-dung-cu",
    "154": "ke-toan-chi-phi-san-xuat-kinh-doanh-dich-vu-do-dang",
    "211": "ke-toan-tai-san-co-dinh-cua-don-vi",
    "214": "ke-toan-khau-hao-hao-mon-tscd",
    "241": "ke-toan-dau-tu-xay-dung-co-ban-chu-de",
    "511": "ke-toan-doanh-thu-hanh-chinh-su-nghiep", "512": "ke-toan-doanh-thu-hanh-chinh-su-nghiep",
    "514": "ke-toan-doanh-thu-hanh-chinh-su-nghiep",
    "611": "ke-toan-chi-phi-hanh-chinh-su-nghiep", "612": "ke-toan-chi-phi-hanh-chinh-su-nghiep",
    "711": "ke-toan-hoat-dong-hanh-chinh-su-nghiep-khac", "811": "ke-toan-hoat-dong-hanh-chinh-su-nghiep-khac",
    "531": "ke-toan-doanh-thu-hoat-dong-san-xuat-kinh-doanh-dich-vu",
    "632": "ke-toan-chi-phi-hoat-dong-san-xuat-kinh-doanh-dich-vu", "642": "ke-toan-chi-phi-hoat-dong-san-xuat-kinh-doanh-dich-vu",
    "229": "ke-toan-chi-phi-hoat-dong-san-xuat-kinh-doanh-dich-vu",
    "515": "ke-toan-doanh-thu-chi-phi-hoat-dong-dau-tu-tai-chinh", "615": "ke-toan-doanh-thu-chi-phi-hoat-dong-dau-tu-tai-chinh",
    "121": "ke-toan-doanh-thu-chi-phi-hoat-dong-dau-tu-tai-chinh",
    "911": "ke-toan-xac-dinh-ket-qua-hoat-dong",
    "421": "ke-toan-phan-phoi-ket-qua-cac-hoat-dong", "431": "ke-toan-phan-phoi-ket-qua-cac-hoat-dong",
    "468": "ke-toan-phan-phoi-ket-qua-cac-hoat-dong",
    "008": "tai-khoan-ngoai-bang", "009": "tai-khoan-ngoai-bang", "012": "tai-khoan-ngoai-bang", "013": "tai-khoan-ngoai-bang",
}


def main():
    pages = [json.loads(l) for l in (ROOT / "data" / "normalized" / f"{COURSE}.pages.jsonl").open(encoding="utf-8")]
    ptxt = [(p["source_id"], p["page"], T(p["text"])) for p in pages]
    concepts = []
    for canon, aliases, ch, topic, pref, sl in S:
        names = [T(canon)] + [T(a) for a in aliases]
        refs = []
        for sid in pref:
            hit = [pg for s, pg, t in ptxt if s == sid and any(n in t for n in names)]
            if hit:
                refs.append({"source_id": sid, "page": hit[0]})
        if not refs:
            hit = [(s, pg) for s, pg, t in ptxt if any(n in t for n in names)]
            refs = [{"source_id": s, "page": pg} for s, pg in hit[:2]]
        concepts.append({
            "concept_id": f"{PREFIX}-{sl or slug(canon)}", "canonical_name": canon, "aliases": aliases,
            "same_as": None, "chapter": ch, "topic": topic, "source_refs": refs,
            "evidence_status": "OBSERVED", "confidence": "high" if topic else "medium",
        })
    ids = {c["concept_id"] for c in concepts}
    amap = {}
    for a, t in ACCOUNTS.items():
        cid = f"{PREFIX}-{t}"
        assert cid in ids, cid
        amap[a] = cid
    doc = {
        "course_id": COURSE, "version": "0.1.0", "id_prefix": PREFIX,
        "regulation_basis": {
            "note": "Giáo trình ghi theo Thông tư 24/2024/TT-BTC (chế độ kế toán HCSN). Thông tư 107/2017/TT-BTC chỉ được nhắc một lần như văn bản có hiệu lực đến hết năm 2024. Ghi nguyên văn, không hợp nhất.",
            "observations": [
                {"ref": "Thông tư 24/2024/TT-BTC", "source_id": "src-0489", "page": 11},
                {"ref": "Thông tư 24/2024/TT-BTC", "source_id": "src-0457", "page": 2},
                {"ref": "Thông tư 107/2017/TT-BTC", "source_id": "src-0409", "page": 2},
            ],
            "evidence_status": "OBSERVED",
        },
        "concepts": concepts, "account_map": amap, "edges": [],
        "conflicts": [
            {"type": "REGULATION_VINTAGE",
             "note": "Script ghi hai văn bản cho cùng nội dung chữa sổ kế toán: TT 107/2017 hiệu lực đến hết năm 2024, TT 24/2024 từ năm 2025. Giữ nguyên cả hai, không tự hợp nhất.",
             "quote": "thông tư 107/2017/TT-BTC chế độ kế toán HCSN có hiệu lực đến hết năm 2024. Đến năm 2025 thì thông tư 24/2024/TT-BTC có hiệu lực",
             "source_id": "src-0409", "page": 2, "evidence_status": "OBSERVED", "resolution": "UNKNOWN"},
            {"type": "TITLE_VARIANT", "chapter": 5,
             "note": "Tên chương 5 khác nhau giữa script và tài liệu ôn tập; cả hai giữ làm tên/alias của cùng concept chương.",
             "observations": [
                 {"title": "Chương 5: Kế toán hoạt động hành chính sự nghiệp", "source_id": "src-0449", "page": 1},
                 {"title": "CHƯƠNG 5: KẾ TOÁN DOANH THU, CHI PHÍ HOẠT ĐỘNG HÀNH CHÍNH SỰ NGHIỆP", "source_id": "src-0489", "page": 6}],
             "evidence_status": "OBSERVED", "resolution": "UNKNOWN"},
            {"type": "TITLE_VARIANT", "chapter": 6,
             "note": "Tài liệu ôn tập thêm 'hoạt động khác' vào tên chương 6 và chủ đề 6.1/6.4; script đặt hoạt động khác ở chủ đề 5.3. Không tự đồng nhất phạm vi chủ đề.",
             "observations": [
                 {"title": "Chương 6: Kế toán hoạt động sản xuất kinh doanh, dịch vụ và hoạt động đầu tư tài chính", "source_id": "src-0457", "page": 1},
                 {"title": "CHƯƠNG 6: KẾ TOÁN DOANH THU, CHI PHÍ HOẠT ĐỘNG SẢN XUẤT KINH DOANH, HOẠT ĐỘNG ĐẦU TƯ TÀI CHÍNH VÀ HOẠT ĐỘNG KHÁC", "source_id": "src-0489", "page": 7},
                 {"title": "Chủ đề 6.4 Kế toán doanh thu, chi phí hoạt động đầu tư tài chính và hoạt động khác", "source_id": "src-0489", "page": 8}],
             "evidence_status": "OBSERVED", "resolution": "UNKNOWN"},
            {"type": "ASSESSMENT_WEIGHT_CONFLICT",
             "note": "Script chương mở đầu ghi A1 và A2 mỗi phần 50%, nhưng cùng tài liệu ghi A2 là 60% tổng điểm. Không tự sửa.",
             "observations": [
                 {"quote": "mỗi phần chiếm 50% tổng điểm", "source_id": "src-0487", "page": 2},
                 {"quote": "A2. Đánh giá cuối kỳ (60% tổng điểm)", "source_id": "src-0487", "page": 3}],
             "evidence_status": "OBSERVED", "resolution": "UNKNOWN"},
        ],
    }
    out = ROOT / "curriculum" / "concepts" / f"{COURSE}.yaml"
    out.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print("wrote", out, len(concepts), "concepts", len(amap), "accounts")


if __name__ == "__main__":
    main()
