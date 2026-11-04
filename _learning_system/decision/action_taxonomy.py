# -*- coding: utf-8 -*-
"""Small controlled intervention taxonomy. Phase 4 does not execute lessons."""

ACTIONS = (
    "RECALL_REFRESH",
    "MECHANISM_EXPLANATION",
    "CONTRASTIVE_EXAMPLE",
    "WORKED_EXAMPLE",
    "PROCEDURE_REHEARSAL",
    "APPLICATION_PRACTICE",
    "PREREQUISITE_MICRO_BACKFILL",
    "TERMINOLOGY_CLARIFICATION",
    "MECHANICAL_CORRECTION",
    "VERIFY_MORE",
    "NO_INTERVENTION",
)

# Broader actions that Phase 4 must reject even if pedagogically tempting.
FORBIDDEN = (
    "REVIEW_ENTIRE_CHAPTER",
    "REVIEW_ALL_NLKT",
    "REVIEW_ALL_FUNDAMENTALS",
    "FULL_STUDY_PLAN",
    "SPACED_REPETITION",
    "MULTI_GAP_BUNDLE",
)

DEPTH = {
    "RECALL_REFRESH": "MICRO",
    "MECHANICAL_CORRECTION": "MICRO",
    "TERMINOLOGY_CLARIFICATION": "MICRO",
    "PREREQUISITE_MICRO_BACKFILL": "MICRO",
    "CONTRASTIVE_EXAMPLE": "SHORT",
    "MECHANISM_EXPLANATION": "SHORT",
    "WORKED_EXAMPLE": "SHORT",
    "PROCEDURE_REHEARSAL": "SHORT",
    "APPLICATION_PRACTICE": "SHORT",
    "VERIFY_MORE": "MICRO",
    "NO_INTERVENTION": "MICRO",
}

EFFECT = {
    "RECALL_REFRESH": "Restore the taught term, account number, or formula name without re-teaching the model.",
    "MECHANISM_EXPLANATION": "Correct the taught mechanism for this concept only.",
    "CONTRASTIVE_EXAMPLE": "Separate two taught buckets/methods so the misclassified object is placed correctly.",
    "WORKED_EXAMPLE": "Show one taught recording of the diagnosed object, not a full journal-methods course.",
    "PROCEDURE_REHEARSAL": "Rehearse the skipped taught sequence for this task.",
    "APPLICATION_PRACTICE": "Apply the same taught concept in a context the course treats differently.",
    "PREREQUISITE_MICRO_BACKFILL": "Patch only the confirmed NLKT rule that the KTTC1 error depends on.",
    "TERMINOLOGY_CLARIFICATION": "Distinguish the two near-synonyms as the corpus uses them.",
    "MECHANICAL_CORRECTION": "Correct the arithmetic/copy slip; do not re-teach the method.",
    "VERIFY_MORE": "Obtain one discriminating response before any teaching action.",
    "NO_INTERVENTION": "No learning gap is evidenced; do not treat.",
}

# Causal rank: upstream cause before downstream symptom. Lower = more causal.
CAUSAL_RANK = {
    "prerequisite_gap": 0,
    "conceptual_failure": 1,
    "classification_error": 2,
    "interpretation_error": 3,
    "terminology_confusion": 4,
    "formula_selection_error": 5,
    "transfer_failure": 6,
    "recall_failure": 7,
    "procedural_error": 8,
    "journal_entry_error": 9,
    "arithmetic_error": 10,
    "source_conflict": 11,
    "unknown": 20,
    "none": 21,
}
