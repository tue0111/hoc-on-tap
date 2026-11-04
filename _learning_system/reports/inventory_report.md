# Inventory report — Phase 0–1

Generated: 2026-09-07  
Source root: `D:\Hoc`  
Output root: `D:\Hoc\_learning_system`  
Layer: curriculum inventory only.

## Scope

Recursive scan of `D:\Hoc` excluding `_learning_system`.

| Item | Count | Evidence |
|---|---|---|
| Course folders | 12 | OBSERVED directory names |
| Source files | 192 | OBSERVED |
| PDF | 187 | OBSERVED |
| DOCX | 4 | OBSERVED |
| PPTX | 1 | OBSERVED |
| Exact SHA-256 duplicate groups | 0 | OBSERVED |
| Parse errors (open/extract crash) | 0 | OBSERVED |
| Likely-scanned PDFs (empty text layer) | 0 | OBSERVED |

No extra top-level folders or files besides the 12 courses (and this system directory).

## Files per course

| course_id | folder | files |
|---|---|---|
| kinh-doanh-va-nghiep-vu | Kinh doanh và nghiệp vụ | 36 |
| nguyen-ly-ke-toan | Nguyên lý kế toán | 28 |
| tai-chinh-doanh-nghiep-1 | Tài chính doanh nghiệp 1 | 24 |
| ngan-hang-thuong-mai | Ngân hàng thương mại | 20 |
| luat-kinh-doanh | Luật kinh doanh | 17 |
| thi-truong-tai-chinh | Thị trường tài chính | 14 |
| tai-chinh-hanh-chinh-su-nghiep | Tài chính hành chính sự nghiệp | 14 |
| ke-toan-tai-chinh-1 | Kế toán tài chính 1 | 12 |
| ke-toan-ngan-hang | Kế toán ngân hàng | 10 |
| ke-toan-tai-chinh-2 | Kế toán tài chính 2 | 7 |
| ke-toan-chi-phi | Kế toán chi phí | 5 |
| kiem-toan-1 | Kiểm toán 1 | 5 |

## Filename-heuristic roles (inventory pass)

These are **filename** roles. Content inspection overrode several (see `curriculum/source_registry_overrides.yaml`).

| role | count |
|---|---|
| lecture_note | 121 |
| lecture_slide | 33 |
| unknown | 12 |
| summary | 8 |
| exam | 7 |
| syllabus | 5 |
| assignment | 3 |
| textbook (filename heuristic) | 2 |
| reference | 1 |

After inspection, the large course-named PDFs are **compiled scripts**, not textbooks. True bound textbooks cited in intros are mostly **absent** from the folders.

## Same filename, different courses

`Chương N.pdf` and `Slide Chương N.pdf` collide across courses. Retrieval must key on `course_id`, not filename. This is a filename collision, not a content duplicate (SHA-256 groups = 0).

## Nested folders

| path | role |
|---|---|
| Kiểm toán 1/Thảo luận 1, Thảo luận 2 | assignment |
| Kế toán chi phí/Thảo luận 1 | assignment |
| Kế toán ngân hàng/tmp/** | generated render artifacts — **not curriculum** |
| Kế toán tài chính 2/tmp/** | generated render artifacts — **not curriculum** |

## Parseability

- All 187 PDFs opened. Text layer present on extracted pages.
- Slide PDFs are often **image-heavy**: extract_ok true but char_count on first pages is thin. PDF bookmarks are the better TOC for those files.
- Chapter scripts (`BÀI GIẢNG DẠNG VĂN BẢN`) extract well.
- Large files were page-capped (typically first 6–8 pages). Full-body extraction is a later phase.
- `Bảng hệ thống tài khoản kế toán ngân hàng.docx`: 174 characters — tables not in paragraph XML.
- `Corporate_Finance_Blueprint.pptx`: not extracted (`python-pptx` missing).
- TCDN1 `TCDN1-Tailieuhuongdanntap.docx`: 412 characters — thin.

## Course codes OBSERVED in documents

| code | course | conflict |
|---|---|---|
| ACCO1305 | Kinh doanh và nghiệp vụ | no |
| ACCO1325 | Nguyên lý kế toán | no |
| ACCO2310 | Kế toán tài chính 1 | no |
| ACCO1334 and ACCO2315 | Kế toán tài chính 2 | **yes** — official code UNKNOWN |
| ACCO1331 | Kế toán ngân hàng | no |

## Year tokens

- `2025` on NHTM sample exam filename.
- `2022` on TCHCSN exam and ôn tập.

Semester for every course: **UNKNOWN**.

## Source integrity

Phase 0–1 wrote only under `D:\Hoc\_learning_system`. Inventory SHA-256 is the baseline for later verification.
