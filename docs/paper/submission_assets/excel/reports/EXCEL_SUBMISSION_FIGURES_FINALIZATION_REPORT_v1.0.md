# Excel Submission Figures Finalization Report v1.0

## 1. Verdict

```text
PHASE_7_2C_J_EXCEL_FIGURES_FINAL_READY
```

This Phase 7.2C-J changeset is limited to native Excel presentation remediation. It does not change frozen scientific data, statistical meaning, manuscript content, Word files, or Figure 1.

## 2. Baseline and scope

| Item | Value |
|---|---|
| Branch | `main` |
| Accepted baseline commit | `35378e4c2828d717baec6fcdf5baed2373f934ef` |
| Baseline reconciliation | Exact HEAD match at task start |
| Unrelated worktree item | Untracked `docs/paper/phase7/PAPER_PHASE7_2B_ALL_EQUATIONS_STANDARD_LATEX_v1.0.md`; preserved and excluded |
| Environment | Jetson Linux, Python 3.10.12, XlsxWriter 3.2.9 |

Files in this changeset:

- `docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py`
- `docs/paper/submission_assets/excel/Figure2_E2E_performance.xlsx`
- `docs/paper/submission_assets/excel/Figure3_run_level_distribution.xlsx`
- `docs/paper/submission_assets/excel/reports/EXCEL_SUBMISSION_FIGURES_FINALIZATION_REPORT_v1.0.md`

The Phase 7.2B-J production report remains as historical production evidence and was not rewritten.

## 3. Panel-caption relocation

All panel labels and descriptions are now native Excel X-axis titles. They are part of their corresponding chart objects and will travel with a chart copied into Word. No panel caption is stored as an ordinary `Figure` worksheet cell.

| Panel | Top chart title/annotation | Native bottom X-axis panel caption |
|---|---|---|
| Figure 2(a) | `V0→V2R  2.24×；V2R→V3R  +4.07%` | `(a) FPS（均值±样本SD；每路径5进程）` |
| Figure 2(b) | `V0→V2R  −55.45%；V2R→V3R  −4.03%` | `(b) 合并样本平均 E2E 延迟（n=5400/路径）` |
| Figure 2(c) | None | `(c) 合并样本 P95 / P99（n=5400/路径）` |
| Figure 3(a) | None | `(a) 进程级 FPS（点：独立进程；横线/误差：均值±样本SD）` |
| Figure 3(b) | None | `(b) 进程级延迟比较（独立进程；横向偏移仅用于区分）` |

OOXML validation resolves the bottom axis of every chart and requires the exact caption above under its native `<c:title>` element. It separately rejects `(a)`, `(b)`, or `(c)` in any top chart title.

## 4. Figure 3 category correction

The Phase 7.2B-J scatter X-axis used this conditional numeric format:

```text
[=1]"V0";[=2]"V2R";"V3R"
```

Its fallback rendered non-matching numeric ticks as `V3R` in Windows Excel, producing repeated `V3R` labels.

The final builder now:

1. Keeps the original fixed-jitter numeric X positions and all measurements unchanged.
2. Hides the numeric scatter-axis tick labels.
3. Adds an invisible native helper series whose custom data labels reference `DisplayValues` cells.
4. Maps the three Figure 3(a) positions explicitly to `V0`, `V2R`, and `V3R`.
5. Uses the same native method for Figure 3(b) labels `均值`, `P95`, and `P99`, avoiding the same fallback defect there.

The Figure 3(a) OOXML contains these distinct worksheet-backed label references and cached values:

| Position | Cell reference | Native cached label |
|---:|---|---|
| 1 | `DisplayValues!$C$71` | `V0` |
| 2 | `DisplayValues!$C$72` | `V2R` |
| 3 | `DisplayValues!$C$73` | `V3R` |

This is a presentation mapping correction only. The 15 process-level points remain attached to their original V0/V2R/V3R groups.

## 5. Axis-format correction

| Figure/panel | Y-axis number format | Effect |
|---|---|---|
| Figure 3(a), FPS | `0` | Integer tick labels; no nine-decimal rendering |
| Figure 3(b), latency | `0.0` | Concise one-decimal latency ticks |

Axis limits and underlying numerical values were not changed to conceal formatting behavior.

## 6. Figure-sheet cleanup and layout

Engineering descriptions formerly written beside the composition were removed from both visible `Figure` worksheets. Their OOXML `<sheetData>` sections are empty: zero worksheet cells and only native chart drawings remain.

Figure 2 retains three vertically arranged chart objects; Figure 3 retains two. Chart heights and vertical anchors were adjusted only to reserve room for category labels followed by the native X-axis panel caption without excessive gaps.

## 7. Scientific non-regression

```text
PASS
```

Frozen authority hashes before and after generation:

| Authority | SHA-256 |
|---|---|
| `docs/paper/phase5_6/phase56b_run_level_metrics.csv` | `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` |
| `docs/paper/phase5_6/phase56b_publication_display_values.json` | `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655` |

The builder revalidated all prior contracts: five accepted independent processes per path, 1080 measured frames per process, FPS mean/sample SD parity, pooled mean-latency parity, pooled P95/P99 authority semantics, V0/V2R/V3R order, accepted display comparisons, and no new statistical claims.

Frozen displayed values remain:

- V0: 54.600 FPS; 18.273 ms pooled mean E2E latency.
- V2R: 122.122 FPS; 8.140 ms.
- V3R: 127.097 FPS; 7.812 ms.
- V0→V2R: 2.24× FPS; −55.45% mean latency.
- V2R→V3R: +4.07% FPS; −4.03% mean latency.
- P95: +0.15%; P99: −0.12%; directions remain opposite.

## 8. Native-chart and OOXML validation

Builder command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 docs/paper/submission_assets/excel/scripts/build_excel_submission_figures.py
```

| Workbook | SHA-256 | Worksheets | Native chart objects | Chart XML parts | Embedded media | Figure cells |
|---|---|---|---:|---:|---:|---:|
| `Figure2_E2E_performance.xlsx` | `1044f7eb7d5604046b22b0e09d805da9d9bbfb60dd4a88b987334c33476c355c` | RawRuns; DisplayValues; Figure | 3 | 3 | 0 | 0 |
| `Figure3_run_level_distribution.xlsx` | `f9cd4bac346978471c95ff819ada8c731e4120453588044be4b67fe347ac736e` | RawRuns; DisplayValues; Figure | 2 | 2 | 0 | 0 |

Both packages contain workbook, worksheet, drawing, drawing-relationship, and chart XML parts. Every chart series remains worksheet-backed. No PNG, SVG, screenshot, or other media payload is embedded.

## 9. Remaining Windows visual QA

Linux OOXML validation cannot claim the final Microsoft Excel rendering result. Windows visual QA remains required for font substitution, caption spacing, legend/caption order, helper-label position, and copy/paste behavior.

Exact next step:

```text
OPEN BOTH XLSX FILES IN MICROSOFT EXCEL AND VISUALLY VERIFY THE FIGURE SHEETS BEFORE INSERTING THEM INTO WORD.
```
