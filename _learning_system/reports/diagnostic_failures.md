# Diagnostic failures (Phase 3)

Failure classes (for this and later logs):

`wrong_target_concept`, `wrong_root_cause`, `surface_symptom_only`, `false_prerequisite_gap`, `missed_prerequisite_gap`, `poor_diagnostic_question`, `question_leaks_answer`, `unnecessary_question`, `premature_diagnosis`, `failed_hypothesis_elimination`, `unsupported_diagnosis`, `source_contamination`, `retrieval_failure`, `insufficient_evidence_not_detected`, `unknown`.

## Controlled benchmark (System C)

On `evals/diagnostic_cases.jsonl` (90 constructed items), System C has **0 remaining fails**. System B also 90/90. System A 0/90 (by design: it never diagnoses).

This is not a claim that the engine will classify messy free text at 100%. The cases embed the error cue on purpose so the state machine, backtrace guard, and contrastive pairs can be scored.

## Failures that were found and fixed during the build

These are historical, not residual C fails:

| id / pattern | class | cause | fix |
|---|---|---|---|
| FIFO items with no concept | `wrong_target_concept` | `fifo` is a generic retrieval alias | pin `pp-tinh-gia-xuat-kho` in the diagnostic engine (retrieval untouched) |
| `kttc1-01` 112 vs 111 | `wrong_root_cause` | account set taken from `work_shown` which repeated 111 | compare accounts on `learner_response`; `thay vì` / `sai tài khoản` |
| `kttc1-02` target `dinh-khoan` | `wrong_target_concept` | “định khoản” beat hàng hóa | pin inventory object over generic journal |
| `pre-05` / `kttc1-20` target `kktx-kkdk` | `wrong_target_concept` | “kê khai thường xuyên” stole giá vốn / xuất kho | pin inventory movement before perpetual-vs-periodic |
| prereq recall | `missed_prerequisite_gap` | reversed Nợ/Có lost to conceptual rank; unconfirmed guard too strict on written rules | rank `prerequisite_gap` above conceptual; confirmed written rule skips the extra question |
| `amb-09` “Không biết.” | `insufficient_evidence_not_detected` | regex required `em không biết` | accept `không biết` |
| `nlkt-04` / `nlkt-05` | `unsupported_diagnosis` | journal-worded definition with no TK numbers → unknown | conceptual fallback for journal/definition with no mechanical signal |
| `kttc1-03` after arith/formula pair | `wrong_root_cause` | competitor H-arith ranked above explicit bình quân | do not add arith competitor when formula_mismatch is already named |
| generic A/B/C | `failed_hypothesis_elimination` | needle `c` matched Vietnamese `có` | option letters must be `(c)` / `c.` / `hiểu ngược` |

## Residual risks (not benchmark fails)

1. **Signal-aligned cases.** Learner text that never says `tính nhầm` / `tăng tài sản ghi Có` will often return `PARTIAL` or `INCONCLUSIVE`. Prefer that over a false prerequisite gap.
2. **`dq-arith-vs-formula` number cue.** The template mentions “50 đơn vị”. It does not state the correct total. Rubric: majority pass; tighten if naturalistic eval shows leakage.
3. **Unnecessary question on some single-turn items.** System C attaches a discriminator when two hypotheses remain (e.g. class vs account) even without a follow-up. Status stays `PARTIAL` / low until tested. Not a quiz marathon (max one question).
4. **Phase 2 residual retrieval misses** (`retrieval_failures.md`) are classified as `retrieval_failure` if they later poison a diagnosis. They were **not** patched here.
5. **LLM slot unused.** `diagnostic/llm_hooks.py` is off. Semantic interpretation of messy work is a Level 5/ops concern, not a silent fill of missing curriculum evidence.

## False-gap watch

False prerequisite-gap rate on this set: **0**. The engine will not emit `prerequisite_gap` for a KTTC1 error unless a false Nợ/Có rule is written or a discriminating test confirms it. Keep this as a hard regression check when cases expand.
