# -*- coding: utf-8 -*-
"""Evaluate learner-notes top-3 retrieval, routing, and non-curriculum contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from retrieval.config import SYSTEM
from retrieval.partition import clear_cache, get_partition_index
from retrieval.retrieve import retrieve


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="")
    args = parser.parse_args()
    eval_path = SYSTEM / "evals" / "v3" / "learner-notes_retrieval.jsonl"
    rows = [json.loads(line) for line in eval_path.open(encoding="utf-8") if line.strip()]
    clear_cache()
    learner_index = get_partition_index("learner-notes")
    results = []
    for row in rows:
        package = retrieve(row["question"], top_k=3)
        top3 = [item["source_id"] for item in package.get("items") or []][:3]
        expected = set(row["expected_source_ids"])
        checks = {
            "top3": bool(expected.intersection(top3)),
            "partition": package.get("partition") == "learner-notes",
            "coverage": package.get("coverage") == "learner_material",
            "unknowns": package.get("unknowns") == ["not_curriculum_source"],
            "metadata": all(
                learner_index.by_id[item["chunk_id"]].get("content_role") == "learner_material"
                and learner_index.by_id[item["chunk_id"]].get("authority") == 7
                and learner_index.by_id[item["chunk_id"]].get("partition") == "learner_notes"
                for item in package.get("items") or []
            ),
        }
        results.append({"id": row["id"], "question": row["question"], "expected": sorted(expected), "top3": top3, "checks": checks, "pass": all(checks.values())})

    explicit = retrieve("tra cứu ghi chú", filters={"course_id": "learner-notes"}, top_k=3)
    explicit_smoke = (
        explicit.get("partition") == "learner-notes"
        and explicit.get("coverage") == "learner_material"
        and explicit.get("unknowns") == ["not_curriculum_source"]
    )
    rate = lambda key: sum(1 for row in results if row["checks"][key]) / len(results) if results else 0.0
    metrics = {
        "top3": rate("top3"),
        "implicit_routing": rate("partition"),
        "coverage_contract": rate("coverage"),
        "unknowns_contract": rate("unknowns"),
        "metadata_contract": rate("metadata"),
        "explicit_route": 1.0 if explicit_smoke else 0.0,
    }
    all_pass = len(rows) == 5 and all(row["pass"] for row in results) and explicit_smoke
    output = {
        "partition": "learner-notes",
        "tag": args.tag,
        "eval_sha256": hashlib.sha256(eval_path.read_bytes()).hexdigest(),
        "n": len(rows),
        "metrics": metrics,
        "all_pass": all_pass,
        "results": results,
    }
    report_dir = SYSTEM / "reports" / "v3"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"learner-notes_eval{args.tag}.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    markdown = [
        f"# learner-notes eval {args.tag}",
        "",
        f"eval sha256 `{output['eval_sha256']}` · n={len(rows)} · all_pass={all_pass}",
        "",
        "| metric | value |",
        "|---|---:|",
        *[f"| {key} | {value} |" for key, value in metrics.items()],
        "",
        "## failing rows",
    ]
    for result in results:
        if not result["pass"]:
            markdown.append(f"- {result['id']}: expected={result['expected']} top3={result['top3']} checks={result['checks']}")
    (report_dir / f"learner-notes_eval{args.tag}.md").write_text("\n".join(markdown), encoding="utf-8")
    print(json.dumps(metrics), "ALL_PASS" if all_pass else "GATE_FAIL")
    for result in results:
        if not result["pass"]:
            print("FAIL", result["id"], result["expected"], result["top3"], result["checks"])
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
