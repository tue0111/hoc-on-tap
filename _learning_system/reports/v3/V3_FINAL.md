# V3 readiness — G6 PASS (2026-10-12)

Current status: G4 PASS (A2), G5 PASS, R1 ownership blocker resolved under learner authorization, G6 PASS with explicitly approved RAM-only simulation. Nine curriculum retrieval courses are enabled, including KTCP (D2 waiver) and KTNH. Only TCDN1 remains catalog. Core regression IDENTICAL; all 12 frozen V3 suites unchanged. PAUSE; Wave 7 not started. See `R1_CONTINUATION.md` and `G6.md`; previous STOP/pending statements below are historical.

| Course | Tier | Sources | Pages/slides | Characters | Chunks | Concepts | Gate |
|---|---|---:|---:|---:|---:|---:|---|
| ke-toan-tai-chinh-2 | retrieval | 34 | 349 | 662767 | 464 | 33 | G1 pass |
| ke-toan-chi-phi | retrieval | 45 | 405 | 685189 | 362 | 30 | R1 pass, D2 waiver |
| kiem-toan-1 | retrieval | 33 | 368 | 642218 | 358 | 40 | G2b pass |
| ke-toan-ngan-hang | retrieval | 54 | 630 | 1073853 | 959 | 30 | R1 pass |
| kinh-doanh-va-nghiep-vu | retrieval | 36 | 225 | 436837 | 521 | 25 | G3a pass |
| luat-kinh-doanh | retrieval | 17 | 95 | 142860 | 177 | 18 | G3b pass |
| tai-chinh-doanh-nghiep-1 | catalog | 24 | 653 | 797548 | 392 | 29 | G3c fail |
| ngan-hang-thuong-mai | retrieval | 20 | 986 | 692683 | 357 | 23 | G3d pass |
| thi-truong-tai-chinh | retrieval | 14 | 318 | 167990 | 196 | 27 | G3e pass |
| tai-chinh-hanh-chinh-su-nghiep | retrieval | 14 | 1191 | 888967 | 768 | 26 | G3f pass |
| learner-notes | retrieval | 14 | 132 | 276921 | 307 | 0 | G3g pass |

## Evaluation metrics

Latest R1 metrics supersede the three historical entries below: KTCP include=0.90,
chapter=0.80, source-bound=1.00 (D2 waiver); KTNH include=1.00, chapter=0.8333,
source-bound=1.00; TCDN1 include=0.9167, chapter=0.5833, source-bound=0.6667.
Raw reports: `<course>_eval_r1_final.json`; KTCP adjusted gate: `ktcp_r1_final_d2.json`.
The earlier per-course metrics below are preserved as the pre-R1 historical snapshot.

- ke-toan-tai-chinh-2: `{"direct_must_include": 1.0, "direct_chapter_at1": 0.9, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": 1.0, "topic_owner": 1.0}`; `reports/v3/ke-toan-tai-chinh-2_eval_g3x_fixed.json`.
- ke-toan-chi-phi: `{"direct_must_include": 0.9, "direct_chapter_at1": 0.7, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": 1.0, "topic_owner": 0.0}`; `reports/v3/ke-toan-chi-phi_eval_run3.json`.
- kiem-toan-1: `{"direct_must_include": 1.0, "direct_chapter_at1": 1.0, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": null, "topic_owner": null}`; `reports/v3/kiem-toan-1_eval_g3x_fixed.json`.
- ke-toan-ngan-hang: `{"direct_must_include": 0.9166666666666666, "direct_chapter_at1": 0.75, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": 1.0, "topic_owner": null}`; `reports/v3/ke-toan-ngan-hang_eval_run3.json`.
- kinh-doanh-va-nghiep-vu: `{"direct_must_include": 1.0, "direct_chapter_at1": 1.0, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": null, "topic_owner": null}`; `reports/v3/kinh-doanh-va-nghiep-vu_eval_g3x_fixed.json`.
- luat-kinh-doanh: `{"direct_must_include": 1.0, "direct_chapter_at1": 0.9166666666666666, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": null, "topic_owner": null}`; `reports/v3/luat-kinh-doanh_eval_g3x_fixed.json`.
- tai-chinh-doanh-nghiep-1: `{"direct_must_include": 0.9166666666666666, "direct_chapter_at1": 0.3333333333333333, "source_bound": 0.6666666666666666, "insufficient": 1.0, "collision_contamination": 0, "account": null, "topic_owner": null}`; `reports/v3/tai-chinh-doanh-nghiep-1_eval_run3.json`.
- ngan-hang-thuong-mai: `{"direct_must_include": 0.9166666666666666, "direct_chapter_at1": 0.8333333333333334, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": null, "topic_owner": null}`; `reports/v3/ngan-hang-thuong-mai_eval_g3x_fixed.json`.
- thi-truong-tai-chinh: `{"direct_must_include": 1.0, "direct_chapter_at1": 1.0, "source_bound": 1.0, "insufficient": 1.0, "collision_contamination": 0, "account": null, "topic_owner": null}`; `reports/v3/thi-truong-tai-chinh_eval_g3x_fixed.json`.
- tai-chinh-hanh-chinh-su-nghiep: `{"direct_must_include": 1.0, "direct_chapter_at1": 0.8333333333333334, "source_bound": 0.6666666666666666, "insufficient": 1.0, "collision_contamination": 0, "account": null, "topic_owner": null}`; `reports/v3/tai-chinh-hanh-chinh-su-nghiep_eval_g3x_fixed.json`.
- learner-notes: `{"top3": 1.0, "implicit_routing": 1.0, "coverage_contract": 1.0, "unknowns_contract": 1.0, "metadata_contract": 1.0, "explicit_route": 1.0}`; `reports/v3/learner-notes_eval_g3x_fixed.json`.

Aggregate gate pass is not a claim that every individual row passes. Core remains NLKT + KTTC1, index 2.0.0, 810 chunks. Real Grok bot acceptance by the learner has not been performed.

## Open items

- TCDN1: metadata repair gives chapter@1 0.5833<0.80; remains catalog after two R1 rounds. No silent source demotion or chunking change.
- KTCP: D2 waiver applies only to kp-t01..03; raw results retained, no frozen eval edited. KTCP/KTNH lexical knob and ownership fix are verified.
- KTTC2 course code, NHTM law vintage, TCDN1 exam duration conflicts remain unresolved.
- External layer enabled; 62 status records remain unknown. Manual refresh enabled after approved in-memory G6; real new-source disk publication and human bot acceptance are not yet demonstrated.
- Final core regression: `run_20261012_074136/diff.txt` IDENTICAL. Core source integrity OK 40/40; see G6.md.

## Learner-material list — confirmation pending

- src-0040: Kiểm toán 1/Thảo luận 1/Đạo Đức Nghề Kiểm Toán.pdf (7 pages/slides, 17622 characters).
- src-0041: Kiểm toán 1/Thảo luận 2/Han_Che_Kiem_Soat_Noi_Bo_Gian_Lan_BCTC.pdf (4 pages/slides, 11926 characters).
- src-0046: Kế toán chi phí/Thảo luận 1/Phân Loại Chi Phí Doanh Nghiệp.pdf (15 pages/slides, 23223 characters).
- src-0139: Ngân hàng thương mại/SO_TAY_THI_MO_NHTM.docx (13 pages/slides, 36288 characters).
- src-0140: Ngân hàng thương mại/SO_TAY_THI_MO_NHTM.pdf (17 pages/slides, 35337 characters).
- src-0165: Tài chính doanh nghiệp 1/Corporate_Finance_Blueprint.pptx (14 pages/slides, 0 characters).
- src-0173: Tài chính doanh nghiệp 1/SO_TAY_THI_MO_TCDN1.docx (18 pages/slides, 51792 characters).
- src-0174: Tài chính doanh nghiệp 1/SO_TAY_THI_MO_TCDN1.pdf (25 pages/slides, 50066 characters).
- src-0334: Kế toán chi phí/NguyenDucTue_BKTC6_trinh_bay.docx (1 pages/slides, 2336 characters).
- src-0335: Kế toán chi phí/NguyenDucTue_BKTC6.docx (1 pages/slides, 2216 characters).
- src-0336: Kế toán chi phí/NguyenDucTue_BKTC6.pdf (2 pages/slides, 1993 characters).
- src-0337: Kế toán chi phí/Claude outputs/Nguyễn Đức Tuệ_Thaoluanchude03_KTCP.docx (5 pages/slides, 14790 characters).
- src-0338: Kế toán chi phí/Claude outputs/Nguyễn Đức Tuệ_Thaoluanchude03_KTCP.pdf (5 pages/slides, 14660 characters).
- src-0339: Kế toán chi phí/Claude outputs/Thaoluan_chude3_DANG_DIEN_DAN.txt (5 pages/slides, 14672 characters).

Image-only src-0165: 14 slides, zero extracted characters, no indexed text. No OCR or visual-content validation claimed. All learner material stays separate from curriculum.

## D1/D2 update

Learner approved D1 and the three-row D2 waiver. D1 trial caused a TCHCSN gate regression and did not repair TCDN1; it was reverted. No tiers changed. D2 is no longer awaiting approval. G4 still blocked; see `reports/v3/D1_rerun.md`.

G4 PASS under Amendment A2.1; KTCP, KTNH, TCDN1 remain catalog (open items R1). Earlier G4 BLOCKED statements are historical and superseded. Wave 5 proceeds before R1.

## Wave 5 external status plane

G5 PASS: 5/5 frozen external tests; candidate core regression IDENTICAL. Final enabled-runtime verification is recorded in G5.md.
67 harvested citation forms (including incomplete regex candidates) map to 69 records including two required research leads: 7 checked statuses, 62 unknown. Unknown is not a legal conclusion and is not indexed as positive evidence.
23 isolated external chunks: checked status summaries plus one official 7-page PDF (14,659 extracted characters). Ten TT99 PDF segments could not be downloaded because the CDN certificate chain failed verification; security checks were not disabled. TT99 replacement scope is supported by official Ministry/Official Gazette pages, not a claim to have indexed its full text.
All search attempts are in research/search_logs; records in research/regulations; downloads and hashes in research/source_downloads.json.
Routing keeps explicit course filters, learner notes and named core curriculum scope ahead of external keyword detection to preserve frozen core questions (including IFRS asked within NLKT). Use --course external to request an external-only answer. Notes are appended only for instruments actually cited by retrieved curriculum chunks.
R1 is pending after the G5 pause; KTCP, KTNH and TCDN1 remain catalog. No Wave 6/7 work. Grok bot live acceptance remains unverified.
