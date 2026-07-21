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

当前规划状态：`M0–M5 CLOSED`；Stage J Plan v0.3：`FROZEN`；D041：`Accepted`；J0 Planning Freeze：`COMPLETE`；Stage J execution：`PENDING J1`；J1：`BLOCKED pending device`；Device-observed facts：`pending J1`；implementation branch：`feature/jetson-onnxruntime`。Stage T 和 Stage P 尚未开始。

| 环境 | 用途 | 当前状态 |
|---|---|---|
| Local Development PC | 代码开发、Python / C++ ONNX Runtime 验证 | M1 core contracts/CPU preprocessing 已完成；WSL2 GPU 当前不可访问 |
| Cloud Training Platform | YOLOv8n 训练、验证、ONNX export | 已知 GPU |
| Edge Deployment Platform | Stage J Jetson CPU baseline；后续 Stage T TensorRT FP16 | planned target; pending J1 |

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
| CMake version | 3.22.1 |
| CMake project minimum version | 3.16 |
| C++ compiler | GCC / G++ 11.4.0 |
| C++ language standard | C++17 |
| OpenCV C++ version | 4.5.4 |
| OpenCV Python version | 4.10.0.84 |
| yaml-cpp version | 0.7.0 |
| ONNX Runtime C++ runtime API version | 1.23.2（M0.3 已验证） |
| Python version | 3.10.12 |
| Virtual environment | `.venv` |

说明：

本地开发 PC 不作为论文核心性能实验平台。

### 4.1 2026-07-13 部署验证环境检查

使用项目 `.venv/bin/python` 和当前 WSL2 shell 实际检查：

| 检查项 | 结果 |
|---|---|
| Python | 3.10.12 |
| torch | 2.3.1+cu118 |
| `torch.version.cuda` | 11.8（PyTorch build version） |
| `torch.cuda.is_available()` | `False` |
| `torch.cuda.device_count()` | `0` |
| TensorRT Python binding | 未安装，`ModuleNotFoundError: tensorrt` |
| `nvidia-smi` | 失败，GPU access blocked by the operating system |

该检查只说明当前 WSL2 进程无法访问 CUDA GPU；不覆盖上方历史环境快照中的硬件和 driver 记录。当前环境可继续 Python / C++ ONNX Runtime 功能验证，但不作为 TensorRT FP16 validation 或论文性能实验平台。未执行 TensorRT、CUDA、driver 或系统级安装修改。

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
| GPU | RTX 3090 (24 GB) |
| OS | Ubuntu 22.04 (kernel 5.15.0-94-generic) |
| CPU | TBD |
| RAM | TBD |
| CUDA version | 11.8 |
| NVIDIA driver version | TBD |
| Python version | 3.10.8 |
| PyTorch version | 2.3.1+cu118 |
| torchvision version | 0.18.1+cu118 |
| Ultralytics version | 8.4.50 |
| OpenCV Python version | TBD |
| Virtual environment | `.venv` |

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
| Jetson model | planned target; pending J1 |
| JetPack version | planned target 6.2.2; pending J1 |
| Ubuntu / L4T version | planned target Ubuntu 22.04-based / L4T 36.5; pending J1 |
| CUDA version | pending J1 |
| TensorRT version | pending J1 / Stage T |
| cuDNN version | pending J1 |
| ONNX Runtime C++ version | planned 1.23.2 native source build; pending J1/J2 |
| OpenCV version | pending J1 |
| CMake version | pending J1 |
| C++ compiler | pending J1 |
| Power mode | planned MAXN_SUPER; pending J1 |
| Resource monitoring method | pending J1 |

说明：

Jetson 平台是 Stage J CPU baseline、后续 Stage T TensorRT FP16 部署和论文核心性能数据采集平台；本表为 planned target，不是 hardware observed fact。

### 6.1 Stage J Planned Jetson Target

> **Status: planned target; not yet observed on hardware. All device-specific values require J1 verification.**

```text
device: Jetson Orin Nano Super Developer Kit
memory: 8GB
storage: 256GB NVMe
root filesystem: NVMe
JetPack: 6.2.2
L4T: 36.5
architecture: aarch64
OS: Ubuntu 22.04-based
ONNX Runtime: 1.23.2 native source build
EP: CPUExecutionProvider
mode: MAXN_SUPER planned
cooling: active fan planned
build: native Jetson build
cross-compilation: excluded from Stage J
```

这些是冻结的 planned target 合同，不是 J0 或当前 WSL 环境的 Jetson observed facts。

### 6.2 J1 Observed Facts Placeholder

以下字段在 J1 前保持 `pending J1`，不得填入推测值：

| Field | Status |
|---|---|
| actual SKU | pending J1 |
| serial / board identifiers | pending J1 |
| actual JetPack | pending J1 |
| actual L4T | pending J1 |
| actual GCC | pending J1 |
| actual CMake | pending J1 |
| actual OpenCV | pending J1 |
| actual Python | pending J1 |
| actual online CPUs | pending J1 |
| actual allowed CPUs | pending J1 |
| actual MAXN_SUPER mode ID | pending J1 |
| actual thermal zones | pending J1 |
| actual frequency paths | pending J1 |
| actual tegrastats rails | pending J1 |
| actual OC/UV paths | pending J1 |
| actual power supply status | pending J1 |

---

## 7. 依赖版本记录要求

### 7.1 C++ Dependencies

需要在集成前或集成时记录：

| Dependency | Version | Status |
|---|---|---|
| OpenCV | 4.5.4 | C++17 include/compile/link/run probe verified in M1.0 |
| yaml-cpp | 0.7.0 | CONFIG package target `yaml-cpp`；M1.2 loader compile/link/test verified |
| ONNX Runtime C++ SDK | 1.23.2 | Runtime API and CPU Provider verified in M0.3 |
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
| onnx | 1.16.1 | Verified |
| onnxruntime (Python package) | 1.23.2 | Verified for Python reference validation |
| tensorrt | Not installed | Deferred to compatible CUDA / Jetson platform |
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

### 7.3 ONNX Runtime C++ SDK（M0.2）

Python `onnxruntime` package 与 C++ SDK 是两个独立依赖。本节只记录 C++
SDK 的本地依赖接入，不代表已经调用 runtime API、验证 Provider、加载模型或执行推理。

| 项目 | 当前值 |
| --- | --- |
| Official package | `onnxruntime-linux-x64-1.23.2.tgz` |
| Version | 1.23.2 |
| Platform | Linux x64 CPU |
| Official URL | `https://github.com/microsoft/onnxruntime/releases/download/v1.23.2/onnxruntime-linux-x64-1.23.2.tgz` |
| Archive size | `8309231` bytes |
| Archive local SHA256 | `1fa4dcaef22f6f7d5cd81b28c2800414350c10116f5fdd46a2160082551c5f9b` |
| Local extraction path | `third_party/onnxruntime/1.23.2/linux-x64/` |
| Current `ONNXRUNTIME_ROOT` | `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/third_party/onnxruntime/1.23.2/linux-x64` |
| Shared library | `lib/libonnxruntime.so -> libonnxruntime.so.1 -> libonnxruntime.so.1.23.2` |
| `ldd` result | All dependencies resolved; no `not found` entries |
| M0.2 status | Dependency integrated; no ORT API call |
| M0.3 status | Runtime API version and CPU Provider verified |
| M0 final status | Runtime, model contract and synthetic inference smoke verified |

该 SHA256 仅用于记录本次本地下载文件和后续文件一致性检查；未与发布方独立
digest 核对，不表述为官方真实性验证。

### 7.4 ONNX Runtime C++ API smoke（M0.3）

| 检查项 | 实际结果 |
| --- | --- |
| Runtime API version | `1.23.2` |
| Available providers | `CPUExecutionProvider` |
| CPUExecutionProvider | PASS |
| `Ort::Env` lifecycle | PASS |
| `Ort::SessionOptions` lifecycle | PASS |
| Smoke executable | `build/tests/test_ort_runtime_smoke` |
| Dynamic library | 项目 SDK 的 `libonnxruntime.so.1.23.2` |
| Unset `LD_LIBRARY_PATH` | PASS，依靠 build RUNPATH 解析项目 SDK |
| M0.4 model loading | Not executed |
| M0.5 synthetic inference | Not executed |

本次仅验证 runtime API、精确版本、available Provider 与基础对象生命周期；
没有创建 `Ort::Session`、加载模型、创建 tensor 或执行推理。

### 7.5 Frozen ONNX model contract smoke（M0.4）

| 检查项 | 实际结果 |
| --- | --- |
| Frozen ONNX path | `models/onnx/yolov8n_neudet_frozen.onnx` |
| File size | `12242487` bytes |
| SHA256 | `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944` |
| `Ort::Session` model load | PASS |
| Input count | `1` |
| Input metadata | `images`, `float32`, `[1,3,640,640]` |
| Output count | `1` |
| Output metadata | `output0`, `float32`, `[1,10,8400]` |
| Static positive dimensions | PASS |
| Model contract | PASS |
| Missing model path | Expected load failure detected |
| Intentional metadata mismatch | Expected input-name mismatch detected |
| M0.5 synthetic inference | Not executed |

本次只创建 Session 并查询模型 metadata；没有创建输入 tensor、调用
`Session::Run`、读取推理输出或执行性能测试。

### 7.6 Frozen ONNX synthetic inference smoke（M0.5）

| 检查项 | 实际结果 |
| --- | --- |
| Runtime | ONNX Runtime C++ 1.23.2 default CPU runtime |
| Synthetic input dtype | `float32` |
| Synthetic input shape | `[1,3,640,640]` |
| Synthetic input elements | `1228800` |
| Synthetic input value | `0.5F` |
| Input tensor creation | PASS |
| `Session::Run` | PASS，单次同步执行 |
| Output dtype | `float32` |
| Output shape | `[1,10,8400]` |
| Output elements | `84000` |
| Finite count | `84000` |
| NaN count | `0` |
| Positive infinity count | `0` |
| Negative infinity count | `0` |
| Diagnostic output min / max | `0` / `638.494`，不作为验收阈值 |
| Performance test | Not performed |
| Warm-up | Not performed |
| Formal `OnnxRuntimeEngine` | Not implemented |
| Next step | M0.6 closeout |

本次只证明当前 C++ ONNX Runtime CPU 能使用真实 frozen model 完成一次
synthetic inference，并验证输出 shape、element count 与数值有限性；不形成性能、
模型精度或正式 baseline 结论。

### 7.7 M0.6 最终环境与回归状态

| 检查项 | 最终结果 |
| --- | --- |
| CMake minimum / current | `3.16` / `3.22.1` |
| Compiler / C++ standard | GCC / G++ `11.4.0` / C++17 |
| ONNX Runtime C++ SDK | Linux x64 CPU `1.23.2` |
| Archive size / SHA256 | `8309231` bytes / `1fa4dcaef22f6f7d5cd81b28c2800414350c10116f5fdd46a2160082551c5f9b` |
| SDK extraction path | `third_party/onnxruntime/1.23.2/linux-x64/` |
| Runtime API version / Provider | `1.23.2` / `CPUExecutionProvider` PASS |
| Dynamic library source | 项目 SDK 的 `libonnxruntime.so.1.23.2`，无 `not found` |
| Frozen ONNX size / SHA256 | `12242487` bytes / `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944` |
| Input contract | `images`, `float32`, `[1,3,640,640]` |
| Output contract | `output0`, `float32`, `[1,10,8400]` |
| Synthetic inference | `84000` finite；NaN / positive Inf / negative Inf 均为 `0` |
| Model Smoke OFF | 2/2 CTest PASS |
| Model Smoke ON | 6/6 CTest PASS |
| Formal `OnnxRuntimeEngine` | Not implemented |
| Performance data | Not collected |
| Jetson / TensorRT validation | Not performed |

M0 工程、依赖与真实模型 smoke 验证完成。该结果是本地 WSL2 CPU 功能验证，
不是正式 C++ Serial Baseline、Jetson/TensorRT 验证或性能证据。

### 7.8 M1.0 C++ dependency capability probe

| 检查项 | 实际结果 |
| --- | --- |
| OpenCV C++ | `4.5.4`，`pkg-config opencv4` 可用 |
| OpenCV headers | `core.hpp`、`imgproc.hpp`、`imgcodecs.hpp` 可用 |
| OpenCV operations | `cv::Mat`、`cv::resize`、`IMREAD_IGNORE_ORIENTATION` 编译链接运行 PASS |
| yaml-cpp | `0.7.0`，`pkg-config yaml-cpp` 可用 |
| yaml-cpp operations | `YAML::Load`、标量和序列读取编译链接运行 PASS |
| Probe compiler | GCC/G++ `11.4.0`，C++17 |
| System changes | 未安装、升级或修改系统依赖 |

Python reference 使用 OpenCV `4.10.0`，与 C++ OpenCV `4.5.4` 不同。当前不升级
任一侧；M1.5 通过 Level A 实测后再依据证据判断，不预先放宽容差。

### 7.9 M1.2 Frozen Model Contract 环境与验证状态

| 检查项 | 实际结果 |
| --- | --- |
| yaml-cpp version | `0.7.0` |
| CMake package mode | `find_package(yaml-cpp 0.7 REQUIRED CONFIG)` |
| Exported CMake target | `yaml-cpp` |
| Formal contract path | `configs/model_contracts/yolov8n_neudet_frozen.yaml` |
| Contract schema version | `1` |
| `test_model_contract` | 43/43 PASS |
| Model Smoke OFF CTest | 3/3 PASS |
| Current production capability | core contracts + strict model contract loader |
| OpenCV in production CMake | Not integrated yet |
| Preprocessor | Not started |

当前 loader 只读取并校验 Git-tracked contract YAML，不加载 ONNX、不计算模型
SHA256、不调用 ONNX Runtime。OpenCV C++ `4.5.4` 仅完成 M1.0 capability probe，
尚未接入生产 CMake target。

### 7.10 M1 最终环境与验证状态

| 检查项 | 最终结果 |
| --- | --- |
| CMake minimum / current | `3.16` / `3.22.1` |
| GCC / G++ | `11.4.0` |
| C++ standard | C++17 |
| yaml-cpp | `0.7.0` |
| ONNX Runtime C++ SDK/runtime | `1.23.2` / `1.23.2` |
| C++ OpenCV | `4.5.4` |
| Python / NumPy / Python OpenCV | `3.10.12` / `1.26.4` / `4.10.0` |
| Formal contract | `configs/model_contracts/yolov8n_neudet_frozen.yaml` |
| Level A assets | `tests/data/preprocess_level_a/` |
| Level A report | `results/validation/preprocess_level_a/level_a_report.json` |
| Level A provenance | `results/validation/preprocess_level_a/provenance.json` |
| Level A result | 8/8 PASS；MAE/max_abs 均为 `0` |
| Model Smoke OFF / ON | 10/10 PASS / 14/14 PASS |
| strict / ASan+UBSan | 10/10 PASS / 10/10 PASS |
| Current production capability | core contracts + model contract loader + LetterBox + CPU `Preprocessor` |

Level A raw BGR/golden 资产由 18 项 `SHA256SUMS` 和 manifest 中 16 个 asset
digest 自动交叉验证；validator 在打开资产前执行 resolved realpath containment。
stable provenance 引用前置 evidence source commit
`a7d21ce18f988fccf62f467bcf9a4eae367c5b79`，不包含时间、主机、用户、绝对路径
或 build/temp 路径。

M1 的 test-only manifest、compare helper 和 evidence verifier 不链接 production
target。正式 `OnnxRuntimeEngine` 尚未实现，当前没有性能数据；WSL2 GPU 仍不可用，
Jetson/TensorRT 尚未验证。

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
| ONNX Runtime C++ version | 1.23.2，runtime API 与 CPU Provider 已在 M0.3 验证 |
| OpenCV version | C++ 项目骨架创建前 |
| CMake minimum version | 3.16，已在 M0.1 冻结 |
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

* 本地 GTX 1050 Ti Python 训练环境已通过 smoke training 验证。
* RTX 3090 训练环境已通过 9 组正式 YOLOv8n baseline 实验验证，环境信息已记录。
* 训练阶段已完成，模型已冻结为 `models/pytorch/yolov8n_neudet_frozen.pt`。
* ONNX export、ONNX Runtime smoke test 和 PyTorch / ONNX Runtime consistency validation 已在本地 Python 环境通过。
* C++ 工程最低 CMake 版本为 3.16；当前实际开发环境使用 CMake 3.22.1、GCC / G++ 11.4.0 和 C++17。
* ONNX Runtime C++ 1.23.2 runtime API、CPUExecutionProvider、`Ort::Env` 与 `Ort::SessionOptions` 已在 M0.3 验证。
* Frozen ONNX 的文件哈希、Session 加载和静态输入输出 metadata 合同已在 M0.4 验证。
* M0.4 missing-model、contract-mismatch 和 non-tensor 检查已在 M0.5A 加固。
* M0.5 已使用常量 `0.5F` synthetic tensor 完成一次真实 CPU inference，输出 84000 个元素全部 finite。
* M0.6 最终回归、边界审计、资产复核和文档收尾已通过，M0 阶段正式关闭。
* M1.1～M1.6 已完成并正式关闭；当前正式生产能力为 core contracts、model contract loader、LetterBox 与 CPU `Preprocessor`。
* Level A 8/8、SHA/provenance 自动验收、Model Smoke OFF/ON、strict 与 ASan/UBSan 最终回归均已通过。
* 下一阶段为 M2 `ONNX Runtime Engine`，当前尚未开始。
* 正式 `OnnxRuntimeEngine` 仍未实现，当前生产程序继续保持 runtime skeleton。
* 当前 WSL2 进程无法访问 CUDA GPU 且未安装 TensorRT Python binding；TensorRT FP16 validation 延后到 Jetson 或兼容 CUDA / TensorRT 平台。
* 进入目标设备部署实验前，必须补齐 Jetson、JetPack、TensorRT 和资源监控方法等信息。

---

## 12. 环境用途隔离

| 环境 | 用途 | 当前阶段边界 |
| --- | --- | --- |
| WSL2 Ubuntu 22.04 | C++ 开发、ONNX Runtime CPU、软件架构验证 | 当前 C++ Serial Baseline 开发环境 |
| RTX 3090 | 训练、frozen model 生成、模型导出 | 不承担当前 C++ baseline 或 Jetson 性能结论 |
| Jetson | TensorRT、FP16、目标设备性能测试 | TensorRT 与性能阶段开始后使用 |

不同环境的用途必须隔离记录；不得将 WSL2 CPU 验证表述为 Jetson 或 TensorRT 性能证据。
