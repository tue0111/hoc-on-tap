# -*- coding: utf-8 -*-
from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import os as _os
_SYS = Path(_os.environ.get("HOC_ROOT", r"D:\Hoc")) / "_learning_system"

OUT = (_SYS / "evals" / "admission_cases.jsonl")
OUT_L = (_SYS / "evals" / "admission_longitudinal.jsonl")
OUT_N = (_SYS / "evals" / "admission_naturalistic.jsonl")

k1 = "ke-toan-tai-chinh-1"
nlkt = "nguyen-ly-ke-toan"


def cand(cid, concept, dim, outcome, obs, **kw):
    d = {
        "candidate_id": cid,
        "learner_event_type": kw.get("learner_event_type", "DIAGNOSTIC_ANSWER"),
        "course_id": kw.get("course_id", k1),
        "concept_id": concept,
        "dimension": dim,
        "observation": obs,
        "outcome": outcome,
        "support_level": kw.get("support_level", "INDEPENDENT"),
        "independence": kw.get("independence", "INDEPENDENT_TASK"),
        "hint_level": kw.get("hint_level", "NO_HINT"),
        "source_session_id": kw.get("session", f"sess-{cid}"),
        "source_task_id": kw.get("task", f"task-{cid}"),
        "curriculum_evidence_refs": kw.get("refs", [{"source_id": "src-0062"}]),
        "diagnostic_result_ref": kw.get("diag", f"diag-{cid}"),
        "decision_ref": kw.get("dec", f"dec-{cid}"),
        "lineage_ids": kw.get("lineage", [f"diag-{cid}"]),
        "evidence_strength": kw.get("strength", "MEDIUM"),
        "explicit_false_rule": kw.get("explicit_false_rule", False),
        "mechanical_only": kw.get("mechanical_only", False),
        "wrong_reason_with_correct_result": kw.get("wrong_reason", False),
        "diagnosis_status": kw.get("diagnosis_status", "DIAGNOSED"),
        "error_type": kw.get("error_type"),
        "timestamp": kw.get("timestamp", "2026-09-01T00:00:00+00:00"),
        "observed_at": kw.get("timestamp", "2026-09-01T00:00:00+00:00"),
        "provenance": {"session": kw.get("session", f"sess-{cid}")},
    }
    return d


def row(cid, category, candidate, gold, prior=None, mates=None):
    return {
        "id": cid,
        "category": category,
        "candidate": candidate,
        "prior": prior or [],
        "cluster_mates": mates or [],
        "gold": gold,
    }


def main():
    cases = []

    # 20 one-off mistakes → HOLD
    for i in range(20):
        cases.append(
            row(
                f"adm-oneoff-{i+1:02d}",
                "one_off",
                cand(
                    f"c-oneoff-{i+1:02d}",
                    "hang-ton-kho" if i % 2 == 0 else "tien-va-tuong-duong-tien",
                    "APPLICATION",
                    "INCORRECT",
                    "Selected expense account where the taught task required inventory recognition."
                    if i % 2 == 0
                    else "Recorded TK 112 on a cash-on-hand receipt task.",
                    error_type="classification_error" if i % 2 == 0 else "journal_entry_error",
                    strength="MEDIUM",
                ),
                {"decision": "HOLD", "must_not_admit": True, "reason_contains": "INSUFFICIENT_REPETITION"},
            )
        )

    # 15 same-task retries → REJECT independence
    for i in range(15):
        first = cand(
            f"c-retry-base-{i+1:02d}",
            "hang-ton-kho",
            "APPLICATION",
            "INCORRECT",
            "Selected expense account where the taught task required inventory recognition.",
            session="sess-retry",
            task="task-same-q",
            independence="INDEPENDENT_TASK",
        )
        retry = cand(
            f"c-retry-{i+1:02d}",
            "hang-ton-kho",
            "APPLICATION",
            "INCORRECT",
            f"Retry {i+1} on the same purchase item: still selected an expense account instead of inventory.",
            session="sess-retry",
            task="task-same-q",
            independence="SAME_TASK_RETRY",
            lineage=[f"diag-retry-{i}"],
        )
        cases.append(
            row(
                f"adm-retry-{i+1:02d}",
                "same_task_retry",
                retry,
                {"decision": "REJECT", "must_not_admit": True, "reason_contains": "SAME_TASK_RETRY"},
                prior=[first],
            )
        )

    # 20 repeated independent errors → ADMIT
    for i in range(20):
        a = cand(
            f"c-rep-a-{i+1:02d}",
            "hang-ton-kho",
            "APPLICATION",
            "INCORRECT",
            "Selected expense account on a cash purchase of goods for resale.",
            session=f"sess-a-{i}",
            task=f"task-a-{i}",
            independence="INDEPENDENT_TASK",
        )
        b = cand(
            f"c-rep-b-{i+1:02d}",
            "hang-ton-kho",
            "APPLICATION",
            "INCORRECT",
            "Selected expense account on a credit purchase of goods for resale.",
            session=f"sess-b-{i}",
            task=f"task-b-{i}",
            independence="INDEPENDENT_TASK" if i < 15 else "CROSS_CONTEXT_TRANSFER",
        )
        cases.append(
            row(
                f"adm-repind-{i+1:02d}",
                "repeated_independent",
                b,
                {"decision": "ADMIT", "reason_contains": "REPEATED_INDEPENDENT_EVIDENCE"},
                prior=[a],
            )
        )

    # 15 independent successes → ADMIT
    for i in range(15):
        dim = "TRANSFER" if i < 8 else "APPLICATION"
        cases.append(
            row(
                f"adm-pos-{i+1:02d}",
                "independent_success",
                cand(
                    f"c-pos-{i+1:02d}",
                    "hang-ton-kho" if dim == "TRANSFER" else "no-co",
                    dim,
                    "CORRECT",
                    "Independently classified goods for resale as inventory on a service-vs-merchandising contrast task."
                    if dim == "TRANSFER"
                    else "Stated that an asset increase is recorded on the debit side, then applied it to TK 111.",
                    independence="CROSS_CONTEXT_TRANSFER" if dim == "TRANSFER" else "INDEPENDENT_TASK",
                    strength="STRONG",
                    error_type=None,
                ),
                {"decision": "ADMIT", "reason_contains": "POSITIVE_INDEPENDENT_EVIDENCE"},
            )
        )

    # 10 self-report → REJECT
    for i in range(10):
        cases.append(
            row(
                f"adm-self-{i+1:02d}",
                "self_report",
                cand(
                    f"c-self-{i+1:02d}",
                    "no-co",
                    "CONCEPTUAL",
                    "CORRECT",
                    "em hiểu rồi",
                    support_level="SELF_REPORTED",
                    learner_event_type="SELF_REPORT",
                    strength="WEAK",
                    independence="INDEPENDENT_TASK",
                ),
                {"decision": "REJECT", "must_not_admit": True, "reason_contains": "SELF_REPORT_ONLY"},
            )
        )

    # 10 hinted / answer exposed → REJECT as independent positive
    for i in range(10):
        cases.append(
            row(
                f"adm-hint-{i+1:02d}",
                "hinted",
                cand(
                    f"c-hint-{i+1:02d}",
                    "pp-tinh-gia-xuat-kho",
                    "APPLICATION",
                    "CORRECT",
                    "Produced FIFO total after the worked solution was shown.",
                    support_level="GUIDED" if i < 5 else "COPIED",
                    hint_level="ANSWER_EXPOSED" if i >= 5 else "DIRECT_HINT",
                    strength="MEDIUM",
                ),
                {"decision": "REJECT", "must_not_admit": True, "reason_contains": "HINT_CONTAMINATED"},
            )
        )

    # 10 correct answer / wrong reason → split
    for i in range(10):
        dim = "CONCEPTUAL" if i < 5 else "APPLICATION"
        c = cand(
            f"c-cawr-{i+1:02d}",
            "pp-tinh-gia-xuat-kho",
            dim,
            "CORRECT" if dim == "APPLICATION" else "INCORRECT",
            "Computed 50×10=500 but described FIFO as using the newest lot cost."
            if dim == "CONCEPTUAL"
            else "Numeric FIFO total matched the taught lot while the verbal rule named the newest lot.",
            wrong_reason=True,
            explicit_false_rule=(dim == "CONCEPTUAL"),
            strength="STRONG",
        )
        gold = (
            {"decision": "ADMIT", "reason_contains": "SPLIT_DIMENSIONS"}
            if dim == "CONCEPTUAL"
            else {"decision": "HOLD", "must_not_admit": True, "reason_contains": "SPLIT_DIMENSIONS"}
        )
        cases.append(row(f"adm-cawr-{i+1:02d}", "correct_wrong_reason", c, gold))

    # 10 contradictory — ADMIT new observation, keep relation
    for i in range(10):
        old = cand(
            f"c-con-old-{i+1:02d}",
            "hang-ton-kho",
            "APPLICATION",
            "INCORRECT",
            "Selected expense account on a cash purchase of goods for resale.",
            session=f"sess-old-{i}",
            task=f"task-old-{i}",
            timestamp="2026-08-01T00:00:00+00:00",
        )
        new = cand(
            f"c-con-new-{i+1:02d}",
            "hang-ton-kho",
            "APPLICATION",
            "CORRECT",
            "Independently recognized goods for resale as inventory on a later purchase task.",
            session=f"sess-new-{i}",
            task=f"task-new-{i}",
            timestamp="2026-09-01T00:00:00+00:00",
            strength="STRONG",
            independence="INDEPENDENT_TASK",
        )
        cases.append(
            row(
                f"adm-contra-{i+1:02d}",
                "contradiction",
                new,
                {"decision": "ADMIT", "expect_contradiction": True},
                prior=[old],
            )
        )

    # 10 duplicate lineage
    for i in range(10):
        orig = cand(
            f"c-dup-orig-{i+1:02d}",
            "no-co",
            "CONCEPTUAL",
            "INCORRECT",
            "Stated that an asset increase is recorded on the credit side.",
            session="sess-dup",
            task="task-dup",
            lineage=["diag-dup-shared", "dec-dup-shared"],
            explicit_false_rule=True,
            strength="STRONG",
        )
        clone = cand(
            f"c-dup-clone-{i+1:02d}",
            "no-co",
            "CONCEPTUAL",
            "INCORRECT",
            "Stated that an asset increase is recorded on the credit side.",
            session="sess-dup",
            task="task-dup",
            lineage=["diag-dup-shared"],
            diag="diag-dup-shared",
            dec="dec-dup-shared",
            explicit_false_rule=True,
            strength="STRONG",
        )
        cases.append(
            row(
                f"adm-dup-{i+1:02d}",
                "duplicate",
                clone,
                {"decision": "REJECT", "must_not_admit": True, "reason_contains": "DUPLICATE_EVIDENCE"},
                prior=[orig],
            )
        )

    assert len(cases) == 120, len(cases)
    print("admission", len(cases), Counter(c["category"] for c in cases))
    OUT.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cases), encoding="utf-8")

    # ----- 40 longitudinal -----
    longs = []
    for i in range(10):
        s1 = cand(f"lon-a1-{i}", "hang-ton-kho", "APPLICATION", "INCORRECT", "Selected expense account on purchase of goods.", session=f"L{i}s1", task=f"L{i}t1")
        s2 = cand(f"lon-a2-{i}", "hang-ton-kho", "APPLICATION", "INCORRECT", "Selected expense account on a different credit purchase.", session=f"L{i}s2", task=f"L{i}t2")
        longs.append({"id": f"lon-A-{i+1:02d}", "category": "hold_then_admit", "steps": [
            {"candidate": s1, "gold": {"decision": "HOLD"}},
            {"candidate": s2, "gold": {"decision": "ADMIT", "reason_contains": "REPEATED_INDEPENDENT_EVIDENCE"}},
        ]})
    for i in range(8):
        s1 = cand(f"lon-b1-{i}", "hang-ton-kho", "APPLICATION", "INCORRECT", "Selected expense account on purchase of goods.", session=f"Lb{i}s1", task=f"Lb{i}t1")
        s2 = cand(f"lon-b2-{i}", "hang-ton-kho", "APPLICATION", "CORRECT", "Independently recognized goods as inventory on a later transfer-style task.", session=f"Lb{i}s2", task=f"Lb{i}t2", independence="CROSS_CONTEXT_TRANSFER", strength="STRONG")
        longs.append({"id": f"lon-B-{i+1:02d}", "category": "error_then_success", "steps": [
            {"candidate": s1, "gold": {"decision": "HOLD"}},
            {"candidate": s2, "gold": {"decision": "ADMIT", "expect_contradiction": True}},
        ]})
    for i in range(8):
        s1 = cand(f"lon-c1-{i}", "pp-tinh-gia-xuat-kho", "APPLICATION", "CORRECT", "FIFO total after worked example.", session=f"Lc{i}s1", support_level="GUIDED", hint_level="DIRECT_HINT")
        s2 = cand(f"lon-c2-{i}", "pp-tinh-gia-xuat-kho", "APPLICATION", "CORRECT", "FIFO total after another worked example.", session=f"Lc{i}s2", support_level="GUIDED", hint_level="ANSWER_EXPOSED")
        longs.append({"id": f"lon-C-{i+1:02d}", "category": "guided_repeat", "steps": [
            {"candidate": s1, "gold": {"decision": "REJECT", "must_not_admit": True}},
            {"candidate": s2, "gold": {"decision": "REJECT", "must_not_admit": True}},
        ]})
    for i in range(7):
        s1 = cand(f"lon-d1-{i}", "no-co", "CONCEPTUAL", "CORRECT", "em hiểu rồi", support_level="SELF_REPORTED", learner_event_type="SELF_REPORT", strength="WEAK", session=f"Ld{i}s1")
        s2 = cand(f"lon-d2-{i}", "no-co", "TRANSFER", "INCORRECT", "Reversed debit/credit on a new cash task.", session=f"Ld{i}s2")
        longs.append({"id": f"lon-D-{i+1:02d}", "category": "self_report_fail_transfer", "steps": [
            {"candidate": s1, "gold": {"decision": "REJECT", "must_not_admit": True}},
            {"candidate": s2, "gold": {"decision": "HOLD", "must_not_admit": True}},
        ]})
    for i in range(7):
        s1 = cand(f"lon-e1-{i}", "no-co", "CONCEPTUAL", "INCORRECT", "Stated that an asset increase is recorded on the credit side.", session=f"Le{i}s1", explicit_false_rule=True, strength="STRONG", timestamp="2026-07-01T00:00:00+00:00")
        s2 = cand(f"lon-e2-{i}", "no-co", "CONCEPTUAL", "CORRECT", "Stated that an asset increase is recorded on the debit side and applied it to cash.", session=f"Le{i}s2", strength="STRONG", timestamp="2026-09-01T00:00:00+00:00")
        longs.append({"id": f"lon-E-{i+1:02d}", "category": "chrono_contradiction", "steps": [
            {"candidate": s1, "gold": {"decision": "ADMIT"}},
            {"candidate": s2, "gold": {"decision": "ADMIT", "expect_contradiction": True}},
        ]})
    assert len(longs) == 40, len(longs)
    OUT_L.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in longs), encoding="utf-8")
    print("longitudinal", len(longs), Counter(x["category"] for x in longs))

    # ----- 40 naturalistic -----
    nats = []
    vague = [
        "em không chắc bên nào",
        "gì đó 111",
        "huh",
        "N111 C511",
        "em ghi 642 chắc vậy",
        "fifo 600",
        "chắc vậy",
    ]
    for i in range(25):
        obs = vague[i % len(vague)]
        nats.append(
            row(
                f"natadm-{i+1:02d}",
                "naturalistic",
                cand(
                    f"c-nat-{i+1:02d}",
                    "tien-va-tuong-duong-tien",
                    "CONCEPTUAL",
                    "INCONCLUSIVE",
                    obs,
                    strength="WEAK",
                    diagnosis_status="INCONCLUSIVE",
                    independence="INDEPENDENT_TASK",
                ),
                {"decision": "HOLD", "must_not_admit": True, "conservative": True},
            )
        )
    for i in range(8):
        nats.append(
            row(
                f"natadm-self-{i+1:02d}",
                "naturalistic",
                cand(
                    f"c-natself-{i+1:02d}",
                    "hang-ton-kho",
                    "CONCEPTUAL",
                    "CORRECT",
                    "em nhớ cái này, dễ",
                    support_level="SELF_REPORTED",
                    learner_event_type="SELF_REPORT",
                    strength="WEAK",
                ),
                {"decision": "REJECT", "must_not_admit": True},
            )
        )
    for i in range(7):
        nats.append(
            row(
                f"natadm-typo-{i+1:02d}",
                "naturalistic",
                cand(
                    f"c-nattypo-{i+1:02d}",
                    "hang-ton-kho",
                    "CONCEPTUAL",
                    "INCORRECT",
                    "Wrote 165 instead of 156 then corrected the digit; no conceptual claim.",
                    mechanical_only=True,
                    strength="MEDIUM",
                ),
                {"decision": "REJECT", "must_not_admit": True, "reason_contains": "MECHANICAL_ONLY"},
            )
        )
    assert len(nats) >= 40
    OUT_N.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in nats), encoding="utf-8")
    print("naturalistic", len(nats))
    print("WROTE", OUT, OUT_L, OUT_N)


if __name__ == "__main__":
    main()
