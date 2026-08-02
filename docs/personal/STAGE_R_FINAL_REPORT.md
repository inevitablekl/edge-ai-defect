# Stage R Final Report — Documentation-Only Negative-Result Closeout

## 1. Executive Summary

Stage R investigated INT8 data-path optimization after Stage Q. The Stage Q
INT8 V0 baseline was retained as the selected candidate. CUDA fused
preprocessing was implemented and validated as an experimental path, but it
did not satisfy the frozen task-level replacement criteria.

Final classification:

```text
STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED
```

This closeout does not establish a V2 performance benefit. No V0-vs-V2
performance comparison was executed.

## 2. Scope and Research Questions

Stage R addressed:

1. Whether CPU preprocessing and the INT8 V0 data path are significant costs.
2. Whether CUDA fused preprocessing is technically feasible while preserving
   detection correctness.
3. Whether pageable raw, pinned raw, and limited overlap candidates justify
   further optimization.

Assessment:

| Question | Assessment |
|---|---|
| V0 data-path bottleneck | Answered for the evaluated V0 path |
| CUDA preprocessing feasibility | Partially answered: runnable, but not correctness-equivalent replacement |
| Pinned raw value | Not evaluated; continuation not justified after V2 Gate D failure |
| Double-buffer value | Not evaluated; V4 skipped because V3 was skipped |

## 3. Entry State and Authority

| Item | Value |
|---|---|
| Branch | `feature/jetson-int8-data-path-optimization` |
| R6 starting HEAD | `488a6089f24a3c96a91c8120ee6a5b26d2b34de2` |
| Stage Q selected-candidate commit | `4c67858610e14ba7d3c951b33f0948230451827f` |
| Stage Q canonical detection SHA | `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` |
| Result JSON | v4 |
| Stage Q Evidence | unchanged |

The R6 entry worktree was clean. R2.2 negative-result implementation and
Evidence were already contained in the starting commit.

## 4. R1 Baseline and Profiling

The tracked R1 profiling summary reports the following V0 means:

| Component | Mean |
|---|---:|
| CPU source | 0.932768299 ms |
| CPU preprocessing | 3.652910182 ms |
| Synchronous host inference roundtrip | 3.762928002 ms |
| TensorRT CUDA | 2.806860778 ms |
| H2D | 0.690427356 ms |
| D2H | 0.099916267 ms |
| Host output construction | 0.034834906 ms |
| Pre-sink total | 8.628215226 ms |

The valid conclusion is:

> CPU preprocessing and synchronous host-side data movement were significant
> components of the evaluated V0 path.

These measurements are V0 observations only. They do not establish a V2, V3,
or V4 performance improvement.

## 5. V2 Experimental Path

The evaluated V2 path was:

```text
pageable raw staging
→ CUDA fused preprocessing
→ TensorRT device input
→ TensorRT INT8 inference
→ CPU postprocess
```

The path used one CUDA stream, one TensorRT execution context, persistent
device buffers, no pinned memory, and no cross-frame overlap. Result JSON v4
and the public backend-neutral interfaces were unchanged. V2-specific device
input capability remained inside the TensorRT backend boundary.

## 6. Correctness Results

| Gate | Result |
|---|---|
| Gate A | PASS |
| Gate B | PASS |
| Gate C | PASS |
| Gate D | FAIL |

Gate B tensor evidence reported MAE `0.00041216449077775033`, P99
`0.0039216279983520508`, maximum absolute error `0.0039216279983520508`, and
zero non-finite values. Geometry cases passed.

Original V2 Gate D result:

```text
mAP50 drop:          0.00552337
max class AP50 drop: 0.02751543
max class Recall:    0.03030303
```

After the authorized minimal 11-bit fixed-point resize remediation:

```text
mAP50 drop:          0.00537575
max class AP50 drop: 0.02673348
max class Recall:    0.03030303
```

The remediation improved the result but did not satisfy the frozen
replacement thresholds. The absolute mAP50 drop is approximately `0.0054`,
or about 0.54 percentage points; it is not 0.05%.

## 7. Root-Cause Analysis

The mismatch was attributed primarily to numerical differences between the
CUDA resize implementation and the OpenCV 4.5.4 `INTER_LINEAR` reference path.
The evidence shows geometry correctness, padding behavior, BGR/RGB conversion,
normalization, and tensor-level thresholds passing. The maximum tensor error
was approximately `1/255`. The fixed-point approximation produced only a small
improvement and remained insufficient at task level.

The supported paper-level statement is:

> Under the evaluated YOLOv8n INT8 deployment configuration, small resize
> interpolation differences remained within tensor-level tolerance but
> affected task-level metrics near the frozen replacement threshold. The V2
> path was therefore not selected as a correctness-equivalent replacement.

## 8. Candidate Disposition

```text
Selected candidate:
Stage Q INT8 V0

V2:
Experimental negative result; not selected as replacement

V3:
Skipped

V4:
Skipped
```

V3 changes raw staging memory type but does not address the observed resize
numerical mismatch. V4 depends on a valid V3 candidate and is therefore not
applicable to this closeout.

## 9. R3–R5 Disposition

The original planned path was R3–R5. Following the controlled negative-result
Decision D086, the actual disposition is:

```text
R3: SKIPPED_BY_NEGATIVE_RESULT_DISPOSITION
R4: NOT APPLICABLE
R5: SKIPPED — Stage Q V0 retained
R6: COMPLETE
```

No R3 performance authority was generated. No performance claim is made for
V2, pinned memory, or double buffering.

## 10. Limitations

- V0 versus V2 performance was not formally measured.
- Pinned raw staging was not validated.
- Double buffering and cross-frame overlap were not validated.
- Results apply only to the evaluated YOLOv8n, NEU-DET, Jetson, TensorRT INT8
  configuration and frozen evaluation contract.
- A complete OpenCV-compatible separable fixed-point resize was not implemented.
- V2 is not a deployment recommendation.

## 11. Future Work

Future work may investigate OpenCV-compatible CUDA resize, QAT or more robust
preprocessing training, pinned staging, and a limited double-buffer experiment.
These are not current Stage R tasks and are not required for the project
closeout.

## 12. Closeout Scope Audit

```text
Production code: UNCHANGED during R6
Performance benchmark: NOT EXECUTED during R6
V2 performance claim: NONE
Stage Q Evidence: UNCHANGED
Result JSON: v4 unchanged
Paper Stop Rule: ACTIVE
```

---

# D087 Reopening Addendum (2026-08-02, read-only append)

Previous closeout:

```text
valid as the replacement-selection disposition at b008af7
```

Current research status:

```text
REOPENED_FOR_MULTI_BRANCH_ABLATION under D087
```

```text
Stage R:
REOPENED_FOR_MULTI_BRANCH_ABLATION

V0:
FORMAL_BASELINE

V2:
V2_ACCURACY_TRADE_OFF_BASELINE

R2.3 / V3:
AUTHORIZED

V4:
AUTHORIZED AFTER V3 FUNCTIONAL VALIDATION

R3:
PENDING V3/V4 AVAILABILITY
```

The negative-result sections above remain the historical replacement-selection
disposition and are not rewritten.

---

# R3/R5 Multi-Branch Ablation and Pareto Disposition Addendum (2026-08-02, read-only append)

The earlier negative-result closeout applied to replacement selection. D087
subsequently reopened the research branch for multi-variant ablation without
altering the Gate D result.

Formal ablation authority is Attempt 2:

```text
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/
classification: R3_ATTEMPT_2_UNIFIED_HARNESS
comparability:  UNIFIED_HARNESS_COMPARABLE
```

Attempt 1 (`r3_v0_v2_v3_v4_ablation_v1/`) is retained as
`R3_ATTEMPT_1_NONCOMPARABLE_HARNESS` and is not used for final cross-variant
numerical conclusions. The Attempt 1 PipelineRunner V0 figure of ~231.9 FPS is
system-level background context only and is not comparable with the unified
single-thread ablation.

## Formal ablation table

Aggregate means over five interleaved formal runs per variant:

| Variant | FPS | Mean | P95 | P99 | CPU cores | mAP50 Δ | Disposition |
|---|---:|---:|---:|---:|---:|---:|---|
| V0 | 54.87 | 18.168 | 18.830 | 19.004 | 0.841 | 0 | Correctness baseline |
| V2 | 126.12 | 7.870 | 9.935 | 11.552 | 0.756 | -0.00537575 | Best trade-off |
| V3 | 127.00 | 7.807 | 9.894 | 11.220 | 0.837 | -0.00537575 | No meaningful increment |
| V4 | 26.75 | 32.278 | 22.675 | 22.907 | 1.001 | -0.00537575 | Negative result |

Units: FPS in frames/s, latency in ms, CPU cores dimensionless, mAP50 Δ as an
absolute fraction. Values were re-read from Attempt 2 Evidence for this
addendum.

## Per-run variability (5 runs)

| Variant | Metric | Mean | Std | Min | Max |
|---|---|---|---:|---:|---:|
| V0 | FPS | 54.865 | 0.312 | 54.382 | 55.279 |
| V0 | mean latency ms | 18.168 | 0.104 | 18.030 | 18.331 |
| V2 | FPS | 126.120 | 1.075 | 124.483 | 127.662 |
| V2 | mean latency ms | 7.870 | 0.068 | 7.774 | 7.974 |
| V3 | FPS | 127.005 | 0.677 | 126.098 | 127.842 |
| V3 | mean latency ms | 7.807 | 0.039 | 7.758 | 7.854 |
| V4 | FPS | 26.746 | 0.276 | 26.224 | 26.969 |
| V4 | mean latency ms | 32.278 | 0.390 | 31.968 | 33.020 |

V4 max/outlier latency must be reported alongside P95/P99, which mask the
extreme long tail:

| Run | latency_max ms | latency_stddev ms |
|---|---:|---:|
| set_01_v4 | 10236.582 | 312.831 |
| set_02_v4 | 8976.955 | 275.066 |
| set_03_v4 | 9173.937 | 280.916 |
| set_04_v4 | 8991.817 | 275.505 |
| set_05_v4 | 9241.866 | 283.018 |

Every V4 run contains a single-frame long tail of approximately 8.98–10.24 s.
One V4 run was OOM-killed (return code -9) during the formal set and was
rerun per the frozen rule.

## Paired differences (same interleaved run set)

| Comparison | FPS | Mean ms | P95 ms | P99 ms | CPU cores | mAP50 Δ |
|---|---:|---:|---:|---:|---:|---:|
| V2 − V0 | +71.255 (+129.87%) | −10.298 (−56.68%) | −8.895 | −7.452 | −0.084 | −0.00537575 |
| V3 − V2 | +0.885 (+0.70%) | −0.064 (−0.81%) | −0.041 | −0.332 | +0.081 | 0 |
| V4 − V3 | −100.259 (−78.94%) | +24.471 (+313.47%) | +12.781 | +11.686 | +0.163 | 0 |
| V4 − V0 | −28.119 (−51.25%) | +14.110 (+77.66%) | +3.845 | +3.902 | +0.160 | −0.00537575 |

With five runs per variant these are observed differences; no complex
significance testing is performed and no strong statistical-significance claim
is made.

## Accuracy (inherited)

```text
V0:
mAP50 delta          = 0

V2/V3/V4:
mAP50 delta          = -0.00537575
max class AP50 delta = -0.02673348
max class Recall     = -0.03030303
```

V3/V4 inherit V2 task metrics because their complete detection SHA is identical
to the remediated V2 path
(`0a668fd5937d83b28521a00847c9dd8567299697c8e1f5c1159b4e84fe81f5ed`). Gate D
remains FAIL with the frozen limit (0.005) unchanged; V2 exceeds it by
`0.00037575` (approximately 0.038 percentage points).

## Final disposition

```text
Stage R final status:
STAGE_R_COMPLETE_MULTI_BRANCH_ABLATION

Deployment baseline:
STAGE_Q_INT8_V0

Best controlled research trade-off:
STAGE_R_V2_CUDA_PREPROCESSING

V3:
NOT SELECTED

V4:
NEGATIVE_ABLATION_RESULT

V5:
NOT IMPLEMENTED
```

This final status supersedes the earlier closeout classification
`STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED`, which remains
valid and is retained as the historical b008af7 replacement-selection record.

Full Pareto evaluation: `docs/personal/STAGE_R_R5_PARETO_REPORT.md`.
Machine-readable closeout: `results/validation/stage_r/r5_pareto_closeout_v1/`.
