# Phase 3 diagnostic demonstrations

Five representative traces from the live engine (`diagnose()`). Curriculum sources are Phase 2 EvidencePackage items. `persist_to_learner_state` is false on every trace.

---

## 1. NLKT misconception diagnosed on the current concept

**Case** `nlkt-02`

**Question.** Bên Nợ của tài khoản tài sản phản ánh điều gì theo NLKT?

**Learner.** Bên Nợ phản ánh giảm tài sản. Tăng tài sản ghi Có.

**Hypotheses.** `H-noco` / `conceptual_failure` on `no-co`. Not a “prerequisite gap” — the learner is inside NLKT.

**Diagnostic question.** None. The written false asset-direction rule is direct evidence.

**Eliminated.** —

**Diagnosis.** `DIAGNOSED` / high. Primary `conceptual_failure`. `prerequisite_gap=false`. `next_action_class=REVIEW_CURRENT`.

**Why.** Failure is explained on the current concept; NLKT is not “blamed” as a missing earlier course. The stated rule contradicts Bên Nợ / Bên Có as taught.

**Provenance.** `src-0106` `Nguyên lý kế toán/NLKT-C3-CD3.1-Taikhoanketoan_v2.pdf`

---

## 2. KTTC1 error diagnosed inside KTTC1 (classification, not Nợ/Có)

**Case** `mt-03` (contrastive with demo 3)

**Question.** Mua hàng hóa nhập kho trả tiền mặt, định khoản KTTC1?

**Learner.** Nợ 642 / Có 111. Ghi nhận vào chi phí ngay khi mua hàng hóa.

**Hypotheses.** `H-class` (goods treated as expense) vs `H-acct` (recording slip with correct class). NLKT Nợ/Có is **not** in the set — no false direction rule was written.

**Diagnostic question.** Đối tượng vừa mua là hàng hóa để bán hay chi phí kỳ này? Không cần định khoản.

**Learner follow-up.** Đó là chi phí kỳ này.

**Eliminated.** `H-acct`

**Diagnosis.** `DIAGNOSED` / high. Primary `classification_error` on `hang-ton-kho`. `prerequisite_gap=false`. Secondary journal line is the symptom. `next_action_class=REVIEW_CURRENT`.

**Provenance.** `src-0062` `Kế toán tài chính 1/Chương 3.pdf`; `src-0067` Slide Chương 3.

---

## 3. KTTC1 error traced to an NLKT prerequisite (only because the rule was written)

**Case** `pre-01` (same purchase/cash family as demo 2, different evidence)

**Question.** Thu tiền mặt bán hàng, định khoản KTTC1 (TK 111, 511).

**Learner.** Có 111 / Nợ 511 vì tăng tài sản ghi Có.

**Hypotheses.** `H-noco` / `prerequisite_gap` on `no-co`. The surface journal is reversed **because** the learner stated a false asset-direction rule.

**Diagnostic question.** None. Written false rule is sufficient; the engine does not ask “Bạn có hiểu Nợ/Có không?”

**Diagnosis.** `DIAGNOSED` / high. Primary `prerequisite_gap`. `prerequisite_concept_id=no-co`. `prerequisite_confirmed=confirmed`. `next_action_class=REVIEW_PREREQUISITE`.

**Why.** Root cause is a sourced NLKT mechanism, not merely a wrong KTTC1 line.

**Provenance.** `src-0061` `Kế toán tài chính 1/Chương 2.pdf` (current-course retrieve). Prerequisite relation from the concept graph (`no-co` → later KTTC1 recording).

Contrast: `mt-04` is the same purchase stem with `Có 156 / Nợ 111 vì tăng tài sản ghi Có` → also `prerequisite_gap`, not classification. Demo 2 vs demo 3 is the required root-cause contrast.

---

## 4. Mechanical mistake not diagnosed as a conceptual gap

**Case** `mt-01` (contrastive with `mt-02` / `kttc1-03`)

**Question.** FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?

**Learner.** FIFO, 50*10=600. Work: FIFO; tính nhầm; 50 * 10 = 600.

**Hypotheses.** `H-arith` vs `H-formula` (same wrong total could be a method mix-up).

**Diagnostic question.** Bạn đang dùng phương pháp giá xuất nào (FIFO, bình quân gia quyền, đích danh)? Tính lại đúng 50 đơn vị × đơn giá lô FIFO đầu tiên.

**Learner follow-up.** A. Sai vì nhầm phép tính. FIFO.

**Eliminated.** `H-formula`

**Diagnosis.** `DIAGNOSED` / high. Primary `arithmetic_error` on `pp-tinh-gia-xuat-kho`. `prerequisite_gap=false`. `next_action_class=PRACTICE_APPLICATION`.

The engine does **not** say the learner lacks FIFO or Nợ/Có. Pair `mt-02` (explicit bình quân on the same stem) is `formula_selection_error`.

**Provenance.** `src-0062` Chương 3; `src-0067` Slide Chương 3.

---

## 5. Ambiguous case returned INCONCLUSIVE

**Case** `amb-09`

**Question.** Giúp em câu này.

**Learner.** Không biết.

**Hypotheses.** None that isolate an operation.

**Diagnostic question.** None committed as a diagnosis. Next action `VERIFY_MORE`.

**Diagnosis.** `INCONCLUSIVE` / inconclusive. Primary `unknown`. `prerequisite_gap=false`. No mastery implication.

The engine is willing to say it cannot locate the failed operation. Out-of-slice items (`amb-01` TSCĐ-in-KTTC1, `amb-02` WACC, `amb-03` IFRS 15) take the same status.
