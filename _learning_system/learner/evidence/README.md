# Long-term learner evidence (Phase 6)

Append-only observation store. **Not mastery.**

- `admitted.jsonl` — ADMIT only
- `held.jsonl` — HOLD candidates
- `admission_log.jsonl` — every decision
- `conflicts.jsonl` — contradiction links

Policy version is recorded on every write (`admission_policy_version` 1.0.0).
Do not edit past rows. Do not store “user is weak” judgments.
