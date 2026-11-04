# -*- coding: utf-8 -*-
"""Admission policy v1.0.0. Evidence only. No mastery scores."""

POLICY_VERSION = "1.0.0"

REASON = (
    "STRONG_DIRECT_EVIDENCE",
    "REPEATED_INDEPENDENT_EVIDENCE",
    "TRANSFER_EVIDENCE",
    "CURRICULUM_GROUNDED",
    "HINT_CONTAMINATED",
    "SELF_REPORT_ONLY",
    "SAME_TASK_RETRY",
    "INSUFFICIENT_REPETITION",
    "CONTRADICTORY_EVIDENCE",
    "DUPLICATE_EVIDENCE",
    "DIAGNOSIS_INCONCLUSIVE",
    "LOW_PARSE_CONFIDENCE",
    "MECHANICAL_ONLY",
    "SOURCE_UNCERTAIN",
    "TEMPORARY_CONTEXT",
    "POSITIVE_INDEPENDENT_EVIDENCE",
    "SPLIT_DIMENSIONS",
)

INDEPENDENT = {"INDEPENDENT_TASK", "CROSS_CONTEXT_TRANSFER"}
HINT_BAD = {"DIRECT_HINT", "ANSWER_EXPOSED", "STRUCTURAL_HINT"}
FORBIDDEN_INFERENCE = (
    "Do not store 'learner is weak at this concept'.",
    "Do not store a mastery percentage.",
    "Do not store a personality judgment.",
    "Observation only.",
)
