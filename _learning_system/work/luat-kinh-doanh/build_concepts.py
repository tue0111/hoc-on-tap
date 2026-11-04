"""Build the audited concept table for luat-kinh-doanh."""

import json
import re
import sys
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from retrieval.textutil import fold


COURSE = "luat-kinh-doanh"
PREFIX = "lkd"


def slug(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    value = unicodedata.normalize("NFD", value)
    value = "".join(c for c in value if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalized(value: str) -> str:
    return fold(re.sub(r"\s+", " ", value))


# canonical name, aliases, chapter, topic, same_as, extra chapters
S = [
    ("TỔNG QUAN VỀ LUẬT KINH DOANH", ["đối tượng điều chỉnh", "phương pháp điều chỉnh"], 1, None, None, None),
    ("Pháp luật về chủ thể kinh doanh", [], 2, None, None, None),
    ("Quy chế pháp lý chung về doanh nghiệp", ["ĐKKD", "ĐKDN"], 2, "2.1", None, None),
    ("Công ty trách nhiệm hữu hạn", ["TNHH"], 2, "2.2", None, None),
    ("CÔNG TY CỔ PHẦN", ["CTCP"], 2, "2.3", None, None),
    ("Công ty hợp danh và doanh nghiệp tư nhân", ["công ty hợp danh", "doanh nghiệp tư nhân"], 2, "2.4", None, None),
    ("Hộ kinh doanh và hợp tác xã", ["HKD", "HTX"], 2, "2.5", None, None),
    ("PHÁP LUẬT VỀ HỢP ĐỒNG KINH DOANH, THƯƠNG MẠI", [], 3, None, None, None),
    ("Khái quát về pháp luật hợp đồng, hợp đồng kinh doanh, thương mại", ["khái niệm hợp đồng", "phân loại hợp đồng"], 3, "3.1", None, None),
    ("Pháp luật về hợp đồng dân sự", ["giao kết hợp đồng dân sự", "thực hiện hợp đồng dân sự"], 3, "3.2", None, None),
    ("Pháp luật về hợp đồng trong hoạt động kinh doanh, thương mại", ["vi phạm hợp đồng kinh doanh"], 3, "3.3", None, None),
    ("PHÁP LUẬT VỀ PHÁ SẢN", [], 4, None, None, None),
    ("Khái quát pháp luật về phá sản", ["mất khả năng thanh toán"], 4, "4.1", None, None),
    ("Trình tự, thủ tục giải quyết phá sản", ["mở thủ tục phá sản"], 4, "4.2", None, None),
    ("GIẢI QUYẾT TRANH CHẤP KINH DOANH, THƯƠNG MẠI", [], 5, None, None, None),
    ("Giải quyết tranh chấp kinh doanh, thương mại bằng phương thức thương lượng và hòa giải", ["thương lượng và hòa giải"], 5, "5.1", None, None),
    ("GIẢI QUYẾT TRANH CHẤP KINH DOANH, THƯƠNG MẠI BẰNG PHƯƠNG THỨC TÒA ÁN", ["thẩm quyền theo lãnh thổ"], 5, "5.2", None, None),
    ("GIẢI QUYẾT TRANH CHẤP KINH DOANH, THƯƠNG MẠI BẰNG PHƯƠNG THỨC TRỌNG TÀI", ["trọng tài thương mại"], 5, "5.3", None, None),
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
        suffix = topic.replace(".", "-") if topic else str(chapter)
        concept_id = f"{concept_id}-{suffix}"
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
            item[0].get("topic") != topic if topic else item[0].get("chapter") != chapter,
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
    "conflicts": [],
}

output_path = ROOT / "curriculum" / "concepts" / f"{COURSE}.yaml"
output_path.parent.mkdir(parents=True, exist_ok=True)
with output_path.open("w", encoding="utf-8", newline="\n") as handle:
    yaml.safe_dump(document, handle, allow_unicode=True, sort_keys=False, width=120)

print(len(concepts), "concepts; dropped:", dropped)
