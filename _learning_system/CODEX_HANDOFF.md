# CODEX HANDOFF — V3 build, tiếp từ sau Wave 2

Bạn (Codex) là **executor** tiếp quản build V3 của hệ thống học kế toán ở `D:\Hoc\_learning_system`.
Hợp đồng duy nhất: `V3_EXPANSION_PLAN.md` (cùng thư mục, gồm Amendment A1 ở cuối). File này chỉ là bản đồ trạng thái và cách làm; nếu file này mâu thuẫn với plan thì **plan thắng**.

Bạn không phải tutor, không phải Grok bot. Không thiết kế lại. Không bỏ cổng kiểm tra.

---

## 0. Đọc trước khi làm gì

1. `V3_EXPANSION_PLAN.md` — toàn bộ, nhất là §2 (invariants), §5 Wave 3–6, §6 playbook, §7 specs, §8 runtime contract text, §9 stop conditions, Amendment A1.
2. `autopilot/v3_progress.yaml` — trạng thái chuẩn. `current_step` hiện là `PAUSE after G2c`.
3. `reports/v3/G-*.md` — 4 báo cáo cổng đã có (mẫu để viết báo cáo mới).
4. `work/kiem-toan-1/build_concepts.py` — mẫu script dựng bảng khái niệm (đã pass validator).
5. `evals/v3/kiem-toan-1_retrieval.jsonl` — mẫu file eval 20 dòng đúng schema.

---

## 1. Trạng thái hiện tại (2026-10-11)

| Wave | Môn | Cổng | Tier | Ghi chú |
|---|---|---|---|---|
| 0 | — | G0 PASS | — | baseline core đã chụp (`reports/v3/baseline`) |
| 1 | ke-toan-tai-chinh-2 | G1 provisional pass | retrieval | `insufficient` hoãn sang G3x |
| 2a | ke-toan-chi-phi | G2a **FAIL** | catalog | chapter@1 0.70 < 0.80; 3 dòng topic_owner viết sai kỳ vọng (file đã frozen, KHÔNG sửa) |
| 2b | kiem-toan-1 | G2b provisional pass | retrieval | insufficient 2/3 (kt-i03 ra `partial`) → G3x |
| 2c | ke-toan-ngan-hang | G2c **FAIL** | catalog | chapter@1 0.75 < 0.80 |

Core regression: IDENTICAL sau mọi bước.

**Nguyên nhân gốc của 2 FAIL** (đã ghi escalation): token tên môn trong câu hỏi ("kế toán chi phí", "kế toán ngân hàng") khớp lexical với chunk giới thiệu chung đầu chương, kéo sai chương lên top-1. Không knob nào trong §6.8 sửa được.
**Đề xuất đang chờ người dùng/Opus quyết** (KHÔNG tự làm): trong `retrieve_partition`, bỏ token cue tên môn khỏi query lexical (hàm `_strip_course_cues` đã có sẵn trong code routing). Xem §5 bên dưới.

---

## 2. Môi trường trên máy người dùng

Phiên trước chạy ở cloud mirror; bạn chạy trực tiếp trên PC nên đơn giản hơn:

```powershell
cd D:\Hoc\_learning_system
$env:HOC_ROOT = "D:\Hoc"
$env:PYTHONIOENCODING = "utf-8"
python -m pip install pypdf python-docx python-pptx numpy pyyaml   # nếu thiếu
```

- Tất cả lệnh chạy từ `D:\Hoc\_learning_system` (package `retrieval` import tương đối từ đây).
- Bỏ qua bước "stage/commit" của plan §3 — bạn ghi trực tiếp. Nhưng thay cho `expectedMtimeMs`: **trước khi ghi đè một file đã tồn tại, kiểm tra nó đúng là file bạn định sửa** (không ghi đè file người dùng vừa sửa).
- Nếu `D:\Hoc\_learning_system` là git repo thì commit sau mỗi nhóm step. Nếu không, tạo `git init` là KHÔNG được — chỉ cập nhật progress file là đủ.

---

## 3. Luật cứng (nhắc lại từ plan §2 — vi phạm = DỪNG)

- **Không bao giờ** ghi / di chuyển / đổi tên / xóa bất cứ thứ gì trong `D:\Hoc\<thư mục môn>\**`. Chỉ đọc.
- Chỉ ghi bên trong `D:\Hoc\_learning_system`. Không xóa file nào trên D:.
- File đóng băng (không đụng):
  - `data/normalized/nlkt_kttc1.*`, `data/chunks/nlkt_kttc1.*`, `data/indexes/2.0.0/*`
  - mọi file có sẵn trong `evals/` (kể cả `evals/v3/*` đã ghi trong `evals/v3/FROZEN.json`)
  - entry cũ trong `curriculum/concept_registry.yaml`, `curriculum/concept_graph.yaml`
  - logic engine trong `diagnostic/ decision/ adaptive/ admission/ mastery/ learning_policy/`
  - `learner/**`, `pilot/events|sessions|corrections|feedback/**`
- Không bịa traffic/evidence của người học. Mọi fact curriculum mới phải có provenance (source_id + page) và nhãn evidence.
- Không bao giờ sửa file eval để test pass. File eval mới đóng băng ngay sau lần chạy đầu (ghi sha256 + điểm vào `FROZEN.json`).
- Trọng số hybrid (bm25 .42 / tfidf .22 / concept .18 / metadata .12 / authority .06) không được chỉnh.
- **Không làm Wave 7** (OPUS_ONLY).

---

## 4. Việc cần làm, đúng thứ tự

### Bước 0 — Chờ lệnh
Người dùng phải nói **"tiếp"** cho PAUSE sau G2c trước khi bạn bắt đầu Wave 3. Nếu họ đã nói "tiếp" khi giao file này cho bạn thì coi như đã có. Đồng thời hỏi/ghi nhận quyết định về đề xuất §5 (mặc định: KHÔNG áp dụng).

### Wave 3 — 6 môn (playbook §6, mỗi môn một cổng)

Thứ tự: `kinh-doanh-va-nghiep-vu` (G3a) → `luat-kinh-doanh` (G3b) → `tai-chinh-doanh-nghiep-1` (G3c) → `ngan-hang-thuong-mai` (G3d) → `thi-truong-tai-chinh` (G3e) → `tai-chinh-hanh-chinh-su-nghiep` (G3f) → learner-notes (G3g).

Với mỗi môn `C`:

```powershell
# 6.1 hash-check: so sha256 từng file của C với data/inventory (script extract tự làm; mismatch -> STOP)
python scripts/v3_extract_course.py --course C          # 6.2  -> errors phải == []
python scripts/v3_dedupe.py --course C                  # 6.3  -> có REVIEW nào -> STOP
python scripts/v3_concept_candidates.py --course C      # 6.4  -> work/C/concept_candidates.json
# 6.5 viết work/C/build_concepts.py theo mẫu kiem-toan-1, chạy nó -> curriculum/concepts/C.yaml
python work/C/build_concepts.py
python scripts/v3_validate_concepts.py --course C       # phải PASS
python scripts/v3_build_partition.py --course C         # 6.6
# 6.7 viết evals/v3/C_retrieval.jsonl (>=20 dòng) TRƯỚC mọi tuning
python scripts/v3_eval_course.py --course C             # chạy lần 1 -> ghi FROZEN.json
# 6.8 tối đa 2 vòng tuning (chỉ cue registry / alias / account_map / dup_group)
python scripts/v3_regression.py                         # core phải IDENTICAL
```

**Mẹo bảng khái niệm (6.5) — những lỗi đã gặp:**
- `canonical_name` phải là chữ xuất hiện nguyên văn trong text của môn (validator dò). Lấy từ dòng "Chủ đề x.y: …" hoặc "Chương n: …" trong `concept_candidates.json`.
- Alias không được trùng giữa hai concept.
- Số concept 15–40. Quá 40 thì gộp/bỏ term phụ.
- Cấu trúc trong `build_concepts.py`: list `S` gồm tuple `(canonical, aliases, chapter, topic, same_as_core_id_or_None, extra_chapters)`; script tự lọc alias không có trong text và sinh `account_map` từ tài khoản có count ≥ 2.
- Nếu validator đòi alias mà text không có → đó là điều kiện DỪNG (§9), không bịa alias.

**Mẹo viết eval (6.7) — những lỗi đã gặp:**
- Schema mỗi dòng: `id, course, category, question, expected_course, expected_chapter, expected_concepts, expected_source_types, must_include_source_ids, must_not_include_courses, expected_coverage, mode`.
- `direct`: câu hỏi kiểu sinh viên, có tên môn; `must_include_source_ids` = unit script hoặc PDF chương.
- `insufficient` (3 dòng): theo Amendment A1, chỉ ra `insufficient` khi (a) term không có trong corpus của C, hoặc (b) có môn khác rõ ràng tốt hơn (`topic_in_other_course`). Chọn câu hỏi thỏa đúng 1 trong 2, ví dụ hỏi WACC trong Luật kinh doanh.
- `collision`: tránh câu hỏi chứa cue của **hai** môn (ví dụ "ngân hàng" vừa là cue KTNH vừa NHTM) — `resolve_extended_scope` coi là mơ hồ và rơi về đường legacy.
- `topic_owner`: chỉ bắt buộc ở Wave 1. Nếu viết, nhớ spec 4.3: gợi ý **chỉ phát** khi coverage core != sufficient HOẶC câu hỏi không có cue core. Câu nào core (NLKT/KTTC1) trả lời đủ thì sẽ KHÔNG có gợi ý.
- Môn không có tài khoản (Luật, TTTC…) thì không viết dòng `account`; runner coi gate đó là n/a.

**Ghi chú riêng Wave 3 (plan §5):**
- Không có thư mục `_nguon`. PDF gộp đã có override: src-0130 (NHTM), src-0178 (TCDN1), src-0186 (TCHCSN) → `combined_duplicate: true`, extract để đo coverage, loại khỏi index.
- Dedupe thêm `Slide <môn>.pdf` / `Slide.pdf` / `SlideHành chính và sự nghiệp.pdf` / `Slide Ngân hàng Thương Mại.pdf` so với slide từng chương; ≥ 0.85 → combined.
- `Corporate_Finance_Blueprint.pptx` là learner_material → vào learner-notes (3g), KHÔNG vào TCDN1.
- NHTM: xung đột Luật TCTD 2010 vs 32/2024/QH15 → ghi vào `conflicts` của bảng khái niệm, không gộp.
- TCDN1: xung đột thời lượng thi 75 vs 90 phút → ghi, không giải quyết.
- `TCDN1-Tailieuhuongdanntap.docx` → đưa vào.

**Sau mỗi môn:** cập nhật `autopilot/v3_progress.yaml` (step, gate status, report path, tier), cập nhật `curriculum/course_registry.yaml` (tier `retrieval` nếu pass, giữ `catalog` nếu fail), viết `reports/v3/G-C.md` theo mẫu, commit.
**Fail sau 2 vòng tuning:** tier `catalog`, báo cáo fail, thêm escalation vào progress, đi tiếp môn sau (nếu lỗi chỉ cục bộ môn đó).

**3g learner-notes:** làm đúng plan §5 Wave 3g (index `data/indexes/3.0.0/learner-notes/`, coverage luôn `learner_material`, `unknowns: ["not_curriculum_source"]`, 5 dòng eval top-3, assert không partition môn nào chứa chunk learner_material).

`PAUSE` sau G3g → báo người dùng bằng tiếng Việt ngắn gọn, chờ "tiếp".

### Checkpoint G3x (Amendment A1) — trước Wave 4
- Chạy lại `v3_eval_course.py` cho **mọi** môn tier `retrieval` (KTTC2, KT1 và các môn Wave 3 đã pass).
- Gate `insufficient` phải 100% ở từng môn. Môn nào trượt → trả về `catalog` + escalation.
- `v3_regression.py` IDENTICAL.
- Ghi `reports/v3/G3x.md`.

### Wave 4, 5, 6
Theo plan §5, đúng từng step.
- 4.7: chèn **nguyên văn** text §8 (runtime contract, "3A. COURSE TIERS") vào chỗ plan chỉ định. Không diễn giải lại.
- Wave 5: được web search; chỉ ghi vào `research/` và partition `external`. Các lead phải xác minh trạng thái hiệu lực: QĐ 479/2004 (hệ thống TK ngân hàng), TT 200/2014 → TT 99/2025, Luật TCTD 32/2024/QH15. Văn bản không xác minh được trạng thái → đánh dấu `status: unverified`, **không phải** điều kiện dừng.
- Wave 6: refresh tăng dần cho file mới trong `D:\Hoc`.

Mỗi chỗ `PAUSE` trong plan: báo kết quả cổng tiếng Việt ngắn, chờ "tiếp".

---

## 5. Quyết định đang treo (KHÔNG tự làm nếu người dùng chưa duyệt)

**D1 — Strip cue tên môn khỏi query lexical trong partition.**
- Sửa ở `retrieval/` (hàm `retrieve_partition`): trước khi tính BM25/TF-IDF, loại các token thuộc cue của chính môn đang truy vấn (dùng `_strip_course_cues`). Giữ nguyên query gốc cho bước routing/concept.
- Nếu người dùng nói "duyệt D1":
  1. Áp dụng sửa đổi.
  2. Chạy `v3_regression.py` → core phải IDENTICAL (sửa này chỉ chạm nhánh partition).
  3. Chạy lại eval của **tất cả** môn retrieval + KTCP + KTNH, ghi kết quả vào `reports/v3/D1_rerun.md`. Không sửa file eval nào.
  4. KTCP / KTNH nếu đạt §6.9 (trừ dòng topic_owner viết sai của KTCP — ghi rõ là lỗi spec của executor, xin người dùng chấp nhận miễn) → nâng tier `retrieval`.
  5. Môn đang `retrieval` nếu tụt dưới gate → báo ngay, không tự hạ/nâng.
- Nếu không duyệt: KTCP, KTNH ở lại `catalog`, giữ escalation.

**D2 — Dòng topic_owner KTCP (3 dòng).** File frozen, không sửa. Chỉ có thể: người dùng chấp nhận miễn, hoặc Opus viết file eval bổ sung mới (`evals/v3/ke-toan-chi-phi_topic_owner_v2.jsonl`) với câu hỏi không có cue core.

---

## 6. Điều kiện DỪNG (plan §9)

Baseline lệch · core regression khác baseline · hash file nguồn lệch inventory · lỗi extraction · dedupe có `REVIEW` · validator cần alias bịa · gate trượt sau 2 vòng tuning (cục bộ thì ghi escalation rồi đi tiếp; toàn hệ thì dừng) · cần sửa file đóng băng · ghi thất bại · cần ghi ra ngoài `D:\Hoc\_learning_system`.

Khi dừng: thêm entry vào `escalations:` trong progress file (step, reason, at, resolution: null), rồi gửi người dùng **một** tin nhắn ngắn tiếng Việt.

---

## 7. Cách báo cáo cho người dùng

- Tiếng Việt, xưng "tao/mày" thoải mái được, ngắn.
- Mỗi PAUSE: môn nào pass/fail, số liệu gate trượt (giá trị vs ngưỡng), core regression, việc tiếp theo.
- Không dán log dài. Chi tiết để trong `reports/v3/`.
