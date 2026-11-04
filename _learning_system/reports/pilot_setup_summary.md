# Pilot setup summary

Instrumentation around the frozen Phase 8 core. No curriculum expansion. No fake learner sessions counted toward gates.

## Entrypoint

```
cd D:\Hoc\_learning_system
python -m study "CÂU HỎI"
python -m study "CÂU HỎI" --attempt "BÀI LÀM"
python -m study --feedback "Tao chỉ tính nhầm."
python -m study --next --debug
```

Bare questions retrieve/explain. Diagnosis runs only when there is learner work.

## Layout

- `study/` — session wrapper, user/debug views, feedback, integrity, freeze
- `pilot/core_freeze_manifest.json` — versions + frozen-suite hashes
- `pilot/events|sessions|feedback|corrections` — append-only JSONL
- `pilot/failures/` — empty until a real reproducible failure
- `autopilot/state.yaml`

## Freeze

Source integrity **OK** (40 NLKT+KTTC1 files vs inventory sha256). Index **2.0.0** (810 chunks). Policy 8.0.0.

## Instrumentation eval

`scripts/pilot_instrumentation_eval.py` pass. `kind=instrumentation_test` → real counters remain 0.
