# R1 continuation — resolved ownership blocker, 2026-10-12

Authorization: learner replied "ok, tiếp" to the specific request to repair the
topic-ownership coverage rule. This authorizes the narrow rule repair below,
not changes to frozen suites, core logic, weights, or Wave 7.

## Mechanism and patch

Course labels were matching KTCP's generic alias "kế toán tài chính" and being
treated as subject evidence. Coverage ownership now uses the subject query with
the requested course cues removed. This does not change local concept detection,
routing, ranking, or prerequisite queries. Explicit chapter/source-bound queries
retain their selected scope. If a term is outside the requested corpus, A1's
existing corpus/rival-evidence branch owns the coverage decision and reasons;
the concept-owner shortcut does not insert redundant competing explanations.

The lexical-only knob is enabled for KTCP and KTNH only. Other courses default
to false. No course-specific exception was added to the ownership rule.

## Verified outcome — second and final R1 round

- KTCP: include@5 0.90, chapter@1 0.80, source-bound 1.00; all gates pass with
  **D2 waiver**, excluding only kp-t01, kp-t02, kp-t03. Raw rows retained.
- KTNH: include@5 1.00, chapter@1 0.8333, source-bound 1.00; all gates pass.
- Both enabled in the actual registry and retrieval_scope, not just in-memory.
- Seven pre-existing course result arrays and every recorded rank/score match
  the pre-R1 snapshot byte-for-byte (including after actual promotion):
  `r1_final_non_targets.json`, SHA-256
  `e506277740b2b6322fb31b4eede6f36ca9ca374491a501e68d9ae1a982a96f71`.
- Core after ownership/lexical repair: `run_20261012_073139/diff.txt` IDENTICAL.
- Core after R1b metadata repair: `run_20261012_073324/diff.txt` IDENTICAL.
- Learner-notes: ALL_PASS; external: 5/5 PASS, schema and additive isolation PASS.
- freeze_core: source integrity OK, 40 core sources checked; 12 frozen V3 suites unchanged.

## TCDN1 remains catalog

Nearest-preceding-heading metadata repair is restored in the builder and TCDN1
partition only. It improves chapter@1 from 0.3333 to 0.5833 but remains below 0.80.
Some unchanged chunks span multiple chapters; the metadata records those chapter
headings and source offsets. Chunk content/boundaries and source authority are
unchanged. No further tuning is attempted after two R1 rounds. This local failure
does not block Wave 6 under A2.1/A2.3.

Current evidence: `ke-toan-chi-phi_eval_r1_final.json`, `ktcp_r1_final_d2.json`,
`ke-toan-ngan-hang_eval_r1_final.json`, `tai-chinh-doanh-nghiep-1_eval_r1_final.json`.
Previous STOP and rollback remain documented in R1.md as history.
