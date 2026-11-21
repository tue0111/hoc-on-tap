# Personal accounting & finance learning system

## Wave 6 — nạp file mới (thủ công)

Dán `V3_KICKOFF_PROMPT.md` và nhắn **"chạy Wave 6 refresh"**. Hoặc từ thư mục hệ thống:

```powershell
python scripts/v3_refresh.py --plan
python scripts/v3_refresh.py --apply
```

`--plan` lập danh sách NEW / CHANGED / MISSING và lưu bản sao có hash trong `work/refresh/`.
`--apply` mặc định dùng kế hoạch mới nhất; có thể chỉ định đường dẫn `plan.json`.
Không có thay đổi thì không xây lại index. MISSING hoặc thay đổi nguồn lõi sẽ dừng;
không xóa nguồn cũ. CHANGED tạo source_id mới có `supersedes`, giữ nguyên lịch sử.
Tài liệu cá nhân được tách riêng. Nội dung mới cần duyệt khái niệm và trích dẫn
trước khi công bố; xem `review_required.json` trong thư mục kế hoạch, không tự ghi
`concepts_reviewed`/`citations_reviewed` khi chưa kiểm tra.

Refresh dựng ứng viên riêng, kiểm tra rồi mới công bố; bản sao trước công bố được giữ lại.
Không chạy đồng thời với phiên học đang ghi dữ liệu. Quét thông thường so theo đường dẫn
và kích thước, **không phát hiện sửa nội dung cùng kích thước ở nguồn ngoài lõi**;
nguồn lõi được kiểm tra thêm bằng hash. Không có tác vụ theo lịch/chạy nền được tạo.
Kiểm thử G6 dùng bộ nhớ theo phê duyệt người học; chưa có lần nạp nguồn mới thật trên đĩa.

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
| C External | `research/` | Enabled since G5: official-source status records (`research/regulations/`), separate `external` partition; never overwrites A |

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

## V3 course tiers

| Tier | Courses | Behavior |
|---|---|---|
| `core` | nguyen-ly-ke-toan, ke-toan-tai-chinh-1 | Unchanged v8 loop: retrieve → diagnose → decide → adapt → admit → state → policy. Index 2.0.0. |
| `retrieval` | each course that passed its gate | Teach / source lookup / attempt-checking against evidence. No diagnosis, no admission, no state. Own partition index 3.0.0. |
| `catalog` | not yet ingested | Retrieval returns `insufficient` + `course_not_indexed`. |

Current runtime clarification: catalog also includes candidate indexes that failed a gate; these are not served. Thirteen curriculum courses are retrieval-enabled (nine from Waves 1-3 incl. KTCP with D2 waiver and KTNH, plus HTTTKT1, Kế toán thuế 1, KTTC3 and KTHCSN from W6b); only TCDN1 remains catalog after R1. learner-notes is non-curriculum. External updates are enabled after G5 (31 checked status records, 100 unknown after W6b); manual refresh is enabled after G6 (approved RAM-only simulation). Full-loop diagnostic/admission/state instructions apply to CORE only.

From `D:\Hoc\_learning_system`:
```powershell
python -m retrieval.cli retrieve "QUESTION" --course <id>
```

See `curriculum/course_registry.yaml` and `reports/v3/V3_FINAL.md` for current readiness. Pilot real-traffic requirements still apply to full-loop expansion, not authorized curriculum ingestion.

## Wave 5 external status plane

G5 PASS: 5/5 frozen external tests; candidate core regression IDENTICAL. Final enabled-runtime verification is recorded in G5.md.
67 harvested citation forms (including incomplete regex candidates) map to 69 records including two required research leads: 7 checked statuses, 62 unknown. Unknown is not a legal conclusion and is not indexed as positive evidence.
23 isolated external chunks: checked status summaries plus one official 7-page PDF (14,659 extracted characters). Ten TT99 PDF segments could not be downloaded because the CDN certificate chain failed verification; security checks were not disabled. TT99 replacement scope is supported by official Ministry/Official Gazette pages, not a claim to have indexed its full text.
All search attempts are in research/search_logs; records in research/regulations; downloads and hashes in research/source_downloads.json.
Routing keeps explicit course filters, learner notes and named core curriculum scope ahead of external keyword detection to preserve frozen core questions (including IFRS asked within NLKT). Use --course external to request an external-only answer. Notes are appended only for instruments actually cited by retrieved curriculum chunks.
R1 continuation: KTCP/KTNH enabled; TCDN1 remains catalog. G6 uses the learner-approved RAM simulation. Wave 7 was not started. Grok bot live acceptance remains unverified.
