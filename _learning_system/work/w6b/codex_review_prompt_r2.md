Bạn là TESTER + REVIEWER độc lập, VÒNG 2, cho đợt W6b ở `D:\Hoc` (hệ thống ôn tập kế toán). Vòng 1 là báo cáo của chính bạn: `_learning_system/reports/v3/CODEX_REVIEW_W6B.md`. Người build đã sửa theo báo cáo đó. Việc của bạn là kiểm xem các bản sửa có thật sự đúng không và có gây lỗi mới không. Đọc `_learning_system/reports/v3/W6B_FINAL.md` mục 2, 3, 4 để biết đã sửa gì và chưa sửa gì.

Môi trường và phạm vi ghi giống vòng 1:
- Dùng Python 3.12.14 (runtime của Codex) như lần trước. Đặt HOC_ROOT, `-X utf8`.
- Chạy mọi test ghi file trên bản sao trong `_learning_system/work/codex_review_r2/`. Không sửa code, data, eval, registry, inventory, `_grok_pack`, thư mục môn gốc. Không git ghi (add/commit/push/checkout/reset).
- Chỉ được ghi `_learning_system/reports/v3/CODEX_REVIEW_W6B_R2.md` và `_learning_system/work/codex_review_r2/`.

Việc cần làm:
1. So `git diff HEAD` cho từng file đã sửa sau vòng 1, đối chiếu với `work/w6b/*.before_*` (bản trước khi sửa): `scripts/v3_build_external.py`, `retrieval/external.py`, `scripts/v3_regression.py`, `scripts/v3_refresh.py`, `scripts/v3_extract_course.py`, `scripts/v3_eval_course.py`, `retrieval/courses.py`, `curriculum/course_registry.yaml`. Với mỗi file nêu rõ: sửa có giải quyết đúng finding chưa, có gây hồi quy gì không. Hãy dùng test thật, không chỉ đọc.
2. B1: join record YAML → chunk → nhãn trong `_grok_pack/17_van-ban-phap-quy.md`. Mỗi chunk phải mang đúng `evidence_status` của record, URL phải là nguồn chính thức khi có. Kiểm lại 11 record INFERRED. Kiểm `external_notes` trả thêm `evidence_status`.
3. B3: `pilot/core_freeze_manifest.json` phải khớp snapshot hiện tại: sha256 inventory, chunk_count từng partition, hash meta index. 17 frozen suites core vẫn đúng.
4. M1: chứng minh bằng test trên bản sao rằng (a) `.xls` mới trong môn cũ không làm `affected` thay đổi và có cờ ở dòng inventory; (b) cổng trích xuất của refresh chấp nhận PPTX `not wired` nhưng vẫn dừng với lỗi trích xuất khác (chèn một PDF hỏng vào bản sao). Nếu `apply()` có thể chạy trong bản sao cô lập thì chạy; nếu không, nêu rõ không chạy được vì sao.
5. M2: chèn lỗi (suite exit 9, raw không được ghi mới) vào bản sao và xác nhận regression báo DIFFERENT; chạy thật xác nhận vẫn IDENTICAL.
6. M3: gate mới `collision_rows_failed`. Chạy lại cả 13 môn + file `_r1`. Gate nào đổi so với vòng 1? Test âm: collision trả rỗng phải fail gate.
7. M4: cue Thuế 1. Chạy tập câu hỏi cũ (mọi `evals/**/*.jsonl`) so detect trước/sau; tự viết ≥10 câu tiếng Việt tự nhiên về thuế (có/không nhãn môn, có/không "TNDN hoãn lại", GTGT, XNK, TTĐB) và nêu môn nào nhận. Có câu nào từng đúng mà giờ sai không?
8. M6: rebuild HTTTKT1 trong bản sao hai lần bằng `v3_extract_course.py --course he-thong-thong-tin-ke-toan-1`, xác nhận topic, documents, pages ổn định và 339 dòng parser lịch sử không đổi. Môn khác không có cờ `topic_from_page1` phải cho output y hệt.
9. Hồi quy tổng: `v3_regression.py` IDENTICAL; eval 13 môn; `v3_refresh.py --plan` ra 0/0/0; `v3_eval_external.py`; `v3_validate_concepts.py` 4 môn mới. So metric với vòng 1.
10. Quyết định B2 (kt-d01 giữ nguyên là chấp nhận): đọc `retrieval/partition.py` quanh dòng 307-350 và cho ý kiến độc lập có nên chấp nhận không, hoặc đề xuất cách sửa có thể chứng minh an toàn cho `kt-i02` và `kn-i02` (hai câu phải giữ insufficient). Nếu đề xuất cách sửa, chạy thử nó trong bản sao và nêu kết quả trên 188 câu cũ + 91 câu mới.
11. Tìm lỗi mới: những thứ đã thêm trong vòng sửa (script `w6b_export_pack17.py`, `w6b_ch4_update.py`, manifest KTTC3/KTHCSN, `make_manifests.py`, các sửa trong AGENTS/README/GROK) có sai sót, mâu thuẫn hay thông tin cũ không.

Báo cáo `_learning_system/reports/v3/CODEX_REVIEW_W6B_R2.md`, tiếng Việt: (1) bảng từng finding vòng 1 → ĐÃ SỬA ĐÚNG / SỬA CHƯA ĐỦ / SỬA GÂY LỖI / CHƯA SỬA (có chủ đích), kèm bằng chứng; (2) finding mới theo BLOCKER/MAJOR/MINOR/NIT, có file:dòng và cách tái hiện; (3) những gì không kiểm được; (4) kết luận có nên push không. Dòng cuối in ra stdout: `R2 BLOCKER=n MAJOR=n MINOR=n NIT=n`.
