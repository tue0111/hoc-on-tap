# -*- coding: utf-8 -*-
from __future__ import annotations
from retrieval.retrieve import retrieve


def handle(
    question: str,
    *,
    learner_response: str | None = None,
    work_shown: str | None = None,
    course_id: str | None = None,
    chapter=None,
    followup_response: str | None = None,
    filters: dict | None = None,
    system: str = "hybrid",
) -> dict:
    """Learning Director entry. Diagnostic Mode only when a learner attempt exists."""
    from retrieval.courses import is_core, normalize_course

    _cid = normalize_course(course_id) if course_id else None
    if _cid and not is_core(_cid):
        # V3: retrieval/catalog tier courses have no diagnosis, decision, admission or state.
        _f = dict(filters or {})
        _f["course_id"] = _cid
        return {"director_mode": "teach", "result": answer(question, filters=_f, system=system),
                "note": "diagnosis_not_available_for_course_tier"}
    if (learner_response and learner_response.strip()) or (work_shown and work_shown.strip()):
        from diagnostic.engine import diagnose

        req = {
            "question": question,
            "learner_response": learner_response or "",
            "work_shown": work_shown or "",
            "course_context": {"course_id": course_id, "chapter": chapter},
        }
        diag = diagnose(req, followup_response=followup_response)
        from decision.engine import decide

        dec = decide(
            {
                "diagnostic_result": diag,
                "session_context": {"course_id": course_id, "chapter": chapter},
                "constraints": {"max_actions": 1, "allow_prerequisite_backfill": True},
            }
        )
        return {"director_mode": "decision", "result": diag, "decision": dec}
    out = answer(question, filters=filters, system=system)
    return {"director_mode": "teach", "result": out}


def adapt(question: str, learner_response: str = "", work_shown: str = "", course_id=None, chapter=None, evidence: list | None = None):
    """Session-level adapt: diagnose → decide → ingest new evidence → re-diagnose/re-decide if triggered."""
    from adaptive.controller import ingest, start, summary

    sess = start(
        {
            "question": question,
            "learner_response": learner_response,
            "work_shown": work_shown,
            "course_context": {"course_id": course_id, "chapter": chapter},
        }
    )
    deltas = []
    for ev in evidence or []:
        if isinstance(ev, str) and ev.strip():
            deltas.append(ingest(sess, ev))
    return {
        "director_mode": "adapt",
        "session": sess,
        "deltas": deltas,
        "summary": summary(sess),
        "result": sess.get("current_diagnosis"),
        "decision": sess.get("current_decision"),
    }


def answer(question: str, filters: dict | None = None, system: str = "hybrid") -> dict:
    from retrieval.external import note_lines
    result = _answer_curriculum(question, filters, system)
    extra = note_lines(result['package'])
    if extra:
        result['answer'] += '\n\n' + '\n'.join(extra)
    return result


def _answer_curriculum(question: str, filters: dict | None = None, system: str = "hybrid") -> dict:
    pkg = retrieve(question, filters=filters, system=system)
    if pkg.get("partition"):
        return _answer_partition(pkg)
    lines = []
    coverage = pkg["coverage"]
    mode = pkg["mode"]
    course = pkg["current_course"]

    if coverage == "insufficient":
        lines.append("CURRICULUM EVIDENCE IS INSUFFICIENT.")
        lines.append("Không đủ bằng chứng trong corpus NLKT/KTTC1 đã index để trả lời như một curriculum fact.")
        if pkg.get("unknowns"):
            lines.append("Unknowns: " + ", ".join(pkg["unknowns"]))
        if pkg.get("detected_concepts"):
            lines.append("Concepts detected in the question: " + ", ".join(pkg["detected_concepts"]))
        # still show any weak hits as non-authoritative pointers
        if pkg.get("items"):
            lines.append("Nearest (non-sufficient) hits:")
            for it in pkg["items"][:3]:
                lines.append(
                    f"- {it['course_id']} ch.{it.get('chapter')} {it.get('source')} p.{it.get('page_range')} [{it.get('source_type')}]"
                )
        lines += _suggestion_lines(pkg)
        text = "\n".join(lines)
        return {"answer": text, "package": pkg, "grounded": False}

    lines.append("Answer (curriculum-grounded):")
    # stitch top lecture-note excerpts first
    theory = [it for it in pkg["items"] if it.get("source_type") in {"lecture_note", "syllabus"}]
    use = theory or pkg["items"]
    top = use[0]
    snippet = top["excerpt"].replace("\n", " ")
    if len(snippet) > 700:
        snippet = snippet[:700] + "…"
    lines.append(snippet)
    lines.append("")
    lines.append("Source / course context:")
    for it in use[:4]:
        lines.append(
            f"- {it['course_id']} ({it.get('course_code')}) | ch.{it.get('chapter')} | "
            f"{it.get('source')} p.{it.get('page_range')} | {it.get('source_type')} | authority={it.get('authority')}"
        )
        lines.append(f"  reason: {it.get('reason_selected')}")

    if pkg.get("conflicts"):
        lines.append("")
        lines.append("SOURCE_CONFLICT (not merged):")
        for c in pkg["conflicts"]:
            lines.append(f"- {c.get('note')}")

    if pkg.get("prerequisite_evidence") and mode in {"prerequisite_recovery", "cross_course"}:
        lines.append("")
        lines.append("Prerequisite link (NLKT), only because this question needs it:")
        for it in pkg["prerequisite_evidence"][:3]:
            lines.append(
                f"- {it['course_id']} ch.{it.get('chapter')} {it.get('source')} p.{it.get('page_range')} "
                f"concepts={it.get('concept_ids')}"
            )
    elif mode == "current_course":
        lines.append("")
        lines.append("Prerequisite NLKT was not pulled (not required for this question).")

    lines.append("")
    lines.append("CURRICULUM FACT above is quoted/paraphrased from retrieved chunks only.")
    if coverage == "partial":
        lines.append("INFERENCE: coverage is partial; some requested facets may be missing from extracts.")
    lines += _suggestion_lines(pkg)

    return {"answer": "\n".join(lines), "package": pkg, "grounded": True}


def _suggestion_lines(pkg: dict) -> list[str]:
    sug = [x for x in (pkg.get("other_course_suggestions") or []) if x.get("type") == "topic_owner"]
    if not sug:
        return []
    out = [""]
    for x in sug:
        ch = ", ".join(str(c) for c in x.get("chapters") or []) or "?"
        out.append(f"Gợi ý: chủ đề này được dạy ở {x['course_name']} (chương {ch}); có thể tra cứu ở đó.")
    return out


def _answer_partition(pkg: dict) -> dict:
    from retrieval.courses import course_name

    name = course_name(pkg["partition"])
    lines = []
    if pkg["partition"] == "external":
        from retrieval.external import LABEL, evidence_label, record_for_item, source_text
        lines.append(LABEL)
        if not pkg['items']:
            lines.append('Chưa đủ nguồn đã xác minh: ' + ', '.join(pkg['unknowns']))
        for item in pkg['items'][:3]:
            rec = record_for_item(item) or {}
            lines += [item['excerpt'], 'Chứng cứ: ' + evidence_label(item.get('evidence_status'))]
            lines.append('Nguồn: ' + (source_text(rec) or item['source']))
            if rec.get('checked_at'):
                lines.append('Kiểm tra ngày: ' + str(rec['checked_at']))
        lines.append('Đây là ảnh chụp nguồn đã kiểm tra, không bảo đảm bao quát mọi sửa đổi. Làm bài theo giáo trình trừ khi bạn yêu cầu quy định hiện hành.')
        return {'answer':'\n'.join(lines),'package':pkg,'grounded':bool(pkg['items'])}
    if pkg["partition"] == "learner-notes":
        lines.append("Tài liệu cá nhân của bạn, không phải giáo trình.")
        items = pkg.get("items") or []
        if not items:
            lines.append("Không tìm thấy đoạn phù hợp trong kho ghi chú cá nhân đã index.")
            return {"answer": "\n".join(lines), "package": pkg, "grounded": False}
        snippet = items[0]["excerpt"].replace("\n", " ")
        if len(snippet) > 700:
            snippet = snippet[:700] + "…"
        lines += [snippet, "", "Nguồn tài liệu cá nhân:"]
        for item in items[:4]:
            lines.append(
                f"- {item['course_id']} | {item.get('source')} p.{item.get('page_range')} | authority={item.get('authority')}"
            )
        return {"answer": "\n".join(lines), "package": pkg, "grounded": True}
    if pkg["coverage"] == "insufficient":
        lines.append("CURRICULUM EVIDENCE IS INSUFFICIENT.")
        lines.append(f"Không đủ bằng chứng trong corpus đã index của {name} để trả lời như một curriculum fact.")
        if pkg.get("unknowns"):
            lines.append("Unknowns: " + ", ".join(pkg["unknowns"]))
        for it in (pkg.get("items") or [])[:3]:
            lines.append(f"- {it['course_id']} ch.{it.get('chapter')} {it.get('source')} p.{it.get('page_range')} [{it.get('source_type')}]")
        return {"answer": "\n".join(lines), "package": pkg, "grounded": False}
    theory = [it for it in pkg["items"] if it.get("source_type") in {"lecture_note", "syllabus"}]
    use = theory or pkg["items"]
    snippet = use[0]["excerpt"].replace("\n", " ")
    if len(snippet) > 700:
        snippet = snippet[:700] + "…"
    lines += [f"Answer (curriculum-grounded, {name}, tier retrieval):", snippet, "", "Source / course context:"]
    for it in use[:4]:
        lines.append(f"- {it['course_id']} | ch.{it.get('chapter')} | {it.get('source')} p.{it.get('page_range')} | "
                     f"{it.get('source_type')} | authority={it.get('authority')}")
    if pkg.get("prerequisite_evidence"):
        lines += ["", "Prerequisite evidence (không dùng để chẩn đoán):"]
        for it in pkg["prerequisite_evidence"][:3]:
            lines.append(f"- {it['course_id']} ch.{it.get('chapter')} {it.get('source')} p.{it.get('page_range')}")
    if pkg["coverage"] == "partial":
        lines.append("INFERENCE: coverage is partial; some requested facets may be missing from extracts.")
    return {"answer": "\n".join(lines), "package": pkg, "grounded": True}
