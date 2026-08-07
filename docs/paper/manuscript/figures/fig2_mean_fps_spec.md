# Figure 2 deterministic specification

## Identity

- Candidate: `F2`
- Chinese title: `V0、V2R和V3R平均帧率比较`
- English title: `Mean Frame-Rate Comparison of V0, V2R, and V3R`
- Artifact type: bar chart
- Y-axis: `平均帧率/FPS`

## Frozen data

| Variant | Mean metric ID | Raw mean | Display mean | SD metric ID | Raw SD | Display SD |
|---|---|---:|---:|---|---:|---:|
| V0 | `M_R_V0_FPS` | 54.5999763574 | 54.600 | `M_R_V0_FPS_SD` | 0.2233775769 | 0.223 |
| V2R | `M_R_V2R_FPS` | 122.1221922222 | 122.122 | `M_R_V2R_FPS_SD` | 0.4918299468 | 0.492 |
| V3R | `M_R_V3R_FPS` | 127.0972584510 | 127.097 | `M_R_V3R_FPS_SD` | 1.2792256601 | 1.279 |

## Error-bar semantics

Each error bar is the corresponding frozen FPS sample SD over five
process-level FPS values. It is not a confidence interval, standard
error, min-max range, or significance marker.

## Limitations

- Descriptive evidence from one Jetson platform, one frozen YOLOv8n
  INT8 Engine, 640 x 640 input, batch 1, and 180-image offline replay.
- Five processes per variant; no significance test.
- No power, resource, endurance, or real-camera result.
- No ratio, percentage, or superiority annotation is included.

## Generation

The SVG is emitted by `scripts/paper/generate_phase3_results_figures.py`.
Its only data input is
`docs/paper/phase3/PAPER_PHASE3_SECTION4_RESULT_DATA_v1.0.csv`.
No reported result metric is recalculated.
