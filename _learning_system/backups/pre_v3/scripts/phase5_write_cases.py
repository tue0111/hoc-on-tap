# -*- coding: utf-8 -*-
"""Adaptive multi-turn sessions. Natural Vietnamese. Gold specified independently."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

OUT = Path(r"D:\Hoc\_learning_system\evals\adaptive_sessions.jsonl")
OUT_ADV = Path(r"D:\Hoc\_learning_system\evals\adaptive_adversarial.jsonl")

k1 = "ke-toan-tai-chinh-1"
nlkt = "nguyen-ly-ke-toan"


def S(cid, category, question, course, chapter, response, work, events, gold):
    return {
        "id": cid,
        "category": category,
        "input": {
            "question": question,
            "learner_response": response,
            "work_shown": work,
            "course_context": {"course_id": course, "chapter": chapter},
            "events": events,
        },
        "gold": gold,
    }


def G(**kw):
    d = {
        "must_not_confirm_prereq": True,
        "must_not_resolve_on_self_report": True,
        "expect_transition": True,
    }
    d.update(kw)
    return d


def main():
    cases = []

    # ---------- 30 VERIFY_MORE → clarified ----------
    fifo_q = "FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?"
    buy_q = "Mua hàng hóa nhập kho trả tiền mặt, định khoản KTTC1?"
    cash_q = "Thu tiền mặt bán hàng TK 111 KTTC1?"
    vm_specs = []
    for i in range(10):
        vm_specs.append(
            S(
                f"ad-vm-arith-{i+1:02d}",
                "verify_more_clarified",
                fifo_q,
                k1,
                3,
                "em không chắc chỗ này",
                "",
                [{"content": "em nhân 50 với 10 ra 600"}],
                G(
                    final_error_type="arithmetic_error",
                    final_action="MECHANICAL_CORRECTION",
                    overdiagnosis_recovery=True,
                    must_not_confirm_prereq=True,
                ),
            )
        )
    for i in range(8):
        vm_specs.append(
            S(
                f"ad-vm-class-{i+1:02d}",
                "verify_more_clarified",
                buy_q,
                k1,
                3,
                "em ghi 642 gì đó, không chắc",
                "",
                [{"content": "đưa vào chi phí vì trả tiền rồi, hàng hóa là chi phí"}],
                G(
                    final_error_type="classification_error",
                    final_action="CONTRASTIVE_EXAMPLE",
                    overdiagnosis_recovery=True,
                    must_not_confirm_prereq=True,
                ),
            )
        )
    for i in range(6):
        vm_specs.append(
            S(
                f"ad-vm-noco-{i+1:02d}",
                "verify_more_clarified",
                cash_q,
                k1,
                2,
                "111 với 511, không chắc bên nào",
                "",
                [{"content": "tăng thì ghi bên có, tài sản tăng ghi có"}],
                G(
                    final_error_type="prerequisite_gap",
                    final_action="PREREQUISITE_MICRO_BACKFILL",
                    overdiagnosis_recovery=True,
                    must_not_confirm_prereq=False,
                    expect_prereq=True,
                ),
            )
        )
    for i in range(6):
        vm_specs.append(
            S(
                f"ad-vm-formula-{i+1:02d}",
                "verify_more_clarified",
                fifo_q,
                k1,
                3,
                "em lấy số 10 với 12 chia gì đó",
                "",
                [{"content": "em lấy bình quân gia quyền rồi nhân"}],
                G(
                    final_error_type="formula_selection_error",
                    final_action="CONTRASTIVE_EXAMPLE",
                    overdiagnosis_recovery=True,
                    must_not_confirm_prereq=True,
                ),
            )
        )
    cases.extend(vm_specs)
    assert len(vm_specs) == 30, len(vm_specs)

    # ---------- 20 initial wrong hyp → corrected ----------
    for i in range(10):
        cases.append(
            S(
                f"ad-corr-mech-{i+1:02d}",
                "corrected_hypothesis",
                fifo_q,
                k1,
                3,
                "FIFO là lấy giá lô cuối nên em ra 600",
                "lô cuối",
                [{"content": "thôi em dùng fifo lô đầu, nhân 50 với 10 ra 600"}],
                G(
                    final_error_type="arithmetic_error",
                    final_action="MECHANICAL_CORRECTION",
                    overdiagnosis_recovery=True,
                ),
            )
        )
    for i in range(10):
        cases.append(
            S(
                f"ad-corr-class-{i+1:02d}",
                "corrected_hypothesis",
                buy_q,
                k1,
                3,
                "em đảo nợ có gì đó",
                "",
                [{"content": "không phải đảo, em để 642 vì hàng hóa là chi phí kỳ này"}],
                G(
                    final_error_type="classification_error",
                    final_action="CONTRASTIVE_EXAMPLE",
                    overdiagnosis_recovery=True,
                    must_not_confirm_prereq=True,
                ),
            )
        )

    # ---------- 15 prereq suspected → rejected ----------
    for i in range(15):
        cases.append(
            S(
                f"ad-pre-rej-{i+1:02d}",
                "prereq_rejected",
                cash_q,
                k1,
                2,
                "em ghi có 111, không chắc",
                "",
                [{"content": "tiền mặt tăng ghi nợ, em chỉ nhầm 112 thay vì 111"}],
                G(
                    final_error_type="journal_entry_error",
                    final_action="WORKED_EXAMPLE",
                    must_not_confirm_prereq=True,
                    expect_prereq=False,
                    overdiagnosis_recovery=True,
                ),
            )
        )

    # ---------- 15 prereq unconfirmed → confirmed ----------
    for i in range(15):
        cases.append(
            S(
                f"ad-pre-conf-{i+1:02d}",
                "prereq_confirmed",
                "Gửi tiền mặt vào ngân hàng (111 → 112) theo KTTC1.",
                k1,
                2,
                "em ghi ngược, chưa rõ",
                "",
                [{"content": "tài sản tăng thì ghi bên có nên em có 112"}],
                G(
                    final_error_type="prerequisite_gap",
                    final_action="PREREQUISITE_MICRO_BACKFILL",
                    must_not_confirm_prereq=False,
                    expect_prereq=True,
                    overdiagnosis_recovery=True,
                ),
            )
        )

    # ---------- 10 mechanical vs conceptual transitions ----------
    for i in range(5):
        cases.append(
            S(
                f"ad-mc-to-arith-{i+1:02d}",
                "mech_vs_concept",
                fifo_q,
                k1,
                3,
                "em nghĩ fifo sai bản chất",
                "",
                [{"content": "fifo đúng, em nhân 50 với 10 ra 600"}],
                G(
                    final_error_type="arithmetic_error",
                    final_action="MECHANICAL_CORRECTION",
                    overdiagnosis_recovery=True,
                ),
            )
        )
    for i in range(5):
        cases.append(
            S(
                f"ad-mc-to-concept-{i+1:02d}",
                "mech_vs_concept",
                fifo_q,
                k1,
                3,
                "50*10=500 nhưng fifo là lấy lô cuối",
                "ra đúng số; fifo là lô cuối",
                [{"content": "kết quả đúng nhưng fifo là lấy giá lô mới nhất"}],
                G(
                    final_error_type="conceptual_failure",
                    final_action="MECHANISM_EXPLANATION",
                    must_not_resolve=True,
                ),
            )
        )

    # ---------- 10 remaining INCONCLUSIVE ----------
    for i in range(10):
        cases.append(
            S(
                f"ad-inc-{i+1:02d}",
                "inconclusive",
                "Câu định khoản giúp với.",
                k1,
                2,
                "em không chắc",
                "",
                [
                    {"content": "chắc vậy", "event_type": "AMBIGUOUS_RESPONSE"},
                    {"content": "hình như đúng", "event_type": "SELF_REPORT"},
                    {"content": "gì đó", "event_type": "AMBIGUOUS_RESPONSE"},
                ],
                G(
                    final_error_type="unknown",
                    final_action="VERIFY_MORE",
                    expect_transition=False,
                    must_not_confirm_prereq=True,
                    must_not_resolve=True,
                    allow_inconclusive=True,
                ),
            )
        )

    assert len(cases) == 100, len(cases)

    # a few extra overdiagnosis recoveries beyond the 100 core (keep ==100)
    cats = Counter(c["category"] for c in cases)
    print("sessions", len(cases), dict(cats))
    assert cats["verify_more_clarified"] >= 30
    assert cats["corrected_hypothesis"] >= 20
    assert cats["prereq_rejected"] >= 15
    assert cats["prereq_confirmed"] >= 15
    assert cats["mech_vs_concept"] >= 10
    assert cats["inconclusive"] >= 10

    OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")

    adv = []
    adv.append(
        S(
            "adv-01-mindchange",
            "adversarial",
            cash_q,
            k1,
            2,
            "em ghi nợ 111",
            "",
            [{"content": "thôi em đổi, tăng thì ghi bên có"}],
            G(final_error_type="prerequisite_gap", final_action="PREREQUISITE_MICRO_BACKFILL", expect_prereq=True, must_not_confirm_prereq=False),
        )
    )
    adv.append(
        S(
            "adv-02-contradict",
            "adversarial",
            cash_q,
            k1,
            2,
            "không chắc bên nào",
            "",
            [{"content": "ghi nợ khi tăng"}, {"content": "tăng thì ghi bên có"}],
            G(final_action="VERIFY_MORE", allow_inconclusive=True, must_not_confirm_prereq=True, expect_transition=True, must_not_resolve=True),
        )
    )
    adv.append(
        S(
            "adv-03-copied",
            "adversarial",
            buy_q,
            k1,
            3,
            "nợ 642 vì chi phí",
            "ghi nhận vào chi phí",
            [{"content": "Nợ 156 / Có 111"}],
            G(final_error_type="classification_error", final_action="CONTRASTIVE_EXAMPLE", must_not_resolve=True),
        )
    )
    adv.append(
        S(
            "adv-04-wrong-reason",
            "adversarial",
            fifo_q,
            k1,
            3,
            "500",
            "ra đúng số",
            [{"content": "fifo là lấy giá lô mới nhất, ra đúng số 500"}],
            G(final_error_type="conceptual_failure", final_action="MECHANISM_EXPLANATION", must_not_resolve=True),
        )
    )
    adv.append(
        S(
            "adv-05-calc",
            "adversarial",
            fifo_q,
            k1,
            3,
            "em bấm máy ra 600",
            "",
            [{"content": "máy tính nhân 50 với 10 ra 600"}],
            G(final_error_type="arithmetic_error", final_action="MECHANICAL_CORRECTION", overdiagnosis_recovery=True),
        )
    )
    adv.append(
        S(
            "adv-06-hieuroi",
            "adversarial",
            buy_q,
            k1,
            3,
            "em không chắc 642 hay 156",
            "",
            [{"content": "em hiểu rồi", "event_type": "SELF_REPORT"}],
            G(final_action="VERIFY_MORE", must_not_resolve=True, must_not_confirm_prereq=True, expect_transition=False, allow_inconclusive=True),
        )
    )
    adv.append(
        S(
            "adv-07-chacvay",
            "adversarial",
            cash_q,
            k1,
            2,
            "em không chắc",
            "",
            [{"content": "chắc vậy", "event_type": "AMBIGUOUS_RESPONSE"}],
            G(final_action="VERIFY_MORE", must_not_resolve=True, allow_inconclusive=True, expect_transition=False),
        )
    )
    adv.append(
        S(
            "adv-08-other-q",
            "adversarial",
            cash_q,
            k1,
            2,
            "không chắc",
            "",
            [{"content": "thầy ơi nộp bài lúc mấy giờ"}],
            G(final_action="VERIFY_MORE", must_not_resolve=True, allow_inconclusive=True, expect_transition=False),
        )
    )
    adv.append(
        S(
            "adv-09-incomplete-je",
            "adversarial",
            buy_q,
            k1,
            3,
            "nợ 156",
            "",
            [{"content": "nợ 156 thôi, chưa có bên có"}],
            G(final_action="VERIFY_MORE", allow_inconclusive=True, must_not_confirm_prereq=True),
        )
    )
    adv.append(
        S(
            "adv-10-shorthand",
            "adversarial",
            cash_q,
            k1,
            2,
            "N111 C511",
            "",
            [{"content": "N111 C511, tăng thì ghi bên có"}],
            G(final_error_type="prerequisite_gap", final_action="PREREQUISITE_MICRO_BACKFILL", expect_prereq=True, must_not_confirm_prereq=False),
        )
    )
    adv.append(
        S(
            "adv-11-transfer-fail",
            "adversarial",
            buy_q,
            k1,
            3,
            "em hiểu rồi hàng hóa là tài sản",
            "",
            [{"content": "công ty dịch vụ cũng dùng 156 giống ví dụ bán hàng", "event_type": "RETRY_ANSWER"}],
            G(final_error_type="transfer_failure", final_action="APPLICATION_PRACTICE", must_not_resolve=True),
        )
    )
    adv.append(
        S(
            "adv-12-self-then-fail",
            "adversarial",
            fifo_q,
            k1,
            3,
            "fifo 50*10",
            "",
            [{"content": "em hiểu rồi", "event_type": "SELF_REPORT"}, {"content": "em lấy bình quân gia quyền"}],
            G(final_error_type="formula_selection_error", final_action="CONTRASTIVE_EXAMPLE", overdiagnosis_recovery=True),
        )
    )
    adv.append(
        S(
            "adv-13-empty",
            "adversarial",
            cash_q,
            k1,
            2,
            "không chắc",
            "",
            [{"content": "", "event_type": "NO_RESPONSE"}],
            G(final_action="VERIFY_MORE", must_not_resolve=True, allow_inconclusive=True, expect_transition=False),
        )
    )
    adv.append(
        S(
            "adv-14-double-arith-concept",
            "adversarial",
            fifo_q,
            k1,
            3,
            "em nhân ra 600",
            "",
            [{"content": "fifo là lô cuối nên 600"}, {"content": "em nhân 50 với 10 ra 600"}],
            G(final_error_type="arithmetic_error", final_action="MECHANICAL_CORRECTION", overdiagnosis_recovery=True),
        )
    )
    adv.append(
        S(
            "adv-15-prereq-then-reject",
            "adversarial",
            cash_q,
            k1,
            2,
            "có 111 vì tăng",
            "",
            [{"content": "tiền mặt tăng ghi nợ, lúc nãy em nói nhầm"}],
            G(final_error_type="journal_entry_error", final_action="WORKED_EXAMPLE", must_not_confirm_prereq=True, expect_prereq=False),
        )
    )
    adv.append(
        S(
            "adv-16-three-vague",
            "adversarial",
            "Giúp em câu này.",
            k1,
            2,
            "huh",
            "",
            [{"content": "gì đó"}, {"content": "chắc vậy"}, {"content": "em hiểu rồi", "event_type": "SELF_REPORT"}],
            G(final_action="VERIFY_MORE", must_not_resolve=True, allow_inconclusive=True, expect_transition=False, must_not_confirm_prereq=True),
        )
    )

    OUT_ADV.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in adv), encoding="utf-8")
    print("adversarial", len(adv))
    print("WROTE", OUT)
    print("WROTE", OUT_ADV)


if __name__ == "__main__":
    main()
