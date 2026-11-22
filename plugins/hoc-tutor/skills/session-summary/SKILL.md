---
name: session-summary
description: >
  Summarize a study session against curriculum evidence only. Use at the end of
  a tutoring session or when the user runs /session-summary.
---
# Session summary

## HOC_ROOT

`HOC_ROOT` = repo root (`_grok_pack/`, `_learning_system/`). Local Windows của Tuệ: thường `D:\Hoc`.

## Include

- course_ids and concept_ids actually touched
- sources opened (source_id)
- questions asked
- diagnostic_ids if any
- UNKNOWN items that retrieval missed
- suggested next sources (paths), not a mastery score

## Exclude

- invented strengths/weaknesses
- external news
- semester claims that manifests mark UNKNOWN
