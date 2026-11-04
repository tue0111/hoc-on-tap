# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(r"D:\Hoc")
SYSTEM = ROOT / "_learning_system"
SOURCE_ROOT = ROOT

SLICE_COURSE_IDS = ("nguyen-ly-ke-toan", "ke-toan-tai-chinh-1")
COURSE_NAMES = {
    "nguyen-ly-ke-toan": "Nguyên lý kế toán",
    "ke-toan-tai-chinh-1": "Kế toán tài chính 1",
}
COURSE_CODES = {
    "nguyen-ly-ke-toan": "ACCO1325",
    "ke-toan-tai-chinh-1": "ACCO2310",
}

INDEX_VERSION = "2.0.0"
CHUNKING_VERSION = "2.0.0"
EXTRACT_VERSION = "2.0.0"

DATA = SYSTEM / "data"
NORMALIZED = DATA / "normalized"
CHUNKS_DIR = DATA / "chunks"
INDEX_DIR = DATA / "indexes" / INDEX_VERSION
CACHE = SYSTEM / "cache" / "phase2"

INVENTORY = SYSTEM / "inventory" / "files.json"
CONCEPT_REGISTRY = SYSTEM / "curriculum" / "concept_registry.yaml"
CONCEPT_GRAPH = SYSTEM / "curriculum" / "concept_graph.yaml"
SOURCE_OVERRIDES = SYSTEM / "curriculum" / "source_registry_overrides.yaml"
SOURCE_AUTHORITY = SYSTEM / "curriculum" / "source_authority.yaml"

# Combined concatenations: extract for coverage, exclude from default retrieval index.
COMBINED_SOURCE_IDS = frozenset({"src-0093", "src-0063", "src-0068"})

AUTHORITY_BY_ROLE = {
    "syllabus": 1,
    "lecture_slide": 2,
    "lecture_note": 2,
    "textbook": 3,
    "exercise": 4,
    "solution": 4,
    "exam": 5,
    "quiz": 5,
    "assignment": 5,
    "reference": 6,
    "summary": 6,
    "unknown": 8,
}

CONTENT_ROLE_AUTHORITY = {
    "lecture_note_combined": 2,
    "lecture_slide_combined": 2,
    "exercise": 4,
    "solution": 4,
}

TARGET_CHUNK_CHARS = 900
MAX_CHUNK_CHARS = 1600
MIN_CHUNK_CHARS = 180
THIN_CHARS_PER_PAGE = 40

HYBRID_WEIGHTS = {
    "bm25": 0.42,
    "tfidf": 0.22,
    "concept": 0.18,
    "metadata": 0.12,
    "authority": 0.06,
}

TOP_K_DEFAULT = 8
PREREQ_TOP_K = 5
