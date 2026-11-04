# Phase 2–7 regression (run at Phase 8 close)

Phase 8 added `learning_policy/` and a `retrieval.cli next` command. Frozen JSONL and prior engines were not edited for expected outputs.

| suite | result |
|---|---|
| Phase 2 60 | hybrid 58/60, contamination 0.0 |
| Phase 3 90 | C 90/90 |
| Phase 4 130 | C 130/130; nat VERIFY_MORE 0.85, false prereq 0 |
| Phase 5 100+16 | C 100/100, adv 16/16 |
| Phase 6 120+40+40 | C 120/120, long 40, nat 40, false ADMIT 0 |
| Phase 7 150+60+50 | D 150/150, long 60, nat 50 |

No material regression.
