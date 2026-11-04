# -*- coding: utf-8 -*-
from __future__ import annotations
import json
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))

from retrieval.director import answer
from retrieval.retrieve import retrieve

TESTS = Path(r"D:\Hoc\_learning_system\evals\phase2_retrieval_tests.jsonl")
OUT_DIR = Path(r"D:\Hoc\_learning_system\reports")


def load_tests():
    rows = []
    with TESTS.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def classify_failure(test, pkg, reasons) -> str:
    if "insufficient_miss" in reasons:
        return "insufficient_source"
    if "contamination" in reasons:
        return "wrong_course"
    if "course_miss" in reasons:
        return "wrong_course"
    if "chapter_miss" in reasons:
        return "wrong_chapter"
    if "concept_miss" in reasons:
        return "wrong_concept"
    if "must_include_miss" in reasons:
        return "ranking_failure"
    if "prereq_miss" in reasons:
        return "prerequisite_missing"
    if "prereq_overreach" in reasons:
        return "prerequisite_overreach"
    if "authority_miss" in reasons:
        return "authority_failure"
    return "unknown"


def evaluate_one(test, system: str) -> dict:
    filters = {}
    if test.get("mode"):
        filters["mode"] = test["mode"]
    if test.get("expected_course") in {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"} and test.get("category") != "ambiguous":
        # do not pass course_id for ambiguous; for others let analyzer use the question
        pass
    t0 = time.perf_counter()
    pkg = retrieve(test["question"], filters=filters, system=system)
    dt = time.perf_counter() - t0
    items = pkg.get("items") or []
    prereq = pkg.get("prerequisite_evidence") or []
    top_courses = [it["course_id"] for it in items]
    top_ids = [it["source_id"] for it in items]
    reasons = []
    flags = {}

    expected_course = test.get("expected_course")
    if expected_course in {"nguyen-ly-ke-toan", "ke-toan-tai-chinh-1"} and test.get("expected_coverage") != "insufficient":
        if items and items[0]["course_id"] != expected_course:
            # prereq/cross may have mixed; for current_course require top-1
            if test.get("mode") in {"current_course", "source_bound"}:
                reasons.append("course_miss")
        flags["course_ok"] = (not items) or (items[0]["course_id"] == expected_course) or test.get("mode") in {
            "cross_course",
            "prerequisite_recovery",
        }
        if test.get("mode") in {"cross_course", "prerequisite_recovery"}:
            flags["course_ok"] = expected_course in top_courses or expected_course == "cross_course"
        if expected_course == "cross_course":
            flags["course_ok"] = True
    elif expected_course == "cross_course":
        flags["course_ok"] = True
    elif test.get("ambiguous"):
        flags["course_ok"] = pkg.get("current_course") == "unknown" or len(set(top_courses)) != 1
    else:
        flags["course_ok"] = True

    # contamination: forbidden courses in MAIN items
    forbidden = set(test.get("must_not_include_courses") or [])
    contaminated = [c for c in top_courses if c in forbidden]
    flags["contamination"] = bool(contaminated)
    if contaminated:
        reasons.append("contamination")

    # must_include any of listed source ids in top-5 (main or prereq if prereq test)
    must = test.get("must_include_source_ids") or []
    pool_ids = list(top_ids)
    if test.get("category") in {"prerequisite", "cross_course"}:
        pool_ids += [it["source_id"] for it in prereq]
    if must:
        flags["relevant"] = any(s in pool_ids for s in must)
        if not flags["relevant"]:
            reasons.append("must_include_miss")
    else:
        flags["relevant"] = True

    # chapter
    exp_ch = test.get("expected_chapter")
    if exp_ch is not None and test.get("expected_coverage") == "sufficient" and items:
        same = [it for it in items if it["course_id"] == expected_course] if expected_course in {
            "nguyen-ly-ke-toan",
            "ke-toan-tai-chinh-1",
        } else items
        chs = [it.get("chapter") for it in (same or items)[:5]]
        flags["chapter_ok"] = exp_ch in chs
        if not flags["chapter_ok"]:
            reasons.append("chapter_miss")
    else:
        flags["chapter_ok"] = True

    # concepts in top-5
    exp_c = test.get("expected_concepts") or []
    got_c = set()
    for it in items[:5]:
        got_c.update(it.get("concept_ids") or [])
    for it in prereq[:5]:
        got_c.update(it.get("concept_ids") or [])
    if exp_c:
        flags["concept_ok"] = bool(set(exp_c) & got_c)
        if not flags["concept_ok"]:
            reasons.append("concept_miss")
    else:
        flags["concept_ok"] = True

    # insufficient
    exp_cov = test.get("expected_coverage")
    flags["insufficient_ok"] = True
    if exp_cov == "insufficient":
        flags["insufficient_ok"] = pkg.get("coverage") == "insufficient"
        if not flags["insufficient_ok"]:
            reasons.append("insufficient_miss")

    # prereq
    flags["prereq_ok"] = True
    if test.get("expect_prereq_course"):
        pc = {it["course_id"] for it in prereq}
        flags["prereq_ok"] = test["expect_prereq_course"] in pc
        if not flags["prereq_ok"]:
            reasons.append("prereq_miss")
        # precision: prereq items should be that course
        if prereq and any(it["course_id"] != test["expect_prereq_course"] for it in prereq):
            reasons.append("prereq_overreach")
            flags["prereq_ok"] = False
    if test.get("mode") == "current_course" and test.get("expected_coverage") != "insufficient":
        # NLKT should not appear in main items when KTTC1 current course
        if test.get("expected_course") == "ke-toan-tai-chinh-1" and "nguyen-ly-ke-toan" in top_courses:
            reasons.append("prereq_overreach")
            flags["prereq_ok"] = False

    # authority
    exp_types = test.get("expected_source_types") or []
    flags["authority_ok"] = True
    if exp_types and items and test.get("expected_coverage") == "sufficient":
        types = {it["source_type"] for it in items[:5]}
        flags["authority_ok"] = bool(types & set(exp_types))
        if not flags["authority_ok"]:
            reasons.append("authority_miss")

    both_ok = True
    if test.get("expect_both_courses"):
        cs = set(top_courses) | {it["course_id"] for it in prereq}
        both_ok = "nguyen-ly-ke-toan" in cs and "ke-toan-tai-chinh-1" in cs
        flags["both_courses"] = both_ok
        if not both_ok:
            reasons.append("must_include_miss")
    else:
        flags["both_courses"] = True

    passed = (
        flags["course_ok"]
        and not flags["contamination"]
        and flags["relevant"]
        and flags["chapter_ok"]
        and flags["concept_ok"]
        and flags["insufficient_ok"]
        and flags["prereq_ok"]
        and flags["authority_ok"]
        and flags["both_courses"]
    )
    fail_type = None if passed else classify_failure(test, pkg, reasons)
    return {
        "id": test["id"],
        "category": test["category"],
        "system": system,
        "passed": passed,
        "reasons": reasons,
        "fail_type": fail_type,
        "latency_s": round(dt, 4),
        "coverage": pkg.get("coverage"),
        "mode": pkg.get("mode"),
        "detected_course": pkg.get("current_course"),
        "top_courses": top_courses,
        "top_source_ids": top_ids[:5],
        "top_chapters": [it.get("chapter") for it in items[:5]],
        "prereq_source_ids": [it["source_id"] for it in prereq[:5]],
        "flags": flags,
        "question": test["question"],
    }


def summarize(results):
    n = len(results)
    p = sum(1 for r in results if r["passed"])
    by_cat = defaultdict(lambda: {"n": 0, "pass": 0})
    fail_types = defaultdict(int)
    # metrics
    course_n = course_ok = 0
    ch_n = ch_ok = 0
    conc_n = conc_ok = 0
    rel_n = rel_ok = 0
    cont_n = cont_hit = 0
    ins_n = ins_ok = 0
    pr_n = pr_ok = 0
    auth_n = auth_ok = 0
    for r in results:
        by_cat[r["category"]]["n"] += 1
        by_cat[r["category"]]["pass"] += int(r["passed"])
        if r["fail_type"]:
            fail_types[r["fail_type"]] += 1
        f = r["flags"]
        if r["category"] not in {"ambiguous", "insufficient"}:
            course_n += 1
            course_ok += int(f["course_ok"])
        if f.get("chapter_ok") is not None:
            ch_n += 1
            ch_ok += int(f["chapter_ok"])
        conc_n += 1
        conc_ok += int(f["concept_ok"])
        rel_n += 1
        rel_ok += int(f["relevant"])
        if r["category"] not in {"prerequisite", "cross_course", "ambiguous"}:
            cont_n += 1
            cont_hit += int(f["contamination"])
        if r["category"] == "insufficient":
            ins_n += 1
            ins_ok += int(f["insufficient_ok"])
        if r["category"] == "prerequisite":
            pr_n += 1
            pr_ok += int(f["prereq_ok"])
        auth_n += 1
        auth_ok += int(f["authority_ok"])
    lat = [r["latency_s"] for r in results]
    metrics = {
        "n": n,
        "pass": p,
        "pass_rate": round(p / n, 4) if n else 0,
        "course_accuracy": round(course_ok / course_n, 4) if course_n else None,
        "chapter_accuracy": round(ch_ok / ch_n, 4) if ch_n else None,
        "concept_accuracy": round(conc_ok / conc_n, 4) if conc_n else None,
        "relevant_top5": round(rel_ok / rel_n, 4) if rel_n else None,
        "wrong_course_contamination": round(cont_hit / cont_n, 4) if cont_n else None,
        "prerequisite_precision": round(pr_ok / pr_n, 4) if pr_n else None,
        "authority_correctness": round(auth_ok / auth_n, 4) if auth_n else None,
        "insufficient_detection": round(ins_ok / ins_n, 4) if ins_n else None,
        "grounded_answer_rate": round(p / n, 4),
        "latency_mean_s": round(sum(lat) / len(lat), 4) if lat else None,
        "latency_max_s": round(max(lat), 4) if lat else None,
        "by_category": {k: {"n": v["n"], "pass": v["pass"], "rate": round(v["pass"] / v["n"], 4)} for k, v in by_cat.items()},
        "fail_types": dict(fail_types),
    }
    return metrics


GATES = {
    "wrong_course_contamination": ("<=", 0.05),
    "course_accuracy": (">=", 0.95),
    "relevant_top5": (">=", 0.90),
    "insufficient_detection": (">=", 0.90),
}


def gates_ok(metrics):
    report = {}
    all_ok = True
    for k, (op, thr) in GATES.items():
        val = metrics.get(k)
        if val is None:
            report[k] = {"value": None, "pass": False, "reason": "missing"}
            all_ok = False
            continue
        ok = val <= thr if op == "<=" else val >= thr
        report[k] = {"value": val, "threshold": f"{op} {thr}", "pass": ok}
        all_ok = all_ok and ok
    return all_ok, report


def main():
    tests = load_tests()
    systems = ["naive", "hybrid", "hybrid_prereq"]
    all_results = {}
    all_metrics = {}
    for sys_name in systems:
        print("EVAL", sys_name, len(tests), flush=True)
        rows = [evaluate_one(t, sys_name) for t in tests]
        all_results[sys_name] = rows
        all_metrics[sys_name] = summarize(rows)
        print(json.dumps(all_metrics[sys_name], ensure_ascii=False), flush=True)

    hybrid_ok, gate_report = gates_ok(all_metrics["hybrid"])
    # ablation gains
    def gain(metric):
        a = all_metrics["naive"].get(metric)
        b = all_metrics["hybrid"].get(metric)
        if a is None or b is None:
            return None
        return round(b - a, 4)

    ablation = {
        "course_accuracy_gain": gain("course_accuracy"),
        "relevant_top5_gain": gain("relevant_top5"),
        "contamination_reduction": round(
            (all_metrics["naive"].get("wrong_course_contamination") or 0)
            - (all_metrics["hybrid"].get("wrong_course_contamination") or 0),
            4,
        ),
        "insufficient_gain": gain("insufficient_detection"),
        "pass_rate_gain": gain("pass_rate"),
        "hybrid_vs_hybrid_prereq_pass": {
            "hybrid": all_metrics["hybrid"]["pass_rate"],
            "hybrid_prereq": all_metrics["hybrid_prereq"]["pass_rate"],
        },
    }
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "n_tests": len(tests),
        "metrics": all_metrics,
        "gates": gate_report,
        "hybrid_gates_pass": hybrid_ok,
        "ablation": ablation,
        "results": all_results,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "retrieval_benchmark_raw.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("GATES", hybrid_ok, json.dumps(gate_report, ensure_ascii=False))
    print("WROTE", OUT_DIR / "retrieval_benchmark_raw.json")


if __name__ == "__main__":
    main()
