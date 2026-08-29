# Excel Submission Figures Layout Tightening Report v1.0

## 1. Verdict

```text
PHASE_7_2D_J_EXCEL_LAYOUT_REMEDIATION_READY
```

This Phase 7.2D-J changeset only tightens the native Excel figure layout and reserves clear bottom-caption bands. It does not change frozen scientific data, statistical meaning, manuscript content, Word files, or Figure 1.

## 2. Baseline and files changed

| Item | Value |
|---|---|
| Branch | `main` |
| Baseline commit | `fe9cccac1fb3751453bc23783505c47e0679b581` |
| Baseline state | Exact Phase 7.2C-J HEAD at task start |
| Unrelated worktree item | Untracked `docs/paper/phase7/PAPER_PHASE7_2B_ALL_EQUATIONS_STANDARD_LATEX_v1.0.md`; preserved and excluded |
| Environment | Jetson Linux, Python 3.10.12, XlsxWriter 3.2.9 |

Files changed:

- `docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py`
- `docs/paper/submission_assets/excel/Figure2_E2E_performance.xlsx`
- `docs/paper/submission_assets/excel/Figure3_run_level_distribution.xlsx`
- `docs/paper/submission_assets/excel/reports/EXCEL_SUBMISSION_FIGURES_LAYOUT_TIGHTENING_REPORT_v1.0.md`

## 3. Panel-spacing tightening

The Phase 7.2C-J chart-object anchors left approximately seven worksheet rows between Figure 2 panels and eight rows between Figure 3 panels. Phase 7.2D-J reduces every inter-panel anchor gap to one row boundary. Because each preceding chart ends halfway through its final row, this is approximately a half-row visible gap rather than a full blank row.

| Workbook | Previous start/end rows | Final start/end rows | Final inter-panel row gaps |
|---|---|---|---|
| Figure 2 | starts `0,25,50`; ends `18,43,69` | starts `0,18,36`; ends `17,35,54` | `1,1` |
| Figure 3 | starts `0,29`; ends `21,50` | starts `0,20`; ends `19,40` | `1` |

Chart heights were reduced conservatively while retaining the same width:

- Figure 2: `370/370/390 px` → `350/350/370 px`.
- Figure 3: `420/430 px` → `390/410 px`.

The visible compositions are therefore materially shorter without placing chart objects on top of each other.

## 4. Bottom-caption clearance

All panel captions remain native X-axis titles below their corresponding charts. No caption was moved back to a top title or converted into a worksheet cell.

The obstruction fix uses explicit native plot-area layouts. Each plot body is shortened vertically to reserve a dedicated lower band for:

```text
plot body
→ category/metric labels
→ native X-axis panel caption
```

| Panel | Plot-area bottom fraction | Reserved chart fraction below plot | Bottom caption retained |
|---|---:|---:|---|
| Figure 2(a) | `0.75` | `0.25` | `(a) FPS（均值±样本SD；每路径5进程）` |
| Figure 2(b) | `0.75` | `0.25` | `(b) 合并样本平均 E2E 延迟（n=5400/路径）` |
| Figure 2(c) | `0.64` | `0.36` | `(c) 合并样本 P95 / P99（n=5400/路径）` |
| Figure 3(a) | `0.75` | `0.25` | `(a) 进程级 FPS（点：独立进程；横线/误差：均值±样本SD）` |
| Figure 3(b) | `0.73` | `0.27` | `(b) 进程级延迟比较（独立进程；横向偏移仅用于区分）` |

Figure 2(c) reserves the larger lower band because its legend remains at the accepted bottom position. In Figure 3(b), the pooled-tail annotation helper position moved upward from `7.55` to `7.72` only as a chart-layout coordinate, separating the annotation box from the metric-label/caption region; its scientific text and values are unchanged.

The builder now fails with `STOP_PANEL_CAPTION_CLEARANCE_FAILURE` if a chart lacks a manual plot layout or if its plot extends below `0.76` of the chart height. It fails with `STOP_EXCESSIVE_SPACING_REMEDIATION_FAILURE` if any inter-panel anchor gap exceeds one row.

## 5. Figure 3 category and axis sanity

```text
PASS
```

- Figure 3(a) still uses distinct worksheet-backed native labels `V0`, `V2R`, and `V3R` from `DisplayValues!$C$71:$C$73`.
- The numeric scatter X-axis labels remain hidden, so the conditional-format repeated-`V3R` defect cannot recur.
- The five fixed-jitter process points per path remain attached to their original category.
- Figure 3(a) FPS Y-axis format remains concise integer format `0`.
- Figure 3(b) latency Y-axis format remains concise one-decimal format `0.0`.
- Figure 3(b) native metric labels remain `均值`, `P95`, and `P99`.

## 6. Scientific non-regression

```text
PASS
```

Frozen authority hashes remained unchanged before and after regeneration:

| Authority | SHA-256 |
|---|---|
| `docs/paper/phase5_6/phase56b_run_level_metrics.csv` | `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` |
| `docs/paper/phase5_6/phase56b_publication_display_values.json` | `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655` |

The builder revalidated the five independent processes per path, FPS mean/sample SD, pooled mean latency, pooled P95/P99 authority semantics, accepted V0/V2R/V3R ordering, publication display values, and opposite-direction tail annotation. No numerical value, scientific interpretation, or claim changed.

## 7. Native Excel structure

```text
PASS
```

| Workbook | SHA-256 | Sheets | Native charts | Chart XML | Embedded media | Figure cells |
|---|---|---|---:|---:|---:|---:|
| `Figure2_E2E_performance.xlsx` | `1266c9ebf34da205b78334961908b0bd5616367083db77f12dfcba5e1860ce00` | RawRuns; DisplayValues; Figure | 3 | 3 | 0 | 0 |
| `Figure3_run_level_distribution.xlsx` | `4efaeae708f04f4c774cf74650c44bb58feb4a23c3c13ce21d8e7031fc514819` | RawRuns; DisplayValues; Figure | 2 | 2 | 0 | 0 |

Both workbooks retain worksheet-backed editable Excel chart series, drawing relationships, axes, error bars, data labels, legends, and native X-axis captions. The clean `Figure` sheets contain no worksheet cells and no raster/vector media payloads.

## 8. Validation command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py
```

The generated workbook hashes were stable across consecutive reruns.

## 9. Windows next action

Jetson/Linux OOXML validation cannot substitute for final Microsoft Excel rendering inspection. Verify caption clearance, helper-label position, legend order, font substitution, compact panel spacing, and Word copy/paste behavior on Windows.

```text
OPEN BOTH XLSX FILES IN MICROSOFT EXCEL AND CHECK THE FIGURE SHEETS, THEN TRY INSERTING THEM INTO WORD.
```
