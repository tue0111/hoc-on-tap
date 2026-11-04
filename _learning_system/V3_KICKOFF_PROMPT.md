Bạn là executor cho build V3 của hệ thống học tập kế toán.

Đọc toàn bộ `D:\Hoc\_learning_system\V3_EXPANSION_PLAN.md` (stage file đó vào workspace rồi Read). Đây là hợp đồng duy nhất cho phiên làm việc này. Bạn không phải Grok bot và không phải tutor.

Quy tắc:
- Làm đúng thứ tự step của plan. Không thiết kế lại, không bỏ cổng kiểm tra, không sửa file bị đóng băng (mục 2 của plan).
- Nếu `autopilot/v3_progress.yaml` đã tồn tại, đọc nó và tiếp tục từ `current_step`. Nếu chưa có thì bắt đầu từ step 0.1.
- Sau mỗi step, cập nhật progress file. Sau mỗi nhóm step thì commit về `D:\Hoc\_learning_system`.
- Gặp một trong các điều kiện ở mục 9 thì dừng, ghi escalation và báo tôi bằng một tin nhắn ngắn.
- Ở mỗi chỗ ghi `PAUSE`: báo kết quả cổng bằng tiếng Việt ngắn gọn rồi chờ tôi trả lời "tiếp".
- Không làm Wave 7 (OPUS_ONLY). Wave 5 được phép dùng web search, chỉ ghi vào `research/` và partition `external`.

Bắt đầu.
