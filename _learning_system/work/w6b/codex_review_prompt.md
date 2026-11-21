Bạn là TESTER + REVIEWER độc lập cho đợt build W6b, gồm việc nạp 4 môn mới vào hệ thống ôn tập kế toán ở `D:\Hoc`. Bạn không phải người build. Nhiệm vụ là tìm lỗi và lỗ hổng logic, không phải sửa.

## Đọc trước
- `_learning_system/V3_EXPANSION_PLAN.md`: hợp đồng build. Các mục quan trọng: mục 2 (bất biến cứng), mục 6 (playbook theo môn), mục 7 (đặc tả), mục 9 (điều kiện dừng).
- `_learning_system/reports/v3/PLAN_W6B_MON_MOI.md`: kế hoạch đợt này, gồm Pha A, B, C.
- `_learning_system/AGENTS.md`: các luật cứng, mới thêm mục Git/publishing.
- Diff cần review: `git diff 8f735a4` cộng các file untracked (`git status`). Hai commit 358a276 và 5c845c7 là Pha A.

## Môi trường
- Python dùng `C:\Users\Admin\AppData\Local\Programs\Python\Python312\python.exe -X utf8`. Python 3.14 trên PATH thiếu thư viện.
- Đặt `HOC_ROOT=D:\Hoc` và `PYTHONIOENCODING=utf-8`, chạy lệnh từ `D:\Hoc\_learning_system`.

## Phạm vi ghi
- Bạn CHỈ được tạo hoặc ghi `_learning_system/reports/v3/CODEX_REVIEW_W6B.md` và các file trong `_learning_system/work/codex_review/`.
- KHÔNG sửa code, data, eval, registry, inventory, `_grok_pack`, thư mục môn gốc.
- Không git add, commit, push, checkout hay reset.
- Không chạy `v3_refresh.py --apply`.
- Nếu một test bạn chạy làm đổi file tracked, ghi rõ vào báo cáo. Ví dụ đã biết: `v3_regression.py` ghi `reports/v3/run_*` (cái này ổn), còn `freeze_core.py` ghi `pilot/core_freeze_manifest.json`.

## Cần TEST (tự chạy, ghi lệnh và kết quả)
1. `scripts/v3_regression.py` phải ra IDENTICAL. Sau khi chạy, `git status` không được có `reports/*_raw.json` hay `pilot/**` bị đổi.
2. `scripts/v3_eval_course.py --course <C> --tag _codex` cho cả 4 môn mới: he-thong-thong-tin-ke-toan-1, ke-toan-thue-1, ke-toan-tai-chinh-3, ke-toan-hanh-chinh-su-nghiep.
   - Gate mục 6.9 phải đạt.
   - So với `reports/v3/<C>_eval_pc.json`.
3. Eval của 10 môn retrieval cũ, so với `reports/v3/<C>_eval_w6bPre.json` (đây là trước W6b).
   - Metric phải giống hệt.
   - Liệt kê mọi dòng có `coverage`/`unknowns`/`suggestions` thay đổi. Đánh giá thay đổi nào là hợp lý (gợi ý cộng thêm) và thay đổi nào là hồi quy hành vi.
   - Trường hợp đã biết: `kt-d01` của kiem-toan-1 đổi coverage partial → insufficient do luật rival (A1) với KTHCSN.
4. `scripts/v3_validate_concepts.py --course <C>` cho 4 môn mới.
5. `scripts/v3_refresh.py --plan` trên dữ liệu thật phải ra 0 NEW / 0 CHANGED / 0 MISSING và không bị blocked. Nếu bị chặn vì thiếu record văn bản thì ghi lại.
6. Test logic mới của refresh **trong bộ nhớ** (monkeypatch `listing`, không tạo file trên D:):
   - Thư mục môn mới → `NEW_COURSE`.
   - `.git` / `_grok_pack` / file ở gốc bị bỏ qua.
   - `.xls` mới trong môn cũ → không abort, có `index_include: false`. Nếu cần chạy `apply()` thì chỉ làm trên bản sao trong `work/codex_review/`, hoặc đọc code và chứng minh bằng lập luận.
7. Parser `scripts/v3_extract_course.py::parse_name`: re-parse toàn bộ `inventory/files.json`.
   - Các dòng ≤ src-0339 phải cho kết quả giống hệt bản `backups/w6b_20261121/scripts/v3_extract_course.py`.
   - Các dòng mới: liệt kê dòng nào mất chương hoặc chủ đề.
8. `retrieval/courses.py::detect_courses` (masking cue lồng nhau): so với bản backup trên mọi câu hỏi trong `evals/**/*.jsonl`. Tự viết thêm các ca biên: hai cue chồng một phần, cùng môn lồng nhau, cue ngắn ≤5 ký tự có ranh giới từ.
9. `_grok_pack/18..21_*.md`:
   - Nhãn đúng format `[môn | ch.N | file | tr.a-b | role]`.
   - Số chunk khớp `data/chunks/<C>.chunks.jsonl`, trừ src-0341 bị loại có chủ đích.
   - `00_MUC_LUC.md` liệt kê đủ.

## Cần REVIEW (đọc code/data, có chứng cứ file:dòng)
- Bất biến mục 2: file thư mục môn gốc không bị sửa (so sha256 với inventory), file core/frozen không đổi, eval của 4 môn mới không bị sửa sau lần chạy đầu (sha256 khớp `evals/v3/FROZEN.json`).
- `inventory/files.json`: chỉ append src-0340..0595, không đánh số lại. Các dòng mới bị sửa role trong Pha C đều phải có bằng chứng trang 1 (xem `work/<C>/role_overrides_proposed.yaml`). Tôi đã sửa `source_role` trong inventory vì `v3_extract_course.py` lấy authority từ inventory, không lấy từ override. Đánh giá cách làm này đúng hay sai so với hợp đồng.
- `curriculum/concepts/<C>.yaml` của 4 môn: lấy mẫu ít nhất 8 concept mỗi môn. Kiểm canonical_name có trong heading thật, alias có trong text, edge có câu trích đúng source_id và trang, account_map ≥2 lần xuất hiện.
- `evals/v3/<C>_retrieval.jsonl`: câu hỏi có thật sự kiểm được điều cần kiểm không, hay quá dễ hoặc bị "dạy theo đề"? Category `insufficient`/`collision` có hợp lý không?
- Registry: cue của môn mới có cướp câu hỏi của môn cũ không. Ví dụ cue "kế toán thuế" có bắt nhầm "kế toán thuế TNDN hoãn lại" (KTTC3) không. Cũng xem xét `explicit_prerequisites` KTTC3 → KTTC2 và `explicit_prerequisites_family` của HTTTKT1.
- `research/regulations/*.yaml` mới: status khác unknown phải có nguồn chính thức. Không có suy diễn "còn hiệu lực".
- Bất kỳ lỗi logic, race, giả định sai, hay chỗ nào báo "đạt" mà thực ra chưa kiểm.

## Báo cáo
Viết `_learning_system/reports/v3/CODEX_REVIEW_W6B.md` bằng tiếng Việt:
1. Bảng kết quả test: lệnh, kỳ vọng, thực tế, PASS/FAIL.
2. Danh sách finding, xếp theo mức độ **BLOCKER / MAJOR / MINOR / NIT**. Mỗi finding gồm: file:dòng, mô tả, cách tái hiện, đề xuất sửa.
3. Những gì bạn KHÔNG kiểm được, và lý do.
4. Kết luận: có nên push không.

Cuối cùng in ra stdout một dòng tóm tắt dạng `BLOCKER=n MAJOR=n MINOR=n NIT=n`.

## Cập nhật sau khi viết brief (Pha C đã xong, hãy review cả phần này)
- HTTTKT1 Chương 4: Tuệ bổ sung `script_4.1..4.3.pdf` (src-0596..0598) và đổi tên 3 script cũ thành `script_4.4..4.6` (src-0379, src-0377, src-0378 giữ source_id, có `renamed_from`). Script `scripts/w6b_ch4_update.py`. File eval bổ sung `evals/v3/he-thong-thong-tin-ke-toan-1_retrieval_r1.jsonl`, key `..._r1` trong FROZEN.json, chạy bằng `v3_eval_course.py --suffix _r1`. Kiểm: việc đổi path in-place cho row đã có (chưa publish) có đúng hợp đồng "không rewrite history" không, và `git status` thấy 3 file `D` + 6 file `??` có nhất quán với inventory không.
- 62 record văn bản mới ở `research/regulations/` + 62 search log. Index external dựng lại (47 chunk). `_grok_pack/17_van-ban-phap-quy.md` xuất lại từ `data/chunks/external.chunks.jsonl`. Hãy kiểm 5-8 record có status khác unknown: nguồn url có thật và đúng nội dung câu "thay thế / hết hiệu lực" không (bạn có thể dùng web). Chú ý các record INFERRED chỉ dựa nguồn phụ.
- `scripts/v3_refresh.py` đã sửa 3 chỗ (listing bỏ `.`/`_`/file gốc; `NEW_COURSE`; `SUPPORTED_EXTENSIONS` + `index_include:false` cho định dạng không hỗ trợ). `scripts/v3_regression.py` đã thêm khôi phục `reports/*_raw.json`. `scripts/v3_eval_course.py` thêm `--suffix`. `scripts/v3_validate_concepts.py` thêm PREFIX. Đường `.xls` trong `apply()` CHƯA được chạy thử, hãy kiểm bằng lập luận hoặc bản sao.
- Đã biết, chưa quyết: `kt-d01` (kiem-toan-1) đổi coverage partial → insufficient vì luật rival A1 với KTHCSN. Hãy phân tích nguyên nhân gốc trong `retrieval/partition.py::_rival_coverage` (dòng ~150-345) và đề xuất cách sửa ít xâm lấn nhất.
- Git: chưa commit gì từ Pha C. `git diff HEAD --stat` cho thấy toàn bộ thay đổi.
