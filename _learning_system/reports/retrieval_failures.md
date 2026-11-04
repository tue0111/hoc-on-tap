# Retrieval failures (hybrid, frozen 60)

Taxonomy used: wrong_course, wrong_chapter, wrong_concept, ranking_failure, insufficient_source, prerequisite_missing, prerequisite_overreach, authority_failure, …

Hard-gate metrics all pass. Two tests still fail.

## kttc1-08 — wrong_concept

Question: “Tổng quan về kế toán tài chính chương 1 ACCO2310 nói gì?”

- Top-5 is the right file (`Chương 1.pdf`, chapter 1).
- Expected concept `bao-cao-tai-chinh` is not tagged on those overview chunks (the phrase is later in the chapter / study guide).
- Root cause: **chunk_boundary / concept mapping**, not wrong course.
- Not fixed by a prompt. Later: map section headings in Ch1 (yếu tố BCTC) more tightly, or drop that expected concept from the test.

## pre-07 — ranking_failure

Question: “Sổ nhật ký chung ở KTTC1 liên hệ sổ sách kế toán đã học ở Nguyên lý ra sao?”

- Main hits: KTTC1 Chương 1 (correct course).
- Prereq hits: NLKT chứng từ (`src-0116`) and ghi sổ kép, **not** sổ sách `src-0117`.
- Root cause: **ranking_failure** on near-duplicate NLKT C5 units (chứng từ vs sổ sách).
- Not fixed by adding random instructions. Later: distinguish C5.1 P1 vs P2 with a stronger topic prior when “nhật ký chung” / “sổ sách” is explicit.

## Failures that were real bugs and were fixed before freeze

| issue | class | fix |
|---|---|---|
| TSCĐ in KTTC1 answered from an incidental journal example | insufficient_source | Mode A KTTC1 + TSCĐ → coverage=insufficient (no TSCĐ chapter in ACCO2310) |
| “Nợ/Có từ Nguyên lý” classified as cross_course | prerequisite_missing | Prereq cues beat dual-course → cross_course |
| VCSH asked as KTTC1 ch.3 returned HTK chapter as sufficient | insufficient_source | Topic not in KTTC1 outline → insufficient |
| Nợ phải thu ranked slides above scripts | authority_failure | Downrank `lecture_slide` vs lecture_note |

Naive system: 17 wrong_course + 5 missed insufficient. Those are the contamination/hallucination modes hybrid is meant to stop.

No failure was “fixed” by injecting IFRS or lecturer-corrections.
