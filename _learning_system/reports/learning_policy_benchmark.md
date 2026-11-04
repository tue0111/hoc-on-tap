# Learning-policy benchmark (Phase 8)

Controlled **180** cases. System D = full policy. Baselines A/B/C are naive.

| mode | pass | next-action | concept | dimension | false prereq backfill | unknown-as-failure | SUPPORTED-as-mastered |
|---|---|---|---|---|---|---|---|
| A lowest-state | 0.2278 | 0.2278 | 0.9444 | 0.5889 | 0.0556 | 0.0556 | 0 |
| B prereq-first | 0.8889 | 0.8889 | 0.8889 | 0.8889 | 0.1111 | 0.0556 | 0 |
| C static APPLICATION map | 0.8167 | 0.8167 | 0.9444 | 0.8722 | 0 | 0.0556 | 0 |
| **D full policy** | **1.00** | **1.00** | **1.00** | **1.00** | **0** | **0** | **0** |

## Gates (system D)

| metric | gate | D |
|---|---|---|
| Next-action accuracy | ≥ 0.90 | 1.00 |
| Target concept | ≥ 0.95 | 1.00 |
| Target dimension | ≥ 0.95 | 1.00 |
| Prerequisite-backfill precision | ≥ 0.97 | 1.00 |
| False prerequisite-backfill | ≤ 0.02 | 0 |
| Irrelevant remediation | ≤ 0.03 | 0 |
| UNKNOWN-as-failure | 0 | 0 |
| SUPPORTED-as-mastered | 0 | 0 |
| Recovery handling | ≥ 0.90 | 1.00 |
| Minimal intervention | ≥ 0.95 | 1.00 |
| Current-diagnostic override (adversarial) | ≥ 0.95 | 1.00 |

## Where baselines fail

- **A** remediates the globally worst state (including irrelevant NLKT CONCERN and missing evidence as if it were weakness). Forces teaching on SUPPORTED/TENTATIVE.
- **B** always backfills NLKT when `no-co` is CONCERN, including FIFO calculation where Nợ/Có is not the mechanism (false backfill 0.11).
- **C** maps only current-concept APPLICATION, so conceptual CONCERN on an explanation task is missed; also cannot backfill a justified bottleneck.

## Naturalistic (60)

Pass **1.00**. Sparse history, old NLKT concern on FIFO, MIXED, recovery, vague task, journal shorthand, several gaps, “em không biết gì” without behavioral evidence → VERIFY_MORE or CONTINUE, never a guessed lesson.

## Adversarial (8)

Pass **1.00**. Override, mechanical typo, self-report, multi-concern, historical CONCERN + current success, irrelevant prereq, no evidence, “I know nothing” with SUPPORTED history.

Raw: `learning_policy_benchmark_raw.json`.
