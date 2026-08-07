# Figure 3 deterministic specification

## Identity

- Candidate: `F3`
- Chinese title: `V0、V2R和V3R平均及尾延迟比较`
- English title: `Mean and Tail Latency Comparison of V0, V2R, and V3R`
- Artifact type: grouped bar chart
- Y-axis: `延迟/ms`
- Groups: `V0`; `V2R`; `V3R`
- Series: `mean`; `P95`; `P99`

## Frozen data

| Variant | Statistic | Metric ID | Raw value (ms) | Display value (ms) | Aggregation |
|---|---|---|---:|---:|---|
| V0 | mean | `M_R_V0_LAT_MEAN` | 18.2729918109 | 18.273 | pooled mean |
| V0 | P95 | `M_R_V0_P95` | 18.8541178 | 18.854 | pooled Type 7 P95 |
| V0 | P99 | `M_R_V0_P99` | 19.06830438 | 19.068 | pooled Type 7 P99 |
| V2R | mean | `M_R_V2R_LAT_MEAN` | 8.1402787896 | 8.140 | pooled mean |
| V2R | P95 | `M_R_V2R_P95` | 9.82713435 | 9.827 | pooled Type 7 P95 |
| V2R | P99 | `M_R_V2R_P99` | 11.52898548 | 11.529 | pooled Type 7 P99 |
| V3R | mean | `M_R_V3R_LAT_MEAN` | 7.8118285628 | 7.812 | pooled mean |
| V3R | P95 | `M_R_V3R_P95` | 9.8420113 | 9.842 | pooled Type 7 P95 |
| V3R | P99 | `M_R_V3R_P99` | 11.5153358 | 11.515 | pooled Type 7 P99 |

## Statistic semantics

All latency values are pooled 5400-sample frozen metrics. Mean, P95,
and P99 are three distinct statistics; the percentile bars are not
variance measures or error bars.

## Limitations

- Descriptive evidence from one Jetson platform, one frozen YOLOv8n
  INT8 Engine, 640 x 640 input, batch 1, and 180-image offline replay.
- Five processes per variant; no significance test.
- No power, resource, endurance, or real-camera result.
- No speedup, percentage, confidence interval, or significance
  annotation is included.
- V3R tail directions are mixed and V3R has no independent Gate D.

## Generation

The SVG is emitted by `scripts/paper/generate_phase3_results_figures.py`.
Its only data input is
`docs/paper/phase3/PAPER_PHASE3_SECTION4_RESULT_DATA_v1.0.csv`.
No reported result metric is recalculated.
