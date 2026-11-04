# Phase 2–8 regression (after pilot instrumentation)

Instrumentation added `study/` and `pilot/` only. Frozen eval JSONL and learning engines were not edited for expected outputs.

| suite | result |
|---|---|
| Phase 2 60 | hybrid 58/60, contamination 0.0 |
| Phase 3 90 | C 90/90 |
| Phase 4 130 | C 130/130; nat VERIFY_MORE 0.85 |
| Phase 5 100+16 | C 100/100, adv 16/16 |
| Phase 6 120+40+40 | C 120/120, long 40, nat 40 |
| Phase 7 150+60+50 | D 150/150, long 60, nat 50 |
| Phase 8 180+80+60+8+30 | D 180/180, closed 80, nat 60, adv 8, e2e 30 |

No material regression. Not `PILOT_INSTRUMENTATION_REGRESSION`.
