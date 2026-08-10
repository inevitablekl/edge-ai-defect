# Paper Phase 5.4A Minor Theory-Boundary Remediation v1.0

## 1. Verdict

`MINOR_REMEDIATION_COMPLETE`

Independent review verdict: `PASS_WITH_MINOR_REVISIONS`.

This work unit closes Findings F1–F4 without reopening scientific results, experiments, contribution architecture, citation integration, figures/tables, title, abstract, or conclusion.

## 2. Starting state

- Branch: `main`
- Starting HEAD: `e658f77cfc755c5420c433e138bc9a274ea566c2`
- Starting subject: `docs(paper): reconstruct theory and narrative for supervisor revision`
- Worktree/index: clean

## 3. Independent-review findings

- F1 MINOR: scalar `T_common` could imply identical elapsed-time contribution across variants.
- F2 MINOR: broader/narrower structural scope was linked too closely to Amdahl `alpha`.
- F3 MINOR: the Section 1.3 heading overstated the conceptual framework as a performance model.
- F4 EDITORIAL: publication prose retained internal governance/project-management wording.

## 4. Exact corrections

### F1 — T2 decomposition

Before:

\[
T_v
=
T_{\mathrm{common}}
+
T_{\mathrm{specific},v},
\qquad
v\in\{V0,V2R,V3R\}.
\]

After:

\[
T_v
=
T_{\mathrm{shared},v}
+
T_{\mathrm{specific},v},
\qquad
v\in\{V0,V2R,V3R\}.
\]

`T_shared,v` now denotes elapsed-time contribution associated with execution components whose functional semantics and configuration are intentionally common, evaluated under variant `v`. The variant subscript explicitly prevents an assumption of numerical equality across V0/V2R/V3R. `T_specific,v` denotes the path-dependent contribution under variant `v`. Neither term was independently instrumented or measured, and no stage-level values were added.

### F2 — Amdahl boundary

The retained Amdahl-type relation is now bounded as follows:

- `alpha` is the fraction of execution workload or time actually affected in the idealized relation.
- Broader/narrower labels describe structural and configuration scope only.
- Structural scope is not a measurement or ordering of `alpha`.
- No inequality between the V0→V2R and V2R→V3R `alpha` values is asserted.
- A structurally narrow intervention may affect a dominant bottleneck.
- Structural breadth alone does not predict speedup.
- The relation states only that overall benefit depends on the actual affected fraction and improvement achieved there.
- The experiment estimates no affected-time fraction.
- The formula is not used to explain the numerical values `2.236671×` or `4.0738%`.

Sections 4.2 and 4.3 now separate structural design descriptions from observations. The V0→V2R major E2E gain and V2R→V3R limited mean increment are reported as experimental observations, not deductions from structural breadth or Amdahl `alpha`.

### F3 — Section heading

Before:

`## 1.3 端到端性能模型与优化覆盖范围`

After:

`## 1.3 端到端执行概念分解与优化覆盖关系`

The introduction roadmap was aligned to “端到端执行概念分解”; no third contribution was created.

### F4 — Publication-neutral language

The manuscript body received narrow replacements in these categories:

- internal freeze/governance language → fixed, predefined, established, or unified experimental conditions;
- `Phase 1 冻结指标 provenance` → direct manuscript percentile definition;
- `companion identity` / identity-validation wording → companion or implementation consistency validation;
- `正式证据` → experimental results;
- model/result `合同` where project-facing → input/output specification, conditions, or criteria;
- causal-sounding `归因/归属于` → observation and interpretation within the controlled comparison boundary.

The Table 1 term `冻结 TensorRT INT8 混合精度 Engine` remains because it is a scientifically meaningful fixed-object label required by the current structural contract. Surrounding prose uses publication-neutral wording.

## 5. Supporting-map amendments

- CN-04 now states that Amdahl supports only the generic coverage principle and does not establish an `alpha` ordering between V0→V2R and V2R→V3R.
- VF-01/VT-01 now forbid visually equating broader structural scope with larger `alpha` or larger speedup.
- No bibliography entry, citation key, figure, or table was added.

## 6. Files changed

- `docs/paper/manuscript/sections/01_introduction.md`
- `docs/paper/manuscript/sections/02_problem_definition.md`
- `docs/paper/manuscript/sections/03_method.md`
- `docs/paper/manuscript/sections/04_experiment.md`
- `docs/paper/manuscript/sections/05_results.md`
- `docs/paper/phase5/PAPER_PHASE5_4A_CITATION_NEEDS_v1.0.md`
- `docs/paper/phase5/PAPER_PHASE5_4A_VISUAL_NEEDS_v1.0.md`
- `docs/paper/phase5/PAPER_PHASE5_4A_MINOR_REMEDIATION_v1.0.md`

`00_title_abstract.md`, `06_conclusion.md`, bibliography, figures, tables, and build pipeline were not modified.

## 7. Scientific freeze check

| Category | Verdict |
|---|---|
| Frozen results changed | `NO` |
| Metric definitions changed | `NO` |
| Protocol changed | `NO` |
| Correctness changed | `NO` |
| Comparison direction changed | `NO` |
| Contribution count | `2` |
| Excluded evidence restored | `NO` |
| New experimental fact | `NONE` |
| Theory | `MINOR_BOUNDARY_REMEDIATION_ONLY` |

Frozen results confirmed:

1. V2R/V0 FPS ratio: `2.236671×`.
2. V2R/V0 mean latency reduction: `55.4519%`.
3. V3R/V2R FPS: `+4.0738%`.
4. V3R/V2R mean latency: `-4.0349%`.
5. V3R/V2R P95: `+0.1514%`, higher/slower.
6. V3R/V2R P99: `-0.1184%`, lower/faster.

Tail behavior remains `MIXED`.

## 8. Formula validation

- T1: retained as `T_E2E = sum T_k`.
- T2: changed only to `T_shared,v + T_specific,v` with the revised conceptual definition.
- T3: Amdahl-type relation retained unchanged.
- Display-equation total: `8` Full; `8` Anonymous.
- OMML generation: PASS.
- Full/Anonymous equation semantic parity: PASS.
- Malformed raw TeX: none detected.
- Display style: `HFUTEquation`, `320/atLeast`, `0/0`, centered, `keepLines=true` — PASS.
- Ordinary body style: `HFUTBody`, `320/exact`, `0/0` — PASS.
- MathType: not performed.

## 9. Build and validation

### Full

- Build: PASS.
- Pages: `11`, A4.
- SHA256: `d2ff847be8a55d19d329f327fdbfc6fa3b60d06ca836b7301943f06fc8c92a01`.

### Anonymous

- Build: PASS.
- Pages: `11`, A4.
- SHA256: `de32c10ce278be84c9db5cd123b8f20f67f2278432e598d279d0321b03a48f20`.

Passed checks:

- source citation validation;
- Full and Anonymous authoritative builds;
- production `--check`;
- bibliography and first-citation order;
- static cross-references;
- Full structural validation;
- Anonymous identity scan and scientific-body parity;
- journal-format mechanical validation;
- ZIP/XML integrity;
- eight-equation OMML and semantic-parity audit;
- adaptive equation-spacing audit;
- malformed-TeX scan;
- LibreOffice A4 pagination;
- frozen-result/direction/contribution scan;
- `git diff --check` before commit.

The numeric-token comparison removed only the internal label numeral in deleted wording `Phase 1`; all scientific and protocol numeric values remain present.

## 10. Recommendation

`READY_FOR_5_4B_MAIN_AI_REVIEW`

The independent-review minor findings are closed. Main AI should confirm the remediation and authorize Phase 5.4B separately; this work unit does not begin citation integration.

## 11. Git state

- Commit: created after validation.
- Subject: `docs(paper): refine theory boundaries after independent review`.
- Worktree/index: expected clean after commit.
- Pushed: `NO`.
