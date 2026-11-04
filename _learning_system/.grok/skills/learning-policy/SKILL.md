---
name: learning-policy
description: >
  Choose the single highest-value next learning action from current task,
  curriculum relations, and Phase 7 concept×dimension state. Use when asking
  what to do next given evidence, or /learning-policy. Not a study calendar.
  Not a mastery percentage. Distinct from /learning-decision (Phase 4, live diagnosis only).
---

# Learning policy (Phase 8)

Cross-session. One action. Does not write learner state. Does not schedule reviews.

```
cd D:\Hoc\_learning_system
python -m learning_policy.cli --course ke-toan-tai-chinh-1 --concept hang-ton-kho --task-type application
python -m retrieval.cli next --course ke-toan-tai-chinh-1 --concept hang-ton-kho --task-type journal_entry
python -m learning_policy.cli --request-json path.json
```

Reads `learner/state/current_state.json` unless `--request-json` supplies a snapshot.

## Policy

1. Live strong diagnosis outranks historical SUPPORTED for that error.
2. Arithmetic/typo → `MECHANICAL_CORRECTION` only.
3. `INSUFFICIENT_EVIDENCE` is not weakness; gather evidence if the task needs it, else CONTINUE.
4. `PREREQUISITE_MICRO_BACKFILL` only if the edge is curriculum-supported, the prereq dimension shows concern (or confirmed diagnostic gap), and the current task needs that mechanism.
5. KTTC1 stays in KTTC1 unless that NLKT backfill is justified. FIFO calculation does not auto-backfill Nợ/Có.
6. RECOVERY_SIGNAL → small independent confirmation, not full review, not mastery.
7. SUPPORTED → CONTINUE the current task; never “mastered forever”.
8. `persistence` is always false.

## Forbidden

- Spaced repetition / review dates / forgetting curves
- Global mastery % / weak-strong labels
- Multi-item study plans
- Teaching from missing evidence
- Writing `admitted.jsonl` or `current_state.json` from this action
