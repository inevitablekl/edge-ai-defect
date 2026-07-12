# TASKS.md

## 1. 用途

本文档用于记录项目开发任务、迭代状态、每日进展、阻塞问题和后续计划。

项目名称：

**边缘 AI 工业缺陷检测部署与优化项目**

英文名称：

**Edge AI Industrial Defect Detection Deployment and Optimization**

本文档需要由 agent 在每天开发结束后，或每轮迭代完成后更新。

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
2026-07-12
```

当前阶段：

```text
YOLOv8n + NEU-DET 训练阶段完成，模型已冻结，进入 ONNX export 阶段
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
| ONNX Runtime C++ version   | TODO | C++ ONNX Runtime 集成前         |
| OpenCV version             | TODO | C++ 项目骨架创建前                  |
| CMake minimum version      | TODO | C++ 项目骨架创建前                  |
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
| INIT-004 | P0  | TODO | 创建 `include/edge_ai_defect/` 模块目录 |
| INIT-005 | P0  | DONE | 创建 `src/` 模块目录                    |
| INIT-006 | P0  | DONE | 创建 `experiments/` 子目录             |
| INIT-007 | P0  | TODO | 创建 `models/README.md`             |
| INIT-008 | P0  | TODO | 创建 `data/README.md`               |
| INIT-009 | P0  | DONE | 更新 `.gitignore`                   |
| INIT-010 | P0  | TODO | 初始化 top-level `CMakeLists.txt`    |

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
| EXPORT-001 | P0  | TODO | 编写 ONNX export 脚本                        |
| EXPORT-002 | P0  | TODO | 导出 320 输入尺寸 ONNX                         |
| EXPORT-003 | P0  | TODO | 导出 416 输入尺寸 ONNX                         |
| EXPORT-004 | P0  | TODO | 导出 640 输入尺寸 ONNX                         |
| EXPORT-005 | P0  | TODO | 记录 opset、shape、export command            |

---

### 6.5 C++ 部署任务

| ID      | 优先级 | 状态   | 任务                              |
| ------- | --- | ---- | ------------------------------- |
| CPP-001 | P0  | TODO | 初始化 C++ CMake 工程                |
| CPP-002 | P0  | TODO | 实现 `ConfigManager`              |
| CPP-003 | P0  | TODO | 实现 `FrameSource` image sequence |
| CPP-004 | P0  | TODO | 实现 `FrameSource` video file     |
| CPP-005 | P0  | TODO | 实现 `Preprocessor`               |
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

## 7. 每日 / 每轮迭代日志

### 2026-07-09 - 文档规范化迭代

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

### 2026-07-09 - 文档闭环与环境记录迭代

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

### 2026-07-09 - 第一阶段数据集与训练框架初始化

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

### 2026-07-10 - NEU-DET 到 YOLO 转换脚本实现

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

### 2026-07-10 - YOLOv8n 训练启动脚本与配置

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

### 2026-07-10 - 第一阶段正式训练前验证

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

### 2026-07-12 - NEU-DET 训练阶段完成与模型冻结

当前工作：

* 在 RTX 3090 上完成 V1～V6 及多 seed（seed=7、seed=123、seed=42 deterministic）共 9 组 YOLOv8n baseline 训练实验。
* 完成三 seed deterministic baseline 稳定性统计（mAP50-95 σ≈0.006）。
* 完成全部实验逐类别（6 类）validation AP50、AP50-95、Precision、Recall 指标提取。
* 依据 mAP50-95 和 Recall 优先的工程规则，选定 seed=7 deterministic 为最终冻结模型。
* 冻结模型路径：`models/pytorch/yolov8n_neudet_frozen.pt`，SHA256 已验证。
* 完成 frozen model 在 test split 上的最终评价（mAP50-95=0.431）。
* 生成训练实验汇总表（`results/training/training_experiment_summary.csv` / `.json`）。
* 生成训练最终报告（`docs/TRAINING_FINAL_REPORT.md`）和模型冻结记录（`docs/MODEL_FREEZE_RECORD.md`）。
* 创建训练阶段归档目录和压缩包。

修改文件：

* `configs/train/yolov8n_neudet_baseline_seed42_deterministic.yaml`（新增）
* `configs/train/yolov8n_neudet_v2.yaml` 等 V2～V6 配置（新增）
* `configs/train/yolov8n_neudet_baseline_seed7.yaml`、`_seed123.yaml`（新增）
* `models/pytorch/yolov8n_neudet_frozen.pt`（新增，Git 忽略）
* `docs/TRAINING_FINAL_REPORT.md`（新增）
* `docs/MODEL_FREEZE_RECORD.md`（新增）
* `results/training/training_experiment_summary.csv` / `.json`（新增）
* `scripts/extract_per_class_metrics.py`（训练时临时使用；最终证据入库后已删除）
* `scripts/run_seed42_deterministic_training.py`（训练时临时使用；最终收尾已删除，后续统一通过 `train_yolo.py`）
* `docs/personal/TASKS.md`、`EXPERIMENT_PLAN.md`、`DECISIONS.md`、`ENVIRONMENT.md`（更新）
* `.gitignore`（更新）

已完成：

* NEU-DET 转换和全量 label 校验完成（4186 个有效 bbox）。
* 本地 GTX 1050 Ti smoke test 完成。
* RTX 3090 多 seed 和有限训练策略实验全部完成。
* 所有实验 validation 指标（整体 + 六类别）完整提取，无估算数据。
* 模型冻结完成，SHA256 已验证。
* test split 最终评价完成（含 confusion matrix、PR/F1/P/R curves、预测图）。
* 训练阶段正式结束。

未完成：

* 尚未执行 ONNX export。
* 尚未执行 TensorRT 转换。
* 尚未开始 C++ ONNX Runtime / TensorRT 部署代码。

阻塞问题：

* 无阻塞。

下一步计划：

* 进入 ONNX export 与 ONNX Runtime 推理一致性验证阶段。
* 使用 frozen model 导出 ONNX（opset、动态/静态 shape 待定）。
* 验证 PyTorch vs ONNX Runtime 输出一致性。

备注：

* V2～V6 均未在 mAP50-95 上超过 baseline，训练阶段不继续扩大超参数搜索。
* seed=7 和 seed=42 deterministic 属于同一性能水平，选择基于工程规则而非统计显著差异。
* test split 结果仅用于最终报告，未用于模型选择。

---

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

### 2026-07-12 18:30 - 训练阶段最终审计收尾

当前工作：

* 修复统一训练入口的配置参数传递和运行摘要。
* 将轻量 effective args、validation/test 指标、命令和 provenance 纳入 Git。
* 参数化重构 evidence archive utility，并补充纯单元测试。
* 修正文档中的 deterministic、统计解释和实验变量描述。

已完成：

* 全部 9 组真实 `args.yaml` 确认为 `deterministic=true`。
* V2 记录为 configured 200 / completed 161；V3、V4 记录为关联参数组合实验；V5、V6 记录为严格单变量实验。
* test 摘要补充真实 `image_count=180`、`instance_count=442` 和来源说明。
* 删除重复且硬编码服务器路径的 seed42 训练脚本，后续统一使用 `scripts/train_yolo.py --config ...`。
* 冻结模型、原始训练归档和 evidence patch 继续作为 Git 外本地资产保存。

未完成：

* 尚未执行 ONNX export。
* 历史状态：当时 8 个非冻结 checkpoint 尚未进入离线归档；该状态已由下方 2026-07-12 最终归档记录取代。

阻塞问题：

* 训练阶段无阻塞；完成本轮提交后可合并 `main`。

下一步计划：

* 从更新后的 `main` 创建 `feature/onnx-export`。
* 使用冻结模型导出 ONNX，并执行 PyTorch / ONNX Runtime 输出一致性验证。

备注：

* 本轮未运行训练、validation、ONNX export 或 TensorRT。
* test split 未用于模型选择或训练调参。

---

### 2026-07-12 - 训练归档与 provenance 最终收尾

已完成：

* 原始 training stage archive、evidence patch 和 checkpoint patch 三组离线归档均已完成并通过外部 SHA256 与内部 MANIFEST 校验。
* 全部 9 个正式实验的 `best.pt` 已归档并校验，9 个 checkpoint 哈希均唯一；seed=7 checkpoint 与 frozen model 哈希一致。
* Git 中的轻量 provenance 已更新为 checkpoint archive 名称、成员路径、大小和真实 SHA256，不依赖服务器绝对路径定位。
* 本地 Git、冻结模型和三组归档已覆盖全部必须保留的训练资产，训练服务器不再保存唯一必要资产。
* 训练阶段证据链收尾完成，无需继续训练或 validation。

下一步计划：

* 合并训练阶段分支后，从更新后的 `main` 创建 `feature/onnx-export`。
* 使用 frozen model 执行 ONNX export，并验证 PyTorch / ONNX Runtime 输出一致性。

备注：

* 模型权重和三组归档继续保留在 Git 之外。
* 后续部署主线只使用 `models/pytorch/yolov8n_neudet_frozen.pt`。

---

## 8. Agent 更新规则

每次 agent 更新本文档时，应遵守以下规则：

1. 不删除历史日志。
2. 每次追加新的时间戳条目。
3. 中文描述当前进展。
4. 专业术语保留英文原文。
5. 明确写出：

   * 本轮完成了什么。
   * 修改了哪些文件。
   * 当前是否有 blocking issue。
   * 下一步计划是什么。
6. 如果任务完成，更新对应任务状态为 `DONE`。
7. 如果任务受阻，更新状态为 `BLOCKED` 并说明原因。
8. 不得把未完成任务标记为 `DONE`。
9. 不得伪造实验数据。
10. 不得替用户做未经确认的重大技术决策。

---

## 9. 标准迭代记录模板

```markdown
### YYYY-MM-DD HH:mm - 本轮迭代标题

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

---

## 10. 当前最近计划

近期优先级：

1. 合并训练阶段最终收尾提交到 `main`。
2. 从 `main` 创建 `feature/onnx-export`。
3. 使用冻结模型导出 ONNX，并记录 opset、shape 和导出环境。
4. 验证 PyTorch 与 ONNX Runtime 的预处理、输出和后处理一致性。
