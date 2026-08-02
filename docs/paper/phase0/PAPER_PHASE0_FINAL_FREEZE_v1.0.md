# Paper Phase 0 Final Freeze v1.0

## 1. Document Status

```text
Phase 0 status:
COMPLETE

Evidence authority:
FROZEN

Contribution assessment:
ACCEPTED

New experiment requirement:
NONE

Research scope expansion:
PROHIBITED

Paper正文写作:
NOT STARTED
```

Authority inputs:

- `docs/paper/phase0/PAPER_EVIDENCE_AUTHORITY_MAP_v1.0.md`
- `docs/paper/phase0/PAPER_ASSET_MANIFEST_v1.0.csv`
- `docs/paper/phase0/PAPER_PHASE0_GAP_REGISTER_v1.0.md`
- `docs/paper/phase0/PAPER_CONTRIBUTION_ASSESSMENT_v1.1.md`
- `docs/paper/phase0/PAPER_EXPERIMENT_USE_MATRIX_v1.0.csv`

## 2. Project and Paper Positioning

The frozen project positioning is:

- an Electronic Information master's thesis;
- an engineering-oriented small paper;
- an Edge AI Deployment job-seeking project;
- not an algorithm-innovation project;
- not an industrial product-delivery system.

The paper must present a bounded systems/deployment study. Routine training,
export, backend integration, quantization, and Pipeline implementation are
necessary engineering assets, not standalone algorithmic innovations.

## 3. Frozen Central Research Question

在当前 Jetson Orin Nano Super、YOLOv8n、TensorRT INT8、640×640、batch=1
和冻结工作负载下，分析推理计算加速后的输入预处理与数据路径优化机会，并通过
统一实验边界下的数据路径分支消融，研究任务精度、吞吐、平均延迟、尾延迟和
CPU 开销之间的多目标权衡。

This question is restricted to the frozen platform, model, TensorRT INT8
Engine, 640×640 input, batch=1, 180-image workload, preprocessing and
postprocessing contracts, task-correctness criteria, and executed V0/V2/V3/V4
variants. It must not be rewritten as a general claim that bottlenecks
necessarily migrate after INT8 acceleration.

## 4. Frozen Core Contributions

### 4.1 INT8 后数据路径分析与统一实验边界

**Contribution statement:** Under the frozen model, INT8 Engine, dataset,
correctness criteria, and workload, establish a unified single-thread data-path
harness that removes the runner-topology confounding identified in Stage R
Attempt 1 and supports analysis of input-preprocessing and data-path
optimization opportunities in the tested system.

**Supporting stages:** Training and ONNX freeze the research object; Stage Q
provides the INT8 accuracy/performance prerequisite; Stage R R1 and unified
validation establish the profiling motivation and controlled comparison
boundary.

**Allowed claim:** In the frozen Jetson Orin Nano Super, YOLOv8n, TensorRT
INT8, 640×640, batch=1 workload, input preprocessing and the data path showed
further optimization opportunities. Attempt 2 provides the authoritative
unified-harness comparison.

**Mandatory limitations:** This is not evidence that INT8 universally or
necessarily moves the bottleneck to the input path. It does not generalize to
other hardware, models, sizes, batches, workloads, dynamic shapes, multiple
ExecutionContexts, or PipelineRunner throughput. Five runs per variant do not
establish statistical significance.

### 4.2 数据路径分支消融、负向结果和多目标权衡

**Contribution statement:** Under one INT8 execution boundary, compare the
V0 CPU/OpenCV path, V2 CUDA-fused preprocessing, V3 pinned raw staging, and V4
limited double buffering using task accuracy, throughput, mean/P95/P99/maximum
latency, and CPU cost; retain failed gates, negligible increments, severe
tails, and OOM evidence to distinguish a correctness-first deployment point
from a performance-first research trade-off.

**Supporting stages:** Stage Q supplies the frozen INT8 correctness and
performance baseline. Stage R Attempt 2 supplies the authoritative ablation,
the V2 accuracy gate, V3 incremental result, V4 negative result and anomaly,
and R5 Pareto closeout.

**Allowed claim:** In the tested boundary, V2 produced a large descriptive FPS
and mean-latency improvement over V0 but failed Gate D and is research-only;
V3 added no meaningful increment under the project rule; the tested V4 was
dominated, tail-unstable, and accompanied by an OOM anomaly. The retained
decision points are V0 correctness-first and V2 performance-first.

**Mandatory limitations:** V2 is neither correctness-equivalent nor a
production replacement. V3 does not prove pinned memory generally ineffective.
V4 does not prove double buffering generally harmful, and its OOM root cause
was not established. V3/V4 inherit V2 task accuracy through identical
detection SHA. The Pareto result covers only the executed V0/V2/V3/V4 set.

## 5. Important Supporting Chain

```text
Training → ONNX → ORT → FP16 → INT8 → bounded Pipeline
```

- Training freezes the selected YOLOv8n model and recorded task metrics.
- ONNX freezes the export identity and cross-backend contract.
- ORT supplies the Jetson CPU baseline.
- TensorRT FP16 supplies task-level acceptance, raw-Level-B negative evidence,
  descriptive performance, and bounded stability.
- TensorRT INT8 supplies calibration provenance and the accuracy-performance
  prerequisite for Stage R.
- bounded Pipeline supplies execution-form, throughput-boundary, functional,
  and bounded-stability background.

This chain is B/C-grade support for the research and must not be presented as
independent core innovation. Layered raw/task correctness, frozen hashes,
configuration, split, timing boundary, supersession, and negative-evidence
traceability are likewise important B-grade methodology support.

## 6. Thesis Asset Allocation

| Research or chapter function | Frozen asset allocation | Role |
|---|---|---|
| Research object and frozen boundary | Training, frozen PT, ONNX contract, split v2, Engine identities, workload and configuration hashes | Define the bounded study object and provenance |
| ORT baseline | J5.6 tuned k5 and J6 stability | CPU deployment baseline and supporting engineering chain |
| FP16 layered correctness | K5 raw Level B, K5 task evaluation, K7 performance, K6 stability | Explain raw FAIL versus task-level acceptance |
| INT8 accuracy-performance | Q3 calibration/build, Q5 accuracy, Q6 Serial | Establish the direct prerequisite for Stage R |
| bounded Pipeline | P4/P5R/P6/P7 and Q7/Q7 confirmation | Explain execution form, descriptive throughput, and no-material-regression boundaries |
| Stage R profiling | R1 baseline profiling | Motivate current-system input/data-path analysis |
| Stage R ablation | Unified validation and Attempt 2 V0/V2/V3/V4 | Supply the controlled core experiment |
| Pareto and negative results | V2 Gate D, V3 increment, V4 tails/OOM, R5 closeout | Supply multi-objective disposition and limitations |

This is a chapter-function allocation only; it is not thesis prose.

## 7. Engineering Paper Asset Allocation

Frozen topic:

> 面向 Jetson TensorRT INT8 工业缺陷检测的数据路径优化机会与分支消融：精度、吞吐和尾延迟的多目标权衡

- Stage R is the engineering paper's main body and source of core results.
- Stage Q is the important prerequisite for the frozen INT8 accuracy and
  performance context.
- Stages J, K, and P appear only as necessary background.
- The Stage P `4.165718x` observation does not enter the core results.
- The paper does not expand the nine-run training process or the complete
  deployment implementation history.
- Timing boundaries, V2 Gate D FAIL, V4 extreme tails, and the OOM anomaly
  travel with all applicable tables and figures.

## 8. Mandatory Result Boundaries

1. FP16 raw Level B remains `FAIL` (1/16 PASS). It is current canonical
   negative correctness evidence, not invalid historical data.
2. FP16 is accepted only at task level under the frozen evaluation and D066;
   task-level acceptance does not establish raw equivalence.
3. INT8 has a measured accuracy decrease relative to FP16. It must not be
   described as lossless quantization.
4. Stage P `4.165718x` is a formal descriptive throughput observation from a
   frozen offline replay workload under the corrected protocol. It is not
   statistical significance, a universal guarantee, a real-camera result, or
   evidence of lower single-frame latency.
5. Q7 supports `NO_MATERIAL_REGRESSION` from the observed `1.012575x` ratio,
   not a large Pipeline gain.
6. Stage R Attempt 2/v2 is the horizontal ablation authority. Attempt 1 is
   noncomparable diagnostic history only.
7. V2 Gate D is `FAIL`: the mAP50 drop `0.00537575` exceeds the frozen `0.005`
   threshold by `0.00037575`.
8. V2 is a performance-first research trade-off only. It is not
   correctness-equivalent and is not the production/deployment replacement.
9. V3's observed increment over V2 is not meaningful under the project rule;
   it does not support a general conclusion about pinned memory.
10. The tested V4 has severe approximately 8.98–10.24 s tail events in every
    formal run and a retained OOM anomaly. P95/P99 must be accompanied by
    maximum/tail behavior. The OOM root cause is not proven.
11. Metrics with different timing boundaries or execution forms must not be
    placed in an unlabeled direct ranking. Backend host-roundtrip timing is not
    GPU-kernel-only timing, and reciprocal inference FPS is not application
    wall throughput.
12. No power-improvement, no-throttling, industrial long-term stability,
    reliability, leak-certification, or product-readiness claim is permitted.

## 9. Explicitly Excluded Assets and Claims

The detailed exclusion disposition is governed by the Authority Map and
Experiment Use Matrix. Explicitly excluded assets are:

- the invalidated Stage K K7 output-allocation tree and all of its values;
- Stage R Attempt 1 cross-variant metrics, including the approximately 231.9
  FPS V0 figure, from final comparisons;
- Stage Q `split_v1` as the current split authority;
- the old Stage P P5 conclusion based on the invalid cross-window RUN-SHA
  rule;
- superseded reports or closeouts as current numerical/status authorities,
  including the original Stage R R6 overall disposition;
- unexecuted V1 and V5 as results or inferred evidence;
- failed, rejected, smoke, diagnostic, or selective-precision artifacts as
  final numerical sources unless the Authority Map explicitly retains them as
  a current limitation.

The V4 OOM record is excluded from aggregate performance samples but retained
as current supplemental anomaly evidence. FP16 raw Level B FAIL is also
retained current negative evidence and is not part of the historical exclusion
set.

Prohibited claims include universal INT8 bottleneck migration, new detection
or quantization algorithms, raw FP16 equivalence, lossless INT8, V2 production
replacement, generally effective CUDA preprocessing, generally ineffective
pinned memory, generally harmful double buffering, statistical significance,
cross-stage performance ranking without timing boundaries, real-camera
generalization from offline replay, power improvement, and industrial-grade
stability or reliability.

## 10. Experiment Sufficiency Decision

```text
SUFFICIENT_WITH_LIMITATIONS

Must rerun:
NONE

Should rerun:
NONE

Retraining:
NONE

Engine rebuild:
NONE

Additional model/platform/variant:
NONE
```

No new experiment is required. Later table or figure rendering is presentation
work and must use the existing canonical machine-readable inputs.

## 11. Asset Retention Status

- Frozen PT: verified at the recorded external path; size and SHA-256 match;
  `FROZEN_PT_VERIFIED`, `EXTERNAL_LOCAL_ONLY`, `HASH_VERIFIED`, and
  `RETENTION_CONFIRMED`.
- Training archives: verified by external SHA-256, gzip/tar integrity,
  per-file internal manifests, and path/symlink safety.
- ONNX binary: locally present at the canonical ignored path and verified
  against the frozen identity; it remains local-only and absent from a clean
  Git checkout.
- FP16 Engine: externally retained and hash verified against its manifest.
- INT8 Engine and calibration cache: externally retained and hash verified;
  rebuild/recalibration is not required.
- Paper visualizations: not generated yet. Canonical inputs exist, and final
  rendering belongs to later paper-presentation work.

## 12. Phase 1 Entry Conditions

Paper Phase 1 may perform only:

- paper requirements and formatting input;
- paper structure design;
- figure and table inventory design;
- data-table extraction planning;
- chapter-to-evidence mapping;
- literature-search planning.

Paper Phase 1 must not:

- start large-scale body-text drafting directly;
- alter the frozen contribution classification;
- add experiments;
- change the central research line;
- mix timing boundaries or execution forms.

## 13. Final Phase 0 Verdict

COMPLETE

## 14. Next Actor

Paper Project Manager
