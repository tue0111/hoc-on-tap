# Phase 5 adaptive demonstrations

Eight live traces. `persist_to_learner_state: false` on every session.

---

## 1. VERIFY_MORE → current-concept classification (overdiagnosis recovery)

**ad-vm-class-01**

Initial: “em ghi 642 gì đó, không chắc” → Phase 3 `conceptual_failure`, Phase 4 `VERIFY_MORE`.

Evidence: “đưa vào chi phí vì trả tiền rồi, hàng hóa là chi phí” (STRONG).

H-class CONFIRMED; H-noco REJECTED.

**Adapted.** `classification_error` → `CONTRASTIVE_EXAMPLE`. Status `DIAGNOSIS_RESOLVED` (session-local).

---

## 2. VERIFY_MORE → mechanical error

**ad-vm-arith-01**

Initial: “em không chắc chỗ này” on FIFO 50@10 → `VERIFY_MORE`.

Evidence: “em nhân 50 với 10 ra 600”.

**Adapted.** `arithmetic_error` → `MECHANICAL_CORRECTION`. H-concept REJECTED.

---

## 3. NLKT prerequisite suspected → rejected

**ad-pre-rej-01**

Initial vague Có 111 → `VERIFY_MORE` (not a confirmed gap).

Evidence: “tiền mặt tăng ghi nợ, em chỉ nhầm 112 thay vì 111”.

H-noco REJECTED; H-acct CONFIRMED.

**Adapted.** `journal_entry_error` → `WORKED_EXAMPLE`. Stays in KTTC1.

---

## 4. NLKT unconfirmed → confirmed

**ad-pre-conf-01**

Initial “em ghi ngược, chưa rõ” → `VERIFY_MORE`.

Evidence: “tài sản tăng thì ghi bên có nên em có 112”.

**Adapted.** `prerequisite_gap` confirmed `no-co` → `PREREQUISITE_MICRO_BACKFILL` (micro rule, not all of NLKT).

---

## 5. Initial hypothesis corrected by later work

**ad-corr-mech-01**

Initial “FIFO là lấy giá lô cuối nên em ra 600” under-specified → `VERIFY_MORE`/`unknown`.

Evidence: “thôi em dùng fifo lô đầu, nhân 50 với 10 ra 600”.

**Adapted.** `arithmetic_error` → `MECHANICAL_CORRECTION`. Previous conceptual reading dropped.

---

## 6. Correct number, wrong reason — not resolved

**adv-04-wrong-reason**

“500” with “fifo là lấy giá lô mới nhất”.

Stays `conceptual_failure` / `MECHANISM_EXPLANATION`. Status ACTIVE, `resolution_kind=None`. Correct figure ≠ mastery.

---

## 7. “Em hiểu rồi” does not resolve

**adv-06-hieuroi**

VERIFY_MORE, then self-report.

No re-diagnosis. Status remains `NEED_MORE_EVIDENCE`. Weak evidence cannot close the session.

---

## 8. Contradictory Nợ/Có evidence → INCONCLUSIVE

**adv-02-contradict**

“ghi nợ khi tăng” then “tăng thì ghi bên có”.

Both STRONG, opposite directions. System does not average and does not confirm a prerequisite gap. `VERIFY_MORE` / `INCONCLUSIVE`.
