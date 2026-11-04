# Incremental refresh summary — Phase 2.1

## Decision

**REFRESH_OK_NO_PHASE2_IMPACT**

New material is outside the NLKT + KTTC1 vertical slice. Frozen Phase 2 tests and index 2.0.0 were left in place. Benchmark was **not** rerun (no slice source change). Historical baseline copied to `reports/retrieval_benchmark_phase2_baseline.md`.

## What was done

1. Hash delta vs inventory (141 NEW / 0 CHANGED / 0 MISSING).
2. Appended inventory records `src-0193`–`src-0333` without renumbering old IDs.
3. Light-extracted 20 canonical new PDFs (chapters, ôn tập, đề mẫu).
4. Catalogued `_nguon` unit scripts only (`READY_FOR_FUTURE_INGESTION`).
5. Updated curriculum_manifest coverage for the four affected courses.
6. Added sourced concepts + graph edges; flagged one TITLE_VARIANT (audit Ch6).
7. Did **not** expand Learning Director production retrieval scope.

## Impact classes

| course | class |
|---|---|
| nguyen-ly-ke-toan | NO_RETRIEVAL_IMPACT |
| ke-toan-tai-chinh-1 | NO_RETRIEVAL_IMPACT |
| ke-toan-tai-chinh-2 | METADATA_ONLY |
| ke-toan-chi-phi | METADATA_ONLY |
| kiem-toan-1 | METADATA_ONLY |
| ke-toan-ngan-hang | METADATA_ONLY |

No REINDEX / RECHUNK / FULL_REEXTRACT of the Phase 2 slice.

## Frozen eval policy

`evals/phase2_retrieval_tests.jsonl` untouched.  
Previously-insufficient items (e.g. TSCĐ in KTTC1) remain insufficient: TSCĐ still lives in KTTC2, which is not in the production index. No historical test expected-results were rewritten to pass.

## Do not do next automatically

Diagnostic / mastery / Research Agent. Next explicit step, if wanted: a **Phase 2.2 ingest** of one completed course (KTTC2 or KTCP) into retrieval — not a silent scope expansion.
