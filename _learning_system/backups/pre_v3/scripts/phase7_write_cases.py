# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path

OUT = Path(r"D:\Hoc\_learning_system\evals\state_cases.jsonl")
OUT_L = Path(r"D:\Hoc\_learning_system\evals\state_longitudinal.jsonl")
OUT_N = Path(r"D:\Hoc\_learning_system\evals\state_naturalistic.jsonl")


def ev(eid, concept, dim, outcome, when, **kw):
    return {
        "artifact_id": eid,
        "candidate_id": eid,
        "concept_id": concept,
        "dimension": dim,
        "outcome": outcome,
        "independence": kw.get("independence", "INDEPENDENT_TASK"),
        "support_level": kw.get("support_level", "INDEPENDENT"),
        "hint_level": kw.get("hint_level", "NO_HINT"),
        "course_id": kw.get("course_id", "ke-toan-tai-chinh-1"),
        "source_session_id": kw.get("session", f"s-{eid}"),
        "source_task_id": kw.get("task", f"t-{eid}"),
        "observation": kw.get("obs", f"{outcome} {dim} {concept}"),
        "observed_at": when,
        "timestamp": when,
    }


def case(cid, category, evidence, gold_concept, gold_dim, gold_state, **g):
    return {
        "id": cid,
        "category": category,
        "evidence": evidence,
        "gold": {
            "concept_id": gold_concept,
            "dimension": gold_dim,
            "state": gold_state,
            **g,
        },
    }


def main():
    rows = []
    c_htk = "hang-ton-kho"
    c_noco = "no-co"
    c_fifo = "pp-tinh-gia-xuat-kho"
    c_cash = "tien-va-tuong-duong-tien"

    # 20 insufficient
    for i in range(10):
        rows.append(case(f"st-ins-{i+1:02d}", "insufficient", [], c_htk, "APPLICATION", "INSUFFICIENT_EVIDENCE"))
    for i in range(5):
        rows.append(
            case(
                f"st-ins-retry-{i+1:02d}",
                "insufficient",
                [
                    ev(f"r{i}a", c_htk, "APPLICATION", "CORRECT", "2026-01-01", independence="SAME_TASK_RETRY"),
                    ev(f"r{i}b", c_htk, "APPLICATION", "CORRECT", "2026-01-02", independence="SAME_TASK_RETRY", session="s-same", task="t-same"),
                ],
                c_htk,
                "APPLICATION",
                "INSUFFICIENT_EVIDENCE",
            )
        )
    for i in range(5):
        rows.append(
            case(
                f"st-ins-hint-{i+1:02d}",
                "insufficient",
                [ev(f"h{i}", c_fifo, "APPLICATION", "CORRECT", "2026-01-01", support_level="GUIDED", hint_level="ANSWER_EXPOSED")],
                c_fifo,
                "APPLICATION",
                "INSUFFICIENT_EVIDENCE",
            )
        )

    # 20 tentative positive
    for i in range(20):
        rows.append(
            case(
                f"st-tpos-{i+1:02d}",
                "tentative_positive",
                [ev(f"tp{i}", c_noco, "CONCEPTUAL", "CORRECT", "2026-02-01")],
                c_noco,
                "CONCEPTUAL",
                "TENTATIVELY_SUPPORTED",
            )
        )

    # 20 strong supported
    for i in range(20):
        rows.append(
            case(
                f"st-sup-{i+1:02d}",
                "supported",
                [
                    ev(f"s{i}a", c_htk, "TRANSFER", "CORRECT", "2026-02-01", independence="CROSS_CONTEXT_TRANSFER"),
                    ev(f"s{i}b", c_htk, "TRANSFER", "CORRECT", "2026-03-01", independence="INDEPENDENT_TASK"),
                ],
                c_htk,
                "TRANSFER",
                "SUPPORTED",
            )
        )

    # 20 tentative concern
    for i in range(20):
        rows.append(
            case(
                f"st-tcon-{i+1:02d}",
                "tentative_concern",
                [ev(f"tc{i}", c_cash, "APPLICATION", "INCORRECT", "2026-02-01")],
                c_cash,
                "APPLICATION",
                "TENTATIVE_CONCERN",
            )
        )

    # 20 repeated concern
    for i in range(20):
        rows.append(
            case(
                f"st-con-{i+1:02d}",
                "concern",
                [
                    ev(f"cn{i}a", c_htk, "APPLICATION", "INCORRECT", "2026-01-01"),
                    ev(f"cn{i}b", c_htk, "APPLICATION", "INCORRECT", "2026-02-01"),
                ],
                c_htk,
                "APPLICATION",
                "CONCERN",
            )
        )

    # 20 mixed (pos then neg, or 1 and 1)
    for i in range(20):
        rows.append(
            case(
                f"st-mix-{i+1:02d}",
                "mixed",
                [
                    ev(f"m{i}a", c_fifo, "APPLICATION", "CORRECT", "2026-01-01"),
                    ev(f"m{i}b", c_fifo, "APPLICATION", "INCORRECT", "2026-03-01"),
                ],
                c_fifo,
                "APPLICATION",
                "MIXED",
            )
        )

    # 15 recovery signal: 2 neg then 1 pos
    for i in range(15):
        rows.append(
            case(
                f"st-rec-{i+1:02d}",
                "recovery_signal",
                [
                    ev(f"rc{i}a", c_noco, "CONCEPTUAL", "INCORRECT", "2026-01-01"),
                    ev(f"rc{i}b", c_noco, "CONCEPTUAL", "INCORRECT", "2026-02-01"),
                    ev(f"rc{i}c", c_noco, "CONCEPTUAL", "CORRECT", "2026-04-01"),
                ],
                c_noco,
                "CONCEPTUAL",
                "RECOVERY_SIGNAL",
            )
        )

    # 15 recovery completed
    for i in range(15):
        rows.append(
            case(
                f"st-recdone-{i+1:02d}",
                "recovery_completed",
                [
                    ev(f"rd{i}a", c_noco, "CONCEPTUAL", "INCORRECT", "2026-01-01"),
                    ev(f"rd{i}b", c_noco, "CONCEPTUAL", "INCORRECT", "2026-02-01"),
                    ev(f"rd{i}c", c_noco, "CONCEPTUAL", "CORRECT", "2026-04-01"),
                    ev(f"rd{i}d", c_noco, "CONCEPTUAL", "CORRECT", "2026-05-01"),
                ],
                c_noco,
                "CONCEPTUAL",
                "SUPPORTED",
            )
        )

    assert len(rows) == 150, len(rows)

    # counterfactual extras attached as extra categories still in 150? already 150.
    # leakage checks on supported cases: other dims insufficient
    for r in rows:
        if r["category"] in {"supported", "concern", "tentative_positive"}:
            r["gold"]["other_dims_insufficient"] = True
            r["gold"]["no_other_concepts"] = True

    print("state_cases", len(rows), Counter(r["category"] for r in rows))
    OUT.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")

    longs = []
    for i in range(10):
        longs.append({
            "id": f"lonst-A-{i+1:02d}",
            "category": "pos_pos_supported",
            "steps": [
                {"add": [ev(f"la{i}1", c_htk, "APPLICATION", "CORRECT", "2026-01-01")], "gold": "TENTATIVELY_SUPPORTED"},
                {"add": [ev(f"la{i}2", c_htk, "APPLICATION", "CORRECT", "2026-02-01")], "gold": "SUPPORTED"},
            ],
            "concept_id": c_htk,
            "dimension": "APPLICATION",
        })
    for i in range(10):
        longs.append({
            "id": f"lonst-B-{i+1:02d}",
            "category": "neg_neg_concern",
            "steps": [
                {"add": [ev(f"lb{i}1", c_htk, "APPLICATION", "INCORRECT", "2026-01-01")], "gold": "TENTATIVE_CONCERN"},
                {"add": [ev(f"lb{i}2", c_htk, "APPLICATION", "INCORRECT", "2026-02-01")], "gold": "CONCERN"},
            ],
            "concept_id": c_htk,
            "dimension": "APPLICATION",
        })
    for i in range(8):
        longs.append({
            "id": f"lonst-C-{i+1:02d}",
            "category": "neg_then_recovery",
            "steps": [
                {"add": [ev(f"lc{i}1", c_noco, "CONCEPTUAL", "INCORRECT", "2026-01-01"), ev(f"lc{i}2", c_noco, "CONCEPTUAL", "INCORRECT", "2026-02-01")], "gold": "CONCERN"},
                {"add": [ev(f"lc{i}3", c_noco, "CONCEPTUAL", "CORRECT", "2026-04-01")], "gold": "RECOVERY_SIGNAL"},
            ],
            "concept_id": c_noco,
            "dimension": "CONCEPTUAL",
        })
    for i in range(8):
        longs.append({
            "id": f"lonst-D-{i+1:02d}",
            "category": "recovery_to_supported",
            "steps": [
                {"add": [
                    ev(f"ld{i}1", c_noco, "CONCEPTUAL", "INCORRECT", "2026-01-01"),
                    ev(f"ld{i}2", c_noco, "CONCEPTUAL", "INCORRECT", "2026-02-01"),
                    ev(f"ld{i}3", c_noco, "CONCEPTUAL", "CORRECT", "2026-04-01"),
                ], "gold": "RECOVERY_SIGNAL"},
                {"add": [ev(f"ld{i}4", c_noco, "CONCEPTUAL", "CORRECT", "2026-05-01")], "gold": "SUPPORTED"},
            ],
            "concept_id": c_noco,
            "dimension": "CONCEPTUAL",
        })
    for i in range(8):
        longs.append({
            "id": f"lonst-E-{i+1:02d}",
            "category": "pos_then_fail_mixed",
            "steps": [
                {"add": [ev(f"le{i}1", c_fifo, "APPLICATION", "CORRECT", "2026-01-01"), ev(f"le{i}2", c_fifo, "APPLICATION", "CORRECT", "2026-02-01")], "gold": "SUPPORTED"},
                {"add": [ev(f"le{i}3", c_fifo, "APPLICATION", "INCORRECT", "2026-06-01")], "gold": "MIXED"},
            ],
            "concept_id": c_fifo,
            "dimension": "APPLICATION",
        })
    for i in range(8):
        longs.append({
            "id": f"lonst-F-{i+1:02d}",
            "category": "no_decay",
            "steps": [
                {"add": [ev(f"lf{i}1", c_cash, "CONCEPTUAL", "CORRECT", "2025-01-01"), ev(f"lf{i}2", c_cash, "CONCEPTUAL", "CORRECT", "2025-02-01")], "gold": "SUPPORTED"},
                {"add": [], "gold": "SUPPORTED"},
            ],
            "concept_id": c_cash,
            "dimension": "CONCEPTUAL",
        })
    for i in range(8):
        longs.append({
            "id": f"lonst-G-{i+1:02d}",
            "category": "cross_dimension",
            "steps": [
                {"add": [
                    ev(f"lg{i}1", c_htk, "RECALL", "CORRECT", "2026-01-01"),
                    ev(f"lg{i}2", c_htk, "RECALL", "CORRECT", "2026-02-01"),
                    ev(f"lg{i}3", c_htk, "APPLICATION", "INCORRECT", "2026-01-15"),
                    ev(f"lg{i}4", c_htk, "APPLICATION", "INCORRECT", "2026-02-15"),
                ], "gold_by_dim": {"RECALL": "SUPPORTED", "APPLICATION": "CONCERN", "CONCEPTUAL": "INSUFFICIENT_EVIDENCE"}},
            ],
            "concept_id": c_htk,
            "dimension": "RECALL",
        })
    assert len(longs) == 60, len(longs)
    OUT_L.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in longs), encoding="utf-8")
    print("longitudinal", len(longs), Counter(x["category"] for x in longs))

    nats = []
    for i in range(15):
        nats.append(case(f"stnat-sparse-{i+1:02d}", "naturalistic", [], c_htk, "TRANSFER", "INSUFFICIENT_EVIDENCE"))
    for i in range(10):
        nats.append(case(
            f"stnat-gap-{i+1:02d}", "naturalistic",
            [ev(f"ng{i}a", c_fifo, "APPLICATION", "CORRECT", "2025-01-01"), ev(f"ng{i}b", c_fifo, "APPLICATION", "CORRECT", "2025-02-01")],
            c_fifo, "APPLICATION", "SUPPORTED",
        ))
    for i in range(10):
        nats.append(case(
            f"stnat-mix-{i+1:02d}", "naturalistic",
            [ev(f"nm{i}a", c_cash, "APPLICATION", "CORRECT", "2026-01-01"), ev(f"nm{i}b", c_cash, "APPLICATION", "INCORRECT", "2026-08-01")],
            c_cash, "APPLICATION", "MIXED",
        ))
    for i in range(8):
        nats.append(case(
            f"stnat-rec-{i+1:02d}", "naturalistic",
            [
                ev(f"nr{i}a", c_noco, "CONCEPTUAL", "INCORRECT", "2026-01-01"),
                ev(f"nr{i}b", c_noco, "CONCEPTUAL", "INCORRECT", "2026-03-01"),
                ev(f"nr{i}c", c_noco, "CONCEPTUAL", "CORRECT", "2026-09-01"),
            ],
            c_noco, "CONCEPTUAL", "RECOVERY_SIGNAL",
        ))
    for i in range(7):
        nats.append(case(
            f"stnat-mal-{i+1:02d}", "naturalistic",
            [{"artifact_id": f"bad{i}", "outcome": "CORRECT", "independence": "INDEPENDENT_TASK"}],
            c_htk, "APPLICATION", "INSUFFICIENT_EVIDENCE",
        ))
    assert len(nats) == 50, len(nats)
    OUT_N.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in nats), encoding="utf-8")
    print("naturalistic", len(nats))
    print("WROTE", OUT, OUT_L, OUT_N)


if __name__ == "__main__":
    main()
