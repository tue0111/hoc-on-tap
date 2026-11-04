# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main():
    p = argparse.ArgumentParser(prog="admission")
    p.add_argument("--candidate-json", help="Path to a candidate JSON object")
    p.add_argument("--persist", action="store_true")
    args = p.parse_args()
    from admission.engine import decide_admission
    from admission.store import write_decision

    cand = json.loads(Path(args.candidate_json).read_text(encoding="utf-8"))
    dec = decide_admission(cand)
    dec = write_decision(cand, dec, persist=args.persist)
    print(json.dumps(dec, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
