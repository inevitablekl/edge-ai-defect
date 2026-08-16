# Paper Phase 5.7G — Final Minor Remediation Report

## 1. Verdict

`PHASE57G_FINAL_MINOR_REMEDIATION_CANDIDATE`

- `FINAL_REVIEW_MINOR_FINDINGS = CLOSED`
- `NO_FURTHER_CONTENT_REVISION_RECOMMENDED = YES`
- `WORD_DESKTOP_FINAL_QA_REQUIRED = YES`

## 2. Repository state

- Repository: `/home/orin/edge-ai/edge-ai-defect`.
- Branch: `main`.
- Starting `HEAD = origin/main`: `30195974fc4ce8cf6e09be08056697760d0925c5`.
- Starting worktree and index: clean.
- Phase 5.6 historical package and earlier Phase 5.7 reports/manifests changed: none.
- No experiments, profiling, H2D timing, format compression, or unrelated manuscript revision was performed.

## 3. MR1 — Table 2 Engine wording

- Before: `TensorRT INT8混合精度（INT8 + FP16 fallback）；host input FP32`.
- After: `TensorRT INT8混合精度（INT8 + FP16 fallback）；Engine输入张量：FP32`.
- Result: Table 2 no longer implies that V2R/V3R form the Engine input as a host-side FP32 tensor. The visible interpretation now remains V0 host-side FP32 tensor formation versus V2R/V3R packed-BGR host staging followed by device-side FP32 Engine-input formation.
- Other Table 2 rows, Engine identity, INT8, and FP16 fallback are unchanged.

`MR1 = CLOSED`

## 4. MR2 — Table 1 staging row

- Before: `原始图像暂存` with values `否 / Pageable / Pinned`.
- After: `额外打包原始图像暂存` with the same values `否 / Pageable / Pinned`.
- Result: the row now distinguishes the additional packed raw-image staging buffer introduced by V2R/V3R from V0's existing decoded `CV_8UC3` host image.
- No other Table 1 cell or table structure changed.

`MR2 = CLOSED`

## 5. MR3 — Section 2.3 citation precision

- Old source target: `archet_et_al_2023_embedded_soc` (previously rendered as [21]).
- New source targets: `bateni_et_al_2020_integrated_memory` and `rodriguez_et_al_2025_gpu_memory_allocation` (rendered as [16,17]).
- The two replacement works directly support integrated host/GPU memory-management strategy and workload-dependent GPU allocation behavior.
- Per the superseding Phase 5.7G clarification, the now-orphaned Archet work was not relocated or replaced and is no longer rendered.

`MR3 = CLOSED`

## 6. Reference audit

- Bibliography library entries: 27.
- Cited/rendered references: 22.
- Unresolved citations: 0.
- Dead rendered references: 0.
- Uncited retained library entries: 5, including the legitimately orphaned Archet entry.
- Full/Anonymous bibliography identity: PASS.
- Rendered numbering after [20] updates mechanically: Shin & Kim is [21], and Lema et al. is [22].

## 7. Scientific non-regression

All frozen scientific values remain unchanged:

| Quantity | Frozen value |
|---|---|
| FPS, V0 / V2R / V3R | 54.600 / 122.122 / 127.097 |
| Mean latency (ms), V0 / V2R / V3R | 18.273 / 8.140 / 7.812 |
| V0→V2R | 2.24× FPS; −55.45% mean latency |
| V2R→V3R | +4.07% FPS; −4.03% mean latency |
| P95 / P99 | +0.15% / −0.12% |
| Nominal payload | 4.9152 / 0.1200 MB per frame; 40.96× |
| Correctness tuple | 0.6913 / 0.6991 / 0.6476 / 0.3523 |
| V2R FPS range | 121.443–122.759 |
| V3R FPS range | 125.595–128.301 |
| V2R mean-latency range (ms) | 8.098–8.185 |
| V3R mean-latency range (ms) | 7.740–7.894 |

The Phase 5.7G integration validator passes the frozen scientific-token, path, tail-latency, payload, and correctness contracts.

## 8. Figure, table, and equation inventory

- Contributions: 2.
- Figures: 4; no image source or embedded payload mutation.
- Tables: 4; only the authorized T1 row label and T2 Engine-cell wording changed.
- Table row/column structures and all data values are unchanged.
- Display equations: 2; no equation mutation.
- Title, abstract, contributions, RQs, results, conclusion, related-work prose, and captions are unchanged.

## 9. Builds, hashes, and pages

| Output | Pages | SHA-256 |
|---|---:|---|
| Full DOCX | — | `3513282279ecbeeea7c677523249ec593bb61aa78343c2eafd819c79096bfe8b` |
| Full mechanical PDF | 7 | `b6c8ef8a65cfbffb601c4f0b84a12c792ab6d78a2c5dc303226c08df2dc829b2` |
| Anonymous DOCX | — | `b505dfdf56b9caabdd80ed495f58f6eef67e82be978f8f9c364e69cefeee7149` |
| Anonymous mechanical PDF | 8 | `e8d36a450952634a234757cd8289be9f6e3d812b21fa7d45ed88e092977d8487` |

Both PDFs are A4 and satisfy the `<= 8` page gate.

## 10. Official-format validation

Official HFUT format validation: PASS. The page size, margins, column geometry, body and table styles, first-line indent, footer distance, headings, captions, abstract/keyword layout, and equation count remain conforming. The Chinese title remains one centered, unclipped line in 22-pt bold SimSun with the automatic safe line box and `snapToGrid=false` fix intact. The frozen reference DOCX SHA-256 remains `31b65361f50262240630d1453637218e2455b150dadc653edfa8e535439c55c0`.

## 11. Mechanical QA

All 7 Full pages and all 8 Anonymous pages were raster-inspected.

- Table 1's new row label is readable without overflow or clipping.
- Table 2's revised Engine wording wraps normally within the narrow value column and remains unambiguous and unclipped.
- Section 2.3 renders the replacement citations as [16,17].
- Title, headings, F1–F4, T1–T4, both display equations, references, and column transitions remain readable.
- No overlap, clipping, unexpected blank region, or new orphan paragraph was observed.
- Anonymous page 6 retains the pre-existing intentional whitespace before the Table 4 page-break guard; this is expected and not a Phase 5.7G regression.

## 12. Open submission exceptions and handoff

- `SUBMISSION_EXCEPTION_MATHTYPE = OPEN` (unchanged).
- `SUBMISSION_EXCEPTION_VISIO_ORIGIN = OPEN` (unchanged).
- LibreOffice mechanical PDF QA is complete; final Microsoft Word Desktop visual QA remains required before submission.
- Commit: `COMMIT_CONTAINING_THIS_REPORT`.
- No push, tag, merge, or amend is authorized in this phase.

