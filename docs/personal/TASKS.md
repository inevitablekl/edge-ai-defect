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
2026-07-19
```

当前阶段：

```text
M0、M1、M2、M3、M4 已关闭；M4.6 first Gate FAIL、remediation complete、Gate rerun PASS；M4.7 documentation-only closeout complete。
M5 Pre-Planning Discovery Audit 已完成；M5.0 Planning Freeze COMPLETE；M5.1 COMPLETE；M5.2A COMPLETE；M5.2B COMPLETE；Formal Level C comparison PASS；第一次 M5.2 Level C Gate FAIL；Gate remediation COMPLETE；Gate rerun PASS；M5.2 overall COMPLETE；M5.3 COMPLETE；M5.4 COMPLETE；M5.5 COMPLETE；M5.6 Gate Rerun PASS；M5.7 COMPLETE；M5 Level C Validation and WSL2 ORT CPU Engineering Baseline 已 CLOSED。
```

M2 状态：

- M2.0 Design Freeze：complete。
- M2.1 Contract：complete。
- M2.2 Session initialization：complete。
- M2.3 Run path：complete。
- M2.4 Boundary hardening：complete。
- M2.5 Level B validation：complete。
- M2.6 closeout：complete；M2 CLOSED。

M3 状态：

- M3.0 PostProcessor repository audit and design freeze：complete。
- M3.1 Detection / PostProcessor contract：complete。
- M3.2 candidate decode：complete。
- M3.3 IoU / class-aware NMS：complete。
- M3.4 inverse LetterBox / clipping / public process integration：complete。
- M3.4 shallow Gate：complete。
- M3.5 PostProcessor-only Validation：complete。
- M3 Deep Gate remediation：complete。
- M3 Deep Gate Rerun：PASS；M3 CLOSED。
- 最终回归：Model Smoke OFF 17/17 PASS；Model Smoke ON 24/24 PASS。
- Strict、ASan、UBSan：`Not configured`，未记录为 PASS。

M4 状态：

- M4.0 Planning Freeze：complete。
- M4.1 Runtime Contracts, Config and CLI Parser：complete。
- M4.2 ImageSource and DirectorySource：complete。
- M4.3 ResultSink System：complete。
- M4.4 SerialRunner and Basic Timing：complete；M4.4 Shallow Gate：first FAIL，test/documentation remediation complete，rerun PASS；M4.4 COMPLETE。
- M4.5 Application Assembly and Actual ORT Smoke：complete。
- M4.6 Standard Final Gate：first FAIL；production architecture PASS，blocker 为 application subprocess 测试证据缺口；
  test/documentation remediation complete（`1bc0260fd88530e1d44ee8dc8042d7103cb7e571`），Gate rerun PASS。
- M4.7 Documentation-only Closeout：complete；M4 CLOSED。
- M4.1 已新增 runtime contracts、strict YAML RuntimeConfigLoader、CLI parser 和对应测试；M4.2 已新增
  deterministic non-recursive DirectorySource；M4.3 已新增 deterministic Console/JSON/Composite ResultSink。
  已新增 SerialRunner；M4.5 已将 main 替换为 actual application composition 并完成实际 ORT smoke。
- Strict、ASan、UBSan：保持当前真实状态 `Not configured`。

M5 状态：

- M5.0 Planning Freeze：complete。
- M5.1 Corpus Assets and Validation Contract：complete。
- M5.2A Harness Implementation：complete。
- M5.2B Formal Evidence Generation：complete；Formal Level C evidence 已生成，comparison PASS。
- M5.2 Level C Reference, Comparator and Formal Validation：complete。
- M5.2 Level C Gate：第一次 `FAIL`；remediation `COMPLETE`；Gate rerun `PASS`；M5.2 overall `COMPLETE`。
- M5.3 Benchmark Harness and Offline Analyzer：complete。
- M5.4 Formal WSL2 ORT CPU Baseline Execution：complete；正式 Evidence 已生成。
- M5.5 Evidence Consolidation：首次生成已完成，但 `20260719_c24eefa` 因 provenance command_records 不完整而标记为
  `historical_invalidated_consolidation`，保留且不修改。
- M5.5 Planning Freeze Remediation：`COMPLETE`；已冻结 generation-time Git snapshot、旧 Evidence 失效/保留规则、新
  source commit/新 Evidence ID、15 条 command_records 和 commands 一对一、stable regeneration 合同。
- M5.5 Consolidation Remediation Generation：`COMPLETE`；active consolidation 为
  `results/consolidation/m5/20260719_da86e53/`，包含 15/15 provenance records 和 stable regeneration PASS；未重跑正式
  benchmark。
- M5.6 Deep Evidence Gate Rerun：`PASS`；active consolidation 已通过只读 Gate。
- M5.7 Documentation-Only Closeout：`COMPLETE`。
- M5：`CLOSED`。
- Level C Gate rerun 已 `PASS`，documentation-only 状态已固化；正式 Level C 与 benchmark Evidence 均已生成并完成 consolidation。
- Strict、ASan、UBSan：保持 `Not configured`，不因 M5.1 改变。

下一阶段：

```text
Jetson/TensorRT planning（下一阶段入口；`PENDING`，尚未开始）
```

M5.5 首次预审曾在修改文件前 `STOPPED`：原计划未冻结 consolidation 目录、文件集合、schema、summary 和
`sha256sums` 规则，分类为 `M5.5 evidence consolidation planning gap`，不是执行失败。本次 Planning Freeze
Remediation 已完成并新增 D040，冻结路径 `results/consolidation/m5/<evidence_id>/`、固定六文件、三个 JSON
schema version 1、README/commands/SHA 规则、staging 后单次 rename、失效边界和 `26214400` bytes retention；本次
remediation planning freeze 进一步冻结 generation-time Git snapshot、旧 consolidation historical invalidated 规则、
15 条独立 command_records、commands 一对一和 stable regeneration 输入。第一次 M5.6 Deep Evidence Gate 的唯一 blocker
为 `20260719_c24eefa` provenance command_records `6/15`，其余底层 Evidence、重建、合同、corpus、privacy、asset、
retention 和 CTest 均 PASS。旧目录保留但不可作为 Gate PASS 依据；本轮 planning freeze 后已基于新 clean committed HEAD
`da86e53` 生成 active consolidation `results/consolidation/m5/20260719_da86e53/`，15/15 records、commands 一对一、
stable regeneration 和发布后 SHA 均 PASS。随后 M5.6 Deep Evidence Gate Rerun 判定 `PASS`；本轮 closeout 不重新运行
application、benchmark、build、CTest 或 Evidence 重建。M5.7 已完成，M5 正式关闭；下一阶段仅按冻结计划保持 `PENDING`。

M5.7 Documentation-Only Closeout（2026-07-19）：

- M5.6 Gate Rerun：`PASS`；旧 `20260719_c24eefa` 保持 `historical_invalidated_consolidation`；active consolidation 为
  `results/consolidation/m5/20260719_da86e53/`；
- Level C Evidence：`results/validation/level_c/20260719_1073fa8/`；Benchmark Evidence：
  `results/benchmark/ort_cpu/20260719_850252b/`；
- M5.0～M5.5：`COMPLETE`；M5.7：`COMPLETE`；M5：`CLOSED`；
- Strict/ASan/UBSan：`Not configured`；本轮未重新运行 build、CTest、Comparator、application、Pilot 或 benchmark；
- M5 仅证明冻结 corpus 上的 Level C 正确性和 WSL2 x86_64 ORT CPU 工程基线，不代表 Jetson、TensorRT、生产实时或最终
  部署性能；
- 下一阶段入口为冻结的 Jetson/TensorRT planning，保持 `PENDING`，尚未开始。

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
| CPP-006 | P0  | DONE | 定义 `InferenceEngine` 抽象接口       |
| CPP-007 | P0  | DONE | 实现 `ONNXRuntimeEngine`          |
| CPP-008 | P0  | DONE | 实现 `PostProcessor`              |
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

#### M2.6 ONNX Runtime Engine 阶段关闭

当前工作：

- 完成 M2 Gate closeout 文档、任务状态与决策记录；未修改 production C++、接口、
  CMake 或测试逻辑。

修改文件：

- `docs/personal/M2_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`
- `docs/personal/DECISIONS.md`

已完成：

- M2.0 Design Freeze、M2.1 Inference contract、M2.2 ORT Session initialization、
  M2.3 ORT Run path、M2.4 Boundary hardening、M2.5 Level B validation 和 M2.6
  closeout 均已完成；M2 正式关闭。
- 最终回归：Model Smoke OFF 为 11/11 CTest PASS；Model Smoke ON 为 18/18 CTest
  PASS。
- strict 与 ASan/UBSan 在当前工程中均为 `Not configured`；未执行且未写成通过。
- M2 已提供 contract-validated CPU synchronous `OnnxRuntimeEngine`、owned
  `HostTensor` I/O、negative/boundary tests 与 Python/C++ Level B raw-output
  evidence，不包含 postprocess 或完整 runner。

未完成：

- `PostProcessor`、NMS、`Detection`、`SerialRunner`、`Pipeline`、Profiler、
  benchmark、TensorRT、CUDA、GPU EP、ROS2 和 Qt 均不属于 M2，尚未实现。

阻塞问题：

- M2 closeout 无阻塞。strict/ASan/UBSan 未配置是当前回归矩阵限制，不构成已通过的
  sanitizer/strict 证据。

下一步计划：

- 进入 M3 `PostProcessor` preparation，先冻结 raw output 解码、置信度阈值和 NMS
  的设计/验证边界；不得回改 M2 Engine contract。

#### M3.0 PostProcessor 仓库事实审计与设计冻结

当前工作：

- 读取 M2 closed 后的 model contract、core tensor/LetterBox、Engine interface、Python
  PT/ONNX reference、M2 Level B evidence、CMake 和 tests，完成 M3 semantic audit。

修改文件：

- `docs/personal/M3_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`
- `docs/personal/DECISIONS.md`

已完成：

- 冻结 output 为 `float32 BCN [1,10,8400]`：0～3 为 `cx,cy,w,h`，4～9 为六类分数；
  无 objectness、无 embedded NMS，类别顺序与 frozen `ModelContract` 一致。
- 冻结最小 concrete `PostProcessor`、original-image `Detection` coordinate contract、
  `ImageTransformMetadata` inverse LetterBox、strict confidence/NMS/排序/原子性语义。
- 冻结 M3 PostProcessor-only Python/C++ Level B evidence 方案；现有 PT/ONNX shared
  NMS comparison 不能替代该独立验证。

未完成：

- `Detection`/`PostProcessor` production contract、decode、NMS、tests、M3 evidence 和
  M3 closeout 尚未实现；未进入 M4 Runner 或 M5 benchmark。

阻塞问题：

- 无 M3.1 前的代码阻塞项。当前 Python reference 未冻结 equal-score candidate tie，
  已在 M3 plan 中以独立 reference/canonical tie-break 解决，不能复用现有 shared-NMS
  script 作为 M3 evidence。

下一步计划：

- 执行 M3.1，只定义 `Detection` 和 concrete `PostProcessor` contracts 及必要 target；
  不实现 decode、NMS 或 M4 模块。

#### M3.1 Detection / PostProcessor contract

当前工作：

- 建立 M3 public types、配置验证、`edge_ai_postprocess` target 和 contract-level test。

修改文件：

- `include/edge_ai_defect/postprocess/detection.hpp`
- `include/edge_ai_defect/postprocess/postprocess_config.hpp`
- `include/edge_ai_defect/postprocess/postprocessor.hpp`
- `src/postprocess_config.cpp`
- `src/postprocessor.cpp`
- `tests/test_postprocessor_contract.cpp`
- `CMakeLists.txt`
- `docs/personal/M3_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- 定义 original-image continuous xyxy `Detection`、冻结 defaults 的
  `PostprocessConfig` 和最小配置合法性验证。
- 定义 concrete `PostProcessor::process()` signature；保持普通 value copy/move，未
  创建 `IPostProcessor`、pImpl 或 backend abstraction。
- 补充连续 bbox 面积无 `+1`、clip 闭区间、使用 metadata 已保存 gain/left/top 和
  class-offset NMS 的精确定义。
- 新 target 只显式依赖 `edge_ai_core`；未链接 ORT/TensorRT/CUDA/OpenCV DNN。
- Model Smoke OFF configure/build 完成；contract/core 定向 CTest 2/2 PASS，完整 CTest
  12/12 PASS。

未完成：

- `process()` 尚无 definition；candidate decode、confidence filter、IoU、NMS、inverse
  LetterBox、clipping 和 8400-candidate tests 均未实现。

阻塞问题：

- 无 M3.2 前代码阻塞。strict 与 ASan/UBSan 仍未配置，是后续工程债务，不能记录为已
  通过。

下一步计划：

- 执行 M3.2 candidate decode，只实现 raw tensor validation、candidate parsing、
  confidence filter 和 deterministic pre-NMS ordering；NMS 留给 M3.3。

#### M3.2 YOLO raw candidate decode 与 deterministic pre-NMS preparation

当前工作：

- 实现 internal `DecodedCandidate`、固定 raw BCN decode、class argmax、confidence
  filter、model-space xyxy、deterministic sort 与 `max_nms` truncation。

修改文件：

- `src/postprocess_detail.hpp`
- `src/postprocessor_decode.cpp`
- `tests/test_postprocessor_decode.cpp`
- `CMakeLists.txt`
- `docs/personal/M3_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- 严格接受 `float32 BCN [1,10,8400]` / 84000 elements；任一 raw NaN、`+Inf`、`-Inf`
  返回 `kInvalidArgument` 且不污染 caller output。
- `w/h <= 0` 仅跳过 candidate；class score 用严格 `>` argmax，tie 选择最小 class id；
  confidence 必须严格大于 threshold。
- 固定 `data[channel * 8400 + candidate_index]` BCN 索引、continuous model-space xyxy、
  confidence/class/candidate 的完整 deterministic order 和 sorted `max_nms` 截断。
- 新 decode test 覆盖 raw contract、BCN/BNC 区分、边界、ties、排序、geometry、empty
  success 和 output atomicity；未实现 IoU、NMS、class offset、inverse LetterBox、clip 或
  public `PostProcessor::process()`。
- Model Smoke OFF configure/build 成功；定向 CTest 3/3 PASS，完整 CTest 13/13 PASS。

未完成：

- IoU、class-aware NMS、`max_det` 应用、inverse LetterBox、clipping、public Detection
  输出和 M3 Level B evidence 尚未实现。

阻塞问题：

- 无 M3.3 前代码阻塞。strict 与 ASan/UBSan 仍为 `Not configured`，不能记录为通过。

下一步计划：

- 执行 M3.3，只实现 continuous xyxy IoU 和 class-aware NMS，消费 M3.2 已排序的
  internal candidates；仍不实现 inverse LetterBox 或 public `process()`。

#### M3.3 continuous xyxy IoU 与 deterministic class-aware greedy NMS

当前工作：

- 在不改变 M3.2 decode/排序语义的前提下，实现 internal continuous IoU、temporary
  class offset、greedy NMS 及其边界测试。

修改文件：

- `src/postprocess_detail.hpp`
- `src/postprocessor_nms.cpp`
- `tests/test_postprocessor_nms.cpp`
- `CMakeLists.txt`
- `docs/personal/M3_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- 冻结并实现 continuous xyxy IoU：交集/面积无 inclusive-pixel `+1`；zero/invalid union
  或 non-finite geometry 产生 `0.0F` IoU。
- NMS 直接消费 canonical-sorted candidates，不重新排序；仅当
  `IoU > iou_threshold` 时抑制，达到 `max_det` 时停止，输出保持 canonical retain order。
- 对比较临时使用 `class_id * max_wh` 加到全部 xyxy coordinate；不同类不相互抑制，返回
  candidate 坐标不包含 offset。
- 防御性限制处理到 `min(size, max_nms)`；配置或 internal candidate 非法时返回
  `kInvalidArgument`，不污染 caller output。
- Model Smoke OFF configure/build 成功；M3/core 定向 CTest 4/4 PASS，完整 CTest
  14/14 PASS。strict 与 ASan/UBSan 仍为 `Not configured`。

未完成：

- inverse LetterBox、clipping、public `Detection` conversion、
  `PostProcessor::process()` definition 和 M3 PostProcessor-only Level B evidence 均未实现。

阻塞问题：

- 无 M3.4 前代码阻塞。strict 与 ASan/UBSan 未配置，不能记录为通过。

下一步计划：

- 执行 M3.4，仅完成基于 `ImageTransformMetadata` 的 inverse LetterBox、clip 与 public
  `PostProcessor::process()` integration；不进入 Runner、Pipeline、benchmark 或 M3 Level B。

#### M3.4 inverse LetterBox、continuous clipping 与 public process integration

当前工作：

- 先解决 M3 plan 与固定 Ultralytics 8.4.50 `scale_boxes()/clip_boxes()` 的 post-clip
  degeneracy conflict，再完成 metadata-driven public PostProcessor pipeline。

修改文件：

- `src/postprocess_detail.hpp`
- `src/postprocessor.cpp`
- `src/postprocessor_transform.cpp`
- `tests/test_postprocessor_process.cpp`
- `CMakeLists.txt`
- `docs/personal/M3_EXECUTION_PLAN.md`
- `docs/personal/DECISIONS.md`
- `docs/personal/TASKS.md`

已完成：

- 追加 D027：M3 baseline 按固定 Ultralytics 8.4.50 parity 只做 continuous coordinate clamp；
  post-clip 零宽/零高 `Detection` 保留，不做 minimum-size filter。decode 阶段负/零 `w/h`
  skip 与 xyxy overflow skip 维持不变。
- 使用 M1 实际 `ImageTransformMetadata` 的 original/target/resized dimensions、`double gain`
  与四侧 padding 验证 transform，并直接按保存的 `gain`、`pad_left`、`pad_top` 执行 inverse
  LetterBox；不依据 image dimensions 重新推导参数。
- 实现完整 public `PostProcessor::process()`：config/metadata validation → decode → NMS →
  transform/clip → original-image `Detection`。每个 failure path 保持 caller output，empty
  valid result 成功返回 empty vector。
- 新 process test 覆盖 asymmetric odd padding、clipping 后的四侧退化框保留、NMS-before-
  transform、class-aware integration、strict confidence、limits、invalid raw/metadata/config、
  null output 和 atomicity。
- Model Smoke OFF configure/build 成功；M3/core 定向 CTest 5/5 PASS，完整 CTest 15/15 PASS。
  strict、ASan、UBSan 仍为 `Not configured`。

未完成：

- M3.4 shallow Gate 与 M3.5 独立 Python/C++ PostProcessor-only Level B validation；未实现
  Runner、Pipeline、benchmark、TensorRT 或 CUDA。

阻塞问题：

- 无 shallow Gate 前代码阻塞。strict 与 ASan/UBSan 未配置，不能记录为通过。

下一步计划：

- 执行 M3.4 shallow Gate，只读审查范围、public process 行为、reference parity 语义、测试
  证据和 Git cleanliness；通过后才启动 M3.5。

#### M3.5 PostProcessor-only Validation

当前工作：

- 建立独立 NumPy Python reference、deterministic synthetic BCN assets、public C++
  `PostProcessor::process()` TSV comparison 和 tracked provenance；不调用 ORT/Preprocessor/
  Engine，也不将其称为 Level C。

修改文件：

- `tests/data/postprocessor_reference/`
- `results/validation/postprocessor_only/`
- `tools/validation/generate_postprocessor_reference_assets.py`
- `tools/validation/postprocessor_reference.py`
- `tools/validation/generate_postprocessor_reference_provenance.py`
- `tests/test_postprocessor_reference.cpp`
- `CMakeLists.txt`
- `docs/personal/M3_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- 固定 no-padding、M1 horizontal odd-padding 和 M1 vertical odd-padding 三个 case；覆盖
  decode/argmax/threshold/order、class-aware NMS、candidate provenance、metadata actual padding、
  continuous clipping 与 post-clip zero-width/zero-height retain。
- Python reference 仅使用 standard library/NumPy，显式复现 C++ float32 decode/NMS arithmetic、
  double transform promotion 与最终 float32 cast；不调用 Ultralytics 后处理或 C++ detail API。
- C++ validator 只调用 public `PostProcessor::process()`，逐项比较完整 ordered Detection；三个
  case 的 count/class/order/candidate index/finite 均一致，confidence 和 bbox max/mean abs
  均为 0，满足 `1e-6` / `1e-4` 冻结阈值。
- 生成器/reference 在独立临时目录重复运行，raw 与 golden SHA256 全部与 tracked assets
  一致；provenance 记录环境、Git、命令、阈值和所有 evidence 文件 SHA256。
- Model Smoke OFF configure/build 成功；M3/core/reference 定向 CTest 6/6 PASS，完整 CTest
  16/16 PASS。strict、ASan、UBSan 仍为 `Not configured`。

未完成：

- 重新执行 M3 Deep Gate、M3 closeout；未进入 Runner、Pipeline、benchmark、TensorRT、CUDA 或
  Serial Baseline/Level C。

阻塞问题：

- 等待重跑 M3 Deep Gate。strict 与 ASan/UBSan 未配置，不能记录为通过。

下一步计划：

- 重新执行 M3 Deep Gate，只读审查 M3.0～M3.5 scope、production semantics、independent evidence、
  provenance、regression 和 remaining scope；通过后才考虑 M3 closeout。

#### M4.0 C++ ONNX Runtime Serial Baseline 计划冻结

当前工作：

- 在 M3 `CLOSED` 起点完成 production modules、public headers、targets、tests、validation tools、
  configs 和 executable skeleton 的事实审计。
- 冻结 M4 新增 RuntimeConfig、DirectorySource、ResultSink、SerialRunner、基础计时、CLI、
  runtime JSON schema、应用组装和 M4/M5 边界。

修改文件：

- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`
- `docs/personal/DECISIONS.md`

已完成：

- 创建可由后续独立 Codex 对话直接执行的 M4.0～M4.7 task cards；每张卡均包含 objective、
  starting facts、allowed/forbidden scope、planned files、contracts、tests、acceptance、commit、next step 和 Gate。
- 确认当前可直接复用 M1 `Preprocessor`、M2 `IInferenceEngine`/`OnnxRuntimeEngine` 和 M3
  `PostProcessor`；当前 `edge_ai_infer` 仍只是 skeleton。
- 确认 RuntimeConfig/ImageSource/DirectorySource/ResultSink/SerialRunner/Profiler 均尚不存在；
  production C++ 未使用 JSON library。
- 冻结 M4.4 后 Shallow Gate、M4.6 Standard Final Gate、M4.7 documentation-only closeout；M4 不做 Deep Gate。

未完成：

- M4.1 及所有 M4 production code、tests、CMake/runtime configs/assets 均未开始。

阻塞问题：

- 无 M4.1 前已知架构冲突。

下一步计划：

- 仅执行 M4.1 Runtime Contracts, Config and CLI Parser；不得自动进入 M4.2。

备注：

- M4 基础 `FrameTimings` 不属于正式 benchmark；完整 Level C、Profiler 和 ORT 性能基线属于 M5。
- 本轮不运行 CTest，不执行 `git push`。

#### M4.1 Runtime Contracts, Config and CLI Parser

当前工作：

- 实现 runtime value contracts、strict YAML `RuntimeConfigLoader` 和最小 CLI parser；不实现
  ImageSource、ResultSink、SerialRunner 或真实 application flow。

修改文件：

- `include/edge_ai_defect/runtime/runtime_types.hpp`
- `include/edge_ai_defect/runtime/runtime_config.hpp`
- `include/edge_ai_defect/runtime/cli.hpp`
- `src/runtime_config.cpp`
- `src/cli.cpp`
- `tests/test_runtime_config.cpp`
- `tests/test_cli.cpp`
- `tests/test_runtime_types.cpp`
- `CMakeLists.txt`
- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- RuntimeConfig schema version 1 严格要求全部 section/field，拒绝 unknown/duplicate key、缺失字段、
  错误 mapping/scalar type、非法 backend/input type 与空 path；内部相对路径相对配置文件目录解析并
  `lexically_normal()`。
- Loader 只解析、验证和解析路径；不会加载 model、初始化 Engine、打开目录或创建 sink；全部 failure
  保持 caller RuntimeConfig 原值。
- CLI 只接受 `edge_ai_defect --config <runtime.yaml>` 或单独 `edge_ai_defect --help` 的参数语义；
  library parser 返回 `Status` 和 action，不处理 process exit code。
- 新增 `FrameTimings`、`RunMetadata`、`FrameResult`、`RunSummary`，并保持 M3 Detection/
  PostprocessConfig value contracts 的既有定义。
- Model Smoke ON 全量 CTest：27/27 PASS；独立 Model Smoke OFF 全量 CTest：20/20 PASS。

未完成：

- ImageSource、DirectorySource、ResultSink、SerialRunner、main application assembly 和 actual M4
  serial runtime smoke 均未开始。

阻塞问题：

- 无 M4.2 前已知阻塞。

下一步计划：

- 仅执行 M4.2 ImageSource and DirectorySource；不得提前创建 ResultSink、SerialRunner 或完整 main。

备注：

- Strict、ASan、UBSan 仍为 `Not configured`；没有 benchmark、TensorRT、CUDA、Pipeline、ROS2 或图片读取实现。

#### M4.2 ImageSource and DirectorySource

当前工作：

- 实现最小 `ImageSource`、`ImageItem` 和 deterministic `DirectorySource`；不实现 ResultSink、
  SerialRunner、main application assembly 或 ORT 调用。

修改文件：

- `include/edge_ai_defect/runtime/image_source.hpp`
- `include/edge_ai_defect/runtime/directory_source.hpp`
- `src/directory_source.cpp`
- `tests/test_directory_source.cpp`
- `CMakeLists.txt`
- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- DirectorySource factory 只枚举第一层真实 regular image file，不递归并跳过所有 symlink；支持
  `.jpg`、`.jpeg`、`.png`、`.bmp` 的 ASCII 大小写不敏感扩展名，按相对路径
  `generic_string()` 字节序确定性排序。
- 每次 `next()` 仅解码一张 `CV_8UC3` BGR 图片，成功序号从 0 连续递增；正常 EOS 以 success +
  `nullopt` 表达，重复 EOS 保持相同行为。
- 读取损坏、删除或不可访问图片时 fail-fast；output 保持原值且 cursor 不推进。创建失败也保持 factory
  output 原值。
- OpenCV `imgcodecs` 仅私有接入 runtime target；没有修改 M1/M2/M3、`main.cpp` 或引入 sink/Runner/
  ORT/benchmark。
- `test_directory_source` 覆盖目录筛选、symlink、FIFO、hidden file、排序、索引、解码、EOS 与失败原子性；
  M4.2 定向/必要回归 8/8 PASS，Model Smoke OFF 全量 CTest 21/21 PASS，Model Smoke ON 全量 CTest
  28/28 PASS。

未完成：

- ResultSink、SerialRunner、CLI 接入 main 和完整 application assembly 均未开始。

阻塞问题：

- 无 M4.3 前已知阻塞。

下一步计划：

- 仅执行 M4.3 ResultSink System；不得提前实现 SerialRunner、main assembly、实际 ORT 流程或 benchmark。

备注：

- Strict、ASan、UBSan 仍为 `Not configured`；本轮未运行 benchmark，未修改 `DECISIONS.md`，也未进入 M4.3。

#### M4.3 ResultSink System

当前工作：

- 实现 `IResultSink`、ConsoleSink、JsonSink 和 CompositeSink；不实现 SerialRunner、main assembly、ORT 调用或计时采集。

修改文件：

- `include/edge_ai_defect/runtime/result_sink.hpp`
- `include/edge_ai_defect/runtime/console_sink.hpp`
- `include/edge_ai_defect/runtime/json_sink.hpp`
- `include/edge_ai_defect/runtime/composite_sink.hpp`
- `src/result_sink.cpp`
- `src/console_sink.cpp`
- `src/json_sink.cpp`
- `src/composite_sink.cpp`
- `src/result_sink_detail.hpp`
- `tests/test_result_sinks.cpp`
- `CMakeLists.txt`
- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- 固化单运行级 deterministic JSON schema；JsonSink 只在 successful `end_run()` 以同目录 temp + flush/close +
  POSIX rename 发布最终文件，且 overwrite=true 的旧文件在提交前不变。
- ConsoleSink 通过注入 stream 产生稳定 RUN/IMAGE/DETECTION/SUMMARY 输出；CompositeSink 固定 begin/write
  正序、end 逆序，Console end 失败时 JsonSink 不提交。
- 测试覆盖 sink lifecycle、JSON schema/escaping/UTF-8/locale/precision/timing、overwrite 与原子失败语义、
  temp cleanup、输入验证和 Composite 调用顺序/失败停止。
- M4.3 runtime 定向 5/5 PASS，Model Smoke OFF 全量 CTest 22/22 PASS，Model Smoke ON 全量 CTest 29/29 PASS。

未完成：

- SerialRunner、Frame timing 采集、CLI 接入 main 和完整 application assembly 均未开始。

阻塞问题：

- 无 M4.4 前已知阻塞。

下一步计划：

- 仅执行 M4.4 SerialRunner and Basic Timing；随后必须执行只读 M4.4 Shallow Gate，不能提前进入 M4.5。

备注：

- Strict、ASan、UBSan 仍为 `Not configured`；未运行 benchmark，未修改 `DECISIONS.md`，也未进入 M4.4。

#### M4.4 SerialRunner 输入合同修正

当前工作：

- 审计发现原冻结 Runner 构造函数缺少真实 M1 `Preprocessor::preprocess()` 所需的 `TensorInfo` 执行依赖；
  已由人工决策关闭该 planning blocker，M4.4 恢复为 pending，尚未开始 production 实现。

已完成：

- 冻结 `SerialRunner` 构造时显式接收已验证 `ModelContract.input.tensor_info`；Runner 保存值副本，
  不修改 M1 Preprocessor 或 M2 `IInferenceEngine`，也不让 Runner 重载 ModelContract。

下一步计划：

- 在该文档修订提交后继续仅执行 M4.4 SerialRunner and Basic Timing；M4.5 仍不得开始。

#### M4.4 SerialRunner and Basic Timing

当前工作：

- 实现严格同步 SerialRunner 与基础 `FrameTimings`；不实现 main assembly、实际 ORT application、benchmark 或 Level C。

修改文件：

- `include/edge_ai_defect/runtime/serial_runner.hpp`
- `src/serial_runner.cpp`
- `tests/test_serial_runner.cpp`
- `CMakeLists.txt`
- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- Runner 借用 source/preprocessor/engine/postprocessor/sink，保存外部注入的 `ModelContract.input.tensor_info`
  值副本；不依赖 concrete ORT 或 concrete source/sink，不重新加载 ModelContract。
- 严格完成 begin/source/preprocess/inference/postprocess/write/end 编排、fail-fast、错误上下文与 RunSummary
  在 end 成功后的原子提交。
- timing enabled 在 write 前记录五个 `steady_clock` stage 值；disabled 时完全保持 `timings=nullopt`。
- `test_serial_runner` 覆盖正常多帧、timing、EOS、全部主要失败阶段、summary 原子性、Status context、
  detection 顺序和 TensorInfo 注入/值副本；M4.4 runtime 定向 6/6 PASS，Model Smoke OFF 全量 CTest
  23/23 PASS，Model Smoke ON 全量 CTest 30/30 PASS。

#### M4.4 Shallow Gate remediation

当前工作：

- 首次只读 Shallow Gate 的 production 审查 PASS、总体 Gate FAIL；阻断原因为 SerialRunner 测试证据缺少
  null summary、一帧成功后的 source failure 和 injected TensorInfo 底层错误保留断言，另有 null summary 覆盖的文档漂移。

已完成：

- 在既有 `test_serial_runner` 中补齐 null summary、partial-progress source failure、M1 底层 TensorInfo 错误保留、
  zero-Detection summary，以及 source/engine/sink 共享 test-only event log；未修改任何 production contract。
- M4.4 Shallow Gate rerun 已 PASS；remediation commit 为
  `0eb4bf3669ce1da1c8d0ce546adffc007c7a2bfe`。此前 blocker（null summary、partial-progress source failure、
  TensorInfo 底层错误保留、zero-Detection frame）均已关闭，production contracts 未修改。
- M4.4 COMPLETE；M4.5 已在后续独立任务中完成 actual application assembly 与 ORT runtime smoke。

备注：

- Strict、ASan、UBSan 仍为 `Not configured`；未运行 benchmark。

#### M4.5 Application Assembly and Actual ORT Smoke

当前工作：

- 完成真实 `edge_ai_defect --config <runtime.yaml>` composition；不进入 M4.6、M5、Level C 或 benchmark。

修改文件：

- `src/main.cpp`
- `CMakeLists.txt`
- `tests/test_application_smoke.py`
- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- main 仅负责 CLI/config、组件组装、SerialRunner 调用、stderr 和 exit mapping；Runner 保持逐图处理循环。
- 同一已验证 ModelContract 用于 ORT initialize、SerialRunner 的 `input.tensor_info` 值注入和 RunMetadata，未改 D033 或
  M1/M2/M3/Runner/runtime config/CLI 合同。
- OFF executable smoke 覆盖 help、非法 CLI、config/schema 和 assembly failures；ON smoke 用 build 临时目录的
  确定性 BMP/YAML 运行实际 ORT 全链路，验证 deterministic JSON 重跑、Console、output preflight/overwrite failure。
- Model Smoke OFF 全量 CTest `24/24 PASS`；Model Smoke ON 全量 CTest `32/32 PASS`。

未完成：

- M4.6 read-only Standard Final Gate 和 M4.7 documentation-only closeout；M4 仍为 `IN_PROGRESS`。

下一步计划：

- 仅执行 M4.6 Standard Final Gate；不得在 Gate 中修改文件、提交、关闭 M4 或进入 M5。

备注：

- Strict、ASan、UBSan 仍为 `Not configured`；未执行 benchmark，未形成 Level C 或性能结论。

#### M4.6 Standard Final Gate remediation

当前工作：

- 关闭第一次 Standard Final Gate 发现的 application subprocess 测试证据缺口；不修改 production code，不执行 Gate rerun、
  M4.7、M5 或 benchmark。

修改文件：

- `tests/test_application_smoke.py`
- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- 第一次 M4.6 Gate 为 FAIL，但 production architecture 审查 PASS；当时 OFF `24/24`、ON `32/32` 回归通过，未发现
  production defect。
- 人工确认 output preflight 的 executable 证据属于 Model Smoke ON；Model Smoke OFF 保持不依赖 frozen ONNX，并由
  `result_sinks` unit tests 覆盖 output parent、overwrite、atomicity 和 temporary cleanup。未改变 D028～D033、组装顺序，
  未增加 fake backend 或 production seam。
- application smoke 现统一断言 exit `2/3/4` 的 empty stdout、non-empty/stable stderr、final JSON 与 temporary-file
  failure state；新增真实 `broken.png` source decode 的 Runner exit `4`，并验证 `overwrite=false` 旧文件不变。

未完成：

- M4.6 Standard Final Gate rerun；M4.7 未开始，M4 仍为 `IN_PROGRESS`。

下一步计划：

- 仅执行只读 M4.6 Standard Final Gate rerun；不得修改文件、创建 remediation commit、关闭 M4 或进入 M5。

备注：

- Strict、ASan、UBSan 均为 `Not configured`；未运行 benchmark。

---

### 2026-07-19 - M4.7 C++ ONNX Runtime Serial Baseline documentation-only closeout

当前工作：

- 在 M4.6 Standard Final Gate rerun PASS 后，仅固化最终 Gate 证据和阶段关闭状态；不修改 production、测试、CMake、配置、模型或 validation evidence。

修改文件：

- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- M4.6 Gate rerun 已记录为 PASS。Git/提交范围正确，M4.5 后 production 未变化；main 保持薄 composition root，
  exit `0/1/2/3/4`、单次 ModelContract load、D033 TensorInfo 值注入和既有 runtime contracts 均成立。
- output preflight 的 OFF/ON executable 与 ResultSink unit-test 分层、exit `2/3/4` subprocess stream evidence、
  failure JSON/temp atomicity 和 `overwrite=false` 旧文件保持均已确认；无新 blocker。
- 最终回归为 Model Smoke OFF M4 定向 `7/7 PASS`、OFF 全量 `24/24 PASS`；Model Smoke ON
  `application_ort_smoke` PASS、ON 全量 `32/32 PASS`。actual ORT 两张 deterministic BMP 串行闭环和 Console smoke 均通过。
- 两次 timing-disabled JSON byte-identical，SHA256 均为
  `5fbc1847f54716c3e809ecefa4ee297d368c08d08b2d0964a8a479bf620f7071`；不含 timing、timestamp、FPS 或 percentile。
- M4.0～M4.7 全部完成，M4 CLOSED。Strict、ASan、UBSan 仍为 `Not configured`；benchmark 和 Level C 均未执行。

未完成：

- M5 implementation、Level C、formal Profiler 和 performance baseline 均未开始。

阻塞问题：

- 无 M4 closeout 阻塞。M5 开始前需要先由独立任务制定并冻结 M5 执行计划。

下一步计划：

- 仅进入 M5 Level C and ORT Baseline Planning：PENDING；不得将其表述为 M5 started 或 benchmark started。

备注：

- `DECISIONS.md` 未修改；D028～D033 与最终实现一致。本轮未重新运行 Gate、CTest 或 benchmark。

### 2026-07-19 - M5 Pre-Planning Discovery Audit

当前工作：

- 完成只读 M5 pre-planning discovery；未创建 `M5_EXECUTION_PLAN.md`，未修改 production、tests、CMake、配置 schema、模型或正式 validation/benchmark evidence。
- Discovery 临时输出和独立 `build-m5-discovery` 已在任务结束时清理；source worktree 保持 clean。

已确认：

- 冻结 ONNX、ModelContract、C++ application JSON schema、`candidate_index` 语义和 M2 ORT SessionOptions 均可作为 M5 输入事实；不需要修改 M4 production 接口。
- 现有 Python 能力可按“`Reusable with M5 harness changes`”复用：preprocess、ORT raw output 和 postprocess helper 分层存在，但尚无完整的图片到 Detection 的 Level C wrapper。
- 本地 validation split 的 360 张图片可覆盖六类、多 Detection 和近阈值样本；当前 confidence 0.25 扫描仅发现 1 张零 Detection，尚不能满足发现任务期望的至少 2 张零 Detection。
- Git 中没有 tracked 原始图片，也没有找到可直接复现 NEU-DET 图片的 dataset archive；资产许可、portable corpus 和确定性导入仍需在 M5.0 明确。
- 1000 帧非正式 JSON size probe 成功：约 1.21 MB raw、约 51.9 KB `gzip -n`、峰值 RSS 164,824 KiB；该结果不是 benchmark，不形成 latency/FPS 结论，JsonSink 缓存暂不构成 blocker。

未决规划输入：

- Level C 第二张零 Detection 的选择规则；
- 12 张原图、20 张 benchmark 原图及四张派生图的 portable/tracked 策略；
- 派生图格式和确定性生成规则；
- 完整 application JSON、timings 和压缩 evidence 的保留策略。

状态结论：

- M5.0 documentation-only planning 具备开始条件；M5 implementation、Level C、formal Profiler 和 benchmark 仍未开始。
- 本审计不新增 DECISIONS.md 决策；D028～D033 保持不变。
- 下一步仅为独立 M5.0 计划制定与人工未决项冻结，不得将本审计表述为 M5 started 或 benchmark started。

#### M5.0 Level C Validation and WSL2 ORT CPU Engineering Baseline Planning Freeze

当前工作：

- 以 `86fd46d16e8d579613001e7c99df19b9e59a2249` clean HEAD 为经人工确认的新起点，完成 M5.0 documentation-only planning freeze。
- 不修改 production、tests、tools、CMake、RuntimeConfig schema、模型、配置、data 或 results，不进入 M5.1。

修改文件：

- `docs/personal/M5_EXECUTION_PLAN.md`
- `docs/personal/EXPERIMENT_PLAN.md`
- `docs/personal/DECISIONS.md`
- `docs/personal/TASKS.md`

已完成：

- 建立 M5 直接事实权威，冻结 M5.0～M5.7、M5.2 Level C Gate 和 M5.6 Deep Evidence Gate；M5 overall 转为 `IN_PROGRESS`，M5.0 COMPLETE。
- 冻结 Python explicit ORT Reference、12 原图 + 4 runtime-derived BMP、20 原图 benchmark corpus、不提交 NEU-DET 图片的 portable asset 策略。
- 冻结按 class 的确定性最大二分匹配，confidence tolerance `1e-4`、bbox tolerance `0.01 pixel`，以及 Python/C++ 各两次 byte-identical 和 16/16 PASS。
- 冻结复用 M4 FrameTimings 的离线 benchmark：pilot 100/drop 20、formal warmup 50、measured >=500 且 >=30 秒、五个独立进程、30 秒间隔、最低允许 CPU affinity、Type 7、sample stddev 和 no outlier removal。
- 冻结 Level C/benchmark evidence、完整 provenance、25 MiB retention 上限和失效规则；新增长期决策 D034～D039。
- 修订 EXPERIMENT_PLAN，明确 M5 是 WSL2 x86_64 ONNX Runtime CPU Engineering Baseline；TensorRT、Pipeline、input-size 和 stability 延期到后续 Jetson 阶段。

未完成：

- M5.1 corpus manifests、导入/SHA 校验工具和 derived generator 尚未实现。
- Level C Reference/Comparator、正式 Level C evidence、benchmark harness、正式 baseline 和 Deep Gate 均未开始。

阻塞问题：

- 无 M5.1 planning blocker；本地合法 `--dataset-root` 是 M5.1 执行输入，不是 Git 资产。

下一步计划：

- 仅执行 M5.1 Corpus Assets and Validation Contract；不得自动进入 M5.2，不得导入图片到 Git 或运行正式 Level C/benchmark。

备注：

- Strict、ASan、UBSan 仍为 `Not configured`；M5.0 未运行 build、CTest、Level C 或 benchmark，未生成正式 evidence。

#### M5.1 Corpus Assets and Validation Contract

当前工作：

- 完成 M5.1 corpus contract、三份文字/哈希 manifest、严格 parser/validator、regular-file preparation 工具和独立 Python/CTest 测试。
- 起点 Git upstream 为 behind `0` / ahead `0`；ahead 0 已确认不是阶段启动阻断条件，未人为恢复历史 ahead 14。

修改文件：

- `tools/validation/prepare_m5_corpus.py`
- `tests/data/m5/manifests/level_c_original_corpus.json`
- `tests/data/m5/manifests/level_c_derived_corpus.json`
- `tests/data/m5/manifests/benchmark_corpus.json`
- `tests/test_prepare_m5_corpus.py`
- `CMakeLists.txt`
- `docs/personal/M5_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- 12 张 Level C original、4 张确定性 derived BMP 和 20 张 benchmark original 均按冻结顺序、SHA、尺寸和 coverage 验证。
- 工具只接受显式 `--dataset-root`，执行 source regular-file 检查、SHA fail-fast、regular copy、OpenCV 4.10 `INTER_LINEAR`/BGR 114 derived 生成、临时目录原子发布和稳定 prepared manifest。
- 本地 ignored `data/yolo/neu_det/images/val` 验证通过；图片未复制到 tracked 目录，源文件未修改，Git 未跟踪图片或 prepared 输出。
- Model Smoke OFF 定向 `1/1`、OFF 全量 `25/25`、ON 全量 `33/33` CTest 通过；Strict/ASan/UBSan 保持 `Not configured`。

未完成：

- Python ORT Reference、Level C Comparator、正式 Level C、benchmark harness、benchmark execution、formal evidence 均未开始。

状态结论：

- M5.1：`COMPLETE`；M5.2：`PENDING`；M5 overall：`IN_PROGRESS`。
- 本轮没有新增长期决策，`DECISIONS.md` 不变。

下一步计划：

- 仅可进入 M5.2 Harness 实现；不得在本任务中运行正式 Level C、benchmark 或生成正式 evidence。

#### M5.2A Level C Reference、Comparator 和 Validation Harness 实现

当前工作：

- 完成 explicit Python ONNX Runtime Reference、稳定 Reference JSON schema、DirectorySource 等价枚举、显式 LetterBox/预处理、BCN 后处理、candidate_index 保留、最大二分匹配 Comparator 和临时 dry-run orchestrator。
- 起点为 `2739ceb94b618113cab4a126cb6e9cd5f48e6042` clean HEAD；upstream behind `0` / ahead `1`，ahead 只记录实际值。

修改文件：

- `tools/validation/m5_level_c_common.py`
- `tools/validation/m5_level_c_reference.py`
- `tools/validation/m5_level_c_compare.py`
- `tools/validation/run_m5_level_c.py`
- `tests/test_m5_level_c_reference.py`
- `tests/test_m5_level_c_compare.py`
- `tests/test_m5_level_c_runner.py`
- `CMakeLists.txt`
- `docs/personal/M5_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

已完成：

- Reference 严格读取 RuntimeConfig/ModelContract/frozen ONNX；使用 CPU EP、ORT_SEQUENTIAL、ORT_ENABLE_ALL、intra/inter-op=1；不使用 PyTorch、Ultralytics 或 C++ executable 作为 oracle。
- Comparator 使用真实确定性 augmenting-path maximum matching；测试包含 greedy 反例、confidence/bbox tolerance 边界、candidate_index 不同仍可 PASS、顺序差异和 no-compatible-edge。
- 本地 16 张 dry-run：Python/C++ 两侧各自两次 byte-identical，Comparator `16/16 PASS`；最大 confidence 误差 `4.980773571361397e-10`，最大 bbox 误差 `1.2131195092024427e-05`。
- Model Smoke OFF M5.2A 定向 `3/3`、全量 `28/28`；ON 定向 `3/3`、全量 `36/36`。

未完成：

- 正式 Level C evidence、正式 provenance、Level C Gate、benchmark harness 和 M5.3 均未开始。

状态结论：

- M5.2A：`COMPLETE`；M5.2B：`PENDING`；M5 overall：`IN_PROGRESS`。
- 本轮没有新增长期决策，`DECISIONS.md` 不变；M5.1 manifests 未漂移。

下一步计划：

- 仅可进入只读 M5.2 Level C Gate；不得把 Formal comparison PASS 写为 Gate PASS，也不得执行 benchmark。

#### M5.2B Formal Evidence Generation

当前工作：

- 在 source commit `1073fa8be1644dd8562f5704ae31996121883dbb` 上完成正式 Level C evidence；起点 upstream behind `0` / ahead `2`，
  worktree clean，ahead 仅记录实际值。
- Evidence ID：`20260719_1073fa8`；目录：`results/validation/level_c/20260719_1073fa8/`。

验证结果：

- 12 张 validation original + 4 张 runtime-derived BMP 准备和 SHA 校验通过，图片本体未进入 Git/evidence。
- Python Reference 两次 byte-identical；真实 C++ `edge_ai_defect` 两次 byte-identical；Run 1/Run 2 comparison 均 `16/16 PASS`。
- 最大 confidence 误差 `4.980773571361397e-10`；最大 bbox 误差 `1.2131195092024427e-05`；Detection 总数 `54`，per-class `[4, 28, 7, 4, 5, 6]`。
- Model Smoke OFF 定向/全量 `4/4`、`28/28 PASS`；ON 定向/全量 `4/4`、`36/36 PASS`。
- Strict/ASan/UBSan 保持 `Not configured`；benchmark 未开始；Level C Gate 未执行。

状态结论：

- M5.1：`COMPLETE`；M5.2A：`COMPLETE`；M5.2B：`COMPLETE`；Formal Level C comparison：`PASS`。
- M5 overall：`IN_PROGRESS`；Level C Gate：`PENDING`；M5.3：`PENDING`。
- 下一步仅为只读 M5.2 Level C Gate；不得将 Formal comparison PASS 写为 Gate PASS。

#### M5.2 Level C Gate remediation

当前工作：

- 第一次 Level C Standard Validation Gate 已记录为 `FAIL`；本轮仅修复既有测试证明和 evidence metadata blocker，
  不修改 production、Reference、Comparator、orchestrator、M5.1 manifests、ONNX 或 ModelContract 本体。
- 修正 ModelContract 64 位 SHA：`9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190`，同步到 M5 计划和
  `results/validation/level_c/20260719_1073fa8/provenance.json`。
- `tests/test_m5_level_c_compare.py` 已补齐真实 `[[0, 1], [0]]` greedy 反例、confidence/bbox 双方向边界和略超容差、
  Detection 重排、non-finite JSON rejection。
- provenance 增加 15 条 machine-readable command records；正式 Detection/comparison/manifests/RuntimeConfig 和
  `commands.txt` 未重新生成。

验证结果：

- Python Comparator 定向测试通过；Model Smoke OFF targeted/full `4/4`、`28/28 PASS`；ON targeted/full `4/4`、`36/36 PASS`。
- Formal comparison 仍 `16/16 PASS`，Detection `54`，per-class `[4, 28, 7, 4, 5, 6]`；正式结果文件 byte-identical。
- `sha256sum -c` 全部通过；Strict/ASan/UBSan 为 `Not configured`；benchmark 未开始。

状态结论：

- M5.2A：`COMPLETE`；M5.2B：`COMPLETE`；第一次 Level C Gate：`FAIL`；remediation：`COMPLETE`。
- Gate rerun：`PENDING`；M5.3：`PENDING`；M5 overall：`IN_PROGRESS`。
- 下一步唯一允许任务为只读 M5.2 Level C Gate rerun，不得进入 M5.3 或运行 benchmark。

#### M5.2 Level C Standard Validation Gate Rerun PASS 固化

当前工作：

- M5.2 第一次 Standard Validation Gate：`FAIL`（历史）；Gate remediation：`COMPLETE`；本次只读 Gate rerun：`PASS`。
- 固化 Evidence ID `20260719_1073fa8`，source commit `1073fa8be1644dd8562f5704ae31996121883dbb`，Evidence commit
  `011ac3ca046a40f8da4bd5b0be7e7fa3e55b27c6`，remediation commit `26bfca7b291145b7889ea976e4221dd15d1751d2`。
- 正确 ModelContract SHA 为 `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190`；旧错误 SHA 无残留。
- Greedy adjacency `[[0, 1], [0]]`、双方向 tolerance、Detection 重排、non-finite rejection、15 条 command records 和
  Evidence SHA 检查均通过；Comparator production 未修改。

验证结果：

- Python/C++ 两次输出各自 byte-identical；comparison Run 1/2 均 `16/16 PASS`；Detection `54`；per-class
  `[4, 28, 7, 4, 5, 6]`；最大 confidence/bbox error 分别为 `4.980773571361397e-10` 和
  `1.2131195092024427e-05`。
- OFF targeted/full：`4/4 PASS`、`28/28 PASS`；ON targeted/full：`4/4 PASS`、`36/36 PASS`。
- Release binary SHA：`0f38995c4d179a724c275c025fd51e22eb18c282b89ff34c73d786c0f02ef315`；Evidence 大小 `174145` bytes；
  无图片、隐私路径、timing 或 benchmark 数据；未发现新 blocker。

状态结论：

- M5.2A：`COMPLETE`；M5.2B：`COMPLETE`；M5.2 overall：`COMPLETE`。
- M5.2 Gate rerun：`PASS`；M5.3：`PENDING`；M5 overall：`IN_PROGRESS`。
- Strict/ASan/UBSan：`Not configured`；benchmark 未执行；本次提交不启动 M5.3。
- 当时下一步为 `M5.3 Benchmark Harness and Offline Analyzer`；该阶段已在本日后续记录中完成。

#### M5.3 Benchmark Harness and Offline Analyzer

当前工作：

- M5.3 已完成；新增 `tools/benchmark/m5_ort_cpu_common.py`、`m5_ort_cpu_analyze.py`、
  `run_m5_ort_cpu_baseline.py`，实现 benchmark workload、pilot/正式帧数计算、五进程编排、CPU affinity、
  M4 `FrameTimings` 严格解析、warmup、Type 7 与 n-1 统计、per-run/aggregate summary、deterministic gzip 和
  evidence staging/原子发布。
- 复用 M5.1 20 张 benchmark corpus preparation；未修改 M1～M4 production、RuntimeConfig/JsonSink schema、
  M5.1 manifests 或 Level C evidence。

验证结果：

- Python unit tests、CTest M5.3 tests 和 OFF/ON Release 全量回归通过：OFF `31/31 PASS`，ON `39/39 PASS`；
  Strict、ASan、UBSan 保持 `Not configured`。
- `build-m5-3-development-smoke/` 下真实 application smoke 通过：exit 0、JSON/timing 解析、TSV、summary 和
  deterministic gzip round-trip 均 PASS。该 smoke 明确为 `NON-FORMAL DEVELOPMENT SMOKE`，未形成任何正式
  latency/FPS/P50/P95/P99 结论。

未完成：

- M5.4 正式 WSL2 ORT CPU baseline 尚未执行；正式 benchmark evidence 尚未生成。

状态结论：

- M5.3：`COMPLETE`；M5.4：`PENDING`；M5 overall：`IN_PROGRESS`。
- 下一步为 M5.4 Formal WSL2 ORT CPU Baseline Execution；本轮未运行 benchmark、未进入 M5.4。

#### M5.3 formal-execution remediation

当前工作：

- M5.4 能力预审发现初始 M5.3 CLI 仍为 `formal execution is reserved for M5.4`；本轮未运行 Pilot、未生成部分
  benchmark Evidence，M5.4 保持 `PENDING`。
- 已补齐显式互斥的 `--check-only`、`--development-smoke`、`--formal` 模式和可注入正式 orchestrator：preflight、
  Pilot、正式 N、五个独立 application run、四次 30 秒等待、CPU affinity、run 分析、aggregate、environment、
  provenance、commands、gzip、SHA、25 MiB 检查和原子 Evidence staging。

验证结果：

- fake application 端到端 formal 测试通过：六次独立 invocation、五个 formal run、Pilot 不进入 aggregate、四次等待、
  五份 summary、aggregate、environment/provenance、gzip、SHA 和原子发布均验证；测试未真实等待 30 秒。
- Model Smoke OFF Release：定向 `7/7 PASS`、全量 `31/31 PASS`；ON Release：定向 `7/7 PASS`、全量 `39/39 PASS`。
- `NON-FORMAL DEVELOPMENT SMOKE` 通过 application/analyzer/summary/gzip 功能验证；未记录性能数字。

状态结论：

- M5.3 formal-execution remediation：`COMPLETE`；M5.3：`COMPLETE`；M5.4：`PENDING`。
- 正式 benchmark 和正式 Evidence 仍未执行/生成；Strict、ASan、UBSan 为 `Not configured`。
- 下一步可基于本轮新 source commit 重新执行 M5.4；原候选 Evidence ID `20260719_fed96c1` 不具备正式效力。

#### M5.4 Formal WSL2 x86_64 ONNX Runtime CPU Engineering Baseline Execution

正式执行结果：

- source commit：`850252b3c176622e3f4461e78f1b7e517e8b06b6`；Evidence ID：`20260719_850252b`；路径：
  `results/benchmark/ort_cpu/20260719_850252b/`。
- 全新 Release OFF/ON 回归通过：OFF targeted/full `7/7`、`31/31 PASS`；ON targeted/full `7/7`、`39/39 PASS`。
- binary SHA：`0f38995c4d179a724c275c025fd51e22eb18c282b89ff34c73d786c0f02ef315`；check-only PASS；20 张 benchmark
  corpus SHA/尺寸校验通过，source 未被修改。
- Pilot 100/discard20/analyzed80；Pilot mean `108.5349276625 ms`；正式 workload `560` 帧，measured `510` 帧。
- 五个独立 formal run 全部 exit 0，PID `97460`、`97778`、`98133`、`98487`、`98786`；四次 30 秒等待已执行；
  每个 run measured duration 均超过 30 秒，summary status 均为 `PASS`。
- Type 7、n-1 sample stddev、keep-all measured samples、deterministic gzip、TSV/summary/aggregate 重建和
  `sha256sum -c` 全部通过；Evidence 大小 `492434` bytes，无图片、未压缩 raw JSON 或个人绝对路径。
- CPU affinity：allowed `[0,1,2,3,4,5]`，selected/effective CPU `0`；环境限制按 WSL2 warm-cache、未 drop caches、
  host load/governor 未控制记录。

状态结论：

- M5.4：`COMPLETE`；正式 benchmark Evidence 已生成；M5.5：`PENDING`；M5 overall：`IN_PROGRESS`。
- Strict、ASan、UBSan：`Not configured`；M5.6 Deep Evidence Gate 尚未执行；下一步为 M5.5 Evidence Consolidation。

---

## 8. 当前最近计划

近期优先级：

1. M0 与 M1 已完成并正式关闭。
2. M2 已正式关闭：production `OnnxRuntimeEngine` 已具备 contract-validated
   CPU Session initialization、synchronous `HostTensor` inference、boundary tests 和
   Level B Python/C++ raw-output evidence。
3. M3 Deep Gate Rerun 已 PASS，M3 已正式关闭；M2/M3 均不包含完整 Serial Baseline 或性能结论。
4. M4.0～M4.7 已完成；M4.4 Shallow Gate rerun PASS，M4.6 第一次 Standard Final Gate FAIL 后 remediation complete，
   M4.6 Gate rerun PASS，M4 已 CLOSED。
5. M5.0 Planning Freeze、M5.1、M5.2A、M5.2B 和 M5.2 Level C Validation 已完成；第一次 Level C Gate `FAIL`，
   remediation 已完成，Gate rerun `PASS`；M5.2 overall `COMPLETE`，M5 overall 仍为 `IN_PROGRESS`。下一步为 M5.3，
   但 benchmark 尚未开始。
6. M5 复用 M4 FrameTimings 并由离线 Python 工具统计，不新增 production Profiler；TensorRT、Pipeline、input-size、
   stability、ROS2 和 Qt 不进入 M5，保留给后续 Jetson/TensorRT 阶段。

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

### 2026-07-21 - Stage J J0 Planning Freeze

当前工作：

- 同步 Stage J Plan v0.3、Decision D041 以及项目全局规划文档的当前状态。

修改文件：

- `AGENTS.md`
- `README.md`
- `docs/personal/TASKS.md`
- `docs/personal/ENVIRONMENT.md`
- `docs/personal/EXPERIMENT_PLAN.md`

已完成：

- J0.1：`COMPLETE`；新增 `docs/personal/STAGE_J_EXECUTION_PLAN.md`；Plan v0.3 `FROZEN`；commit `87d4459f4d25e630f38ae279b0423e39036e64af`。
- J0.2：`COMPLETE`；新增 Decision D041；commit `38e8e068a6d38e69b8845098197d6632cef4f5b0`。
- J0.3：`COMPLETE`；同步 AGENTS、README、TASKS、ENVIRONMENT、EXPERIMENT_PLAN；commit to be recorded by Git history。

当前状态：

- `M0–M5 CLOSED`；Stage J Plan v0.3：`FROZEN`；J0：`IN PROGRESS`；Stage J：`PENDING`；Stage T/Stage P：未开始。
- J0：`IN PROGRESS`；Stage J：`PENDING`。
- Stage J implementation branch：`not created`。
- Stage J production code：`not modified`。
- Stage J formal Evidence：`not generated`。
- Device-observed facts：`pending J1`；planned target 与 observed fact 保持分离。

未完成：

- J0.4 测试名称与分类清单；
- J0.5 里程碑任务卡；
- J0.6 Git 起点核验和分支创建。

阻塞问题：

- 无；Jetson 实机验收仍等待 J1，尚未开始 Stage J 实现。

下一步计划：

- 完成 J0.4、J0.5 和 J0.6；不得将上述任务提前标记为完成。

备注：

- 本记录时间：`2026-07-21 22:52:39 CST`。

### 2026-07-21 - Stage J J0.4 Baseline Test Inventory

当前工作：

- 冻结当前 HEAD 的 CMake/CTest baseline test inventory 和 Stage J 测试分类。

已完成：

- J0.4：`COMPLETE`；新增 `configs/stage_j/test_inventory.yaml`。
- source commit：`2da4d2cae6c5075e516c7edcfbd28e52f5301299`。
- Model Smoke OFF：31；Model Smoke ON：39；ON-only：8；unique baseline：39。
- 分类数量：`portable_required=39`、`model_asset_required=19`、`x86_only=0`、`jetson_only=0`、`sanitizer_required=15`。
- 未来 Stage J requirements：JTEST-001～JTEST-011，共 11 项，均为 `not_implemented` 且无 CTest 名称。

第一次 J0.4 attempt：

- 因旧任务预期 28/39 与当前 HEAD 旧 build metadata 的 24/32 不一致，按 Gate 停止；未修改文件、未创建提交。
- 该次停止不是代码失败或测试失败。

第二次 J0.4 attempt：

- 发现仓库内旧 `build/off` 和 `build` metadata 与当前 CMake 静态注册不一致；旧 metadata 缺少 7 个 M5 tests。
- 未修改文件、未创建提交；该次停止不是代码失败或测试失败。

最终处理：

- 保留旧 build directories 不变，并将其标记为 stale、排除出 inventory 权威来源。
- 使用仓库外临时 OFF/ON configure 生成 fresh CTest metadata；当前 CMake 静态注册与 fresh metadata exact match。
- 未新增真实测试、未运行 CTest 实际测试、未编译、未修改 CMake。

当前状态：

- J0：`IN PROGRESS`；Stage J：`PENDING`。
- Stage J implementation branch：`not created`。
- Stage J production code：`not modified`。
- Stage J formal Evidence：`not generated`。
- J0.5、J0.6：`PENDING`。

下一步计划：

- J0.5 里程碑任务卡；
- J0.6 Git 起点核验和 Stage J 分支创建。

备注：

- 本记录时间：`2026-07-21T23:47:11+08:00`。
- J0.4 commit：commit to be recorded by Git history。

### 2026-07-22 - Stage J J0.5 Milestone Task Cards

- J0.5：`COMPLETE`；新增并冻结 [`docs/personal/STAGE_J_TASK_CARDS.md`](STAGE_J_TASK_CARDS.md)，版本 `v0.1`，文档状态 `FROZEN`。
- 父协议：Stage J Plan v0.3（`FROZEN`）；Decision D041：`Accepted`。
- 任务卡覆盖 J1–J9，共 45 张：J1（5）、J2（6）、J3（10）、J4（4）、J5（10，含 J5.1a/J5.1b/J5.1c）、J6（4）、J7（2）、J8（2）、J9（2）。
- J1 设备依赖卡保持 `BLOCKED`；J2–J9 均未执行且未标记 `COMPLETE`。J0.6 分支创建仍为 `PENDING`，J0 仍为 `IN PROGRESS`。
- 卡片冻结了依赖图、硬 Gate、PASS/FAIL/BLOCKED、失效与重跑范围、source/Evidence 分离提交策略及用户 merge/tag/backup/push 交接责任。
- 起始 source commit：`6e1c46ac4f9d09ef2e620f316723957144a66cf0`；Stage J production 未修改；J1–J9 formal Evidence 未生成。
- 本记录时间：`2026-07-22T00:01:04+08:00`。
- J0.5 commit：commit to be recorded by Git history。

### 2026-07-22 - Stage J J0.6 Planning Freeze Closeout

- J0.6：`COMPLETE`；J0：`COMPLETE`；J0.1–J0.5 均已完成。
- Stage J Plan v0.3：`FROZEN`；D041：`Accepted`；test inventory Model Smoke OFF=`31` / ON=`39`；Task Cards v0.1：`FROZEN`，共 45 张。
- 最终 J0 base commit：commit to be recorded by Git history。
- 目标分支：`feature/jetson-onnxruntime`；该分支将在本 closeout commit 后立即从最终 main HEAD 创建。
- Stage J production code 未修改；未执行 build/test/benchmark；Stage J formal Evidence 未生成。
- Stage J execution：`PENDING J1`；J1：`BLOCKED pending device arrival`；下一张任务卡：J1.1 — Device Identity, Storage and Flash Acceptance。
- implementation branch：`feature/jetson-onnxruntime`；device-observed facts：`pending J1`；Stage T/P 尚未开始。
- 本记录时间：`2026-07-22T00:07:37+08:00`。
- J0.6 closeout commit：commit to be recorded by Git history。

### 2026-07-22 - Stage J J1.1 Device Acceptance

- J1.1：`COMPLETE`；设备身份为 Jetson Orin Nano Super / `aarch64` / Tegra234。
- MemTotal：`7,976,910,848` bytes，符合 nominal 8GB SKU。
- NVMe：PUSKILL 256GB，`256,060,514,304` bytes；rootfs 位于 NVMe，ext4 read-write。
- Boot slot A/B：正常；SMART critical warning=`0`，media errors=`0`。
- `unsafe_shutdowns=11` 为历史累计值；当前无明确 NVMe 故障，后续继续观察是否增长。
- Fan、heatsink、稳定原装电源、设备独占和无已知随机重启/掉盘问题：`USER_CONFIRMED`。
- Network/SSH/sudo：available；sudo 仅通过 command-scoped read-only wrapper 提供给 Codex，unrestricted NOPASSWD 为 false。
- 用户在正式采集前安装了临时受限只读 wrapper：`/usr/local/sbin/edge-ai-j1-readonly`；sudo authorization 为 command-scoped NOPASSWD。该变更不安装软件、不改变功耗模式、时钟、风扇或推理环境；J1.4 完成或不再需要特权采集后由用户手工移除。
- 未安装软件；未改变 nvpmodel、时钟、风扇或系统配置；未运行 build/test/benchmark。
- 原始采集保存在 repository-external temporary location，未加入 Git，未作为 Published Evidence。
- J1 overall：`IN PROGRESS`；J1.2：`READY_WITH_WARNINGS`；J1.3～J1.5：`PENDING`。
- Carry-forward warnings：CMake、OpenCV metadata、Python `cv2`、15W mode、MAXN_SUPER、jetson_clocks root requirement、unsafe shutdown counter。
- Commit：`commit to be recorded by Git history`。

### 2026-07-22T23:14:52+08:00 - Stage J J1.4 Post-D042 Closeout Verification

- 当前 HEAD `697a58ee3f4f4a93fe507e7b48a27e5906f08d09` 保持不变；worktree clean。
- D042：`Accepted`；未修改 D042，不新增 D043。
- Stable evidence manifest validation：全部 `OK`；authoritative Phase A/final supplemental SHA 与 D042 一致；superseded attempts retained。
- J1.4：`COMPLETE`；J1 remains `IN PROGRESS`；J1.5：`READY`。
- MAXN_SUPER/ID 2、CPU online 0-5、CPU/GPU/EMC locked state、fan PWM 255 和 nvfancontrol inactive 均 retained。
- 未执行 workload、build、test、benchmark 或 J1.5；未发生 system、wrapper 或 sudoers 变更。
- Commit：`commit to be recorded by Git history`。

### 2026-07-22T22:55:09+08:00 - Stage J J1.4 Telemetry and Throttling Freeze

- J1.4 Phase A：`DISCOVERY_PASS`；用户授权 J1 discovery 使用 composite immutable discovery evidence。
- J1.4：`COMPLETE`；新增 D042 `Freeze Stage J Jetson Telemetry and Throttling Contract`，状态 `Accepted`。
- Composite raw SHA：Phase A `91eb86daebd31a96e6ddc74b9beda89c7aa466e7d74f0da53a0ea291689f99a0`；supplemental `75cb07a6149b6b69b3774397ee58bd754743aa7df9181f86d9749833d17732a5`；均 repository-external、untracked、not Published Evidence。
- Frozen thermal relevant set：cpu/gpu/soc0/soc1/soc2/tj；CV0/CV1/CV2 因稳定 `EAGAIN` 排除 numeric hard maximum。
- CPU/GPU/EMC authority、tegrastats `1000 ms`、rail current/average semantics、OC1 Under Voltage / OC2 Average Overcurrent / OC3 Instantaneous Overcurrent 已冻结。
- OC/UV counter delta、throttle-enable、INA3221 alarm Gate 已冻结；当前 counter 为 `0`、enable 为 `1`、alarm 为 `0`。
- `Stage J Sustained Throttling Algorithm v1` 与 environment-drift/boot invalidation 规则已冻结；all-core telemetry CPU0 overlap limitation 已记录。
- 未执行 workload、benchmark、正式 T_idle_ref 或稳定性验证；未发生系统、production 或 wrapper/sudoers 变更。
- J1 overall：`IN PROGRESS`；J1.5：`READY`。不得将 J1 标记为 COMPLETE。
- Commit：`commit to be recorded by Git history`。

### 2026-07-22 - Stage J J1.3 MAXN_SUPER and Clock-Control Acceptance

- J1.3：`COMPLETE`；Phase A：`DISCOVERY_PASS`。
- Pre-change 15W/ID=`0` successfully changed to MAXN_SUPER/ID=`2` using the fixed command-scoped power-control wrapper；未使用 `--force`，无需 reboot。
- CPU online set remained `0-5`。
- `jetson_clocks` applied successfully；observed locked state: CPU `1728000`，GPU `1020000000`，EMC `3199000000`。
- `jetson_clocks --fan` applied successfully；PWM=`255`，fan dynamic speed control disabled，nvfancontrol enabled but inactive after the apply。
- Post-change query remained MAXN_SUPER/ID=`2`，无 silent fallback；NVMe `unsafe_shutdowns=11` 未增加。
- First Phase B attempt stopped before changes because Codex could not read root-owned sudoers SHA；second stopped before changes because user SHA labels conflicted。用户随后通过明确标签提供 wrapper/sudoers SHA 和 `visudo parsed OK` 证据；wrapper SHA 由 Codex 独立复核。
- Wrapper self-test PASS；unrestricted sudo negative check PASS；未读取 sudoers 正文。
- 未安装 package、未修改 wrapper/sudoers、未执行 reboot、未运行 configure/build/test/benchmark。
- raw attempt repository-external、untracked、not Published Evidence；未加入 Git。
- J1 overall：`IN PROGRESS`；J1.4：`READY`；J1.5：`PENDING`。
- Commit：`commit to be recorded by Git history`。

### 2026-07-22 - Stage J J1.2 Platform and Toolchain Inventory

- J1.2：`COMPLETE`；L4T observed `R36.5.0`，JetPack meta-package 未安装，APT candidate 为 `6.2.2+b24`，exact installed JetPack 未独立验证。
- Ubuntu `22.04.5`，kernel `5.15.185-tegra`，architecture `aarch64`，glibc `2.35`；online/allowed CPU 均为 `0-5`。
- GCC/G++ `11.4.0`，Make `4.3`，pkg-config `0.29.2`；CMake/CTest、Ninja、patchelf 缺失。
- Python `3.10.12`，python3-dev、NumPy `1.21.5`、PyYAML `5.4.1` 可用；pip/venv、ONNX、Python ORT、Python cv2 不可用。
- OpenCV C++ classification：`RUNTIME_AND_HEADERS_PRESENT_METADATA_MISSING`；runtime/headers 4.5.4 和 Debian component packages 存在，但 pkg-config/CMake metadata 缺失。
- yaml-cpp：未发现 header、runtime 或 metadata，阻塞 J3 configure/build。
- 系统 ONNX Runtime：未发现；J2 构建官方 1.23.2 SDK，不以系统缺失判定 J1.2 失败。
- CUDA 12.6、cuDNN runtime libraries、TensorRT 10.3 为 recorded-only pre-existing facts；未使用这些后端，未开始 Stage T。
- dpkg audit 无异常，未发现 held packages；root/var/tmp 均约 11% 使用率。
- Remediation：CMake/CTest 在 J2.1/J2.2 前处理；OpenCV metadata 和 yaml-cpp 在 J3.1 前处理；ORT 在 J2 构建；Python cv2 当前不阻塞 C++ Stage J。
- 未安装或修复软件；未修改 APT、系统配置、功耗、时钟或风扇；未运行 configure/build/test/benchmark；未开始 J1.3。
- raw attempt 为 repository-external、untracked、not Published Evidence；未记录随机临时路径。
- J1 overall：`IN PROGRESS`；J1.3：`READY_WITH_WARNINGS`。
- Commit：`commit to be recorded by Git history`。
