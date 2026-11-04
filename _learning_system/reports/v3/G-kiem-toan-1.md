# G2b — Kiểm toán 1 (kiem-toan-1): PROVISIONAL PASS (tier `retrieval`; gate insufficient hoãn sang G3x theo Amendment A1)

Extraction 33 doc / 368 trang / 0 lỗi; dedupe: 6 PDF chương = combined_duplicate (Chương 1 cov 0.8937), REVIEW rỗng; validator PASS (40 khái niệm, không có account_map vì môn không có tài khoản);
partition 358 chunk. Eval 20 dòng đóng băng, chạy 1 lần, không cần tuning.

| gate | giá trị | ngưỡng | kết quả |
|---|---|---|---|
| direct_must_include | 1.0 | 0.85 | PASS |
| direct_chapter_at1 | 1.0 | 0.80 | PASS |
| source_bound | 1.0 | 0.67 | PASS |
| insufficient | 0.667 | 1.0 | hoãn → G3x (A1); kt-i03 "giá thành theo quy trình" trả `partial` |
| collision contamination | 0 | 0 | PASS |
| account / topic_owner | n/a | – | không có dòng (không có tài khoản; topic_owner chỉ Wave 1) |

Ghi chú: kt-i03 có thể do KTCP đang `catalog` nên không là đối thủ trong rival check; chạy lại ở G3x khi mọi môn đã nạp.
TITLE_VARIANT: Chương 6 "Hoàn thành kiểm toán" (script) vs "Báo cáo kiểm toán" (ôn tập) → cả hai là tên của khái niệm `kt1-hoan-thanh-kiem-toan`.
Core regression: IDENTICAL.
