# Autopilot latest

**Status:** `REAL_PILOT_READY`

**Completion level named:** CORE_COMPLETE (Phase 8). CORE_REAL_VALIDATED is **not** reached (0 real sessions).

## Detected project state

- Last validated intelligence phase: `PHASE8_PASS_CORE_LEARNING_SYSTEM_READY`
- Production scope: NLKT / ACCO1325 + KTTC1 / ACCO2310, index 2.0.0
- `autopilot/` and `pilot/` were absent; now present
- No real learner traffic

## Actions performed

1. Inspected artifacts; confirmed Phase 8 pass reports and engines
2. Verified 40 production source files against inventory sha256 → OK
3. Wrote `autopilot/state.yaml` and `pilot/core_freeze_manifest.json`
4. Built `study/` entrypoint (user vs debug, feedback, exclude, logging)
5. Built pilot JSONL sinks; instrumentation tests tagged `instrumentation_test`
6. Reran frozen Phase 2–8 suites — no material regression
7. Did **not** create fake learner sessions counted toward 20/50
8. Did **not** enable expansion, SRS, or external research

## Files/components changed

`study/*`, `pilot/*`, `autopilot/state.yaml`, `scripts/freeze_core.py`, `scripts/pilot_instrumentation_eval.py`, `retrieval/cli.py` (`study` subcommand), skills `study`, reports listed below, AGENTS.md

Learning engines (retrieve/diagnose/decide/adapt/admit/state/policy) were not semantically rewritten.

## Tests run

- Source integrity: 40/40 hash match
- Instrumentation eval: pass
- Frozen P2–P8: same gates as Phase 8 close

## Metrics

Real sessions 0 / turns 0 / high-severity 0.

## Regressions

None material.

## Open failures

Historical watchlist only (retrieval 2 residual, vague Vietnamese, FIFO wording). No real-traffic fixtures.

## Exact blocker / completion reason

Pilot harness is ready. The next gate (`REAL_PILOT_CORE_STABLE`) needs **genuine** learner behavior (≥20 meaningful sessions, ≥50 substantive turns). Fabricating that traffic is forbidden.

## Next legal action

Use `python -m study` on real NLKT/KTTC1 study. Then resume this controller. Do not expand courses until `REAL_PILOT_CORE_STABLE`.
