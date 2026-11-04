# Phase 6 summary — longitudinal evidence admission

NLKT + KTTC1. No mastery scores. Policy **1.0.0**.

## A. Architecture

Deterministic gate: provenance, dedup, self-report, mechanical-only, retries, hints, split dimensions, independent repeats. See `admission_architecture.md`.

## B. Evidence schema

`LongTermEvidenceCandidate` + `AdmissionDecision` (`ADMIT|HOLD|REJECT`) + clusters by concept×dimension. Store: `learner/evidence/`.

## C. Controlled benchmark

120 cases. System C pass **1.00**. Precision 1.00. False admission **0**. See `admission_benchmark.md`.

## D. Longitudinal simulation

40 sequences, pass **1.00** (HOLD→ADMIT, contradiction keep-both, guided never independent, self-report weak).

## E. Naturalistic

40 candidates. False ADMIT **0**. HOLD/REJECT **1.00**.

## F. False-admission risk

Priority metric 0.00 on controlled, longitudinal, and naturalistic sets.

## G. Positive vs negative

Admitted +25 / −25 on the controlled set. Not a failure-only memory.

## H. Hint / self-report

Self-report false ADMIT **0**. Hint-contaminated false ADMIT **0**.

## I. Contradiction

Preservation 1.00. Later success does not delete earlier observations.

## J. Deduplication

Inflation 0. Same diag/decision/summary lineage cannot triple-count.

## K. Regression

Phase 2 58/60. Phase 3 C 90/90. Phase 4 C 130/130. Phase 5 C 100/100 + adv 16/16.

## L. Next step

**A mastery *estimator* that reads admitted observations only** — still nullable, still no SRS — and never treats HOLD/REJECT as evidence.

## Decision

**PHASE6_PASS_EVIDENCE_MEMORY_READY**
