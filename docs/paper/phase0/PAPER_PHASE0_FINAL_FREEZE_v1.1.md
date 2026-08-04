# Paper Phase 0 Final Freeze v1.1

Previous version: `docs/paper/phase0/PAPER_PHASE0_FINAL_FREEZE_v1.0.md`

Supersedes: Paper Phase 0 Final Freeze v1.0.

Supersession reason: final unified freeze after Paper Phase 0.5 validity
remediation and evidence reconciliation.

Effective authority date: `2026-08-04`.

Basis: Paper Phase 0.5 validity remediation.

## 1. Document Status

```text
Phase 0 original freeze: HISTORICAL_BASELINE
Phase 0.5 validity remediation: COMPLETE
Evidence authority: REFROZEN
Contribution scope: REFROZEN
Further experiment: NONE
Paper Phase 1: AUTHORIZED_AFTER_DOCUMENT_REVIEW
```

The v1.0 freeze remains immutable historical baseline. This v1.1 document is
the current authority for paper evidence and contribution scope.

## 2. Frozen Paper Positioning

The engineering paper is scoped as:

> 面向 Jetson TensorRT INT8 工业缺陷检测的数据路径优化与受控消融：正确性约束下的吞吐与尾延迟分析

Stage R is the main body. Stage Q is supporting prerequisite evidence. Stages
J, K, and P are necessary background only. This remains an engineering
deployment study, not a new detection or quantization algorithm paper.

## 3. Frozen Core Contributions

Exactly two A-level core contributions remain.

### 3.1 INT8 后数据路径分析与统一实验边界

The frozen model, TensorRT INT8 Engine, workload, correctness contract, and
external timing boundary establish a reproducible V0/V2R/V3R comparison. The
allowed claim is limited to the tested platform/path: CUDA preprocessing was
the main observed performance source.

### 3.2 正确性约束下的数据路径分支消融与性能权衡

The formal objects are V0, V2R, and V3R. V2R is correctness-accepted and
provides the primary average performance gain. V3R provides limited additional
average FPS and mean-latency benefit but no clear P95/P99 improvement. The
highest average FPS is not a claim that all tail metrics are better.

V4 is not a core contribution. It is classified
`PARTIAL_BUFFER_ROTATION_NOT_TRUE_OVERLAP` and retained only as a historical
engineering limitation/anomaly record.

## 4. Dataset and Checkpoint Closure

The historical train/validation split had one image-content duplicate. Test
membership and its 180 entries were unchanged. Split v2 is `1260 train / 359
validation / 180 test`. Matched split-v1 control and split-v2 sensitivity
evaluation were executed; seed 7 ranked first on both and all nine checkpoint
ranks were unchanged.

```text
Checkpoint sensitivity: SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL
Dataset split: CLOSED_WITH_DISCLOSURE
Dataset split remediation: DATASET_SPLIT_REMEDIATION_COMPLETE
```

No retraining, checkpoint re-freeze, ONNX re-export, TensorRT Engine rebuild,
calibration rerun, or split-driven downstream rerun is required. Historical
absolute validation metrics remain contemporaneous records and must not be
described as byte-identically reproduced.

## 5. Stage R Formal Results

Only V0, V2R, and V3R enter the formal performance table.

| Variant | Meaning | FPS mean | FPS SD | Mean latency | P95 | P99 |
|---|---|---:|---:|---:|---:|---:|
| V0 | CPU/OpenCV preprocessing baseline | 54.600 | 0.223 | 18.273 ms | 18.854 ms | 19.068 ms |
| V2R | pageable raw staging + correctness-aligned CUDA preprocessing | 122.122 | 0.492 | 8.140 ms | 9.827 ms | 11.529 ms |
| V3R | pinned raw staging + same CUDA preprocessing | 127.097 | 1.279 | 7.812 ms | 9.842 ms | 11.515 ms |

V2R versus V0: FPS ratio `2.2367x`, FPS increase `123.67%`, mean latency
reduction `55.45%`, P95 reduction `47.88%`, P99 reduction `39.54%`.

V3R versus V0: FPS ratio `2.3278x`, FPS increase `132.78%`, mean latency
reduction `57.25%`, P95 reduction `47.80%`, P99 reduction `39.61%`.

V3R versus V2R: FPS increase `4.07%`, mean latency reduction `4.03%`, P95
approximately `0.15%` worse, and P99 approximately flat with `0.12%`
improvement. This is a marginal average-performance optimization.

V2R correctness metrics are precision `0.6912751678`, recall `0.6990950226`,
mAP50 `0.6476254638`, and mAP50-95 `0.3523443910`, with all V0 deltas `0.0`
and Gate D `PASS`. V3R correctness is accepted with identity evidence.

## 6. Timing and Run Contract

Start: before source pull/frame acquisition.

End: after preprocessing, inference, postprocess, and frame-result construction,
before JSON serialization/write.

Included: source pull/decode, raw staging, H2D, CUDA preprocessing, TensorRT
inference, synchronization, D2H, postprocess, and frame-object construction.

Excluded: JSON serialization, file I/O, digest finalization, and summary
persistence.

All branches used `timing.enabled=false`, `profiling.mode=off`, warmup `60`,
measured `1080`, six measured cycles, five independent processes per variant,
15/15 valid runs, zero drop, and EOS PASS.

## 7. V4 and Historical Evidence Disposition

V4 formal performance, Pareto, and double-buffer overlap claims are excluded.
The retained record permits only these statements: two fixed resource slots
were rotated serially; a severe tail and one OOM event were recorded; and the
implementation is an engineering limitation. It does not permit claims of
true double buffering, cross-frame overlap, multi-stream overlap, that
double-buffering caused OOM, or that double buffering is generally harmful.

Historical Attempt 2 is
`SUPERSEDED_FOR_FINAL_PAPER_USE`. It may support remediation motivation,
audit trail, historical process evidence, and timing/correctness background,
but it does not enter the final table, figure, abstract, or conclusion.

## 8. Sufficiency and Entry Decision

```text
Paper Phase 0.5 technical remediation: COMPLETE
V2R correctness: ACCEPTED
V3R correctness inheritance: ACCEPTED_WITH_IDENTITY_EVIDENCE
Timing-aligned rerun: PASS
Further experiment: NOT REQUIRED
New code optimization: NOT AUTHORIZED
Open Must gaps: NONE
Open Should experimental gaps: NONE
```

Paper Phase 1 may begin after document review. Remaining work is figures,
tables, chapter drafting, and literature mapping; those activities must use
the v1.1 authority and must not invent measurements.
