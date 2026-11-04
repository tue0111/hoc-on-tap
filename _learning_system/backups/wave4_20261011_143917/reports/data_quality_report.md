# Data quality report

## Phase 2.1 increment

- Files: 192 → **333** (141 NEW, 0 CHANGED, 0 MISSING).
- Old source_ids preserved.
- `_nguon/` unit scripts are catalogued, not fully extracted.
- TITLE_VARIANT: Kiểm toán 1 Ch6 script “Hoàn thành kiểm toán” vs ôn tập “Báo cáo kiểm toán”.
- KTTC2 new Ch3 still uses **ACCO1334** (same as Ch1 body / Ch2), not ACCO2315.
- Phase 2 retrieval index not rebuilt.

## Phase 0–1 checklist (historical)

## Validation checklist

| # | Check | Result |
|---|---|---|
| 1 | Every folder under `D:\Hoc` scanned | **Pass** — 12 course folders, **333 files** after Phase 2.1 |
| 2 | Files with unknown role | **Yes** — 12 filename-unknown; several resolved by content overrides |
| 3 | Notable duplicates | **No exact hashes**. Combined PDFs duplicate topic/chapter scripts. Filename collisions (`Chương 1.pdf`) across courses |
| 4 | Courses missing a dedicated syllabus file | **Most**. Functional intros exist as Chương 0 / giới thiệu PDFs for many courses. TTTC has no course intro, only chapter 1 |
| 5 | Exercises without theory | **No course is exercise-only**. Inverse is common: theory without standalone exercise books |
| 6 | Parse failures | **No crashes**. Thin text: slides, one DOCX chart of accounts, one PPTX, one ôn tập DOCX |
| 7 | Prerequisites attached from guesswork | **Avoided**. Inferred edges are labeled. Course-name “2 after 1” is not used as the sole KTTC2 prereq; a document quote exists |
| 8 | Semester/year undetermined | **All courses**. Two document-year tokens (2022, 2025) only |
| 9 | Concept ID / alias conflicts | **One title conflict**: KDNV script also says “Kế toán và doanh nghiệp”. KTTC2 course-code conflict ACCO1334 vs ACCO2315 |
| 10 | Source files outside `_learning_system` modified | **Intended none**. Recheck hashes vs `inventory/files.json` |

## Completeness by course

| course | syllabus/intro | theory | exercises | solutions | exams | advertised vs files |
|---|---|---|---|---|---|---|
| KDNV | yes (C0 + script) | yes | in-script / quizzes on LMS not in folder | no file | sample exam | 6/6 |
| NLKT | no dedicated file | yes | in-script only | no | no | 6/6 |
| KTTC1 | study guide + C0 | yes | mentioned, file not in folder | answer key on sample exam | sample exam | 3/3 |
| KTTC2 | intro embedded in Ch1 | yes (1–4) | Đề 2 + đề mẫu | no separate key | đề mẫu (2.1) | **4/4** |
| KTCP | intro embedded in Ch1 | yes (1–7) | thảo luận | no | đề mẫu (2.1) | **7/7** |
| Kiểm toán 1 | intro embedded in Ch1 | yes (1–6) | 2 thảo luận | no | đề mẫu (2.1) | **6/6** |
| KTNH | intro embedded in Ch1 | yes (1–9) | no standalone booklet | no | đề mẫu (2.1) | **9/9** |
| NHTM | C0 + slide 0 | yes | ôn tập / sổ tay | answers on sample exam | 2025 sample | 6 content + intro |
| TCDN1 | C0 | yes | sổ tay / ôn tập | đáp án đề mẫu | đề mẫu | 9/9 scripts; slides incomplete |
| TTTC | no | yes | no | no | no | 7 files, advertised count UNKNOWN |
| TCHCSN | no dedicated C0 | yes | ôn tập 2022 | no separate key | 2022 sample | 6 files |
| LKD | C0 + hướng dẫn | yes | in-script | exam includes answers | sample exam | 5/5 |

Legend: **complete / partial / missing / ambiguous**.

## Ambiguous / conflicting material

1. **KTTC2 course code**: ACCO2315 on embedded Chương 0; ACCO1334 on Ch1 body, Ch2, Đề 2. Official code UNKNOWN.
2. **NHTM law vintage**: lecture scripts cite Luật các TCTD 2010; 2025 sample exam cites 32/2024/QH15. Keep both; do not merge.
3. **TCDN1 exam duration**: Chương 0 says 75 minutes; đề mẫu / sổ tay say 90 minutes.
4. **KTTC1 HUONG DAN**: under chapter 3 heading, leftover “nợ phải thu” sentences.
5. **KTNH Ch2 title**: intro “tiền mặt” vs file “ngân quỹ”.
6. **NHTM chapter count**: “7 chương” then lists 1–6.
7. **KDNV alternate title** “Kế toán và doanh nghiệp” inside one intro script.
8. **Compiled PDFs** look like textbooks by filename/size; they are script concatenations.

## Thin or incomplete extracts

- Slide PDFs: low character counts, use bookmarks.
- Harvest cap of 6–8 pages on long scripts: later chủ đề often known only from PDF outlines.
- KTNH chart of accounts DOCX: tables missing.
- `Corporate_Finance_Blueprint.pptx`: not parsed.
- tmp/render PDFs skipped by design.

## Coverage gaps that block later diagnosis

- No learner attempts in the corpus → cannot populate mastery.
- Missing advertised chapters (KTTC2 3–4, KTCP 5–7, Audit 4–6, KTNH 6–9) → cannot retrieve those topics from this dump.
- Missing solution books for most courses.
- TTTC has no assessment artifacts.

## Quality classes

**Complete enough for retrieval of taught theory:** NLKT, KDNV, LKD, KTTC1, NHTM, TCDN1, TTTC, TCHCSN (with the extract-page cap).

**Partial (advertised outline longer than files):** KTTC2, KTCP, Kiểm toán 1, KTNH.

**Missing official syllabus PDF:** all except functional C0/study-guide stand-ins.

**Ambiguous identifiers:** KTTC2 course code; several combined PDFs.
