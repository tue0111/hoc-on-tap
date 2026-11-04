# Learner-state failures (Phase 7)

Critical: FALSE_SUPPORTED, FALSE_CONCERN, ABSENCE_EQUALS_FAILURE, DIMENSION_LEAKAGE, CONCEPT_LEAKAGE, HISTORY_ERASURE, RECENCY_FAKE_DECAY, CONTRADICTION_FLATTENING, FALSE_RECOVERY, STATE_NOT_RECOMPUTABLE.

## System D

**0 remaining fails** on 150 + 60 + 50.

## What naive aggregations get wrong

- Latest-wins: one success → SUPPORTED; recovery last-positive → SUPPORTED (misses RECOVERY_SIGNAL).
- Majority: recovery (2 neg + 1 pos) → CONCERN.
- Net count: recovery completed (2+2) → MIXED instead of SUPPORTED.

## Residual risks

1. Independence labels come from Phase 6. If production admits a retry as INDEPENDENT_TASK, Phase 7 will trust it.
2. `SUPPORTED` after two transfer successes is **evidence support**, not “mastered inventory.”
3. Empty `admitted.jsonl` yields zero concepts — that is INSUFFICIENT globally, not failure.
