# Adaptive failures (Phase 5)

Tracked: `BELIEF_LOCK_IN`, `OVER_UPDATE`, `UNDER_UPDATE`, `FALSE_PREREQUISITE_CONFIRMATION`, `PREMATURE_RESOLUTION`, `VERIFY_MORE_LOOP`, `SELF_REPORT_OVERWEIGHT`, `CORRECT_ANSWER_EQUALS_MASTERY_ERROR`, `CONTRADICTORY_STATE`.

## Main set (System C)

**0 remaining fails** on 100 sessions.

## Adversarial

**0 remaining fails** on 16 after one build-time miss:

| id | class | cause | fix |
|---|---|---|---|
| adv-15-prereq-then-reject | BELIEF_LOCK_IN | Learner retracted a false direction (“tiền tăng ghi Nợ”) but Phase 3 stayed conceptual | session-aware: correct Nợ/Có + prior Có 111 → `journal_entry_error`, not a concept lecture |

## Residual risks

1. Overdiagnosis recovery is 0.88, not 1.00: some recovery-tagged items never started as conceptual/VERIFY_MORE, so they do not count as “recovered overcalls.”
2. Adaptive STRONG patterns are still regexes. Unseen slang can UNDER_UPDATE; that should become VERIFY_MORE, not a confirmed NLKT gap.
3. `DIAGNOSIS_RESOLVED` is session-local. Promoting it into `learner/` would be a Phase 6 policy error.
4. Phase 2/3/4 engines were not patched to chase this benchmark.
