# GROK BUILD AUTOPILOT — PERSONAL ACCOUNTING & FINANCE LEARNING SYSTEM

**Project root:** `D:\Hoc\_learning_system`  
**Source corpus:** `D:\Hoc`  
**Mode:** Autonomous build / validate / patch / regress / gate  
**Controller version:** `1.0.0`

---

## 0. PURPOSE

This file is the root autonomous controller for the Personal Accounting & Finance Learning System.

Treat this file as the highest-level execution contract for Grok Build inside this project.

The operator should not have to manually paste phase prompts one by one.

Your job is to:

1. inspect the current project state;
2. determine what is already complete;
3. determine the next valid task;
4. execute it;
5. validate it;
6. classify failures by layer;
7. apply the smallest justified patch;
8. rerun affected tests;
9. rerun frozen regression suites;
10. continue until the current roadmap reaches a HARD STOP or COMPLETION GATE.

Do not ask for confirmation between ordinary steps.

Ask / stop only when a real blocker exists as defined in this controller.

---

# 1. AUTHORITY ORDER

When instructions conflict, use this priority:

1. current source files under `D:\Hoc`
2. current validated project artifacts
3. latest explicit correction in project reports
4. this autopilot controller
5. older phase reports
6. inferred/default accounting knowledge

Never let an older artifact override newer source evidence.

Never silently replace curriculum content with generic accounting knowledge.

---

# 2. SOURCE SAFETY

`D:\Hoc` is READ ONLY.

Never:

- rename source files;
- move source files;
- delete source files;
- overwrite source files;
- rewrite PDFs/DOCX/PPTX;
- normalize source content in place.

Generated artifacts belong under:

`D:\Hoc\_learning_system`

Before and after any operation that may touch files, verify source integrity using hashes where available.

If any source file changes unexpectedly:

STOP with:

`SOURCE_INTEGRITY_BLOCK`

---

# 3. CURRENT KNOWN BASELINE

The project has already passed the following validated stages:

Phase 0–1:
- curriculum inventory
- source registry
- manifests
- concept registry
- concept graph
- learner schemas
- error taxonomy
- Learning Director scaffold

Phase 2:
- NLKT + KTTC1 full-text vertical slice
- normalized documents
- chunks
- hybrid retrieval
- EvidencePackage
- prerequisite-aware retrieval
- frozen retrieval suite
- production index 2.0.0

Phase 3:
- session-local diagnosis
- competing hypotheses
- discriminating questions
- root-cause classification
- conservative KTTC1 → NLKT prerequisite backtrace

Phase 4:
- one smallest next learning action
- decision policy
- VERIFY_MORE safety behavior
- no mastery writes

Phase 5:
- session adaptation
- evidence events
- hypothesis revision
- diagnosis / decision transitions
- no belief lock-in
- no long-term mastery

Phase 6:
- long-term evidence admission
- ADMIT / HOLD / REJECT
- provenance
- deduplication
- hint/self-report guards
- admitted observations only
- no mastery scores

Phase 7:
- recomputable concept × dimension learner state
- dimensions:
  - recall
  - conceptual
  - procedural
  - application
  - transfer
- states:
  - INSUFFICIENT_EVIDENCE
  - TENTATIVELY_SUPPORTED
  - SUPPORTED
  - TENTATIVE_CONCERN
  - CONCERN
  - MIXED
  - RECOVERY_SIGNAL
- no numeric global mastery

Phase 8:
- longitudinal adaptive learning policy
- one next action
- task relevance
- dimension targeting
- prerequisite guard
- current diagnosis override
- no SRS
- no calendar
- no global mastery score

Known Phase 8 final status:

`PHASE8_PASS_CORE_LEARNING_SYSTEM_READY`

Validated core loop:

`retrieve → diagnose → decide → adapt → admit → recompute state → choose one next action`

Do not rebuild completed phases from scratch.

---

# 4. CORE INVARIANTS

These invariants are mandatory across all future work.

## 4.1 Curriculum truth

Curriculum evidence is authoritative for curriculum questions.

External accounting knowledge must never silently overwrite course material.

## 4.2 Evidence before learner claims

Never convert a single mistake into a durable learner trait.

## 4.3 Evidence is durable; learner state is derived

Raw admitted evidence is source of truth.

Derived learner state must remain fully recomputable.

## 4.4 Unknown is not weak

`INSUFFICIENT_EVIDENCE` must never become zero mastery or weakness.

## 4.5 Supported is not mastered

`SUPPORTED` means evidence currently supports competence in a dimension.

It is not permanent mastery.

## 4.6 Dimensions stay separate

Recall, conceptual, procedural, application, and transfer do not automatically imply each other.

## 4.7 Current strong evidence may override historical derived state

But one trivial error must not erase a strong historical pattern.

## 4.8 Prerequisite backfill is conservative

Never send the learner backward merely because a graph edge exists.

## 4.9 One-action default

Select the smallest causally relevant next action.

Do not produce broad remedial plans by default.

## 4.10 No hidden test editing

Frozen expected outputs must not be changed just to make a new implementation pass.

---

# 5. AUTOPILOT STATE

On first run, create if absent:

`autopilot/state.yaml`

Suggested fields:

```yaml
controller_version: 1.0.0
current_stage: INSPECT
current_status: RUNNING
core_version: null
active_scope:
  - ACCO1325
  - ACCO2310
last_successful_gate: PHASE8_PASS_CORE_LEARNING_SYSTEM_READY
current_task: null
patch_cycle: 0
pilot:
  meaningful_sessions: 0
  substantive_turns: 0
  high_severity_open: 0
expansion:
  enabled: false
  current_course: null
external_research:
  enabled: false
srs:
  enabled: false
blocked_reason: null
```

Update this state atomically after every meaningful step.

Do not use the state file as evidence of success.

Success must come from actual validation artifacts.

---

# 6. MASTER AUTONOMOUS LOOP

Repeat:

```text
INSPECT
  ↓
DETECT CURRENT VALIDATED STATE
  ↓
SELECT NEXT LEGAL TASK
  ↓
PLAN BRIEFLY
  ↓
EXECUTE
  ↓
VALIDATE
  ↓
PASS?
  ├─ YES → FREEZE / VERSION → SELECT NEXT TASK
  └─ NO
       ↓
     CLASSIFY FAILURE
       ↓
     MINIMAL PATCH
       ↓
     RERUN AFFECTED TESTS
       ↓
     RERUN ALL REQUIRED FROZEN REGRESSIONS
       ↓
     PASS?
       ├─ YES → CONTINUE
       └─ NO → repeat patch loop within limits
```

Do not stop after the first implementation attempt if a local, well-understood patch can fix the failure.

Do not continue forever.

---

# 7. SELF-HEALING LIMITS

For one failure family:

`max_patch_cycles = 5`

A patch cycle means:

- identify cause;
- implement one bounded patch;
- test;
- regress.

If the same failure family still does not satisfy its gate after 5 justified cycles:

STOP with:

`AUTOPILOT_PATCH_LIMIT_REACHED`

Include:

- failure family;
- attempted patches;
- current metrics;
- suspected architectural issue;
- recommended human decision.

Do not hide repeated failures by weakening tests.

---

# 8. FAILURE-LAYER DISCIPLINE

Always diagnose the layer before patching.

Possible layers:

- source
- extraction
- normalization
- metadata
- chunking
- retrieval
- concept mapping
- graph relation
- query interpretation
- terminology normalization
- diagnosis
- decision
- session adaptation
- evidence admission
- learner-state derivation
- learning policy
- pilot instrumentation
- UX
- infrastructure

Examples:

If `"lô sau cùng"` is not understood:

patch terminology/query interpretation or alias handling.

Do NOT rewrite the diagnostic engine unless evidence shows diagnosis itself is responsible.

If wrong chapter is retrieved:

patch metadata/ranking/chunking.

Do NOT replace the entire retrieval architecture.

If a single arithmetic typo triggers conceptual remediation:

patch decision/policy guard.

Do NOT rewrite learner-state architecture.

---

# 9. PATCH CONTRACT

Every accepted semantic patch must create a reproducible regression case first.

Create:

`pilot/failures/<failure_id>/`

or the equivalent project convention.

Store:

- observed input
- relevant context
- actual output
- expected behavior
- affected layer
- root cause
- patch description
- test added
- regression impact
- final result

Patch sequence:

```text
REAL OR REPRODUCIBLE FAILURE
→ FREEZE FAILURE CASE
→ IDENTIFY RESPONSIBLE LAYER
→ MINIMAL PATCH
→ RUN LOCAL TEST
→ RUN AFFECTED PHASE TESTS
→ RUN GLOBAL FROZEN REGRESSION
→ ACCEPT OR REJECT PATCH
```

Never patch first and invent the failure explanation afterward.

---

# 10. HISTORICAL REGRESSION SUITES

Treat prior validated tests as frozen dependencies.

At minimum preserve and rerun according to project reality:

- Phase 2 retrieval suite
- Phase 3 diagnostic suite
- Phase 4 decision suite
- Phase 5 adaptive suite + adversarial
- Phase 6 admission suite + longitudinal/naturalistic
- Phase 7 state suite + longitudinal/naturalistic
- Phase 8 policy suite + longitudinal/naturalistic/end-to-end

Do not hardcode counts if the actual frozen suite now contains more tests.

Read the actual current test manifests.

Historical expected outputs may only change through an explicit documented semantic migration.

---

# 11. NEXT STAGE FROM CURRENT BASELINE

Because Phase 8 already passed, the next legal task is:

`REAL-USE PILOT SETUP`

This is instrumentation, not a new intelligence phase.

Do not expand curriculum yet.

Do not create fake learner traffic.

---

# 12. REAL-USE PILOT SETUP

If a pilot harness is not yet present:

create:

```text
pilot/
  core_freeze_manifest.*
  state.*
  sessions/
  events/
  corrections/
  failures/
  feedback/
  patches/
```

Create/update reports:

```text
reports/
  pilot_setup_summary.md
  pilot_status.md
  pilot_failures.md
  pilot_corrections.md
  pilot_memory_review.md
  pilot_patch_candidates.md
```

Record frozen baseline versions:

- source corpus version/hashes
- retrieval index version
- concept registry version
- diagnostic version
- decision version
- adaptive version
- admission policy version
- state derivation version
- learning policy version
- frozen test hashes

Do not change semantic learning behavior merely to add instrumentation.

Rerun regressions after instrumentation.

If instrumentation changes semantic results:

STOP:

`PILOT_INSTRUMENTATION_REGRESSION`

---

# 13. LEARNER-FACING STUDY ENTRYPOINT

Ensure a simple real-use entrypoint exists.

Use existing conventions where possible.

Example conceptual interface:

```text
study
```

It must support natural behavior such as:

- ask a question;
- ask for an explanation;
- attempt an accounting exercise;
- provide partial work;
- give a journal entry;
- change an answer;
- use shorthand Vietnamese;
- say "không hiểu";
- request another test question.

Normal study questions must not automatically trigger interrogation.

Use diagnosis only when actual learner evidence warrants it.

---

# 14. USER VIEW VS DEBUG VIEW

Normal user-facing output should be concise and pedagogically useful.

Do not expose:

- hypothesis IDs;
- internal policy names;
- hidden scoring internals;
- EvidencePackage structure;
- state-machine jargon;

unless debug mode is explicitly requested.

Debug mode may expose:

- retrieved curriculum sources;
- current course/chapter;
- current diagnosis;
- selected action;
- admission status;
- current concept × dimension state;
- provenance references;
- transition history.

Never expose hidden chain-of-thought.

---

# 15. PILOT LOGGING

For each real substantive interaction, record append-only audit metadata.

Include:

- session_id
- turn_id
- timestamp
- course context
- task context
- learner input
- system mode
- retrieved evidence refs
- diagnosis status
- selected immediate decision
- adaptive transition if any
- admission decision if any
- state transition if any
- Phase 8 next action if any
- policy versions
- latency if practical
- learner correction if present

Do not duplicate the same learner behavior as multiple independent evidence events.

---

# 16. USER CORRECTION SIGNALS

Capture explicit user feedback such as:

- "Mày hiểu sai."
- "Không, ý tao là..."
- "Tao chỉ tính nhầm."
- "Đề này thuộc chương khác."
- "Giáo trình ghi khác."
- "Không cần quay lại NLKT."
- "Đúng rồi."
- "Giải thích khó hiểu."
- "Tao không muốn lần này được dùng để đánh giá."

Typed feedback may include:

- CORRECT
- WRONG_ANSWER
- WRONG_SOURCE
- WRONG_COURSE
- WRONG_CONCEPT
- WRONG_DIAGNOSIS
- WRONG_INTERVENTION
- OVERREACH
- UNDER_EXPLANATION
- OVER_EXPLANATION
- MISUNDERSTOOD_QUERY
- TERMINOLOGY_MISMATCH
- USEFUL
- EXCLUDE_FROM_LONG_TERM_EVIDENCE
- UNKNOWN

Do not treat all user disagreement as proof the curriculum is wrong.

Preserve disagreement for review.

---

# 17. MEMORY SAFETY DURING REAL PILOT

Real learner behavior is now involved.

Be more conservative than synthetic benchmarks.

If admission is uncertain:

`HOLD`

not:

`ADMIT`

If user explicitly requests:

"do not use this interaction to assess/remember my learning"

or equivalent:

set:

`exclude_from_long_term_evidence = true`

for the relevant interaction/session evidence.

This prevents Phase 6 admission.

Do not modify curriculum evidence.

---

# 18. KNOWN RISK WATCHLIST

Explicitly monitor:

## 18.1 Retrieval residual

Historical Phase 2 result was not perfect.

Do not assume the remaining retrieval failures are irrelevant.

Record whether they appear in real traffic.

## 18.2 Vague Vietnamese over-diagnosis

Phase 3 historically tended to overcall `conceptual_failure` on vague text.

Phase 4/5 guards reduced downstream harm.

Still track:

`false_conceptual_overcall`

## 18.3 Accounting terminology variants

Examples include FIFO wording such as:

- lô sau cùng
- lô mới nhất
- lô cuối
- hàng nhập sau
- shorthand variants

Do not special-case only these strings.

Build evidence-backed terminology normalization when real failures justify it.

## 18.4 Correct answer with wrong reasoning

Surface correctness must not suppress diagnosis if reasoning is supplied and clearly wrong.

---

# 19. REAL PILOT COUNTERS

Track only genuine real learner traffic.

Minimum recommended before expansion review:

- 20 meaningful study sessions
- 50 substantive learning turns

A meaningful study session contains actual accounting learning behavior.

A substantive turn includes one or more of:

- accounting question;
- attempted solution;
- explanation request;
- diagnostic response;
- worked step;
- classification;
- journal entry;
- meaningful correction;
- transfer/application response.

Do not count system setup or synthetic tests.

---

# 20. PILOT METRICS

Track separately:

- retrieval acceptance
- learner correction rate
- wrong-course incidents
- wrong-source incidents
- diagnostic acceptance
- false conceptual overcall
- false prerequisite backfill
- VERIFY_MORE usefulness
- intervention acceptance
- memory false admission
- disputed learner-state incidents
- next-action usefulness
- average diagnostic turns
- unnecessary-question rate
- terminology/query interpretation failures
- insufficient-evidence handling
- high-severity incidents
- patch rate over time

Do not collapse everything into one score.

---

# 21. HIGH-SEVERITY INCIDENTS

Flag HIGH severity:

- FALSE_LONG_TERM_MEMORY
- WRONG_CURRICULUM_SOURCE_PRESENTED_AS_FACT
- FALSE_PREREQUISITE_BACKFILL
- REPEATED_WRONG_DIAGNOSIS_AFTER_CORRECTION
- STATE_CORRUPTION
- PROVENANCE_LOSS
- CROSS_COURSE_CONTAMINATION
- SOURCE_INTEGRITY_CHANGE

A high-severity incident requires immediate review and a reproducible failure fixture.

Do not automatically rewrite architecture.

---

# 22. PILOT PATCH POLICY

Ordinary failure:

Do not patch from one anecdote unless it is a clear deterministic bug.

Patch may be justified by:

- reproducible deterministic failure;
- repeated real learner failures;
- high-severity incident;
- clear provenance/integrity defect.

For ordinary semantic ambiguity, prefer collecting more examples before widening behavior.

---

# 23. PILOT AUTONOMOUS PATCH LOOP

When enough evidence exists:

```text
OPEN FAILURE
→ classify layer
→ create regression fixture
→ propose minimal patch
→ patch
→ run local tests
→ run relevant phase tests
→ run global frozen regression
→ replay real failure
→ compare behavior
→ accept or rollback
```

If patch is accepted:

- version affected component;
- document migration;
- update patch log;
- never alter historical evidence silently.

---

# 24. PILOT EXIT GATE

When BOTH are true:

- real meaningful sessions >= 20
- substantive real turns >= 50

perform formal pilot review.

Return one of:

`REAL_PILOT_CORE_STABLE`

`REAL_PILOT_NEEDS_TARGETED_PATCHES`

`REAL_PILOT_REVEALS_ARCHITECTURAL_GAP`

If patches are needed and bounded:

apply targeted patches autonomously and rerun pilot review.

If architectural gap is genuine:

STOP.

Do not invent a major redesign without human approval.

---

# 25. PILOT STABILITY RULE

Pilot is considered stable only when:

- no unresolved source/provenance corruption;
- no unresolved false long-term-memory high severity issue;
- prerequisite backfill remains conservative;
- real retrieval failures are characterized;
- natural-language failure patterns are characterized;
- recent patch rate is stabilizing;
- no repeated need for broad architecture rewrites.

Synthetic 100% scores do not satisfy this gate.

---

# 26. EXPANSION ENABLEMENT

Default:

```yaml
expansion:
  enabled: false
```

After:

`REAL_PILOT_CORE_STABLE`

set internally:

```yaml
expansion:
  eligible: true
```

Do NOT automatically enable expansion if pilot is not stable.

If project policy explicitly allows autonomous expansion after a stable pilot, proceed using the rules below.

This controller DOES authorize autonomous curriculum expansion after a stable pilot unless a blocker appears.

---

# 27. CURRICULUM EXPANSION PRINCIPLE

Expand one bounded course slice at a time.

Do not ingest all remaining 333 files into production in one step.

Default evidence-backed queue from current corpus:

1. Kế toán tài chính 2
2. Kế toán chi phí
3. Kế toán ngân hàng
4. Kiểm toán 1

After these, inspect actual curriculum evidence and manifests before choosing the remaining course order.

Do not infer prerequisite order from folder names alone.

If manifests provide explicit dependency evidence, prefer that order.

---

# 28. COURSE EXPANSION WORKFLOW

For each candidate course:

```text
SELECT COURSE
→ inspect coverage
→ verify source quality
→ full extract
→ normalize
→ semantic chunking
→ concept mapping
→ graph update only with evidence
→ build course-scoped retrieval
→ create retrieval benchmark
→ create cross-course prerequisite cases where sourced
→ run benchmark
→ run all historical regression
→ integrate into production scope only if pass
```

Do not let new course ingestion degrade NLKT/KTTC1 behavior.

---

# 29. EXPANSION QUALITY GATES

For each new course require at minimum:

- source coverage documented;
- every production evidence chunk has provenance;
- course retrieval precision acceptable;
- wrong-course contamination tightly controlled;
- same-filename collisions prevented;
- source authority preserved;
- insufficient-source behavior works;
- cross-course prerequisite retrieval only when evidence supports it;
- existing frozen suites show no material regression.

Create new frozen tests before promoting a course to production.

Never promote based only on "index built successfully."

---

# 30. EXPANSION FAILURE HANDLING

If one course fails:

do not block unrelated validated courses.

Mark:

`COURSE_EXPANSION_NEEDS_PATCH`

Patch only that course pipeline/layer where possible.

Do not weaken global policies just to ingest one difficult source set.

If parse quality is the blocker:

report it.

Do not mass-OCR the entire corpus automatically.

Use targeted extraction/OCR only when justified.

---

# 31. REAL PILOT AFTER EACH MAJOR EXPANSION

After adding a materially new dependency layer, especially:

`NLKT → KTTC1 → KTTC2`

require real-use validation before declaring that expansion stable.

Synthetic evaluation is necessary but not sufficient.

Track real interactions for the new course separately.

Do not count old NLKT/KTTC1 sessions as evidence that KTTC2 works.

---

# 32. EXTERNAL RESEARCH PLANE

Default:

```yaml
external_research:
  enabled: false
```

Do not build or activate a Research Agent until:

- core pilot is stable;
- curriculum retrieval is stable across the intended internal courses;
- source/provenance boundaries are proven;
- external knowledge has a clear use case.

When eventually enabled, preserve separation:

A. curriculum knowledge  
B. learner evidence/state  
C. external/current professional knowledge

External research must never silently overwrite curriculum.

Conflict format:

`CURRICULUM_SOURCE_CONFLICT`

or:

`CURRICULUM_VS_EXTERNAL_CONFLICT`

with both sources preserved.

---

# 33. EXTERNAL SOURCE AUTHORITY

When research is eventually enabled:

prefer:

1. official standards / regulators
2. official university/course material
3. professional bodies
4. textbooks / peer-reviewed or strong technical publications
5. reputable technical references
6. community discussion

Never use community consensus to override official standards.

Store provenance, date, jurisdiction, authority, and freshness.

---

# 34. SRS / CALENDAR

Default:

```yaml
srs:
  enabled: false
```

Do not implement automatically.

The core adaptive system already chooses next actions from evidence.

Scheduling requires a separate explicit design and validation because it introduces:

- forgetting assumptions;
- time decay;
- workload tradeoffs;
- notification behavior.

Do not sneak SRS into Phase 8 policy.

---

# 35. NUMERIC MASTERY

Do not create global mastery percentages automatically.

Existing categorical concept × dimension state is the default.

A future numeric model is allowed only if:

- there is a real decision benefit;
- calibration data exists;
- uncertainty semantics are explicit;
- it improves decisions over categorical state;
- it does not create false precision.

Otherwise keep categorical states.

---

# 36. AUTOPILOT COMPLETION DEFINITION

There are multiple completion levels.

## CORE_COMPLETE

Already achieved when:

`PHASE8_PASS_CORE_LEARNING_SYSTEM_READY`

## CORE_REAL_VALIDATED

Achieved when:

`REAL_PILOT_CORE_STABLE`

## CURRENT_CURRICULUM_PRODUCTION_READY

Achieved when:

- selected intended courses in current corpus are individually validated;
- cross-course retrieval is validated;
- no material regression remains;
- each material dependency layer has at least some real-use validation.

## EXTERNAL_KNOWLEDGE_READY

Optional.

Requires external research plane enabled and validated.

The autopilot must not claim "complete" without naming which completion level was reached.

---

# 37. HARD STOPS

Stop autonomous work immediately when one of these occurs:

`SOURCE_INTEGRITY_BLOCK`

Source files unexpectedly modified.

`REAL_DATA_REQUIRED`

A gate requires genuine learner behavior and no more real traffic exists.

`MISSING_SOURCE_REQUIRED`

A required curriculum chapter/source is absent and cannot be reconstructed legitimately.

`AUTOPILOT_PATCH_LIMIT_REACHED`

Five patch cycles failed for the same failure family.

`ARCHITECTURAL_GAP_REQUIRES_APPROVAL`

Evidence suggests a major redesign rather than a bounded patch.

`SEMANTIC_MIGRATION_REQUIRES_APPROVAL`

A proposed change would invalidate established learner-state or evidence semantics.

`EXTERNAL_RESEARCH_PERMISSION_REQUIRED`

A task requires external/current knowledge while external research remains disabled.

`PILOT_INSTRUMENTATION_REGRESSION`

Instrumentation changes validated learning behavior.

`PRIOR_PHASE_REGRESSION_BLOCK`

New work materially breaks validated behavior.

Do not work around hard stops by weakening requirements.

---

# 38. DO NOT ASK UNNECESSARY QUESTIONS

If enough information exists:

proceed.

Do not ask:

"Should I continue?"
"Do you want me to run tests?"
"Should I patch this obvious deterministic bug?"

Those are part of autonomous execution.

Ask only when a HARD STOP genuinely requires human input.

---

# 39. REPORTING STYLE

During autonomous execution:

write detailed reports to files.

Keep interactive output concise.

At major checkpoints report:

- current stage;
- what changed;
- test result;
- regression status;
- next autonomous action.

Do not dump large internal logs into chat unless requested.

---

# 40. FINAL OUTPUT CONTRACT

When the autonomous run stops, return exactly one top-level status:

`AUTOPILOT_CONTINUING`

only if the environment supports continued execution in the same run.

Otherwise one of:

`REAL_PILOT_READY`

`REAL_DATA_REQUIRED`

`REAL_PILOT_CORE_STABLE`

`REAL_PILOT_NEEDS_TARGETED_PATCHES`

`REAL_PILOT_REVEALS_ARCHITECTURAL_GAP`

`COURSE_EXPANSION_NEEDS_PATCH`

`CURRENT_CURRICULUM_PRODUCTION_READY`

`SOURCE_INTEGRITY_BLOCK`

`MISSING_SOURCE_REQUIRED`

`AUTOPILOT_PATCH_LIMIT_REACHED`

`ARCHITECTURAL_GAP_REQUIRES_APPROVAL`

`SEMANTIC_MIGRATION_REQUIRES_APPROVAL`

`EXTERNAL_RESEARCH_PERMISSION_REQUIRED`

`PILOT_INSTRUMENTATION_REGRESSION`

`PRIOR_PHASE_REGRESSION_BLOCK`

For any stop status, also write/update:

`reports/autopilot_latest.md`

with:

- detected project state;
- actions performed;
- files/components changed;
- tests run;
- metrics;
- regressions;
- open failures;
- exact blocker or completion reason;
- next legal action.

---

# 41. FIRST RUN FROM CURRENT PROJECT

Given the known baseline `PHASE8_PASS_CORE_LEARNING_SYSTEM_READY`, the first run should:

1. inspect actual project artifacts and verify the claimed Phase 8 state;
2. verify source integrity;
3. create/update `autopilot/state.yaml`;
4. freeze current core versions and test hashes;
5. build real-pilot instrumentation if missing;
6. build/verify learner-facing study entrypoint;
7. build feedback/correction capture;
8. build debug views;
9. rerun all frozen regression suites;
10. do not create fake learner sessions;
11. if instrumentation passes, return:

`REAL_PILOT_READY`

12. then stop because real learner traffic is required.

Do not continue into curriculum expansion before the real pilot gate is satisfied.

---

# 42. RESUME BEHAVIOR

On every future Grok Build invocation:

1. read this file;
2. read `autopilot/state.yaml`;
3. read `reports/autopilot_latest.md` if present;
4. inspect actual filesystem/project state;
5. reconcile state file against actual artifacts;
6. never trust stale state over real validated files;
7. continue from the next legal unfinished task;
8. do not repeat already validated work unnecessarily.

If new source files were added to `D:\Hoc`:

run incremental corpus delta detection first.

Do not rebuild the entire project unless evidence requires it.

If source changes affect an indexed production course:

invalidate/rebuild only affected normalized/chunk/index artifacts and rerun all affected regressions.

---

# 43. OPERATOR COMMAND

When this controller file exists inside the project, the operator should only need to tell Grok Build:

> Read `D:\Hoc\_learning_system\GROK_BUILD_AUTOPILOT.md`, treat it as the root controller, inspect the actual project state, and execute autonomously until you reach a defined hard stop or completion gate. Do not ask for confirmation for ordinary work.

Then follow this controller.

---

# 44. FINAL PRINCIPLE

Optimize for a trustworthy learning system, not for the appearance of autonomous progress.

A correct stop is better than fabricated completion.

A conservative HOLD is better than false learner memory.

A targeted patch is better than an architecture rewrite.

Real learner evidence is more valuable than another saturated synthetic benchmark once the core is validated.
