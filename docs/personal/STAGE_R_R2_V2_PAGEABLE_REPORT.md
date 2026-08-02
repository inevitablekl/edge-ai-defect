# Stage R R2.2 — V2 Pageable CUDA Data Path

## Verdict

`STAGE_R_R2_2_GATE_B_PASS_PENDING_C_D` — the CUDA/TensorRT build, R2.1
regression, and V2 Gate B passed. Gate C and Gate D were intentionally not
executed. No performance conclusion is made.

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
- 180-image task gate and V0 runtime regression: NOT RUN by order constraint.

## Gate Results

The tracked machine-readable Gate B record is
`results/validation/stage_r/r2_v2_pageable_correctness_v1/v2_tensor_gate_summary.json`.
Gate B passed for 16 images with MAE `0.000412164`, P99 `0.00392163`, Max
`0.00392163`, non-finite `0`, and geometry `16/16 PASS`. Gate C and Gate D
remain `NOT RUN`; no V2 detection identity is frozen by this turn.

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
- V2 task summary: `2dd872a736658151d6d0fa6d8777c9639952bc1e42c37e17521560b687b04988`
- V2 identity baseline: `574499173279cd9ea3b026f4c684a9ff9c39dd1b586c940ce21207656834861c`

## Authorization

`R2.2: NOT COMPLETE — Gate B PASS; Gate C/D pending.`

`R2.3: NOT AUTHORIZED PENDING USER REVIEW.`

`R3–R6: NOT AUTHORIZED.`

`Push/Merge/Tag: NOT EXECUTED.`
