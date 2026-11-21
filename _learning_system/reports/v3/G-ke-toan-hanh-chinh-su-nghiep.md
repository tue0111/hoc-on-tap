# G-W6b — Kế toán hành chính sự nghiệp: GATE PASS (Pha B, chờ Pha C)

Tier trên đĩa vẫn là `catalog`. Phiên B không đổi tier. Pha C1 sẽ đổi sang `retrieval` sau khi gộp `ke-toan-hanh-chinh-su-nghiep_frozen_entry.json` vào `FROZEN.json`.

## 6.1 Kiểm tra nguồn
Có 84 dòng inventory (src-0407..src-0490). Sha256 và size khớp 84/84 (`work/ke-toan-hanh-chinh-su-nghiep/hash_check.json`). Lượt này không stage.

## 6.2 Extract
- Có 84 tài liệu. 43 tài liệu được trích: 40 script PDF, 2 PDF ôn tập/đề thi, 1 DOCX chương mở đầu. Tổng 199 trang, 479.236 ký tự.
- Lỗi thật: 0. Page count khớp pypdf (mismatch = []). UNPARSED = []. THIN = [].
- 41 PPTX có `parse_quality=error` với lý do `pptx extractor not wired (non-learner pptx)`. Đây là hành vi đã biết (PLAN_W6B mục 3), không phải lỗi trích. Mỗi slide đều có script PDF cùng chủ đề, riêng `src-0488` (slide chương mở đầu) có DOCX `src-0487`. Vì vậy không cần escalate.
- Luật tên file `kthcsn` parse 40/40 script (chương, chủ đề, phần P1..P3). DOCX theo `inventory_apparent` vào chương 0. `src-0489` (summary) và `src-0490` (exam) có chapter = null.

## 6.3 Dedupe
Không có tài liệu cấp chương hay PDF gộp, cũng không có `_nguon`, nên số cặp = 0 và REVIEW = []. Báo cáo ở `reports/v3/ke-toan-hanh-chinh-su-nghiep_dedupe.json`.

## 6.5 Concept table
`curriculum/concepts/ke-toan-hanh-chinh-su-nghiep.yaml` có 37 concept với prefix `kthcsn-`: 1 chương mở đầu, 8 chương, 24 chủ đề và 4 thuật ngữ chung. Account map có 37 tài khoản (mỗi tài khoản đếm ≥ 2). Edges: 0, vì không có câu trích nào nằm gọn trong một trang. `same_as`: không có, vì nghĩa trong HCSN khác với concept core của doanh nghiệp.
Mục `conflicts` gồm:
- REGULATION_VINTAGE: TT 107/2017 (hiệu lực đến hết 2024) và TT 24/2024 (từ 2025), trích từ src-0409 tr.2. Phần còn lại của giáo trình theo TT 24/2024/TT-BTC.
- TITLE_VARIANT ch.5: script ghi "Kế toán hoạt động hành chính sự nghiệp", ôn tập ghi "Kế toán doanh thu, chi phí hoạt động hành chính sự nghiệp".
- TITLE_VARIANT ch.6: ôn tập thêm "và hoạt động khác" vào tên chương 6 và chủ đề 6.1/6.4. Script đặt nội dung này ở 5.3.
- ASSESSMENT_WEIGHT_CONFLICT: src-0487 ghi "mỗi phần chiếm 50%" nhưng cũng ghi "A2 (60% tổng điểm)".

Validator: PASS 37 concept. Validator gốc chưa có prefix `kthcsn` trong `PREFIX` nên phải chạy qua `work/.../overlay_run.py validate`. Overlay này chỉ vá trong bộ nhớ, không ghi đĩa. Pha C cần thêm `"ke-toan-hanh-chinh-su-nghiep": "kthcsn"` vào `scripts/v3_validate_concepts.py::PREFIX`.

## 6.6 Partition
569 chunk, vocab 1.491, dup_groups 0. Mọi tài liệu được index đều có chunk. `source_hashes` ⊆ inventory. Index nằm ở `data/indexes/3.0.0/ke-toan-hanh-chinh-su-nghiep/`.

## 6.7 Eval (đã đóng băng sau lần chạy đầu)
File `evals/v3/ke-toan-hanh-chinh-su-nghiep_retrieval.jsonl`, 21 dòng, sha256 `03e575bc1ac60ea770a362c0c7b5b50308b355972dac5184feac2b5e1c7d201d`.
Thành phần: 10 direct, 3 source_bound, 3 insufficient (WACC, thuế thu nhập hoãn lại, quyền chọn phái sinh, không dùng chủ đề ngân sách), 3 collision (cả 3 có `must_not_include_courses` gồm TCHCSN; c03 hỏi "Kế toán HCSN khác gì môn Tài chính hành chính sự nghiệp?"), 2 account.
Lần chạy đầu dùng overlay (tier=retrieval trong bộ nhớ). Kết quả ở `reports/v3/ke-toan-hanh-chinh-su-nghiep_eval_run1.json/.md`. Không cần vòng tinh chỉnh nào.

| gate | giá trị | ngưỡng | kết quả |
|---|---:|---:|---|
| direct must_include@5 | 1.0 | 0.85 | PASS |
| direct expected_chapter@1 | 0.9 | 0.80 | PASS |
| source_bound | 1.0 (3/3) | 2/3 | PASS |
| insufficient | 1.0 (3/3) | 1.0 | PASS |
| collision contamination | 0 | 0 | PASS |
| account | 1.0 (2/2) | 0.5 | PASS |
| topic_owner | n/a | — | PASS (n/a) |

Dòng trượt riêng lẻ: `kthcsn-d01`. Top-1 là summary src-0489 với chapter = null, nên chapter@1 sai, nhưng must_include vẫn đạt.

## Routing / collision với TCHCSN
- "Hành chính sự nghiệp: ngân sách nhà nước là gì?" đi vào TCHCSN.
- "HCSN tự chủ tài chính" đi vào TCHCSN.
- "kế toán hcsn tài khoản 611" đi vào KTHCSN (hiện trả `course_not_indexed` vì trên đĩa còn là catalog).
- Kiểm tra trong bộ nhớ, không ghi file: chạy lại eval đã đóng băng của 9 môn retrieval cũ có báo cáo `_eval_w6bA.json` trong lúc index KTHCSN đã có mặt. Kết quả khớp 100% (pass, coverage, top-5). TCDN1 không có `_eval_w6bA.json` nên không so.

## Core regression
Không chạy (`v3_regression.py` bị cấm ở Pha B). Phiên này không sửa file core, engine hay file dùng chung nào. Pha C2 phải chạy regression.

## Mã môn / tiên quyết
- Mã môn: không tìm thấy trong tài liệu (UNKNOWN). Nhóm biên soạn thuộc Khoa Kế toán – Kiểm toán, Trường ĐH Mở TP.HCM (src-0487).
- Tiên quyết: không có câu trích dẫn chứng → `work/.../prerequisite_proposed.yaml` để `[]`.
- Đề xuất role: src-0487 (`unknown` → `lecture_note`), xem `work/.../role_overrides_proposed.yaml`.

## Lưu ý cho Pha C
1. `_rival_coverage` tính trên mọi partition có `meta.json`, gồm cả 3 môn W6b đang build song song. Unknown của i02 có nhắc `ke-toan-tai-chinh-3`. Coverage của dòng đó vẫn là insufficient nhờ luật OOV, nhưng Pha C nên chạy lại eval KTHCSN (không sửa file eval) sau khi gộp.
2. Thêm prefix `kthcsn` vào validator (xem 6.5).
