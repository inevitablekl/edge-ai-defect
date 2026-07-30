# P7 Pipeline Stability Report

## 1 Verdict

`P7_PIPELINE_STABILITY_PASS`

The single bounded Pipeline lifecycle completed normally after the required
1800-second source-active interval. No rerun was performed.

## 2 Environment

- Platform: Jetson Codex, aarch64.
- Jetson: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super.
- L4T: R36.5.0.
- TensorRT runtime: 10.3.0.30-1+cuda12.5.
- CUDA runtime: 12.6.68.
- OpenCV: 4.5.4.
- Git HEAD: `cd5933353d0676dcf5517a318f389be99b246ab1`.
- Frozen engine, manifest, ModelContract, corpus manifest, and config identities
  are recorded in `environment/frozen_hashes.txt`.

## 3 Runtime Configuration

- Backend: TensorRT FP16.
- Runtime: Pipeline.
- Source: CorpusReplaySource.
- Cycle length: 180 frames.
- Queue capacity: 1.
- Drop policy: `block`.
- Sink: bounded CYCLE hash sink; no JsonSink.
- Trace: ConcurrentFrameTraceRecorder `AGGREGATE_ONLY`.
- Full per-frame trace and full detection storage were not retained.

## 4 Duration

- Start: `2026-07-31T00:44:50+08:00`.
- End: `2026-07-31T01:14:59+08:00`.
- Source-active duration: `1800.006143093 s`.
- Runner wall duration: `1800.026338449 s`.
- Source frames: `410691`.
- Processed images: `410691`.
- Complete cycles: `2281`.
- Partial cycle frames: `111`.
- Partial cycle was not used as a complete-cycle PASS.

## 5 Correctness Evidence

- Expected complete-cycle SHA-256:
  `6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3`.
- Complete cycle hash records: `2281`.
- Matching records: `2281`.
- Mismatching records: `0`.
- Partial-cycle SHA-256:
  `94dc5e99aa190a6b8df6e09f099384cee8a72b9239dbe8d6bd48fbcaa5442bfc`.
- Global sequence ended at `410690`; first and last corpus identities are
  recorded in `runtime/hash_summary.txt`.

Error gate result:

- crash: `0` — harness exit code `0`.
- deadlock: `0` — normal EOS and return completed.
- non-finite: `0` — timing validation and canonical hash processing completed
  without error.
- inference error: `0` — all `410691` frames processed successfully.
- drop: `0` — `source_frames == processed_images` under block policy.

## 6 Queue Lifecycle

- Q1: `CLOSED`, drained.
- Q2: `CLOSED`, drained.
- Q3: `CLOSED`, drained.
- Cancelled queues: `0`.
- High-water marks: `Q1=1`, `Q2=1`, `Q3=1`.

The lifecycle record is retained in `runtime/queue_lifecycle.txt`. Terminal
state is evidenced by normal EOS completion, successful runner return, zero
remaining output, and the PipelineRunner normal-EOS close propagation.

## 7 Worker Lifecycle

All four workers joined before the successful runner return. No worker error was
reported, and no interrupted or cancelled lifecycle was observed.

## 8 Resource Observation

- Process RSS observed range: approximately `13.4–356.9 MB`; the initial
  allocator/runtime growth settled at approximately `356.8 MB`.
- System RAM used by `tegrastats`: approximately `2237–2403 MB`.
- CPU observation: approximately `247–251%` during the steady-state run.
- GPU observation: approximately `77–82%` GR3D utilization during steady state.
- EMC, power, RAM, CPU, GPU, and temperature samples are retained in
  `telemetry/tegrastats.log` and `telemetry/process_resources.csv`.

This is a bounded-memory stability observation, not industrial leak
certification. The observed RSS plateau did not show unexplained continuous
monotonic growth after startup.

## 9 Thermal Limitation

`thermal_throttle_status=unavailable`.

Observed junction temperature was approximately `48.4–74.4°C`. Because the
thermal throttle interface was unavailable, this report does not claim
`no throttling PASS`.

## 10 Known Limitations

- Thermal throttle status could not be verified and is disclosed as unavailable.
- Queue terminal states are recorded from the normal-EOS lifecycle contract and
  successful runner completion; the production summary exposes high-water marks,
  not a separate terminal-state field.
- The TensorRT runtime emitted its existing cross-device engine-plan warning;
  the run nevertheless completed with exit code `0` and all correctness gates
  above passed.
- No industrial leak certification was performed.

## 11 Next Authorization

`P8_AUTHORIZED`

P8 was not executed by this task.
