# Source coverage — NLKT + KTTC1 (Phase 2 full extract)

Page cap from Phase 0–1 is removed. 40 documents, 1512 pages, 1,157,630 characters. Parse errors: 0. Document-level `thin` flags: 0.

## KTTC1 — extract growth vs Phase 0–1

| source | pages | phase0 chars | phase2 chars | index |
|---|---|---|---|---|
| Chương 1.pdf | 40 | 14486 | 74094 | yes |
| Chương 2.pdf | 60 | 11723 | 83346 | yes |
| Chương 3.pdf | 55 | 9617 | 85699 | yes |
| Slide Chương 1–3 | 116/196/153 | ~900–1300 | 27798 / 42235 / 38153 | yes |
| KTTC 1.pdf combined | 158 | 10229 | 247579 | **no** (duplicate) |
| Slide KTTC 1.pdf combined | 476 | 1440 | 109900 | **no** (duplicate) |
| Đề thi mẫu + Hướng dẫn + Ch0 | 3+3+3 | full already | full | yes |

Slides have a text layer but remain lower-density than scripts. Bookmarks are stored on the document record. No OCR in this phase.

## NLKT

Topic scripts were already short (2–11 pages) and fully extracted in Phase 0–1. Phase 2 re-extracted without a cap; char counts match. Combined `Nguyên Lý Kế Toán.pdf` (119 pages, 213620 chars) is coverage-only, not indexed.

## Index

- 810 chunks from 37 indexed documents
- vocab 1981
- index version 2.0.0 at `data/indexes/2.0.0/`

## Blockers

None that prevent the slice. Slide density is the main residual limitation for “slide-only” questions; scripts remain the theory authority.
