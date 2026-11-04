# Retrieval benchmark (Phase 2)

Frozen set: `evals/phase2_retrieval_tests.jsonl` (60 tests).  
Executed: `python scripts/phase2_eval.py`  
Raw: `reports/retrieval_benchmark_raw.json`

## Systems

| id | description |
|---|---|
| naive | TF-IDF cosine, no course/chapter mask, no concept/authority, no prereq list |
| hybrid | BM25 + TF-IDF + concept + metadata + authority + mode masks |
| hybrid_prereq | hybrid with prereq expansion forced when mode allows |

On this frozen file, tests already carry an expected `mode`, so hybrid and hybrid_prereq score the same. Default production system is **hybrid** (mode selected by analysis, not forced).

## Metrics

| metric | naive | hybrid | gate |
|---|---|---|---|
| pass rate | 0.35 | **0.967** | — |
| course accuracy | 0.90 | **1.00** | >= 0.95 **PASS** |
| chapter accuracy | 0.95 | **1.00** | — |
| concept accuracy | 0.917 | 0.983 | — |
| relevant evidence top-5 | 0.917 | **0.983** | >= 0.90 **PASS** |
| wrong-course contamination | **0.629** | **0.000** | <= 0.05 **PASS** |
| prerequisite precision | 0.00 | **1.00** | — |
| insufficient-evidence detection | 0.00 | **1.00** | >= 0.90 **PASS** |
| authority correctness | 0.967 | 1.00 | — |
| mean latency | 4 ms | 7 ms | — |

## Ablation

Hybrid vs naive:

- pass_rate +0.62
- contamination −0.63 (0.63 → 0.00)
- insufficient detection +1.00
- course accuracy +0.10
- relevant top-5 +0.07

Naive lexical/semantic search cannot keep NLKT and KTTC1 apart (`Chương 1.pdf` collision) and never says insufficient. Those two failures are why the architecture exists.

## By category (hybrid)

| category | n | pass |
|---|---|---|
| nlkt_direct | 15 | 15 |
| kttc1_direct | 15 | 14 |
| prerequisite | 10 | 9 |
| cross_course | 10 | 10 |
| ambiguous | 5 | 5 |
| insufficient | 5 | 5 |

2 residual misses are listed in `retrieval_failures.md`. They do not fail the hard gates.

## Decision on components

Keep hybrid masks + BM25. TF-IDF alone (naive) is not sufficient. Do not add a hosted vector DB for this slice: latency is already < 15 ms and correctness is mask-driven.
