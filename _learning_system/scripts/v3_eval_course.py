# -*- coding: utf-8 -*-
"""V3 course eval runner (plan 7.5/6.9). usage: --course C [--first-run] ; writes reports/v3/C_eval.json/.md"""
from __future__ import annotations
import argparse, sys, hashlib, json, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retrieval.config import SYSTEM
from retrieval.retrieve import retrieve

GATES = {"direct_must_include": 0.85, "direct_chapter_at1": 0.80, "source_bound": 2 / 3, "insufficient": 1.0,
         "collision_contamination": 0, "account": 0.5, "topic_owner": 1.0, "collision_rows_failed": 0}


def run_row(r):
    f = {"mode": r["mode"]} if r.get("mode") else {}
    if r.get("pass_course"): f["course_id"] = r["course"]
    pkg = retrieve(r["question"], filters=f)
    items = pkg.get("items") or []
    top5 = [it["source_id"] for it in items[:5]]
    out = {"id": r["id"], "category": r["category"], "question": r["question"], "coverage": pkg.get("coverage"),
           "top_sources": top5, "top_chapters": [it.get("chapter") for it in items[:5]], "partition": pkg.get("partition"),
           "unknowns": pkg.get("unknowns")}
    must = r.get("must_include_source_ids") or []
    out["must_include"] = (not must) or any(s in top5 for s in must)
    exp = r.get("expected_chapter")
    out["chapter_at1"] = (exp is None) or (bool(items) and items[0].get("chapter") == exp)
    forb = set(r.get("must_not_include_courses") or [])
    out["contaminated"] = any(it["course_id"] in forb for it in items)
    cat = r["category"]
    if cat == "direct": out["pass"] = out["must_include"] and out["chapter_at1"]
    elif cat == "source_bound": out["pass"] = out["must_include"] and out["chapter_at1"]
    elif cat == "insufficient": out["pass"] = pkg.get("coverage") == "insufficient"
    elif cat == "collision": out["pass"] = (not out["contaminated"]) and bool(items) and pkg.get("partition") == r["course"]
    elif cat == "account": out["pass"] = out["must_include"]
    elif cat == "topic_owner":
        sug = pkg.get("other_course_suggestions") or []
        out["suggestions"] = sug
        out["pass"] = any(s.get("type") == "topic_owner" and s.get("course_id") == r["expect_suggestion_course"]
                          and r["expect_suggestion_chapter"] in (s.get("chapters") or []) for s in sug)
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--course", required=True); ap.add_argument("--tag", default="")
    # Wave 6.2: new-topic rows live in a separate frozen file evals/v3/<C>_retrieval_r<N>.jsonl (--suffix _r1)
    ap.add_argument("--suffix", default="")
    # W6b R2 G09: gate failure => exit code 3 (returned by main(); only the __main__ guard exits). --report-only keeps 0.
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args(); cid = a.course
    if "+" in a.tag or "+" in a.suffix: ap.error("'+' is reserved in --tag/--suffix (report-name namespace)")
    path = SYSTEM / "evals" / "v3" / f"{cid}_retrieval{a.suffix}.jsonl"
    rows = [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]
    if not rows:
        sys.exit(f"EVAL_EMPTY: {path.name} has no rows; refusing to write a passing report")  # W6b G09
    res = [run_row(r) for r in rows]
    by = defaultdict(list)
    for x in res: by[x["category"]].append(x)
    rate = lambda lst, k: sum(1 for x in lst if x[k]) / len(lst) if lst else None
    m = {
        "direct_must_include": rate(by["direct"], "must_include"), "direct_chapter_at1": rate(by["direct"], "chapter_at1"),
        "source_bound": rate(by["source_bound"], "pass"), "insufficient": rate(by["insufficient"], "pass"),
        "collision_contamination": sum(1 for x in by["collision"] if x["contaminated"]), "account": rate(by["account"], "pass"),
        "topic_owner": rate(by["topic_owner"], "pass"),
        # W6b review M3: a collision row that returns no items / the wrong partition must fail the gate, not only contamination
        "collision_rows_failed": sum(1 for x in by["collision"] if not x["pass"]),
    }
    # account / topic_owner are n/a (pass) when the course has no such rows (e.g. no account map; topic_owner rows are Wave 1 only, plan 6.7)
    # a supplementary file (--suffix) only holds some categories; absent categories are n/a there, never a failure
    na_ok = ("account", "topic_owner") + (tuple(GATES) if a.suffix else ())
    LOWER_BETTER = ("collision_contamination", "collision_rows_failed")
    gates = {k: ((m[k] is None and k in na_ok) or (m[k] is not None and (m[k] <= GATES[k] if k in LOWER_BETTER else m[k] >= GATES[k]))) for k in GATES}
    # W6b review M3: report (do not gate; frozen files are not edited) rows whose coverage differs from expected_coverage
    cov_mismatch = [{"id": x["id"], "category": x["category"], "expected": r.get("expected_coverage"), "got": x["coverage"]}
                    for r, x in zip(rows, res) if r.get("expected_coverage") and x["coverage"] != r["expected_coverage"]]  # S3 G11: every category
    out = {"course_id": cid, "tag": a.tag, "coverage_mismatch_rows": cov_mismatch, "eval_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "n": len(rows),
           "metrics": m, "gates": gates, "all_pass": all(gates.values()), "results": res}
    rep = SYSTEM / "reports" / "v3"; rep.mkdir(parents=True, exist_ok=True)
    # W6b R2 G09: base keeps <C>_eval<tag>; a supplement is <C>_eval+<suffix><tag>. '+' never occurs in a tag/suffix
    # used here, so a supplement can never share a name with a base report whatever the tag/suffix split.
    stem = f"{cid}_eval+{a.suffix}{a.tag}" if a.suffix else f"{cid}_eval{a.tag}"
    (rep / f"{stem}.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [f"# {cid} eval {a.tag}", "", f"eval sha256 `{out['eval_sha256']}` · n={len(rows)} · all_pass={out['all_pass']}", "", "| gate | value | threshold | pass |", "|---|---|---|---|"]
    for k in GATES: md.append(f"| {k} | {m[k]} | {GATES[k]} | {gates[k]} |")
    md += ["", "## failing rows"]
    for x in res:
        if not x["pass"]: md.append(f"- {x['id']} ({x['category']}): {x['question']} → cov={x['coverage']} top={x['top_sources']} ch={x['top_chapters']} unknowns={x['unknowns']}")
    (rep / f"{stem}.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(m), "ALL_PASS" if out["all_pass"] else "GATE_FAIL")
    if cov_mismatch: print("WARN coverage differs from expected_coverage:", json.dumps(cov_mismatch, ensure_ascii=False))
    for x in res:
        if not x["pass"]: print("FAIL", x["id"], x["question"], x["coverage"], x["top_sources"], x["top_chapters"])
    return 0 if (out["all_pass"] or a.report_only) else 3


if __name__ == "__main__":
    sys.exit(main())
