# Stage R R5 — Pareto Evaluation and Final Closeout

## 1. Objective

Close Stage R with a final performance–accuracy–complexity evaluation of the
four data-path variants produced under D087 multi-branch ablation, and record
the resulting Pareto disposition.

This closeout uses **only existing R3 Attempt 2 Evidence**. No new benchmark is
executed, no run is added or removed, and no production code is modified.

## 2. Evidence Authority

Formal R5 evaluation uses only:

```text
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/
```

Attempt 1:

```text
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v1/
```

is retained as:

```text
R3_ATTEMPT_1_NONCOMPARABLE_HARNESS
```

and is not used for any final cross-variant numerical conclusion.

The Attempt 1 PipelineRunner V0 figure of approximately `231.9 FPS` is
reported strictly as system-level background information and is explicitly
labeled:

```text
CONTEXT ONLY
NOT COMPARABLE WITH THE UNIFIED SINGLE-THREAD ABLATION
```

Attempt 2 was run under a unified single-thread ablation harness: batch-1,
640×640, one CUDA stream, one TensorRT execution context, queue capacity 1 with
a block drop policy, five independent interleaved runs per variant (20 runs
total, all PASS). The harness is identical across V0/V2/V3/V4, so paired
differences are computed on the same interleaved run set.

Attempt 2 Evidence files:

```text
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/per_run_metrics.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/aggregate_metrics.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/comparison_matrix.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/performance_accuracy_tradeoff.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/experiment_manifest.json
results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/failure.json
```

All values in this report were re-read from `per_run_metrics.json` /
`aggregate_metrics.json` / `comparison_matrix.json` for this closeout and
cross-checked; they were not copied from memory.

## 3. Unified Experiment Summary

| Variant | Mechanism | Runs | Measured frames / run | Drop count | Detection SHA |
|---|---|---|---:|---:|---|
| V0 | CPU/OpenCV preprocessing, pageable FP32 HostTensor | 5 | 1080 | 0 | `12bdb79…513de2` |
| V2 | CUDA fused preprocessing, pageable raw staging | 5 | 1080 | 0 | `0a668fd…81f5ed` |
| V3 | V2 + long-lived pinned raw staging | 5 | 1080 | 0 | `0a668fd…81f5ed` |
| V4 | V3 + two pinned raw/device slots, limited fixed alternation | 5 | 1080 | 0 | `0a668fd…81f5ed` |

All runs are `PASS`. Per-variant detection SHA is identical across the five
runs of each variant. V2/V3/V4 share the remediated R2 identity; their
complete detection SHA is identical, so V3 and V4 inherit the V2 task metrics.

## 4. Per-Run Variability

Each metric is reported per variant as mean, standard deviation, min, max, and
the five individual run values. Standard deviation is the population standard
deviation over the five formal runs.

### FPS

| Variant | Mean | Std | Min | Max | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 54.865 | 0.312 | 54.382 | 55.279 | 54.658 | 55.023 | 55.279 | 54.983 | 54.382 |
| V2 | 126.120 | 1.075 | 124.483 | 127.662 | 124.483 | 127.662 | 125.719 | 125.903 | 126.834 |
| V3 | 127.005 | 0.677 | 126.098 | 127.842 | 127.565 | 126.353 | 126.098 | 127.842 | 127.166 |
| V4 | 26.746 | 0.276 | 26.224 | 26.969 | 26.224 | 26.963 | 26.852 | 26.969 | 26.723 |

### Mean latency (ms)

| Variant | Mean | Std | Min | Max | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 18.168 | 0.104 | 18.030 | 18.331 | 18.235 | 18.117 | 18.030 | 18.127 | 18.331 |
| V2 | 7.870 | 0.068 | 7.774 | 7.974 | 7.974 | 7.774 | 7.895 | 7.884 | 7.826 |
| V3 | 7.807 | 0.039 | 7.758 | 7.854 | 7.772 | 7.849 | 7.854 | 7.758 | 7.799 |
| V4 | 32.278 | 0.390 | 31.968 | 33.020 | 33.020 | 31.974 | 32.129 | 31.968 | 32.298 |

### P95 latency (ms)

| Variant | Mean | Std | Min | Max | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 18.830 | 0.072 | 18.690 | 18.879 | 18.867 | 18.690 | 18.840 | 18.876 | 18.879 |
| V2 | 9.935 | 0.119 | 9.765 | 10.100 | 9.913 | 9.765 | 10.031 | 10.100 | 9.864 |
| V3 | 9.894 | 0.160 | 9.694 | 10.068 | 9.714 | 10.068 | 10.040 | 9.694 | 9.954 |
| V4 | 22.675 | 0.063 | 22.582 | 22.781 | 22.666 | 22.673 | 22.672 | 22.582 | 22.781 |

### P99 latency (ms)

| Variant | Mean | Std | Min | Max | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 19.004 | 0.029 | 18.950 | 19.030 | 19.013 | 18.950 | 19.030 | 19.026 | 19.002 |
| V2 | 11.552 | 0.652 | 10.251 | 11.937 | 11.901 | 10.251 | 11.885 | 11.937 | 11.786 |
| V3 | 11.220 | 0.809 | 10.219 | 11.896 | 10.240 | 11.893 | 11.896 | 10.219 | 11.854 |
| V4 | 22.907 | 0.095 | 22.760 | 23.051 | 22.870 | 22.939 | 22.913 | 22.760 | 23.051 |

### CPU equivalent cores

| Variant | Mean | Std | Min | Max | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| V0 | 0.841 | 0.126 | 0.772 | 1.092 | 1.092 | 0.776 | 0.775 | 0.788 | 0.772 |
| V2 | 0.756 | 0.096 | 0.698 | 0.947 | 0.706 | 0.947 | 0.698 | 0.723 | 0.708 |
| V3 | 0.837 | 0.222 | 0.688 | 1.277 | 1.277 | 0.722 | 0.786 | 0.714 | 0.688 |
| V4 | 1.001 | 0.030 | 0.973 | 1.059 | 1.059 | 0.996 | 0.988 | 0.988 | 0.973 |

### V4 max / outlier latency (ms)

For V4 the tail metrics must be reported alongside P95/P99, which mask the
extreme long tail. Every one of the five V4 runs contains a single-frame
long-tail event:

| Run | latency_max_ms | latency_stddev_ms |
|---|---:|---:|
| set_01_v4 | 10236.582 | 312.831 |
| set_02_v4 | 8976.955 | 275.066 |
| set_03_v4 | 9173.937 | 280.916 |
| set_04_v4 | 8991.817 | 275.505 |
| set_05_v4 | 9241.866 | 283.018 |

Range: `8976.96 – 10236.58 ms`, approximately `8.98 – 10.24 s` per run. During
the formal run set one V4 run was OOM-killed (return code `-9`), recorded in
`failure.json` (run_id `set_01_v4`), and was rerun under the frozen rule; the
rerun is the `set_01_v4` PASS entry above.

## 5. Performance Matrix

Aggregate means from `aggregate_metrics.json`:

| Variant | FPS | Mean (ms) | P95 (ms) | P99 (ms) | CPU cores |
|---|---:|---:|---:|---:|---:|
| V0 | 54.865 | 18.168 | 18.830 | 19.004 | 0.841 |
| V2 | 126.120 | 7.870 | 9.935 | 11.552 | 0.756 |
| V3 | 127.005 | 7.807 | 9.894 | 11.220 | 0.837 |
| V4 | 26.746 | 32.278 | 22.675 | 22.907 | 1.001 |

Paired differences on the same interleaved run set (from `comparison_matrix.json`,
cross-checked against per-run values):

| Comparison | FPS diff | FPS rel. | Mean diff (ms) | Mean rel. | P95 diff (ms) | P99 diff (ms) | CPU cores diff | mAP50 Δ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V2 − V0 | +71.255 | +129.87% | −10.298 | −56.68% | −8.895 | −7.452 | −0.084 | −0.00537575 |
| V3 − V2 | +0.885 | +0.70% | −0.064 | −0.81% | −0.041 | −0.332 | +0.081 | 0 |
| V4 − V3 | −100.259 | −78.94% | +24.471 | +313.47% | +12.781 | +11.686 | +0.163 | 0 |
| V4 − V0 | −28.119 | −51.25% | +14.110 | +77.66% | +3.845 | +3.902 | +0.160 | −0.00537575 |

Reading under identical harness semantics: V2 shows a large observed
throughput gain and mean-latency reduction relative to V0; V3 is essentially
flat relative to V2; V4 is substantially slower than both V0 and V2/V3. With
five runs per variant, no complex significance testing is performed, and no
strong statistical-significance claim is made.

## 6. Accuracy Matrix

The accuracy axis is inherited, not recomputed. V2/V3/V4 share the same
remediated detection SHA (`0a668fd5937d83b28521a00847c9dd8567299697c8e1f5c1159b4e84fe81f5ed`),
so V3 and V4 inherit the V2 task metrics:

```text
V0:
mAP50 delta          = 0

V2/V3/V4:
mAP50 delta          = -0.00537575
max class AP50 delta = -0.02673348
max class Recall     = -0.03030303
```

| Variant | mAP50 Δ | Max class AP50 Δ | Max class Recall Δ | Detection SHA family |
|---|---:|---:|---:|---|
| V0 | 0 | 0 | 0 | Stage Q baseline |
| V2 | −0.00537575 | −0.02673348 | −0.03030303 | remediated R2 |
| V3 | −0.00537575 | −0.02673348 | −0.03030303 | remediated R2 (inherit) |
| V4 | −0.00537575 | −0.02673348 | −0.03030303 | remediated R2 (inherit) |

## 7. Complexity and Stability Matrix

| Variant | Implementation increment | Complexity class | Runtime stability | Correctness classification |
|---|---|---|---|---|
| V0 | None (baseline) | Baseline | Stable; low run-to-run dispersion | CORRECTNESS_FIRST_BASELINE |
| V2 | CUDA fused preprocessing, pageable raw | Moderate (CUDA path) | Stable | NOT CORRECTNESS-EQUIVALENT REPLACEMENT |
| V3 | V2 + long-lived pinned raw staging | Moderate + pinned allocation | Stable | NOT CORRECTNESS-EQUIVALENT REPLACEMENT |
| V4 | V3 + two-slot limited alternation | Highest (two slots + sync) | Severe tail; OOM event | NOT CORRECTNESS-EQUIVALENT REPLACEMENT |

Stability notes:

- V0: FPS std 0.312, mean-latency std 0.104, no outliers.
- V2: FPS std 1.075; P99 std 0.652 is the widest tail among V0/V2/V3 but all
  five runs stay within ~1.9 ms of the median.
- V3: FPS std 0.677; P99 std 0.809. Variability is comparable to V2.
- V4: P95/P99 appear stable (std ~0.06–0.10) but are misleading; latency_max
  spans 8.98–10.24 s and latency_stddev is ~275–313 ms in every run. One OOM
  kill occurred during the formal set and was rerun per frozen rule.

## 8. V0 Evaluation

```text
CORRECTNESS_FIRST_BASELINE
FORMAL DEPLOYMENT BASELINE
```

- Satisfies the frozen correctness contract; Stage Q authority is unchanged.
- In the unified single-thread ablation it has the lowest throughput (54.865
  FPS) and highest latency (18.168 ms mean).
- The existing PipelineRunner can achieve higher system throughput through
  concurrency, but that figure belongs to the pipeline context and is not part
  of the unified single-thread ablation table.

## 9. V2 Evaluation

```text
BEST_CONTROLLED_PERFORMANCE_TRADE_OFF
EXPERIMENTAL_OPTIMIZATION_CANDIDATE
NOT CORRECTNESS-EQUIVALENT REPLACEMENT
```

Under the unified single-thread ablation protocol:

```text
FPS change vs V0:      +129.9%
mean latency change:   -56.7%

mAP50 absolute drop:   0.00537575
                       approximately 0.54 percentage points

amount exceeding the
frozen Gate D limit
(0.005):               0.00037575
                       approximately 0.038 percentage points
```

CPU equivalent cores are observed lower for V2 (0.756) than V0 (0.841), a
`−0.084` paired difference; the per-set differences vary in sign across runs,
so this is reported as an observed directional tendency within run-level
variation, not a strong claim.

Conclusion boundary: V2 is the primary performance–accuracy trade-off branch
for the paper, but it cannot be written as a direct production replacement for
the existing formal PipelineRunner path.

## 10. V3 Incremental Evaluation

Relative to V2, the current aggregate:

```text
FPS:                   +0.7%
mean latency:          -0.8%
P95:                   -0.04 ms
CPU equivalent cores:  +0.08
```

The paired P99 difference (−0.332 ms) and P95 difference (−0.041 ms) are
small, and the paired per-set differences for FPS and CPU cores change sign
across runs (FPS per-set: +3.08, −1.31, +0.38, +1.94, +0.33; CPU cores per-set:
+0.571, −0.225, +0.088, −0.009, −0.020). The incremental effect was small
relative to run-level variation.

Classification:

```text
NO_MEANINGFUL_INCREMENTAL_BENEFIT_OBSERVED
```

Conclusion is deliberately scoped — not a claim that pinned memory can never
help on Jetson:

```text
Under the evaluated batch-1, 640×640, single-thread Jetson path, pinned raw
staging did not provide a practically meaningful incremental benefit over V2.
```

## 11. V4 Negative Result

```text
DOMINATED_NEGATIVE_ABLATION_RESULT
NOT SELECTED
```

Recorded observations:

- FPS falls ~78.9% relative to V3 (and ~51.3% relative to V0).
- Mean latency increases ~313.5% relative to V3.
- CPU equivalent cores are the highest of the four variants (1.001).
- Every formal run contains a single-frame long tail of approximately
  8.98–10.24 s.
- One OOM kill occurred during the formal run set and was rerun under the
  frozen rule.
- Detection SHA is identical to V2/V3, so this is not an accuracy problem.

No root cause beyond the evidence is asserted:

```text
The evaluated limited double-buffer implementation introduced severe
tail-latency and stability costs and provided no measured performance benefit
under the tested synchronization model.
```

This does not claim that double buffering is inherently ineffective.

## 12. Pareto Frontier

The final recommendation is two-layered; there is no single "overall
champion".

**Deployment layer**

```text
Selected correctness-first deployment baseline:
Stage Q INT8 V0
```

- Correctness contract passed.
- Stage Q Evidence is complete.
- Existing PipelineRunner system path.
- V2 did not satisfy the correctness-equivalent replacement Gate.

**Research / ablation layer**

```text
Best controlled performance-accuracy trade-off:
V2
```

- Largest observed performance gain under the unified single-thread condition.
- CPU occupancy did not increase (observed lower CPU equivalent cores with
  directionality within run-level variation).
- Accuracy cost is explicit and reproducible.
- Engineering complexity is lower than V3/V4.

Pareto operating points:

```text
V0 and V2 represent two different Pareto operating points.

V0:
correctness-first

V2:
performance-first with measured task-metric cost
```

V3 and V4 are not on the final Pareto frontier:

```text
V3:
incremental benefit insufficient relative to added mechanism

V4:
dominated by V2/V3 and affected by severe tail instability
```

## 13. Deployment Interpretation

- The formal deployment baseline remains the Stage Q INT8 V0 path, with the
  existing PipelineRunner as the system-level runner. No V2/V3/V4 path is
  selected for deployment.
- The ablation result is a research finding about the data-path behavior under
  a controlled single-thread harness; it is not a direct comparison of V2
  against the multi-thread PipelineRunner deployment throughput.

## 14. Paper-Ready Conclusions

Allowed statement:

```text
Under the unified single-thread ablation protocol, V2 increased throughput by
approximately 129.9% and reduced mean latency by approximately 56.7% relative
to V0, with an absolute mAP50 drop of approximately 0.0054.
```

Must also state:

```text
The comparison isolates data-path behavior under a controlled single-thread
harness and does not directly compare V2 against the existing multi-thread
PipelineRunner deployment throughput.
```

Prohibited statements (not used):

```text
V2 is 129.9% faster than the complete deployed system
Pinned memory is useless
Double buffering never works
CUDA preprocessing is accuracy-neutral
V2 passed Gate D
```

The Attempt 1 PipelineRunner V0 figure of ~231.9 FPS is background context
only and is not comparable with the unified single-thread ablation.

## 15. Limitations

- Five formal runs per variant; paired differences are descriptive and are not
  claimed as statistically significant.
- The unified harness is single-thread and batch-1; results describe this
  controlled path, not the concurrent PipelineRunner.
- Accuracy metrics are inherited from the R2 Gate D evaluation; V3/V4 inherit
  V2 task metrics through identical detection SHA, so incremental accuracy
  effects of pinned staging and double buffering were not independently
  measured at task level.
- V4 root cause beyond the tested synchronization model was not established.
- The frozen Gate D limit (0.005) remains unchanged; V2 is a trade-off
  candidate, not a Gate-passing replacement.
- No attempt was made to repair the V4 outlier or to implement V5 / zero-copy.

## 16. Final Disposition

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

The earlier classification

```text
STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED
```

remains valid as the historical replacement-selection closeout (b008af7) and
is retained as history, but it is superseded as the current final state by the
complete multi-branch ablation result produced after D087.

Machine-readable closeout Evidence:

```text
results/validation/stage_r/r5_pareto_closeout_v1/
```
