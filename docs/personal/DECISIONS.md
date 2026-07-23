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
