# Retrieval architecture (Phase 2)

Slice: `nguyen-ly-ke-toan` (ACCO1325) + `ke-toan-tai-chinh-1` (ACCO2310).

## Pipeline

```
USER QUESTION
  → question analysis (intent, course_scope, mode, concepts, chapter)
  → hard metadata mask (course / chapter / source_type depending on mode)
  → hybrid rank: BM25 + TF-IDF cosine + concept overlap + metadata + authority
  → EvidencePackage.items (current course)
  → optional prerequisite_evidence (NLKT only, separate list)
  → Learning Director answer from the package
```

Not: question → vector dump → summarize.

## Modes

| Mode | Main evidence | NLKT prereq list |
|---|---|---|
| `current_course` | Named course only | empty |
| `prerequisite_recovery` | KTTC1 | NLKT concepts on graph / bookkeeping chain |
| `cross_course` | both | optional |
| `source_bound` | named course + chapter/source_type | empty |

Ambiguous questions (no course cue) do not silently pick a course.

## Signals

A. BM25 (lexical)  
B. TF-IDF cosine (numpy; no sklearn / no hosted embeddings)  
C. Metadata filter (hard mask)  
D. Course context from cues `NLKT` / `KTTC1` / `ACCO1325` / `ACCO2310`  
E. Chapter cue `chương N`  
F. Concept phrases from `concept_registry.yaml`  
G. Authority prior (syllabus 1 … exam 5; slides downranked vs scripts; exam is not theory authority)  
H. Prerequisite expansion into a **separate** array

Weights (`retrieval/config.py`): bm25 0.42, tfidf 0.22, concept 0.18, metadata 0.12, authority 0.06.

## What is indexed

Canonical topic/chapter files only. Combined concatenations are extracted for coverage then **excluded** from the default index:

- `Nguyên Lý Kế Toán.pdf` (src-0093)
- `KTTC 1.pdf` (src-0063)
- `Slide KTTC 1.pdf` (src-0068)

This prevents same-content duplication and same-filename collisions.

## Chunking

Heading / slide / page-aware packing (~900 chars target, 180–1600 bounds). Definitions are not split from the following sentence when a heading is not present.

## Runtime

```
cd D:\Hoc\_learning_system
python -m retrieval.cli retrieve "QUESTION" [--mode current_course|prerequisite_recovery|cross_course|source_bound] [--system naive|hybrid|hybrid_prereq]
python -m retrieval.cli build
python scripts\phase2_eval.py
```

## Schema migration

`schemas/evidence_package.schema.json` gained optional Phase 2 fields: `query`, `mode`, `current_course`, `coverage`, `prerequisite_evidence`, `detected_concepts`. Required `package_id` / `layer` / `items` unchanged. No curriculum YAML migration.

## Explicitly not in this runtime

Research Agent, mastery scores, Level 4 diagnostics, web/IFRS injection.
