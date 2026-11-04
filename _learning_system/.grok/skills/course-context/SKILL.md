---
name: course-context
description: >
  Resolve which D:\Hoc course, chapter, and source family a question belongs to.
  Use when the course is unstated, filenames collide (many "Chương 1.pdf"),
  or the user runs /course-context.
---

# Course context

`Chương 1.pdf` exists in multiple courses. Never key on filename alone.

## Steps

1. If the user named a course folder or course_id, use that.
2. Else match question terms to `concept_registry.yaml` `courses` and `aliases`.
3. Else match to chapter titles in the relevant `course_manifests`.
4. If two courses remain plausible, return both with evidence; do not pick silently.
5. Load that course manifest: sources present/missing, chapter list, known vs inferred prerequisites.

## Output

```
course_id:
course_name:
evidence_status: OBSERVED | INFERRED | UNKNOWN
chapter:
topic:
competing_courses: []
missing_in_this_course: [syllabus, solutions, ...]
```
