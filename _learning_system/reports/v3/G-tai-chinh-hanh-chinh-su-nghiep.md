# G3f — Tài chính hành chính sự nghiệp: PROVISIONAL PASS (tier `retrieval`)

Hash-check đạt 14/14. Extraction 14 tài liệu / 1.191 trang / 888.967 ký tự / 0 lỗi; page count khớp, không có `UNPARSED` hay tài liệu mỏng. Dedupe: `src-0186` cov 0,9998 và slide gộp `src-0191` cov 0,9996 → `combined_duplicate`; `REVIEW` rỗng. Validator PASS với 26 khái niệm; xung đột hình thức thi và số chủ đề được giữ tách biệt. Partition gồm 768 chunk, vocab 1.431.

Eval 20 dòng đã đóng băng ngay sau lần chạy đầu (`sha256 6365ddfa557dd2caeee16bb2ffa75173e1fc78ce208d74a9998dde4452689b24`); không cần tuning. Gate `insufficient` được hoãn sang G3x theo Amendment A1.

| gate | giá trị | ngưỡng | kết quả |
|---|---:|---:|---|
| direct must_include@5 | 1.0 | 0.85 | PASS |
| direct expected_chapter@1 | 0.833 | 0.80 | PASS |
| source_bound | 0.667 | 0.667 | PASS |
| insufficient | 0.667 | 1.0 | DEFERRED → G3x |
| collision contamination | 0 | 0 | PASS |
| account / topic_owner | n/a | n/a | PASS |

Hai direct row (`hcsn-d04`, `hcsn-d08`) và một source-bound row (`hcsn-s01`) trượt riêng lẻ nhưng aggregate vẫn đạt gate; eval giữ nguyên theo freeze rule. Core regression: `IDENTICAL` (`reports/v3/run_20261011_120239`).
