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
