# Diagnostic benchmark (Phase 3)

Cases: `evals/diagnostic_cases.jsonl` (90). Multiturn overlay: `evals/diagnostic_multiturn.jsonl` (20).  
Rubric: `evals/diagnostic_rubric.yaml`.  
Raw: `reports/diagnostic_benchmark_raw.json`.  
Command: `python scripts/phase3_eval.py`

## Composition (controlled, curriculum-grounded)

| category | n | intent |
|---|---|---|
| nlkt_current | 19 | current-concept errors inside NLKT |
| kttc1_current | 26 | current-concept errors inside KTTC1 (do **not** blame NLKT) |
| kttc1_prereq_nlkt | 19 | KTTC1 surface error caused by a written false Nợ/Có rule |
| mechanical | 14 | arithmetic/procedural; conceptual knowledge is not the problem |
| insufficient | 12 | out of slice, empty work, or no object to diagnose |
| **total** | **90** | ≥70 required |

Contrastive pairs (same surface, different root cause):

- FIFO `50*10=600`: arithmetic (`mt-01` / `mech-01`) vs bình quân formula (`mt-02` / `kttc1-03`)
- Wrong `Nợ 642` purchase: classification (`mt-03`) vs reversed Nợ/Có (`mt-04`)

20 cases carry a simulated follow-up. System C asked a diagnostic question on **23** cases (including contrastive mechanical/classification items). Confirmed Nợ/Có rules diagnose immediately and do not force a quiz turn.

These cases are **constructed with explicit error phrases** from the NLKT+KTTC1 corpus. They test the pipeline, not naturalistic handwriting. 100% here is saturation of that controlled set.

## Baselines

| system | meaning | pass | target | root-cause | false prereq | questions |
|---|---|---|---|---|---|---|
| A | immediate correction, no diagnosis | 0/90 | 0.53 | 0.00 | 0.00 | 0 |
| B | single-shot root-cause, no question | 90/90 | 1.00 | 1.00 | 0.00 | 0 |
| **C** | hypotheses → optional question → update | **90/90** | **1.00** | **1.00** | **0.00** | **23** |

A never identifies why the learner is wrong. That is the point of the architecture.

B and C match on this set because most gold labels are already in the written work. C’s measurable value is **discrimination**: it asks a question when arith vs formula or class vs account remain, and it still refuses false NLKT blame.

## System C vs gates

| metric | C | gate | result |
|---|---|---|---|
| target concept accuracy | 1.00 | ≥ 0.90 | PASS |
| root-cause accuracy | 1.00 | ≥ 0.80 | PASS |
| prerequisite-gap precision | 1.00 | ≥ 0.90 | PASS |
| prerequisite-gap recall | 1.00 | — | 19/19 |
| false prerequisite-gap rate | 0.00 | ≤ 0.05 | PASS |
| evidence-grounded diagnosis | 1.00 | ≥ 0.95 | PASS |
| insufficient/inconclusive detection | 1.00 | ≥ 0.85 | PASS |
| symptom-as-root-cause rate | 0.00 | — | 0 |
| wrong-course contamination | 0.00 | — | 0 |
| premature diagnosis rate | 0.00 | — | 0 |
| avg diagnostic turns | 1.256 | — | — |
| Phase 2 retrieval | 58/60 unchanged | no material regression | PASS |

## Diagnostic question rubric

Templates scored against `evals/diagnostic_rubric.yaml`:

| template | relevance | discrimination | grounding | minimality | no leak | verdict |
|---|---|---|---|---|---|---|
| dq-noco-vs-acct | pass | pass | Nợ/Có, tiền mặt | one item | pass | pass |
| dq-arith-vs-formula | pass | pass | FIFO / BQ | one item | mild number cue | pass |
| dq-class-vs-acct | pass | pass | hàng hóa vs chi phí | one item | pass | pass |
| dq-class-vs-noco | pass | pass | Bảng CĐKT | one item | pass | pass |
| dq-generic-split | pass | pass | A/B/C | one item | pass | pass |
| dq-need-work | pass | weak | object/direction | one item | pass | pass |

None match fail_if (“Bạn có hiểu Nợ/Có không?”, “explain everything”, mastery scores). Majority pass.

## What the numbers do **not** mean

Do not read 1.00 as naturalistic learner-log performance. Free-text without the cue phrases (`tăng tài sản ghi Có`, `tính nhầm`, `nhầm thuật ngữ`) will fall through to `PARTIAL` / `INCONCLUSIVE` unless `diagnostic/llm_hooks.py` is enabled later. That conservatism is intended.
