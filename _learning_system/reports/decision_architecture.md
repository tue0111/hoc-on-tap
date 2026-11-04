# Decision architecture (Phase 4 / Level 5)

## Goal

Given a grounded Phase 3 `DiagnosticResult`, choose the **single smallest** next learning action. Not: what content could be taught. Not: execute the lesson.

```
DiagnosticResult
  → validate
  → NO_INTERVENTION (no gap / typo / correct)
  → thin/hedged observation → VERIFY_MORE
  → unresolved class-vs-Nợ/Có fork → VERIFY_MORE
  → causal-priority (upstream cause over journal symptom)
  → prerequisite guard (confirmed only)
  → current-concept-first for KTTC1
  → error → action policy
  → minimality (MICRO/SHORT)
  → LearningDecision
```

## Components

| piece | path |
|---|---|
| request/result schemas | `schemas/learning_decision_request.schema.json`, `learning_decision.schema.json` |
| taxonomy | `decision/action_taxonomy.py` |
| policy | `decision/policy.py` |
| guards | `decision/selector.py` |
| engine | `decision/engine.py` |
| preview | `decision/preview.py` (one sentence, not a lesson) |
| CLI | `python -m decision.cli` / `python -m retrieval.cli decide` |

Phase 2 `retrieve()` and Phase 3 `diagnose()` are called as dependencies. They were not rebuilt.

## Action taxonomy (closed)

`RECALL_REFRESH` · `MECHANISM_EXPLANATION` · `CONTRASTIVE_EXAMPLE` · `WORKED_EXAMPLE` · `PROCEDURE_REHEARSAL` · `APPLICATION_PRACTICE` · `PREREQUISITE_MICRO_BACKFILL` · `TERMINOLOGY_CLARIFICATION` · `MECHANICAL_CORRECTION` · `VERIFY_MORE` · `NO_INTERVENTION`

Forbidden: entire-chapter review, all-of-NLKT, study plans, SRS, multi-gap bundles.

## Prerequisite backfill

Only when Phase 3 `prerequisite_gap=true` **and** `prerequisite_confirmed=confirmed`. Graph membership is not a gap. Unconfirmed suspicion → `VERIFY_MORE`.

## Thin-evidence guard

Phase 3 may label vague free text as `conceptual_failure` (H-concept fallback). Phase 4 does not teach from that unless a specific error signal or a complete false claim is present. Hedged Vietnamese (`không chắc`, `gì đó`, `nhỉ`) → `VERIFY_MORE`.

## Persistence

`persistence: false` always. One diagnosis is not mastery. Level 6 is not started from this layer.
