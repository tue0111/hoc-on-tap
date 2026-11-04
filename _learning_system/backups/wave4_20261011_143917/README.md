# Personal accounting & finance learning system

Phase 0–8 core tutor loop over the corpus in `D:\Hoc` (NLKT + KTTC1). Admitted evidence yields per-concept × per-dimension **states**. Phase 8 chooses **one** next action from that state and the current task. There is still no mastery percentage and no review calendar.

## What this is

Not a PDF chatbot. A **curriculum layer** with:

- inventory of every source file
- per-course manifests
- a conservative concept registry and graph
- schemas for learner diagnosis and future research
- one Grok agent (Learning Director) plus skills

## Layers (do not mix)

| Layer | Path | Meaning |
|---|---|---|
| A Curriculum | `curriculum/` | What the program taught |
| B Learner | `learner/` | Schema only; no scores yet |
| C External | `research/` | Schema only; must not overwrite A |

## Source policy

`D:\Hoc\<course>\**` is read-only. All generated files live here.

## Layout

```
_learning_system/
  AGENTS.md
  .grok/agents/learning-director.md
  .grok/skills/          native Grok skills
  skills/                same skills, documented tree
  agents/learning_director/
  curriculum/
    curriculum_manifest.yaml
    course_manifests/
    source_registry.yaml
    source_registry_overrides.yaml
    source_authority.yaml
    concept_registry.yaml
    concept_graph.yaml
  learner/
  research/
  schemas/
  evals/
  extracts/              text harvested from sources
  inventory/
  retrieval/             Phase 2 hybrid retrieve + Director teach/diagnose/decide
  diagnostic/            Phase 3 Level 4 engine (session-local)
  decision/              Phase 4 Level 5 one-gap decision (session-local)
  adaptive/              Phase 5 Level 6 session adaptation (not mastery)
  admission/             Phase 6 evidence admission (ADMIT/HOLD/REJECT, no scores)
  mastery/               Phase 7 derived concept×dimension state (recomputable)
  learning_policy/       Phase 8 one next action from state + current task
  study/                 learner-facing entry (pilot)
  pilot/                 real-use logs, freeze manifest
  autopilot/             controller state
  reports/
  scripts/
```

Open Grok with cwd = `D:\Hoc\_learning_system` so `.grok/skills` and `.grok/agents` load.

## Evidence labels

- **OBSERVED** — in a file or path
- **INFERRED** — reasonable, not proven
- **UNKNOWN** — not determined

## Start here

1. `reports/inventory_report.md`
2. `reports/curriculum_map.md`
3. `reports/data_quality_report.md`
4. `reports/next_steps.md`
5. `curriculum/curriculum_manifest.yaml`
