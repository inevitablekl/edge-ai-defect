# Paper Phase 0.5D-I2 Execution Report

## 1. Verdict

`TIMING_ALIGNED_RERUN_PASS`

All 15 frozen formal processes completed successfully: V0, V2R, and V3R each
ran five times with 60 warmup frames and 1080 measured frames. No run was
retried, discarded, reordered, or changed in response to results.

## 2. Git State

```text
Branch: main
HEAD: 6885dc5c8d1099c34f1cd8d10c4b30426df61daf
Expected HEAD: 6885dc5
Source/config before execution: clean
```

The benchmark used the frozen post-fix binary and did not modify source or
configuration files. The prior pre-fix failure record remains preserved under
the existing `runs/set_01_p01_v0/` directory; this formal execution used new
directories under `formal_runs/`.

## 3. Environment

| Item | Observed value |
|---|---|
| Board | NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super |
| Architecture | aarch64 |
| L4T | R36.5 |
| CUDA | 12.6.11 / runtime 12.6.68 |
| TensorRT | 10.3.0.30 |
| OpenCV | 4.5.4 |
| Power mode | MAXN_SUPER, mode 2 |
| Process affinity | 0-5 |
| Input | frozen NEU-DET test manifest, 180 images |
| ZRAM | six zram devices, 0 used at pre-run observation |
| Temperature | approximately 46.8-47.1°C pre-run; 48.7-49.6°C post-run |
| Clock state | `jetson_clocks --show` unavailable as non-root; no clock-setting command invoked |

The same non-root clock observation was present in the frozen preflight record.
No dependency, engine, calibration, model, or environment setting was changed.

Frozen artifact hashes:

```text
engine:         8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee
engine manifest: 67f6ce3337d9c28c4aa2b32ba62554eaaa028f096c448041c063ec695f3b981c
model contract: 9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190
test manifest:  ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194
runner binary:  e58fa95efd05aab33d29b38f200fac10c16fbdc2a474490f0cc7d41325f5ee0c
```

## 4. Run Schedule

The frozen interleaved schedule was executed exactly:

| Set | Process 1 | Process 2 | Process 3 |
|---|---|---|---|
| 1 | V0 | V2R | V3R |
| 2 | V3R | V2R | V0 |
| 3 | V2R | V0 | V3R |
| 4 | V0 | V3R | V2R |
| 5 | V2R | V3R | V0 |

Result root:

```text
results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_runs/
```

## 5. Per-Run Result

All rows are valid formal runs. FPS is measured frames divided by the runner's
recorded measured process-wall interval. Latency values are the external
source-to-pre-sink samples in milliseconds.

| Run | Variant | FPS | Latency mean | P95 | P99 | CPU equiv. cores | Frames | Drop | Identity |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| set_01_p01 | V0 | 54.484 | 18.312 | 18.827 | 19.078 | 0.673 | 1080 | 0 | PASS |
| set_01_p02 | V2R | 122.395 | 8.122 | 9.831 | 11.454 | 0.568 | 1080 | 0 | PASS |
| set_01_p03 | V3R | 128.064 | 7.754 | 9.792 | 11.768 | 0.590 | 1080 | 0 | PASS |
| set_02_p01 | V3R | 125.595 | 7.894 | 9.684 | 10.665 | 0.574 | 1080 | 0 | PASS |
| set_02_p02 | V2R | 122.002 | 8.148 | 9.818 | 11.629 | 0.559 | 1080 | 0 | PASS |
| set_02_p03 | V0 | 54.846 | 18.192 | 18.761 | 19.064 | 0.671 | 1080 | 0 | PASS |
| set_03_p01 | V2R | 121.443 | 8.185 | 9.858 | 11.554 | 0.564 | 1080 | 0 | PASS |
| set_03_p02 | V0 | 54.289 | 18.377 | 18.910 | 19.102 | 0.676 | 1080 | 0 | PASS |
| set_03_p03 | V3R | 128.301 | 7.740 | 9.866 | 11.472 | 0.581 | 1080 | 0 | PASS |
| set_04_p01 | V0 | 54.612 | 18.268 | 18.840 | 19.029 | 0.673 | 1080 | 0 | PASS |
| set_04_p02 | V3R | 125.846 | 7.893 | 9.985 | 11.501 | 0.579 | 1080 | 0 | PASS |
| set_04_p03 | V2R | 122.012 | 8.148 | 9.850 | 11.495 | 0.564 | 1080 | 0 | PASS |
| set_05_p01 | V2R | 122.759 | 8.098 | 9.768 | 11.507 | 0.566 | 1080 | 0 | PASS |
| set_05_p02 | V3R | 127.680 | 7.778 | 9.847 | 11.521 | 0.584 | 1080 | 0 | PASS |
| set_05_p03 | V0 | 54.769 | 18.215 | 18.851 | 19.055 | 0.671 | 1080 | 0 | PASS |

## 6. Aggregate Metrics

FPS mean and sample standard deviation are calculated over the five valid run
FPS values for each variant. Latency P95/P99 are calculated over the pooled
5400 measured-frame samples for each variant.

| Variant | Valid runs | FPS mean ± SD | FPS min-max | Latency mean | P95 | P99 | CPU equiv. cores mean ± SD |
|---|---:|---:|---:|---:|---:|---:|---:|
| V0 | 5 | 54.600 ± 0.223 | 54.289-54.846 | 18.273 ms | 18.854 ms | 19.068 ms | 0.673 ± 0.002 |
| V2R | 5 | 122.122 ± 0.492 | 121.443-122.759 | 8.140 ms | 9.827 ms | 11.529 ms | 0.564 ± 0.003 |
| V3R | 5 | 127.097 ± 1.279 | 125.595-128.301 | 7.812 ms | 9.842 ms | 11.515 ms | 0.581 ± 0.006 |

Descriptive pairwise ratios from these valid runs:

| Comparison | FPS ratio | Mean latency ratio | CPU ratio |
|---|---:|---:|---:|
| V2R / V0 | 2.237x | 0.445x | 0.838x |
| V3R / V0 | 2.328x | 0.428x | 0.864x |
| V3R / V2R | 1.041x | 0.960x | 1.031x |

## 7. Latency Statistics

The primary latency boundary was identical for all variants: immediately before
source pull through preprocessing, TensorRT execution, postprocessing, and
frame-result construction, ending before sink serialization/write. JSON
serialization, file I/O, digest finalization, and summary persistence were
excluded. `timing.enabled=false` and `profiling=off` were effective in every run;
no internal or per-frame timing field was present.

## 8. CPU Measurement

CPU measurement was available uniformly from the runner's
`CLOCK_PROCESS_CPUTIME_ID` over the measured process-wall window. The report
uses CPU equivalent cores (`process_cpu_ms / process_wall_ms`), not a claim of
instantaneous system CPU utilization.

## 9. Correctness Identity

All 15 runs passed independent artifact validation:

```text
warmup frames: 60 per run
measured frames: 1080 per run
processed frames: 1080 per run
drop count: 0 per run
EOS / worker join: PASS per run
Result schema: v4, identical field set
timing_enabled_config: false for all runs
timing_enabled_metadata: false for all runs
profiling_mode: off for all runs
internal_timing_fields: false for all runs
per_frame_timing_field: false for all runs
```

Every run produced the same detection SHA:

```text
788d5a8917ed9574e1b1d6419187dd44fd03cfbfd67aecfe7bb9888b60ccdc0f
```

The config validator passed with the only intentional configuration difference
being `data_path.variant`; engine, engine manifest, model contract, test
manifest, thresholds, NMS, input size, batch, timing, profiling, and output
contracts were common.

## 10. Limitations

- Results are descriptive for this Jetson platform, frozen model, engine, and
  180-image replay workload; no statistical significance or universality claim
  is made.
- CPU equivalent-core data is process CPU time, not full resource monitoring.
- GPU utilization, power, and long-term stability were not measured by this
  timing-aligned protocol.
- `jetson_clocks --show` requires root and was unavailable; no clock-setting
  command was invoked. This limitation matches the frozen preflight record.
- The prior pre-fix failed attempt remains historical evidence and is excluded
  from these 15 valid post-fix formal runs.

## 11. Commit/Tag Status

```text
HEAD: 6885dc5c8d1099c34f1cd8d10c4b30426df61daf
New commit: none
New tag: none
Push/merge: none
```

No code or configuration was modified during benchmark execution.
