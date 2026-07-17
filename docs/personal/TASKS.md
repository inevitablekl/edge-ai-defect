# TASKS.md

## 1. 用途

本文档用于记录项目开发任务、迭代状态、每日进展、阻塞问题和后续计划。

项目名称：

**边缘 AI 工业缺陷检测部署与优化项目**

英文名称：

**Edge AI Industrial Defect Detection Deployment and Optimization**

本文档由 agent 在每天开发结束时统一更新一次；同一天的多轮迭代必须归并到同一条日记录。

记录形式要求：

- 使用时间戳。
- 使用中文描述。
- 专业术语保留英文原文，例如 `ONNX Runtime`、`TensorRT FP16`、`SerialRunner`、`PipelineRunner`。
- 只记录真实发生的进展，不编造完成状态。
- 不删除历史记录，只追加或在任务状态表中更新状态。

---

## 2. 状态标记

| 状态 | 含义 |
|---|---|
| TODO | 尚未开始 |
| IN_PROGRESS | 正在进行 |
| BLOCKED | 被阻塞 |
| DONE | 已完成 |
| CANCELED | 已取消 |
| DEFERRED | 延后处理 |

---

## 3. 优先级标记

| 优先级 | 含义 |
|---|---|
| P0 | 核心主线，必须完成 |
| P1 | 重要功能，建议完成 |
| P2 | 辅助功能，可后续完成 |
| P3 | 扩展功能，非 v1 必需 |

---

## 4. 当前项目快照

更新时间：

```text
2026-07-18
```

当前阶段：

```text
M1.1～M1.6 已全部完成，M1 Core Contracts + CPU Preprocessor 阶段正式关闭；M2 尚未开始
```

当前主线：

```text
NEU-DET
→ YOLOv8n
→ ONNX
→ C++ ONNX Runtime baseline
→ C++ TensorRT FP16
→ Serial / Pipeline comparison
→ CSV / JSON experiment logs
```

当前已确定信息：

| 项目项               | 当前决策                              |
| ----------------- | --------------------------------- |
| 主数据集              | NEU-DET                           |
| 主模型               | YOLOv8n                           |
| 数据集划分             | train / val / test = 70 / 20 / 10 |
| 输入尺寸              | 320, 416, 640                     |
| 训练语言              | Python                            |
| 部署语言              | C++                               |
| 配置格式              | YAML                              |
| 构建系统              | CMake                             |
| baseline backend  | ONNX Runtime                      |
| optimized backend | TensorRT FP16                     |
| runtime modes     | Serial, Pipeline                  |
| v1 GUI            | 不实现                               |
| v1 ROS2           | 只预留接口                             |
| INT8              | 后续可选，不进入当前主线                      |

---

## 5. 当前待确认事项

| 事项                         | 状态   | 决策时机                         |
| -------------------------- | ---- | ---------------------------- |
| Jetson 具体型号                | TODO | 本地 ONNX Runtime baseline 跑通后 |
| JetPack version            | TODO | Jetson 型号确定后                 |
| CUDA version               | TODO | JetPack version 确定后          |
| TensorRT version           | TODO | JetPack version 确定后          |
| ONNX Runtime C++ version   | DONE | 已冻结并验证为 1.23.2              |
| OpenCV version             | DONE | C++ 4.5.4；Python 4.10.0       |
| CMake minimum version      | DONE | 已冻结为 3.16                    |
| TensorRT engine 生成方式       | TODO | Jetson TensorRT 部署前          |
| Resource monitoring method | TODO | 性能实验前                        |

---

## 6. 任务总览

### 6.1 文档任务

| ID      | 优先级 | 状态          | 任务                      |
| ------- | --- | ----------- | ----------------------- |
| DOC-001 | P0  | DONE        | 确定 `AGENTS.md`          |
| DOC-002 | P0  | DONE        | 确定 `PROJECT_BRIEF.md`   |
| DOC-003 | P0  | DONE        | 确定 `REQUIREMENTS.md`    |
| DOC-004 | P0  | DONE        | 确定 `ARCHITECTURE.md`    |
| DOC-005 | P0  | DONE        | 确定 `CODING_RULES.md`    |
| DOC-006 | P0  | DONE        | 确定 `TASKS.md`           |
| DOC-007 | P0  | DONE        | 确定 `EXPERIMENT_PLAN.md` |
| DOC-008 | P0  | DONE        | 确定 `DECISIONS.md`       |
| DOC-009 | P1  | TODO        | 确定 `DATASET.md`         |
| DOC-010 | P1  | DONE        | 确定 `ENVIRONMENT.md`     |
| DOC-011 | P1  | TODO        | 初始化 `PROGRESS_LOG.md`   |
| DOC-012 | P1  | DONE        | 编写 `BASELINE_TRAINING.md` |

---

### 6.2 仓库与工程骨架任务

| ID       | 优先级 | 状态   | 任务                                |
| -------- | --- | ---- | --------------------------------- |
| INIT-001 | P0  | DONE | 按确定目录结构整理仓库                       |
| INIT-002 | P0  | DONE | 创建 `configs/` 目录                  |
| INIT-003 | P0  | DONE | 创建 `scripts/` 子目录                 |
| INIT-004 | P0  | DONE | 创建 `include/edge_ai_defect/` 模块目录 |
| INIT-005 | P0  | DONE | 创建 `src/` 模块目录                    |
| INIT-006 | P0  | DONE | 创建 `experiments/` 子目录             |
| INIT-007 | P0  | TODO | 创建 `models/README.md`             |
| INIT-008 | P0  | TODO | 创建 `data/README.md`               |
| INIT-009 | P0  | DONE | 更新 `.gitignore`                   |
| INIT-010 | P0  | DONE | 初始化 top-level `CMakeLists.txt`    |

---

### 6.3 数据集任务

| ID       | 优先级 | 状态   | 任务                                      |
| -------- | --- | ---- | --------------------------------------- |
| DATA-001 | P0  | DONE | 获取 NEU-DET 数据集                          |
| DATA-002 | P0  | DONE | 明确 NEU-DET 原始目录格式                       |
| DATA-003 | P0  | DONE | 实现 NEU-DET 到 YOLO 格式转换脚本                |
| DATA-004 | P0  | DONE | 实现 train / val / test = 70 / 20 / 10 划分 |
| DATA-005 | P0  | DONE | 生成 `dataset.yaml`                       |
| DATA-006 | P0  | DONE | 记录类别、数量、random seed                     |
| DATA-007 | P1  | DONE | 检查缺失 label 和无效 annotation               |
| DATA-008 | P1  | DONE | 清理并记录完全重复 YOLO bbox                     |

---

### 6.4 训练与导出任务

| ID         | 优先级 | 状态   | 任务                                       |
| ---------- | --- | ---- | ---------------------------------------- |
| TRAIN-001  | P0  | DONE | 编写 YOLOv8n 训练脚本                          |
| TRAIN-002  | P0  | DONE | 在 RTX 3090 上训练 YOLOv8n                   |
| TRAIN-003  | P0  | DONE | 记录 Precision、Recall、mAP@0.5、mAP@0.5:0.95 |
| TRAIN-004  | P0  | DONE | 保存 `best.pt`                             |
| TRAIN-005  | P0  | DONE | 建立项目 `.venv` 并固定 Python 训练依赖             |
| TRAIN-006  | P0  | DONE | 完成本地 YOLOv8n smoke training 链路验证           |
| TRAIN-007  | P0  | DONE | 冻结 NEU-DET baseline 配置并通过 dry-run          |
| EXPORT-001 | P0  | DONE | 编写 ONNX export 脚本                        |
| EXPORT-002 | P0  | TODO | 导出 320 输入尺寸 ONNX                         |
| EXPORT-003 | P0  | TODO | 导出 416 输入尺寸 ONNX                         |
| EXPORT-004 | P0  | DONE | 导出 640 输入尺寸 ONNX                         |
| EXPORT-005 | P0  | DONE | 记录 opset、shape、export metadata           |
| EXPORT-006 | P0  | DONE | 完成 ONNX checker 与 ONNX Runtime smoke test  |
| EXPORT-007 | P0  | DONE | 完成 PyTorch vs ONNX Runtime 一致性验证          |
| EXPORT-008 | P1  | DONE | 检查 TensorRT Python validation 环境           |

---

### 6.5 C++ 部署任务

| ID      | 优先级 | 状态   | 任务                              |
| ------- | --- | ---- | ------------------------------- |
| CPP-001 | P0  | DONE | 初始化 C++ CMake 工程                |
| CPP-002 | P0  | TODO | 实现 `ConfigManager`              |
| CPP-003 | P0  | TODO | 实现 `FrameSource` image sequence |
| CPP-004 | P0  | TODO | 实现 `FrameSource` video file     |
| CPP-005 | P0  | DONE | 实现 `Preprocessor`               |
| CPP-006 | P0  | TODO | 定义 `InferenceEngine` 抽象接口       |
| CPP-007 | P0  | TODO | 实现 `ONNXRuntimeEngine`          |
| CPP-008 | P0  | TODO | 实现 `PostProcessor`              |
| CPP-009 | P0  | TODO | 实现 `Profiler`                   |
| CPP-010 | P0  | TODO | 实现 `ResultSink`                 |
| CPP-011 | P0  | TODO | 实现 `SerialRunner`               |
| CPP-012 | P1  | TODO | 实现 `PipelineRunner`             |
| CPP-013 | P0  | TODO | 实现 command-line app             |
| CPP-014 | P0  | TODO | 完成本地 ONNX Runtime baseline 验证   |
| CPP-015 | P0  | TODO | 实现 `TensorRTEngine`             |
| CPP-016 | P0  | TODO | 完成 Jetson TensorRT FP16 验证      |

---

### 6.6 实验任务

| ID      | 优先级 | 状态   | 任务                                  |
| ------- | --- | ---- | ----------------------------------- |
| EXP-001 | P0  | DONE | 完成模型精度实验                            |
| EXP-002 | P0  | TODO | 完成 ONNX Runtime vs TensorRT FP16 对比 |
| EXP-003 | P0  | TODO | 完成 Serial vs Pipeline 对比            |
| EXP-004 | P0  | TODO | 完成 320 / 416 / 640 输入尺寸对比           |
| EXP-005 | P1  | TODO | 完成 10 分钟稳定性测试                       |
| EXP-006 | P1  | TODO | 完成 30 分钟稳定性测试                       |
| EXP-007 | P1  | TODO | 完成 60 分钟稳定性测试                       |
| EXP-008 | P0  | TODO | 生成 CSV / JSON 实验日志                  |
| EXP-009 | P1  | TODO | 生成论文表格和图表                           |

---

## 7. 每日进展日志

### 2026-07-09 - 文档规范化、文档闭环与数据训练框架初始化

#### 文档规范化迭代

当前工作：

* 根据项目定位重新压缩并规范核心文档。
* 明确 `AGENTS.md`、`PROJECT_BRIEF.md`、`REQUIREMENTS.md`、`ARCHITECTURE.md`、`CODING_RULES.md` 的内容边界。
* 确定文档原则：只保留稳定、核心、全局信息。
* 确定 `TASKS.md` 用于每天或每轮迭代记录开发状态。
* 确定记录形式：时间戳 + 中文；专业术语保留英文原文。

已完成：

* `AGENTS.md` 初版内容已生成。
* `PROJECT_BRIEF.md` 初版内容已生成。
* `REQUIREMENTS.md` 初版内容已生成。
* `ARCHITECTURE.md` 初版内容已生成。
* `CODING_RULES.md` 初版内容已生成。
* `TASKS.md` 当前版本已生成。

当前状态：

```text
项目仍处于文档与工程骨架准备阶段，尚未进入正式编码阶段。
```

下一步建议：

* 将以上文档写入仓库。
* 让 agent 检查文档之间是否存在冲突。
* 提交一次 git commit。
* 继续生成 `EXPERIMENT_PLAN.md` 和 `DECISIONS.md`。

阻塞问题：

```text
暂无阻塞。
```

---

#### 文档闭环与环境记录迭代

当前工作：

* 统一 agent 约束文档中关于 `docs/personal/` 的记录路径。
* 新增 `docs/personal/ENVIRONMENT.md`，作为环境信息和实验复现环境的记录入口。
* 修正新增文档中的 Markdown 代码块格式。
* 更新文档任务和已完成仓库初始化任务状态。

修改文件：

* `AGENTS.md`
* `docs/ARCHITECTURE.md`
* `docs/REQUIREMENTS.md`
* `docs/CODING_RULES.md`
* `docs/personal/DECISIONS.md`
* `docs/personal/EXPERIMENT_PLAN.md`
* `docs/personal/ENVIRONMENT.md`
* `docs/personal/TASKS.md`

已完成：

* `CODING_RULES.md`、`DECISIONS.md`、`TASKS.md`、`EXPERIMENT_PLAN.md` 和 `ENVIRONMENT.md` 已形成当前文档闭环。
* `AGENTS.md` 已明确文档优先级和 personal 文档路径。
* 实验环境记录规则已建立。

未完成：

* `DATASET.md` 尚未创建。
* `PROGRESS_LOG.md` 尚未初始化。
* `CMakeLists.txt` 尚未初始化。

阻塞问题：

* 暂无阻塞。

下一步计划：

* 创建 `include/edge_ai_defect/` 模块目录。
* 创建 `models/README.md` 和 `data/README.md`。
* 初始化 CMake 工程骨架。

备注：

* 当前仍处于文档与工程骨架准备阶段，尚未进入正式编码阶段。

---

#### 第一阶段数据集与训练框架初始化

当前工作：

* 创建 `feature/dataset-training` 分支。
* 初始化数据集、训练配置、训练实验和模型 artifact 的基础目录。
* 新增 NEU-DET 到 YOLO 转换脚本骨架。
* 新增 YOLOv8n 训练启动与实验记录脚本骨架。
* 补充 `.gitignore`，忽略数据集、权重、训练缓存和大文件输出。

修改文件：

* `.gitignore`
* `scripts/convert_neudet_to_yolo.py`
* `scripts/train_yolo.py`
* `configs/dataset/.gitkeep`
* `configs/train/.gitkeep`
* `data/interim/.gitkeep`
* `data/yolo/.gitkeep`
* `experiments/training/.gitkeep`
* `models/pytorch/.gitkeep`

已完成：

* 第一阶段目录结构已建立。
* 转换脚本支持参数解析、路径校验、YOLO 输出目录规划和 manifest 记录框架。
* 训练脚本支持 dry-run、实验目录创建、git commit、环境信息、训练命令和配置快照记录框架。

未完成：

* 尚未实现 NEU-DET annotation 解析与实际 label 转换。
* 尚未创建真实训练配置。
* 尚未运行训练。
* 尚未生成任何真实训练结果。

阻塞问题：

* 需要人工提供 NEU-DET 原始数据集路径。
* 需要确认 NEU-DET 原始目录结构和类别顺序。

下一步计划：

* 根据人工提供的数据集路径和目录结构实现 annotation parser。
* 创建 `configs/dataset/` 和 `configs/train/` 下的最小 YAML 配置。
* 在确认数据后生成 `data/yolo/neu_det/dataset.yaml`。

备注：

* 本轮没有下载数据集，没有运行训练，没有生成伪造结果。

---

### 2026-07-10 - 数据转换、训练配置与正式训练前验证

#### NEU-DET 到 YOLO 转换脚本实现

当前工作：

* 补全 `scripts/convert_neudet_to_yolo.py`。
* 按 NEU-DET 原始 `IMAGES/` 和 `ANNOTATIONS/` 目录读取图片与 Pascal VOC XML annotation。
* 实现 bbox 到 YOLO `class_id x_center y_center width height` 的归一化转换。
* 实现固定 random seed 的 train / val / test = 70 / 20 / 10 划分。
* 实现图片复制、label 写入、`dataset.yaml` 和 `conversion_manifest.json` 生成。
* 保留 `--dry-run`，dry-run 只输出统计，不写文件。

修改文件：

* `scripts/convert_neudet_to_yolo.py`
* `docs/personal/TASKS.md`

已完成：

* 转换脚本已经从骨架变为可执行转换工具。
* manifest 记录 `image_count`、`bbox_count`、`class_count`、`split_seed`、`split_counts` 和 class counts。
* 缺失图片、未知类别、缺失 bbox、越界 bbox、空 annotation 会显式失败。

未完成：

* 尚未使用真实 NEU-DET 数据集运行转换。
* 尚未人工确认本地 NEU-DET 数据集路径。

阻塞问题：

* 需要人工提供 NEU-DET 原始数据集路径。

下一步计划：

* 使用真实 NEU-DET 路径执行 dry-run。
* dry-run 统计无误后执行实际转换，生成 `data/yolo/neu_det/`。

备注：

* 本轮没有下载数据集，没有运行训练，没有伪造任何结果。

---

#### YOLOv8n 训练启动脚本与配置

当前工作：

* 新增 `configs/train/yolov8n_neudet_smoke.yaml`。
* 新增 `configs/train/yolov8n_neudet_640.yaml`。
* 完善 `scripts/train_yolo.py`，改为读取 YAML 配置驱动训练命令。
* 支持 `--dry-run`，只检查配置和打印计划命令，不创建实验目录、不启动训练。
* 支持 `--smoke`，覆盖 `epochs=1`、`imgsz=320`、`batch=2`。
* 预留正式运行时的实验目录、配置快照、命令、git commit、环境、起止时间和 summary 记录。

修改文件：

* `configs/train/yolov8n_neudet_smoke.yaml`
* `configs/train/yolov8n_neudet_640.yaml`
* `scripts/train_yolo.py`
* `docs/personal/TASKS.md`

已完成：

* 训练启动流程已具备可复现记录结构。
* 训练参数从 YAML 读取，脚本不硬编码 epochs、imgsz、batch、dataset path 等训练参数。
* `dataset.yaml` 缺失时会显式报错，不会自动伪造。

未完成：

* 尚未运行正式训练。
* 尚未产生 Precision、Recall、mAP 或权重文件。
* 尚未保存 `best.pt`。

阻塞问题：

* 需要先完成真实 NEU-DET 到 YOLO 转换，生成 `data/yolo/neu_det/dataset.yaml`。

下一步计划：

* 使用真实 `dataset.yaml` 执行 `--dry-run`。
* 在训练环境准备完成后使用 smoke 配置验证训练链路。
* smoke 通过后再执行 640 正式训练配置。

备注：

* 本轮没有下载数据集，没有运行训练，没有生成假结果，没有提交权重文件。

---

#### 第一阶段正式训练前验证

当前工作：

* 检查 `scripts/convert_neudet_to_yolo.py` 的 CLI、dry-run、输出目录、`dataset.yaml` 和 `conversion_manifest.json`。
* 检查 `scripts/train_yolo.py` 的 YAML 配置读取、dry-run、smoke 覆盖和实验记录逻辑。
* 检查 `configs/train/*.yaml` 是否使用相对路径，适合本地 dry-run 和服务器训练。
* 检查 `.gitignore` 是否忽略数据集、权重、runs、训练输出和大文件。
* 使用 `/tmp` 临时样例验证转换 dry-run、转换输出、训练 dry-run 和 smoke dry-run。

修改文件：

* `docs/personal/TASKS.md`

已完成：

* `convert_neudet_to_yolo.py` dry-run 不写输出目录。
* 转换脚本真实输出会生成 `images/train|val|test`、`labels/train|val|test`、`dataset.yaml` 和 `conversion_manifest.json`。
* `train_yolo.py` 在 `dataset.yaml` 缺失时会清晰报错。
* `train_yolo.py --dry-run` 和 `--smoke` 在临时配置下只打印计划命令，不创建实验目录，不启动训练。
* 未发现硬编码绝对路径、Windows 路径或服务器私有路径。
* `.gitignore` 已覆盖权重、ONNX、runs、`experiments/training/**` 和数据集输出。

未完成：

* 尚未使用真实 NEU-DET 数据集执行转换。
* 尚未运行 smoke training。
* 尚未运行 baseline training。

阻塞问题：

* 需要人工提供真实 NEU-DET 数据集路径。

下一步计划：

* 真实数据到位后先执行 conversion dry-run。
* dry-run 统计无误后执行实际转换。
* 转换完成后执行 training dry-run 和 smoke training。

备注：

* 本轮没有下载数据集，没有运行正式训练，没有生成伪造结果。

---

### 2026-07-11 - NEU-DET 数据冻结与 baseline 训练前准备

当前工作：

* 使用真实 `data/raw/NEU-DET` 完成数据转换、重复 bbox 清理和全量 label 校验。
* 建立项目级 `.venv`，固定 Python、PyTorch、Ultralytics、NumPy、Matplotlib 等依赖版本。
* 在 GTX 1050 Ti 上完成 `epochs=1`、`imgsz=320`、`batch=2` 的本地 smoke training。
* 冻结 `configs/train/yolov8n_neudet_baseline.yaml`，并完成正式训练命令 dry-run。
* 调整训练实验记录与 Git 管理规则，保留轻量复现信息，忽略权重、缓存和大型输出。

修改文件：

* `.gitignore`
* `scripts/convert_neudet_to_yolo.py`
* `scripts/train_yolo.py`
* `configs/train/yolov8n_neudet_smoke.yaml`
* `configs/train/yolov8n_neudet_640.yaml`
* `configs/train/yolov8n_neudet_baseline.yaml`
* `requirements.txt`
* `requirements-lock.txt`
* `environment_snapshot.txt`
* `docs/BASELINE_TRAINING.md`
* `experiments/training/README.md`
* `docs/personal/TASKS.md`
* `docs/personal/EXPERIMENT_PLAN.md`
* `docs/personal/ENVIRONMENT.md`

已完成：

* 数据集包含 1800 张图片，划分为 train 1260、val 360、test 180。
* 原始转换统计为 4189 个 bbox；删除 3 个完全重复 bbox 后冻结为 4186 个。
* 全量 YOLO label 校验结果为 `errors=0`，不存在重复 label 行。
* `.venv` 中 PyTorch CUDA、cuDNN 和 Ultralytics 导入及依赖检查通过。
* 最新隔离环境 smoke run 状态为 `completed`、return code 为 0；该结果仅验证训练链路，不作为正式 baseline 结果。
* baseline 配置固定为 YOLOv8n、640、100 epochs、seed 42、`amp=false`。
* baseline dry-run 已通过，未启动正式训练。

未完成：

* 尚未在 RTX 3090 上执行正式 baseline training。
* 尚未产生正式 baseline 的 Precision、Recall、mAP 或 `best.pt`。
* 尚未执行 ONNX export。

阻塞问题：

* 代码与数据准备无阻塞。
* 正式训练需要在 RTX 3090 环境中确认依赖和显存后执行。

下一步计划：

* 在 RTX 3090 训练环境中安装 `requirements-lock.txt`。
* 执行 baseline dry-run，确认 GPU、路径和 `batch=16`。
* 使用冻结配置运行正式 baseline，并保存真实实验记录和 `best.pt`。
* 正式训练完成后进入 ONNX export。

备注：

* 一次早期 smoke 尝试因 NumPy / Matplotlib 环境冲突失败，失败记录保留；随后在独立 `.venv` 中验证成功。
* 本轮没有运行正式 baseline，没有上传数据，没有提交数据集或权重文件。

---

### 2026-07-12 - 训练阶段完成、模型冻结与证据归档收尾

当日工作：

* 在 RTX 3090 上完成 V1～V6、seed=7、seed=123 和 seed=42 deterministic 共 9 组 YOLOv8n 正式训练实验。
* 完成三 seed deterministic baseline 稳定性统计及全部实验的总体、六类别 validation 指标整理。
* 依据预先约定的 mAP50-95 和 Recall 工程规则选择 seed=7，并冻结为 `models/pytorch/yolov8n_neudet_frozen.pt`。
* 完成 frozen model 的 held-out test split 最终评价、训练报告、模型冻结记录和机器可读实验汇总。
* 修复统一训练入口的参数传递与运行摘要，整理 effective args、validation/test 指标、命令和 provenance。
* 完成 training stage archive、evidence patch 和 checkpoint patch 三组 Git 外离线归档及最终删除前审计。

主要产出：

* 训练配置：V1～V6 及三组 seed baseline 配置。
* 训练汇总：`results/training/training_experiment_summary.csv` / `.json`。
* 训练证据：`results/training/evidence/` 下的 9 组 effective args、validation/test JSON/CSV、命令和 provenance。
* 最终文档：`docs/TRAINING_FINAL_REPORT.md`、`docs/MODEL_FREEZE_RECORD.md`、`docs/TRAINING_ARCHIVE_INDEX.md`。
* 统一入口：`scripts/train_yolo.py`；训练时临时使用的重复脚本和一次性指标提取脚本已删除。
* 冻结模型：`models/pytorch/yolov8n_neudet_frozen.pt`（Git 忽略）。
* 三组离线归档：training stage archive、evidence patch、checkpoint patch（均不进入 Git）。

完成情况：

* 9 组真实 `args.yaml` 均确认 `deterministic=true`。
* V2 记录为 configured 200 / completed 161；V3 同时改变 `mosaic` 和 `close_mosaic`；V4 同时改变 optimizer 和 `lr0`；V5、V6 为单变量实验。
* V2～V6 均未证明相对 baseline 有稳定提升，训练阶段不继续扩大超参数搜索。
* seed=7 与 seed=42 deterministic 属于同一性能水平；seed=7 是工程规则选择，不宣称统计显著优胜。
* Frozen model SHA256 已验证；test split 最终评价完成，且结果未反向用于训练、调参或模型选择。
* Test evidence 已记录 `image_count=180`、`instance_count=442`、六类别指标和真实来源。
* 全部 9 个正式实验的 `best.pt` 已归档并校验，9 个 checkpoint SHA256 均唯一；seed=7 checkpoint 与 frozen model 完全一致。
* 三组离线归档均通过外部 SHA256 和内部 MANIFEST 校验。
* 本地 Git、冻结模型和离线归档已覆盖全部必须保留的训练资产，训练服务器不再是任何必要资产的唯一来源。
* 训练阶段和证据链正式收尾，无需继续训练或 validation。

当日修正说明：

* 统一训练入口已正确传递 `False`、`0` 和 `0.0` 等有效配置值，并区分 configured/completed/last/best epoch 与指标。
* Evidence archive utility 已参数化、fail-fast、默认不覆盖，且不会启动训练、validation 或修改 Git。
* 删除硬编码服务器路径和重复训练逻辑的 seed42 临时脚本。
* 文档已修正 deterministic、实验变量、统计解释、test gap 及 checkpoint 归档状态。
* 轻量测试全部通过；收尾过程未重新运行训练、validation、ONNX export 或 TensorRT。

尚未完成：

* ONNX export。
* PyTorch / ONNX Runtime 输出一致性验证。
* C++ ONNX Runtime baseline、TensorRT FP16 和 Jetson 部署。
* Serial / Pipeline 性能实验。

阻塞问题：

* 训练阶段无阻塞。
* 后续部署阶段按更新后的 `main` 继续推进。

下一步计划：

* 合并训练阶段分支后，从更新后的 `main` 创建 `feature/onnx-export`。
* 使用唯一标准输入 frozen model 导出 ONNX，并记录 opset、shape 和导出环境。
* 验证 PyTorch 与 ONNX Runtime 的预处理、输出和后处理一致性。
* 完成 ONNX Runtime baseline 后再进入 TensorRT FP16 与 Serial / Pipeline 实验。

备注：

* Git 只保存轻量代码、配置、指标、文档和 provenance，不保存模型权重、数据集、实验图片或离线归档。
* 非冻结 checkpoint 仅用于离线审计或必要时重新 validation，不参与后续模型选择和部署。
* 三组归档应至少保留两份独立本地副本。

---

### 2026-07-13 - ONNX export 与 ONNX Runtime validation 阶段完成

当前工作：

* 使用唯一 frozen model 完成 640 静态输入 ONNX export，并核对源模型 SHA256。
* 完成 ONNX 文件存在性检查、`onnx.checker`、输入输出节点检查和 export provenance 记录。
* 使用 CPU `ONNX Runtime` 完成一次 dummy input smoke inference。
* 在 10 张 validation 图片上使用共享 preprocess / postprocess 完成 PyTorch 与 ONNX Runtime 一致性验证。
* 检查当前 WSL2 开发环境的 TensorRT Python、CUDA runtime 和 GPU 可用性。

修改文件：

* `scripts/export_onnx.py`、`configs/export/yolov8n_neudet_frozen.yaml`。
* `tools/validation/onnxruntime_smoke_test.py`、`tools/validation/compare_pt_onnx.py`。
* `tests/test_export_onnx.py`、`tests/test_onnxruntime_smoke_test.py`、`tests/test_compare_pt_onnx.py`。
* `results/onnx_export/` 下的 export metadata、environment provenance、smoke test 和 consistency validation JSON。
* `requirements.txt`、`requirements-lock.txt`。

已完成：

* `models/pytorch/yolov8n_neudet_frozen.pt` 已导出为 `models/onnx/yolov8n_neudet_frozen.onnx`；模型文件继续由 Git 忽略。
* ONNX checker 通过；模型 input 为 `float32 [1, 3, 640, 640]`，output 为 `float32 [1, 10, 8400]`。
* ONNX Runtime smoke test 通过，输出非空且不包含 NaN / Inf。
* PyTorch vs ONNX Runtime 一致性验证通过：10 张图片逐图 detection count 和 class 一致，raw output 与 bbox / confidence 误差均在预先记录的容差内。
* ONNX export 和 validation 的模型 SHA256、软件版本、时间戳、输入输出信息与数值统计均已写入轻量 JSON evidence。
* TensorRT Python 环境检查已完成：当前 `.venv` 缺少 `tensorrt` binding，且 WSL2 中 GPU / NVML 不可访问，因此未执行 TensorRT FP16 Python sanity validation，也未修改系统 CUDA、驱动或 TensorRT。

未完成：

* C++ ONNX Runtime baseline。
* TensorRT backend 与 TensorRT FP16 validation。
* Jetson 部署。
* Serial / Pipeline 实现和性能实验。

阻塞问题：

* C++ ONNX Runtime 开发主线无新增阻塞，待确定 C++ 依赖版本并初始化工程骨架。
* TensorRT validation 需要 Jetson 或具备完整、可访问 CUDA / TensorRT 环境的平台；当前 WSL2 开发机不作为 TensorRT 验证平台。

下一步计划：

* 使用 C++17、OpenCV、yaml-cpp 和 ONNX Runtime C++ API 建立本地 baseline。
* 保持 `InferenceEngine` backend 解耦，先完成 Serial mode，再完成 Pipeline mode。
* 在目标平台确定后实现 TensorRT FP16 backend，并在 Jetson 上完成论文性能实验。

备注：

* 本阶段只完成格式导出、可加载性和数值一致性验证，没有执行 FPS、latency、mAP 或稳定性性能实验。
* 项目总体路线仍为 ONNX Runtime baseline → TensorRT FP16 optimized backend → Jetson deployment。

---

### 2026-07-15 - C++ ONNX Runtime Serial Baseline 阶段启动准备完成

当前工作：

- 进入 `feature/cpp-onnxruntime` 分支的 M0：工程与依赖初始化阶段。

已完成：

- `feature/cpp-onnxruntime` 分支已创建。
- frozen ONNX model contract 已冻结。
- Python reference semantics 已完成源码级核查。
- C++ 架构方案已完成审查。

当前任务：

- M0：建立 CMake 工程与 CTest 基础。
- 接入 ONNX Runtime C++ 1.23.2 CPU Linux x64。
- 建立 `edge_ai_core`、`edge_ai_backend_ort` 和 `edge_ai_infer` targets。
- 完成 runtime smoke test。

后续阶段：

- M1：Core contract + Preprocessor。
- M2：ONNX Runtime Engine。
- M3：PostProcessor。
- M4：完整 Serial Baseline。
- M5：独立 benchmark 分支。

当前不开发：

- TensorRT、Jetson、Pipeline、ROS2、Qt、INT8 或 GPU 优化。

---

### 2026-07-16 - M0 收尾与 M1 执行计划冻结

#### M0.2 ONNX Runtime C++ SDK 依赖接入完成

已完成：

- M0.1 已建立 C++17、CMake、CTest 最小工程骨架及 `edge_ai_core`、`edge_ai_backend_ort`、`edge_ai_infer`、`test_core` targets。
- 下载官方 `onnxruntime-linux-x64-1.23.2.tgz`，记录本地 archive SHA256：`1fa4dcaef22f6f7d5cd81b28c2800414350c10116f5fdd46a2160082551c5f9b`。
- SDK 已解压到 `third_party/onnxruntime/1.23.2/linux-x64/`，archive 与 payload 均由 Git 忽略。
- CMake 已通过 `ONNXRUNTIME_ROOT`、`onnxruntime::onnxruntime` imported target 和 target 级 build RPATH 接入 SDK。
- `edge_ai_backend_ort` 已建立对 imported target 的构建依赖。
- SDK header、shared library、符号链接和 `ldd` 已验证，动态依赖无 `not found`。
- 无效 `ONNXRUNTIME_ROOT` 负向配置测试通过；有效 root 下 configure、build、CTest 和最小可执行程序均通过。

待执行：

- M0.3：调用 ONNX Runtime C++ API，验证 runtime version 和 CPU Provider。

边界：

- M0.2 未调用 ORT API，未加载 frozen ONNX，未执行推理，也未创建 ORT smoke test 或正式 `OnnxRuntimeEngine`。

---

#### M0.3 ONNX Runtime C++ API smoke 完成

已完成：

- 新增测试专用 `test_ort_runtime_smoke` target 和 `ort_runtime_smoke` CTest，仅位于 `tests/smoke/`。
- 实际 ONNX Runtime C++ runtime version 精确验证为 `1.23.2`。
- 实际 available Provider 完整列表为 `CPUExecutionProvider`，完全匹配检查通过。
- `Ort::Env` 和 `Ort::SessionOptions` 创建与销毁通过。
- smoke executable 通过 build RUNPATH 动态加载项目 SDK 的 `libonnxruntime.so.1.23.2`，unset `LD_LIBRARY_PATH` 后仍可运行。
- 错误期望版本 `0.0.0` 的负向比较返回非零，版本不一致路径通过。
- 原有 `test_core`、生产 target 和 `edge_ai_defect` 继续通过。

待执行：

- M0.4：frozen ONNX model loading 与 contract smoke。

边界：

- M0.3 未创建 `Ort::Session`，未加载模型，未创建 tensor，未执行推理，也未创建正式 `OnnxRuntimeEngine`。

---

#### M0.4 Frozen ONNX model contract smoke 完成

已完成：

- frozen ONNX 文件大小 `12242487` bytes 与 SHA256 `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944` 已核对。
- 新增默认关闭的 `EDGE_AI_ENABLE_MODEL_SMOKE` 资产测试开关和 `EDGE_AI_FROZEN_ONNX_PATH` cache path；关闭时普通无模型资产构建继续通过。
- 新增测试专用 `test_ort_model_contract_smoke` target，以及 positive、missing-model、contract-mismatch 三个 CTest。
- `Ort::Session` 成功加载 frozen ONNX；input 为 `images` / `float32` / `[1,3,640,640]`，output 为 `output0` / `float32` / `[1,10,8400]`。
- 输入输出数量均为 1，所有维度均为静态正数，完整合同验证通过。
- 不存在模型路径的预期加载失败被正确捕获；故意设置 `wrong_images` 的 input name mismatch 被正确检测。
- 原有 `test_core`、`ort_runtime_smoke`、生产 targets 和 `edge_ai_defect` 继续通过。

待执行：

- M0.5：常量 synthetic tensor 的真实 CPU inference smoke。

边界：

- M0.4 只完成模型加载和 metadata 合同验证；未创建输入 tensor，未调用 `Session::Run`，未读取输出，也未执行推理或性能测试。

---

#### M0.5A M0.4 负向测试加固完成

已完成：

- missing-model 仅在 `Ort::Exception::GetOrtErrorCode()` 精确为 `ORT_NO_SUCHFILE` 时通过；当前实际错误码为 `3`。
- contract-mismatch 改为结构化 `field`、`expected`、`actual` 判断，不再使用错误消息子串匹配。
- metadata 查询在调用 tensor shape API 前显式检查 `ONNX_TYPE_TENSOR`。
- 抽取 `tests/smoke/` 内部 `edge_ai_ort_smoke_support`，仅复用 metadata 与合同校验代码。
- 原有五个 CTest 全部通过，未创建 tensor 或执行推理。

边界：

- 测试 helper 未进入 public include 或生产 target，不形成正式 `ModelContract`、`TensorInfo`、`Status` 或 backend API。

---

#### M0.5 Frozen ONNX synthetic inference smoke 完成

已完成：

- 新增测试专用 `test_ort_inference_smoke` target 和 `ort_inference_smoke` CTest，仅在模型资产开关开启时建立。
- 使用 `float32 [1,3,640,640]`、`1228800` 个常量 `0.5F` 创建 CPU input tensor。
- 默认 ONNX Runtime CPU Session 单次同步 `Session::Run` 成功。
- 输出为 `float32 [1,10,8400]`、`84000` elements。
- 输出 finite count 为 `84000`，NaN、正 infinity、负 infinity count 均为 `0`。
- model smoke OFF 构建继续通过；正式 M0.5 CTest 为 6/6 通过。
- unset `LD_LIBRARY_PATH` 后独立 inference smoke 通过，动态链接解析到项目 ONNX Runtime SDK。

待执行：

- M0.6：M0 阶段完整收尾、文档复核与 checkpoint。

边界：

- 本阶段只证明 C++ ONNX Runtime CPU 能执行一次真实 frozen model synthetic inference。
- 未进行计时、warm-up、FPS 或性能实验，未建立正式 `OnnxRuntimeEngine`，不描述为正式 Serial Baseline。

---

#### M0.6 最终回归与阶段收尾完成

已完成：

- M0.0～M0.5 的工程骨架、依赖接入、runtime smoke、模型合同与 synthetic inference smoke 已全部完成。
- Model Smoke OFF 独立干净构建成功，只注册并通过 `test_core` 和 `ort_runtime_smoke`，结果为 2/2。
- Model Smoke ON 正式干净构建成功，当前六个 CTest 精确发现并全部通过，结果为 6/6。
- ONNX Runtime C++ runtime version 为 `1.23.2`，`CPUExecutionProvider` 验证通过。
- Frozen ONNX input/output 合同、missing-model、结构化 contract-mismatch 和 synthetic inference 均独立验证通过。
- synthetic inference 输出 `84000` 个元素全部 finite，NaN、正 infinity、负 infinity 均为 `0`。
- runtime 与 inference smoke 的动态链接均解析到项目内 ONNX Runtime 1.23.2 SDK，无 `not found`。
- 无效 ORT root、空模型路径和不存在模型路径均以预期的明确配置错误失败。
- 资产 provenance、代码边界、Git 跟踪与 ignore 状态复核通过。
- M0 阶段正式关闭。

当前边界：

- 当前生产程序仍为 C++ runtime skeleton，`edge_ai_backend_ort` 仍为占位 target，正式 backend 尚未实现。
- 下一阶段为 M1 Core Contract + Preprocessor；M1 尚未开始。
- 当前没有正式 `OnnxRuntimeEngine`、Serial Baseline 或性能数据。
- 当前不进入 TensorRT、Pipeline、ROS2、Qt 或性能 benchmark。

结论：

- M0 工程、依赖与真实模型 smoke 验证完成，可进入 M1。

---

#### M1.0 仓库预检与执行计划冻结完成

已完成：

- 完整复核 M0 后的 CMake、生产骨架、测试结构和阶段边界；M0 已关闭，M1 生产模块尚未开始。
- 当前 OpenCV C++ `4.5.4` 与 yaml-cpp `0.7.0` 均通过 C++17 最小编译、链接和运行验证，未安装或升级系统依赖。
- 确认当前没有正式可供 C++ 读取的 model contract；M1.2 唯一路径冻结为 `configs/model_contracts/yolov8n_neudet_frozen.yaml`。
- 核对 Python preprocessing reference、LetterBox 实际参数、round/padding、颜色/layout/normalization 和 EXIF orientation 行为。
- 确认当前没有独立 Level A generator、manifest、synthetic assets、tensor golden 或 validation report。
- 创建 `docs/personal/M1_EXECUTION_PLAN.md`，冻结 M1.1～M1.6、Gate、通用规则及 M1.1 精确边界。

下一步：

- M1.1 Core Contracts；本轮未实现任何 C++ 生产模块，未进入 M1.1。

边界：

- 正式 `OnnxRuntimeEngine`、postprocess/NMS、SerialRunner、benchmark、Pipeline、TensorRT、ROS2 和 Qt 均不属于 M1。

---

### 2026-07-17 - M1.2 Frozen Model Contract 深度 Gate 通过

已完成：

- M1.1 Core Contracts 已完成，提供 `Status`、`TensorInfo`、`HostTensor` 和安全 element count。
- M1.2 已创建正式 Git-tracked contract：`configs/model_contracts/yolov8n_neudet_frozen.yaml`。
- `ModelContract`、严格 `ModelContractLoader` 与 yaml-cpp `0.7.0` target 级接入已完成。
- `test_model_contract` 共 43 个用例全部通过；Model Smoke OFF 的 CTest 为 3/3 通过。
- 深度 Gate 完成 public API、所有权、严格 schema、duplicate key、错误传播、权威边界、依赖边界和复杂度审查，判定为 `PASS WITH DOCUMENTATION CHANGES`。

当前边界：

- 当前正式生产能力仅为 core contracts 与 model contract loader。
- `Preprocessor`、LetterBox、正式 `OnnxRuntimeEngine` 和后续 runtime 模块均未实现。
- 今日暂停，不进入 M1.3。

下一步：

- 明日按独立任务执行 M1.3 LetterBox Geometry；M1.3 当前尚未开始。

---

### 2026-07-18 - M1 CPU Preprocessing 阶段关闭

当前工作：

- 完成 M1.3～M1.6 的最终验收汇总、证据硬化、完整回归和阶段文档关闭。

修改文件：

- 测试侧 Level A manifest/parser/validator、数值比较 helper、CMake 验证脚本与
  provenance generator/evidence。
- `docs/personal/M1_EXECUTION_PLAN.md`、`TASKS.md`、`ENVIRONMENT.md` 和
  `DECISIONS.md`。

已完成：

- M1.1 Core Contracts、M1.2 Frozen Model Contract、M1.3 LetterBox、M1.4
  CPU `Preprocessor`、M1.5 Level A Validation 与 M1.6 Closeout 全部完成。
- 当前 production 能力为 `Status`/tensor contracts、严格 `ModelContract`
  loader、LetterBox 与连续 `float32 NCHW` CPU `Preprocessor`。
- Level A A～H 共 8 个 case 全部通过，Python OpenCV `4.10.0` 与 C++ OpenCV
  `4.5.4` 的 MAE/max_abs 均为 `0`；正式 report 逐字节复核一致。
- 新增实际资产→`SHA256SUMS`→manifest digest 自动闭环、resolved realpath
  containment、non-finite numeric guard 和 stable provenance 验证。
- 最终 Model Smoke OFF 为 10/10，Model Smoke ON 为 14/14，strict 为 10/10，
  ASan/UBSan 为 10/10；ModelContract 43/43 与 ORT runtime smoke 继续通过。
- M1 阶段正式关闭，所有提交均为本地提交，未执行 `git push`。

未完成：

- 正式 `OnnxRuntimeEngine`、`SerialRunner`、完整 inference loop 与性能实验尚未实现。
- M2 尚未开始。

阻塞问题：

- 暂无 M2 前的已知代码阻断项。

下一步计划：

- 以独立任务启动 M2 `ONNX Runtime Engine` 的设计与实现。
- 继续保持 TensorRT、Pipeline、ROS2、Qt 和 benchmark 在当前范围之外。

备注：

- M1 测试 helper 只链接测试 target，不进入 production target。
- 当前 `edge_ai_defect` 仍为 runtime skeleton，不宣称 C++ inference baseline 已闭环。

---

## 8. 当前最近计划

近期优先级：

1. M0 与 M1 已完成并正式关闭。
2. 当前 production 能力止于 core contracts、model contract loader、LetterBox
   与 CPU `Preprocessor`。
3. 下一任务为 M2 `ONNX Runtime Engine`；M2 尚未开始。
4. 正式 `SerialRunner`、完整 Serial Baseline 和性能实验继续按后续阶段执行。
5. TensorRT、Pipeline、ROS2 和 Qt 当前不进入开发范围。

---

## 9. Agent 更新规则

每次 agent 更新本文档时，应遵守以下规则：

1. 不删除跨日期的历史日志；每个自然日只保留一条 `### YYYY-MM-DD` 日记录。
2. 同一天的新增进展必须归并到当天记录；确需区分阶段时使用 `####` 子标题，不按小时或任务反复追加同级日期记录。
3. 跨日期时新增一条日记录，并保持日期顺序。
4. 中文描述当前进展。
5. 专业术语保留英文原文。
6. 明确写出：

   * 本轮完成了什么。
   * 修改了哪些文件。
   * 当前是否有 blocking issue。
   * 下一步计划是什么。
7. 如果任务完成，更新对应任务状态为 `DONE`。
8. 如果任务受阻，更新状态为 `BLOCKED` 并说明原因。
9. 不得把未完成任务标记为 `DONE`。
10. 不得伪造实验数据。
11. 不得替用户做未经确认的重大技术决策。

---

## 10. 标准每日记录模板

```markdown
### YYYY-MM-DD - 当日进展标题

当前工作：

-

修改文件：

-

已完成：

-

未完成：

-

阻塞问题：

-

下一步计划：

-

备注：

-
```
