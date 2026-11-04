# Admission benchmark (Phase 6)

Cases: `evals/admission_cases.jsonl` (120).  
Longitudinal: `evals/admission_longitudinal.jsonl` (40).  
Naturalistic: `evals/admission_naturalistic.jsonl` (40).  
Raw: `reports/admission_benchmark_raw.json`.

## Controlled (120)

| bucket | n |
|---|---|
| one-off mistakes | 20 |
| same-task retries | 15 |
| repeated independent errors | 20 |
| independent successes | 15 |
| self-report only | 10 |
| hinted / answer-exposed | 10 |
| correct number / wrong reason | 10 |
| contradictory clusters | 10 |
| duplicate lineage | 10 |

## Baselines vs C

| | A store everything | B repeat ignoring quality | **C policy** |
|---|---|---|---|
| pass | 0.00 | 0.08 | **1.00** |
| precision | 0.42 | 0.55 | **1.00** |
| false admission | 0.58 | 0.21 | **0.00** |
| self-report false ADMIT | 1.00 | 0.00 | **0** |
| duplicate inflation | 1.00 | 1.00 | **0** |

## Gates (System C)

| metric | C | gate |
|---|---|---|
| admission precision | 1.00 | ≥ 0.95 |
| false long-term admission | 0.00 | ≤ 0.03 |
| one-off false admission | 0.00 | ≤ 0.02 |
| self-report false admission | 0 | 0 |
| duplicate inflation | 0 | 0 |
| repeated-independent recall | 1.00 | ≥ 0.90 |
| positive-evidence recall | 1.00 | ≥ 0.90 |
| contradiction preservation | 1.00 | ≥ 0.95 |
| provenance completeness | 1.00 | 1.00 |
| HOLD appropriateness | 1.00 | — |
| admitted + / − | 25 / 25 | not negative-only |

## Longitudinal (40)

Pass 40/40: HOLD then ADMIT; error then later success keeps both; guided repeats never ADMIT; self-report stays weak; chronology preserved.

## Naturalistic (40)

Pass 40/40. False ADMIT **0**. HOLD-or-REJECT **1.00**. Vague Vietnamese and “em nhớ cái này” do not enter long-term evidence.
