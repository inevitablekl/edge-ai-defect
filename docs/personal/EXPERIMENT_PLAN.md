# EXPERIMENT_PLAN.md

## 1. 用途

本文档用于记录本项目的实验设计、实验变量、实验指标、实验日志格式和后续实验补充计划。

项目名称：

**边缘 AI 工业缺陷检测部署与优化项目**

英文名称：

**Edge AI Industrial Defect Detection Deployment and Optimization**

本文档会随着实验设计细化、代码完成和真实测试结果产生而持续更新。

当前阶段主要记录：

- 已确定的实验方向。
- 必须控制的变量。
- 必须采集的指标。
- 实验日志格式。
- 后续待补充事项。

本文档不记录虚构数据。

所有实验结论必须来自真实测试结果。

---

## 2. 实验总目标

本项目实验目标不是证明新算法优越性，而是验证一个工业缺陷检测模型在边缘设备上的工程部署效果。

核心实验问题：

1. YOLOv8n 在 NEU-DET 数据集上是否具备基本缺陷检测能力？
2. TensorRT FP16 相比 ONNX Runtime 是否能提升 Jetson 上的推理性能？
3. Pipeline mode 相比 Serial mode 是否能提升系统 throughput / FPS？
4. 不同输入尺寸在 accuracy、latency、FPS 之间如何权衡？
5. 系统在持续运行时是否具备基本稳定性？

---

## 3. 固定实验前提

| 项目 | 当前决策 |
|---|---|
| 数据集 | NEU-DET / NEU Surface Defect Database |
| 模型 | YOLOv8n |
| 数据集划分 | train / val / test = 70 / 20 / 10 |
| 输入尺寸 | 320, 416, 640 |
| 训练语言 | Python |
| 部署语言 | C++ |
| 配置格式 | YAML |
| baseline backend | ONNX Runtime |
| optimized backend | TensorRT FP16 |
| runtime modes | Serial, Pipeline |
| 主实验平台 | NVIDIA Jetson |
| 日志格式 | CSV / JSON |
| 训练 split seed | 42 |
| 正式 baseline 配置 | `configs/train/yolov8n_neudet_baseline.yaml` |
| v1 GUI | 不实现 |
| v1 ROS2 | 只预留接口 |
| INT8 | 当前不做，后续可选 |

---

## 4. 实验平台说明

### 4.1 Cloud Training Platform

用途：

- YOLOv8n 训练。
- 模型验证。
- ONNX export。
- 训练日志记录。

当前平台：

```text
RTX 3090
```

该平台不作为最终边缘部署性能实验平台。

---

### 4.2 Local Development Platform

用途：

* 代码开发。
* C++ 编译。
* ONNX Runtime baseline 初步验证。
* 小规模功能测试。

当前平台：

```text
GTX1050Ti
```

该平台不作为论文核心性能实验平台。

---

### 4.3 Edge Deployment Platform

用途：

* ONNX Runtime vs TensorRT FP16 对比。
* Serial vs Pipeline 对比。
* 输入尺寸对比。
* 稳定性测试。
* 小论文核心性能数据采集。

当前状态：

```text
Jetson model: TBD
JetPack version: TBD
CUDA version: TBD
TensorRT version: TBD
ONNX Runtime C++ version: TBD
```

以上信息在 Jetson 设备确定后补充。

---

## 5. 实验数据原则

所有实验数据必须真实采集。

禁止伪造：

* Precision
* Recall
* mAP
* latency
* FPS
* CPU usage
* GPU usage
* memory usage
* power usage
* stability result
* paper table
* paper figure

如果数据尚未采集，使用：

```text
TBD: real experiment data required
```

或：

```text
Not measured yet
```

---

## 6. 通用实验控制变量

不同实验之间应尽量控制以下变量：

| 控制项                  | 要求                               |
| -------------------- | -------------------------------- |
| 测试数据                 | 同一 test split 或同一 input source   |
| 模型                   | 同一 YOLOv8n 训练结果                  |
| 输入尺寸                 | 单项实验内保持一致，除非该实验专门比较 input size   |
| backend              | 单项实验内保持一致，除非该实验专门比较 backend      |
| runtime mode         | 单项实验内保持一致，除非该实验专门比较 runtime mode |
| 测试设备                 | 同一实验组内保持一致                       |
| warmup frames        | 统一配置                             |
| measured frames      | 统一配置                             |
| confidence threshold | 统一配置                             |
| NMS threshold        | 统一配置                             |
| preprocessing        | ONNX Runtime 与 TensorRT 保持一致     |
| postprocessing       | ONNX Runtime 与 TensorRT 保持一致     |

---

## 7. 通用实验配置项

实验应由 YAML 配置驱动。

配置项至少包括：

* backend
* runtime mode
* model path
* TensorRT engine path
* input source
* source type
* input size
* confidence threshold
* NMS threshold
* output directory
* log directory
* warmup frames
* measured frames
* pipeline queue size
* pipeline drop policy
* device name
* precision mode

---

## 8. 通用指标定义

### 8.1 Accuracy Metrics

用于模型精度实验：

* Precision
* Recall
* mAP@0.5
* mAP@0.5:0.95

---

### 8.2 Latency Metrics

单位：

```text
ms
```

需要记录：

* preprocess latency
* inference latency
* postprocess latency
* output latency if needed
* total latency

统计项：

* average latency
* p50 latency
* p95 latency
* max latency if needed

---

### 8.3 Throughput Metrics

需要记录：

* FPS
* processed frame count
* dropped frame count if pipeline mode is used

注意：

```text
FPS / throughput 不等于 single-frame latency
```

Pipeline mode 可能提升 FPS，但不一定降低单帧端到端 latency。

---

### 8.4 Resource Metrics

尽量记录：

* CPU usage
* GPU usage
* memory usage
* power usage if available
* temperature if available

如果某项不可采集，记录：

```text
Not available
```

不得伪造。

---

## 9. Warmup 与 Measured Frames

每次性能测试应区分：

* warmup frames
* measured frames

warmup frames 不进入最终统计。

建议初始值：

```text
warmup_frames: 20
measured_frames: 500
```

最终数值可根据 Jetson 实际性能和测试输入长度调整。

调整后需记录在实验日志中。

---

## 10. 实验组 E1：模型精度实验

### 10.1 目的

验证 YOLOv8n 在 NEU-DET 上具备基本工业缺陷检测能力。

---

### 10.2 实验对象

| 项目          | 内容                                |
| ----------- | --------------------------------- |
| dataset     | NEU-DET                           |
| split       | train / val / test = 70 / 20 / 10 |
| model       | YOLOv8n                           |
| input sizes | 320, 416, 640                     |

---

### 10.3 指标

必须记录：

* Precision
* Recall
* mAP@0.5
* mAP@0.5:0.95

---

### 10.4 输出

输出内容：

* training log
* validation result
* model accuracy table
* sample detection images if needed

---

### 10.5 当前准备状态

截至 2026-07-11，E1 正式实验尚未开始，当前只完成前置验证：

* 真实 NEU-DET 已转换为 YOLO 格式，共 1800 张图片。
* split 固定为 train 1260、val 360、test 180，random seed 为 42。
* 删除 3 个完全重复 bbox 后，数据集包含 4186 个有效 bbox。
* 全量 label 校验结果为 `errors=0`。
* GTX 1050 Ti 本地 smoke training 已完成，用于验证 dataloader、预训练权重加载、forward/backward 和 checkpoint 保存链路。
* smoke 指标不作为 E1 baseline 结果，不填入论文精度表。
* 正式 baseline 配置已冻结为 640 输入、100 epochs、seed 42、`amp=false`，并已通过 dry-run。

正式 Precision、Recall、mAP 和 `best.pt` 仍为待完成项。

---

### 10.7 2026-07-12 更新：E1 训练阶段已完成

截至 2026-07-12，E1 模型精度实验（640 输入尺寸）已正式完成：

* V1 baseline、两个 seed-only repeat、seed=42 同参数 repeat、V2 extended schedule、V3 Mosaic controls、V4 AdamW + lr0、V5 cosine LR、V6 no warmup 共 9 组实验全部完成；真实 `args.yaml` 均为 `deterministic=true`。
* V2～V6 变体均未在 mAP50-95 上获得超过 baseline 的稳定提升。
* 最终冻结模型：seed=7 deterministic（`models/pytorch/yolov8n_neudet_frozen.pt`，SHA256 `5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7`）。
* Test split 最终评价：mAP50=0.769，mAP50-95=0.431。
* 320 和 416 输入尺寸的训练与评价不在训练阶段范围内 — 这些尺寸将仅在 ONNX/TensorRT 部署实验（E4）中通过输入 resize 评估推理性能差异，不重新训练模型。
* 详细结果见 `docs/TRAINING_FINAL_REPORT.md`。
* V2 配置为 200 epochs、patience 50，early stopping 后实际完成 161 epochs；V3 同时关闭 `mosaic` 和 `close_mosaic`；V4 同时设置显式 AdamW 和 `lr0=0.001`。V5、V6 为严格单变量实验。
* 真实 effective args、validation/test 指标、命令和 provenance 见 `results/training/evidence/`。test split 只在模型冻结后使用，未反向调参。

E1 状态：

```text
DONE — 640 训练实验完成，模型冻结，后续实验重点转向：
- PyTorch vs ONNX Runtime 输出一致性验证
- ONNX Runtime vs TensorRT FP16 性能对比（E2）
- Serial vs Pipeline 对比（E3）
- 320 / 416 / 640 输入尺寸推理对比（E4，不重新训练）
- 稳定性与资源占用测试（E5）
```

---

### 10.6 表格模板

| Model   | Input Size | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 |
| ------- | ---------: | --------: | -----: | ------: | -----------: |
| YOLOv8n |        320 |       TBD |    TBD |     TBD |          TBD |
| YOLOv8n |        416 |       TBD |    TBD |     TBD |          TBD |
| YOLOv8n |        640 |       TBD |    TBD |     TBD |          TBD |

---

## 11. 实验组 E2：Inference Backend 对比

### 11.1 目的

比较 ONNX Runtime baseline 与 TensorRT FP16 optimized backend 在 Jetson 上的性能差异。

---

### 11.2 对比对象

```text
ONNX Runtime
TensorRT FP16
```

---

### 11.3 控制变量

| 控制项             | 要求               |
| --------------- | ---------------- |
| device          | 同一 Jetson        |
| model           | 同一 YOLOv8n       |
| input size      | 同一尺寸             |
| input source    | 同一输入             |
| runtime mode    | 优先使用 Serial mode |
| preprocessing   | 一致               |
| postprocessing  | 一致               |
| warmup frames   | 一致               |
| measured frames | 一致               |

---

### 11.4 指标

必须记录：

* average latency
* p50 latency
* p95 latency
* FPS
* memory usage

建议记录：

* CPU usage
* GPU usage
* power usage
* temperature

---

### 11.5 表格模板

| Device | Input Size | Runtime Mode | Backend      | Precision Mode | Avg Latency ms | P50 ms | P95 ms | FPS | Memory MB |
| ------ | ---------: | ------------ | ------------ | -------------- | -------------: | -----: | -----: | --: | --------: |
| TBD    |        640 | Serial       | ONNX Runtime | FP32 / TBD     |            TBD |    TBD |    TBD | TBD |       TBD |
| TBD    |        640 | Serial       | TensorRT     | FP16           |            TBD |    TBD |    TBD | TBD |       TBD |

---

## 12. 实验组 E3：Runtime Mode 对比

### 12.1 目的

比较 Serial mode 与 Pipeline mode 对实时推理 throughput / FPS 的影响。

---

### 12.2 对比对象

```text
Serial mode
Pipeline mode
```

---

### 12.3 控制变量

| 控制项             | 要求                 |
| --------------- | ------------------ |
| device          | 同一 Jetson          |
| backend         | 优先使用 TensorRT FP16 |
| model           | 同一 YOLOv8n         |
| input size      | 同一尺寸               |
| input source    | 同一输入               |
| queue size      | Pipeline mode 中记录  |
| drop policy     | Pipeline mode 中记录  |
| measured frames | 一致或记录实际处理帧数        |

---

### 12.4 指标

必须记录：

* FPS
* total latency
* p95 latency
* processed frame count
* dropped frame count if available
* CPU usage
* GPU usage
* memory usage

---

### 12.5 重要解释规则

可以写：

```text
Pipeline mode improved throughput under the tested configuration.
```

不能直接写：

```text
Pipeline mode reduced latency.
```

除非真实数据支持。

必须区分：

* throughput / FPS
* single-frame latency
* end-to-end latency

---

### 12.6 表格模板

| Device | Backend       | Input Size | Runtime Mode | Queue Size | Drop Policy | FPS | Avg Total Latency ms | P95 ms | Dropped Frames |
| ------ | ------------- | ---------: | ------------ | ---------: | ----------- | --: | -------------------: | -----: | -------------: |
| TBD    | TensorRT FP16 |        640 | Serial       |        N/A | N/A         | TBD |                  TBD |    TBD |            TBD |
| TBD    | TensorRT FP16 |        640 | Pipeline     |          2 | drop_oldest | TBD |                  TBD |    TBD |            TBD |

---

## 13. 实验组 E4：Input Size 对比

### 13.1 目的

分析输入尺寸对 accuracy、latency、FPS 的影响。

---

### 13.2 对比对象

```text
320 × 320
416 × 416
640 × 640
```

---

### 13.3 控制变量

| 控制项           | 要求                 |
| ------------- | ------------------ |
| dataset       | 同一 NEU-DET split   |
| model family  | YOLOv8n            |
| device        | 同一 Jetson          |
| backend       | 优先使用 TensorRT FP16 |
| runtime mode  | 优先使用 Serial mode   |
| threshold     | 一致                 |
| NMS threshold | 一致                 |

---

### 13.4 指标

必须记录：

* Precision
* Recall
* mAP@0.5
* mAP@0.5:0.95
* average latency
* p95 latency
* FPS

---

### 13.5 表格模板

| Model   | Input Size | mAP@0.5 | mAP@0.5:0.95 | Avg Latency ms | P95 ms | FPS |
| ------- | ---------: | ------: | -----------: | -------------: | -----: | --: |
| YOLOv8n |        320 |     TBD |          TBD |            TBD |    TBD | TBD |
| YOLOv8n |        416 |     TBD |          TBD |            TBD |    TBD | TBD |
| YOLOv8n |        640 |     TBD |          TBD |            TBD |    TBD | TBD |

---

## 14. 实验组 E5：Stability Test

### 14.1 目的

验证系统在持续运行下是否具备基本工程稳定性。

---

### 14.2 测试时长

建议测试：

```text
10 minutes
30 minutes
60 minutes
```

如果时间不足，至少完成 10 minutes 测试。

---

### 14.3 控制变量

| 控制项           | 要求                    |
| ------------- | --------------------- |
| device        | Jetson                |
| backend       | TensorRT FP16         |
| runtime mode  | Serial 或 Pipeline，需注明 |
| input size    | 需注明                   |
| input source  | 固定输入源                 |
| output saving | 需注明是否开启               |

---

### 14.4 指标

必须记录：

* average FPS
* maximum memory usage
* abnormal exit status
* error count
* performance degradation if observable

建议记录：

* temperature
* power usage
* GPU usage

---

### 14.5 表格模板

| Device | Backend       | Runtime Mode | Input Size | Duration | Avg FPS | Max Memory MB | Abnormal Exit | Note |
| ------ | ------------- | ------------ | ---------: | -------- | ------: | ------------: | ------------- | ---- |
| TBD    | TensorRT FP16 | Serial       |        640 | 10 min   |     TBD |           TBD | TBD           | TBD  |
| TBD    | TensorRT FP16 | Pipeline     |        640 | 30 min   |     TBD |           TBD | TBD           | TBD  |

---

## 15. 实验日志格式

### 15.1 Per-frame CSV

建议文件名：

```text
per_frame_latency.csv
```

建议字段：

```text
run_id
timestamp
frame_index
backend
runtime_mode
input_size
precision_mode
preprocess_latency_ms
inference_latency_ms
postprocess_latency_ms
output_latency_ms
total_latency_ms
is_warmup
note
```

---

### 15.2 Summary JSON

建议文件名：

```text
summary.json
```

建议字段：

```json
{
  "run_id": "TBD",
  "timestamp": "TBD",
  "git_commit": "TBD",
  "device": "TBD",
  "jetpack_version": "TBD",
  "cuda_version": "TBD",
  "tensorrt_version": "TBD",
  "onnxruntime_version": "TBD",
  "model_name": "yolov8n",
  "input_size": "640",
  "backend": "tensorrt",
  "runtime_mode": "serial",
  "precision_mode": "fp16",
  "warmup_frames": 20,
  "measured_frames": 500,
  "avg_latency_ms": "TBD",
  "p50_latency_ms": "TBD",
  "p95_latency_ms": "TBD",
  "fps": "TBD",
  "cpu_usage_percent": "TBD",
  "gpu_usage_percent": "TBD",
  "memory_usage_mb": "TBD",
  "note": "TBD"
}
```

---

## 16. Run ID 规则

每次实验应生成唯一 `run_id`。

建议格式：

```text
YYYYMMDD_HHMMSS_device_backend_mode_size
```

示例：

```text
20260709_213000_jetson_tensorrt_serial_640
```

实验输出建议放在：

```text
experiments/logs/<run_id>/
experiments/results/<run_id>/
```

---

## 17. 实验输出目录

推荐结构：

```text
experiments/
├── configs/
├── logs/
│   └── <run_id>/
│       ├── per_frame_latency.csv
│       ├── summary.json
│       ├── config_snapshot.yaml
│       └── environment_snapshot.txt
├── results/
│   └── <run_id>/
│       ├── images/
│       └── detections.json
├── figures/
└── tables/
```

---

## 18. 论文表格来源规则

论文表格必须来自真实实验日志。

推荐流程：

```text
CSV / JSON logs
→ summarize_experiments.py
→ paper-ready tables
→ paper/tables/
```

论文图表不能手工编造。

如果图表基于筛选后的数据，必须记录筛选条件。

---

## 19. 结论表述规则

允许表述：

```text
在本实验配置下，TensorRT FP16 相比 ONNX Runtime 降低了推理延迟。
```

```text
在测试输入源和指定队列策略下，Pipeline mode 提高了系统 throughput。
```

```text
输入尺寸增大提高了检测精度，但也增加了推理延迟。
```

前提是有真实数据支持。

禁止表述：

```text
本方法提出了新型目标检测算法。
```

```text
Pipeline mode 一定降低延迟。
```

```text
TensorRT 在所有设备上都有固定倍数加速。
```

```text
本系统达到 state-of-the-art。
```

除非有严格证据，否则不使用夸大表达。

---

## 20. 当前待补充事项

| 事项                                | 状态  | 补充时机             |
| --------------------------------- | --- | ---------------- |
| Jetson model                      | TBD | Jetson 设备确定后     |
| JetPack version                   | TBD | Jetson 环境配置后     |
| CUDA version                      | TBD | Jetson 环境配置后     |
| TensorRT version                  | TBD | Jetson 环境配置后     |
| ONNX Runtime C++ version          | TBD | ONNX Runtime 集成前 |
| TensorRT engine generation method | TBD | TensorRT 部署前     |
| Resource monitoring method        | TBD | 性能实验前            |
| Warmup frames final value         | TBD | 初步性能测试后          |
| Measured frames final value       | TBD | 初步性能测试后          |
| Stability test input source       | TBD | 稳定性测试前           |
| Paper table final format          | TBD | 实验结果产生后          |

---

## 21. 更新规则

后续更新本文档时，应遵守：

1. 不删除已确定的核心实验目标。
2. 新增实验设计必须说明目的、控制变量、指标和输出。
3. 不记录虚构实验结果。
4. 实验结果应记录到日志文件，而不是只写在本文档中。
5. 如果实验设计发生重大变化，需要同步更新 `docs/personal/DECISIONS.md`。
6. 如果实验指标发生变化，需要同步更新 `docs/REQUIREMENTS.md`。
7. 如果实验影响系统结构，需要同步更新 `docs/ARCHITECTURE.md`。
8. 如果实验环境、硬件、驱动或依赖版本发生变化，需要同步更新 `docs/personal/ENVIRONMENT.md`。

---

## 22. Final Summary

本项目实验设计围绕：

```text
模型精度
→ backend 性能对比
→ runtime mode 对比
→ input size 权衡
→ 稳定性测试
```

实验目标是用真实数据证明：

* YOLOv8n 可以完成 NEU-DET 工业缺陷检测任务。
* TensorRT FP16 可以在 Jetson 上作为 optimized backend 进行评估。
* Pipeline mode 可以作为 runtime optimization 进行 throughput 分析。
* 输入尺寸会影响 accuracy 和 speed trade-off。
* 系统具备基本工程稳定性。
