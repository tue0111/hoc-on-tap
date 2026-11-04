# Phase 3 summary — Level 4 diagnostic vertical slice

Scope: Nguyên lý kế toán (ACCO1325) + Kế toán tài chính 1 (ACCO2310).  
Production retrieval remains hybrid index **2.0.0**. Phase 2 was not rebuilt.

## A. What was implemented

- Typed `DiagnosticRequest` / `DiagnosticSession` / `DiagnosticResult`.
- Deterministic diagnostic engine: signals → competing hypotheses → optional discriminator → confidence band.
- Session-local state only (`persist_to_learner_state: false`).
- Learning Director Diagnostic Mode (`retrieval.director.handle`, `python -m retrieval.cli diagnose`, `python -m diagnostic.cli`).
- Controlled benchmark: 90 cases (19 NLKT, 26 KTTC1 current, 19 KTTC1←NLKT, 14 mechanical, 12 insufficient), 20 multiturn, contrastive pairs.
- Baselines A (correction) vs B (single-shot) vs C (hypothesis + question).
- Phase 2 frozen suite re-run as a regression gate.

Not implemented (by design): mastery scores, Level 5 policy, Level 6, SRS, Research Agent, web accounting, KTTC2/KTCP/KTNH/Kiểm toán 1 production ingest.

## B. Benchmark composition

See `diagnostic_benchmark.md`. 90 constructed, curriculum-grounded items. Minimums met.

## C. Root-cause performance (System C)

Target concept 1.00. Root-cause 1.00. Symptom-as-root-cause 0.00.

## D. Prerequisite-gap performance

Precision 1.00. Recall 1.00 (19/19 confirmed-rule items).

## E. False-gap behavior

False prerequisite-gap rate **0.00**. Unconfirmed NLKT blame is refused.

## F. Multi-turn diagnostic quality

23 cases received one discriminating question. Contrastive FIFO arith vs formula, and classification vs Nợ/Có, diagnose differently. Confirmed written rules do not force a quiz.

## G. Representative failures

No remaining System C fails on this set. Build-time misses and residual risks: `diagnostic_failures.md`.

## H. Phase 2 regression

Hybrid 58/60 before and after. Gates unchanged. `phase2_regression_phase3.md`.

## I. Architecture changes

New `diagnostic/` package and schemas. Director mode switch. No Phase 2 retrieval architecture change. LLM hooks exist but are off for reproducible eval.

## J. One recommended next step

**Level 5 DECIDE on session diagnostic artifacts** — which single gap to treat — without turning one diagnosis into permanent mastery. Do not auto-build it from this report.

## Decision

**PHASE3_PASS_READY_FOR_LEVEL5**
