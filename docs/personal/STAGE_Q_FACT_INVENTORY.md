# Stage Q Fact Inventory

## 0. Scope and reading rule

本报告用于 Stage Q（TensorRT INT8 Quantization Evaluation）Q0 Planning Freeze
的事实盘点。盘点基于 Stage Q 分支起点 `630822c7aeec471cc1f82b019d97bc431855045e`，
时间为 2026-07-31。当前分支已按授权从 exact baseline 创建；本报告只记录真实
可验证事实，不把 Q1 平台或资产预检写成 PASS。模型 Engine/ONNX 等大文件的 SHA
来自当前仓库中已提交的 manifest/evidence；这些二进制本身不在当前 Git 工作树中。

结论边界：当前可复核的 TensorRT Engine 是 Engine 内部 `FP32+FP16 mixed
precision`、FP32 输入/输出、`int8_enabled=false` 的 Stage K Original FP16
Engine。项目尚无 INT8 calibration implementation。

## 1. Git 状态

### 1.1 当前引用关系

| 项目 | 当前事实 |
|---|---|
| 当前 branch | `feature/jetson-tensorrt-int8` |
| Q0 branch base HEAD | `630822c7aeec471cc1f82b019d97bc431855045e` |
| `main` | `630822c7aeec471cc1f82b019d97bc431855045e` |
| `origin/main` | `630822c7aeec471cc1f82b019d97bc431855045e` |
| `main...origin/main` | `0 0`；当前 main 与 origin/main 无 ahead/behind 差异 |
| 盘点开始前工作树 | 仅有预期未跟踪 `docs/personal/STAGE_Q_FACT_INVENTORY.md`；无 tracked 修改、staged、删除、重命名或其他 untracked 文件 |
| remote | `origin = https://github.com/inevitablekl/edge-ai-defect.git` |

### 1.2 最近 20 个 commit

| # | Commit | 时间 | Subject |
|---:|---|---|---|
| 1 | `630822c7aeec471cc1f82b019d97bc431855045e` | 2026-07-31 01:31:25 +08:00 | Merge pull request #5 from inevitablekl/feature/jetson-pipeline-runtime |
| 2 | `f78df4b23d4c62a7a7e699250f576e835d5ff454` | 2026-07-31 01:30:18 +08:00 | docs(stage-p): finalize evidence index and repository cleanup |
| 3 | `c1b64cbfd14a08cd6501c431d031f12a53abdb79` | 2026-07-31 01:26:14 +08:00 | docs(stage-p): consolidate final pipeline runtime results |
| 4 | `cb89e60e35479575583455129f3f4222e221326d` | 2026-07-31 01:19:28 +08:00 | test(stage-p): retain P7 stability telemetry evidence |
| 5 | `da7087ce9169f5eaf2e6ffcbc1c93c1a310ac6c8` | 2026-07-31 01:19:10 +08:00 | test(stage-p): validate long running pipeline stability |
| 6 | `cd5933353d0676dcf5517a318f389be99b246ab1` | 2026-07-31 00:36:38 +08:00 | feat(stage-p): add video file source support |
| 7 | `9ebadf8e51dae15db05472fd789d105d38aa4632` | 2026-07-31 00:21:05 +08:00 | docs(stage-p): amend p5 validity protocol and reclassify evidence |
| 8 | `d45342e0c9224df4521fae6db97555fd4257ae24` | 2026-07-30 23:46:40 +08:00 | fix(stage-p): align corpus replay with frozen manifest |
| 9 | `e313b5855be6d2a50e46e089fe045b9903abfa9` | 2026-07-30 23:33:42 +08:00 | fix(stage-p): add experiment runner execution entry |
| 10 | `cebf36415ca5bc96f061c75df687d175c9de7c59` | 2026-07-30 23:13:05 +08:00 | fix(stage-p): accept runtime config v4 in tensorrt backend |
| 11 | `1d944a58fbe5ee34408c1681aad437cd0264da69` | 2026-07-30 22:55:06 +08:00 | feat(stage-p): implement bounded pipeline runtime |
| 12 | `86f74968c4bb242d29862564e2c865f0d93b8663` | 2026-07-30 22:43:04 +08:00 | feat(stage-p): implement bounded queue primitives |
| 13 | `bca6679cda43b9e4e65b3c3cf18d4ffd25cafd3f` | 2026-07-30 22:08:54 +08:00 | fix(stage-p): close P1 contract gate gaps |
| 14 | `ccbe3bfc2afe2833b77a8d1e451100624b87a22d` | 2026-07-30 01:45:02 +08:00 | feat(stage-p): implement runtime contracts and canonical serialization |
| 15 | `674ecc8d9b659fc0ae14cc1b046f283d5889c436` | 2026-07-30 01:29:53 +08:00 | docs(stage-p): freeze bounded pipeline execution plan |
| 16 | `c6890d86e7534500cfe31c40dd73f151d77d5362` | 2026-07-29 23:10:45 +08:00 | Merge pull request #4 from inevitablekl/feature/jetson-tensorrt-fp16 |
| 17 | `7cae8eb067c84199d4dd343df7b9ab8f197e739b` | 2026-07-29 23:06:33 +08:00 | chore(stage-k): archive diagnostics and prepare stage-p |
| 18 | `d4b50739c2f5f1db9ba7b48e653618b2af9cd98a` | 2026-07-29 22:58:16 +08:00 | docs(stage-k): finalize TensorRT deployment validation |
| 19 | `703bbbdae3b36bb0d288f785cfd8e18b6ee1a852` | 2026-07-29 22:50:11 +08:00 | evidence(stage-k): complete TensorRT performance benchmark |
| 20 | `940988cff4a20b5ab7f95c039e6c4629e5b942b4` | 2026-07-29 22:14:38 +08:00 | evidence(stage-k): complete TensorRT FP16 stability validation |

### 1.3 Stage K / Stage P tags

| Tag | Tag object | Peeled commit | HEAD relation |
|---|---|---|---|
| `stage-k-tensorrt-fp16-complete-v1.0` | `3b1770b8b56caa0f9cb4217d019c641243249be` | `c6890d86e7534500cfe31c40dd73f151d77d5362` | 是 HEAD 的祖先；HEAD 比该 commit 多 15 个 commit |
| `stage-p-bounded-pipeline-complete-v1.0` | `46c56dcbc167139f66222ce352d0c32caa495486` | `630822c7aeec471cc1f82b019d97bc431855045e` | 存在，peeled commit 等于当前 HEAD |

Stage P tag 已存在。另有 `stage-j-complete-v1.0` 和 `m5-onnxruntime-baseline-v1`。

## 2. TensorRT Backend Inventory

### 2.1 相关路径

| 组件 | 路径 |
|---|---|
| TensorRT public header | `include/edge_ai_defect/backend_tensorrt/tensorrt_engine.hpp` |
| TensorRT engine implementation | `src/tensorrt_engine.cpp` |
| TensorRT disabled-build fallback | `src/tensorrt_backend_stub.cpp` |
| TensorRT logger | `src/tensorrt_logger.hpp`, `src/tensorrt_logger.cpp` |
| Engine factory header/implementation | `include/edge_ai_defect/inference/inference_engine_factory.hpp`, `src/inference_engine_factory.cpp` |
| Manifest header/loader | `include/edge_ai_defect/model/tensorrt_engine_manifest.hpp`, `src/tensorrt_engine_manifest.cpp` |
| Tracked Stage K manifest | `models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json` |
| Stage K runtime configs | `configs/stage_k/selective_fp16_notf32_v1.yaml`, `configs/stage_k/selective_fp16_notf32_m3.yaml` |
| Build evidence/script | `results/build/tensorrt/k2_fp16_engine_v1/build_invocation.sh` |
| Build command record | `results/build/tensorrt/k2_fp16_engine_v1/build_command.txt` |
| Platform/trtexec evidence | `results/platform/tensorrt/k1_environment_v1/` through `k1_environment_v4/` |
| Stage K build evidence | `results/build/tensorrt/k2_fp16_engine_v1/` |
| Stage K serial performance evidence | `results/validation/stage_k7/performance_v1/` |
| Stage P runtime evidence | `results/validation/stage_p/`, `results/benchmark/stage_p/` |

### 2.2 Factory and runtime contract

`src/inference_engine_factory.cpp` has explicit branches for:

- `backend.type == "onnxruntime_cpu"`
- `backend.type == "tensorrt_fp16"`

There is no `tensorrt_int8` branch. `src/runtime_config.cpp` accepts TensorRT
schema 3/4 only when `backend.type` is exactly `tensorrt_fp16`. The TensorRT
engine also validates schema 3/4 and the same backend string.

### 2.3 Current FP16 Engine generation chain

```text
models/onnx/yolov8n_neudet_frozen.onnx
  --sha256 c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944
        |
        | /usr/src/tensorrt/bin/trtexec
        | --onnx=models/onnx/yolov8n_neudet_frozen.onnx
        | --fp16
        | --memPoolSize=workspace:4096M
        | --inputIOFormats=fp32:chw
        | --outputIOFormats=fp32:chw
        | --saveEngine=/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine
        | --skipInference
        v
/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine
  --sha256 6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc
        |
        | models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json
        v
manifest SHA256 39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63
```

Manifest facts: schema 1; TensorRT `10.3.0.30`; CUDA `12.6.68`; L4T
`R36.5.0`; static batch 1; input `[1,3,640,640]` FP32 CHW; output
`[1,10,8400]` FP32 CHW; `precision_mode = "FP32+FP16 mixed precision"`;
`fp16_builder_mode = true`; `int8_enabled = false`; DLA disabled; custom
plugin dependency false.

The Engine itself and the ONNX file are local-only/absent from this Git worktree;
their SHA values are the frozen values recorded by the manifest and evidence.

### 2.4 `trtexec` usage locations

Build and inspection uses appear in the Stage K build evidence and platform
evidence. The formal build script is `results/build/tensorrt/k2_fp16_engine_v1/build_invocation.sh`.
The platform discovery records `/usr/src/tensorrt/bin/trtexec`; the recorded
help exposes `--fp16`, `--int8`, `--calib=<file>`, and `--saveEngine`.
The current project build command uses `--fp16` and does not use `--int8` or
`--calib`.

## 3. Precision Contract Inventory

| Contract item | Current fact |
|---|---|
| Runtime precision field | No dedicated `RuntimeConfig.precision` field. Precision is encoded indirectly by backend string `tensorrt_fp16`. |
| Manifest precision fields | JSON manifest contains `fp16_builder_mode`, `precision_mode`, and `int8_enabled`; current values are `true`, `FP32+FP16 mixed precision`, and `false`. |
| Datatype fields | ModelContract uses `dtype: float32`; TensorRT manifest uses `dtype: FP32` for input/output. |
| C++ datatype enum | `core::TensorDataType` currently has only `kFloat32`. |
| FP16/F32 precision enum | No dedicated FP16/F32 precision enum was found. `kFloat32` is a tensor datatype enum, not an engine precision enum. |
| TensorRT manifest loader | Requires manifest keys including `precision_mode` and `int8_enabled`, but the current `TensorRtEngineManifest` struct/loader only materializes and validates a subset; tensor dtype is hard-coded to FP32/CHW. |
| TensorRT engine runtime | `src/tensorrt_engine.cpp` requires `nvinfer1::DataType::kFLOAT` for both IO tensors. |
| Preprocessor | Rejects non-FP32 model input; current preprocessing emits FP32. |
| INT8 reservation | Existing manifest key `int8_enabled` is the only explicit INT8 artifact flag; no production INT8 backend contract exists. |

### 最小修改点（事实定位，不是实施方案）

若未来 INT8 Engine 仍保持 FP32 输入/输出，只改变 Engine 内部计算精度，
需要触达的最小 production contract 点是：

1. `include/edge_ai_defect/runtime/runtime_config.hpp` 与 `src/runtime_config.cpp`：接受并验证 INT8 backend/precision 标识。
2. `src/inference_engine_factory.cpp`：允许 INT8 Engine 选择。
3. `src/tensorrt_engine.cpp`：调整当前只接受 `tensorrt_fp16` 的校验，并保留/扩展 INT8 Engine 合同校验。
4. `include/edge_ai_defect/model/tensorrt_engine_manifest.hpp` 与 `src/tensorrt_engine_manifest.cpp`：把 precision、INT8、calibration identity 等已存在/新增元数据纳入可验证结构；当前 loader 对这些字段并未全部建模。
5. Stage Q 的 Engine manifest/build evidence：记录 INT8 build command、Engine SHA、calibration identity/cache SHA 和 TensorRT 环境。
6. `include/edge_ai_defect/runtime/runtime_types.hpp`、`src/application_runner.cpp` 及 Result JSON 校验：让结果能区分 backend/precision/artifact identity。

在 FP32 IO 前提下，`core::TensorDataType`、ModelContract 和现有 FP32
Preprocessor 不一定因 Engine 内部 INT8 而改变；如果改为 INT8 IO，则这些
位置也必须扩展。目前它们没有 INT8 表达能力。

## 4. Calibration Capability Inventory

| 能力 | 当前状态 | 事实位置 |
|---|---|---|
| Calibration dataset interface | **NOT IMPLEMENTED** | 未发现 production calibration dataset abstraction 或 loader |
| TensorRT calibrator | **NOT IMPLEMENTED** | 未发现 `IInt8Calibrator` 或项目 calibrator class |
| Entropy calibrator | **NOT IMPLEMENTED** | 未发现 entropy calibrator implementation |
| Calibration cache mechanism | **NOT IMPLEMENTED** | 未发现项目 calibration cache file/path/schema；已有 timing/compilation cache 不属于 calibration cache |
| Calibration metadata | **NOT IMPLEMENTED** | Result JSON、RuntimeConfig、ModelContract、当前 Engine manifest 均没有 calibration dataset/cache identity 字段 |
| `trtexec --calib` use | **NOT USED** | 仅在 `trtexec --help` 证据中出现；当前 FP16 build command 未使用 |
| `int8_enabled` | 已有 manifest 字段，但当前为 `false` | `models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json` |

## 5. Model Baseline Inventory

### 5.1 Frozen artifact identities

| Artifact | Path | SHA256 | 当前可用性 |
|---|---|---|---|
| ONNX | `models/onnx/yolov8n_neudet_frozen.onnx` | `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944` | SHA 由 manifest/evidence 冻结；文件不在当前 worktree |
| FP16 Engine | `/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine` | `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc` | local-only；不在 Git worktree |
| Engine manifest | `models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json` | `39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63` | 当前仓库可读 |
| ModelContract | `configs/model_contracts/yolov8n_neudet_frozen.yaml` | `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190` | 当前仓库可读 |

### 5.2 当前精度基线

存在两个不能混写的精度口径：冻结 YOLO 模型的 Ultralytics test 评价，以及
Stage K 生产 Engine 的 project-local task-level evaluator。

| 口径 | Precision | Recall | mAP50 | mAP50-95 | 数据 |
|---|---:|---:|---:|---:|---|
| Frozen YOLOv8n test | 0.724 | 0.728 | 0.769 | 0.431 | `results/training/evidence/frozen_test_metrics.json`；180 images |
| TRT FP16 Original Stage K task-level | 0.6347305 | 0.7194570 | 0.6560242 | 0.3595495 | `results/validation/stage_k_task_eval_v2/metrics/backend_metrics.json`；project-local evaluator，180 images |

当前 Engine precision baseline 不是纯 INT8：Engine metadata 为
`FP32+FP16 mixed precision`，FP32 IO，`int8_enabled=false`。

### 5.3 Input contract and preprocessing

- ModelContract input: `images`, FP32, NCHW, `[1, 3, 640, 640]`。
- ModelContract output: `output0`, FP32, BCN, `[1, 10, 8400]`。
- Source color: BGR。
- Resize: aspect-preserving LetterBox 到 `640x640`。
- Interpolation: OpenCV `INTER_LINEAR`。
- Padding: value `114`；padding 使用与 Python 兼容的 round 规则。
- Tensor color order: RGB；layout: NCHW；normalization: `uint8 / 255.0`。
- Postprocess currently uses confidence `0.25`、IoU `0.45`、`max_det=300`、class-aware NMS。

## 6. Dataset Inventory

### 6.1 Frozen split

| Split | Images | BBoxes | Manifest |
|---|---:|---:|---|
| train | 1260 | 2916 | `results/validation/stage_k_task_eval_v2/split/train_manifest.json` |
| val | 360 | 828 | `results/validation/stage_k_task_eval_v2/split/val_manifest.json` |
| test | 180 | 442 | `results/validation/stage_k_task_eval_v2/split/test_manifest.json` |
| Total after duplicate-bbox cleanup | 1800 | 4186 | raw bbox 4189，移除 3 个 exact duplicate rows |

Split contract is `70/20/10`, `random seed=42`，排序 XML 后使用
`random.Random(seed).shuffle`；六类为 `crazing, inclusion, patches,
pitted_surface, rolled-in_scale, scratches`。

### 6.2 Stage K / Stage P evaluation corpus

- Stage K task-level evaluation corpus: frozen test split，180 images，442 GT boxes；test manifest SHA256 `fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8`。
- Stage K Level B reference: 16 input images/raw-output reference bundle；input manifest SHA256 `d81d6bb57346231f3ea4cd2dcf0f5285b5993b4b16953641c45f85359b9d0fbf`，bundle SHA256 `fed5755ce630d0902449f3052fcbb915592245583df19bf924ec867d1c1e1e29`。
- Stage K7 serial performance: 上述 180-image test corpus 按序循环，100 warmup、每个 process 5000 measured iterations、3 个独立 processes/backend。
- Stage P P4/P5/P7: 继续使用 frozen 180-frame test corpus，P5 formal 每次 5100 accepted/processed frames，P7 cycle length 180。
- Stage P P6: 另有 frozen MJPG video validation asset，16 frames；它是 VideoFileSource 验证资产，不是 calibration corpus。

### 6.3 对 INT8 calibration 的数据角色确认

- `train` split 是当前唯一被项目事实标记为训练用途、且不属于 held-out evaluation 的数据集；从数据角色上可作为 calibration candidate。
- `val` 与 `test` 已被用于模型选择/最终评价或 Stage K/P evaluation；当前盘点不把它们标记为 calibration data。
- Stage K/P evaluation corpus、16-image Level B reference 和 P6 video 均是评估/验证资产，不是已定义的 calibration corpus。
- 当前仓库没有 calibration manifest、sample selection metadata 或 calibration cache，因此“可作为 candidate”不等于“已完成 calibration capability”。

### 6.4 Q1-B deduplicated split

Q1-B 在保留 historical split 的前提下生成了
`results/validation/stage_q/split_v2_deduplicated/`。使用 image content
SHA256 去重，按 normalized relative path 的 UTF-8 byte order 保留 first，未
重新 shuffle。唯一重复组保留 `train/IMAGES/patches_101.jpg`，移除
`val/IMAGES/patches_105.jpg`。

| Split | Images | BBoxes | Manifest SHA256 |
|---|---:|---:|---|
| train v2 | 1260 | 2916 | `4e937507e0663ff76740b3fc6dd00552d82a3392a07a99fab17d816b7bc062b6` |
| val v2 | 359 | 825 | `4be24ebe0a6b8c7e3b75840bd9bab8f67d72b1608e97c21172ce7eb9a6713dd9` |
| test v2 | 180 | 442 | `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194` |

Q1-B path isolation and content SHA256 isolation both pass for every split
pair. The v2 train split is the intended future calibration source, but no
calibration manifest or calibration run has been generated.

### 6.5 Final Q1 split gate state

```text
split_v1_historical
status: preserved
reason: historical evidence reference

split_v2_deduplicated
status: Stage Q dataset authority
train_count: 1260
val_count: 359
test_count: 180
```

The Q1-B remediation result is content-isolated and path-isolated. The
historical preflight failure remains retained in the original report; the
final Q1 gate is represented as
`Q1_PLATFORM_AND_ASSET_PASS_WITH_SPLIT_REMEDIATION`. Training impact remains
`PENDING VERIFICATION`; Stage K/P test corpus identity is unchanged.

## 7. Benchmark Inventory

### 7.1 已有实验

| 实验 | 当前事实 | 主要 Evidence |
|---|---|---|
| ORT FP32 / CPU | M5 WSL2 x86_64 ORT CPU engineering baseline：20-image corpus，5 formal runs，每次 510 measured frames；另有 Stage J Jetson ORT CPU k1：5 runs、560 frames/run，wall throughput mean `2.3086948023 FPS`。二者硬件/协议不同。 | `results/benchmark/ort_cpu/20260719_850252b/`；`results/benchmark/jetson_ort_cpu/profile_baseline/j5_5_profile_baseline_v1/` |
| TRT FP16 Serial | Stage K7 Original FP16：3 valid runs，15000 measured samples，300 warmup；inference mean `11.1649436 ms` / `89.5660592 FPS`；e2e mean `17.0652018 ms` / `58.5987796 FPS`。 | `results/validation/stage_k7/performance_v1/fp16_original/benchmark_report.json` |
| TRT FP16 Pipeline | Stage P P5 corrected verdict `P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE`；queue capacity `1`；formal 5100/5100 processed、0 dropped，paired Pipeline/Serial ratio mean `4.165718`；P7 1800.006143093 s source-active，410691 frames，2281 complete cycles。 | `docs/personal/STAGE_P_FINAL_REPORT.md`；`results/benchmark/stage_p/p5_serial_vs_pipeline_v1/P5R_EVIDENCE_INDEX.md`；`results/validation/stage_p/p7_stability_v1/attempt_001/` |

Stage P 当前仓库保留的是 consolidated/index 文档和 P7 Evidence；P5 raw
attempt 目录由文档引用但不在当前工作树中，因此本报告不补写绝对 Serial/FPS
数值，只记录已提交的 ratio、frame count 和 verdict。

### 7.2 论文已有实验表结构

`docs/personal/EXPERIMENT_PLAN.md` 已有以下模板：

1. Model accuracy table：`Model | Input Size | Precision | Recall | mAP@0.5 | mAP@0.5:0.95`。
2. Backend comparison table：`Device | Input Size | Runtime Mode | Backend | Precision Mode | Avg Latency ms | P50 ms | P95 ms | FPS | Memory MB`。
3. Runtime comparison table：`Device | Backend | Input Size | Runtime Mode | Queue Size | Drop Policy | FPS | Avg Total Latency ms | P95 ms | Dropped Frames`。

当前 Stage Q 若出现在同一体系中，已有表结构能表达 backend/precision、精度
和运行时性能；但当前实际报告中尚无 INT8 行、calibration identity 列或
INT8-specific cache metadata。

## 8. Runtime Inventory

### 8.1 RuntimeConfig

| Schema | Backend/runtime 事实 |
|---:|---|
| 1 | legacy ORT directory serial config |
| 2 | `onnxruntime_cpu`，含 ORT options、serial runtime |
| 3 | `tensorrt_fp16`，TensorRT Engine/manifest、serial runtime |
| 4 | `tensorrt_fp16`，serial 或 pipeline；pipeline 要求 `queue_capacity` 1–16 和 `drop_policy=block` |

`RuntimeConfig` 当前包含 backend type、model contract path、model/input/output
path、postprocess、timing、ORT options、TensorRT engine path/manifest path/device
id 和 pipeline config；没有 precision、datatype 或 calibration fields。

### 8.2 Result JSON

`RunMetadata`/Result JSON 当前记录：

- `backend_type`；
- model filename/SHA；TensorRT 时的 source ONNX SHA 与 Engine manifest filename；
- ModelContract filename/artifact kind；
- class names、postprocess config、timing；
- Stage P runtime v3 的 `runtime_mode`、`input_type`、pipeline queue metadata；
- per-frame detections and `source_ms`、`preprocess_ms`、`inference_ms`、`postprocess_ms`、`pre_sink_total_ms`；pipeline 还记录 queue wait timings；
- summary 中的 processed/source frames、wall time、queue high-water marks。

Result JSON 没有 dedicated `precision`、tensor `datatype`、calibration dataset
identity、calibration cache SHA 或 calibration metadata。

### 8.3 Evidence 目录

当前与 INT8 前置事实直接相关的 Evidence 目录包括：

- `results/build/tensorrt/`
- `results/platform/tensorrt/`
- `results/validation/stage_k_task_eval_v2/`
- `results/validation/stage_k6/`
- `results/validation/stage_k7/`
- `results/validation/stage_k8/`
- `results/validation/stage_p/`
- `results/benchmark/stage_p/`
- `results/benchmark/ort_cpu/`
- `results/benchmark/jetson_ort_cpu/`

### 8.4 是否需要 INT8 runtime 扩展

需要。当前 parser/factory/engine 只识别 `tensorrt_fp16`，当前 Result JSON
也无法完整声明 INT8/calibration identity；因此 INT8 Engine 即使能由外部
`trtexec` 生成，也不能作为当前 production runtime 的一等 backend 被配置、
加载和审计记录。

## 9. Stage Q 可能风险

本节只记录风险，不提出实施方案。

- INT8 accuracy loss：量化可能改变置信度、框位置、NMS 输入和最终 mAP/Recall；当前已有 raw TensorRT Level B 数值限制，误差归因可能更困难。
- Calibration difficulty：当前没有项目 calibration dataset interface、calibrator、entropy calibrator、cache 或 metadata；校准覆盖不足、类别/纹理分布不均会影响结果。
- Evaluation leakage：把 val/test 或 Stage K/P evaluation corpus 用作 calibration，可能破坏 held-out 对比的解释性。
- Engine compatibility：Serialized TensorRT Engine 与 TensorRT/CUDA/L4T、Jetson GPU 架构绑定；INT8 tactic、workspace、插件和 runtime 版本变化可能造成加载失败或性能差异。
- Contract mismatch：当前 C++ TensorRT runtime 强制 FP32 IO、NCHW/BCN 和静态 shape；INT8 IO 或不同 output datatype 会触发当前 contract rejection。
- Benchmark comparability：当前 FP16 baseline 是 `FP32+FP16 mixed precision`，不是全层 FP16；ORT CPU、TRT Serial、TRT Pipeline 的硬件和计时语义不同，不能直接把不同 evidence 的数字拼成单一 speedup。
- Provenance incompleteness：当前 manifest 记录 `int8_enabled=false`，但没有 calibration identity；若新增 INT8 artifact，缺少这类元数据会使 Engine/数据/cache/结果之间无法闭环复核。
- Runtime observability：Result JSON 当前没有 precision/datatype/calibration fields，可能导致同一个 backend 名称下的不同量化 Engine 难以区分。
- Pipeline interpretation：Stage P 的 thermal status 为 unavailable；Pipeline throughput 结果不能自动转化为单帧 latency 或无 throttling 结论。

## 10. Fact sources

本报告主要依据以下当前 HEAD 文件/目录：

- `src/inference_engine_factory.cpp`
- `src/runtime_config.cpp`
- `src/tensorrt_engine.cpp`
- `src/tensorrt_engine_manifest.cpp`
- `include/edge_ai_defect/core/tensor.hpp`
- `include/edge_ai_defect/runtime/runtime_config.hpp`
- `include/edge_ai_defect/runtime/runtime_types.hpp`
- `models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json`
- `configs/model_contracts/yolov8n_neudet_frozen.yaml`
- `results/build/tensorrt/k2_fp16_engine_v1/`
- `results/validation/stage_k_task_eval_v2/`
- `results/validation/stage_k7/performance_v1/`
- `results/validation/stage_p/`
- `results/benchmark/stage_p/`
- `docs/personal/EXPERIMENT_PLAN.md`
- `docs/personal/STAGE_P_FINAL_REPORT.md`
- `docs/personal/STAGE_P_EVIDENCE_INDEX.md`

## 11. Q0 Freeze Status and Boundary

### 11.1 Normalization result

```text
Q0 normalization result: PASS
Decision numbering conflict resolved:
Existing Stage P decisions preserved: D072, D073
Stage Q allocation: D074-D080
Output layout correction: CHW -> BCN
```

The Stage Q plan remains `v0.3 FINAL`. The numbering allocation and output-layout
label are consistency corrections only; calibration route, thresholds, scope,
milestones, gates, runtime contract, and authorization chain are unchanged.

### 11.2 Stage status

| Item | Q0 fact |
|---|---|
| Stage J | COMPLETE |
| Stage K | COMPLETE |
| Stage P | COMPLETE |
| Stage Q plan | v0.3 FINAL |
| Q0 | Planning Freeze; documentation-only scope |
| Q1 platform and asset verification | NOT VERIFIED AT Q0 |
| Asset recovery | Asset recovery is not required at Q0 and has not been executed |
| Production implementation | NOT AUTHORIZED |

Q1 asset and platform verification has not been executed. Asset recovery is not
required at Q0. No Q1 hardware, dataset actual-existence, split-isolation, or
artifact-SHA result is represented as a Q0 PASS.

### 11.3 Read-only CMake and test inventory

The existing configured build directory is `build/`. Its recorded options are
`EDGE_AI_ENABLE_TENSORRT=OFF` and `EDGE_AI_ENABLE_MODEL_SMOKE=OFF`; no new build
directory was created and no CMake configure/build was run during Q0. Existing
configured build inventory was inspected with `ctest -N`; it lists 46 tests.

Current top-level targets include `edge_ai_core`, `edge_ai_backend_ort`,
`edge_ai_backend_trt` (stub in the recorded OFF configuration),
`edge_ai_postprocess`, `edge_ai_runtime`, `edge_ai_backend_factory`,
`edge_ai_application`, `edge_ai_infer`, `stage_j_profile_runner`,
`stage_k_raw_tensor_runner`, and `stage_p_experiment_runner`. Existing test
targets cover core, postprocessing, inference contracts, runtime configuration,
TensorRT contract, bounded queue/pipeline, sources, sinks, serial runner,
model/preprocessor contracts, and ORT smoke. This is an inventory only; no
formal test was executed.

### 11.4 Q0 evidence limit

The current repository facts establish the frozen contracts and historical
Stage K/P evidence references. They do not establish that the Q1 assets are
present on the current device, that split isolation has been rerun, or that any
INT8 Engine/calibration artifact exists. Such items remain `NOT VERIFIED AT Q0`.
