# Paper Phase 0.5D-I2 Minimal Fix Report

## 1. Verdict

`COMPLETE`

The frozen formal runner now replays the 180-image manifest for the required
number of cycles. V0, V2R, and V3R each completed one capability validation with
60 warmup frames and 1080 measured frames. The formal 15-run benchmark was not
executed.

## 2. Root Cause

The runner passed `cycles=1` to `CorpusReplaySource` for both warmup and measured
sources. The source therefore exposed at most one 180-image cycle, so the
measured phase produced `180/1080` frames and was rejected by the existing
count check.

The minimal fix computes the required replay cycles from the requested frame
count and the frozen 180-image manifest length:

```text
warmup=60   -> 1 cycle, max_frames=60
measured=1080 -> 6 cycles, max_frames=1080
```

## 3. Changed Files

- `tools/benchmark/stage_r_phase0_5d_timing_aligned_runner.cpp`
  - added the minimal `replay_cycles_for()` calculation;
  - passed the calculated cycle count to warmup and measured
    `CorpusReplaySource` instances.
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_MINIMAL_FIX_REPORT.md`

The prior `PAPER_PHASE0_5D_I2_EXECUTION_REPORT.md` BLOCKED report was preserved
and committed as historical execution evidence; it was not modified by the fix.

No configuration file was modified.

## 4. Validation

### Build

PASS:

```bash
cmake --build /home/orin/edge-ai-local-build/paper_phase0_5d_i1 \
  --target stage_r_phase0_5d_timing_aligned_runner \
           stage_r_phase0_5d_config_validator -j2
```

### Existing focused tests

PASS, 6/6:

```text
runtime_config
stage_r_runtime
stage_r_cuda_preprocess
stage_r_capture_control
result_sinks
serial_runner
```

### Config identity

PASS:

```text
common_identity_equal=true
variants=V0,V2R,V3R
variant-only difference=data_path.variant
timing_enabled=false
profiling_mode=off
schedule_positions=15
```

### 60/1080 capability validation

Each variant was executed once with `FORMAL_AUTHORITY`, `warmup=60`, and
`measured=1080`. No 15-run benchmark was executed.

| Variant | Return | Warmup | Measured | Drop | EOS | Timing | Profiling | Result schema | Latency samples | Detection SHA |
|---|---:|---:|---:|---:|---|---|---|---:|---:|---|
| V0 | 0 | 60 | 1080 | 0 | PASS | false | off | v4 | 1080 | `788d5a8917ed9574e1b1d6419187dd44fd03cfbfd67aecfe7bb9888b60ccdc0f` |
| V2R | 0 | 60 | 1080 | 0 | PASS | false | off | v4 | 1080 | same as V0 |
| V3R | 0 | 60 | 1080 | 0 | PASS | false | off | v4 | 1080 | same as V0 |

All three run manifests also reported `timing_enabled_config=false`,
`timing_enabled_metadata=false`, `internal_timing_fields=false`, and
`per_frame_timing_field=false`.

These are capability-validation runs, not formal performance aggregates.

## 5. Scope Compliance

Confirmed unchanged:

```text
timing boundary
timing.enabled behavior
profiling behavior
V0/V2R/V3R dispatch
TensorRT
CUDA preprocessing
V2R semantic contract
model / engine
postprocess
benchmark protocol
```

No benchmark framework, retry system, scheduler, or statistics module was added.

## 6. Commit

```text
fix(stage-r): repeat replay corpus for formal measured frames
```

## 7. Git Status

HEAD before fix: `45cfd55`.

After the fix commit, no source or configuration changes remain. No push, merge,
or tag was performed.

## 8. Recommended Next Actor

`Paper Project Manager`

The next actor may authorize the frozen 15-run Phase 0.5D-I2 formal benchmark.
