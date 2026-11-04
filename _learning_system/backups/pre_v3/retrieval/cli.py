# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))


def cmd_build(_args):
    from retrieval.chunking import build_chunks
    from retrieval.index import build_index

    chunks = build_chunks()
    print("chunks", len(chunks))
    idx = build_index()
    print("index", idx["meta"]["chunk_count"], "vocab", idx["meta"]["vocab_size"])


def cmd_retrieve(args):
    from retrieval.director import answer

    filters = {}
    if args.course:
        filters["course_id"] = args.course
    if args.chapter is not None:
        filters["chapter"] = args.chapter
    if args.mode:
        filters["mode"] = args.mode
    if args.include_prereq:
        filters["include_prerequisites"] = True
    if args.no_prereq:
        filters["include_prerequisites"] = False
    result = answer(args.question, filters=filters, system=args.system)
    if args.json:
        print(json.dumps({"answer": result["answer"], "package": result["package"], "grounded": result["grounded"]}, ensure_ascii=False, indent=2))
    else:
        print(result["answer"])
        pkg = result["package"]
        print("\n--- package ---")
        print("mode", pkg["mode"], "course", pkg["current_course"], "coverage", pkg["coverage"])
        print("concepts", pkg["detected_concepts"])
        print("items", len(pkg["items"]), "prereq_items", len(pkg.get("prerequisite_evidence") or []))


def cmd_adapt(args):
    from retrieval.director import adapt

    out = adapt(
        args.question,
        learner_response=args.response,
        work_shown=args.work,
        course_id=args.course,
        chapter=args.chapter,
        evidence=args.evidence,
    )
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
        return
    sess = out["session"]
    print("director_mode:", out["director_mode"])
    print("status:", sess.get("status"), "resolution:", sess.get("resolution_kind"))
    diag = sess.get("current_diagnosis") or {}
    dec = sess.get("current_decision") or {}
    print("diagnosis:", diag.get("primary_error_code"), "prereq:", (diag.get("root_cause") or {}).get("prerequisite_gap"))
    print("decision:", (dec.get("decision") or {}).get("action_type"))
    print("diag_transitions:", sess.get("diagnosis_transitions"))
    print("persist:", sess.get("persist_to_learner_state"))


def cmd_study(args):
    from study.cli import main as study_main

    argv = []
    if args.question:
        argv.append(args.question)
    if args.attempt:
        argv.extend(["--attempt", args.attempt])
    if args.work:
        argv.extend(["--work", args.work])
    if args.course:
        argv.extend(["--course", args.course])
    if args.chapter is not None:
        argv.extend(["--chapter", str(args.chapter)])
    if args.feedback:
        argv.extend(["--feedback", args.feedback])
    if args.next:
        argv.append("--next")
    if args.debug:
        argv.append("--debug")
    if args.exclude:
        argv.append("--exclude")
    if args.json:
        argv.append("--json")
    argv.extend(["--kind", "real"])
    study_main(argv)


def cmd_next(args):
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


def cmd_diagnose(args):
    from retrieval.director import handle

    wrapped = handle(
        args.question,
        learner_response=args.response,
        work_shown=args.work,
        course_id=args.course,
        chapter=args.chapter,
        followup_response=args.followup,
    )
    out = wrapped["result"]
    if args.json:
        payload = {"director_mode": wrapped["director_mode"], "diagnostic": out}
        if wrapped.get("decision"):
            payload["decision"] = wrapped["decision"]
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return
    print("director_mode:", wrapped["director_mode"])
    print("status:", out.get("status"), "confidence:", out.get("confidence"))
    print("target:", out.get("target_concept"), "course:", out.get("course_id"))
    rc = out.get("root_cause") or {}
    print("root_cause:", rc.get("error_type"), "prereq_gap:", rc.get("prerequisite_gap"), rc.get("prerequisite_concept_id"))
    print("why:", rc.get("why") or out.get("why"))
    if out.get("followup_question"):
        print("diagnostic_question:", out["followup_question"])
    for q in out.get("diagnostic_questions") or []:
        print("diagnostic_question:", q.get("text"))
    for s in (out.get("curriculum_sources") or [])[:3]:
        print("source:", s.get("source_id"), s.get("relative_path"))
    print("persist_to_learner_state:", out.get("persist_to_learner_state"))
    dec = wrapped.get("decision")
    if dec:
        print("decision:", (dec.get("decision") or {}).get("action_type"), dec.get("status"), "prereq:", (dec.get("primary_gap") or {}).get("is_prerequisite"))
        print("decision_reason:", (dec.get("decision") or {}).get("reason"))
        print("decision_persist:", dec.get("persistence"))


def main():
    p = argparse.ArgumentParser(prog="retrieval")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.set_defaults(func=cmd_build)
    r = sub.add_parser("retrieve")
    r.add_argument("question")
    r.add_argument("--course")
    r.add_argument("--chapter", type=int)
    r.add_argument("--mode")
    r.add_argument("--system", default="hybrid", choices=["naive", "hybrid", "hybrid_prereq"])
    r.add_argument("--include-prereq", action="store_true")
    r.add_argument("--no-prereq", action="store_true")
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_retrieve)
    d = sub.add_parser("diagnose")
    d.add_argument("question")
    d.add_argument("--response", default="")
    d.add_argument("--work", default="")
    d.add_argument("--course")
    d.add_argument("--chapter", type=int)
    d.add_argument("--followup")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_diagnose)
    de = sub.add_parser("decide")
    de.add_argument("question")
    de.add_argument("--response", default="")
    de.add_argument("--work", default="")
    de.add_argument("--course")
    de.add_argument("--chapter", type=int)
    de.add_argument("--followup")
    de.add_argument("--json", action="store_true")
    de.set_defaults(func=cmd_diagnose)
    a = sub.add_parser("adapt")
    a.add_argument("question")
    a.add_argument("--response", default="")
    a.add_argument("--work", default="")
    a.add_argument("--course")
    a.add_argument("--chapter", type=int)
    a.add_argument("--evidence", action="append", default=[])
    a.add_argument("--json", action="store_true")
    a.set_defaults(func=cmd_adapt)
    n = sub.add_parser("next")
    n.add_argument("--course")
    n.add_argument("--concept", action="append", default=[])
    n.add_argument("--task-type", default="application")
    n.add_argument("--request-json")
    n.add_argument("--json", action="store_true")
    n.set_defaults(func=cmd_next)
    st = sub.add_parser("study")
    st.add_argument("question", nargs="?")
    st.add_argument("--attempt")
    st.add_argument("--work", default="")
    st.add_argument("--course")
    st.add_argument("--chapter", type=int)
    st.add_argument("--feedback")
    st.add_argument("--next", action="store_true")
    st.add_argument("--debug", action="store_true")
    st.add_argument("--exclude", action="store_true")
    st.add_argument("--json", action="store_true")
    st.set_defaults(func=cmd_study)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
