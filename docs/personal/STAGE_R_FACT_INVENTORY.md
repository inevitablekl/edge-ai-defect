# Stage R Fact Inventory

## 0. Scope and Reading Rule

本报告用于 Stage R（Jetson INT8 Inference Data-Path Profiling and Optimization）
R0 Planning Freeze 的事实盘点。盘点基于 Stage R 分支起点
`4c67858610e14ba7d3c951b33f0948230451827f`（Stage Q merge commit），时间为
2026-08-01。

本报告只记录真实可验证事实，不把 R1 实施、CUDA preprocessing 或 Profiling
结果写成当前状态。

---

## 1. Git and Stage Q Authority

### 1.1 当前引用关系

| 项目 | 当前事实 |
|---|---|
| 当前 Stage R branch | `feature/jetson-int8-data-path-optimization` |
| exact baseline | `4c67858610e14ba7d3c951b33f0948230451827f` |
| `main` | `4c67858610e14ba7d3c951b33f0948230451827f` |
| `origin/main` | `4c67858610e14ba7d3c951b33f0948230451827f` |
| 盘点开始前工作树 | clean；无 tracked 修改、staged、untracked 文件 |
| Stage Q branch | `feature/jetson-tensorrt-int8`（已 merged） |
| remote | `origin = https://github.com/inevitablekl/edge-ai-defect.git` |

### 1.2 Stage Q Tag

| 项目 | 当前事实 |
|---|---|
| Tag name | `stage-q-int8-complete-v1.0` |
| Tag type | annotated tag |
| Tag object | `066eefb134ecaadb3069933efff89d132b9a938d` |
| Peeled commit | `4c67858610e14ba7d3c951b33f0948230451827f` |
| Tag message | `Stage Q complete: TensorRT INT8 PTQ evaluation and deployment optimization` |
| Tagger | `inevitablekl <1062460759@qq.com>` |

### 1.3 Stage Q Final Classification

```text
STAGE_Q_COMPLETE_INT8_RECOMMENDED
```

### 1.4 Stage Q Document and Evidence Paths

| Document | Path |
|---|---|
| Final Report | `docs/personal/STAGE_Q_FINAL_REPORT.md` |
| Evidence Index | `docs/personal/STAGE_Q_EVIDENCE_INDEX.md` |
| Task Cards | `docs/personal/STAGE_Q_TASK_CARDS.md` |
| Fact Inventory | `docs/personal/STAGE_Q_FACT_INVENTORY.md` |
| Execution Plan | `docs/personal/STAGE_Q_EXECUTION_PLAN.md` |
| Release Readiness | `docs/personal/STAGE_Q_RELEASE_READINESS_REPORT.md` |

---

## 2. Stage Q INT8 Artifact Authority

### 2.1 INT8 Engine

| 项目 | 当前事实 |
|---|---|
| Engine location | local-only: `/home/orin/edge-ai-local-models/stage_q/` |
| Engine manifest | `results/build/tensorrt/q3_int8_engine_v1/` |
| Calibration manifest | `results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json` |
| Layer audit | `results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json` |
| INT8 compute layers | 262 |
| FP16 compute layers | 6 |
| FP32 compute layers | 64 |
| Precision mode | INT8 + FP16 + FP32 mixed precision |
| FP32 Host I/O | confirmed |
| Static batch | 1 |
| Input name | `images` |
| Input shape/dtype | `[1, 3, 640, 640]` / `float32` |
| Output name | `output0` |
| Output shape/dtype | `[1, 10, 8400]` / `float32` |

### 2.2 TensorRT / CUDA / L4T Versions

| 项目 | 当前事实 |
|---|---|
| TensorRT | `10.3.0.30` |
| CUDA | `12.6.68` |
| L4T | `R36.5.0` |
| JetPack | 6.2.2 |
| Kernel | `5.15.185-tegra` |

### 2.3 Stage Q Accuracy and Evidence

| 项目 | 当前事实 |
|---|---|
| 180-frame canonical detection SHA | `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` |
| Test manifest SHA | `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194` |
| Cycle length | 180 |
| Result JSON authority | v4 |
| Q5 Accuracy | `Q5_ACCURACY_EVIDENCE_VALID`, accuracy `ACCEPTABLE` |
| Q6 Serial Performance | `MATERIAL_INT8_INFERENCE_GAIN`, `NO_MATERIAL_END_TO_END_REGRESSION` |
| Q7 Pipeline Evidence | `Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION` |
| Q1 Platform/Asset | `Q1_PLATFORM_AND_ASSET_PASS_WITH_SPLIT_REMEDIATION` |

### 2.4 Stage Q Evidence Paths

| Gate | Evidence Path |
|---|---|
| Q1 | `results/validation/stage_q/q1_platform_asset_preflight_v1/` |
| Q2 | `results/build/tensorrt/q2_int8_smoke_v1/` |
| Q3 | `results/build/tensorrt/q3_int8_engine_v1/` |
| Q5 | `results/validation/stage_q/q5_accuracy_v1/` |
| Q6 | `results/validation/stage_q/q6_serial_performance_v1/` |
| Q7 | `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/` |

---

## 3. Current Production Data Path

以下事实基于只读检查当前仓库中 `src/`、`include/` 和 `CMakeLists.txt`。

### 3.1 Preprocessing

| 项目 | 状态 |
|---|---|
| CPU/OpenCV preprocessing | IMPLEMENTED |
| 入口 | `Preprocessor::process(const ImageItem&)` |
| LetterBox resize/padding | IMPLEMENTED |
| BGR→RGB conversion | IMPLEMENTED |
| HWC→CHW conversion | IMPLEMENTED |
| float32/255 normalization | IMPLEMENTED |
| CUDA fused preprocessing | NOT IMPLEMENTED |
| Pinned raw staging (persistent) | NOT IMPLEMENTED |
| Pageable raw staging | NOT IMPLEMENTED |

### 3.2 TensorRT Engine

| 项目 | 状态 |
|---|---|
| `IInferenceEngine::run(const HostTensor&, HostTensor*)` | IMPLEMENTED |
| `HostTensor` ownership and allocation | IMPLEMENTED (caller-owned output copy) |
| Host input API (FP32 HostTensor) | IMPLEMENTED |
| H2D (`cudaMemcpyAsync`) | IMPLEMENTED |
| `setTensorAddress` | IMPLEMENTED |
| `enqueueV3` | IMPLEMENTED |
| `cudaStreamSynchronize` | IMPLEMENTED |
| Host output construction (pageable, exact-size) | IMPLEMENTED |
| D2H (`cudaMemcpyAsync`) | IMPLEMENTED |
| `TensorRtDeviceInputCapability` (device FP32 NCHW input) | NOT IMPLEMENTED |

### 3.3 PipelineRunner

| 项目 | 状态 |
|---|---|
| PipelineRunner with 4 workers | IMPLEMENTED |
| Source / Preprocess / Inference / Postprocess+Sink | IMPLEMENTED |
| Queue capacity | 1 (configurable via RuntimeConfig) |
| Drop policy | block |
| Single TensorRT ExecutionContext | IMPLEMENTED |
| Single inference worker | IMPLEMENTED |

### 3.4 RuntimeConfig and Result JSON

| 项目 | 状态 |
|---|---|
| RuntimeConfig v5 (supports tensorrt_fp16, tensorrt_int8) | IMPLEMENTED |
| RuntimeConfig v6 (adds data_path variant, profiling mode) | NOT IMPLEMENTED |
| Result JSON v4 | IMPLEMENTED |

### 3.5 CUDA and Advanced Features

| 项目 | 状态 |
|---|---|
| CUDA preprocessing | NOT IMPLEMENTED |
| Pinned raw staging | NOT IMPLEMENTED |
| Device-input capability | NOT IMPLEMENTED |
| Phase Barrier | NOT IMPLEMENTED |
| Stage R profiling instrumentation | NOT IMPLEMENTED |
| CUDA timing sampling (10-cycle stratified rotation) | NOT IMPLEMENTED |
| Double Buffer / multiple CUDA streams | NOT IMPLEMENTED |
| GPU NMS / GPU postprocess | NOT IMPLEMENTED |
| General BufferManager | NOT IMPLEMENTED |
| General async inference API | NOT IMPLEMENTED |
| Zero-Copy / Mapped memory | NOT IMPLEMENTED |
| input-consumed Event | NOT IMPLEMENTED |

---

## 4. Stage R Estimated Minimal Touch Points

以下仅列事实定位和候选触点，不进行 R1 设计或编码。

### 4.1 RuntimeConfig Parser/Types

- `include/edge_ai_defect/config/runtime_config.hpp`
- `src/runtime_config.cpp`
- 需新增 `data_path` section（variant, profiling mode）
- 需新增 schema_version 6

### 4.2 Application/PipelineRunner

- `include/edge_ai_defect/runner/pipeline_runner.hpp`
- `src/pipeline_runner.cpp`
- 需新增 Phase Barrier（warmup/measured boundary）
- 需新增 profiling instrumentation

### 4.3 Current Preprocessor

- `include/edge_ai_defect/preprocess/preprocessor.hpp`
- `src/preprocessor.cpp`
- CPU preprocessing 保持 V0 不变
- V2/V3/V4 需新增 CUDA preprocessing kernel/module

### 4.4 TensorRT Backend

- `include/edge_ai_defect/backend/tensorrt_engine.hpp`
- `src/tensorrt_engine.cpp`
- 需新增 `TensorRtDeviceInputCapability`
- 需新增 device FP32 NCHW input 支持
- 需新增 CUDA stream 管理（V4 用）

### 4.5 Stage-Specific Validation and Evidence Tooling

- `tools/` 目录
- 需新增 Stage R run manifest 生成
- 需新增 profiling summary / correctness summary / performance summary 工具

### 4.6 Build Boundary

- `CMakeLists.txt`
- TensorRT ON/OFF build boundary 已存在（`EDGE_AI_ENABLE_TENSORRT`）
- V2–V4 CUDA preprocessing 需要 CUDA toolkit 编译依赖

---

## 5. Pre-R0 Evidence Sources

### 5.1 Pre-R0 Baseline Manifest

| 项目 | 事实 |
|---|---|
| Path | `results/validation/stage_r/r0_planning_freeze_v1/pre_r0_baseline_manifest.json` |
| Source evidence | Git commands (read-only), Stage Q Evidence Index, Q5 accuracy Evidence |
| Git facts | directly observed via `git rev-parse`, `git status`, `git cat-file` |
| Stage Q tag | directly observed via `git cat-file tag` |
| Canonical detection SHA | from `results/validation/stage_q/q5_accuracy_v1/expected_int8_cycle_sha.json` |
| Test manifest SHA | from Stage Q Evidence Index and Q5 accuracy evidence |
| Verification result | `PRE_R0_VERIFIED` |

### 5.2 Pre-R0 Environment Manifest

| 项目 | 事实 |
|---|---|
| Path | `results/validation/stage_r/r0_planning_freeze_v1/pre_r0_environment_manifest.json` |
| Source evidence | Stage J J1 discovery, Stage Q Q1 platform preflight, read-only system queries |
| Device model | directly observed via `/proc/device-tree/model` |
| L4T/CUDA/TensorRT versions | directly observed via `dpkg -l` |
| nvpmodel mode | directly observed via `nvpmodel -q` |
| CPU online set | directly observed via `/sys/devices/system/cpu/online` |
| Kernel | directly observed via `uname -r` |
| INT8 Engine | asserted from Q3 evidence; local-only, not independently verified in R0 |
| Verification result | `VALID` |

### 5.3 Source Evidence File Status

| File | Status |
|---|---|
| `results/validation/stage_q/q5_accuracy_v1/expected_int8_cycle_sha.json` | TRACKED |
| `results/validation/stage_q/q5_accuracy_v1/int8_result.json` | TRACKED |
| `results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json` | TRACKED |
| `results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json` | TRACKED |
| `docs/personal/STAGE_Q_EVIDENCE_INDEX.md` | TRACKED |
| `docs/personal/STAGE_Q_FINAL_REPORT.md` | TRACKED |
| INT8 Engine binary | LOCAL-ONLY (not in Git) |
| INT8 calibration cache | LOCAL-ONLY (not in Git) |

---

## 6. Current Stage R Branch State

| 项目 | 事实 |
|---|---|
| Current branch | `feature/jetson-int8-data-path-optimization` |
| HEAD | `4c67858610e14ba7d3c951b33f0948230451827f` |
| Merge-base with main | `4c67858610e14ba7d3c951b33f0948230451827f` |
| Diff against baseline | empty (no commits yet) |
| Worktree | clean |
| R0 documents written | STAGE_R_EXECUTION_PLAN.md, D081–D083, this Fact Inventory, Task Cards, Pre-R0 manifests, TASKS.md update |
| R0 NOT started | R1 implementation, CUDA preprocessing, CMake changes, hardware experiments |
