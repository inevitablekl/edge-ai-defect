# Paper Phase 5.9C Reconstruction Comparison

| Dimension | Phase 5.7 manuscript | Phase 5.9C manuscript |
|---|---|---|
| Research object | A collection of V0/V2R/V3R implementation paths and optimizations | A fixed-object input data-path system described by `P=(R,F,M,E)` |
| Section 1 role | Model/platform facts, additive stage narrative, and timing scope | Conceptual center: fixed object, descriptor, derived payload, intervention hierarchy, correctness condition, measured response, RQ1/RQ2 |
| Section 2 role | Procedural implementation sequence and buffer lifecycle | Architecture and structural change first, followed by minimal reproducibility mapping |
| Figure 1 | Implementation/result overview with E2E numbers | Conceptual host/device path abstraction and hierarchical interventions; no result numbers |
| Old Figure 2 | V2R/V3R buffer, lifecycle, and single-stream implementation figure | Removed from publication after its necessary semantics were retained in Figure 1, Table 1, and Section 2 |
| Aggregate figure | Figure 3 | Figure 2; frozen statistical asset unchanged |
| Run/tail figure | Figure 4 | Figure 3; frozen statistical asset unchanged |
| Table 1 | Feature/checklist matrix | Structural-variable matrix instantiating `R`, `F`, `M`, `E` and derived `B(P)` |
| Table 4 | Related-work attribute checklist in Results | Removed; scientifically useful literature moved to the Introduction's three evidence streams |
| Results style | Reports complete-path gain, payload fact, run ranges, and a related-work checklist | Observed response → intervention relation → allowed inference → prohibited inference → bounded implication |
| Formula inventory | Additive E2E stage sum plus displayed FPS definition | Three core equations: path descriptor, derived nominal payload, and measured source-to-pre-sink boundary; FPS moved inline |
| Technical detail | API and lifecycle narration is prominent | API/lifecycle references compressed to reproducibility mappings; protocol detail moved to Table 2/Section 3 |
| Mechanism discussion | Limited distinction between joint and local path changes | Explicit separation of path-level joint reconstruction, policy-level isolated change, and mean/tail response dimensions |

## Narrative statistics

The comparison uses committed Phase 5.7/current-baseline Markdown at `7a5db56` and the Phase 5.9C candidate sources.

| Measure | Before | After | Change |
|---|---:|---:|---:|
| Introduction characters (`wc -m`) | 1324 | 2052 | +55.0% |
| Introduction scientific prose paragraphs | 4 | 7 | +3 paragraphs |
| Section 1 characters (`wc -m`) | 1564 | 2447 | +56.5% |
| Section 2 characters (`wc -m`) | 1920 | 1162 | −39.5% |
| Selected implementation/API mentions in Section 2 | 10 | 2 | −80.0% |
| Display equations | 2 | 3 | concentrated on the research object |
| Publication figures | 4 | 3 | implementation Figure 2 removed |
| Publication tables | 4 | 3 | related-work Table 4 removed |
| Rendered references | 22 | 22 | all remain claim-bearing; none kept only for count |

The measured shift is from implementation procedure toward research-object definition and mechanism-consistent interpretation; it does not add experimental evidence or strengthen causal claims.
