# Excel Submission Figures Canvas Tightening Report v1.0

## 1. Verdict

```text
PHASE_7_2E_J_EXCEL_CANVAS_TIGHTENING_READY
```

This Phase 7.2E-J changeset only tightens the internal native-chart canvas and explicitly separates bottom captions from X-axis elements. Frozen scientific data, statistical meaning, manuscript content, Word files, and Figure 1 remain unchanged.

## 2. Baseline and files changed

| Item | Value |
|---|---|
| Branch | `main` |
| Baseline commit | `adc787cfbe8bf7ae1f874295d65e79f7a3bd99bc` |
| Baseline state | Exact Phase 7.2D-J HEAD at task start |
| Unrelated worktree item | Untracked `docs/paper/phase7/PAPER_PHASE7_2B_ALL_EQUATIONS_STANDARD_LATEX_v1.0.md`; preserved and excluded |
| Environment | Jetson Linux, Python 3.10.12, XlsxWriter 3.2.9 |

Files changed:

- `docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py`
- `docs/paper/submission_assets/excel/Figure2_E2E_performance.xlsx`
- `docs/paper/submission_assets/excel/Figure3_run_level_distribution.xlsx`
- `docs/paper/submission_assets/excel/reports/EXCEL_SUBMISSION_FIGURES_CANVAS_TIGHTENING_REPORT_v1.0.md`

## 3. Left-whitespace reduction

The plot area was expanded leftward inside every native chart object while preserving room for the Y-axis title and ticks. The useful plot width also grew toward the unchanged 97% right edge.

| Workbook/panels | Previous plot left | Final plot left | Previous plot width | Final plot width | Final plot right |
|---|---:|---:|---:|---:|---:|
| Figure 2(a–c) | `0.13` | `0.10` | `0.82` | `0.87` | `0.97` |
| Figure 3(a–b) | `0.15` | `0.11` | `0.80` | `0.86` | `0.97` |

This primarily corrects the chart-object bounding box rather than merely moving chart anchors on the worksheet. The builder now stops with `STOP_CHART_CANVAS_TIGHTENING_FAILURE` if a generated plot starts to the right of `0.111` or ends before `0.969` of chart width.

## 4. Bottom-whitespace reduction

Useful plot height increased while the enclosing chart objects became shorter:

| Panel | Previous plot bottom | Final plot bottom | Previous height | Final height |
|---|---:|---:|---:|---:|
| Figure 2(a) | `0.75` | `0.78` | 350 px | 335 px |
| Figure 2(b) | `0.75` | `0.78` | 350 px | 335 px |
| Figure 2(c) | `0.64` | `0.68` | 370 px | 355 px |
| Figure 3(a) | `0.75` | `0.78` | 390 px | 370 px |
| Figure 3(b) | `0.73` | `0.76` | 410 px | 390 px |

Figure 2(c) continues to reserve more lower space than the other panels because its accepted legend remains below the native X-axis caption. Inter-panel anchor gaps remain at the compact Phase 7.2D-J value of one row boundary; no large vertical gaps were reintroduced.

## 5. Native caption separation

All `(a)/(b)/(c)` captions remain native Excel X-axis titles below their panels. Phase 7.2E-J replaces automatic axis-title placement with explicit chart-relative X/Y positions.

The horizontal positions were centered using 9-point compatible CJK font-metric estimates in the Jetson environment. The vertical positions create a measured separation between plot bottom and caption while leaving limited safe padding below the caption; Microsoft Excel visual centering remains part of the Windows check.

| Panel | Caption X/Y | Plot-to-caption clearance | Native bottom caption |
|---|---|---:|---|
| Figure 2(a) | `0.34 / 0.88` | `0.10` | `(a) FPS（均值±样本SD；每路径5进程）` |
| Figure 2(b) | `0.33 / 0.88` | `0.10` | `(b) 合并样本平均 E2E 延迟（n=5400/路径）` |
| Figure 2(c) | `0.34 / 0.75` | `0.07` | `(c) 合并样本 P95 / P99（n=5400/路径）` |
| Figure 3(a) | `0.26 / 0.88` | `0.10` | `(a) 进程级 FPS（点：独立进程；横线/误差：均值±样本SD）` |
| Figure 3(b) | `0.28 / 0.87` | `0.11` | `(b) 进程级延迟比较（独立进程；横向偏移仅用于区分）` |

Figure 3 therefore follows the required internal order: useful plot, worksheet-backed native category/metric labels, a 10–11% chart-height clearance, then the native caption. The builder requires every caption to have a native manual layout, at least `0.065` plot-to-caption clearance, and a Y position no lower than `0.89`; otherwise it stops with `STOP_PANEL_CAPTION_SEPARATION_FAILURE`.

## 6. Figure 3 regression safety

```text
PASS
```

- Figure 3(a) retains distinct worksheet-backed `V0`, `V2R`, and `V3R` native labels from `DisplayValues!$C$71:$C$73`.
- Numeric scatter X-axis labels remain hidden; repeated conditional-format `V3R` labels cannot recur.
- All 15 fixed-jitter process observations remain under their original path identities.
- FPS Y-axis format remains concise `0`; latency remains `0.0`.
- Figure 3(b) retains `均值`, `P95`, `P99`, `P95 +0.15%`, `P99 −0.12%`, and `方向相反`.

## 7. Native chart preservation

```text
PASS
```

| Workbook | SHA-256 | Sheets | Native charts | Chart XML | Embedded media | Figure cells |
|---|---|---|---:|---:|---:|---:|
| `Figure2_E2E_performance.xlsx` | `b9df80c01ea7234c08b193abaa8e74f0da616bd35460ab1632ec50d3a71de0ad` | RawRuns; DisplayValues; Figure | 3 | 3 | 0 | 0 |
| `Figure3_run_level_distribution.xlsx` | `d8dee06036cd25474fb323c115eb898c1c5fa83a0bebec539966fec4cd833f71` | RawRuns; DisplayValues; Figure | 2 | 2 | 0 | 0 |

Both workbooks retain worksheet-backed editable chart series, native axes and captions, error bars, data labels, legends, drawing parts, and drawing relationships. No image or screenshot was introduced.

## 8. Scientific non-regression

```text
PASS
```

| Frozen authority | SHA-256 |
|---|---|
| `docs/paper/phase5_6/phase56b_run_level_metrics.csv` | `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` |
| `docs/paper/phase5_6/phase56b_publication_display_values.json` | `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655` |

The builder verified the frozen source hashes before and after regeneration and rechecked all prior aggregation, order, display-value, process-independence, pooled-tail, and annotation contracts. No scientific value, direction, claim, or interpretation changed.

## 9. Validation command

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py
```

Consecutive regeneration produced identical workbook hashes.

## 10. Windows next action

Jetson/Linux OOXML validation cannot replace final Microsoft Excel visual inspection. Check internal centering, Y-axis clearance, caption positions, legend ordering, font substitution, and Word copy/paste behavior on Windows.

```text
OPEN BOTH XLSX FILES IN MICROSOFT EXCEL, CHECK THE FIGURE SHEETS, AND TEST INSERTION INTO WORD.
```
