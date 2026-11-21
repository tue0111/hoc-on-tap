# Review độc lập W6b — 21/11/2026

**Quyết định: CHƯA PUSH.** Cả bốn môn vượt ngưỡng điểm của bộ eval chính, 598/598 tệp nguồn khớp SHA-256 và regression core trả `IDENTICAL`. Ba vấn đề chặn phát hành là 11 kết luận pháp quy bị nâng nhãn chứng cứ khi phục vụ, một câu đúng phạm vi Kiểm toán 1 bị từ chối dù lấy đúng nguồn, và manifest ký nhận một snapshot cũ. Quy trình tạo file mới trong môn cũng chưa chạy được như cam kết.

Đã xét diff từ `8f735a4`, hai commit Pha A `358a276`, `5c845c7`, diff Pha C so với HEAD và file untracked. Đường dẫn bên dưới tính từ `_learning_system/`, trừ `../_grok_pack/` và thư mục môn gốc. Phân biệt snapshot hiện tại, dữ liệu đối chứng và thí nghiệm chèn lỗi.

## 1. Kết quả chạy

Thư mục làm việc thực là `D:\Hoc\_learning_system`. Binary 3.12 do brief chỉ định trả `Access is denied`. Đã chạy bằng CPython **3.12.14** tại `C:\Users\Admin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, với `-X utf8`, `PYTHONIOENCODING=utf-8`, `PYTHONDONTWRITEBYTECODE=1` và PyYAML 6.0.3 từ wheel cache cục bộ. Ký hiệu `py` trong bảng là binary và cờ này. `suite.py` sao chép script, dữ liệu, reports, pilot và nguồn core vào `work/codex_review/mirror/`, rồi đặt `HOC_ROOT` của tiến trình con thành mirror. Các phép đọc gốc và scan thật dùng `HOC_ROOT=D:\Hoc`. Riêng CLI plan đọc listing của D: thật, chỉ chuyển thư mục chứa bản inventory tương đương, lock và đầu ra sang mirror. Chi tiết tái chạy ở [suite.py](../../work/codex_review/suite.py), [logic.py](../../work/codex_review/logic.py), [compare.py](../../work/codex_review/compare.py), [data_check.py](../../work/codex_review/data_check.py) và [negative.py](../../work/codex_review/negative.py).

| Lệnh / kiểm tra | Kỳ vọng | Thực tế | Kết quả |
|---|---|---|---|
| `py scripts/v3_regression.py` | 8 suite chạy, comparator IDENTICAL | 8 stdout, 10 raw đối chứng, exit 0, `run_20261121_164123/diff.txt = IDENTICAL`. SHA trước/sau toàn bộ pilot và raw lịch sử trong mirror khớp | PASS |
| `git status --short` riêng raw lịch sử và pilot | Sạch trước commit | Không có raw lịch sử bị đổi. `M pilot/core_freeze_manifest.json` đã có trước test và giữ nguyên SHA. Không test nào làm đổi tracked file trong cây gốc | FAIL điều kiện Git |
| `py scripts/v3_eval_course.py --course <C> --tag _codex` × 4 | §6.9 đạt, metric bằng `_pc` | 88 câu. Bốn bộ đạt đúng metric. Dữ liệu từng dòng của ba môn giống hoàn toàn. HTTTKT1 đổi thứ tự/nguồn top-5 ở 6 dòng sau bổ sung Ch4. Toàn bộ kết quả HTTTKT1 khớp `_eval_ch4.json` | PASS điểm |
| Cùng lệnh cho các môn cũ | So từng dòng với `_w6bPre.json` | 9 môn retrieval thực, 188 dòng. 9/9 bộ có metric bằng tuyệt đối, 6 dòng đổi hành vi/chú thích, trong đó 1 dòng mất coverage. KTCP vẫn trượt raw `topic_owner` như baseline, có miễn D2 đúng 3 dòng | PASS metric / FAIL C2 |
| Cùng lệnh cho `tai-chinh-doanh-nghiep-1` | Xác minh môn thứ 10 trong brief | Đã chạy. Registry trước và sau đều là `catalog`. Direct@5, chapter@1, source_bound = 0, insufficient = 1, contamination = 0. Không có `_w6bPre.json` thứ 10. Các pseudo-partition learner-notes/external có runner riêng | Không có đối chứng thứ 10 |
| `py scripts/v3_eval_course.py --course he-thong-thong-tin-ke-toan-1 --suffix _r1 --tag _codex_r1` | Ba PDF mới trả đúng nguồn/chương | 3/3 đúng nguồn và chương. Kết quả từng dòng khớp `_eval_ch4_r1.json`. CLI in `GATE_FAIL` nhưng exit 0 | PASS ca trực tiếp / FAIL biểu diễn gate |
| `py scripts/v3_validate_concepts.py --course <C>` × 4 | Exit 0, không lỗi | PASS cả 4. Lần lượt 36, 35, 28, 37 concept theo thứ tự bảng dưới | PASS validator |
| `py work/codex_review/data_check.py` — extraction/dedupe | 0 lỗi và lệch trang, không REVIEW | Đếm độc lập 125 PDF có text, số trang khớp pypdf. Không lỗi PDF/DOCX hay UNPARSED. 112 PPTX vẫn nằm **trong** `coverage.errors` dù kế hoạch W6b cho phép bỏ extractor PPTX. 4 báo cáo dedupe đều có REVIEW rỗng | PASS theo ngoại lệ W6b / FAIL kiểm `errors == []` nguyên văn |
| `py scripts/v3_refresh.py --plan` qua `logic.py` | 0 NEW / 0 CHANGED / 0 MISSING, không blocked | Đúng 0/0/0, `blocked=null`, exit 0. Kiểm riêng 130 citation theo hàm slug, đều có file YAML. No-op plan tự nó chỉ scan nguồn/core, không chạy gate citation trong apply | PASS |
| `py work/codex_review/logic.py` — listing/plan trong RAM | Môn mới báo NEW_COURSE, bỏ mục hệ thống, nhận .xls | Thêm một path trong môn lạ → exit 2, NEW_COURSE. `.git`, `_grok_pack`, `README.md` → danh sách rỗng. Một .xls mới trong Kế toán thuế 1 → exit 0, stage đúng 1, không ghi fixture. Luồng publish tiếp theo bị chặn theo M1 | PASS plan / FAIL hợp đồng đầu-cuối |
| Cùng script — `parse_name` với backup | Không đổi output cũ, liệt kê metadata mới thiếu | So đủ dict chapter/topic/part/parse_rule, 339/339 giữ nguyên. Đủ 259 dòng mới. 10 thiếu chương, 70 thiếu topic, không trường nào vốn có ở parser backup bị xóa | PASS tương thích, chi tiết ở dưới |
| Cùng script — `detect_courses` với backup | Giải cue lồng, giữ câu cũ | 793 trường question kể cả lồng trong 37 JSONL. So cả registry backup và giữ registry mới để cô lập thuật toán. 91 delta toàn thuộc 88+3 dòng mới, trong đó 20 khác do masking khi giữ cùng registry mới. Bốn chuỗi có dấu hỏi ngoài trường question cũng không đổi. Ca biên bảng dưới | PASS bộ cũ / FAIL ca thuế thực |
| `py work/codex_review/data_check.py` — Grok 18–21 | Nhãn đúng chunk, nội dung/trang đúng, mục lục đủ | 277 + 673 + 379 + 569 = 1.898 khối. So multiset toàn bộ nhãn và kiểm nội dung từng khối. Loại đúng 804 chunk src-0341. Đủ 5 file, gồm hai phần số 21. Tất cả page range dạng a-b, 144 nhãn dùng `ch.—` đúng với `chapter:null` | PASS có quy ước chương trống |
| Cùng script — external | 62 YAML/log, 47 chunk/pack/index, giữ nhãn | 62 YAML mới, 62 đường dẫn log phân biệt và tồn tại. 38 UNKNOWN có lý do, 13 OBSERVED, 11 INFERRED. 47/47 thân chunk nằm trong pack 17, 47 nhãn, meta 47. Cả 11 INFERRED mất nhãn | FAIL |
| `py work/codex_review/negative.py` | Lỗi subprocess hoặc collision trả rỗng phải lộ ở gate | Chèn 8 child exit 9 vẫn IDENTICAL với raw cũ. Chèn một collision trả rỗng vẫn ALL_PASS | FAIL |

Kiểm bổ sung hai partition đặc biệt trong mirror. `py scripts/v3_eval_learner_notes.py --tag _codex` đạt 5/5 và `py scripts/v3_eval_external.py` đạt 5/5. Lần đầu runner external thiếu jsonschema; sau khi nạp bản 4.26.0 cùng dependency từ wheel cache vào thư mục review, runner chạy thành công. Năm ca external hiện tại vẫn xanh khi 11 nhãn chứng cứ bị nâng.

### Gate theo môn mới

| Môn | n | direct nguồn@5 | chương@1 | source_bound | insufficient | contamination | account | PDF / trang normalized / lỗi PPTX | chunk index / pack |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| HTTTKT1 | 24 | 14/14 | 13/14 | 2/3 | 3/3 | 0 | 2/2 | 30 / 549 / 21 | 1081 / 277 |
| Kế toán thuế 1 | 20 | 10/10 | 8/10 | 3/3 | 3/3 | 0 | 2/2 | 26 / 176 / 25 | 673 / 673 |
| KTTC3 | 23 | 11/12 | 12/12 | 3/3 | 3/3 | 0 | 3/3 | 27 / 130 / 25 | 379 / 379 |
| KTHCSN | 21 | 10/10 | 9/10 | 3/3 | 3/3 | 0 | 2/2 | 42 / 199 / 41 | 569 / 569 |

Ngưỡng direct là 85%/80%, source_bound 2/3, insufficient 100%, contamination 0, account ≥1/2. Không bộ mới nào có topic_owner, phù hợp phạm vi Wave 1. Mọi tài liệu mang `index_include:true` có chunk. HTTTKT1 thay top-5 so với `_pc` ở `ht-d01, ht-d11, ht-s02, ht-i01, ht-i02, ht-i03`. Dòng tìm đề mẫu `ht-s02` vẫn trượt. Bộ bổ sung Ch4 dùng đúng src-0596..0598.

### Metric từng môn cũ

Mỗi ô bằng đúng giá trị trong JSON trước W6b khi so số chưa làm tròn. Bảng làm tròn để đọc, contamination là số ca.

| Môn cũ | n | Nguồn@5 | Chương@1 | Source-bound | Insufficient | Contamination | Account | Topic owner |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ke-toan-chi-phi | 23 | 90% | 80% | 100% | 100% | 0 | 100% | 0% |
| ke-toan-ngan-hang | 22 | 100% | 83,3% | 100% | 100% | 0 | 100% | — |
| ke-toan-tai-chinh-2 | 23 | 100% | 90% | 100% | 100% | 0 | 100% | 100% |
| kiem-toan-1 | 20 | 100% | 100% | 100% | 100% | 0 | — | — |
| kinh-doanh-va-nghiep-vu | 20 | 100% | 100% | 100% | 100% | 0 | — | — |
| luat-kinh-doanh | 20 | 100% | 91,7% | 100% | 100% | 0 | — | — |
| ngan-hang-thuong-mai | 20 | 91,7% | 83,3% | 100% | 100% | 0 | — | — |
| tai-chinh-hanh-chinh-su-nghiep | 20 | 100% | 83,3% | 66,7% | 100% | 0 | — | — |
| thi-truong-tai-chinh | 20 | 100% | 100% | 100% | 100% | 0 | — | — |

### Sáu thay đổi trên 188 câu cũ

Runner chỉ lưu suggestions cho category topic_owner. Đã gọi lại `retrieve` cho cả 188 dòng với registry và hàm detect của backup, giữ nguyên index cũ, rồi so package hiện tại. Mọi coverage/unknowns và suggestions có lưu trong mốc trước đều tái lập được. Bảng liệt kê mọi delta, không có suggestion nào bị xóa. Chi tiết trước/sau ở [old_behavior.json](../../work/codex_review/old_behavior.json).

| Dòng | Thay đổi | Phán định |
|---|---|---|
| `kp-i03` | unknowns thêm `topic_in_other_course:ke-toan-hanh-chinh-su-nghiep` | Hỏi ghi nhận TSCĐ hữu hình trong KTCP. KTHCSN có chủ đề TSCĐ. Bổ sung hợp lý như nơi tham khảo, không chứng minh tiêu chuẩn ghi nhận doanh nghiệp và đơn vị sự nghiệp giống nhau. |
| `k2-t02` | suggestions thêm KTHCSN, concept `kthcsn-nhung-van-de-chung-ve-tai-san-co-dinh`, ch.4 | Giữ gợi ý KTTC2; gợi ý mới rộng hơn câu hỏi “vô hình”. Hợp lý nếu mô tả là liên quan, độ đặc hiệu thấp. |
| `kt-d01` | partial → insufficient, thêm `topic_in_other_course:ke-toan-hanh-chinh-su-nghiep` và `insufficient_curriculum_evidence` | **Hồi quy** dù giữ nguyên 5/5 nguồn và chương. Xem B2. |
| `kd-i03` | unknowns thêm `topic_in_other_course:ke-toan-tai-chinh-3` | Thuế hoãn lại đúng chủ đề KTTC3 ch.4. Giữ nguyên insufficient ở KDNV. |
| `lk-i02` | unknowns thêm `topic_in_other_course:ke-toan-thue-1` | FIFO có ở src-0532 tr.2,7 như giả thiết bài GTGT. Có liên quan nhưng ghi “môn dạy FIFO” là quá mạnh. Không thay đổi quyết định của Luật kinh doanh. |
| `tt-i03` | unknowns thêm `topic_in_other_course:ke-toan-hanh-chinh-su-nghiep` | Kiểm kê quỹ tiền mặt liên quan KTHCSN ch.2. Giữ nguyên insufficient và nguồn của TTTC. |

144 nhãn pack có chương trống dùng dấu gạch dài, gồm 25/35/41/43 nhãn theo thứ tự bốn môn ở bảng gate. Nếu `ch.N` bắt buộc N là **số** cho cả đề thi và tài liệu ôn tập toàn môn thì 144 nhãn này **FAIL định dạng nghiêm ngặt**; so với metadata và quy ước chương trống hiện hành chúng khớp. Nên chốt sentinel trong hợp đồng, tránh suy diễn số chương cho nguồn toàn môn.

### Parser và router

Các khoảng sau bao gồm hai đầu và dùng tiền tố `src-`. Thiếu chương ở **0340–0341, 0405–0406, 0489–0490, 0541–0542, 0594–0595**. Thiếu topic ở **0340–0369, 0376–0383, 0388–0406, 0487–0490, 0539–0543, 0592–0595**. Danh sách phân biệt nguồn tổng hợp/đề/Excel với script thực sự có chủ đề. Toàn bộ tên file và output cũ/mới ở [parse.json](../../work/codex_review/parse.json). Ch4 hiện phục vụ 4.1/4.2/4.3 từ ba ID mới, 4.4/4.5/4.6 lần lượt từ 0379/0377/0378.

| Ca thử detect hoặc resolve | Kết quả |
|---|---|
| A có `alpha beta`, `beta`, B có `beta gamma`. Hỏi `alpha beta gamma` | [A,B], giữ hai span giao một phần |
| Cùng bảng, hỏi `alpha beta` | [A] đúng một lần |
| Cue ngắn `beta` trong `xbetax`, `(beta)`; cue thật `hcsn` trong `xhcsnx`, `(hcsn)` | Rỗng khi nằm giữa chữ, khớp khi có ngoặc. HCSN trơn về TCHCSN |
| `kế toán thuế TNDN hoãn lại` | Scope Thuế 1, insufficient, dù KTTC3 có chương tương ứng |
| `KTTC3: kế toán thuế TNDN hoãn lại` / `Chương 4 của KTTC3: kế toán thuế TNDN hoãn lại` | Nhãn đầu câu chọn đúng KTTC3. Khi thêm tiền tố chương, hai cue thành scope_unresolved |
| `ACCO3301` | Mã có trong codes nhưng vắng ở cues → không định được partition từ câu tự do. Mã chính thức KTTC3 vẫn UNKNOWN |

## 2. Findings theo mức độ

### BLOCKER

**B1 — 11 kết luận pháp quy được trình bày như đã quan sát trực tiếp.** `scripts/v3_build_external.py:41`, `:50`, `retrieval/external.py:36`, `../_grok_pack/17_van-ban-phap-quy.md:8`. Tái hiện bằng cách join YAML → chunk theo relative_path → nhãn pack. Hàm dựng chunk mặc định OBSERVED, caller bỏ qua evidence_status của YAML và chỉ lấy URL đầu. Additive note cũng bỏ trường chứng cứ. Ví dụ Luật 106/2016 có đánh dấu INFERRED cho việc hết hiệu lực toàn bộ nhưng được dán OBSERVED cạnh PDF chỉ chứng minh phần GTGT. Nội dung đúng ở một số bản ghi vẫn không hợp thức hóa đường dẫn chứng cứ. **Đề nghị** giữ nhãn và URL theo từng kết luận xuyên suốt record → index → note → pack. Với C3, giữ unknown có lý do cho quan hệ chưa kiểm được từ nguồn chính thức, rồi dựng và kiểm lại 11 record.

**B2 — Kiểm toán 1 mất câu trả lời có ngay trong giáo trình.** `retrieval/partition.py:315`, `:319`, `:339`; `curriculum/concepts/ke-toan-hanh-chinh-su-nghiep.yaml:472`; `evals/v3/kiem-toan-1_retrieval.jsonl:1`. `kt-d01` hỏi hai giả định của BCTC. Src-0197 tr.10–12 giải thích hoạt động liên tục và cơ sở dồn tích. Top-5 đều là src-0197. Sau bỏ cue và từ hỏi còn 6 token, 5 bigram. Coverage nội môn = 5/5, rival KTHCSN = 3/5. Nhánh rival không thể thỏa ngưỡng 0,75 và hơn nội môn 0,25. **Nguyên nhân trực tiếp** là nhánh `owners` phía trước: khi không khớp concept Kiểm toán 1, cụm chung “báo cáo tài chính” khớp canonical của KTHCSN, lập tức đặt insufficient. Tắt riêng match nước ngoài này trong RAM khôi phục partial, unknowns chỉ còn `no_course_concept_match`, 5 nguồn giữ nguyên. **Đề nghị** giữ concept hợp lệ ở cả hai môn. Chỉ sửa nhánh owners cho trường hợp chứng cứ nội môn phủ đầy đủ bigram và chủ đề đối thủ chỉ giải thích một phần câu hỏi: giữ partial và coi owner là gợi ý. Giữ nguyên nhánh OOV, ngưỡng rival, ranking và eval đóng băng. Chạy lại 188 câu cũ, 91 câu mới và cặp phản chứng hỏi thật sự lệch môn trước khi chốt quy tắc.

**B3 — Manifest phát hành đóng băng nhầm snapshot.** `pilot/core_freeze_manifest.json:32`, `:207`, `:213`; `AGENTS.md:28`; `reports/v3/PLAN_W6B_MON_MOI.md:51`. Đối chiếu SHA: manifest ghi inventory 595 dòng, `d7911dd1…`; hiện là 598, `a82e9c2f…`. HTTTKT1 ghi 1036 chunk/27 nguồn, thực 1081/30. External ghi 23 chunk, thực 47. Hai hash meta cũng lệch. 17 frozen suites core vẫn đúng. Trước review Git đã có `M pilot/core_freeze_manifest.json`. **Đề nghị** đóng băng lại sau thay đổi cuối, kiểm hash với đúng snapshot dự định phát hành. C2 yêu cầu tạo manifest nhưng luật Git cấm mọi thay đổi pilot trước commit. Cần ghi ngoại lệ có giới hạn cho manifest đã xác minh, hoặc thống nhất quy trình tại bước phát hành. Khôi phục mù manifest cũ sẽ giữ lỗi.

### MAJOR

**M1 — File .xls được stage nhưng không đi hết refresh.** `scripts/v3_refresh.py:276`, `:288`, `:307`, `:315`, `:325`, `:337`; `scripts/v3_extract_course.py:135`; `scripts/w6b_append_inventory.py:87`; kế hoạch W6b dòng 23. Tái hiện phần plan trong RAM với `Kế toán thuế 1/C1/sheet.xls`. Trong apply, .xls bỏ qua extract riêng nhưng vẫn đánh dấu partition bị ảnh hưởng, ghi inventory thiếu `index_include` và lý do, chỉ ghi hai field vào override rồi extract lại cả môn. Coverage Thuế 1 hiện có 25 lỗi PPTX, làm nhánh kiểm errors dừng. Ngay với môn sạch, một .xls có hash mới cũng bị đưa vào danh sách cần review concept/citation. 19 spreadsheet HTTTKT1 hiện đều có vấn đề về vị trí lưu cờ. **Đề nghị** ghi lý do/cờ ngay ở row, cho đường inventory-only đối với file không hỗ trợ và không thay thế nguồn đang index. Nếu thay thế nguồn đã phục vụ, vẫn phải xử lý tác động bỏ chunk. Phân loại PPTX đã chấp nhận thành skipped có lý do, giữ lỗi đọc bất ngờ là điều kiện dừng. Xác minh một file mới đi hết quy trình trong bản sao.

**M2 — Regression có thể in IDENTICAL dù toàn bộ suite hỏng.** `scripts/v3_regression.py:65`, `:68`, `:75`, `:91`. `negative.py` tạo raw lịch sử bằng baseline trong thư mục riêng rồi cho 8 subprocess trả 9. Kết quả 8 lần SCRIPT_FAIL và sau đó IDENTICAL, main trả thành công. Trường hợp chạy thật lần này đủ log của cả 8 suite. **Đề nghị** bắt nonzero thành lỗi gate, chỉ so đầu ra mới của run, kiểm đủ tập baseline/output. Khôi phục snapshot trong finally để ngoại lệ chưa so xong cũng trả dữ liệu về trước chạy. Run song song cần thư mục raw riêng hoặc khóa để tránh khôi phục đè lượt khác.

**M3 — Gate collision có thể xanh cho partition rỗng, direct có thể xanh cho coverage sai.** `scripts/v3_eval_course.py:34`, `:38`, `:67`; `evals/v3/ke-toan-hanh-chinh-su-nghiep_retrieval.jsonl:19`. Trong test âm, trả rỗng cho kthcsn-c01 → chính dòng báo fail nhưng contamination=0 và ALL_PASS. Trong dữ liệu thật, c03 hỏi so sánh hai môn, chỉ lấy một partition, coverage insufficient nhưng vẫn pass. Runner bỏ qua expected_coverage của 9 dòng mới khác kỳ vọng thực, gồm ht-d01/d02, k3-d01, kthcsn-d03/d05/d08/d09/s03/c03. **Đề nghị** bên cạnh contamination, gate phải kiểm collision có items và đúng scope. Báo riêng mọi sai expected_coverage và để release so hành vi với baseline. Với câu so sánh cần oracle về hai scope/nhu cầu hỏi lại; giữ nguyên file cũ, thêm ca độc lập.

**M4 — Cue Thuế 1 chiếm một chủ đề của KTTC3.** `curriculum/course_registry.yaml:148`, `retrieval/partition.py:48`, `curriculum/concepts/ke-toan-tai-chinh-3.yaml:413`. Hai ca tái hiện và biến thể kèm chương ở bảng router. Không có câu cũ frozen nào đổi detect, nhưng hỏi tự nhiên đã đi sai môn. **Đề nghị** ưu tiên tên môn đủ “Kế toán thuế 1”, mã môn hoặc chỉ dấu gọi tên môn, giữ chủ đề thuế TNDN hoãn lại như tín hiệu chủ đề. Không ép scope nếu còn hai cách hiểu. Kiểm cả nhãn môn ở giữa câu và thêm kiểm mã ACCO3301 nếu chính sách công nhận mã này như alias.

**M5 — Inventory khớp nguồn nhưng C đã viết lại dòng ghi ở A.** `scripts/w6b_ch4_update.py:42`, `:64`, `inventory/files.json:15335`, `scripts/v3_inventory.py:11`, `scripts/v3_extract_course.py:123`; hợp đồng Wave 6.2 ở `V3_EXPANSION_PLAN.md:332`. So JSON với `358a276` cho 32 thay đổi role/căn cứ phân loại, 3 đổi đường dẫn/filename, 1 thêm apparent_chapter (0543). Src-0001..0339 nguyên vẹn. Ba rename **do người học thực hiện**, 3 D + 6 untracked khớp hiện trạng: ba hash PDF cũ trùng tuyệt đối blob HEAD ở tên mới, ba nội dung mới là 0596..0598. Không có chứng cứ builder sửa nội dung PDF. Giữ ID giúp eval cũ tiếp tục trỏ đúng bytes, nhưng “chưa push” không phải ngoại lệ append-only đã ghi trong hợp đồng. `renamed_from` là dấu vết một lần, và cờ `added_in_w6b` còn tồn tại sau publish. **Đề nghị** giữ identity/hash, ghi sự kiện đổi đường dẫn tách khỏi row lịch sử hoặc xin quyết định migration một lần có old/new/hash và phiên bản. Hàm supersedes hiện yêu cầu cùng path nên không thể đơn giản thêm nó vào row đổi tên. Với role, sửa trực tiếp **đúng về authority hiện phục vụ, sai về lưu lịch sử**: extractor lấy content_role từ override nhưng lookup role thường như lecture_note/reference từ inventory. Sửa phép tính theo effective role hoặc dùng authority override có chứng cứ, không ép rewrite row để đạt điểm.

**M6 — Rebuild thông thường làm mất topic HTTTKT1.** `scripts/v3_extract_course.py:49`, `:145`; `work/he-thong-thong-tin-ke-toan-1/set_topics.py:20`; `scripts/v3_refresh.py:324`. So parse của 70 tài liệu HTTTKT1 với normalized hiện hành: 18 topic chỉ có sau bước hậu xử lý Pha B. Ví dụ script_4.4/4.5/4.6 đang có 4.4/4.5/4.6 nhưng parse lại đều trả null. Refresh gọi extractor/dedupe/candidates, không gọi bước gán từ heading trang 1. **Đề nghị** đưa quy tắc metadata có provenance vào đường build chung, giới hạn theo môn, rồi kiểm rebuild hai lần ra cùng topic và 339 dòng parser lịch sử vẫn khớp.

**M7 — Hồ sơ Pha C chưa đủ và tài liệu đang mô tả sai phạm vi.** `reports/v3/PLAN_W6B_MON_MOI.md:54`, `curriculum/course_manifests/he-thong-thong-tin-ke-toan-1.yaml:26`, `:42`, `:47`; `AGENTS.md:135`, `autopilot/state.yaml:33`. `W6B_FINAL.md` chưa có. Manifest môn vẫn bảo ba chủ đề chỉ có PPTX và ghi 1036 chunk. Registry có 13 môn curriculum retrieval, state và hướng dẫn vẫn nêu chín. Có manifest của HTTTKT1 và Thuế 1, thiếu manifest KTTC3/KTHCSN và cả bốn đường `course_scans/<C>.yaml` được liệt kê ở phạm vi Pha B. README, bảng hướng dẫn Grok và mục lục pack đã có môn mới. **Đề nghị** đồng bộ các tài liệu tra cứu đang dùng với snapshot sau Ch4, ghi rõ artifact nào có chủ đích không làm, phát hành C5 kèm các ngoại lệ và chờ quyết định của người học.

### MINOR

**m1 — Kiểm tên concept chưa phân biệt heading với câu văn.** `V3_EXPANSION_PLAN.md:368`; `scripts/v3_validate_concepts.py:58`; `curriculum/concepts/he-thong-thong-tin-ke-toan-1.yaml:170`, `:185`; `curriculum/concepts/ke-toan-thue-1.yaml:441`; `curriculum/concepts/ke-toan-hanh-chinh-su-nghiep.yaml:503`. Xem mẫu bên dưới. Hai tên sheet được chính báo cáo Pha B xác nhận lấy trong text. “Tờ khai hải quan” xuất hiện trong danh sách bộ chứng từ, “rút dự toán” trong diễn giải/ví dụ. Có text và có giá trị học tập nhưng thiếu bằng chứng là heading theo §6.5. **Đề nghị** trỏ chính xác đến heading/outline có thật hoặc ghi nhận loại thuật ngữ xuyên chủ đề và ngoại lệ được duyệt. Giữ alias có chứng cứ.

**m2 — Gate của file bổ sung và tên output không an toàn cho baseline báo cáo.** `scripts/v3_eval_course.py:51`, `:70`, `:75`, `:86`. R1 chỉ có direct nên hai category vắng thành False; kết quả lưu và stdout đều GATE_FAIL dù đúng 3/3, process vẫn exit 0. Cùng `--tag` giữa base và suffix ghi đè chung đường output. **Đề nghị** chấm phần bổ sung với metric áp dụng hoặc gộp base+r1 khi xét gate toàn môn; bảo toàn tên suffix ở output, trả mã lỗi cho thất bại thực.

**m3 — Harvest đã thêm trích dẫn nhưng 14 YAML cũ thiếu môn dẫn nguồn mới.** `research/curriculum_citations.json:2415`, `research/regulations/thong-tu-107-2017-tt-btc.yaml:13`, `scripts/v3_build_external.py:35`. Ví dụ TT107 thiếu KTHCSN/src-0409 tr.2 trong YAML. Join 130 ref bằng slug, đủ file nhưng 14 record thiếu ít nhất một course: Luật 83/2015, 88/2015, 97/2015, Luật các tổ chức tín dụng, Luật kế toán, Luật ngân sách nhà nước, Luật thuế gtgt, TT107/2017, TT133/2016, TT200/2014, TT45/2013, VAS 2/3/4. Một ref “Luật thuế gtgt” khớp filename nhưng YAML có dấu “…” ở cuối; runtime lookup theo chuỗi. **Đề nghị** merge lại occurrences/variants/cited_in_courses khi rebuild từ records, dùng cùng khóa chuẩn hóa và giữ nguyên phán định pháp lý.

**m4 — Trường tiên quyết KTTC3 mạnh hơn câu trích.** `curriculum/course_registry.yaml:166`, `work/ke-toan-tai-chinh-3/prerequisite_proposed.yaml:5`; đối chiếu src-0580 tr.1. Giảng viên nhắc kiến thức nợ phải trả đã học ở KTTC2; đây là căn cứ cho quan hệ học trước theo chủ đề. Registry ghi người học đã duyệt nhưng quan hệ chính thức bắt buộc toàn học phần chưa có dẫn chứng đề cương. `retrieval/partition.py:281` dùng trường này để lấy bằng chứng tiên quyết. **Đề nghị** giữ quyết định người học và ghi loại “tham chiếu kiến thức đã học” cùng trang; chỉ nâng thành điều kiện chính thức khi có căn cứ. HTTTKT1 ở `course_registry.yaml:141` đúng mức family: src-0404 tr.2 nói rõ học sau kế toán tài chính, không nêu phần nào. Không suy sang NLKT.

**m5 — Reload registry có thể tiếp tục định tuyến theo cue đã gỡ.** `retrieval/courses.py:29`, `:84`. Trong một process, detect ACCO2311, đổi REGISTRY_PATH sang backup, gọi reload_registry: get_course trả None nhưng detect vẫn ra Thuế 1. Sau khi clear riêng _cue_table thì trả rỗng. Không ảnh hưởng CLI mới khởi động. **Đề nghị** xóa cache _cue_table cùng các cache khác trong reload_registry.

**m6 — Hai cách ghi cùng TT80/2021 tạo hai bằng chứng.** `research/regulations/thong-tu-80-2021.yaml:1`, `research/regulations/thong-tu-80-2021-tt-btc.yaml:1`, `scripts/v3_build_external.py:46`. Record ngắn tự nhận đồng nhất với bản đủ hậu tố, nhưng cả hai phát riêng chunk về cùng quan hệ thay thế. **Đề nghị** chuẩn hóa theo số hiệu/cơ quan khi đủ chứng cứ, giữ variants và provenance của cả hai, chỉ index một kết luận.

**m7 — Thư mục môn rỗng không kích hoạt NEW_COURSE.** `scripts/v3_refresh.py:52`, `:67`, `:169`. Listing chỉ sinh row cho file. Thư mục mới chỉ chứa thư mục con rỗng và không có file cho cùng listing như trước; guard chỉ xét delta NEW. **Đề nghị** nếu quy tắc publishing phải phát hiện ngay cả thư mục trống thì lưu/tách danh sách tên thư mục cấp 1, hoặc mô tả điểm kích hoạt là “file đầu tiên trong thư mục môn mới”.

### NIT

**n1 — Bằng chứng Owen khác ấn bản.** `work/he-thong-thong-tin-ke-toan-1/role_overrides_proposed.yaml:10`; `inventory/files.json:14570`. Trang 1 PDF src-0341 là ảnh bìa Glenn Owen, *Using Excel & Access for Accounting 2013*; trang 1 của hướng dẫn src-0406 liệt kê bản 2016. Xem [ảnh bìa đã kiểm](../../work/codex_review/owen_cover.png). Role reference hợp lý, nhưng chưa chứng minh chính file 2013 là ấn bản được chỉ định. **Đề nghị** ghi cả hai ấn bản và giữ việc đồng nhất là suy luận.

**n2 — Ranh giới từ của cue ngắn lệch ví dụ regex trong đặc tả.** `retrieval/courses.py:78`, `V3_EXPANSION_PLAN.md:484`. `1hcsn` và `hcsn2` bị loại đúng; `_hcsn_` vẫn nhận TCHCSN vì biểu thức tự viết coi gạch dưới là dấu phân cách. Với quy tắc word boundary trong hợp đồng, gạch dưới và chữ đều là ký tự từ. Hành vi này có cả trước W6b. **Đề nghị** thống nhất cách xử lý identifier có gạch dưới và thêm ca biên tương ứng khi sửa router.

## 3. Kiểm chứng dữ liệu và nguồn

### Bất biến, provenance và chất lượng eval

- **Nguồn và core.** 598 ID liên tục. So 339 dòng đầu theo toàn bộ object với Git base, sau đó tính SHA-256 từng file hiện hữu so với inventory. Không thiếu/lệch. Không thấy diff của index 2.0.0, normalized/chunks core, concept registry/graph core, six engine directories, learner hoặc logs pilot được bảo vệ. Tập `frozen_suites` của manifest bằng bản base, 17/17 hash thực khớp. 17/17 entry FROZEN V3 khớp file, entry cũ giữ nguyên. Bốn hash/metrics trong báo cáo run1 bằng entry Pha B và FROZEN; r1 có entry riêng. Dữ liệu nhất quán với cam kết đóng băng.
- **32 thay đổi role.** Đã so toàn bộ proposal (kể cả proposal khai báo nhóm ID), trang 1 và role/authority của document hiện phục vụ. HTTTKT1 có 7 reference: 0341, 0343, 0352, 0362, 0376, 0388, 0399. Năm tệp hướng dẫn chương đều có tiêu đề hướng dẫn/tài liệu tham khảo ở trang 1 dù proposal nhóm chỉ trỏ một ví dụ. Bìa Owen là ảnh, có lưu riêng bằng chứng ở n1. Thuế 1 có 0539/0542 (script/ôn tập), KTHCSN có 0487 (script). KTTC3 gồm 0543–0544, 0546, 0548, 0550, 0552, 0554–0555, các ID chẵn từ 0568 đến 0592, và 0595. Trang 1 của 0543 ghi bài tập tự đánh giá chương 4; 0595 là hướng dẫn học tập. Ngữ liệu ủng hộ việc phân vai. Cách ghi vào lịch sử và sự khác nhau giữa hai ấn bản Owen đã nêu ở M5/n1. [Đối chiếu 32 dòng](../../work/codex_review/role_evidence.json)
- **Chất lượng đề.** 88/88 câu base tự qua router, không ép `pass_course`. Direct và source_bound kiểm được đúng nguồn/chương; ví dụ đề mẫu HTTTKT1 thực sự trượt nên phép đo có khả năng phân biệt. Những câu lặp tiêu đề hoặc gọi rõ tên môn chủ yếu kiểm tra tra cứu tài liệu. Trong 12 ca insufficient, WACC được dùng ở cả Thuế 1, KTTC3 và KTHCSN, có thể đạt chỉ nhờ từ ngoài từ vựng. Ca chênh lệch tỷ giá trong Thuế 1, tài sản thuế hoãn lại trong KTHCSN và phân bổ chi phí dở dang trong KTTC3 khó hơn, phù hợp để thử phân định phạm vi. Hai câu collision cơ bản mỗi môn dùng mẫu “Chương N của [tên môn]”, đúng playbook nhưng không đo được cue đa nghĩa nếu người học bỏ tên môn. KTHCSN c03 có hai cue thật và bộc lộ giới hạn oracle. Cả bốn bộ thiếu đối chứng gần như “kế toán thuế TNDN hoãn lại” không có nhãn môn. Không có bằng chứng file đề bị sửa để qua gate. Chưa thể dùng điểm này để kết luận hệ thống giải được bài tập hoặc tổng hợp được câu trả lời so sánh.
- **Export.** Nhãn course pack khớp course_id/chapter/filename/page_range/content_role của chunk, kể cả tên file từng đổi. Từng chunk được kiểm có thân text theo ngay sau nhãn; số lượng mỗi nhãn tính theo multiplicity. File 17 khớp text external dù kế thừa lỗi chứng cứ B1. Bộ 18–21 dùng chunk của xuất bản hiện hành. Quan hệ ngữ nghĩa đầy đủ giữa PDF và slide cùng chủ đề cần kiểm riêng, nhất là chỗ slide không có text.

### Mẫu 32 concept

Mỗi môn lấy tám vị trí cách đều từ đầu đến cuối YAML. Đối chiếu diễn ngôn quanh tên tại source_refs, đối chiếu thêm outline khi có biến thể. Cột alias là số alias của concept có mặt trong text môn / tổng alias khai báo. Dấu “—” nghĩa là không khai báo alias. Chứng cứ ngữ cảnh đầy đủ và số trang chứa từng alias ở [concept_sample.json](../../work/codex_review/concept_sample.json).

| Môn | canonical_name | Trang đối chiếu | Alias | Quan sát |
|---|---|---|---:|---|
| HTTTKT1 | Chương mở đầu: Giới thiệu môn học | src-0404 tr.1 | — | Heading chương/chủ đề. |
| HTTTKT1 | Các hàm thường dùng trong kế toán | src-0355 tr.1 | 2/2 | Heading chương/chủ đề. |
| HTTTKT1 | Nhóm hàm Database | src-0355 tr.2 | 2/2 | Mục 6 trong danh sách nhóm hàm. |
| HTTTKT1 | Kỹ thuật lập các sổ nhật ký | src-0363 tr.1 | — | Heading chương/chủ đề. |
| HTTTKT1 | Kỹ thuật lập sổ chi tiết và sổ cái tài khoản | src-0406 tr.3 | — | Heading chương/chủ đề. |
| HTTTKT1 | Thẻ tính giá thành sản phẩm | src-0377 tr.1 | 1/1 | Heading chương/chủ đề. |
| HTTTKT1 | Bảng tổng hợp chi tiết công nợ | src-0388 tr.1 | — | Tiêu đề mục trong hướng dẫn, kế đó là cấu trúc và cách lập. |
| HTTTKT1 | Lập báo cáo lưu chuyển tiền tệ | src-0401 tr.1 | — | Heading chương/chủ đề. |
| Thuế 1 | Giới thiệu môn học | src-0539 tr.1 | — | Heading chương/chủ đề. |
| Thuế 1 | Kế toán thuế Giá trị gia tăng | src-0530 tr.1 | 2/2 | Heading chương/chủ đề. |
| Thuế 1 | Các nội dung cơ bản liên quan đến thuế XK – NK | src-0500 tr.1 | 1/1 | Heading chương/chủ đề. |
| Thuế 1 | Các nội dung cơ bản liên quan đến thuế TTĐB | src-0510 tr.1 | 1/1 | Heading chương/chủ đề. |
| Thuế 1 | Nhận diện những rủi ro và cơ hội về thuế TTĐB tại doanh nghiệp | src-0518 tr.1 | 1/1 | Heading chương/chủ đề. |
| Thuế 1 | Nhận diện những rủi ro và cơ hội về thuế BVMT tại doanh nghiệp | src-0528 tr.1 | 1/1 | Heading chương/chủ đề. |
| Thuế 1 | Nhận diện rủi ro và cơ hội về thuế GTGT | src-0538 tr.1 | 1/1 | Heading chương/chủ đề. |
| Thuế 1 | Tờ khai hải quan | src-0504 tr.1 | — | Tên chứng từ trong danh sách, chưa xác minh heading. |
| KTTC3 | GIỚI THIỆU MÔN HỌC | src-0592 tr.1 | 1/1 | Heading chương/chủ đề. |
| KTTC3 | KẾ TOÁN HOẠT ĐỘNG NHẬP KHẨU TRỰC TIẾP | src-0550 tr.1 | 1/1 | Heading chương/chủ đề. |
| KTTC3 | Tổng quan về bất động sản đầu tư | src-0554 tr.1 | 2/2 | Heading chương/chủ đề. |
| KTTC3 | Kế toán chuyển đổi mục đích sử dụng | src-0564 tr.1 | 2/2 | Heading chương/chủ đề. |
| KTTC3 | TỔNG QUAN VỀ ĐẦU TƯ TÀI CHÍNH | src-0568 tr.1 | 2/2 | Heading chương/chủ đề. |
| KTTC3 | Kế toán dự phòng tổn thất đầu tư tài chính | src-0576 tr.1 | 3/3 | Heading đúng ở src-0568 tr.1. Trang được trỏ dùng biến thể khác, validator qua nhờ alias. |
| KTTC3 | PHÂN BIỆT CHÊNH LỆCH GIỮA SỐ LIỆU KẾ TOÁN VÀ SỐ LIỆU TÍNH THUẾ TNDN | src-0584 tr.1 | 3/3 | Heading chương/chủ đề. |
| KTTC3 | chi phí thuế TNDN hoãn lại | src-0584 tr.1 | — | Cụm nằm trong diễn giải. Có tên TK 8212 tại src-0586 tr.3, cần trỏ heading nếu dùng làm canonical. |
| KTHCSN | Giới thiệu môn học | src-0487 tr.1 | 1/1 | Heading chương/chủ đề. |
| KTHCSN | Tài khoản ngoài bảng | src-0413 tr.2 | — | Hai loại tài khoản được nêu trong câu diễn giải, chưa xác minh heading. |
| KTHCSN | Kế toán các khoản phải trả cho người lao động | src-0427 tr.1 | 2/2 | Heading chương/chủ đề. |
| KTHCSN | Kế toán tài sản cố định và đầu tư xây dựng cơ bản | src-0439 tr.1 | — | Heading chương/chủ đề. |
| KTHCSN | Kế toán doanh thu hành chính sự nghiệp | src-0449 tr.1 | 2/2 | Heading chương/chủ đề. |
| KTHCSN | Kế toán doanh thu hoạt động sản xuất kinh doanh, dịch vụ | src-0461 tr.1 | — | Heading chương/chủ đề. |
| KTHCSN | Kế toán phân phối kết quả các hoạt động | src-0475 tr.1 | 3/3 | Heading chương/chủ đề. |
| KTHCSN | rút dự toán | src-0419 tr.3 | — | Động tác nghiệp vụ trong câu/ví dụ, chưa xác minh heading. |

Đã kiểm **toàn bộ** edge và account_map ngoài mẫu. Ba edge HTTTKT1 trỏ src-0363 tr.3, 0364 tr.3, 0365 tr.2 (quan hệ lấy dữ liệu sổ và ghi sổ cái). Sáu edge KTTC3 trỏ 0558, 0560, 0562, 0564, 0582 và 0586 đều tr.1 (giảng viên nhắc chủ đề ngay trước). Cả chín quote có nội dung, khớp đúng trang sau chuẩn hóa Unicode/khoảng trắng. Thuế 1 và KTHCSN không khai báo edge. Account_map lần lượt 8, 4, 24, 37 số hiệu: 73/73 xuất hiện ít nhất hai lần kể cả khi yêu cầu tiền tố “TK” hoặc “tài khoản” và ranh giới số. Hash nguồn ở meta của cả bốn index đều nằm trong inventory. [Chi tiết edge và số lần xuất hiện của từng mã](../../work/codex_review/edge_account.json)

### Mẫu 8/24 record mới có status khác unknown

Kiểm riêng **URL mà build lưu**, đối tượng văn bản, quan hệ được tuyên bố và thời điểm chuyển tiếp. Một trang thuộc Chính phủ xác nhận ngày ban hành văn bản mới chưa đủ chứng minh nó bãi bỏ một văn bản cụ thể. Link bổ sung do reviewer tìm được không được tính là chứng cứ đã lưu trong build.

| Record / claim | Kết quả đọc nguồn |
|---|---|
| Luật 13/2008/QH12 → Luật 48/2024/QH15 | PDF chính thức mở được. Điều 18 khoản 1,3 trang 19/20 ghi mốc 01/07/2025 và chỉ đích danh luật cũ hết hiệu lực. Phù hợp với claim. [Công báo, Luật 48](https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/01/luat48.pdf) |
| Luật 107/2016/QH13 được Luật 90/2025 sửa | Trang văn bản đúng số, phạm vi thuế xuất nhập khẩu. Văn bản của Chính phủ đăng trên cổng Bộ Công Thương cũng dẫn rõ luật gốc và luật sửa. Xác nhận quan hệ này; danh sách mọi sửa đổi về sau chưa được kiểm toàn bộ. [Luật 90](https://vanban.chinhphu.vn/?docid=214558&pageid=27160) · [Văn bản dẫn chiếu](https://vntr.moit.gov.vn/vi/legal-documents/501) |
| TT24/2024/TT-BTC được TT46/2025 sửa | Đúng văn bản; trả lời của BTC xác định khoản 1 Điều 2 TT46 sửa đối tượng áp dụng, bỏ ngoại lệ UBND cấp xã. [TT46](https://chinhphu.vn/?docid=214192&pageid=27160) · [Giải đáp của BTC](https://isa.mof.gov.vn/hoidapcstc/home/cthoidap/156408) |
| TT78/2021/TT-BTC → TT32/2025/TT-BTC | Chính URL trong record đăng nội dung khoản 1 Điều 12, đúng số văn bản thay thế và ngày 01/06/2025. [Cổng Chính phủ, Điều 12](https://xaydungchinhsach.chinhphu.vn/mot-so-noi-dung-moi-cua-thong-tu-so-32-2025-tt-btc-ve-hoa-don-chung-tu-119250608110422544.htm) |
| TT23/2023/TT-BTC → TT141/2025/TT-BTC, INFERRED | URL build xác nhận số, đối tượng và ngày. Reviewer tìm được xác nhận trực tiếp của Bộ ban hành về thay thế, hiệu lực 01/01/2026. Có thể cập nhật record bằng nguồn này. [TT141](https://vanban.chinhphu.vn/?docid=216466&pageid=27160) · [Bộ Tài chính xác nhận thay thế](https://mof.gov.vn/tin-tuc-tai-chinh/tin-chinh-sach-tai-chinh/mot-so-luu-y-trong-trien-khai-thuc-hien-thong-tu-so-1412025tt-btc) |
| TT78/2014/TT-BTC → TT20/2026/TT-BTC, INFERRED | Metadata của BTC đúng văn bản. PDF scan có 22 trang; chưa xác minh trực tiếp câu ở khoản 6 Điều 10 qua bản ký. Có nguồn công khai của cơ quan địa phương xác nhận thay thế TT78 và TT96, từ kỳ 2025. Quan hệ có thêm căn cứ, record chưa gắn bằng chứng điều khoản chính thức mà nó viện dẫn. [Bản ký TT20](https://datafiles.chinhphu.vn/cpp/files/vbpq/2026/3/20-btc.pdf) · [Thông tin phổ biến của tỉnh Vĩnh Long](https://portal.vinhlong.gov.vn/portal/wpipbc/ipbc/page/xemtin.cpx?item=69b9094a1a3f9b0c757273f9) |
| TT80/2021/TT-BTC → TT89/2026/TT-BTC, INFERRED | Trang Chính phủ xác nhận TT89 hiệu lực 01/07/2026 và có cả bản đính chính. Log `ref_126.json` dùng nguồn phụ cho bãi bỏ. PDF ký vượt giới hạn tải của công cụ (17.281.751 byte); chưa xác nhận trực tiếp Điều 99 hoặc ảnh hưởng đính chính. Không nâng nhãn. [TT89 và bản đính chính](https://vanban.chinhphu.vn/?docid=218974&pageid=27160) |
| Luật 106/2016/QH13 hết hiệu lực toàn bộ 01/01/2026, INFERRED | PDF Luật 48 Điều 18 khoản 3 xác nhận quan hệ với phần GTGT. Record gộp thêm phần QLT và TTĐB; chính scope ghi điều khoản cuối dựa nguồn phụ. URL đầu của chunk không chứng minh cả ba phần, nên nhãn OBSERVED trong file 17 sai kể cả khi kết luận cuối có thể đúng. [Luật 48, Điều 18](https://datafiles.chinhphu.vn/cpp/files/vbpq/2025/01/luat48.pdf) |

G5 của hợp đồng rộng cho phép ghi INFERRED (`V3_EXPANSION_PLAN.md:326`); §9.11 và C3 yêu cầu để unknown/có lý do khi chưa xác minh được chính thức. Các record bộc lộ bất định tốt hơn bản export. 11 ID cần rà lại gồm Luật 106/2016, 21/2012, 27/2008, 70/2014; NĐ123/2020; TT219/2013, 228/2009, 23/2023, 78/2014, 80/2021 có và không có hậu tố. Không có record mới nào gán trạng thái in_force do không tìm thấy văn bản thay thế.

## 4. Giới hạn và quyết định phát hành

- Chỉ có 9 mốc retrieval cũ. Không thể cung cấp phép so W6bPre cho TCDN1. Full-package replay trước W6b dùng registry/detector backup vì các runner lịch sử không lưu gợi ý cho mọi category. Các trường baseline thực sự lưu đều khớp.
- Hash/run1 cho biết trạng thái hiện tại khớp dữ liệu đã ghi. Chúng không chứng minh trình tự tác giả viết đề, thời điểm tinh chỉnh hoặc chưa từng sửa rồi phục hồi trong Pha B/C chưa commit. Không quy kết dạy theo đề từ điểm cao.
- Không chạy `freeze_core.py`, `v3_refresh.py --apply` hoặc ghi file giả vào thư mục môn. Kết luận về publish .xls dựa trên test plan trong RAM, điều kiện trong code và coverage thật của môn đích. Điều kiện mtime/rollback/concurrency của một publish thật chưa được diễn tập. So nguồn bằng SHA-256 và Git xác nhận nội dung, không xác định ai đổi tên hoặc thời điểm đổi tên ngoài mô tả của người học.
- 32 concept được đọc theo mẫu, chín edge và 73 account kiểm toàn bộ. Đối chiếu số trang với PDF và text normalized không thay thế đánh giá trực quan từng slide/trang, ngữ nghĩa mọi alias hoặc khả năng dạy người học thật. Đã kiểm online tám record, không chứng nhận toàn bộ lịch sử hiệu lực của 62 văn bản tại ngày phát hành. Không có Jev MCP khả dụng trong phiên; quyết định phát hành dưới đây là phán định của reviewer từ các phép thử.
- File/log và bản sao kiểm thử được giữ trong `work/codex_review/`, tách khỏi đầu ra build. Từ đầu đến cuối review, ngoài vùng được phép không phát sinh thay đổi tracked do test. Không dùng thao tác Git ghi trạng thái, không commit hay push.

**Kết luận: chưa push W6b.** Ưu tiên giữ nguyên nhãn pháp quy xuyên suốt đường phục vụ, khôi phục hành vi kt-d01 và sửa gate có thể xanh giả. Sau đó kiểm luồng refresh dự kiến, chốt chính sách lịch sử inventory, đóng băng đúng snapshot và hoàn tất C5 trước khi xin quyết định publish.

`BLOCKER=3 MAJOR=7 MINOR=7 NIT=2`

