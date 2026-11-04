# AMENDMENT A2 (design model, 2026-10-11): unblock G4, scoped repair for 3 courses

Status: BINDING. This amendment has the same authority as Amendment A1. The executor appends this file verbatim to the end of `V3_EXPANSION_PLAN.md` (after A1), then follows it.

## Why

G4 says "all course gates pass". That contradicts §6.9, which explicitly allows a failed course to stay `catalog` with a failure report so the build can continue. The executor (Codex) read the G4 text literally and stopped correctly. The design decision is below.

## A2.1: G4 reinterpreted (takes effect now)

**GATE G4** passes when all of these hold:
1. Frozen suites identical to baseline (`v3_regression.py` IDENTICAL).
2. **Every course has a final state:**
   - either tier `retrieval` with its gate report passing,
   - or tier `catalog` with a failure report in `reports/v3/G-<C>.md` and an escalation entry in progress.
3. Docs 4.1–4.9 are updated, and `V3_FINAL.md` lists the catalog courses under "Open items".
4. All frozen V3 eval hashes are unchanged.

From the current state (G4.md + D1_rerun.md) this is already satisfied, so **G4 = PASS (A2)**. The executor:
- updates `autopilot/v3_progress.yaml`: `gates.G4.status: pass_a2`, `resolution` of the G4 escalation = `Amendment A2.1`;
- adds a line to `reports/v3/G4.md`: "G4 PASS under Amendment A2.1; KTCP, KTNH, TCDN1 remain catalog (open items R1)";
- does **not** change any tier.

Then go to **Wave 5** according to the plan (PAUSE at the plan's gates).

## A2.2: D2 recorded

The learner has waived 3 rows kp-t01..03 (KTCP topic_owner). Raw results stay as they are. A gate calculation for KTCP **excludes these 3 rows** and must state "D2 waiver" in the report. Nothing else is waived.

## A2.3: R1, scoped repair (do after G5 PASS, before Wave 6)

Uniform D1 (strip cues for every course) is **rejected**, because it lowered TCHCSN to 0.75. Replace it with a per-course knob.

**R1a: `strip_course_cues` flag per course (KTCP, KTNH)**
- Add an optional field to the registry: `retrieval.strip_course_cues: true|false` (default `false`). This is a registry cue knob and falls within the spirit of §6.8.
- In `retrieve_partition`: only when the target course has `strip_course_cues: true`, remove that course's cue tokens from the query **for the BM25/TF-IDF lexical part only**. Concept matching, routing and the coverage/A1 computation keep the original query.
- Enable it for `ke-toan-chi-phi` and `ke-toan-ngan-hang` only.
- Every other course must have output that is **byte-identical** to before the change. Check this by diffing the `_eval_g3x_fixed.json` output of the 7 retrieval courses before and after (rank + score per row). Any difference means revert and STOP.

**R1b: TCDN1 — attach the correct chapter to chunks of the multi-chapter document (data, not ranking)**
- Cause (D1_rerun): the summary src-0177 and the chapter-0 overview win top-1, and their chapter label is wrong or null, so chapter@1 = 0.333.
- Repair: in `v3_build_partition.py`, for documents that span chapters (src-0177 and the chapter-0 overview), assign `chapter` **per chunk** based on the nearest preceding `Chương n` / `Chủ đề n.x` heading in that document's text (regex from spec 6.4). If there is no heading, set `chapter: null` and `content_role: overview`.
- Do not change hybrid weights or demote any source. Only fix metadata, rebuild the TCDN1 partition, then run the eval.
- Allowed together with R1b: mark a dup_group if the summary is ≥0.85 overlapping a chapter file (spec 7.3, with evidence).

**R1 gate for each of the 3 courses:** §6.9 thresholds (KTCP after excluding D2). At most **2 rounds** for the whole of R1.
- Pass: tier `retrieval`, update the G-<C>.md report, add the course to `retrieval_scope` in `autopilot/state.yaml`, run `freeze_core.py` again, update `V3_FINAL.md`.
- Fail: stay `catalog` and write `reports/v3/R1.md`. **This is not a STOP**, because the courses already have a final state under A2.1. Continue to Wave 6.

Core regression must be IDENTICAL after R1a and after R1b. If it is not: revert and STOP.

## A2.4: Unchanged

Frozen evals, hybrid weights, core engine, Wave 7 OPUS_ONLY, and the stop conditions in §9 (except the G4 wording above).
