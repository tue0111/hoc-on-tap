# -*- coding: utf-8 -*-
"""Level 4 diagnostic engine. Session-local. Curriculum-grounded via Phase 2 retrieve()."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from diagnostic.hypotheses import build_hypotheses
from diagnostic.questions import apply_followup, select_question
from diagnostic.session_state import new_session
import re

from diagnostic.signals import extract_signals, infer_task, normalize_course
from retrieval.textutil import fold
from retrieval.concepts import detect_query_concepts, prerequisite_concepts
from retrieval.retrieve import retrieve

ALLOWED = {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"}


def _band(n_remaining: int, exclusive: bool, tested: bool, prereq: bool, confirmed_rule: bool) -> str:
    if n_remaining == 0:
        return "inconclusive"
    if n_remaining == 1 and (exclusive or tested or confirmed_rule):
        return "high"
    if n_remaining == 1:
        return "medium"
    if prereq and not confirmed_rule and not tested:
        return "low"
    return "low"


def _next_action(error_type: str | None, prereq: bool, status: str) -> str:
    if status == "INCONCLUSIVE":
        return "VERIFY_MORE"
    if prereq:
        return "REVIEW_PREREQUISITE"
    if error_type in {"arithmetic_error", "procedural_error", "journal_entry_error"}:
        return "PRACTICE_APPLICATION"
    if error_type in {"conceptual_failure", "classification_error", "terminology_confusion", "recall_failure"}:
        return "REVIEW_CURRENT"
    return "NONE"


def diagnose(request: dict, followup_response: str | None = None, allow_question: bool = True) -> dict:
    q = request.get("question") or ""
    ctx = request.get("course_context") or {}
    course = normalize_course(ctx.get("course_id"))
    resp = request.get("learner_response") or ""
    work = request.get("work_shown") or ""
    followup = followup_response if followup_response is not None else request.get("followup_response")

    task = infer_task(q)
    concepts = detect_query_concepts(q)
    if ctx.get("topic"):
        extra = detect_query_concepts(str(ctx.get("topic")))
        for c in extra:
            if c not in concepts:
                concepts.append(c)
    target = concepts[0] if concepts else None
    qf = fold(q)
    pinned = None
    # Surface operation vs underlying concept: pin the object the item operationalizes.
    # Inventory valuation / movement beats perpetual-vs-periodic, which otherwise steals
    # "kê khai thường xuyên" items that are actually about giá vốn / xuất kho.
    if re.search(r"fifo|bình quân|giá xuất|đích danh", qf):
        pinned = "pp-tinh-gia-xuat-kho"
    elif re.search(r"giá vốn|xuất kho|nhập kho|\bhtk\b|hàng gửi", qf):
        pinned = "hang-ton-kho"
    elif re.search(r"kê khai|kiểm kê định kỳ", qf):
        pinned = "kktx-kkdk"
    elif re.search(r"phải thu|tạm ứng|bán chịu|\b131\b|\b141\b|\b2293\b|\b133\b", qf):
        pinned = "no-phai-thu"
    elif re.search(r"hàng hóa|tồn kho|thành phẩm|nguyên vật liệu", qf):
        pinned = "hang-ton-kho"
    elif re.search(r"trình bày tiền|tiền mặt|tiền gửi|tương đương tiền|xuất quỹ|về quỹ|\b111\b|\b112\b", qf):
        pinned = "tien-va-tuong-duong-tien"
    elif re.search(r"ghi sổ kép", qf):
        pinned = "ghi-so-kep"
    elif re.search(r"bên nợ|nợ/có|nợ có", qf):
        pinned = "no-co"
    elif re.search(r"phương trình kế toán|\bvcsh\b", qf) and re.search(
        r"phương trình|\bvcsh\b|\bts\b|tài sản", qf
    ):
        pinned = "phuong-trinh-ke-toan"
    elif re.search(r"bút toán điều chỉnh", qf):
        pinned = "but-toan-dieu-chinh"
    elif re.search(r"kết chuyển", qf):
        pinned = "ket-chuyen"
    elif re.search(r"chi phí trả trước", qf):
        pinned = "chi-phi-tra-truoc"
    elif re.search(r"bản chất của kế toán|khái niệm kế toán", qf):
        pinned = "ke-toan-he-thong-thong-tin"
    elif re.search(r"lĩnh vực kế toán", qf):
        pinned = "linh-vuc-ke-toan"
    elif re.search(r"nhật ký chung|sổ sách", qf):
        pinned = "so-sach-ke-toan"
    elif re.search(r"doanh thu", qf):
        pinned = "bao-cao-kqkd"
    elif re.search(r"khấu hao", qf):
        pinned = "khau-hao"
    if pinned:
        target = pinned
        if pinned not in concepts:
            concepts = [pinned] + concepts
    else:
        for preferred in (
            "hang-ton-kho",
            "tien-va-tuong-duong-tien",
            "no-phai-thu",
            "pp-tinh-gia-xuat-kho",
            "kktx-kkdk",
            "ghi-so-kep",
            "no-co",
            "phuong-trinh-ke-toan",
        ):
            if preferred in concepts:
                target = preferred
                break

    filters = {}
    if course in ALLOWED:
        filters["course_id"] = course
    if ctx.get("chapter") is not None:
        filters["chapter"] = ctx["chapter"]
    pkg = retrieve(q, filters=filters or None, system="hybrid")
    retrieval_coverage = pkg.get("coverage")
    curriculum_sources = [
        {"source_id": it.get("source_id"), "relative_path": it.get("relative_path"), "course_id": it.get("course_id")}
        for it in (pkg.get("items") or [])[:5]
    ]

    signals = extract_signals(q, resp, work)
    # scope guard: do not diagnose TSCĐ as a KTTC1 current concept
    if retrieval_coverage == "insufficient" and (
        signals.get("out_of_scope") or (course == "ke-toan-tai-chinh-1" and "tscd" in (concepts or []))
    ):
        return _inconclusive(
            q, course, target, task, pkg, curriculum_sources, "curriculum evidence insufficient or outside production slice"
        )

    if signals.get("out_of_scope"):
        return _inconclusive(
            q, course, target, task, pkg, curriculum_sources, "topic outside NLKT/KTTC1 production slice or not taught as a KTTC1 chapter"
        )

    hypotheses = build_hypotheses(task, target, course, signals)
    remaining = list(hypotheses)
    rejected = []
    questions = []
    tested = False
    confirmed_rule = bool(signals.get("reversed_dc_rule"))
    if len(remaining) == 1 and remaining[0]["error_type"] == "unknown":
        return _inconclusive(q, course, target, task, pkg, curriculum_sources, "no discriminating learner evidence")

    # Written false Nợ/Có rule is direct evidence. Do not ask a follow-up that
    # can dilute a confirmed prerequisite/current-concept rule into PARTIAL.
    if confirmed_rule and any(h["hypothesis_id"] == "H-noco" for h in remaining):
        rejected.extend([h for h in remaining if h["hypothesis_id"] != "H-noco"])
        remaining = [h for h in remaining if h["hypothesis_id"] == "H-noco"]

    qspec = select_question(remaining) if allow_question else None
    if len(remaining) == 1:
        qspec = None
    if confirmed_rule and any(h["error_type"] == "prerequisite_gap" for h in remaining):
        qspec = None

    if qspec and allow_question:
        questions.append({"id": qspec["template_id"], "text": qspec["text"]})
        if followup:
            remaining, newly = apply_followup(remaining, qspec, followup)
            rejected.extend(newly)
            tested = True
        # Do not abort into PARTIAL-only. Rank the current top so a single-shot
        # diagnosis remains available; the question is attached when still needed.

    # If still many remaining after followup, inconclusive-ish partial
    if not remaining:
        remaining = [h for h in hypotheses if h["hypothesis_id"] not in {x["hypothesis_id"] for x in rejected}] or hypotheses

    rank = {
        "arithmetic_error": 0,
        "formula_selection_error": 1,
        "prerequisite_gap": 2,
        "classification_error": 3,
        "recall_failure": 4,
        "terminology_confusion": 5,
        "procedural_error": 6,
        "transfer_failure": 7,
        "interpretation_error": 8,
        "journal_entry_error": 9,
        "conceptual_failure": 10,
        "unknown": 20,
    }
    remaining.sort(key=lambda h: (0 if h.get("exclusive") else 1, rank.get(h["error_type"], 15)))
    top = remaining[0]

    # Premature NLKT blame guard
    prereq_gap = bool(top.get("prerequisite_concept_id") or top["error_type"] == "prerequisite_gap")
    if prereq_gap:
        if course != "ke-toan-tai-chinh-1":
            # NLKT current-concept conceptual failure, not a "gap" into another course
            if top["error_type"] == "prerequisite_gap":
                top = dict(top)
                top["error_type"] = "conceptual_failure"
                top["prerequisite_concept_id"] = None
            prereq_gap = False
        elif not (confirmed_rule or tested):
            prereq_gap = False
            top = dict(top)
            top["error_type"] = "conceptual_failure"
            top["prerequisite_confirmed"] = "unconfirmed"

    # Graph check
    prereq_rel = "ok"
    if prereq_gap:
        edges = prerequisite_concepts([target] if target else [], course)
        if top.get("prerequisite_concept_id") and top["prerequisite_concept_id"] not in edges and "no-co" not in edges:
            prereq_rel = "PREREQUISITE_RELATION_UNCERTAIN"

    n = len(remaining)
    exclusive = bool(top.get("exclusive"))
    conf = _band(n, exclusive, tested, prereq_gap, confirmed_rule)
    if top["error_type"] == "unknown" and (signals.get("no_answer") or signals.get("confusion_only")):
        return _inconclusive(q, course, target, task, pkg, curriculum_sources, "no discriminating learner evidence")

    status = "DIAGNOSED" if conf in {"high", "medium"} and top["error_type"] != "unknown" else "PARTIAL"
    if conf == "low" and n > 1:
        status = "PARTIAL"
    if top["error_type"] == "unknown":
        status = "INCONCLUSIVE"
        conf = "inconclusive"

    secondary = []
    if prereq_gap:
        secondary.append("journal_entry_error" if task == "journal_entry" else "conceptual_failure")
    elif top["error_type"] == "classification_error" and task == "journal_entry":
        secondary.append("journal_entry_error")

    why = top.get("evidence_for") or ""
    if prereq_gap:
        why = "Root cause is a sourced NLKT mechanism (not merely a wrong KTTC1 line). " + why
    else:
        why = "Failure is explained on the current concept/operation; NLKT is not blamed. " + why

    session = new_session(
        target_concept=target,
        course_id=course,
        hypotheses=hypotheses,
        questions_asked=questions,
        eliminated=[h["hypothesis_id"] for h in rejected],
        remaining=[h["hypothesis_id"] for h in remaining],
        diagnosis={"status": status, "error_type": top["error_type"], "prerequisite_gap": prereq_gap},
        confidence=conf,
    )
    session_id = session["session_id"]
    result = {
        "diagnostic_id": f"diag-{uuid.uuid4().hex[:12]}",
        "attempt_id": request.get("request_id"),
        "session_id": session_id,
        "learner_id": None,
        "status": status,
        "target_concept": target,
        "course_id": course,
        "concept_ids": concepts,
        "observed_failure": (resp or work or "")[:400],
        "task_type": task,
        "primary_error_code": top["error_type"],
        "secondary_error_codes": secondary,
        "root_cause": {
            "error_type": top["error_type"],
            "concept_id": top.get("concept_id"),
            "prerequisite_gap": prereq_gap,
            "prerequisite_concept_id": top.get("prerequisite_concept_id") if prereq_gap else None,
            "prerequisite_confirmed": "confirmed" if prereq_gap and (confirmed_rule or tested) else ("unconfirmed" if top.get("prerequisite_concept_id") else "rejected"),
            "confidence": conf,
            "why": why,
        },
        "prerequisite_gaps": (
            [
                {
                    "concept_id": top.get("prerequisite_concept_id"),
                    "edge_evidence": "explicit" if prereq_rel == "ok" else "inferred",
                    "confidence": conf,
                }
            ]
            if prereq_gap
            else []
        ),
        "evidence": curriculum_sources,
        "hypotheses_considered": hypotheses,
        "hypotheses_rejected": rejected,
        "diagnostic_questions": questions,
        "curriculum_sources": curriculum_sources,
        "unknowns": ([] if prereq_rel == "ok" else [prereq_rel]),
        "next_action_class": _next_action(top["error_type"], prereq_gap, status),
        "why": why,
        "suggested_review": [{"concept_id": target, "source_ids": [s["source_id"] for s in curriculum_sources], "reason": "current concept"}]
        if target
        else [],
        "decide_hook": {"gap_to_treat": None, "strategy": None},
        "adapt_hook": {"strategy_change": None, "trigger_evidence_ids": []},
        "evidence_status": "OBSERVED" if curriculum_sources else "UNKNOWN",
        "confidence": conf,
        "persist_to_learner_state": False,
        "retrieval_coverage": retrieval_coverage,
        "signals": {k: v for k, v in signals.items() if v},
        "session": session,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return result


def _inconclusive(q, course, target, task, pkg, sources, reason):
    return {
        "diagnostic_id": f"diag-{uuid.uuid4().hex[:12]}",
        "attempt_id": None,
        "session_id": f"dsess-{uuid.uuid4().hex[:12]}",
        "status": "INCONCLUSIVE",
        "target_concept": target,
        "course_id": course,
        "concept_ids": [target] if target else [],
        "observed_failure": reason,
        "task_type": task,
        "primary_error_code": "unknown",
        "secondary_error_codes": [],
        "root_cause": {
            "error_type": "unknown",
            "concept_id": target,
            "prerequisite_gap": False,
            "prerequisite_concept_id": None,
            "prerequisite_confirmed": "rejected",
            "confidence": "inconclusive",
            "why": reason,
        },
        "prerequisite_gaps": [],
        "evidence": sources,
        "hypotheses_considered": [],
        "hypotheses_rejected": [],
        "diagnostic_questions": [],
        "curriculum_sources": sources,
        "unknowns": [reason],
        "next_action_class": "VERIFY_MORE",
        "why": reason,
        "suggested_review": [],
        "decide_hook": {"gap_to_treat": None, "strategy": None},
        "adapt_hook": {"strategy_change": None, "trigger_evidence_ids": []},
        "evidence_status": "UNKNOWN" if not sources else "OBSERVED",
        "confidence": "inconclusive",
        "persist_to_learner_state": False,
        "retrieval_coverage": pkg.get("coverage"),
        "signals": {},
        "session": {"persist_to_learner_state": False},
    }


def _partial(q, course, target, task, pkg, sources, hypotheses, remaining, rejected, questions, signals):
    return {
        "diagnostic_id": f"diag-{uuid.uuid4().hex[:12]}",
        "attempt_id": None,
        "session_id": f"dsess-{uuid.uuid4().hex[:12]}",
        "status": "PARTIAL",
        "target_concept": target,
        "course_id": course,
        "concept_ids": [target] if target else [],
        "observed_failure": "competing hypotheses remain; one diagnostic question asked",
        "task_type": task,
        "primary_error_code": remaining[0]["error_type"] if remaining else "unknown",
        "secondary_error_codes": [],
        "root_cause": {
            "error_type": remaining[0]["error_type"] if remaining else "unknown",
            "concept_id": target,
            "prerequisite_gap": False,
            "prerequisite_concept_id": None,
            "prerequisite_confirmed": "unconfirmed",
            "confidence": "low",
            "why": "Need the diagnostic answer before committing to a root cause.",
        },
        "prerequisite_gaps": [],
        "evidence": sources,
        "hypotheses_considered": hypotheses,
        "hypotheses_rejected": rejected,
        "diagnostic_questions": questions,
        "curriculum_sources": sources,
        "unknowns": ["awaiting_diagnostic_response"],
        "next_action_class": "VERIFY_MORE",
        "why": "Need one discriminating question.",
        "suggested_review": [],
        "decide_hook": {"gap_to_treat": None, "strategy": None},
        "adapt_hook": {"strategy_change": None, "trigger_evidence_ids": []},
        "evidence_status": "OBSERVED" if sources else "UNKNOWN",
        "confidence": "low",
        "persist_to_learner_state": False,
        "retrieval_coverage": pkg.get("coverage"),
        "signals": {k: v for k, v in signals.items() if v},
        "session": {
            "hypotheses": hypotheses,
            "questions_asked": questions,
            "remaining_hypotheses": [h["hypothesis_id"] for h in remaining],
            "persist_to_learner_state": False,
        },
        "needs_followup": True,
        "followup_question": questions[0]["text"] if questions else None,
    }


def baseline_correction(request: dict) -> dict:
    """Baseline A: explain the right answer, skip diagnosis."""
    pkg = retrieve(request.get("question") or "", system="hybrid")
    return {
        "diagnostic_id": f"diag-baseA-{uuid.uuid4().hex[:8]}",
        "status": "DIAGNOSED",
        "target_concept": (detect_query_concepts(request.get("question") or "") or [None])[0],
        "primary_error_code": "unknown",
        "root_cause": {
            "error_type": "unknown",
            "concept_id": None,
            "prerequisite_gap": False,
            "prerequisite_concept_id": None,
            "prerequisite_confirmed": "rejected",
            "confidence": "inconclusive",
            "why": "Baseline A restates the correct curriculum answer and does not identify why the learner is wrong.",
        },
        "curriculum_sources": [{"source_id": it.get("source_id")} for it in (pkg.get("items") or [])[:3]],
        "evidence_status": "OBSERVED",
        "confidence": "inconclusive",
        "persist_to_learner_state": False,
        "baseline": "A",
        "next_action_class": "REVIEW_CURRENT",
    }
