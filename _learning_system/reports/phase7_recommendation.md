# Phase 7 recommendation (not started)

Phase 6 admits observations. Do **not** automatically implement mastery scoring.

## Recommended next step (one)

**Read-only mastery *estimate* from admitted evidence, per concept × dimension, nullable until enough observations exist.**

- Input: `learner/evidence/admitted.jsonl` only
- Output: nullable recall/conceptual/procedural/application/transfer — never 0/1 defaults
- Contradictory observations remain visible; do not average into a fake 50%
- HOLD/REJECT never enter the estimate
- Still no SRS, no calendar, no “weak student” label

## Explicitly not next

- Forgetting curves / spaced repetition
- Web/IFRS research agent
- Expanding production retrieval beyond NLKT + KTTC1
- Silent edits of admitted rows
