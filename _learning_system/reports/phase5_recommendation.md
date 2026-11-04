# Phase 5 / Level 6 recommendation

Phase 4 (Level 5 DECIDE) is ready as a session-local service. Do **not** start Level 6 automatically.

## Recommended next step (one)

**ADAPT: change strategy only after new evidence from the last decision’s outcome.**

- If the last action was `VERIFY_MORE` and the learner answers the discriminator, re-run Phase 3+4. That is adaptation, not a new bot.
- If `MECHANICAL_CORRECTION` succeeded, do not open a concept lesson.
- If `PREREQUISITE_MICRO_BACKFILL` was used, require a second KTTC1 observation before any further NLKT work.
- Never write a mastery score from a single `LearningDecision`.

## Explicitly not next

- Spaced repetition calendars
- Research Agent / web IFRS
- Production ingest of KTTC2 / KTCP / KTNH / Kiểm toán 1
- Persistent Decision/Adaptive Bot
- Promoting session decisions into `learner/` instance files
