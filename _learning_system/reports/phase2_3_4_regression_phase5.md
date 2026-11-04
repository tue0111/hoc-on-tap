# Phase 2–4 regression (run at Phase 5 close)

Phase 5 did not edit `retrieval/retrieve.py`, `diagnostic/engine.py`, `decision/engine.py`, or frozen eval JSONL for those phases.

| suite | result |
|---|---|
| Phase 2 60 retrieval | hybrid 58/60, gates pass, contamination 0 |
| Phase 3 90 diagnostic | C 90/90 |
| Phase 4 130 decision | C 130/130; naturalistic shadow unchanged (VERIFY_MORE 0.85) |

No material regression.
