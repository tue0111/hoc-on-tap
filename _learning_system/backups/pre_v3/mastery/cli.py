# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))


def main():
    p = argparse.ArgumentParser(prog="mastery")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("recompute")
    r.add_argument("--write", action="store_true")
    r.add_argument("--from-jsonl")
    q = sub.add_parser("query")
    q.add_argument("--concept")
    q.add_argument("--concern", action="store_true")
    q.add_argument("--recovery", action="store_true")
    q.add_argument("--insufficient", action="store_true")
    args = p.parse_args()
    from mastery.estimator import recompute
    from mastery.query import concept_state, concern, dimensions_insufficient, recovery
    from mastery.store import CURRENT, full_recompute, load_admitted, load_jsonl

    if args.cmd == "recompute":
        ev = load_jsonl(Path(args.from_jsonl)) if args.from_jsonl else load_admitted()
        snap = full_recompute(persist=args.write, admitted=ev)
        print(json.dumps({"concept_count": snap["concept_count"], "coverage": snap["coverage"], "invalid": snap["invalid_input_count"]}, indent=2))
        return
    snap = json.loads(CURRENT.read_text(encoding="utf-8")) if CURRENT.exists() else recompute(load_admitted())
    if args.concept:
        print(json.dumps(concept_state(snap, args.concept), ensure_ascii=False, indent=2))
    elif args.concern:
        print(json.dumps(concern(snap), ensure_ascii=False, indent=2))
    elif args.recovery:
        print(json.dumps(recovery(snap), ensure_ascii=False, indent=2))
    elif args.insufficient:
        print(json.dumps(dimensions_insufficient(snap), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(snap.get("coverage"), indent=2))


if __name__ == "__main__":
    main()
