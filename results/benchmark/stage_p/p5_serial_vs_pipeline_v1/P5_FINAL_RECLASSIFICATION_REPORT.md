# P5R Protocol Correction Report

## 1. Verdict

`P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE`

The completed P5 attempt_001 Evidence passes the corrected correctness
contract:

- all six formal RUN SHA values are identical;
- every complete 180-frame CYCLE SHA matches the P4 expected CYCLE SHA;
- every pilot and formal run has zero dropped frames;
- pilot and formal measured traces are complete;
- all processes returned successfully.

Thermal throttle interfaces were unavailable. This is recorded as a known
limitation; it is not reclassified as throttling-free PASS evidence.

No P6 execution was performed.

## 2. Environment

- Execution environment: Jetson Codex
- Repository: `inevitablekl/edge-ai-defect`
- Branch: `feature/jetson-pipeline-runtime`
- Source HEAD used by attempt_001:
  `d45342e0c9224df4521fae6db97555fd4257ae24`
- Platform: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super
- L4T: R36.5
- Power mode: `MAXN_SUPER`
- CPU affinity: `0-5`
- OpenCV threads: `1`
- Engine SHA256:
  `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc`
- Engine manifest SHA256:
  `39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63`
- ModelContract SHA256:
  `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190`
- Corpus manifest SHA256:
  `fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8`
- Executable SHA256:
  `4d817adbac1b93a7fcbd14a923229d9dd4e8dfd9c442eb732d56a6d6e9e9d4dc`

## 3. Protocol Corrections

The historical P5 rule `P5 RUN SHA == P4 RUN SHA` was incorrect because P4
uses 180 accepted frames while P5 uses 1100 or 5100 accepted frames. RUN SHA
is now compared only among runs with the same P5 protocol and window.

P4 RUN SHA remains the 180-frame single-cycle reference. P5 correctness uses:

```text
all six formal P5 RUN SHA values identical
complete 180-frame CYCLE SHA == P4 expected CYCLE SHA
```

The P4 expected CYCLE SHA is:

```text
6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3
```

Partial cycles are retained but excluded from complete-cycle PASS.

Thermal handling is also corrected: unavailable thermal interfaces produce
`thermal_throttle_status=unavailable` and a known limitation. Only detected
throttling produces `RUN_INVALID_THERMAL_THROTTLING`.

## 4. Evidence Reviewed

Only existing attempt_001 Evidence was read:

- `results/benchmark/stage_p/p5_queue_pilot_v1/attempt_001/`
- `results/benchmark/stage_p/p5_serial_vs_pipeline_v1/attempt_001/`
- P4 reference: `results/validation/stage_p/p4_correctness_v1/attempt_009/`

The historical `attempt_001/P5_QUEUE_PILOT_AND_FORMAL_BENCHMARK_REPORT.md`
was not deleted or modified. Its invalid conclusion is retained as a
historical interpretation under the superseded cross-window RUN-SHA rule.

P5R performed no benchmark, build, runtime, telemetry, or data-generation
command.

## 5. Queue Selection

The existing pilot measured:

| Capacity | Throughput (FPS) | 95% of best | Eligible |
|---:|---:|---:|:---:|
| 1 | 210.744599 | 200.207369 | yes |
| 2 | 208.482792 | 200.207369 | yes |
| 4 | 205.452877 | 200.207369 | yes |

Best throughput is `210.744599 FPS`; the eligibility threshold is
`0.95 × best = 200.207369 FPS`. The smallest eligible capacity is:

```text
selected_queue_capacity = 1
```

This selection is frozen by this reclassification. Formal Pipeline runs also
used capacity 1 and recorded Q1/Q2/Q3 high-water marks of `1/1/1`.

## 6. Correctness Reclassification

All six formal runs had `accepted=5100`, `processed=5100`, `dropped=0`, and
5000 complete measured trace frames.

All six formal runs produced the same P5 RUN SHA:

```text
7e115aa5661f38864955bb9eb7481e86290d0a0cb55e6c308270401d683cd929
```

Each run's 28 complete 180-frame cycles matched the frozen P4 CYCLE SHA.
The final partial cycle was retained and excluded from PASS. The corrected
correctness gate therefore passes.

## 7. Performance Classification

Existing formal throughput values were retained without recalculation from
new data. Paired Pipeline/Serial ratios were:

```text
4.158743
4.164089
4.174321
```

Arithmetic mean:

```text
4.165718
```

Sample SD (`n-1`):

```text
0.007915
```

Classification:

```text
MATERIAL_MEASURED_THROUGHPUT_INCREASE
```

This is a measured classification under the frozen protocol, not a claim of
statistical significance or a guarantee of speedup.

## 8. Thermal Handling

The existing Evidence records:

```text
thermal_throttle_status=unavailable
```

No throttling PASS is claimed. No attempt is marked
`RUN_INVALID_THERMAL_THROTTLING`, because the throttle-detection interface was
unavailable; this is not a claim that throttling was absent. The unavailable
interface remains a known limitation in the final P5 status.

## 9. Documentation Changes

Added:

- `P5R_PROTOCOL_AMENDMENT.md`
- `P5R_EVIDENCE_INDEX.md`
- this final reclassification report

Updated the Stage P Execution Plan, Task Cards, Decisions, Experiment Plan,
and Tasks status with the P5R amendment, corrected hash/thermal rules,
attempt_001 reclassification, and the frozen capacity selection. Historical
P5 protocol and invalid-state Evidence remain preserved.

## 10. Commit

```text
docs(stage-p): amend p5 validity protocol and reclassify evidence
```

This report and the documentation amendment are included in that local commit.
No push, merge, rebase, or tag was performed.

## 11. Next Authorization

P5 is complete under the amended contract with thermal status limitation.
`selected_queue_capacity=1` is frozen and the P5 formal protocol is complete.

P6 was not executed in this task. A later explicit task may begin P6; no P6
implementation or validation was performed here.
