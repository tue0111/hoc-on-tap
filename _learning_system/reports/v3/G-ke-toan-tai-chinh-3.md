# G-ke-toan-tai-chinh-3 — Kế toán tài chính 3: PASS (tạm, chờ Pha C)

W6b, phiên môn, 2026-11-21. Tier vẫn để `catalog` trong registry. Pha C đổi sang `retrieval` sau khi gộp FROZEN và chạy regression core.

## 6.1 Nguồn
53/53 dòng inventory (src-0543..src-0595) có sha256 và size khớp file trên `D:\Hoc\Kế toán tài chính 3`. Không thiếu file, cũng không có file nào nằm ngoài inventory.

## 6.2 Extract (`data/normalized/ke-toan-tai-chinh-3.*`)
- 53 tài liệu, 130 trang, 266.526 ký tự. 28 tài liệu được index: 26 PDF, 1 DOCX, đề thi và hướng dẫn ôn tập (đã tính trong số trên).
- page count khớp pypdf 100%. `UNPARSED`: không có (không có thư mục `_nguon`). `THIN`: không có.
- 25 lỗi là toàn bộ PPTX, với thông báo `pptx extractor not wired (non-learner pptx)`. Theo PLAN_W6B mục 3, các file này được ghi `not_extracted`, không tính là lỗi extract. Mỗi PPTX đều có script PDF/DOCX cùng chủ đề, và script đó được dùng làm nguồn index (danh sách cặp ở `work/ke-toan-tai-chinh-3/role_overrides_proposed.yaml`). Ngoài PPTX, extract có **0 lỗi**. Không bật extractor PPTX nên không phải escalate.
- Trang 1 của mọi PDF chủ đề, kể cả `C2_CD2.1_P1/P2.pdf`, đều mở đầu bằng "BÀI GIẢNG DẠNG VĂN BẢN (SCRIPT)" kèm lời giảng. Đây là script, không phải slide xuất PDF. Đã đề xuất `lecture_note` cho 19 file đang để `unknown`, `exercise` + chapter 4 cho src-0543, và `summary` cho src-0595 (inventory đang để `syllabus`). Các đề xuất chưa được áp dụng.

## 6.3 Dedupe
`reports/v3/ke-toan-tai-chinh-3_dedupe.json`: không có cặp chapter-vs-unit (vì không có `_nguon`), không có PDF gộp hay slide gộp. `REVIEW` rỗng. Đã kiểm thêm overlap 8-shingle giữa mọi cặp tài liệu (`work/.../pairwise_overlap.json`): cặp cao nhất là src-0543↔src-0590 với cov 0.28 (cùng dạng bài tập tổng hợp, khác số liệu), dưới ngưỡng 0.50. Không có bản trùng, không có dup_group. PDF/PPTX trùng chủ đề không phát sinh trùng trong index vì PPTX không được extract.

## 6.4–6.5 Concept table (`curriculum/concepts/ke-toan-tai-chinh-3.yaml`)
- Validator **PASS**, 28 concept (prefix `kttc3-`), 24 account map, 6 edge `explicit_sequence` có trích dẫn (BĐSĐT 2.1→2.2→2.3→2.4→2.5; thuế 4.1→4.2, 4.3→4.4).
- Chạy qua wrapper `work/.../validate.py`, vì `PREFIX` trong `scripts/v3_validate_concepts.py` chưa có `ke-toan-tai-chinh-3`. Wrapper chỉ thêm prefix trong bộ nhớ, không sửa script. **Pha C cần thêm `"ke-toan-tai-chinh-3": "kttc3"` vào PREFIX.**
- `same_as`: không có. Không concept core nào trùng nghĩa hẳn (core `khau-hao` là khấu hao TSCĐ, còn các concept `ktnh-*` riêng cho ngân hàng).
- Chương 4 không dùng alias trần "thuế" hay "thuế TNDN", vì đụng Kế toán thuế 1.
- Conflicts đã ghi:
  - COURSE_CODE: ACCO3310 (docx, tên file), ACCO1335 (trang 1 các script), ACCO3301 (hướng dẫn ôn tập). Chưa giải quyết.
  - TITLE_VARIANT: chương 1 có 5 chủ đề theo script, 6 theo ôn tập (ôn tập có 1.4 "xử lý chênh lệch tỷ giá giai đoạn trước hoạt động" nhưng không có script); tên chủ đề 4.2, 4.3, 3.5 lệch giữa các nguồn.

## 6.6 Partition (`data/indexes/3.0.0/ke-toan-tai-chinh-3/`)
379 chunk, vocab 1.219, 0 dup_group. Mọi tài liệu index đều có ít nhất 1 chunk. `source_hashes` ⊆ inventory.

## 6.7 Eval (đã đóng băng sau lần chạy đầu)
`evals/v3/ke-toan-tai-chinh-3_retrieval.jsonl`, 23 dòng: 12 direct, 3 source_bound, 3 insufficient, 2 collision, 3 account. sha256 `fbcbcacfa23ce207dbea697065e4ba6be901d92c10a1a27a2cb2ca26ea797868`.
Chạy bằng `work/.../run_eval.py`: gọi `scripts/v3_eval_course.py` nguyên bản, tier `retrieval` chỉ đặt trong bộ nhớ.
Dòng insufficient không dùng chủ đề thuế: WACC (TCDN1), rủi ro kiểm soát (KT1), chi phí SXC/sản phẩm dở dang (KTCP).

| gate | run1 | ngưỡng | kết quả |
|---|---:|---:|---|
| direct must_include@5 | 0.917 (11/12) | 0.85 | PASS |
| direct expected_chapter@1 | 1.0 | 0.80 | PASS |
| source_bound | 1.0 (3/3) | 0.67 | PASS |
| insufficient | 1.0 (3/3) | 1.0 | PASS |
| collision contamination | 0 | 0 | PASS |
| account | 1.0 (3/3) | 0.5 | PASS |
| topic_owner | n/a | — | PASS |

Dòng trượt duy nhất: k3-d04 (BĐSĐT khác BĐS chủ sở hữu sử dụng). Top-5 là src-0564/0555, đúng chương 2 nhưng thiếu src-0554.

## 6.8 Tinh chỉnh
0 vòng, vì gate đã đạt ở lần chạy đầu.

## Kiểm tra phụ (không thuộc gate)
- `work/.../cross_course_check.json`: chạy lại eval đóng băng của 9 môn có mốc W6b-A, lần lượt với KTTC3 ở `catalog` và ở `retrieval` (trong bộ nhớ). Kết quả **0 khác biệt**, cả so với mốc w6bA.
- Insufficient phụ thuộc vào index của môn khác:
  - k3-i01 bắt được nhờ `term_not_in_course_corpus:wacc`, không phụ thuộc môn khác.
  - k3-i02 nhờ owner `kiem-toan-1`.
  - k3-i03 nhờ rival `ke-toan-chi-phi`. Đây là index đã đóng băng; khi chạy, các index W6b khác (thuế 1, KTHCSN, HTTTKT1) đang tồn tại.
- Pha C nên chạy lại eval này sau khi gộp.

## 6.9 Những việc chưa làm trong phiên này (thuộc Pha C)
- Regression core (`v3_regression.py`): không chạy, theo chỉ dẫn. Phiên này không sửa file core, engine hay file dùng chung nào.
- Đổi tier và gộp `reports/v3/ke-toan-tai-chinh-3_frozen_entry.json` vào FROZEN.json.
- Đề xuất: `work/ke-toan-tai-chinh-3/role_overrides_proposed.yaml` (role, mã môn, cue `acco1335`) và `work/ke-toan-tai-chinh-3/prerequisite_proposed.yaml` (KTTC2 explicit, src-0580 tr.1; KTTC1 không có trích dẫn).

Escalation: không có.
