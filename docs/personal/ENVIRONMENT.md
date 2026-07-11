# ENVIRONMENT.md

## 1. 用途

本文档用于记录本项目开发、训练、部署和实验相关的真实环境信息。

项目名称：

**边缘 AI 工业缺陷检测部署与优化项目**

英文名称：

**Edge AI Industrial Defect Detection Deployment and Optimization**

本文档只记录已确认或待确认的环境信息。

不得伪造硬件型号、软件版本、驱动版本、性能数据或实验结果。

如果环境信息尚未确认，必须写：

```text
TBD
```

如果某项信息无法采集，必须写：

```text
Not available
```

---

## 2. 环境记录原则

每次影响构建、训练、推理或实验复现的环境变化，都应更新本文档。

必须记录：

* 硬件平台。
* 操作系统。
* GPU / accelerator。
* CUDA / TensorRT / JetPack。
* ONNX Runtime C++ version。
* OpenCV version。
* CMake version。
* Python version。
* Python package versions when relevant。
* Git commit used for experiments。

实验日志中的 `environment_snapshot.txt` 或 `summary.json` 应与本文档保持一致。

---

## 3. 当前环境总览

| 环境 | 用途 | 当前状态 |
|---|---|---|
| Local Development PC | 代码开发、本地 smoke training、C++ 初步验证 | Python 训练环境已验证 |
| Cloud Training Platform | YOLOv8n 训练、验证、ONNX export | 已知 GPU |
| Edge Deployment Platform | Jetson TensorRT FP16 部署和论文核心性能实验 | TBD |

---

## 4. Local Development PC

用途：

* 代码开发。
* C++ 编译。
* 基础 ONNX Runtime 验证。
* 小规模功能测试。

当前已知信息：

| 项目 | 当前值 |
|---|---|
| GPU | NVIDIA GeForce GTX 1050 Ti, 4096 MiB |
| OS | Ubuntu 22.04.5 LTS on WSL2 |
| CPU | TBD |
| RAM | TBD |
| NVIDIA driver supported CUDA | 13.0 (`nvidia-smi`) |
| PyTorch CUDA runtime | 11.8 |
| cuDNN version | 8.7.0 / 8700 |
| NVIDIA driver version | 582.28 |
| CMake version | TBD |
| C++ compiler | TBD |
| OpenCV Python version | 4.10.0.84 |
| yaml-cpp version | TBD |
| ONNX Runtime C++ version | TBD |
| Python version | 3.10.12 |
| Virtual environment | `.venv` |

说明：

本地开发 PC 不作为论文核心性能实验平台。

---

## 5. Cloud Training Platform

用途：

* YOLOv8n training。
* Model validation。
* ONNX export。
* Training record generation。

当前已知信息：

| 项目 | 当前值 |
|---|---|
| GPU | RTX 3090 |
| OS | TBD |
| CUDA version | TBD |
| NVIDIA driver version | TBD |
| Python version | TBD |
| PyTorch version | TBD |
| Ultralytics version | TBD |
| OpenCV Python version | TBD |

说明：

云端训练平台不作为最终边缘部署性能实验平台。

---

## 6. Edge Deployment Platform

用途：

* ONNX Runtime vs TensorRT FP16 comparison。
* Serial mode vs Pipeline mode comparison。
* Input size comparison。
* Stability test。
* Paper-level performance data collection。

当前状态：

| 项目 | 当前值 |
|---|---|
| Jetson model | TBD |
| JetPack version | TBD |
| Ubuntu / L4T version | TBD |
| CUDA version | TBD |
| TensorRT version | TBD |
| cuDNN version | TBD |
| ONNX Runtime C++ version | TBD |
| OpenCV version | TBD |
| CMake version | TBD |
| C++ compiler | TBD |
| Power mode | TBD |
| Resource monitoring method | TBD |

说明：

Jetson 平台是最终 TensorRT FP16 部署和论文核心性能数据采集平台。

---

## 7. 依赖版本记录要求

### 7.1 C++ Dependencies

需要在集成前或集成时记录：

| Dependency | Version | Status |
|---|---|---|
| OpenCV | TBD | TBD |
| yaml-cpp | TBD | TBD |
| ONNX Runtime C++ API | TBD | TBD |
| TensorRT | TBD | TBD |
| CUDA Runtime | TBD | TBD |
| GoogleTest | TBD | Optional |

### 7.2 Python Dependencies

需要在训练、导出或分析脚本可运行后记录：

| Dependency | Version | Status |
|---|---|---|
| Python | 3.10.12 | Verified |
| ultralytics | 8.4.50 | Verified |
| torch | 2.3.1+cu118 | Verified |
| torchvision | 0.18.1+cu118 | Verified |
| opencv-python | 4.10.0.84 | Verified |
| numpy | 1.26.4 | Verified |
| pyyaml | 6.0.2 | Verified |
| matplotlib | 3.8.4 | Verified |
| pandas | Not installed | Not required by current training launcher |

完整依赖版本记录：

```text
requirements-lock.txt
```

项目级环境快照：

```text
environment_snapshot.txt
```

本地 `.venv` 已通过 `pip check`，结果为 `No broken requirements found`。

---

## 8. 实验环境快照要求

每次正式实验应保存环境快照。

推荐输出：

```text
experiments/logs/<run_id>/environment_snapshot.txt
```

快照至少包含：

* run_id。
* git commit。
* device name。
* OS / JetPack / L4T。
* CUDA version。
* TensorRT version。
* ONNX Runtime version。
* OpenCV version。
* model path。
* engine path if TensorRT is used。
* config path。
* power mode if available。

如果某项无法采集，写 `Not available`。

---

## 9. 待确认事项

| 事项 | 决策时机 |
|---|---|
| Jetson model | 本地 ONNX Runtime baseline 跑通后 |
| JetPack version | Jetson 设备确定后 |
| CUDA version | JetPack version 确定后 |
| TensorRT version | JetPack version 确定后 |
| ONNX Runtime C++ version | C++ ONNX Runtime 集成前 |
| OpenCV version | C++ 项目骨架创建前 |
| CMake minimum version | C++ 项目骨架创建前 |
| TensorRT engine generation method | Jetson TensorRT 部署前 |
| Resource monitoring method | 性能实验前 |

---

## 10. 更新规则

后续 agent 更新本文档时，必须遵守：

1. 只记录真实环境信息。
2. 不得把 `TBD` 写成具体版本，除非已经确认。
3. 环境变化影响实验结果时，必须同步更新 `docs/personal/EXPERIMENT_PLAN.md` 或实验日志说明。
4. 环境选择变成技术决策时，必须同步更新 `docs/personal/DECISIONS.md`。
5. 不删除历史环境记录；如果需要，可追加新的环境快照小节。

---

## 11. 当前结论

当前本地 Python 训练环境已经建立并通过真实 YOLO smoke training 验证。

正式 baseline training 前仍需在 RTX 3090 平台采集独立环境快照。进入部署实验前，必须补齐 Jetson、JetPack、TensorRT、ONNX Runtime C++ 和资源监控方法等信息。
