# Phase 2 regression gate (run at Phase 3 close)

Frozen suite: `evals/phase2_retrieval_tests.jsonl` (60 tests).  
Command: `python scripts/phase2_eval.py`  
Production index: `data/indexes/2.0.0/` (not rebuilt).  
Phase 3 did not edit `retrieval/retrieve.py`, chunking, or the frozen tests.

## Phase2_before vs Phase2_after (hybrid)

| metric | before (Phase 2 / 2.1 baseline) | after (Phase 3 close) | delta |
|---|---|---|---|
| pass | 58/60 | 58/60 | 0 |
| pass rate | 0.9667 | 0.9667 | 0 |
| course accuracy | 1.00 | 1.00 | 0 |
| chapter accuracy | 1.00 | 1.00 | 0 |
| concept accuracy | 0.9833 | 0.9833 | 0 |
| relevant top-5 | 0.9833 | 0.9833 | 0 |
| wrong-course contamination | 0.00 | 0.00 | 0 |
| prerequisite precision | 1.00 | 1.00 | 0 |
| insufficient detection | 1.00 | 1.00 | 0 |
| fail types | wrong_concept 1, ranking_failure 1 | wrong_concept 1, ranking_failure 1 | same |

Naive remains 21/60 (0.35). Gates still pass.

## Residual Phase 2 misses (unchanged)

Documented in `retrieval_failures.md`. Not patched in Phase 3.

## Verdict

No material retrieval regression. Phase 3 is not blocked by Phase 2.
