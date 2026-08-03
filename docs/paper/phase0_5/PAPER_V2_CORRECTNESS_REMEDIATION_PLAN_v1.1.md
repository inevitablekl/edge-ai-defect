# Paper V2 Correctness Remediation Plan v1.1

## 1. Plan Status

```text
READY_FOR_PROJECT_MANAGER_REVIEW
```

This is the Paper Phase 0.5C-P bounded planning output. It is a design and
execution contract only. No production source, kernel, configuration, result,
model, Engine, or historical evidence was changed while preparing it. No
build, correctness run, accuracy run, benchmark, commit, push, or tag is
authorized by this document.

The sole planned remediation is an OpenCV 4.5.4-aligned fixed-contract CUDA
resize semantic remediation. The scope is intentionally limited to the
already supported resize numerical-contract difference between the V0 CPU path
and the V2 CUDA path.

## 2. Repository and Evidence Baseline

### 2.1 Git and execution state

| Item | Observed value |
|---|---|
| Repository root | `/home/orin/edge-ai/edge-ai-defect` |
| Branch | `main` |
| HEAD | `cccfec41505fa68991cab1a9ba7ed1d6b20ceb59` |
| `origin/main` | `cccfec41505fa68991cab1a9ba7ed1d6b20ceb59` |
| Required synchronization commit | present; exact HEAD is the required commit |
| `git status --short` | empty; no tracked or untracked modification |
| Current date/time | `2026-08-03 21:50:10 CST +0800` |
| Time zone | `Asia/Shanghai` / `CST` / `+0800` |

`git fetch origin` was executed. The required fast-forward was unnecessary
because HEAD already equals `origin/main`. No rebase, reset, clean, stash,
merge commit, evidence deletion, commit, push, or tag was performed.

### 2.2 Platform and software facts

The current shell reports L4T R36, revision 5.0, and OpenCV C++ `4.5.4`
through `pkg-config`. The repository's platform authority records the Stage K
target/observed deployment environment as Jetson Orin Nano Super, aarch64,
L4T `R36.5.0`, CUDA `12.6.68`, TensorRT `10.3.0.30` / `v100300`, with
JetPack `6.2.2` retained as the target contract. These values are referenced
from `docs/personal/ENVIRONMENT.md` and the Stage K platform evidence; they
are not reclassified as new experiment evidence by this plan.

The installed OpenCV package exposes the project-used `opencv4` module, but
the current include path does not contain `opencv2/cudaimgproc.hpp` or
`opencv2/cudawarping.hpp`. NPP headers/libraries are present in the CUDA
installation, but NPP is not an existing project dependency or resize
semantic authority. No package, SDK, JetPack, CUDA, TensorRT, or OpenCV
installation was changed.

### 2.3 Read-only authorities used

The following required authorities were read:

- `docs/paper/phase0_5/PAPER_CORE_VALIDITY_AUDIT_v1.0.md`
- `docs/paper/phase0_5/PAPER_DATASET_SPLIT_SENSITIVITY_FINAL_v1.0.md`
- `docs/paper/phase0/PAPER_EVIDENCE_AUTHORITY_MAP_v1.0.md`
- `docs/paper/phase0/PAPER_EXPERIMENT_USE_MATRIX_v1.0.csv`
- `docs/paper/phase0/PAPER_PHASE0_FINAL_FREEZE_v1.0.md`
- `docs/personal/STAGE_R_FINAL_REPORT.md`
- `docs/personal/STAGE_R_R2_V2_PAGEABLE_REPORT.md`
- `docs/personal/STAGE_R_EVIDENCE_INDEX.md`
- `docs/personal/STAGE_R_EXECUTION_PLAN.md`
- `docs/personal/STAGE_R_TASK_CARDS.md`
- `docs/personal/ENVIRONMENT.md`

The dataset split decision remains closed as
`DATASET_SPLIT_REMEDIATION_COMPLETE` / `SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL`.
No training, model re-freeze, ONNX export, Engine rebuild, calibration change,
or test-split change is part of this plan.

## 3. Confirmed Problem Boundary

The current V2 evidence is bounded as follows:

| Item | Current authority |
|---|---|
| Gate A | PASS: 180 frames, order/paths/dimensions valid, drop 0, EOS PASS, worker join PASS, Result JSON v4 valid |
| Gate B | PASS: geometry valid; tensor MAE `0.00041216449077775033`, P99 `0.0039216279983520508`, max absolute error `0.0039216279983520508`, non-finite `0` |
| Gate C | PASS: V0 regression and frozen baseline detection SHA remain valid |
| Gate D | FAIL after the existing 11-bit remediation |
| Current V2 mAP50 drop | `0.00537575` |
| Frozen mAP50 drop limit | `0.005` |
| Excess over limit | `0.00037575` |
| Current role | performance-first research trade-off; not a correctness-equivalent replacement |

The evidence supports one numerical difference: CUDA uses a custom resize
implementation while V0 uses OpenCV `INTER_LINEAR`. The current CUDA path
also contains custom coefficient quantization, clamping, and integer
accumulation. The previous 11-bit coefficient change improved the task result
but did not pass Gate D. It did not implement a complete OpenCV 4.5.4-aligned
fixed-contract separable resize contract.

The evidence does not support adding BGR/RGB order, normalization, HWC/CHW,
letterbox geometry, padding, postprocessing, NMS, calibration, Engine, or
FP16-preprocessing candidates to this remediation.

## 4. Current CPU and CUDA Resize Contracts

### 4.1 CPU/OpenCV call chain

The V0 path is:

```text
Preprocessor::preprocess
  -> letterbox_bgr
     -> compute_letterbox_geometry
     -> cv::resize(..., cv::INTER_LINEAR) when dimensions change
     -> cv::copyMakeBorder(..., cv::BORDER_CONSTANT, 114)
  -> BGR cv::Mat to RGB NCHW float32, /255
```

Relevant files and functions are:

- `src/preprocessor.cpp`: `Preprocessor::preprocess`; writes RGB NCHW
  float32 values from `cv::Vec3b`.
- `src/letterbox.cpp`: `compute_letterbox_geometry` and `letterbox_bgr`;
  owns resize, padding, and the CPU geometry contract.
- `include/edge_ai_defect/preprocess/letterbox.hpp`:
  `ImageTransformMetadata` and the geometry interface.

The geometry is computed from the shared CPU helper: gain, resized dimensions,
and split padding are not independently recomputed by the CUDA path.

### 4.2 CUDA call chain

The V2 path is:

```text
PageableRunner::run
  -> CudaPreprocessor::compute_geometry
  -> CudaPreprocessor::preprocess
     -> cudaMemcpy2DAsync H2D
     -> preprocess_kernel on the TensorRT CUDA stream
  -> TensorRtEngine::run_device_input
  -> existing postprocess and ResultSink
```

The same shape applies to `PinnedRunner`; V4's `DoubleBufferRunner` adds two
resource sets but remains serialized by one CUDA stream and explicit
synchronization. Relevant files are:

- `backend_tensorrt/cuda_preprocessor.cu` and
  `backend_tensorrt/cuda_preprocessor.hpp`;
- `stage_r/pageable_runner.cpp`;
- `stage_r/pinned_runner.cpp`;
- `stage_r/double_buffer_runner.cpp`;
- `tools/validation/stage_r_v2_tensor_gate.cpp`;
- `tools/validation/stage_r_v2_task_harness.cpp`;
- `tools/benchmark/stage_r_r3_ablation_runner.cpp`.

Inside the current CUDA kernel:

- source coordinates use a half-pixel mapping;
- coefficients are quantized to the current 11-bit fixed-point scale;
- weights are rounded with CUDA round-to-nearest conversion;
- samples are clamped to input edges;
- products are accumulated with 64-bit integers and shifted with a fixed
  rounding constant;
- padding writes normalized `114/255` to all three planes;
- BGR input is written as RGB NCHW float32 and divided by 255.

The confirmed mismatch boundary is the resize numerical contract: source
coordinate mapping, coefficient table/precision, rounding, accumulation,
saturation/clamping, and the order in which the resize operation is applied.
The other operations remain outside the remediation.

## 5. Candidate Remediation Analysis

### Candidate A — OpenCV 4.5.4-aligned fixed-contract CUDA resize

This is the only candidate that directly targets the proven difference without
adding a runtime dependency. The implementation would remain in the existing
CUDA preprocessor and would freeze, from the locally used OpenCV C++ 4.5.4
CPU reference, the following items for the fixed Stage R contract:

- source-coordinate mapping;
- coefficient table construction and precision;
- coefficient rounding;
- horizontal/vertical accumulation order;
- output rounding and 8-bit saturation behavior;
- edge handling;
- unchanged BGR-to-RGB channel order and final normalization.

The frozen applicability is the current Jetson environment, the current
`compute_letterbox_geometry`, `CV_8UC3` BGR input, 640x640 output, uint8 resize
result semantics, and RGB NCHW float32 `/255` output. This is not a universal
bit-exact claim for all OpenCV inputs, dimensions, data types, or versions; it
is not a claim to implement generic OpenCV resize. The implementation must be
small and fixed-contract, and must not copy a large OpenCV implementation into
the repository. A BSD-licensed implementation may be informed by the local
contract, but the project will retain only its own minimal code and an
attribution note if source-level consultation is needed.

Advantages: direct causal scope, no new library, GPU pixel processing remains
the research object, and the existing tensor comparator can validate it.

Risks: the public `cv::resize` API does not expose all internal tables, exact
behavior may be version-specific, and a complete separable fixed-point
implementation can be larger than the existing kernel. Therefore the future
implementation must first freeze the bounded OpenCV 4.5.4-aligned facts and
must stop as `REMEDIATION_INVALID`/`BLOCKED` if the bounded implementation
cannot be completed without broad source copying or scope expansion.

### Candidate B — `cv::cuda::resize`, NPP, or another CUDA primitive

`cv::cuda::resize` is not available through the current OpenCV headers and is
not part of the project's current CMake dependency graph. NPP libraries are
installed, but using them would add an explicit NPP dependency and its API
version/platform contract to the build. No existing evidence establishes that
the selected NPP resize mode is numerically identical to the project's OpenCV
4.5.4 CPU `INTER_LINEAR` path. This candidate would also complicate the
license, build, and provenance boundary without addressing that proof gap.

Disposition: not selected. No JetPack, CUDA, OpenCV upgrade, package install,
or new framework is permitted to make it available.

### Candidate C — CPU-reference-assisted coefficients with GPU pixel processing

This could keep the final resize pixels on the GPU while computing small
coordinate/coefficient tables on the host and uploading them. It would still
be GPU preprocessing, not a complete CPU resize, but it adds a host-side
per-image contract, a small H2D metadata transfer, and another lifetime/state
boundary. It does not remove the need to establish the exact OpenCV 4.5.4
coefficient semantics. The host work is small relative to a full CPU resize,
but its cost must be measured rather than assumed.

Disposition: comparison-only fallback. It is not the single planned
implementation because Candidate A keeps the semantic implementation and
resource model inside the existing CUDA preprocessor with fewer moving parts.

### Candidate D — keep current V2 unchanged

This is the formal no-remediation fallback: retain V2 as research-only,
preserve Gate D FAIL, and move directly to a timing-aligned 0.5D comparison.
It is preferred over scope expansion if Candidate A cannot be specified and
tested against OpenCV 4.5.4 within the bounded file scope.

Disposition: fallback only, not the primary recommendation below.

## 6. Recommended Single Remediation

Recommend Candidate A:

```text
OpenCV 4.5.4-aligned fixed-contract CUDA resize
inside the existing CUDA preprocessor, with explicit V2R/V3R identity.
```

The implementation contract is:

1. Keep `compute_letterbox_geometry`, target shape, padding value, BGR input,
   RGB NCHW output, float32 output, normalization, TensorRT input, and
   postprocessing unchanged.
2. Replace only the current V2R/V3R resize semantic with the frozen OpenCV
   4.5.4-aligned fixed-contract mapping, coefficient, rounding, accumulation,
   saturation, and edge behavior.
3. Keep historical V2/V3 semantics selectable and unchanged. The new mode
   must not silently rewrite the historical V2/V3 evidence identity.
4. Use one fixed semantic implementation. There is no coefficient-precision
   search, rounding-mode search, test-mAP tuning, or second remediation round.
5. Preserve the existing single-stream GPU preprocessing path. Do not add
   Pipeline, additional streams, V4 overlap, GPU NMS, or performance work.
6. If the OpenCV 4.5.4 contract cannot be established without copying broad
   third-party internals, stop before expanding scope and use Candidate D's
   research-only disposition.

The already executed 11-bit change is historical evidence, not the new
remediation. It remains recorded as an improvement that was insufficient;
its result must not be overwritten or relabeled as V2R.

## 7. Variant and Evidence Identity

### 7.1 Variant names

The planned identities are:

| Identity | Runtime path | Role |
|---|---|---|
| `V2` | pageable raw staging -> historical CUDA resize -> TensorRT device input | historical research evidence; unchanged |
| `V3` | pinned raw staging -> historical CUDA resize -> TensorRT device input | historical research evidence; unchanged |
| `V2R` | pageable raw staging -> OpenCV 4.5.4-aligned fixed-contract CUDA resize -> TensorRT device input | primary correctness remediation candidate |
| `V3R` | pinned raw staging -> the same OpenCV 4.5.4-aligned fixed-contract CUDA resize -> TensorRT device input | corresponding pinned companion |
| `V0` | CPU/OpenCV preprocessing -> HostTensor -> TensorRT | correctness baseline |

`V2R` and `V3R` must use the same CUDA resize semantic mode. Staging memory
type is their only intended difference. If their tensor digest or detection
SHA differs under the same workload, the difference is a correctness failure,
not a reason to tune the kernel.

### 7.2 Config and source identity

Future implementation may add independent configs, for example:

- `configs/stage_r/runtime_v6_v2r_pageable.yaml`;
- `configs/stage_r/runtime_v6_v3r_pinned.yaml`;
- `configs/stage_r/runtime_v6_v0_timing_aligned.yaml` for the later 0.5D
  common timing contract.

The historical V2/V3 configs and evidence directories remain intact. New
correctness results must use separate directories such as:

- `results/validation/stage_r/r2_v2r_correctness_v1/`;
- `results/validation/stage_r/r2_v3r_correctness_v1/`.

If accepted for the later performance comparison, the separate 0.5D bundle
must use a new directory such as
`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_v1/`; it must never overwrite
`r3_v0_v2_v3_v4_ablation_v2`.

### 7.3 Metadata and hash binding

Every new run manifest/result must record, at minimum:

- `variant`: `V2R` or `V3R`;
- `remediation_id`: `opencv_4_5_4_aligned_fixed_contract_cuda_resize_v1`;
- `parent_variant`: `V2` or `V3`;
- `resize_semantic_contract`: OpenCV C++ `4.5.4` CPU reference;
- commit SHA;
- config SHA-256;
- binary SHA-256;
- frozen Engine SHA-256 and Engine manifest SHA-256;
- model contract SHA-256;
- test manifest SHA-256;
- result JSON SHA-256 and detection/tensor digest values.

The historical V2/V3 metadata remains historical. New metadata must make it
impossible to confuse the old 11-bit result with V2R. The frozen Engine,
model, calibration, postprocess thresholds, and 180-image test manifest must
be byte-identical to the current authorities.

## 8. Authorized File Scope

Only a later, explicit 0.5C-I implementation task may touch the following
minimum set, and only for the remediation:

- `backend_tensorrt/cuda_preprocessor.cu`: the bounded resize semantic and
  any directly necessary fixed-contract helper;
- `backend_tensorrt/cuda_preprocessor.hpp`: only if an explicit semantic-mode
  or variant-selection interface is required;
- `stage_r/pageable_runner.cpp` / `.hpp` and `stage_r/pinned_runner.cpp` /
  `.hpp`: only to select V2R/V3R while preserving V2/V3 behavior;
- `include/edge_ai_defect/runtime/runtime_types.hpp` and
  `src/runtime_config.cpp`: only for explicit V2R/V3R enum/parser support;
- the two new V2R/V3R configs and the timing-aligned V0 config;
- `tests/test_stage_r_cuda_preprocess.cpp` or one narrowly scoped
  resize-focused test registration;
- `tools/validation/stage_r_v2_tensor_gate.cpp`,
  `tools/validation/stage_r_v2_task_harness.cpp`, and
  `tools/validation/stage_r_v3_task_harness.cpp` only where required for
  focused differential validation or V2R/V3R identity;
- `CMakeLists.txt` only for necessary target/test registration;
- the minimum runtime/result metadata files needed to emit remediation
  identity and hash binding.

No implementation task may modify the TensorRT Engine implementation or
Engine, postprocessor, NMS, model, calibration, `src/letterbox.cpp` CPU
authority, Stage P Pipeline, V4 overlap, ROS2, UI, general memory framework,
other backend, or unrelated tests.

## 9. Verification Gates

The future implementation must run exactly one bounded implementation cycle.
The existing formal thresholds below are copied from Stage R task/evidence
authorities; this plan creates no new task-acceptance threshold.

### Gate C0 — Build and Unit Contract

Required checks:

- CUDA-enabled build of the affected targets;
- existing Stage R CUDA/preprocessing tests with no regression;
- one resize-focused test for identity, upscale/downscale, non-square input,
  edge coordinates, and dimensions producing both horizontal and vertical
  padding;
- exact geometry and padding-region checks;
- BGR-to-RGB ordering, normalized FP32 NCHW shape `[1,3,640,640]`, and no
  NaN/Inf;
- row-stride and boundary safety checks;
- CUDA launch/error and stream synchronization checks; sanitizer use only
  within the capability of the target environment, with no unsupported
  sanitizer claim.

The unit test may use deterministic synthetic inputs and the existing CPU
OpenCV reference. It must not use test-set mAP to choose constants.

### Gate C1 — Preprocessing Differential and Remediation Effectiveness

On the existing frozen 16-case CUDA preprocessing corpus, compare all three
identities:

```text
V0 CPU/OpenCV reference
vs historical V2
vs V2R CUDA preprocessed tensor
```

Record per image and aggregate for historical V2 and V2R:

- MAE;
- P99 absolute error;
- maximum absolute error;
- non-finite count;
- mismatch distribution;
- edge and padding-region error;
- geometry status;
- per-image V2-to-V2R error delta;
- V2R/V3R tensor digest identity where both variants are executed.

Formal tensor acceptance remains the existing Gate B contract:

- MAE `<= 5e-4`;
- P99 `<= 2/255 + 1e-6`;
- maximum absolute error `<= 4/255 + 1e-6`;
- non-finite count `0`;
- geometry PASS.

The remediation must also demonstrate all of the following relative criteria:

- V2R aggregate MAE is strictly lower than historical V2;
- V2R P99 absolute error is not higher than historical V2;
- V2R maximum absolute error is not higher than historical V2;
- non-finite count remains `0`;
- geometry, padding, BGR-to-RGB, NCHW layout, and normalization do not
  regress.

These are relative remediation-effectiveness criteria, not replacements for
the existing Gate B absolute thresholds. If V2R produces no verifiable resize
differential improvement over historical V2, the decision is
`REMEDIATION_INVALID`.

The distributions and regional errors are diagnostics unless an existing
authority is later cited. No new acceptance threshold may be invented during
implementation.

### Gate C2 — Inference Tensor and Geometry

Using the same frozen INT8 Engine and existing postprocess contract, verify
on the focused validation inputs:

- finite TensorRT outputs;
- input/output shape and geometry integration;
- result order, paths, dimensions, EOS, and drop behavior;
- detection integration and V0 regression;
- V2R/V3R tensor and detection identity.

The Engine SHA, model SHA, calibration identity, `conf=0.25`, `iou=0.45`,
`max_nms=30000`, and `max_det=300` remain unchanged. Gate A/B/C definitions
and thresholds remain unchanged.

### Gate C3 — Task-Level Gate D (I2 only)

After I1 is frozen and accepted by the Paper Project Manager, I2 executes the
single formal 180-image frozen test-set check.
Compare V2R to the existing V0 accuracy authority using the existing Gate D
limits:

- mAP50-95 drop `<= 0.005`;
- mAP50 drop `<= 0.005`;
- precision drop `<= 0.010`;
- recall drop `<= 0.010`;
- per-class AP50 drop `<= 0.020`;
- per-class recall drop `<= 0.030`.

The test set may be used here only for this one post-freeze formal Gate D
validation. No confidence, IoU, max-detection, NMS, model, Engine,
calibration, or resize coefficient can be tuned from the result.

V3R is not independently tuned or given a second 180-image parameter
evaluation. I1 verifies V2R/V3R preprocessing tensor and detection identity;
only after the V2R Gate D conclusion is established may V3R enter 0.5D as the
corresponding pinned companion.

### Gate C4 — Bounded Decision

The only allowed final decisions are:

```text
V2R_CORRECTNESS_ACCEPTED
V2R_REMAINS_RESEARCH_ONLY
REMEDIATION_INVALID
BLOCKED
```

- `V2R_CORRECTNESS_ACCEPTED`: all required gates PASS, including Gate D;
  V2R can enter the later timing-aligned 0.5D formal rerun. V3R is carried
  forward only if its identity checks pass.
- `V2R_REMAINS_RESEARCH_ONLY`: implementation and pre-task gates are valid,
  but Gate D still FAILs. Stop immediately; do not start a second resize
  remediation. The Project Manager chooses whether 0.5D uses historical V2
  or the new research-only V2R.
- `REMEDIATION_INVALID`: the implementation does not realize the frozen
  OpenCV 4.5.4-aligned fixed-contract semantic, causes a new correctness
  problem, or cannot be
  attributed to the bounded resize change. Preserve historical V2/V3 and
  stop expansion.
- `BLOCKED`: a required external/platform fact or dependency prevents a
  defensible bounded implementation or verification.

## Implementation and Test-Set Separation

The remediation is split into two explicitly separated phases.

### Phase 0.5C-I1 — implementation and pre-test correctness freeze

I1 is the only phase permitted to implement the single Candidate A route. It
may perform the affected CUDA build, unit tests, Gate C0, Gate C1, Gate C2,
V2R/V3R identity checks, and remediation metadata generation. I1 must not run,
inspect, or generate new formal 180-image task metrics, formal Gate D evidence,
or any 0.5D benchmark/result bundle.

I1 must freeze one implementation commit after C0–C2 and identity checks pass.
That commit is the implementation authority for I2. If I1 fails, it goes
directly to the C4 disposition; there is no second implementation or semantic
optimization round.

I1 may touch only the focused scope in Section 8. The Stage R formal benchmark
harness, 0.5D bundle, V4, Stage P, Pipeline, TensorRT Engine implementation,
postprocessor, NMS, calibration, model, ONNX, and Engine binary are outside I1.

### Phase 0.5C-I2 — one-time formal Gate D

I2 is not authorized until the I1 implementation commit is frozen and the
Paper Project Manager accepts it. I2 may run exactly once on the frozen 180
image test set and generate the correctness decision evidence. It may not
modify the CUDA kernel, coefficients, rounding, resize semantics, or any
other implementation after Gate D. Gate D execution commit must be exactly
the I1 frozen implementation commit:

```text
Gate D execution commit == I1 frozen implementation commit
```

I2 does not authorize a second repair round, parameter search, or 0.5D
benchmark. A failed Gate D goes directly to C4.

## 11. Stop Conditions

The future task must stop after one implementation and one formal validation
cycle. The following are prohibited even if Gate D is close to passing:

- a second resize remediation round;
- coefficient-precision sweeps;
- rounding-mode sweeps;
- test-driven parameter search;
- relaxing or rewriting any Gate;
- changing the test split or test membership;
- retraining, re-freezing, re-exporting, recalibrating, or rebuilding the
  Engine;
- changing confidence, IoU, NMS, or postprocess settings;
- implementing V4, Pipeline, V4 overlap, GPU NMS, GPU preprocessing beyond
  the selected resize semantic, INT8/QAT, ROS2, UI, or V4;
- running the formal 0.5D benchmark before C4 and Project Manager review;
- overwriting or silently relabeling historical V2/V3 evidence.

Compilation errors and obvious implementation bugs may be fixed inside the
authorized files, but they do not create another semantic experiment.

## 12. Phase 0.5D Handoff Contract

0.5D is not executed by this plan. It becomes eligible only after C4 and
Project Manager review.

The final candidate set is:

```text
V0 timing-aligned baseline
V2R, or frozen historical/research-only V2 according to C4
V3R, or the corresponding historical pinned variant according to C4
```

The later formal rerun must reuse the Attempt 2 comparison boundary: the same
180-image frozen workload, same process invocation, same warmup policy, same
measured-frame count, same interleaved order schedule, same result fields,
same external timing boundary, and the same five-run protocol recorded in
`results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/`.

All branches must have `timing_enabled=false` for the common comparison. The
existing V0 config currently has timing enabled and therefore cannot be used
unchanged as the final matched-timing V0 identity; the timing-aligned V0
config must be separate and hashed. This removes the documented V0-only
internal timing mismatch before comparing V0 with V2R/V3R.

0.5D must preserve historical Attempt 2 evidence, use new result directories,
and include commit/config/binary/Engine/test-manifest hashes in every run.
It must not claim lower single-frame latency from pipeline behavior or expand
the result beyond the frozen platform, model, Engine, workload, and timing
boundary.

## 13. Risks and Controls

| Risk | Control |
|---|---|
| OpenCV internal interpolation semantics are difficult to reproduce | Freeze behavior against the installed OpenCV 4.5.4 reference before implementation; stop if broad source copying is required |
| OpenCV-version boundary changes | Record OpenCV 4.5.4 in contract and metadata; do not generalize to another version |
| CUDA kernel complexity grows | Fixed 640x640/CV_8UC3 scope; no generic resize framework; one implementation cycle |
| Performance decreases | Measure only later under 0.5D; correctness is the current priority; do not optimize during 0.5C-I |
| Tensor error improves but Gate D still fails | C4 explicitly permits `V2R_REMAINS_RESEARCH_ONLY`; no second tuning round |
| Test-driven overfitting | Freeze semantics before the 180-image Gate D run; no test-driven coefficient search |
| New and historical variant identity is confused | V2R/V3R enum, configs, directories, remediation ID, and hash-bound metadata are mandatory |
| V3 does not inherit the correction | V3R must call the same semantic mode and pass tensor/detection identity checks |
| OpenCV source is copied too broadly | Reimplement only the narrow contract and preserve attribution; otherwise choose bounded fallback D |
| 1050 Ti and Jetson differ | Use Jetson/OpenCV 4.5.4 facts for the target contract; local-PC observations are not Jetson evidence |
| Scope expands into a generic resize implementation | Fixed dimensions, channels, dtype, and existing geometry only; no new image API |
| NPP appears attractive because it is installed | Do not add it: no current project dependency or OpenCV numerical-compatibility evidence |
| 0.5D timing mismatch persists | Require a separate timing-aligned V0 config and `timing_enabled=false` for every branch |

## 14. Explicitly Prohibited Work

This plan does not authorize:

- production implementation before Project Manager review;
- CUDA/TensorRT smoke, Engine build, benchmark, or accuracy execution in this
  planning turn;
- model, ONNX, Engine, calibration, test split, threshold, NMS, or
  postprocess changes;
- Pipeline, V4 overlap, ROS2, UI, INT8/QAT, GPU NMS, or memory-framework work;
- changing historical result files or paper正文;
- commits, pushes, tags, rebases, resets, cleans, stashes, or merge commits.

## 15. Implementation Authorization Decision

```text
Implementation Authorization Decision:

PHASE_0_5C_I1_READY_PENDING_PROJECT_MANAGER_AUTHORIZATION

PHASE_0_5C_I2_NOT_AUTHORIZED
PHASE_0_5D_NOT_AUTHORIZED
```

## 16. Recommended Next Actor

```text
Paper Project Manager
```
