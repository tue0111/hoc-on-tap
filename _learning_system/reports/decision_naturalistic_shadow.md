# Naturalistic shadow set (Phase 4)

Cases: `evals/decision_naturalistic_shadow.jsonl` (40).  
Raw: `reports/decision_naturalistic_raw.json`.

**Not averaged with the controlled set.** Gold is mostly `VERIFY_MORE`. Cue phrases from Phase 3 (`tăng tài sản ghi Có`, `tính nhầm`, `em không nhớ số hiệu`) are absent on purpose.

## Phase 3 on this set

| metric | value | reading |
|---|---|---|
| DIAGNOSED rate | 0.75 | Phase 3 H-concept fallback still fires on vague text |
| INCONCLUSIVE rate | 0.25 | higher than controlled 12/90, still not the majority |
| PARTIAL rate | 0.00 | — |
| false prerequisite-gap | 0.00 | no NLKT blame |
| unsupported HIGH-confidence decisions | 0.00 | Phase 4 never taught at HIGH on these items |

Phase 3 over-labeling conceptual_failure on conversational Vietnamese is a known residual. Phase 4’s job is not to “fix” Phase 3 scores; it is to refuse to teach from that label when the observation is thin.

## Phase 4 on this set

| metric | value |
|---|---|
| VERIFY_MORE rate | 0.85 |
| action accuracy vs gold (VERIFY_MORE-heavy) | 0.85 |
| false prerequisite backfill | 0.00 |
| over-treatment | 0.00 |
| remaining mismatches | 6 (complete-looking false claims that Phase 4 treated as MECHANISM; gold still VERIFY_MORE) |

## Calibration stance

False confident teaching and false NLKT backfill are worse than extra VERIFY_MORE. The shadow set meets that bar. It does **not** meet controlled-set action accuracy, and it should not.

Level 6 must not promote a Phase 3 `conceptual_failure` from hedged free text into mastery or a long-term plan.
