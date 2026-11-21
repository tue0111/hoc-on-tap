# G-ke-toan-thue-1: course gate (playbook 6.9), W6b Pha B

Date 2026-11-21 · course `ke-toan-thue-1` (Kế toán thuế 1, ACCO2311) · **GATE: PASS** (first run, 0 tuning rounds)
Tier stays `catalog` in the registry. Pha C switches it to `retrieval` and merges the frozen entry.

## 6.1 Sources
- 52 inventory rows (src-0491..src-0542); sha256 + size match the inventory for 52/52 (read from `D:\Hoc` in place, no staging).

## 6.2 Extraction (`data/normalized/ke-toan-thue-1.*`)
- 27 documents extracted: 24 topic scripts PDF (`NN. Cx. Scrip CHUONG x.y.pdf`, rule `thue_cn`, chapter/topic parsed for 24/24),
  1 DOCX script for Chương 0 (src-0539, 2 synthetic pages), DE THI MAU (src-0541, 4 pages), HUONG DAN HOC TAP (src-0542, 7 pages).
- 176 pages (174 PDF + 2 synthetic) · 313,976 chars · page counts = pypdf for every PDF · THIN: none · UNPARSED: none.
- Real extraction errors: **0**. The 25 PPTX (24 topic slides + KeToanThue1_Slide.pptx) carry the extractor's known
  `pptx extractor not wired (non-learner pptx)` status. This is the expected skip from PLAN_W6B point 3, not a failure. Every
  PPTX has a script PDF/DOCX for the same chủ đề, so no topic is missing from the index. List in `work/ke-toan-thue-1/role_overrides_proposed.yaml`.

## 6.3 Dedupe
- `reports/v3/ke-toan-thue-1_dedupe.json`: 0 pairs and 0 REVIEW. The course has no chapter-level or combined PDF and no `_nguon` units.
  Each chủ đề has exactly one script, so all 27 documents are canonical (no dup_group).

## 6.4–6.5 Concepts (`curriculum/concepts/ke-toan-thue-1.yaml`)
- 35 concepts with prefix `thue1-`: 1 for Chương 0, 5 chapter-level, 24 per-chủ đề (canonical = verbatim "Chủ đề x.y: …" heading),
  and 5 cross-topic terms with ≥3 occurrences (Hoàn thuế, Hóa đơn điện tử, Đối tượng không chịu thuế, trị giá tính thuế, Tờ khai hải quan;
  canonical taken from a "Slide N." heading line, confidence medium).
- account_map: 3333 (XK-NK), 3332 (TTĐB), 3331 and 1331 (GTGT). The 5-digit sub-accounts 33381 (BVMT) and 33311/33312 are not mapped
  because the course account regex only reads 3-4 digits.
- edges: none (no quotable explicit sequence). conflicts: none. same_as: none (the core registry has no tax concept).
- The Chương 4 heading reads "Bảo vệ mội trường" (typo). It is kept verbatim, and "thuế bảo vệ môi trường" is an alias.
- Validator: **PASS** (35 concepts). It was run via `work/ke-toan-thue-1/run_validator.py`, because `v3_validate_concepts.py::PREFIX`
  has no entry for the W6b courses. The wrapper adds `thue1` in memory only, and the shared script is unchanged. **Pha C: add
  `"ke-toan-thue-1": "thue1"` to PREFIX.**

## 6.6 Partition (`data/chunks/ke-toan-thue-1.*`, `data/indexes/3.0.0/ke-toan-thue-1/`)
- 673 chunks · vocab 1641 · 27/27 indexed docs have ≥1 chunk · source_hashes ⊆ inventory · unchanged `pages_to_units()`.

## 6.7 Eval (`evals/v3/ke-toan-thue-1_retrieval.jsonl`, 20 rows, written before the first run)
sha256 `3d9eb60aae42b12939cf3a22fb90a9c03e2ba504c196cc29161bad5a7c8a3024`. Entry: `reports/v3/ke-toan-thue-1_frozen_entry.json`.
The first run used `work/ke-toan-thue-1/run_eval.py`, which sets the tier to `retrieval` in memory only. The registry file is not touched.

| gate | value | threshold | pass |
|---|---|---|---|
| direct must_include@5 | 1.00 (10/10) | ≥0.85 | ✔ |
| direct expected_chapter@1 | 0.80 (8/10) | ≥0.80 | ✔ (at threshold) |
| source_bound | 1.00 (3/3) | ≥2/3 | ✔ |
| insufficient | 1.00 (3/3) | 1.00 | ✔ |
| collision contamination | 0 | 0 | ✔ |
| account | 1.00 (2/2) | ≥1/2 | ✔ |
| topic_owner | n/a (no rows, Wave 1 only) | — | ✔ |

- The insufficient rows avoid every tax topic: WACC (TCDN1), chênh lệch tỷ giá hối đoái cuối kỳ (KTTC2/KTNH), ý kiến kiểm toán ngoại trừ (Kiểm toán 1).
  All 3 have reasons that do not depend on another agent's state: `term_not_in_course_corpus` (wacc; hối/đoái) or `topic_in_other_course:kiem-toan-1`.
- Chapter@1 misses: th-d03 (HTKK, top-1 = 3.4 report script that also teaches HTKK; correct src-0496 at rank 5) and th-d09 (PP khấu trừ vs trực tiếp, top-1 = 1.4 src-0496; correct src-0532 at ranks 2-3).
- 6.8 tuning: **not used** (0/2 rounds).

## Checks outside this course
- Core regression (`v3_regression.py`) was **not run**, as instructed (it writes shared files). No core, engine, or shared file was modified. This is left to Pha C (C2).
- Cross-check (informational, `work/ke-toan-thue-1/crosscheck.json`): the 188 frozen eval rows of the existing retrieval courses were run
  with and without ke-toan-thue-1 at tier retrieval (in memory). **0 differences** in pass, coverage, top-5 or unknowns.
- th-i02 also lists `topic_in_other_course:ke-toan-tai-chinh-3 / ke-toan-hanh-chinh-su-nghiep`, because the parallel agents' partitions already exist on disk.
  The row stays insufficient without them (OOV terms).

## Notes for Pha C / the learner
1. Add the `thue1` prefix to `scripts/v3_validate_concepts.py::PREFIX`.
2. Role proposals (`work/ke-toan-thue-1/role_overrides_proposed.yaml`): src-0539 → lecture_note (now unknown/authority 8); src-0542 → summary (now syllabus/authority 1). Neither one affects the gate.
3. The scripts cite instruments of the curriculum vintage (Luật QLT 38/2019/QH14, NĐ 126/2020, TT 80/2021, Luật XNK 107/2016, NĐ 134/2016, TT 200, TT 219, TT 78, NĐ 123). Not updated here. Citation harvest is Pha C3.
4. No prerequisite sentence was found, so `explicit_prerequisites` is not recorded.
5. Escalation: none.
