---
name: nap-giao-trinh
description: >
  Nạp / mở gói giáo trình _grok_pack vào session Claude Code. Dùng khi Tuệ nói
  "nạp", "mở môn", "ôn [tên môn]", hoặc bắt đầu buổi học. Slash: /nap-giao-trinh.
---

# Nạp giáo trình (_grok_pack)

## Mục tiêu

Đưa đúng file chữ của môn vào ngữ cảnh session để tutor trả lời bám giáo trình, không đoán.

## HOC_ROOT

Repo root chứa `_grok_pack/`. Trên máy Tuệ: thường `D:\Hoc`.

## Quy trình nạp

1. Đọc `_grok_pack/00_HUONG_DAN_GROK.md` (luật tutor) nếu chưa nạp trong session.
2. Đọc `_grok_pack/00_MUC_LUC.md` để map môn → file.
3. Xác định môn Tuệ muốn. Nếu mơ hồ (vd. "HCSN"), hỏi một câu rồi dừng.
4. Mở **đúng file** (và `_p1`/`_p2` nếu có). Không nạp cả pack trừ khi Tuệ bảo "nạp hết".
5. Tóm tắt ngắn: môn, số chương có trong pack, sẵn sàng hỏi gì.
6. Với NLKT / KTTC1, ưu tiên thêm CLI:

```bash
cd HOC_ROOT/_learning_system
python -m retrieval.cli retrieve "CÂU HỎI" --course <id>
```

## Bảng file nhanh

| File | Môn |
|---|---|
| 01 | Kế toán tài chính 1 (ACCO2310) |
| 02 | Nguyên lý kế toán (ACCO1325) |
| 03 | Kế toán tài chính 2 |
| 04 | Kế toán chi phí |
| 05 | Kiểm toán 1 |
| 06 `_p1`/`_p2` | Kế toán ngân hàng |
| 07 `_p1`/`_p2` | Kinh doanh và nghiệp vụ |
| 08 | Luật kinh doanh |
| 09 | Ngân hàng thương mại |
| 10 | Thị trường tài chính |
| 11 `_p1`/`_p2` | Tài chính hành chính sự nghiệp |
| 12 | Tài chính doanh nghiệp 1 |
| 13–16 | Ghi chú / bài làm cá nhân |
| 17 | Văn bản pháp quy |
| 18 | Hệ thống thông tin kế toán 1 |
| 19 | Kế toán thuế 1 |
| 20 | Kế toán tài chính 3 |
| 21 `_p1`/`_p2` | Kế toán hành chính sự nghiệp |

## Ví dụ lệnh người dùng

- `/hoc-tutor:nap-giao-trinh KTTC1`
- "Nạp Kiểm toán 1"
- "Ôn thuế GTGT" → nạp file 19, tìm chương GTGT trong mục lục

## Sau khi nạp

Giữ luật tutor (`tutor-hoc`): trích nguồn, không bịa, đúng môn. Không sửa file gốc.
