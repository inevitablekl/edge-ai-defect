# Paper Phase 5 Supervisor Revision Plan v1.0

## 1. Status and authority

- Status: `FROZEN`
- Decision authority: Main AI frozen supervisor-revision decision
- Materialized by: Paper Phase 5.4A
- Scope: theory and narrative reconstruction of the engineering application paper

This document records the accepted plan without reinterpreting it. The revision does not redesign the project, add experiments, or introduce a new scientific contribution.

## 2. Supervisor feedback summary

The current manuscript has a valid controlled benchmark and evidence base, but its central body reads primarily as an engineering implementation and benchmark report. The revision must make the research problem, system-level explanatory framework, controlled intervention hierarchy, evidence reasoning, and journal-oriented technical narrative more explicit while retaining all frozen facts and results.

## 3. Accepted strategy

| Dimension | Frozen strategy |
|---|---|
| Formulas | Moderate increase |
| Figures/tables | Clear enhancement, deferred to Phase 5.4C |
| Narrative | Major enhancement |
| Theory | Medium-strong explanatory support |

The target narrative is a theory-guided deployment/data-path optimization paper, not an improved-detector paper and not a new algorithm paper.

## 4. Theory architecture

The central explanatory chain is: a fixed INT8 detector remains embedded in a complete E2E execution path; E2E time contains multiple stage-associated contributions; a local optimization affects only the part of the path it covers; V0→V2R is a broader controlled intervention and V2R→V3R is a narrower controlled intervention; observed average and tail behavior must be interpreted within the frozen evidence boundary.

The theory layer contains exactly three new display equations: a conceptual E2E decomposition, a controlled-path common/specific abstraction, and an Amdahl-type optimization-coverage relationship. They support the two existing contributions. They are not fitted measurement models, do not create stage-level timing evidence, and do not constitute a third contribution.

## 5. Narrative architecture

The body shall follow this reasoning sequence:

`industrial problem → fixed detector and INT8 execution object → complete E2E path → optimization coverage → controlled V0/V2R/V3R interventions → fixed correctness and timing contract → mean and tail observations → bounded engineering implications`.

The introduction states the contrast with detector-architecture research and presents exactly two contributions. Section 1 formalizes the system object, controlled paths, theory model, timing boundary, and research questions. Section 2 presents a baseline plus two intervention levels. Section 3 presents benchmark methodology rather than a procedural log. Section 4 uses theoretical expectation, observation, interpretation, and evidence boundary.

## 6. Formula strategy

- Add only T1, T2, and T3 in Phase 5.4A.
- Retain all existing experiment formulas and their definitions.
- Do not add decorative PTQ, bandwidth, roofline, queueing, memory-latency, or additional percentile formulas.
- Preserve production equation semantics and adaptive spacing: ordinary `HFUTBody` 320/exact; inline-math `HFUTBody` direct 360/atLeast; display `HFUTEquation` 320/atLeast, 0/0, centered, `keepLines=true`.
- MathType conversion is deferred until content freeze.

## 7. Figure and table strategy

Phase 5.4A records needs only. Phase 5.4C will validate and produce: an E2E path/optimization-scope figure, an upgraded implementation path figure, consistently encoded FPS and latency figures, and a controlled-path matrix. No final figure or table is created or renumbered in Phase 5.4A.

## 8. Literature strategy

Phase 5.4A writes conservative theory and creates a claim-level citation-needs map. Phase 5.4B will verify sources, integrate formal citations, and preserve the existing citation system. Phase 5.4A must not bulk-add literature, fabricate metadata or keys, or manually renumber references.

## 9. Scientific freeze

No new experiment is authorized. Numeric results, metric definitions, timing boundaries, correctness thresholds, workload, comparison directions, and the contribution count of exactly two remain unchanged. No cross-stage speedup combination, total acceleration claim, statistical significance claim, confidence interval, excluded variant, or unmeasured mechanism may be introduced.

The frozen central results are: V2R/V0 FPS ratio `2.236671×`; V2R/V0 mean-latency reduction `55.4519%`; V3R/V2R FPS `+4.0738%`; V3R/V2R mean latency `-4.0349%`; V3R/V2R P95 `+0.1514%` higher/slower; and V3R/V2R P99 `-0.1184%` lower/faster. Tail behavior is `MIXED`.

## 10. Execution order

`5.4A → independent review → 5.4B → 5.4C → 5.4D → 5.4E → second supervisor review`.

Each phase requires its own authorization. Phase 5.4A does not self-authorize Phase 5.4B.

## 11. Deferred publication operations

- MathType conversion: after content freeze.
- Plagiarism check: pre-submission.
- Title, abstract, and conclusion reconciliation: Phase 5.4D.
- Final visual assets and controlled-path table: Phase 5.4C.
