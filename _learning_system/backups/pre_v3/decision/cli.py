# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))


def main():
    p = argparse.ArgumentParser(prog="decision")
    p.add_argument("question")
    p.add_argument("--response", default="")
    p.add_argument("--work", default="")
    p.add_argument("--course")
    p.add_argument("--chapter", type=int)
    p.add_argument("--followup")
    p.add_argument("--no-prereq-backfill", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    from decision.engine import decide

    req = {
        "question": args.question,
        "learner_response": args.response,
        "work_shown": args.work,
        "followup_response": args.followup,
        "session_context": {"course_id": args.course, "chapter": args.chapter},
        "constraints": {
            "max_actions": 1,
            "allow_prerequisite_backfill": not args.no_prereq_backfill,
        },
    }
    out = decide(req)
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return
    print("status:", out["status"], "confidence:", out["confidence_band"])
    print("action:", (out.get("decision") or {}).get("action_type"), "depth:", (out.get("decision") or {}).get("depth"))
    g = out.get("primary_gap") or {}
    print("gap:", g.get("error_type"), "concept:", g.get("concept_id"), "prereq:", g.get("is_prerequisite"))
    print("reason:", (out.get("decision") or {}).get("reason"))
    print("preview:", (out.get("decision") or {}).get("preview"))
    print("persist:", out.get("persistence"))


if __name__ == "__main__":
    main()
