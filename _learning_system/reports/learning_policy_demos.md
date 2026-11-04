# Phase 8 demos — one next action

Live `choose()`. `persistence: false`. Not a semester plan.

## 1. Conceptual CONCERN → mechanism explanation

- **Task:** KTTC1 Ch.3, explanation, `hang-ton-kho`
- **State:** conceptual CONCERN, application SUPPORTED
- **Diagnosis:** none
- **Rejected:** chapter review, all-of-NLKT, study plan
- **Action:** `MECHANISM_EXPLANATION` SHORT on CONCEPTUAL

## 2. Application CONCERN, conceptual SUPPORTED → application practice

- **Task:** application, `hang-ton-kho`
- **State:** conceptual SUPPORTED, application CONCERN
- **Rejected:** `MECHANISM_EXPLANATION` (wrong layer)
- **Action:** `APPLICATION_PRACTICE` SHORT

## 3. INSUFFICIENT but irrelevant → CONTINUE

- **Task:** FIFO calculation
- **State:** FIFO application SUPPORTED; `khau-hao` conceptual INSUFFICIENT
- **Action:** `CONTINUE` / `NO_INTERVENTION` — missing depreciation evidence is not this task

## 4. INSUFFICIENT and required → VERIFY_MORE

- **Task:** FIFO calculation
- **State:** FIFO application INSUFFICIENT
- **Rejected:** teaching a guessed gap
- **Action:** `VERIFY_MORE` MICRO — UNKNOWN is not weakness

## 5. Relevant NLKT prerequisite CONCERN → micro-backfill

- **Task:** KTTC1 journal, `hang-ton-kho`
- **State:** HTK application INSUFFICIENT; `no-co` conceptual CONCERN
- **Curriculum:** NLKT Nợ/Có is a journal bottleneck
- **Action:** `PREREQUISITE_MICRO_BACKFILL` MICRO, `is_prerequisite=true`

## 6. Irrelevant NLKT CONCERN → stay in KTTC1

- **Task:** FIFO calculation
- **State:** FIFO application SUPPORTED; `no-co` conceptual CONCERN
- **Rejected:** backfill (calculation does not need Nợ/Có)
- **Action:** `CONTINUE` on FIFO

## 7. MIXED → targeted verification

- **Task:** application, `hang-ton-kho`
- **State:** application MIXED
- **Action:** `VERIFY_MORE` — not chapter review

## 8. RECOVERY_SIGNAL → independent confirmation

- **Task:** application, `hang-ton-kho`
- **State:** application RECOVERY_SIGNAL
- **Action:** `APPLICATION_PRACTICE` MICRO — confirm; do not restart full review; do not declare mastery

## 9. SUPPORTED → continue, not “mastered”

- **Task:** application, `hang-ton-kho`
- **State:** application and conceptual SUPPORTED
- **Action:** `CONTINUE` / `NO_INTERVENTION`. Reason states this is **not mastery**.

## 10. Historical SUPPORTED overridden by strong current diagnostic

- **Task:** application, `hang-ton-kho`
- **State:** application and conceptual SUPPORTED
- **Diagnosis:** high-confidence `conceptual_failure` (inventory as period expense)
- **Rejected:** CONTINUE because history was SUPPORTED
- **Action:** `MECHANISM_EXPLANATION` (`CURRENT_DIAGNOSTIC_OVERRIDE`)

## 11. Mechanical typo does not trigger unrelated remediation

- **Task:** FIFO calculation
- **State:** FIFO SUPPORTED; `no-co` CONCERN
- **Diagnosis:** `arithmetic_error` (50×10=600, method named)
- **Rejected:** mechanism explanation; NLKT backfill
- **Action:** `MECHANICAL_CORRECTION` MICRO

## 12. Multiple concerns → one causally highest-value action

- **Task:** application, `hang-ton-kho`
- **State:** conceptual SUPPORTED, application CONCERN, recall CONCERN
- **Recall is irrelevant to this task.**
- **Action:** `APPLICATION_PRACTICE` only
