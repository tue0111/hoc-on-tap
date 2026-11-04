# G3a — Kinh doanh và nghiệp vụ: PROVISIONAL PASS (tier `retrieval`)

Extraction 36 tài liệu / 225 trang / 436.837 ký tự / 0 lỗi; page count khớp, không có `UNPARSED` hay tài liệu mỏng. Dedupe không có cặp cần xử lý và `REVIEW` rỗng. Validator PASS với 25 khái niệm, không có account map. Partition 3.0.0 gồm 521 chunk, vocab 2.086; mọi tài liệu được index đều có chunk và mọi source hash thuộc inventory.

Eval 20 dòng đã đóng băng sau lần chạy đầu (`sha256 892eeb3f66ca29e2f4d96613767f2854386c42a039b9b8f4a436c6b3fb381e38`); không cần tuning.

| gate | giá trị | ngưỡng | kết quả |
|---|---:|---:|---|
| direct must_include@5 | 1.0 | 0.85 | PASS |
| direct expected_chapter@1 | 1.0 | 0.80 | PASS |
| source_bound | 1.0 | 0.67 | PASS |
| insufficient | 0.667 | 1.0 | hoãn đến G3x theo Amendment A1 |
| collision contamination | 0 | 0 | PASS |
| account / topic_owner | n/a | n/a | PASS |

`kd-i03` (thuế thu nhập hoãn lại) hiện trả `partial`; sẽ được kiểm lại tại G3x khi các partition Wave 3 đã index. Core regression: `IDENTICAL` (`reports/v3/run_20261011_114131`).
