# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    p = argparse.ArgumentParser(prog="adaptive")
    p.add_argument("question")
    p.add_argument("--response", default="")
    p.add_argument("--work", default="")
    p.add_argument("--course")
    p.add_argument("--chapter", type=int)
    p.add_argument("--evidence", action="append", default=[], help="Additional learner evidence (repeatable)")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    from adaptive.controller import ingest, start, summary

    sess = start(
        {
            "question": args.question,
            "learner_response": args.response,
            "work_shown": args.work,
            "course_context": {"course_id": args.course, "chapter": args.chapter},
        }
    )
    for ev in args.evidence:
        ingest(sess, ev)
    if args.json:
        print(json.dumps({"session": sess, "summary": summary(sess)}, ensure_ascii=False, indent=2, default=str))
        return
    print("status:", sess.get("status"), "resolution:", sess.get("resolution_kind"))
    diag = sess.get("current_diagnosis") or {}
    dec = sess.get("current_decision") or {}
    print("diagnosis:", diag.get("primary_error_code"), "prereq:", (diag.get("root_cause") or {}).get("prerequisite_gap"))
    print("decision:", (dec.get("decision") or {}).get("action_type"))
    print("transitions:", sess.get("diagnosis_transitions"))
    print("pending:", sess.get("pending_question"))
    print("persist:", sess.get("persist_to_learner_state"))


if __name__ == "__main__":
    main()
