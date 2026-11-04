# G2c — Kế toán ngân hàng: PASS (R1), tier `retrieval`

**Current: PASS / retrieval (2026-10-12).** Authorized ownership repair preserves
all seven existing-course outputs after actual promotion. Chapter@1=0.8333.
See `R1_CONTINUATION.md`; previous failures below are historical.

R1 update 2026-10-12: candidate gate passed (chapter@1 0.8333), but joint KTCP/KTNH promotion violated non-target output invariance. A2.3 STOP and full rollback; current tier remains catalog. See `R1.md`. Prior results below are historical.

Extraction 54 doc / 630 trang / 0 lỗi (4 file `tmp/` render không index; DOCX hệ thống tài khoản src-0047 đã trích bảng, authority 6);
dedupe: 9 PDF chương = combined_duplicate (Chương 1 cov 0.8995), REVIEW rỗng; validator PASS (30 khái niệm, 67 tài khoản); partition 959 chunk.
Eval 22 dòng đóng băng, 3 lần chạy, 2 vòng tuning (alias).

| gate | run1 | run3 | ngưỡng | kết quả |
|---|---|---|---|---|
| direct_must_include | 0.917 | 0.917 | 0.85 | PASS |
| direct_chapter_at1 | 0.75 | 0.75 | 0.80 | **FAIL** (9/12; cần 10/12) |
| source_bound | 1.0 | 1.0 | 0.67 | PASS |
| insufficient (A1) | 1.0 | 1.0 | 1.0 | PASS (kiểm lại G3x) |
| collision | 0 | 0 | 0 | PASS |
| account | 1.0 | 1.0 | 0.5 | PASS |

## Nguyên nhân (3 dòng trượt)
- kn-d02, kn-d06: chunk mở đầu chương 4 (src-0271-0002, "kế toán ngân hàng thực hiện nghiệp vụ như thế nào…") thắng chunk đúng chỉ 0.693 vs 0.675/0.691 vì tên môn trong câu hỏi ("kế toán ngân hàng", "nghiệp vụ") trùng chữ với đoạn giới thiệu chung. Alias không đổi được. Gốc rễ giống KTCP.
- kn-d10: câu hỏi chứa cả cue KTNH và cue NHTM ("ngân hàng thương mại") → `detect_courses` ra 2 môn → ambiguous → đi đường legacy (đúng spec 4.3, nhưng dòng eval do tao viết mơ hồ).

## Đề xuất cho Opus (không tự làm vì ngoài knob cho phép)
Bỏ các token cue của môn (kể cả tên môn) khỏi truy vấn lexical trong `retrieve_partition` (đã có `_strip_course_cues`). Có thể cứu cả KTCP (d01/d02/d10) và KTNH (d02/d06). Cần re-run toàn bộ eval đã đóng băng khi áp dụng.

Trạng thái: tier = `catalog`; data/partition/khái niệm giữ trên D:. Core regression IDENTICAL.
