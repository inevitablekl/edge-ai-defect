# Paper Phase 6.1 — Academic Narrative Reconstruction Report

## 1. Verdict

`PHASE_6_1_IMPLEMENTED_AWAITING_INDEPENDENT_REVIEW`

Phase 6.1 Work Unit A is implemented. The academic narrative is re-centered on
the fixed-inference-object input data path, Figure 1 has been semantically and
mechanically remediated, scientific non-regression passes, both production
DOCX variants build, both mechanical PDFs render, and the final diff contains
only authorized files.

This verdict is an implementation disposition. It is not final academic,
supervisor, HFUT-format, or submission approval.

## 2. Repository baseline

The mandated preflight was executed before any edit:

- repository root: `/home/orin/edge-ai/edge-ai-defect`;
- branch: `main`;
- initial `HEAD`: `3fa14a4e217df7f92edc1b4c8a4b509f64bbb763`;
- initial `origin/main`: `3fa14a4e217df7f92edc1b4c8a4b509f64bbb763`;
- initial worktree: clean;
- initial index: clean.

The current baseline is a legitimate post-Phase-5.9 repository state. The
recent history records theory reconstruction, supervisor packaging, review
closure, and the final metric-symbol repair. No rollback or baseline-forcing
operation was needed.

No reset, checkout, restore, clean, rebase, merge, push, tag, or amend was
performed.

## 3. Authoritative sources inspected

The following production authorities were identified and inspected:

- manuscript content authority: the seven ordered Markdown files under
  `docs/paper/manuscript/sections/`;
- manuscript source contract: `docs/paper/manuscript/README.md`;
- bibliography: `docs/paper/manuscript/references/references.bib`;
- CSL: `docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl`;
- Figure 1 semantic specification and deterministic generator:
  `docs/paper/phase5_9/visual/FIGURE1_INPUT_DATA_PATH_MODEL_SPEC.md` and
  `docs/paper/phase5_9/visual/scripts/generate_phase59c_figure1.py`;
- Figure 1 production assets: SVG, PDF, PNG, and grayscale PNG under
  `docs/paper/phase5_9/visual/production/figures/`;
- Figures 2 and 3 production authorities:
  `fig3_main_e2e_phase56.*` and `fig4_run_level_distribution_phase56.*`;
- DOCX builder: `scripts/paper/build_manuscript_docx.sh`;
- figure insertion: `scripts/paper/full_manuscript_filter.lua`;
- section/layout postprocessor:
  `scripts/paper/postprocess_full_manuscript_docx.py`;
- table and anonymity postprocessors:
  `scripts/paper/postprocess_publication_tables.py` and
  `scripts/paper/sanitize_anonymous_manuscript_docx.py`;
- active production validators: citation, reference, heading, Full,
  Anonymous, Phase 5.9C integration, and Phase 6.1 non-regression validators;
- production outputs: `draft_full.docx` and `draft_anonymous.docx`;
- mechanical render path: LibreOffice 7.3 headless DOCX-to-PDF conversion,
  with `pdfinfo`, `pdftotext`, and 150 dpi `pdftoppm` inspection renders.

The Phase 5.9C, 5.9E, 5.9F, and 5.9H reports were reconciled as historical
context. Generated files under `docs/paper/manuscript/output/` remain derived,
ignored artifacts rather than manuscript source.

## 4. Files changed

### `AUTHORIZED_MANUSCRIPT_SOURCE`

- `docs/paper/manuscript/sections/00_title_abstract.md`;
- `docs/paper/manuscript/sections/01_introduction.md`;
- `docs/paper/manuscript/sections/02_problem_definition.md`;
- `docs/paper/manuscript/sections/03_method.md`;
- `docs/paper/manuscript/sections/05_results.md`;
- `docs/paper/manuscript/sections/06_conclusion.md`.

`docs/paper/manuscript/sections/04_experiment.md` was deliberately not changed.

### `AUTHORIZED_FIGURE1_SOURCE`

- `docs/paper/phase5_9/visual/FIGURE1_INPUT_DATA_PATH_MODEL_SPEC.md`;
- `docs/paper/phase5_9/visual/scripts/generate_phase59c_figure1.py`;
- regenerated Figure 1 SVG, PDF, PNG, and grayscale PNG production assets.

### `AUTHORIZED_BUILD_LAYOUT`

- `scripts/paper/postprocess_full_manuscript_docx.py`.

### `AUTHORIZED_VALIDATION`

- `scripts/paper/validate_phase61_nonregression.py`;
- `docs/paper/phase6_1/phase6_1_scientific_nonregression.json`.

### `AUTHORIZED_PHASE_REPORT`

- this report.

No bibliography, CSL, Figure 2/3 source, raw data, benchmark result,
implementation, Engine, CUDA kernel, frozen table value, or equation meaning
was changed.

## 5. Abstract reconstruction

Both abstracts now follow the required academic sequence:

1. deployment contradiction: lower model/Engine precision does not define or
   eliminate input-formation and host-device data-path costs;
2. problem and purpose: the remaining input data path is a separate structural
   evaluation object under a fixed inference object;
3. method: four structural decisions, hierarchical controlled intervention,
   correctness admission, and separate mean/tail evaluation;
4. evidence and bounded conclusion: `2.24×`, `−55.45%`, an approximately 4%
   local mean response, and no consistent P95/P99 improvement.

API names, V0/V2R/V3R labels, TensorRT version detail, and the complete list of
six percentage changes no longer dominate either abstract. The English and
Chinese scientific meanings remain aligned.

## 6. Introduction reconstruction

The Introduction now progresses from complete E2E industrial-edge response to
the unresolved relation left after the inference object is fixed. It derives
the need to decide representation, tensor-formation location, host staging,
and execution topology before introducing the path descriptor.

The research gap is now an evaluation-object and knowledge-organization gap:
without a unified structural description, coupled path-level changes and
single-variable local refinements are easily presented as isolated tricks
under incomparable boundaries. The descriptor and controlled RQs therefore
follow from the system problem rather than appearing as post-hoc notation.

The contribution statement remains exactly two contributions and is aligned
with the bounded evaluation object and evidence.

## 7. Section 1 alignment

- Section 1.1 retains the fixed inference object and system boundary without
  material expansion and appears before Figure 1.
- Section 1.2 now explicitly derives the four structural decisions before
  `P=(R,F,M,E)`.
- `P` is explicitly not a latency predictor and remains only a descriptor for
  changed and controlled structural variables.
- `B(P)` remains a representation-derived nominal payload and is explicitly
  not measured traffic, bandwidth, H2D time, or transfer speedup.
- Section 1.3 defines hierarchy only by intervention scope:
  `P0 -> P2` changes `R/F/M` with fixed `E`; `P2 -> P3` changes only `M` with
  fixed `R/F/E`.
- Correctness remains a first-class admission gate before performance
  comparison.

## 8. Section 2 hierarchy normalization

Sections 2.1–2.3 now use the same narrative hierarchy:

`path semantics -> changed variables -> controlled variables -> implementation mapping`.

V0 is led by host tensor formation and FP32 NCHW boundary representation;
V2R is led by the `R/F/M` structural change with fixed sequential `E`; V3R is
led by the `M`-only pageable-to-pinned refinement under fixed `R/F/E` and
downstream controls. OpenCV, `cudaMemcpy2DAsync`, fused GPU preprocessing, and
`cudaHostAlloc` are subordinate implementation mappings rather than the
scientific subject.

Section 2.4 controls and correctness semantics are preserved.

## 9. Experiment preservation

Section 3 is byte-identical to the initial baseline:

`SHA256 = 20f45e645dce7f76c47aa7369e69b580ff64a6ceb8a09b5b67074d173afef5aa`.

The detector, input, Engine, FP32 input, frozen 180-image split-v2 workload,
60-frame warm-up, 1080 measured frames/process, five independent
processes/path, 5400 samples/path, 16200 total samples, unpaired runs, and
descriptive-only statistics remain unchanged. No experiment was rerun.

## 10. Results and discussion reconstruction

Sections 4.2–4.4 now explicitly separate observation, structural
interpretation, and boundary:

- 4.2 assigns the `2.24×` and `−55.45%` response only to the complete coupled
  `R/F/M` intervention with fixed `E`; the 40.96× nominal payload contrast is
  not a transfer speedup or component attribution;
- 4.3 treats `+4.07%` FPS and `−4.03%` mean E2E latency as the response of an
  `M`-only local refinement under fixed `R/F/E`, preprocessing semantics,
  Engine, stream, and downstream structure;
- 4.4 makes mean and tail response distinct dimensions and retains the exact
  P95/P99 changes and descriptive-only boundary;
- 4.5 adds the bounded positive principle that path-level structural choices
  should be separated from local staging policies and that mean response must
  not replace tail-response evaluation.

No bottleneck, bandwidth, stage-attribution, stability, significance, or
generalization claim was added.

## 11. Conclusion reconstruction

The Conclusion now opens with the research insight that a fixed inference
object does not uniquely define its input data path. It then distinguishes the
two intervention objects and separates mean from tail interpretation before
presenting the frozen quantitative evidence. Scope and limitations close the
section. No general theory or universal pinned-memory rule is claimed.

## 12. Citation-role audit and impact

The same 22 verified citation keys remain cited and rendered; the bibliography
still contains 27 entries, with five uncited entries and zero unresolved keys.
The established first-occurrence order was preserved so numeric bibliography
order and reference formatting did not drift.

Existing citations continue to cover these roles:

- industrial defect task/background;
- detector and model context;
- edge E2E deployment;
- quantization and correctness;
- CPU-GPU/data-path organization;
- memory and staging semantics;
- tail latency;
- benchmark and reproducibility boundaries.

No new source was needed. `CITATION_SOURCE_GAP = NONE`.

## 13. Figure 1 remediation

The ambiguous floating sentence
`固定推理对象：同一检测器 / Engine / 工作负载 / 后处理语义` was removed from
the deterministic Figure 1 generator and all regenerated outputs. It was not
replaced by another floating sentence. Section 1.1 remains the formal location
of the fixed-object definition.

Figure 1 retains the host/device domains, boundary, P0/V0, P2/V2R, P3/V3R,
`R/F/M/E`, both intervention levels, and the warning that hierarchy denotes
intervention scope rather than gain magnitude or component causality. The PNG
and grayscale render show no clipping or overflow.

The builder now places Figure 1 in a 16 cm, one-column `nextPage` section.
The preceding section remains two-column continuous, and the text after the
caption resumes in two columns. Figures 2 and 3 retain their established
continuous full-width behavior.

## 14. Scientific non-regression

`SCIENTIFIC_NONREGRESSION = PASS`

The Phase 6.1 validator checks:

- all three path definitions and structural-variable meanings;
- frozen research configuration and task workload;
- all task metrics and table metric rows;
- all frozen mean, tail, ratio, and percentage values;
- all protocol counts and descriptive-statistics boundaries;
- the three display equations plus the FPS definition;
- one formal RQ1 and one formal RQ2 with unchanged scientific meanings;
- correctness, causality, significance, and generalization limitations;
- byte identity of Section 3 and frozen Figure 2/3 PNG authorities;
- Figure 1 semantic inventory and absence of the removed sentence;
- Full/Anonymous Figure 1 OpenXML placement and 16 cm width.

Machine-readable result:
`docs/paper/phase6_1/phase6_1_scientific_nonregression.json`.

The explicit overclaim scan found 18 keyword matches. Every match is classified
`LEGITIMATE_NEGATION_OR_BOUNDARY`; zero are violations. The matches concern
bandwidth/transfer-speed disclaimers, non-causal component/bottleneck wording,
the rejection of “pinned improves stability,” descriptive-only significance
limits, and cross-platform/cross-model scope limits.

Equation meaning and inventory remain unchanged:

- `P=(R,F,M,E)`;
- `B(P)`;
- `T_E2E(P)`;
- `f_i=N/T_i`.

`DEFERRED_PHASE6_3_EQUATION_NUMBERING` remains applicable to any later visible
numbering-format work; no numbering mechanism was changed here.

## 15. Build results

Final production commands:

```bash
scripts/paper/build_manuscript_docx.sh --build-full
scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Both passed the heading, citation, reference, Full/Anonymous, anonymity,
scientific parity, and Phase 5.9C integration validators.

Final derived outputs:

| Artifact | Size | SHA256 |
|---|---:|---|
| Full DOCX | 469778 bytes | `3fa732579fe6ba9ef6511d78c82526648dceeef1073204e21df74e742b62797c` |
| Anonymous DOCX | 469079 bytes | `a9ef76ba2a7daa17f547945c0c2cbb685707c36a813e74c7b5c0ff9a37b65465` |
| Mechanical Full PDF | 747669 bytes | `27f946fd440d4a1e27064fa7cc5e0ffae9049d045d79cfe6b4f75fa7b5f38c3a` |
| Mechanical Anonymous PDF | 735713 bytes | `438b2cf2e6c8eaed8211f7af9d4c8e85f1f42704220680bfe10e5c17708d3fb3` |

The DOCX and PDF files remain generated artifacts under the existing ignored
output path and are not manuscript source.

## 16. Page and render inspection

Both mechanical PDFs are A4 and eight pages. All eight Full pages and all eight
Anonymous pages were inspected at 150 dpi.

- Chinese and English abstracts are readable;
- the reconstructed Introduction and section flow are intact;
- Figure 1 is on page 4, full-width and at page top;
- no two-column body text appears above Figure 1 on page 4;
- Figure 1 is not clipped, and its caption is below the figure;
- two-column body text resumes only below the Figure 1 caption;
- there is no blank catastrophic page;
- all three tables, three display equations, and three figures remain present;
- Figures 2 and 3 retain their scientific content;
- all 22 references remain present.

Page 3 intentionally ends early because Figure 1 is forced to the top of page
4. This whitespace is the accepted consequence of the supervisor's explicit
placement contract and was not compressed away.

Table 3 continues onto page 6 with its header repeated and all three scientific
rows present. This is non-blocking for Phase 6.1 because no data are lost; its
final pagination treatment is deferred to Phase 6.3 format remediation.

`FIGURE1_LAYOUT = PASS`

## 17. Known deferred Phase 6.3 issues

The following remain outside this work unit:

- final HFUT figure typography and font substitution;
- final Figure 2/3 layout and panel-label treatment;
- Table 3 final pagination/keep-together treatment;
- global `等 -> et al.` remediation;
- DOI policy and conference publisher metadata;
- global reference-format alignment;
- visible equation-numbering finalization;
- Visio, Origin, and MathType conversions;
- Microsoft Word Desktop manual QA and Document Inspector workflow.

No Phase 6.3 item was implemented.

## 18. Open findings

- Independent academic review has not yet been performed.
- Microsoft Word Desktop visual QA has not been performed for the rebuilt
  Phase 6.1 DOCX files.
- The mechanical PDFs are validation renders, not final submission artifacts.
- The Table 3 page continuation noted above remains a deferred format issue,
  not a scientific omission.

No blocking scientific, build, citation, anonymity, or Figure 1 finding remains.

## 19. Final Git diff scope

The final pre-commit diff contains only:

- six authorized manuscript source files;
- Figure 1 specification, generator, and four regenerated assets;
- one minimal production layout postprocessor change;
- one Phase 6.1 validator;
- one machine-readable validation artifact;
- one Phase 6.1 report.

There are no staged changes before the commit step and no unexplained files.

`UNEXPECTED_DIFF = NONE`

## 20. Commit

One focused commit is authorized after final validation:

```text
paper: reconstruct Phase 6.1 academic narrative
```

Commit identity in this self-contained report:
`COMMIT_CONTAINING_THIS_REPORT`.

The immutable commit SHA is supplied with the external execution handoff;
embedding a commit's own SHA in its contents would require a forbidden amend or
an additional commit.

## 21. Next required action

STOP.
Return the Phase 6.1 report and commit information to the Main Project AI.
Do not begin Phase 6.2 or Phase 6.3 automatically.
