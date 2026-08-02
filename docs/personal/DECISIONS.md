# DECISIONS.md

## 1. 用途

本文档用于记录本项目中的重要技术路线选择。

项目名称：

**边缘 AI 工业缺陷检测部署与优化项目**

英文名称：

**Edge AI Industrial Defect Detection Deployment and Optimization**

本文档采用追加记录方式。

每当项目发生重要技术决策时，都应新增一条记录，而不是删除历史记录。

---

## 2. 记录原则

每条决策记录必须说明：

- 决策时间。
- 决策编号。
- 决策标题。
- 当前选择。
- 备选方案。
- 决策理由。
- 影响范围。
- 后续是否可调整。
- 当前状态。

记录语言：

- 中文为主。
- 专业术语保留英文原文，例如 `YOLOv8n`、`TensorRT FP16`、`ONNX Runtime`、`PipelineRunner`。

不得记录虚假信息。

不得把未确认事项写成已确认。

---

## 3. 状态标记

| 状态 | 含义 |
|---|---|
| ACTIVE | 当前有效 |
| SUPERSEDED | 已被后续决策替代 |
| DEFERRED | 延后决定 |
| REJECTED | 已明确不采用 |
| TBD | 尚未确定 |

---

## 4. 当前稳定决策总览

| ID | 决策项 | 当前选择 | 状态 |
|---|---|---|---|
| D001 | 项目定位 | Jetson 边缘 AI 工业缺陷检测部署与优化 | ACTIVE |
| D002 | 主数据集 | NEU-DET | ACTIVE |
| D003 | 主模型 | YOLOv8n | ACTIVE |
| D004 | 数据集划分 | train / val / test = 70 / 20 / 10 | ACTIVE |
| D005 | 输入尺寸 | 320, 416, 640 | ACTIVE |
| D006 | 训练语言 | Python | ACTIVE |
| D007 | 部署语言 | C++ | ACTIVE |
| D008 | 配置格式 | YAML | ACTIVE |
| D009 | 构建系统 | CMake | ACTIVE |
| D010 | baseline backend | ONNX Runtime | ACTIVE |
| D011 | optimized backend | TensorRT FP16 | ACTIVE |
| D012 | runtime modes | Serial, Pipeline | ACTIVE |
| D013 | v1 GUI | 不实现 GUI | ACTIVE |
| D014 | v1 ROS2 | 只预留接口 | ACTIVE |
| D015 | INT8 | 当前不做，后续可选 | ACTIVE |
| D016 | 主平台 | NVIDIA Jetson | ACTIVE |
| D017 | 冻结模型 | seed=7 deterministic baseline | ACTIVE |
| D018 | 正式训练 checkpoint 保留边界 | Git 外完整归档，部署只使用 frozen model | ACTIVE |
| D019 | TensorRT 验证平台与部署阶段路线 | 本地 ONNX Runtime 开发，TensorRT 延后到完整 CUDA / Jetson 平台 | ACTIVE |
| D020 | C++ ONNX Runtime Serial Baseline 阶段范围 | M0～M4 先完成 CPU Serial 主线 | ACTIVE |
| D021 | Preprocess Level A 证据边界 | raw BGR、独立冻结语义、SHA CTest 与前置提交 provenance | ACTIVE |
| D022 | C++ ONNX Runtime CPU 部署 baseline | M2 以 CPU synchronous Engine 作为后续 Serial Baseline foundation | ACTIVE |
| D023 | Engine tensor 所有权合同 | `HostTensor` 作为 Engine 输入和独占输出 | ACTIVE |
| D024 | Inference Level B 一致性方法 | 同一 raw input 下 Python ORT 与 C++ ORT 比较 | ACTIVE |
| D025 | M2 阶段边界 | 不包含 PostProcessor/NMS/TensorRT/Pipeline | ACTIVE |
| D026 | M3 frozen YOLOv8 PostProcessor 语义 | original-image Detection、class-aware NMS、独立 Python/C++ validation | ACTIVE |
| D027 | M3 clipping parity with Ultralytics 8.4.50 | clamp-only clipping，保留 post-clip 零面积 Detection | ACTIVE |
| D028 | M4 与 M5 验证边界 | M4 功能串行闭环和基础 FrameTimings；M5 Level C、正式 Profiler 与性能证据 | ACTIVE |
| D029 | M4 runtime 配置和 CLI | strict YAML；CLI 仅接受单个 `--config` 或单独 `--help` | ACTIVE |
| D030 | M4 图片输入抽象 | 最小 ImageSource；非递归、确定性、fail-fast DirectorySource | ACTIVE |
| D031 | M4 串行编排 | SerialRunner 仅依赖 IInferenceEngine，borrowed dependencies，fail-fast 与 summary 原子提交 | ACTIVE |
| D032 | M4 结果输出 | 单运行级 deterministic JSON、JsonSink 原子提交、CompositeSink 固定顺序 | ACTIVE |
| D033 | M4 Runner 模型输入合同 | 应用组装层注入 `ModelContract.input.tensor_info`，Runner 保存值副本 | ACTIVE |
| D034 | M5 Level C Reference | 同一冻结 ONNX 上的 Python ONNX Runtime 显式 pipeline | ACTIVE |
| D035 | M5 Level C Detection Matching | 按类别的确定性最大二分匹配；confidence 1e-4、bbox 0.01 pixel | ACTIVE |
| D036 | M5 Benchmark Instrumentation | 复用 M4 FrameTimings 和真实 application；离线 Python 统计 | ACTIVE |
| D037 | M5 ORT CPU Baseline 定位 | WSL2 x86_64 ONNX Runtime CPU Engineering Baseline | ACTIVE |
| D038 | M5 Evidence、Retention 和失效 | clean committed HEAD、raw samples/summary/provenance、明确失效边界 | ACTIVE |
| D039 | M5 NEU-DET 资产策略 | 不提交图片；跟踪 manifest/SHA/工具；本地合法 dataset root | ACTIVE |
| D067 | Stage P baseline、scope 与 execution authority | `main@c6890d86…`、v1.2 FINAL、P0→P8 | ACTIVE |
| D068 | Four-worker topology 与 single-inference boundary | 4 workers、3 bounded SPSC queues、最多一个 `engine.run()` | ACTIVE |
| D069 | RuntimeConfig v4、Result JSON v3 与 compatibility | TensorRT-only v4，独立 Result v3，历史行为不变 | ACTIVE |
| D070 | Exact correctness、timing 与 benchmark contract | RUN/CYCLE 独立域、精确 EOS/timing/window/Gate | ACTIVE |
| D071 | Offline block-only sources 与 deferred live-stream scope | Directory/Video block-only；live/drop 延后 | ACTIVE |
| D072 | Stage P P5R protocol correction and Evidence reclassification | Extended-window RUN SHA 比较同 protocol runs；complete CYCLE SHA 继承 P4；thermal unavailable 为 known limitation | ACTIVE |
| D073 | Stage P P8 consolidation and closeout | Stage P P4–P7 Evidence closed；bounded Pipeline closeout | ACTIVE |
| D074 | Stage Q baseline, scope and authority | Stage Q exact baseline、v0.3 FINAL plan、Q0–Q8 authorization chain | ACTIVE |
| D075 | TensorRT 10.3 version-bound legacy PTQ | Implicit INT8 calibration with entropy calibrator、INT8+FP16 fallback、FP32 Host I/O | ACTIVE |
| D076 | Calibration data isolation and ordering | All 1260 train images、path/content split isolation、seed 42 deterministic ordering | ACTIVE |
| D077 | Builder, cache and artifact authority | Stage Q builder唯一；Q2 smoke、Q3 formal force-miss、atomic publication | ACTIVE |
| D078 | Manifest, runtime and result mapping | RuntimeConfig v5、Manifest v2 INT8、Result JSON v4、validated provenance | ACTIVE |
| D079 | Accuracy, hash and Serial performance authority | Same-runtime-build controls、frozen replay/hash、three paired Serial runs | ACTIVE |
| D080 | Conditional Pipeline and final disposition | Frozen Pipeline gate、300-second confirmation、mechanical disposition tree | ACTIVE |
| D081 | Controlled CUDA Preprocessing Exception | Stage R V2–V4 CUDA fused preprocessing authorization; no GPU NMS/postprocess/通用BufferManager/Zero-Copy | ACTIVE |
| D082 | Limited Application CUDA Streams Exception | V2/V3 no overlap; V4 max 2 streams, 2 slots; no concurrent inference/output overlap | ACTIVE |
| D083 | Cross-Preprocess Identity Exception | V0 vs GPU family by geometry/tensor/task accuracy Gates; V2/V3/V4 same-path identity required | ACTIVE |

---

## 5. 决策记录

---

### D001 - 项目定位

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

本项目定位为：

```text
Jetson-based edge AI deployment and real-time inference optimization system for industrial visual defect detection
```

中文定位：

```text
面向工业视觉场景的 Jetson 边缘 AI 部署与实时推理优化系统
```

备选方案：

* 核心 AI 算法研究项目。
* 自研目标检测网络项目。
* 完整机器人系统项目。
* 工业视觉部署优化项目。

选择理由：

* 项目负责人背景更偏嵌入式、半导体设备软件、Qt 和工程部署。
* 毕业设计、小论文和求职都更适合走工程部署路线。
* 自研算法路线难度高、风险大，且与求职定位不完全匹配。
* Jetson + TensorRT 能体现边缘部署、性能优化和工程落地能力。

影响范围：

* 项目整体叙事。
* 论文创新点表述。
* 简历项目描述。
* Codex 任务边界。
* 实验设计方向。

后续调整：

不建议调整。除非导师明确要求算法创新，否则项目应保持工程部署定位。

---

### D002 - 主数据集选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

主数据集选择：

```text
NEU-DET / NEU Surface Defect Database
```

备选方案：

* COCO。
* MVTec AD。
* DAGM。
* 自采集工业缺陷数据集。
* NEU-DET。

选择理由：

* NEU-DET 属于工业表面缺陷检测场景。
* 数据规模适中，适合有限时间内完成训练和实验。
* 适合转换为 YOLO object detection 格式。
* 与论文中的工业视觉、边缘质检叙事匹配。
* 避免项目转向 anomaly detection、segmentation 或大规模标注。

影响范围：

* 数据处理脚本。
* 训练流程。
* 论文实验设计。
* 模型精度实验。
* 输入尺寸对比实验。

后续调整：

可增加其他数据集作为扩展实验，但不应替代 NEU-DET 主线。

---

### D003 - 主模型选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

主模型选择：

```text
YOLOv8n
```

备选方案：

* YOLOv5n。
* YOLOv8n。
* YOLO11n。
* 更大的 YOLO 模型。
* 自研检测网络。

选择理由：

* YOLOv8n 轻量，适合 Jetson 边缘部署。
* 生态成熟，训练、导出和部署资料较多。
* 适合 NEU-DET 这类中小规模工业缺陷检测任务。
* 复杂度可控，适合毕业设计和小论文周期。
* 与项目“工程部署而非算法创新”的定位一致。

影响范围：

* 训练脚本。
* ONNX export。
* TensorRT engine 生成。
* C++ PostProcessor。
* 实验指标和论文表述。

后续调整：

YOLOv5n 或 YOLO11n 可作为可选对比模型，但不进入 v1 主线。

---

### D004 - 数据集划分比例

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

数据集划分比例为：

```text
train / val / test = 70 / 20 / 10
```

备选方案：

* 80 / 10 / 10。
* 70 / 20 / 10。
* 训练集和验证集，不单独保留 test。
* 随机临时划分。

选择理由：

* 保留独立 test split，有利于实验可信度。
* 70 / 20 / 10 在小数据集上能提供相对充足的 validation 数据。
* 有利于训练、调参和最终评估分离。
* 便于论文说明实验流程。

影响范围：

* 数据集转换脚本。
* 训练配置。
* 精度实验。
* 论文实验可信度。

后续调整：

原则上不调整。若数据量或类别分布导致某类样本过少，可记录原因后重新决策。

---

### D005 - 输入尺寸选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

输入尺寸对比选择：

```text
320 × 320
416 × 416
640 × 640
```

备选方案：

* 只使用 640。
* 320 / 640 两组。
* 320 / 416 / 640 三组。
* 额外增加 512 或 1280。

选择理由：

* 320、416、640 能形成清晰的 speed / accuracy trade-off。
* 640 是 YOLO 常用输入尺寸。
* 320 有利于边缘设备实时性能。
* 416 作为中间点，有利于观察性能和精度变化趋势。
* 三组实验复杂度可控，适合小论文表格。

影响范围：

* 训练配置。
* ONNX export。
* TensorRT engine。
* 输入尺寸实验。
* 论文表格。

后续调整：

原则上保持三组。若 Jetson 性能或时间不足，可优先完成 320 和 640，再补 416。

---

### D006 - 训练语言选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

训练部分使用：

```text
Python
```

备选方案：

* Python。
* C++。
* 混合方式。

选择理由：

* YOLOv8n 训练生态主要基于 Python。
* `ultralytics`、`torch` 等工具链成熟。
* 训练不是本项目的核心工程创新点，使用 Python 可降低成本。
* 有利于快速获得 `best.pt` 和 ONNX 模型。

影响范围：

* `scripts/train/`
* `scripts/export/`
* 数据集转换脚本。
* 训练日志和精度结果。

后续调整：

不建议调整。Python 只负责训练、导出和分析，不作为部署主运行时。

---

### D007 - 部署语言选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

部署部分使用：

```text
C++
```

备选方案：

* Python 部署。
* C++ 部署。
* Python 先部署，C++ 后迁移。
* Python / C++ 混合部署。

选择理由：

* C++ 更符合嵌入式软件和边缘部署岗位定位。
* TensorRT C++ 能更好体现部署能力。
* 有利于面试中展示工程实现能力。
* 有利于后续扩展到 ROS2 或设备软件场景。
* 避免项目被理解为纯 Python demo。

影响范围：

* C++ 工程结构。
* CMake。
* ONNX Runtime C++ API。
* TensorRT C++ API。
* SerialRunner / PipelineRunner。
* Profiler。
* ResultSink。

后续调整：

不建议改为 Python 主部署。可以用 Python 做辅助脚本，但 C++ 是部署主线。

---

### D008 - 配置文件格式选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

配置文件格式选择：

```text
YAML
```

备选方案：

* YAML。
* JSON。
* TOML。
* 命令行参数硬编码。
* C++ 源码中硬编码。

选择理由：

* YAML 可读性好，适合实验配置。
* 便于 Codex 和人工同时维护。
* 适合表达嵌套配置，例如 backend、runtime mode、paths、thresholds、profiling。
* 有利于实验复现。

影响范围：

* `configs/`
* `ConfigManager`
* 实验运行方式。
* 日志中的 config snapshot。
* 论文实验复现。

后续调整：

不建议调整。JSON 可用于日志输出，但不作为主配置格式。

---

### D009 - 构建系统选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

C++ 构建系统选择：

```text
CMake
```

备选方案：

* Makefile。
* CMake。
* Bazel。
* Meson。
* 手工编译命令。

选择理由：

* CMake 是 C++ 工程常用构建系统。
* 适合管理 OpenCV、yaml-cpp、ONNX Runtime、TensorRT、CUDA Runtime 等依赖。
* 适合 Jetson 和本地环境。
* 对毕业设计和求职展示足够正式。

影响范围：

* `CMakeLists.txt`
* C++ 工程结构。
* 依赖管理。
* 构建说明。
* 测试集成。

后续调整：

不建议调整。CMake minimum version 后续根据环境确定。

---

### D010 - Baseline Backend 选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

Baseline backend 选择：

```text
ONNX Runtime
```

备选方案：

* PyTorch。
* ONNX Runtime。
* TensorRT。
* OpenCV DNN。
* OpenVINO。

选择理由：

* ONNX Runtime 可作为跨平台推理 baseline。
* 与 ONNX export 路线自然衔接。
* 便于和 TensorRT FP16 进行对比。
* 复杂度低于直接从 TensorRT 起步。
* 适合先完成本地 baseline 验证。

影响范围：

* `ONNXRuntimeEngine`
* C++ inference interface。
* backend comparison 实验。
* 论文 baseline 设计。

后续调整：

不建议取消。即使 TensorRT 是主优化，ONNX Runtime 仍应保留为 baseline。

---

### D011 - Optimized Backend 选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

Optimized backend 选择：

```text
TensorRT FP16
```

备选方案：

* TensorRT FP32。
* TensorRT FP16。
* TensorRT INT8。
* RKNN。
* OpenVINO。
* NCNN。

选择理由：

* TensorRT 是 NVIDIA Jetson 平台核心推理优化工具。
* FP16 相比 INT8 复杂度更低，不需要 calibration。
* FP16 更适合作为当前小论文和毕设主线。
* TensorRT FP16 能体现边缘推理优化能力。

影响范围：

* `TensorRTEngine`
* TensorRT engine 生成。
* backend comparison 实验。
* Jetson 部署。
* 论文核心实验。

后续调整：

INT8 可作为后续扩展，但当前不进入 v1 主线。

---

### D012 - Runtime Mode 选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

实现两种 runtime mode：

```text
Serial mode
Pipeline mode
```

备选方案：

* 只做 Serial mode。
* Serial mode + Pipeline mode。
* 更复杂的多阶段异步框架。
* 多进程架构。

选择理由：

* Serial mode 作为 baseline，结构清晰，容易测量。
* Pipeline mode 用于分析 throughput / FPS 优化。
* 两者对比适合形成论文工程实验。
* 三线程 pipeline 复杂度可控。
* 有利于面试中解释系统设计能力。

影响范围：

* `SerialRunner`
* `PipelineRunner`
* 队列设计。
* profiling 设计。
* runtime comparison 实验。
* 论文实验章节。

后续调整：

可调整 pipeline 细节，但不应取消 Serial baseline。

---

### D013 - v1 GUI 决策

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

v1 不实现 GUI。

所有核心功能必须支持 command-line 运行。

备选方案：

* v1 实现 Qt GUI。
* v1 实现 Web UI。
* v1 不实现 GUI，只保存结果。
* 后续扩展 GUI。

选择理由：

* GUI 会消耗大量时间，但不是小论文核心。
* 当前核心目标是推理部署、profiling 和实验。
* 命令行方式更适合实验复现。
* 可视化结果可以通过保存图片或视频实现。

影响范围：

* `ResultSink`
* 项目范围。
* 任务优先级。
* 毕设 demo 计划。

后续调整：

GUI 可作为毕业设计后期扩展，但不能影响核心推理和实验框架。

---

### D014 - v1 ROS2 决策

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

v1 只预留 ROS2 接口，不实现完整 ROS2 publisher。

备选方案：

* v1 完整实现 ROS2 package。
* v1 实现 ROS2 publisher。
* v1 只预留接口。
* 完全不考虑 ROS2。

选择理由：

* ROS2 对求职有一定加分，但不是当前小论文主线。
* 引入 ROS2 会增加依赖和构建复杂度。
* 预留 `DetectionResult` 输出结构即可支持后续扩展。
* 避免项目在 v1 阶段跑偏。

影响范围：

* `ResultSink`
* `DetectionResult`
* 架构扩展点。
* 后续机器人感知接口扩展。

后续调整：

核心系统稳定后，可新建 ROS2 publisher 扩展模块。

---

### D015 - INT8 决策

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

当前主线不做 INT8。

INT8 仅作为后续可选优化项。

备选方案：

* 当前就做 INT8。
* 只做 TensorRT FP16。
* FP16 完成后再评估 INT8。
* 不考虑 INT8。

选择理由：

* INT8 需要 calibration dataset 和校准流程。
* INT8 会增加 TensorRT 部署复杂度。
* FP16 已足够支撑小论文的优化实验。
* 当前更重要的是完成可运行、可测量、可解释的主线。

影响范围：

* TensorRT engine 生成。
* 实验设计。
* 项目范围控制。
* Codex 任务边界。

后续调整：

只有在 TensorRT FP16 完成并且时间充足时，才考虑 INT8。

---

### D016 - 主部署平台选择

时间：

```text
2026-07-09
```

状态：

```text
ACTIVE
```

决策：

主部署平台选择：

```text
NVIDIA Jetson + TensorRT
```

备选方案：

* NVIDIA Jetson + TensorRT。
* RK3588 + RKNN。
* x86 GPU + TensorRT。
* 双平台同时推进。

选择理由：

* TensorRT 与 Jetson 平台匹配。
* Jetson 更适合边缘 AI 部署叙事。
* 双平台会显著增加项目复杂度。
* 当前目标是完成一个可运行、可测、可写论文的系统。

影响范围：

* 硬件采购或借用。
* TensorRT 部署。
* 小论文实验数据。
* 求职项目定位。

后续调整：

RK3588 / RKNN 可作为长期扩展，不进入当前主线。

---

### D017 - 冻结模型选择

时间：

```text
2026-07-12
```

状态：

```text
ACTIVE
```

决策：

最终冻结模型选择：

```text
seed=7 deterministic baseline → models/pytorch/yolov8n_neudet_frozen.pt
SHA256: 5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7
```

备选方案：

- seed=42 deterministic baseline（mAP50 最高，mAP50-95 与 seed=7 仅差 0.001）。
- seed=123 deterministic baseline（Recall 最高，但名义 mAP50-95 低于另外两个 seed；不作显著性结论）。
- V1 / seed=42 repeat（真实 `args.yaml` 均为 `deterministic=true`，两者有效参数和指标一致）。
- V2～V6 变体（均未在 mAP50-95 上获得稳定提升）。

选择理由：

- mAP50-95 在所有 deterministic baseline 中名义最高（0.45085），虽然与 seed=42 的 0.001 差距远小于三次实验观察到的波动范围（σ≈0.006）。
- Recall 高于 seed=42 deterministic，满足性能相当模型优先选择较高 Recall 的工程规则。
- `deterministic=true` 提高固定软件栈和硬件条件下的可重复性，但不保证跨平台、驱动或框架版本的位级一致。
- 属于同一性能水平内的工程选择，不宣称统计显著优胜。

影响范围：

- 后续所有 ONNX export、TensorRT 转换、Jetson 部署实验统一使用此冻结模型及对应 SHA256。
- test split 结果仅用于最终报告，不得反向用于训练调参或模型选择。
- 训练阶段不再继续扩大超参数搜索。
- 轻量机器可读证据保存在 `results/training/evidence/`；冻结模型和完整归档不进入 Git。

后续调整：

原则上不调整。如需更换模型，必须记录新的决策并更新 SHA256。

---

### D018 - 正式训练 checkpoint 的离线保留边界

时间：

```text
2026-07-12
```

状态：

```text
ACTIVE
```

决策：

* 全部 9 个正式训练实验的 `best.pt` 作为离线审计资产保存在独立 checkpoint archive 中。
* Git 不保存任何模型权重或归档包，只保存轻量文档、SHA256、指标和 provenance。
* 后续 ONNX、TensorRT 和 Jetson 部署只使用 frozen model；其余 checkpoint 不参与后续模型选择。
* 在本地归档校验和 `feature/dataset-training` Git push 完成后，训练服务器可以释放。

备选方案：

* 仅保存 frozen model：体积更小，但无法完整离线审计其他正式实验 checkpoint。
* 将全部 checkpoint 纳入 Git：可集中管理，但违反大模型资产边界并显著增大仓库。

选择理由：

* 独立归档同时满足完整审计、哈希校验和 Git 仓库轻量化要求。
* 非冻结 checkpoint 仅用于历史复核或必要时重新 validation，不属于部署运行依赖。
* seed=7 checkpoint 与 frozen model 哈希一致，冻结模型来源链可离线验证。

影响范围：

* `results/training/evidence/EXPERIMENT_PROVENANCE.json`
* `docs/TRAINING_ARCHIVE_INDEX.md`
* 训练服务器生命周期和后续 ONNX 分支起点

后续调整：

归档至少保留两份独立本地副本。除非新增正式训练决策，否则不再改变 checkpoint 集合或模型选择。

---

### D019 - TensorRT验证平台调整与部署阶段路线收敛

时间：

```text
2026-07-13
```

状态：

```text
ACTIVE
```

背景：

* 当前开发环境为 WSL2 Ubuntu 22.04。
* 当前开发机记录的 GPU 为 GTX1050Ti，但本次检查中 GPU / NVML 无法在 WSL2 内访问。
* 项目 `.venv` 缺少 TensorRT Python binding，`torch.cuda.is_available()` 为 `False`。
* 当前环境已经完成 ONNX export、Python ONNX Runtime smoke test 和 PyTorch / ONNX Runtime 数值一致性验证，但不适合作为 TensorRT FP16 验证平台。

决策：

1. 开发机阶段使用 C++17、ONNX Runtime 和 OpenCV，完成 C++ inference framework、Serial mode、Pipeline mode 与软件架构验证。
2. TensorRT FP16 backend 的构建和验证推迟到 Jetson，或具备完整且可访问 CUDA / TensorRT 环境的平台。
3. TensorRT 保持为 optimized backend 和最终部署主线，但不作为当前 WSL2 开发机的验证目标。
4. 当前环境不强制安装 TensorRT，不修改系统 CUDA、NVIDIA driver 或 WSL GPU 配置来绕过平台限制。

备选方案：

* 在当前 WSL2 环境强行补装 TensorRT Python：binding 与 GPU runtime 均不满足，不能形成有效 FP16 验证证据。
* 暂停全部部署开发直至 Jetson 到位：会阻塞与硬件无关的 C++ 架构和 ONNX Runtime baseline 工作。

选择理由：

* ONNX Runtime 可在当前开发环境完成跨平台 baseline、接口和 runtime architecture 验证。
* `InferenceEngine` backend 解耦后，SerialRunner / PipelineRunner 不依赖具体推理库，可先稳定软件结构。
* TensorRT engine 与目标 GPU、CUDA、driver 和 TensorRT 版本强相关，在目标或兼容平台验证更可复现。

影响范围：

* 本地开发顺序调整为 C++ ONNX Runtime baseline → Serial / Pipeline architecture。
* TensorRT FP16 engine、backend 和论文性能数据延后到 Jetson 或兼容 GPU 平台。
* 不改变项目总体路线：

```text
PyTorch
→ ONNX
→ ONNX Runtime baseline
→ TensorRT FP16
→ Jetson deployment
```

后续调整：

Jetson 或兼容 CUDA / TensorRT 平台确定后，记录 GPU、driver、CUDA、TensorRT、engine generation method 和环境 provenance，再启动 TensorRT validation 与性能实验。

---

## 6. 待决策事项

以下事项尚未确定，后续确定后应追加新的决策记录。

| 事项                         | 当前状态 | 决策时机                         |
| -------------------------- | ---- | ---------------------------- |
| Jetson 具体型号                | TBD  | 本地 ONNX Runtime baseline 跑通后 |
| JetPack version            | TBD  | Jetson 型号确定后                 |
| CUDA version               | TBD  | JetPack version 确定后          |
| TensorRT version           | TBD  | JetPack version 确定后          |
| ONNX Runtime C++ version   | TBD  | C++ ONNX Runtime 集成前         |
| OpenCV version             | TBD  | C++ 项目骨架创建前                  |
| CMake minimum version      | TBD  | C++ 项目骨架创建前                  |
| TensorRT engine 生成方式       | TBD  | Jetson TensorRT 部署前          |
| Resource monitoring method | TBD  | 性能实验前                        |
| Pipeline queue size 最终值    | TBD  | PipelineRunner 实现与测试后        |
| Warmup frames 最终值          | TBD  | 初步性能测试后                      |
| Measured frames 最终值        | TBD  | 初步性能测试后                      |

---

## 7. 新决策记录模板

后续追加新决策时，使用以下字段结构：

* 标题：`### DXXX - 决策标题`
* 时间：`YYYY-MM-DD HH:mm`
* 状态：`ACTIVE` / `SUPERSEDED` / `DEFERRED` / `REJECTED` / `TBD`
* 决策：填写最终选择，未确认时不得写成已确认。
* 备选方案：列出至少两个被比较的方案。
* 选择理由：说明为什么当前方案更适合本项目。
* 影响范围：列出受影响的模块、文档或实验。
* 后续调整：说明是否可调整，以及什么情况下调整。

---

## 8. 更新规则

后续 agent 更新本文档时，必须遵守：

1. 新决策只追加，不删除历史记录。
2. 如果旧决策被替代，将旧记录状态改为 `SUPERSEDED`，并新增替代决策。
3. 不得把未确认事项写成已确认。
4. 不得伪造环境版本、实验数据或硬件信息。
5. 重大技术路线变化必须同步更新相关文档：
   - `AGENTS.md`
   - `PROJECT_BRIEF.md`
   - `REQUIREMENTS.md`
   - `ARCHITECTURE.md`
   - `docs/CODING_RULES.md`
   - `docs/personal/EXPERIMENT_PLAN.md`
   - `docs/personal/ENVIRONMENT.md`
   - `docs/personal/TASKS.md`
6. 影响实验的决策必须同步更新 `docs/personal/EXPERIMENT_PLAN.md`。
7. 影响代码结构的决策必须同步更新 `ARCHITECTURE.md`。
8. 影响需求边界的决策必须同步更新 `REQUIREMENTS.md`。
9. 影响硬件、系统、驱动、依赖或测试环境的决策必须同步更新 `docs/personal/ENVIRONMENT.md`。

---

## 9. Final Summary

当前项目的稳定技术路线是：

```text
NEU-DET
→ YOLOv8n
→ Python training
→ ONNX export
→ C++ ONNX Runtime baseline
→ C++ TensorRT FP16 optimized inference
→ Jetson deployment
→ Serial / Pipeline comparison
→ CSV / JSON experiment logs
→ thesis, paper, and job-seeking evidence
```

所有后续决策都应服务于这个主线，不应把项目扩展成算法研究、GUI 应用、完整机器人系统或多平台部署项目。

---

### D020 - C++ ONNX Runtime Serial Baseline 阶段范围

时间：

```text
2026-07-15
```

状态：

```text
ACTIVE
```

决策：

1. C++ 部署阶段从 ONNX Runtime CPU Serial Baseline 开始。
2. TensorRT 延后到 Jetson 阶段；TensorRT 性能数据只在目标设备采集。
3. 当前阶段不引入 Pipeline、ROS2、Qt、INT8、GPU preprocessing 或 GPU NMS。

选择理由：

- 当前开发环境是 WSL2 x86_64，适合先建立和验证 C++ 软件架构。
- TensorRT 强依赖 CUDA、driver 和 Jetson 环境；在非目标平台不能形成有效性能结论。
- 先完成可验证的 Serial Baseline，控制范围并保持后续 backend 替换的接口抽象。

影响范围：

- M0 至 M4 仅覆盖 C++17、OpenCV、yaml-cpp、ONNX Runtime CPU 和 SerialRunner。
- TensorRT、Jetson、Pipeline 与性能优化保留为后续阶段。

---

### D021 - Preprocess Level A 证据边界

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

1. Level A 输入使用 headerless raw BGR bytes，排除图像解码与 EXIF 行为差异。
2. Python golden generator 与 C++ validator 独立实现；A～H 的 frozen case 语义由
   test-only `FrozenCaseSpec` 再独立冻结。
3. 实际资产通过 CTest 校验 `SHA256SUMS`，manifest 中 16 个 asset digest 与其
   自动交叉验证。
4. stable provenance 引用已经存在的前置 evidence source commit，避免最终文档
   提交或未来提交的自引用。
5. manifest parser、compare helper 与 evidence verifier 只链接 test target，不进入
   production target。

备选方案：

- 使用 PNG/JPEG 输入：更接近业务文件，但会混入 decoder 与 orientation 差异。
- 只依赖 manifest 或人工 `sha256sum`：实现更少，但无法形成持续自动证据闭环。
- provenance 引用最终关闭提交：会形成不可生成的提交自引用。

选择理由：

- raw BGR 使 Level A 只验证 LetterBox、颜色/layout 转换与 normalization。
- 双重冻结可防止 generator 与 validator 同步漂移后产生假阳性。
- CTest SHA、resolved-path containment 和前置提交 provenance 提供确定、可复查且
  不污染 production dependency 的轻量证据链。

影响范围：

- `tests/data/preprocess_level_a/`
- `tests/preprocess_level_a_*`
- `tests/cmake/verify_preprocess_level_a_*.cmake`
- `results/validation/preprocess_level_a/`

后续调整：

M1 证据语义原则上冻结。如增加图像解码/orientation 验证，应建立独立 validation
level，不得改写现有 Level A A～H case 或 provenance 语义。

---

### D022 - C++ ONNX Runtime CPU 部署 baseline

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M2 使用 C++ ONNX Runtime `CPUExecutionProvider` 的 synchronous
`OnnxRuntimeEngine` 作为后续 C++ Serial Baseline 的 Engine foundation。其固定执行
语义为 `ORT_SEQUENTIAL`、`ORT_ENABLE_ALL`、intra/inter-op thread 各为 1；该选择
用于确定性和可验证性，不构成性能优化或 benchmark 结论。

备选方案：

- 在 M2 直接引入 TensorRT、CUDA 或 GPU Execution Provider。
- 在未完成 Engine contract 验证前实现完整 SerialRunner。

选择理由：

- 当前环境已具备可复现的 ONNX Runtime CPU 1.23.2 验证路径。
- CPU Engine 先提供稳定、backend-neutral 的推理基础，后续才能独立实现
  PostProcessor、Runner 和 TensorRT backend。

影响范围：

- `edge_ai_backend_ort` 和 M2 相关 validation。
- 后续 M3/M4 只能消费该 Engine contract，不得将 backend-specific 逻辑迁入 runner。

后续调整：

TensorRT、CUDA 和 GPU EP 仅在目标环境及独立阶段决定；它们不追溯改变 M2 CPU
baseline 的验证结论。

---

### D023 - Engine tensor 所有权合同

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

`IInferenceEngine` 和 `OnnxRuntimeEngine` 均使用 `HostTensor` 作为输入与输出
合同。`run()` 只借用调用方 input buffer 至 `Session::Run` 返回；成功输出必须复制为
调用方独占的 `HostTensor`，失败时不得修改调用方既有 output。

备选方案：

- 新建 `InferenceOutput` 包装类型。
- 返回借用的 `Ort::Value` 指针或 device tensor。

选择理由：

- 现有 `HostTensor` 已表达 M2 所需的 `float32`、layout、shape 和连续 CPU owned
  buffer。
- 独占输出消除 ORT output 生命周期泄漏，且不为尚未开始的 detection metadata 或
  device memory 预设抽象。

影响范围：

- M2 Engine public API、run failure 语义和后续 PostProcessor input。

后续调整：

如后续需求确实需要 backend-specific metadata 或 device memory，须新增独立设计与
兼容性审查；不得静默修改当前 `HostTensor` contract。

---

### D024 - Inference Level B 一致性方法

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M2 使用同一固定 `float32 NCHW [1,3,640,640]` raw input，以 Python ONNX Runtime
1.23.2 golden 与 C++ `OnnxRuntimeEngine` raw output 对比，作为 inference
Level B 一致性验证。验证输出为 `float32 BCN [1,10,8400]`，比较完整 84000 个元素的
shape、element count、finite、MAE 与 max_abs；冻结阈值为 `MAE <= 1e-6`、
`max_abs <= 1e-5`。

备选方案：

- 仅验证 C++ `Session::Run` 不抛异常。
- 使用 PostProcessor/detection 结果进行间接比较。

选择理由：

- raw tensor 对比直接覆盖 Engine I/O、metadata 和 ORT run path，不混入
  preprocessing 或后处理差异。
- Python/C++ 使用相同 ORT 1.23.2，且已保存 input、golden、C++ output、comparison
  report 和 provenance，能够复核实际结果。

影响范围：

- `results/validation/onnx_runtime_engine_level_b/` 和 M2 Gate 结论。

后续调整：

阈值或 reference environment 变更必须提供差异证据并独立评审，不能为了通过而放宽
当前阈值。

---

### D025 - M2 阶段边界

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M2 只关闭 ONNX Runtime Engine foundation；不包含 `PostProcessor`、NMS、
`Detection`、`SerialRunner`、`Pipeline`、Profiler、benchmark、TensorRT、CUDA 或
GPU Execution Provider。

备选方案：

- 将 raw output 解码、NMS、runner 或性能测量和 Engine 一并实现。
- 提前增加 TensorRT/CUDA backend。

选择理由：

- 分离 Engine correctness 与后处理、编排和性能问题，确保 Level B numerical
  evidence 的边界清晰。
- 防止当前 CPU 验证环境被误表述为 Jetson/TensorRT 性能或完整应用验证。

影响范围：

- M2 closeout、M3 PostProcessor preparation 和 M4 Serial Baseline 的工作分界。

后续调整：

M3 可在不修改 M2 Engine contract 的前提下开始 PostProcessor design/implementation；
TensorRT、CUDA、Pipeline 与 benchmark 继续留在各自独立阶段。

---

### D026 - M3 frozen YOLOv8 PostProcessor 语义

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

1. M3 只处理 frozen `float32 BCN [1,10,8400]` raw `HostTensor`。channels 0～3 为
   `cx,cy,w,h`，channels 4～9 为与 frozen `ModelContract` 一致的六类分数；没有
   objectness 或 embedded NMS。
2. `PostProcessor` 是 concrete class，不引入 `IPostProcessor`。它输出含 xyxy、
   confidence、class id 和 candidate index 的最小 `Detection`；坐标在 M3 内通过
   `ImageTransformMetadata` 恢复为 original-image space 并 clip。
3. 候选使用最大 class score（score tie 取较小 class id），只保留
   `confidence > 0.25F`；NMS 为 class-aware、`IoU > 0.45F` 抑制、`max_nms=30000`、
   `max_det=300`、`max_wh=7680.0F`。pre-NMS 与最终 Detection 均采用
   confidence desc / class id asc / candidate index asc 的显式 deterministic order。
4. M3 consistency evidence 必须使用独立 Python reference 与同一 frozen raw tensor
   比较完整 detection；不得使用现有 PT/ONNX shared-NMS comparison，也不得经过
   C++ Preprocessor、ORT Engine 或 Runner。完整 E2E Level C 保留给 M5。

备选方案：

- 保留 model-input coordinates，将 inverse LetterBox 延后给 Runner。
- 使用 OpenCV DNN NMS、class-agnostic NMS 或仅比较最终 detection count。
- 为潜在多模型实现预先引入 `IPostProcessor`/通用解析框架。

选择理由：

- M1 已生成完整且可验证的 transform metadata，M3 可在不读取图像的情况下履行
  architecture/requirements 的 original-coordinate restoration 职责。
- 现有 Python export comparison 未固定 equal-score candidate order、且两侧共用 NMS，
  不能独立证明 C++ 后处理；明确 canonical order 和独立 reference 使结果可复查。
- frozen model contract 只有一个静态 YOLOv8 output，最小 concrete contract 能避免
  对未实现 backend、dynamic shape 或 application metadata 的过早抽象。

影响范围：

- M3.1 Detection/PostProcessor contract、M3 decode/NMS implementation 和
  `tests/data/postprocessor_reference/` / `results/validation/postprocessor_only/` evidence。
- M4 Runner 将消费 original-image `Detection`，但不拥有 decode/NMS 或坐标恢复逻辑。

后续调整：

若模型 output、类别语义、NMS 策略或 coordinate contract 改变，必须提供新的 model
contract/reference evidence 并经架构审查；不得静默改变已冻结的 M3 detection semantics。

---

### D027 - M3 clipping parity with Ultralytics 8.4.50

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M3 baseline `PostProcessor` 的 inverse LetterBox 后使用 continuous xyxy clipping：x clamp
到 `[0, original_width]`，y clamp 到 `[0, original_height]`。为与本地固定
Ultralytics 8.4.50 的 `scale_boxes() -> clip_boxes()` 行为保持 parity，M3 不做 post-clip
degeneracy 或 minimum-size filtering；零宽或零高的最终 `Detection` 必须保留。所有输出坐标
仍必须 finite，且满足非降序边界。零面积过滤若为业务所需，必须作为后续显式业务层策略，
不属于 M3 baseline。

选择理由：

- 固定 Ultralytics 8.4.50 `scale_boxes()` 在 inverse transform 后只调用 `clip_boxes()`；
  后者 clamp 四个坐标后直接返回，未过滤 `x1 == x2` 或 `y1 == y2` 的框。
- decode 阶段 `w <= 0` / `h <= 0` skip 和 xyxy overflow skip 是 raw prediction 的非法
  geometry policy，不等同于有效 NMS candidate 被恢复并 clip 后退化。
- 保持该边界行为使后续 M3 Python/C++ PostProcessor-only validation 能比较完整 detection
  而无隐式过滤差异。

影响范围：

- M3.4 transform/clip/process implementation 与其 unit tests。
- 后续 `tests/data/postprocessor_reference/` 的 Python/C++ PostProcessor-only detection evidence。

后续调整：

任何业务层零面积过滤必须有单独的配置/contract、测试和架构决策；不得倒灌修改 M3 baseline
PostProcessor。

---

### D028 - M4 与 M5 验证边界

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M4 只建立 deterministic single-thread C++ ONNX Runtime functional baseline，包括 strict runtime
configuration、DirectorySource、M1/M2/M3 composition、ResultSink、SerialRunner、actual ORT smoke 和
per-frame 基础 `FrameTimings`。M4 不建立 public Profiler，不做 warmup、statistics、FPS 或 benchmark。

完整 Level C image-to-detection parity、正式 Profiler、warmup/minimum sample rules、mean/percentiles/FPS、
ORT CPU performance baseline、stability 和 paper performance evidence 全部属于 M5。

备选方案：

- 在 M4 同时实现完整 Level C 和正式 performance baseline。
- M4 完全不记录 stage timing。

选择理由：

- 功能正确性、application orchestration 与性能证据的验证风险不同，应分阶段关闭。
- 最小 per-frame timing 能验证 stage boundary wiring，但不足以支撑正式性能结论。

影响范围：

- M4/M5 task boundary、`FrameTimings`、SerialRunner、runtime JSON/Console 输出和 Gate 口径。

后续调整：

M5 可在不追溯改变 M4 functional output 的前提下引入正式 Profiler；不得把 M4 timing 重新解释为论文性能证据。

---

### D029 - M4 runtime 配置和 CLI

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M4 runtime 使用 schema version 1 的 strict YAML：全部 section/field 必填，无 implicit defaults，拒绝 unknown
field、duplicate key 和错误类型。CLI 唯一正常运行形式为 `edge_ai_infer --config <runtime.yaml>`；只允许
单独 `--help` 作为帮助形式，不提供 `-h`、positional arguments 或 YAML overrides。

备选方案：

- 为缺失字段提供默认值并允许 unknown fields。
- 同时提供大量 model/input/postprocess CLI overrides。

选择理由：

- 单一完整配置可使 smoke runs 可复查，避免 CLI/YAML precedence 和 silent typo。
- 当前只有一个 backend/input mode，无需提前建立通用配置或 override framework。

影响范围：

- RuntimeConfig/Loader、CLI parser、application exit mapping 和 runtime config tests。

后续调整：

新增 backend/runtime mode 时必须通过新 schema version 或显式兼容设计扩展，不得静默放宽 M4 strictness。

---

### D030 - M4 图片输入抽象

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M4 采用只有 `next(optional<ImageItem>*)` 的最小 `ImageSource`。`DirectorySource` 只枚举第一层真实 regular
image files，跳过 symlink，以 relative generic path byte order 确定性排序，按次解码，遇到坏图 fail-fast；不提供
reset/size，也不为 Video/Camera/RTSP/ROS2 设计提前抽象。

备选方案：

- 递归目录并跳过坏图继续运行。
- 立即设计统一 image/video/camera/stream interface 与 random access。

选择理由：

- M4 需要可复查的 deterministic finite input sequence 和明确 failure semantics。
- 最小接口足以支持 SerialRunner dependency injection，避免未实现 source types 驱动过度设计。

影响范围：

- ImageItem、ImageSource、DirectorySource、source tests 和 SerialRunner EOS/failure behavior。

后续调整：

Video/Camera/RTSP 必须在独立阶段基于真实需求新增 source implementation；不得改变 M4 DirectorySource 顺序和 fail-fast 证据。

---

### D031 - M4 串行编排

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

`SerialRunner` 严格同步单线程，只借用 ImageSource、Preprocessor、`IInferenceEngine`、PostProcessor 和
IResultSink；不拥有或构造依赖，不加载 YAML，不解析 CLI，不接触 concrete ORT type。任一 stage 首次失败立即停止，
不处理下一帧、不调用成功 `end_run()`；caller `RunSummary` 只在 sink end 成功后一次提交。

备选方案：

- Runner 直接构造/分支 `OnnxRuntimeEngine` 并管理 application configuration。
- 失败时跳过 frame 继续并返回 partial summary。

选择理由：

- interface-only dependency 保持 M2 backend boundary，并使 fake-based orchestration tests 可覆盖全部 failure paths。
- fail-fast 和 summary atomicity 避免把 partial run 表述为完整成功。

影响范围：

- SerialRunner public contract、lifetime、Status context、sink lifecycle、tests 和未来 backend composition。

后续调整：

Pipeline 或 tolerant processing policy 必须作为独立 runtime mode 设计，不得修改 M4 SerialRunner baseline 语义。

---

### D032 - M4 结果输出

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

M4 JSON 是单个运行级、固定字段顺序的 deterministic UTF-8 functional output。JsonSink 在内存缓存完整 run，
仅在 `end_run()` 通过同目录 temporary file + flush/close + POSIX atomic rename 提交；运行失败时目标文件保持不变。
CompositeSink 固定拥有 JsonSink 后 optional ConsoleSink，begin/write 正序、end 逆序，使 Console end 成功后才提交 JSON。
当前仓库无 production JSON library，因此使用固定 schema 的最小 writer，不新增大型 DOM dependency。

备选方案：

- 每图 JSON/JSON Lines 或运行中持续覆盖 final file。
- 引入 dynamic sink registry 和大型 general-purpose JSON framework。

选择理由：

- 单运行级文件能表达 metadata、ordered images 和 committed summary；atomic replacement 避免失败后留下假完整结果。
- 固定 composition order 保留 JSON final commit 作为最后成功点，同时维持实现范围最小。

影响范围：

- IResultSink lifecycle、ConsoleSink/JsonSink/CompositeSink、JSON schema、overwrite/failure tests 和 application assembly。

后续调整：

M5 可新增正式 experiment logs，但不得静默改变 M4 schema version 1 或其 atomic commit semantics。

---

### D033 - M4 Runner 模型输入合同

时间：

```text
2026-07-18
```

状态：

```text
ACTIVE
```

决策：

`SerialRunner` 在构造时显式接收已验证 `ModelContract.input.tensor_info`，并在内部保存可复制
`core::TensorInfo` 的值副本。每帧仅使用该副本调用 M1 `Preprocessor`；应用组装层必须将同一份已验证
ModelContract 同时用于 Engine initialize 与 Runner 注入。

备选方案：

- 扩展 M2 `IInferenceEngine` 以暴露输入 metadata。
- 让 Runner 重新加载 ModelContract、从 RunMetadata 推导 shape，或硬编码 640 输入。

选择理由：

- M1 Preprocessor 的公开合同需要 TensorInfo，而 M2 Engine 接口按既有边界不提供 getter。
- 外部依赖注入保持 Runner backend-neutral，避免修改 M1/M2 冻结合同，并可被未来 TensorRT backend 复用。

影响范围：

- M4.4 SerialRunner public constructor、M4.4 tests、M4.5 application composition 与未来 backend 替换。

后续调整：

不得把 TensorInfo 加入 RunMetadata 或以 shared_ptr/裸引用替代 Runner 的值副本；如需扩展模型能力，应通过
新的明确 ModelContract 与应用组装设计处理。

---

### D034 - M5 Level C Reference

时间：

```text
2026-07-19
```

状态：

```text
ACTIVE
```

决策：

M5 Level C 使用同一冻结 ONNX 上的 Python ONNX Runtime 显式 pipeline 作为 Reference。Reference 读取同一
ModelContract 和 RuntimeConfig，显式执行图片排序/读取、LetterBox、BGR→RGB、HWC→CHW、float32/255、ORT、
BCN decode、strict confidence threshold、class-aware NMS、坐标恢复和 `candidate_index` 保留。

PyTorch、Ultralytics `model.predict()`、Ultralytics hidden LetterBox/NMS/scale_boxes 和历史
`compare_pt_onnx.py` 的 shared/greedy pipeline 均不是 Level C oracle。

备选方案：

- 使用 PyTorch 或 Ultralytics 高层结果作为 C++ golden；
- 继续使用历史 PT/ORT consistency report；
- 对 M1/M2/M3 分层结果做人工拼接而不建立 E2E Reference。

选择理由：

- 同一 ONNX/ORT 隔离模型导出差异，只验证完整 image-to-detection deployment pipeline；
- 显式实现可审计每个语义边界，并复用已验证的 M1/M2/M3 参考逻辑；
- 独立稳定 JSON 支持 self-determinism 和跨语言语义比较。

影响范围：

- M5 Level C Reference、Comparator、corpus、evidence、provenance 和 Level C Gate。

后续调整：

Reference、依赖版本或任一语义变化使既有 Level C evidence 失效，必须重新评审和执行 Gate。

---

### D035 - M5 Level C Detection Matching

时间：

```text
2026-07-19
```

状态：

```text
ACTIVE
```

决策：

Python/C++ Detection 按 `class_id` 分组，以 confidence absolute error `<=1e-4` 且 bbox 任一坐标 absolute error
`<=0.01 pixel` 建立兼容边，每类使用确定性的最大二分匹配并要求完整一对一 matching。输出顺序和
`candidate_index` 不作为跨语言 PASS 条件；`candidate_index` 保留用于诊断。16 张图片必须全部 PASS。

备选方案：

- 按输出下标或 confidence 排序后逐项比较；
- IoU 最近或兼容边 greedy matching；
- 只比较 count、平均误差或通过率。

选择理由：

- 多个相近 Detection 可能存在多条兼容边，greedy 会产生假失败；
- 最大匹配验证是否存在完整容差内一对一对应，不依赖实现输出顺序；
- 冻结逐项容差和全量 PASS 防止平均值掩盖个别错误。

影响范围：

- M5 Comparator、反例测试、comparison report、tolerance 和 Level C Gate。

后续调整：

matching 或 tolerance 变化必须人工决定并使旧 Level C/benchmark evidence 失效，不得为通过而自动放宽。

---

### D036 - M5 Benchmark Instrumentation

时间：

```text
2026-07-19
```

状态：

```text
ACTIVE
```

决策：

M5 使用真实 Release `edge_ai_defect`，复用 M4 `FrameTimings` 和 JsonSink；pilot、warmup、重复 regular-file
workload、进程编排、CPU affinity、统计、压缩和 provenance 由离线 Python 工具完成。不新增 C++ Profiler、
`--benchmark`、RuntimeConfig benchmark mode，也不修改 SerialRunner、FrameTimings 或 production JSON schema。

备选方案：

- 在 C++ 引入正式 Profiler/benchmark mode；
- 通过 RuntimeConfig 或 CLI 增加 warmup/measured/run 参数；
- 使用外部 wall clock 代替已有阶段 timing。

选择理由：

- M4 已提供完整且可序列化的 stage boundary；离线工具足以执行严格统计并保持 production 合同冻结；
- 真实 executable 覆盖实际 source/preprocess/ORT/postprocess 路径，避免建立第二条 benchmark-only runtime。

影响范围：

- M5 benchmark harness、RuntimeConfig 使用方式、evidence schema 和 performance Gate。

后续调整：

未来 Jetson/Pipeline 若确需新 instrumentation，必须在独立阶段设计，不追溯改变 M5 WSL baseline。

---

### D037 - M5 ORT CPU Baseline 定位

时间：

```text
2026-07-19
```

状态：

```text
ACTIVE
```

决策：

M5 正式性能结果名称为 **WSL2 x86_64 ONNX Runtime CPU Engineering Baseline**。它用于记录当前环境、冻结
single-thread ORT 配置和 C++ Serial pipeline 的工程测量，不是 Jetson baseline、TensorRT baseline、最终部署硬件
性能或论文同硬件 backend speedup。

备选方案：

- 不采集本地 baseline；
- 将 WSL CPU 数字与未来 Jetson TensorRT 数字直接比较；
- 把 M5 表述为最终论文性能实验。

选择理由：

- 当前 WSL2 环境可稳定验证工具、measurement protocol 和 C++ CPU baseline；
- 跨设备、CPU/GPU、系统和电源策略的数字不能形成有效加速比；
- 未来论文 backend comparison 仍需在同一 Jetson 平台采集。

影响范围：

- M5 evidence 命名、报告措辞、EXPERIMENT_PLAN、论文引用边界和后续 Jetson/TensorRT 计划。

后续调整：

定位不可由结果好坏改变。Jetson 数据必须作为独立 evidence 和阶段产生。

---

### D038 - M5 Evidence、Retention 和失效

时间：

```text
2026-07-19
```

状态：

```text
ACTIVE
```

决策：

正式 M5 evidence 仅在 clean committed source HEAD 生成，使用 `YYYYMMDD_<short_source_git_commit>` 标识，保存
原始样本、统计、commands、exit codes 和完整 provenance。Level C 保留未压缩原始 JSON；benchmark 保留固定压缩级别、
mtime=0 的 deterministic gzip raw application JSON，以及可追溯的 `timings.tsv`、per-run/aggregate summary。
单个 evidence set tracked 上限为 25 MiB，超过时停止并人工决定，不自行删减。

关键模型/合同/config/corpus/图片、Reference/Comparator/production、ORT/OpenCV、tolerance/matching 变化使 Level C
evidence 失效；Release flags、FrameTimings、benchmark corpus、pilot/warmup/measured/run/wait/affinity、percentile、
outlier 或 retention 变化还使 benchmark evidence 失效。无关 documentation-only 修改不强制重跑。

备选方案：

- 只保留 summary 或手工表格；
- 保留全部未压缩 benchmark JSON；
- 不记录失效条件，持续覆盖同一路径。

选择理由：

- 原始样本允许独立重建统计并审查 warmup/outlier；
- deterministic compression 控制体积且保留完整数据；
- 明确 source commit 和失效边界防止旧 evidence 被误用于变化后的实现或协议。

影响范围：

- `results/validation/level_c/`、`results/benchmark/ort_cpu/`、所有 M5 tools、Gate 和 closeout。

后续调整：

Retention 或失效规则变化属于新决策，并使受影响的正式 baseline evidence 失效。

---

### D039 - M5 NEU-DET 资产策略

时间：

```text
2026-07-19
```

状态：

```text
ACTIVE
```

决策：

在未确认明确再分发许可的情况下，不将 NEU-DET 原图或基于其生成的派生图提交 Git。仓库只跟踪 corpus manifest、
文件名、split、expected SHA256、GT 类别、选择理由、导入/SHA 工具和派生规则。正式运行由用户通过
`--dataset-root <path>` 提供本地合法数据，工具 fail-fast 验证 regular file、split 和 SHA；不联网下载或使用硬编码
个人绝对路径。

备选方案：

- 将 12/20 张 JPG 和 derived BMP 直接提交 Git；
- 自动从网络或第三方镜像下载；
- 只记录文件名，不记录 SHA 或来源。

选择理由：

- 当前仓库没有 tracked NEU-DET 图片、dataset archive 或明确再分发许可；
- manifest+SHA 可验证 corpus 身份和顺序，同时避免未经确认的再分发；
- 显式本地 root 使工具可移植且不会依赖某台机器目录。

影响范围：

- M5 corpus manifests、preparation tool、derived images、provenance、Level C/benchmark evidence 和复现说明。

后续调整：

若取得明确许可或官方可归档来源，可新增决策调整分发策略；不得静默提交图片或虚构许可状态。

---

### D040 - M5 Evidence Consolidation Contract

时间：

```text
2026-07-19
```

状态：

```text
Accepted
```

Context：

M5.5 首次能力预审确认原计划只定义了目标、检查范围、提交信息和下一阶段，未冻结 consolidation 持久化目录、
文件集合、machine-readable schema、human-readable summary 或 `sha256sums` 规则。因此预审在修改任何文件前
停止；该问题分类为 `M5.5 evidence consolidation planning gap`，不是 M5.5 执行失败。此次 remediation 不运行
application/benchmark、不重建 Evidence、不修改正式 Level C/benchmark Evidence。

Decision：

- 正式路径固定为 `results/consolidation/m5/<evidence_id>/`；Evidence ID 为 `YYYYMMDD_<short_source_commit>`，
  每个完整 source commit 只允许一套 consolidation。
- 目录固定恰好包含 `README.txt`、`evidence_index.json`、`verification_report.json`、`provenance.json`、
  `commands.txt` 和 `sha256sums.txt` 六个文件。
- 三份 JSON 使用 schema version 1；README 是 human-readable summary；机器可读文件只引用现有 Evidence，不复制
  raw/gzip/TSV/图片/模型/binary。
- `sha256sums.txt` 按字节序索引其他五个文件并排除自身；发布采用 staging 完整验证后单次 rename。
- D038 的 25 MiB retention 统一上限为 `26214400` bytes；输入 Evidence 或合同变化时 consolidation 失效，必须
  完整重新生成，不得手工 patch。
- M5.6 直接验证 consolidation 及底层 Evidence；consolidation PASS 不等于 M5.6 Gate PASS，也不等于 M5 CLOSED。

Alternatives rejected：

- 将 consolidation 放入 validation 或 benchmark 单侧目录；
- 只修改阶段文档而不提供稳定 machine-readable index；
- 复制两套正式 Evidence；
- 使用随机 ID、秒级时间或个人路径；
- 让 M5.6 只信任 consolidation 而不检查底层 Evidence。

Consequences：

增加一个小型、稳定、可审计的跨 Evidence 索引，避免大体积重复数据，并为 M5.6 提供明确入口；任何底层 Evidence
变化都会使该 consolidation 失效。M5.5 Planning Freeze Remediation 完成后，必须从新的 clean committed HEAD
重新计算未来 consolidation 的 Evidence ID。

Clarification（M5.5 Consolidation Evidence Remediation Planning Freeze，2026-07-19）：

- `provenance.json` 中的 `branch`、`upstream`、`behind`、`ahead` 和
  `worktree_clean_before_generation` 固定表示 consolidation 生成开始前采集的 generation-time Git snapshot；提交后
  不因后续 push、upstream 变化或新 commit 回填。M5.6 审计单独记录 current Git facts，Gate 不要求历史 `ahead` 与审计时
  `ahead` 相等。Stable regeneration 使用 source commit 和冻结的 generation snapshot，不重新查询动态 Git 状态、时间、
  hostname、临时目录或当前 HEAD/upstream。
- 第一次 M5.6 Deep Evidence Gate 的唯一 blocker 是 consolidation provenance completeness：旧
  `20260719_c24eefa` 的 `command_records` 只有 6 条聚合记录，而合同要求 15 个独立阶段；Level C、Benchmark、重建、
  model/contract、corpus、privacy、retention 和 CTest 均保持 PASS。该问题不是 production、Reference、Comparator、
  Benchmark 结果、统计或底层 Evidence 损坏，不需要重跑正式 benchmark。
- 旧 `results/consolidation/m5/20260719_c24eefa/` 保留为 `historical_invalidated_consolidation`，不修改、不删除、不
  重算其 SHA，不作为下一次 M5.6 的 active Consolidation；失效状态只由阶段文档记录，旧 Evidence 内不增加标记文件或
  字段。
- 本次提交只冻结 remediation contract。提交后先形成新的 clean committed HEAD，再以该新 source commit 重新计算
  Evidence ID 并生成新的完整六文件 consolidation；不复用或覆盖旧目录，不产生新的检测或性能样本。
- 新 provenance 必须按固定顺序恰好包含 15 条唯一 `command_records`：
  `git_preflight`、`git_ancestry`、`level_c_sha`、`benchmark_sha`、`gzip_validation`、
  `timings_tsv_rebuild`、`per_run_summary_rebuild`、`aggregate_summary_rebuild`、
  `model_contract_consistency`、`corpus_consistency`、`privacy_scan`、`asset_scan`、
  `retention_check`、`stable_regeneration`、`consolidation_sha`。每条记录必须包含实际执行的 command、phase、
  working directory、exit code 和 result，不得合并阶段或记录 application/Pilot/formal run/benchmark 命令。
- 新 `commands.txt` 与 15 条 `command_records` 一对一：恰好 15 个编号段，顺序、ID、phase、command、working directory、
  exit code 和 result 完全一致，且只使用 repo-relative 检查命令。
- Stable regeneration 必须在 staging A/B 使用完全相同的冻结输入生成并比较六文件；五个内容文件和
  `sha256sums.txt` 必须 byte-identical，随后才可原子发布。新 consolidation 完成前，M5.5 remediation generation、M5.6
  Gate rerun 和 M5.7 均保持 PENDING；不得 patch 历史 consolidation。

### D041 - Freeze Stage J Jetson ONNX Runtime CPU Baseline Route

时间：

```text
2026-07-21
```

状态：

```text
Accepted
```

Context：

M0～M5 C++ ONNX Runtime CPU Serial Baseline 已完成并关闭，当前已有 WSL2 x86_64 正确性验证和工程基线。下一步需要在同一目标 Jetson 上建立可信的 ONNX Runtime CPU baseline，作为后续 Stage T TensorRT FP16 同设备比较的参考。WSL 与 Jetson 只做环境差异描述，不计算正式 speedup。

本决策依据冻结计划 [`docs/personal/STAGE_J_EXECUTION_PLAN.md`](STAGE_J_EXECUTION_PLAN.md)：

- Plan version：`Stage J Plan v0.3`
- Document status：`FROZEN`
- Plan SHA256：`a723ae1ffae70366c7435313869f5a2ec1318c47ed43398ffdfcf40e8ba6a9bd`

Decision：

#### A. 阶段分离

冻结阶段关系：

- Stage J：Jetson ONNX Runtime CPU Baselines；
- Stage T：TensorRT FP16；
- Stage P：Pipeline / System Optimization；
- Stage R：Research Extension。

Stage J 不实现 TensorRT、CUDA EP、TensorRT EP、FP16、INT8、PipelineRunner、ROS2、Qt、摄像头、RTSP、PLC，也不引入通用插件或通用 Factory 系统。

#### B. 目标平台合同

Stage J 的 planned target 为 Jetson Orin Nano Super Developer Kit、8GB、256GB NVMe、JetPack 6.2.2、Jetson Linux / L4T 36.5、Ubuntu 22.04-based root filesystem、aarch64、MAXN_SUPER、主动风扇和 Jetson 原生构建。

以上是 planned target，不是 J0 已验证的 observed facts。所有设备事实必须在 J1 采集并冻结，包括实际 thermal zone、CPU frequency sysfs、MAXN_SUPER mode ID、OC/UV counter、sustained throttling 目标频率、tegrastats rail、allowed/online CPU set 以及 Jetson 工具链版本。

#### C. ONNX Runtime 合同

冻结使用官方 ONNX Runtime 1.23.2 source，在 Jetson 上进行原生 aarch64 Release shared-library 构建，仅使用 CPUExecutionProvider、FP32，且不做交叉编译。禁止 CUDA EP、TensorRT EP、XNNPACK、ACL/ArmNN、OpenMP、minimal build、reduced operator config、training、custom ops、LTO 和人为 `-march=native`。

#### D. 继承的推理语义

Stage J 不重新定义 Frozen ONNX 和 SHA、ModelContract、HostTensor、Preprocessor / LetterBox、PostProcessor / NMS、Detection、IInferenceEngine、SerialRunner 的处理顺序、Level A/B/C Reference 和容差、以及 class-aware maximum bipartite matching。原则上不修改这些公共合同。

#### E. RuntimeConfig v2 与 Protocol 分离

RuntimeConfig v2 只管理进程内部软件配置；StageJRunProtocol 管理实验执行条件、CPU set、thermal、telemetry、campaign 和 Evidence。schema v1 保留历史兼容路径；v1 与 v2 字段禁止混用；launcher 不得绕过 RuntimeConfig 修改 Engine 私有状态；正式协议开始后 Resolved Protocol SHA 不得变化。

#### F. ORT 配置证据模型

冻结 `requested options`、`applied options`、`queried options` 三层证据。`applied` 只能由 Engine 实际成功调用 ORT API 后记录，不得由调用方复制 requested 值；`queried` 仅用于 ORT 1.23.2 真正支持独立查询的字段；不可查询字段以成功的配置 API 调用作为应用证据。不得宣称所有 SessionOptions 均已完成独立运行时回读。

#### G. CPU Profile

冻结两套正式 CPU baseline 角色：Controlled 1-Core Application Profile 和 Tuned k-Core Application Profile。

Controlled 固定为 ORT sequential、`intra=1`、`inter=1`、OpenCV threads=1、spinning enabled 和固定单核 affinity。

Tuned 候选为 `unique({1, 2, 4, non_cpu0_count, all_allowed_cpu_count})`，并固定 `intra_op_threads = k`、`inter_op_threads = 1`、ORT sequential、OpenCV threads=1 和 spinning enabled。不得将 `inter_op_threads` 设为 `k`，不得切换 ORT parallel mode。

Tuned 结论只能限定为当前模型、20 图 workload、当前 JetPack、ORT build、MAXN_SUPER 和预注册候选集合中的最优 Profile，不得声称普遍最优线程数。

#### H. 正确性 Gate

冻结 J4 Level A/B/C、J5 20 图 Python Reference，以及每个 Candidate Profile 的两次 separate-process semantic precheck。每个 precheck 进程重新创建 ORT Session 且只执行一个完整 20 图 cycle；不同 Profile 不要求 byte-identical，但每个 Profile 必须分别与 Python Reference 在冻结容差内语义一致；性能 run 的每个完整 cycle SHA 必须匹配该 Profile 的 expected SHA。

#### I. Benchmark 和稳定性

Selection Campaign 使用完整平衡 rotation；正式 Controlled/Tuned baseline 各执行五次 separate-process repetitions；每次正式 measured window 至少 30 秒；任一正式 run 无效则整套五次重跑；不删除 outlier。J6 只验证 Tuned Profile，持续运行至少 30 分钟。Controlled 1-Core 不做独立 30 分钟稳定性测试，除非新增 Decision。

#### J. 实验控制

冻结 MAXN_SUPER、`jetson_clocks --fan`、Thermal Gate、application affinity、telemetry affinity、TID 生命周期采样、tegrastats、rail telemetry、OC/UV counter Gate、monotonic Frame Trace 和 telemetry coverage Gate。实际设备路径、rail 名称、mode ID 和目标频率在 J1 冻结，不得在 J0 猜测。

#### K. Evidence

冻结 local attempt 与 published Evidence 分离；published Evidence 只能来自一个完整 PASS attempt 或 campaign，禁止拼接、patch 或覆盖历史 Evidence。J7 负责 Consolidation，J8 负责只读独立重建审计，J9 仅进行文档收尾。Stage J tracked Evidence 总预算不超过 25 MiB。`sha256sums.txt` 不包含自身，输入按 repo-relative UTF-8 path byte order 排序，输出使用固定 `<sha256><two spaces><relative_path>` 格式和 LF 行尾，不允许绝对路径或动态元数据影响 byte-identical 重建。

选择理由：

1. ORT CPU baseline 与 TensorRT FP16 必须在同一 Jetson、相同模型、corpus、功耗和 Trace 定义下比较；
2. WSL x86 与 Jetson aarch64 不适合计算正式 speedup；
3. 先完成 CPU baseline 可以隔离平台迁移、跨架构正确性和 TensorRT 优化变量；
4. Controlled 与 Tuned 两套 Profile 分别提供受控参考和当前 workload 下的实用 CPU 性能；
5. RuntimeConfig 与 Run Protocol 分离可以避免实验编排层绕过应用合同；
6. 严格 Evidence 和 Deep Gate 用于防止部分重跑、证据拼接和结论污染；
7. Stage J 不提前引入 TensorRT/Pipeline，可避免同时改变多个关键变量。

影响范围：

- Stage J 开始前必须先完成 J0；
- Stage J implementation branch 尚未创建；
- production 代码修改尚未开始；
- J1 前不得将 planned target 写成 observed fact；
- RuntimeConfig v2 必须保持 v1 兼容；
- 当前 `IInferenceEngine` 不因 Stage J 扩展；
- 后续 Stage T 必须继承 Stage J 的 trace 和统计语义；
- Stage J 不产生 TensorRT、Pipeline 或最终 Jetson 性能结论；
- WSL M5 Evidence 不回写、不改名、不重算。

风险与限制：

- Jetson 尚未到货；
- JetPack/L4T/MAXN_SUPER 实际状态未验证；
- ORT 1.23.2 aarch64 build command 尚需在 J2 基于真实 `build.sh --help` 冻结；
- 多线程 Profile 可能产生可容忍的浮点差异；
- telemetry 与 all-core candidate 可能在 CPU0 上重叠；
- thermal zone、frequency、OC/UV 和 rail 路径依赖设备事实；
- 严格 campaign invalidation 可能增加实机重复运行成本；
- Stage J 只能证明 30 分钟受控持续运行，不能证明生产长期稳定性。

替代方案及拒绝理由：

- 在 WSL 上直接交叉编译 Jetson binary：拒绝，因为 Stage J 要求目标设备原生构建；
- 使用非目标设备上的 TensorRT 代替 Jetson TensorRT：拒绝，因为这不构成同设备参考；
- Stage J 同时实现 TensorRT 和 Pipeline：拒绝，因为会同时改变多个关键变量；
- 只测试单一 ORT 线程数：拒绝，因为无法形成 Controlled 与 Tuned 两种角色；
- 将 all-core 或某个 k 直接预设为最优：拒绝，因为 Profile 必须经过预注册候选和选择协议；
- 使用 WSL 与 Jetson 计算正式 speedup：拒绝，因为跨设备结果不可作正式加速比；
- 使用一个进程内两个 cycle 替代 separate-process semantic precheck：拒绝，因为无法覆盖进程级 Session 重建边界；
- 允许局部补跑后拼接正式 campaign：拒绝，因为会破坏 campaign 完整性；
- 将不可查询的 SessionOptions 伪装成 queried actual values：拒绝，因为会污染配置证据语义。

后续调整：

Stage J 范围、RuntimeConfig 与 Protocol 权威关系、J4/J5 语义 Gate、Profile 选择规则、Thermal/Telemetry 合同、Evidence 和 Deep Gate 边界的变化，必须通过新的 Decision 记录，并重新评估受影响 Gate。当前设备事实、ORT 实际 build command 和目标频率不在本 Decision 中预先编造。

### D042 - Freeze Stage J Jetson Telemetry and Throttling Contract

时间：

```text
2026-07-22
```

状态：

```text
Accepted
```

Context：

J1.4 Phase A 已完成 thermal、frequency、EMC、tegrastats、rail、OC/UV
和 environment-drift discovery。原始 Phase A attempt 未包含全部 OC/UV 与
INA3221 字段；根据用户明确的 J1 discovery 工程协议裁决，J1 discovery
允许使用多个独立、不可变、repository-external raw attempt 组成 composite
evidence。本裁决不改变 J5/J6 formal benchmark/stability campaign 的连续性、
不可拼接和不可删除要求。

Evidence provenance：

1. Phase A discovery raw SHA256：
   `91eb86daebd31a96e6ddc74b9beda89c7aa466e7d74f0da53a0ea291689f99a0`
   覆盖 thermal zones、30 秒 thermal/frequency sampling、CPU/GPU/EMC
   sources、tegrastats、rail-name set、environment-drift candidates 和
   sustained-throttling candidate。
2. Supplemental OC/UV/INA3221 raw SHA256：
   `75cb07a6149b6b69b3774397ee58bd754743aa7df9181f86d9749833d17732a5`
   覆盖 hwmon identity/realpath、OC1/2/3 counters、throttle-enable fields、
   INA3221 labels 和实际 alarm paths/values。

两个 raw attempt 均 repository-external、untracked、immutable 且未作为
Published Evidence。旧 Phase A raw 未被修改或覆盖；J1.4 composite discovery
evidence v1 不伪装为单一 raw attempt。中间未通过 provenance/字段完整性 Gate
的 supplemental attempts 不属于 composite evidence。

Observed platform facts：

- Device：Jetson Orin Nano Engineering Reference Developer Kit Super，
  `aarch64`，Tegra234。
- Power mode：`MAXN_SUPER` / ID `2`；CPU online `0-5`。
- CPU policies：policy0 CPUs `0-3`，policy4 CPUs `4-5`；driver `tegra194`，
  governor `schedutil`；target/min/max `1728000 kHz`。
- GPU devfreq：
  `/sys/devices/platform/bus@0/17000000.gpu/devfreq/17000000.gpu`；
  target/min/max `1020000000 Hz`，governor `nvhost_podgov`。
- EMC configuration/cap source：`/sys/kernel/nvpmodel_clk_cap/emc`，
  target `3199000000 Hz`；`jetson_clocks --show` reports current/max
  `3199000000` and `FreqOverride=1`。
- Fan：PWM `255`，dynamic speed control disabled；nvfancontrol inactive
  after `jetson_clocks --fan`。

Thermal contract：

- Raw unit is milli-degree Celsius; gates use raw integer values and display
  conversion is `raw / 1000.0`.
- Required readable relevant set is exactly:
  `cpu-thermal` (`thermal_zone0`), `gpu-thermal` (`thermal_zone1`),
  `soc0-thermal` (`thermal_zone5`), `soc1-thermal` (`thermal_zone6`),
  `soc2-thermal` (`thermal_zone7`) and `tj-thermal` (`thermal_zone8`).
- `cv0-thermal`, `cv1-thermal` and `cv2-thermal` at `thermal_zone2-4` are
  inventory members but stably return `EAGAIN`; they are excluded from the
  numeric hard maximum, never converted to zero, and any future stable value
  requires relevant-set review.
- Each formal sample takes the maximum of the readable relevant set. A read
  failure in any required zone invalidates that sample; no forward fill or
  interpolation is allowed.
- Any required zone at or above its lowest passive trip is a hard
  thermal-throttling failure; critical trip is an immediate hard failure.
  Active trips alone do not define throttling; frequency Gate is independent.
- Formal `T_idle_ref` remains a later protocol operation: 5-minute idle,
  60 one-second maxima, median reference, 30-second pre-run wait,
  `T_idle_ref + 2°C` and 10-second range `<= 1°C`, timeout 600 seconds.
  J1.4 did not establish a formal reference.

Frequency and EMC authority：

- CPU runtime sources are policy0/policy4 `scaling_cur_freq`; downward
  deviation means observed value below `1728000 kHz`.
- GPU runtime source is the discovered devfreq `cur_freq`; downward
  deviation means observed value below `1020000000 Hz`.
- EMC cap and `jetson_clocks --show` current/max/`FreqOverride` are
  preflight/postflight authority only. No independent reliable ordinary-user
  1 Hz EMC runtime source was found, and tegrastats does not report EMC
  frequency. EMC therefore does not enter the 1 Hz sustained sequence.
- Formal start/end EMC Gate requires cap/current/max `3199000000` and
  `FreqOverride=1`; mismatch is environment-drift hard failure.

tegrastats and rail contract：

- Executable: `/usr/bin/tegrastats`; package `nvidia-l4t-tools`
  `36.5.0-20260115194252`; interval `1000 ms`.
- Formal lines carry UTC and `CLOCK_MONOTONIC ns`; gap `>2500 ms` invalidates
  the run; telemetry coverage must be at least `0.90` and sample count must
  satisfy the formal protocol.
- Rail-name set is exactly `VDD_IN`, `VDD_CPU_GPU_CV`, `VDD_SOC`.
- Rail telemetry is onboard rail telemetry, not wall power, PSU input power,
  precision energy measurement or calibrated external power-meter data.
- For `current_power / average_power`, both values are retained. The first
  value in mW is used for arithmetic mean, time-weighted linear mean, min,
  max, Type-7 P50/P95 and count. The second device-emitted value is diagnostic
  only and is not averaged or used for precise energy integration.

OC/UV and INA3221 hard Gate：

- `soctherm_oc` realpath is
  `/sys/devices/platform/soctherm-oc-event/hwmon/hwmon3`.
- OC1 Under Voltage:
  `/sys/class/hwmon/hwmon3/oc1_event_cnt`, current `0`,
  `/sys/class/hwmon/hwmon3/oc1_throt_en`, current `1`.
- OC2 Average Overcurrent:
  `/sys/class/hwmon/hwmon3/oc2_event_cnt`, current `0`,
  `/sys/class/hwmon/hwmon3/oc2_throt_en`, current `1`.
- OC3 Instantaneous Overcurrent:
  `/sys/class/hwmon/hwmon3/oc3_event_cnt`, current `0`,
  `/sys/class/hwmon/hwmon3/oc3_throt_en`, current `1`.
- Counters are cumulative; they are not cleared before a run. Each attempt
  records start/end and compares deltas. Any positive delta is a hard failure;
  reboot requires a new baseline. dmesg is diagnostic only.
- INA3221 realpath is
  `/sys/devices/platform/bus@0/c240000.i2c/i2c-1/1-0040/hwmon/hwmon1`.
  Labels are `in1_label=VDD_IN`, `in2_label=VDD_CPU_GPU_CV`,
  `in3_label=VDD_SOC`, plus `in7_label=sum of shunt voltages`.
  Observed current-alarm paths are `curr1/2/3_crit_alarm`,
  `curr1/2/3_max_alarm` and `curr4_crit_alarm`; all observed values are `0`.
  Formal telemetry samples every alarm field at 1 second; any non-zero value
  is a hard failure.

Stage J Sustained Throttling Algorithm v1：

- Sample every 1 second with `CLOCK_MONOTONIC ns`.
- Monitor CPU policy0/policy4 `scaling_cur_freq` and GPU `cur_freq`.
- A downward-deviation sample is `observed < target`.
- Three consecutive valid one-second downward samples for the same source are
  a sustained-throttling event and hard-fail the current run/campaign.
- One or two consecutive samples are warnings unless an OC/UV counter delta or
  alarm occurs, which is a hard failure.
- Upward values, configuration mismatch, CPU-set changes, mode changes,
  EMC Gate mismatch or fan-state mismatch are environment-drift hard failures.
- Gap `>2500 ms`, coverage `<0.90`, insufficient samples or required-source
  read failure invalidates the run; no fill or interpolation.
- Thermal and frequency Gates are independent and both are recorded when
  simultaneous. EMC is excluded from the 1 Hz sequence.
- With all allowed CPUs, telemetry is pinned to CPU0; CPU0 overlap with the
  application is recorded as an interference limitation.

Environment-drift contract：

Hard-match fields are kernel release, `/etc/nv_tegra_release` SHA256,
`nvidia-l4t-core` version, active nvpmodel config path/SHA256, mode name/ID,
CPU present/possible/online/allowed sets, policy paths/mappings and targets,
GPU path and targets, EMC cap/show/FreqOverride, fan PWM/control state,
thermal type/path sets, tegrastats path/package version, rail-name set,
OC/UV paths and enable values, and wrapper SHA256 values. Attempt preflight
mismatch prevents startup; in-run mismatch invalidates the run and is never
silently repaired. Boot ID is recorded per resolved attempt; reboot invalidates
the reference and requires new preflight, thermal reference and protocol.

Rationale and consequences：

This Decision converts J1 observed telemetry facts into explicit formal Gates,
separates EMC cap from runtime measurement, preserves INA3221/onboard rail
limitations, and makes OC/UV counter deltas auditable. It does not validate
workload throttling, establish `T_idle_ref`, change system state, or authorize
J1.5 by itself. J5/J6 formal runs remain single continuous attempts with no
post-hoc telemetry patching, deletion or evidence splicing.

### D043 - Freeze Stage J1.5 Published Evidence Contract

时间：

```text
2026-07-22
```

状态：

```text
Accepted
```

Purpose：

本 Decision 定义 J1.5 Platform Evidence Gate 的 Published Evidence artifact
contract，补全 evidence root、required files、machine-readable schema、manifest
和 privacy/redaction 规则。D043 不执行 J1.5，不授权 J2，也不改变 D041 或 D042。

Evidence root：

```text
results/platform/jetson/environment/j1_baseline_v1/
```

Required files：

```text
README.md
PLATFORM_ACCEPTANCE.md
TOOLCHAIN_INVENTORY.md
POWER_CLOCK_ACCEPTANCE.md
TELEMETRY_CONTRACT.md
EVIDENCE_PROVENANCE.md
environment_snapshot.yaml
sha256sums.txt
```

Published Evidence must contain exactly the required artifact set above. It is
tracked, sanitized and derived from reviewed local evidence; local raw evidence
remains external, untracked and immutable preservation, and is not Published
Evidence.

Manifest contract：

`sha256sums.txt` excludes itself, contains only Published Evidence-root-relative
paths, sorts paths by UTF-8 byte order, uses deterministic formatting and LF
line endings, and contains no absolute path, directory entry or duplicate path.
Each line uses:

```text
<sha256><two spaces><relative-path>
```

The manifest must be validated with `sha256sum -c sha256sums.txt` from the
Published Evidence root. The local evidence manifest must not be copied as the
Published Evidence manifest.

`environment_snapshot.yaml` contract：

```yaml
schema_version: 1
```

The top-level schema must contain these required sections:

```text
device
software
toolchain
power
clock
fan
thermal
telemetry
evidence_provenance
```

Observed, planned, missing and null meanings must remain distinct. Formatting
is UTF-8, LF and deterministic; no YAML anchors, aliases or environment
variable expansion are allowed.

Privacy and redaction：

Published Evidence must not contain serial numbers, MAC addresses, IP
addresses, UUID/PARTUUID values, passwords, tokens, credentials, sudoers
content or private-key paths. It must not contain `/home/orin`,
`/tmp/edge-ai-j1*` or `raw_output.txt`. Logical evidence labels, basenames,
booleans, package versions and SHA256 values are allowed where they do not
reveal a prohibited identifier.

Evidence source rules：

- Local raw evidence: repository-external, untracked and immutable preservation;
  it is not Published Evidence.
- Published Evidence: tracked, sanitized and derived; it must never directly
  copy unreviewed raw output.
- Raw evidence absolute local paths are not portable Published Evidence
  locators; provenance uses logical evidence IDs and relative preservation
  labels.

Size and validation：

- Total tracked Evidence under this contract is `<=25 MiB`.
- All files are UTF-8 with LF line endings.
- File ordering and manifest generation are deterministic.
- Validation must check the exact file set, parser validity, line endings,
  privacy scan, no absolute local paths, no raw files, no duplicate evidence,
  total size and manifest checksums before J1.5 can pass.

Consequences：

D043 supplies the missing J1.5 contract but does not create the evidence
directory or any results files. J1.5 must use only this exact root and file set,
must preserve the distinction between local raw evidence and derived tracked
evidence, and must remain blocked if any required artifact or schema validation
is unavailable. J1.5 remains a separate gate; J1 and Stage J are not completed
by this Decision alone.

### D044 - Freeze J2 Formal Build Remediation and SDK Packaging Contract

时间：2026-07-23T19:30:42+08:00

状态：`Accepted`

D044 only completes the execution, artifact, provenance and evidence contract
for the existing J2.2 formal build remediation and J2.3 SDK packaging work. It
does not change the Stage J scope, ORT version, CPU-only contract, J2 task
numbering, J2.4 RPATH Gate, J2.5 Evidence Gate or J3 task boundary. J3.0 is not
a task in the frozen sequence.

#### Historical J2.2 attempt disposition

The existing external SDK is technically valid for the facts already audited:
the main and providers-shared library hashes match the recorded values, the
payload is AArch64 ELF64, the SONAME and symlink chain are valid, CUDA/TensorRT
dependencies are absent, and the CMake package uses `_IMPORT_PREFIX`.

The existing external build and SDK artifacts, failed-build directory and raw
logs must not be deleted, modified or overwritten. The historical successful
build is classified as:

`development_build_valid_artifact_not_formal_published_evidence`

The historical attempt cannot independently satisfy the complete frozen J2.2
provenance Gate because the source tree is no longer available for independent
verification, the successful build has no independent exit-code record and the
local attempt/staging manifest is incomplete. This disposition does not mean
that the SDK is corrupt or that the historical technical build failed.

The historical J2.2 attempt disposition is `SUPERSEDED`. `SUPERSEDED` means it
is not the sole authoritative source for future formal J2.2 Published Evidence;
it does not invalidate its already observed technical artifact facts.

#### Frozen J2 status correction

- J2.2: `IN_PROGRESS` pending formal remediation PASS.
- J2.3: `BLOCKED` pending formal J2.2 remediation PASS.
- J2.4: `PENDING`.
- J2.5: `PENDING`.
- J2 overall: `IN PROGRESS`.
- J3: `BLOCKED_BY_J2.5`.
- J3.0: `NOT_DEFINED`.

Historical status entries are retained for audit history and are not silently
rewritten. The live status is corrected by the current task record.

#### J2 local attempt contract

The repository-external local attempt root is:

`/home/orin/edge-ai-local-evidence/stage_j/j2_attempts/`

Each attempt uses an immutable, non-overwriting directory named
`<task_id>_<semantic_name>_v<integer>`. The first formal remediation attempt is
`j2.2_formal_clean_v1`. A failed attempt is retained intact and the next attempt
increments the version; no attempt directory may be reused or overwritten.

Each formal attempt must contain exactly these required files:

```text
README.txt
commands.txt
stdout.log
stderr.log
exit_codes.tsv
timestamps.tsv
environment.txt
source_provenance.txt
build_configuration.txt
artifact_inventory.txt
sha256sums.txt
```

`tegrastats.log` is optional and may exist only when telemetry is actually
collected. Command logs must record executed commands in order and must never
present planned commands as executed commands. stdout/stderr must preserve raw
command boundaries without post-hoc deletion or concatenation across attempts.

`exit_codes.tsv` uses the fixed columns `sequence`, `command_id` and
`exit_code`, and records source acquisition, source verification, submodule
preparation, configure/build, install/staging, artifact verification and local
manifest verification. `timestamps.tsv` uses `event`, `iso8601_local` and
`monotonic_ns`, and records attempt start, source ready, build start/end,
install start/end, verification end and attempt end.

The remaining attempt files record, respectively, the attempt identity and
disposition; execution environment; official source URL, exact tag/commit,
VERSION_NUMBER, clean status, submodules and source inventory; the exact
build.sh command and CPU-only cache/flag facts; and the complete artifact,
ELF, dependency, header, package, license and notice inventory.

The attempt-local `sha256sums.txt` excludes itself, uses attempt-root-relative
paths, UTF-8 byte-order sorting, two spaces between hash and path, LF line
endings, and covers every regular file. Symlinks are recorded separately in
`artifact_inventory.txt`. `sha256sum -c` must pass for every entry.

#### J2.2 formal remediation paths

The first formal remediation uses new, previously nonexistent roots and does
not reuse or remove historical artifacts:

```text
Source: /home/orin/edge-ai-local-build/j2.2-formal-v1/source/
Build: /home/orin/edge-ai-local-build/j2.2-formal-v1/build/
Installed SDK: /home/orin/edge-ai-local-build/j2.2-formal-v1/sdk/
Local attempt: /home/orin/edge-ai-local-evidence/stage_j/j2_attempts/j2.2_formal_clean_v1/
```

The source must come from the official ONNX Runtime repository, tag `v1.23.2`,
commit `a83fc4d58cb48eb68890dd689f94f28288cf2278`, with a clean tree, complete
recursive submodules and `VERSION_NUMBER=1.23.2`.

#### J2.2 formal build contract

The formal build is native AArch64, Release, shared-library, CPU
ExecutionProvider, upstream tests skipped and parallelism four. It uses the
external CMake 3.28.6 binary at
`/home/orin/edge-ai-local-build/cmake-3.28/bin/cmake`; the archive SHA256 must
be `7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7`.

Before execution, the actual v1.23.2 `build.sh --help` output must be checked.
The planned command semantics are exactly:

```text
./build.sh --build_dir <fixed-new-build-root> \
  --cmake_path <external-cmake> --config Release --build_shared_lib \
  --skip_tests --parallel 4 --update --build
```

If staging requires a separate install command, it must be recorded with its
own exit code and must use the successful build/install output rather than
manually selecting headers. Any actual parameter change stops the formal
attempt and requires a new decision.

The formal build must not enable CUDA EP, TensorRT EP, XNNPACK, ACL, ArmNN,
OpenMP, minimal build, reduced operator configuration, training, custom ops,
LTO or manual `-march=native`.

#### J2.3 local SDK contract

The final Stage J local SDK logical root is:

```text
third_party/onnxruntime/1.23.2/linux-aarch64/
```

The complete payload remains local-only and must not enter Git. The required
logical structure is:

```text
include/
lib/
BUILD_MANIFEST.json
HEADER_SHA256SUMS.txt
FILE_SHA256SUMS.txt
LICENSE
THIRD_PARTY_NOTICES
README.md
```

The include/lib payload, including real symlinks, must come entirely from one
formal J2.2 PASS SDK. Failed-build artifacts and mixed SDK attempts are
prohibited. J2.3 may track only the metadata, license/notice and README files;
its controlled `.gitignore` update must prevent `.so` files and complete SDK
headers from entering Git.

`BUILD_MANIFEST.json` uses schema version 1 and records the artifact kind
`onnxruntime_aarch64_cpu_sdk`, status `complete`, ORT 1.23.2, AArch64,
FP32, CPUExecutionProvider, source/build/toolchain/SDK facts, libraries,
headers, CMake package, features, license, provenance and limitations. It
uses logical or repository-relative paths only, distinguishes observed from
unverified facts, contains no NaN/Infinity or absolute local paths, and never
uses the historical superseded build as the active artifact source.

`HEADER_SHA256SUMS.txt` covers only regular files under `include/` using SDK
root-relative paths. `FILE_SHA256SUMS.txt` covers regular include/lib/CMake
package files plus BUILD_MANIFEST.json, LICENSE, THIRD_PARTY_NOTICES and
README.md. Each excludes itself, the other manifest and symlinks; both use
UTF-8 byte-order sorting, LF endings and two spaces between hash and path.
Symlink path, target and resolved target are recorded in BUILD_MANIFEST.json.

LICENSE and THIRD_PARTY_NOTICES must be obtained from a newly retrieved and
verified official ORT v1.23.2 source. They must not be reconstructed from
memory, copied from an unknown web page or substituted with an individual
dependency license. Source-relative path, source commit, source SHA, copy
command and destination SHA are recorded.

#### J2.3 Published Evidence contract

The frozen Published Evidence logical root is:

```text
results/build/onnxruntime_aarch64/j2_sdk_v1/
```

It contains exactly:

```text
README.md
provenance.json
verification_report.json
commands.txt
sha256sums.txt
```

`provenance.json` and `verification_report.json` use schema version 1. They
record the evidence/task/contract identity, source and formal attempt
provenance, all manifest and artifact hashes, historical superseded attempt,
privacy status, exact file-set and manifest validation, clean source/build
exit codes, ELF/SONAME/symlink/ldd facts, CPU-only absence of CUDA/TensorRT,
CMake package relocatability, license/notice validation, tracked size and
limitations. Absolute local paths are prohibited.

`commands.txt` records only commands actually used for J2.3 packaging,
copying, manifest generation, validation, privacy scan and Git checks.
`sha256sums.txt` excludes itself, is root-relative, deterministic, LF-only,
and must pass `sha256sum -c` for the exact five-file set.

#### Privacy and invalidation

Tracked Published Evidence must not contain home/tmp paths, IP or MAC
addresses, serials, UUID/PARTUUID values, passwords, tokens, credentials,
sudoers content, private-key paths or raw output files. Logical labels,
basenames, versions, booleans, commits and SHA256 values are allowed.

Any change to ORT source/tag/commit, build flags, compiler, external CMake,
CPU-only configuration, source/build/SDK attempt, public headers, libraries,
symlinks/SONAME, license/notice source, manifest schema or generation rules
invalidates formal J2.2/J2.3. Documentation-only changes do not invalidate
the SDK.

After formal J2.2 remediation PASS: J2.2 becomes COMPLETE and J2.3 becomes
READY. After J2.3 PASS: J2.3 becomes COMPLETE and J2.4 becomes READY. After
J2.4 PASS: J2.4 becomes COMPLETE and J2.5 becomes READY. After J2.5 PASS:
J2 becomes COMPLETE and J3.1 becomes READY.

### D045 - Accept J2.2 v2 Non-Build Evidence Reconciliation

时间：2026-07-23T22:00:04+08:00

状态：`Accepted`

D045 accepts the non-build evidence reconciliation for the immutable
`j2.2_formal_clean_v2` attempt. The formal build, independent install and SDK
technical results remain valid, and J2.2 remains `COMPLETE`. No second ORT
full clean build is required. The v2 local attempt and its manifest remain
immutable; this decision authorizes an independent reconciliation document and
does not backfill the original attempt.

D045 only corrects the non-substantive evidence-field requirements identified
under D044. It does not change the ORT tag or commit, build flags, CPU-only
contract, formal SDK, J2 task order, J2.4/J2.5 gates or the J3 boundary.

#### Accepted evidence deviations

1. Command and exit-code indexing: commands 001–006 have no independent
   `exit_codes.tsv` rows; command 007 uses the semantic ID
   `environment_preflight`; later command and exit-row identifiers are not
   numerically identical. The substantive clone, source-gate, build, install,
   artifact and local-manifest operations have verifiable successful exit
   rows. The original `commands.txt` and `exit_codes.tsv` must not be changed.

2. Timestamp fields: `source_ready`, `verification_end` and `attempt_end` are
   `not_recorded`. No timestamp is fabricated from file mtimes or current
   time. The recorded build and install boundaries remain valid and the gap
   does not trigger a rebuild.

3. Wrapper path typos: 008a is `HARMLESS_WRAPPER_TYPO`; 013a and 018a are
   `RECORDED_NON_SUBSTANTIVE_FAILURE`; 020a is `HARMLESS_WRAPPER_TYPO`. The
   wrong target did not exist and received no files. Clone and help were not
   executed when their redirections failed. The two read-only snapshot and
   provenance operations ran without saved wrapper output and were then
   executed correctly in the same v2 attempt. Formal build stdout/stderr were
   retained; no cross-attempt copying or evidence splicing occurred.

4. The historical source aggregate
   `4f460795adeab01ac3a0b207ff18ec9d6af01d3957456af59dcb201645e9c5ab` is
   classified as `historical_recorded_not_future_authority`. It is retained,
   is not claimed to be independently reproducible, and need not equal the
   new canonical aggregate.

#### Canonical source aggregate contract

The new reconciliation identity is frozen as
`stage_j_ort_source_aggregate_v1`. Its UTF-8/LF payload is derived from the
superproject Git index and Git object blob bytes, preserves mode, hashes
symlink target blobs without following worktree symlinks, represents gitlinks
with their recorded submodule commits, and normalizes clean recursive
submodules by UTF-8 path order. It does not depend on mtime, inode, absolute
path, hostname, current time or worktree enumeration order.

The reconciliation records the canonical payload SHA256, algorithm,
entry/submodule counts and an independently reproducible code block. A new
aggregate is a post-PASS reconciliation identity, not a replacement historical
timestamp or original-attempt record.

#### Status and rebuild authority

The reconciliation PASS establishes `J2.3 READY`; it does not execute J2.3.
J2.4 and J2.5 remain pending, J2 remains `IN PROGRESS`, J3 remains
`BLOCKED_BY_J2.5`, and J3.0 remains `NOT_DEFINED`. J2.3 must use only the
formal v2 SDK, must not use the historical development SDK, and must not
rebuild ORT. Future rebuild is required only if the ORT tag/commit/version,
recursive submodule commits, compiler/external CMake/build command, SDK
library/header/symlink/SONAME, main library SHA, formal build/install logs or
exit codes, or the canonical aggregate under the same source state changes or
fails validation.

The D045 contract commit is intentionally a placeholder until the owner
reviews and records the repository commit. No push, merge, rebase or tag is
authorized by this decision.

### D046 - Accept third-party OpenCV/TBB Leak Limitation in J3.9 Sanitizer Validation

时间：2026-07-24T01:27:43+08:00

状态：`Accepted`

#### Decision scope

D046 is limited to the J3.9 Jetson ASan/UBSan validation gate. It records the
formal disposition of the existing sanitizer failure after the independent
J3.9 remediation investigation. It does not change production source, test
logic, CMake sanitizer flags, Release build behavior, ORT SDK contents or
frozen assets.

#### Recorded strict sanitizer result

- ASan: no heap corruption, use-after-free or invalid memory access was
  observed.
- UBSan: PASS; no undefined-behavior diagnostic was emitted.
- LeakSanitizer: detected 792 bytes in 3 allocations during the
  `runtime_config` test.
- The original J3.9 configure and build completed successfully; `serial_runner`
  passed and `runtime_config` failed only on the LeakSanitizer report.

#### Ownership conclusion

The remediation Evidence `j3_9_remediation_investigation_v1` records:

- Scenario A reproduced the leak with the current code and leak detection
  enabled.
- Scenario B bypassed only OpenCV thread-policy activation in a diagnostic
  shim, and the leak disappeared.
- The allocation stack is below the project boundary in OpenCV/TBB
  initialization (`cv::setNumThreads(int)` and `libtbb.so.2`).
- Scenario C disabled leak detection and produced no non-leak ASan/UBSan
  diagnostic.
- No project-owned allocation was identified.

The accepted ownership classification is:

`B — third-party OpenCV/TBB initialization leak`

#### Acceptance and limitations

For J3.9 only, the project accepts this third-party initialization leak as a
documented limitation and does not require strict LeakSanitizer PASS for the
J3.9 final disposition. ASan and UBSan checks remain required and are not
weakened. No leak suppression is added, and no production source change is
authorized or required by this Decision. The existing Release runtime
validation remains valid.

This acceptance must not affect J4 inference pipeline work, benchmark work,
TensorRT, CUDA EP, ROS2, camera operation or any later runtime gate. Any
future change to the OpenCV/TBB runtime, sanitizer policy or J3.9 acceptance
requires a new Decision.

### D047 - Reconcile J3 Provenance and Freeze J4 Entry Interpretation

状态：`Accepted`

#### J3.5 provenance reconciliation

- Incorrect recorded source commit：`9b14631a773518b9eea73d875af1e46b4e3a0b9e`。
- Correct source commit：`9b146317922561c55d91ad7126dbde4164b0c800`。
- J3.5 Evidence commit：`8d57466516b470b2889a10b680e2ffa2034fcf26`。
- The correct source commit is a direct ancestor of the Evidence commit。
- The Evidence commit adds only documentation and the J3.5 Evidence；no
  production source was changed。
- The original J3.5 Evidence remains immutable；the original technical result
  remains `PASS` and does not require a technical rerun。
- Final J3.5 status：`COMPLETE_WITH_RECONCILED_PROVENANCE`。

#### J3.10 authority

- `j3_10_j3_evidence_gate_v1` is retained unchanged。
- Because v1 inherited the invalid J3.5 source SHA, its disposition is
  `SUPERSEDED_FOR_FINAL_AUTHORITY_BY_J3_10_V2`。
- `j3_10_j3_evidence_gate_v2` is the sole final J3 provenance authority after
  its PASS。
- J3.1–J3.9 technical tests are not rerun and no old Evidence is modified。

#### Stage J authority hierarchy

The authority order is frozen as follows:

1. Stage J Plan v0.3；
2. Accepted Decisions D041–D047；
3. Frozen Stage J Task Cards, as interpreted by later accepted Decisions；
4. Published Evidence；
5. The latest live-status section at the end of `docs/personal/TASKS.md`；
6. README, PROJECT_BRIEF, EXPERIMENT_PLAN, ENVIRONMENT and ARCHITECTURE as
   summaries only。

`PENDING` in a frozen Task Card is the card-definition status, not the live
execution status。

#### J4 protocol section mapping

The authoritative mapping is:

- J4.1 — Level A correctness：Stage J Plan §18.1；
- J4.2 — Level B runtime/integration：Stage J Plan §18.2；
- J4.3 — Level C robustness：Stage J Plan §18.3；
- J4.4 — Cross-level Evidence gate：Stage J Plan §18 and §26。

The frozen Task Cards' J4 `Parent protocol sections: §28` reference is a
`FROZEN_CROSS_REFERENCE_DEFECT` because Plan §28 is J7 Consolidation. The
Task Cards are not modified；this Decision is the formal interpretation。

#### J4.3 dependency interpretation

The Task Card dependency `J4.2 PASS; J3.9 PASS` is interpreted as follows:

- J4.2 must actually PASS；
- the J3.9 dependency is satisfied by the retained strict-failure Evidence,
  remediation classification B, Accepted Decision D046, and
  `J3.10 v2 PASS_WITH_ACCEPTED_THIRD_PARTY_LIMITATION`。

This interpretation satisfies only the J4.3 entry dependency. J3.9 is not
rewritten as strict PASS；the LeakSanitizer finding is not deleted, hidden or
suppressed；and the J4.3 gate is not relaxed. J4.3 itself remains the Plan
§18.3 Level C scope: 16 images, class-aware maximum bipartite matching,
confidence/bounding-box tolerance, and byte-identical payloads across two
canonical Jetson runs. J4.3 does not start a new sanitizer campaign; any such
campaign requires a new Decision。

#### Live transition state

After D047 and J3.10 v2 PASS:

- J0 `COMPLETE`；J1 `COMPLETE`；J2 `COMPLETE`；
- J3 `COMPLETE_WITH_ACCEPTED_THIRD_PARTY_LIMITATION`；
- J4 `NOT_STARTED`；J4.1 `READY`；J4.2/J4.3/J4.4 `PENDING`；
- Stage T `NOT_STARTED`；Stage P `NOT_STARTED`。

The next authorized task is `J4.1 — Level A correctness`。

### D048 - Accept Platform-Specific AArch64 ORT CPU Numerical Envelope for J4.2

状态：`Accepted`

#### Strict Plan result remains unchanged

The original Stage J Plan §18.2 strict Gate remains authoritative:

- overall MAE `<= 1e-6`；
- overall max_abs `<= 1e-4`。

The original Jetson `j4.2_level_b_v1` result does not satisfy that Gate and is
retained unchanged as a strict failure. `strict_plan_gate_pass=false` remains
the permanent record. The Python golden, production inference code, model,
contract and original attempt are not rewritten.

#### Evidence basis

The accepted classification is
`SUPPORTED_CROSS_ARCH_ORT_CPU_NUMERICAL_DRIFT`, not a proven single-kernel
root cause. The evidence is:

- the same frozen model, input, ORT 1.23.2 and CPUExecutionProvider were used；
- the historical x86 C++ result exactly matched the Python golden；
- the WSL x86_64 Python reference was deterministic across two processes；
- the Jetson aarch64 C++ result was deterministic across two processes；
- Jetson `ORT_ENABLE_ALL` versus `ORT_DISABLE_ALL` diagnostics produced the
  same result；
- Jetson intra/inter-op `1/1` diagnostics produced the same result；
- the mismatch is concentrated in the bbox group, while score error is much
  smaller；
- all output values are finite。

#### D048 AArch64 acceptance policy

This policy is limited to the frozen combination of Jetson Orin Nano Super,
L4T R36.5, aarch64, the formal Stage J ORT 1.23.2 CPU-only build,
CPUExecutionProvider only, the frozen model/input/Python golden hashes,
Controlled 1-Core, ORT sequential/all/1/1 with spinning enabled, OpenCV
threads 1, MAXN_SUPER and `jetson_clocks --fan`.

The D048 acceptance Gate requires two deterministic separate-process Jetson
outputs, canonical raw SHA256
`a64a1028c3ce0c3b6cf2263122fe555338a75dd38bd9cbb6b0f62495359af358`, the
declared float32 BCN `[1,10,8400]` contract, all 84000 values finite,
requested/applied options matching, session creation success, OpenCV 1/1,
and unchanged model/input/golden/config/binary/ORT/contract identities.
Its numerical envelope is overall MAE `<= 1e-5`, overall max_abs `<= 0.01`,
bbox max_abs `<= 0.01`, and score max_abs `<= 1e-4`.

The policy field is `d048_cross_arch_acceptance_pass`; it is distinct from
`strict_plan_gate_pass` and does not rewrite the strict result.

#### Final J4.2 and J4.3 interpretation

When `strict_plan_gate_pass=false` and
`d048_cross_arch_acceptance_pass=true`, J4.2 is
`COMPLETE_WITH_ACCEPTED_CROSS_ARCH_NUMERICAL_LIMITATION`. D048 supplements
and supersedes only D047's strict wording that J4.2 must actually PASS for
this documented cross-architecture limitation. J4.3's own §18.3 Gate is not
relaxed: its 16/16 checks, confidence and bbox tolerances, class-aware
matching and byte-identical canonical payload requirements remain unchanged.

D048 is invalidated by any ORT/build, model, input/golden, RuntimeConfig
semantic, CPU provider, JetPack/L4T, architecture, canonical raw SHA or
production inference algorithm change.

### D049 - Reconcile J5 Task Mapping and Authorize the J5.1 Python Reference Campaign

状态：`Accepted`

1. The Stage J Plan remains the highest authority.

2. The frozen Task Cards' J5.1–J5.7 references to Stage J Plan §24.6–§24.8,
   §26–§28 are classified as `FROZEN_CROSS_REFERENCE_DEFECT` because the
   Plan contains only §24.1–§24.4 and Plan §28 is J7 Consolidation rather
   than the J5 execution protocol. The Task Cards remain frozen and are not
   modified.

3. The authoritative task mapping is:

   - J5.1a Reference protocol/provenance: Plan §10.3, §19.1, §26–§27;
   - J5.1b Python Reference dual run: Plan §19.1;
   - J5.1c smoke/evidence budget: Plan §26–§27;
   - J5.2 Candidate semantic precheck: Plan §19.2–§19.3;
   - J5.3 Candidate sizing: Plan §20;
   - J5.4 Profile selection: Plan §21;
   - J5.5/J5.6 formal baselines: Plan §22;
   - J5.7 J5 Evidence gate: Plan §26–§27 and the J5 matrix in §30.

4. Formal J5.1 Reference execution is authorized only in the frozen WSL
   x86_64 Python Reference environment. The Jetson 20-image corpus copy is
   reserved for J5.2 and later Jetson campaigns and cannot replace the x86
   Python Reference authority.

5. The current M5 Reference, common helper and corpus preparation tool SHA256
   values match the historical provenance. Existing frozen M5 Reference
   tooling is therefore reused unchanged:
   `EXISTING_FROZEN_M5_REFERENCE_TOOLING_REUSED_UNCHANGED`.
   No second Reference pipeline and no source modification are authorized.

6. The historical corpus recovery report remains unchanged. The new 20/20
   validation resolves current live readiness without rewriting the historical
   blocked recovery attempt.

7. The J5.1 Python Reference Campaign is the current authorized campaign.
   J5.2 and all later J5 work remain unauthorized until J5.1 is complete and
   separately reviewed.

### D050 - Decouple RuntimeConfig Schema from Result Metadata Schema

状态：`Accepted`

1. RuntimeConfig schema 与 RunMetadata/JsonSink output schema 是独立合同。

2. Stage J RuntimeConfig v2 继续保持 `schema_version=2`。

3. 当前 JsonSink detection output schema 继续保持 `schema_version=1`。

4. 禁止把 RuntimeConfig schema 直接传播为 RunMetadata schema。

5. 修复范围仅限 schema bridge，不改变 model、ModelContract、preprocessing、
   ORT inference、postprocessing、Detection、JSON detection 字段、JsonSink
   output schema、RuntimeConfig v1/v2 isolation 或 D048。

6. J4.3 中保留的 v2 failure 是历史事实，不修改历史 Evidence。

7. J4.3 成功的 v1-compatible Level C Evidence 继续有效。

8. J5.2 v1 attempt 保持 `FAILED`，不追加或覆盖。

9. remediation 后必须创建新的 J5.2 attempt，并重新执行全部候选。

### D051 - Freeze J5 CPU Profile Selection

状态：`Accepted`

1. Controlled profile：candidate `k1`；CPU set `5`；
   `intra_op_threads=1`；`inter_op_threads=1`。

2. Tuned profile：candidate `k5`；CPU set `1-5`；
   `intra_op_threads=5`；`inter_op_threads=1`。

3. 选择依据：J5.3 Candidate Sizing Evidence
   `j5_3_candidate_sizing_v1`。Selection 综合 cycle latency、CPU
   utilization、VmRSS、temperature、VDD_IN power 和 determinism，不以单个
   指标决定。

4. k1 作为 Controlled profile：候选集合中总在线 CPU utilization、VmRSS、
   temperature 和 VDD_IN current mean 最低；两次输出均精确匹配 J5.2 frozen
   semantic SHA。其较高 latency 是 Controlled 最小资源/可复现角色的已接受代价。

5. k5 作为 Tuned profile：cycle mean 相对 k1 降低 `74.25%`，相对 k4
   降低 `16.87%`。k6 相对 k5 仅再降低 `3.48%`，但总在线 CPU utilization
   增加 `11.28` 个百分点、VmRSS max 增加 `540 KB`、最高温度增加 `0.438 C`、
   VDD_IN current mean 增加约 `5.47%`；因此按收益递减原则选择较低线程数 k5，
   不选择最高线程 k6。

6. 保持：model unchanged；ORT build/version/provider unchanged；不启用新的 EP
   或 ORT feature；contract unchanged；semantic SHA unchanged。k1/k5 仅分别冻结
   J5.3 已验证的 candidate thread setting。J5.4 只读分析 J5.3 Evidence，未重新运行。

7. 后续 J5.5/J5.6 必须使用本 Decision 冻结的 Controlled `k1` 与 Tuned `k5`
   profile；不得在后续任务中静默改变候选、CPU set 或 ORT thread settings。

### D052 - Adopt Research-Grade Stage J Remediation and Closeout Policy

状态：`Accepted`

1. Stage J Plan v0.3 保持冻结；不修改其历史文本或 SHA。

2. 当前诊断结论保持为：
   `J8 FAIL under the original frozen v0.3 Deep Evidence Gate`。

3. 当前仓库不得声称：
   - `J8 v0.3 PASS`；
   - `J9 COMPLETE`；
   - `STAGE J CLOSED`。

4. 当前项目用途为：
   - 研究生毕业设计；
   - 学术论文实验；
   - 求职工程项目。

5. 对论文和后续 Stage T 具有实质价值且必须补齐：
   - Tuned k5 五次正式 baseline；
   - 可复核的 30 分钟 k5 stability Evidence；
   - J5 Evidence Gate；
   - Stage J Consolidation；
   - final research-grade independent audit。

6. 不重新执行：
   - J1–J4；
   - J5.1–J5.5；
   - ORT build；
   - 模型、ModelContract、corpus；
   - profile selection。

7. 现有
   `results/benchmark/jetson_ort_cpu/profile_stability/j5_6_profile_stability_v1`
   重新分类为 `HISTORICAL_PRE_J6_STABILITY_RUN`。它是真实的 30 分钟运行记录，
   但不是冻结计划中的 J5.6 Tuned formal baseline，也不是完整 J6 Evidence。
   历史目录不得删除、覆盖或重命名，不得伪装为完整 PASS。

8. J5.5/J5.6 历史 manifest 中的 `./` 路径形式分类为
   `ACCEPTED_NON_SUBSTANTIVE_MANIFEST_PATH_FORMAT_DEVIATION`。旧 Evidence
   不修改；后续 Consolidation 使用规范化 repo-relative 索引；不得声称旧
   manifest 可按 v0.3 规则 byte-identical 重建。

9. OC/UV、thermal throttle 或 power throttle 接口若平台不可用：
   - 记录 `unavailable`；
   - 保留原始探测命令和返回结果；
   - 禁止声称 counter PASS；
   - 不能仅因接口缺失宣称无 throttling。

10. 补齐任务完成后允许的最终状态是
    `STAGE_J_COMPLETE_WITH_DOCUMENTED_EVIDENCE_LIMITATIONS`，不是
    `J8_PASS_UNDER_ORIGINAL_V0_3`。

11. 只有新的 research-grade final audit PASS 后，才允许规划 Stage T。

12. 本 Decision 不改变：
    - 模型；
    - preprocessing/postprocessing；
    - ORT CPU 语义；
    - J4 容差；
    - D048；
    - k1/k5 profile；
    - benchmark 统计真实性要求。

### D053 - Accept Controlled k1 Historical Statistics Limitation and Adopt Research-Grade J5 Gate

状态：`Accepted`

1. 原始 Stage J Plan v0.3 不修改。原始 J5.7 v1 结论保持为：
   `BLOCKED under the original frozen §22.4/J5.7 contract`。

2. 不声称 original J5.7 v0.3 PASS、J8 v0.3 PASS、J9 COMPLETE 或
   STAGE J CLOSED。

3. J5.5 k1 已真实完成五个 separate processes、每次 560 frames、semantic
   correctness、determinism、whole-process wall time、FPS 和 resource summary。

4. J5.5 不具备 measured-window per-frame latency distribution、per-frame
   P50/P95/P99、per-frame sample standard deviation，或 published raw
   telemetry chain 的独立重建能力。上述缺口不得通过文档虚构或从缺失原始数据
   推导，且不重新运行 J5.5。

5. J5.5 的研究级角色调整为：
   `Controlled 1-Core Resource and Reproducibility Reference`。
   它是次要工程基线，不作为 Stage T speedup 的主要分母。

6. J5.6 v3 的研究级角色为：
   `Tuned k5 Formal CPU Performance Baseline`。
   它是论文和后续 Stage T 对照设计中的正式 ORT CPU baseline；Stage T 仍未授权。

7. 允许从 immutable J5.5 published summaries 确定性生成补充统计，但不得修改
   旧 Evidence、虚构 per-frame 数据、将 whole-process wall time 称为 per-frame
   latency，或从缺失原始数据推导分布。补充报告必须明确使用
   `latency_scope=whole_process_wall_time`，并列出不可用指标。

8. 新的 research-grade J5 Gate 可以判定为
   `PASS_WITH_DOCUMENTED_J5_5_LIMITATION`，前提是 J5.1–J5.4 asset/provenance/
   correctness PASS，J5.5 事实和限制完整记录，J5.6 v3 formal statistics、
   correctness、determinism、telemetry 和 SHA PASS，且未发现模型、Corpus、
   Reference 或 Profile 漂移。

9. 该 research-grade Gate PASS 后允许进入 J6，但不直接授权 Stage T。Stage T
   仍需 J6 research-grade stability、J7 consolidation 和 final research-grade
   independent audit PASS。

### D054 - Close Stage J Research Baseline and Open Stage K Planning

状态：`Accepted`

1. 基于已发布且通过 manifest 验证的 J5.1–J7 Evidence、J8 lightweight audit
   和最终文档审查，Stage J Research Baseline 正式状态为
   `COMPLETE`。

2. J8 lightweight audit 的定位是 research-grade lightweight closeout audit；
   它不等同于原冻结 J8 Deep Evidence Gate，不声称原 J8 Deep Gate 通过，也
   不修改原 J8 `FAIL` 历史事实。

3. 下列限制继续对论文和工程结论有效：J5.5 process-wall statistics
   limitation、J6 unavailable power telemetry，以及未进行 TensorRT/GPU
   backend 和 production validation。

4. Stage J closeout 只修改允许的最终报告、状态文档和本 Decision；不修改
   冻结 Stage J Plan、J1–J7 Evidence、模型、contract、corpus 或 runtime
   SHA，也不删除历史失败 attempt。

5. Stage K Planning：`READY_FOR_PLANNING`，允许开始下一阶段规划审查。
   Stage T remains `NOT_STARTED` and `NOT_AUTHORIZED` for implementation or
   execution until separate next-stage planning and governance authorization。

### D055 - Resolve Stage K and Historical Stage T Naming

状态：`Accepted`

D055 refines and freezes the formal execution naming after D054.
D054 remains an unchanged historical planning fact and is not
rewritten.

Stage K is the formal TensorRT serial backend stage.
Historical Stage T remains a non-executed placeholder.
Stage J closure, accepted limitations and final Evidence remain
historical facts.
Stage K does not reopen superseded Stage J draft gates.
Stage P remains the formal required downstream Pipeline stage.

### D056 - Use Direct TensorRT C++ Runtime API

状态：`Accepted`

TensorRT candidate backend uses the direct TensorRT C++ Runtime API.
ONNX Runtime TensorRT EP, provider fallback and ORT GPU rebuild
are excluded.

### D057 - Freeze Offline FP16-Enabled Engine Build

状态：`Accepted`

The Engine is built offline with trtexec.
FP16 builder mode is enabled.
The Engine is mixed precision; all-layer FP16 is not claimed.
Host I/O remains FP32.
Batch=1 and static 640×640 shape are frozen.
An explicit memory-pool limit and exact command must be frozen
by D062 after K1 and before formal K2 execution.

### D058 - Preserve Synchronous HostTensor Backend Boundary

状态：`Accepted`

TensorRtEngine implements IInferenceEngine.
The public API remains synchronous HostTensor input/output.
inference_ms is backend host-roundtrip latency.
Execution uses one CUDA stream with ordered H2D, enqueueV3,
D2H and synchronization.
Persistent CUDA device buffers are required. Per-frame CUDA
allocation and per-frame stream or ExecutionContext creation are
prohibited. Caller-owned output remains an owned HostTensor, so
the Decision does not claim zero host allocation.
CUDA preprocessing, pinned-buffer optimization, GPU NMS,
multi-stream and Pipeline are excluded from Stage K.

### D059 - Introduce RuntimeConfig v3 and Result Metadata v2

状态：`Accepted`

RuntimeConfig v3 accepts only tensorrt_fp16.
v1/v2 behavior remains unchanged.
v3 runtime requires Engine, Engine Manifest and ModelContract.
The actual source ONNX file is not a runtime dependency.
TensorRT support is optional through CMake.
ORT Result JSON schema v1 remains unchanged.
TensorRT Result JSON schema v2 is a minimal metadata extension
of the existing v1 image, detection, postprocess, timing and
summary body semantics.
The existing candidate_index field remains for compatibility and
diagnostic candidate identity, but it is not a normal matching
criterion or sufficient boundary evidence by itself.
The implementation reuses the existing sink and detection
serialization path and does not introduce a schema registry or
parallel sink framework.
RuntimeConfig and Result JSON schema versions are independent
version namespaces.

### D060 - Freeze Correctness Authority and Numerical Policy

状态：`Accepted`

Python ORT explicit Reference remains authoritative.
C++ ORT is the same-commit regression control.
TensorRT is the candidate backend.
C++ ORT Level C retains the Stage J strict detection tolerances.
C++ ORT Level B first evaluates the Stage J strict raw-output Gate.
When that strict Gate is not met solely because of the already
accepted WSL-to-Jetson cross-architecture numerical behavior,
a D048-derived per-tensor Gate may close the control with an
explicit inherited cross-architecture limitation. The Jetson C++
ORT output must be repeatable and its per-tensor canonical SHA
must be recorded.
Level B uses 16 frozen image-derived tensors and per-tensor MAE,
Type-7 P99 where applicable, and max-absolute-error metrics.
The derivative Reference Bundle is generated in the existing
validated WSL Python ORT environment and transferred to Jetson
with SHA verification.
Level C uses original-image coordinates and deterministic maximum
matching.
Threshold-boundary variation requires exact candidate identity
and raw-output evidence. A targeted diagnostic record is generated
only when an actual mismatch or boundary case occurs.
A full all-candidate postprocess provenance or replay framework
is not a Stage K requirement.

### D061 - Freeze Benchmark, Stability, Evidence and Downstream Scope

状态：`Accepted`

Formal comparison reruns ORT k5 and TensorRT from the same source
commit and the same executable SHA.
The backends use separately frozen configuration files and
configuration SHA values. Shared RuntimeConfig fields are verified
semantically equivalent. Timing-stage equivalence is verified
through the common Stage K profile runner, executable and trace
schema rather than configuration SHA equality.
Five independent runs per backend, 60 warmup and 500 measured
frames are sufficient. Run-level statistics and paired speedups
are primary; pooled frames are descriptive only.
TensorRT receives one 30-minute stability run using the inherited
Stage J J6 stability and telemetry semantics.
K0–K9 are logical gates and do not require separate full evidence
packages, separate commits or separate implementation cycles.
Stage P Pipeline optimization remains required downstream project
scope, but is outside Stage K and is not authorized before Stage K
closeout.
Evidence remains research-grade and does not claim industrial
certification. Only formal or decision-relevant failures require
retention.

### D062 - Freeze Exact TensorRT Engine Build Contract

状态：`Accepted`

D062 freezes the offline TensorRT Engine build contract after K1 PASS on the
real Jetson environment. No formal Engine was built while accepting this
Decision.

Environment identity:

- Jetson Orin Nano Engineering Reference Developer Kit Super, `aarch64`
- L4T `R36.5.0`
- CUDA `12.6.68`
- TensorRT `10.3.0.30`
- trtexec `/usr/src/tensorrt/bin/trtexec`, TensorRT `v100300`
- Frozen ONNX SHA256:
  `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944`
- Frozen ModelContract SHA256:
  `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190`

Exact build contract:

```text
/usr/src/tensorrt/bin/trtexec \
  --onnx=models/onnx/yolov8n_neudet_frozen.onnx \
  --fp16 \
  --memPoolSize=workspace:4096M \
  --inputIOFormats=fp32:chw \
  --outputIOFormats=fp32:chw \
  --saveEngine=/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine \
  --skipInference
```

The frozen model contract is static batch 1, input `[1,3,640,640]`, output
`[1,10,8400]`, with FP32 host I/O. `--minShapes`, `--optShapes`, and
`--maxShapes` are intentionally omitted because dynamic profiles are disabled.
TensorRT 10.3 help exposes `--memPoolSize=poolspec` and does not expose the
TensorRT 8.x `--workspace` option. The selected `workspace:4096M` is an
explicit reproducibility ceiling, not a measured optimum claim. FP16 enables
mixed-precision builder selection; it does not claim all-layer FP16.

Engine artifacts remain local-only under
`/home/orin/edge-ai-local-models/stage_k/`. K2 will create and verify the
Engine, build log, inspection log and independent load-engine smoke log.
The tracked manifest is
`models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json`.

D062 Evidence:
`results/platform/tensorrt/d062_contract_v1`.
K2 is `READY`; formal Engine build remains separately authorized only by K2.

### D063 - Accept Stage K ORT Cross-Architecture Numerical Limitation

状态：`Accepted`

Stage K K5 exposed numerical drift between WSL `x86_64` Python ONNX
Runtime 1.23.2 and Jetson `aarch64` C++ ONNX Runtime 1.23.2. The formal
K5 result remains `K5_FAILED` / `ORT_CONTROL_FAIL`; this Decision records
the reviewed disposition path and does not rewrite that historical failure.

新增诊断证据保存在
`/home/orin/edge-ai-local-evidence/stage_k/diagnostics/ort_cross_arch_drift_diagnostic_v1/diagnostic_attempt_001/diagnostic_report.json`.
The diagnostic verdict is `DIAGNOSIS_B` — architecture/kernel numerical
drift dominant. The frozen Reference Bundle was verified with SHA256
`fed5755ce630d0902449f3052fcbb915592245583df19bf924ec867d1c1e1e29`;
all 16/16 input tensor identities were verified. Jetson C++ ORT output was
deterministic and 16/16 repeatability checks were byte-identical. CPU arena
off, memory pattern off, and thread configurations `1/1`, `2/1`, and `4/1`
showed no material runtime-configuration influence; only the `4/1` case
showed a minor change. The remaining drift is bbox-dominated, while score
channels remain stable at approximately `2.9e-8` MAE.

Decision:

- The observed behavior is the D048-inherited cross-architecture numerical
  limitation class.
- Stage K accepts this limitation as a known boundary of the ORT baseline
  control, subject to the closure conditions below.
- D063 does not modify TensorRT Level B tolerance, TensorRT Level C
  tolerance, the Reference Bundle, ONNX, or ModelContract.

ORT Level B may use the disposition
`ORT_CONTROL_PASS_WITH_INHERITED_CROSS_ARCH_LIMITATION` only when all of the
following are satisfied in the applicable formal review:

- input identity `PASS`;
- output shape `PASS`;
- finite `PASS`;
- Jetson repeatability `PASS`;
- score deviation bounded;
- bbox deviation within the accepted numerical envelope; and
- no semantic regression.

D063 does not make K5 pass, does not authorize TensorRT Level B/C or K6,
and does not remove the requirement for a K5 rerun before K6.

### D064 — Reopen K2 for Bounded Sensitivity-Aware TensorRT Precision Remediation

状态：`Accepted`

D064 reopens K2 in a bounded, numerical-precision-only remediation of the
historical TensorRT Level B failure. The original D062 and original Engine
remain frozen historical facts. The original Engine's K5.3 Level B `FAIL`
remains unchanged and is not rewritten.

The global TensorRT `--fp16` builder mode remains enabled. New candidates
must disable TF32 with `--noTF32`. Only layers confirmed by actual graph
tracing to belong to the BBox regression, DFL, or decode-sensitive path may
be constrained to FP32. Backbone, Neck, and the classification branch remain
unconstrained and FP16-enabled mixed precision. No guessed layer names are
permitted.

The ONNX, ModelContract, Host FP32 I/O, static batch 1, static 640 input,
TensorRT Level B/C tolerances, Level B comparator, Level B gate, ORT control,
Reference Bundle, TensorRtEngine, RuntimeConfig parser, and result schemas are
unchanged. K2R may create one local-only noTF32 diagnostic Engine C0 and at
most two sensitivity-aware formal candidates C1/C2. C1 is the terminal BBox
sensitive subgraph policy; C2, authorized only when C1 fails, is the maximum
policy covering the complete BBox regression branches through decode while
still excluding Backbone, Neck, and classification. All constrained layers
must use `precisionConstraints=obey` with exact `layerPrecisions` and required
`layerOutputTypes` controls; no global non-BBox FP16 constraint is allowed.

The smallest candidate that passes the frozen TensorRT Level B Gate at 16/16
is selected. If both C1 and C2 fail, no Engine is selected, K5.3 remains
`FAIL`, and K5.4 remains `NOT READY`; the FP32 scope is not expanded. TensorRT
Level C, K6, benchmark, stability, Pipeline, GPU preprocessing/NMS, INT8,
DLA, ONNX rewrite, model re-export, C++ Builder, Polygraphy, package changes,
push, merge, and tag are not authorized. K5.4 remains unauthorized until a
new selected Engine formally passes K5.3 Level B 16/16.

### D065 — Establish Strict FP32 TensorRT Baseline and Authorize Bounded Selective-FP16 Investigation

状态：`Accepted`

Python ORT remains the correctness authority for this investigation. The
Strict FP32 noTF32 TensorRT Engine is the TensorRT-side correctness baseline;
it is not a replacement for the Python ORT Reference Bundle. The original
FP16 Engine, TF32-enabled FP32 Engine, and the failed K2R C1/C2 results remain
frozen historical evidence. TensorRT Level B and Level C gates and their
unchanged tolerances are not modified.

This decision authorizes a bounded investigation with global TensorRT FP16
builder mode enabled, TF32 disabled, and `precisionConstraints=obey`. Only
graph-traced Detect/BBox-sensitive operations may be constrained to FP32,
including the BBox terminal path, DFL, Softmax, projection/integral,
Slice/Sub/Concat, coordinate decode, and stride multiplication. Backbone and
Neck must remain unconstrained; no global non-Detect FP16 constraint is
permitted.

Because K2R C1 already tested the bbox-only policy under noTF32, and C2 tested
the complete traced BBox regression scope under noTF32, this investigation
must not rebuild an equivalent bbox-only candidate. At most two new candidates
are authorized: M1 (BBox/DFL/decode FP32) and M2 (the complete ONNX
`/model.22` Detect Head FP32). Under the current legacy audit, only the new
M2 route is eligible. M2 is the maximum allowed FP32 scope; if it fails, the
investigation stops without expanding FP32 into Backbone or Neck.

Every constrained layer requires exact layer identity, graph-ancestry evidence,
FP32 compute precision, and the required FP32 output type. If mapping,
inspection, or the TensorRT toolchain cannot establish those facts, the
investigation is blocked. A candidate may enter performance precheck only
after 16/16 Level B, 16/16 TensorRT Level C, and byte-identical repeatability
pass. Performance precheck is non-formal: compared with Strict FP32, it
requires paired median backend latency improvement of at least 10% and 3/3
independent mixed runs no slower than their paired Strict FP32 runs. It does
not authorize K6, stability, Pipeline, formal benchmarking, production
runtime changes, manifest replacement, push, merge, or tag.

### D066 - Accept TensorRT FP16 Deployment Candidate Based on Task-Level Validation

时间：

```text
2026-07-29
```

状态：

```text
ACTIVE
```

主题：

Accept TensorRT FP16 deployment candidate based on task-level validation。

背景：

TensorRT FP16 raw tensor does not satisfy strict numerical equality. The
frozen TensorRT FP16 Level B result is `FAIL`, with the retained failure
characterized as bbox-dominated raw tensor numerical deviation. This raw
tensor limitation is not removed or rewritten by the Stage K8 summary.

决策：

Accept the Original TensorRT FP16 Engine as the final Stage K serial
deployment candidate based on the combined evidence of:

- task accuracy;
- continuous stability; and
- formal serial performance.

The acceptance criterion is task-level deployment behavior, not bitwise raw
tensor equality. The frozen task-level verdict is
`TASK_LEVEL_FP16_ACCEPTED`; the inherited stability verdict is
`K6_STABILITY_PASS`; and the formal benchmark verdict is
`K7_PERFORMANCE_COMPLETE`.

限制：

The raw tensor Level B limitation remains documented and remains part of the
final deployment evidence. This Decision does not claim strict raw-tensor
equality, industrial certification, universal TensorRT superiority, or
Pipeline completion.

影响范围：

- freezes the Original TensorRT FP16 Engine as the Stage K deployment
  candidate;
- establishes task accuracy, stability, and performance as the acceptance
  basis for this candidate;
- preserves the raw Level B failure as a known numerical boundary; and
- closes Stage K documentation and evidence consolidation without changing
  Engine, ONNX, ModelContract, runtime implementation, comparator tolerance,
  benchmark results, or existing Evidence.

备选方案：

- reject the FP16 candidate because raw tensors are not bitwise equal;
- select the Strict FP32 reference as the deployment candidate; or
- continue precision search.

选择理由：

The existing task-level accuracy, stability, and formal K7 performance
evidence support the Original TensorRT FP16 candidate. K8 is a consolidation
and freeze activity, so it does not generate new evidence or reopen precision
search.

后续是否可调整：

可调整。若后续获得新的授权和真实证据，可重新评估部署候选；任何此类
变化必须新增 Decision，并不得改写本 Decision 或历史 raw tensor Evidence。

### D067 — Stage P baseline, scope and execution authority

时间：`2026-07-30`
状态：`ACTIVE`

冻结 Stage P 起点为
`main@c6890d86e7534500cfe31c40dd73f151d77d5362`，并要求本地 main、
`origin/main` 与 annotated tag
`stage-k-tensorrt-fp16-complete-v1.0^{}` 相等。Stage P 的技术与实验协议权威
为 `STAGE_P_EXECUTION_PLAN.md` v1.2 FINAL，任务边界权威为
`STAGE_P_TASK_CARDS.md`，执行授权严格遵循 P0→P8。

P0 在包含本 changeset 的 commit 完成；P1 仅在用户审查该 P0 commit 后才能
授权。P0 不包含 production、header、CMake、tests、config schema、Engine build、
正式 benchmark/stability 或 Evidence attempt。Stage K 已 COMPLETE；D066 的
Original TensorRT FP16 candidate 与 raw Level B retained limitation 均不改写。

### D068 — Four-worker topology and single-inference boundary

时间：`2026-07-30`
状态：`ACTIVE`

Stage P Pipeline 固定为 Source、Preprocess、single Inference、
Postprocess+Sink 四个 workers 与三条 bounded SPSC queues。使用一个 TensorRT
ExecutionContext、一个 CUDA stream、batch 1，且最大并发
`engine.run() = 1`。组件由唯一 worker 使用，不实现可配置 worker 数、独立 Sink
worker、thread pool、MPMC、multiple contexts 或 multiple streams。

`D012 remains ACTIVE.` D068 只 supersede D012 rationale 中历史性的
“three-thread pipeline” implementation detail；它不 supersede Serial + Pipeline
路线。

### D069 — RuntimeConfig v4, Result JSON v3 and compatibility

时间：`2026-07-30`
状态：`ACTIVE`

RuntimeConfig v4 是 TensorRT-only strict union：runtime 为 serial/pipeline，
input 为 directory/video_file，Pipeline 仅允许 bounded `block`。配置 schema 与
Result schema 独立；v4 明确映射到 Result JSON v3。Result v3 使用可选 internal
`runtime_v3` metadata/summary carrier 承载 runtime/input/pipeline、source_frames、
positive finite wall time 与 queue high-water marks。v1/v2/v3 config regression
和 Result v1/v2 历史行为、字段与 bytes 不得因新默认值改变。

Video 的 `max_frames` 只属于 constructor/test/experiment control，不进入
RuntimeConfig v4；nominal FPS 不进入 production Result JSON v3。

### D070 — Exact correctness, timing and benchmark contract

时间：`2026-07-30`
状态：`ACTIVE`

最终 Detection 按 canonical little-endian binary 精确比较。RUN scope=1 与 CYCLE
scope=2 是相互独立的 byte streams；`RUN_AND_CYCLE` 必须维护两个 SHA，不能拼接
成单一 digest。P4 与 P5 使用双 scope；P6 只用 RUN；P7 只用 CYCLE。Incomplete
cycle 只记录 frame count/partial digest，不与完整 180-frame expected CYCLE SHA
比较。

`source_frames` 只统计 successful run 中 successfully returned non-EOS frames；
final EOS probe、failed call、source-only EOS trace、cancelled/discarded item
均不计。block-only successful run 必须
`source_frames == processed_images`。Immediate EOS before the first accepted
frame 是 failure；Serial/Pipeline 都只 probe 一次、不调用 `end_run`、不改变 caller
summary、不伪造 wall time，也不生成成功的零帧 Result v3。

任何 trace callback failure 均为 first error：cancel queues、join workers、不调用
`end_run`、summary unchanged。Runner 成功后的 buffered trace write failure 使
attempt invalid 且 sidecar 不得发布为 valid；已经 atomic committed 的 production
JSON 不回滚，必须披露。

P5 formal measured window 固定为完整 frames 100—5099，throughput 使用 frame 100
source begin 到 frame 5099 outer Sink end；三对顺序、Type-7 percentile、paired
ratio arithmetic mean、sample SD (n-1) 与 1.10× material classification 不变。
D066 的 raw TensorRT Level B `FAIL — retained known limitation` 不因 Stage P
exact scheduling identity 被改写。

### D071 — Offline block-only sources and deferred live-stream scope

时间：`2026-07-30`
状态：`ACTIVE`

Stage P 仅支持 DirectorySource 与 VideoFileSource 的离线无损 backpressure，
`drop_policy = block`。Video identity 固定为：

```text
video_filename = video_path.filename().generic_u8string()
relative_path = <video_filename>/frame_<zero-padded minimum width 6 index>
```

P6 正式 asset 与 MJPG codec preflight 在 Jetson 生成/执行；WSL codec smoke 仅为
非正式能力检查。Jetson preflight 失败为 `P6_BLOCKED_CODEC_PREFLIGHT`，不得静默
换 codec、引入 GStreamer 或扩大范围。FPS、container frame count、FourCC、decoded
count 与 resolution 仅进入 codec/asset sidecar，其中 FPS 是 descriptive metadata，
不是 pacing 或 timing authority。

Camera、RTSP、`drop_oldest`、`drop_newest`、live-stream policy、DeepStream、
GStreamer 专项优化与 ROS2 runtime 延后。P6 仅在 P5 queue capacity 已 selected
and frozen 且 P5 formal benchmark protocol complete 后授权。

### D072 — Stage P P5R protocol correction and Evidence reclassification

时间：`2026-07-31`
状态：`ACTIVE`

P5R 修正 Stage P P5 validity interpretation。P4 的 RUN SHA 对应 180-frame
single-cycle reference；P5 pilot/formal 使用 1100/5100 accepted-frame
extended windows，因此不得要求 P5 RUN SHA 等于 P4 RUN SHA。

P5 RUN SHA 定义为该 run 全部 accepted frames 的 hash；六个 formal run 必须
使用同一窗口并产生 identical RUN SHA。完整 180-frame CYCLE SHA 继续继承 P4
expected CYCLE SHA；partial cycle 只记录，不参与 complete-cycle PASS。

thermal interface unavailable 必须记录为
`thermal_throttle_status=unavailable` 并作为 known limitation；只有实际检测
到 throttling 才产生 `RUN_INVALID_THERMAL_THROTTLING`，不得把 unavailable
解释为 no-throttling PASS。

本 Decision 只改变 Evidence 解释，不授权重新运行、runtime 修改或 P6 提前执行。
基于既有 attempt_001 Evidence，P5 重分类为
`P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE`，selected queue capacity 冻结为
`1`，throughput classification 为 `MATERIAL_MEASURED_THROUGHPUT_INCREASE`。
历史 P5 invalid report 和 raw Evidence 保持不变。

### D073 — Stage P P8 consolidation and closeout

时间：`2026-07-31`
状态：`ACTIVE`

Stage P P4–P7 Evidence 已完成整理并闭环：P4 为
`P4_PIPELINE_CORRECTNESS_PASS`，P5 为
`P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE`，P6 为
`P6_VIDEO_SOURCE_PASS`，P7 为 `P7_PIPELINE_STABILITY_PASS`。

接受 Stage P 的最终 bounded Pipeline 形态为四个 workers、三条 bounded SPSC
queues、single inference worker，并将离线工作负载的 selected queue capacity
冻结为 `1`。Stage P Final Report 与 Evidence Index 是 closeout 的文档入口；原始
Evidence、生成视频、large trace 和 telemetry 按 retention boundary 保持
local-only，不在文档 commit 中提交。

本 Decision 不修改 src、include、tests、CMakeLists.txt、TensorRT Engine、ONNX、
模型、Pipeline topology、queue semantics 或 benchmark data；不授权下一阶段开发。
thermal status unavailable、Stage K inherited raw Level B limitation 和 no
industrial certification claim 必须继续保留。

### D074 — Stage Q baseline, scope and authority

时间：`2026-07-31`
状态：`ACTIVE`

当前选择：

冻结 Stage Q 的权威起点为 `main@630822c7aeec471cc1f82b019d97bc431855045e`，
Stage P annotated tag 的 peeled commit 与之相同；Stage Q 分支必须从该 exact
commit 创建。Stage Q 技术、实验和授权正文为
`STAGE_Q_EXECUTION_PLAN.md` v0.3 FINAL，任务边界由
`STAGE_Q_TASK_CARDS.md` 固定，执行链为 Q0→Q1→Q2→Q3→Q4→Q5→Q6→Q7→Q8。
Q0 只冻结计划和事实，不执行 Q1；INT8 负结果不自动构成 Stage Q 失败。

备选方案：

- 从旧 feature branch 开始；
- 在 Q0 执行平台、资产或 Engine 预检；
- 将 Q0 计划与 Q1/Q2 实施合并。

决策理由：

exact baseline、独立 Q0 freeze 和逐 Gate 授权链保证后续实验可追溯、可复核，
并防止在资产和平台事实尚未验证时提前改变 production 行为。

影响范围：

- Stage Q 分支从 exact Stage P closeout commit 创建；
- Q0 仅允许文档、事实盘点和只读 inventory；
- Q1 仅在用户审查 Q0 commit 后授权；
- Q2–Q8 与 production implementation 继续保持未授权。

后续是否可调整：

可调整。若基线、范围或授权链需要变化，必须新增 Decision，不得改写本记录或
历史 Stage P D072/D073。

### D075 — TensorRT 10.3 version-bound legacy PTQ

时间：`2026-07-31`
状态：`ACTIVE`

当前选择：

Stage Q 使用 TensorRT 10.3 的 version-bound legacy implicit INT8 calibration
workflow、`IInt8EntropyCalibrator2`、`BuilderFlag::kINT8`、
`BuilderFlag::kFP16`、FP32 Host I/O、static batch 1、input
`[1,3,640,640]` 和 output `[1,10,8400]`。正式 Engine 只能描述为
`TensorRT INT8-enabled mixed-precision Engine` 或
`INT8 + FP16 + FP32 mixed-precision Engine`。

备选方案：

- QAT；
- NVIDIA ModelOpt；
- ONNX Q/DQ rewrite；
- pure/full/all-layer INT8；
- TensorRT 11 migration。

决策理由：

该路线与冻结 TensorRT 10.3 平台和既有 FP32 Host I/O 合同一致，能够回答
INT8 PTQ 相对 FP16 的工程性能—精度权衡问题，同时避免把 deprecated workflow
误述为新 TensorRT 项目的推荐方案。

影响范围：

calibration、builder、audit、Manifest、runtime 和报告均必须遵守该版本与
mixed-precision表述；未来版本迁移属于 Future Work。

后续是否可调整：

可调整。只有新增授权和真实平台证据才能改变版本路线；不得在 Stage Q 中
引入另一种量化路线。

### D076 — Calibration data isolation and ordering

时间：`2026-07-31`
状态：`ACTIVE`

当前选择：

正式 calibration 只使用全部 1260 张 train images；val、test、Stage K/P
evaluation corpus、Level B corpus 和 P6 video 均禁止使用。split isolation
同时按 normalized relative path 和 image content SHA256 验证。正式 ordering
固定为 `sha256_key_permutation_v1`，seed 为 `42`；算法只改变顺序，不进行
selection。

备选方案：

- 使用 val/test 或混合评估 corpus；
- calibration-size ablation；
- 其他 sample selection 或 ordering 算法。

决策理由：

保持 calibration 与 held-out evaluation 隔离，避免数据泄漏，并使 1260-image
formal build 可以被确定性复核。

影响范围：

manifest 必须记录 source split、数量、每张图的 path/SHA/decoded shape/index/
ordering key；任一 split 交集必须阻断 Q1/Q3 路径。

后续是否可调整：

可调整。必须新增 Decision 和独立实验授权；不得在 Stage Q 内改变数量、顺序或
隔离域。

### D077 — Builder, cache and artifact authority

时间：`2026-07-31`
状态：`ACTIVE`

当前选择：

`stage_q_int8_builder` 是唯一 formal builder。Q2 仅执行 4-image smoke；Q3
使用同一权威 invocation 完成 1260-image calibration、cache 和 Engine，首次
formal build 强制 cache miss。cache reuse 必须逐项验证 metadata；`trtexec`
只用于 load/inspection。formal artifacts 必须在同一文件系统的 attempt 临时
目录完成后原子发布，不覆盖既有 attempt。

备选方案：

- 直接用 trtexec 生成正式 Engine；
- 将 smoke cache 复用于 formal build；
- 忽略 cache metadata 或覆盖既有 attempt。

决策理由：

单一 builder 与 atomic publication 使 calibration、cache、Engine、audit、
Manifest 和 build summary 具有同一 attempt、builder identity 和环境 provenance。

影响范围：

builder、cache sidecar、artifact identity、attempt 目录和失败处置均受此合同
约束；cache provenance mismatch 必须拒绝复用。

后续是否可调整：

可调整。只能通过新增 builder/artifact authority Decision；不得在 Q2/Q3 中
静默改变正式构建入口。

### D078 — Manifest, runtime and result mapping

时间：`2026-07-31`
状态：`ACTIVE`

当前选择：

RuntimeConfig v5 支持 `tensorrt_fp16` 与 `tensorrt_int8`。Manifest v1 仅用于
历史 FP16 Engine；Manifest v2 仅用于 Stage Q INT8 Engine。Result JSON v4 的
precision 必须来自 validated Manifest；INT8 才携带 calibration object，FP16
不得输出空 calibration object。Manifest v2 必须绑定 layer audit、Engine、
ONNX、ModelContract、calibration provenance 和 FP32 Host I/O 合同。

备选方案：

- 只修改 Result writer；
- 让 runtime 从配置字符串推断 precision；
- 用 Manifest v2 加载 FP16 Engine；
- 为 FP16 输出空 calibration object。

决策理由：

将 artifact provenance 的验证放在 loader/runtime contract 中，避免同一 backend
名称下的 Engine 被错误标识或错误运行，同时保持历史 Result v1/v2/v3 字节行为。

影响范围：

RuntimeConfig、Manifest loader、factory、TensorRtEngine、Result JSON v4 和
兼容性测试均必须遵守该映射；audit sidecar 是构建期 authority，不是 runtime
依赖。

后续是否可调整：

可调整。schema 变化必须新增 Decision、迁移合同和真实回归证据。

### D079 — Accuracy, hash and Serial performance authority

时间：`2026-07-31`
状态：`ACTIVE`

当前选择：

FP16 与 INT8 各执行一次正式 CorpusReplaySource Serial invocation，使用相同
frozen test manifest、image root、manifest order、relative-path domain 和
cycle length 180。evaluator 必须消费同一 invocation 生成的 Result JSON v4。
Serial 性能固定为三组 paired process，100 warmup、5000 measured、drop=0，
并使用完整 cycle SHA、partial-cycle 记录、Type-7 percentile 和固定
accuracy/performance thresholds。

备选方案：

- 用 DirectorySource 重新枚举 accuracy corpus；
- 从 evaluator summary 反向生成 expected hash；
- 改变 cycle/path domain 或临时增加指标阈值；
- 只运行单一方向或单一 process。

决策理由：

单一 source 和 Result JSON authority 使 accuracy、hash、timing 与性能比较保持
可追溯；FP16/INT8 不要求 detection hash 相同，但同一 backend 必须 deterministic。

影响范围：

Q5/Q6 的 source、sink、evaluator、统计公式、窗口、阈值、Engine/runtime
identity 和 Evidence disposition 均被冻结。

后续是否可调整：

可调整。只能在新增 protocol Decision 和重新生成真实 Evidence 后调整。

### D080 — Conditional Pipeline and final disposition

时间：`2026-07-31`
状态：`ACTIVE`

当前选择：

Pipeline 只有在 accuracy 为 ACCEPTABLE 或 TRADEOFF 且 mean paired Serial
inference speedup 至少 1.05 时进入；queue capacity 固定为 1，drop policy
固定为 block。Q7 必须输出五种互斥状态之一。只有 accuracy ACCEPTABLE、Serial
speedup 至少 1.05、无 material end-to-end regression 且 Q7 Pipeline valid
no-regression 时，才可执行 INT8 Pipeline 的正常 EOS 300-second confirmation。
最终分类按 frozen decision tree 机械执行；zero INT8 compute、accuracy
unacceptable、Serial gain insufficient 或有效 Pipeline 负结果均可得到
FP16 retained，而非自动 Stage failure。

备选方案：

- 无条件进入 Pipeline；
- retune queue 或改变 drop policy；
- 在 cycle 中间取消 300-second run；
- 将有效负结果写成 Evidence invalid 或工业稳定性认证。

决策理由：

把 Pipeline 的吞吐收益、单帧端到端回归、runtime failure 和 Evidence invalid
分开，避免把吞吐改善误报为低延迟，也避免把真实负结果误写成实验失败。

影响范围：

Q7/Q8 的 entry gate、五态 disposition、300-second EOS/drain/join 语义、zero
INT8 early stop 和最终 `INT8_RECOMMENDED`/`FP16_RETAINED` 分类均受此合同约束。

后续是否可调整：

可调整。必须新增真实 Evidence 和 Decision；不得在执行中途修改 gate 或分类树。

Stage Q closeout result（2026-08-01）：Q1–Q7 evidence gates completed with
Q7 `Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION`; the required INT8
300-second confirmation passed. Q8 documentation closeout is
`Q8_COMPLETE_READY_FOR_MAIN_MERGE`, with final classification
`STAGE_Q_COMPLETE_INT8_RECOMMENDED`. Merge and tag remain unauthorized.

---

### D081 — Controlled CUDA Preprocessing Exception

时间：

```text
2026-08-01
```

状态：

```text
ACTIVE
```

决策：

1. Stage R 特例授权 V2–V4 使用 CUDA fused preprocessing。
2. 该 CUDA preprocessing 只允许服务于冻结的 TensorRT INT8 Stage R 数据路径。
3. 允许在 TensorRT backend 中增加窄能力 `TensorRtDeviceInputCapability`。
4. CUDA 类型不得扩散到通用 `IInferenceEngine`、ORT、FP16 或 TensorRT-OFF target。
5. 不授权 GPU NMS、GPU postprocess、通用 CUDA BufferManager、通用异步推理 API、
   Zero-Copy 或 Mapped memory。
6. 本 Decision 只解除 Stage R 所需的最小 CUDA preprocessing 禁令。
7. R0 本身不授权实施；实施仅在 R1–R6 经逐 Gate 授权后进行。

备选方案：

- 在通用 `IInferenceEngine` 级别增加 device-input capability；
- 将 CUDA preprocessing 实现为独立通用预处理库；
- 完全禁止 CUDA preprocessing，仅使用 CPU preprocessing。

选择理由：

- Stage R 的研究问题需要评估 CUDA fused preprocessing 是否能降低 CPU preprocessing
  在数据路径中的成本；
- 窄能力授权（TensorRT INT8 专用）将 CUDA 类型暴露范围限制在最小必要接口内；
- 不修改通用 Engine 接口可保护 ORT、FP16 和 TensorRT-OFF 的稳定性；
- 在 Decision 级别明确授权边界，防止 CUDA preprocessing 在 R1 实施时扩散。

影响范围：

- Stage R V2–V4 CUDA preprocessing implementation（仅 R2 授权后）；
- `TensorRtEngine` 的 device-input 能力（仅 R2 授权后）；
- `IInferenceEngine` 通用接口保持不变；
- ORT、FP16、TensorRT-OFF target 不受影响。

后续是否可调整：

可调整。任何扩展 CUDA preprocessing 范围（如 GPU NMS、通用 BufferManager、
多 backend device-input）必须新增 Decision，并重新评估对既有接口和 target
的影响。

---

### D082 — Limited Application CUDA Streams Exception

时间：

```text
2026-08-01
```

状态：

```text
ACTIVE
```

决策：

1. V2/V3 不进行跨帧 overlap。
2. V4 最多使用 `preprocess_stream` 和 `inference_stream` 两条 CUDA stream。
3. V4 固定两个 GPU slot。
4. 只允许 `preprocess(N+1)` 与 `inference(N)` 重叠。
5. 继续保持一个 TensorRT ExecutionContext。
6. 继续保持一个 inference worker。
7. 最大 unfinished `enqueueV3` 数量为 1。
8. `D2H(N)` 和 output packet(N) 必须在 `enqueueV3(N+1)` 前完成。
9. 禁止第三条 stream、第三个 slot、并发 TensorRT inference、output copy overlap
   和 input-consumed Event。
10. V4 只有通过 profiling opportunity gate 后才可授权。
11. R0 本身不授权实施。

备选方案：

- 允许任意数量 CUDA streams 和 GPU slots；
- 允许并发 TensorRT inference；
- 允许 output copy overlap；
- 完全禁止 CUDA streams，所有操作串行。

选择理由：

- 双 stream 设计提供了最小可行跨帧重叠（preprocess 与 inference），同时避免
  multi-context、output overlap 和 triple-buffering 的复杂性；
- 固定两个 slot 和单 ExecutionContext 保持实现复杂度可控；
- 限制最大 unfinished enqueueV3 为 1 确保了 D2H 和 output packet 顺序；
- profiling gate 确保只有存在实际机会时才投入 V4 实施成本。

影响范围：

- V4 Double Buffer implementation（仅 R4 授权后）；
- CUDA stream 管理；
- GPU slot/buffer 管理；
- V2/V3 不受影响。

后续是否可调整：

可调整。任何增加 stream、slot 或放宽 overlap 约束必须新增 Decision，并
通过真实 profiling evidence 证明必要性。

---

### D083 — Cross-Preprocess Identity Exception

时间：

```text
2026-08-01
```

状态：

```text
ACTIVE
```

决策：

1. V0 CPU preprocessing 与 GPU preprocessing family 不要求 detection SHA 或
   tensor digest 完全相同。
2. V0 与 GPU family 通过 geometry、全 tensor 误差阈值和 task accuracy Gate
   建立可比性。
3. V2 与 V3 必须保持 detection SHA 和 tensor digest 完全一致。
4. 若实施 V4，V4 必须与 V2 保持 detection SHA 和 tensor digest 完全一致。
5. 该例外不得被解释为放宽 V2/V3/V4 同路径确定性。
6. 不得改变 Stage Q 的历史 correctness authority。
7. R0 本身不执行 correctness 实验。

备选方案：

- 要求 V0 与 GPU family 的 detection SHA 完全一致；
- 要求所有 Variant 的 tensor digest 完全一致；
- 完全放弃 cross-preprocess identity 验证。

选择理由：

- CPU OpenCV preprocessing 与 CUDA preprocessing 使用不同的数值路径（CPU
  resize/interpolation、颜色转换等 vs GPU texture/sampler），位级相同不可行；
- geometry + tensor 误差阈值 + task accuracy 三层 Gate 提供了可靠的可比性；
- V2/V3/V4 同路径确定性保证了 GPU preprocessing family 内部可比；
- 保留 Stage Q correctness authority 防止历史 Evidence 被重新解读。

影响范围：

- Stage R Gate 2 — Correctness 的 same-path identity 合同；
- V2/V3/V4 的 detection SHA 和 tensor digest 验证；
- Stage Q historical correctness baseline 不受影响。

后续是否可调整：

可调整。任何放宽 same-path identity 或改变 V0 vs GPU family 可比性合同
必须新增 Decision，并重新评估 correctness Gate 和论文结论。

---

### D084 — Stage R R2 Minimal CUDA Data-Path Planning Freeze

时间：

```text
2026-08-02
```

状态：

```text
ACTIVE — planning contract; implementation not authorized
```

决策：

1. V2 固定为：decoded `cv::Mat` → CPU row-aware raw staging → raw H2D →
   CUDA fused preprocessing → TensorRT device input → existing TensorRT
   output path → existing postprocess。
2. CPU 只允许负责 decode、geometry metadata 和 raw staging copy；resize、
   padding、BGR→RGB、float32 normalization、HWC→CHW 属于 CUDA preprocessing。
3. V3 仅在 V2 基础上替换为 long-lived pinned raw buffer；允许 pinned raw
   buffer、device raw buffer、device FP32 input buffer。
4. Pinned output、mapped memory、zero-copy、double buffer、跨帧 overlap 和
额外 CUDA stream 不属于 R2。
5. `TensorRtDeviceInputCapability` 只存在于 `backend_tensorrt`，不得进入
   `IInferenceEngine`、`HostTensor` 或 runtime core。
6. CUDA kernel 输入为 uint8 BGR raw image、width、height、row stride 和
   geometry metadata；输出为 float32 device NCHW `[1,3,640,640]`。
7. CUDA kernel 不负责 NMS、decode、Result JSON 或 TensorRT enqueue。
8. R2 tensor gate 固定为 MAE `<=5e-4`、P99 `<=2/255+1e-6`、maximum
   `<=4/255+1e-6`、non-finite `0`；V2/V3 tensor digest 与 detection SHA
   必须分别相同。
9. R2 实施文件仅限 Stage R、TensorRT backend、validation/tests、Stage R
   configs、CMake、Stage R docs 和 Stage R validation Evidence；既有
   HostTensor、IInferenceEngine、ORT、FP16、Result JSON v4 和 Stage Q
   Evidence 受保护。
10. 本 Decision 只冻结 R2 实施合同，不授权生产代码、CMake、编译或实验。
11. 当前通用 PipelineRunner 与 packet contract 携带 HostTensor input；V2/V3
   必须使用 Stage R 专用 data-path adapter/runner 或等价的 backend-only
   execution path，不得向通用 runner、packet 或 runtime contract 加入 CUDA 类型。

理由：

- 保持 V0 的通用 HostTensor/同步 TensorRT 合同不变；
- 将 CUDA 类型限制在 TensorRT INT8 Stage R backend 边界；
- 使 V2/V3 只研究 pageable 与 pinned raw staging 差异；
- 通过 geometry、tensor、task accuracy 和 V2/V3 identity 形成最小正确性闭环；
- 防止 R2 扩展为通用异步推理、Zero-Copy 或 GPU postprocess 项目。

影响范围：

- 仅 Stage R R2 V2/V3 planning and implementation boundary；
- 不改变 Stage Q correctness authority；
- 不授权 R3/R4 或 V4。

### D085 — Stage R R2.2 V2 Negative Result Closure

时间：

```text
2026-08-02
```

状态：

```text
ACCEPTED — negative result closure
```

决策：

1. V2 pageable raw staging → CUDA preprocessing → TensorRT device input →
   TensorRT INT8 → existing postprocess is accepted as a runnable experimental
   path, not as the selected replacement.
2. Gate B and Gate C remain `PASS`; the Stage Q V0 canonical SHA
   `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` remains
   the correctness authority.
3. Gate D remains `FAIL` after the first minimal 11-bit fixed-point resize
   remediation. The remediation improved task metrics but did not satisfy the
   frozen replacement criteria.
4. Stage Q INT8 V0 is retained as the selected candidate:
   `STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED`.
5. V2 is recorded as an experimental result only. No further CUDA resize
   compatibility expansion, including separable resize, is authorized by this
   closure.
6. V3 is `SKIPPED`, V4 is `SKIPPED`, R2.3 is `NOT AUTHORIZED`, and no benchmark
   or performance conclusion is made.

技术结论：

```text
Under the evaluated YOLOv8n INT8 deployment configuration, CUDA fused
preprocessing introduced small numerical differences relative to OpenCV CPU
preprocessing due to resize interpolation implementation differences. These
differences remained within tensor-level tolerance but affected task-level
metrics near the replacement threshold.
```

理由：

- V2 runtime and frame contracts are valid;
- tensor-level correctness is within the frozen Gate B contract;
- task-level replacement criteria are not satisfied;
- retaining the Stage Q V0 baseline preserves the existing correctness
  authority without inventing success metrics or expanding scope.

影响范围：

- Stage R R2.2 final classification and evidence;
- selected candidate remains Stage Q INT8 V0;
- V2 remains experimental only;
- V3/V4 and R2.3 remain skipped/not authorized.

### D086 — Controlled Negative-Result Closeout and R3–R5 Skip

时间：

```text
2026-08-02
```

状态：

```text
ACCEPTED — Stage R closeout decision
```

决策：

1. R2.2 Gate D did not pass the frozen replacement correctness thresholds.
2. V2 passed tensor, integration, and V0 regression checks, but was not selected as a replacement.
3. The authorized 11-bit fixed-point resize remediation produced limited improvement and still failed Gate D.
4. V3 changes only raw staging memory type and cannot resolve the observed CUDA resize numerical mismatch; V3 is skipped.
5. V4 depends on a correctness-qualified V3 candidate and is not applicable.
6. R3 formal performance experiments are not required for candidate selection after the negative correctness disposition and are skipped.
7. Stage Q INT8 V0 remains the selected candidate.
8. R3–R5 are skipped under this controlled disposition, and documentation-only R6 closeout is authorized.
9. No performance benefit may be claimed for V2, pinned memory, or double buffering.
10. Future work may investigate OpenCV-compatible CUDA resize, pinned staging, and limited overlap experiments; these are not current Stage R tasks.

影响范围：

- Stage R final classification;
- R3–R5 status and R6 documentation-only closeout;
- Stage Q INT8 V0 correctness and selected-candidate authority;
- Stage R paper tables and limitations.

本 Decision 不修改 D001–D085，不修改 Stage Q Evidence，不授权新的实现或 benchmark。

### D087 — Multi-Branch Ablation Reopening and Gate-D Metric Disposition

时间：

```text
2026-08-02
```

状态：

```text
ACCEPTED — Stage R multi-branch ablation reopening
```

背景：

Stage R 的执行模式调整为 `MULTI_BRANCH_ABLATION_MODE`。项目核心归宿为研究生
毕业论文、工程应用型论文和 Edge AI Deployment 求职项目。Experimental Integrity
和 Comparative Study 优先于单一 replacement Gate 的阶段阻断。本 Decision 不修改
D085/D086 的记录内容；D085/D086 作为 b008af7 时刻 replacement-selection 处置的
有效历史记录保留。

决策：

1. V2 Gate D 的 FAIL 与冻结阈值保持原样：不修改、不伪造 PASS。
2. V2 的状态调整为：

   ```text
   V2_ACCURACY_TRADE_OFF_BASELINE
   NOT CORRECTNESS-EQUIVALENT REPLACEMENT
   ```

3. Gate A/B/C 仍是实验有效性检查。
4. Gate D 调整为任务精度评价维度，不再作为阻断 V3/V4 的硬性进度屏障。
5. 授权继续：

   ```text
   V3: pinned raw staging
   V4: limited double buffering/overlap
   R3: V0/V2/V3/V4 comparative benchmark
   R5: performance-accuracy Pareto evaluation
   ```

6. Stage Q V0 继续作为正式 correctness-first baseline。
7. V3/V4 不需要重新证明 V2 与 OpenCV 的完全等价性。
8. 禁止修改 Gate D 阈值。
9. 禁止为了跨过 Gate D 再次修改 CUDA resize。
10. 最终论文必须同时报告性能收益、任务指标变化和实现复杂度。

准确记录（不得写成 V2 总精度只下降 `0.05%`）：

```text
Remediated V2 mAP50 absolute drop:
0.00537575
approximately 0.54 percentage points

Amount exceeding frozen 0.005 limit:
0.00037575
approximately 0.038 percentage points
```

理由：

- 单一 replacement Gate 的阶段阻断会掩盖多分支研究中的有效 trade-off 信息；
- V2 的精度代价是已定位、有界、可复现的（CUDA resize 插值数值差异），适合作为
  trade-off 基准而非研究终止条件；
- 保持 V0 作为 correctness-first baseline，同时允许 V2/V3/V4 作为 ablation
  分支进入比较研究，满足论文的 Comparative Study 需求；
- 明确禁止改写阈值、伪造 PASS 或再次修改 CUDA resize，保证 Experimental
  Integrity。

影响范围：

- Stage R 执行模式：MULTI_BRANCH_ABLATION_MODE；
- V2：V2_ACCURACY_TRADE_OFF_BASELINE，非 correctness-equivalent replacement；
- R2.3/V3：AUTHORIZED；
- V4：AUTHORIZED AFTER V3 FUNCTIONAL VALIDATION；
- R3：PENDING V3/V4 AVAILABILITY；
- Stage Q Evidence、Gate D 阈值、CUDA resize：UNCHANGED。

本 Decision 不修改 D001–D086 的历史记录，不修改 Stage Q Evidence，不修改 Gate D
阈值，不授权新的 CUDA resize remediation。
