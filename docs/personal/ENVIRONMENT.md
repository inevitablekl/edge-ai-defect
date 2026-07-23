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

## 13. Stage J J1.1 Device Acceptance

J1.1 状态：`COMPLETE`。

本节只记录 J1.1 已观察并验收的 Jetson 设备事实；J1.2～J1.4 的平台、工具链、功耗、时钟、温度和 rail/OC/UV 验收仍未完成。

- 设备型号：NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super。
- Architecture：`aarch64`；device-tree compatible 包含 `nvidia,tegra234`。
- L4T observed：`R36.5.0`。
- MemTotal：`7,976,910,848` bytes；与 nominal 8GB SKU 合理一致。
- NVMe：PUSKILL 256GB，`256,060,514,304` bytes；未记录设备序列号。
- Rootfs：位于 NVMe，ext4，read-write；J1.1 采集时约 11% 使用率。
- Boot：bootloader slot A/B 均报告 `normal`；NVIDIA L4T bootloader/core/initrd/kernel 包存在。
- NVMe SMART：critical warning `0`，media errors `0`，error log 无明确当前故障。
- `unsafe_shutdowns=11`：历史累计计数；当前无 media error、critical warning 或 SMART error log，后续需观察是否增长。
- Network/SSH：available。
- sudo：通过 command-scoped read-only wrapper 进行特权采集；unrestricted NOPASSWD 为 false。
- Active fan：`USER_CONFIRMED`。
- Heatsink secure：`USER_CONFIRMED`。
- Stable original power adapter：`USER_CONFIRMED`。
- Device exclusivity：`USER_CONFIRMED`。
- Known random reboot, power loss or NVMe drop：用户未报告。

Carry-forward warnings：CMake 缺失；OpenCV pkg-config/CMake metadata 缺失；Python `cv2` 不可用；当前 nvpmodel mode 为 15W；MAXN_SUPER 尚未验证；jetson_clocks 查询要求 root；unsafe shutdown counter 需后续观察。

J1.1 期间未安装软件，未改变 nvpmodel、时钟、风扇或系统配置，未运行 build/test/benchmark。原始采集保存在仓库外临时目录，未作为 Published Evidence 或 Git 文件。

## 14. Stage J J1.2 Platform and Toolchain Inventory

J1.2 状态：`COMPLETE`。

### Observed platform

- OS：Ubuntu 22.04.5 LTS。
- Kernel：`5.15.185-tegra`。
- Architecture：`aarch64`。
- L4T：`R36.5.0`；NVIDIA L4T package family observed at `36.5.0-20260115194252`。
- glibc：`2.35`。
- Online/allowed CPUs：`0-5` / `0-5`。

### JetPack and NVIDIA provenance

- Installed `nvidia-jetpack` meta-package：not installed。
- APT metadata candidate：`nvidia-jetpack 6.2.2+b24`；`nvidia-jetpack-runtime` and `nvidia-jetpack-dev` have the same candidate.
- NVIDIA APT sources：configured for Jetson `common`, `t234` and `ffmpeg`, repository series `r36`。
- Exact installed JetPack version：not independently verified；the APT candidate is not evidence that the meta-package is installed.
- L4T/core/kernel/bootloader/initrd/tools packages：installed and consistent with observed L4T `R36.5.0`。

### Native toolchain

- GCC/G++：`11.4.0`。
- CMake/CTest：missing。
- Make：`4.3`。
- Ninja：missing。
- pkg-config：`0.29.2`。
- Git：`2.34.1`。
- binutils：installed；`readelf` and `objdump` available。
- `patchelf`：missing。

Capability/remediation matrix：

| Capability | Observed | Required milestone | Deadline/action |
|---|---|---|---|
| GCC/G++/Make | present | J2/J3 | none currently |
| CMake/CTest | missing | J2.1/J2.2/J3 | user-approved minimal installation before first CMake task |
| Ninja | missing | optional | no action unless selected by later build protocol |
| pkg-config/binutils | present | J2/J3 | none currently |
| patchelf | missing | J2.3 if required by packaging | assess before J2.3 |

### Python

- Python：`/usr/bin/python3.10`, version `3.10.12`。
- python3-dev：installed。
- pip/ensurepip：unavailable。
- venv：package not installed。
- NumPy：`1.21.5`；PyYAML：`5.4.1`。
- ONNX, ONNX Runtime Python and Python `cv2`：unavailable。
- Python TensorRT binding：unavailable (ImportError)。

### OpenCV C++

Classification: `RUNTIME_AND_HEADERS_PRESENT_METADATA_MISSING`。

- Runtime libraries：present。
- Headers/component headers：present。
- Version: `4.5.4`。
- Debian component packages: `4.5.4+dfsg-9ubuntu4` installed for core/imgproc/imgcodecs development and runtime components。
- pkg-config metadata: missing。
- CMake package metadata: missing。
- Python `cv2`: unavailable。
- CUDA support: not required by Stage J1.2。
- J3 impact: native configure/build remains blocked until metadata and build dependency remediation is defined and completed。

### yaml-cpp and ONNX Runtime

- yaml-cpp: `NOT_FOUND`; header, runtime, pkg-config metadata and CMake metadata not found. This blocks J3 configure/build until remediation。
- System ONNX Runtime: not found; Python ONNX Runtime unavailable. This is expected to be resolved by the official ONNX Runtime 1.23.2 build in J2 and is not a J1.2 failure。

### CUDA/cuDNN/TensorRT pre-existing facts

These are recorded only and were not used by Stage J:

- CUDA toolkit/runtime: `/usr/local/cuda-12.6`, toolkit `12.6.11`, cudart `12.6.68`。
- cuDNN runtime libraries: present; `libcudnn9`/`libcudnn9-dev` package status was not installed in dpkg query。
- TensorRT packages: `10.3.0.30-1+cuda12.5` runtime/dev/parser packages installed。
- `trtexec`: unavailable。
- TensorRT Python binding: unavailable。
- No TensorRT smoke, CUDA inference or Stage T work was executed。

### Package and storage health

- `dpkg --audit`: no output; no incomplete package state observed。
- Held packages: none observed。
- Root, `/var` and `/tmp`: NVMe ext4, approximately 11% used, approximately 211 GB available。

### Planned versus observed summary

| Field | Planned target | Observed fact | Status |
|---|---|---|---|
| Device | Jetson Orin Nano Super | Jetson Orin Nano Engineering Reference Developer Kit Super | MATCH |
| Memory | nominal 8GB | MemTotal 7,976,910,848 bytes | MATCH |
| NVMe | 256GB class | 256,060,514,304 bytes | MATCH |
| Architecture | aarch64 | aarch64 | MATCH |
| Ubuntu | 22.04 | 22.04.5 LTS | MATCH |
| L4T | 36.5 planned | R36.5.0 | MATCH |
| JetPack | 6.2.2 planned | APT candidate 6.2.2+b24; meta-package not installed | NOT_INDEPENDENTLY_VERIFIED |
| GCC/G++ | 11.x | 11.4.0 | MATCH |
| glibc | 2.35 | 2.35 | MATCH |
| CMake | required | not installed | NOT_INSTALLED |
| OpenCV C++ | 4.x | 4.5.4 runtime/headers, metadata missing | OBSERVED_DIFFERENCE |
| yaml-cpp | 0.7.x | not found | NOT_INSTALLED |
| Python | 3.10 | 3.10.12 | MATCH |
| Online/allowed CPUs | 0-5 / 0-5 | 0-5 / 0-5 | MATCH |
| ORT | official 1.23.2 in J2 | not found | NOT_INSTALLED |
| CUDA/cuDNN/TensorRT | recorded only | CUDA 12.6, cuDNN libs, TensorRT 10.3 observed | NOT_APPLICABLE_IN_J1.2 |

J1.2 did not install packages, modify APT sources, alter system settings, run configure/build/test/benchmark, or begin J1.3。

## 15. Stage J J1.3 MAXN_SUPER and Clock-Control Acceptance

J1.3 状态：`COMPLETE`。

- Phase A discovery：`DISCOVERY_PASS`；active nvpmodel configuration SHA256 remained `5b3c6779df10506928fb9f6a9213d7a9ad0c4ef0a3fe542a95031103079a2dcf`。
- Pre-change mode：15W / ID `0`；post-change mode：`MAXN_SUPER` / ID `2`。
- MAXN_SUPER apply：observed successful；未使用 `--force`；无需 reboot，boot ID unchanged。
- CPU online set：`0-5` before and after。
- `jetson_clocks` apply：observed successful；CPU locked at `1728000`，GPU locked at `1020000000`，EMC observed at `3199000000`。
- `jetson_clocks --fan` apply：observed successful；PWM observed `255`，`FAN Dynamic Speed Control=disabled`。
- Post-state `nvfancontrol.service`：enabled but inactive after fan-control apply；该状态与 `jetson_clocks --fan` 的 observed state 一致。
- Post-state `nvpmodel.service`：enabled but inactive after boot-time completion。
- No silent fallback：post-change query remained `MAXN_SUPER` / ID `2`。
- NVMe `unsafe_shutdowns` remained `11`；SMART critical warning/media errors remained clear。
- Phase B used only the command-scoped power-control wrapper and the existing read-only wrapper；unrestricted sudo remained unavailable。

The first Phase B attempt stopped before system changes because Codex could not read the root-owned sudoers SHA. The second stopped before system changes because the two user-provided SHA labels conflicted. The user then supplied explicitly labelled wrapper/sudoers SHA values and `visudo` validation evidence; wrapper SHA was independently rechecked by Codex.

J1.3 did not install packages, modify wrappers/sudoers, run build/test/benchmark, or perform reboot. This acceptance does not complete J1.4 thermal, rail, OC/UV or long-duration stability work.

## 16. Stage J J1.4 Telemetry and Throttling Contract

J1.4 状态：`COMPLETE`。Decision D042：`Accepted`。

J1.4 使用 composite immutable discovery evidence v1：

- Phase A raw SHA256：`91eb86daebd31a96e6ddc74b9beda89c7aa466e7d74f0da53a0ea291689f99a0`；覆盖 thermal、frequency、EMC、tegrastats、rail-name、environment-drift 和 sustained-throttling discovery。
- Supplemental raw SHA256：`75cb07a6149b6b69b3774397ee58bd754743aa7df9181f86d9749833d17732a5`；覆盖 OC/UV counters、throttle-enable fields、hwmon identity/realpath、INA3221 labels 和 alarm values。
- 两个 raw attempt 均 repository-external、untracked、immutable、not Published Evidence；不修改旧 raw、不伪装为单一 raw。

### Thermal

Raw unit 为 milli-degree Celsius；正式 Gate 使用 raw integer，展示时除以 `1000.0`。Readable relevant set：

- `cpu-thermal`：`/sys/class/thermal/thermal_zone0/temp`
- `gpu-thermal`：`/sys/class/thermal/thermal_zone1/temp`
- `soc0-thermal`：`/sys/class/thermal/thermal_zone5/temp`
- `soc1-thermal`：`/sys/class/thermal/thermal_zone6/temp`
- `soc2-thermal`：`/sys/class/thermal/thermal_zone7/temp`
- `tj-thermal`：`/sys/class/thermal/thermal_zone8/temp`

`cv0-thermal`、`cv1-thermal`、`cv2-thermal` 位于 `thermal_zone2-4`，稳定返回 `EAGAIN`，仅纳入 inventory，不纳入 numeric hard maximum，不转换为零。正式样本要求所有 required readable zones 成功读取；不 forward-fill、不插值。Passive/critical trip 和 formal `T_idle_ref` 规则由 D042 冻结；本任务未建立正式 `T_idle_ref`。

### Frequency and EMC

- CPU sources：policy0/policy4 `scaling_cur_freq`；affected CPUs 分别为 `0-3`、`4-5`；target/min/max `1728000 kHz`；governor `schedutil`。
- GPU source：`/sys/devices/platform/bus@0/17000000.gpu/devfreq/17000000.gpu/cur_freq`；target/min/max `1020000000 Hz`；governor `nvhost_podgov`。
- EMC cap source：`/sys/kernel/nvpmodel_clk_cap/emc`，`3199000000 Hz`；`jetson_clocks --show` current/max 为 `3199000000`，`FreqOverride=1`。未发现可靠普通用户可读的独立 1 Hz EMC runtime source；EMC 只做 preflight/postflight Gate。

### tegrastats and rails

`/usr/bin/tegrastats` 来自 `nvidia-l4t-tools 36.5.0-20260115194252`，正式 interval 为 `1000 ms`，每行记录 UTC 和 `CLOCK_MONOTONIC ns`。Gap `>2500 ms`、coverage `<0.90` 或 sample count 不足会使 run invalid。

冻结 rail-name set：`VDD_IN`、`VDD_CPU_GPU_CV`、`VDD_SOC`。格式为 `current_power / average_power`，单位 mW；first value 用于正式统计，second value 仅保留为 device-emitted diagnostic。该数据只称为 onboard rail telemetry，不称为 wall power 或精密能量测量。

### OC/UV and INA3221

`soctherm_oc` realpath：`/sys/devices/platform/soctherm-oc-event/hwmon/hwmon3`。

| Event | Counter | Enable | Observed |
|---|---|---|---|
| OC1 Under Voltage | `/sys/class/hwmon/hwmon3/oc1_event_cnt` | `oc1_throt_en` | `0 / 1` |
| OC2 Average Overcurrent | `/sys/class/hwmon/hwmon3/oc2_event_cnt` | `oc2_throt_en` | `0 / 1` |
| OC3 Instantaneous Overcurrent | `/sys/class/hwmon/hwmon3/oc3_event_cnt` | `oc3_throt_en` | `0 / 1` |

Counters 为 cumulative；每个 attempt/campaign 记录 start/end delta，不清零 counter；正 delta 为 hard failure，reboot 后必须重新建立 baseline。

INA3221 realpath：`/sys/devices/platform/bus@0/c240000.i2c/i2c-1/1-0040/hwmon/hwmon1`。Labels：`in1_label=VDD_IN`、`in2_label=VDD_CPU_GPU_CV`、`in3_label=VDD_SOC`、`in7_label=sum of shunt voltages`。Observed alarm paths：`curr1/2/3_crit_alarm`、`curr1/2/3_max_alarm`、`curr4_crit_alarm`，全部 observed value 为 `0`；formal telemetry 每秒采样，任一非零 alarm 为 hard failure。

### Sustained throttling and environment drift

D042 冻结 `Stage J Sustained Throttling Algorithm v1`：每秒使用 monotonic timestamp 采集 CPU policy0/policy4 和 GPU runtime frequency；同一 source 连续 3 个有效样本低于 target 即 hard fail。上升值、配置不一致、CPU set/mode/EMC/fan 状态变化为 environment-drift hard failure；gap、coverage、required-source read failure 按 run invalid 处理。EMC 不进入 1 Hz sequence；all-core profile 下 telemetry 固定 CPU0，记录 CPU0 overlap limitation。

Environment-drift hard-match fields 包括 kernel/L4T/package/config SHA、mode/CPU sets、frequency paths/targets、EMC、fan、thermal path/type sets、tegrastats/package、rail set、OC/UV paths/enables 和 wrapper SHA。Boot ID 变化使 resolved reference 失效，reboot 后必须重新 preflight、thermal reference 和 protocol。

J1.4 未执行 workload、benchmark、正式 T_idle_ref 或稳定性验证；MAXN_SUPER、locked clocks 和 fan state 保持不变。

### J1.4 Post-D042 closeout verification

- Stable local evidence manifest validation：全部记录 `OK`；manifest SHA256：`ed7acc2296dc1c76eb4e8231907570d17551e71b30cfbc7b56cb8113562870cb`。
- Component A 和 final supplemental stable copies 的 SHA256 与 D042 一致；证据目录无可写路径。
- Superseded supplemental attempts 保留、未修改、未删除，且不作为最终合同 authority。
- J1.4 closeout verification confirmed `J1.4 COMPLETE`、`J1 IN PROGRESS`、`J1.5 READY`。
- Closeout 未执行 workload/build/test/benchmark/J1.5，未改变 device state、system settings、wrapper 或 sudoers。

## 17. Stage J J1.5 Platform Evidence Gate

J1.5 状态：`COMPLETE`；J1 状态：`COMPLETE`；Stage J 状态：`IN PROGRESS`。

- Published Evidence logical root：`results/platform/jetson/environment/j1_baseline_v1/`。
- Published Evidence exact file set：README、platform acceptance、toolchain inventory、power/clock acceptance、telemetry contract、evidence provenance、`environment_snapshot.yaml` 和 `sha256sums.txt`。
- Published manifest SHA256：`6fb506bd47ce52bcc80c7f8067e4c9bf3547040af937aa273b413154c7d10d46`。
- Local preservation manifest SHA256：`ed7acc2296dc1c76eb4e8231907570d17551e71b30cfbc7b56cb8113562870cb`。
- Published Evidence：tracked、sanitized、derived；local raw evidence：external、untracked、immutable、not Published Evidence。
- Evidence total size：`14309` bytes；tracked limit `<=25 MiB`。
- YAML schema parse、manifest checksum、UTF-8/LF、deterministic ordering、privacy/redaction 和 cross-document consistency：`PASS`。
- Carried gaps：CMake missing；OpenCV metadata missing；yaml-cpp missing；ORT 1.23.2 pending J2；JetPack exact installed version not independently verified；Python `cv2` non-blocking。
- Device controlled state retained：MAXN_SUPER/ID 2、CPU online 0-5、CPU/GPU/EMC locked、PWM 255、nvfancontrol inactive；无 reboot/system/package change。
- J1.5 未执行 build/test/benchmark；J2 尚未开始。

## 18. Stage J J2.0 Build Interface Discovery

J2.0 状态：`COMPLETE`；J2.1：`READY_WITH_WARNINGS`。

### Read-only platform/toolchain facts

- OS：Ubuntu `22.04.5 LTS`；kernel `5.15.185-tegra`；architecture `aarch64`。
- GCC/G++：`11.4.0`；Make：`4.3`；Git：`2.34.1`；Python：`3.10.12`。
- CMake/CTest：missing；Ninja：missing；未安装或修复。
- `build-essential`：installed `12.9ubuntu3`；CMake APT candidate：`3.22.1-1ubuntu1.22.04.2`。
- NumPy `1.21.5`、PyYAML `5.4.1` 和 Python `google.protobuf` import 可用；Python `flatbuffers` import 不可用。
- `protoc`、`flatc`：not found；protobuf/flatbuffers development packages 未安装。
- OpenCV runtime/header 存在，pkg-config/CMake metadata 缺失；yaml-cpp header/runtime 缺失。
- Root NVMe filesystem：约 `197G` available、约 `11%` used；未创建 build directory。

### ORT 1.23.2 CPU-only build interface strategy

- Source acquisition：后续从官方 ONNX Runtime source repository 获取并固定 tag `v1.23.2`；J2.0 未下载 source。
- Target：native Jetson `aarch64`，Release shared library，CPUExecutionProvider/CPU-only。
- Candidate build interface：`build.sh --config Release --build_shared_lib --use_cpu --skip_tests --parallel <n>`；必要时通过 `--cmake_extra_defines CMAKE_INSTALL_PREFIX=<prefix>` 指定 install prefix。
- 禁止项：CUDA EP、TensorRT EP、GPU build、configure、build、CTest、benchmark、inference。
- Dependencies：CMake/CTest、GCC/G++/Make、Git、Python、NumPy/PyYAML，以及 build script 实际需要的 protobuf/flatbuffers tooling；J2.1 必须先依据真实 `build.sh --help` 验证参数和 dependency resolution。
- Suggested install prefix：仓库外的固定 staging prefix；J2.0 未创建或写入 prefix。
- Disk estimate：建议正式 build 前保留至少 `20 GiB` free；当前约 `197G` available。
- Time estimate：native Release build 预计几十分钟；未实测，不是 benchmark 或 performance result。

J2.0 未安装软件、未运行 configure/build/CTest、未下载 ONNX Runtime、未执行 benchmark/inference。J2.1 前必须解决或明确处理 CMake、protobuf/flatbuffers tooling 和构建依赖。

## 19. Stage J J2.1 Development Feasibility Probe

J2.1 状态：`COMPLETE`；J2.2：`READY_WITH_WARNINGS`；未开始 J2.2。

### Probe result

- Starting gate：branch `feature/jetson-onnxruntime`；HEAD `56d0c9ba7dfc50ff02fa9e481ae3a1026357df0c`；worktree clean；三个 frozen asset SHA 全部匹配。
- Platform：Ubuntu `22.04.5 LTS`、kernel `5.15.185-tegra`、native `aarch64`、glibc `2.35`。
- Toolchain：GCC/G++ `11.4.0`、Make `4.3`、Git `2.34.1`、Python `3.10.12`；`build-essential` installed；CMake/CTest、Ninja、`protoc` 和 `flatc` missing。
- Package candidates were inspected read-only; no package or Python package was installed. Candidates: CMake `3.22.1-1ubuntu1.22.04.2`、Ninja `1.10.1-1`、protobuf `3.12.4-1ubuntu7.22.04.6`、flatbuffers compiler `1.12.1~git20200711.33e2d80+dfsg1-0.6`、pip `22.0.2+dfsg-1ubuntu0.7`、venv `3.10.6-1~22.04.1`。
- Python：NumPy `1.21.5`、PyYAML `5.4.1`、`google.protobuf` import available；Python `flatbuffers` import unavailable。
- ORT source was cloned only into a repository-external temporary directory using tag `v1.23.2`; observed source HEAD `a83fc4d58cb48eb68890dd689f94f28288cf2278` and `VERSION_NUMBER=1.23.2`。`build.sh` only delegates to `tools/ci_build/build.py`；the parser source confirms the required interface flags. Neither script was invoked。

### Frozen J2.2 build strategy

- Source：official ONNX Runtime repository, tag `v1.23.2`。
- Target：native Jetson `aarch64`，Release shared library，CPUExecutionProvider；CPU-only is represented by omitting `--use_cuda`、`--use_tensorrt` and all other non-CPU EP flags。
- Candidate command：`build.sh --config Release --build_shared_lib --skip_tests --parallel 4 --cmake_extra_defines CMAKE_INSTALL_PREFIX=<external-staging-prefix>`。This is a plan only and was not executed。
- Parallelism：start conservatively at 4 jobs on the 6-CPU online set；adjust only under J2.2 observation if memory pressure requires it。
- Install prefix：repository-external staging prefix；none was created during this probe。
- Dependencies：CMake/CTest、GCC/G++/Make、Git、Python, NumPy/PyYAML, protobuf compiler/development files and flatbuffers compiler/Python module; exact dependency resolution remains a J2.2 pre-build check。
- Capacity estimate：retain at least `20 GiB` free; current NVMe filesystem has approximately `197G` available. Expected native Release build time is tens of minutes; not measured。

### Risks and limitations

- Existing JetPack CUDA/TensorRT libraries were not selected; CPU-only strategy must continue to omit their EP flags and CUDA definitions。
- Protobuf candidate/runtime compatibility and flatbuffers tooling remain unvalidated until dependencies are made available through an authorized installation step。
- GCC `11.4.0` and native aarch64 are plausible for this Ubuntu/L4T environment, but compiler compatibility is not proven until the later authorized build。
- No configure, build, test, benchmark, inference, TensorRT, CUDA EP or GPU build was executed。

## 20. Stage J J2.2 ONNX Runtime CPU-only Build

J2.2 状态：`COMPLETE`；J3：`READY`；未开始 J3。

### Build and dependency record

- Starting gate：branch `feature/jetson-onnxruntime`；HEAD `7a41a91c5d45150f55aa866b5c0fd35a24018536`；worktree clean。
- User-installed package versions：CMake `3.22.1-1ubuntu1.22.04.2`、Ninja `1.10.1-1`、protobuf compiler/development `3.12.4-1ubuntu7.22.04.6`、flatbuffers compiler/development/Python module `1.12.1~git20200711.33e2d80+dfsg1-0.6`。
- ORT source：tag `v1.23.2`；source HEAD `a83fc4d58cb48eb68890dd689f94f28288cf2278`。
- System CMake 3.22.1 was insufficient for ORT v1.23.2. Official CMake `3.28.6` aarch64 binary was placed only in external staging and used through `--cmake_path`; system CMake and `/usr/local` were not changed. Archive SHA256：`7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7`。
- Build command：`build.sh --build_dir <external>/ort-build --cmake_path <external>/cmake-3.28/bin/cmake --config Release --build_shared_lib --skip_tests --parallel 4 --update --build`。
- Build interval：`2026-07-22T23:49:15+08:00` to `2026-07-23T00:47:22+08:00`；elapsed `3487 s`；exit code `0`。
- Resource snapshot：CPU online `0-5`；memory `1.5Gi/7.4Gi` used before and `1.3Gi/7.4Gi` after；disk approximately `196G` available before and `195G` after。

### CPU-only artifact and SDK record

- External SDK staging：`historical_external_ort_sdk`；owner/group `orin/orin`；mode `775`；size approximately `51M`。
- SDK contains `include/`、`lib/` and `lib/cmake/onnxruntime/`；headers include `onnxruntime_c_api.h` and `onnxruntime_cxx_api.h`。
- `lib/libonnxruntime.so.1.23.2`：ARM aarch64 ELF shared object；SHA256 `bd6193ae6028a9e1a16e2cc567e14bd9ea61760686c2d9d3c07df5524a7e362a`。
- `lib/libonnxruntime_providers_shared.so`：ARM aarch64 ELF shared object；SHA256 `2558ceb1670e58d0e6103c2b528af7b7802f850b2145b9f10d71d8283f525a21`。
- SDK manifest `sha256sums.txt` SHA256：`e49aff468656baa91521dbcb3ec10564db7515be25f6643552d2dc9955921d9a`。
- CMake cache verification：`CMAKE_BUILD_TYPE=Release`、shared library `ON`；CUDA/CUDA interface/TensorRT/TensorRT interface `OFF`；no CUDA or TensorRT runtime dependency in `libonnxruntime.so.1.23.2`。
- System tests, benchmark, inference and J3 were not executed. The first CMake 3.22 attempt stopped at the minimum-version check before compilation; it was retained as external failure evidence only。

## 21. Stage J J2.2 Formal Clean Build Remediation v2

- D044：`Accepted`；historical development build：`SUPERSEDED` as formal Evidence authority；`j2.2_formal_clean_v1`：`BLOCKED` and retained immutable。
- Formal attempt `j2.2_formal_clean_v2`：`PASS`；ORT source tag/commit：`v1.23.2` / `a83fc4d58cb48eb68890dd689f94f28288cf2278`。
- Build：native AArch64、Release、shared library、CPU-only，external CMake `3.28.6`，parallel `4`，elapsed `3883 s`，formal build exit `0`；independent install exit `0`。
- SDK validation：public headers、`libonnxruntime.so` symlink chain、AArch64 ELF64、SONAME、NEEDED、ldd、CMake package relocatability 均 `PASS`；主库 SHA256：`6eb17924b41234997354dd006b997ef079a10ddbe5fe082ae6373b6581b36740`。
- 未执行 SDK binary、CTest、inference、benchmark 或 RPATH smoke；未启用 CUDA/TensorRT/cuDNN；未修改系统 CMake、`/usr/local` 或生产源码。
- J2.2：`COMPLETE`；J2.3：`READY`；J2.4/J2.5：`PENDING`；J2 overall：`IN PROGRESS`；J3：`BLOCKED_BY_J2.5`。
- Next authorized task：`J2.3 — SDK packaging and manifest`；J2.3 尚未执行。

### Stage J J2.3 SDK packaging and manifest

- J2.3：`COMPLETE`；只使用 formal v2 SDK，未使用 historical development SDK、v1 SDK 或新的 ORT 构建产物。
- Local SDK logical path：`third_party/onnxruntime/1.23.2/linux-aarch64/`；`include/` 和 `lib/` 为 local-only payload，保留真实 symlink，不进入 Git。
- ORT：`1.23.2` / `v1.23.2` / `a83fc4d58cb48eb68890dd689f94f28288cf2278`；formal attempt：`j2.2_formal_clean_v2`；attempt manifest SHA256：`a4028cbca5ced9abbd95d1aedaa5f83b55ee062820700fb44fbd6e479f2d2b32`。
- Canonical source aggregate SHA256：`c060f538ac72eb5d801781ac1c5fb6c1a12001ce57f873a952ea37aebce3f81c`；main library SHA256：`6eb17924b41234997354dd006b997ef079a10ddbe5fe082ae6373b6581b36740`。
- Metadata SHA256：`BUILD_MANIFEST.json` `94c5430c879715e3e8015cef5143b69d115c55dfcfc3221bf0c16fb5cfe21406`；`HEADER_SHA256SUMS.txt` `3aace362a8a6d65f9852e501df69d4b33720e51f5017c4e7d25d21d33ffe9029`；`FILE_SHA256SUMS.txt` `8fb13ae5f579a4c148725ed5e1ce96ba1fe25c6d0024ec377517fdf8c5d99f02`。
- Official source license SHA256：`2f07c72751aed99790b8a4869cf2311df85a860b22ded05fa22803587a48922c`；third-party notice SHA256：`e9e90971a8e75a9a8ac0c6412e29c1202d079998389915aa485f46c816c3b4cc`。
- Published Evidence：`j2_sdk_v1`；Evidence manifest 4/4 PASS；无 payload、`.so`、完整 headers 或绝对私有路径。
- J2.4 runtime/RPATH smoke：`PENDING`；J2.5 Evidence gate：`PENDING`；J2 overall：`IN PROGRESS`；J3：`BLOCKED_BY_J2.5`。
- 未执行 binary/runtime smoke、inference、benchmark、CTest、J2.4、J2.5 或 J3。Next authorized task：`J2.4 — RPATH smoke`。

### Stage J J2.4 RPATH smoke

- J2.4：`COMPLETE`；使用 formal Stage J aarch64 SDK 完成仓库外最小 consumer configure/build 和基本 ORT runtime smoke。
- Smoke binary SHA256：`d08391424b42d0720293cc9b5a07431d33f8b2763296e25912d03e1951a20d40`；SDK main library SHA256：`6eb17924b41234997354dd006b997ef079a10ddbe5fe082ae6373b6581b36740`。
- `RUNPATH` 解析到 logical path：`third_party/onnxruntime/1.23.2/linux-aarch64/lib`；清除 `LD_LIBRARY_PATH` 后精确解析到 Stage J SDK，resolved library SHA PASS。
- Runtime：ORT `1.23.2`、`CPUExecutionProvider`、`Ort::Env` 和 `Ort::SessionOptions` 均 PASS；未加载模型，未执行 inference、CTest 或 benchmark。
- Local attempt：`j2.4_rpath_smoke_v1`；manifest SHA256：`3cb3bc88814340bed450b037236e3d03eaaf06aee37674e5e8a4075b419dad03`。Published Evidence：`j2_rpath_smoke_v1`。
- J2.5：`READY`；J2 overall：`IN PROGRESS`；J3：`BLOCKED_BY_J2.5`；J3.0：`NOT_DEFINED`。
- Next authorized task：`J2.5 — J2 Evidence gate`；J2.5 未执行。
