---
name: diagnostic-question
description: >
  Ask or classify a diagnostic item using the error taxonomy without inventing
  mastery scores. Use when the user wants to test understanding, asks why an
  answer is wrong, or runs /diagnostic-question.
---

# Diagnostic question (Phase 3 / Level 4)

Session-local diagnosis only. Do not write mastery numbers or update `learner/` instance files.

## Mode switch

- No learner attempt → teach/retrieve (`python -m retrieval.cli retrieve "QUESTION"`).
- Learner error, wrong journal, wrong reasoning, “không hiểu”, partial work, or correct number / wrong reason → Diagnostic Mode:

```
cd D:\Hoc\_learning_system
python -m diagnostic.cli "QUESTION" --response "..." --work "..." --course ke-toan-tai-chinh-1
python -m retrieval.cli diagnose "QUESTION" --response "..." --work "..." --course ke-toan-tai-chinh-1
```

## Workflow (deterministic engine)

1. Parse the observed error. Do not treat a wrong journal as the root cause.
2. Identify the target concept (the object the operation operationalizes).
3. Retrieve Phase 2 EvidencePackage (NLKT + KTTC1 only). If coverage is insufficient → `INCONCLUSIVE`.
4. Build a small competing hypothesis set from `learner/error_taxonomy.yaml`.
5. Diagnose immediately when evidence is exclusive (arithmetic slip, written false Nợ/Có rule).
6. Otherwise ask one discriminating question. 2–3 only if required. Never “Bạn có hiểu Nợ/Có không?”
7. Update session-local evidence. `persist_to_learner_state` is always false.
8. Return `DIAGNOSED | PARTIAL | INCONCLUSIVE` with confidence band high/medium/low/inconclusive.

## KTTC1 → NLKT backtrace

Check the current KTTC1 concept first. Blame NLKT `prerequisite_gap` only with a written false Nợ/Có rule or a discriminating follow-up. One KTTC1 mistake is not “you forgot the fundamentals.”

## Output

Fill `schemas/diagnostic_result.schema.json`. `next_action_class` is coarse only (`NONE | REVIEW_CURRENT | REVIEW_PREREQUISITE | PRACTICE_APPLICATION | VERIFY_MORE`). Do not prescribe a study plan.

## Forbidden

- “You are 40% on journal entries” without attempts.
- Treating missing homework files as failure.
- Web/IFRS injection.
- Expanding production retrieval past NLKT + KTTC1.
- Permanent learner_state writes.
