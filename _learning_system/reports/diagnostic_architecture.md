# Diagnostic architecture (Phase 3 / Level 4)

## Goal

Given a learner answer, journal, reasoning, or “I don’t understand”, identify **why** they are wrong. Not: restate the correct answer.

```
observed error
  → target concept (object the operation operationalizes)
  → required knowledge + sourced prerequisites
  → competing hypotheses
  → Phase 2 EvidencePackage
  → one discriminating question if needed
  → hypothesis elimination
  → root-cause estimate or INCONCLUSIVE
```

## Components

| piece | path | role |
|---|---|---|
| request/session/result schemas | `schemas/diagnostic_*.schema.json` | typed contracts |
| signals | `diagnostic/signals.py` | deterministic error cues |
| hypotheses | `diagnostic/hypotheses.py` | small ranked competing set |
| question selector | `diagnostic/questions.py` | one discriminator, no quiz marathon |
| session state | `diagnostic/session_state.py` | session-local only |
| engine | `diagnostic/engine.py` | state machine, confidence bands |
| LLM slots | `diagnostic/llm_hooks.py` | off by default (`DIAGNOSTIC_LLM`) |
| CLI | `python -m diagnostic.cli` / `python -m retrieval.cli diagnose` | Director Diagnostic Mode |
| error codes | `learner/error_taxonomy.yaml` | unchanged; no new class added |

Deterministic code owns schema validation, state transitions, confidence bands, session tracking, and metrics. Model reasoning is an optional hook and must not mutate workflow status.

## Director mode switch

- No learner attempt → retrieve/teach (`retrieval.director.answer`).
- Learner response or work shown → `retrieval.director.handle` → `diagnose()`.

No persistent Diagnostic Bot.

## Symptom vs root cause

A wrong journal line is a **symptom**. Primary error is the failed operation (classification, Nợ/Có rule, arithmetic, …). `journal_entry_error` is used when the account/object is wrong and a deeper class/rule failure is not evidenced. It may appear as `secondary_error_codes`.

## KTTC1 → NLKT backtrace

1. Can current KTTC1 knowledge explain the failure? If yes, stay in KTTC1.
2. Prerequisite_gap only if the learner wrote a false Nợ/Có / asset-direction rule, or a discriminating follow-up confirmed it.
3. Otherwise `prerequisite_confirmed = unconfirmed` and the engine will not emit `prerequisite_gap`.
4. One KTTC1 mistake is never “you forgot the fundamentals.”

## Confidence bands

Not fabricated decimals.

| band | when |
|---|---|
| high | one remaining hypothesis and (exclusive signal or confirmed rule or discriminating test) |
| medium | one remaining hypothesis without a test |
| low | alternatives remain |
| inconclusive | no discriminating evidence, out of slice, or unknown |

Status: `DIAGNOSED` (high/medium), `PARTIAL` (low / alternatives remain), `INCONCLUSIVE`.

## `next_action_class`

Coarse only: `NONE | REVIEW_CURRENT | REVIEW_PREREQUISITE | PRACTICE_APPLICATION | VERIFY_MORE`. Not a teaching policy.

## Persistence

`persist_to_learner_state: false` always. Session may later become a Phase 5 evidence artifact; Phase 3 does not admit it into mastery.

## Retrieval boundary

Calls Phase 2 `retrieve()` hybrid index 2.0.0. Does not rebuild chunks or expand the production slice past NLKT + KTTC1.
