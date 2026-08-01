# Stage R R1 Baseline and Profiling Report

## Verdict

R1 is `BLOCKED_PENDING_CAPTURE`: the V0 canonical and profiling perturbation
sub-gates pass, but the bounded Nsight capture has not been run. The initial
missing-tool blocker and subsequent capture-control defects are retained
below. R2 is not authorized by this report.

## Entry and environment

R0 entry matched the requested branch and commit chain:

- branch: feature/jetson-int8-data-path-optimization
- starting HEAD: d8d443d10d4b47d78769344d9d9aaef1a3a892a8
- HEAD^: 60a04a22bbfeae320312dd018f4ebfebae9eeafe
- HEAD^^ and merge-base with main: 4c67858610e14ba7d3c951b33f0948230451827f
- commits after baseline: 2
- worktree: clean at entry
- baseline aggregate: f7091e171ceb21a51ab051ac39c07294db209aca086f47a925c7dfd851062790
- environment aggregate: 0f601f7f76d90b66a0308a3fa884b6eb359155b46565777ef8a919bc9cfeddfa

Both R0 source-evidence links, SHA-256 values, statuses, tracked source
SHA/blob identities, and placeholder checks passed.

Measured environment was Jetson Orin Nano Super, MAXN_SUPER mode 2, CPU
affinity 0-5, OpenCV threads 1, automatic fan, and jetson_clocks not
invoked. The test corpus used the actual tracked
results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json; its
SHA is the frozen ea7616...1b194. The R0 manifest's logical
data/yolo/neu_det/test_manifest.json path is absent, but the aggregate source
evidence and expected SHA identify the tracked v2 manifest used here.

## Implementation

RuntimeConfig v5 now derives closed V0/off state internally. RuntimeConfig v6
adds strict data_path.variant (V0, V2, V3, V4) and profiling.mode (off,
diagnostic, formal) fields. Unknown fields, duplicate fields, missing fields,
and illegal enum values fail fast. V2/V3/V4 parse but are rejected before
source startup or TensorRT allocation.

The Phase Barrier is implemented by two same-process PipelineRunner invocations
sharing the loaded Engine, preprocessor, and postprocessor. Warmup uses a
discarding sink; measured creates fresh source/sinks and starts at sequence 0.
PipelineRunner return establishes EOS, drain, and four-worker join. TensorRT
run() already synchronizes after enqueue and after D2H, so the barrier records
the existing per_frame_synchronous_tensorrt_run_contract as CUDA-idle
authority and adds no global synchronization.

The narrow stage_r_experiment_runner validates exact arguments and output
conflicts, runs the warmup/measured phases, publishes result/hash/profiling
outputs atomically, and emits per-run manifests. Result JSON remains schema
v4. Diagnostic mode creates six reusable CUDA events only after warmup and
samples only the existing V0 stream. Off mode creates no events and emits no
samples.

The capture-control remediation adds `nvToolsExt.h` markers only around the
measured invocation. The CUDA Profiler API fallback adds one profiler start
and one profiler stop around the same measured invocation. After the measured
sink and its counter have been constructed, the exact order is:

```text
nvtxMarkA("stage_r.measured_phase_start")
cudaProfilerStart()
nvtxRangePushA("stage_r.measured")
measured phase
cudaProfilerStop()
nvtxMarkA("stage_r.measured_phase_end")
nvtxRangePop()
```

The NVTX calls and CUDA Profiler API calls are capture-boundary controls only.
The profiler calls are outside the measured timing interval; none participate
in throughput or latency calculations, and Result JSON v4 is unchanged.

## Baseline equivalence

Both v5 and v6 used warmup 180, measured 180, one complete cycle, queue
capacity 1, block, and drop count 0. Both detection SHA values equal the
frozen expected SHA:

12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2

Frame count, order, relative paths, dimensions, and per-frame detections were
identical. Result JSON v4 semantic fields were identical after excluding
runtime timing values, which are expected to vary between processes. Engine,
engine manifest, model contract, postprocess contract, pipeline metadata, and
warmup exclusion were verified.

## Profiling perturbation

The final measured runs used warmup 180 and measured 1800 frames (10 complete
cycles), with identical binary, Engine, corpus, and contract:

| mode | throughput FPS | mean pre-sink ms | samples |
|---|---:|---:|---:|
| off | 255.085 | 8.330720 | 0 |
| diagnostic | 258.034 | 8.628220 | 180 |

Derived diagnostic/off ratios are throughput 1.011560852 and latency
1.035711199; both gates pass. The result SHA remained
12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2.

## Component profiling and interpretation

Measured facts from 180 diagnostic samples: mean H2D 0.690427 ms, TensorRT
CUDA 2.806861 ms, D2H 0.099916 ms, host output construction 0.034835 ms,
and host roundtrip 3.705427 ms. CPU means from the measured Result JSON were
source 0.932768 ms, preprocess 3.652910 ms, synchronous host inference
roundtrip 3.762928 ms, postprocess 0.279609 ms, and pre-sink 8.628215 ms.
Pipeline queue wait means were source-to-preprocess 3.819664 ms,
preprocess-to-inference 1.011639 ms, and inference-to-postprocess 0 ms.

These are V0 measured facts. The engineering interpretation is that CPU
preprocessing and synchronous host-side inference roundtrip are substantial
parts of this V0 path. It is not a claim that V2/V3/V4 will improve
performance, and no cross-variant conclusion is authorized.

## Nsight

The initial R1 attempt was:

```text
R1_BLOCKED_NSIGHT_CAPTURE_FAILED
Reason: nsys command not found
```

Nsight Systems was subsequently installed from the configured Jetson source:
`nsight-systems-2024.5.4`, version `2024.5.4.34-245434855735v0`, architecture
`arm64`. The first post-install audit found the real control defect:
`stage_r_experiment_runner` had no measured NVTX capture boundary. This
remediation adds that boundary and passes the source/evidence contract tests.

The bounded Nsight capture is explicitly **NOT RUN** in this changeset. No raw
trace, capture duration, captured frame count, or CUDA activity observation is
claimed. The previous `NSYS_NVTX_CAPTURE_RANGE_UNRESOLVED` diagnosis is
retained; this changeset prepares the CUDA Profiler API fallback without
executing capture. Nsight is not treated as a formal throughput/latency
authority.

## Scope audit

- V2: NOT IMPLEMENTED
- V3: NOT IMPLEMENTED
- V4: NOT IMPLEMENTED
- CUDA fused preprocessing: NOT IMPLEMENTED
- Pinned raw staging: NOT IMPLEMENTED
- Device-input capability: NOT IMPLEMENTED
- Double Buffer: NOT IMPLEMENTED
- GPU NMS, Zero-Copy, mapped memory, generic BufferManager, and generic async inference API: NOT IMPLEMENTED
- Result JSON: v4 unchanged
- Stage Q configs and Evidence: unchanged
- R2-R6: not executed

## Tests and builds

- TensorRT-OFF build: PASS
- TensorRT-ON Release build: PASS
- RuntimeConfig v6 and sampling tests: PASS
- Pipeline and Stage P component regression tests: PASS
- Stage R runner help test: PASS
- TensorRT engine target compiled: PASS
- Stage R capture-control contract test: PASS (OFF and ON)
- Related CTest: PASS, 5/5 (OFF and ON)
- CUDA Profiler API boundary: one start/stop pair, measured-only, verified by
  the capture-control contract test
- Sanitizer: NOT CONFIGURED
- Nsight bounded capture: NOT RUN - explicitly deferred after control remediation

## Evidence

Tracked Evidence is under
results/validation/stage_r/r1_baseline_profiling_v1/. Full Result JSON and
raw per-sample output were local-only during analysis and were not included in
tracked Evidence.
