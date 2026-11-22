# Học — Kế toán / Tài chính / Ngân hàng

Tài liệu ôn tập các môn: Nguyên lý kế toán, Kế toán tài chính 1–3, Kế toán chi phí, Kế toán ngân hàng, Kế toán thuế 1, Kế toán hành chính sự nghiệp, Hệ thống thông tin kế toán 1, Kiểm toán 1, Kinh doanh và nghiệp vụ, Luật kinh doanh, Ngân hàng thương mại, Thị trường tài chính, Tài chính doanh nghiệp 1, Tài chính hành chính sự nghiệp.

- `_grok_pack/` — bản tóm tắt dạng Markdown từng môn, dễ nạp vào AI (bắt đầu từ `00_MUC_LUC.md`).
- `_learning_system/` — hệ thống ôn tập (curriculum, câu hỏi, script).
- `plugins/hoc-tutor/` — **plugin Claude Code** để nạp giáo trình (marketplace: `.claude-plugin/`).
- Các thư mục môn học — tài liệu gốc (PDF, DOCX, PPTX, XLS, ghi chú).

## Nạp vào Claude Code (tra + học)

```bash
claude plugin marketplace add tue0111/hoc-on-tap
claude plugin install hoc-tutor@hoc-on-tap
```

Plugin có **MCP**: `hoc-tra-cuu` (`tra_cuu`, `mo_pack`, `muc_luc`) và filesystem read-only `_grok_pack`. Trong session: `/hoc-tutor:nap-giao-trinh` hoặc gọi MCP. Chi tiết: `plugins/hoc-tutor/README.md`.

## Thêm tài liệu mới

1. Chép file vào đúng thư mục môn (hoặc thư mục môn mới) trong `D:\Hoc`. Không sửa, không đổi tên file cũ.
2. Chạy refresh: dán `_learning_system/V3_KICKOFF_PROMPT.md` và nhắn "chạy Wave 6 refresh"
   (hoặc `python scripts/v3_refresh.py --plan` rồi `--apply` trong `_learning_system`).
   - Thư mục môn **mới** sẽ bị chặn với `NEW_COURSE`. Làm theo `_learning_system/reports/v3/PLAN_W6B_MON_MOI.md`
     (Pha A đăng ký môn → Pha B playbook từng môn → Pha C gộp, gate, `_grok_pack`).
3. **Chỉ commit và push khi** refresh/gate đã qua, regression core IDENTICAL và `_grok_pack` đã cập nhật.
   Không push riêng tài liệu thô của môn mới.
