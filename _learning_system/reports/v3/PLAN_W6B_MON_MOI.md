# Kế hoạch W6b: nạp 4 môn mới (2026-11-21)

Hợp đồng gốc là `V3_EXPANSION_PLAN.md`: mục 2 (bất biến), mục 6 (playbook theo môn) và mục 7 (đặc tả).
File này chỉ bổ sung những điểm mà Wave 6 không có: **thêm môn mới**. Wave 6 chỉ hỗ trợ file mới trong môn đã có;
`v3_refresh.py` sẽ dừng với lỗi `Unknown course folder`.

## Môn mới

| course_id | Thư mục | Mã (OBSERVED từ tên file) | File |
|---|---|---|---|
| he-thong-thong-tin-ke-toan-1 | Hệ thống thông tin kế toán 1 | ACCO3315 | PDF/PPTX/XLS/XLSM, có bản tải trùng `script (n).pdf` |
| ke-toan-thue-1 | Kế toán thuế 1 | ACCO2311 | script PDF + slide PPTX theo chủ đề |
| ke-toan-tai-chinh-3 | Kế toán tài chính 3 | ACCO3310 | PDF + PPTX theo chủ đề, bài tập tự đánh giá |
| ke-toan-hanh-chinh-su-nghiep | Kế toán hành chính sự nghiệp | UNKNOWN | script PDF + slide PPTX, chương mở đầu đến chương 8 |

Tổng cộng: 122 pdf, 112 pptx, 18 xls, 1 xlsm, 3 docx.

## Những điểm cần quyết định trước (ghi vào báo cáo, không tự suy diễn)

1. **Cue bị đụng:** cue `hành chính sự nghiệp` và `hcsn` hiện thuộc TCHCSN, nên KTHCSN cần cue riêng (`kế toán hành chính sự nghiệp`, `kthcsn`).
   Theo luật longest-first, chuỗi "kế toán hành chính sự nghiệp" sẽ thắng. Cue trơn "hcsn" vẫn thuộc TCHCSN. Hai môn này phải có eval `collision`.
   `thuế` không được dùng làm cue trần, vì KTTC3 chương 4 (thuế TNDN hoãn lại) cũng dùng từ này.
2. **Định dạng chưa hỗ trợ:** `.xls` và `.xlsm` (bài tập Excel của HTTTKT1) không thuộc danh sách extension. Ghi vào inventory với `index_include: false` và lý do `unsupported_extension`. Không chuyển đổi file gốc.
3. **PPTX:** extractor ghi `pptx extractor not wired (non-learner pptx)`. Môn nào đã có script PDF cho cùng chủ đề thì dùng PDF làm nguồn index.
   Slide PPTX không có PDF tương ứng thì ghi `THIN`/`not_extracted` trong báo cáo. Bật extractor PPTX là thay đổi engine nên phải escalate.
4. **Bản trùng** (`script (1).pdf`…): giao cho dedupe (spec 7.3) quyết định. Không xóa file nào trên D:.
5. **Tiên quyết:** chỉ ghi khi có câu trích dẫn chứng (ví dụ KTTC3 → KTTC2, KTHCSN → TCHCSN, HTTTKT1 → NLKT). Không có trích dẫn thì không ghi.

## Pha A — nền chung (làm tuần tự, 1 phiên, đụng file dùng chung)

A1. Backup mọi file sắp sửa vào `backups/w6b_20261121/`.
A2. `scripts/build_inventory.py::COURSE_IDS` thêm 4 thư mục. `curriculum/course_registry.yaml` thêm 4 môn, ở tier `catalog`, kèm codes và cues (mục 1 ở trên).
A3. Append inventory: thêm các dòng NEW với `src-` tiếp nối, không đánh số lại. Phân loại theo luật learner/tmp của bước 0.6.
A4. Kiểm tra `v3_regression.py` IDENTICAL, `retrieve(... --course <môn mới>)` trả về `course_not_indexed`. Commit nội bộ, chưa push.

## Pha B — mỗi môn một phiên (chạy song song sau A)

Mỗi phiên chỉ ghi file của **môn mình**:
`data/normalized/<C>.*`, `data/chunks/<C>.*`, `data/indexes/3.0.0/<C>/`, `curriculum/concepts/<C>.yaml`,
`evals/v3/<C>_retrieval.jsonl`, `work/<C>/`, `reports/v3/<C>_*`, `reports/v3/G-<C>.md`, `curriculum/course_manifests/<C>.yaml`, `course_scans/<C>.yaml`.

Các bước theo playbook 6.2 → 6.9: extract, dedupe, concept candidates, **concept table** (bước cần phán đoán), partition, eval (≥20 dòng, viết trước khi tinh chỉnh), tối đa 2 vòng tinh chỉnh, chấm gate.

**Không** sửa: registry, inventory, `evals/v3/FROZEN.json`, core, file của môn khác.
Sha256 của eval và điểm lần chạy đầu ghi vào `reports/v3/<C>_frozen_entry.json`, Pha C sẽ gộp vào `FROZEN.json`.
Không commit, không push. Kết thúc phiên bằng báo cáo gate (đạt hay trượt) và danh sách file đã ghi.

## Pha C — gộp, kiểm tra, công bố (tuần tự, phiên chính)

C1. Gộp `*_frozen_entry.json` vào `FROZEN.json`. Môn đạt gate thì đổi tier sang `retrieval` trong registry; môn trượt giữ `catalog`.
C2. Chạy eval của mọi môn retrieval cũ: kết quả không được đổi. Regression core phải IDENTICAL. Chạy `freeze_core.py`.
C3. Harvest trích dẫn văn bản (5.1). Văn bản mới phải có record `research/regulations/` (official hoặc `unknown` kèm lý do).
C4. `_grok_pack`: xuất `18_…`–`21_…md` từ `data/normalized/<C>.pages.jsonl` theo đúng nhãn `[môn | ch.N | file | tr.a-b | loại]`. Cập nhật `00_MUC_LUC.md`, bảng môn trong `00_HUONG_DAN_GROK.md`, `README.md` gốc.
C5. Báo cáo `reports/v3/W6B_FINAL.md`, rồi **PAUSE**: báo Tuệ, chờ "tiếp" rồi mới commit và push.
