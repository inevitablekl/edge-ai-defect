# Paper Phase 5.7B — Primary Safe Length Compression Report

## 1. Verdict

`PHASE57B_PRIMARY_COMPRESSION_CANDIDATE`

- First complete P1 mechanical rebuild: 7 A4 pages.
- Final full manuscript: 7 A4 pages.
- Final anonymous manuscript: 7 A4 pages.
- The `<= 8` page gate was met on the first complete P1 rebuild, so no P2 or further prose compression was performed.

## 2. Repository and authority state

- Starting branch: `main`.
- Starting `HEAD = origin/main`: `4a1c25d4ce553146e47cf5578cf0f23d62e6377b`.
- Scientific/format comparison authority: `59a5b57dc867185217c61b985e79d2990233140c`.
- Starting worktree/index: clean.
- Phase 5.6 paths changed: none (`git diff -- docs/paper/phase5_6` was empty).
- No experiment, inference, benchmark, or profiling execution was performed.

## 3. Compression implementation

### Introduction and Sections 1.1–1.3

- Introduction reduced to four substantive paragraphs plus exactly two contributions; the manuscript-roadmap paragraph was removed.
- Section 1.1 reduced to one compact paragraph while retaining Jetson Orin Nano Super, YOLOv8n, 640×640, batch 1, NEU-DET split-v2, the fixed 180-image test workload, 1260 deduplicated calibration-training images, test-split exclusion, `IInt8EntropyCalibrator2`, and the INT8 + FP16 mixed-precision Engine.
- The JetPack mapping paragraph, Amdahl paragraph/citation, and MLPerf-specific disclaimer/citation were removed.
- Sections 1.2–1.3 retain the complete E2E boundary equation, the no-stage-attribution boundary, both research questions, and concise tail-latency motivation.

### Methods and correctness

- V0 retains `INTER_LINEAR`, padding 114, BGR→RGB, HWC→CHW, 1/255 normalization, host FP32 NCHW formation, and the device copy.
- V2R retains packed BGR, 200×200 geometry, 600-B row width, `cudaMemcpy2DAsync`, the persistent device raw buffer, fused resize/padding/color/normalization/layout preprocessing, direct TensorRT-owned device input, and the same TensorRT CUDA stream.
- V3R retains `cudaHostAlloc(..., cudaHostAllocDefault)`, a long-lived reused pinned buffer, `cudaFreeHost`, and allocation type as the isolated variable while preprocessing, stream, Engine, and downstream behavior remain fixed.
- Repeated method disclaimers were consolidated into one scope paragraph.
- Section 2.4 replaces six publication-visible numeric thresholds with the governed evaluator/provenance/lifecycle description while retaining the frozen-workload boundary and V3R legitimacy.

### Experiment, statistics, results, and conclusions

- Table 2 now carries platform/model/protocol detail; prose retains MAXN_SUPER, `nvpmodel mode 2`, no `jetson_clocks`, no independently archived frequencies, and non-continuous temperatures.
- The protocol retains 60 warmup frames, 1080 measured frames/process, 5 processes/path, 15 total processes, 5400 latency samples/path, the common manifest/order, zero dropped frames, predefined interleaving, and disabled diagnostics/profiling. Exact permutations remain only in frozen evidence.
- Statistics retain only `f_i=N/T_i` as the Section 3 display equation; arithmetic mean, sample SD, pooled latency, Type-7 interpolation, and descriptive-only inference remain in prose.
- Results retain the complete frozen numeric payload: identical task metrics, V0→V2R 2.24× FPS and −55.45% mean latency, V2R→V3R +4.07% FPS and −4.03% mean latency, all four run-level ranges, P95 +0.15%, P99 −0.12%, and the opposite-direction/no-consistent-tail-improvement conclusion.
- The 40.96× value remains explicitly nominal input-copy payload, not measured traffic or component-level causal attribution.
- Table 3 was laid out as two columns (path plus the ordered P/R/mAP50/mAP50-95 tuple) so all four unchanged values remain readable at the frozen table font, margins, and total width.
- Related work is one positioning paragraph, one classification-rule paragraph, and compact Table 4; no first/unique/performance-ranking claim was added.
- Limitations are one paragraph covering every required limitation category; the conclusion is exactly two paragraphs.

## 4. Phase 5.7 visual and table assets

### Figure 2

- New deterministic asset size: 160 mm × 62 mm (Phase 5.6: 160 mm × 82 mm).
- PNG/grayscale raster size: 1893×736 px; PDF media box: 454.28×176.485 pt.
- Minimum source label maps to approximately 7.65 pt at 16-cm insertion.
- Color and grayscale visual inspection: PASS; no clipping observed.
- Retained topology: host/device domains, pageable/pinned staging, `cudaMemcpy2DAsync`, device raw buffer, fused CUDA preprocessing, TensorRT-owned input, `enqueueV3`, and the single TensorRT CUDA-stream rail.
- Determinism: two consecutive generator runs produced identical hashes.

| Asset | SHA-256 |
|---|---|
| F2 SVG | `868e199abfbe23fa3ae81cdc7c1d7092d0acb07c8ba5e55fc196874c0ccef880` |
| F2 PDF | `b72aab415faad7e13ed0f31f5c4735c51c516d68a765689680e0439bb850d480` |
| F2 PNG | `d0cd2496420fa46eb1950bdef33af170891ffb043dd87f8f13e6d08238b07563` |
| F2 grayscale PNG | `39ffaadeecee2054b98a64027b85f87041b8cdd6370843bb80b77ebafd8552b5` |

### Frozen figures and compact tables

- Frozen Phase 5.6 PNG hashes remain unchanged: F1 `9fcd9388b6d12bfc027adfb7c0a1aac8690a324f7b987efe6229b7109e4fcb05`; F3 `dfa125e8d20c28c93cb8a210417d72103988057cfd2bca371f2bd1c17a802ea9`; F4 `c30ee465b6707064819504994c569d48a01067602b19c5a4c79b4b90fe296e96`.
- Phase 5.7 T1: 7 governed rows; pageable/pinned and single-frame/no-cross-frame-pipeline semantics remain explicit. Source SHA-256: `e04ebb50827e5c996d284de8e535707b7996b4d2b02b1cf8a27b2f078b78938c`.
- Phase 5.7 T4: 6 total columns (work + 5 retained attributes); all retained classifications are unchanged. Source SHA-256: `7273b89b42bf340e79ca16b9e429c4ec9a297b8a4adb9808cd4525edaecd2f16`.
- Phase 5.7 caption authority SHA-256: `5094c03c4646f1d61ce1434101383469582bad793aca0c1e5be62f17625acc84`.

## 5. Before/after compression metrics

| Metric | Phase 5.6 frozen | Phase 5.7B | Change |
|---|---:|---:|---:|
| Mechanical A4 pages | 10 | 7 | −3 (−30.0%) |
| Body-source CJK characters | 7030 | 3404 | −3626 (−51.6%) |
| Body prose paragraphs | 69 | 42 | −27 (−39.1%) |
| Display equations | 5 | 2 | −3 |
| Rendered references | 26 | 23 | −3 |
| F2 dimensions | 160×82 mm | 160×62 mm | height −20 mm (−24.4%) |
| T1 data rows | 10 | 7 | −3 |
| T4 total columns | 8 | 6 | −2 |
| Caption non-whitespace characters | 1090 | 383 | −707 (−64.9%) |

Metric method: body-source counts use Sections 01–06, exclude HTML comments and front matter; CJK counts include visible headings, captions, and table content; paragraph counts exclude headings, Markdown table rows, and display-equation blocks but include prose/list/caption paragraphs. Caption counts cover F1–F4 and T1–T4 after removing Markdown emphasis and whitespace.

## 6. References and equation inventory

- Removed prose and rendered citations: `nvidia_jetpack_6_2_2`, `hill_marty_2008_amdahl`, `reddi_et_al_2019_mlperf_inference`.
- Bibliography library: 27 entries; cited/rendered: 23; uncited library entries: 4; unresolved citations: 0.
- Every rendered reference has a substantive in-text citation; no dead rendered reference was retained to reach a count.
- Display equation 1: `T_E2E = Σ T_k` in Section 1.
- Display equation 2: `f_i = N/T_i` in Section 3.3.

## 7. Validation and build outputs

- Full build: PASS.
- Anonymous build: PASS.
- Full/anonymous scientific-body and bibliography parity: PASS.
- Anonymous package identity scan: PASS.
- Phase 5.7B integration validation: PASS (4 figures, 4 tables, 2 equations, 2 contributions, 23 references).
- Official HFUT format: PASS; reference DOCX SHA-256 remains `31b65361f50262240630d1453637218e2455b150dadc653edfa8e535439c55c0`.
- Chinese title: 22-pt bold SimSun, centered, one rendered line, automatic line rule, `snapToGrid=false`, no clipping risk.
- All 23 rendered title/heading lines: single-line.
- DOCX ZIP checks, citation resolution, frozen scientific-token checks, and `git diff --check`: PASS.
- Raster review covered every final full/anonymous page; Table 3 digit wrapping and anonymous Table 4 cross-section overlap were corrected without changing font, margins, spacing, or scientific values. The anonymous Table 4 page break is a rendering-integrity fix and does not change the 7-page result.

| Output | SHA-256 |
|---|---|
| Full DOCX | `a762f11f48af5f717044859734bc1a3880453d2a4d78d8c339267d0c0bbfa654` |
| Anonymous DOCX | `601baaf1cef6982e08ba9efc89fb660d38435c18ebded09f80bc6be56fa38fb6` |
| Full mechanical PDF | `fcfd4b472f6a4560a32a8aa6f56d0e090e902e210b9dd45b8bc0d774b2483462` |
| Anonymous mechanical PDF | `361a9b999a7ec858edef1e80be57d45c3394abfbc37619f5cb354b95511972b1` |

## 8. Open findings and submission exceptions

- `SUBMISSION_EXCEPTION_MATHTYPE = OPEN` (unchanged).
- `SUBMISSION_EXCEPTION_VISIO_ORIGIN = OPEN` (unchanged).
- The mechanical page count and raster QA use LibreOffice PDF rendering; final Microsoft Word Desktop visual recheck remains required before submission.
- No push, tag, merge, or amend is part of this phase.
