# -*- coding: utf-8 -*-
from __future__ import annotations
import re
from functools import lru_cache
from pathlib import Path

import yaml

from retrieval.config import CONCEPT_GRAPH, CONCEPT_REGISTRY
from retrieval.textutil import fold, nfc

# Aliases too generic to map a whole chunk (course titles, short tokens).
GENERIC_ALIASES = frozenset(
    {
        "htk",
        "bctc",
        "tt 200",
        "fifo",
        "t-account",
        "kế toán tài chính",
        "kế toán quản trị",
        "bút toán",
    }
)

ACCOUNT_MAP = {
    "111": "tien-va-tuong-duong-tien",
    "112": "tien-va-tuong-duong-tien",
    "113": "tien-va-tuong-duong-tien",
    "131": "no-phai-thu",
    "133": "no-phai-thu",
    "136": "no-phai-thu",
    "138": "no-phai-thu",
    "141": "no-phai-thu",
    "2293": "no-phai-thu",
    "151": "hang-ton-kho",
    "152": "hang-ton-kho",
    "153": "hang-ton-kho",
    "154": "hang-ton-kho",
    "155": "hang-ton-kho",
    "156": "hang-ton-kho",
    "157": "hang-ton-kho",
    "2294": "hang-ton-kho",
}

SLICE_CONCEPTS = frozenset(
    {
        "ke-toan-he-thong-thong-tin",
        "linh-vuc-ke-toan",
        "bao-cao-tai-chinh",
        "bang-can-doi-ke-toan",
        "bao-cao-kqkd",
        "bao-cao-lctt",
        "thuyet-minh-bctc",
        "phuong-trinh-ke-toan",
        "phuong-trinh-ke-toan-mo-rong",
        "nguyen-tac-ke-toan",
        "co-so-don-tich",
        "nguyen-tac-phu-hop",
        "tai-khoan-ke-toan",
        "no-co",
        "ghi-so-kep",
        "dinh-khoan",
        "kiem-tra-doi-chieu",
        "but-toan-dieu-chinh",
        "chi-phi-tra-truoc",
        "khau-hao",
        "ket-chuyen",
        "chung-tu-ke-toan",
        "so-sach-ke-toan",
        "tt200",
        "tien-va-tuong-duong-tien",
        "no-phai-thu",
        "hang-ton-kho",
        "kktx-kkdk",
        "pp-tinh-gia-xuat-kho",
        "chuan-muc-ke-toan",
        "tscd",  # appears in NLKT C4.3; KTTC1 questions about TSCĐ should often be insufficient
    }
)


@lru_cache(maxsize=1)
def load_registry() -> list[dict]:
    doc = yaml.safe_load(Path(CONCEPT_REGISTRY).read_text(encoding="utf-8"))
    return list(doc.get("concepts") or [])


@lru_cache(maxsize=1)
def load_graph() -> dict:
    return yaml.safe_load(Path(CONCEPT_GRAPH).read_text(encoding="utf-8")) or {}


def _phrases_for(concept: dict) -> list[tuple[str, str]]:
    cid = concept["concept_id"]
    if cid not in SLICE_CONCEPTS:
        return []
    out = []
    name = nfc(concept.get("canonical_name") or "")
    if name:
        out.append((fold(name), "canonical"))
    for a in concept.get("aliases") or []:
        if not isinstance(a, str):
            continue
        fa = fold(a)
        if fa in GENERIC_ALIASES or len(fa) < 6:
            continue
        out.append((fa, "alias"))
    # extra distinctive phrases
    extras = {
        "no-co": ["bên nợ", "bên có", "ghi nợ", "ghi có", "nợ/có", "nợ có", "nguyên tắc nợ"],
        "ghi-so-kep": ["ghi sổ kép", "nguyên tắc ghi sổ kép"],
        "phuong-trinh-ke-toan": ["phương trình kế toán"],
        "kktx-kkdk": ["kê khai thường xuyên", "kiểm kê định kỳ"],
        "pp-tinh-gia-xuat-kho": ["bình quân gia quyền", "nhập trước xuất trước", "giá thực tế đích danh"],
        "tt200": ["thông tư 200", "200/2014/tt-btc"],
        "co-so-don-tich": ["cơ sở dồn tích"],
        "but-toan-dieu-chinh": ["bút toán điều chỉnh"],
        "tien-va-tuong-duong-tien": ["tương đương tiền", "tiền mặt", "hạch toán tiền", "kế toán tiền"],
        "hang-ton-kho": ["hàng tồn kho"],
        "no-phai-thu": ["nợ phải thu", "phải thu khách hàng"],
        "dinh-khoan": ["định khoản"],
        "khau-hao": ["khấu hao"],
        "ket-chuyen": ["kết chuyển"],
        "chung-tu-ke-toan": ["chứng từ kế toán"],
        "so-sach-ke-toan": ["sổ sách kế toán", "nhật ký chung"],
        "bang-can-doi-ke-toan": ["bảng cân đối kế toán"],
        "bao-cao-kqkd": ["báo cáo kết quả hoạt động"],
        "bao-cao-lctt": ["báo cáo lưu chuyển tiền tệ"],
        "bao-cao-tai-chinh": ["báo cáo tài chính"],
        "tai-khoan-ke-toan": ["tài khoản kế toán"],
        "chuan-muc-ke-toan": ["chuẩn mực kế toán"],
        "tscd": ["tài sản cố định", "tscđ"],
    }
    for p in extras.get(cid, []):
        out.append((fold(p), "extra"))
    # longer first
    out.sort(key=lambda x: -len(x[0]))
    return out


@lru_cache(maxsize=1)
def phrase_table() -> list[tuple[str, str, str]]:
    rows = []
    for c in load_registry():
        cid = c["concept_id"]
        for phrase, kind in _phrases_for(c):
            rows.append((phrase, cid, kind))
    rows.sort(key=lambda x: -len(x[0]))
    return rows


def map_text(text: str) -> list[dict]:
    f = fold(text)
    found = {}
    for phrase, cid, kind in phrase_table():
        if phrase and phrase in f:
            conf = "high" if kind == "canonical" else "medium"
            prev = found.get(cid)
            if not prev or (conf == "high" and prev["confidence"] != "high"):
                found[cid] = {"concept_id": cid, "confidence": conf, "match": phrase, "kind": kind}
    for m in re.finditer(r"\b(tk|tài khoản)\s*(\d{3,4})\b", f):
        num = m.group(2)
        cid = ACCOUNT_MAP.get(num)
        if cid and cid not in found:
            found[cid] = {"concept_id": cid, "confidence": "medium", "match": m.group(0), "kind": "account"}
    return list(found.values())


def detect_query_concepts(question: str) -> list[str]:
    return [m["concept_id"] for m in map_text(question)]


def prerequisite_concepts(concept_ids: list[str], current_course: str | None) -> list[str]:
    """NLKT concepts that are explicit/inferred bases for the detected set."""
    graph = load_graph()
    edges = graph.get("edges") or []
    detected = set(concept_ids)
    prereq = []
    for e in edges:
        src = e.get("from")
        dst = e.get("to")
        if dst in detected and src not in detected:
            # only pull NLKT-native nodes as prerequisites of KTTC1 concepts
            if current_course == "ke-toan-tai-chinh-1":
                if src in {
                    "phuong-trinh-ke-toan",
                    "tai-khoan-ke-toan",
                    "no-co",
                    "ghi-so-kep",
                    "dinh-khoan",
                    "bao-cao-tai-chinh",
                    "bang-can-doi-ke-toan",
                    "nguyen-tac-ke-toan",
                    "co-so-don-tich",
                    "chung-tu-ke-toan",
                    "so-sach-ke-toan",
                    "but-toan-dieu-chinh",
                }:
                    prereq.append(src)
            elif dst in detected:
                if e.get("edge_type") in {"prerequisite", "conceptual_basis", "applied_as", "used_in"}:
                    prereq.append(src)
    # always consider core bookkeeping chain if KTTC1 journal/account question
    if current_course == "ke-toan-tai-chinh-1":
        if detected & {"tien-va-tuong-duong-tien", "no-phai-thu", "hang-ton-kho", "dinh-khoan", "tt200"}:
            for c in ("tai-khoan-ke-toan", "no-co", "ghi-so-kep", "dinh-khoan"):
                if c not in detected:
                    prereq.append(c)
    # unique preserve order
    seen = set()
    out = []
    for c in prereq:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


# ---------------------------------------------------------------------------
# V3: per-course concept tables (curriculum/concepts/<course_id>.yaml).
# Core functions above never read these files.
# ---------------------------------------------------------------------------
def _course_concept_path(course_id: str) -> Path:
    from retrieval.config import SYSTEM

    return SYSTEM / "curriculum" / "concepts" / f"{course_id}.yaml"


@lru_cache(maxsize=32)
def load_course_concepts(course_id: str) -> dict:
    p = _course_concept_path(course_id)
    if not p.exists():
        return {"course_id": course_id, "concepts": [], "account_map": {}, "edges": [], "conflicts": []}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


@lru_cache(maxsize=32)
def course_phrase_table(course_id: str) -> list[tuple[str, str, str]]:
    rows = []
    for c in load_course_concepts(course_id).get("concepts") or []:
        cid = c["concept_id"]
        name = nfc(c.get("canonical_name") or "")
        if name:
            rows.append((fold(name), cid, "canonical"))
        for a in c.get("aliases") or []:
            if not isinstance(a, str):
                continue
            fa = fold(a)
            if not fa:
                continue
            rows.append((fa, cid, "alias"))
    rows.sort(key=lambda x: -len(x[0]))
    return rows


def map_text_course(text: str, course_id: str) -> list[dict]:
    f = fold(text)
    found = {}
    for phrase, cid, kind in course_phrase_table(course_id):
        if phrase and phrase in f:
            conf = "high" if kind == "canonical" else "medium"
            prev = found.get(cid)
            if not prev or (conf == "high" and prev["confidence"] != "high"):
                found[cid] = {"concept_id": cid, "confidence": conf, "match": phrase, "kind": kind}
    amap = load_course_concepts(course_id).get("account_map") or {}
    for m in re.finditer(r"\b(tk|tài khoản)\s*(\d{3,4})\b", f):
        cid = amap.get(m.group(2))
        if cid and cid not in found:
            found[cid] = {"concept_id": cid, "confidence": "medium", "match": m.group(0), "kind": "account"}
    return list(found.values())


def detect_course_concepts(question: str, course_id: str) -> list[str]:
    return [m["concept_id"] for m in map_text_course(question, course_id)]
