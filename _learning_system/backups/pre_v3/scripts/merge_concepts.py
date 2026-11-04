# -*- coding: utf-8 -*-
"""Normalize heterogeneous course-scan concept lists into concept_registry.yaml."""
from __future__ import annotations
import json
import re
from pathlib import Path

import yaml

SCANS = Path(r"D:\Hoc\_learning_system\course_scans")
OUT = Path(r"D:\Hoc\_learning_system\curriculum\concept_registry.yaml")
DUMP = Path(r"D:\Hoc\_learning_system\inventory\normalized_courses.json")

# Cross-course aliases → a single concept_id. Only when the taught object is the same.
CANON = {
    "phuong-trinh-ke-toan": {
        "canonical_name": "Phương trình kế toán",
        "aliases": ["phương trình kế toán", "Tài sản = Nợ phải trả + Vốn chủ sở hữu", "accounting equation"],
        "match": re.compile(r"phương trình kế toán(?! mở rộng)|accounting.equation|ptkt$", re.I),
    },
    "bang-can-doi-ke-toan": {
        "canonical_name": "Bảng cân đối kế toán",
        "aliases": ["BCĐKT", "bảng cân đối", "balance sheet"],
        "match": re.compile(r"bảng cân đối kế toán|bcdkt|balance sheet", re.I),
    },
    "bao-cao-kqkd": {
        "canonical_name": "Báo cáo kết quả hoạt động kinh doanh",
        "aliases": ["BCKQKD", "BCKQHĐKD", "income statement"],
        "match": re.compile(r"báo cáo kết quả|bckqk|income statement", re.I),
    },
    "bao-cao-lctt": {
        "canonical_name": "Báo cáo lưu chuyển tiền tệ",
        "aliases": ["BCLCTT", "cash flow statement"],
        "match": re.compile(r"lưu chuyển tiền tệ|bclctt|cash.?flow", re.I),
    },
    "bao-cao-tai-chinh": {
        "canonical_name": "Báo cáo tài chính",
        "aliases": ["BCTC", "financial statements"],
        "match": re.compile(r"^báo cáo tài chính$|tổng quan về báo cáo tài chính|các yếu tố.*bctc|người sử dụng.*bctc", re.I),
    },
    "tai-khoan-ke-toan": {
        "canonical_name": "Tài khoản kế toán",
        "aliases": ["T-account", "kết cấu tài khoản"],
        "match": re.compile(r"^tài khoản kế toán$|kết cấu tài khoản", re.I),
    },
    "no-co": {
        "canonical_name": "Bên Nợ và bên Có",
        "aliases": ["Nợ/Có", "debit/credit", "ghi Nợ", "ghi Có"],
        "match": re.compile(r"\bnợ\b.*\bcó\b|debit|credit|bên nợ|bên có", re.I),
    },
    "ghi-so-kep": {
        "canonical_name": "Ghi sổ kép",
        "aliases": ["double entry", "nguyên tắc ghi sổ kép"],
        "match": re.compile(r"ghi sổ kép|double.?entry", re.I),
    },
    "dinh-khoan": {
        "canonical_name": "Định khoản kế toán",
        "aliases": ["bút toán", "journal entry"],
        "match": re.compile(r"định khoản|journal entry", re.I),
    },
    "but-toan-dieu-chinh": {
        "canonical_name": "Bút toán điều chỉnh",
        "aliases": ["adjusting entries"],
        "match": re.compile(r"bút toán điều chỉnh|điều chỉnh", re.I),
    },
    "khau-hao": {
        "canonical_name": "Khấu hao tài sản cố định",
        "aliases": ["khấu hao", "depreciation"],
        "match": re.compile(r"khấu hao", re.I),
    },
    "ket-chuyen": {
        "canonical_name": "Kết chuyển xác định kết quả kinh doanh",
        "aliases": ["closing entries", "kết chuyển"],
        "match": re.compile(r"kết chuyển", re.I),
    },
    "chung-tu-ke-toan": {
        "canonical_name": "Chứng từ kế toán",
        "aliases": ["source documents"],
        "match": re.compile(r"chứng từ kế toán", re.I),
    },
    "so-sach-ke-toan": {
        "canonical_name": "Sổ sách kế toán",
        "aliases": ["nhật ký chung", "sổ cái"],
        "match": re.compile(r"sổ sách kế toán|nhật ký chung|sổ cái", re.I),
    },
    "co-so-don-tich": {
        "canonical_name": "Cơ sở dồn tích",
        "aliases": ["accrual basis"],
        "match": re.compile(r"cơ sở dồn tích|dồn tích", re.I),
    },
    "nguyen-tac-phu-hop": {
        "canonical_name": "Nguyên tắc phù hợp",
        "aliases": ["matching principle"],
        "match": re.compile(r"nguyên tắc phù hợp|phù hợp", re.I),
    },
    "tien-va-tuong-duong-tien": {
        "canonical_name": "Tiền và tương đương tiền",
        "aliases": ["tiền", "cash and cash equivalents"],
        "match": re.compile(r"tiền và tương đương|tương đương tiền|^tiền$", re.I),
    },
    "no-phai-thu": {
        "canonical_name": "Nợ phải thu",
        "aliases": ["phải thu khách hàng", "receivables"],
        "match": re.compile(r"nợ phải thu|phải thu", re.I),
    },
    "hang-ton-kho": {
        "canonical_name": "Hàng tồn kho",
        "aliases": ["HTK", "inventory"],
        "match": re.compile(r"hàng tồn kho|\bhtk\b", re.I),
    },
    "tscd": {
        "canonical_name": "Tài sản cố định",
        "aliases": ["TSCĐ", "PPE"],
        "match": re.compile(r"tài sản cố định|tscd", re.I),
    },
    "no-phai-tra": {
        "canonical_name": "Nợ phải trả",
        "aliases": ["liabilities"],
        "match": re.compile(r"nợ phải trả", re.I),
    },
    "von-chu-so-huu": {
        "canonical_name": "Vốn chủ sở hữu",
        "aliases": ["equity", "VCSH"],
        "match": re.compile(r"vốn chủ sở hữu|vcsh", re.I),
    },
    "chi-phi-truc-tiep": {
        "canonical_name": "Chi phí trực tiếp",
        "aliases": ["direct cost"],
        "match": re.compile(r"chi phí trực tiếp|direct cost", re.I),
    },
    "chi-phi-gian-tiep": {
        "canonical_name": "Chi phí gián tiếp",
        "aliases": ["indirect cost"],
        "match": re.compile(r"chi phí gián tiếp|indirect", re.I),
    },
    "phan-bo-chi-phi": {
        "canonical_name": "Phân bổ chi phí",
        "aliases": ["allocation", "SXC allocation"],
        "match": re.compile(r"phân bổ", re.I),
    },
    "ktcp-theo-cong-viec": {
        "canonical_name": "Kế toán chi phí theo công việc",
        "aliases": ["job-order costing"],
        "match": re.compile(r"theo công việc|job.?order", re.I),
    },
    "ktcp-theo-quy-trinh": {
        "canonical_name": "Kế toán chi phí theo quy trình",
        "aliases": ["process costing", "theo quá trình"],
        "match": re.compile(r"theo quy trình|theo quá trình|process costing", re.I),
    },
    "kiem-soat-noi-bo": {
        "canonical_name": "Kiểm soát nội bộ",
        "aliases": ["KSNB", "internal control"],
        "match": re.compile(r"kiểm soát nội bộ|ksnb", re.I),
    },
    "kiem-toan": {
        "canonical_name": "Kiểm toán",
        "aliases": ["audit"],
        "match": re.compile(r"^kiểm toán$|tổng quan về kiểm toán", re.I),
    },
    "nhtm": {
        "canonical_name": "Ngân hàng thương mại",
        "aliases": ["NHTM", "commercial bank"],
        "match": re.compile(r"ngân hàng thương mại|^nhtm$", re.I),
    },
    "huy-dong-von": {
        "canonical_name": "Huy động vốn",
        "aliases": ["tiền gửi", "deposit"],
        "match": re.compile(r"huy động vốn", re.I),
    },
    "cap-tin-dung": {
        "canonical_name": "Cấp tín dụng",
        "aliases": ["tín dụng ngân hàng", "cho vay"],
        "match": re.compile(r"tín dụng|cho vay", re.I),
    },
    "thi-truong-tai-chinh": {
        "canonical_name": "Thị trường tài chính",
        "aliases": ["financial market"],
        "match": re.compile(r"thị trường tài chính", re.I),
    },
    "thoi-gia-tien-te": {
        "canonical_name": "Thời giá của tiền tệ",
        "aliases": ["TVM", "chiết khấu dòng tiền", "time value of money"],
        "match": re.compile(r"thời giá|chiết khấu dòng tiền|time value", re.I),
    },
    "capm": {
        "canonical_name": "Mô hình định giá tài sản vốn (CAPM)",
        "aliases": ["CAPM"],
        "match": re.compile(r"\bcapm\b|định giá tài sản vốn", re.I),
    },
    "chi-phi-su-dung-von": {
        "canonical_name": "Chi phí sử dụng vốn",
        "aliases": ["WACC", "cost of capital"],
        "match": re.compile(r"chi phí sử dụng vốn|chi phí vốn|wacc", re.I),
    },
    "dao-duc-nghe-nghiep-ke-toan": {
        "canonical_name": "Đạo đức nghề nghiệp kế toán",
        "aliases": ["đạo đức kế toán", "ethics"],
        "match": re.compile(r"đạo đức nghề", re.I),
    },
}


def name_of(item: dict) -> str:
    for k in ("canonical_name", "label", "name", "title", "text"):
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""


def id_of(item: dict, course_id: str, idx: int) -> str:
    for k in ("id", "suggested_id", "concept_id"):
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    slug = re.sub(r"[^a-z0-9]+", "-", name_of(item).lower())[:40].strip("-")
    return f"{course_id}-{slug or idx}"


def map_canon(name: str, local_id: str) -> str | None:
    blob = f"{local_id} {name}"
    for cid, spec in CANON.items():
        if spec["match"].search(blob):
            return cid
    return None


def walk_concepts(doc: dict, course_id: str):
    raw = doc.get("concepts")
    if raw is None:
        return []
    if isinstance(raw, dict):
        # maybe {items: []}
        if "items" in raw:
            raw = raw["items"]
        else:
            raw = list(raw.values()) if raw else []
    out = []
    if not isinstance(raw, list):
        return out
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            continue
        # skip quality-issue records accidentally under concepts
        local_id = id_of(item, course_id, i)
        if local_id.startswith("designed_") or local_id.startswith("chuong") or local_id.startswith("tmp_"):
            continue
        name = name_of(item) or local_id
        out.append(
            {
                "local_id": local_id,
                "name": name,
                "aliases": item.get("aliases") or [],
                "source_refs": item.get("source_refs") or item.get("sources") or ([item.get("source")] if item.get("source") else []),
                "confidence": item.get("confidence") or "medium",
                "evidence_status": item.get("evidence_status") or "OBSERVED",
                "course_id": course_id,
                "raw": {k: item.get(k) for k in item if k != "raw"},
            }
        )
    return out


def scalar(doc, *keys):
    cur = doc
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    if isinstance(cur, dict) and "value" in cur:
        return cur.get("value")
    return cur


def main():
    courses = []
    all_concepts = []
    for p in sorted(SCANS.glob("*.yaml")):
        if p.name.startswith("_"):
            continue
        try:
            doc = yaml.safe_load(p.read_text(encoding="utf-8"))
        except Exception as e:
            print("YAML_FAIL", p.name, e)
            continue
        if not isinstance(doc, dict):
            continue
        cid = doc.get("course_id") or p.stem
        name = doc.get("course_name")
        if isinstance(name, dict):
            name = name.get("value")
        courses.append(
            {
                "course_id": cid,
                "course_name": name,
                "course_code": scalar(doc, "course_code") or (doc.get("course_code") or {}).get("value") if isinstance(doc.get("course_code"), dict) else doc.get("course_code"),
                "institution": scalar(doc, "institution"),
                "file": p.name,
                "has_concepts": "concepts" in doc,
            }
        )
        all_concepts.extend(walk_concepts(doc, cid))

    DUMP.write_text(json.dumps({"courses": courses, "concept_count": len(all_concepts)}, ensure_ascii=False, indent=2), encoding="utf-8")

    groups = {}
    leftovers = []
    for c in all_concepts:
        mapped = map_canon(c["name"], c["local_id"])
        if mapped:
            groups.setdefault(mapped, []).append(c)
        else:
            leftovers.append(c)

    lines = [
        "registry_id: concept-registry",
        'version: "0.1.0"',
        "layer: curriculum",
        "note: >",
        "  High-value structural concepts from syllabi, headings, learning objectives,",
        "  and recurring terms. Cross-course ids are merged only when the taught object",
        "  is the same (e.g. Bảng cân đối kế toán). Course-local ids keep provenance.",
        "  Prerequisites inside this file are pointers; graph edges live in concept_graph.yaml.",
        f"generated_from_scans: {len(courses)}",
        f"raw_concept_records_in_scans: {len(all_concepts)}",
        "concepts:",
    ]

    for cid, spec in CANON.items():
        items = groups.get(cid, [])
        if not items:
            continue
        courses_hit = sorted({x["course_id"] for x in items})
        srcs = []
        for x in items:
            for s in x["source_refs"]:
                if s and s not in srcs:
                    srcs.append(s)
        aliases = list(spec["aliases"])
        for x in items:
            if isinstance(x["aliases"], list):
                for a in x["aliases"]:
                    if isinstance(a, str) and a not in aliases:
                        aliases.append(a)
        lines.append(f"  - concept_id: {cid}")
        lines.append(f"    canonical_name: {json.dumps(spec['canonical_name'], ensure_ascii=False)}")
        lines.append("    aliases:")
        for a in aliases:
            lines.append(f"      - {json.dumps(a, ensure_ascii=False)}")
        lines.append("    courses:")
        for c in courses_hit:
            lines.append(f"      - {c}")
        lines.append("    appearances:")
        for x in items[:12]:
            lines.append(f"      - course_id: {x['course_id']}")
            lines.append(f"        local_id: {x['local_id']}")
            lines.append(f"        name: {json.dumps(x['name'], ensure_ascii=False)}")
        lines.append("    source_refs:")
        for s in srcs[:20]:
            if isinstance(s, dict):
                lines.append(f"      - {json.dumps(s, ensure_ascii=False)}")
            else:
                lines.append(f"      - {s}")
        lines.append("    prerequisites:")
        lines.append("      explicit: []")
        lines.append("      inferred: []")
        lines.append("    related: []")
        lines.append("    confidence: high")
        lines.append("    evidence_status: OBSERVED")
        lines.append("    merge_note: cross-course canonical id from matching names in course scans")

    # Keep leftover high-value locals (cap to avoid dumping noise)
    # Prefer ids that look like real concept slugs (contain a hyphen and a course prefix)
    kept = []
    for x in leftovers:
        lid = x["local_id"]
        if lid.startswith("designed_") or "unknown" in lid:
            continue
        if len(x["name"]) < 3:
            continue
        kept.append(x)

    # Dedup leftovers by local_id
    seen = set()
    for x in kept:
        if x["local_id"] in seen:
            continue
        seen.add(x["local_id"])
        lines.append(f"  - concept_id: {x['local_id']}")
        lines.append(f"    canonical_name: {json.dumps(x['name'], ensure_ascii=False)}")
        als = x["aliases"] if isinstance(x["aliases"], list) else []
        if als:
            lines.append("    aliases:")
            for a in als:
                if isinstance(a, str):
                    lines.append(f"      - {json.dumps(a, ensure_ascii=False)}")
        else:
            lines.append("    aliases: []")
        lines.append("    courses:")
        lines.append(f"      - {x['course_id']}")
        lines.append("    appearances:")
        lines.append(f"      - course_id: {x['course_id']}")
        lines.append(f"        local_id: {x['local_id']}")
        srcs = x["source_refs"] or []
        lines.append("    source_refs:")
        if srcs:
            for s in srcs[:8]:
                if isinstance(s, (str, int)):
                    lines.append(f"      - {s}")
                else:
                    lines.append(f"      - {json.dumps(s, ensure_ascii=False)}")
        else:
            lines.append("      []")
        lines.append("    prerequisites:")
        lines.append("      explicit: []")
        lines.append("      inferred: []")
        lines.append("    related: []")
        lines.append(f"    confidence: {x.get('confidence') or 'medium'}")
        lines.append(f"    evidence_status: {x.get('evidence_status') or 'OBSERVED'}")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("courses", len(courses), "raw_concepts", len(all_concepts), "canonical_groups", len(groups), "leftovers_kept", len(seen))


if __name__ == "__main__":
    main()
