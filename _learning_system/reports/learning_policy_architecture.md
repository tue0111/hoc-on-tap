# Learning-policy architecture (Phase 8)

Longitudinal **next-action** policy. Not a study calendar. Does not write learner state.

```
current task / learning context
  + curriculum concept relationships
  + Phase 7 concept×dimension state (admitted evidence only)
  + optional live Phase 3–5 DiagnosticResult
        ↓
identify relevant learning need
        ↓
one AdaptiveLearningAction
        ↓
learner behavior → Phase 5 session evidence
        → Phase 6 admission
        → Phase 7 recompute
        → Phase 8 again
```

Phase 4 decides from a **current DiagnosticResult** (local remediation).
Phase 8 decides from **longitudinal state** plus the current task (cross-session policy). Phase 8 may call Phase 4 when a live diagnosis is strong.

## Components

| piece | path |
|---|---|
| request/action schemas | `schemas/adaptive_learning_request.schema.json`, `adaptive_learning_action.schema.json` |
| lexicographic priority | `learning_policy/priority.py` |
| prerequisite guard | `learning_policy/prerequisite.py` |
| engine | `learning_policy/engine.py` (`choose`) |
| CLI | `python -m learning_policy.cli` / `python -m retrieval.cli next` |

Policy version **8.0.0**. `persistence` is always `false`.

## Priority (ordered rules, no numeric weights)

1. Strong current diagnostic error (high/medium, not `none`/`unknown`) outranks historical SUPPORTED.
2. Arithmetic/typo → `MECHANICAL_CORRECTION` only; does not overturn concept state.
3. Current item success (`error_type=none`) → `CONTINUE`; historical CONCERN is not a permanent weakness; this success is not mastery.
4. Prerequisite micro-backfill only if curriculum edge **and** relevant dimension concern/confirmed gap **and** the current task needs that mechanism.
5. Both current-concept concern and NLKT concern, causal role unclear → `VERIFY_MORE` (do not auto-blame NLKT).
6. Irrelevant dimensions (e.g. recall CONCERN on a FIFO calculation) are ignored.
7. `INSUFFICIENT_EVIDENCE` on a required dim → `VERIFY_MORE`, not a lesson. Irrelevant insufficient → `CONTINUE`.
8. Among remaining relevant needs: CONCERN > TENTATIVE_CONCERN > RECOVERY_SIGNAL > MIXED, then lowest confirmed failure layer (conceptual → procedural → application → transfer → recall).

## Action taxonomy

Reuse Phase 4: `RECALL_REFRESH`, `MECHANISM_EXPLANATION`, `CONTRASTIVE_EXAMPLE`, `WORKED_EXAMPLE`, `PROCEDURE_REHEARSAL`, `APPLICATION_PRACTICE`, `PREREQUISITE_MICRO_BACKFILL`, `TERMINOLOGY_CLARIFICATION`, `MECHANICAL_CORRECTION`, `VERIFY_MORE`, `NO_INTERVENTION`.

Status: `ACTION_SELECTED | VERIFY_MORE | CONTINUE | NO_ACTION`.

Forbidden: entire-chapter review, all-of-NLKT, study plans, SRS fields (`next_review_date`, `interval_days`, `ease_factor`, `forgetting_probability`, `review_due`).

## Prerequisite (KTTC1 current-concept-first)

Backfill NLKT (`no-co`, `ghi-so-kep`, `dinh-khoan`, `tai-khoan-ke-toan`, `phuong-trinh-ke-toan`) only for journal-like tasks (`journal_entry`, `procedure`, `classification`) or inventory/receivable/cash **recording** tasks. FIFO **calculation** does not require Nợ/Có. Historical NLKT CONCERN alone is not enough.

## Non-rules

- SUPPORTED ≠ mastered
- INSUFFICIENT_EVIDENCE ≠ weak
- CONCERN ≠ permanent identity
- RECOVERY_SIGNAL ≠ restart from mechanism
- HOLD/REJECT evidence never used
- Phase 8 never writes `admitted.jsonl` or `current_state.json`
