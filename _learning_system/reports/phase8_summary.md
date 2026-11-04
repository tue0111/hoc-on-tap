# Phase 8 summary — longitudinal adaptive learning policy

NLKT + KTTC1. One next action from current task + curriculum relations + Phase 7 state. No SRS, no calendar, no global mastery score.

## A. Adaptive policy architecture

Lexicographic policy in `learning_policy/`. Strong live diagnosis > historical state. Arithmetic stays mechanical. Current success does not full-review CONCERN and is not mastery. See `learning_policy_architecture.md`.

## B. State → action semantics

State is one input. Dimension × task relevance × prerequisite necessity × confidence × live diagnosis decide. CONCERN does not map to “review chapter”. INSUFFICIENT does not map to “teach”. SUPPORTED does not map to “mastered / skip forever”.

## C. Controlled benchmark

180 cases. System D pass **1.00** on next action, concept, dimension. False NLKT backfill **0**. UNKNOWN-as-failure **0**. SUPPORTED-as-mastered **0**. Baselines A 0.23 / B 0.89 / C 0.82.

## D. Longitudinal closed-loop simulation

80 snapshot chains **1.00**. 80 admit→recompute→choose loops **1.00** (recovery, stay-supported, gather-then-continue, prereq-then-current). Phase 6/7 not bypassed.

## E. Naturalistic results

60/60. Prefer VERIFY_MORE / CONTINUE over unsupported intervention.

## F. Prerequisite behavior

Precision **1.00**. False backfill **0**. Journal + NLKT CONCERN + current INSUFFICIENT → micro-backfill. FIFO calculation + NLKT CONCERN → stay in KTTC1. Both-concern → VERIFY_MORE.

## G. Dimension targeting

Conceptual CONCERN → mechanism. Application CONCERN with conceptual SUPPORTED → practice, not re-teach. Irrelevant recall CONCERN ignored.

## H. Recovery handling

RECOVERY_SIGNAL → MICRO confirmation practice. Closed loop: CONCERN → RECOVERY_SIGNAL → SUPPORTED → CONTINUE. Accuracy **1.00**.

## I. Over-remediation behavior

Irrelevant insufficient ignored. SUPPORTED continues. Mechanical typo does not backfill NLKT. Minimal-intervention **1.00**.

## J. 30 end-to-end sessions

30/30 chain: question → retrieve → diagnose → decide → adapt → admit → recompute → next. Persistence false. Downstream action cites state and/or live diagnosis.

## K. Prior-phase regression

Phase 2 hybrid 58/60, contamination 0. Phase 3 C 90/90. Phase 4 C 130/130, nat VERIFY_MORE 0.85. Phase 5 C 100/100, adv 16/16. Phase 6 C 120/120, long 40, nat 40. Phase 7 D 150/150, long 60, nat 50. No material regression.

## L. Core system status

**PHASE8_PASS_CORE_LEARNING_SYSTEM_READY**

## M. Recommended next step (exactly one)

**Use the frozen core on real NLKT/KTTC1 study sessions** (retrieve → diagnose → decide → adapt → admit → recompute → next). Do not start SRS, KTTC2 ingest, or a Research Agent until that usage produces new evidenced gaps.
