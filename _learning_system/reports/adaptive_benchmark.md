# Adaptive benchmark (Phase 5)

Main: `evals/adaptive_sessions.jsonl` (100).  
Adversarial (separate): `evals/adaptive_adversarial.jsonl` (16).  
Raw: `reports/adaptive_benchmark_raw.json`, `adaptive_adversarial_raw.json`.

## Composition (100)

| category | n |
|---|---|
| VERIFY_MORE → clarified | 30 |
| initial hyp corrected | 20 |
| prereq suspected → rejected | 15 |
| prereq unconfirmed → confirmed | 15 |
| mechanical vs conceptual | 10 |
| remain INCONCLUSIVE | 10 |

Vietnamese turns avoid Phase 3 cue-phrase crutches on the **first** utterance.

## Baselines vs System C

| system | pass | diagnosis trans. | decision trans. | lock-in | overdiagnosis recovery |
|---|---|---|---|---|---|
| A never revises | 0.15 | 0.15 | 0.15 | 0.85 | 0.00 |
| B rerun latest utterance only | 0.36 | 0.36 | 0.36 | 0.24 | 0.25 |
| **C stateful adapt** | **1.00** | **1.00** | **1.00** | **0.00** | **0.88** |

B cannot recover Phase 3 conceptual overcall because it has no session overlay. That is the point of Level 6.

## System C vs gates

| metric | C | gate |
|---|---|---|
| diagnosis transition | 1.00 | ≥ 0.90 |
| decision transition | 1.00 | ≥ 0.90 |
| false prerequisite confirmation | 0.00 | ≤ 0.03 |
| belief lock-in | 0.00 | ≤ 0.03 |
| premature resolution | 0.00 | ≤ 0.05 |
| unsupported HIGH | 0.00 | ≤ 0.03 |
| VERIFY_MORE loop | 0.00 | ≤ 0.03 |
| overdiagnosis recovery | 0.88 | ≥ 0.85 |
| persist_to_learner_state | false | — |

100/100 on this constructed multi-turn set is saturation of the event patterns, not a claim about unbounded chat.

## Adversarial (16, not averaged)

Pass 16/16. Covers mind-change, contradiction → INCONCLUSIVE, copied journal, correct-number/wrong-reason, calculator arithmetic, “em hiểu rồi”, “chắc vậy”, off-topic, incomplete JE, shorthand, transfer after “hiểu rồi”.
