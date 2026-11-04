# Admission failures (Phase 6)

Priority: **FALSE_LONG_TERM_ADMISSION**.

## Controlled / longitudinal / naturalistic (System C)

**0 remaining fails.** False admission 0. Self-report leakage 0. Duplicate inflation 0.

## What baselines get wrong (not C failures)

- A admits one-off mistakes, self-report, hints, and duplicates.
- B treats retries as repeats and still inflates duplicates; misses first independent successes.

## Residual risks

1. Semantic “same mechanism?” across unlike tasks is not a learned classifier; independence labels are on the candidate. Mis-tagged independence in production would be the failure mode.
2. ADMIT of a STRONG explicit false rule is an **observation**, not a trait. Downstream mastery code must not promote it.
3. Empty `admitted.jsonl` until `--persist`. Eval is dry-run.
