# Paper Contribution Assessment v1.2

Previous version: `docs/paper/phase0/PAPER_CONTRIBUTION_ASSESSMENT_v1.1.md`

Supersedes: Paper Contribution Assessment v1.1.

Supersession reason: reclassifies the contribution boundary after validity
remediation and removes V4, old Gate D, and old Pareto claims from core scope.

Effective authority date: `2026-08-04`.

Basis: Paper Phase 0.5 validity remediation.

## 1. Review Verdict

```text
Contribution scope: REFROZEN
A-level core contributions: 2
Further experiment: NOT REQUIRED
New code optimization: NOT AUTHORIZED
```

The engineering paper theme is:

> 面向 Jetson TensorRT INT8 工业缺陷检测的数据路径优化与受控消融：正确性约束下的吞吐与尾延迟分析

Stage R is the main body. Stage Q supplies INT8 precision and Engine
prerequisite evidence. Stages J, K, and P are necessary background only. The
Stage P `4.165718x` observation is not a core result.

## 2. Core Contribution 1 — A-level

### INT8 后数据路径分析与统一实验边界

Under the frozen platform, model, INT8 Engine, workload, and correctness
contract, the work establishes a common external timing boundary and a formal
V0/V2R/V3R comparison. The contribution is an engineering measurement and
evidence-boundary contribution, not a new detection, quantization, or CUDA
algorithm.

Required evidence:

- frozen platform, model, Engine, workload, and correctness contract;
- common timing instrumentation and external timing boundary;
- 60/1080 lifecycle contract and 15 valid formal processes;
- formal V0/V2R/V3R summary, CSV/JSON metadata, and hash records.

Allowed conclusion: CUDA preprocessing is the main observed performance source
in this frozen tested path. This is not a universal claim that INT8 always
migrates the bottleneck to input processing.

## 3. Core Contribution 2 — A-level

### 正确性约束下的数据路径分支消融与性能权衡

The formal comparison uses V0 CPU/OpenCV preprocessing, V2R pageable raw
staging with correctness-aligned CUDA preprocessing, and V3R pinned raw
staging with the same preprocessing semantic. V2R and V3R task-level identity
is preserved by Gate D and identity evidence; performance is evaluated under
the same timing boundary.

Main findings:

- V2R provides the primary average performance gain and is correctness-accepted;
- V3R provides limited additional average FPS and mean-latency benefit;
- V3R does not provide a clear P95/P99 tail-latency improvement;
- pinned memory is an average-performance marginal optimization in this path;
- maximum average FPS must not be expanded into a claim that every tail metric
  is better.

V4 is not part of this core contribution. Its fixed-slot serial rotation,
severe tail, and OOM event are retained only as an engineering limitation and
validity-audit record. They do not establish true double buffering,
cross-frame overlap, multi-stream overlap, or a causal statement that
double-buffering caused OOM.

## 4. Supporting Contributions

Training, ONNX export, ORT CPU baseline, TensorRT FP16/INT8 integration,
Pipeline implementation, layered correctness checks, and evidence provenance
remain supporting engineering assets. They are not additional A-level core
contributions. Checkpoint sensitivity is thesis SUPPORTING and engineering
paper BACKGROUND/LIMITATION evidence.

## 5. Scope and Claim Restrictions

The paper must disclose the historical train/validation duplicate, unchanged
180-image test set, split-v2 counts, and matched-control selection result.
Historical Attempt 2 is superseded for final paper use. V4 formal performance,
Pareto, and double-buffer overlap claims are excluded. No universal hardware,
model, input-size, memory, or overlap conclusion is permitted.

## 6. Sufficiency Decision

```text
Must rerun: NONE
Should rerun: NONE
Retraining: NONE
ONNX re-export: NONE
TensorRT Engine rebuild: NONE
Calibration rerun: NONE
Additional variant: NONE
```
