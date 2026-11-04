"""Build the audited concept table for thi-truong-tai-chinh."""

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retrieval.textutil import fold


COURSE = "thi-truong-tai-chinh"
PREFIX = "tttc"


def slug(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalized(value: str) -> str:
    return fold(re.sub(r"\s+", " ", value))


# canonical name, aliases, chapter, topic
S = [
    ("Tổng quan về Thị trường tài chính", [], 1, "1"),
    ("Tổng quan về Thị trường tài chính", [], 1, "1.1"),
    ("Tổ chức tài chính", [], 1, "1.2"),
    ("Vai trò và nguyên tắc hoạt động của các loại hình tổ chức tài chính", [], 1, "1.3"),
    ("Thị trường tiền tệ (TTTT)", ["thị trường tiền tệ", "TTTT"], 2, "2"),
    ("Tổng quan về TTTT", [], 2, "2.1"),
    ("Công dụng các sản phẩm trên TTTT", [], 2, "2.2"),
    ("Các loại lãi suất trên TTTT", ["phương trình Fisher"], 2, "2.3"),
    ("Thị trường trái phiếu", ["TTTP"], 3, "3"),
    ("Tổng quan về thị trường trái phiếu", [], 3, "3.1"),
    ("Vai trò TTTP đối với các chủ thể", [], 3, "3.2"),
    ("Ảnh hưởng của lãi suất thị trường đối với giá trái phiếu", [], 3, "3.3"),
    ("Thị trường cổ phiếu", ["TTCP"], 4, "4"),
    ("Tổng quan về thị trường cổ phiếu", [], 4, "4.1"),
    ("Vai trò của TTCP", [], 4, "4.2"),
    ("Quy trình giao dịch cổ phiếu trên sàn giao dịch", [], 4, "4.3"),
    ("Thị trường ngoại hối", [], 5, "5"),
    ("Tổng quan về thị trường ngoại hối", [], 5, "5.1"),
    ("Vai trò Thị trường Ngoại hối", [], 5, "5.2"),
    ("Sự tương tác giữa lạm phát, lãi suất với tỷ giá", ["quy luật ngang bằng sức mua", "quy luật ngang bằng lãi suất"], 5, "5.3"),
    ("Thị trường tài chính phái sinh", ["TTTCPS"], 6, "6"),
    ("Tổng quan về TTTCPS", [], 6, "6.1"),
    ("Các loại công cụ TCPS", ["hợp đồng kỳ hạn", "hợp đồng hoán đổi", "hợp đồng tương lai", "hợp đồng quyền chọn"], 6, "6.2"),
    ("Công dụng TTTCPS", [], 6, "6.3"),
    ("THỊ TRƯỜNG CHỨNG KHOÁN THẾ CHẤP BẤT ĐỘNG SẢN", ["TTCK TCBĐS"], 7, "7"),
    ("Tổng quan về chứng khoán thế chấp BĐS", ["Mortgage-backed securities"], 7, "7.1"),
    ("Thị trường chứng khoán thế chấp bất động sản sơ cấp", ["secondary mortgage market"], 7, "7.2"),
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
            "type": "COURSE_SEQUENCE_CONFLICT",
            "note": "Chương 6 tự gọi là chương cuối cùng, nhưng nguồn vẫn có đầy đủ Chương 7. Giữ cả hai và không tự suy đoán Chương 7 ngoài phạm vi.",
            "observations": [
                {"claim": "Chương 6 là chương cuối cùng", "source_id": "src-0146", "page": 1},
                {"claim": "Chương 7 hiện diện", "source_id": "src-0147", "page": 1},
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
