# Paper Phase 5.4A Theory and Narrative Reconstruction v1.0

## 1. Verdict

`THEORY_NARRATIVE_RECONSTRUCTION_COMPLETE`

## 2. Starting state

- Branch: `main`
- Starting HEAD: `f2dc0fd8bc69a91032687170661275e050910bd3`
- Starting subject: `docs(paper): finalize adaptive equation spacing`
- Worktree/index: clean
- Frozen plan: `PAPER_PHASE5_SUPERVISOR_REVISION_PLAN_v1.0.md`

## 3. Supervisor feedback addressed

The revision responds to the need to move the manuscript from an implementation-and-benchmark report toward a theory-guided deployment/data-path optimization paper. It makes the research problem, E2E execution object, optimization-coverage idea, controlled intervention hierarchy, benchmark contract, and result-interpretation boundaries explicit without changing scientific evidence.

## 4. Files changed

Authorized manuscript sources:

- `docs/paper/manuscript/sections/01_introduction.md`
- `docs/paper/manuscript/sections/02_problem_definition.md`
- `docs/paper/manuscript/sections/03_method.md`
- `docs/paper/manuscript/sections/04_experiment.md`
- `docs/paper/manuscript/sections/05_results.md`

Governance assets:

- `docs/paper/phase5/PAPER_PHASE5_SUPERVISOR_REVISION_PLAN_v1.0.md`
- `docs/paper/phase5/PAPER_PHASE5_4A_CITATION_NEEDS_v1.0.md`
- `docs/paper/phase5/PAPER_PHASE5_4A_VISUAL_NEEDS_v1.0.md`
- `docs/paper/phase5/PAPER_PHASE5_4A_THEORY_NARRATIVE_RECONSTRUCTION_v1.0.md`

`00_title_abstract.md`, `06_conclusion.md`, references, figures, tables, source code, historical reports, and generated publication assets were not modified as tracked sources.

## 5. Before/after narrative architecture

Before:

`industrial motivation → three implementations → benchmark protocol → numeric comparison → bounded conclusion`

After:

`industrial problem → fixed detector and INT8 execution object → complete E2E path → optimization coverage → broader V0→V2R and narrower V2R→V3R controlled interventions → fixed correctness/timing contract → average and tail observations → bounded engineering implications`

The theory layer remains an explanatory framework for the existing controlled comparison. It is not presented as a new algorithm, a fitted predictive model, or a third contribution.

## 6. Section 0 changes — Introduction

- Shortened the industrial-defect opening and made the contrast with architecture-focused defect detection explicit.
- Stated that the paper is not another improved-YOLO study.
- Brought runtime, preprocessing, staging/data movement, inference/synchronization, postprocessing, and result construction into the E2E motivation.
- Explained why fixed INT8 model computation does not automatically optimize non-network path components.
- Sharpened the research gap around a fixed detector, TensorRT INT8 Engine, workload, correctness contract, and timing boundary.
- Introduced the broader V0→V2R and narrower V2R→V3R intervention hierarchy plus mean/tail evaluation.
- Preserved exactly two contributions and included all six frozen central results.
- Preserved established first-citation order so the frozen numbered bibliography remains valid.

## 7. Section 1 changes — System object and problem definition

- Retained the model, dataset, platform, frozen Engine, fixed test-set, no-retraining, and TensorRT 10.3 historical/deprecated-interface facts.
- Distinguished network/model execution from the complete deployment execution path.
- Defined V0, V2R, and V3R as controlled system variants.
- Defined V0→V2R as a broader path intervention and V2R→V3R as a narrower host-staging intervention, explicitly not a causal decomposition.
- Added Section 1.3 for the E2E conceptual model and optimization coverage.
- Renumbered the timing-boundary/research-question content to Section 1.4 without changing timing semantics or protocol.

## 8. Section 2 changes — Method

- Reframed V0 as a controlled CPU/OpenCV baseline, not a globally inefficient design.
- Connected V2R implementation facts to its broader path scope while denying stage-level gain attribution.
- Connected V3R to the narrower intervention: CUDA preprocessing semantics, model, Engine, postprocessing, and topology remain fixed; only raw-image host-staging allocation changes.
- Reaffirmed that pinned memory is an experimental variable, not a guaranteed optimization, and that V3R contains no zero-copy, double buffering, explicit transfer/compute overlap, multi-inference-stream execution, or cross-frame pipeline.
- Strengthened the rule that correctness/semantic validation precedes performance attribution and retained V3R's companion-identity boundary.

## 9. Section 3 changes — Experiment methodology

- Retained platform, workload, warmup, measured-frame, replay, process-order, and metric facts.
- Reframed the section around an explicit benchmark contract: controlled object/workload, correctness admission, timing boundary, and aggregation rules.
- Emphasized five independent processes per variant, `60` warmup frames, `1080` measured frames per run, fixed `180`-image test replayed six times, and `5400` pooled per-frame latency samples per variant.
- Preserved the distinction between process-wall FPS aggregation and source-to-pre-sink per-frame latency aggregation.
- Preserved all five experiment display equations, Type-7 percentile semantics, sample-SD meaning, and the absence of confidence intervals or significance inference.
- Stated only the broader benchmark principle; no MLPerf compliance claim was added.

## 10. Section 4 changes — Results and discussion

- Made correctness an explicit prerequisite for later path-performance attribution without upgrading V3R identity checks to independent task-level accuracy validation.
- Reorganized V0→V2R around theoretical scope, observed results, compatible interpretation, and evidence boundary.
- Reorganized V2R→V3R around the narrower staging intervention, limited average gain, workload dependence, and non-universality.
- Strengthened the mixed tail-latency result: P95 is higher/slower while P99 is lower/faster; average improvement does not imply consistent tail improvement.
- Declined post-hoc attribution to unmeasured cache, scheduler, runtime, DVFS, page-migration, or memory-controller effects.
- Closed with a bounded engineering implication: within the frozen configuration, prioritize optimizations that cover a larger and measurably influential portion of the complete path before narrower staging changes.

## 11. Theory formulas and boundaries

### T1 — Conceptual E2E decomposition

\[
T_{\mathrm{E2E}}
=
\sum_{k=1}^{m} T_k .
\]

- Purpose: formalize that the defined E2E interval contains multiple stage-associated contributions.
- Location: Section 1.3.
- Boundary: no \(T_k\) was independently instrumented or measured; no stage values are asserted.
- Citation need: CN-02/CN-03 for deployment-path framing.

### T2 — Controlled-path abstraction

\[
T_v
=
T_{\mathrm{common}}
+
T_{\mathrm{specific},v},
\qquad
v\in\{V0,V2R,V3R\}.
\]

- Purpose: distinguish intentionally common execution components from path-dependent portions and motivate the two intervention scopes.
- Location: Section 1.3.
- Boundary: terms were not separately timed; the abstraction is not a causal decomposition.
- Citation need: CN-02/CN-03; local implementation authority remains primary for variant mapping.

### T3 — Amdahl-type optimization coverage

\[
S_{\mathrm{E2E}}
=
\frac{1}
{(1-\alpha)+\alpha/S_{\mathrm{opt}}}.
\]

- Purpose: explain conceptually that overall benefit is constrained by the fraction of an abstract workload affected by an optimization.
- Location: Section 1.3.
- Boundary: no fitting, inverse solution, \(\alpha\) estimate, or Jetson speedup prediction; real memory, runtime, and synchronization effects are outside the simplified relation.
- Citation need: CN-04, Hill & Marty 2008 candidate.

## 12. Citation-needs summary

- CN-01: industrial-defect/improved-YOLO landscape.
- CN-02: deployment/runtime optimization independent of network architecture.
- CN-03: preprocessing bottleneck and CPU/GPU preprocessing.
- CN-04: Amdahl-type optimization coverage.
- CN-05: integrated CPU/GPU memory-policy dependence.
- CN-06: GPU allocation/memory-policy workload dependence.
- CN-07: inference benchmark methodology.
- CN-08: mean versus tail/percentile methodology.
- CN-09: INT8/PTQ approximation and correctness validation.

Formal source verification and citation integration remain deferred to Phase 5.4B.

## 13. Future visual-needs summary

- VF-01: conceptual E2E data-path and optimization-scope figure.
- VF-02: implementation-validated upgrade of the current path figure.
- VF-03: FPS figure restyled with consistent variant encoding.
- VF-04: mean/P95/P99 figure restyled to emphasize mixed tail behavior.
- VT-01: controlled-path matrix covering staging, preprocessing location, preparation/data-path property, changed component, and scope.

No final visual or table was created in Phase 5.4A.

## 14. Scientific diff audit

| Category | Verdict | Audit statement |
|---|---|---|
| Numeric result | `UNCHANGED` | Every baseline numeric occurrence in the Results section is retained; no authoritative metric was recalculated. |
| Metric definition | `UNCHANGED` | FPS, pooled mean, sample SD, and Type-7 P95/P99 definitions are unchanged. |
| Experimental protocol | `UNCHANGED` | 60 warmup, 1080 measured frames, 180 images × 6 replays, five independent processes per variant, and interleaved order are preserved. |
| Correctness condition | `UNCHANGED` | All aggregate/class thresholds and V3R companion-identity semantics are preserved. |
| Comparison direction | `UNCHANGED` | V3R/V2R P95 remains higher/slower and P99 remains lower/faster. |
| Contribution | `UNCHANGED` | Count remains exactly 2; theory supports those contributions and is not Contribution 3. |
| New theoretical interpretation | `ADDED_WITH_BOUNDARY` | E2E composition, controlled-path abstraction, and optimization coverage were added only as conceptual explanation. |
| New experimental fact | `NONE` | No new measurement, experiment, significance claim, or mechanism attribution was added. |

Frozen central results confirmed:

1. V2R/V0 FPS ratio: `2.236671×`.
2. V2R/V0 mean latency reduction: `55.4519%`.
3. V3R/V2R FPS: `+4.0738%`.
4. V3R/V2R mean latency: `-4.0349%`.
5. V3R/V2R P95: `+0.1514%`, higher/slower.
6. V3R/V2R P99: `-0.1184%`, lower/faster.

Tail behavior: `MIXED`.

## 15. Validation results

### Authoritative production validation

- `scripts/paper/build_manuscript_docx.sh --build-full`: PASS.
- `scripts/paper/build_manuscript_docx.sh --build-anonymous`: PASS.
- `scripts/paper/build_manuscript_docx.sh --check`: PASS.
- Citation source validation: PASS; 15 bibliography entries, 14 cited keys, zero unresolved.
- Rendered bibliography, citation order, and reference typography: PASS.
- Static cross-references: PASS; figures F1/F2/F3 and tables T1/T2.
- Full manuscript structure/content validator: PASS.
- Anonymous identity scan, scientific-body parity, and bibliography identity: PASS.
- Journal-format mechanical validator: PASS; section columns `['1','2','1','2']`, three figures, two tables, eight formal display equations.
- ZIP package integrity: PASS for Full and Anonymous.
- `git diff --check`: PASS before report creation and required again before commit.

### Legacy-validator disposition

- `validate_manuscript_sources.py`: not applicable; it still enforces the historical Phase 2 skeleton-only state and fails on the unchanged starting manuscript, including untouched title/conclusion prose and existing citations.
- `validate_manuscript_assets.py`: not applicable; it enforces pre-publication asset/output absence and historical manifest statuses already superseded before the starting HEAD.
- `audit_hfut_format_regression.py`: content/style inspection begins but returns fixed-SHA mismatch because it is pinned to earlier generated manuscript hashes; the current journal-format validator and direct OOXML checks pass. No frozen audit hash was changed.

## 16. DOCX, equation, and rendering validation

Full DOCX:

- Pages: `11`, A4, LibreOffice rendering PASS.
- SHA256: `9a0ab769035752052217a547181b665aa605b62c485cb361b3bf5ffbba854ce7`.

Anonymous DOCX:

- Pages: `11`, A4, LibreOffice rendering PASS.
- SHA256: `9a1c212b7948b7921775b73451b15c8ec81d365a76a1114049d6cb2e935d59ce`.

Equation regression:

- Previous experiment display equations: `5/5` retained as OMML.
- New theory display equations: `3/3` represented as OMML.
- Total display equations: `8` in Full and `8` in Anonymous.
- Full/Anonymous equation semantic parity: PASS.
- Malformed plain-text TeX: NONE detected.
- Display contract: `HFUTEquation`, `320/atLeast`, `0/0`, centered, `keepLines=true` — PASS.
- Inline-math contract: `HFUTBody` direct `360/atLeast`, `0/0` — PASS.
- Ordinary body contract: `HFUTBody`, `320/exact`, `0/0` — PASS.
- LibreOffice visual inspection of the theory pages: formulas legible, centered, and unclipped.
- MathType conversion: NOT performed; deferred until content freeze.

The increase from the nine-page baseline to eleven pages is within the Phase 5.4A intermediate-draft sanity range and reflects the authorized theory/narrative additions.

## 17. Deferred reconciliation

Phase 5.4D must reconcile the unchanged title, Chinese/English abstracts, keywords, and conclusion with the accepted central-body narrative after independent review and subsequent phases. Potential reconciliation items include explicit E2E framing, broader/narrower intervention language, and consistent use of the mixed-tail conclusion. No change to `00_title_abstract.md` or `06_conclusion.md` was made here.

Other deferred operations:

- Formal new-literature citation integration: Phase 5.4B.
- Figures and tables: Phase 5.4C.
- Title/abstract/conclusion: Phase 5.4D.
- MathType: after content freeze.
- Plagiarism check: pre-submission.

## 18. Open risks

- The nine mapped citation needs require source-level verification in Phase 5.4B; current prose is deliberately conservative pending that review.
- Independent review must specifically test Amdahl misuse, causal overclaim, integrated-memory wording, contribution creep, and narrative over-packaging before Phase 5.4B is authorized.
- Final visual integration may alter pagination in Phase 5.4C and must re-run the same equation/layout checks.

## 19. Final recommendation

Return to `MAIN_AI` for independent Phase 5.4A review. Do not begin Phase 5.4B until that review accepts the theory boundaries, controlled-path narrative, numerical freeze, and contribution count.

## 20. Git state

- Commit: created after all validations and final diff audit.
- Subject: `docs(paper): reconstruct theory and narrative for supervisor revision`.
- Worktree/index: expected clean after commit.
- Pushed: `NO`.
