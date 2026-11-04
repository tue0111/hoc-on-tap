# Phase 3 recommendation

## Decision: PASS

Phase 2 retrieval on NLKT → KTTC1 meets the hard gates and the success conditions A–G.

Ready for **Phase 3: Diagnostic vertical slice** on the same two courses only.

## Do

- Use this EvidencePackage runtime as the only curriculum memory for diagnostics.
- Start with KTTC1 đề mẫu items + NLKT in-script exercises.
- Classify errors with `learner/error_taxonomy.yaml` against retrieved theory + official answers when present.
- Keep mastery empty until a real attempt log exists.

## Do not

- Open a Research Agent.
- Fan out to the other 10 courses until diagnostics work on this slice.
- Create more persistent agents.
- Treat the 2 remaining ranking/concept-tag misses as a reason to redesign the stack.

If Phase 3 needs better C5 sổ-sách ranking or Ch1 BCTC tagging, fix those as retrieval bugs inside this slice — not as a new ontology.
