# Phase 6 recommendation (not started)

Phase 5 implemented session-level adaptation. Do **not** automatically build long-term personalization.

## Recommended next step (one)

**Define admission rules for `SessionEvidenceSummary.candidate_long_term_evidence`.**

- Require repeated session-local `DIAGNOSIS_RESOLVED` on the same concept, or an explicit learner opt-in.
- Never admit VERIFY_MORE, self-report, or a single correct number.
- Still no percent mastery, no forgetting curve, no review calendar.

## Explicitly not next

- Spaced repetition
- Research Agent / web IFRS
- Production ingest of KTTC2 / KTCP / KTNH / Kiểm toán 1
- Permanent Adaptive Bot
- Inferring weakness from one session
