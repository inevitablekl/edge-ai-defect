# M5 Level C Validation and WSL2 ORT CPU Engineering Baseline Execution Plan

Stage：**M5 Level C Validation and WSL2 ORT CPU Engineering Baseline**

正式名称：**M5 Level C Validation and WSL2 x86_64 ONNX Runtime CPU Engineering Baseline**

| 状态项 | 当前状态 |
| --- | --- |
| M5 overall | `IN_PROGRESS` |
| Current task | M5.1 Corpus Assets and Validation Contract |
| M4 prerequisite | `CLOSED` |
| M5.0 Planning Freeze | `COMPLETE` |
| M5.1 Corpus Assets and Validation Contract | `COMPLETE` |
| M5.2 Level C Reference, Comparator and Formal Validation | `PENDING` |
| M5.2 Level C Gate | `PENDING` |
| M5.3 Benchmark Harness and Offline Analyzer | `PENDING` |
| M5.4 Formal WSL2 ORT CPU Baseline Execution | `PENDING` |
| M5.5 Evidence Consolidation | `PENDING` |
| M5.6 Deep Evidence Gate | `PENDING` |
| M5.7 Documentation-Only Closeout | `PENDING` |
| M5 final | 尚未 `CLOSED` |

M5.0 只冻结计划，不实现 M5.1，不导入图片，不生成正式 Level C/benchmark evidence，也不运行 benchmark。

## 1. 事实权威与 M5.0 起点

### 1.1 事实权威顺序

发生冲突时按以下顺序处理：

1. 当前 HEAD 的 production 源码和测试；
2. 已冻结的 M1～M4 合同与 Gate 结果；
3. 本文件；
4. `docs/personal/EXPERIMENT_PLAN.md`；
5. `docs/personal/DECISIONS.md`；
6. 历史对话和 Discovery 报告。

不得根据历史对话跳过任务卡，或用 Discovery 临时结果替代正式 evidence。

### 1.2 起点 Git 事实

2026-07-19 经人工确认，以 Discovery 状态固化提交作为 M5.0 起点：

- branch：`feature/cpp-onnxruntime`；
- HEAD：`86fd46d16e8d579613001e7c99df19b9e59a2249`；
- HEAD subject：`docs: record M5 pre-planning discovery audit`；
- worktree：clean；
- upstream：behind `0`、ahead `13`；
- M4：`CLOSED`；
- M5：planning `PENDING`，production implementation 尚未开始。

原任务文本中的 `99447c5...` / ahead 12 是 M5 Discovery 前的历史起点；本节经人工确认取代该预检值，
不改变其余 M5.0 冻结要求。

## 2. M5 总目标与证明边界

### 2.1 总目标

M5 必须：

1. 建立同一冻结 ONNX 上的 Python ONNX Runtime 显式 Reference；
2. 建立 Python ORT 与真实 C++ `edge_ai_defect` application 的 Level C 端到端一致性验证；
3. 建立可移植 corpus 选择、导入、SHA 校验和派生图生成流程；
4. 建立确定性最大二分匹配 Comparator；
5. 验证 Python 和 C++ 各自两次输出 byte-identical；
6. 建立完整 Level C evidence 和 provenance；
7. 仅在 Level C Gate PASS 固化后建立正式 benchmark harness；
8. 在 WSL2 x86_64 上生成 ONNX Runtime CPU Engineering Baseline；
9. 保存每帧原始 timing、每 run 统计、跨 run 汇总和环境快照；
10. 执行 Deep Evidence Gate；
11. documentation-only closeout，并为后续 Jetson/TensorRT 阶段提供可复用工具。

### 2.2 明确非目标

M5 不包含：

- 重新比较 PyTorch 与 C++，或重新评估 mAP/Recall；
- 使用 PyTorch、Ultralytics `model.predict()`、隐藏 LetterBox/NMS/scale_boxes 作为 Level C oracle；
- 重新训练、重新导出 ONNX 或改变冻结模型；
- 修改 RuntimeConfig schema，新增 `--benchmark` 或 YAML/CLI override；
- 新增 C++ Profiler 类，修改 `SerialRunner`、`FrameTimings` 或 JsonSink schema；
- 搜索 ORT 线程参数，新增 `-march=native`/LTO；
- TensorRT、CUDA、Jetson 性能、Pipeline、多线程、ROS2、Qt、Camera、RTSP；
- 320/416/640 输入尺寸对比、长时间 soak test；
- 最终部署硬件性能或论文 TensorRT 性能结论。

M5 结果不得称为 Jetson baseline、TensorRT baseline、同硬件加速比或最终实时性能结论。WSL ORT 与未来
Jetson TensorRT 数字不得直接计算 speedup。

## 3. 冻结模型、合同和环境

### 3.1 模型与 ModelContract

| 项目 | 冻结值 |
| --- | --- |
| ONNX | `models/onnx/yolov8n_neudet_frozen.onnx` |
| ONNX SHA256 | `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944` |
| ModelContract | `configs/model_contracts/yolov8n_neudet_frozen.yaml` |
| Contract SHA256 | `9dd74f8420d8326fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190` |
| Input | `images`, float32 NCHW `[1,3,640,640]` |
| Output | `output0`, float32 BCN `[1,10,8400]` |

类别顺序固定为：

| ID | Class |
| ---: | --- |
| 0 | `crazing` |
| 1 | `inclusion` |
| 2 | `patches` |
| 3 | `pitted_surface` |
| 4 | `rolled-in_scale` |
| 5 | `scratches` |

### 3.2 Python 与 C++ 环境

| 环境 | 冻结/当前值 |
| --- | --- |
| Python executable | `.venv/bin/python` |
| Python | 3.10.12 |
| Python ONNX Runtime | 1.23.2 |
| Python OpenCV | 4.10.0 |
| NumPy | 1.26.4 |
| PyYAML | 6.0.2 |
| SciPy | 1.15.3 |
| NetworkX | 3.4.2 |
| psutil | 7.2.2 |
| pandas | 不需要 |
| GCC | 11.4.0 |
| CMake | 3.22.1 |
| glibc | 2.35 |
| C++ OpenCV | 4.5.4 |
| C++ ONNX Runtime | 1.23.2 |

Python OpenCV 4.10.0 与 C++ OpenCV 4.5.4 的差异必须进入 provenance；该已知差异本身不构成 blocker。

### 3.3 ORT SessionOptions

Python Reference 与 C++ baseline 都必须记录并采用：

- CPU Execution Provider；
- `ORT_SEQUENTIAL`；
- `ORT_ENABLE_ALL`；
- intra-op threads = 1；
- inter-op threads = 1；
- CPU arena enabled。

M5 不搜索或改变这些参数。

## 4. 已有基础与 Reference 选择

### 4.1 可复用等级

现有 Python 脚本复用等级固定为 **Reusable with M5 harness changes**：

- `generate_preprocess_level_a.py`：显式 resize/padding、BGR→RGB、HWC→CHW、float32/255 的分层参考；
- `generate_onnx_runtime_engine_level_b_golden.py`：同一冻结 ONNX 的显式 Python ORT raw-output 参考；
- `postprocessor_reference.py`：BCN decode、strict threshold、class-aware NMS、坐标恢复、`candidate_index` 参考；
- `compare_pt_onnx.py`：仅为历史 PT/ORT consistency evidence，不是 Level C Reference。

M5 优先新建独立 wrapper，不修改既有 M1/M2/M3 golden generator 的历史语义。

### 4.2 D034：Level C Reference 语义

Level C Reference 是同一冻结 ONNX 上的 Python ONNX Runtime 显式 pipeline。它必须：

1. 读取同一 ModelContract 和 RuntimeConfig；
2. 按 M4 DirectorySource 的第一层 regular file、扩展名和 relative generic path byte-order 规则排序；
3. 使用 `cv2.imread(..., cv2.IMREAD_COLOR)`；
4. 显式执行 LetterBox、BGR→RGB、HWC→CHW、float32/255；
5. 使用配置一致的 `onnxruntime.InferenceSession`；
6. 显式解析 BCN，执行 `confidence > threshold`、class-aware `IoU > threshold` NMS 和坐标逆变换；
7. 保留 raw BCN 的零基 `candidate_index`；
8. 生成字段顺序稳定、UTF-8 LF、无时间戳的 Reference JSON。

禁止使用 PyTorch、Ultralytics high-level/hidden pipeline 或 `compare_pt_onnx.py` 的 greedy matching 作为 oracle。

## 5. 数据合规和 portable corpus 策略

### 5.1 D039：资产边界

在未确认明确再分发许可时：

- 不将 NEU-DET 原始 JPG 或基于其生成的派生图片提交 Git；
- Git 只跟踪选择 manifest、文件名、split、expected SHA256、GT 类别、选择理由、导入/校验工具和派生规则；
- 工具通过显式 `--dataset-root <path>` 接收用户合法持有的数据根；
- 不使用本机硬编码绝对路径，不自动联网下载，不隐式访问第三方镜像；
- 文件缺失、不是 regular file、split 不符或 SHA 不符均 fail-fast；
- 正式 provenance 记录数据来源说明和 SHA，但不包含图片内容，也不得虚构开放再分发许可。

M5.1 未来冻结的 manifest 路径为：

- `tests/data/m5/manifests/level_c_original_corpus.json`；
- `tests/data/m5/manifests/level_c_derived_corpus.json`；
- `tests/data/m5/manifests/benchmark_corpus.json`。

这些路径只保存文字/哈希元数据，不能包含图片。M5.1 的 corpus preparation 工具放在
`tools/validation/`，实际 prepared corpus 只能位于调用者指定的仓库外或 build 临时目录。

## 6. Level C corpus：12 张原图 + 4 张派生图

### 6.1 冻结 12 张 validation 原图

表中顺序是正式逻辑顺序。M5.1 必须重新验证文件 SHA 和 frozen validation split；任一不符即停止人工审查，
不得自动替换。

| # | Filename | SHA256 | Role |
| ---: | --- | --- | --- |
| 0 | `crazing_51.jpg` | `185daa31428cf2467d48f9f57ff582575d07a796cd26d77f3e05537bae681503` | zero Detection |
| 1 | `crazing_10.jpg` | `522352a6c3532d45a64184b7b1435a74e8cdb732ebdc8e062ced67fa737cf63c` | near-threshold, multi-Detection |
| 2 | `inclusion_18.jpg` | `c1c54814ecaf2bf4f6d84aaf5c744fb648dc3c8323c3b0cfe1bd9f55df20788b` | near-threshold, dense multi-Detection |
| 3 | `inclusion_217.jpg` | `e40821c51a341286572663cbba1159e7efe8a7cd729c763a5c439d851e6a9c77` | near-threshold |
| 4 | `patches_156.jpg` | `9961f0ffde85a40516f54262b3fa74eb35cee24fc87a54d4fe8f07b7e7fb2ec2` | near-threshold, multi-Detection |
| 5 | `patches_211.jpg` | `f988631bac3b31eac7be7a1f56e118d14d3327989ce4b454370761c5c8700305` | multi-class, multi-Detection |
| 6 | `pitted_surface_224.jpg` | `419e1d0d40ce7c53fcce40b55f4b8091d4573881d2315969d74318df493a0e80` | near-threshold |
| 7 | `pitted_surface_231.jpg` | `0bfa310238545597ac7a48495a85ae1a945d2f6f8e4fa470d1bce5f4648c931c` | multi-Detection |
| 8 | `rolled-in_scale_146.jpg` | `4b76ee7c33602b95115a2acec07b4cd74cab87eeb2cdc2a602534646cbed047b` | near-threshold, multi-Detection |
| 9 | `rolled-in_scale_262.jpg` | `67cab4d93752e5def8a7d34b72504c1ecacadc673f252d4d719b716aeda0c083` | near-threshold, single Detection |
| 10 | `scratches_126.jpg` | `fd1f86fe4349e991e98e1b00c1b1aa94088669822cdb30a5c0dfffa5782134c3` | near-threshold, multi-Detection |
| 11 | `scratches_246.jpg` | `06811a835826c47ad78e91e90cb758f6334f348d21765375b2ce9146be1309b4` | multi-Detection |

覆盖要求：六类全部覆盖、每类至少两张、至少三张 multi-Detection、至少两张 near-threshold、至少一张真实
zero-Detection。**不要求第二张 zero-Detection**，也不得为凑数跨 split 选择。

prepared 目录中使用 `0000_`～`0011_` 数字前缀和 regular-file copy，强制 DirectorySource 字节序；不得 symlink。

### 6.2 冻结四张非方形派生 BMP

派生图在 M5.1 运行时生成，不进入 Git。统一使用 Python OpenCV 4.10.0、`IMREAD_COLOR`、
`cv2.resize(..., INTER_LINEAR)`、`cv2.copyMakeBorder`、BGR `[114,114,114]`，保持宽高比，不拉伸。

| # | Source | Target W×H | Resized W×H | Padding T/B/L/R | Output name |
| ---: | --- | --- | --- | --- | --- |
| 12 | `crazing_10.jpg` | 319×201 | 201×201 | 0/0/59/59 | `derived_319x201_crazing_10.bmp` |
| 13 | `inclusion_18.jpg` | 201×319 | 201×201 | 59/59/0/0 | `derived_201x319_inclusion_18.bmp` |
| 14 | `pitted_surface_224.jpg` | 321×199 | 199×199 | 0/0/61/61 | `derived_321x199_pitted_surface_224.bmp` |
| 15 | `scratches_126.jpg` | 199×321 | 199×199 | 61/61/0/0 | `derived_199x321_scratches_126.bmp` |

M5.1 必须记录 source SHA、target/resized dimensions、padding、OpenCV version、output SHA，并重复生成证明
byte-identical。prepared 名称使用 `0012_`～`0015_` 前缀；四张均为 24-bit BMP regular files。

## 7. Level C RuntimeConfig 和 Reference schema

### 7.1 运行配置

Level C 使用 M4 schema version 1，不扩展 schema：

- `backend.type=onnxruntime_cpu`；
- `timing.enabled=false`；
- `output.console=false`；
- `output.overwrite=true`；
- `confidence_threshold=0.25`；
- `iou_threshold=0.45`；
- `max_nms=30000`；
- `max_det=300`；
- `max_wh=7680.0`；
- `agnostic=false`；
- `multi_label=false`。

“`classes=null`”只表示不做类别过滤。当前 strict RuntimeConfig 没有 `classes` 字段，因此 runtime YAML **不得**
写入该 unknown field；Python Reference 读取同一配置并处理全部六类。不得为比较方便修改 threshold。

### 7.2 Reference JSON

Python Reference 可使用独立 schema，但必须稳定包含：

- schema version、backend、model SHA、contract filename、class names、postprocess config；
- ordered images 的 `sequence_index`、`relative_path`、`width`、`height`；
- Detection 的 xyxy、confidence、class_id、candidate_index；
- processed image 和 total detection summary。

它不包含 timing、timestamp、hostname、username 或个人绝对路径。Comparator 严格验证两侧 schema，缺失或未知字段失败。

## 8. D035：最大二分匹配、容差和确定性

### 8.1 跨语言匹配

每张图片先要求 relative path、width/height、Detection 总数和每类数量完全一致，再按 `class_id` 分组建立二分图。
Python/C++ Detection 之间存在兼容边，当且仅当：

```text
abs(conf_python - conf_cpp) <= 1e-4

max(abs(x1_python - x1_cpp),
    abs(y1_python - y1_cpp),
    abs(x2_python - x2_cpp),
    abs(y2_python - y2_cpp)) <= 0.01 pixel
```

每类必须用确定性的最大二分匹配找到完整一对一 matching。禁止下标逐项、排序逐项、IoU 最近、候选边 greedy
或人工配对。Comparator 测试必须包含“greedy 失败但 maximum matching 成功”的明确反例。

`candidate_index` 进入报告并用于诊断，但不是跨语言 PASS 的必要条件，也不改变兼容边；Detection 跨语言顺序不是
PASS 条件，但每一侧自身两次输出必须稳定。

### 8.2 Level C 验收

正式顺序：Python Run 1、Python Run 2、C++ Run 1、C++ Run 2，然后跨语言语义比较。

必须满足：

- Python 两次 byte-identical；C++ 两次 byte-identical；
- 16/16 图片全部 PASS，不使用通过率；
- image 数、relative path、width/height、class 名称和顺序完全一致；
- Detection 总数、每类数量和 summary 完全一致；
- 每个匹配的 confidence/bbox 满足冻结容差；
- 任一 non-finite、schema missing/unknown、未完整 matching 立即失败。

不得用平均误差替代逐项 PASS、忽略失败图片或自动扩大容差。容差变化必须停止、报告误差分布、分析根因、取得人工
决策，并使旧 evidence 失效。

## 9. Benchmark 20 张原图 corpus

Benchmark 只使用 frozen validation split 原图，不使用派生图。前 12 张与 Level C 原图相同：

| # | Filename | SHA256 |
| ---: | --- | --- |
| 0 | `crazing_51.jpg` | `185daa31428cf2467d48f9f57ff582575d07a796cd26d77f3e05537bae681503` |
| 1 | `crazing_10.jpg` | `522352a6c3532d45a64184b7b1435a74e8cdb732ebdc8e062ced67fa737cf63c` |
| 2 | `inclusion_18.jpg` | `c1c54814ecaf2bf4f6d84aaf5c744fb648dc3c8323c3b0cfe1bd9f55df20788b` |
| 3 | `inclusion_217.jpg` | `e40821c51a341286572663cbba1159e7efe8a7cd729c763a5c439d851e6a9c77` |
| 4 | `patches_156.jpg` | `9961f0ffde85a40516f54262b3fa74eb35cee24fc87a54d4fe8f07b7e7fb2ec2` |
| 5 | `patches_211.jpg` | `f988631bac3b31eac7be7a1f56e118d14d3327989ce4b454370761c5c8700305` |
| 6 | `pitted_surface_224.jpg` | `419e1d0d40ce7c53fcce40b55f4b8091d4573881d2315969d74318df493a0e80` |
| 7 | `pitted_surface_231.jpg` | `0bfa310238545597ac7a48495a85ae1a945d2f6f8e4fa470d1bce5f4648c931c` |
| 8 | `rolled-in_scale_146.jpg` | `4b76ee7c33602b95115a2acec07b4cd74cab87eeb2cdc2a602534646cbed047b` |
| 9 | `rolled-in_scale_262.jpg` | `67cab4d93752e5def8a7d34b72504c1ecacadc673f252d4d719b716aeda0c083` |
| 10 | `scratches_126.jpg` | `fd1f86fe4349e991e98e1b00c1b1aa94088669822cdb30a5c0dfffa5782134c3` |
| 11 | `scratches_246.jpg` | `06811a835826c47ad78e91e90cb758f6334f348d21765375b2ce9146be1309b4` |
| 12 | `crazing_102.jpg` | `b4e276eb131f61b44084d0c06640b00cbaecbffb48d3a8f3120d7aaa5cc84a53` |
| 13 | `inclusion_135.jpg` | `96a0fd79d5c8d6eab03b09e2331e258b931fd1b4523668b5b49f8ab69075ce67` |
| 14 | `patches_164.jpg` | `87c1b46a01c796c71030ee72ca51ae732fb2e4e8a39117e483e5b42fa55a9b8e` |
| 15 | `pitted_surface_225.jpg` | `23be66132f661ba432b06ba402734cbe12d05d5eca0bebed90b99d9f15cec92f` |
| 16 | `rolled-in_scale_133.jpg` | `f66ffd8a184bc11ec947078c3c206fac71b1118683deb5e8b3731811a0ae2ec3` |
| 17 | `scratches_154.jpg` | `3e96489cf25f15a08c3dcebbec97afabdfb58468847e51a70d880a35a104b72c` |
| 18 | `inclusion_16.jpg` | `1ff85f67c5d902bf00a37895e4ea86ca2a49bb1c452fa9fc44d0431f154a3940` |
| 19 | `scratches_221.jpg` | `e65d748792cd1010f663588aec6437acad9a26c92a30ea263b67febed363b27b` |

20 张必须全部 SHA/split 通过并覆盖六类每类至少三张。Prepared workload 使用 real regular-file copies，固定数字
前缀，不使用 symlink；manifest 记录每个重复文件到原始图片的映射。

## 10. D036：Benchmark 实现和运行协议

### 10.1 实现边界与构建

- 使用真实 Release `edge_ai_defect --config <runtime.yaml>`；
- 复用 M4 `FrameTimings` 和 JsonSink schema；
- 离线 Python orchestrator 负责 workload、进程、affinity、等待、解析、统计、压缩和 provenance；
- 不修改 production，不新增 Profiler、CLI flag、RuntimeConfig mode；
- RuntimeConfig 固定 `timing.enabled=true`、`console=false`、`overwrite=true`、`onnxruntime_cpu`；
- build 固定 `CMAKE_BUILD_TYPE=Release`、`EDGE_AI_ENABLE_MODEL_SMOKE=ON`；不使用 Debug、ASan、UBSan、coverage，
  不额外开启 `-march=native` 或 LTO。

### 10.2 Pilot 和正式帧数

Pilot：100 帧，丢弃前 20 帧，不进入正式统计。以余下 80 帧的 `pre_sink_total_ms` mean 计算：

```text
target_measured_frames = max(500, ceil(33000 / pilot_mean_ms))
total_frames = 20 * ceil((50 + target_measured_frames) / 20)
actual_measured_frames = total_frames - 50
```

33,000 ms 提供约 10% 余量；`total_frames` 是 20 张 corpus 的整数周期。每个正式 run 必须实际验证
`actual_measured_frames >= 500` 且 measured `pre_sink_total_ms` sum >= 30,000 ms。任一不满足则整个 run 无效，
调整 N 后重新执行全部五个正式 run，不得在同一 evidence 中局部补帧。

### 10.3 独立进程和系统条件

- 五个独立进程，每次重新初始化 ORT Session，输入顺序相同；
- run 之间等待 30 秒，最后一个 run 后不等待；
- 绑定当前允许 CPU 集合中最低编号逻辑 CPU，并记录实际 affinity；
- 不 drop caches、不要求 root，结果标记为 warm-cache；
- 记录 WSL 无法冻结主机 governor、电源策略和频率的限制；
- 记录进程 wall-clock throughput，仅作为辅助指标。

## 11. Timing 和统计协议

### 11.1 样本定义

正式样本字段：`source_ms`、`preprocess_ms`、`inference_ms`、`postprocess_ms`、`pre_sink_total_ms`。

- `inference_ms` 是 backend latency，继承 M2 `IInferenceEngine::run()`，包含 backend execution 和 output copy；
- `pre_sink_total_ms` 包含 source+preprocess+inference+postprocess，不包含 sink、JSON 最终序列化、Console、Session 初始化或进程启动；
- `pre_sink_fps = measured_frames * 1000 / sum(pre_sink_total_ms)`；
- `backend_fps_equivalent = measured_frames * 1000 / sum(inference_ms)`，必须保留 `equivalent`，不能称完整应用 FPS。

### 11.2 每 run 统计

对每个 timing 字段报告 sample_count、mean、minimum、maximum、P50、P95、P99、sample standard deviation。
sample standard deviation 使用 `n-1`。百分位固定 Hyndman–Fan Type 7：排序后 `h=(n-1)*p`，相邻样本线性插值。
不得依赖库的未声明默认实现。

除前 50 帧 warmup 外，不删除、不裁剪、不 Winsorize，不以 IQR 或标准差剔除任何 measured outlier；异常值保留并说明。

### 11.3 跨 run 汇总

保留五个 run 各自统计，并分别汇总：

- 五个 run mean 的 median/minimum/maximum；
- 五个 run P95 的 median/minimum/maximum；
- 五个 run `pre_sink_fps` 的 median/minimum/maximum；
- 五个 run `backend_fps_equivalent` 的 median/minimum/maximum。

pooled percentile 可以输出，但只能是辅助指标。

## 12. D038：Evidence、Retention、Provenance 和失效

### 12.1 Evidence ID 与生成前提

Evidence ID 固定为 `YYYYMMDD_<short_source_git_commit>`。`source_git_commit` 是已提交 harness/protocol 的 clean
HEAD；正式 evidence 在该 clean HEAD 生成后再独立提交，因此不形成 self-reference。

每个 source commit 只保留一个正式有效 Level C evidence 和一个正式有效 ORT CPU baseline evidence。Discovery、失败和
预运行结果不得进入正式 results。所有正式 evidence 必须由 clean committed HEAD 生成。

### 12.2 Level C evidence

目录：`results/validation/level_c/<evidence_id>/`，至少包含：

- `corpus_manifest.json`、`derived_manifest.json`、`runtime_config.yaml`；
- `python_reference_run_1.json`、`python_reference_run_2.json`；
- `cpp_run_1.json`、`cpp_run_2.json`；
- `comparison_report.json`、`provenance.json`、`commands.txt`、`README.txt`。

Level C JSON 保留未压缩原始文件。

### 12.3 Benchmark evidence

目录：`results/benchmark/ort_cpu/<evidence_id>/`，至少包含：

- `benchmark_corpus_manifest.json`、`benchmark_protocol.json`；
- `environment.json`、`provenance.json`、`commands.txt`、`aggregate_summary.json`；
- `run_01/`～`run_05/`，每个含 `raw_application.json.gz`、`timings.tsv`、`summary.json`、
  `command.txt`、`exit_code.txt`。

运行时先生成 raw JSON 并记录 SHA256，再以 compression level 9、mtime=0 且不嵌入原始文件名的 deterministic gzip
压缩并记录 SHA256；正式 evidence
不保留未压缩副本。`timings.tsv`/summary 必须引用并可追溯到未压缩 SHA。使用 TSV，避免全局 `*.csv` ignore。

单个正式 evidence set 的 Git tracked 总量上限为 25 MiB；超过时停止，不能自行删减原始证据，必须人工 retention 决策。

### 12.4 Provenance 必填字段

正式 provenance 至少包含：

- evidence schema version、Git commit/branch/worktree clean；
- binary、Reference、Comparator、corpus tool、benchmark orchestrator、statistics analyzer SHA256；
- model、ModelContract、RuntimeConfig、corpus manifest、每张 source/derived image SHA256；
- Python executable/version、Python ORT/OpenCV/NumPy/PyYAML；
- C++ ORT/OpenCV、GCC、CMake、glibc、Release build type 和 compile flags；
- CPU model、visible logical CPUs、actual affinity、WSL kernel、memory；
- ORT SessionOptions；
- warmup、pilot、formal total/measured frames、measured duration、run count、inter-run wait；
- 实际命令、exit codes、raw/compressed evidence SHA256。

hostname、username 和个人绝对路径不能作为 evidence 标识。

### 12.5 失效规则

以下变化使 Level C evidence 失效：ONNX、ModelContract、RuntimeConfig、corpus manifest/任一图片 SHA、Python Reference、
Comparator、C++ production、ORT/OpenCV version、tolerance 或 matching 算法变化。

以下变化还使 benchmark evidence 失效：Release flags、FrameTimings 语义、benchmark corpus、pilot、warmup、measured
帧数/时长规则、run count、inter-run wait、affinity、percentile、outlier 或 retention 规则变化。

仅 documentation-only 且不影响上述事实的修改不强制重跑。

## 13. 阶段状态机和 Gate 规则

```text
M5.0 Planning Freeze
  → M5.1 Corpus Assets and Validation Contract
  → M5.2 Level C Reference, Comparator and Formal Validation
  → read-only M5.2 Level C Gate
  → docs-only Gate PASS 状态固化提交
  → M5.3 Benchmark Harness and Offline Analyzer
  → M5.4 Formal WSL2 ORT CPU Baseline Execution
  → M5.5 Evidence Consolidation
  → read-only M5.6 Deep Evidence Gate
  → M5.7 Documentation-Only Closeout
  → M5 CLOSED
```

规则：Level C Gate PASS 固化前不得执行正式 benchmark；所有只读 Gate 结果进入下一阶段前必须固化；Gate FAIL 后只允许
针对性 remediation；Gate 本身不得修改仓库；M5.6 PASS 可由 M5.7 一次性固化并关闭 M5。

## 14. M5.0～M5.7 独立任务卡

每次只执行一张卡，完成后停止；不得自动进入下一阶段。

### M5.0 — Planning Freeze

- **objective**：冻结本文件、M5 长期决策、实验协议、任务卡和 Gate；不实现代码。
- **starting facts**：M4 CLOSED；Discovery complete；第 1.2 节 Git 起点成立。
- **allowed changes**：本文件、TASKS、EXPERIMENT_PLAN、DECISIONS；项目稳定文档仅在明确漂移时最小同步。
- **forbidden scope**：production/tests/tools/CMake/config/model/data/results、Level C、benchmark、M5.1、push。
- **required verification**：docs-only diff、状态/协议一致性、`git diff --check`/cached check。
- **acceptance**：本文件完整；D034～D039、EXPERIMENT_PLAN 和 TASKS 同步；M5 IN_PROGRESS、M5.1 PENDING。
- **commit**：`docs: freeze M5 Level C and ORT baseline plan`。
- **next**：仅 M5.1。

### M5.1 — Corpus Assets and Validation Contract

- **objective**：建立三份 manifest、本地导入/SHA 工具、确定性 derived BMP 和正式工具测试；验证 12+4 与 20 corpus 准备。
- **allowed future scope**：`tools/validation/` corpus tool、上述 manifests、M5 Python tests、最小 CMake/CTest 接入和状态文档。
- **forbidden**：提交图片、Python ORT Reference、C++ production、正式 Level C evidence、benchmark。
- **required tests**：dataset-root/文件缺失、SHA 错、duplicate、非 val split、顺序/数字前缀、regular copy/no symlink、
  derived dimensions/padding/output SHA/重复 byte-identical、rerun deterministic、temp cleanup、source 不变。
- **acceptance**：12 originals、4 derived、20 benchmark originals 全部验证；六类覆盖；manifest SHA；source tree 无图片；
  OFF/ON 回归通过；状态真实。
- **commit**：`feat: add M5 corpus preparation and manifests`。
- **next**：仅 M5.2 harness；不得运行正式 Level C。

### M5.2 — Level C Reference, Comparator and Formal Validation

分两个提交边界：

1. **Harness**：实现 explicit Python ORT Reference、stable schema、DirectorySource-equivalent sorting、candidate_index、
   maximum matching Comparator、self determinism、cross-language comparison、provenance 和机器可读失败分类。
2. **Evidence**：Harness 已提交且 worktree clean；新 Release build，OFF/ON CTest 和 corpus SHA PASS；Python/C++ 各两次，
   自身 byte-identical，16/16 comparison，生成正式 evidence。

Harness 必测：LetterBox、BGR/RGB、NCHW、BCN decode、`confidence > 0.25`、`IoU > 0.45` suppression、class-aware
NMS、coordinate restore、candidate_index、empty/multi/near-threshold/non-finite、schema missing/unknown、greedy 反例、
no complete matching、duplicate edges、deterministic matching、tolerance boundary、Python byte determinism。

- **commits**：`feat: add M5 Level C validation harness`；`test: add M5 Level C validation evidence`。
- **next**：只读 Level C Gate；不得 benchmark。

### M5.2 Level C Gate — Read-only Standard Validation Gate

检查 Reference 无 PT/Ultralytics hidden pipeline；contract/config、corpus SHA/顺序、derived 规则、candidate_index、真实
maximum matching/greedy 反例、冻结 tolerance、两侧 self determinism、16/16、evidence/provenance、OFF/ON regression、
无 production 修改且未开始 benchmark。输出 PASS/FAIL，不修改仓库。

PASS 后必须 docs-only 提交 `docs: record M5 Level C gate pass`；固化前不得进入 M5.3。

### M5.3 — Benchmark Harness and Offline Analyzer

- **objective**：实现 20 图 regular-copy workload、pilot/N、5 processes、affinity、30s wait、FrameTimings parser、
  warmup filtering、30s/500 validation、Type 7、TSV、run/aggregate summary、deterministic gzip、environment/provenance。
- **forbidden**：C++ production 修改、正式 baseline、论文性能结论。
- **required tests**：N/20-cycle rounding、pilot20/formal50、sample filtering、duration invalidation、Type7 vector、sample stddev、
  no outlier removal、两种 FPS、five-run aggregate、missing timing/schema/non-finite、gzip mtime=0、SHA、affinity、commands/exit、
  temp cleanup/no pollution。
- **commit**：`feat: add M5 ORT CPU baseline harness`。
- **next**：仅 M5.4。

### M5.4 — Formal WSL2 ORT CPU Baseline Execution

- **prerequisites**：Level C Gate PASS 已固化；M5.3 committed；clean HEAD；Release；OFF/ON CTest；corpus/protocol SHA；
  provenance 环境可采集。
- **execution**：pilot100/drop20/compute N；prepare regular files；lowest allowed CPU；5 independent processes；30s waits；
  validate each run >=500 and >=30s；保存 gzip raw、TSV、per-run/aggregate、environment/provenance；tracked <=25 MiB。
- **result name**：`WSL2 x86_64 ONNX Runtime CPU Engineering Baseline`。
- **commit**：`test: add M5 WSL2 ORT CPU baseline evidence`。
- **next**：仅 M5.5。

### M5.5 — Evidence Consolidation

- **objective**：审核 Level C、五次 raw benchmark、从 TSV 重算、验证 summary/aggregate/SHA/commands/exit/build/environment，
  建 evidence index，并更新 EXPERIMENT_PLAN 的真实结果位置。
- **required checks**：raw/gzip SHA、TSV↔raw、run summary↔TSV、aggregate↔five runs、Release、无 warmup 混入、无 outlier
  删除、五 run 有效、size、clean source。
- **commit**：`docs: consolidate M5 validation and baseline evidence`。
- **next**：只读 M5.6。

### M5.6 — Read-only Deep Evidence Gate

检查 Reference 选择/隐藏 pipeline、corpus 合规/SHA/no image commit、derived reproducibility、maximum matching、tolerance、
真实 16/16、benchmark 时序、Release/SessionOptions、warmup、500+30s、五进程/30s wait、Type7/no outlier、raw→summary、
aggregate、provenance、WSL 定位、commands reproducibility、M1～M4 无漂移、无 TensorRT/Jetson 越界。输出 PASS/FAIL，
不得修改仓库。

PASS 后只进入 M5.7；FAIL 后另行批准 targeted remediation。

### M5.7 — Documentation-Only Closeout

- **prerequisite**：M5.6 PASS。
- **objective**：固化 Gate PASS、Level C 结论、baseline evidence 位置/环境限制/SHA/未执行项目；标记 M5 CLOSED；
  下一阶段为 Jetson/TensorRT planning PENDING。
- **forbidden**：production、重跑 benchmark、修改 evidence、开始 TensorRT、把 WSL 数字称 Jetson 结论。
- **commit**：`docs: close M5 Level C and ORT CPU baseline`。

## 15. M5.0 完成结论

- M5 完整阶段、两个 Gate、12+4 Level C corpus、20 图 benchmark corpus、数据合规、Reference、matching、统计、
  evidence/provenance/retention/失效规则已冻结；
- M5 状态为 `IN_PROGRESS`，M5.0 `COMPLETE`，M5.1 已完成；
- Level C、benchmark 和正式 evidence 尚未执行；M5 未 CLOSED；
- Strict、ASan、UBSan 仍为 `Not configured`，M5.0 未改变其状态；
- 下一步且唯一允许任务为 **M5.2 Level C Reference, Comparator and Formal Validation**。

## 16. M5.1 实际结果（2026-07-19）

M5.1 已完成，M5.2 保持 `PENDING`，M5 overall 仍为 `IN_PROGRESS`。本轮仅建立 corpus contract 和准备工具，未进入
Python ORT Reference、Comparator、正式 Level C、benchmark 或 evidence。

### 16.1 文件与 schema

- `tests/data/m5/manifests/level_c_original_corpus.json`：schema version 1，固定 12 项、validation split、六类覆盖、角色覆盖和原图 SHA256。
- `tests/data/m5/manifests/level_c_derived_corpus.json`：schema version 1，固定 4 项、24-bit BMP、OpenCV `INTER_LINEAR`、BGR border `[114,114,114]`、尺寸/padding 和输出 SHA256。
- `tests/data/m5/manifests/benchmark_corpus.json`：schema version 1，固定 20 项 validation 原图，前 12 项与 Level C original 一致。
- `tools/validation/prepare_m5_corpus.py`：严格 JSON parser/validator、重复键/未知键/缺失键/类型/路径/SHA/schema 校验、regular-file copy、确定性 derived BMP、原子 prepared 目录和临时 prepared manifest。
- `tests/test_prepare_m5_corpus.py`：manifest contract、失败路径、派生规则、regular copy、非 symlink 和重复准备测试。
- `CMakeLists.txt`：新增独立 `m5_corpus_preparation` CTest，使用项目 Python，不依赖数据集或模型。

三个 manifest 均不包含绝对路径、时间戳、主机名、运行结果或图片内容；没有提交 NEU-DET JPG/BMP，也没有修改 `.gitignore`。

### 16.2 本地 ignored 数据验证

本轮只读使用仓库已有 ignored validation root `data/yolo/neu_det/images/val`：

- 12 张 Level C original：SHA、200×200 尺寸和六类 coverage 全部通过；prepared 顺序为 `0000`～`0011`。
- 4 张 derived：目标尺寸分别为 319×201、201×319、321×199、199×321；连续两次生成 byte-identical；最终 SHA256 为：
  - `0012_derived_319x201_crazing_10.bmp`: `8b7457f25d17344440dbd26ada74a6373bf0a177a0e4b89ce754ff12893f9b29`
  - `0013_derived_201x319_inclusion_18.bmp`: `1b2c956884c7b7e573cfa634e3a93e5a510ca41d6d6b54cd44aa6148e3538ccb`
  - `0014_derived_321x199_pitted_surface_224.bmp`: `01e52085c57fe641d20ce3212f88dd40ac80f0604676b7bc9d5c7fa080214bbb`
  - `0015_derived_199x321_scratches_126.bmp`: `fbe8c46a58125d8cd58c623efc4da5fed8cc162f3ff2f53aad86363273336dd4`
- 20 张 benchmark original：SHA、200×200 尺寸、validation split 和六类 coverage 全部通过；prepared 顺序为 `0000`～`0019`。
- 所有 prepared 图片均为 regular file，不使用 symlink/hard link，OpenCV `IMREAD_COLOR` 可解码；源文件未修改。

Prepared 输出仅写入 `build-m5-1-validation/` 临时目录，未进入 `data/`、`results/` 或 Git。

### 16.3 验证与边界

- Python `py_compile`：通过。
- M5.1 定向 CTest：Model Smoke OFF `1/1 PASS`。
- Model Smoke OFF 全量 CTest：`25/25 PASS`。
- Model Smoke ON 全量 CTest：`33/33 PASS`。
- Strict、ASan、UBSan：仍为 `Not configured`。
- 未运行正式 Level C、benchmark，未生成正式 evidence。

下一步仅为 M5.2 Harness 实现；不得在本提交中提前实现或运行 M5.2 内容。
