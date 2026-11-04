# Phase 2 summary — vertical slice retrieval

Scope: Nguyên lý kế toán (ACCO1325) + Kế toán tài chính 1 (ACCO2310).  
Source tree `D:\Hoc` was not modified (192 files, 0 hash mismatches).

## Built

- Full-text extract, no page cap: `data/normalized/`
- 810 structure-aware chunks: `data/chunks/`
- Hybrid index 2.0.0: `data/indexes/2.0.0/`
- Runtime: `retrieval/` (`analyze`, `retrieve`, `director`, CLI)
- 60 frozen tests: `evals/phase2_retrieval_tests.jsonl`
- Benchmark + ablation executed (not estimated)

## Demonstrated

| condition | result |
|---|---|
| A correct course | course accuracy 1.00 |
| B chapter/concept | chapter 1.00; concept 0.98; relevant top-5 0.98 |
| C KTTC1 can recover NLKT prereqs | prereq precision 1.00; 9/10 prereq tests |
| D NLKT not pulled into KTTC1 current-course | contamination 0.00 on masked tests |
| E provenance | every item has source_id, path, page_range, authority |
| F say insufficient | 5/5 insufficient tests; TSCĐ-in-KTTC1 refuses to invent a chapter |
| G hybrid beats naive | pass 0.97 vs 0.35; contamination 0.00 vs 0.63 |

## Not built (backlog, out of scope)

- Research Agent / IFRS updater
- Learner mastery
- Level 4 diagnostic engine
- Graph expansion beyond v0.1
- OCR for residual slide density

## Decision

**PASS → Phase 3 diagnostic vertical slice** (same two courses).
