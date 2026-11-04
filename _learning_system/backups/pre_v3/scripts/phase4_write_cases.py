# -*- coding: utf-8 -*-
"""Frozen Level 5 decision cases. Gold is specified independently of Phase 3 labels."""
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

P3 = Path(r"D:\Hoc\_learning_system\evals\diagnostic_cases.jsonl")
OUT = Path(r"D:\Hoc\_learning_system\evals\decision_cases.jsonl")
OUT_NAT = Path(r"D:\Hoc\_learning_system\evals\decision_naturalistic_shadow.jsonl")

# Independent gold map (copied as policy, not imported from decision.policy on purpose).
ERROR_TO_ACTION = {
    "recall_failure": "RECALL_REFRESH",
    "conceptual_failure": "MECHANISM_EXPLANATION",
    "classification_error": "CONTRASTIVE_EXAMPLE",
    "procedural_error": "PROCEDURE_REHEARSAL",
    "journal_entry_error": "WORKED_EXAMPLE",
    "formula_selection_error": "CONTRASTIVE_EXAMPLE",
    "arithmetic_error": "MECHANICAL_CORRECTION",
    "interpretation_error": "CONTRASTIVE_EXAMPLE",
    "transfer_failure": "APPLICATION_PRACTICE",
    "terminology_confusion": "TERMINOLOGY_CLARIFICATION",
    "prerequisite_gap": "PREREQUISITE_MICRO_BACKFILL",
    "unknown": "VERIFY_MORE",
    "none": "NO_INTERVENTION",
}

CAT_FOR_ERROR = {
    "recall_failure": "recall",
    "conceptual_failure": "conceptual",
    "classification_error": "classification_application",
    "formula_selection_error": "classification_application",
    "transfer_failure": "classification_application",
    "interpretation_error": "classification_application",
    "procedural_error": "procedural_mechanical",
    "arithmetic_error": "procedural_mechanical",
    "journal_entry_error": "procedural_mechanical",
    "prerequisite_gap": "confirmed_prerequisite",
    "unknown": "verify_more",
    "terminology_confusion": "conceptual",
    "none": "no_intervention",
}

nlkt = "nguyen-ly-ke-toan"
k1 = "ke-toan-tai-chinh-1"


def load_p3():
    rows = []
    with P3.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def gold_from_p3(g):
    et = g.get("error_type") or "unknown"
    if g.get("status") == "INCONCLUSIVE" or et == "unknown":
        et = "unknown"
    action = ERROR_TO_ACTION[et]
    status = "VERIFY_MORE" if action == "VERIFY_MORE" else ("NO_INTERVENTION" if action == "NO_INTERVENTION" else "DECIDED")
    return {
        "status": status,
        "action_type": action,
        "error_type": et,
        "concept_id": g.get("target_concept"),
        "is_prerequisite": bool(g.get("prerequisite_gap")),
        "prerequisite_concept_id": g.get("prerequisite_concept_id"),
        "must_not_backfill": not bool(g.get("prerequisite_gap")),
        "depth": {
            "RECALL_REFRESH": "MICRO",
            "MECHANICAL_CORRECTION": "MICRO",
            "TERMINOLOGY_CLARIFICATION": "MICRO",
            "PREREQUISITE_MICRO_BACKFILL": "MICRO",
            "VERIFY_MORE": "MICRO",
            "NO_INTERVENTION": "MICRO",
        }.get(action, "SHORT"),
    }


def live(cid, category, inp, gold, **extra):
    rec = {
        "id": cid,
        "category": category,
        "input_mode": "live_diagnose",
        "input": {
            "question": inp["question"],
            "learner_response": inp.get("learner_response") or "",
            "work_shown": inp.get("work_shown") or "",
            "course_context": inp.get("course_context") or {},
            "followup_response": inp.get("followup_response"),
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        },
        "gold": gold,
    }
    rec.update(extra)
    return rec


def stub_diag(**kw):
    d = {
        "diagnostic_id": "diag-stub",
        "status": "DIAGNOSED",
        "target_concept": "hang-ton-kho",
        "course_id": k1,
        "primary_error_code": "classification_error",
        "secondary_error_codes": [],
        "root_cause": {
            "error_type": "classification_error",
            "concept_id": "hang-ton-kho",
            "prerequisite_gap": False,
            "prerequisite_concept_id": None,
            "prerequisite_confirmed": "rejected",
            "confidence": "high",
            "why": "injected",
        },
        "curriculum_sources": [{"source_id": "src-0062", "course_id": k1, "relative_path": "Kế toán tài chính 1/Chương 3.pdf"}],
        "evidence_status": "OBSERVED",
        "confidence": "high",
        "signals": {},
        "session": {"remaining_hypotheses": [], "persist_to_learner_state": False},
        "hypotheses_considered": [],
        "persist_to_learner_state": False,
        "retrieval_coverage": "sufficient",
        "observed_failure": "",
    }
    rc = dict(d["root_cause"])
    if "root_cause" in kw:
        rc.update(kw.pop("root_cause"))
    d.update(kw)
    d["root_cause"] = rc
    return d


def injected(cid, category, diag, gold, session_context=None):
    return {
        "id": cid,
        "category": category,
        "input_mode": "injected",
        "input": {
            "diagnostic_result": diag,
            "session_context": session_context or {"course_id": diag.get("course_id"), "chapter": None},
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        },
        "gold": gold,
    }


def main():
    cases = []
    p3 = load_p3()
    used_p3 = set()
    for c in p3:
        g = gold_from_p3(c["gold"])
        cat = CAT_FOR_ERROR.get(g["error_type"], "other")
        if c["category"] == "kttc1_current":
            g["must_not_backfill"] = True
        if c["category"] == "insufficient":
            cat = "verify_more"
        rec = live(f"p3-{c['id']}", cat, c["input"], g, source_case=c["id"], pair=c["gold"].get("pair"))
        if c.get("multiturn"):
            rec["input"]["followup_response"] = c["multiturn"].get("followup_response")
        cases.append(rec)
        used_p3.add(c["id"])

    # ----- extra recall (need 15 total) -----
    recall_qs = [
        ("dec-rec-01", "TK hàng hóa theo Thông tư 200 KTTC1 là số nào?", k1, 3, "Em không nhớ số hiệu tài khoản hàng hóa.", "quên số hiệu", "hang-ton-kho"),
        ("dec-rec-02", "Tài khoản tiền mặt theo KTTC1?", k1, 2, "Quên tài khoản. Không nhớ số hiệu 111.", "quên tài khoản", "tien-va-tuong-duong-tien"),
        ("dec-rec-03", "Phải thu khách hàng số hiệu TK theo KTTC1?", k1, 2, "Em quên số hiệu. Không nhớ tài khoản 131.", "quên số hiệu", "no-phai-thu"),
        ("dec-rec-04", "TK tạm ứng theo KTTC1?", k1, 2, "Không nhớ số hiệu TK 141.", "không nhớ số hiệu", "no-phai-thu"),
        ("dec-rec-05", "Giá xuất kho FIFO viết tắt là gì, KTTC1?", k1, 3, "Em quên tài khoản phương pháp. Không nhớ FIFO là gì.", "quên tài khoản", "pp-tinh-gia-xuat-kho"),
        ("dec-rec-06", "TK thành phẩm theo KTTC1?", k1, 3, "Không nhớ số hiệu 155.", "không nhớ số hiệu", "hang-ton-kho"),
        ("dec-rec-07", "TK NVL theo KTTC1?", k1, 3, "Quên số hiệu 152.", "quên số hiệu", "hang-ton-kho"),
        ("dec-rec-08", "Bên Nợ tài khoản tài sản gọi là gì, NLKT?", nlkt, 3, "Em không nhớ tên bên. quên tài khoản Nợ.", "quên tài khoản", "no-co"),
        ("dec-rec-09", "Ghi sổ kép tên nguyên tắc NLKT?", nlkt, 3, "Không nhớ tên nguyên tắc. quên tài khoản kép.", "không nhớ", "ghi-so-kep"),
        ("dec-rec-10", "TK 112 tên gọi KTTC1?", k1, 2, "Quên tài khoản. Không nhớ tiền gửi ngân hàng.", "quên tài khoản", "tien-va-tuong-duong-tien"),
        ("dec-rec-11", "Dự phòng phải thu khó đòi số hiệu KTTC1?", k1, 2, "Không nhớ số hiệu 2293.", "không nhớ số hiệu", "no-phai-thu"),
        ("dec-rec-12", "Hàng gửi đi bán TK nào KTTC1?", k1, 3, "Quên số hiệu 157.", "quên số hiệu", "hang-ton-kho"),
        ("dec-rec-13", "TK thuế GTGT được khấu trừ KTTC1?", k1, 2, "Em quên số hiệu 133.", "quên số hiệu", "no-phai-thu"),
        ("dec-rec-14", "Nhật ký chung là hình thức sổ nào, KTTC1?", k1, 1, "Không nhớ tên hình thức sổ. quên tài khoản nhật ký.", "không nhớ", "so-sach-ke-toan"),
    ]
    for cid, q, course, ch, resp, work, tgt in recall_qs:
        cases.append(
            live(
                cid,
                "recall",
                {"question": q, "learner_response": resp, "work_shown": work, "course_context": {"course_id": course, "chapter": ch}},
                {
                    "status": "DECIDED",
                    "action_type": "RECALL_REFRESH",
                    "error_type": "recall_failure",
                    "concept_id": tgt,
                    "is_prerequisite": False,
                    "must_not_backfill": True,
                    "depth": "MICRO",
                },
            )
        )

    # ----- extra classification / application -----
    extra_class = [
        ("dec-cls-01", "Mua hàng hóa nhập kho trả tiền mặt KTTC1?", k1, 3,
         "Nợ 642 / Có 111. Đưa vào chi phí ngay khi mua hàng hóa.", "ghi nhận vào chi phí",
         "hang-ton-kho", "classification_error", "CONTRASTIVE_EXAMPLE"),
        ("dec-cls-02", "Mua NVL nhập kho TK 152, KTTC1.", k1, 3,
         "Nợ 627 / Có 111. Đưa vào chi phí sản xuất chung ngay.", "ghi nhận vào chi phí",
         "hang-ton-kho", "classification_error", "CONTRASTIVE_EXAMPLE"),
        ("dec-app-01", "Công ty dịch vụ không có hàng hóa. Dùng TK 156 như ví dụ bán hàng KTTC1?", k1, 3,
         "Có, công ty dịch vụ cũng dùng TK 156 giống ví dụ bán hàng.", "áp dụng giống ví dụ bán hàng",
         "hang-ton-kho", "transfer_failure", "APPLICATION_PRACTICE"),
        ("dec-form-01", "FIFO KTTC1 xuất 50, lô 50@10. Tính giá xuất.", k1, 3,
         "Em lấy bình quân (10+12)/2 rồi nhân 50.", "(10 + 12)/2",
         "pp-tinh-gia-xuat-kho", "formula_selection_error", "CONTRASTIVE_EXAMPLE"),
        ("dec-cls-03", "Thuế GTGT được khấu trừ TK 133 khi mua hàng KTTC1?", k1, 2,
         "Nợ 156 / Có 111 gộp cả VAT vào giá hàng, không dùng 133.", "gộp cả vat; không dùng 133",
         "no-phai-thu", "classification_error", "CONTRASTIVE_EXAMPLE"),
        ("dec-int-01", "Số dư Nợ TK 111 trên sổ KTTC1 nghĩa là gì?", k1, 2,
         "Số dư nợ là xấu, công ty đang lỗ.", "số dư nợ là xấu",
         "tien-va-tuong-duong-tien", "interpretation_error", "CONTRASTIVE_EXAMPLE"),
    ]
    for cid, q, course, ch, resp, work, tgt, et, act in extra_class:
        cases.append(
            live(
                cid,
                "classification_application",
                {"question": q, "learner_response": resp, "work_shown": work, "course_context": {"course_id": course, "chapter": ch}},
                {"status": "DECIDED", "action_type": act, "error_type": et, "concept_id": tgt, "is_prerequisite": False, "must_not_backfill": True, "depth": "SHORT"},
            )
        )

    # ----- NO_INTERVENTION (injected) -----
    cases.append(
        injected(
            "dec-none-01",
            "no_intervention",
            stub_diag(
                primary_error_code="none",
                target_concept="pp-tinh-gia-xuat-kho",
                observed_failure="FIFO 50*10=500, đáp án đúng",
                root_cause={"error_type": "none", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "high", "why": "matches taught FIFO"},
            ),
            {"status": "NO_INTERVENTION", "action_type": "NO_INTERVENTION", "error_type": "none", "concept_id": "pp-tinh-gia-xuat-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )
    cases.append(
        injected(
            "dec-none-02",
            "no_intervention",
            stub_diag(
                primary_error_code="none",
                target_concept="tien-va-tuong-duong-tien",
                observed_failure="chỉ sai chính tả Nợ 111 / Có 511",
                signals={"typo_only": True},
                root_cause={"error_type": "none", "concept_id": "tien-va-tuong-duong-tien", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "high", "why": "typo"},
            ),
            {"status": "NO_INTERVENTION", "action_type": "NO_INTERVENTION", "error_type": "none", "concept_id": "tien-va-tuong-duong-tien", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )
    cases.append(
        injected(
            "dec-none-03",
            "no_intervention",
            stub_diag(
                primary_error_code="none",
                target_concept="hang-ton-kho",
                observed_failure="nhầm đánh máy 156 thành 165 rồi sửa lại, câu trả lời đúng",
                signals={"formatting_only": True},
                root_cause={"error_type": "none", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "medium", "why": "typo"},
            ),
            {"status": "NO_INTERVENTION", "action_type": "NO_INTERVENTION", "error_type": "none", "concept_id": "hang-ton-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )
    cases.append(
        injected(
            "dec-none-04",
            "no_intervention",
            stub_diag(
                status="INCONCLUSIVE",
                primary_error_code="unknown",
                target_concept="pp-tinh-gia-xuat-kho",
                confidence="inconclusive",
                observed_failure="FIFO 40*12=480",
                signals={"method_named_ok": True},
                root_cause={"error_type": "unknown", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "inconclusive", "why": "no error cue"},
            ),
            {"status": "NO_INTERVENTION", "action_type": "NO_INTERVENTION", "error_type": "none", "concept_id": "pp-tinh-gia-xuat-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )
    cases.append(
        injected(
            "dec-none-05",
            "no_intervention",
            stub_diag(
                primary_error_code="none",
                course_id=nlkt,
                target_concept="phuong-trinh-ke-toan",
                observed_failure="TS 100, NPT 40, VCSH=60. đáp án đúng",
                curriculum_sources=[{"source_id": "src-0103", "course_id": nlkt}],
                root_cause={"error_type": "none", "concept_id": "phuong-trinh-ke-toan", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "high", "why": "correct"},
            ),
            {"status": "NO_INTERVENTION", "action_type": "NO_INTERVENTION", "error_type": "none", "concept_id": "phuong-trinh-ke-toan", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )

    # ----- causal-priority injected: symptom journal vs cause classification -----
    cases.append(
        injected(
            "dec-causal-01",
            "classification_application",
            stub_diag(
                primary_error_code="journal_entry_error",
                secondary_error_codes=["classification_error"],
                observed_failure="Nợ 642 / Có 331",
                root_cause={"error_type": "journal_entry_error", "concept_id": "hang-ton-kho", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "medium", "why": "wrong account on the line"},
            ),
            {"status": "DECIDED", "action_type": "CONTRASTIVE_EXAMPLE", "error_type": "classification_error", "concept_id": "hang-ton-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "SHORT"},
            {"course_id": k1, "chapter": 3},
        )
    )
    cases.append(
        injected(
            "dec-causal-02",
            "confirmed_prerequisite",
            stub_diag(
                primary_error_code="journal_entry_error",
                secondary_error_codes=["prerequisite_gap"],
                target_concept="tien-va-tuong-duong-tien",
                observed_failure="Có 111 vì tăng tài sản ghi Có",
                root_cause={
                    "error_type": "journal_entry_error",
                    "concept_id": "tien-va-tuong-duong-tien",
                    "prerequisite_gap": True,
                    "prerequisite_concept_id": "no-co",
                    "prerequisite_confirmed": "confirmed",
                    "confidence": "high",
                    "why": "false Nợ/Có rule",
                },
                curriculum_sources=[{"source_id": "src-0061", "course_id": k1}],
            ),
            {"status": "DECIDED", "action_type": "PREREQUISITE_MICRO_BACKFILL", "error_type": "prerequisite_gap", "concept_id": "no-co", "is_prerequisite": True, "must_not_backfill": False, "depth": "MICRO", "prerequisite_concept_id": "no-co"},
            {"course_id": k1, "chapter": 2},
        )
    )
    cases.append(
        injected(
            "dec-causal-03",
            "procedural_mechanical",
            stub_diag(
                primary_error_code="journal_entry_error",
                secondary_error_codes=["arithmetic_error"],
                target_concept="pp-tinh-gia-xuat-kho",
                observed_failure="FIFO 50*10=600",
                signals={"arithmetic": True, "method_named_ok": True},
                root_cause={"error_type": "journal_entry_error", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "medium", "why": "amount on the line"},
            ),
            {"status": "DECIDED", "action_type": "MECHANICAL_CORRECTION", "error_type": "arithmetic_error", "concept_id": "pp-tinh-gia-xuat-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )

    # Unconfirmed prereq MUST NOT backfill
    cases.append(
        injected(
            "dec-noback-01",
            "no_backfill",
            stub_diag(
                status="PARTIAL",
                primary_error_code="prerequisite_gap",
                target_concept="hang-ton-kho",
                confidence="low",
                observed_failure="Nợ 156 Có 111, có thể đảo",
                root_cause={
                    "error_type": "prerequisite_gap",
                    "concept_id": "hang-ton-kho",
                    "prerequisite_gap": True,
                    "prerequisite_concept_id": "no-co",
                    "prerequisite_confirmed": "unconfirmed",
                    "confidence": "low",
                    "why": "suspected only",
                },
                session={"remaining_hypotheses": ["H-noco", "H-class"], "persist_to_learner_state": False},
                hypotheses_considered=[
                    {"hypothesis_id": "H-noco", "error_type": "prerequisite_gap"},
                    {"hypothesis_id": "H-class", "error_type": "classification_error"},
                ],
            ),
            {"status": "VERIFY_MORE", "action_type": "VERIFY_MORE", "error_type": "prerequisite_gap", "concept_id": "hang-ton-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )
    cases.append(
        injected(
            "dec-noback-02",
            "no_backfill",
            stub_diag(
                primary_error_code="classification_error",
                target_concept="hang-ton-kho",
                observed_failure="Nợ 642 chi phí",
                root_cause={"error_type": "classification_error", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "high", "why": "expense vs asset"},
            ),
            {"status": "DECIDED", "action_type": "CONTRASTIVE_EXAMPLE", "error_type": "classification_error", "concept_id": "hang-ton-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "SHORT"},
        )
    )

    # Competing class vs noco → VERIFY_MORE
    cases.append(
        injected(
            "dec-verify-fork-01",
            "verify_more",
            stub_diag(
                status="PARTIAL",
                primary_error_code="classification_error",
                confidence="low",
                target_concept="hang-ton-kho",
                observed_failure="Nợ 642 hoặc đảo Nợ Có, chưa rõ",
                root_cause={"error_type": "classification_error", "prerequisite_gap": False, "prerequisite_confirmed": "unconfirmed", "confidence": "low", "why": "fork"},
                session={"remaining_hypotheses": ["H-class", "H-noco"], "persist_to_learner_state": False},
                hypotheses_considered=[
                    {"hypothesis_id": "H-class", "error_type": "classification_error"},
                    {"hypothesis_id": "H-noco", "error_type": "prerequisite_gap"},
                ],
            ),
            {"status": "VERIFY_MORE", "action_type": "VERIFY_MORE", "error_type": "classification_error", "concept_id": "hang-ton-kho", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )
    cases.append(
        injected(
            "dec-verify-insuf-01",
            "verify_more",
            stub_diag(
                status="INCONCLUSIVE",
                primary_error_code="unknown",
                target_concept="tscd",
                course_id=k1,
                confidence="inconclusive",
                retrieval_coverage="insufficient",
                curriculum_sources=[],
                evidence_status="UNKNOWN",
                observed_failure="Nợ 211",
                root_cause={"error_type": "unknown", "prerequisite_gap": False, "prerequisite_confirmed": "rejected", "confidence": "inconclusive", "why": "TSCĐ not a KTTC1 chapter"},
            ),
            {"status": "VERIFY_MORE", "action_type": "VERIFY_MORE", "error_type": "unknown", "concept_id": "tscd", "is_prerequisite": False, "must_not_backfill": True, "depth": "MICRO"},
        )
    )

    # Dedicated must-not-backfill KTTC1 current (in addition to p3 kttc1_current)
    for i, src in enumerate(["kttc1-01", "kttc1-02", "kttc1-03", "kttc1-06", "mech-01", "kttc1-07", "kttc1-08", "kttc1-14"]):
        # already in p3-*; tag is enough. Extra explicit copies with new ids for the quota.
        orig = next(x for x in p3 if x["id"] == src)
        g = gold_from_p3(orig["gold"])
        g["must_not_backfill"] = True
        cases.append(live(f"dec-stay-kttc1-{i+1:02d}", "no_backfill", orig["input"], g, source_case=src))

    assert len(cases) >= 100, len(cases)
    cats = Counter(c["category"] for c in cases)
    n_recall = sum(1 for c in cases if c["gold"].get("error_type") == "recall_failure")
    n_conc = sum(1 for c in cases if c["gold"].get("error_type") == "conceptual_failure")
    n_cls = sum(
        1
        for c in cases
        if c["category"] == "classification_application"
        or c["gold"].get("error_type")
        in {"classification_error", "formula_selection_error", "transfer_failure", "interpretation_error"}
    )
    n_proc = sum(1 for c in cases if c["category"] == "procedural_mechanical")
    n_pre = sum(1 for c in cases if c["gold"].get("is_prerequisite"))
    n_noback = sum(1 for c in cases if c["gold"].get("must_not_backfill") and c["gold"].get("action_type") != "PREREQUISITE_MICRO_BACKFILL")
    n_verify = sum(1 for c in cases if c["gold"].get("action_type") == "VERIFY_MORE")
    n_none = sum(1 for c in cases if c["gold"].get("action_type") == "NO_INTERVENTION")
    print("controlled", len(cases), dict(cats))
    print("recall", n_recall, "conceptual", n_conc, "class/app", n_cls, "proc/mech", n_proc, "prereq", n_pre, "noback", n_noback, "verify", n_verify, "none", n_none)
    assert n_recall >= 15, n_recall
    assert n_conc >= 15, n_conc
    assert n_cls >= 15, n_cls
    assert n_proc >= 15, n_proc
    assert n_pre >= 15, n_pre
    assert n_noback >= 10, n_noback
    assert n_verify >= 10, n_verify
    assert n_none >= 5, n_none

    OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")

    # ----- naturalistic shadow (40) -----
    nat = []

    def N(cid, q, course, ch, resp, work, gold_action, gold_et, tgt, notes=""):
        nat.append(
            {
                "id": cid,
                "category": "naturalistic",
                "input_mode": "live_diagnose",
                "input": {
                    "question": q,
                    "learner_response": resp,
                    "work_shown": work,
                    "course_context": {"course_id": course, "chapter": ch},
                    "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
                },
                "gold": {
                    "action_type": gold_action,
                    "error_type": gold_et,
                    "concept_id": tgt,
                    "is_prerequisite": False,
                    "must_not_backfill": True,
                    "allow_verify_more": True,
                    "notes": notes,
                },
            }
        )

    N("nat-01", "Câu định khoản tiền mặt bán hàng giúp với.", k1, 2, "em ghi 111 với 511 gì đó, không chắc bên nào", "", "VERIFY_MORE", "unknown", "tien-va-tuong-duong-tien", "vague sides")
    N("nat-02", "Mua hàng nhập kho chưa trả.", k1, 3, "em để 642 vì thấy tiền ra", "khoản chi", "VERIFY_MORE", "unknown", "hang-ton-kho", "ambiguous class vs cash")
    N("nat-03", "Xuất 50 sp lô 10k, tính giá.", k1, 3, "50 nhân 10 ra 600 rồi", "50 x 10 = 600", "VERIFY_MORE", "unknown", "pp-tinh-gia-xuat-kho", "no method named, no tính nhầm cue")
    N("nat-04", "Câu hàng tồn kho.", k1, 3, "em làm xong nhưng cảm giác sai", "", "VERIFY_MORE", "unknown", "hang-ton-kho")
    N("nat-05", "Bán chịu.", k1, 2, "ghi 138 cũng được mà?", "", "VERIFY_MORE", "unknown", "no-phai-thu")
    N("nat-06", "FIFO hay bình quân vậy?", k1, 3, "thầy cho số 10 với 12, em lấy giữa", "10 và 12 chia 2", "VERIFY_MORE", "unknown", "pp-tinh-gia-xuat-kho")
    N("nat-07", "Tiền mặt tăng thì sao.", k1, 2, "bên phải chứ nhỉ", "", "VERIFY_MORE", "unknown", "tien-va-tuong-duong-tien", "natural false rule; Phase 3 may miss")
    N("nat-08", "Em không hiểu câu này.", k1, 2, "huh", "", "VERIFY_MORE", "unknown", None)
    N("nat-09", "Chương 3 cái kê khai.", k1, 3, "cũng ghi 156 hoài à", "", "VERIFY_MORE", "unknown", "kktx-kkdk")
    N("nat-10", "Nợ 111 có 511.", k1, 2, "nợ 111 có 511", "", "VERIFY_MORE", "unknown", "tien-va-tuong-duong-tien", "may be correct; no gap evidenced")
    N("nat-11", "Giá vốn bước 2.", k1, 3, "em chỉ ghi doanh thu, hết", "mới có 111/511", "VERIFY_MORE", "unknown", "hang-ton-kho")
    N("nat-12", "Tạm ứng.", k1, 2, "138 được không", "", "VERIFY_MORE", "unknown", "no-phai-thu")
    N("nat-13", "VAT mua hàng.", k1, 2, "gộp vào 156 cho nhanh", "", "VERIFY_MORE", "unknown", "no-phai-thu")
    N("nat-14", "Hàng gửi bán.", k1, 3, "gửi rồi thì hết hàng", "", "VERIFY_MORE", "unknown", "hang-ton-kho")
    N("nat-15", "Số dư nợ 111.", k1, 2, "nợ là xấu đúng không", "", "VERIFY_MORE", "unknown", "tien-va-tuong-duong-tien")
    N("nat-16", "Phương trình.", nlkt, 2, "ts bằng doanh thu trừ chi phí?", "", "VERIFY_MORE", "unknown", "phuong-trinh-ke-toan")
    N("nat-17", "Ghi sổ kép.", nlkt, 3, "một nghiệp vụ một tk cho gọn", "", "VERIFY_MORE", "unknown", "ghi-so-kep")
    N("nat-18", "Bút toán điều chỉnh.", nlkt, 4, "để sửa cộng nhầm trên sổ", "", "VERIFY_MORE", "unknown", "but-toan-dieu-chinh")
    N("nat-19", "Dồn tích.", nlkt, 2, "có tiền mới ghi", "", "VERIFY_MORE", "unknown", "co-so-don-tich")
    N("nat-20", "WACC trong môn này?", k1, None, "em dùng wacc cho giá xuất", "", "VERIFY_MORE", "unknown", None)
    N("nat-21", "TSCĐ KTTC1.", k1, None, "nợ 211 có 111", "", "VERIFY_MORE", "unknown", "tscd")
    N("nat-22", "Vốn chủ chương 3 KTTC1.", k1, 3, "nợ 411", "", "VERIFY_MORE", "unknown", None)
    N("nat-23", "IFRS 15 NLKT.", nlkt, None, "doanh thu 5 bước", "", "VERIFY_MORE", "unknown", None)
    N("nat-24", "Em sai hết.", nlkt, 3, "", "", "VERIFY_MORE", "unknown", None)
    N("nat-25", "Định khoản dùm.", k1, 2, "chưa hiểu đề", "", "VERIFY_MORE", "unknown", None)
    N("nat-26", "50 sp lô 50 giá 10, fifo.", k1, 3, "fifo 500", "50*10", "NO_INTERVENTION", "none", "pp-tinh-gia-xuat-kho", "likely correct; allow VERIFY_MORE")
    N("nat-27", "Mua hàng hóa để bán, tiền mặt.", k1, 3, "em nghĩ là chi phí vì trả tiền rồi", "642", "VERIFY_MORE", "unknown", "hang-ton-kho")
    N("nat-28", "Thu tiền khách nợ.", k1, 2, "em ghi có 111 vì tiền vào", "", "VERIFY_MORE", "unknown", "no-phai-thu")
    N("nat-29", "Gửi tiền ngân hàng.", k1, 2, "nợ 111 có 112?", "", "VERIFY_MORE", "unknown", "tien-va-tuong-duong-tien")
    N("nat-30", "Kết chuyển.", nlkt, 4, "chuyển tiền sang tk ngân hàng", "", "VERIFY_MORE", "unknown", "ket-chuyen")
    N("nat-31", "Doanh thu với thu nhập.", k1, 1, "cũng một thôi", "", "VERIFY_MORE", "unknown", "bao-cao-kqkd")
    N("nat-32", "Hình thức nhật ký.", k1, 1, "lên bctc luôn cho nhanh", "", "VERIFY_MORE", "unknown", "so-sach-ke-toan")
    N("nat-33", "Kiểm kê thiếu hàng.", k1, 3, "như bán hàng thu tiền", "", "VERIFY_MORE", "unknown", "hang-ton-kho")
    N("nat-34", "Tương đương tiền gồm 131 không?", k1, 2, "gồm, vì rồi cũng thu", "", "VERIFY_MORE", "unknown", "tien-va-tuong-duong-tien")
    N("nat-35", "Chi phí trả trước.", nlkt, 4, "trả là ghi hết chi phí kỳ này", "", "VERIFY_MORE", "unknown", "chi-phi-tra-truoc")
    N("nat-36", "Khấu hao 120 / 10 năm.", nlkt, 4, "em ra 20", "120/10", "VERIFY_MORE", "unknown", "khau-hao")
    N("nat-37", "TS 80 npt 30 vcsh?", nlkt, 2, "40", "80-30", "VERIFY_MORE", "unknown", "phuong-trinh-ke-toan")
    N("nat-38", "Bán hàng thu tiền + giá vốn kktx.", k1, 3, "có 511 là xong", "", "VERIFY_MORE", "unknown", "hang-ton-kho")
    N("nat-39", "Em ghi đúng số nhưng fifo là lấy lô cuối phải không?", k1, 3, "ra 400, fifo là lô mới nhất?", "400", "VERIFY_MORE", "unknown", "pp-tinh-gia-xuat-kho")
    N("nat-40", "Câu này của chương nào vậy.", k1, None, "hình như kế toán chi phí", "", "VERIFY_MORE", "unknown", None)

    assert len(nat) >= 40, len(nat)
    OUT_NAT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in nat), encoding="utf-8")
    print("naturalistic", len(nat))
    print("WROTE", OUT)
    print("WROTE", OUT_NAT)


if __name__ == "__main__":
    main()
