# Admission architecture (Phase 6)

Long-term memory stores **evidence**, not conclusions. Policy version **1.0.0**.

```
session candidate
  → provenance?
  → duplicate lineage?
  → self-report?
  → mechanical-only conceptual claim?
  → inconclusive / weak?
  → same-task retry?
  → hint / answer exposed?
  → split correct-number / wrong-reason dimensions
  → independent repeated error or unhinted success?
  → ADMIT | HOLD | REJECT
```

ADMIT writes `learner/evidence/admitted.jsonl` (append-only) and `admission_log.jsonl`.  
HOLD writes `held.jsonl`. REJECT is logged only. Past rows are never edited.

`admission_scope` is always `OBSERVATION_ONLY`. Forbidden inferences (“weak at Nợ/Có”, “mastery 42%”) are attached as `do_not_infer`.

## Independence

`SAME_TASK_RETRY` does not count. `INDEPENDENT_TASK` and `CROSS_CONTEXT_TRANSFER` do. One ordinary mistake → HOLD. Two independent mistakes on the same concept+dimension → ADMIT those observations.

## Positive vs negative

Unhinted independent success is admissible. Hinted/copied success is REJECT as independent knowledge evidence. Memory is not failure-only.

## Contradictions

Later independent success does not delete an earlier admitted error. Both remain; `conflicts.jsonl` records `contradicts`. Recovery is **not** declared here.
