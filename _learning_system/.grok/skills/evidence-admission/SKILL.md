---
name: evidence-admission
description: >
  Decide whether session evidence may enter long-term learner memory.
  Use after a session summary or /evidence-admission. Never writes mastery scores.
---

# Evidence admission (Phase 6)

Store **observations with provenance**, not “user is weak” or percentages.

```
cd D:\Hoc\_learning_system
python -m admission.cli --candidate-json path.json
```

`--persist` writes ADMIT rows to `learner/evidence/admitted.jsonl` and always appends `admission_log.jsonl`.

## Decisions

- **ADMIT** — independent repeated error, independent unhinted success, or a STRONG explicit false rule as an observation
- **HOLD** — one ordinary mistake, inconclusive/vague, split dimensions
- **REJECT** — self-report, hinted/copied success, same-task retry, duplicate lineage, conceptual claim from a typo

## Forbidden

- Mastery scores, SRS, “poor fundamentals”
- Admitting “em hiểu rồi”
- Counting retries as independent
- Editing past admitted rows
