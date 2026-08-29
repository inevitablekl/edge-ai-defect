# Excel Submission Figures Production Report v1.0

## 1. Verdict

```text
PHASE_7_2B_J_EXCEL_FIGURE_ASSETS_READY
```

Figure 2 and Figure 3 were produced as native Excel chart workbooks. They do not embed the accepted PNG/SVG references and contain no `xl/media` parts.

## 2. Repository baseline and execution environment

| Item | Recorded value |
|---|---|
| Repository | `/home/orin/edge-ai/edge-ai-defect` |
| Starting branch | `main` |
| Starting HEAD | `c73e4119289b7484316762f62476ac1939073c5e` |
| Starting worktree exception | Unrelated untracked `docs/paper/phase7/PAPER_PHASE7_2B_ALL_EQUATIONS_STANDARD_LATEX_v1.0.md`; preserved and excluded from this task |
| Execution platform | Jetson Linux; no Windows or WSL used |
| Python | `3.10.12` |
| XlsxWriter | `3.2.9`, installed in the active user's Python environment |
| Final rendering workflow | Manual opening and copying in Microsoft Excel/Word on Windows |

No reset, clean, merge, rebase, amend, push, Word edit, manuscript-text edit, or Figure 1 work was performed.

## 3. Scientific and visual sources

The CSV and JSON below are the frozen scientific authorities. The generator and accepted SVG/PNG files were inspected as semantic and visual references only.

| Role | Path | SHA-256 |
|---|---|---|
| Figure manifest | `docs/paper/manuscript/figures/figure_manifest.csv` | `3694e0bd01b698fb5f31c8d618a8eecd071ffac62082f76679c48067c640efab` |
| Frozen run-level authority | `docs/paper/phase5_6/phase56b_run_level_metrics.csv` | `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` |
| Frozen publication display authority | `docs/paper/phase5_6/phase56b_publication_display_values.json` | `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655` |
| Accepted statistical generator | `docs/paper/phase5_6/visual/scripts/generate_phase56d_production_statistical.py` | `3efc2828bc1aa4be5400c2874d1af5b5ebd2a00a6af9dbca83f11d3068987bfb` |
| Figure 2 SVG reference | `docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.svg` | `be3a5207bab8973c769e307acd5ac3834ef4c1d4efae355f46273a0a9c394ac4` |
| Figure 2 PNG reference | `docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.png` | `30e0d1254c0505b1bc1bfdcf5adf60c47d911a7c02b0ee93b3d2991c295db938` |
| Figure 3 SVG reference | `docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.svg` | `f1c95f5b67800aff6a29c8ed242ee6bc0b707e8c598a9dcf1551c54c7ab2958a` |
| Figure 3 PNG reference | `docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.png` | `2f077a25bfddb50a8aaa186567a466180ba61b0ce0f16b1e10928cf73e28e2c8` |

The builder checks the two frozen authority hashes before reading any values and again after workbook creation.

## 4. Produced assets

| Asset | Absolute path | Size / role | SHA-256 or trace |
|---|---|---:|---|
| Figure 2 workbook | `/home/orin/edge-ai/edge-ai-defect/docs/paper/submission_assets/excel/Figure2_E2E_performance.xlsx` | 16,434 bytes | `ba0b5a49152e6072c1aa2c4be0928b75705967f476625d42d9e6f3a209c03391` |
| Figure 3 workbook | `/home/orin/edge-ai/edge-ai-defect/docs/paper/submission_assets/excel/Figure3_run_level_distribution.xlsx` | 17,238 bytes | `3a6279339e849ff942d16843e718f6e77659d671429e8b16e305e52ab5a91649` |
| Builder | `/home/orin/edge-ai/edge-ai-defect/docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py` | Reproducible Python + XlsxWriter builder | Frozen CSV/JSON sources |
| Submission manifest | `/home/orin/edge-ai/edge-ai-defect/docs/paper/submission_assets/excel/submission_asset_manifest.csv` | Separate submission-asset register | Does not alter frozen scientific-status fields |

The two workbook SHA-256 values remained identical across two consecutive builder reruns.

## 5. Workbook structure

Both workbooks contain the same three real worksheets:

| Worksheet | Purpose |
|---|---|
| `RawRuns` | All 15 accepted run-level CSV rows, including provenance fields |
| `DisplayValues` | Traceable aggregate/display tables and chart source ranges |
| `Figure` | Neatly aligned embedded native Excel chart composition |

| Workbook | Panel layout | Chart XML parts | Native chart objects | Worksheet XML parts | Embedded media parts |
|---|---|---:|---:|---:|---:|
| Figure 2 | (a), (b), (c), vertical | 3 | 3 | 3 | 0 |
| Figure 3 | (a), (b), vertical | 2 | 2 | 3 | 0 |

All five chart objects use native chart series, axes, legends or data labels, worksheet-backed data references, and editable Excel formatting. Figure 2 panels (a) and Figure 3 panel (a) contain native error-bar XML for sample SD. No raster or SVG is embedded in either workbook.

## 6. Expected figure appearance

Figure 2 follows the accepted vertical three-panel structure:

- (a) V0/V2R/V3R FPS mean with sample SD error bars, absolute labels, and accepted `2.24×` / `+4.07%` comparisons.
- (b) V0/V2R/V3R pooled mean E2E latency with accepted `−55.45%` / `−4.03%` comparisons and `n=5400/路径` semantics.
- (c) grouped pooled P95/P99 values in V0/V2R/V3R order.

Figure 3 follows the accepted vertical two-panel structure:

- (a) five fixed-jitter independent-process FPS points per path plus mean/sample-SD summary markers and error bars.
- (b) independent-process mean/P95/P99 latency points for V2R and V3R, with fixed offsets used only for visual distinction and the accepted annotation `P95 +0.15%; P99 −0.12% / 方向相反`.

The accepted color-role mapping is retained: V0 gray, V2R blue, and V3R orange. Figure 2 also uses distinct native Excel patterns; Figure 3 uses square/circle/triangle marker roles. Excel rendering is expected to be visually close but not pixel-identical to Matplotlib.

## 7. Scientific non-regression

```text
PASS
```

Checks performed:

- Frozen CSV and JSON SHA-256 values matched before and after generation.
- Exactly 15 accepted independent processes were loaded: five each for V0, V2R, and V3R; each records 1080 measured frames.
- V0/V2R/V3R ordering was explicitly frozen in the builder and retained in all applicable panels.
- FPS mean and sample SD were independently recomputed from the CSV and matched the JSON authority to absolute tolerance `1e-10`.
- Pooled mean latency was independently recomputed from the five equal-sized process means and matched the JSON authority to absolute tolerance `1e-10`.
- Pooled P95/P99 values were read from the frozen JSON authority and were not reinterpreted as means of process-level percentiles.
- All process-level Figure 3 points trace directly to CSV rows; fixed horizontal offsets do not imply pairing.
- Display precision and comparisons trace directly to `publication_display_precision`.
- No confidence intervals, significance stars, paired-run inference, new scientific claim, or component-level causal attribution was introduced.
- Accepted Chinese labels, `P95 +0.15%`, `P99 −0.12%`, and `方向相反` are present in chart XML.

## 8. Structural validation

Builder command:

```bash
python3 docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py
```

Validation result:

```text
Figure2_E2E_performance.xlsx: XLSX ZIP PASS; sheets PASS; 3 chart XML parts; 3 native chart objects; 0 media parts
Figure3_run_level_distribution.xlsx: XLSX ZIP PASS; sheets PASS; 2 chart XML parts; 2 native chart objects; 0 media parts
Scientific non-regression: PASS
Consecutive rerun SHA comparison: PASS
```

The builder stops with `STOP_EXCEL_NATIVE_CHART_GENERATION_FAILURE` when an expected chart XML/drawing object is absent or its count is wrong. It stops with `STOP_SCIENTIFIC_NONREGRESSION_FAILURE` if a frozen authority changes during generation.

## 9. Manual copy instructions

For Figure 2 and Figure 3:

1. Open the `.xlsx` file in Microsoft Excel on Windows.
2. Go to the `Figure` sheet.
3. Select the chart composition carefully. Hold `Ctrl` while clicking chart borders to select all panel charts in that workbook if copying the composition together.
4. Copy the selected chart composition into the final Word submission file. Prefer **Keep Source Formatting & Embed Workbook** or **Paste Special → Microsoft Excel Chart Object** when available.
5. After pasting, verify that Word recognizes the result as an embedded Excel object or chart-capable object rather than a flat image, if possible. Double-clicking the pasted chart/object should expose editable chart data or Excel chart controls.

Also visually verify panel order, Chinese glyph rendering, legends, axis units, all absolute labels, error bars, and the Figure 3 mixed-tail annotation after opening in Microsoft Excel.

Final Word insertion is manual and is not part of this task. No Word document was modified.

## 10. Exact next action

On a Windows machine with Microsoft Excel and the final Word submission file, open `Figure2_E2E_performance.xlsx`, inspect and copy the three native charts from `Figure`, then repeat for `Figure3_run_level_distribution.xlsx`; paste them into the corresponding Figure 2 and Figure 3 positions in Word using an embedded/chart-capable paste option and perform the visual verification in Section 9.
