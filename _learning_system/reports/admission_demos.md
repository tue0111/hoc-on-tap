# Phase 6 admission demonstrations

Ten live `decide_admission` traces. Scope is always `OBSERVATION_ONLY`.

1. **One mistake → HOLD** (`adm-oneoff-01`)  
   Observation: selected expense where inventory was required.  
   `HOLD` `INSUFFICIENT_REPETITION` `TEMPORARY_CONTEXT`. Not a stored weakness.

2. **Repeated independent mistake → ADMIT** (`adm-repind-01`)  
   Second session, different credit-purchase task, same mechanism.  
   `ADMIT` `REPEATED_INDEPENDENT_EVIDENCE` `CURRICULUM_GROUNDED` HIGH.

3. **Same-task retries → not independent** (`adm-retry-01`)  
   `REJECT` `SAME_TASK_RETRY`.

4. **Strong transfer success → ADMIT positive** (`adm-pos-01`)  
   Independent merchandising-vs-service classification.  
   `ADMIT` `POSITIVE_INDEPENDENT_EVIDENCE` `TRANSFER_EVIDENCE`.

5. **“Em hiểu rồi” → not admitted** (`adm-self-01`)  
   `REJECT` `SELF_REPORT_ONLY`.

6. **Correct after full hint → not independent positive** (`adm-hint-01`)  
   `REJECT` `HINT_CONTAMINATED`.

7. **Correct number / wrong reason → split** (`adm-cawr-01`)  
   50×10=500 with FIFO described as newest lot. Conceptual observation `ADMIT` `SPLIT_DIMENSIONS` `STRONG_DIRECT_EVIDENCE`. Not flattened to “correct.”

8. **Later contradictory success → preserve both** (`adm-contra-01`)  
   New independent correct `ADMIT` with `CONTRADICTORY_EVIDENCE` linking the earlier incorrect candidate. No overwrite.

9. **Duplicate lineage → deduplicate** (`adm-dup-01`)  
   Same session/task/diag lineage. `REJECT` `DUPLICATE_EVIDENCE` `duplicate_of: c-dup-orig-01`.

10. **Mechanical typo → reject as conceptual evidence** (`natadm-typo-01`)  
    165 vs 156 digit slip. `REJECT` `MECHANICAL_ONLY`.
