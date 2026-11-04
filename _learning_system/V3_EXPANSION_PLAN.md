# V3 EXPANSION PLAN — Build contract for the executor model

Project root: `D:\Hoc\_learning_system` · Curriculum root: `D:\Hoc`
Plan version: 1.0 · Authored: 2026-10-11 (design model) · Executor: Claude Sonnet (Cowork)
Status file: `autopilot/v3_progress.yaml` (create in step 0.1, update after every step)

---

## TÓM TẮT (cho người học)

Hệ thống hiện tại (core v8) chỉ chạy được trên NLKT + KTTC1. 10 môn còn lại mới có danh mục và extract bị cắt (≤12 trang/chương). Bản kế hoạch này mở rộng phần **truy xuất giáo trình** sang cả 10 môn mà **không đụng vào lõi** đã test (index 2.0.0, các engine chẩn đoán/quyết định/ghi nhận/state).

Cách làm: mỗi môn mới có **index riêng (partition)**. Câu hỏi thuộc NLKT/KTTC1 hoặc không rõ môn vẫn đi đúng đường cũ → kết quả cũ không thể đổi. Câu hỏi có nhắc tên môn mới (hoặc truyền `--course`) đi sang partition của môn đó. Môn mới ở tầng **RETRIEVAL**: tutor trả lời và đối chiếu giáo trình được, nhưng chưa chẩn đoán / chưa ghi bằng chứng dài hạn.

Thứ tự: Wave 0 chuẩn bị + refactor đường dẫn → Wave 1 KTTC2 → Wave 2 KTCP, Kiểm toán 1, KTNH → Wave 3 6 môn còn lại + kho tài liệu cá nhân → Wave 4 dọn tài liệu + cập nhật Grok bot → Wave 5 lớp quy định hiện hành (nguồn chính thức mới nhất, tách riêng khỏi giáo trình) → Wave 6 cơ chế tự nạp file mới. Mỗi wave có cổng kiểm tra; trượt cổng là dừng và báo.

Người học đã duyệt (2026-10-11): **nạp hết** mọi file trong `D:\Hoc` (kể cả bài làm / sổ tay cá nhân, nhưng để ở kho riêng `learner_notes`, không bao giờ coi là giáo trình) và **bật lớp cập nhật mới nhất** (văn bản pháp quy / chuẩn mực hiện hành, lưu riêng, luôn ghi rõ "theo giáo trình" vs "theo quy định hiện hành").

Không cần Grok bot cho khâu nào trong build. Grok bot chỉ dùng ở cuối để test thật.

---

## 1. ROLES AND AUTHORITY

| Actor | Role |
|---|---|
| Learner (Tuệ) | Owner. Approves waves, resolves escalations. Authorized on 2026-10-11: (a) lift the expansion lock for ingestion of **all** files in `D:\Hoc`, learner material included as a separate non-curriculum partition; (b) enable the external research plane for the most recent official regulations/standards (Wave 5); (c) incremental refresh of new files (Wave 6). Core diagnosis logic remains locked. |
| Design model (Opus) | Wrote this plan. Handles escalations and anything marked `OPUS_ONLY`. |
| Executor (Sonnet) | Executes steps exactly as written. Does not redesign. Does not skip gates. |
| Grok bot | Runtime tutor only. Not used for any build step. Used after Wave 4 for acceptance testing by the learner. |

Executor rule: when this plan and your own judgment disagree, follow the plan or stop and escalate. Never "improve" architecture.

---

## 2. HARD INVARIANTS (violating any = stop immediately)

1. Files under `D:\Hoc\<course folder>\**` are read-only. Never write, rename, move, or delete them.
2. Frozen core artifacts — never modify:
   - `data/normalized/nlkt_kttc1.*`, `data/chunks/nlkt_kttc1.*`, `data/indexes/2.0.0/*`
   - every existing file in `evals/` (all `*.jsonl`, `*rubric.yaml`)
   - existing entries in `curriculum/concept_registry.yaml` and `curriculum/concept_graph.yaml` (do not edit, do not add aliases to them)
   - engine logic in `diagnostic/`, `decision/`, `adaptive/`, `admission/`, `mastery/`, `learning_policy/` (Wave 0 path refactor is the only permitted edit there)
   - `learner/**`, `pilot/events|sessions|corrections|feedback/**`
3. No fabricated learner traffic, sessions, or evidence.
4. Every new curriculum fact carries provenance (source_id + page) and an evidence label (OBSERVED / INFERRED / UNKNOWN).
5. Never edit an eval file to make a test pass. New eval files are frozen once their first run is recorded.
6. Every commit back to `D:\` overwriting an existing file must pass `expectedMtimeMs` from staging. If a commit is rejected for mtime drift, stop and report.
7. Do not delete anything on `D:\`. Superseded files are left in place or listed for the learner.

---

## 3. EXECUTION ENVIRONMENT (cloud mirror)

The executor runs in the Cowork cloud container. The learner's PC is reachable only through stage/commit file tools (no remote shell). Work on a mirror and commit results back.

### 3.1 Mirror layout

- Staged files land in `/mnt/user-data/uploads/Hoc/<relative path>` (mirrors `D:\Hoc`).
- Working copy: `cp -a /mnt/user-data/uploads/Hoc /home/claude/Hoc` after staging. All work happens in `/home/claude/Hoc`.
- Export for commit: copy changed/new files into `/mnt/user-data/outputs/commit/<relative path under D:\Hoc>` then `device_commit_files` with `stagedPath` = that file and `devicePath` = `D:\Hoc\<same relative path>`. Max 50 files per call, 30 MB per file.
- Record every staged file's `mtimeMs` in `/home/claude/stage_log.jsonl` (`{"path":..., "mtimeMs":...}`), so overwrites can pass `expectedMtimeMs`.

### 3.2 What to stage

- Wave 0: everything under `_learning_system` except `__pycache__`, `extracts/`, `data/normalized/*.pages.jsonl` is optional (stage it; it is needed for regression). Plus the 40 core source PDFs (only for integrity check; paths from `inventory/files.json` where `course_id` in core).
- Each course wave: every inventory row of that course (`relative_path`), excluding `/tmp/` paths.
- Stage at most 50 paths per call. Build path lists from `inventory/files.json` with a script, then pass them literally.

### 3.3 Python environment

```
pip install --break-system-packages pdfplumber pypdf python-docx python-pptx pyyaml numpy
export HOC_ROOT=/home/claude/Hoc
cd /home/claude/Hoc/_learning_system
```
Record library versions into `reports/v3/env.json`.

### 3.4 Progress file

`autopilot/v3_progress.yaml`:
```yaml
plan_version: "1.0"
current_wave: 0
current_step: "0.1"
steps: {}        # step_id: {status: done|failed|blocked, at: ISO, note: "..."}
gates: {}        # gate_id: {status: pass|fail, report: path}
escalations: []  # {step, reason, at}
```
Update after every step and commit it at the end of every step group.

---

## 4. TARGET ARCHITECTURE (v3)

### 4.1 Course tiers

| Tier | Courses | Behavior |
|---|---|---|
| `core` | nguyen-ly-ke-toan, ke-toan-tai-chinh-1 | Unchanged v8 loop: retrieve → diagnose → decide → adapt → admit → state → policy. Index 2.0.0. |
| `retrieval` | each course that passed its gate | Teach / source lookup / attempt-checking against evidence. No diagnosis, no admission, no state. Own partition index 3.0.0. |
| `catalog` | not yet ingested | Retrieval returns `insufficient` + `course_not_indexed`. |

### 4.2 New files

```
curriculum/course_registry.yaml          # single source of truth for courses (spec 7.1)
curriculum/concepts/<course_id>.yaml     # per-course concept table + account map (spec 7.4)
retrieval/courses.py                     # registry loader, cue detection, partition paths
retrieval/partition.py                   # retrieve_partition(), topic_owner_suggestions()
scripts/v3_extract_course.py             # full extract for one course (no page cap)
scripts/v3_dedupe.py                     # chapter-vs-unit duplication analysis
scripts/v3_build_partition.py            # chunk + index for one course
scripts/v3_concept_candidates.py         # mechanical candidate harvest
scripts/v3_validate_concepts.py          # concept table validator
scripts/v3_eval_course.py                # course eval runner
scripts/v3_regression.py                 # core regression comparator
data/normalized/<course_id>.documents.jsonl | .pages.jsonl | .coverage.json
data/chunks/<course_id>.chunks.jsonl | .chunks.meta.json
data/indexes/3.0.0/<course_id>/meta.json | idf.json | vectors.jsonl | chunk_ids.json
evals/v3/<course_id>_retrieval.jsonl
evals/v3/FROZEN.json
reports/v3/*.md|json
```

### 4.3 Routing rule (the core of the design)

In `retrieval/retrieve.py::retrieve()`, before any legacy logic:

```
ext = resolve_extended_scope(question, filters)
if ext is not None:
    return retrieve_partition(question, ext, filters, top_k, system)
pkg = <legacy code, byte-for-byte unchanged>
pkg["other_course_suggestions"] = topic_owner_suggestions(question, pkg)   # additive key only
return pkg
```

`resolve_extended_scope`:
1. If `filters.course_id` normalizes to a non-core course → return it (tier `retrieval` or `catalog`).
2. Else run legacy core cue check (`NLKT_CUES`, `KTTC1_CUES` from analyze.py). If any core cue hits → return None (legacy path).
3. Else run `courses.detect_courses(question)` (non-core cues, longest match first). Exactly one hit → return it. Zero or several → return None (legacy path; several = add `ambiguous_courses` to suggestions).

Consequence: every question the core suite contains still runs the legacy path. Core results cannot change except for the additive `other_course_suggestions` key.

`retrieve_partition` (in `retrieval/partition.py`):
- Tier `catalog` → package with `items: []`, `coverage: "insufficient"`, `unknowns: ["course_not_indexed"]`.
- Load `Index(chunks_path, index_dir)` for that course (cache per course).
- Scoring: identical hybrid formula and `HYBRID_WEIGHTS`; concept score uses the course concept table; authority score identical to legacy.
- Mask: `source_bound` cues (reuse `SOURCE_BOUND_CUES`) → filter chapter / source_type like legacy `source_bound`.
- Result de-dup: skip a chunk if its `dup_group` (spec 7.3) is already in the picked list.
- Prerequisite evidence: only if the question hits `PREREQ_CUES` and the registry lists an explicit prerequisite course. Fetch up to `PREREQ_TOP_K` chunks from that course's index (core index for KTTC1) with BM25 only. Label `prerequisite_evidence`. Never used for diagnosis.
- Coverage: same thresholds as legacy (`sufficient` if ≥1 item and top score ≥ 0.15; `insufficient` if top < 0.08; else `partial`). Additionally, if the question's detected concepts all belong to other courses' tables and none to this course → `insufficient` + `unknowns: ["topic_in_other_course:<id>"]`.
- Package: same keys as legacy plus `"partition": course_id, "tier": "retrieval", "index_version": "3.0.0"`.

`topic_owner_suggestions(question, pkg)` (legacy path only, additive):
- Run every `retrieval`-tier concept table over the question. For each course with ≥1 concept hit, emit `{course_id, concept_ids, chapters}`.
- Emit only when `pkg.coverage != "sufficient"` OR the question carries no core cue. Never alters `items`, `coverage`, or `unknowns`.

`retrieval/director.py`:
- `answer()`: legacy wording unchanged on the legacy path. On the partition path use: `"Không đủ bằng chứng trong corpus đã index của {course_name} để trả lời như một curriculum fact."` and append suggestions when present.
- `handle()`: if `course_id` normalizes to a non-core course → do not call diagnose/decide; return `answer(...)` with `director_mode: "teach"` and `note: "diagnosis_not_available_for_course_tier"`. If this guard changes any frozen suite result (gate G0b/G1), revert the guard and escalate.

### 4.4 Index class change

`retrieval/index.py`: `Index(chunks_path=None, index_dir=None)` and `build_index(chunks_path=None, index_dir=None, meta_extra=None)`. Defaults = legacy paths, so legacy callers are unaffected. `_load_chunks(path=None)` likewise.

### 4.5 Concept mapping change

`retrieval/concepts.py`: keep `map_text(text)` and `detect_query_concepts(question)` exactly as is (core). Add `map_text_course(text, course_id)` and `detect_course_concepts(question, course_id)` that use only `curriculum/concepts/<course_id>.yaml` (phrases + course account map). Core functions must not read the new files.

---

## 5. WAVES AND STEPS

Each step: do it, verify its check, update progress file. Each gate: write the report, commit, stop for the learner only where marked `PAUSE`.

### WAVE 0 — Preparation (no data change)

**0.1 Progress file + backup**
- Create `autopilot/v3_progress.yaml` (section 3.4).
- Copy every file you will modify in Wave 0 (list in 0.3) into `backups/pre_v3/<same relative path>` and commit those copies first.
- Check: backup commit succeeded.

**0.2 Environment + baseline (before any code change)**
- Stage per 3.2, build mirror, install env (3.3).
- Run core integrity: `python -c "from study.integrity import verify_sources; import json; print(json.dumps(verify_sources(), ensure_ascii=False))"`. Must be `OK`, checked = 40. (Needs HOC_ROOT support → if this fails only because of the hardcoded path, do 0.3 first, then return here; baseline must still precede any non-path change.)
- Run frozen suites `scripts/phase2_eval.py` … `scripts/phase8_eval.py` and `scripts/pilot_instrumentation_eval.py`. Save stdout and each raw JSON they produce into `reports/v3/baseline/`. Do not commit the overwritten historical `reports/*.md`; restore them from staging after the run.
- Compare baseline headline metrics with the historical reports (`reports/retrieval_benchmark.md`, `phase3_summary.md` … `phase8_summary.md`). Retrieval must show the same 2 failing tests (`kttc1-08`, `pre-07`).
- Check: metrics match history. If they differ (library drift in the cloud), STOP and escalate — the cloud environment is not a valid judge.

**0.3 Path refactor (behavior-neutral)**
- `retrieval/config.py`:
  ```python
  import os
  ROOT = Path(os.environ.get("HOC_ROOT", r"D:\Hoc"))
  SYSTEM = ROOT / "_learning_system"
  ```
- Every `sys.path.insert(0, str(Path(r"D:\Hoc\_learning_system")))` → `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))`.
- Every other `Path(r"D:\Hoc\_learning_system...")` (study/log.py, study/freeze.py, mastery/store.py, admission/store.py, scripts/phase*_eval.py, scripts/freeze_core.py, …) → derive from `retrieval.config.SYSTEM`. Find them with `grep -rn 'D:\\\\Hoc' --include=*.py`.
- No other edits.
- Check: rerun all frozen suites → output identical to 0.2 baseline (`scripts/v3_regression.py` diff, spec 7.7).

**0.4 Course registry + loader**
- Write `curriculum/course_registry.yaml` with all 12 courses (data in spec 7.1). All non-core courses start at tier `catalog`.
- Write `retrieval/courses.py`: `load_registry()`, `normalize_course(id_or_alias)`, `tier(course_id)`, `detect_courses(question)` (non-core cues only, folded, longest-first), `partition_paths(course_id)`.
- Check: unit smoke — `detect_courses("Kế toán tài chính 2 chương 4")` → `["ke-toan-tai-chinh-2"]`; `detect_courses("KTTC1 FIFO")` → `[]`; `detect_courses("kế toán ngân hàng và ngân hàng thương mại")` → both.

**0.5 Partition plumbing**
- Implement 4.3 and 4.4 and 4.5 with all non-core courses at tier `catalog` (no partitions yet).
- Check: frozen suites identical to baseline except the additive key `other_course_suggestions` (allowed). `retrieve("Doanh thu KTTC2", {})` → `course_not_indexed`.

**0.6 Inventory delta + learner-material classification**
- Hash every staged course file; compare with `inventory/files.json` (relative_path + size + sha256). Append NEW files as `src-0334…` with `notes: ["added_in_v3"]`; never renumber. Expected NEW: the 6 files under `Kế toán chi phí/` (Claude outputs, NguyenDucTue_*). Supported new extensions: `.pdf .docx .pptx .txt .md .xlsx`.
- Add `curriculum/source_registry_overrides.yaml` entries with `content_role: learner_material`, `partition: learner_notes` for: src-0040, src-0041, src-0046, src-0139, src-0140, src-0165, src-0173, src-0174, and every NEW learner file from this step. Rule for any other candidate: page 1 contains `Nguyễn Đức Tuệ` or `Họ tên sinh viên`, or path contains `Claude outputs` → learner_material.
- Learner material is **not** indexed in its course partition. It goes into the separate `learner_notes` partition (Wave 3, step 3g).
- `tmp_artifacts_not_curriculum` (render previews) stays excluded everywhere — they are rendering by-products, duplicates of learner files.
- Add tier `learner_notes` to the registry (spec 7.1): `{id: learner-notes, name: Tài liệu cá nhân, tier: catalog, cues: ["bài làm của tao", "bài thảo luận của tao", "sổ tay", "ghi chú của tao", "bài của tao"]}`.
- Check: inventory count = 333 + NEW; overrides parse.

**GATE G0** — `reports/v3/G0.md`: integrity OK, frozen suites identical (diff attached), registry loads, catalog routing works. Commit Wave 0. `PAUSE` — report to learner, wait for "tiếp".

### WAVE 1 — KTTC2 (ke-toan-tai-chinh-2)

Run the **course playbook** (section 6) for `ke-toan-tai-chinh-2`. Specific notes:
- 27 `_nguon` unit scripts (C1 1.1–1.7, C2 2.1–2.7, C3 3.1–3.5, C4 4.1–4.8) are expected to make `Chương 1–4.pdf` combined duplicates. Let the dedupe rule decide; do not assume.
- `Đề 2.pdf` = exercise (override src-0075 exists). `Đề thi mẫu.pdf` = exam. `Hướng dẫn ôn tập.pdf` = summary.
- Course code conflict ACCO1334 vs ACCO2315: store both in registry `codes`, `official: UNKNOWN`. Do not resolve.
- Prerequisite: registry `explicit_prerequisites: [ke-toan-tai-chinh-1]` (OBSERVED, src-0059).
- Topic-owner link required: core KTTC1 questions about TSCĐ must get `other_course_suggestions` → `ke-toan-tai-chinh-2`, chapter 1. Add an eval row for it in `evals/v3/ke-toan-tai-chinh-2_retrieval.jsonl` (category `topic_owner`) checking the suggestion key, not core items.

**GATE G1** = course gate (6.9) for KTTC2. `PAUSE` — learner tests 5 real questions with `python -m retrieval.cli retrieve "..." --course ke-toan-tai-chinh-2` (or via Grok bot) before Wave 2.

### WAVE 2 — ke-toan-chi-phi, kiem-toan-1, ke-toan-ngan-hang

Run the playbook per course, one at a time, gate each (G2a, G2b, G2c). Notes:
- KTCP: unit names `CHUONG n CHU DE m Pk` and `KTCP-Cn-CDx.y(.z)-…`. Chapters 2, 4, 7 have unit scripts; check each chapter with dedupe separately.
- Kiểm toán 1: units `NN_Script_ChN_Clip k` (topic = `clip k`) and `NN_Script_ChN_CD x.y(_Pk)`. `59_TLTK_BCKiT_CD 6.3.pdf` → `source_role: reference` (authority 6).
- Title variant: Ch6 script "Hoàn thành kiểm toán" vs ôn tập "Báo cáo kiểm toán" → both as aliases on the chapter concept, flag `TITLE_VARIANT` in report.
- KTNH: units `SCRIP KTNH_Cn_CDx.y_…(-Video k)`. Chart-of-accounts DOCX (src-0047): extract tables with python-docx (spec 7.2); authority 6; include in index. Bank account numbers go into the KTNH account map only.
- KTNH ↔ NHTM: no prerequisite edge (INFERRED low only). Do not add.

`PAUSE` after G2c.

### WAVE 3 — kinh-doanh-va-nghiep-vu, luat-kinh-doanh, tai-chinh-doanh-nghiep-1, ngan-hang-thuong-mai, thi-truong-tai-chinh, tai-chinh-hanh-chinh-su-nghiep

Playbook per course, gate each (G3a…G3f). Notes:
- These have no `_nguon` folders; combined PDFs are handled by existing overrides: src-0130 (NHTM combined), src-0178 (TCDN1), src-0186 (TCHCSN) → `combined_duplicate: true`, extract for coverage, exclude from index. Also run dedupe for `Slide <course>.pdf` / `Slide.pdf` / `SlideHành chính và sự nghiệp.pdf` / `Slide Ngân hàng Thương Mại.pdf` vs per-chapter slides; ≥0.85 → combined.
- `Corporate_Finance_Blueprint.pptx` is learner_material (0.6) — goes to `learner_notes` in 3g, not to TCDN1.
- NHTM law vintage conflict (Luật TCTD 2010 vs 32/2024/QH15): record as `conflicts` entry in the course concept table; do not merge.
- TCDN1 exam duration conflict (75 vs 90 phút): record, do not resolve.
- TCDN1 `TCDN1-Tailieuhuongdanntap.docx` → summary, include.

**3g — learner_notes partition (G3g)**
- Sources: every `learner_material` file (0.6) across all courses, plus any future file whose path contains `Claude outputs` or the learner's name.
- Extract with the same extractor (pptx via python-pptx: slide titles + text frames, one page per slide; txt/md: one synthetic page per 3000 chars).
- No concept table; chunks get `course_id` = the folder's course, `partition: learner_notes`, `authority: 7`, `content_role: learner_material`.
- Index in `data/indexes/3.0.0/learner-notes/`.
- Routing: only when the learner cue hits or `--course learner-notes`; never mixed into course partitions or core.
- Coverage on this partition is never reported as `sufficient` curriculum evidence: package sets `coverage: "learner_material"` and `unknowns: ["not_curriculum_source"]`.
- Gate G3g: extraction 0 errors; 5 eval rows (one per learner file family) retrieve the right file in top-3; core regression IDENTICAL; no course partition contains a learner_material chunk (assert).

`PAUSE` after G3g.

### WAVE 4 — Consistency, docs, runtime contract

**4.1** Regenerate `extracts/index.json` to list all extract `.md` files including Phase 2.1 ones. Add to `extracts/README.md`: "Legacy capped extracts (≤12 pages). Canonical text is `data/normalized/`."
**4.2** Course manifests: in each ingested manifest set `coverage.advertised_chapters_missing_files: []`, `chapters_with_script_files: <observed>`, add `v3: {tier: retrieval, index: 3.0.0, gate: G…, chunk_count: n}`. Fix the stale KTTC2 lines (`chapters_with_script_files: [1, 2]`, `advertised_chapters_missing_files: [3, 4]`, `missing_materials_vs_intro` chapter 3–4 item).
**4.3** `curriculum/curriculum_manifest.yaml`: per course add `v3_tier`. Do not change other fields.
**4.4** `reports/data_quality_report.md`: append section "V3" with per-course extraction stats; mark the "Missing advertised chapters" bullet as superseded (do not delete history).
**4.5** `autopilot/state.yaml`:
```yaml
core_version: "9.0.0"
active_scope: [ACCO1325, ACCO2310]          # core tier unchanged
retrieval_scope: [<course_ids that passed>]
expansion:
  enabled: true
  mode: curriculum_ingestion_only
  authorized_by: learner
  authorized_at: "2026-10-11"
external_research:
  enabled: true            # set by Wave 5 gate; false until G5 passes
  mode: official_sources_only
refresh:
  enabled: true            # set by Wave 6 gate
```
Keep pilot fields as they are.
**4.6** `README.md`, `AGENTS.md`: add a "V3 course tiers" section (copy 4.1 table) and new CLI usage `--course <id>`. Do not rewrite existing text.
**4.7** `GROK_BOT_MASTER_INSTRUCTIONS.md`: replace the line `**Validated production scope:** NLKT (ACCO1325) + KTTC1 (ACCO2310)` with `**Core scope (full loop):** NLKT (ACCO1325) + KTTC1 (ACCO2310) · **Retrieval scope:** see curriculum/course_registry.yaml (tier: retrieval)` and insert section 8 text verbatim after section 3. Apply the same insert to `.grok/agents/learning-director.md` and `skills/curriculum-retrieval/SKILL.md` + `.grok/skills/curriculum-retrieval/SKILL.md` (short form: first 4 bullets).
**4.8** Run `scripts/freeze_core.py` → new `pilot/core_freeze_manifest.json` must still show core integrity OK and identical frozen suite hashes. Add `v3_partitions` block listing each partition's meta (chunk_count, source hashes count).
**4.9** Final report `reports/v3/V3_FINAL.md`: per course table (sources, pages, chars, chunks, concepts, eval scores), escalations, open items, learner-material list for the learner to confirm.

**GATE G4**: frozen suites identical to baseline; all course gates pass; docs updated. Commit. Done.

### WAVE 5 — External "latest regulation" plane (layer C)

Goal: the tutor can say "giáo trình dạy theo X; quy định hiện hành là Y (hiệu lực từ …)". External text never overwrites or merges into curriculum. Executor uses web search / fetch tools of the session.

**5.1 Regulation inventory from the curriculum (mechanical)**
- Over all `data/normalized/*.pages.jsonl` (core + partitions), regex-harvest references: `Thông tư\s*\d+/\d{4}/TT-[A-ZĐ]+`, `TT\s*\d+/\d{4}`, `Nghị định\s*\d+/\d{4}/NĐ-CP`, `Luật\s+[^\n,.;]{3,60}?\s*(?:số\s*)?\d+/\d{4}/QH\d+`, `Luật\s+(Kế toán|Doanh nghiệp|Các tổ chức tín dụng|Kiểm toán độc lập|Ngân sách nhà nước|Chứng khoán|Thuế [^\n]{2,30})(\s*năm\s*\d{4})?`, `VAS\s*\d+`, `Chuẩn mực kế toán (Việt Nam )?số\s*\d+`, `IFRS\s*\d+`, `IAS\s*\d+`, `Quyết định\s*\d+/\d{4}/QĐ-[A-Z]+`.
- Output `research/curriculum_citations.json`: `{ref_normalized, variants, courses, occurrences:[{source_id,page}]}`.

**5.2 Status check per cited instrument (web, official sources first)**
- For each `ref_normalized` determine: current status (`in_force | amended | replaced | expired | unknown`), replacing/amending instrument, effective date, scope.
- Source priority: 1) `vbpl.vn`, `chinhphu.vn`, `mof.gov.vn`, `sbv.gov.vn`, `quochoi.vn`, `congbao.chinhphu.vn`; 2) `thuvienphapluat.vn` (secondary, must be confirmed by 1 when possible); 3) Big-4 / university summaries only as pointers, never as sole evidence. Record retrieval date.
- Known leads the executor must verify (do not record as fact without a source): TT 200/2014/TT-BTC → TT 99/2025/TT-BTC (chế độ kế toán doanh nghiệp); TT 107/2017/TT-BTC → TT 24/2024/TT-BTC (kế toán HCSN); Luật các TCTD 2010 → Luật 32/2024/QH15; Vietnam IFRS roadmap (QĐ 345/QĐ-BTC 2020) and any successor; Luật Doanh nghiệp 2020 amendments.
- Output one record per instrument in `research/regulations/<slug>.yaml` conforming to `research/research_evidence.schema.yaml` (extend with fields below if missing, without breaking it):
  ```yaml
  ref: "Thông tư 200/2014/TT-BTC"
  status: replaced
  replaced_by: "Thông tư 99/2025/TT-BTC"
  effective_from: "YYYY-MM-DD"
  scope: "..."
  key_changes: ["…"]          # ≤ 8 bullets, each with its own source URL
  cited_in_courses: [ke-toan-tai-chinh-1, ke-toan-tai-chinh-2, …]
  sources: [{url, publisher, retrieved_at, authority: official|secondary}]
  evidence_status: OBSERVED | INFERRED | UNKNOWN
  layer: external
  ```
- Download the official text (PDF/DOC) only when the site allows it; save under `research/sources/<slug>.<ext>` (not under `D:\Hoc\<course>`), extract with the same extractor, index into `data/indexes/3.0.0/external/` (partition `external`, authority 8).

**5.3 Runtime wiring**
- `retrieval/partition.py`: `external_notes(pkg)` — for every chunk in a curriculum package whose text cites an instrument with status `replaced|amended|expired`, add to `pkg["v3"]["regulation_updates"]` `{ref, status, replaced_by, effective_from, record}`. Additive only; never changes items or coverage. Legacy path: add under the additive key `other_course_suggestions`'s sibling `regulation_updates` (ignored by the regression comparator — add it to the ignore list in 7.7).
- Routing to the `external` partition only when the question contains cues: `hiện hành`, `mới nhất`, `cập nhật`, `còn hiệu lực`, `thay thế`, `IFRS`, `quy định mới`, or `--course external`.
- Answers from `external` always carry the label `theo quy định hiện hành (nguồn ngoài giáo trình)`.

**GATE G5**: every cited instrument has a record (status may be `unknown` with reason); every non-`unknown` status has ≥1 official source or is marked `INFERRED`; core regression IDENTICAL; 5 eval rows (`evals/v3/external_retrieval.jsonl`) pass: TT200 question gets a `regulation_updates` entry; a pure curriculum question gets none. Then set `external_research.enabled: true`. `PAUSE`.

### WAVE 6 — Incremental refresh (new files in `D:\Hoc`)

**6.1** `scripts/v3_refresh.py --plan`: compare current `D:\Hoc` listing (from `device_list_dir` recursive, saved to `work/listing.json`) with inventory by relative_path + size; list NEW / CHANGED (size differs) / MISSING. Stage NEW+CHANGED, hash, confirm.
**6.2** `--apply`: append NEW to inventory (next src ids); for CHANGED keep the old row, add a new row with `supersedes: src-XXXX` (never rewrite history); classify (learner rule from 0.6; tmp rule); re-run playbook steps 6.2–6.6 for affected courses only, then 6.9 gate using the already-frozen course evals (do not rewrite them; add new rows in a new file `evals/v3/<C>_retrieval_r<N>.jsonl` if new topics appeared).
**6.3** Core sources changed or added (NLKT/KTTC1) → do NOT touch index 2.0.0; STOP and escalate (`OPUS_ONLY`).
**6.4** Re-run 5.1 citation harvest for affected courses; check new citations (5.2).
**6.5** Write `reports/v3/refresh_<date>.md`. Document in `README.md` how the learner triggers it: paste `V3_KICKOFF_PROMPT.md` and say "chạy Wave 6 refresh".

**GATE G6**: dry run on the current corpus reports 0 NEW / 0 CHANGED after Waves 0–5 (idempotent); a simulated NEW file in the mirror (copy any unit script under a new name in the cloud mirror only, never on D:) is detected, ingested, and removed again. `PAUSE`, done.

### WAVE 7 — OPUS_ONLY (not for the executor)
Extending diagnosis/decision/admission to `retrieval`-tier courses (starting with KTTC2, prerequisite KTTC1). Requires new design and new eval suites. Executor must not start it.

---

## 6. COURSE PLAYBOOK (repeat per course)

`C` = course_id. Work dir `work/<C>/` (not committed except reports).

**6.1 Stage** all inventory rows of C (not `/tmp/`). Hash-check against inventory; mismatch → STOP.

**6.2 Extract** — `python scripts/v3_extract_course.py --course C`
- Generalize `scripts/phase2_extract.py`: course from arg; names/codes from registry; output to `data/normalized/C.*`; `EXTRACT_VERSION = "3.0.0"`; no page cap.
- Include `_nguon/` files. Parse chapter/topic per spec 7.2. Store `unit_script: true` for `_nguon` files.
- DOCX via python-docx (paragraphs + tables, spec 7.2). PPTX skipped unless not learner_material (then python-pptx text frames).
- Apply overrides (`content_role`, `index_include: false` for learner_material and combined).
- Check: `errors == []`; every PDF `page_count` equals pypdf count; list docs with `chars_per_page < 300` that are not slides as `THIN` in the report (do not stop).

**6.3 Dedupe** — `python scripts/v3_dedupe.py --course C` (spec 7.3). Writes `reports/v3/C_dedupe.json` and sets `combined_duplicate`/`index_include`/`dup_group` in `C.documents.jsonl`.

**6.4 Concept candidates** — `python scripts/v3_concept_candidates.py --course C` → `work/C/concept_candidates.json`:
- unit-script topic titles (from filename and first-page "Chủ đề x.y: …" line),
- lines matching `^(Chương|CHƯƠNG)\s*\d+[:.\-]\s*(.+)$`, `^(Chủ đề|CHỦ ĐỀ)\s*\d+(\.\d+)*[:.\-]\s*(.+)$`, `^PHẦN\s*\d+[:.\-]\s*(.+)$`,
- PDF outline titles,
- account numbers `TK\s*(\d{3,5})` with counts,
- each with source_id, page, count.

**6.5 Concept table (the only judgment step)** — write `curriculum/concepts/C.yaml` (spec 7.4):
- 15–40 concepts. One concept per teachable topic (usually one per "Chủ đề"), plus key cross-topic terms that appear ≥3 times.
- `canonical_name`: exact Vietnamese text from a heading.
- `aliases`: only strings present in C's extracted text (validator checks). Include abbreviations used in the text (e.g. "TSCĐ", "DTBH").
- `same_as`: a core concept id if the meaning is identical (e.g. `tscd`, `khau-hao`, `hang-ton-kho`, `bao-cao-kqkd`). Do not edit the core entry.
- `account_map`: accounts with count ≥ 2 in C's text → concept id.
- Edges: only `explicit` ones you can quote (quote + source_id + page). Otherwise none.
- Run `python scripts/v3_validate_concepts.py --course C`. Must pass.

**6.6 Partition build** — `python scripts/v3_build_partition.py --course C`
- Chunk with the unchanged `pages_to_units()` algorithm and constants; chunk ids `chk-<source_id>-NNNN`; concept tags via `map_text_course(text, C)`; carry `dup_group`, `unit_script`, `chapter`, `topic`.
- Build index into `data/indexes/3.0.0/C/` with `build_index(chunks_path, index_dir, meta_extra={"course_id": C, "concept_table_version": ...})`.
- Check: chunk_count > 0; every indexed document has ≥1 chunk; `meta.source_hashes` ⊆ inventory hashes.

**6.7 Write course evals (before any tuning)** — `evals/v3/C_retrieval.jsonl`, ≥20 rows, schema = phase2 tests + `"course": C`:
- 10 `direct`: one per major topic; question phrased like a student, includes the course name; `must_include_source_ids` = the unit script (or chapter PDF if no unit); `expected_chapter`.
- 3 `source_bound`: "theo chương N …", "đề thi mẫu …", "hướng dẫn ôn tập …".
- 3 `insufficient`: topics owned by another course, asked inside C (e.g. "WACC trong <C>").
- 2 `collision`: "Chương 1 của <course name> nói về gì?" → must_not_include any other course.
- 2 `account`: question naming an account number from C's account map.
- Wave 1 also: `topic_owner` rows (see Wave 1).
- Run `python scripts/v3_eval_course.py --course C` once; record file sha256 + first-run scores in `evals/v3/FROZEN.json`. From now on the file is frozen.

**6.8 Tuning (max 2 rounds)** — allowed knobs only: course cues in registry, concept aliases / account map in `concepts/C.yaml`, `dup_group` decisions with evidence. Not allowed: eval file, hybrid weights, core files. Re-run 6.6 if concepts changed, then 6.7 runner.

**6.9 Course gate** — all must hold:
- extraction: 0 errors; page counts match.
- dedupe report present; no unresolved `REVIEW` pairs (spec 7.3) — if any, STOP.
- validator pass.
- course evals: `direct` must_include@5 ≥ 85%; `direct` expected_chapter@1 ≥ 80%; `source_bound` ≥ 2/3; `insufficient` 100%; `collision` contamination 0; `account` ≥ 1/2; `topic_owner` 100%.
- core regression: `scripts/v3_regression.py` → identical to baseline (additive key allowed).
- then set registry tier `retrieval`, write `reports/v3/G-<C>.md`, commit the course's data, concepts, evals, reports, registry.

If a gate fails after 2 tuning rounds → leave tier `catalog`, write the failure report, escalate, continue with the next course only if the failure is local to C.

---

## 7. SPECS

### 7.1 `curriculum/course_registry.yaml`

```yaml
version: "1.0.0"
courses:
  - id: nguyen-ly-ke-toan
    name: Nguyên lý kế toán
    codes: [ACCO1325]
    tier: core
    cues: []                       # core cues stay in analyze.py
  - id: ke-toan-tai-chinh-1
    name: Kế toán tài chính 1
    codes: [ACCO2310]
    tier: core
    cues: []
    explicit_prerequisites: [nguyen-ly-ke-toan]
  - id: ke-toan-tai-chinh-2
    name: Kế toán tài chính 2
    codes: [ACCO1334, ACCO2315]
    code_official: UNKNOWN
    tier: catalog
    cues: ["kế toán tài chính 2", "kttc2", "kttc 2", "acco1334", "acco2315"]
    explicit_prerequisites: [ke-toan-tai-chinh-1]
  - id: ke-toan-chi-phi
    name: Kế toán chi phí
    codes: []
    tier: catalog
    cues: ["kế toán chi phí", "ktcp"]
  - id: kiem-toan-1
    name: Kiểm toán 1
    codes: []
    tier: catalog
    cues: ["kiểm toán 1", "môn kiểm toán"]
    explicit_prerequisites_family: ke-toan-tai-chinh   # which part UNKNOWN
  - id: ke-toan-ngan-hang
    name: Kế toán ngân hàng
    codes: [ACCO1331]
    tier: catalog
    cues: ["kế toán ngân hàng", "ktnh", "acco1331"]
  - id: ngan-hang-thuong-mai
    name: Ngân hàng thương mại
    codes: []
    tier: catalog
    cues: ["ngân hàng thương mại", "nhtm"]
  - id: tai-chinh-doanh-nghiep-1
    name: Tài chính doanh nghiệp 1
    codes: []
    tier: catalog
    cues: ["tài chính doanh nghiệp 1", "tài chính doanh nghiệp", "tcdn1", "tcdn 1", "tcdn"]
  - id: thi-truong-tai-chinh
    name: Thị trường tài chính
    codes: []
    tier: catalog
    cues: ["thị trường tài chính", "tttc"]
  - id: tai-chinh-hanh-chinh-su-nghiep
    name: Tài chính hành chính sự nghiệp
    codes: []
    tier: catalog
    cues: ["tài chính hành chính sự nghiệp", "hành chính sự nghiệp", "tchcsn", "hcsn"]
  - id: luat-kinh-doanh
    name: Luật kinh doanh
    codes: []
    tier: catalog
    cues: ["luật kinh doanh", "lkd"]
  - id: kinh-doanh-va-nghiep-vu
    name: Kinh doanh và nghiệp vụ
    codes: [ACCO1305]
    tier: catalog
    cues: ["kinh doanh và nghiệp vụ", "kdnv", "kdvnv", "acco1305"]
  - id: learner-notes
    name: Tài liệu cá nhân
    tier: catalog            # becomes retrieval after G3g; content is never curriculum
    cues: ["bài làm của tao", "bài thảo luận của tao", "sổ tay", "ghi chú của tao", "bài của tao"]
  - id: external
    name: Quy định hiện hành (nguồn ngoài giáo trình)
    tier: catalog            # becomes retrieval after G5; layer C
    cues: ["hiện hành", "mới nhất", "còn hiệu lực", "quy định mới", "thay thế thông tư"]
partition_root: data/indexes/3.0.0
```
Cue matching: folded (NFC + lower), word-boundary for tokens ≤ 5 chars (`\btcdn\b`), substring for multi-word phrases. Longest cue wins inside one course.

### 7.2 Filename parsing (chapter / topic / part)

Apply in order; first match wins; record `parse_rule`:

| Pattern (case-insensitive) | chapter | topic | part |
|---|---|---|---|
| `KTTC2-C(\d+)-CD(\d+\.\d+)` | g1 | g2 | — |
| `KTCP-C(\d+)-CD(\d+(?:\.\d+)+)` | g1 | g2 | — |
| `CHUONG\s*(\d+)\s*CHU\s*DE\s*(\d+)\s*P\s*(\d+)` | g1 | `g1.g2` | g3 |
| `CHUONG\s*(\d+)\s*CHU\s*DE\s*(\d+)` | g1 | `g1.g2` | — |
| `KTNH_C(\d+)_CD(\d+\.\d+)` | g1 | g2 | `Video k` if present |
| `Script_Ch(\d+)[_-]\s*CD\s*(\d+\.\d+)(?:_P(\d+))?` | g1 | g2 | g3 |
| `Script_Ch(\d+)_Cli[pP]\s*(\d+)` | g1 | `clip g2` | — |
| `TLTK_.*CD\s*(\d+)\.(\d+)` | g1 | `g1.g2` | role reference |
| `KDNV-C(\d+)-CD(\d+\.\d+)` / `Chuong(\d+)-Chude\s*(\d+\.\d+)` / `LKD-C(\d+)-\s*CD\.\s*(\d+\.\d+)` / `NLKT-C(\d+)-CD(\d+\.\d+)` | g1 | g2 | — |
| `(?:Slide\s*)?(?:Chương|chương|Chuong)\s*(\d+)` | g1 | — | — |
| otherwise | inventory `apparent_chapter` or null | — | — |

Every `_nguon` file must get a chapter; otherwise list as `UNPARSED` in the report and STOP for that course.

DOCX: paragraphs in order; each table → rows joined with ` | `, prefixed `[TABLE n]`. One synthetic page per 3000 chars (`page` = 1..n, `synthetic_pages: true`).

### 7.3 Dedupe rule

For each chapter N of course C that has both a chapter-level document (chapter PDF or combined PDF) and unit scripts:
- Normalize text: fold, remove `----- PAGE n -----` lines, collapse whitespace, drop lines shorter than 4 chars.
- Shingles = 8-token windows (use `tokenize()`).
- `cov = |S(chapter) ∩ ∪S(units)| / |S(chapter)|`; `back = |S(chapter) ∩ ∪S(units)| / |∪S(units)|`.
- `cov ≥ 0.85` → chapter doc `combined_duplicate: true, index_include: false` (coverage only); units canonical.
- `cov ≤ 0.50` → both canonical, no dup_group.
- `0.50 < cov < 0.85` → both indexed; chunk-level de-dup: chunks whose 8-shingle Jaccard with any unit chunk ≥ 0.6 share that unit chunk's `dup_group` (ids `dg-<C>-NNNN`). Mark pair `REVIEW` only if `back < 0.5` too (units and chapter mostly differ yet partially overlap) → STOP for that course.
- Course-wide combined slide/script PDFs vs per-chapter files: same rule, chapter-level docs play the "units" role.
Report every pair with cov/back and the decision.

### 7.4 `curriculum/concepts/<C>.yaml`

```yaml
course_id: ke-toan-tai-chinh-2
version: "0.1.0"
id_prefix: kttc2
concepts:
  - concept_id: kttc2-dieu-kien-ghi-nhan-doanh-thu
    canonical_name: "Điều kiện ghi nhận doanh thu"
    aliases: ["ghi nhận doanh thu", "điều kiện ghi nhận"]
    same_as: null
    chapter: 4
    topic: "4.1"
    source_refs: [{source_id: src-XXXX, page: 2}]
    evidence_status: OBSERVED
    confidence: high
account_map:
  "3387": kttc2-doanh-thu-chua-thuc-hien
edges:
  - from: kttc2-...
    to: kttc2-...
    type: explicit_sequence
    quote: "..."
    source_id: src-XXXX
    page: 3
conflicts: []
```
Id prefixes: kttc2, ktcp, kt1, ktnh, nhtm, tcdn1, tttc, hcsn, lkd, kdnv. Slug = ASCII kebab of canonical name (strip diacritics, đ→d).

Validator checks: YAML schema; ids unique across all concept files and the core registry; prefix correct; every alias and canonical name occurs (folded substring) in C's pages ≥ 1 time; alias length ≥ 6 after fold unless it is an all-caps abbreviation present in text; no alias shared by two concepts of the same course; `same_as` ids exist in core registry; every `source_refs` page contains the canonical name or an alias; edges have quote found on that page.

### 7.5 Course eval runner

`scripts/v3_eval_course.py --course C`: for each row call `retrieve(question, filters={"mode": row.mode} if set)`. Do not pass `course_id` except for rows with `"pass_course": true`. Metrics per category as in 6.9. Writes `reports/v3/C_eval.json` + `.md`.

### 7.6 Package compatibility

Partition packages must validate against `schemas/evidence_package.schema.json`. If extra keys break validation, put them under `"v3": {...}` instead of top level.

### 7.7 Core regression comparator

`scripts/v3_regression.py`: re-run P2–P8 eval scripts into `reports/v3/run_<ts>/`, then compare with `reports/v3/baseline/`:
- P2: per-test pass/fail and top-5 `source_id` list per test must be identical.
- P3–P8: per-case outcome fields (status, action, admission decision, state, next action) identical.
- Ignore timestamps, uuids, latency, and the additive keys `other_course_suggestions` and `regulation_updates`.
Output `IDENTICAL` or a diff list. Anything not `IDENTICAL` fails the gate.

---

## 8. RUNTIME CONTRACT TEXT (insert in Wave 4.7, verbatim)

```markdown
## 3A. COURSE TIERS (v3)

The system now has three course tiers. Check `curriculum/course_registry.yaml`.

- **CORE** — NLKT (ACCO1325), KTTC1 (ACCO2310). Full loop: retrieve, diagnose, decide, adapt, admit, state, next action.
- **RETRIEVAL** — courses with `tier: retrieval`. Teach and look up sources only. When the learner submits an attempt, compare it with the retrieved curriculum evidence and point out exactly where it differs ("đối chiếu giáo trình"). Do not output diagnosis labels, do not make learner-state claims, do not admit evidence.
- **CATALOG** — material exists in `D:\Hoc` but is not indexed. Say so; do not answer from model knowledge as if it were the curriculum.

Routing:
- When the learner names the course, always pass it: `python -m retrieval.cli retrieve "..." --course <id>`.
- If the topic exists in several courses and the course is unknown, and the answer depends on it, ask once.
- If a package carries `other_course_suggestions`, mention that the topic is taught in that course and offer to look there.
- Never use RETRIEVAL-tier material to diagnose or backfill CORE concepts.

Learner notes (`learner-notes` partition): the learner's own write-ups and handbooks. Use only when the learner refers to their own work. Always label "tài liệu cá nhân của bạn, không phải giáo trình". Never cite it as curriculum evidence.

Latest regulations (`external` partition, `regulation_updates` in packages):
- When a package carries `regulation_updates`, answer per the curriculum first ("theo giáo trình"), then add one short note "theo quy định hiện hành: … (hiệu lực …, nguồn …)".
- For exam/assignment answers, follow the curriculum unless the learner asks for the current rule.
- A difference between curriculum and current regulation is never a learner error.
```

---

## 9. STOP / ESCALATE CONDITIONS

Stop the current course (or wave, where stated), write `escalations` entry, report to the learner in one short message, wait:
1. Cloud baseline ≠ historical metrics (0.2) — whole plan.
2. Any core regression diff (0.3, 0.5, every gate) — whole plan.
3. Hash mismatch / missing source on stage.
4. Extraction error, or `_nguon` file without parsed chapter.
5. Dedupe `REVIEW` pair.
6. Validator cannot pass without inventing aliases.
7. Course gate failed after 2 tuning rounds.
8. Any need to edit a frozen artifact or engine logic.
9. Commit rejected (mtime drift, read-only, size).
10. Anything that would require writing outside `D:\Hoc\_learning_system`.
11. NOT a stop: a regulation whose status cannot be verified from an official source — record `status: unknown` / `INFERRED` with the reason and continue.

---

## 10. REPORTING TO THE LEARNER

Vietnamese, short. After each gate: what passed, the numbers (sources / chunks / concepts / eval %), anything flagged, and the next step. No architecture lectures.

---

## AMENDMENT A1 (design model, 2026-10-11) — off-outline detection in partitions

Trigger: G1 escalation. In `retrieve_partition` the legacy min-max hybrid score always gives the best chunk ~1.0, so `top < 0.08 → insufficient` never fires. A hard "no course concept → insufficient" rule passed the frozen eval but flagged 7/8 realistic in-course questions (chiết khấu thương mại, cổ tức bằng cổ phiếu, trái phiếu…) as insufficient: rejected as overfit.

Adopted rule (4.3a/4.3b, implemented in `retrieval/partition.py`), only for a free question (no chapter, mode ≠ source_bound) that matches **no concept of this course**:
1. coverage is capped at `partial`; unknown `no_course_concept_match` (tutor hedges, shows nearest evidence).
2. a content term absent from the course's whole corpus → `insufficient` + `term_not_in_course_corpus:<t>`.
3. another indexed course (core courses included) explains the question clearly better — query-bigram coverage of its BM25 top-5 ≥ 0.75 and ≥ this course + 0.25 → `insufficient` + `topic_in_other_course:<id>`.
4. core-registry concepts owned by other courses add `topic_owner_hint:<id>` (explanatory only).
Thresholds fixed a priori, not fitted to eval rows.

Gate change: rule 3 can only work once other courses are indexed. The `insufficient` metric of every course gate is therefore **deferred** to a new checkpoint **G3x** (after Wave 3, before Wave 4): re-run every frozen `evals/v3/*_retrieval.jsonl`; all gates incl. `insufficient 100%` must hold then. Until G3x a course passes its gate provisionally if all other metrics hold. If G3x fails, the failing courses go back to `catalog` and escalate. Eval files are not edited.

# AMENDMENT A2 (design model, 2026-10-11): unblock G4, scoped repair for 3 courses

Status: BINDING. This amendment has the same authority as Amendment A1. The executor appends this file verbatim to the end of `V3_EXPANSION_PLAN.md` (after A1), then follows it.

## Why

G4 says "all course gates pass". That contradicts §6.9, which explicitly allows a failed course to stay `catalog` with a failure report so the build can continue. The executor (Codex) read the G4 text literally and stopped correctly. The design decision is below.

## A2.1: G4 reinterpreted (takes effect now)

**GATE G4** passes when all of these hold:
1. Frozen suites identical to baseline (`v3_regression.py` IDENTICAL).
2. **Every course has a final state:**
   - either tier `retrieval` with its gate report passing,
   - or tier `catalog` with a failure report in `reports/v3/G-<C>.md` and an escalation entry in progress.
3. Docs 4.1–4.9 are updated, and `V3_FINAL.md` lists the catalog courses under "Open items".
4. All frozen V3 eval hashes are unchanged.

From the current state (G4.md + D1_rerun.md) this is already satisfied, so **G4 = PASS (A2)**. The executor:
- updates `autopilot/v3_progress.yaml`: `gates.G4.status: pass_a2`, `resolution` of the G4 escalation = `Amendment A2.1`;
- adds a line to `reports/v3/G4.md`: "G4 PASS under Amendment A2.1; KTCP, KTNH, TCDN1 remain catalog (open items R1)";
- does **not** change any tier.

Then go to **Wave 5** according to the plan (PAUSE at the plan's gates).

## A2.2: D2 recorded

The learner has waived 3 rows kp-t01..03 (KTCP topic_owner). Raw results stay as they are. A gate calculation for KTCP **excludes these 3 rows** and must state "D2 waiver" in the report. Nothing else is waived.

## A2.3: R1, scoped repair (do after G5 PASS, before Wave 6)

Uniform D1 (strip cues for every course) is **rejected**, because it lowered TCHCSN to 0.75. Replace it with a per-course knob.

**R1a: `strip_course_cues` flag per course (KTCP, KTNH)**
- Add an optional field to the registry: `retrieval.strip_course_cues: true|false` (default `false`). This is a registry cue knob and falls within the spirit of §6.8.
- In `retrieve_partition`: only when the target course has `strip_course_cues: true`, remove that course's cue tokens from the query **for the BM25/TF-IDF lexical part only**. Concept matching, routing and the coverage/A1 computation keep the original query.
- Enable it for `ke-toan-chi-phi` and `ke-toan-ngan-hang` only.
- Every other course must have output that is **byte-identical** to before the change. Check this by diffing the `_eval_g3x_fixed.json` output of the 7 retrieval courses before and after (rank + score per row). Any difference means revert and STOP.

**R1b: TCDN1 — attach the correct chapter to chunks of the multi-chapter document (data, not ranking)**
- Cause (D1_rerun): the summary src-0177 and the chapter-0 overview win top-1, and their chapter label is wrong or null, so chapter@1 = 0.333.
- Repair: in `v3_build_partition.py`, for documents that span chapters (src-0177 and the chapter-0 overview), assign `chapter` **per chunk** based on the nearest preceding `Chương n` / `Chủ đề n.x` heading in that document's text (regex from spec 6.4). If there is no heading, set `chapter: null` and `content_role: overview`.
- Do not change hybrid weights or demote any source. Only fix metadata, rebuild the TCDN1 partition, then run the eval.
- Allowed together with R1b: mark a dup_group if the summary is ≥0.85 overlapping a chapter file (spec 7.3, with evidence).

**R1 gate for each of the 3 courses:** §6.9 thresholds (KTCP after excluding D2). At most **2 rounds** for the whole of R1.
- Pass: tier `retrieval`, update the G-<C>.md report, add the course to `retrieval_scope` in `autopilot/state.yaml`, run `freeze_core.py` again, update `V3_FINAL.md`.
- Fail: stay `catalog` and write `reports/v3/R1.md`. **This is not a STOP**, because the courses already have a final state under A2.1. Continue to Wave 6.

Core regression must be IDENTICAL after R1a and after R1b. If it is not: revert and STOP.

## A2.4: Unchanged

Frozen evals, hybrid weights, core engine, Wave 7 OPUS_ONLY, and the stop conditions in §9 (except the G4 wording above).
