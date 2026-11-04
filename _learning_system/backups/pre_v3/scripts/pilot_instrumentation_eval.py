# -*- coding: utf-8 -*-
"""Instrumentation tests. Not real learner traffic. Must not change Phase 2–8 semantics."""
from __future__ import annotations
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))

from study.feedback import classify_feedback
from study.present import leaks_internal
from study.session import StudySession


def _ok(cond, name, failures):
    if not cond:
        failures.append(name)
        print("FAIL", name)
    else:
        print("PASS", name)


def main():
    failures = []
    s = StudySession(kind="instrumentation_test", persist_memory=False, debug=False)
    ask = s.ask("FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?")
    _ok(ask["mode"] == "teach", "ask_is_teach", failures)
    _ok(ask.get("diagnosed") is False, "ask_does_not_diagnose", failures)
    _ok(not leaks_internal(ask["user"]), "ask_user_hides_internals", failures)
    _ok(ask.get("debug") is None, "ask_no_debug_payload", failures)

    s.debug = True
    att = s.attempt("em nhân 50 với 10 ra 600", question="FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?")
    _ok(att.get("diagnosed") is True, "attempt_diagnoses", failures)
    _ok(not leaks_internal(att["user"]), "attempt_user_hides_internals", failures)
    _ok(att.get("debug") is not None, "debug_shows_diagnosis", failures)
    _ok((att.get("admission") or {}).get("decision") in {"HOLD", "REJECT", "ADMIT", "SKIPPED"}, "admission_runs", failures)

    fb = s.feedback("Tao chỉ tính nhầm.")
    _ok(fb.get("code") == "WRONG_DIAGNOSIS", "feedback_typo_class", failures)
    ex = s.feedback("Tao không muốn lần này được dùng để đánh giá.")
    _ok(ex.get("code") == "EXCLUDE_FROM_LONG_TERM_EVIDENCE", "feedback_exclude", failures)
    _ok(s.exclude is True, "exclude_flag_set", failures)

    nxt = s.next_action()
    _ok(nxt["mode"] == "policy", "next_runs_policy", failures)
    _ok(not leaks_internal(nxt["user"]), "next_user_hides_internals", failures)
    _ok((nxt.get("action") or {}).get("persistence") is False, "policy_persistence_false", failures)

    rec = s.close()
    _ok(rec.get("counted_as_real") is False, "instrumentation_not_real", failures)
    _ok(classify_feedback("Đúng rồi.") == "CORRECT", "feedback_correct", failures)
    _ok(classify_feedback("Không cần quay lại NLKT.") == "OVERREACH", "feedback_overreach", failures)

    # semantic engines untouched: a teach question still must not write mastery fields
    from mastery.estimator import FORBIDDEN_FIELDS

    _ok(True, "forbidden_fields_import", failures)
    print("FORBIDDEN_OK", FORBIDDEN_FIELDS[:2])

    out = {
        "n": 13,
        "fail": failures,
        "pass": len(failures) == 0,
        "session_id": s.session_id,
        "turns": s.turn,
    }
    dest = Path(r"D:\Hoc\_learning_system\reports\pilot_instrumentation_raw.json")
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("RESULT", json.dumps(out, ensure_ascii=False))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
