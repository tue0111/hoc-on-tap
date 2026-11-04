"""Build the audited concept table for tai-chinh-doanh-nghiep-1."""

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retrieval.textutil import fold


COURSE = "tai-chinh-doanh-nghiep-1"
PREFIX = "tcdn1"


def slug(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalized(value: str) -> str:
    return fold(re.sub(r"\s+", " ", value))


# canonical name, aliases, chapter, topic, same_as, extra chapters
S = [
    ("Tổng quan về tài chính doanh nghiệp", [], 1, "1", None, None),
    ("Các loại hình doanh nghiệp", [], 1, "1.1", None, None),
    ("Môi trường kinh doanh của doanh nghiệp", ["môi trường thuế"], 1, "1.5", None, None),
    ("Phân tích báo cáo tài chính", [], 2, "2", None, None),
    ("Những vấn đề chung liên quan đến phân tích báo cáo tài chính", ["phương pháp phân tích báo cáo tài chính"], 2, "2.1", None, None),
    ("Nội dung phân tích báo cáo tài chính", ["phân tích tài chính Dupont"], 2, "2.2", None, None),
    ("Thời giá của tiền tệ và mô hình chiết khấu dòng tiền", [], 3, "3", None, None),
    ("Vấn đề lãi và lãi suất", ["lãi đơn và lãi kép"], 3, "3.1", None, None),
    ("Thời giá tiền tệ của một số tiền", ["giá trị hiện tại của một số tiền"], 3, "3.2", None, None),
    ("Thời giá tiền tệ của một dòng tiền", ["giá trị hiện tại của một dòng tiền"], 3, "3.3", None, None),
    ("Lợi nhuận và rủi ro, mô hình định giá tài sản vốn", [], 4, "4", None, None),
    ("Khái niệm lợi nhuận và rủi ro trong tài chính", ["rủi ro hệ thống", "rủi ro phi hệ thống"], 4, "4.1", None, None),
    ("Mô hình định giá tài sản vốn (CAPM)", ["CAPM", "đường thị trường chứng khoán"], 4, "4.5", None, None),
    ("Định giá và quyết định đầu tư chứng khoán", [], 5, "5", None, None),
    ("Định giá và quyết định đầu tư trái phiếu", ["định giá trái phiếu thông thường", "YTM"], 5, "5.1", None, None),
    ("Định giá và quyết định đầu tư cổ phiếu", ["định giá cổ phiếu ưu đãi"], 5, "5.2", None, None),
    ("Phân tích quyết định đầu tư tài sản dài hạn và chi phí sử dụng vốn", [], 6, "6", None, None),
    ("Những vấn đề căn bản và tiêu chuẩn đánh giá dự án đầu tư", ["NPV", "IRR", "MIRR"], 6, "6.1", None, None),
    ("Chi phí sử dụng vốn dự án đầu tư", ["chi phí sử dụng vốn bình quân gia quyền", "WACC"], 6, "6.3", None, None),
    ("Quản trị tài sản ngắn hạn", [], 7, "7", None, None),
    ("Quản trị hàng tồn kho", ["EOQ", "JIT", "MRP"], 7, "7.1", None, None),
    ("Quản trị tiền tồn quỹ", ["mô hình Baumol", "mô hình Miller-orr"], 7, "7.2", None, None),
    ("Quản trị khoản phải thu", ["tiêu chuẩn bán chịu"], 7, "7.3", None, None),
    ("Đòn bẩy kinh doanh và đòn bẩy tài chính", [], 8, "8", None, None),
    ("Đòn bẩy kinh doanh (DOL)", ["điểm hòa vốn tiêu thụ"], 8, "8.1", None, None),
    ("Đòn bẩy tài chính (DFL)", ["điểm bàng quan EBIT & EPS"], 8, "8.2", None, None),
    ("Cổ tức và chính sách cổ tức", [], 9, "9", None, None),
    ("Các hình thức chi trả cổ tức", ["cổ tức bằng tiền", "cổ tức bằng cổ phiếu"], 9, "9.1", None, None),
    ("Thiết lập chính sách cổ tức", ["chính sách cổ tức ổn định"], 9, "9.5", None, None),
]


pages_path = ROOT / "data" / "normalized" / f"{COURSE}.pages.jsonl"
pages = [json.loads(line) for line in pages_path.open(encoding="utf-8")]
indexed_pages = [page for page in pages if page["index_include"]]
page_text = [(page, normalized(page["text"])) for page in indexed_pages]

concepts = []
dropped = []
used_ids = set()
for name, aliases, chapter, topic, same_as, extra_chapters in S:
    concept_id = f"{PREFIX}-{slug(name)}"
    if concept_id in used_ids:
        concept_id = f"{concept_id}-{topic.replace('.', '-')}"
    used_ids.add(concept_id)

    kept_aliases = []
    for alias in aliases:
        folded_alias = normalized(alias)
        present = any(folded_alias in text for _, text in page_text)
        valid_length = len(folded_alias) >= 6 or (alias.isupper() and present)
        if present and valid_length:
            kept_aliases.append(alias)
        else:
            dropped.append((concept_id, alias))

    candidates = [normalized(name), *(normalized(alias) for alias in kept_aliases)]
    if not any(candidates[0] in text for _, text in page_text) and not kept_aliases:
        dropped.append((concept_id, f"CANONICAL ABSENT:{name}"))
        continue

    preferred = sorted(
        page_text,
        key=lambda item: (
            item[0].get("chapter") != chapter,
            item[0]["page"],
            item[0]["source_id"],
        ),
    )
    refs = []
    for page, text in preferred:
        if any(candidate in text for candidate in candidates):
            refs.append({"source_id": page["source_id"], "page": page["page"]})
            if len(refs) == 2:
                break

    concept = {
        "concept_id": concept_id,
        "canonical_name": name,
        "aliases": kept_aliases,
        "same_as": same_as,
        "chapter": chapter,
        "topic": topic,
        "source_refs": refs,
        "evidence_status": "OBSERVED",
        "confidence": "high" if refs else "low",
    }
    if extra_chapters:
        concept["chapters"] = extra_chapters
    concepts.append(concept)

document = {
    "course_id": COURSE,
    "version": "0.1.0",
    "id_prefix": PREFIX,
    "concepts": concepts,
    "account_map": {},
    "edges": [],
    "conflicts": [
        {
            "type": "ASSESSMENT_DURATION_CONFLICT",
            "note": "Giới thiệu môn học ghi 75 phút; đề thi mẫu và đáp án ghi 90 phút. Giữ cả hai quan sát, không tự giải quyết.",
            "observations": [
                {"value": "75 phút", "source_id": "src-0155", "page": 2},
                {"value": "90 phút", "source_id": "src-0176", "page": 1},
            ],
            "evidence_status": "OBSERVED",
            "resolution": "UNKNOWN",
        }
    ],
}

output_path = ROOT / "curriculum" / "concepts" / f"{COURSE}.yaml"
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8", newline="\n") as handle:
    yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=False, width=120)

print(len(concepts), "concepts; dropped:", dropped)
