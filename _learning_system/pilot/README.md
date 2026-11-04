# Real-use pilot

Instrumentation only. Not synthetic learner traffic.

```
python -m study "FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?"
python -m study "FIFO KTTC1: xuất 50 từ lô 50@10. Giá xuất?" --attempt "em nhân 50 với 10 ra 600" --debug
python -m study --feedback "Tao chỉ tính nhầm."
python -m study --exclude --attempt "..." --question "..."
```

- `sessions/` `events/` `feedback/` `corrections/` are append-only JSONL
- `kind=instrumentation_test` is never counted toward the 20-session / 50-turn gate
- `failures/` holds reproducible real-failure fixtures when they exist
- Do not edit `core_freeze_manifest.json` by hand to hide a regression
