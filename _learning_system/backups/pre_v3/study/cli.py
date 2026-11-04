# -*- coding: utf-8 -*-
"""Learner-facing study CLI. python -m study"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))

from study.session import StudySession


def _print(view: dict, debug: bool) -> None:
    print(view.get("user") or "")
    if debug and view.get("debug"):
        print("\n--- debug ---")
        print(json.dumps(view["debug"], ensure_ascii=False, indent=2, default=str))


def _repl(sess: StudySession) -> None:
    print("study  |  hỏi câu hỏi, hoặc: attempt: ... | feedback: ... | next | debug on|off | exclude | status | quit")
    while True:
        try:
            line = input("study> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        low = line.lower()
        if low in {"quit", "exit", "q"}:
            break
        if low == "debug on":
            sess.debug = True
            print("debug on")
            continue
        if low == "debug off":
            sess.debug = False
            print("debug off")
            continue
        if low == "exclude":
            sess.exclude = True
            print("Lượt này không vào bộ nhớ dài hạn.")
            continue
        if low == "next":
            _print(sess.next_action(), sess.debug)
            continue
        if low == "status":
            print(json.dumps({"session_id": sess.session_id, "turns": sess.turn, "exclude": sess.exclude, "kind": sess.kind}, ensure_ascii=False))
            continue
        if low.startswith("attempt:") or low.startswith("làm:"):
            body = line.split(":", 1)[1].strip()
            if not sess.last_question:
                print("Chưa có câu hỏi. Hỏi trước, rồi attempt: ...")
                continue
            _print(sess.attempt(body), sess.debug)
            continue
        if low.startswith("feedback:") or low.startswith("phản hồi:"):
            body = line.split(":", 1)[1].strip()
            _print(sess.feedback(body), sess.debug)
            continue
        _print(sess.ask(line), sess.debug)
    sess.close()


def main(argv=None):
    p = argparse.ArgumentParser(prog="study", description="Học NLKT/KTTC1 từ giáo trình đã index. Không SRS.")
    p.add_argument("question", nargs="?", help="Câu hỏi (không tự chuyển sang chẩn đoán)")
    p.add_argument("--attempt", help="Bài làm / câu trả lời của người học")
    p.add_argument("--work", default="")
    p.add_argument("--followup")
    p.add_argument("--course")
    p.add_argument("--chapter", type=int)
    p.add_argument("--feedback")
    p.add_argument("--next", action="store_true")
    p.add_argument("--debug", action="store_true")
    p.add_argument("--exclude", action="store_true", help="Không đưa lượt này vào bộ nhớ dài hạn")
    p.add_argument("--kind", default="real", help="real | instrumentation_test")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    sess = StudySession(
        course_id=args.course,
        chapter=args.chapter,
        debug=args.debug,
        kind=args.kind,
        exclude_from_long_term_evidence=args.exclude,
        persist_memory=(args.kind == "real" and not args.exclude),
    )
    out = None
    if args.question and not args.attempt and not args.feedback:
        out = sess.ask(args.question)
    if args.question and args.attempt:
        sess.last_question = args.question
        out = sess.attempt(args.attempt, question=args.question, work=args.work, followup=args.followup)
    elif args.attempt and sess.last_question:
        out = sess.attempt(args.attempt, work=args.work, followup=args.followup)
    if args.feedback:
        out = sess.feedback(args.feedback)
    if args.next:
        out = sess.next_action()
    if out is None and not args.question:
        if sys.stdin.isatty():
            _repl(sess)
            return
        p.print_help()
        sess.close()
        return
    if args.json and out:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    elif out:
        _print(out, args.debug)
    sess.close()


if __name__ == "__main__":
    main()
