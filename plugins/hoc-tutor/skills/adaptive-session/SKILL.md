---
name: adaptive-session
description: >
  Update a session diagnosis and decision when new learner evidence arrives.
  Use after VERIFY_MORE, a retry, or /adaptive-session.
---
# Adaptive session (Phase 5 / Level 6)

## HOC_ROOT

`HOC_ROOT` = repo root (`_grok_pack/`, `_learning_system/`). Local Windows của Tuệ: thường `D:\Hoc`.

Session-local only. `persist_to_learner_state` is always false. Not spaced repetition. Not mastery.

```
cd HOC_ROOT/_learning_system
python -m adaptive.cli "QUESTION" --response "..." --course ke-toan-tai-chinh-1 --evidence "follow-up"
python -m retrieval.cli adapt "QUESTION" --response "..." --evidence "..."
```

## Rules

1. New STRONG evidence can revise the previous diagnosis. Do not lock the first label.
2. Self-report (“em hiểu rồi”) is WEAK and does not resolve the session.
3. VERIFY_MORE is bounded to 3 discriminators, then INCONCLUSIVE.
4. Prerequisite confirmation still requires a false Nợ/Có rule, not a graph edge.
5. A correct number with wrong reasoning is not mastery and is not LEARNING_GAP_RESOLVED.
6. Do not write `learner/` instance files.
