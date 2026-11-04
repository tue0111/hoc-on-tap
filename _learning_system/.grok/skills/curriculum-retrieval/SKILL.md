---
name: curriculum-retrieval
description: >
  Retrieve taught accounting/finance evidence from D:\Hoc curriculum manifests
  and source files. Use when the user asks what was taught, where a concept
  appears, which chapter/source covers a topic, or /curriculum-retrieval.
---

# Curriculum retrieval

Hybrid retrieval. Do not use generic accounting knowledge as a substitute.

For NLKT (ACCO1325) and KTTC1 (ACCO2310) Phase 2 runtime:

```
python -m retrieval.cli retrieve "QUESTION" [--course ke-toan-tai-chinh-1|nguyen-ly-ke-toan] [--mode current_course|prerequisite_recovery|cross_course|source_bound] [--system hybrid]
```

CWD must be `D:\Hoc\_learning_system`. Index lives in `data/indexes/2.0.0/`.

The CLI prints an EvidencePackage-backed answer. Do not replace it with generic accounting.

## Pipeline

1. Prefer `python -m retrieval.cli retrieve` when the question is NLKT or KTTC1.
2. Otherwise: read `curriculum/curriculum_manifest.yaml` and the relevant `curriculum/course_manifests/*.yaml`.
3. Detect `concept_id` from `curriculum/concept_registry.yaml` (canonical_name + aliases).
4. Filter `curriculum/source_registry.yaml` by course_id, source_type, chapter, topic, authority_rank.
5. Open the original file under `D:\Hoc` as **read-only**, or Phase 2 normalized pages under `data/normalized/` for the slice.
6. If `include_prerequisites` is true, expand using `curriculum/concept_graph.yaml` edges only. Prerequisite hits go in `prerequisite_evidence`, not mixed into current-course evidence.
7. Return an EvidencePackage (`schemas/evidence_package.schema.json`) with layer=`curriculum`.

## Ranking

Prefer lower `authority_rank` number (1 = syllabus). Do not drop lower-authority items if they conflict; put them in `conflicts`.

## Filters that must work

course, semester (only if known), source_type, chapter, topic, concept, authority, historical/current, version.

If semester/year is UNKNOWN in the manifest, do not filter as if it were known.

## Fail closed

If no curriculum hit: say so. Do not fill from the web. Optionally note that Research Agent is out of scope for this skill.

## 3A. COURSE TIERS (v3)

- **CORE** — NLKT (ACCO1325), KTTC1 (ACCO2310). Full loop: retrieve, diagnose, decide, adapt, admit, state, next action.
- **RETRIEVAL** — courses with `tier: retrieval`. Teach and look up sources only. When the learner submits an attempt, compare it with the retrieved curriculum evidence and point out exactly where it differs ("đối chiếu giáo trình"). Do not output diagnosis labels, do not make learner-state claims, do not admit evidence.
- **CATALOG** — material exists in `D:\Hoc` but is not indexed. Say so; do not answer from model knowledge as if it were the curriculum.
- When the learner names the course, always pass it: `python -m retrieval.cli retrieve "..." --course <id>`.

Current runtime clarification: catalog also includes candidate indexes that failed a gate; these are not served. Nine curriculum courses are retrieval-enabled, including KTCP (D2 waiver) and KTNH; only TCDN1 remains catalog after R1. learner-notes is non-curriculum. External updates are enabled after G5 (7 checked status records, 62 unknown); manual refresh is enabled after G6 (approved RAM-only simulation). Full-loop diagnostic/admission/state instructions apply to CORE only.

For retrieval-tier courses, use the CLI with explicit course before the legacy manifest fallback. Learner notes are always labeled "tài liệu cá nhân của bạn, không phải giáo trình"; never curriculum evidence.
