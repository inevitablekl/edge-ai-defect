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
