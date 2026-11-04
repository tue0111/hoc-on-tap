"""Build the audited concept table for kinh-doanh-va-nghiep-vu.

Names and source references come from the extracted course headings.  Aliases are
kept only when they occur in the indexed course text, matching the Wave 3
contract and validator behavior.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retrieval.textutil import fold


COURSE = "kinh-doanh-va-nghiep-vu"
PREFIX = "kdnv"


def slug(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalized(value: str) -> str:
    return fold(re.sub(r"\s+", " ", value))


# canonical name, aliases, chapter, topic, same_as, extra chapters
S = [
    ("Tổ chức kinh doanh và các bên liên quan", ["các bên liên quan"], 1, "1.1", None, None),
    ("Môi trường kinh doanh", ["phân tích môi trường kinh doanh"], 1, "1.2", None, None),
    ("Môi trường kinh doanh- Các yếu tố chính trị, pháp lý và xã hội", ["các yếu tố chính trị, pháp lý và xã hội"], 1, "1.3", None, None),
    ("Môi trường kinh doanh – Các yếu tố công nghệ và môi trường", ["các yếu tố công nghệ và môi trường"], 1, "1.4", None, None),
    ("Môi trường kinh doanh – Các mô hình phân tích cạnh tranh", ["các mô hình phân tích cạnh tranh"], 1, "1.5", None, None),
    ("Môi trường kinh tế vĩ mô – Các vấn đề cơ bản", [], 1, "1.6", None, None),
    ("Môi trường kinh tế vĩ mô – Các chính sách vĩ mô", ["các chính sách vĩ mô"], 1, "1.7", None, None),
    ("Môi trường kinh tế vi mô – Các vấn đề cơ bản", ["kinh tế vi mô"], 1, "1.8", None, None),
    ("Môi trường kinh tế vi mô – Phân tích cung cầu", ["phân tích cung cầu"], 1, "1.9", None, None),
    ("Cấu trúc doanh nghiệp và chiến lược kinh doanh", ["chiến lược kinh doanh"], 2, "2.1", None, None),
    ("Văn hóa tổ chức", [], 2, "2.2", None, None),
    ("Quản trị doanh nghiệp", [], 2, "2.3", None, None),
    ("Trách nhiệm xã hội của doanh nghiệp", ["trách nhiệm xã hội doanh nghiệp"], 2, "2.4", None, None),
    ("Những vấn đề chung về kế toán", [], 3, "3.1", None, None),
    ("Kiểm soát nội bộ và kiểm toán", ["dịch vụ bảo đảm"], 3, "3.2", None, None),
    ("Phát hiện và ngăn chặn gian lận", ["gian lận"], 3, "3.3", None, None),
    ("Kiểm soát hệ thống thông tin và ảnh hưởng của công nghệ tài chính (Fintech)", ["công nghệ tài chính", "Fintech"], 3, "3.4", None, None),
    ("Lãnh đạo và quản lý", ["phong cách lãnh đạo"], 4, "4.1", None, None),
    ("Tuyển dụng nhân sự", ["tuyển chọn nhân sự"], 4, "4.2", None, None),
    ("Cá nhân, nhóm và đội và việc tạo động lực làm việc", ["động lực làm việc"], 4, "4.3", None, None),
    ("Đào tạo, Phát triển và Đánh giá Thành quả", ["đánh giá thành quả"], 4, "4.4", None, None),
    ("Quản Lý Thời Gian Và Tính Hiệu Quả Trong Công Việc", ["quản lý thời gian"], 5, "5.1", None, None),
    ("Truyền Thông Trong Doanh Nghiệp", ["truyền thông"], 5, "5.2", None, None),
    ("Hành vi đạo đức và đạo đức trong kinh doanh", ["đạo đức kinh doanh"], 6, "6.1", None, None),
    ("Đạo đức nghề nghiệp kế toán", ["đạo đức nghề nghiệp"], 6, "6.2", "dao-duc-nghe-nghiep-ke-toan", None),
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

    refs = []
    preferred = sorted(
        page_text,
        key=lambda item: (
            item[0].get("topic") != topic,
            item[0].get("chapter") != chapter,
            item[0]["page"],
            item[0]["source_id"],
        ),
    )
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
    "conflicts": [],
}

output_path = ROOT / "curriculum" / "concepts" / f"{COURSE}.yaml"
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8", newline="\n") as handle:
    yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=False, width=120)

print(len(concepts), "concepts; dropped:", dropped)
