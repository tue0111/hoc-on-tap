# Learning-policy failures (Phase 8)

## Controlled (system D)

None remaining (180/180).

## Naturalistic / adversarial

None remaining (60/60, 8/8).

## Closed loop / snapshot longitudinal

None remaining (80/80 each).

## End-to-end (30)

Chain continuity **30/30** (retrieve → diagnose → decide → adapt → admit → recompute → next). Persistence false. No SRS fields.

Live Phase 3 labels on some templates still differ from the intended gold (Phase 3 limitation, unchanged): FIFO “lô sau cùng” sometimes `unknown`; a correct FIFO item may stay `unknown`. Phase 8 in those sessions selected `VERIFY_MORE` / `NO_INTERVENTION` / `CONTINUE` rather than inventing a lesson. Classification HTK-vs-expense, FIFO arithmetic, and NLKT Nợ/Có reverse still diagnose as intended.

## Baselines (not system failures)

A 0.23, B 0.89 (false NLKT backfill), C 0.82 (misses conceptual layer and justified backfill). These remain as contrast, not production.

## Critical failure counters (D, controlled)

| class | count |
|---|---|
| SUPPORTED_EQUALS_MASTERED | 0 |
| UNKNOWN_EQUALS_WEAK | 0 |
| IRRELEVANT_REMEDIATION | 0 |
| FALSE_PREREQUISITE_BACKFILL | 0 |
| BROAD_REVIEW_OVERREACH | 0 |
| WRONG_DIMENSION_TREATMENT | 0 |
| RECOVERY_RESET_TO_FULL_REVIEW | 0 |
| SRS_FIELD | 0 |
| PERSISTENCE_TRUE | 0 |
