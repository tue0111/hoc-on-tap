# Phase 4 / Level 5 recommendation

Phase 3 (Level 4 DIAGNOSE) is ready as a session-local service. Do **not** start Level 5 automatically from this file; this is the recommended next slice if the owner chooses to continue.

## Recommended next step (one)

**DECIDE: pick the single gap to treat from a diagnostic session, still without writing long-term mastery.**

Inputs: `DiagnosticResult` + concept graph + Phase 2 EvidencePackage.  
Output: one `gap_to_treat` (current concept vs confirmed prerequisite) plus a coarse `strategy` already stubbed on `decide_hook`.  
Hard rules to keep:

- One confirmed diagnosis is not a mastery score.
- Unconfirmed `prerequisite_gap` cannot become the gap to treat.
- `INCONCLUSIVE` → verify more, do not invent a study plan.
- Production retrieval stays NLKT + KTTC1 index 2.0.0 unless a documented Phase 2 regression re-run accompanies any change.

## Explicitly not next

- Spaced repetition / Level 6 adaptive policy
- Research Agent / IFRS web ingest
- Expanding production retrieval to KTTC2, KTCP, KTNH, Kiểm toán 1
- Persistent Diagnostic Bot
- Promoting session state into `learner/` instance files
