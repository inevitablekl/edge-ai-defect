# Stage R Plan FINAL

## Jetson INT8 Inference Data-Path Profiling and Optimization

## 0. Document Status and Priority

```text
Document:
Stage R Plan FINAL

Based on:
1. Stage R Execution Plan v0.6
2. Stage R Minimal Closure Amendment v1.0
3. Three deterministic editorial fixes

Pre-R0:
PRE_R0_VERIFIED

Environment audit:
VALID

Plan status:
FINAL

Further architecture review:
NOT REQUIRED

R0:
AUTHORIZED

R1–R6:
NOT AUTHORIZED BEFORE R0_PASS

Production implementation:
NOT AUTHORIZED BEFORE R0_PASS
```

This FINAL is the sole execution authority for Stage R.

Where conflicts exist between the prior v0.6 and the Minimal Closure Amendment, the
Minimal Closure Amendment text prevails. Deleted V1, V5, multi-candidate roles,
Replacement Chain, and multi-Variant Stability Matrix are not implementation tasks.

---

# 1. Project Positioning

Stage R serves:

```text
Part-time Master's in Electronic Information Engineering graduation thesis
+
Engineering-application-oriented short paper
+
Edge AI Deployment job-seeking project
```

Stage R does not build an industrial-product-grade inference platform and does not
pursue coverage of all memory modes, exception paths, and runtime combinations.

Execution priority is frozen as:

```text
First:
Obtain credible, reproducible paper experiment data on schedule

Second:
Form a minimal closed loop of correctness and experimental comparability

Third:
Possess basic engineering runnability

Not pursued:
Generalization, productization, and industrial-grade complete exception protection
```

---

# 2. Research Questions

Stage R must answer three questions:

1. After TensorRT INT8 optimization, whether CPU preprocessing and the input data
   path become significant system costs;
2. Whether CUDA fused preprocessing can improve end-to-end performance while
   maintaining detection correctness;
3. Under the same GPU preprocessing path, whether Pinned raw staging is superior to
   Pageable raw staging.

Conditional research:

4. Only when V3 Profiling indicates a real exploitable cross-frame overlap
   opportunity, investigate whether Double Buffer further improves performance.

---

# 3. Verified Baseline

```text
Repository branch:
main

Baseline commit:
4c67858610e14ba7d3c951b33f0948230451827f

Stage Q tag:
stage-q-int8-complete-v1.0

Tag object:
066eefb134ecaadb3069933efff89d132b9a938d

Peeled commit:
4c67858610e14ba7d3c951b33f0948230451827f
```

Stage Q INT8 correctness baseline:

```text
180-frame canonical SHA:
12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2

Test manifest SHA:
ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194

Cycle length:
180
```

Stage R expects to use the following Decisions:

```text
D081 — Controlled CUDA Preprocessing Exception
D082 — Limited Application CUDA Streams Exception
D083 — Cross-Preprocess Identity Exception
```

These Decisions are formally written in R0.

---

# 4. Final Variants

## V0 — Stage Q INT8 Baseline

```text
TensorRT INT8
PipelineRunner
CPU OpenCV preprocessing
Pageable FP32 HostTensor
```

Strictly inherits the Stage Q synchronous ordering:

```text
cudaMemcpyAsync H2D
→ setTensorAddress
→ enqueueV3
→ cudaStreamSynchronize
→ construct exact-size pageable Host output
→ cudaMemcpyAsync D2H
→ cudaStreamSynchronize
→ move HostTensor to postprocess packet
```

## V2 — CUDA Pageable Path

```text
decoded BGR image
→ row-aware copy to pageable raw staging
→ raw H2D
→ CUDA fused preprocessing
→ TensorRT INT8
```

## V3 — CUDA Pinned Path

```text
decoded BGR image
→ row-aware copy to long-lived pinned raw staging
→ raw H2D
→ CUDA fused preprocessing
→ TensorRT INT8
```

V2 and V3 are identical except for the Host allocation type.

## V4 — Conditional Double Buffer

```text
V3
+
2 fixed GPU slots
+
preprocess_stream
+
inference_stream
```

Only allows:

```text
preprocess(N+1)
overlap
inference(N)
```

Continues to maintain:

```text
1 TensorRT ExecutionContext
1 inference worker
maximum unfinished enqueueV3 = 1
D2H(N) before enqueueV3(N+1)
```

---

# 5. Deleted Scope

The following are permanently deleted from Stage R:

```text
V1 Pinned FP32 CPU input
V5 Mapped Zero-Copy
PinnedInputPool
External-backed public HostTensor refactor
General BufferManager
General asynchronous Inference API
Multi-candidate roles
Replacement Chain
Multi-Variant Stability Matrix
Pinned output
Output copy overlap
input-consumed Event
Third CUDA Stream
Third GPU Slot
```

V1 and Zero-Copy are only permitted as paper "Future Work" and must not be restored
as Stage R implementation tasks.

---

# 6. Fixed Runtime Topology

V0–V4 formal experiments uniformly use:

```text
Runner:
PipelineRunner

Workers:
Source
Preprocess
Inference
Postprocess/Sink

Queue capacity:
1

Drop policy:
block

TensorRT ExecutionContext:
1

Inference worker:
1
```

Stage R does not study:

- queue capacity;
- queue topology;
- worker count;
- lock-free queue;
- new Serial vs Pipeline comparisons.

---

# 7. RuntimeConfig v6

RuntimeConfig v5 retains its original behavior.

Stage R uses:

```yaml
schema_version: 6
backend: tensorrt_int8

data_path:
  variant: V0

profiling:
  mode: formal
```

Legal Variants:

```text
V0
V2
V3
V4
```

Legal Profiling Modes:

```text
off
diagnostic
formal
```

Variant uniquely derives:

- CPU or CUDA preprocessing;
- Pageable or Pinned;
- Stream count;
- Slot count;
- Buffering strategy.

Free-form combination of the following is prohibited:

```text
stream_count
slot_count
pinned
mapped
double_buffer
```

Illegal configurations must fail before Source start and CUDA allocation.

---

# 8. Minimal Architecture Contract

The historical interface is preserved:

```cpp
IInferenceEngine::run(const HostTensor&, HostTensor*)
```

V2–V4 permit the addition of one TensorRT-specific narrow capability:

```text
TensorRtDeviceInputCapability
```

This capability is solely responsible for:

- receiving a device FP32 NCHW input;
- using the existing TensorRT Engine and ExecutionContext;
- producing the existing FP32 Host output;
- maintaining the TensorRT INT8-specific boundary.

CUDA types must not leak into the general ORT, FP16, or TensorRT-OFF targets.

---

# 9. V2, V3 Execution Order

Each frame is frozen as:

```text
1. CPU row-aware raw staging copy
2. raw H2D
3. CUDA fused preprocessing
4. setTensorAddress
5. enqueueV3
6. stream synchronize
7. construct exact-size pageable Host output
8. D2H
9. stream synchronize
10. move output to postprocess packet
```

V2 and V3 do not study cross-frame overlap.

---

# 10. V4 Execution Boundaries

Permitted:

```text
preprocess(N+1)
and
inference(N)
concurrent
```

But Frame N must complete in the following order:

```text
inference(N)
→ D2H(N)
→ output packet(N)
→ enqueueV3(N+1)
```

V4 prohibits:

- concurrent TensorRT inference;
- D2H reordering with the next frame's inference;
- output copy overlap;
- more than two in-flight slots.

---

# 11. Phase Barrier

All Diagnostic, Formal, Power, and Stability runs must use the Phase Barrier.

Warmup:

```text
submit exact warmup frames
→ wait last warmup frame reaches Sink
→ verify queues empty
→ verify no in-flight CUDA work
→ synchronize streams
```

Then:

```text
reset timing/stat counters
reset frame/cycle counters
emit measured_phase_start
```

Measured end:

```text
wait last measured frame reaches Sink
→ queues empty
→ synchronize streams
→ emit measured_phase_end
→ finalize evidence
```

Warmup frames must not contaminate measured statistics.

---

# 12. Five Final Gates

## Gate 1 — Baseline

Must satisfy:

```text
RuntimeConfig v5 V0
==
RuntimeConfig v6 V0
```

Including:

- Stage Q canonical SHA;
- Engine, manifest, postprocess;
- frame count/order;
- synchronous ordering;
- Result JSON v4 semantics.

## Gate 2 — Correctness

### Geometry

Per-image preservation of:

- resized dimensions;
- LetterBox scale;
- top/bottom/left/right padding;
- original dimensions.

### Tensor

Freeze a 16-image corpus:

```text
12 original
+
4 deterministic non-square
```

Count all `[1,3,640,640]` FP32 elements, including padding.

Thresholds:

```text
MAE <= 5e-4
P99 <= 2/255 + 1e-6
maximum <= 4/255 + 1e-6
non-finite = 0
```

### Task Accuracy

180-image test manifest, relative to V0:

```text
mAP50-95 drop <= 0.005
mAP50 drop <= 0.005
Precision drop <= 0.010
Recall drop <= 0.010
each-class AP50 drop <= 0.020
each-class Recall drop <= 0.030
```

Drop is absolute metric-point difference.

### Same-path Identity

```text
V2 detection SHA == V3 detection SHA
V2 tensor digest == V3 tensor digest
```

If V4 is implemented:

```text
V4 detection SHA == V2 detection SHA
V4 tensor digest == V2 tensor digest
```

CPU V0 and GPU family are not required to have identical SHA.

## Gate 3 — Performance

Formal paired Evidence is valid.

Lack of performance improvement does not constitute Stage failure.

## Gate 4 — Selected Candidate Stability

```text
300-second stability PASS
normal EOS PASS
cancel/error path PASS
```

## Gate 5 — Evidence Closeout

Must produce:

- accuracy table;
- performance table;
- power/resource table;
- limitations;
- Evidence Index;
- Final Report.

---

# 13. Minimal Profiling

## V0

Execute:

```text
1 × profiling off
1 × profiling diagnostic
1 × bounded Nsight capture
```

Diagnostic perturbation requirement:

```text
diagnostic/off throughput ratio >= 0.95
diagnostic/off mean latency ratio <= 1.05
```

If not satisfied:

```text
PROFILING_PERTURBED
```

Handling:

- component timing is only for qualitative interpretation;
- no strong bottleneck-migration conclusions are claimed;
- V2/V3 formal experiments are still permitted;
- V4 is skipped by default.

## V3

Execute:

```text
1 × diagnostic run
```

Record:

- Host staging copy;
- H2D;
- CUDA preprocess;
- TensorRT;
- D2H;
- worker wait.

## V2

By default, does not execute an independent Diagnostic.

Only when V2/V3 results are anomalous or identity fails, one targeted Diagnostic is
permitted.

## Nsight

V0:

```text
first 180 measured frames
or 15 seconds
whichever comes first
```

If V4 is implemented, one additional bounded Nsight of the same scale is permitted.

Nsight is not the formal throughput or latency authority.

---

# 14. CUDA Timing Sampling

Diagnostic uses 10-cycle stratified rotation:

```text
cycle 0:
frame_in_cycle % 10 == 0

cycle 1:
frame_in_cycle % 10 == 1

...

cycle 9:
frame_in_cycle % 10 == 9
```

After 10 cycles, each of the 180 manifest positions is sampled once.

---

# 15. Formal Performance Matrix

Must execute:

```text
V0 vs V2
V0 vs V3
V2 vs V3
```

If V4 is implemented:

```text
V3 vs V4
```

Each Comparison:

```text
Pair 1:
Control → Candidate

Pair 2:
Candidate → Control

Pair 3:
Control → Candidate
```

Each Process:

```text
warmup:
180 frames

phase barrier:
required

measured:
5040 frames

complete cycles:
28

drop:
0
```

Report:

- throughput;
- mean latency;
- P50;
- P95;
- P99;
- process CPU equivalent cores.

Three paired ratios use geometric mean.

If the three groups show notable fluctuation:

- one complete rerun is permitted;
- if the second run is still unstable, that Comparison is marked `INCONCLUSIVE`;
- other valid Comparisons continue to be used;
- no Variant Replacement mechanism is established.

---

# 16. V4 Conditional Entry

V4 is not a required condition for paper completion.

Use V3 Diagnostic:

```text
P =
mean(H2D duration)
+
mean(CUDA preprocess duration)

T =
mean(TensorRT duration)

opportunity_ratio =
min(P, T) / (P + T)
```

Execution condition:

```text
opportunity_ratio >= 0.05
```

If not satisfied:

```text
DOUBLE_BUFFER_SKIPPED_NO_MATERIAL_OPPORTUNITY
```

If V4 implementation difficulty clearly exceeds expectations, stop and record:

```text
DOUBLE_BUFFER_SKIPPED_IMPLEMENTATION_COST
```

If V4 is correct but has no performance benefit:

```text
DOUBLE_BUFFER_NEGATIVE_RESULT
```

None of the above statuses prevent Stage R completion.

---

# 17. Selected Candidate

Candidate scope:

```text
V2
V3
V4 if implemented
```

Variants entering selection must:

- correctness PASS;
- same-path identity PASS;
- formal Evidence valid;
- no clear non-runnable issues.

Selection order:

1. higher throughput;
2. when throughput difference < 1%, choose the one with lower CPU equivalent cores;
3. when still close, choose the one with lower complexity:

```text
V2
→ V3
→ V4
```

For the Selected Candidate to receive recommendation qualification, it must also
satisfy:

```text
P95 latency ratio <= 1.10
P99 latency ratio <= 1.15
```

If not satisfied, it may be retained as a negative experimental result, but must not
be recommended to replace V0.

---

# 18. Material Benefit Criteria

Relative to V0, satisfying at least one constitutes Material Benefit:

```text
throughput ratio >= 1.05

or

CPU equivalent cores ratio <= 0.85

or

Gross board energy/frame ratio <= 0.95
```

And must simultaneously satisfy:

```text
P95 latency ratio <= 1.10
P99 latency ratio <= 1.15
```

If no benefit criterion is met:

```text
STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED
```

All judgments use unrounded values.

---

# 19. Selected Candidate Stability

Only the Selected Candidate is tested.

## Stability

```text
active duration >= 300 seconds
drop = 0
no crash
no deadlock
no CUDA error
no TensorRT error
complete-cycle SHA stable
clean process exit
```

External timeout:

```text
600 seconds
```

## Rerun

First failure:

```text
allow one complete stability rerun
```

If the second attempt still fails:

- Candidate must not be recommended;
- no other replacement candidate is selected;
- the Stability Matrix is not expanded;
- if correctness and formal performance Evidence remain valid, classify as:

```text
STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED
```

And clearly state in the Final Report:

```text
Candidate showed a stability limitation and is not recommended
to replace the Stage Q baseline.
```

If the failure manifests as deadlock, inability to exit, or unrecoverable CUDA error,
it must be explicitly recorded as a Candidate implementation limitation.

## Memory

Only record:

- post-warmup VmRSS;
- several checkpoints during the run;
- VmRSS before the end;
- `cudaMemGetInfo`;
- fixed CUDA allocation count.

Only require:

```text
no continuous monotonic growth
no fixed per-cycle growth
no long-lived CUDA allocation growth during measured phase
```

No industrial-grade hard memory thresholds are set.

## Lifecycle

Execute:

```text
1 normal EOS/drain
1 controlled cancel or injected downstream error
```

Require:

- threads can exit;
- no deadlock;
- no residual CUDA error;
- subsequent processes can start again.

---

# 20. Power and Resources

Only execute:

```text
V0 vs Selected Candidate
```

Using three alternating Power Pairs.

Primary authority:

```text
tegrastats VDD_IN
```

Compute:

```text
Gross board energy/frame
=
integral(VDD_IN power over measured active window)
/
accepted frames
```

INA3221:

- only one sanity check;
- no 5% hard Gate;
- when significant discrepancy with tegrastats exists, record:

```text
POWER_MEASUREMENT_LIMITATION
```

This limitation does not prevent Stage completion, but Energy must not be the sole
recommendation basis.

Resource data is extracted from the following existing runs:

- Formal run: CPU equivalent cores;
- Power run: GPU, RAM, temperature, VDD_IN;
- Stability run: resource variation trends.

Final report:

- CPU equivalent cores;
- GPU utilization mean;
- RAM mean/peak;
- temperature mean/peak;
- mean/peak VDD_IN;
- J/frame.

No independent Resource Diagnostic Matrix is executed.

---

# 21. Minimal Environment Contract

Formal experiments are fixed at:

```text
nvpmodel:
MAXN_SUPER

mode:
2

CPU affinity:
0-5

OpenCV threads:
1

jetson_clocks:
not invoked

fan:
automatic

manual PWM/clock writes:
prohibited
```

Before each formal Process, confirm:

- critical temperatures below 65°C;
- no throttle/OC;
- no concurrent compilation, training, or other benchmarks;
- power mode, affinity, OpenCV threads correct.

Pairs use alternating order.

If starting temperature or environment is clearly inconsistent:

- wait and rerun the corresponding Process or Pair once;
- no multi-layer environment state machine is established.

If comparable environment still cannot be obtained:

```text
EXPERIMENT_BLOCKED_BY_ENVIRONMENT
```

Do not force-generate performance conclusions.

---

# 22. Minimal Evidence

Result JSON v4 remains unchanged.

Stage R minimal tracked Evidence:

```text
StageRRunManifest v1
profiling_summary.json
correctness_summary.json
performance_summary.csv
power_resource_summary.csv
STAGE_R_FINAL_REPORT.md
STAGE_R_EVIDENCE_INDEX.md
```

Each Run Manifest records at minimum:

- run_id;
- Variant;
- process type;
- commit;
- binary SHA;
- config SHA;
- Engine SHA;
- test manifest SHA;
- environment summary;
- Result JSON path and SHA;
- exit status.

Raw Evidence remains local-only:

- Nsight trace;
- full Result JSON;
- raw tegrastats;
- frame trace;
- tensor dump;
- temporary CUDA output.

No complex Replacement, Memory Strategy, Resource, or multi-level Classification
Schema is implemented.

---

# 23. Stage Breakdown

## R0 — Planning Freeze

Only completes:

- creation from exact baseline of:

```text
feature/jetson-int8-data-path-optimization
```

- writing D081–D083;
- committing this Stage R Plan FINAL;
- committing the Fact Inventory summary;
- committing the Pre-R0 Evidence manifests;
- freezing the minimal Task Cards.

R0 prohibits:

- modifying production code;
- modifying CMake;
- adding CUDA targets;
- running hardware experiments.

Gate:

```text
R0_PASS
```

## R1 — Baseline and Profiling

Completes:

- RuntimeConfig v5/v6 V0 equivalence;
- V0 canonical;
- Phase Barrier;
- V0 off/diagnostic;
- V0 bounded Nsight;
- bottleneck analysis.

## R2 — CUDA Data Path and Correctness

Completes:

- RuntimeConfig v6;
- TensorRT device-input capability;
- V2/V3;
- CUDA fused preprocessing;
- geometry;
- tensor;
- task accuracy;
- V2/V3 identity.

### R2 Planning Freeze — Final Execution Contract

```text
R2 Plan:
FINAL

R2 implementation:
NOT AUTHORIZED

Planning freeze:
DOCUMENTATION-ONLY
```

This section is the unique R2 implementation contract. It freezes the minimum
Stage R data path and correctness boundary; it does not authorize production
implementation, build, or experiment execution.

V2 pageable path:

```text
decoded cv::Mat
→ CPU row-aware raw staging
→ cudaMemcpyAsync H2D
→ CUDA fused preprocessing
→ TensorRT device input
→ existing TensorRT output path
→ existing postprocess
```

The CPU may decode images, compute geometry metadata, and perform the required
row-aware raw staging copy. CPU must not perform the V2/V3 functional pixel
transform. CUDA performs resize, padding, BGR→RGB, float32 normalization, and
HWC→CHW.

V3 is the same path with long-lived pinned raw staging. The only newly allowed
resources are a pinned raw buffer, a device raw buffer, and a device FP32 input
buffer. Pinned output, mapped memory, zero-copy, and double buffering are
forbidden. V2/V3 use one CUDA stream, one TensorRT ExecutionContext, and no
cross-frame overlap.

TensorRtDeviceInputCapability exists only inside backend_tensorrt. It may
receive a device FP32 NCHW input and return the existing FP32 HostTensor
output through the existing TensorRT output path. It must not enter
IInferenceEngine, HostTensor, or runtime core.

The current generic PipelineRunner and packet contract carry HostTensor input.
V2/V3 must therefore use a Stage R-specific data-path adapter/runner or an
equivalent backend-specific execution path. CUDA types must not be added to
the public generic PipelineRunner, packet types, or common runtime contract.

CUDA fused preprocessing has this fixed contract:

```text
Input:  uint8 BGR raw image, width, height, row stride, geometry metadata
Output: float32 device NCHW [1,3,640,640]
```

The kernel boundary excludes NMS, decode, Result JSON generation, and
TensorRT enqueue.

R2 correctness evidence is fixed as follows:

- 16-image tensor gate: MAE `<= 5e-4`, P99 `<= 2/255 + 1e-6`, maximum
  `<= 4/255 + 1e-6`, non-finite count `0`;
- 180-image task accuracy thresholds remain the R2 Task Card thresholds;
- V2 and V3 tensor digests must be identical;
- V2 and V3 detection SHA values must be identical;
- V0 canonical SHA and Stage Q correctness authority remain unchanged;
- Result JSON v4 remains unchanged, with CUDA-specific evidence in separate
  Stage R evidence/manifest records.

Implementation-phase file whitelist:

```text
backend_tensorrt/
stage_r/
tools/validation/
tests/
configs/stage_r/
CMakeLists.txt
docs/personal/
results/validation/stage_r/
```

The following are protected and must not be modified by R2:

```text
HostTensor public contract
IInferenceEngine
ORT backend
FP16 backend
Result JSON v4
Stage Q Evidence
```

## R3 — Formal Performance

Completes:

```text
V0 vs V2
V0 vs V3
V2 vs V3
```

Generates primary performance tables.

## R4 — Conditional Double Buffer

Based on V3 Profiling:

```text
execute V4
```

or:

```text
DOUBLE_BUFFER_SKIPPED
```

If executed:

- V4 correctness;
- V4 identity;
- V3 vs V4;
- bounded V4 Nsight.

## R5 — Selected Candidate Evaluation

Completes:

- Selected Candidate;
- Material Benefit judgment;
- 300-second stability;
- one rerun quota;
- normal EOS;
- cancel/error;
- V0 vs Candidate Power;
- resource summary.

## R6 — Paper Closeout

Only permits:

- accuracy table;
- performance table;
- power/resource table;
- Nsight plots;
- Evidence Index;
- Final Report;
- paper experiment chapter materials;
- release readiness.

Must not add new features or Variants.

---

# 24. Final Classification

## Recommended

```text
STAGE_R_COMPLETE_DATA_PATH_OPTIMIZATION_RECOMMENDED
```

Conditions:

- correctness PASS;
- formal Evidence valid;
- Selected Candidate stable;
- at least one Material Benefit criterion met;
- no significant P95/P99 regression.

## Negative Result

```text
STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED
```

Used for:

- no Material Benefit;
- V4 no benefit;
- Selected Candidate two stability failures;
- performance improvement insufficient to replace V0.

Negative results are still valid paper conclusions.

## Complete with Measurement Limitation

```text
STAGE_R_COMPLETE_WITH_MEASUREMENT_LIMITATION
```

Used for:

- Profiling clearly perturbed;
- Power sanity check shows significant discrepancy;
- partial resource data incomplete;

but correctness and formal performance experiments remain valid.

## Failed Correctness

```text
STAGE_R_FAILED_CORRECTNESS
```

Used for:

- CUDA tensor exceeds thresholds;
- V2/V3 identity cannot be established;
- task accuracy exceeds thresholds.

## Blocked

```text
STAGE_R_BLOCKED_ENVIRONMENT_OR_REQUIRED_ASSET
```

Used for:

- Engine, manifest, hardware, or required tools missing;
- environment cannot satisfy formal experiment requirements long-term;
- required experiments cannot be legally run.

---

# 25. Paper Core Tables

## Table 1: Model Accuracy

| Backend/Path | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| FP16 | | | | |
| INT8 V0 | | | | |
| INT8 CUDA Candidate | | | | |

The FP16 row directly reuses previously frozen Evidence, but must simultaneously
satisfy:

```text
same frozen model
same test manifest
same accuracy definition
same postprocess contract
```

Stage R does not re-execute FP16 unless existing Evidence is missing, corrupted, or
contract-inconsistent.

## Table 2: Deployment Performance

| Variant | Preprocess | Memory | Mean | P95 | P99 | FPS |
|---|---|---|---:|---:|---:|---:|
| V0 | CPU | Pageable FP32 | | | | |
| V2 | CUDA | Pageable Raw | | | | |
| V3 | CUDA | Pinned Raw | | | | |
| V4 | CUDA | Double Buffer | | | | |

When V4 is not executed, note:

```text
Skipped by profiling gate
```

## Table 3: Primary Ablation

| Comparison | Throughput Ratio | Mean Ratio | P95 Ratio | CPU Ratio |
|---|---:|---:|---:|---:|
| V0 vs V2 | | | | |
| V0 vs V3 | | | | |
| V2 vs V3 | | | | |
| V3 vs V4 | | | | |

## Table 4: Power and Resources

| Variant | GPU | CPU | RAM | Mean Power | J/frame |
|---|---:|---:|---:|---:|---:|
| V0 | | | | | |
| Selected Candidate | | | | | |

## Table 5: Stability

| Variant | Duration | Frames | Drop | Crash/Error | SHA Stable |
|---|---:|---:|---:|---|---|
| Selected Candidate | 300 s | | 0 | PASS | PASS |

---

# 26. Paper Stop Rule

After R6 completes, the short paper's technical implementation permanently stops
expansion.

Must not restore or add:

- V1;
- V5;
- Zero-Copy;
- Pinned FP32 CPU input;
- more candidates;
- more Streams or Slots;
- output overlap;
- input-consumed Event;
- GPU postprocess/NMS;
- ROS2, Qt, Web;
- multi-model, multi-device;
- QAT, pruning, distillation;
- industrial-grade Lifecycle.

Subsequently only permitted:

- Evidence repair;
- repeat experiments under the same contract;
- figure organization;
- statistical analysis;
- paper writing;
- limited supplementary experiments required by reviewers.

## 28. Actual R6 Disposition — Documentation-Only Negative Result

The original planned path was R3–R5. After R2.2 Gate D failed and D086 was accepted, the actual disposition is recorded without rewriting the frozen execution contract:

R3: SKIPPED_BY_NEGATIVE_RESULT_DISPOSITION
R4: NOT APPLICABLE
R5: SKIPPED — Stage Q V0 retained
R6: COMPLETE

R6 was documentation-only. No new Variant, performance experiment, correctness experiment, implementation, or Stage Q Evidence change was authorized.
The final classification is:

STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED

---

# 27. Final Authorization

```text
Stage R Plan:
FINAL

Further plan version:
NOT REQUIRED

Further architecture review:
NOT REQUIRED

Pre-R0:
VERIFIED

Environment audit:
VALID

R0:
AUTHORIZED

R1–R6:
NOT AUTHORIZED BEFORE R0_PASS

Feature branch creation:
AUTHORIZED IN R0 ONLY

Decision D081–D083 write:
AUTHORIZED IN R0 ONLY

Production code:
NOT AUTHORIZED BEFORE R0_PASS

CMake/CUDA implementation:
NOT AUTHORIZED BEFORE R0_PASS

Hardware experiments:
NOT AUTHORIZED BEFORE R0_PASS
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

This addendum does not rewrite any frozen plan section above it.
