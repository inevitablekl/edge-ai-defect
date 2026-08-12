# Paper Phase 5.6C Scientific Narrative Reconstruction Report

## 1. Verdict

`PHASE56_NARRATIVE_CANDIDATE`

This verdict means that the scientific narrative is ready for independent
claim review and later visual-architecture work. It is not a final manuscript
or a supervisor-review readiness verdict.

## 2. Starting state

- Repository: `/home/orin/edge-ai/edge-ai-defect`
- Branch: `main`
- Starting `HEAD`: `fd088341b9fdbb7b67e49b2b427b07d596f136ce`
- Starting `origin/main`: `fd088341b9fdbb7b67e49b2b427b07d596f136ce`
- Starting worktree/index: clean
- Scientific starting authority: `PHASE56_DERIVED_EVIDENCE_FROZEN`
- Level-A authority: unchanged
- Level-B authority: unchanged

## 3. Manuscript authority and build discovery

The content authority is the seven Markdown files under
`docs/paper/manuscript/sections/`, in numeric order. Generated DOCX files are
derived candidates and are not content sources.

- Current Full output: `docs/paper/manuscript/output/draft_full.docx`
- Current Anonymous output: `docs/paper/manuscript/output/draft_anonymous.docx`
- Current manuscript PDF from the governed build: none
- Full build: `scripts/paper/build_manuscript_docx.sh --build-full`
- Anonymous build: `scripts/paper/build_manuscript_docx.sh --build-anonymous`
- Main rendered validators:
  - `scripts/paper/validate_full_manuscript_docx.py`
  - `scripts/paper/validate_anonymous_manuscript_docx.py`
  - `scripts/paper/validate_word_heading_numbering_docx.py`
  - `scripts/paper/validate_final_references.py`
  - `scripts/paper/validate_journal_format_docx.py`

Starting section structure was Introduction; four System Object/Problem
Definition subsections; Method; Experiment; four Results subsections; and
Conclusion. Starting asset inventory was F1–F4 and T1–T3. Starting displayed
equations were `T_E2E`, `T_v`, Amdahl, process FPS, mean FPS, FPS sample SD,
Type-7 percentile position, and Type-7 interpolation.

## 4. Structural reconstruction

- Abstract: rewritten from three-variant benchmark description to an
  input-formation/data-movement engineering abstract.
- Introduction: rebuilt as industrial inspection → edge deployment → INT8
  network premise → input-path gap → engineering restructuring → two
  controlled comparisons → exactly two contributions.
- Section 1: compressed to model/dataset/environment, E2E data path and
  controlled variables, and timing boundary/research questions.
- Section 2: reframed around V0 host-side FP32 tensor formation, V2R GPU input
  formation, V3R staging-allocation isolation, and unified correctness/lifecycle
  control.
- Section 3: retained the frozen benchmark protocol while integrating formal
  calibration and runtime-state provenance.
- Section 4: reconstructed as correctness, overall E2E performance, data-path
  analysis, run-level stability/tail, related-work positioning, and limitations.
- Conclusion: rewritten as three paragraphs covering the main restructure,
  marginal pinned result/tail, and scope/future work.

## 5. Final contribution wording

1. 在固定YOLOv8n和TensorRT INT8混合精度Engine的条件下，将CPU/OpenCV主机侧FP32张量输入形成路径重构为packed raw-image staging、`cudaMemcpy2DAsync`和融合CUDA预处理，使device kernel直接形成TensorRT-owned FP32 NCHW设备输入，并通过pageable/pinned配置隔离主机暂存内存类型。
2. 建立统一的任务正确性、E2E latency、process-level FPS与pooled P95/P99评价协议，通过V0→V2R和V2R→V3R两级受控比较，区分完整输入路径重构的主要性能收益与pinned staging的有限平均增量，并利用5次独立进程考察运行级分布和尾延迟行为。

The contribution count is exactly two. Nominal payload analysis is explanatory
Level-B evidence under Contribution 1, not a third contribution.

## 6. Theory reconciliation

### Retained

- `T_E2E = sum_k T_k`: retained only to distinguish complete-pipeline timing
  from network-only TensorRT inference time.
- Process FPS, mean FPS, and Type-7 percentile equations: retained because
  they directly define frozen experimental statistics. FPS sample SD remains
  precisely defined in prose with five samples and denominator four; its
  redundant display equation was removed after mechanical rendering exposed
  incompatible mathematical glyphs.
- Qualitative local-to-E2E principle: retained with the existing Hill and
  Marty citation.

### Removed

- `T_v = T_shared,v + T_specific,v`: removed because the controlled-variable
  relationship is expressed directly in prose and existing visual interfaces.
- Amdahl speedup equation: removed because no alpha, component speedup, bound,
  or fitted theoretical acceleration is estimated.
- FPS sample-SD display equation: removed as a minimal content-only render
  remediation; its experimental definition and use are unchanged.

The Hill and Marty bibliography entry remains cited naturally by the short
qualitative principle; no orphan entry was created.

## 7. Level-B integrations

- V3R task metrics were promoted into manuscript prose using deterministic
  evaluation of frozen predictions: Precision `0.6913`, Recall `0.6991`,
  mAP50 `0.6476`, and mAP50-95 `0.3523` at manuscript precision.
- V0/V2R/V3R overall task metrics are identical on the frozen 180-image
  workload; maximum class AP50 and Recall differences are zero.
- Nominal input-copy payload is stated as V0 `4.9152 MB/frame`, V2R/V3R
  `0.1200 MB/frame`, ratio `40.96×`, with explicit non-traffic/non-timing and
  non-causal boundaries.
- Five-run process distributions are used only as descriptive evidence that
  the V3R mean advantage is not produced by one process.
- Publication display precision is `2.24×`, `55.45%`, `+4.07%`, `−4.03%`,
  `+0.15%`, and `−0.12%`; exact authority remains in machine evidence.
- Tail remains `MIXED` because the two changes are below 0.2% and have
  opposite directions.

## 8. Method and provenance wording

- V0: decoded `CV_8UC3` BGR → OpenCV letterbox/resize → BGR→RGB → HWC→CHW →
  `/255` → host FP32 NCHW → FP32 H2D.
- V2R: reusable pageable `std::vector<uint8_t>` packed BGR →
  `cudaMemcpy2DAsync` → device raw buffer → one fused CUDA preprocessing
  kernel → TensorRT-owned FP32 NCHW device input, using the TensorRT stream.
- V3R: one pre-loop `cudaHostAlloc(..., cudaHostAllocDefault)` allocation,
  reuse, `cudaFreeHost`, and otherwise the same V2R copy, kernel, stream,
  Engine, and downstream topology.
- Common exclusions are centralized once: no zero-copy, double buffering,
  multi-stream, cross-frame pipeline, explicit transfer/compute overlap, or
  GPU NMS.
- Calibration wording states 1,260 deduplicated train images, test exclusion,
  `IInt8EntropyCalibrator2`, batch 1, 640×640, production CPU preprocessing
  identity, INT8+FP16, FP32 I/O, forced cache miss, and cache generation/archive
  after calibration without reuse as formal-build input.
- Runtime wording states MAXN_SUPER/mode 2, no `jetson_clocks` invocation,
  absent independent clock-frequency archive, approximate pre/post
  temperatures, and non-continuous observation.

## 9. Result architecture and limitations

The main result sentence now states that V0→V2R supplies the principal E2E
gain and V2R→V3R only further improves mean performance. Tail interpretation
is separated from the mean-performance conclusion. Pinned staging is not
generalized beyond the fixed platform, implementation, and workload.

Limitations are centralized: single Jetson platform; single detector/Engine;
single dataset/workload; offline replay; no real camera; no continuous runtime
telemetry; no independently archived clock frequencies; no power measurement;
no stage-level causal timing decomposition; no measured H2D time,
preprocessing time, bus traffic, or total DRAM traffic; no cross-platform
generalization; and no statistical significance inference.

## 10. Citation and literature review

- Citations added: none.
- Citations removed: none.
- Bibliography records added/removed: none.
- Citation first-occurrence order: retained for all 26 cited records.
- Hill and Marty: retained for the qualitative local-to-E2E principle after
  removal of the equation.
- `PHASE56C_LITERATURE_SUPPORT_GAP`: none blocking. Existing literature
  supports the conservative positioning. Source-by-source YES/NOT_REPORTED
  visual classification remains a later Table 4 task and was not attempted.

## 11. Figure/table migration interface

Formal F1–F4 production: `NO`. Formal T1–T4 production: `NO`. Historical
assets deleted, overwritten, renamed, or data-modified: `NO`.

Existing F1–F4 and T1–T3 remain in place so the governed build remains stable.
Table 3 retains its current V0/V2R formal threshold record; V3R task-level
metrics are manuscript-visible in surrounding prose pending later table
integration. Stable later-phase semantic targets are:

- F1 Hero; F2 Technical Implementation; F3 Main E2E Results; F4 Run-Level Stability.
- T1 Path Feature Matrix; T2 Platform/Model/Protocol; T3 Correctness; T4 Related Work.

## 12. Claim-control and format-protection review

- Contributions: exactly two.
- Causality: 40.96× always nominal and never used as a measured traffic,
  transfer-time, or sole E2E causal claim.
- Correctness: V3R promoted to task-level manuscript results within the frozen
  workload boundary; no new gate is claimed.
- Tail: `MIXED`; no consistent improvement claim.
- Runtime: no no-throttling, fixed-frequency, fixed-fan, continuous thermal,
  or stable-power claim.
- Calibration: no ambiguous “calibration cache used” wording.
- Statistics: no run correspondence, p-value, confidence interval, or
  significance inference.
- Scope: no new CUDA/TensorRT/quantization algorithm, general framework, or
  third contribution claim.

Format contract modifications:

- Word styles: `NO`
- Equation styles: `NO`
- Margins: `NO`
- Columns: `NO`
- Fonts: `NO`
- Caption formats: `NO`
- Journal template: `NO`

Only validator content expectations for the new title, headings, and governed
publication rounding were updated; validator style/layout checks were not
weakened.

## 13. Build and validation

- Full build: `PASS`.
  - Output: `docs/paper/manuscript/output/draft_full.docx`
  - SHA256: `4ae24f79c971841d94c435aed84ef0039b2a8edd5ee870372ebdbb23622140ce`
- Anonymous build: `PASS`.
  - Output: `docs/paper/manuscript/output/draft_anonymous.docx`
  - SHA256: `3d40482f8ca0c50e09162b08637c27b0964735c0e5a17dcebcee5e6fc39104da`
- Full rendered structure/content validator: `PASS`.
- Anonymous identity scan: `PASS`.
- Full/Anonymous scientific-body parity: `PASS`.
- Heading numbering and style inheritance: `PASS`; 22 explicit headings,
  no direct or inherited automatic numbering.
- Citation source, deterministic order, static figure/table cross-reference,
  rendered bibliography, and Full/Anonymous bibliography identity: `PASS`;
  27 library entries, 26 cited/rendered, one governed unused entry.
- Journal-format validator: `PASS`; five formal equations, four inline figures,
  three native tables, and expected one-/two-column section transitions.
- LibreOffice 7.3 mechanical render: `PASS`; Full and Anonymous are both nine
  A4 pages. All pages were inspected for clipping, heading breaks, equation
  glyph integrity, figure/table overlap, and gross layout failure.
- Anonymous render inspection: no visible author or affiliation identity.
- `git diff --check`: `PASS`.

## 14. Files changed

- Seven authoritative manuscript section files.
- Minimal title/heading/publication-display expectations in four manuscript
  validators.
- This Phase 5.6C report.

Frozen evidence, bibliography, figures, tables, DOCX style definitions,
reference template, and production C++/CUDA sources were not modified.

## 15. Final commit

The final focused commit is the commit containing this report. Its SHA is
reported in the Phase 5.6C completion response because a commit cannot contain
its own final SHA. Push, merge, and tag are not authorized and are not executed.
