# Figure 4 — Run-Level Distribution and Tail Behavior

Status: `CANDIDATE / SPECIFICATION`
Future Chinese section/figure terminology: **运行级分布与尾延迟**. Do not use “长期稳定性” or imply thermal/frequency/statistical stability.

## Two-panel architecture

- (a) five independent process-level FPS points for each of V0, V2R, and V3R, with descriptive mean ± sample SD. Points are not connected.
- (b) five process-level Mean/P95/P99 latency points for V2R and V3R with fixed horizontal offsets. No set/run-ID pairing or connecting lines.
- The formal tail callout is separate: pooled 5400 samples/path, P95 `+0.15%`, P99 `−0.12%`, verdict `MIXED`.
- The V2R/V3R FPS and mean-latency ranges may support descriptive run-level repeatability and separation. Process P95/P99 points are descriptive only and do not replace pooled formal quantiles.
- Full-width target `16.0 cm`; markers plus outline and labels provide grayscale redundancy.

## Source-data contract

Input: `docs/paper/phase5_6/phase56b_run_level_metrics.csv`, SHA256 `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31`.

Required columns: `variant`, `run_id`, `execution_order`, `fps`, `mean_latency_ms`, `process_p95_ms`, `process_p99_ms`, `measured_frames`, `accepted`, and `independence_semantics`. Required population: 15 accepted rows, 5 per variant, 1080 frames per process. Candidate labels map `mean_latency_ms→Mean`, `process_p95_ms→P95`, and `process_p99_ms→P99`; these process quantiles remain descriptive.

The separate formal tail callout comes from `phase56b_publication_display_values.json` (SHA256 `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655`), whose pooled quantiles use 5400 frame samples/path.

## Interpretation guard

Observed V2R/V3R process ranges are non-overlapping for FPS (`121.443–122.759` versus `125.595–128.301`) and mean latency (`8.098–8.185 ms` versus `7.740–7.894 ms`). This supports a descriptive statement that the mean difference is not driven by one process. It does not establish statistical significance, long-term stability, thermal stability, or frequency stability.

## Candidate caption

**运行级分布与尾延迟。** (a) 展示每条路径5个独立进程的FPS及描述性均值与样本标准差；(b) 展示V2R/V3R各进程的平均、P95和P99延迟，横向偏移仅用于区分点且不表示配对。图中进程级尾延迟点用于描述分布；正式尾延迟结论来自每条路径5400帧的pooled统计，P95与P99变化方向相反，判定为MIXED。

## Candidate and D-B plan

- Candidate: `candidates/fig4_run_level_distribution_phase56_candidate.{svg,pdf,png}`
- Generator: `scripts/generate_phase56d_statistical_candidates.py` with fixed offsets, no random jitter.
- D-B output: reviewed SVG/PDF/PNG with candidate mark removed and terminology retained.
- Validation: exact row-count/source-hash assertions, no-line/no-pairing code review, deterministic rerun, raster inspection, and width proof.
- Integration target: future subsection headed `运行级分布与尾延迟` after aggregate results.
