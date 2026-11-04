"""Build the audited concept table for ngan-hang-thuong-mai."""

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retrieval.textutil import fold


COURSE = "ngan-hang-thuong-mai"
PREFIX = "nhtm"


def slug(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalized(value: str) -> str:
    return fold(re.sub(r"\s+", " ", value))


# canonical name, aliases, chapter, topic, same_as, extra chapters
S = [
    ("TỔNG QUAN VỀ NGÂN HÀNG THƯƠNG MẠI", [], 1, "1", None, None),
    ("Khái quát về ngân hàng thương mại", [], 1, "1.1", None, None),
    ("Chức năng của Ngân hàng thương mại", ["trung gian tín dụng", "trung gian thanh toán"], 1, "1.2", None, None),
    ("Nghiệp vụ của Ngân hàng thương mại", [], 1, "1.3", None, None),
    ("NGHIỆP VỤ HUY ĐỘNG VỐN CỦA NGÂN HÀNG THƯƠNG MẠI", [], 2, "2", None, None),
    ("Khái niệm về nghiệp vụ huy động vốn của NHTM", [], 2, "2.1", None, None),
    ("Hình thức huy động vốn của NHTM", ["phát hành giấy tờ có giá"], 2, "2.2", None, None),
    ("TỔNG QUAN VỀ NGHIỆP VỤ CẤP TÍN DỤNG CỦA NGÂN HÀNG", [], 3, "3", None, None),
    ("Khái quát về nghiệp vụ cấp tín dụng", ["hoạt động cấp tín dụng"], 3, "3.1", None, None),
    ("Quy trình tín dụng", [], 3, "3.2", None, None),
    ("Đảm bảo tín dụng", ["bảo đảm tín dụng"], 3, "3.3", None, None),
    ("NGHIỆP VỤ CHO VAY", [], 4, "4", None, None),
    ("Cho vay ngắn hạn", ["hạn mức tín dụng"], 4, "4.1", None, None),
    ("Cho vay trung dài hạn", ["cho vay trung và dài hạn"], 4, "4.2", None, None),
    ("CÁC NGHIỆP VỤ TÍN DỤNG KHÁC", [], 5, "5", None, None),
    ("Nghiệp vụ chiết khấu giấy tờ có giá", ["chiết khấu giấy tờ có giá"], 5, "5.1", None, None),
    ("Nghiệp vụ cho thuê tài chính", ["cho thuê tài chính"], 5, "5.2", None, None),
    ("Nghiệp vụ bao thanh toán", ["bao thanh toán"], 5, "5.3", None, None),
    ("Nghiệp vụ bảo lãnh ngân hàng", ["bảo lãnh ngân hàng"], 5, "5.4", None, None),
    ("DỊCH VỤ NGÂN HÀNG", [], 6, "6", None, None),
    ("Dịch vụ thanh toán", [], 6, "6.1", None, None),
    ("Dịch vụ ngân hàng điện tử", [], 6, "6.2", None, None),
    ("Dịch vụ ủy thác và Dịch vụ phân phối bảo hiểm qua kênh ngân hàng", ["dịch vụ ủy thác", "phân phối bảo hiểm qua kênh ngân hàng"], 6, "6.3", None, None),
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
            "type": "LAW_VINTAGE_CONFLICT",
            "note": "Bài giảng dùng Luật các TCTD 47/2010/QH12 hoặc gọi Luật TCTD 2010; đề thi mẫu 2025 dùng Luật 32/2024/QH15. Giữ tách biệt, không hợp nhất định nghĩa hay hạn mức.",
            "observations": [
                {"instrument": "Luật các tổ chức tín dụng 47/2010/QH12", "source_id": "src-0124", "page": 2},
                {"instrument": "Luật các tổ chức tín dụng 32/2024/QH15", "source_id": "src-0128", "page": 7},
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
