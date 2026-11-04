# G3d — Ngân hàng thương mại: PASS (tier `retrieval`)

Extraction 20 tài liệu / 986 trang / 692.683 ký tự / 0 lỗi; page count khớp, không có `UNPARSED` hay tài liệu mỏng. `src-0139` và `src-0140` là learner material nên không vào partition môn. Dedupe: `src-0130` cov 0,9034 và slide gộp `src-0138` cov 0,9972 → `combined_duplicate`; `REVIEW` rỗng. Validator PASS với 23 khái niệm; xung đột Luật các TCTD 47/2010/QH12 (`src-0124`, trang 2) và 32/2024/QH15 (`src-0128`, trang 7) được giữ tách biệt. Partition gồm 357 chunk, vocab 1.602.

Eval 20 dòng đã đóng băng sau lần chạy đầu (`sha256 3d3dbe4bccd66897c6c84ce0c7f8e74951a8b7c687f297486f538372670fcb9b`); không cần tuning.

| gate | giá trị | ngưỡng | kết quả |
|---|---:|---:|---|
| direct must_include@5 | 0.917 | 0.85 | PASS |
| direct expected_chapter@1 | 0.833 | 0.80 | PASS |
| source_bound | 1.0 | 0.67 | PASS |
| insufficient | 1.0 | 1.0 | PASS |
| collision contamination | 0 | 0 | PASS |
| account / topic_owner | n/a | n/a | PASS |

Hai direct row (`nh-d01`, `nh-d11`) trượt riêng lẻ nhưng aggregate vẫn đạt gate; eval giữ nguyên theo freeze rule. Core regression: `IDENTICAL` (`reports/v3/run_20261011_115403`).
