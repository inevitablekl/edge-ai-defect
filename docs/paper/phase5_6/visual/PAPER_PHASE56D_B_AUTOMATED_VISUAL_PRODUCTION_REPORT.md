# Paper Phase 5.6D-B — Automated Figure and Table Production Report

## 1. Starting Baseline

The task started from the requested clean baseline:

```text
repository = /home/orin/edge-ai/edge-ai-defect
branch = main
HEAD = dfdceea772e2083adbb5809be4c3ba619a276357
origin/main = dfdceea772e2083adbb5809be4c3ba619a276357
git status --short = empty
git diff --stat = empty
git diff --cached --stat = empty
```

No pre-existing user work was present. The work remained inside `docs/paper/phase5_6/visual/`, and no push, tag, merge, inference, benchmark, or diagnostic run was performed.

## 2. D-A Review Resolution

The D-A architecture was retained. `REDESIGN_REQUIRED = NO`; all four figure architectures remain approved. D-B applied only the authorized production adjustments:

- removed all visible/internal candidate, specification, draft, and preview status text from formal figures;
- changed F1 to `名义输入复制载荷比` and retained the exact non-bus-traffic guard;
- changed the F1 boundary to `主机/设备内存域边界`;
- kept all F1 performance values inside the detached complete-path comparison footer;
- connected the F2 stream rail to `cudaMemcpy2DAsync`, the fused CUDA preprocessing operation, and `enqueueV3`, rather than to buffer nodes;
- changed F3 Panel B to `每路径合并5400个延迟样本`;
- reduced F4 pooled-tail content to a compact annotation and placed the full 5400-sample semantics in the caption freeze.

## 3. Figure 1 Production

Produced:

```text
production/figures/fig1_hero_data_path_phase56.svg
production/figures/fig1_hero_data_path_phase56.pdf
production/figures/fig1_hero_data_path_phase56.png
```

The SVG has a fixed `160 mm × 93 mm` structural canvas. Display values are read from the frozen publication/payload JSON inputs: V0 `4.915 MB/frame`, V2R/V3R `0.120 MB/frame`, nominal input-copy payload ratio `40.96×`, V0→V2R `2.24×` and `55.45%`, and V2R→V3R `+4.07%` and `4.03%`. The machine authority remains `4.9152`, `0.1200`, and `40.96`; no bus traffic is inferred.

```text
SVG SHA256 = d5f449ecc1c174d4315876bb2faf38e5f09d1c0bf675861466e413184cb5a887
PDF SHA256 = 61d5a6f2d18d2c8579e1cecbc86da4c974a9d373a09167fc543ec60650cb8b99
PNG SHA256 = 9fcd9388b6d12bfc027adfb7c0a1aac8690a324f7b987efe6229b7109e4fcb05
```

Validation confirms that the four comparison values occur only in the detached footer, not on H2D, CUDA preprocessing, staging, or Engine components.

## 4. Figure 2 Production

Produced:

```text
production/figures/fig2_technical_implementation_phase56.svg
production/figures/fig2_technical_implementation_phase56.pdf
production/figures/fig2_technical_implementation_phase56.png
```

The SVG has a fixed `160 mm × 82 mm` structural canvas. The stream rail carries explicit operation targets for `cudaMemcpy2DAsync`, fused CUDA preprocessing, and `enqueueV3`; output D2H is also labeled as ordered on the same stream. The figure retains single-stream, single-frame, no-cross-frame-overlap semantics and contains no performance or payload number.

```text
SVG SHA256 = 8e81ed1d50322d75c9170e99e6aa54bca9e180c79d2d8bfd947fbb81d045e605
PDF SHA256 = 40b36f859e693f0084952283b1f9354802c8b05c3c3dfd5b8b2cfac4c8a88a90
PNG SHA256 = 935e17fcb1ace1166b586af56adde8ad026e0a9689501f4affed0f08fe13fdc3
```

## 5. Figure 3 Production

Produced:

```text
production/figures/fig3_main_e2e_phase56.svg
production/figures/fig3_main_e2e_phase56.pdf
production/figures/fig3_main_e2e_phase56.png
```

The generator reads the frozen 15-row process CSV and publication display JSON. It verifies exactly five accepted independent processes per path and 1080 measured frames per process, recomputes each FPS mean and sample SD with `ddof=1`, and reads pooled mean/P95/P99 authority for 5400 latency samples per path. No bar height is manually entered. Panel C remains an absolute-axis P95/P99 comparison with no inset, broken axis, or relative-tail magnification.

```text
SVG SHA256 = 881532ab226d72de92735892950d6dd97fef75e51ad390a1223c9827b0ddbdb1
PDF SHA256 = 9562323f0228c494e12e378ded74cf7dbcdfb5a4802894658a1232bc07ff0815
PNG SHA256 = dfa125e8d20c28c93cb8a210417d72103988057cfd2bca371f2bd1c17a802ea9
```

## 6. Figure 4 Production

Produced:

```text
production/figures/fig4_run_level_distribution_phase56.svg
production/figures/fig4_run_level_distribution_phase56.pdf
production/figures/fig4_run_level_distribution_phase56.png
```

Panel A contains 15 independent process-level FPS points, five per path, with descriptive mean ± sample SD. Panel B contains five V2R and five V3R process-level points for each of Mean/P95/P99. Jitter is fixed; no run IDs are paired, no points are connected, and no significance or long-term stability inference is added. The compact pooled annotation remains `P95 +0.15%, P99 −0.12% → MIXED`.

```text
SVG SHA256 = 8d2cb04c771c56b0fe7438cfbae07c4767b64db8553bf10c89ed6d9d67463a5e
PDF SHA256 = dfab0533ab4c7e0ddb04e36544c72929cafdf456886099353f3964c24e7c24aa
PNG SHA256 = 04159ed81757a4451a177a05acbdf7e9aa0680b3508153eeee23d7512abe518d
```

## 7. Tables 1–4 Production

Publication-facing Markdown sources were produced without manuscript integration:

| Table | Output | Production rule |
|---|---|---|
| T1 | `production/tables/table1_path_feature_matrix_phase56.md` | 30 data cells parsed from the frozen implementation evidence map; concise Chinese labels |
| T2 | `production/tables/table2_platform_protocol_phase56.md` | compact `KEEP_IN_TABLE` platform/model/calibration/workload/protocol facts only |
| T3 | `production/tables/table3_correctness_phase56.md` | 3 paths × 4 task metrics generated from the frozen correctness CSV at four decimals |
| T4 | `production/tables/table4_related_work_phase56.md` | 6 works × 7 attributes; 42 cells generated from the full-text evidence matrix |

T3 contains no gate tolerance/pass-fail columns. T4 preserves `未报告` separately from `明确否`, has no rank or YES-count, and explicitly excludes superiority, first, or unique interpretations.

## 8. Caption Freeze

`production/phase56_figure_table_captions.md` freezes F1–F4 and T1–T4 caption text for later Phase 5.6E integration. F3 identifies sample SD of five independent process-level FPS values and 5400 pooled latency samples per path. F4 identifies points as independent process-level descriptors, states that no pairing is implied, and retains Level-A pooled P95/P99 as the formal tail authority. T4 is described only as a qualitative comparison of reported research attributes.

## 9. Evidence Provenance

The production scripts verify the following frozen inputs before generation:

| Input | SHA256 |
|---|---|
| `phase56b_run_level_metrics.csv` | `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` |
| `phase56b_publication_display_values.json` | `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655` |
| `phase56b_correctness_table_source.csv` | `d5424cb940db58eff7c826e9d99236c98ff444b37b7f45bedc993a8b70c9cf39` |
| `phase56b_nominal_payload.json` | `706f441da5df4720b3361a9001f0a6d7c1dbb8e8e85b17c62b8ff4db38833bd8` |
| `phase56b_runtime_state.json` | `ffcc1fad184bef828417201b96484ee734ef5d21ee1b61c048879a93866fdb17` |
| `phase56b_calibration_provenance.json` | `10c673ce3ee3d721db053698d1570208144b5a27baccf8b07e43dbace07f5042` |
| `phase56_visual_evidence_map.csv` | `2d37191c59f9ef957cd56dfd0327ce8e3f3e077b2c18e18e9db7c270adfed5ee` |
| `phase56_related_work_attribute_evidence.csv` | `fbef3e8bff6bd38ee51417d28ff5a407932ac5a7a628b1970fac2efa9321650b` |

The JSON manifest records each figure/table role, source data and hashes, production script, D-A spec, file hashes, dimensions, and authority type.

## 10. Deterministic Regeneration

Production uses no network, randomness, or manual post-editing. Structural SVG uses fixed geometry and fixed physical width. Statistical SVG/PDF uses a fixed Matplotlib hash salt and normalized metadata. Structural PDF metadata is normalized after conversion. F4 uses a fixed jitter vector.

Validation regenerates all 12 figure files, four table sources, and the caption freeze in a temporary directory and compares SHA256. Result:

```text
deterministic_regeneration = PASS
17/17 governed production outputs = byte-identical
```

Regeneration commands:

```bash
python3 docs/paper/phase5_6/visual/scripts/generate_phase56d_production_structural.py
python3 docs/paper/phase5_6/visual/scripts/generate_phase56d_production_statistical.py
python3 docs/paper/phase5_6/visual/scripts/generate_phase56d_production_tables.py
python3 docs/paper/phase5_6/visual/scripts/validate_phase56d_production.py
```

Expected inputs are the frozen files in Section 9. Expected output is four SVG/PDF/PNG triplets, four table sources, one caption freeze, eight inspection rasters, a manifest, a SHA256 file, and a PASS validation JSON.

## 11. Raster Inspection

The four 300-DPI PNGs and PDF/vector conversions were inspected at original resolution. CJK and API tokens render correctly; arrowheads, box borders, hatches, markers, legends, axes, and numerical labels are visible; no clipping or embedded figure-number caption is present.

```text
F1 = PASS
F2 = PASS
F3 = PASS
F4 = PASS
```

## 12. Actual-Width Readability

The journal proof width is fixed at `16.0 cm`. Deterministic 150-DPI proof rasters were generated at exactly 945 px wide:

| Figure | Proof dimensions | Result |
|---|---:|---|
| F1 | 945 × 550 px | PASS |
| F2 | 945 × 485 px | PASS |
| F3 | 945 × 363 px | PASS |
| F4 | 945 × 423 px | PASS |

At proof width, the smallest labels, API tokens, axes, legend, numeric labels, arrowheads, outlines, and hatches remain readable. No journal margin, column, style, or insertion setting was changed.

## 13. Grayscale Validation

Matching grayscale 16-cm/150-DPI proofs were inspected. F1 retains explicit V0/V2R/V3R labels and opposing hatch directions for V2R/V3R. F3 retains dotted/forward-slash/backslash hatches. F4 retains square/circle/triangle markers and outlines. Variant identity does not depend on color.

```text
F1 grayscale = PASS
F2 grayscale = PASS
F3 grayscale = PASS
F4 grayscale = PASS
```

## 14. Scientific-Value Validation

The automated validator records 73 PASS checks. These include:

- all input files and frozen hashes;
- F1 payload display/terminology/guard and complete-path-only attachment;
- F2 no-performance-number and stream-operation targets;
- F3 FPS means/sample SD, pooled mean, absolute pooled P95/P99, and no relative-tail magnification;
- F4 process populations, fixed jitter/no pairing, and pooled-tail annotation;
- T1 30-cell implementation map, T2 compact provenance, T3 12 metric cells, and T4 42 traceable classifications;
- caption semantics, grayscale dynamic range, physical/vector/raster dimensions, protected mutation checks, and deterministic regeneration.

Machine-readable result: `production/phase56_visual_asset_validation.json`.

## 15. Mutation Check

```text
authoritative manuscript Markdown modified = NO
DOCX modified = NO
journal formatting modified = NO
existing Phase 5.4 historical assets deleted = NO
Level-A modified = NO
Level-B modified = NO
manuscript figure/table references modified = NO
```

## 16. Output Hashes

The exhaustive generated-file hash list is `production/phase56_visual_asset_sha256.txt`. The structured asset manifest is `production/phase56_visual_asset_manifest.json`.

```text
manifest SHA256 (pre-report validation run) = 40e9540057de8cbe78d98f7008767f57094e5eac1d76e9adf7d6dc4a161348f3
validation SHA256 (pre-report validation run) = a6c058de8a237cc99b52420076097c71e730dbf0e681aa2af21fbf6b1827c1ba
```

The final validator rerun after this report updates the exhaustive SHA file to include this report without making the manifest self-referential.

## 17. Open Findings

1. No scientific-authority mismatch or visual-remediation blocker remains.
2. Table outputs are publication-facing Markdown sources; native Word table construction and manuscript/DOCX integration remain intentionally deferred to Phase 5.6E.
3. T4 remains scoped qualitative positioning evidence. D-A's `F1_SUPPORT_STATUS = PARTIALLY_SUPPORTED` and `NO_DIRECT_MATCH_IN_AUDITED_SET` do not support a field-wide first/unique claim.
4. F1/F2 compatibility PDFs are emitted by LibreOffice at approximately 16.03 cm page width; SVG authority is exactly 160 mm, and all downstream proof/insertion validation uses the fixed 16.0 cm target.

## 18. Commit

One focused local commit is required with message:

```text
paper: produce phase 5.6 visual assets
```

The exact commit SHA is reported in the final handoff rather than embedded here, avoiding a self-referential commit hash. Push, tag, and merge remain prohibited.

## Verdict

```text
PHASE56_VISUAL_ASSETS_READY
```
