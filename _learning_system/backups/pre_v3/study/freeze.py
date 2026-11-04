# -*- coding: utf-8 -*-
"""Freeze core versions and frozen-suite hashes. Instrumentation only."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from study.integrity import load_inventory, sha256_text, verify_sources

ROOT = Path(r"D:\Hoc\_learning_system")
OUT = ROOT / "pilot" / "core_freeze_manifest.json"

EVAL_FILES = [
    "evals/phase2_retrieval_tests.jsonl",
    "evals/diagnostic_cases.jsonl",
    "evals/decision_cases.jsonl",
    "evals/decision_naturalistic_shadow.jsonl",
    "evals/adaptive_sessions.jsonl",
    "evals/adaptive_adversarial.jsonl",
    "evals/admission_cases.jsonl",
    "evals/admission_longitudinal.jsonl",
    "evals/admission_naturalistic.jsonl",
    "evals/state_cases.jsonl",
    "evals/state_longitudinal.jsonl",
    "evals/state_naturalistic.jsonl",
    "evals/learning_policy_cases.jsonl",
    "evals/learning_policy_longitudinal.jsonl",
    "evals/learning_policy_naturalistic.jsonl",
    "evals/learning_policy_adversarial.jsonl",
    "evals/learning_policy_e2e.jsonl",
]


def _count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    n = 0
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                n += 1
    return n


def build_manifest() -> dict:
    from admission.policy import POLICY_VERSION as ADMISSION_POLICY
    from diagnostic import __version__ as DIAG_V
    from decision import __version__ as DEC_V
    from adaptive import __version__ as ADAPT_V
    from admission import __version__ as ADM_V
    from mastery.estimator import POLICY_VERSION as STATE_V
    from learning_policy.engine import POLICY_VERSION as POL_V
    from retrieval.config import INDEX_VERSION, CHUNKING_VERSION, EXTRACT_VERSION

    integrity = verify_sources()
    inv = load_inventory()
    evals = {}
    for rel in EVAL_FILES:
        p = ROOT / rel
        evals[rel] = {
            "sha256": sha256_text(p) if p.exists() else None,
            "n": _count_jsonl(p),
            "exists": p.exists(),
        }
    index_meta = json.loads((ROOT / "data" / "indexes" / INDEX_VERSION / "meta.json").read_text(encoding="utf-8"))
    concept_reg = (ROOT / "curriculum" / "concept_registry.yaml").read_text(encoding="utf-8").splitlines()[:3]
    return {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "core_status": "PHASE8_PASS_CORE_LEARNING_SYSTEM_READY",
        "active_scope": ["ACCO1325", "ACCO2310"],
        "versions": {
            "index": INDEX_VERSION,
            "chunking": CHUNKING_VERSION,
            "extract": EXTRACT_VERSION,
            "retrieval": "2.0.0",
            "diagnostic": DIAG_V,
            "decision": DEC_V,
            "adaptive": ADAPT_V,
            "admission_module": ADM_V,
            "admission_policy": ADMISSION_POLICY,
            "state_derivation": STATE_V,
            "learning_policy": POL_V,
            "concept_registry": "0.1.0",
        },
        "index_meta": {
            "chunk_count": index_meta.get("chunk_count"),
            "vocab_size": index_meta.get("vocab_size"),
            "courses": index_meta.get("courses"),
            "concept_registry_version": index_meta.get("concept_registry_version"),
        },
        "inventory": {
            "path": "inventory/files.json",
            "sha256": sha256_text(ROOT / "inventory" / "files.json"),
            "file_count": len(inv),
        },
        "source_integrity": {
            "status": integrity["status"],
            "checked": integrity["checked"],
            "missing": len(integrity["missing"]),
            "mismatches": len(integrity["mismatches"]),
            "courses": integrity["courses"],
        },
        "frozen_suites": evals,
        "concept_registry_header": concept_reg,
        "note": "Derived freeze. Not evidence of learning success. Do not edit frozen eval JSONL to pass new code.",
    }


def write_manifest(path: Path | None = None) -> dict:
    man = build_manifest()
    dest = path or OUT
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(man, ensure_ascii=False, indent=2), encoding="utf-8")
    return man
