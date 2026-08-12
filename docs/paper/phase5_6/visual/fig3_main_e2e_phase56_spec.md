# Figure 3 — Main E2E Performance

Status: `CANDIDATE / SPECIFICATION`
Scientific role: headline aggregate performance figure. It replaces neither frozen evidence nor the current production figure in D-A.

## Three-panel architecture

- (a) V0/V2R/V3R process-level FPS mean with sample SD across five independent processes per path. Small annotations: `2.24×` and `+4.07%`.
- (b) absolute pooled mean E2E latency for 5400 frame samples per path. Small annotations: `−55.45%` and `−4.03%`.
- (c) absolute pooled P95/P99 E2E latency for V0/V2R/V3R, 5400 frame samples per path. No magnified relative-difference inset.
- Full-width target `16.0 cm`; color plus hatch/outline/labels; absolute values shown to three decimals.

## Source-data contract

| Input | Required content | Rows / aggregation | Authority / SHA256 |
|---|---|---|---|
| `../phase56b_run_level_metrics.csv` | `variant`, `fps`, `mean_latency_ms`, `process_p95_ms`, `process_p99_ms`, `measured_frames`, `accepted` | 15 rows; exactly 5 accepted independent processes and 1080 frames per path; FPS mean and sample SD only | governed Level-B process source; `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` |
| `../phase56b_publication_display_values.json` | `mean_fps`, `sample_sd_fps`, pooled mean/P95/P99 and display comparisons | pooled latency statistics over 5400 frame samples/path; candidate script verifies process aggregates against the frozen values | derived publication authority; `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655` |

Manual bar-height entry is prohibited. P95/P99 are not the mean of five process percentiles.

## Candidate caption

**三条受控路径的端到端性能。** (a) 柱高为每条路径5个独立进程FPS的均值，误差棒为进程级样本标准差；(b) 为每条路径5400帧的pooled平均端到端延迟；(c) 为相同pooled样本的P95和P99端到端延迟。比较值描述完整路径差异，不构成对单一组件的因果归因。

## Candidate and D-B plan

- Candidate: `candidates/fig3_main_e2e_phase56_candidate.{svg,pdf,png}`
- Generator: `scripts/generate_phase56d_statistical_candidates.py`
- D-B output: reviewed manuscript-ready SVG/PDF/PNG, with the same frozen inputs and aggregation assertions.
- Validation: schema/row-count/hash assertions, recomputation tolerance, deterministic hash rerun, 300-DPI raster inspection, and `16.0 cm` proof.
- Integration target: principal results subsection.
