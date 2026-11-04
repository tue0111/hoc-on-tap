# G3b — Luật kinh doanh: PASS (tier `retrieval`)

Extraction 17 tài liệu / 95 trang / 142.860 ký tự / 0 lỗi; page count khớp, không có `UNPARSED` hay tài liệu mỏng. Dedupe không có cặp cần xử lý và `REVIEW` rỗng. Validator PASS với 18 khái niệm, không có account map. Partition 3.0.0 gồm 177 chunk, vocab 1.017; mọi tài liệu được index đều có chunk và mọi source hash thuộc inventory.

Eval 20 dòng đã đóng băng sau lần chạy đầu (`sha256 1d66c7351b6d868e3f9282645f85fc3ec2b32e75b77d62db6af391a8e8263045`); không cần tuning.

| gate | giá trị | ngưỡng | kết quả |
|---|---:|---:|---|
| direct must_include@5 | 1.0 | 0.85 | PASS |
| direct expected_chapter@1 | 0.917 | 0.80 | PASS |
| source_bound | 1.0 | 0.67 | PASS |
| insufficient | 1.0 | 1.0 | PASS |
| collision contamination | 0 | 0 | PASS |
| account / topic_owner | n/a | n/a | PASS |

`lk-d05` có tài liệu hướng dẫn học đứng top-1 nhưng source đúng vẫn ở top-5; gate chapter@1 vẫn đạt 11/12. Core regression: `IDENTICAL` (`reports/v3/run_20261011_114404`).
