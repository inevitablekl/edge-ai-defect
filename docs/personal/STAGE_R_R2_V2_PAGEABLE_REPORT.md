# Stage R R2.2 — V2 Pageable CUDA Data Path

## Verdict

`STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED` — the V2
validation harness executed the frozen 180-image manifest through the pageable
CUDA path. The runtime and tensor contracts passed, but the task-accuracy
replacement criteria failed. Stage Q INT8 V0 is retained as the selected
candidate. No performance conclusion is made.

## Entry State

- Branch: `feature/jetson-int8-data-path-optimization`
- Starting HEAD: `a5cdfaddf9f6625c0f645daf7e1f0db8a4d99778`
- Parent: `c488283fdc1e328588a0f90430b058b84c9e064e`
- Merge-base with the same branch: `a5cdfaddf9f6625c0f645daf7e1f0db8a4d99778`
- Starting worktree: implementation changes from the prior R2.2 turn were
  present and uncommitted
- R2.1 tensor gate: PASS; 16 images, MAE `0.000412164`, P99
  `0.00392163`, Max `0.00392163`, non-finite `0`; source artifact SHA256 is
  `f6b276a9c2c7c50fb06d65c95225e80b8cd1a1e9c40730dfc005c46aef5f284a`.
- R1 canonical SHA: `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2`.

## Implementation

- `PageableRawStaging` uses reusable ordinary pageable `std::vector<uint8_t>`
  storage and copies exactly `width * 3` bytes per row, respecting
  `cv::Mat.step`.
- `CudaPreprocessor::create_for_external_tensor()` reuses the TensorRT stream
  and writes directly to the TensorRT-owned persistent FP32 input buffer.
- `TensorRtEngine::run_device_input()` is a TensorRT-backend-only capability;
  `IInferenceEngine`, `HostTensor`, ORT, FP16 historical behavior,
  `PipelineRunner`, postprocess, and Result JSON v4 were not changed.
- `PageableRunner` is a Stage R-specific serial adapter. It preserves source
  order and reuses the existing source, postprocess, and result-sink contracts.
- V3/V4 remain rejected before execution/resource allocation.
- `stage_r_v2_tensor_gate` performs correctness-only copy-back from the actual
  `TensorRtEngine::device_input_buffer()` after pageable V2 preprocessing and
  before any TensorRT enqueue; it is not linked into the formal runtime path.

## Builds and Tests

- Host syntax check for `src/tensorrt_engine.cpp`: PASS.
- Host syntax check for `stage_r/pageable_runner.cpp`: PASS.
- Pageable non-contiguous `cv::Mat` test: PASS.
- `git diff --check`: PASS.
- CUDA/TensorRT Release configure and build: PASS using CUDA 12.6.68 and the
  linux-aarch64 ONNX Runtime SDK.
- `test_stage_r_cuda_preprocess`: PASS.
- `test_tensorrt_engine`: PASS with the frozen Engine, manifest, and contract.
- `stage_r_v2_tensor_gate`: PASS.
- V0 Gate C regression: PASS; 180 measured frames and frozen cycle detection
  SHA matched. V2 Gate D executed and failed task-accuracy thresholds.
- V2 validation harness build: PASS; CUDA/TensorRT ON.
- V2 validation harness run: 180 frames, Result JSON v4, order/paths/dimensions
  PASS, drop 0, EOS PASS, worker join PASS.

## Gate Results

The tracked machine-readable Gate B record is
`results/validation/stage_r/r2_v2_pageable_correctness_v1/v2_tensor_gate_summary.json`.
Gate B passed for 16 images with MAE `0.000412164`, P99 `0.00392163`, Max
`0.00392163`, non-finite `0`, and geometry `16/16 PASS`. Gate C passed with
the frozen detection SHA
`12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2`.
Gate D executed through the real V2 path and failed the frozen task-accuracy
thresholds. V2 mAP50 drop was `0.00552337` (limit `0.005`), maximum class AP50
drop was `0.0275154` (limit `0.020`), and maximum class Recall drop was
`0.0303030` (limit `0.030`). The complete machine-readable result is
`results/validation/stage_r/r2_v2_pageable_correctness_v1/v2_task_accuracy_summary.json`.

## Resource and Scope Audit

The intended V2 path uses one existing TensorRT stream and one execution
context, persistent device raw/input/output buffers, and no per-frame CUDA
allocation. The implementation contains no pinned allocation, host register,
mapped memory, zero-copy, second stream, cross-frame overlap, GPU NMS, V3, or
V4 implementation. These resource counts were not hardware-verified in this
workspace.

## Evidence Hashes

- R2.1 tensor gate: `f6b276a9c2c7c50fb06d65c95225e80b8cd1a1e9c40730dfc005c46aef5f284a`
- R1 Nsight summary: `19dee1beae01b6a367b340e5d06d9e1ef976f3dbaca2a1c1d9e60535532130ec`
- V2 config: `a4d9335ed0a13d21b34da4ea05b8c5e50975b2ec08b6419877adb6b5d4595bc3`
- Test manifest: `d4a6be139fbb352ff71d0100b4fb7371cf7c21d99fa199259679a8a10e6583b5`
- V2 tensor validator binary: `aba63d62eb8985f2760b6a8d5634ea515fd57134da2cdbf98a306645aa17710e`
- V2 Engine: `8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee`
- V2 tensor summary: `cb117851c0c4266ecb4d4743a91333259ca625fffbf72f2e138e5a62a8b25014`
- V0 Gate C summary: `dce1d77e2533a63146a98a8db0dee64fe4a174c1a0a54af894a342912056eb49`
- V2 task harness binary: `757d1de2ea7cce98c5e56f07d7715828af6d0cbdabf7fc6e11ce48ac69911425`
- V2 Result JSON: `1e639c974e2d67a95f2cdabbe7b9fe0be5444b8b1f5c302314a782c278660bd2`
- V2 detection SHA: `b4a7f173afdf54b9ed1ed368ea026b0e7fe31a945d5f098377f0864f45a178ab`
- V2 tensor digest: `c00128515fa72b2fe024d865f05edb2e7b49239e3c1aa16f278f16d508effa97`
- V2 task summary: `e573ef8b113c7d4b13f5ef049e8abbf4cad58075f595428c082a3b28816e7651`
- V2 identity baseline: `574499173279cd9ea3b026f4c684a9ff9c39dd1b586c940ce21207656834861c`
- V2 final negative-result summary: `ca71697c6f557b8c44c607c83de01985b7a3fca1825bfa490985b6e5f045916b`

## Final Negative-Result Closure

### Result Classification

```text
V2 CUDA preprocessing candidate: not selected as replacement
reason: task accuracy replacement criteria not satisfied
classification: functional mismatch caused by CUDA resize numerical contract
```

The V2 pageable raw-staging path is a runnable experimental result. It is not
the selected replacement for the Stage Q INT8 V0 baseline.

The original V2 task-accuracy result was:

```text
mAP50 drop:          0.00552337
max class AP50 drop: 0.02751543
max class Recall:    0.03030303
```

The authorized first minimal remediation quantized the CUDA resize
coefficients to 11-bit fixed point without changing geometry, padding, color
conversion, normalization, TensorRT, postprocess, or runtime architecture.
It improved but did not satisfy the frozen replacement criteria:

```text
mAP50 drop:          0.00537575
max class AP50 drop: 0.02673348
max class Recall:    0.03030303
```

No further CUDA resize compatibility expansion was authorized. In particular,
separable resize was not implemented.

### Technical Finding

Under the evaluated YOLOv8n INT8 deployment configuration, CUDA fused
preprocessing introduced small numerical differences relative to OpenCV CPU
preprocessing due to resize interpolation implementation differences. These
differences remained within tensor-level tolerance but affected task-level
metrics near the replacement threshold.

### Stage R Decision

```text
Selected candidate: Stage Q INT8 V0 baseline retained
V2: experimental result only
V3: SKIPPED
V4: SKIPPED
R2.3: NOT AUTHORIZED
```

V3 pinned memory and V4 double buffering were not implemented or benchmarked,
because V2 did not satisfy the replacement correctness criteria and no
performance conclusion is made.

## Authorization

`R2.2: STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED.`

`R2.3: NOT AUTHORIZED.`

`V3: SKIPPED.`

`V4: SKIPPED.`

`R3–R6: NOT AUTHORIZED.`

`Push/Merge/Tag: NOT EXECUTED.`
