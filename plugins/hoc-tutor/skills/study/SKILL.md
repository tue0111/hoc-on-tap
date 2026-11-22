---
name: study
description: >
  Learner-facing study entry for NLKT/KTTC1. Ask a question, submit an attempt,
  capture feedback, or request the next action. Use for ordinary studying or /study.
  Does not auto-diagnose a bare question. Not a review calendar.
---
# Study (real-use pilot)

## HOC_ROOT

`HOC_ROOT` = repo root (`_grok_pack/`, `_learning_system/`). Local Windows của Tuệ: thường `D:\Hoc`.

```
cd HOC_ROOT/_learning_system
python -m study "CÂU HỎI"
python -m study "CÂU HỎI" --attempt "BÀI LÀM"
python -m study --feedback "Tao chỉ tính nhầm."
python -m study --next --debug
python -m retrieval.cli study "CÂU HỎI"
```

Bare questions retrieve and explain. Diagnosis runs only when `--attempt` / `attempt:` provides learner work.

`--exclude` or feedback like "không muốn lần này được dùng để đánh giá" blocks long-term admission.

Normal view hides hypothesis IDs and policy internals. `--debug` shows sources, diagnosis, action, state.

Do not count `kind=instrumentation_test` as real pilot traffic.
