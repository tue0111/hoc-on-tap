# G3x repair — PASS, 2026-10-11

User authorized debugging and fixing the G3x failure. Historical failure report `G3x.md` is preserved.

## Causes and repairs

1. Rival coverage ignored catalog courses even when their complete indexes existed. Compare all existing curriculum indexes for off-outline detection; catalog sources remain unavailable for answering.
2. Query bigrams removed question words, while source bigrams did not. Use the same token normalization on both. Remove request phrases (hướng dẫn, giải thích, trình bày, cho biết) as phrases rather than individual domain words. Thresholds remain 0.75 and 0.25.
3. A leading course label followed by another course mention fell through to legacy core. Recognize a leading label as scope when multiple non-core cues occur. Explicit filters keep priority; comparison questions without a leading label retain ambiguity.

Lexical ranking weights and D1 are unchanged. Frozen evals are unchanged (11 hashes verified).

## Verification

All seven course suites pass their aggregate gates using the actual restored registry. The insufficient rate is 3/3 in every course. Direct/source-bound scores remain at their pre-fix values; some individual rows still fail within the allowed aggregate thresholds.

Re-enabled: KTTC2, Kiểm toán 1, Kinh doanh và nghiệp vụ, Tài chính HCSN.

Already passing: Luật kinh doanh, Ngân hàng thương mại, Thị trường tài chính.

Learner-notes: 5/5 plus routing and metadata contracts PASS. Six independent in-course questions remain sufficient/partial rather than insufficient; explicit routing, ambiguous comparison, and catalog serving checks PASS (`scripts/v3_debug_g3x_checks.py`).

Core regression: IDENTICAL, `reports/v3/run_20261011_213339`.

Detailed suites: `reports/v3/*_eval_g3x_fixed.json`.

KTCP, KTNH and TCDN1 retain their earlier separate gate failures and remain catalog. Wave 4 has not started. This fix resolves the four G3x escalations without waiving other gates.
