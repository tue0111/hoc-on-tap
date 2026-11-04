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
