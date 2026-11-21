# G-he-thong-thong-tin-ke-toan-1: Hệ thống thông tin kế toán 1 (ACCO3315)

W6b pha B, 2026-11-21. Playbook §6 bước 6.1 đến 6.9. Tier vẫn là `catalog`. Pha C đổi tier sau khi gộp và chạy regression.

**Kết quả: ĐẠT (tạm thời).** Mọi tiêu chí trong phạm vi môn đều đạt ở lần chạy đầu và không cần tinh chỉnh vòng nào. Tiêu chí regression core để Pha C chạy (C2), vì pha B không được phép chạy `v3_regression.py`.

## 6.1 Nguồn
- Inventory có 67 dòng (src-0340..src-0406). Đã kiểm sha256 và size của cả 67 file: khớp hết, không file nào thiếu, không có file ngoài inventory (`work/he-thong-thong-tin-ke-toan-1/hash_check.json`).

## 6.2 Extract
- Có 27 PDF extract OK, tổng 526 trang, 951.080 ký tự. Số trang pypdf khớp ở cả 27 file. UNPARSED: không có. THIN: không có.
- Có 21 PPTX bị ghi `pptx extractor not wired (non-learner pptx)`. Đây là hành vi đã định trong PLAN_W6B §3, không phải lỗi extract. Chủ đề nào cũng có script PDF, **trừ Ch4 4.1 (sổ chi tiết thanh toán), 4.2 (sổ chi tiết tiền mặt), 4.3 (sổ chi tiết hàng tồn kho)**. Ba chủ đề này chỉ có PPTX (src-0370..0372), nên ở dạng `not_extracted`. Text duy nhất về chúng nằm trong hướng dẫn ôn tập src-0406 tr.3 và Tailieuthamkhao_Chuong4 src-0376. Muốn bật extractor PPTX thì phải sửa engine, nên cần Pha C hoặc Opus quyết định. Pha B không làm.
- 19 file `.xls`/`.xlsm` được bỏ qua (`index_include: false`, unsupported_extension) và không chuyển đổi.
- Lỗi extract ngoài PPTX: 0.
- Chương lấy từ `apparent_chapter` trong inventory (parse_rule `inventory_apparent`). Chủ đề lấy từ dòng "Chủ đề k: …" ở trang 1 → `N.k` (`work/.../set_topics.py`, chỉ ghi vào file normalized của môn này). Kết quả gán chủ đề cho 18 script: Ch0, Ch1, 2.1–2.3, 3.1–3.3, 4.4–4.6, 5.1–5.4, 6.1–6.3.
- Script ch3–5 và chương mở đầu có lỗi dấu tổ hợp tách rời (ví dụ "Ky ̃thuâṭ"). Lỗi này ít (≤77 ký tự mỗi file) và không ảnh hưởng gate.

## 6.3 Dedupe
- `v3_dedupe.py`: 0 cặp, REVIEW = [] (`reports/v3/he-thong-thong-tin-ke-toan-1_dedupe.json`). Môn này không có thư mục `_nguon`, nên quy tắc 7.3 không có cặp chương ↔ unit nào để so.
- Bằng chứng bổ sung (`he-thong-thong-tin-ke-toan-1_dedupe_pairwise.json`): đã chấm 220 cặp cùng chương bằng chính hàm `compare()` (shingle 8 token). cov lớn nhất là 0.297, tất cả `both_canonical`. Các bản `script (n).pdf` **không trùng nhau**: mỗi bản là một chủ đề khác (content_hash khác nhau, dòng "Chủ đề" khác nhau). Không có dup_group. Không có cặp REVIEW.

## 6.4–6.5 Concept
- Có 36 concept, prefix `httt1-`, `same_as` để null hết. Lý do: các khái niệm core (bảng cân đối kế toán, BCKQKD, LCTT, sổ sách) không đồng nghĩa với kỹ thuật lập chúng trên bảng tính.
- Ba nhóm canonical_name:
  - lấy nguyên văn từ heading chương hoặc chủ đề (script, hoặc hướng dẫn ôn tập src-0406 khi heading trong script bị lỗi dấu);
  - nhóm hàm lấy từ heading "1. Nhóm hàm Logic"… ở src-0355 tr.2;
  - riêng `sheet BDMTK` và `sheet SOKTMAY` là thuật ngữ xuyên chủ đề, lấy nguyên văn trong text (src-0353 tr.1), không phải từ heading.
- account_map có 8 tài khoản, mỗi tài khoản xuất hiện ≥2 lần: 621, 154, 6279, 911, 4212, 5111, 1521, 331.
- Có 3 edge `explicit_sequence`, mỗi edge có câu trích (src-0363 tr.3, src-0364 tr.3, src-0365 tr.2).
- Validator: **PASS** (36 concept). Validator dùng chung chưa có PREFIX cho môn mới, nên tôi bổ sung PREFIX trong bộ nhớ qua `work/.../validate.py`. Không sửa script. Đề xuất Pha C thêm `"he-thong-thong-tin-ke-toan-1": "httt1"`.
- Tiền đề: chỉ có một câu trích "Môn học HTTTKT 1 là môn chuyên ngành; được học sau môn kế toán tài chính." (src-0404 tr.2). Câu này nói về họ môn KTTC, không rõ phần nào (UNKNOWN). Text không nhắc NLKT. Tôi chỉ ghi đề xuất, không ghi vào registry.
- TITLE_VARIANT: Ch4 có "Kỹ thuật lập các sổ chi tiết…" (script), "…lập sổ chi tiết…" (ôn tập) và "Kỹ thuật lập các sổ kế toán" (src-0404). Ch6 có "Lập báo cáo tài chính trên bảng tính" (script) và "KỸ THUẬT LẬP BÁO CÁO TÀI CHÍNH" (ôn tập).

## 6.6 Partition
- 27 tài liệu được index. 1036 chunk, vocab 6583, dup_groups 0. Tài liệu nào được index cũng có chunk. source_hashes (27) ⊆ inventory.
- Riêng src-0341 (Owen, tiếng Anh) chiếm 804/1036 chunk.

## 6.7 Eval (viết trước khi tinh chỉnh, đã đóng băng)
- `evals/v3/he-thong-thong-tin-ke-toan-1_retrieval.jsonl` có 24 dòng: 14 direct, 3 source_bound, 3 insufficient, 2 collision, 2 account. sha256 `dee08790290945add182df20591b77d24c1bb00df58a84661e4f6e81bb890792`.
- Lần chạy đầu: `reports/v3/he-thong-thong-tin-ke-toan-1_eval_run1.json`. Entry đóng băng: `reports/v3/he-thong-thong-tin-ke-toan-1_frozen_entry.json`.
- Runner chạy với tier `retrieval` đặt trong bộ nhớ (`work/.../run_eval.py`, giống cách `v3_r1_check.py` làm). Registry giữ nguyên.

| Tiêu chí | Giá trị | Ngưỡng | Đạt |
|---|---|---|---|
| direct must_include@5 | 14/14 = 1.00 | ≥0.85 | ✔ |
| direct expected_chapter@1 | 13/14 = 0.929 | ≥0.80 | ✔ |
| source_bound | 2/3 = 0.667 | ≥2/3 | ✔ |
| insufficient | 3/3 = 1.00 | 1.00 | ✔ |
| collision contamination | 0 | 0 | ✔ |
| account | 2/2 = 1.00 | ≥1/2 | ✔ |
| topic_owner | n/a (không có dòng) | 1.00 | ✔ |

Các dòng trượt:
- ht-d09 (sổ cái tài khoản tổng hợp): top-1 là src-0390 ch5. src-0378 có trong top-5.
- ht-s02 (đề thi mẫu): src-0405 không có trong top-5. Phân vùng không có `source_type` filter nếu caller không truyền.

## 6.8 Tinh chỉnh
- 0 vòng. Gate đạt ngay lần chạy đầu nên tôi không chỉnh gì.

## 6.9 Các tiêu chí còn lại
- Core regression: **chưa chạy, để Pha C (C2) chạy.** Môn này không ghi file core hay engine nào. Môn đang ở tier `catalog` trong registry, nên đường legacy chưa đọc concept table của môn.
- Kiểm tra ảnh hưởng chéo (`work/.../cross_course_check.json`): chạy lại eval của 9 môn retrieval (188 dòng), một lần với môn này ở catalog và một lần ở retrieval (trong bộ nhớ). Kết quả có **0 khác biệt** về pass, coverage và top-5. Lưu ý: trong cả hai lượt, index của môn này đã nằm trên đĩa và được dùng làm "rival" cho luật A1-3. Các môn W6b khác đang build song song, nên rival thay đổi theo thời gian. Pha C nên so lại với kết quả đã lưu của từng môn.

## Đề xuất role và index (chưa áp dụng)
Chi tiết nằm ở `work/he-thong-thong-tin-ke-toan-1/role_overrides_proposed.yaml`:
- src-0341 Owen → `reference` (authority 6). Hướng dẫn ôn tập ghi nó là "Học liệu bổ trợ (tài liệu tham khảo)" (src-0406 tr.1). Hiện **không** đề xuất `index_include: false`: Owen chiếm 0/24 vị trí top-5, nên không đo được tác động làm loãng.
- src-0343 (báo cáo NCKH sinh viên ĐH Đà Nẵng 2012) → `reference`.
- Tailieuthamkhao_Chương 2–6 (src-0352/0362/0376/0388/0399) → `reference`.

## Escalation
- Không có. Không chạm điều kiện nào ở mục 9. Mục mở cho Pha C: PREFIX của validator, tier, prerequisite family, và PPTX của Ch4 4.1–4.3.
