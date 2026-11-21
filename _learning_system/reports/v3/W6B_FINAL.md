# W6b FINAL — nạp 4 môn mới (2026-11-21)

Trạng thái: **chưa commit, chưa push** (chờ quyết định của Tuệ). Kế hoạch: `PLAN_W6B_MON_MOI.md`. Review độc lập: `CODEX_REVIEW_W6B.md` (vòng 1).

## 1. Kết quả theo môn (tier = retrieval)

| Môn | Gate | Nguồn đã index | Trang | Chunk | Khái niệm | Ghi chú |
|---|---|---:|---:|---:|---:|---|
| Hệ thống thông tin kế toán 1 (ACCO3315) | đạt, 24 + 3 câu bổ sung | 30 | 549 | 1081 | 36 | Ch4 4.1–4.3 do người học bổ sung 21/11 |
| Kế toán thuế 1 (ACCO2311) | đạt | 27 | 176 | 673 | 35 | chapter@1 vừa chạm ngưỡng 0,80 |
| Kế toán tài chính 3 (mã chưa thống nhất) | đạt | 28 | 130 | 379 | 28 | tiên quyết KTTC2 ghi kèm trích dẫn |
| Kế toán hành chính sự nghiệp (chưa rõ mã) | đạt | 43 | 199 | 569 | 37 | theo TT 24/2024, 4 chỗ tài liệu tự mâu thuẫn |

Eval của 4 môn đã đóng băng trong `evals/v3/FROZEN.json` (cộng `he-thong-thong-tin-ke-toan-1_r1`). Phần lõi (NLKT + KTTC1): regression IDENTICAL, 40/40 nguồn khớp mã băm.

## 2. Việc đã làm sau review Codex (vòng 1)

| Mục | Xử lý |
|---|---|
| B1 nhãn pháp quy bị nâng thành OBSERVED | `v3_build_external.py` giữ `evidence_status` của từng record và trích nguồn chính thức đầu tiên; `retrieval/external.py` trả thêm `evidence_status`. Chunk external: 36 OBSERVED + 11 INFERRED; `_grok_pack/17` xuất lại (`w6b_export_pack17.py`) |
| B3 manifest đóng băng sai snapshot | `freeze_core.py` chạy lại sau thay đổi cuối; AGENTS.md ghi ngoại lệ có giới hạn cho `pilot/core_freeze_manifest.json` |
| M1 `.xls` đi hết refresh | cờ `index_include:false` + `exclusion_reason` ghi ngay trên dòng inventory; file không hỗ trợ không kích hoạt dựng lại partition; cổng trích xuất chỉ chấp nhận PPTX/skipped, lỗi khác vẫn dừng. **Chưa chạy `apply()` đầu-cuối** (ghi vào D: thật) |
| M2 regression xanh giả | suite lỗi hoặc raw không được ghi mới → `DIFFERENT` |
| M3 gate collision | thêm gate `collision_rows_failed`; `coverage_mismatch_rows` được báo (không gate, vì không sửa file eval đóng băng); file `--suffix` coi nhóm vắng là n/a |
| M4 cue Thuế 1 | bỏ cue trần "kế toán thuế"; còn "kế toán thuế 1", "môn kế toán thuế", "kt thuế 1", "ktt1", mã môn |
| M6 topic HTTTKT1 | cờ `topic_from_page1` trong registry, đưa vào `v3_extract_course.py` (thay `set_topics.py`); rebuild 2 lần cho cùng topic và cùng 1081 chunk |
| M7 hồ sơ | manifest KTTC3/KTHCSN mới, manifest HTTTKT1/Thuế 1 cập nhật, `state.yaml` + câu "Nine courses" → 13 ở 6 file hướng dẫn, báo cáo này |
| m5 | `reload_registry` xóa cache `_cue_table` |

## 3. Quyết định của Tuệ (2026-11-21, đã duyệt)

1. **B2 — Kiểm toán 1 `kt-d01`: ĐÃ DUYỆT bản sửa** ở mục 3b (nhánh `owners` của `retrieval/partition.py` giữ câu trả lời khi chứng cứ trong môn phủ đủ bigram và vượt môn kia ≥ 0,25). Thay cho lựa chọn "chấp nhận như cũ" ghi trước đó.
2. **M5/G07 — đổi tên script Ch4 HTTTKT1: ĐÃ DUYỆT** cập nhật đường dẫn tại chỗ cho src-0377..0379 (giữ source_id/hash, có `renamed_from`), như một ngoại lệ migration một lần do người học đổi tên. Đính chính: các dòng này **đã** nằm trong commit cục bộ `358a276` (Pha A, chưa push), không phải "chưa từng commit" như ghi trước đó. Vai trò của 32 dòng W6b đổi trong Pha C cũng thuộc ngoại lệ này.
3. **Tiên quyết KTTC3 → KTTC2: ĐÃ DUYỆT** ghi trong `explicit_prerequisites`, ghi rõ bản chất "tham chiếu kiến thức đã học" (src-0580 tr.1), không phải dòng tiên quyết trong đề cương.
4. **PPTX**: 112 slide vẫn chưa trích chữ (extractor chưa bật). Mọi chủ đề đều có script PDF/DOCX nên chưa thiếu nội dung. Không thay đổi.

## 3b. Cập nhật sau Codex vòng 2 (vòng 2 KHÔNG chạy xong, Codex hết hạn mức; chỉ có bản nháp `work/codex_review_r2/report-a.md`)

- **B2 đã áp dụng** (thay cho mục 3.1): `retrieval/partition.py` giữ câu trả lời khi chứng cứ trong môn phủ đủ bigram và vượt môn kia ≥ 0,25 (cách do Codex thử). Kết quả: đúng 1 dòng đổi (`kt-d01` → partial) trên 279 câu; `kt-i02`, `kn-i02` vẫn insufficient; 13 môn vẫn qua cổng; regression IDENTICAL. Bản gốc: `work/w6b/partition.before_B2.py`.
- **G01 đã sửa**: regression xóa raw cũ trước khi chạy, phục hồi trong `finally`; suite không ghi gì → `DIFFERENT 10` (đã thử).
- **Đã sửa thêm sau nháp vòng 2:** G04 (`v3_build_external.py` mặc định dựng từ record đã duyệt; muốn tái tạo từ snapshot Wave 5 phải thêm `--bootstrap-wave5`; chạy không cờ giữ nguyên 131 record), G06 (thêm cue thuế XNK/GTGT/TTĐB/BVMT và "ôn/học/bài kế toán thuế"; 0 khác biệt trên 318 câu eval cũ, "TNDN hoãn lại" vẫn không bị Thuế 1 bắt), G09 (tên báo cáo eval có suffix; file eval rỗng bị từ chối), G14 (export file 17 an toàn khi mục 17 ở cuối), G15 (mục lục `_grok_pack` liệt kê đúng nguồn từng phần của file 21: 35 + 8; script xuất gói idempotent).
- *(Lịch sử, đã thay bằng mục 3c và 3d: danh sách "còn mở" tại thời điểm bản nháp vòng 2. Câu "chưa từng commit" về src-0377..0379 là sai và đã được đính chính ở mục 3.2.)*

## 3c. Đợt sửa D (2026-11-21 tối; Opus lập kế hoạch + QC, Sonnet/Haiku thực hiện)

| Mục | Ai làm | Kết quả QC |
|---|---|---|
| G03 nhãn chứng cứ trong câu trả lời pháp quy | Sonnet (S1) | `retrieval/external.py` + `director.py`: mỗi item in "Chứng cứ: (đã đối chiếu nguồn chính thức / suy luận…)", nguồn chính thức trước (nguồn phụ có ghi chú), ngày kiểm theo record; `v3.checked_at` không còn ghi cứng. 14 câu thử ALL_OK, item/coverage/unknowns y hệt trước |
| G05 + G10 spreadsheet | Sonnet (S2) | `.xls/.xlsm/.xlsx` là inventory-only (`.xlsx` bỏ khỏi danh sách hỗ trợ vì chưa có extractor), không cần review, không dựng partition; bản thay không trích được cho nguồn đang index thì dừng. 19 dòng spreadsheet HTTTKT1 có cờ trên dòng inventory. `apply()` đầu-cuối đã diễn tập trên bản sao (`APPLIED []`); nhánh CHANGED chưa diễn tập |
| G12 + G11 | Sonnet (S3) | topic dự phòng chỉ gán khi có dòng "Chương …"; HTTTKT1 dựng lại giống hệt; `coverage_mismatch_rows` báo mọi category (thêm `kn-c02`, `kthcsn-c03`) |
| G08, G13, m3 | Haiku (H1) | `w6b_ch4_update.py` có danh sách cho phép + kiểm "Chủ đề N"; manifest đếm PPTX theo loại; 13 record pháp quy cập nhật môn dẫn nguồn (chỉ 3 trường). `luat-thue-gtgt.yaml` để nguyên: hai citation trùng slug do harvest cắt chữ ("…") — lỗi nhỏ mới, chưa sửa |
| QC (Opus) | | 13 môn + `_r1`: kết quả giống hệt trước đợt D; regression IDENTICAL; refresh 0/0/0; external all_pass; `freeze_core` OK; không đổi vùng bảo vệ. `.gitignore` thêm `work/codex_review*/`, `work/w6b_s*/`, `work/refresh/*/` (bản sao kiểm thử ~3 GB) |

## 3d. Đợt sửa E sau Codex vòng 2 (`CODEX_REVIEW_W6B_R2.md`: BLOCKER=1 MAJOR=4 MINOR=7 NIT=4)

| Mục | Ai làm | Kết quả QC (Opus) |
|---|---|---|
| G01 regression thiếu baseline vẫn IDENTICAL | Sonnet (S4) | danh mục cố định 10 raw bắt buộc; tập baseline và tập raw mới phải đúng bằng danh mục; 4 ca âm đều DIFFERENT, chạy thật IDENTICAL |
| G09 eval trượt vẫn exit 0, tên báo cáo đè nhau | Sonnet (S4) | CLI trả 3 khi trượt (`--report-only` để chỉ báo cáo; refresh dùng cờ này); `main()` trả mã, không `sys.exit`; supplement ghi `<C>_eval+<suffix><tag>` |
| G17 refresh dựng external thừa / citation trùng slug | Sonnet (S4 + S6) | đồng bộ citation gộp theo slug, chỉ đánh dấu thay đổi ròng; harvest bỏ dấu cắt "…" nên "Luật thuế gtgt" và "Luật thuế gtgt…" thành một citation (130 → 129); record `luat-thue-gtgt` khớp lại |
| G24 nhãn rỗng thành OBSERVED | Sonnet (S6) | builder dừng khi `evidence_status` thiếu/ngoài enum; eval external kiểm enum + OBSERVED phải có nguồn chính thức; ca âm fail đúng |
| G06 router thuế | Sonnet (S5) | `cues` = nhãn môn (thắng), `topic_cues` = cụm nghiệp vụ chỉ dùng khi không có nhãn, `topic_veto_after` chặn "…TNDN/hoãn lại"; 793 câu eval cũ 0 đổi; 3 câu XNK/đầu vào về Thuế 1, câu có nhãn KTTC3 về KTTC3 |
| G08, G13, G12 | Haiku (H2) | script Ch4 kiểm đường dẫn đầy đủ + ràng buộc source_id; manifest đối chiếu lỗi giữa coverage và documents; topic dự phòng chỉ nhận "Chương <số đúng>:" hoặc "Chương mở đầu:" (chương 0) |
| G25, G26 hồ sơ | Opus | `.gitignore` thêm `work/refresh/latest.json`, `work/listing.json`, `work/w6b_h*/` (bỏ theo dõi lúc commit); README lớp C; mục 3b đánh dấu lịch sử |
| Sự cố trong đợt E | | 3 agent chạy regression đồng thời làm 10 `reports/*_raw.json` và báo cáo `*_eval_wave5` của KTTC2 bị ghi lại; đã khôi phục từ HEAD, xóa file KTCP wave5 do S4 tạo nhầm. Bài học: không chạy `v3_regression.py` song song |

QC cuối (tuần tự, không agent nào chạy): 13 môn + `_r1` giống hệt đợt D; regression IDENTICAL; refresh 0/0/0; 4 validator; external all_pass; `freeze_core` OK; vùng bảo vệ và lịch sử không đổi.

## 4. Chưa làm / giới hạn (trạng thái cuối)

- **Chưa sửa, có chủ đích:** G16 một số tên khái niệm lấy từ câu văn ("Tờ khai hải quan", "rút dự toán", hai tên sheet) chưa có bằng chứng là heading; G19 TT 80/2021 có hai record cho cùng văn bản; G20 thư mục môn rỗng chưa kích hoạt `NEW_COURSE` (kích hoạt khi có file đầu tiên); G21 sách Owen: bìa ghi ấn bản 2013, hướng dẫn dẫn bản 2016; G22 cue có gạch dưới (`_hcsn_`).
- 11 record pháp quy INFERRED: lý do suy luận khác nhau theo từng record (ví dụ Luật 21/2012 có nguồn chính thức, suy luận nằm ở việc đối chiếu ký hiệu QH12/QH13), không phải tất cả "chỉ dựa nguồn phụ".
- 112 slide PPTX chưa trích chữ; mọi chủ đề đã có script PDF/DOCX.
- `course_scans/<C>.yaml` không tạo cho 4 môn (đã được manifest + concept table V3 thay thế).
- `apply()` của refresh mới diễn tập trên bản sao, chưa chạy trên kho thật; chưa thử hai lượt publish cạnh tranh.
- Bộ eval đo "tìm đúng nguồn", không đo khả năng giải bài hay tổng hợp câu trả lời so sánh.
