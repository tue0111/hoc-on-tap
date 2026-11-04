---
name: learner-state
description: >
  Query derived per-concept × per-dimension evidence state from admitted
  observations. Use when asking what evidence currently supports, or /learner-state.
  Not a study plan. Not a mastery percentage.
---

# Learner state (Phase 7)

Derived, recomputable, disposable. Durable source is `learner/evidence/admitted.jsonl` only.

```
cd D:\Hoc\_learning_system
python -m mastery.cli recompute
python -m mastery.cli query --concept hang-ton-kho
python -m mastery.cli query --concern
python -m mastery.cli query --recovery
python -m mastery.cli query --insufficient
```

`--write` refreshes `learner/state/current_state.json` and appends `state_transitions.jsonl`.

States: INSUFFICIENT_EVIDENCE, TENTATIVELY_SUPPORTED, SUPPORTED, TENTATIVE_CONCERN, CONCERN, MIXED, RECOVERY_SIGNAL.

Confidence is estimate-confidence, not competence.

## Forbidden

- Averaging dimensions into a course/learner score
- Using HOLD/REJECT as active evidence
- Treating missing evidence as 0.0
- “Weak student” labels
- Spaced repetition / review calendar
- Choosing what to study next (use `learning-policy`)
