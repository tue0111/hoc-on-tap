"""Build the audited concept table for tai-chinh-hanh-chinh-su-nghiep."""

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retrieval.textutil import fold


COURSE = "tai-chinh-hanh-chinh-su-nghiep"
PREFIX = "hcsn"


def slug(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalized(value: str) -> str:
    return fold(re.sub(r"\s+", " ", value))


# canonical name, aliases, chapter, topic
S = [
    ("Tổng quan về tài chính hành chính sự nghiệp", ["ĐVHCSN"], 1, "1"),
    ("ngân sách nhà nước", ["NSNN"], 1, "1.1.1"),
    ("Phương pháp quản lý tài chính", [], 1, "1.1"),
    ("Quy trình quản lý tài chính đơn vị Hành chính sự nghiệp công lập", [], 1, "1.2"),
    ("Nhiệm vụ quyền hạn của các đơn vị hành chính sự nghiệp", [], 1, "1.3"),
    ("Quản lý tài chính theo cơ chế tự chủ, tự chịu trách nhiệm", ["cơ chế tự chủ tài chính"], 2, "2"),
    ("Một số vấn đề cơ bản về cơ chế tự chủ tài chính", [], 2, "2.1"),
    ("Quản lý tài chính theo cơ chế tự chủ cơ quan Hành chính nhà nước", [], 2, "2.2"),
    ("Quản lý tài chính theo cơ chế tự chủ đơn vị sự nghiệp công lập", [], 2, "2.3"),
    ("Quản lý quỹ tiền lương", [], 3, "3"),
    ("Một số vấn đề chung về quỹ tiền lương và các khoản nộp theo lương", [], 3, "3.1"),
    ("Quy trình quản lý quỹ tiền lương và các khoản nộp theo lương", [], 3, "3.2"),
    ("Quản lý tài chính dự án đầu tư công", [], 4, "4"),
    ("Phân loại dự án đầu tư công", [], 4, "4.1"),
    ("Quy trình quản lý tài chính dự án đầu tư công", [], 4, "4.2"),
    ("Quản lý chi phí quản lý dự án đầu tư xây dựng", [], 4, "4.3"),
    ("QUẢN LÝ SỬ DỤNG TÀI SẢN CÔNG", ["tài sản công"], 5, "5"),
    ("Một số vấn đề cơ bản trong quản lý, sử dụng tài sản công", [], 5, "5.1"),
    ("Quản lý, sử dụng tài sản tại cơ quan Hành chính nhà nước", [], 5, "5.2"),
    ("Quản lý, sử dụng tài sản tại Đơn vị sự nghiệp công lập", [], 5, "5.3"),
    ("Phương thức mua sắm tài sản công", ["lựa chọn nhà thầu"], 5, "5.4"),
    ("KẾ HOẠCH TÀI CHÍNH VÀ KẾ HOẠCH TÀI CHÍNH NGÂN SÁCH NHÀ NƯỚC", [], 6, "6"),
    ("Kế hoạch tài chính 5 năm", [], 6, "6.1"),
    ("Kế hoạch tài chính ngân sách nhà nước 3 năm", [], 6, "6.2"),
    ("Xác định các chỉ tiêu cơ sở", [], 6, "6.2.1"),
    ("Nhu cầu chi tiêu mới", [], 6, "6.2.2"),
]


pages_path = ROOT / "data" / "normalized" / f"{COURSE}.pages.jsonl"
pages = [json.loads(line) for line in pages_path.open(encoding="utf-8")]
indexed_pages = [page for page in pages if page["index_include"]]
page_text = [(page, normalized(page["text"])) for page in indexed_pages]

concepts = []
dropped = []
used_ids = set()
for name, aliases, chapter, topic in S:
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

    canonical = normalized(name)
    if not any(canonical in text for _, text in page_text):
        dropped.append((concept_id, f"CANONICAL ABSENT:{name}"))
        continue

    candidates = [canonical, *(normalized(alias) for alias in kept_aliases)]
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

    concepts.append(
        {
            "concept_id": concept_id,
            "canonical_name": name,
            "aliases": kept_aliases,
            "same_as": None,
            "chapter": chapter,
            "topic": topic,
            "source_refs": refs,
            "evidence_status": "OBSERVED",
            "confidence": "high" if refs else "low",
        }
    )

document = {
    "course_id": COURSE,
    "version": "0.1.0",
    "id_prefix": PREFIX,
    "concepts": concepts,
    "account_map": {},
    "edges": [],
    "conflicts": [
        {
            "type": "EXAM_FORMAT_CONFLICT",
            "note": "Slide giới thiệu và đề mẫu 2022 ghi trắc nghiệm 75 phút; tài liệu ôn tập 2022 ghi tự luận 1-2 câu, 75 phút. Không hợp nhất thành một hình thức thi.",
            "observations": [
                {"format": "trắc nghiệm", "source_id": "src-0187"},
                {"format": "40 câu trắc nghiệm", "source_id": "src-0185"},
                {"format": "tự luận 1-2 câu", "source_id": "src-0192"},
            ],
            "evidence_status": "OBSERVED",
            "resolution": "UNKNOWN",
        },
        {
            "type": "TOPIC_NUMBERING_CONFLICT",
            "note": "Lecture scripts và tài liệu ôn tập dùng số chủ đề không đồng nhất ở Chương 2 và Chương 4; giữ chapter làm ranh giới, không tự đồng nhất số chủ đề.",
            "evidence_status": "OBSERVED",
            "resolution": "UNKNOWN",
        },
    ],
}

output_path = ROOT / "curriculum" / "concepts" / f"{COURSE}.yaml"
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8", newline="\n") as handle:
    yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=False, width=120)

print(len(concepts), "concepts; dropped:", dropped)
