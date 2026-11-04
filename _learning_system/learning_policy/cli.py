# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    p = argparse.ArgumentParser(prog="learning_policy")
    p.add_argument("--request-json")
    p.add_argument("--course")
    p.add_argument("--concept", action="append", default=[])
    p.add_argument("--task-type", default="application")
    args = p.parse_args()
    from learning_policy.engine import choose
    from mastery.store import CURRENT

    if args.request_json:
        req = json.loads(Path(args.request_json).read_text(encoding="utf-8"))
    else:
        snap = json.loads(CURRENT.read_text(encoding="utf-8")) if CURRENT.exists() else {"concepts": {}}
        req = {
            "current_context": {"course_id": args.course, "current_concepts": args.concept, "task_type": args.task_type},
            "learner_state": snap,
            "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
        }
    out = choose(req)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
