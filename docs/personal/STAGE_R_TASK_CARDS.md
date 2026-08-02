# Stage R Task Cards

## Overview

Stage R: Jetson INT8 Inference Data-Path Profiling and Optimization

Authority: Stage R Plan FINAL (`docs/personal/STAGE_R_EXECUTION_PLAN.md`)

Baseline: `4c67858610e14ba7d3c951b33f0948230451827f`

Each card contains: Objective, Execution environment, Entry prerequisites,
Authorized files/components, Required actions, Explicit exclusions,
Tests/Evidence, Gate, Failure states, Next authorized stage.

---

## R0 — Planning Freeze

### Objective

Freeze the Stage R execution plan, decisions, fact inventory, task cards,
pre-R0 manifests, and TASKS status update. Create the feature branch from
exact baseline.

### Execution Environment

Jetson Orin Nano Super. Read-only Git and filesystem operations only.

### Entry Prerequisites

- `main` at `4c67858610e14ba7d3c951b33f0948230451827f`
- `origin/main` at same commit
- Stage Q tag `stage-q-int8-complete-v1.0` object `066eefb134ecaadb3069933efff89d132b9a938d`
- Peeled commit equals baseline
- Clean worktree, clean index, no unexpected untracked files
- Target branch `feature/jetson-int8-data-path-optimization` does not exist

### Authorized Files/Components

Only:
1. `docs/personal/STAGE_R_EXECUTION_PLAN.md`
2. `docs/personal/STAGE_R_FACT_INVENTORY.md`
3. `docs/personal/STAGE_R_TASK_CARDS.md`
4. `docs/personal/DECISIONS.md` (append D081–D083 only)
5. `docs/personal/TASKS.md` (append Stage R status only)
6. `results/validation/stage_r/r0_planning_freeze_v1/pre_r0_baseline_manifest.json`
7. `results/validation/stage_r/r0_planning_freeze_v1/pre_r0_environment_manifest.json`

### Required Actions

1. Verify all pre-start Git checks (branch, HEAD, main, origin/main, tag object,
   peeled commit, worktree, index, untracked, target branch).
2. Create `feature/jetson-int8-data-path-optimization` from exact baseline.
3. Write D081 (Controlled CUDA Preprocessing Exception), D082 (Limited Application
   CUDA Streams Exception), D083 (Cross-Preprocess Identity Exception).
4. Write Stage R Plan FINAL.
5. Write Stage R Fact Inventory.
6. Write these Task Cards.
7. Write Pre-R0 baseline and environment manifests.
8. Update TASKS.md with Stage R status (R0 complete, R1–R6 not authorized).
9. Run consistency validation (allowlist, git diff, Decision uniqueness, plan
   consistency, JSON parsing, forbidden-path audit).
10. Commit with message `docs(stage-r): freeze INT8 data-path optimization plan`.

### Explicit Exclusions

- Production code (`src/`, `include/`, `tests/`, `tools/`, `configs/`)
- `CMakeLists.txt`
- `.gitignore`
- Existing Stage Q Evidence
- TensorRT Engine or manifest
- ONNX, models, datasets
- RuntimeConfig implementation
- Result JSON implementation
- PipelineRunner modifications
- Preprocessor modifications
- TensorRtEngine modifications
- CUDA target additions
- Hardware experiments (benchmark, inference, accuracy, tegrastats sampling,
  Nsight capture, stability, power test, CUDA smoke, Engine load smoke,
  calibration, build)
- Push, merge, tag, rebase, reset, stash

### Tests/Evidence

- `git status --short` (clean after commit)
- `git diff --name-status` (only allowlisted files)
- Decision summary table D081–D083 uniqueness
- Plan FINAL status verification
- JSON syntax validation
- SHA256 of all changed files

### Gate

```text
R0_PASS
```

### Failure States

- `R0_BLOCKED_BASELINE_MISMATCH`
- `R0_BLOCKED_TAG_MISMATCH`
- `R0_BLOCKED_DIRTY_WORKTREE`
- `R0_BLOCKED_EXISTING_BRANCH_CONFLICT`
- `R0_BLOCKED_PLAN_TEXT_MISSING`
- `R0_BLOCKED_FINAL_PLAN_INCONSISTENCY`
- `R0_BLOCKED_REQUIRED_PRE_R0_EVIDENCE_MISSING`

### Next Authorized Stage

```text
R1_NOT_AUTHORIZED_PENDING_USER_REVIEW
```

---

## R1 — Baseline and Profiling

### Objective

Establish RuntimeConfig v5/v6 V0 equivalence, V0 canonical, Phase Barrier,
V0 off/diagnostic profiling, bounded Nsight capture, and bottleneck analysis.

### Execution Environment

Jetson Orin Nano Super. MAXN_SUPER mode 2, CPU affinity 0-5, OpenCV threads 1.
jetson_clocks not invoked. Fan automatic.

### Entry Prerequisites

- R0_PASS
- User review of R0 commit complete
- Explicit R1 authorization from user

### Authorized Files/Components

- RuntimeConfig v6 parser and types
- Phase Barrier implementation in PipelineRunner
- Profiling instrumentation (diagnostic CUDA timing, off mode)
- V0 profiling run scripts and analysis tools
- Nsight capture tooling
- Stage R run manifest generation

### Required Actions

1. Implement RuntimeConfig v6 with data_path variant and profiling mode.
2. Verify V0 (v5) == V0 (v6) including canonical SHA, Engine, manifest,
   postprocess, frame count/order, synchronous ordering, Result JSON v4.
3. Implement Phase Barrier (warmup → measured boundary).
4. Execute 1 × profiling off run.
5. Execute 1 × profiling diagnostic run.
6. Verify diagnostic/off perturbation (throughput ratio >= 0.95, latency
   ratio <= 1.05).
7. Execute 1 × bounded Nsight capture (first 180 measured frames or 15 seconds).
8. Produce V0 bottleneck analysis.

### Explicit Exclusions

- CUDA preprocessing implementation
- Device-input capability
- V2/V3/V4 implementation
- Double Buffer
- Pinned raw staging
- Changes to ORT, FP16, or TensorRT-OFF targets
- Accuracy experiments
- Formal performance experiments

### Tests/Evidence

- RuntimeConfig v5/v6 V0 equivalence evidence
- V0 profiling off Result JSON
- V0 diagnostic timing data
- V0 Nsight trace (local-only)
- Bottleneck analysis summary

### Gate

```text
R1_PASS
```

Condition: V0 canonical maintained, profiling perturbation within bounds.

### Failure States

- `R1_BLOCKED_V0_EQUIVALENCE_FAILED`
- `PROFILING_PERTURBED` (diagnostic perturbation out of bounds; V2/V3 still
  permitted but V4 skipped)
- `R1_BLOCKED_NSIGHT_CAPTURE_FAILED`

### Next Authorized Stage

```text
R2_AUTHORIZED_AFTER_R1_PASS_AND_USER_REVIEW
```

---

## R2 — CUDA Data Path and Correctness

### Objective

Implement CUDA fused preprocessing (V2/V3), TensorRT device-input capability,
and pass all correctness Gates (geometry, tensor, task accuracy, V2/V3 identity).

### Execution Environment

Jetson Orin Nano Super. MAXN_SUPER mode 2, CPU affinity 0-5, OpenCV threads 1.

### Entry Prerequisites

- R1_PASS
- User review of R1 commit complete
- Explicit R2 authorization from user

### Authorized Files/Components

- CUDA preprocessing kernel/module
- `TensorRtDeviceInputCapability` in TensorRT backend
- RuntimeConfig v6 V2/V3 variant support
- Row-aware raw staging copy (pageable for V2, pinned for V3)
- Correctness validation tools (geometry, tensor, accuracy)

### Required Actions

1. Implement CUDA fused preprocessing (resize, LetterBox, BGR→RGB, HWC→CHW,
   float32 normalization).
2. Implement `TensorRtDeviceInputCapability` (device FP32 NCHW input to
   existing Engine/ExecutionContext).
3. Implement V2 (pageable raw staging → H2D → CUDA preprocess → TensorRT).
4. Implement V3 (pinned raw staging → H2D → CUDA preprocess → TensorRT).
5. Validate geometry (resized dimensions, LetterBox scale, padding, original
   dimensions per image).
6. Validate tensor (16-image corpus, MAE <= 5e-4, P99 <= 2/255+1e-6,
   maximum <= 4/255+1e-6, non-finite=0).
7. Validate task accuracy (180-image, mAP50-95 drop <= 0.005, mAP50 drop <= 0.005,
   Precision drop <= 0.010, Recall drop <= 0.010, each-class AP50 drop <= 0.020,
   each-class Recall drop <= 0.030).
8. Verify V2 detection SHA == V3 detection SHA, V2 tensor digest == V3 tensor
   digest.

### Explicit Exclusions

- V4 Double Buffer
- Multiple CUDA streams (V2/V3 use single stream)
- Cross-frame overlap
- GPU NMS / GPU postprocess
- General BufferManager
- Zero-Copy / Mapped memory
- Changes to FP16, ORT targets

### Tests/Evidence

- Geometry validation per-image
- Tensor comparison (16-image corpus)
- Task accuracy evaluation (180-image)
- V2/V3 detection SHA identity
- V2/V3 tensor digest identity

### Gate

```text
R2_PASS
```

Condition: geometry PASS, tensor PASS, task accuracy PASS, V2/V3 identity PASS.

### Failure States

- `STAGE_R_FAILED_CORRECTNESS` (CUDA tensor exceeds thresholds, V2/V3 identity
  cannot be established, or task accuracy exceeds thresholds)

### Next Authorized Stage

```text
R3_AUTHORIZED_AFTER_R2_PASS_AND_USER_REVIEW
```

### R2 Planning Freeze — Unique Execution Contract

The following contract is frozen for R2 and takes precedence over any
underspecified implementation detail in this card. This is a planning-only
freeze; it does not authorize implementation.

#### V2 Pageable Data Path

```text
decoded cv::Mat
→ CPU row-aware raw staging
→ cudaMemcpyAsync H2D
→ CUDA fused preprocessing
→ TensorRT device input
→ existing TensorRT output path
→ existing postprocess
```

CPU responsibilities are decode, geometry metadata, and the row-aware raw
staging copy only. CUDA responsibilities are resize, padding, BGR→RGB,
float32 normalization, and HWC→CHW.

#### V3 Pinned Data Path

V3 uses the V2 path with a long-lived pinned raw buffer. The only allowed new
resources are:

- pinned raw buffer;
- device raw buffer;
- device FP32 input buffer.

Pinned output, mapped memory, zero-copy, and double buffer are forbidden.
V2/V3 use one CUDA stream, one TensorRT ExecutionContext, and no cross-frame
overlap.

#### TensorRtDeviceInputCapability Boundary

TensorRtDeviceInputCapability is backend-specific and exists only inside
backend_tensorrt. It must not be added to IInferenceEngine, HostTensor,
or runtime core. It consumes device FP32 NCHW input and returns the existing
FP32 HostTensor output through the existing TensorRT output path.

The generic PipelineRunner and packet contract remain HostTensor-based. V2/V3
must use a Stage R-specific data-path adapter/runner or equivalent backend-only
execution path; CUDA types must not be added to the generic runner, packets,
or common runtime contract.

#### CUDA Kernel Contract

Input:

```text
uint8 BGR raw image
width
height
row stride
geometry metadata
```

Output:

```text
float32 device NCHW [1,3,640,640]
```

The kernel must not perform NMS, decode, Result JSON generation, or TensorRT
enqueue.

#### Correctness Evidence Contract

- 16-image tensor gate: MAE `<= 5e-4`;
- P99 `<= 2/255 + 1e-6`;
- maximum `<= 4/255 + 1e-6`;
- non-finite count `0`;
- 180-image task accuracy uses the frozen thresholds above in this card;
- V2/V3 tensor digest identical;
- V2/V3 detection SHA identical;
- V0 canonical SHA and Stage Q correctness authority unchanged;
- Result JSON v4 unchanged.

#### File Contract

Implementation may modify only:

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

The following are protected:

```text
HostTensor public contract
IInferenceEngine
ORT backend
FP16 backend
Result JSON v4
Stage Q Evidence
```
---

## R3 — Formal Performance

### Objective

Execute formal paired performance experiments: V0 vs V2, V0 vs V3, V2 vs V3.
Generate primary performance tables.

### Execution Environment

Jetson Orin Nano Super. MAXN_SUPER mode 2, CPU affinity 0-5, OpenCV threads 1.
Environment contract enforced per process.

### Entry Prerequisites

- R2_PASS
- User review of R2 commit complete
- Explicit R3 authorization from user

### Authorized Files/Components

- Formal performance experiment scripts
- Phase Barrier
- Performance analysis tools
- Performance evidence output

### Required Actions

1. Execute V0 vs V2: 3 pairs (180 warmup, 5040 measured, 28 complete cycles,
   drop=0).
2. Execute V0 vs V3: 3 pairs.
3. Execute V2 vs V3: 3 pairs.
4. Report throughput, mean latency, P50, P95, P99, CPU equivalent cores.
5. Compute geometric mean of 3 paired ratios per comparison.

### Explicit Exclusions

- V4 Double Buffer
- Power experiments
- Stability experiments
- Video source
- New Variants

### Tests/Evidence

- Paired performance evidence per comparison
- Performance summary CSV

### Gate

```text
R3_PASS
```

Condition: formal paired Evidence valid. Performance improvement not required
for PASS.

### Failure States

- `INCONCLUSIVE` per comparison (optional, after one rerun)
- `EXPERIMENT_BLOCKED_BY_ENVIRONMENT`

### Next Authorized Stage

```text
R4_AUTHORIZED_AFTER_R3_PASS_AND_USER_REVIEW
```

---

## R4 — Conditional Double Buffer

### Objective

Execute or skip V4 Double Buffer based on V3 profiling gate.

### Execution Environment

Jetson Orin Nano Super. MAXN_SUPER mode 2, CPU affinity 0-5, OpenCV threads 1.

### Entry Prerequisites

- R3_PASS
- User review of R3 commit complete
- Explicit R4 authorization from user

### Authorized Files/Components

- V4 CUDA stream management (preprocess_stream + inference_stream)
- 2 GPU slot / double buffer management
- Frame ordering enforcement (D2H(N) before enqueueV3(N+1))
- V4 correctness and identity validation
- V3 vs V4 performance experiment

### Required Actions

1. Compute opportunity_ratio from V3 diagnostic data.
2. If opportunity_ratio < 0.05: `DOUBLE_BUFFER_SKIPPED_NO_MATERIAL_OPPORTUNITY`.
   Skip V4.
3. If opportunity_ratio >= 0.05:
   a. Implement V4 Double Buffer.
   b. Validate V4 correctness (same as R2 Gates).
   c. Verify V4 detection SHA == V2 detection SHA.
   d. Execute V3 vs V4 formal performance (3 pairs).
   e. Execute bounded V4 Nsight capture.

### Explicit Exclusions

- Third CUDA stream
- Third GPU slot
- Concurrent TensorRT inference
- Output copy overlap
- input-consumed Event
- General stream/slot configuration

### Tests/Evidence

- V3 diagnostic opportunity_ratio
- V4 correctness evidence (if executed)
- V4 identity evidence (if executed)
- V3 vs V4 performance evidence (if executed)
- V4 Nsight trace (if executed)

### Gate

```text
R4_PASS
```

Condition: V4 skipped by gate (valid outcome), or V4 executed and correctness/
identity/performance evidence valid.

### Failure States

- `DOUBLE_BUFFER_SKIPPED_NO_MATERIAL_OPPORTUNITY`
- `DOUBLE_BUFFER_SKIPPED_IMPLEMENTATION_COST`
- `DOUBLE_BUFFER_NEGATIVE_RESULT`

### Next Authorized Stage

```text
R5_AUTHORIZED_AFTER_R4_PASS_AND_USER_REVIEW
```

---

## R5 — Selected Candidate Evaluation

### Objective

Select the best candidate from V2/V3/V4 (if implemented), evaluate Material
Benefit, stability, lifecycle, and V0 vs Candidate power comparison.

### Execution Environment

Jetson Orin Nano Super. MAXN_SUPER mode 2, CPU affinity 0-5, OpenCV threads 1.

### Entry Prerequisites

- R4_PASS
- User review of R4 commit complete
- Explicit R5 authorization from user

### Authorized Files/Components

- Selection logic
- Stability test harness
- Lifecycle test harness (EOS, cancel/error)
- Power experiment tooling (tegrastats)
- Resource monitoring tooling

### Required Actions

1. Select candidate from {V2, V3, V4} per frozen selection rules.
2. Judge Material Benefit (throughput ratio >= 1.05 or CPU ratio <= 0.85 or
   energy ratio <= 0.95, plus P95 <= 1.10, P99 <= 1.15).
3. Execute 300-second stability run (drop=0, no crash/deadlock/CUDA error/
   TensorRT error, SHA stable, clean exit).
4. One stability rerun if first fails.
5. Execute normal EOS/drain lifecycle test.
6. Execute controlled cancel or injected downstream error test.
7. Execute V0 vs Selected Candidate power comparison (3 alternating pairs).
8. Record resource data (VmRSS, cudaMemGetInfo, CUDA allocations).

### Explicit Exclusions

- Expanding Stability Matrix beyond Selected Candidate
- Industrial hard memory thresholds
- Multi-candidate stability comparison
- V4 if skipped

### Tests/Evidence

- Candidate selection rationale
- Material Benefit judgment
- 300-second stability evidence
- Lifecycle evidence (EOS, cancel/error)
- Power evidence (VDD_IN, GPU, RAM, temperature)
- Resource summary

### Gate

```text
R5_PASS
```

Condition: Selected Candidate stability PASS, lifecycle PASS, power evidence
valid.

### Failure States

- `STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED` (no Material
  Benefit, or candidate fails stability twice)

### Next Authorized Stage

```text
R6_AUTHORIZED_AFTER_R5_PASS_AND_USER_REVIEW
```

---

## R6 — Paper Closeout

### Objective

Generate paper experiment chapter materials, Evidence Index, Final Report,
and release readiness. Permanent Stop Rule applies.

### Execution Environment

Jetson Orin Nano Super. Documentation and table generation only.

### Entry Prerequisites

- R5_PASS
- User review of R5 commit complete
- Explicit R6 authorization from user

### Authorized Files/Components

- Paper core tables (accuracy, performance, ablation, power/resources, stability)
- Nsight plots
- `STAGE_R_FINAL_REPORT.md`
- `STAGE_R_EVIDENCE_INDEX.md`
- Paper experiment chapter materials

### Required Actions

1. Generate accuracy table (Table 1).
2. Generate deployment performance table (Table 2).
3. Generate primary ablation table (Table 3).
4. Generate power/resource table (Table 4).
5. Generate stability table (Table 5).
6. Generate Nsight plots.
7. Write Final Report.
8. Write Evidence Index.
9. Produce paper experiment chapter materials.
10. Assess release readiness.
11. Apply Paper Stop Rule.

### Explicit Exclusions

- New features or Variants
- V1, V5, Zero-Copy, Pinned FP32 CPU input
- More Streams, Slots, or candidates
- Output overlap, input-consumed Event
- GPU postprocess/NMS
- ROS2, Qt, Web
- Multi-model, multi-device
- QAT, pruning, distillation
- Industrial-grade Lifecycle
- Push, merge, tag

### Tests/Evidence

- All five paper tables
- Final Report
- Evidence Index
- Paper experiment materials

### Gate

```text
R6_PASS
```

### Failure States

None beyond R0–R5 failure states already handled.

### Next Authorized Stage

```text
NONE — PAPER STOP RULE ACTIVE
```

Subsequently only permitted: Evidence repair, repeat experiments under same
contract, figure organization, statistical analysis, paper writing, limited
supplementary experiments required by reviewers.

---

## R6 Actual Disposition — Documentation-Only Negative Result

Following R2.2 Gate D failure and accepted Decision D086, the frozen planned R3–R5 path was closed by controlled disposition:

R3: SKIPPED_BY_NEGATIVE_RESULT_DISPOSITION
R4: NOT APPLICABLE
R5: SKIPPED — Stage Q V0 retained
R6: COMPLETE

This is an actual-status note, not a rewrite of the original task cards. R6 created only documentation and Evidence closeout artifacts. No implementation, benchmark, correctness rerun, V3/V4 execution, or Stage Q Evidence change was performed.

---

## Out of Scope (Future Work)

The following are explicitly NOT Stage R task cards and are only referenced
as potential future work:

- **V1** — Pinned FP32 CPU input (deleted from Stage R)
- **V5** — Mapped Zero-Copy (deleted from Stage R)
- GPU NMS / GPU postprocess
- General BufferManager
- General asynchronous Inference API
- Multi-model, multi-device deployment
- QAT, pruning, distillation
- ROS2, Qt, Web integration
- Industrial-grade Lifecycle and error recovery

---

## D087 Reopening Addendum (2026-08-02, read-only append)

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

This addendum does not rewrite any frozen task card above it.
