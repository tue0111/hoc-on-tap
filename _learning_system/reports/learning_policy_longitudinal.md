# Longitudinal policy simulation (Phase 8)

Does **not** bypass Phase 6 admission or Phase 7 recompute.

## Snapshot chains (80)

Pre-built Phase 7 snapshots → `choose()`. Pass **80/80**.

| category | n | expected path |
|---|---|---|
| recovery_loop | 20 | CONCERN → practice; RECOVERY_SIGNAL → confirmation; SUPPORTED → CONTINUE |
| stay_supported | 20 | CONTINUE, CONTINUE (not “mastered”) |
| gather_then_continue | 20 | INSUFFICIENT → VERIFY_MORE; TENTATIVELY_SUPPORTED → CONTINUE |
| prereq_then_current | 20 | NLKT CONCERN + current INSUFFICIENT → micro-backfill; then NLKT SUPPORTED → VERIFY current |

## Closed loop (80) — admit → recompute → choose

Each step builds `LongTermEvidenceCandidate`s, calls `decide_admission`, keeps only ADMIT rows, `recompute()`, then `choose()`.

Pass **80/80**.

Recovery example (20 replicates):

1. Two independent INCORRECT (STRONG, explicit false rule) → ADMIT → APPLICATION CONCERN → `APPLICATION_PRACTICE`
2. One independent CORRECT → ADMIT → `RECOVERY_SIGNAL` → small confirmation (`APPLICATION_PRACTICE`, MICRO)
3. Second independent CORRECT → ADMIT → `SUPPORTED` → `CONTINUE` / `NO_INTERVENTION`

Prerequisite example (20 replicates):

1. Two independent NLKT `no-co` CONCEPTUAL INCORRECT → ADMIT → KTTC1 journal on `hang-ton-kho` with no current evidence → `PREREQUISITE_MICRO_BACKFILL`
2. Two independent NLKT CORRECT → ADMIT → current still INSUFFICIENT → `VERIFY_MORE` (not another backfill)

HOLD/REJECT rows never entered the estimator. Phase 8 wrote no state files.
