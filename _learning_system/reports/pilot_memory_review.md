# Pilot memory review

- Admission engine unchanged (policy 1.0.0). Uncertain → HOLD.
- `--exclude` / “không muốn lần này được dùng để đánh giá” sets `exclude_from_long_term_evidence` and skips persist.
- Instrumentation tests used `persist_memory=False`.
- `learner/evidence/admitted.jsonl` was not used as a success metric.
- Derived state remains recomputable from admitted rows only.
