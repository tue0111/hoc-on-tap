# -*- coding: utf-8 -*-
"""Small competing-hypothesis set. Prerequisite gap is never the default."""
from __future__ import annotations

from retrieval.concepts import prerequisite_concepts

NLKT_CORE = {"no-co", "ghi-so-kep", "dinh-khoan", "tai-khoan-ke-toan", "phuong-trinh-ke-toan"}


def build_hypotheses(task: str, target: str | None, course: str | None, signals: dict) -> list[dict]:
    hs = []

    def add(hid, error_type, concept, prereq=None, why="", testable=True, exclusive=False):
        hs.append(
            {
                "hypothesis_id": hid,
                "error_type": error_type,
                "concept_id": concept,
                "prerequisite_concept_id": prereq,
                "evidence_for": why,
                "evidence_against": "",
                "confidence_before_test": "medium",
                "testable": testable,
                "exclusive": exclusive,
            }
        )

    if signals.get("out_of_scope") or signals.get("no_answer") and not any(
        signals.get(k) for k in ("reversed_dc_rule", "arithmetic", "formula_mismatch", "classification_asset_expense")
    ):
        if signals.get("out_of_scope"):
            add("H-scope", "unknown", target, why="topic outside NLKT/KTTC1 production slice", testable=False)
            return hs
        if signals.get("confusion_only") or signals.get("no_answer"):
            add("H-unknown", "unknown", target, why="no work shown; cannot locate the failed operation", testable=True)
            return hs

    # Mechanical first. On giá xuất items, keep arith vs formula as a competing
    # pair so one discriminating question can separate a slip from a method mix-up.
    valuation = target == "pp-tinh-gia-xuat-kho"
    if signals.get("arithmetic") and not signals.get("reversed_dc_rule"):
        add(
            "H-arith",
            "arithmetic_error",
            target,
            why="computation does not match a correctly identified method or stated arithmetic slip",
            exclusive=not valuation,
        )
        if not valuation:
            return hs
    if signals.get("formula_mismatch") and not signals.get("reversed_dc_rule"):
        add(
            "H-formula",
            "formula_selection_error",
            target,
            why="named/used a different taught method than the question asked",
            exclusive=not valuation,
        )
        if not valuation:
            return hs
    if valuation and signals.get("arithmetic") and not signals.get("formula_mismatch"):
        add("H-formula", "formula_selection_error", target, why="competing: same wrong total could be a method mix-up")
    if valuation and (signals.get("arithmetic") or signals.get("formula_mismatch")):
        return hs

    if signals.get("recall") and not signals.get("reversed_dc_rule"):
        add("H-recall", "recall_failure", target, why="learner states they cannot retrieve the term/account")

    if signals.get("terminology"):
        add("H-term", "terminology_confusion", target, why="near-synonym mixup in the response")

    if signals.get("classification_asset_expense"):
        add("H-class", "classification_error", target, why="object treated as expense instead of asset (or the reverse)")
        if not any(h["hypothesis_id"] == "H-acct" for h in hs):
            add("H-acct", "journal_entry_error", target, why="competing: expense account may be a recording slip with correct class")
    if signals.get("kktx_mix"):
        add("H-kktx", "conceptual_failure", target, why="perpetual vs periodic methods collapsed")

    if signals.get("wrong_account") and not signals.get("reversed_dc_rule"):
        if not any(h["hypothesis_id"] == "H-acct" for h in hs):
            add("H-acct", "journal_entry_error", target, why="account number/object does not match the taught object")
        if not any(h["hypothesis_id"] == "H-concept" for h in hs):
            add("H-concept", "conceptual_failure", target, why="competing: wrong account may reflect a concept error")

    if signals.get("procedural_skip"):
        add("H-proc", "procedural_error", target, why="taught sequence skipped")

    if signals.get("interpretation"):
        add("H-interp", "interpretation_error", target, why="numbers produced but meaning inverted")

    if signals.get("transfer"):
        add("H-xfer", "transfer_failure", target, why="procedure copied into a context the course treats differently")

    if signals.get("reversed_journal") and not signals.get("reversed_dc_rule"):
        add("H-revje", "journal_entry_error", target, why="debit/credit lines swapped without stating a false Nợ/Có rule")

    specific = {
        "classification_error",
        "journal_entry_error",
        "terminology_confusion",
        "recall_failure",
        "procedural_error",
        "interpretation_error",
        "transfer_failure",
        "arithmetic_error",
        "formula_selection_error",
        "prerequisite_gap",
    }
    # Conceptual current-course — only when no more specific failure is already isolated.
    if not signals.get("reversed_dc_rule") and not signals.get("arithmetic") and not signals.get("formula_mismatch"):
        if not any(h["error_type"] in specific for h in hs):
            if signals.get("correct_number_wrong_reason") or task in {
                "definition",
                "explanation",
                "classification",
                "journal_entry",
            }:
                add("H-concept", "conceptual_failure", target, why="explanation contradicts the taught model")

    # Prerequisite: only if an explicit false NLKT rule is written, or reverse JE with no other current-course explanation
    prereq_ids = prerequisite_concepts([target] if target else [], course)
    noco_available = "no-co" in prereq_ids or course == "ke-toan-tai-chinh-1" or (target in NLKT_CORE)
    if signals.get("reversed_dc_rule") and noco_available:
        add(
            "H-noco",
            "prerequisite_gap" if course == "ke-toan-tai-chinh-1" and target not in NLKT_CORE else "conceptual_failure",
            target if target in NLKT_CORE else "no-co",
            prereq="no-co" if course == "ke-toan-tai-chinh-1" and target not in NLKT_CORE else None,
            why="learner stated a false Nợ/Có / asset-direction rule",
        )
        # competing current-course account mix-up only if they also picked a weird TK
        if signals.get("wrong_account"):
            add("H-acct", "journal_entry_error", target, why="also used an unexpected account number")

    if not hs:
        if task in {"definition", "explanation", "classification", "journal_entry"}:
            add("H-concept", "conceptual_failure", target, why="false statement on a taught concept; no mechanical signal")
        else:
            add("H-unknown", "unknown", target, why="signals do not isolate a failure mode")
    return hs
