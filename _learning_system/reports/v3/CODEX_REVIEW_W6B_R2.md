# W6b · Review độc lập vòng 2 sau đợt D

**Quyết định: chưa push.** Snapshot hiện tại chạy core `IDENTICAL`, đủ 10 raw. Trong 279 câu retrieval chỉ `kt-d01` đổi so với vòng 1, đúng quyết định đã duyệt. Tuy nhiên, cùng một lượt thiếu kết quả của Phase 2 có thể đổi từ `DIFFERENT` sang `IDENTICAL` chỉ bằng việc thiếu thêm một file baseline. Hai cổng khác cũng trả thành công khi dữ liệu kiểm thử thực sự sai. Đây là lý do giữ bản sửa để hoàn thiện trước khi phát hành.

Đối tượng kiểm là working tree trên `HEAD 5c845c7`, gồm cả file chưa track. Mốc so sánh là báo cáo R1, kết quả từng dòng từ mirror R1, bản nháp G01–G23 và các bản trước sửa trong `work/w6b/`. Dùng CPython **3.12.14** của Codex, `-X utf8`, `PYTHONDONTWRITEBYTECODE=1`, `HOC_ROOT` trỏ từng bản sao. Dưới đây, đường dẫn không ghi gốc tính từ `_learning_system/`. Mỗi mã đang mở được đếm một lần. G02, G07, G18 đã đóng theo quyết định của người học.

## 1. Phán định toàn bộ 19 finding vòng 1

| R1 | Phán định | Bằng chứng quyết định |
|---|---|---|
| B1 · nhãn pháp quy | **SỬA CHƯA ĐỦ** | Đúng trên dữ liệu phát hành. Join đủ 47 chunk, 11/11 nhãn INFERRED đi đến cả note và câu trả lời. G03/G04 đóng. Khi trường nguồn có giá trị null, builder tự nâng lên OBSERVED và eval vẫn xanh (G24). |
| B2 · Kiểm toán 1 | **ĐÃ SỬA ĐÚNG** | Thử riêng hàm trước B2 và hàm đang phục vụ trên cùng index. Trong 188+91 câu, chỉ `kt-d01` đổi insufficient → partial. `kt-i02`, `kn-i02` đều tiếp tục insufficient. G02 đóng. |
| B3 · manifest core | **ĐÃ SỬA ĐÚNG** | SHA inventory, 598 row, 16/16 partition, 17/17 bộ core, số dòng và SHA khớp. Toàn bộ khối frozen_suites bằng HEAD. Ngoại lệ freeze cuối kỳ có ở `AGENTS.md:27–30`. |
| M1 · refresh | **ĐÃ SỬA ĐÚNG** | Luồng spreadsheet đạt yêu cầu về row, review, affected và cổng extractor. Hai NEW + một CHANGED → APPLIED []. 19/19 row lịch sử đã có cờ. G05/G10 đóng. Còn một lần dựng external thừa do m3, đã tính ở G17. |
| M2 · comparator | **SỬA CHƯA ĐỦ** | Suite exit 9, bỏ 10 raw, raw cũ còn mới và baseline rỗng đã bị bắt. Thiếu 1 trong 10 baseline vẫn có thể xanh giả (G01). |
| M3 · collision và coverage | **ĐÃ SỬA ĐÚNG** | 27/27 collision thật qua. Bỏ items của `kthcsn-c01` làm gate fail dù contamination=0. Cả 20 mismatch có oracle đều được báo. G11 đóng. Tính chất cảnh báo coverage và exit code được phân tích riêng ở §3, G09. |
| M4 · cue Thuế 1 | **SỬA GÂY LỖI** | 793 trường frozen không đổi. Hai ca mất scope trong nháp đã nhận lại Thuế 1. Cue “học kế toán thuế” lại làm mất scope KTTC3 đã đúng trước G06. Hai câu nhập khẩu từng đúng ở R1 vẫn mất môn. |
| M5 · lịch sử inventory | **ĐÃ SỬA ĐÚNG** | Đã ghi rõ ngoại lệ một lần trong `reports/v3/W6B_FINAL.md:33`. So commit 358a276 thấy đúng 32 role và 3 đường dẫn có trong lịch sử. Cả 3 giữ ID, hash và có renamed_from. G07 đóng. |
| M6 · topic khi rebuild | **SỬA CHƯA ĐỦ** | Hai lượt CLI HTTTKT1 khớp snapshot về topic, nội dung document và pages. Parser 339/339 giữ nguyên. Fixture chapter=4 không có heading trả topic/title/rule=null. Hai fixture có chữ “Chương” vẫn tạo provenance sai (G12). |
| M7 · hồ sơ | **SỬA CHƯA ĐỦ** | Có đủ bốn manifest, đúng 13 môn trong state và sáu hướng dẫn. Bốn course_scan được ghi là chủ đích bỏ. G14/G15 đóng. G13 đếm đúng PPTX nhưng không báo khi hai nguồn thống kê mâu thuẫn. Bảng giới hạn cuối báo cáo và hướng dẫn còn thông tin cũ (G23/G26). |
| m1 · tên concept | **CHƯA SỬA (có chủ đích)** | Bốn YAML concept cùng SHA với mirror R1. Các validator đều qua. Mẫu R1 về “Tờ khai hải quan”, “rút dự toán” và hai tên sheet vẫn chỉ có chứng cứ xuất hiện trong text (G16). |
| m2 · file bổ sung | **SỬA CHƯA ĐỦ** | Supplement thật 3/3. Trống bị từ chối. Cùng tag bình thường cho hai output riêng. Có va chạm khác khi ghép suffix với tag và CLI vẫn exit 0 với gate fail ngoài waiver (G09). |
| m3 · metadata citation | **SỬA CHƯA ĐỦ** | 13 YAML sửa đúng, chỉ khác trong ba trường provenance. Hai tên “Luật thuế gtgt” và “Luật thuế gtgt…” còn chung slug. Một tập nguồn bị mất (G17). |
| m4 · quan hệ KTTC3 | **ĐÃ SỬA ĐÚNG** | Registry, manifest và `W6B_FINAL.md:34` ghi KTTC2 là kiến thức giảng viên nhắc đã học, dẫn src-0580 tr.1. Cách lưu trong explicit_prerequisites đã được duyệt. G18 đóng. |
| m5 · cache registry | **ĐÃ SỬA ĐÚNG** | Cùng process, dò ACCO2311, đổi sang registry trước W6b và reload, rồi khôi phục và reload. Kết quả Thuế 1 → ∅ → Thuế 1. |
| m6 · TT80 ghi đôi | **CHƯA SỬA (có chủ đích)** | Câu hỏi về TT80 vẫn trả cả record ngắn và record đầy đủ (G19). |
| m7 · thư mục môn rỗng | **CHƯA SỬA (có chủ đích)** | listing của fixture có duy nhất một thư mục môn rỗng là []. NEW_COURSE chỉ có cơ hội chạy sau khi có file (G20). |
| n1 · ấn bản Owen | **CHƯA SỬA (có chủ đích)** | SHA tài liệu nguồn khớp. Đối chiếu bìa 2013 và hướng dẫn dẫn 2016 kế thừa từ R1 (G21). |
| n2 · ranh giới cue | **CHƯA SỬA (có chủ đích)** | `detect_courses('_hcsn_')` vẫn trả Tài chính HCSN (G22). |

## 2. Tám file đã sửa và bằng chứng cho từng diff

Đã lưu ba diff cho mỗi file: `<stem>.HEAD.diff`, `.before.diff`, `.r1.diff`. Cột số là **số dòng bản diff** theo thứ tự HEAD / backup chỉ định / mirror R1, gồm cả header và context. Bảy backup tương đương nội dung R1 sau khi đọc UTF-8. Riêng `registry.before_M6.yaml` đã có thay đổi cue nên dùng thêm `registry.before_G06.yaml` và registry thật của R1. [Danh mục diff](../../work/codex_review_r3/diffs.json)

| File | Backup trong work/w6b | Diff | Hành vi sau sửa và hồi quy |
|---|---|---:|---|
| scripts/v3_build_external.py | v3_build_external.before_B1.py | 38/36/36 | CLI mặc định và `--from-records` dựng 47 chunk đúng bytes. Không cờ giữ nguyên 131 YAML, còn đủ 11 INFERRED. Đường bootstrap Wave 5 có cờ riêng. Lỗi khi nhãn null ở G24. |
| retrieval/external.py | external.before_B1.py | 64/62/62 | Đã kiểm nhãn note với YAML và nguồn/ngày đến director trên cả 11 câu. Không thấy mất nhãn trên dữ liệu thật. |
| scripts/v3_regression.py | v3_regression.before_M2.py | 67/55/55 | Bắt output cũ và child nonzero. Core thật và phục hồi raw/pilot qua. Thiếu một baseline vẫn có thể mất luôn phép so (G01). |
| scripts/v3_refresh.py | v3_refresh.before_M1.py | 116/74/74 | XLS/XLSX và revision được inventory-only. Gate chấp nhận đúng lỗi PPTX của môn và dừng với PDF hỏng. Có side effect lên index external khi hai citation chung slug (G17). |
| scripts/v3_extract_course.py | v3_extract_course.before_M6.py | 35/33/33 | Cờ HTTTKT1 chi phối topic dẫn từ trang 1. Fixture không có heading để trống topic, nhưng vẫn nhận sai dòng “Chương trình” (G12). Đối chứng môn không cờ và phần thời gian ghi ở §3. |
| scripts/v3_eval_course.py | v3_eval_course.before_M3.py | 71/63/63 | Gate collision, WARN và supplement hoạt động trên dữ liệu thật. Hợp đồng mã thoát và tên file chưa an toàn (G09). |
| retrieval/courses.py | courses.new.py | 12/10/10 | reload xóa cache cue trong cùng tiến trình. Đối chiếu đủ 37 file frozen, không thấy hồi quy do thay đổi hàm reload. |
| curriculum/course_registry.yaml | registry.before_M6.yaml | 80/29/35 | Cờ topic, thuyết minh tiên quyết, các mã/cue mới có hiệu lực. G06 tái hiện mất môn khi cue ngữ cảnh gặp nhãn KTTC3. |

## 3. Phép kiểm trên snapshot và đối chứng âm

### Core, eval và B2

Core chạy thật tám suite, mười raw, exit 0, `diff.txt=IDENTICAL`. Đối chiếu SHA sau chạy với mọi raw lịch sử và file pilot tương ứng không thấy thay đổi. SHA-256 inventory là `f9c8e48e26b15b3a03b401d9c77c57d5bc70f6330210f33565d23f439272d5b5`. Cả 598 file nguồn đúng hash inventory. Kiểm riêng FROZEN.json của V3 cũng khớp SHA 17/17 entry. [Đối chiếu V3](../../work/codex_review_r3/frozen-v3.json) Ở mỗi partition đã đối chiếu số dòng chunk với manifest, meta, số chunk ID, SHA file meta và số hash nguồn. [Manifest đối chiếu từng suite/partition](../../work/codex_review_r3/freeze.json) · [Log core](../../work/codex_review_r3/regression.log)

Số chunk theo manifest: KTTC2 464, KTCP 362, Kiểm toán 1 358, KTNH 959, NHTM 357, TCDN1 (catalog) 392, TTTC 196, TCHCSN 768, Luật KD 177, Kinh doanh và nghiệp vụ 521, learner-notes 307, external 47, HTTTKT1 1081, Thuế 1 673, KTTC3 379, KTHCSN 569.

Với B2, chỉ hoán đổi hàm `retrieve_partition` trước/sau trên cùng dữ liệu và cùng registry. Nhánh `retrieval/partition.py:319–329` giữ coverage ban đầu nếu bigram trong môn phủ 100% và hơn từng owner ít nhất 0,25. Mốc R2 cho `kt-d01` là 1,0 so với 0,6. Hai câu tài sản cố định đều 1,0 so với 1,0. Lượt hiện tại xác nhận top-5 của `kt-d01` cùng src-0197, coverage partial, grounded=true. Hai câu đối chứng tiếp tục bị từ chối. Câu trả lời render mới trích đoạn dẫn nhập và chỉ trang 11–12. Phép thử chứng minh sửa từ chối sai và tìm được nguồn, chưa chứng minh tutor đã trình bày đủ hai giả định. **Chấp nhận bản sửa đã duyệt.** [A/B đủ 279 dòng](../../work/codex_review_r3/b2-live.json) · [Ba câu trả lời thực](../../work/codex_review_r3/inputs.json)

| Bộ eval | n | Nguồn@5 | Chương@1 | Source-bound | Insufficient | Account | Topic owner | Collision sai/tổng | Gate thô |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| KTCP | 23 | 90% | 80% | 100% | 100% | 100% | 0% | 0/2 | FAIL (waiver D2) |
| KTNH | 22 | 100% | 83,3% | 100% | 100% | 100% | — | 0/2 | PASS |
| KTTC2 | 23 | 100% | 90% | 100% | 100% | 100% | 100% | 0/2 | PASS |
| Kiểm toán 1 | 20 | 100% | 100% | 100% | 100% | — | — | 0/2 | PASS |
| Kinh doanh và nghiệp vụ | 20 | 100% | 100% | 100% | 100% | — | — | 0/2 | PASS |
| Luật KD | 20 | 100% | 91,7% | 100% | 100% | — | — | 0/2 | PASS |
| NHTM | 20 | 91,7% | 83,3% | 100% | 100% | — | — | 0/2 | PASS |
| TCHCSN | 20 | 100% | 83,3% | 66,7% | 100% | — | — | 0/2 | PASS |
| TTTC | 20 | 100% | 100% | 100% | 100% | — | — | 0/2 | PASS |
| HTTTKT1 | 24 | 100% | 92,9% | 66,7% | 100% | 100% | — | 0/2 | PASS |
| Thuế 1 | 20 | 100% | 80% | 100% | 100% | 100% | — | 0/2 | PASS |
| KTTC3 | 23 | 91,7% | 100% | 100% | 100% | 100% | — | 0/2 | PASS |
| KTHCSN | 21 | 100% | 90% | 100% | 100% | 100% | — | 0/3 | PASS |
| HTTTKT1 supplement | 3 | 100% | 100% | — | — | — | — | 0/0 | PASS |

So với R1, mọi metric cũ bằng nhau trước khi làm tròn. 27 collision đều có items, đúng partition, không contamination. Gate mới `collision_rows_failed` qua mọi bộ. Chỉ hai gate đã tồn tại đổi giá trị: `source_bound` và `insufficient` của `_r1` từ false sang true vì category vắng được tính n/a. 12/13 bộ base đạt trực tiếp. KTCP trượt riêng gate topic_owner, 0/3, đúng waiver D2 dành cho kp-t01..03. Có 20 dòng lệch expected_coverage, gồm kn-c02 và kthcsn-c03. Tập WARN khớp phép join độc lập trên từng category. Một câu hỏi so sánh có thể đạt gate cách ly môn và vẫn trả insufficient. [Tất cả delta, mismatch, điểm chưa làm tròn](../../work/codex_review_r3/metrics.json)

Plan không thêm fixture trả 0 NEW / 0 CHANGED / 0 MISSING, blocked=null. External 5/5, all_pass, record_contracts và additive_isolation đều PASS, cùng kết quả vòng 1. Validator bốn môn lần lượt HTTTKT1 36, Thuế 1 35, KTTC3 28, KTHCSN 37 concept, cả bốn exit 0. [Plan](../../work/codex_review_r3/plan.log) · [Eval external](../../work/codex_review_r3/external.log)

### B1, G03/G04 và pack

Có 131 YAML, gồm 100 UNKNOWN, 20 OBSERVED và 11 INFERRED. 31 record có trạng thái xác định phát đúng một summary/record. 16 chunk còn lại là đoạn PDF chính thức. Đối chiếu cả `relative_path`, SHA nguồn, nhãn, URL chính thức đầu tiên nếu có, tiêu đề file 17 và phần text ngay sau nhãn. **47/47 khớp, gồm 36 OBSERVED và 11 INFERRED.** Tìm được 26 regulation note khác nhau qua `external_notes` trên chunk giáo trình, trong đó đủ cả 11 INFERRED.

11 record được kiểm riêng: Luật 106/2016/QH13, Luật 21/2012/QH12, Luật 27/2008/QH12, Luật 70/2014/QH13, Nghị định 123/2020/NĐ-CP, Thông tư 219/2013/TT-BTC, Thông tư 228/2009, Thông tư 23/2023/TT-BTC, Thông tư 78/2014/TT-BTC, Thông tư 80/2021/TT-BTC, Thông tư 80/2021.

Với từng ref trong danh sách, đã gọi `answer(ref + ' còn hiệu lực không?', filters={'course_id':'external'})`. Record đích xuất hiện trong nhóm được render, có dòng “suy luận”, ngày kiểm của record và URL nguồn đã đối chiếu. Đối chứng trước/sau đợt D, cùng 11 câu này và ba câu OBSERVED, cho items, evidence, coverage, unknowns, analysis và grounded giống nhau trên 14/14 câu. Từng item hiển thị có nhãn tương ứng. [Đối chứng trước/sau director và external](../../work/codex_review_r3/legal-ab.json) G14: mục 17 cuối mục lục ở HEAD chạy thành công. Thiếu hẳn mục 17 thì exit 1 trước khi đụng file sentinel. G15: chạy exporter đủ bộ hai lần, SHA bộ pack bằng bản phát hành. Phần 21 p1 có đúng 35 tên, p2 có đúng 8 tên, so theo tập tên thật trong từng file. [Kết quả join, notes và câu trả lời](../../work/codex_review_r3/external-detail.json) · [Fixture mục lục](../../work/codex_review_r3/packs.json)

### M1, G05/G10 và M6

Chạy `--apply` đầu-cuối trên deployment riêng trong `work/codex_review_r3/a/`. Tạo XLS mới trong Thuế 1, workbook XLSX hợp lệ và thay đổi một XLS có sẵn ở HTTTKT1. Plan 2/1/0. Apply exit 0, APPLIED [], không yêu cầu review. Src-0599, 0600, 0601 có `index_include=false` và `exclusion_reason=unsupported_extension`. 0601 supersedes src-0345. Không file chunks nào đổi hash. Ngoài snapshot thử, 18 XLS + 1 XLSM thật ở HTTTKT1 đều có hai cờ. Thử đổi nội dung non-core mà giữ kích thước trả 0/0/0, đúng giới hạn đã công bố tại `README.md:22`. [Row và danh sách publish](../../work/codex_review_r3/sheets.json)

Chèn TXT đọc được vào Thuế 1 khiến apply dựng môn với 25 lỗi PPTX `not wired`. Candidate đi qua cổng extraction và dừng ở bước **REVIEW_REQUIRED** cho nội dung TXT mới. Chèn PDF hỏng mới thì dừng ngay tại bước đọc nguồn. Để thử đúng cổng toàn môn, làm hỏng src-0492 trong fixture, đồng bộ SHA/kích thước inventory thử, rồi dùng TXT để kích hoạt rebuild: `Extraction gate failed: ke-toan-thue-1 [('src-0492', …)]`. Đối chứng thứ ba: từ inventory đã publish, thay trực tiếp PDF đang có chunk src-0492 bằng PDF lỗi khác kích thước. Plan chỉ có 1 CHANGED. Apply exit 2 trước publish, SHA inventory giữ nguyên. [Gate PDF toàn môn](../../work/codex_review_r3/bad-existing-apply.log) · [CHANGED có thật](../../work/codex_review_r3/changed-indexed.json)

Hai lượt `v3_extract_course.py --course he-thong-thong-tin-ke-toan-1` đều cho 70 documents, 549 pages, 18 topic từ trang 1. Không có topic khác snapshot. Cả hai lượt và snapshot có SHA pages `749d9a586cc3aaf1e368b5f6d20d392fdcc9eca3a7a9f1fde8fe521189944787`, coverage giống nhau. Documents bằng nhau sau khi bỏ đúng `provenance.extracted_at`, hash bytes thô khác vì đồng hồ. 339 đầu vào parser đầu tiên cho dict giống nhau giữa backup trước W6b, trước M6 và hiện tại. Tài liệu thử chỉ có “Bài giảng dùng để ôn tập.”, inventory chapter=4, cho ba trường topic/title/rule đều null. Đã chạy trước/sau trên toàn bộ 12 môn retrieval còn lại và TCDN1 catalog: documents (trừ extracted_at), SHA pages và coverage đều bằng nhau. Riêng Luật kinh doanh, chạy cùng đồng hồ cố định cho SHA bytes của cả ba file giống hệt nhau. [Hai lượt HTTTKT1](../../work/codex_review_r3/ht.json) · [Đối chứng cố định thời gian](../../work/codex_review_r3/fixedtime.json)

### M4 và G06 trên câu hỏi tự nhiên

So detector R1 với hiện tại trên mỗi trường `question`, kể cả trong object/list lồng: **793 lượt / 37 JSONL, 0 delta**. Hai ca R2 nháp “Em đang ôn kế toán thuế, cho em ví dụ cách tính thuế GTGT nhé” và “Khi làm bài kế toán thuế xuất nhập khẩu…” đã trở lại Thuế 1. Câu trần “Em chưa rõ kế toán thuế TNDN hoãn lại khác thuế hiện hành chỗ nào” không còn bị cue trần ép sang Thuế 1. Bảng dưới là 12 câu viết thêm trong lần chạy này. Mỗi ô ghi **partition thực phục vụ**, không suy ra môn từ tên xuất hiện trong câu hỏi. [793 lượt và 15 câu đối chứng trước](../../work/codex_review_r3/routes.json) · [12 câu mới, detect và suggestions](../../work/codex_review_r3/tax12.json)

| Câu hỏi | R1 | Trước G06 | Sau D |
|---|---|---|---|
| Kế toán thuế nhập khẩu ghi nhận thuế phải nộp ở tài khoản nào? | Thuế 1 | ∅ | ∅ |
| Kế toán thuế XNK xử lý tiền thuế nộp thừa như thế nào? | Thuế 1 | ∅ | ∅ |
| Phần kế toán thuế bảo vệ môi trường có ví dụ tính thuế trên túi ni lông không? | Thuế 1 | ∅ | Thuế 1 |
| Ở phần kế toán thuế TNDN hoãn lại của KTTC3, em tính chênh lệch tạm thời thế nào? | ∅ | KTTC3 | KTTC3 |
| Em đang học kế toán thuế TNDN hoãn lại trong KTTC3, vì sao có tài sản thuế hoãn lại? | ∅ | KTTC3 | ∅ |
| Kế toán thuế đầu vào của hàng nhập khẩu xử lý thế nào? | Thuế 1 | ∅ | ∅ |
| Môn Kế toán thuế 1 cho khấu trừ thuế GTGT đầu vào ở kỳ nào vậy? | Thuế 1 | Thuế 1 | Thuế 1 |
| Em có lô rượu nhập khẩu, mình tính TTĐB trên giá trước hay sau thuế nhập khẩu? | ∅ | ∅ | ∅ |
| Bài kế toán thuế GTGT yêu cầu tách đầu vào dùng chung, phải chia theo doanh thu nào? | Thuế 1 | ∅ | Thuế 1 |
| Ở KTTC3, nếu thuế suất năm sau giảm thì khoản thuế TNDN hoãn lại được đo lại thế nào? | KTTC3 | KTTC3 | KTTC3 |
| Thầy cho em hỏi KTT1 hạch toán tiền thuế bảo vệ môi trường nộp thay ra sao? | ∅ | Thuế 1 | Thuế 1 |
| Kế toán thuế 1: hàng đã xuất đi rồi bị trả lại thì điều chỉnh thuế XNK lúc nào? | Thuế 1 | Thuế 1 | Thuế 1 |

∅ là partition=null. Hệ thống có thể trả nhánh core hoặc yêu cầu xác định môn. Trong câu hỏi không nhãn có cụm “thuế hiện hành” nêu trên, detect hiện trả [], nhưng partition thực là **external**, coverage partial vì cue “hiện hành” trong `retrieval/external.py:11`. Đó vẫn là một câu hỏi kế toán chưa được đưa đúng về nội dung học.

## 4. Finding còn mở, theo mức ảnh hưởng

### BLOCKER

**G01 · Comparator có thể ký IDENTICAL khi thiếu đầu ra bắt buộc.** `scripts/v3_regression.py:54–58,81`. Cho tám child trả 0 và sinh đúng chín raw trừ `retrieval_benchmark_raw.json`. Có đủ 10 baseline → DIFFERENT 1, exit 1. Cùng child, chỉ bỏ đúng baseline thứ mười khỏi bản sao → **IDENTICAL, exit 0**. Baseline rỗng đã bị từ chối. 10 raw lịch sử mới tạo mà child không ghi → DIFFERENT 10. Child exit 9 dù đủ mười raw mới giống baseline → DIFFERENT 1. Snapshot thật đủ bộ. Trước khi ký kết quả, đối chiếu **tập tên cụ thể** của mười baseline và mười raw mới với danh mục độc lập. [Bốn đối chứng cùng harness](../../work/codex_review_r3/reg_gate.json) · [No-write với raw gần đây](../../work/codex_review_r3/recent.log)

### MAJOR

- **G06 · Cue Thuế 1 lấn nhãn KTTC3 và còn bỏ sót câu XNK.** `curriculum/course_registry.yaml:148–165`, `retrieval/courses.py:95`. “Em đang học kế toán thuế TNDN hoãn lại trong KTTC3…” từng phục vụ KTTC3 ngay trước G06. Sau G06, “học kế toán thuế” cộng KTTC3 thành hai scope, partition=null. “Kế toán thuế XNK xử lý tiền thuế nộp thừa như thế nào?” từng vào Thuế 1 ở R1, hiện scope trống, không có cả gợi ý Thuế 1. Ưu tiên nhãn môn rõ trong ngữ cảnh và kiểm các cách gọi nghiệp vụ khi thiếu nhãn bằng bảng §3.
- **G08 · Allowlist migration kiểm basename nên nhận cả đường dẫn ngoài sáu đường được duyệt.** `scripts/w6b_ch4_update.py:43,55,61,92`. Replay 3 rename + 3 append cho đúng src-0596..0598. Override bằng snapshot, inventory chỉ khác hai field spreadsheet thêm sau đó. Tên lạ, PDF hỏng đúng tên và trang 1 sai chủ đề đều dừng trước khi ghi inventory/override. Nhưng chép đúng bytes 4.1 sang `Chương 4/extra/script_4.1.pdf` rồi chạy apply trên fixture đã migrate: **append src-0599 và thêm override OBSERVED**. So full relative path với danh sách đã duyệt cho cả rename lẫn append, và ràng buộc ID của ba rename. Ngoại lệ migration được người học phê duyệt vẫn đúng. [Bốn ca âm và replay](../../work/codex_review_r3/ch4.json)
- **G09 · Eval sai trả thành công. Một số tag vẫn đè báo cáo khác.** `scripts/v3_eval_course.py:52,77,83–87`. File `_r1` và base cùng tag `_pair` lưu riêng 3 và 24 dòng. File rỗng exit 1. Tuy nhiên, với một dòng direct bắt buộc src-9999, JSON ghi gate fail và CLI exit **0**, không hề dùng waiver KTCP. Test empty collision cũng cho `collision_rows_failed=1` dù contamination=0. Lỗi tên file tái hiện bằng base `--tag _r1_probe` rồi supplement `--suffix _r1 --tag _probe`: cùng tên, báo cáo 24 dòng thành 3. Truyền gate fail qua exit code với waiver tường minh ở caller. Dùng namespace output phân biệt loại bộ. [Gate thật ngoài waiver](../../work/codex_review_r3/unwaived.json) · [Va chạm tên](../../work/codex_review_r3/suffix.json)
- **G24 · Nhãn chứng cứ null bị công bố thành OBSERVED, qua cả eval external.** `scripts/v3_build_external.py:53–55`, `scripts/v3_eval_external.py:40–44`. Trên bản sao, chỉ thay `evidence_status` của Luật 106/2016 từ INFERRED thành YAML null, giữ nguyên nguồn chính thức. CLI không cờ exit 0, chunk thành OBSERVED. Eval external cũng exit 0, all_pass=true. Do validator kiểm sự hiện diện của key và nguồn, giá trị null lọt qua. Validate enum trước khi ghi và yêu cầu nhãn tương ứng với record. Không dùng OBSERVED làm mặc định cho record hỏng. [Đầu vào và hai kết quả CLI](../../work/codex_review_r3/null-status.json)

### MINOR

- **G12 · Dòng “Chương trình” và chương sai số vẫn được gán topic có chứng cứ.** `scripts/v3_extract_course.py:182–185`. Cho inventory chapter=4, chỉ thay dòng đầu của cùng file TXT. “Chương 4: Hệ thống chứng từ” ra topic 4 đúng. “Chương trình: Kế toán đại cương” và “Chương 7: Kiểm soát nội bộ” cũng ra topic 4 với rule page1_chapter_line. Snapshot có hai fallback thật là Chương 1 và Chương mở đầu. Kiểm heading theo cấu trúc thực, cho phép mở đầu, xác minh số chương với inventory khi có số. [Ba lượt CLI](../../work/codex_review_r3/heading-edges.json)
- **G13 · Manifest bỏ qua lỗi khi hai file đầu vào lệch nhau.** `work/w6b/make_manifests.py:3,12–15,20`. Tái hiện đúng fixture cũ: chỉ thêm src-0580 vào coverage.errors và giữ documents sạch. Generator exit 0, không warning, vẫn 25 PPTX và other_extract_errors=[]. Số PPTX nay đúng. Người đọc không thể biết coverage báo thêm một lỗi. Khi hai file cùng ghi lỗi PDF, output phân loại đúng. Đối chiếu tập ID lỗi đã chuẩn hóa từ hai nguồn trước khi xuất. [Chỉ sửa coverage](../../work/codex_review_r3/orphan-coverage.json) · [Sửa cả hai đầu vào](../../work/codex_review_r3/docgen.json)
- **G16 · Chứng cứ cho heading còn thiếu.** `scripts/v3_validate_concepts.py:58`, `curriculum/concepts/ke-toan-thue-1.yaml:441`. Chạy validator rồi đọc trang được trỏ cho “Tờ khai hải quan” hoặc “rút dự toán”. Token nằm trong nội dung nhưng oracle không kiểm dạng heading. Bốn bảng concept cùng SHA R1. Gắn nguồn heading/outline hoặc ghi đúng loại thuật ngữ.
- **G17 · Hai citation chung slug. Refresh spreadsheet cũng dựng lại external.** `research/citations.py:26`, `research/regulations/luat-thue-gtgt.yaml:1,9`, `scripts/v3_refresh.py:398–412`. Join tất cả 130 ref cho đúng một mismatch sau khi 13 record đã sửa. Ref không dấu ba chấm cần KTHCSN, YAML còn ghi Kiểm toán 1 của ref có dấu ba chấm. Refresh ghi lần lượt hai tập metadata vào cùng path, đánh dấu record_changes ngay ở lần đầu. Publish với affected=[] vẫn thay `external/idf.json` (JSON bằng nhau) và `external/meta.json` (khác build_date). Không chunk nào đổi. Chuẩn hóa/giải quyết va chạm trước khi ghi, giữ cả provenance và chỉ rebuild khi có thay đổi ròng. [13 record và hai khóa đụng nhau](../../work/codex_review_r3/citations.json) · [Đường dẫn thực đã publish](../../work/codex_review_r3/sheets.json)
- **G19 · Một văn bản sinh hai summary.** `research/regulations/thong-tu-80-2021.yaml:1`, `research/regulations/thong-tu-80-2021-tt-btc.yaml:1`. Hỏi “Thông tư 80/2021 còn hiệu lực không?” với scope external: câu trả lời có hai mục quan hệ thay thế cùng văn bản. Cần một danh tính văn bản với hai cách trích và provenance riêng.
- **G20 · Môn rỗng không kích hoạt NEW_COURSE.** `scripts/v3_refresh.py:52,67,169`. Tạo thư mục môn trống trong fixture, listing=[], không có NEW. Chốt trigger theo “file đầu tiên” trong hướng dẫn hoặc lưu danh sách thư mục nếu muốn phát hiện ngay.
- **G25 · Git giữ con trỏ latest, bỏ plan mà con trỏ trỏ tới.** `../.gitignore:13`, `work/refresh/latest.json:2`, `scripts/v3_refresh.py:524`. `git ls-files` thấy latest.json. Nó đã đổi sang plan `20261121_144128_996322/plan.json`, file này chưa track và `git check-ignore -v` khớp rule 13. Một checkout chỉ có nội dung dự kiến commit sẽ không có plan đích của lệnh apply mặc định. Thử apply mặc định trong deployment chỉ có latest, đã đổi tiền tố đường dẫn sang đúng deployment: exit 2, No such file or directory tại plan.json. Chạy plan ở máy nhận sẽ khôi phục được. [Log apply](../../work/codex_review_r3/ignored-plan-apply.log) Giữ con trỏ cùng vòng đời với plan cục bộ hoặc phát hành cặp có thể đọc được. [Kết quả check-ignore / ls-files](../../work/codex_review_r3/inputs.json)

### NIT

- **G21 · Khác ấn bản sách.** `work/he-thong-thong-tin-ke-toan-1/role_overrides_proposed.yaml:10`. Bìa src-0341 ghi 2013, src-0406 tr.1 dẫn 2016. Ghi riêng hai ấn bản. Role reference hợp lý.
- **G22 · Biên từ với dấu gạch dưới.** `retrieval/courses.py:77`, `V3_EXPANSION_PLAN.md:484`. Dò `_hcsn_` vẫn ra Tài chính HCSN. Quy ước regex trong đặc tả coi gạch dưới là ký tự từ. Thống nhất hợp đồng khi sửa router.
- **G23 · Gán chung lý do cho 11 INFERRED.** `reports/v3/W6B_FINAL.md:57`, `research/regulations/luat-21-2012-qh12.yaml:7,12,25`. Đọc hai URL official và khoản được dẫn. Bước suy luận ở đối chiếu ký hiệu QH12/QH13. Câu “đều dựa nguồn phụ” không khớp record này. Mô tả bất định theo mệnh đề.
- **G26 · Hồ sơ trạng thái hiện hành tự mâu thuẫn.** `reports/v3/W6B_FINAL.md:42,51,56`: mục 3b ghi lý do “chưa từng commit” như thể vẫn là văn bản hiện tại. Mục 3 đã đính chính. Mục 4 vẫn ghi 14 record thiếu môn và m4 chưa sửa, trong khi mục 3c và 3 xác nhận còn một slug và m4 đã duyệt. `README.md:44,111` cũng mô tả external vừa “Schema only” vừa enabled với 31 record. Đánh dấu rõ các mốc lịch sử và cập nhật phần giới hạn ở cuối. Đây là lỗi hồ sơ, không mở lại ba quyết định đã duyệt.

## 5. Phạm vi release và giới hạn bằng chứng

- Hai manifest sinh từ `work/w6b/make_manifests.py` bằng chính xác bytes của KTTC3 và KTHCSN. Tiêm thêm lỗi PDF src-0580 vào cả documents và coverage: vẫn 25 lỗi PPTX của KTTC3, có cảnh báo và entry PDF riêng trong other_extract_errors. Bốn manifest và metadata pack có mặt. Trạng thái 13 môn phù hợp registry. TCDN1 là catalog. [Đối chứng generator](../../work/codex_review_r3/docgen.json)
- Đã chạy git check-ignore --no-index cho 1220 đường dẫn nguồn học, code, data, eval, research, inventory, pack và hồ sơ phát hành được liệt kê trong harness, không đường nào khớp ignore. Cả sáu hướng dẫn đều ghi 13 môn. [Phạm vi rà Git](../../work/codex_review_r3/release-paths.json) Hai mẫu ignore cho reviewer và `w6b_s*` loại các mirror, harness và bằng chứng cục bộ. Chúng cũng loại bản nháp report-a.md mà W6B_FINAL nhắc tới. Báo cáo này ghi đủ kết quả quyết định để đọc độc lập sau push. Generator `work/w6b/make_manifests.py`, metadata TOC, manifest KTTC3, pack 17 và báo cáo R2 không bị ba rule che. Bốn plan cũ đã track không tự biến mất do .gitignore. File chưa track nhưng không bị ignore vẫn cần được đưa vào thay đổi phát hành. Review không stage file. Ngoại lệ có hậu quả vận hành là G25.
- Phép thử xác minh snapshot, hành vi CLI và một số lỗi có chủ đích tại bản sao. Chưa mô phỏng hai lượt publish cạnh tranh hoặc mất điện lúc ghi. Không chạy apply trên kho học thật. Nhánh CHANGED nhận diện bằng cùng đường dẫn. Đổi đuôi file tự nhiên là NEW+MISSING. Không xem fixture PDF hỏng là bằng chứng rằng điều kiện `unsupported && old_ext_ok` có thể tới được qua đổi đuôi.
- Đã kiểm tính nhất quán của nguồn, nhãn, URL lưu và câu trả lời pháp quy. Chưa tái thẩm định trực tuyến toàn bộ điều khoản, mọi ngày hiệu lực, hoặc mọi trang của 112 slide PPTX. Đánh giá heading/Owen dùng lại đối chiếu trực tiếp R1 ở phần dữ liệu không đổi. Không có công cụ Jev/TypeSafe MCP khả dụng. Mức độ và quyết định push là phán định của reviewer từ các đối chứng trên.

**Chưa push.** Đóng lỗ hổng tập baseline, ngăn nâng nhãn chứng cứ và buộc gate fail truyền ra CLI. Kiểm lại router Thuế và giới hạn đúng đường dẫn migration trước khi ký release. Giữ nguyên ba quyết định người học đã duyệt.

R2 BLOCKER=1 MAJOR=4 MINOR=7 NIT=4
