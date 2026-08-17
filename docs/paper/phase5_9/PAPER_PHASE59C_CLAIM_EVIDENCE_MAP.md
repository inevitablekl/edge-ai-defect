# Paper Phase 5.9C Claim–Evidence Map

Only `T1 DIRECTLY_SUPPORTED` and `T2 DERIVABLE_WITHOUT_NEW_EXPERIMENT` claims are admitted to the reconstructed manuscript. Literature claims remain attributed context and are not used as evidence for the paper's central findings.

| Claim ID | Manuscript claim | Class | Frozen authority | Allowed interpretation | Explicit exclusion | Location |
|---|---|---|---|---|---|---|
| C59-PATH | `P=(R,F,M,E)` describes each tested input path | T2 DERIVABLE_WITHOUT_NEW_EXPERIMENT | Current implementation contract; Phase 5.9B blueprint | Experiment-specific structural abstraction | New or universal data-path theory | 1.2, Table 1, Fig. 1, Section 2 |
| C59-HIERARCHY | `P0→P2` changes multiple path attributes; `P2→P3` changes only `M` | T2 DERIVABLE_WITHOUT_NEW_EXPERIMENT | Frozen V0/V2R/V3R implementation identity | Hierarchical controlled-variable scope | Benefit ordering, Amdahl coverage, mechanism proof | 1.3, Fig. 1, 4.2–4.3 |
| C59-PAYLOAD | Nominal payloads are 4.9152 and 0.1200 MB/frame, with a 40.96× contrast | T2 DERIVABLE_WITHOUT_NEW_EXPERIMENT | `phase56b_nominal_payload.json`; representation geometry | Derived representation property | Measured traffic, bandwidth, H2D speedup, causal attribution | 1.2, Table 1, 4.2 |
| C59-BOUNDARY | E2E is measured from immediately before source-frame acquisition to after result construction and before sink serialization/write | T2 DERIVABLE_WITHOUT_NEW_EXPERIMENT | Frozen timing-boundary contract | Complete path response definition | Independently measured stage sum | 1.1, 1.3, 3.3 |
| C59-CORRECT | Three paths have equal aggregate task metrics and zero maximum classwise AP50/Recall difference under the frozen evaluator | T1 DIRECTLY_SUPPORTED | `phase56b_correctness_table_source.csv`; governed evaluator records | Correctness-constrained comparison on the frozen workload | Bitwise identity or future-input equivalence | 1.3, 2.4, 4.1, Table 3 |
| C59-PATH-RESP | V0→V2R yields 2.236671× raw FPS ratio (2.24× publication) and −55.4519% mean latency (−55.45% publication) | T1 DIRECTLY_SUPPORTED | `phase56b_publication_display_values.json`; `phase56b_run_level_metrics.csv` | Complete-path response under tested conditions | Component contribution or universal superiority | 4.2, Fig. 2, Conclusion |
| C59-POLICY-RESP | V2R→V3R yields +4.0738% FPS and −4.0349% mean latency (+4.07%, −4.03% publication) | T1 DIRECTLY_SUPPORTED | Same frozen performance authorities | Limited average incremental response in tested system | Universal pinned-memory benefit | 4.3, Fig. 2, Conclusion |
| C59-TAIL | V2R→V3R P95 is +0.1514% and P99 is −0.1184%; directions are opposite | T1 DIRECTLY_SUPPORTED | Same frozen performance authorities | No consistent same-direction tail improvement | Stability, significance, or unchanged-distribution claim | 4.4, Fig. 3, Conclusion |
| C59-BOUND | Findings are bounded to one Jetson, detector/Engine, workload, offline replay, and descriptive five-process protocol | T2 DERIVABLE_WITHOUT_NEW_EXPERIMENT | Frozen platform and experiment protocol | Scope qualification | Cross-platform, cross-model, cross-dataset generalization | 3, 4.5, Conclusion |

No T3/T4 claim is admitted as a manuscript contribution or result. No new measurement was performed in Phase 5.9C.
