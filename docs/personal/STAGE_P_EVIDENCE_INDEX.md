# Stage P Evidence Index

## Scope

This index closes the Stage P P4–P7 evidence chain. The raw Evidence remains
local-only under `results/validation/stage_p/` and
`results/benchmark/stage_p/`; large traces, telemetry, generated video, and
other raw runtime artifacts are intentionally not part of the documentation
commit.

The index records the source commit used by each execution, the relevant
artifact or hash identity, the verdict, and the experiment purpose. Historical
attempts remain preserved and are not reinterpreted here unless an explicit
P5R reclassification is the governing status.

## Frozen identities

| Identity | SHA-256 |
|---|---|
| TensorRT FP16 Engine | `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc` |
| Engine manifest | `39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63` |
| ModelContract | `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190` |
| Frozen corpus manifest | `fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8` |
| P4 expected CYCLE SHA | `6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3` |

## Evidence inventory

| Phase | Evidence path | Source commit | Key SHA / identity | Verdict | Experiment purpose |
|---|---|---|---|---|---|
| P4 | `results/validation/stage_p/p4_correctness_v1/attempt_009/` | `d45342e0c9224df4521fae6db97555fd4257ae24` | RUN `d0f5275824e2359cd80f6428bbfb7249e058eb72173bc9a124d8890bc30dd1a5`; CYCLE `6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3` | `P4_PIPELINE_CORRECTNESS_PASS` | Verify Serial and Pipeline exact Detection identity and normal bounded-queue lifecycle over the frozen 180-frame corpus. |
| P5 pilot | `results/benchmark/stage_p/p5_queue_pilot_v1/attempt_001/` | `d45342e0c9224df4521fae6db97555fd4257ae24` | Selected queue capacity `1`; pilot complete-cycle hashes match P4 expected | Included in P5R final status | Select the smallest eligible queue capacity from capacities 1, 2, and 4. |
| P5 formal | `results/benchmark/stage_p/p5_serial_vs_pipeline_v1/attempt_001/` and `results/benchmark/stage_p/p5_serial_vs_pipeline_v1/P5_FINAL_RECLASSIFICATION_REPORT.md` | `d45342e0c9224df4521fae6db97555fd4257ae24` | Formal RUN `7e115aa5661f38864955bb9eb7481e86290d0a0cb55e6c308270401d683cd929`; complete CYCLE SHA matches P4; paired ratio mean `4.165718` | `P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE` | Compare Serial and Pipeline throughput under the frozen three-pair, 5100-accepted-frame protocol. |
| P6 | `results/validation/stage_p/p6_video_v1/` (formal Evidence: `attempt_002/`) | `cd5933353d0676dcf5517a318f389be99b246ab1` | Video `8c1967dc0de607a72ef40525d91dbcddec05ebd7ada094188204fd2942c7cf69`; Serial/Pipeline RUN `932853ac5a5c8a8e210a689b6b83d3751b8b0b6f261849b18dfbbd781a04207b` | `P6_VIDEO_SOURCE_PASS` | Validate deterministic MJPG VideoFileSource input through production Serial and Pipeline paths. |
| P7 | `results/validation/stage_p/p7_stability_v1/attempt_001/` | `cd5933353d0676dcf5517a318f389be99b246ab1` | 1800.006143093 s source-active; 410691 processed frames; 2281 complete cycles; expected CYCLE SHA matches all complete cycles | `P7_PIPELINE_STABILITY_PASS` | Observe one bounded Pipeline lifecycle for 1800 seconds with no crash, deadlock, drop, inference error, or non-finite timing gate failure. |

## P5 interpretation

The original P5 report is retained as historical Evidence. P5R corrected the
cross-window RUN-SHA comparison: P4 is a 180-frame reference while P5 uses
extended windows, so P5 validity compares same-protocol formal RUN SHAs and
complete CYCLE SHAs. `thermal_throttle_status=unavailable` remains an explicit
limitation and is not a no-throttling claim.

## Retention boundary

The following formal Evidence is retained and must not be deleted:

- `results/validation/stage_p/p4_correctness_v1/`
- `results/validation/stage_p/p6_video_v1/`
- `results/validation/stage_p/p7_stability_v1/`
- `results/benchmark/stage_p/p5_queue_pilot_v1/`
- `results/benchmark/stage_p/p5_serial_vs_pipeline_v1/`

Generated video, large trace files, raw telemetry, build directories, runtime
cache, and local evidence directories remain local-only and are excluded from
the P8 documentation commit.
