# Stage R R3 Unified V0/V2/V3/V4 Ablation Report

## Verdict

```text
R3_ABLATION_COMPLETE
R5_PARETO_EVALUATION_READY
```

The R3 comparability remediation is complete. Attempt 2 re-executed the frozen
20-run protocol with one unified benchmark harness: all four variants now run
through the same executable, the same single-thread inline loop, the same
pre-sink end-to-end timing boundary, the same Result JSON v4 generation, and
the same CPU sampling. Four variants completed with valid metrics and hashes;
all results are retained, including one documented OOM-kill anomaly and the
V4 long-tail outlier.

**Attempt 1 is retained but classified
`R3_ATTEMPT_1_NONCOMPARABLE_HARNESS` (diagnostic only). The paper's final
performance table may only cite Attempt 2.**

---

## Attempt 1 — non-comparable runner configuration (diagnostic only)

Classification: `R3_ATTEMPT_1_NONCOMPARABLE_HARNESS`
Evidence: `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v1/`
Disposition: `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v1/ATTEMPT_1_DISPOSITION.md`

### Why Attempt 1 cannot be a formal horizontal comparison

The 20 runs are real independent processes with valid Result JSON, hashes,
drop counts, and tegrastats logs. The blocker is the runner topology: V0
dispatched through `runtime::PipelineRunner` (four worker threads, bounded
queues, source prefetch) because `run_with_components` selects the pipeline
when the frozen V6 config declares `runtime_mode: pipeline`, while V2/V3/V4
executed through dedicated single-thread runners (`stage_r::PageableRunner`,
`stage_r::PinnedRunner`, `stage_r::DoubleBufferRunner`). The thread model,
prefetch behavior, and CPU profile of V0 therefore differ from the other
variants, so cross-variant performance deltas are confounded.

The confound is quantified by the unified rerun: the same V0 data path
measures 54.9 FPS under the unified single-thread harness versus 231.9 FPS
under PipelineRunner in Attempt 1 — the pipeline topology inflated V0
throughput by ~4.2x. Attempt 1's V0-vs-V2 sign flip (V2 appeared 45% slower
than V0; under the unified harness V2 is 130% faster than V0) is the direct
consequence of that topology mismatch.

### Retained elements

- All 20 runs, Result JSON, hash records, drop counts, latency distributions,
  tegrastats logs, and `artifact_sha256.txt` are untouched.
- V2/V3/V4 internal data remain as diagnostic reference.
- The approximately 8-second V4 latency outlier per run is retained.
- Attempt 1 must not enter the paper's final performance table.
- No production code, CUDA resize kernel, TensorRT engine behavior,
  postprocess, thresholds, Stage Q Evidence, or model were changed by either
  attempt.

---

## Attempt 2 — unified harness (formal ablation authority)

Classification: `R3_ATTEMPT_2_UNIFIED_HARNESS`
Evidence: `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/`
Status: `COMPLETE_UNIFIED_HARNESS_COMPARABLE`

### Unified harness design

One benchmark-only executable (`tools/benchmark/stage_r_r3_ablation_runner.cpp`)
runs all four variants. The harness shares:

- **Executable**: one `stage_r_r3_ablation_runner` binary; the variant is
  selected by the frozen per-variant config's `data_path.variant` field.
- **Loop**: one warmup pass (NullSink) followed by one measured pass, driven
  by the same `CorpusReplaySource` over the frozen 180-image manifest.
- **Thread/process model**: every variant executes a single-thread inline loop
  on the calling thread, pinned to CPUs 0-5. V0 runs through
  `runtime::SerialRunner` (CPU/OpenCV preprocessing → HostTensor → TensorRT
  INT8 → CPU postprocess); V2/V3/V4 run their existing Stage R runners
  (CUDA fused preprocessing with pageable raw, pinned raw, and two-slot
  double-buffer staging respectively). `PipelineRunner` is not used by any
  variant. This is the minimal V0 adapter: it reuses the existing
  Preprocessor, Stage Q TensorRT INT8 engine, PostProcessor, JsonSink,
  CanonicalHashSink, frozen manifest, and Result JSON v4; no production code
  was modified.
- **Timing**: one common benchmark-only wall-clock measurement per frame —
  `TimingSource` records the source pull instant and the `FanoutSink` records
  the pre-sink write instant, giving an identical pre-sink end-to-end latency
  for all four variants. Internal stage timings (`timing_ms` in V0's Result
  JSON) are preserved and are diagnostic only; no semantically different
  internal fields are compared across variants.
- **Sampling**: identical per-run tegrastats sampling, parsed by the same
  CPU-equivalent-cores logic.
- **Output**: identical Result JSON v4, run manifest, hashes, and metrics
  generation. A summary-pipeline fallback in the benchmark sink fills zero
  high-water marks so the single-thread V0 summary matches the V2/V3/V4
  convention; the pipeline summary fields are diagnostic only.

### Protocol

```text
device: Jetson Orin Nano Super
power mode: MAXN_SUPER, mode 2 (nvpmodel -m 2; same pinning as Attempt 1)
CPU affinity: 0-5 (taskset)
OpenCV threads: 1
queue: capacity 1, block (frozen config field; unused by the single-thread loop)
warmup: 60 frames per independent process
measurement: 1080 frames per run = 6 fixed 180-image cycles
runs: 5 independent processes per variant, 20 total
order: same deterministic interleaved order schedule as Attempt 1
  (set01 V0,V2,V3,V4 | set02 V4,V3,V2,V0 | set03 V2,V0,V4,V3 | set04 V3,V4,V0,V2 | set05 V0,V3,V2,V4)
drop policy: block
```

Frozen manifest `results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json`,
SHA-256 `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194`.
Entry identity: branch `feature/jetson-int8-data-path-optimization`, HEAD
`b789a672cf1ecbac4a4d7c25cb0c5a8575c5eba0`.

### Harness validation (short run)

Before the formal rerun, each variant executed one short run (10 warmup /
180 measured frames) under
`results/benchmark/stage_r/r3_unified_validation/`. All checks PASS:
Result JSON v4; processed frames = 180; drop count = 0; sequence order,
manifest path order, and 200x200 dimensions PASS; V2/V3/V4 detection SHA
identical; V0 detection SHA equals its official baseline; no silent CPU
preprocessing fallback. This step validated the harness only; no accuracy
evaluation was re-run.

### System anomaly and single permitted rerun

`set_01_v4` of the first formal pass was killed by the kernel OOM killer at
14:37:30 local (PID 22323, anon-rss 5.1 GiB on a 7.4 GiB system;
`journalctl` records `oom-kill ... task=stage_r_r3_abla`). The failure record
is retained in `failure.json` (`returncode: -9`). Per the R3 protocol, an
explicit system anomaly permits one rerun: `set_01_v4` was re-executed once
with the same command and environment and completed successfully; all other
runs were untouched. No code change resulted from the anomaly. The V4 variant
was not re-engineered.

### Formal results

Machine-readable values are in `per_run_metrics.json`, `aggregate_metrics.json`,
and `comparison_matrix.json`. All 20 runs report drop count 0 and Result
JSON v4.

| Variant | FPS mean | mean ms | median ms | P95 ms | P99 ms | min ms | max ms | stddev ms | CPU eq cores | drops |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 54.870 | 18.168 | 18.256 | 18.830 | 19.004 | 14.427 | 19.234 | 0.524 | 0.841 | 0 |
| V2 | 126.122 | 7.870 | 7.605 | 9.935 | 11.552 | 6.657 | 12.686 | 0.893 | 0.756 | 0 |
| V3 | 127.001 | 7.807 | 7.550 | 9.894 | 11.220 | 6.620 | 12.493 | 0.873 | 0.837 | 0 |
| V4 | 26.748 | 32.278 | 22.142 | 22.675 | 22.907 | 18.497 | 9324.231 | 285.467 | 1.001 | 0 |

Per-run FPS ranges: V0 54.38–55.28, V2 124.48–127.66, V3 126.10–127.84,
V4 26.22–26.97. Per-variant detection hashes are identical across all five
runs of each variant:

```text
V0: 12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2
V2: 0a668fd5937d83b28521a00847c9dd8567299697c8e1f5c1159b4e84fe81f5ed
V3: 0a668fd5937d83b28521a00847c9dd8567299697c8e1f5c1159b4e84fe81f5ed
V4: 0a668fd5937d83b28521a00847c9dd8567299697c8e1f5c1159b4e84fe81f5ed
```

V0 retains its official baseline detection SHA; V2/V3/V4 share the current
remediated R2 identity. Their tensor digest field references the current
R2 correctness authority
`0a9b8ead7235bcb340fb8e6eb45833c09b250f4384268d7082255b7dcb1d5d8f`.

### Comparison matrix

Machine-readable calculations in `comparison_matrix.json`
(interpretation status: `FORMAL_ABLATION_AUTHORITY`).

| Comparison | FPS difference | Relative FPS | Mean latency difference | Relative mean latency | P95 difference ms | P99 difference ms | CPU cores difference | Accuracy delta (mAP50) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V2 vs V0 | +71.263 | +129.87% | −10.298 ms | −56.68% | −8.895 | −7.452 | −0.084 | −0.00537575 |
| V3 vs V2 | +0.879 | +0.70% | −0.064 ms | −0.81% | −0.041 | −0.332 | +0.081 | 0 |
| V4 vs V3 | −100.253 | −78.94% | +24.471 ms | +313.47% | +12.781 | +11.686 | +0.163 | 0 |
| V4 vs V0 | −28.122 | −51.25% | +14.110 ms | +77.66% | +3.845 | +3.902 | +0.160 | −0.00537575 |

Implementation increments: V2 = CUDA fused preprocessing with pageable raw
staging; V3 = V2 plus long-lived pinned raw staging; V4 = V3 plus two pinned
raw/device slots with limited fixed alternation; V4 vs V0 = complete V0-to-V4
data-path increment.

Reading the matrix under identical harness semantics: V2's CUDA fused
preprocessing is ~2.3x the throughput of V0's CPU/OpenCV preprocessing at
−0.54 mAP50 percentage points; pinned staging (V3) is effectively neutral
relative to pageable (V2); the current two-slot double-buffer path (V4) is
substantially slower than both V0 and V2/V3. No variant is selected in R3;
Pareto selection is deferred to R5.

### Accuracy axis

The accuracy axis is inherited, not recomputed in R3. V2/V3/V4 detection SHA
equivalence is confirmed by this sampling; their accuracy deltas are:

```text
V0:  accuracy delta = 0
V2/V3/V4: mAP50 drop          = 0.00537575
          max class AP50 drop = 0.02673348
          max class Recall    = 0.03030303
```

### V4 long-tail outlier — retained, not removed

Every V4 run again contained a single-frame pre-sink latency spike
(max per run: 8977.0, 8991.8, 9173.9, 9241.9, 10236.6 ms versus a median of
~22.1 ms). The outlier is retained in the main statistics, appears in the
aggregates above (mean 32.278 ms, max 9324.2 ms), and was not removed,
capped, or treated as invalid. Per-stage attribution for the spike is not
available: V4 stage timings are disabled by design (enabling them would
perturb the measured path), so the spike is reported as a pre-sink
end-to-end latency event. This matches Attempt 1's observation (~8 s spikes)
and is recorded as real system behavior, not a V4 development trigger.

---

## Evidence

```text
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/experiment_manifest.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/per_run_metrics.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/aggregate_metrics.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/comparison_matrix.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/performance_accuracy_tradeoff.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/temperature_summary.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/failure.json          (OOM-kill record)
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/artifact_sha256.txt
results/benchmark/stage_r/r3_unified_validation/validation_summary.json   (harness validation)
```

`artifact_sha256.txt` covers the evidence directory contents except itself.
All JSON evidence parses successfully. The v2 aggregate files were rebuilt
from the per-run artifacts by `aggregate_stage_r_r3_ablation.py` and the
result matched the run-time aggregation (determinism PASS). Nothing was
pushed, merged, tagged, or used to create a PR.

## Scope audit

```text
Production implementation:      UNCHANGED
PipelineRunner:                 UNCHANGED
CUDA resize:                    UNCHANGED
Accuracy thresholds:            UNCHANGED
Attempt 1:                      RETAINED (classified R3_ATTEMPT_1_NONCOMPARABLE_HARNESS)
Stage Q Evidence:               UNCHANGED
```

Changes made for R3 are benchmark-only: the unified harness V0 adapter
(SerialRunner dispatch inside the ablation runner), the benchmark sink
summary-pipeline fallback, the `--validation-short` runner flag, orchestration
attempt/resume parameters, the new validation tool, and evidence/report
records. No production source, CUDA kernel, TensorRT engine, postprocess,
model, engine, thresholds, or Gate D definition was touched.

## Authorization

```text
R3:                          COMPLETE (R3_ABLATION_COMPLETE)
R5:                          READY only after comparable data obtained — comparable data obtained
Further implementation:      NOT AUTHORIZED
Push / Merge / Tag:          NOT EXECUTED
```
