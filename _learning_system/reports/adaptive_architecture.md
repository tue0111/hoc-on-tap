# Adaptive session architecture (Phase 5 / Level 6)

Level 6 here is **session adaptation only**. A past diagnosis is a hypothesis. New evidence can revise it. Nothing is written to long-term learner mastery.

```
USER
 → RETRIEVE (Phase 2)
 → DIAGNOSE (Phase 3)
 → DECIDE (Phase 4)
 → NEW EVIDENCE?
      ├─ NO → return current action
      └─ YES → ADAPT
           → interpret event (strength STRONG/MEDIUM/WEAK)
           → update hypothesis states
           → re-diagnose if triggered
           → override Phase 3 conceptual fallback when evidence is STRONG
           → re-decide if root cause / prereq / status changed
           → continue / DIAGNOSIS_RESOLVED / INCONCLUSIVE
```

## Components

| piece | path |
|---|---|
| session | `adaptive/session.py` |
| evidence events | `adaptive/evidence.py` |
| hypothesis updater | `adaptive/updater.py` |
| triggers | `adaptive/transition.py` |
| controller | `adaptive/controller.py` |
| CLI | `python -m adaptive.cli` / `python -m retrieval.cli adapt` |
| schemas | `schemas/adaptive_session.schema.json`, `learner_evidence_event.schema.json`, `session_evidence_summary.schema.json` |

Phase 3 `diagnose()` and Phase 4 `decide()` are called as-is. They were not rebuilt.

## Evidence

Types: DIAGNOSTIC_ANSWER, RETRY_ANSWER, WORKED_STEP, EXPLANATION, CALCULATION, CLASSIFICATION_CHOICE, JOURNAL_ENTRY, CORRECTION, SELF_REPORT, NO_RESPONSE, AMBIGUOUS_RESPONSE.

Strength: STRONG (false Nợ/Có rule, arithmetic slip, expense-vs-asset claim) · MEDIUM (worked line) · WEAK (self-report, hedges). “Em hiểu rồi” is always WEAK.

## Hypothesis states

ACTIVE → SUPPORTED/WEAKENED → CONFIRMED/REJECTED. History is kept. Revival is allowed: **new evidence > previous commitment**.

## Triggers

Re-diagnose on diagnostic answers, retries, calculations, journals, strong suggested-error mismatch, prereq support/contradict. Not on SELF_REPORT / empty.

Re-decide when primary error, prereq confirmation, or INCONCLUSIVE↔DIAGNOSED changes.

VERIFY_MORE is capped at **3** discriminators, then `NEED_MORE_EVIDENCE` / INCONCLUSIVE.

## Resolution

`DIAGNOSIS_RESOLVED` = session has a confirmed cause and a teaching action.  
`LEARNING_GAP_RESOLVED` = this item looks corrected.  
Neither is “you master the concept.” `persist_to_learner_state: false`.

## Overdiagnosis recovery

Phase 3 still labels many vague turns `conceptual_failure`. Phase 4 often returns VERIFY_MORE. Phase 5, on STRONG later evidence, overrides that fallback (arithmetic, classification, confirmed Nợ/Có) without editing Phase 3.
