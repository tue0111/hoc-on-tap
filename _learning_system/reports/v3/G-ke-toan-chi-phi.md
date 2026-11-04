# G2a — Kế toán chi phí: PASS (R1 + D2 waiver), tier `retrieval`

**Current: PASS / retrieval (2026-10-12).** Authorized ownership repair preserves
all seven existing-course outputs after actual promotion. Chapter@1=0.80;
**D2 waiver** excludes only kp-t01..03. See `R1_CONTINUATION.md`; previous failures below are historical.

R1 update 2026-10-12: candidate gate passed with **D2 waiver** (only kp-t01..03 excluded), but promotion changed other-course coverage. A2.3 STOP and full rollback; current tier remains catalog. See `R1.md`. Prior results below are historical.

Extraction 45 doc / 405 trang / 0 lỗi; dedupe: 7 PDF chương = combined_duplicate, REVIEW rỗng; validator PASS (30 khái niệm, 7 tài khoản);
partition 362 chunk (index 3.0.0 đã build). Eval 23 dòng đóng băng (sha trong evals/v3/FROZEN.json), 3 lần chạy (run1..run3), 2 vòng tuning (chỉ alias).

| gate | run1 | run3 | ngưỡng | kết quả |
|---|---|---|---|---|
| direct_must_include | 0.90 | 0.90 | 0.85 | PASS |
| direct_chapter_at1 | 0.70 | 0.70 | 0.80 | **FAIL** |
| source_bound | 1.0 | 1.0 | 0.67 | PASS |
| insufficient (A1, hoãn sang G3x) | 1.0 | 1.0 | 1.0 | PASS |
| collision contamination | 0 | 0 | 0 | PASS |
| account | 1.0 | 1.0 | 0.5 | PASS |
| topic_owner | 0 | 0 | 1.0 | **FAIL (lỗi thiết kế eval)** |

## Nguyên nhân
1. direct_chapter_at1 (d01, d02, d10): bản script dùng từ ngữ rải rác (vd "cố định" thay vì "định phí"), chương 6 nhắc chi phí trực tiếp/gián tiếp dày hơn chương 2, và tài liệu "Hướng dẫn ôn tập" (chapter=None) xếp hạng 1 với d10. Alias không đổi được thứ hạng; trọng số hybrid bị cấm chỉnh.
2. topic_owner (kp-t01..t03): do tôi viết sai kỳ vọng. Spec 4.3 chỉ phát gợi ý khi coverage != sufficient HOẶC câu hỏi không có core cue. KTTC1 (core) có chương chi phí nên trả `sufficient` → engine đúng khi KHÔNG phát gợi ý. File eval đã đóng băng nên không sửa; ghi nhận là FAIL trung thực. Nên có dòng topic_owner không kèm core cue (vd "Sản lượng tương đương tính thế nào?") nếu được duyệt.

## Trạng thái
Tier = `catalog`. Dữ liệu/partition/khái niệm giữ nguyên trên D: để Opus quyết định (nới gate chapter@1 hoặc cho thêm file eval topic_owner bổ sung). Lỗi cục bộ cho KTCP → tiếp tục khóa tiếp theo.
