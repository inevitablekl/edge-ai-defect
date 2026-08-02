# Attempt 1 Disposition — R3_ATTEMPT_1_NONCOMPARABLE_HARNESS

Classification: `R3_ATTEMPT_1_NONCOMPARABLE_HARNESS`
Evidence directory: `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v1/`
Superceded by: `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/`
(Same 20-run protocol; unified runner semantics; formal ablation authority.)

## Why this record is not a formal horizontal comparison

The 20 independent runs were executed with real measurements, but V0
dispatched through `runtime::PipelineRunner` (four worker threads, bounded
queues, source prefetch), while V2/V3/V4 executed through dedicated
single-thread runners (`stage_r::PageableRunner`, `stage_r::PinnedRunner`,
`stage_r::DoubleBufferRunner`). The runner topology, thread model, and
prefetch behavior therefore differ between V0 and the other variants. The
pre-sink end-to-end latency and CPU sampling capture different execution
semantics for V0, so cross-variant performance deltas in this record are
confounded by runner topology and cannot support an isolated
preprocessing/staging ablation claim.

## What remains valid in this record

- All 20 runs are real independent processes (5 per variant, 60 warmup
  frames, 1080 measured frames per run, zero drops, Result JSON v4).
- Per-run Result JSON, hash records, drop counts, latency distributions,
  tegrastats logs, and artifact hashes are valid execution records.
- V2/V3/V4 internal comparisons and V0's own measurements are retained as
  diagnostic reference only.
- The approximately 8-second V4 latency outlier in each run is retained;
  it was not removed, treated as invalid, or used to justify code changes.
- Attempt 1 must not be cited in the paper's final performance table.
  The final table may only cite Attempt 2 (unified harness).

## Scope

No production code, CUDA resize kernel, TensorRT engine behavior,
postprocess, thresholds, Stage Q Evidence, or model were changed during
Attempt 1. Original data in this directory is not overwritten or rewritten.
