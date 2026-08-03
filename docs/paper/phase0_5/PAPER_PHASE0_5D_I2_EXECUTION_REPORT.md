# Paper Phase 0.5D-I2 Execution Report

## 1. Verdict

`BLOCKED`

Frozen timing-aligned formal execution cannot complete with the current binary.
The runner accepts `FORMAL_AUTHORITY` and `60/1080`, but its measured source is
constructed with `cycles=1`. Because the manifest contains exactly 180 entries,
the measured run stops at 180 frames and is rejected by the runner's required
1080-frame validation. No code or configuration was changed, and no result-based
retry or parameter change was made.

## 2. Git State

Before execution:

```text
Branch: main
HEAD: 45cfd55bb2dba1a51a5f877bf02160292264b47e
Expected commit: 45cfd55
Source/config worktree: clean
```

After the blocked attempt, only generated benchmark artifacts and this report
are untracked. No tracked source or configuration file was modified.

## 3. Environment

| Item | Observation |
|---|---|
| Board | NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super |
| Architecture | aarch64 |
| L4T | R36.5 |
| CUDA | 12.6.11 / runtime 12.6.68 |
| TensorRT | 10.3.0.30 |
| OpenCV | 4.5.4 |
| Power mode | MAXN_SUPER, mode 2 |
| Process affinity | 0-5 |
| ZRAM | 6 zram devices, 0 used at preflight |
| Temperature | approximately 46-48°C at preflight |
| Clock state | `jetson_clocks --show` unavailable as non-root; this matches the prior frozen preflight record; no clock-setting command was invoked |

Pre-run configuration validation passed with common identity equality, three
variants, `timing_enabled=false`, `profiling_mode=off`, and 15 schedule
positions.

Frozen artifact identities observed:

```text
test manifest: ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194
engine manifest: 67f6ce3337d9c28c4aa2b32ba62554eaaa028f096c448041c063ec695f3b981c
model contract: 9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190
```

## 4. Run Schedule

The frozen schedule was not altered:

| Set | Position 1 | Position 2 | Position 3 |
|---|---|---|---|
| 1 | V0 | V2R | V3R |
| 2 | V3R | V2R | V0 |
| 3 | V2R | V0 | V3R |
| 4 | V0 | V3R | V2R |
| 5 | V2R | V3R | V0 |

Only Set 1 / Position 1 was attempted. The remaining 14 processes were not
started after the formal harness failure.

## 5. Per-Run Status

| Schedule position | Variant | Status | Observation |
|---|---|---|---|
| Set 1 / P1 | V0 | `IMPLEMENTATION_FAILURE` | Warmup 60 passed; measured output contained 180 instead of 1080; runner returned code 5 |
| Set 1 / P1 setup probe | V0 | `INCOMPLETE_SETUP` | An old external binary requiring `FORMAL_RUN` was rejected before execution; log retained and not used as evidence |
| Set 1 / P2 | V2R | `NOT RUN` | stopped by block |
| Set 1 / P3 | V3R | `NOT RUN` | stopped by block |
| Sets 2-5 | V0/V2R/V3R | `NOT RUN` | stopped by block |

The valid I1.5 binary accepted `FORMAL_AUTHORITY`, `warmup=60`, and
`measured=1080`. Its actual measured source call is equivalent to:

```text
CorpusReplaySource::create(..., cycles=1, ..., max_frames=1080)
```

With 180 manifest entries, this gives `min(180 * 1, 1080) = 180` frames.

The failed run artifacts are preserved under:

```text
results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/runs/set_01_p01_v0/
```

## 6. Aggregate FPS

`Not available — BLOCKED.`

The observed 180-frame result is invalid for the frozen 1080-frame formal
contract and is excluded from all aggregate metrics. No V0/V2R/V3R aggregate
FPS is reported.

## 7. Latency Mean/P95/P99

`Not available — BLOCKED.`

The failed run did not produce formal `metrics.json`; no latency statistic is
promoted or inferred from the partial Result JSON.

## 8. CPU Measurement

`Not available — BLOCKED.`

No valid formal process-wall interval and CPU measurement artifact was finalized.

## 9. Correctness Identity

No formal correctness identity was accepted. The partial V0 Result JSON had
180 frames and was rejected before hashes and run manifest finalization. It
cannot establish the required 1080-frame order/count, five-run identity, or
V0/V2R/V3R comparison identity.

The following preconditions did pass before execution:

```text
V0/V2R/V3R config identity: PASS
timing.enabled=false: PASS
profiling.mode=off: PASS
manifest SHA: PASS
engine/model artifact identity: PASS
```

## 10. Limitations

- Formal performance comparison was not completed.
- No aggregate or paper performance conclusion is valid.
- The current execution binary must be corrected so the measured source emits
  six complete 180-image cycles for 1080 measured frames.
- That correction requires an explicitly authorized code change; it was not made
  in Phase 0.5D-I2.
- The old binary setup failure and the partial formal V0 failure remain preserved;
  neither was discarded or rerun based on performance.

## 11. Commit/Tag Status

```text
HEAD remains: 45cfd55
New commit: none
New tag: none
Push/merge: none
```

Recommended next actor: `Paper Project Manager`, to authorize a focused harness
remediation before any further formal benchmark execution.
