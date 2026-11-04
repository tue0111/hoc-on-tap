# Phase 4 decision demonstrations

Seven live traces. `persistence` is false on every decision. Previews are one sentence, not lessons.

---

## 1. Recall → RECALL_REFRESH

**Case** `dec-rec-01`

DiagnosticResult: `DIAGNOSED` `recall_failure` on `hang-ton-kho`. `prerequisite_gap=false`.

Candidates: recall refresh · mechanism (rejected: broader than a forgotten code) · NLKT backfill (rejected: not confirmed).

**Decision.** `RECALL_REFRESH` / MICRO / MEDIUM. Scope KTTC1 ch.3.  
Preview: nhắc lại đúng một số hiệu đã dạy cho hàng tồn kho.  
Sources: `src-0062`, `src-0060`, `src-0058`.

---

## 2. Conceptual → MECHANISM_EXPLANATION

**Case** `p3-nlkt-02`

Learner: “Bên Nợ phản ánh giảm tài sản. Tăng tài sản ghi Có.”

DiagnosticResult: `conceptual_failure` on `no-co` (inside NLKT, not a “prerequisite gap”).

**Decision.** `MECHANISM_EXPLANATION` / SHORT / HIGH.  
Rejected: `PREREQUISITE_MICRO_BACKFILL`, entire-chapter review.  
Sources: `src-0106`.

---

## 3. Classification → CONTRASTIVE_EXAMPLE (not a journal drill)

**Case** `p3-kttc1-02`

Learner: `Nợ 642 / Có 331`. Ghi nhận chi phí ngay khi mua hàng hóa.

DiagnosticResult: `classification_error` on `hang-ton-kho`; journal line is secondary symptom.

**Decision.** `CONTRASTIVE_EXAMPLE` / SHORT / MEDIUM. KTTC1 ch.3.  
Rejected: `WORKED_EXAMPLE` (symptom), `PREREQUISITE_MICRO_BACKFILL`.  
Preview: đặt cạnh hàng hóa để bán vs chi phí kỳ.

---

## 4. Confirmed KTTC1 ← NLKT → PREREQUISITE_MICRO_BACKFILL

**Case** `p3-pre-01`

Learner: `Có 111 / Nợ 511 vì tăng tài sản ghi Có.`

DiagnosticResult: `prerequisite_gap` **confirmed** on `no-co`.

**Decision.** `PREREQUISITE_MICRO_BACKFILL` / MICRO / HIGH.  
Scope: error in KTTC1 ch.2; prerequisite course NLKT. Depth is the Nợ/Có asset-direction rule, not “review NLKT chapter 3.”  
Sources: `src-0061`.

---

## 5. KTTC1 error NOT sent back to NLKT

**Case** `p3-kttc1-01`

Learner: `Nợ 112 / Có 511` — nhầm tiền gửi vs tiền mặt.

DiagnosticResult: `journal_entry_error` on `tien-va-tuong-duong-tien`. `prerequisite_confirmed=rejected`.

**Decision.** `WORKED_EXAMPLE` / SHORT / MEDIUM. Course stays `ke-toan-tai-chinh-1`. `is_prerequisite=false`.  
Rejected: `PREREQUISITE_MICRO_BACKFILL`, `PROCEDURE_REHEARSAL` of full journal method.

---

## 6. Arithmetic slip → MECHANICAL_CORRECTION

**Case** `p3-mech-01`

Learner: FIFO, `50 * 10 = 600`. Tính nhầm.

DiagnosticResult: `arithmetic_error` on `pp-tinh-gia-xuat-kho`. Method named correctly.

**Decision.** `MECHANICAL_CORRECTION` / MICRO / MEDIUM.  
Rejected: `MECHANISM_EXPLANATION`, `CONTRASTIVE_EXAMPLE` (not a FIFO-vs-BQ mix-up), NLKT backfill.

---

## 7. Ambiguous free text → VERIFY_MORE

**Case** `nat-01`

Learner: “em ghi 111 với 511 gì đó, không chắc bên nào”

DiagnosticResult: Phase 3 still says `conceptual_failure` / medium (H-concept fallback).

**Decision.** `VERIFY_MORE` / LOW. Thin/hedged observation is not enough to teach.  
Do not do: teach a guessed concept; send the learner to NLKT.
