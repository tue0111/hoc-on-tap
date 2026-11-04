# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    p = argparse.ArgumentParser(prog="diagnostic")
    p.add_argument("question")
    p.add_argument("--response", default="")
    p.add_argument("--work", default="")
    p.add_argument("--course")
    p.add_argument("--chapter", type=int)
    p.add_argument("--followup")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    from diagnostic.engine import diagnose

    req = {
        "question": args.question,
        "learner_response": args.response,
        "work_shown": args.work,
        "course_context": {"course_id": args.course, "chapter": args.chapter},
    }
    out = diagnose(req, followup_response=args.followup, allow_question=True)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    print("status:", out["status"], "confidence:", out["confidence"])
    print("target:", out.get("target_concept"), "course:", out.get("course_id"))
    rc = out.get("root_cause") or {}
    print("root_cause:", rc.get("error_type"), "prereq_gap:", rc.get("prerequisite_gap"), rc.get("prerequisite_concept_id"))
    print("why:", rc.get("why") or out.get("why"))
    if out.get("followup_question"):
        print("diagnostic_question:", out["followup_question"])
    for s in (out.get("curriculum_sources") or [])[:3]:
        print("source:", s.get("source_id"), s.get("relative_path"))
    print("persist_to_learner_state:", out.get("persist_to_learner_state"))


if __name__ == "__main__":
    main()
