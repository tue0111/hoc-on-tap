---
name: learning-decision
description: >
  Choose the single smallest next learning action from a Phase 3 DiagnosticResult.
  Use when the user asks what to study next after an error, or /learning-decision.
---
# Learning decision (Phase 4 / Level 5)

## HOC_ROOT

`HOC_ROOT` = repo root (`_grok_pack/`, `_learning_system/`). Local Windows của Tuệ: thường `D:\Hoc`.

Session-local. One action. Does not write mastery. Does not execute the lesson.

```
cd HOC_ROOT/_learning_system
python -m decision.cli "QUESTION" --response "..." --work "..." --course ke-toan-tai-chinh-1
python -m retrieval.cli decide "QUESTION" --response "..." --course ke-toan-tai-chinh-1
```

## Policy

1. Use Phase 3 root cause, not the journal symptom.
2. `PREREQUISITE_MICRO_BACKFILL` only if `prerequisite_confirmed=confirmed`.
3. KTTC1 errors stay in KTTC1 unless that confirmation exists.
4. Thin/hedged free text → `VERIFY_MORE`, even if diagnosis says conceptual.
5. Arithmetic slip → `MECHANICAL_CORRECTION`, not a concept review.
6. `persistence` is always false.

## Forbidden

- Full chapter / all-of-NLKT review
- Spaced repetition / Level 6
- Multiple simultaneous interventions
- Mastery scores
