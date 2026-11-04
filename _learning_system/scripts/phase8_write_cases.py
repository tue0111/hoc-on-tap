# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
from collections import Counter
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mastery.estimator import empty_dimension

OUT = (_SYS / "evals" / "learning_policy_cases.jsonl")
OUT_L = (_SYS / "evals" / "learning_policy_longitudinal.jsonl")
OUT_N = (_SYS / "evals" / "learning_policy_naturalistic.jsonl")
OUT_A = (_SYS / "evals" / "learning_policy_adversarial.jsonl")
OUT_E = (_SYS / "evals" / "learning_policy_e2e.jsonl")

k1 = "ke-toan-tai-chinh-1"
nlkt = "nguyen-ly-ke-toan"


def D(state, conf="HIGH"):
    d = empty_dimension()
    d["state"] = state
    d["confidence_band"] = "NONE" if state == "INSUFFICIENT_EVIDENCE" else conf
    if "SUPPORTED" in state or state in {"MIXED", "RECOVERY_SIGNAL"}:
        d["positive_evidence_refs"] = ["p1"]
    if "CONCERN" in state or state in {"MIXED", "RECOVERY_SIGNAL"}:
        d["negative_evidence_refs"] = ["n1"]
    if state in {"SUPPORTED", "CONCERN"}:
        d["independent_observation_count"] = 2
        d["confidence_band"] = "HIGH"
    return d


def concept(cid, **over):
    dims = {k: empty_dimension() for k in ("recall", "conceptual", "procedural", "application", "transfer")}
    for k, v in over.items():
        dims[k] = v
    return {"concept_id": cid, "dimensions": dims, "derivation_policy_version": "7.0.0"}


def snap(*cs):
    return {"concepts": {c["concept_id"]: c for c in cs}, "derivation_policy_version": "7.0.0"}


def R(cid, cat, ctx, state, gold, diag=None):
    return {
        "id": cid,
        "category": cat,
        "request": {
            "current_context": ctx,
            "learner_state": state,
            "current_diagnostic_result": diag,
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        },
        "gold": gold,
    }


def ctx(course, concepts, task, dim=None, ch=3):
    return {"course_id": course, "chapter": ch, "task_type": task, "current_concepts": concepts, "required_dimension": dim}


def gold(status, action, concept, dim, prereq=False, **k):
    return {"status": status, "action_type": action, "concept_id": concept, "dimension": dim, "is_prerequisite": prereq, **k}


def main():
    cases = []
    htk, noco, fifo, cash = "hang-ton-kho", "no-co", "pp-tinh-gia-xuat-kho", "tien-va-tuong-duong-tien"

    for i in range(10):
        cases.append(R(f"pol-ins-irr-{i+1:02d}", "insufficient", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("INSUFFICIENT_EVIDENCE")), concept(noco, conceptual=D("INSUFFICIENT_EVIDENCE"))), gold("VERIFY_MORE", "VERIFY_MORE", fifo, "APPLICATION")))
    for i in range(10):
        cases.append(R(f"pol-ins-irrel-{i+1:02d}", "insufficient", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED")), concept("khau-hao", conceptual=D("INSUFFICIENT_EVIDENCE"))), gold("CONTINUE", "NO_INTERVENTION", fifo, "APPLICATION")))

    for i in range(20):
        cases.append(R(f"pol-tsup-{i+1:02d}", "tentatively_supported", ctx(k1, [htk], "application"), snap(concept(htk, application=D("TENTATIVELY_SUPPORTED", "MEDIUM"))), gold("CONTINUE", "NO_INTERVENTION", htk, "APPLICATION")))

    for i in range(20):
        cases.append(R(f"pol-sup-{i+1:02d}", "supported", ctx(k1, [htk], "application"), snap(concept(htk, application=D("SUPPORTED"), conceptual=D("SUPPORTED"))), gold("CONTINUE", "NO_INTERVENTION", htk, "APPLICATION")))

    for i in range(20):
        cases.append(R(f"pol-tcon-{i+1:02d}", "tentative_concern", ctx(k1, [htk], "application"), snap(concept(htk, application=D("TENTATIVE_CONCERN", "MEDIUM"))), gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION")))

    for i in range(8):
        cases.append(R(f"pol-con-conc-{i+1:02d}", "concern", ctx(k1, [htk], "explanation"), snap(concept(htk, conceptual=D("CONCERN"), application=D("SUPPORTED"))), gold("ACTION_SELECTED", "MECHANISM_EXPLANATION", htk, "CONCEPTUAL")))
    for i in range(8):
        cases.append(R(f"pol-con-app-{i+1:02d}", "concern", ctx(k1, [htk], "application"), snap(concept(htk, conceptual=D("SUPPORTED"), application=D("CONCERN"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION", must_not_mechanism=True)))
    for i in range(5):
        cases.append(R(f"pol-con-rec-{i+1:02d}", "concern", ctx(k1, [cash], "recall", "RECALL"), snap(concept(cash, recall=D("CONCERN"), application=D("SUPPORTED"))), gold("ACTION_SELECTED", "RECALL_REFRESH", cash, "RECALL")))
    for i in range(4):
        cases.append(R(f"pol-con-rec-irrel-{i+1:02d}", "concern", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED"), recall=D("CONCERN"))), gold("CONTINUE", "NO_INTERVENTION", fifo, "APPLICATION")))

    for i in range(25):
        cases.append(R(f"pol-mix-{i+1:02d}", "mixed", ctx(k1, [htk], "application"), snap(concept(htk, application=D("MIXED", "MEDIUM"))), gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION")))

    for i in range(20):
        cases.append(R(f"pol-recov-{i+1:02d}", "recovery", ctx(k1, [htk], "application"), snap(concept(htk, application=D("RECOVERY_SIGNAL", "MEDIUM"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION", recovery=True)))

    for i in range(10):
        cases.append(R(f"pol-pre-yes-{i+1:02d}", "prereq_conflict", ctx(k1, [htk], "journal_entry", ch=3), snap(concept(htk, application=D("INSUFFICIENT_EVIDENCE")), concept(noco, conceptual=D("CONCERN"))), gold("ACTION_SELECTED", "PREREQUISITE_MICRO_BACKFILL", noco, "CONCEPTUAL", True)))
    for i in range(10):
        cases.append(R(f"pol-pre-no-{i+1:02d}", "prereq_conflict", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED")), concept(noco, conceptual=D("CONCERN"))), gold("CONTINUE", "NO_INTERVENTION", fifo, "APPLICATION", must_not_backfill=True)))
    for i in range(10):
        cases.append(R(f"pol-pre-both-{i+1:02d}", "prereq_conflict", ctx(k1, [htk], "journal_entry"), snap(concept(htk, application=D("CONCERN")), concept(noco, conceptual=D("CONCERN"))), gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION", must_not_backfill=True)))

    assert len(cases) == 180, len(cases)
    print("controlled", len(cases), Counter(c["category"] for c in cases))
    OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")

    # longitudinal policy sims: state snapshots evolving; we simulate evidence via scripted gold chain
    longs = []
    for i in range(20):
        longs.append({
            "id": f"lpol-recov-{i+1:02d}",
            "category": "recovery_loop",
            "steps": [
                {"request": R("x", "x", ctx(k1, [htk], "application"), snap(concept(htk, application=D("CONCERN"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION"))["request"], "gold": gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION")},
                {"request": R("x", "x", ctx(k1, [htk], "application"), snap(concept(htk, application=D("RECOVERY_SIGNAL", "MEDIUM"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION"))["request"], "gold": gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION")},
                {"request": R("x", "x", ctx(k1, [htk], "application"), snap(concept(htk, application=D("SUPPORTED"))), gold("CONTINUE", "NO_INTERVENTION", htk, "APPLICATION"))["request"], "gold": gold("CONTINUE", "NO_INTERVENTION", htk, "APPLICATION")},
            ],
        })
    for i in range(20):
        longs.append({
            "id": f"lpol-sup-{i+1:02d}",
            "category": "stay_supported",
            "steps": [
                {"request": R("x", "x", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED"))), {})["request"], "gold": gold("CONTINUE", "NO_INTERVENTION", fifo, "APPLICATION")},
                {"request": R("x", "x", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED"))), {})["request"], "gold": gold("CONTINUE", "NO_INTERVENTION", fifo, "APPLICATION")},
            ],
        })
    for i in range(20):
        longs.append({
            "id": f"lpol-ins-{i+1:02d}",
            "category": "gather_then_continue",
            "steps": [
                {"request": R("x", "x", ctx(k1, [cash], "application"), snap(concept(cash, application=D("INSUFFICIENT_EVIDENCE"))), {})["request"], "gold": gold("VERIFY_MORE", "VERIFY_MORE", cash, "APPLICATION")},
                {"request": R("x", "x", ctx(k1, [cash], "application"), snap(concept(cash, application=D("TENTATIVELY_SUPPORTED", "MEDIUM"))), {})["request"], "gold": gold("CONTINUE", "NO_INTERVENTION", cash, "APPLICATION")},
            ],
        })
    for i in range(20):
        longs.append({
            "id": f"lpol-pre-{i+1:02d}",
            "category": "prereq_then_current",
            "steps": [
                {"request": R("x", "x", ctx(k1, [htk], "journal_entry"), snap(concept(htk, application=D("INSUFFICIENT_EVIDENCE")), concept(noco, conceptual=D("CONCERN"))), {})["request"], "gold": gold("ACTION_SELECTED", "PREREQUISITE_MICRO_BACKFILL", noco, "CONCEPTUAL", True)},
                {"request": R("x", "x", ctx(k1, [htk], "journal_entry"), snap(concept(htk, application=D("INSUFFICIENT_EVIDENCE")), concept(noco, conceptual=D("SUPPORTED"))), {})["request"], "gold": gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION")},
            ],
        })
    assert len(longs) == 80, len(longs)
    OUT_L.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in longs), encoding="utf-8")
    print("longitudinal", len(longs))

    nats = []
    for i in range(10):
        nats.append(R(f"npol-sparse-{i+1:02d}", "naturalistic", ctx(k1, [htk], "application"), snap(concept(htk)), gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION")))
    for i in range(10):
        nats.append(R(f"npol-oldcon-{i+1:02d}", "naturalistic", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED")), concept(noco, conceptual=D("CONCERN"))), gold("CONTINUE", "NO_INTERVENTION", fifo, "APPLICATION", must_not_backfill=True)))
    for i in range(10):
        nats.append(R(f"npol-mix-{i+1:02d}", "naturalistic", ctx(k1, [htk], "application"), snap(concept(htk, application=D("MIXED", "LOW"))), gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION")))
    for i in range(10):
        nats.append(R(f"npol-recov-{i+1:02d}", "naturalistic", ctx(k1, [htk], "application"), snap(concept(htk, application=D("RECOVERY_SIGNAL", "MEDIUM"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION")))
    for i in range(5):
        nats.append(R(f"npol-vague-{i+1:02d}", "naturalistic", ctx(k1, [htk], None), snap(concept(htk, application=D("INSUFFICIENT_EVIDENCE"))), gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION")))
    for i in range(5):
        nats.append(R(f"npol-shorthand-{i+1:02d}", "naturalistic", ctx(k1, [htk], "journal_entry"), snap(concept(htk, application=D("CONCERN"), conceptual=D("SUPPORTED"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION", must_not_mechanism=True)))
    for i in range(5):
        nats.append(R(f"npol-multigap-{i+1:02d}", "naturalistic", ctx(k1, [htk], "application"), snap(concept(htk, conceptual=D("SUPPORTED"), application=D("CONCERN"), recall=D("CONCERN"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION", must_not_mechanism=True)))
    for i in range(5):
        nats.append(R(f"npol-idk-{i+1:02d}", "naturalistic", {**ctx(k1, [htk], "application"), "topic": "em không biết gì"}, snap(concept(htk)), gold("VERIFY_MORE", "VERIFY_MORE", htk, "APPLICATION")))
    assert len(nats) == 60, len(nats)
    OUT_N.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in nats), encoding="utf-8")
    print("naturalistic", len(nats))

    adv = []
    diag_c = {
        "status": "DIAGNOSED",
        "primary_error_code": "conceptual_failure",
        "target_concept": htk,
        "confidence": "high",
        "observed_failure": "Learner stated that inventory purchased for resale is period expense (TK 642) by mechanism.",
        "root_cause": {"error_type": "conceptual_failure", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "high"},
        "course_id": k1,
        "curriculum_sources": [{"source_id": "src-0062"}],
    }
    adv.append(R("advp-01-override", "adversarial", ctx(k1, [htk], "application"), snap(concept(htk, application=D("SUPPORTED"), conceptual=D("SUPPORTED"))), gold("ACTION_SELECTED", "MECHANISM_EXPLANATION", htk, "CONCEPTUAL"), diag=diag_c))
    diag_a = {
        "status": "DIAGNOSED",
        "primary_error_code": "arithmetic_error",
        "target_concept": fifo,
        "confidence": "high",
        "observed_failure": "50 x 10 = 600; method named FIFO correctly.",
        "root_cause": {"error_type": "arithmetic_error", "prerequisite_gap": False, "confidence": "high"},
        "course_id": k1,
        "curriculum_sources": [{"source_id": "src-0062"}],
    }
    adv.append(R("advp-02-typo", "adversarial", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED")), concept(noco, conceptual=D("CONCERN"))), gold("ACTION_SELECTED", "MECHANICAL_CORRECTION", fifo, "APPLICATION", must_not_backfill=True, must_not_mechanism=True), diag=diag_a))
    adv.append(R("advp-03-self", "adversarial", ctx(k1, [htk], "application"), snap(concept(htk, application=D("SUPPORTED"))), gold("CONTINUE", "NO_INTERVENTION", htk, "APPLICATION")))
    adv.append(R("advp-04-multi", "adversarial", ctx(k1, [htk], "application"), snap(concept(htk, conceptual=D("SUPPORTED"), application=D("CONCERN"), recall=D("CONCERN"))), gold("ACTION_SELECTED", "APPLICATION_PRACTICE", htk, "APPLICATION")))
    diag_ok = {
        "status": "DIAGNOSED",
        "primary_error_code": "none",
        "target_concept": htk,
        "confidence": "high",
        "observed_failure": "",
        "root_cause": {"error_type": "none", "prerequisite_gap": False, "confidence": "high"},
        "course_id": k1,
        "curriculum_sources": [{"source_id": "src-0062"}],
    }
    adv.append(R("advp-05-oldcon-nowok", "adversarial", ctx(k1, [htk], "application"), snap(concept(htk, application=D("CONCERN"))), gold("CONTINUE", "NO_INTERVENTION", htk, "APPLICATION"), diag=diag_ok))
    adv.append(R("advp-06-irrel-prereq", "adversarial", ctx(k1, [fifo], "calculation"), snap(concept(fifo, application=D("SUPPORTED")), concept(noco, conceptual=D("CONCERN"))), gold("CONTINUE", "NO_INTERVENTION", fifo, "APPLICATION", must_not_backfill=True)))
    adv.append(R("advp-07-no-evidence", "adversarial", ctx(k1, [fifo], "calculation"), snap(concept(fifo)), gold("VERIFY_MORE", "VERIFY_MORE", fifo, "APPLICATION")))
    adv.append(R("advp-08-idk", "adversarial", ctx(k1, [htk], "application"), snap(concept(htk, application=D("SUPPORTED"))), gold("CONTINUE", "NO_INTERVENTION", htk, "APPLICATION")))
    OUT_A.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in adv), encoding="utf-8")
    print("adversarial", len(adv))

    templates = [
        {
            "question": "Mua hàng hóa nhập kho trả tiền mặt, định khoản KTTC1?",
            "response": "Nợ 642 / Có 111. Ghi nhận vào chi phí ngay khi mua hàng hóa.",
            "work": "ghi nhận vào chi phí",
            "followup": "Đó là chi phí kỳ này.",
            "gold_diag": "classification_error",
            "gold_dec4": "CONTRASTIVE_EXAMPLE",
        },
        {
            "question": "FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?",
            "response": "em nhân 50 với 10 ra 600",
            "work": "50 x 10 = 600",
            "followup": "nhân nhầm ra 600 thôi, FIFO lô đầu.",
            "gold_diag": "arithmetic_error",
            "gold_dec4": "MECHANICAL_CORRECTION",
        },
        {
            "question": "KTTC1 FIFO: xuất kho lấy giá lô nào?",
            "response": "FIFO lấy giá lô nhập sau cùng.",
            "work": "lô mới nhất",
            "followup": "lấy giá sau vì hàng mới.",
            "gold_diag": "formula_selection_error",
            "gold_dec4": "CONTRASTIVE_EXAMPLE",
        },
        {
            "question": "Thu tiền mặt bán hàng KTTC1, tài khoản tiền nào?",
            "response": "Nợ 112 / Có 511. Tiền mặt cũng ghi ngân hàng.",
            "work": "112",
            "followup": "tiền mặt thì 112 cho nhanh.",
            "gold_diag": "journal_entry_error",
            "gold_dec4": "WORKED_EXAMPLE",
        },
        {
            "question": "FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?",
            "response": "500. FIFO lấy lô nhập trước 50 x 10 = 500.",
            "work": "50 x 10 = 500",
            "followup": "lô đầu 50@10.",
            "gold_diag": "none",
            "gold_dec4": "NO_INTERVENTION",
        },
        {
            "question": "Tăng tiền mặt theo NLKT ghi bên nào?",
            "response": "Tăng tài sản ghi Có. Tiền vào ghi bên phải.",
            "work": "tăng ghi Có",
            "followup": "bên Có vì tăng.",
            "gold_diag": "conceptual_failure",
            "gold_dec4": "MECHANISM_EXPLANATION",
            "course": nlkt,
            "chapter": 3,
        },
    ]
    e2e = []
    for i in range(30):
        t = templates[i % len(templates)]
        e2e.append({
            "id": f"e2e-{i+1:02d}",
            "question": t["question"],
            "course": t.get("course", k1),
            "chapter": t.get("chapter", 3),
            "response": t["response"],
            "work": t["work"],
            "followup": t["followup"],
            "gold_diag": t["gold_diag"],
            "gold_dec4": t["gold_dec4"],
            "gold_next_status": ["CONTINUE", "VERIFY_MORE", "ACTION_SELECTED", "NO_ACTION"],
        })
    OUT_E.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in e2e), encoding="utf-8")
    print("e2e", len(e2e))
    print("WROTE", OUT)


if __name__ == "__main__":
    main()
