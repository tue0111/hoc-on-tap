# Phase 7 summary — longitudinal learner state

NLKT + KTTC1. Admitted evidence only. No SRS, no global score.

## A. State model

Per concept × {recall, conceptual, procedural, application, transfer}. States: INSUFFICIENT_EVIDENCE, TENTATIVELY_SUPPORTED, SUPPORTED, TENTATIVE_CONCERN, CONCERN, MIXED, RECOVERY_SIGNAL. Recomputable from `admitted.jsonl`.

## B. Dimension semantics

Independent. Recall does not imply application. Nợ/Có does not imply hàng tồn kho. Course view is coverage counts, not a grade.

## C. Controlled benchmark

150 cases. System D pass **1.00**. False SUPPORTED/CONCERN **0**. Insufficient accuracy **1.00**. See `learner_state_benchmark.md`.

## D. Longitudinal transitions

60 sequences, pass **1.00**.

## E. Recovery

2 neg + 1 pos → RECOVERY_SIGNAL. 2 more later pos → SUPPORTED. Negatives retained.

## F. Contradiction

Same dimension opposite outcomes → MIXED (or recovery if chronology matches). Different dimensions are not contradictions.

## G. Naturalistic

50 histories, pass **1.00**. Sparse/malformed → INSUFFICIENT.

## H. False certainty

0 false SUPPORTED, 0 false CONCERN. Latest-wins baseline false-SUPPORTED 0.27.

## I. Provenance / recompute

Provenance 1.00. Full recompute equivalence 1.00.

## J. Regression

Phase 2 58/60. Phase 3 C 90/90. Phase 4 C 130/130. Phase 5 C 100/100 + adv 16/16. Phase 6 C 120/120 + long 40 + nat 40.

## K. Next step

**Phase 8 planning that reads state estimates** (e.g. prefer VERIFY_MORE / practice where CONCERN or INSUFFICIENT) — still no SRS calendar, still no “weak student” label.

## Decision

**PHASE7_PASS_LONGITUDINAL_STATE_READY**
