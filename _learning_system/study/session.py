# -*- coding: utf-8 -*-
"""Learner-facing study session. Wraps existing engines. Does not change their policy."""
from __future__ import annotations
import time
import uuid
from datetime import datetime, timezone

from study.feedback import classify_feedback, is_exclude
from study.log import is_real_traffic, log_event, log_feedback, log_session
from study.present import format_decision, format_next, format_teach

VERSIONS = {
    "retrieval": "2.0.0",
    "diagnostic": "3.0.0",
    "decision": "4.0.0",
    "adaptive": "5.0.0",
    "admission_policy": "1.0.0",
    "state": "7.0.0",
    "learning_policy": "8.0.0",
    "study": "0.1.0",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StudySession:
    def __init__(
        self,
        *,
        course_id: str | None = None,
        chapter=None,
        debug: bool = False,
        kind: str = "real",
        persist_memory: bool | None = None,
        exclude_from_long_term_evidence: bool = False,
        session_id: str | None = None,
    ):
        self.session_id = session_id or f"st-{uuid.uuid4().hex[:12]}"
        self.course_id = course_id
        self.chapter = chapter
        self.debug = debug
        self.kind = kind
        self.exclude = bool(exclude_from_long_term_evidence)
        self.persist_memory = (kind == "real") if persist_memory is None else persist_memory
        self.turn = 0
        self.last_question = None
        self.last_diag = None
        self.last_dec = None
        self.last_pkg = None
        self.events: list[dict] = []
        self.opened_at = _now()
        self.substantive_turns = 0

    def _turn(self) -> str:
        self.turn += 1
        return f"{self.session_id}-t{self.turn:03d}"

    def _record(self, payload: dict) -> dict:
        t0 = payload.get("t0")
        latency = None
        if t0 is not None:
            latency = round(time.perf_counter() - t0, 4)
            payload.pop("t0", None)
        ev = {
            "session_id": self.session_id,
            "turn_id": payload.get("turn_id"),
            "timestamp": _now(),
            "kind": self.kind,
            "course_context": {"course_id": self.course_id, "chapter": self.chapter},
            "task_context": {"question": self.last_question},
            "learner_input": payload.get("learner_input"),
            "system_mode": payload.get("system_mode"),
            "retrieved_evidence_refs": payload.get("retrieved_evidence_refs") or [],
            "diagnosis_status": payload.get("diagnosis_status"),
            "selected_immediate_decision": payload.get("selected_immediate_decision"),
            "adaptive_transition": payload.get("adaptive_transition"),
            "admission_decision": payload.get("admission_decision"),
            "state_transition": payload.get("state_transition"),
            "phase8_next_action": payload.get("phase8_next_action"),
            "policy_versions": VERSIONS,
            "latency_s": latency,
            "learner_correction": payload.get("learner_correction"),
            "exclude_from_long_term_evidence": self.exclude,
            "counted_as_real": is_real_traffic(self.kind) and payload.get("substantive", True),
        }
        self.events.append(ev)
        log_event(ev)
        if ev["counted_as_real"] and payload.get("substantive", True):
            self.substantive_turns += 1
        return ev

    def ask(self, question: str) -> dict:
        """Curriculum question. Does not auto-diagnose."""
        from retrieval.director import answer

        t0 = time.perf_counter()
        self.last_question = question
        filters = {}
        if self.course_id:
            filters["course_id"] = self.course_id
        if self.chapter is not None:
            filters["chapter"] = self.chapter
        out = answer(question, filters=filters or None)
        self.last_pkg = out.get("package")
        view = format_teach(out, debug=self.debug)
        pkg = out.get("package") or {}
        refs = [{"source_id": it.get("source_id"), "chapter": it.get("chapter")} for it in (pkg.get("items") or [])[:5]]
        turn_id = self._turn()
        self._record(
            {
                "t0": t0,
                "turn_id": turn_id,
                "learner_input": question,
                "system_mode": "teach",
                "retrieved_evidence_refs": refs,
                "diagnosis_status": None,
                "selected_immediate_decision": None,
                "substantive": True,
            }
        )
        return {"mode": "teach", "user": view["user"], "debug": view["debug"], "diagnosed": False, "turn_id": turn_id}

    def attempt(self, response: str, *, question: str | None = None, work: str = "", followup: str | None = None) -> dict:
        """Learner work exists → diagnose + decide. Optional adapt if followup."""
        from retrieval.director import adapt, handle

        t0 = time.perf_counter()
        q = question or self.last_question or ""
        self.last_question = q
        if followup:
            wrapped = adapt(q, learner_response=response, work_shown=work, course_id=self.course_id, chapter=self.chapter, evidence=[followup])
            diag = wrapped.get("result") or {}
            dec = wrapped.get("decision")
            adapt_tr = (wrapped.get("session") or {}).get("diagnosis_transitions")
        else:
            wrapped = handle(q, learner_response=response, work_shown=work, course_id=self.course_id, chapter=self.chapter)
            diag = wrapped.get("result") or {}
            dec = wrapped.get("decision")
            adapt_tr = None
        self.last_diag = diag
        self.last_dec = dec
        view = format_decision(diag, dec, debug=self.debug)
        refs = [{"source_id": s.get("source_id")} for s in (diag.get("curriculum_sources") or [])[:5]]
        act = ((dec or {}).get("decision") or {}).get("action_type")
        adm = self._maybe_admit(diag, response)
        turn_id = self._turn()
        self._record(
            {
                "t0": t0,
                "turn_id": turn_id,
                "learner_input": response,
                "system_mode": "adapt" if followup else "decision",
                "retrieved_evidence_refs": refs,
                "diagnosis_status": diag.get("status"),
                "selected_immediate_decision": act,
                "adaptive_transition": adapt_tr,
                "admission_decision": (adm or {}).get("decision"),
                "substantive": True,
            }
        )
        return {
            "mode": "decision",
            "user": view["user"],
            "debug": view["debug"],
            "diagnosed": True,
            "admission": adm,
            "turn_id": turn_id,
        }

    def next_action(self) -> dict:
        from learning_policy.engine import choose
        from mastery.store import CURRENT
        import json
        from pathlib import Path

        t0 = time.perf_counter()
        snap = {"concepts": {}}
        p = Path(CURRENT)
        if p.exists():
            snap = json.loads(p.read_text(encoding="utf-8"))
        concepts = []
        if self.last_diag and self.last_diag.get("target_concept"):
            concepts = [self.last_diag["target_concept"]]
        elif self.last_pkg and self.last_pkg.get("detected_concepts"):
            concepts = list(self.last_pkg.get("detected_concepts") or [])
        req = {
            "current_context": {
                "course_id": self.course_id or (self.last_pkg or {}).get("current_course"),
                "chapter": self.chapter,
                "task_type": "application",
                "current_concepts": concepts,
            },
            "learner_state": snap,
            "current_diagnostic_result": self.last_diag,
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        }
        out = choose(req)
        view = format_next(out, debug=self.debug)
        turn_id = self._turn()
        self._record(
            {
                "t0": t0,
                "turn_id": turn_id,
                "learner_input": None,
                "system_mode": "policy",
                "phase8_next_action": (out.get("action") or {}).get("type"),
                "substantive": False,
            }
        )
        return {"mode": "policy", "user": view["user"], "debug": view["debug"], "action": out, "turn_id": turn_id}

    def feedback(self, text: str) -> dict:
        code = classify_feedback(text)
        if is_exclude(code, text):
            self.exclude = True
        turn_id = self._turn()
        row = {
            "session_id": self.session_id,
            "turn_id": turn_id,
            "text": text,
            "code": code,
            "kind": self.kind,
            "counted_as_real": is_real_traffic(self.kind),
        }
        log_feedback(row)
        self._record(
            {
                "turn_id": turn_id,
                "learner_input": text,
                "system_mode": "feedback",
                "learner_correction": code,
                "substantive": is_real_traffic(self.kind),
            }
        )
        user = "Đã ghi nhận phản hồi."
        if code == "EXCLUDE_FROM_LONG_TERM_EVIDENCE":
            user = "Lượt này sẽ không đưa vào bộ nhớ học tập dài hạn."
        elif code == "UNKNOWN":
            user = "Đã lưu ý kiến. Chưa đủ để kết luận giáo trình sai."
        return {"mode": "feedback", "user": user, "code": code, "debug": {"code": code} if self.debug else None, "turn_id": turn_id}

    def _maybe_admit(self, diag: dict, response: str) -> dict | None:
        if self.exclude:
            return {"decision": "SKIPPED", "reason_codes": ["EXCLUDE_FROM_LONG_TERM_EVIDENCE"]}
        from admission.engine import decide_admission
        from admission.store import write_decision

        et = diag.get("primary_error_code")
        outcome = "INCORRECT" if et not in {None, "none", "unknown", "no_error"} else ("CORRECT" if et in {"none", "no_error"} else "INCONCLUSIVE")
        cand = {
            "candidate_id": f"{self.session_id}-c{self.turn}",
            "learner_event_type": "DIAGNOSTIC_ANSWER",
            "course_id": diag.get("course_id") or self.course_id,
            "concept_id": diag.get("target_concept"),
            "dimension": "APPLICATION",
            "observation": (response or "")[:240],
            "outcome": outcome,
            "support_level": "INDEPENDENT",
            "independence": "INDEPENDENT_TASK",
            "hint_level": "NO_HINT",
            "source_session_id": self.session_id,
            "source_task_id": f"{self.session_id}-task",
            "curriculum_evidence_refs": (diag.get("curriculum_sources") or [])[:1],
            "diagnostic_result_ref": diag.get("diagnostic_id") or f"{self.session_id}-diag",
            "lineage_ids": [diag.get("diagnostic_id") or f"{self.session_id}-diag"],
            "evidence_strength": "MEDIUM",
            "explicit_false_rule": False,
            "mechanical_only": et == "arithmetic_error",
            "wrong_reason_with_correct_result": False,
            "diagnosis_status": diag.get("status"),
            "error_type": et,
            "timestamp": _now(),
            "observed_at": _now(),
        }
        dec = decide_admission(cand, prior=[])
        write_decision(cand, dec, persist=bool(self.persist_memory) and not self.exclude)
        return dec

    def close(self) -> dict:
        rec = {
            "session_id": self.session_id,
            "kind": self.kind,
            "opened_at": self.opened_at,
            "closed_at": _now(),
            "course_id": self.course_id,
            "turns": self.turn,
            "substantive_turns": self.substantive_turns,
            "counted_as_real": is_real_traffic(self.kind),
            "exclude_from_long_term_evidence": self.exclude,
        }
        log_session(rec)
        return rec
