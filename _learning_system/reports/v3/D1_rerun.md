# D1 trial — blocked and reverted

Authorization: learner approved D1 and D2 via "ok, làm xong qua Wave 5".
D2 waiver applies only to kp-t01, kp-t02, kp-t03; raw frozen results remain unchanged.
Candidate tiers were retrieval only in memory during evaluation; registry was never promoted.

| Course | include@5 | chapter@1 | source-bound | insufficient | Raw pass |
|---|---:|---:|---:|---:|---|
| ke-toan-chi-phi | 0.900 | 0.800 | 1.000 | 1.000 | False |
| ke-toan-ngan-hang | 1.000 | 0.833 | 1.000 | 1.000 | True |
| ke-toan-tai-chinh-2 | 1.000 | 0.900 | 1.000 | 1.000 | True |
| kiem-toan-1 | 1.000 | 1.000 | 1.000 | 1.000 | True |
| kinh-doanh-va-nghiep-vu | 1.000 | 0.833 | 1.000 | 1.000 | True |
| luat-kinh-doanh | 1.000 | 0.917 | 1.000 | 1.000 | True |
| ngan-hang-thuong-mai | 0.917 | 0.833 | 1.000 | 1.000 | True |
| tai-chinh-doanh-nghiep-1 | 1.000 | 0.333 | 0.667 | 1.000 | False |
| tai-chinh-hanh-chinh-su-nghiep | 1.000 | 0.750 | 0.667 | 1.000 | False |
| thi-truong-tai-chinh | 1.000 | 0.917 | 0.667 | 1.000 | True |

## Check and decision

- KTCP meets numeric gates with the approved D2 exception; raw topic_owner remains 0/3.
- KTNH meets numeric gates under D1.
- TCDN1 remains chapter@1 4/12 = 0.333 < 0.80; multi-topic summary src-0177 dominates top-1. Removing course cues alone does not resolve this.
- Existing retrieval course TCHCSN regresses from 10/12 to 9/12 = 0.75 < 0.80. This triggers the explicit D1 stop condition.
- Core regression under D1: IDENTICAL, reports/v3/run_20261011_214229.
- D1 lexical change reverted to preserve the previously verified runtime. No tiers changed. All 11 frozen V3 eval hashes unchanged.
- G4 remains blocked. Wave 5 not started; external research and refresh remain disabled.
- Needed: permission for a broader source-role/ranking diagnosis and narrowly scoped repair beyond uniform D1 cue removal. Do not change hybrid weights, frozen evals, or core behavior.
- D2 is approved, not pending. It does not waive any other failed gate.
