# Learner-state benchmark (Phase 7)

Cases: `evals/state_cases.jsonl` (150).  
Longitudinal: `evals/state_longitudinal.jsonl` (60).  
Naturalistic: `evals/state_naturalistic.jsonl` (50).  
Raw: `reports/learner_state_benchmark_raw.json`.

## Controlled (150)

20 each: insufficient, tentative+, supported, tentative concern, concern, mixed; 15 recovery signal; 15 recovery completed.

## Baselines vs System D

| | A latest wins | B majority | C pos−neg | **D chronology+independence** |
|---|---|---|---|---|
| pass | 0.47 | 0.50 | 0.77 | **1.00** |
| false SUPPORTED | 0.27 | 0.17 | 0.00 | **0.00** |
| recovery-signal accuracy | 0.00 | 0.00 | 0.00 | **1.00** |

Latest-wins treats a single success as SUPPORTED and a recovery’s last positive as SUPPORTED without the signal. Majority cannot express recovery.

## Gates (D)

| metric | D | gate |
|---|---|---|
| state classification | 1.00 | ≥ 0.92 |
| false SUPPORTED | 0.00 | ≤ 0.03 |
| false CONCERN | 0.00 | ≤ 0.03 |
| insufficient accuracy | 1.00 | ≥ 0.95 |
| dimension leakage | 0 | 0 |
| cross-concept leakage | 0 | 0 |
| recovery-signal accuracy | 1.00 | ≥ 0.90 |
| history preservation | 1.00 | 1.00 |
| full recompute equivalence | 1.00 | 1.00 |
| provenance completeness | 1.00 | 1.00 |

## Longitudinal (60)

Pass **60/60** including no-decay after a gap, cross-dimension split, recovery → supported.

## Naturalistic (50)

Pass **50/50**. False SUPPORTED/CONCERN **0**. Sparse/malformed histories stay INSUFFICIENT.
