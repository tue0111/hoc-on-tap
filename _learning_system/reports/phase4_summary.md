# Phase 4 summary — Level 5 learning decision

Scope: NLKT + KTTC1. Index 2.0.0 unchanged. Phase 2/3 engines not rebuilt.

## A. Architecture

Deterministic policy on Phase 3 `DiagnosticResult`: causal priority, confirmed-only prerequisite backfill, current-concept-first, thin-evidence → VERIFY_MORE, one MICRO/SHORT action, no lesson execution. See `decision_architecture.md`.

## B. Controlled benchmark

130 cases. System C pass 130/130. Gates: primary gap 1.00, action 1.00, backfill precision 1.00, false backfill 0, over-treat 0, grounding 1.00, VERIFY_MORE 1.00. Baseline A 0.21; B 0.95 (static lookup leaks unconfirmed backfill and symptom treatment).

## C. Naturalistic shadow

40 conversational items, scored separately. Phase 3 DIAGNOSED 0.75 of them (conceptual fallback). Phase 4 VERIFY_MORE 0.85. False prerequisite backfill 0. Unsupported HIGH teaching 0. Six residual MECHANISM calls on complete-looking false claims.

## D. Intervention selection

Controlled action accuracy 1.00. C vs B: C refuses unconfirmed NLKT backfill and treats classification as the cause of a wrong journal.

## E. Prerequisite backfill

Confirmed-only. Precision 1.00, false rate 0.00 on both sets.

## F. Over / under-treatment

Controlled: both 0.00. Shadow over-treatment 0.00 by the mechanical/broad-review definition.

## G. VERIFY_MORE calibration

Controlled 1.00. Shadow 0.85 rate, which is the intended conservative default on hedged Vietnamese.

## H. Representative failures

Controlled: none remaining. Shadow mismatches and Phase 3 over-diagnosis: `decision_failures.md`.

## I. Phase 2 regression

Hybrid 58/60, gates unchanged. `reports/retrieval_benchmark_raw.json`.

## J. Phase 3 regression

Diagnostic C 90/90, same metrics as Phase 3 close. Frozen cases not edited.

## K. One recommended next step

Level 6 ADAPT only as **strategy change after new evidence**, still without turning one decision into mastery. First consume `VERIFY_MORE` outcomes; do not schedule SRS.

## Decision

**PHASE4_PASS_READY_FOR_LEVEL6**
