# G3e — Thị trường tài chính: PASS (tier `retrieval`)

Hash-check đạt 14/14. Extraction 14 tài liệu / 318 trang / 167.990 ký tự / 0 lỗi; page count khớp, không có `UNPARSED` hay tài liệu mỏng. Dedupe không có cặp chapter-vs-unit hoặc slide gộp và `REVIEW` rỗng. Validator PASS với 27 khái niệm; xung đột nguồn “Chương 6 là chương cuối cùng” trong khi `src-0147`/`src-0154` vẫn có Chương 7 được giữ ở trạng thái `UNKNOWN`. Partition gồm 196 chunk, vocab 1.317.

Eval 20 dòng đã đóng băng ngay sau lần chạy đầu (`sha256 2fcdb4464517dde4735bab3556afa5df6a223dfbf443d5ae48c9c0cf9fd20dea`); không cần tuning.

| gate | giá trị | ngưỡng | kết quả |
|---|---:|---:|---|
| direct must_include@5 | 1.0 | 0.85 | PASS |
| direct expected_chapter@1 | 1.0 | 0.80 | PASS |
| source_bound | 1.0 | 0.67 | PASS |
| insufficient | 1.0 | 1.0 | PASS |
| collision contamination | 0 | 0 | PASS |
| account / topic_owner | n/a | n/a | PASS |

Core regression: `IDENTICAL` (`reports/v3/run_20261011_115804`).
