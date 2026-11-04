# G3c — Tài chính doanh nghiệp 1: GATE FAIL → tier giữ `catalog`

**Current (authorized R1 continuation): catalog.** Metadata repair is restored;
chapter@1=0.5833<0.80 after the final permitted R1 round. No ranking/authority change.
This local failure does not block Wave 6 under A2. See `R1_CONTINUATION.md`.

R1 update 2026-10-12: metadata-only candidate improved chapter@1 to 0.5833, below 0.80. All R1 changes were rolled back after the separate KTCP/KTNH promotion invariance failure. Current tier remains catalog; see `R1.md`.

Extraction 24 tài liệu / 653 trang / 797.548 ký tự / 0 lỗi và 0 page-count mismatch. `src-0165` là learner material nên để G3g; `src-0177` được include; `src-0178` bị loại khỏi index theo combined override. Dedupe: `src-0178` cov 0,9981 và `src-0172` (`Slide.pdf`) cov 0,9890 → `combined_duplicate`; `REVIEW` rỗng. Validator PASS với 29 khái niệm, không có account map; xung đột thời lượng thi 75 phút (`src-0155`, trang 2) và 90 phút (`src-0176`, trang 1) được giữ nguyên. Partition gồm 392 chunk.

Eval 20 dòng đã đóng băng (`sha256 215d84accd2b20fd242fda49fa5021666b37b7d025edf5185977b109c1073e6d`). Run 1–3 cho kết quả giống nhau; không có knob hợp lệ nào trong §6.8 thay đổi nguyên nhân.

| gate | run1 | run3 | ngưỡng | kết quả |
|---|---:|---:|---:|---|
| direct must_include@5 | 0.917 | 0.917 | 0.85 | PASS |
| direct expected_chapter@1 | 0.333 | 0.333 | 0.80 | **FAIL** |
| source_bound | 0.667 | 0.667 | 0.667 | PASS |
| insufficient | 1.0 | 1.0 | 1.0 | PASS |
| collision contamination | 0 | 0 | 0 | PASS |
| account / topic_owner | n/a | n/a | n/a | PASS |

## Nguyên nhân

Các chunk `src-0177` (hướng dẫn ôn tập, chapter null), `src-0155` và `src-0166` (giới thiệu/chương 0) chứa tên môn cùng danh sách nhiều chương, nên thắng BM25/TF-IDF top-1 ở 8/12 direct rows. Ở các dòng điển hình, chunk đúng và chunk tóm tắt đã mang cùng concept tag; alias không thể đảo thứ hạng. Dòng đề thi mẫu vẫn đạt aggregate source-bound 2/3 nhưng `src-0176` không vào top-5 vì cùng cơ chế lexical.

Sửa gốc cần D1 (`_strip_course_cues` trước BM25/TF-IDF), hiện chưa được duyệt. Tier giữ `catalog`; dữ liệu, khái niệm và partition được giữ để tái chạy nếu D1 được duyệt. Core regression: `IDENTICAL` (`reports/v3/run_20261011_115026`).
