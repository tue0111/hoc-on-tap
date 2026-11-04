# Learner-state architecture (Phase 7)

Derived **evidence state**, not identity and not a grade.

```
admitted.jsonl only
  → group by concept_id × dimension
  → drop retries / hinted / self-report if they leaked into the store
  → chronology of independent CORRECT / INCORRECT
  → contradiction (same concept AND dimension)
  → state estimate
```

FULL_RECOMPUTE always rebuilds `learner/state/current_state.json` from evidence. Derived state is disposable; admitted observations are durable.

## States

| state | meaning |
|---|---|
| INSUFFICIENT_EVIDENCE | no independent admitted observations |
| TENTATIVELY_SUPPORTED | one independent positive |
| SUPPORTED | ≥2 independent positives, no unresolved later negative; or recovery confirmed |
| TENTATIVE_CONCERN | one independent negative |
| CONCERN | ≥2 independent negatives, no later independent positives |
| MIXED | both sides, not a recovery pattern |
| RECOVERY_SIGNAL | ≥2 earlier independent negatives, then one later independent positive |

Confidence = certainty of the **estimate**, not competence. SUPPORTED is never paired with LOW.

## Non-rules

- No forgetting decay
- No dimension leakage (recall ≠ application)
- No concept leakage (Nợ/Có ≠ hàng tồn kho)
- No `overall_mastery` / course percent
- HOLD/REJECT never enter the estimator
- Course view is **coverage counts**, labeled as such
