# Decision failures (Phase 4)

Tracked classes: `FALSE_PREREQUISITE_BACKFILL`, `BROAD_REVIEW_WHEN_MICRO_FIX_SUFFICIENT`, `TREATING_SYMPTOM_NOT_CAUSE`, `INTERVENTION_WITH_UNCONFIRMED_DIAGNOSIS`, `UNNECESSARY_INTERVENTION`, `wrong_action`, `wrong_primary_gap`.

## Controlled System C

**0 remaining fails** on 130 cases.

Build-time misses (fixed, not residual):

| pattern | class | fix |
|---|---|---|
| journal primary + classification secondary | TREATING_SYMPTOM_NOT_CAUSE | causal-priority `UPSTREAM_WINS` |
| unconfirmed `prerequisite_gap` | FALSE_PREREQUISITE_BACKFILL | confirmed-only guard → VERIFY_MORE |
| thin conceptual fallback vs short NLKT definitions | wrong_action / under-treat | thin-evidence only for non-structured errors; complete-claim patterns (`là`, `=`, `chỉ có`) keep real misconceptions |
| Baseline B backfill on unconfirmed | FALSE_PREREQUISITE_BACKFILL | System C only; B is the contrast |

## Naturalistic (6 action mismatches)

`nat-11`, `nat-15`, `nat-27`, `nat-30`, `nat-35`, `nat-38`: gold `VERIFY_MORE`, pred `MECHANISM_EXPLANATION`. The learner wrote a relatively complete false claim (`là`, `chuyển tiền`, `nợ là xấu`) without Phase 3 cue phrases. Phase 4 treated them as current-concept mechanism. None were NLKT backfills. None were HIGH confidence.

## Residual risks

1. Phase 3 still DIAGNOSES 75% of vague shadow items as conceptual. Phase 4 suppresses most teaching; Level 6 must not ignore that suppression.
2. Preview sentences are not executed lessons; do not treat them as content delivery.
3. Decision grounding uses DiagnosticResult sources, not a new retrieval pass. If Phase 2 later misses a chapter, decisions inherit that miss (`retrieval_failure` — do not patch retrieval to chase this benchmark).
