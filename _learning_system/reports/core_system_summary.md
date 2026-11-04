# Core learning system summary (Phases 2–8)

Production slice: **Nguyên lý kế toán / ACCO1325** and **Kế toán tài chính 1 / ACCO2310**. Index `2.0.0` (810 chunks). No source edits under `D:\Hoc` course folders.

## Closed loop

```
CURRICULUM
  → RETRIEVE (Phase 2 EvidencePackage)
  → DIAGNOSE (Phase 3 DiagnosticResult, session-local)
  → DECIDE (Phase 4 one action from diagnosis)
  → SESSION ADAPT (Phase 5, new evidence revises diagnosis/decision)
  → ADMIT (Phase 6 observations only)
  → RECOMPUTE STATE (Phase 7 concept×dimension, no score)
  → SELECT NEXT ACTION (Phase 8 from state + current task)
  → NEW LEARNER BEHAVIOR → loop
```

Every downstream claim is supposed to trace to learner behavior and/or curriculum evidence. HOLD/REJECT never enter state. Phase 8 never writes state.

## What “ready” means

The core can choose **one** next learning action given a current task and admitted evidence. It cannot: schedule reviews, grade the learner, ingest new courses, or answer from web/IFRS.

## Frozen suite snapshot (rerun at Phase 8 close)

| phase | result |
|---|---|
| 2 retrieve | hybrid 58/60, contamination 0 |
| 3 diagnose | C 90/90 |
| 4 decide | C 130/130 |
| 5 adapt | C 100/100, adv 16/16 |
| 6 admit | C 120/120, long 40, nat 40, false ADMIT 0 |
| 7 state | D 150/150, long 60, nat 50 |
| 8 policy | D 180/180, closed 80, nat 60, adv 8, e2e 30 |

## Decision

**PHASE8_PASS_CORE_LEARNING_SYSTEM_READY**
