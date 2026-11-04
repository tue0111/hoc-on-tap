---
name: prerequisite-check
description: >
  Walk evidenced prerequisite edges in the D:\Hoc concept graph. Use when the
  user asks what to learn first, whether they can skip a topic, why a later
  course depends on an earlier one, or /prerequisite-check.
---

# Prerequisite check

## Allowed edges

Only edges in `curriculum/concept_graph.yaml` with:

- `source` (source_id or relative_path)
- `edge_type`
- `confidence`
- `explicit_or_inferred`

## Rules

- `explicit` = the source states the dependency (syllabus order, “requires”, chapter sequence inside one document).
- `inferred` = filename/course naming or intra-document sequence without a stated “requires”. Keep labeled inferred.
- Course-level “Kế toán tài chính 2 after 1” is INFERRED from names unless a syllabus says so.
- Do not add Accounting-Equation → Debit/Credit unless a source in this corpus supports that chain.

## Output

```
target_concept:
path:
  - from
    to
    edge_type
    explicit_or_inferred
    confidence
    source
missing_evidence:
unknowns:
```
