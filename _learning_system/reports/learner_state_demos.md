# Phase 7 learner-state demonstrations

Live `recompute()` traces. No overall score.

1. **Insufficient remains null** (`st-ins-01`)  
   No admitted rows. Concept absent from snapshot ≡ `INSUFFICIENT_EVIDENCE`, not 0.0.

2. **Two independent successes → SUPPORTED** (`st-sup-01`)  
   Transfer CORRECT ×2. State `SUPPORTED` HIGH. Refs `s0a`, `s0b`.

3. **Two independent failures → CONCERN** (`st-con-01`)  
   Application INCORRECT ×2. `CONCERN` HIGH.

4. **Retries do not inflate** (`st-ins-retry-01`)  
   Two SAME_TASK_RETRY successes. `INSUFFICIENT_EVIDENCE` `RETRIES_DO_NOT_COUNT`.

5. **Recall supported / application concern** (`lonst-G-01`)  
   hang-ton-kho: recall `SUPPORTED`, application `CONCERN`, conceptual/procedural/transfer `INSUFFICIENT_EVIDENCE`.

6. **Concern → recovery signal** (`st-rec-01`)  
   Two independent negatives then one independent positive. `RECOVERY_SIGNAL` MEDIUM. Negative refs kept.

7. **Recovery → supported** (`st-recdone-01`)  
   Two later independent positives. `SUPPORTED` HIGH, still lists `rd0a`/`rd0b` negatives.

8. **Old positives do not decay** (`lonst-F-01`)  
   Two 2025 successes, empty later step. Remains `SUPPORTED`.

9. **Same-dimension pos+neg → MIXED** (`st-mix-01`)  
   CORRECT then INCORRECT application. `MIXED`, contradiction recorded.

10. **Later contradiction changes state, keeps history** (`lonst-E-01`)  
    SUPPORTED (2 pos) → MIXED after a new independent failure. Transition `SUPPORTED→MIXED`. Positive refs still present.
