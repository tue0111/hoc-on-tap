# Decision benchmark (Phase 4) — CONTROLLED SET

Cases: `evals/decision_cases.jsonl` (130).  
Rubric: `evals/decision_rubric.yaml`.  
Raw: `reports/decision_benchmark_raw.json`.  
Command: `python scripts/phase4_eval.py`

This file is the **controlled** set only. Naturalistic shadow is `decision_naturalistic_shadow.md`. Do not average them.

## Composition

| requirement | n (actual) |
|---|---|
| recall failures | 16 |
| conceptual failures | 27 |
| classification/application | 20 |
| procedural/mechanical | 23 |
| confirmed prerequisite gaps | 20 |
| must-not-backfill | 110 tagged (10 dedicated + all non-prereq) |
| VERIFY_MORE | 15 |
| NO_INTERVENTION | 5 |
| **total** | **130** (≥100) |

Gold actions are specified independently of Phase 3 labels (same policy table, separate file). Contrastive triples: same purchase/FIFO stem → CONTRASTIVE vs PREREQUISITE_MICRO_BACKFILL vs MECHANICAL_CORRECTION.

## Baselines vs System C

| system | meaning | pass | action acc | false prereq backfill | over-treat |
|---|---|---|---|---|---|
| A | generic “review the topic” | 0.21 | 0.21 | 0.00 | 1.00 |
| B | static error-type → action | 0.95 | 0.95 | 0.008 | 0.008 |
| **C** | causal + prereq guard + minimality + thin-evidence | **1.00** | **1.00** | **0.00** | **0.00** |

C’s value over B on this set: unconfirmed-prereq refused, journal-as-symptom rerouted to classification, NO_INTERVENTION not taught.

1.00 on the controlled set is saturation of cue-aligned + injected cases, not naturalistic performance.

## System C vs gates

| metric | C | gate | result |
|---|---|---|---|
| primary-gap accuracy | 1.00 | ≥ 0.90 | PASS |
| action accuracy | 1.00 | ≥ 0.85 | PASS |
| prerequisite-backfill precision | 1.00 | ≥ 0.95 | PASS |
| false prerequisite-backfill | 0.00 | ≤ 0.03 | PASS |
| over-treatment | 0.00 | ≤ 0.05 | PASS |
| under-treatment | 0.00 | — | — |
| decision grounding | 1.00 | ≥ 0.95 | PASS |
| VERIFY_MORE correctness | 1.00 | ≥ 0.85 | PASS |
| NO_INTERVENTION correctness | 1.00 | — | — |
| wrong-course intervention | 0.00 | — | — |
