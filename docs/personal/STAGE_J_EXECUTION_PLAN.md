# Stage J Plan v0.3 — FROZEN

**Jetson Orin Nano Super ONNX Runtime CPU Baselines**

## 0. 文档定位与冻结状态

### 0.1 文档性质
本文档是 Stage J 的完整冻结计划，用于：
冻结 Stage J 的阶段边界；
定义 Jetson 平台验收和 ONNX Runtime aarch64 构建合同；
定义跨平台 Level A/B/C 验证；
定义 Controlled 1-Core 与 Tuned k-Core 两套 CPU Baseline；
定义温度、频率、板载功耗 rail telemetry 和稳定性验证；
定义 Evidence、Consolidation 和 Deep Evidence Gate；
约束后续 Agent 的实现、实验和文档行为。
本版本已经完成最终一致性审查。
```text
Document status: FROZEN
Plan version: Stage J Plan v0.3
Stage status: PENDING
J0 status: IN PROGRESS
Open architecture review: CLOSED
```

### 0.2 当前状态
Stage J：PENDING
Stage J Plan v0.3：FROZEN
J0 Planning Freeze：IN PROGRESS
Stage J开发分支：未创建
生产代码修改：未开始
Stage J正式Evidence：未生成
设备事实：等待Jetson到货后在J1采集
冻结本计划不等于 J0 已完成。J0 仍需：
将冻结计划写入仓库；
补充相应 Decision；
生成任务卡；
核验 Git 起点；
从 clean main 创建正式开发分支。

### 0.3 后续审查原则
不再扩大Stage J技术路线
不再重复讨论已关闭决策
不得通过实现便利修改冻结实验协议
实现后只基于真实代码、日志和Evidence审查
任何范围变化必须新增Decision并重新评估受影响Gate

### 0.4 J0 仓库起点事实

- Repository root: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect`
- Planning base branch: `main`
- Planning base commit: `1801e8ad47645f5690b9bf2979929e06d7bdb6ec`
- Historical stage: `M0–M5 CLOSED`
- Production CMake target: `edge_ai_infer`
- Production executable output name: `edge_ai_defect`
- Existing M5 tag: `m5-onnxruntime-baseline-v1`
- Stage J implementation branch: `not created`
- Device-observed facts: `pending J1`
- Stage J production changes: `not started`
- Stage J formal Evidence: `not generated`

以上内容是 J0 时点的仓库事实和计划起点，不代表 J1 设备验收已经完成。

## 1. Stage J 定义

### 1.1 正式名称
Stage J — Jetson Orin Nano Super ONNX Runtime CPU Baselines

### 1.2 核心目标
将已经完成并关闭的 C++ ONNX Runtime Serial Baseline 从：
WSL2 x86_64
迁移到：
Jetson Orin Nano Super 8GB
JetPack 6.2.2
Jetson Linux 36.5
Ubuntu 22.04-based root filesystem
aarch64
256GB NVMe
完成：
设备验收
→ 平台冻结
→ ORT 1.23.2 aarch64源码构建
→ Jetson原生应用构建
→ 全量回归
→ Level A/B/C跨平台验证
→ 20图Benchmark Reference
→ CPU Profile语义预检
→ CPU Profile选择
→ Controlled 1-Core正式基线
→ Tuned k-Core正式基线
→ 30分钟Tuned Profile稳定性验证
→ Evidence Consolidation
→ Deep Evidence Gate
→ Documentation-Only Closeout

### 1.3 Stage J 研究问题
Stage J 回答：
当前冻结 C++ ONNX Runtime 应用能否在 Jetson aarch64 原生构建和运行；
Jetson C++ 预处理、ORT raw output 和最终检测语义是否与冻结 Reference 一致；
在固定 MAXN_SUPER、时钟、风扇和输入 corpus 下：Controlled 1-Core Application Profile 性能如何；
预注册候选中的 Tuned k-Core Application Profile 性能如何；

Tuned k-Core Profile 在持续运行 30 分钟时是否存在：崩溃；
内存异常；
检测语义漂移；
持续降频；
显著 latency 恶化；
OC/UV 事件；

能否为后续 Stage T 的 TensorRT FP16 同设备比较建立可信 CPU 基线。
Controlled 1-Core 不执行独立 30 分钟稳定性测试，除非后续新增正式 Decision。

## 2. 历史阶段关系
历史 M0～M5 属于已关闭的：
C++ ONNX Runtime大阶段
结构：
M0  工程初始化与ORT接入
M1  ModelContract与Preprocessor
M2  OnnxRuntimeEngine
M3  PostProcessor
M4  Serial Application
M5  Level C与WSL2 ORT CPU Baseline
历史 M0～M5：
不追溯改名；
不修改历史 Evidence；
不回写历史 schema；
不改变历史 Git 引用和 Tag。
后续暂定：
Stage T：TensorRT FP16
Stage P：Pipeline / System Optimization
Stage R：Research Extension

## 3. Stage J 里程碑
J0  Planning Freeze

J1  Device Acceptance and Platform Freeze

J2  ONNX Runtime v1.23.2 Native AArch64 Build

J3  Native Application Build, Runtime Controls,
    Regression and Sanitizers

J4  Cross-Platform Level A/B/C Validation

J5  CPU Profile Selection and Formal Baselines

J6  30-Minute Tuned Profile Stability

J7  Evidence Consolidation

J8  Deep Evidence Gate

J9  Documentation-Only Closeout
J5 内部分解：
J5.1  Benchmark Python Reference Preparation
J5.2  Candidate Semantic Precheck
J5.3  Candidate Sizing
J5.4  Profile Selection Campaign
J5.5  Controlled 1-Core Formal Baseline
J5.6  Tuned k-Core Formal Baseline
J5.7  J5 Evidence Gate

## 4. 已冻结输入

### 4.1 硬件目标

| 项目 | 冻结目标 |
| --- | --- |
| 设备 | Jetson Orin Nano Super Developer Kit |
| 内存 | 8GB |
| 存储 | 256GB NVMe SSD |
| Root filesystem | NVMe |
| 散热 | 主动风扇 |
| 设备占用 | 可长期独占 |
| 网络 | 可联网、可SSH |
| 权限 | sudo |
| 编译 | Jetson本机aarch64原生编译 |
| 交叉编译 | Stage J不做 |



### 4.2 软件目标

| 项目 | 冻结目标 |
| --- | --- |
| JetPack | 6.2.2 |
| Jetson Linux / L4T | 36.5 |
| Root filesystem | Ubuntu 22.04-based |
| C++ | C++17 |
| ONNX Runtime | 1.23.2 |
| Execution Provider | CPUExecutionProvider |
| 模型精度 | FP32 |
| 模型Batch | 1 |
| 输入 | float32 [1,3,640,640] |
| 输出 | float32 [1,10,8400] |
| 预处理 | 冻结M5 Preprocessor |
| 后处理 | 冻结M5 PostProcessor/NMS |
| SerialRunner | 继承M5处理顺序和语义 |


设备实际状态必须在 J1 验证。商品页面或商家口头说明不能替代 J1 Evidence。

### 4.3 继承资产
Stage J 不重新定义：
冻结 ONNX 模型及 SHA；
ModelContract；
LetterBox；
六类别及顺序；
PostProcessor 和 NMS；
HostTensor；
Detection；
IInferenceEngine；
最大二分匹配算法；
M5 Level C 容差；
M5 Reference provenance。
M5 benchmark 中未被 Stage J 明确修改的统计公式可以复用。
如 M5 与本计划存在冲突：
Stage J Plan v0.3
是 Stage J 的权威协议。M5 历史 Evidence 不回改。

## 5. Stage J 范围

### 5.1 包含
Jetson 到货验收；
JetPack/L4T、NVMe、QSPI、flash configuration 确认；
MAXN_SUPER 模式确认；
ORT 1.23.2 aarch64 源码构建；
Jetson Release 构建；
x86 与 Jetson 适用测试回归；
ASan/UBSan 模型无关测试；
Jetson Level A/B/C；
Controlled 1-Core Application Profile；
Tuned k-Core Application Profile；
20 图 benchmark Python Reference；
每个 CPU Profile 的语义和确定性 precheck；
CPU Profile selection；
两套正式五次 separate-process baseline；
30 分钟 Tuned Profile 稳定性；
tegrastats、温度、频率和 rail telemetry；
OC/UV counter Gate；
Evidence；
Consolidation；
Deep Evidence Gate；
Documentation-only closeout。

### 5.2 不包含
TensorRT
CUDA EP
TensorRT EP
FP16
INT8
TensorRT Engine
CUDA Stream
CUDA Graph
CUDA Preprocess
GPU NMS
PipelineRunner
BoundedQueue
FramePacket
异步推理
多线程流水线
模型剪枝
知识蒸馏
PTQ/QAT
动态Shape
ROS2
摄像头
RTSP
Qt
PLC
生产现场集成
通用BackendFactory
通用SinkFactory
插件系统
实验数据库
跨机器调度
自动恢复系统

## 6. 接口与扩展边界

### 6.1 Stage J 原则上保持不变
原则上不修改：
IInferenceEngine；
HostTensor；
Preprocessor；
PostProcessor；
Detection；
SerialRunner 的 source→preprocess→inference→postprocess→sink 顺序；
模型合同；
Frozen ONNX；
CPU 后处理。
SerialRunner 允许增加可选 Trace Observer 及错误传播，但不得改变其推理和后处理语义。

### 6.2 Stage J 允许的最小修改
RuntimeConfig v2；
ORT backend-specific immutable options；
OpenCV thread 配置；
IFrameTraceObserver；
FrameTraceRecorder；
Stage J stability executable；
CycleDetectionHashSink；
benchmark monotonic trace；
ASan/UBSan CMake 选项；
Stage J comparator、canonicalizer、launcher 和 Evidence 工具。

### 6.3 后续 Stage T 边界
Stage T 第一版暂定：
TensorRTEngine implements IInferenceEngine
HostTensor float32 input
HostTensor float32 output
TensorRT内部完成H2D、FP16和D2H
SerialRunner保持
PostProcessor保持
只有在第二个真实生产后端出现时，才设计：
BackendKind；
EngineFactory；
TensorRT target；
backend selection schema。

## 7. RuntimeConfig v2

### 7.1 v1 与 v2 隔离
schema_version: 1
继续走历史 v1 解析路径。
schema_version: 2
进入 Stage J v2 解析路径。
禁止：
v1 和 v2 字段混用；
v1 接受 v2 新字段；
通过环境变量覆盖 v2；
未记录 CLI override；
Python launcher 直接修改 Engine 私有成员。

### 7.2 edge_ai_infer v2 Schema
```yaml
schema_version: 2
application_kind: edge_ai_infer

backend:
  type: onnxruntime_cpu
  onnxruntime:
    execution_mode: sequential
    graph_optimization_level: all
    intra_op_threads: 1
    inter_op_threads: 1
    intra_op_allow_spinning: true
    inter_op_allow_spinning: true
    cpu_arena_enabled: true
    memory_pattern_enabled: true

runtime:
  opencv_num_threads: 1

model:
  contract_path: ...
  model_path: ...

input:
  type: directory
  directory: ...

output:
  json_path: ...
  console: false
  overwrite: false

postprocess:
  confidence_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680.0
  agnostic: false
  multi_label: false

timing:
  enabled: true
  monotonic_trace_enabled: true
```
必须包含完整 output mapping。
正式 Stage J 运行：
output.overwrite == false

### 7.3 stage_j_stability v2 Schema
stage_j_stability 必须包含：
application_kind；
backend；
runtime；
model；
input；
postprocess；
timing。
禁止出现整个普通 detection output mapping：
output
以下参数仅来自 Resolved Protocol：
attempt directory；
output evidence paths；
target cycles；
expected cycle SHA；
minimum wall time；
audit cycle roles；
overwrite policy。
不增加：
sink_type
通用SinkFactory

### 7.4 条件严格校验
原则：
所有适用于当前 executable 和 run type 的字段必须显式提供；不适用字段必须禁止出现。

未知字段继续拒绝。
所有 Stage J 正式输出路径均禁止覆盖。

### 7.5 v1 兼容性 Gate
J3 必须证明：
v1 合法配置仍能解析；
v1 拒绝 v2 字段；
v1 映射到历史等价 ORT 设置：sequential；
graph optimization all；
intra=1；
inter=1；
CPU arena enabled；
memory pattern enabled；

v1 保持历史 OpenCV 路径，不因 Stage J v2 自动改变；
x86 Release OFF 全量回归；
x86 Release ON 全量回归；
M5 Level B 适用测试；
M5 Level C 工具和适用测试；
历史 v1 application smoke。
任何行为变化：
J3 FAIL

## 8. ORT Backend Immutable Options

### 8.1 类型
```cpp
struct OnnxRuntimeEngineOptions {
    ExecutionMode execution_mode;
    GraphOptimizationLevel graph_optimization_level;

    int intra_op_threads;
    int inter_op_threads;

    bool intra_op_allow_spinning;
    bool inter_op_allow_spinning;

    bool cpu_arena_enabled;
    bool memory_pattern_enabled;
};
```
使用项目自有枚举，不向公共推理接口暴露 ORT 类型。

### 8.2 构造方式
```cpp
explicit OnnxRuntimeEngine(
    OnnxRuntimeEngineOptions options = {});
```
配置在 Session 创建前固定。
不使用可变 setter 作为正式方案。

### 8.3 配置证据三层模型
Engine 提供：
```cpp
OrtConfigurationRecord configuration_record() const;
```
requested_options
来源：
规范化 RuntimeConfig v2
applied_options
Engine 实际按确定顺序调用 ORT 配置 API 并成功完成的值。
规则：
任一配置调用失败，初始化立即失败；
不允许部分失败后创建 Session；
applied_options 由 Engine 内部记录；
不能由调用方复制 requested 值伪造。
queried_options
只记录 ORT 1.23.2 实际支持独立回读的字段。
可回读：
```json
{
  "value": "...",
  "runtime_queryable": true,
  "verification_method": "ort_session_options_query"
}
```
不可回读：
```json
{
  "runtime_queryable": false,
  "verification_method": "successful_applied_api_call"
}
```
不得复制 requested 值到 queried value。

### 8.4 Evidence Gate
```json
{
  "requested_runtime_options": {},
  "applied_runtime_options": {},
  "queried_runtime_options": {},
  "requested_applied_match": true,
  "session_creation_succeeded": true,
  "field_verification": {}
}
```
硬 Gate：
requested_applied_match == true
session_creation_succeeded == true
对于可回读字段：
queried value == applied value
允许的正式表述：
所有请求配置均被成功应用并完成 Session 创建；ORT 支持查询的字段完成了独立回读，其余字段以成功的配置 API 调用作为应用证据。

禁止表述：
所有 SessionOptions 均已完成运行时独立回读。


## 9. OpenCV 线程合同
应用启动后：
加载并验证RuntimeConfig
→ cv::setNumThreads(1)
→ cv::getNumThreads验证
→ 创建Preprocessor和输入组件
必须早于：
第一次图片解码；
第一次 resize；
Level A；
benchmark warm-up。
Evidence：
requested_opencv_threads = 1
reported_opencv_threads = 1
opencv_version
opencv_build_information_sha256
parallel_backend_or_framework
硬 Gate：
reported_opencv_threads == 1
若当前 OpenCV 没有特定查询 API：
使用该版本实际支持的等价接口；
保存 cv::getBuildInformation()；
不得省略线程后端记录。

## 10. Protocol Template 与 Resolved Protocol

### 10.1 职责
RuntimeConfig v2：
进程内部软件配置

StageJRunProtocol：
实验执行、资源、温度、采样、campaign和输出配置

### 10.2 Protocol Template
Git 跟踪：
configs/stage_j/protocol_templates/
只包含：
算法；
固定阈值；
候选解析政策；
Gate；
统计方法；
路径规则。
不得包含伪造设备事实或占位值，例如：
<attempt_id>
<binary_sha>
<actual_cpu_set>
示意：
```yaml
protocol_schema_version: 1
run_type: profile_selection

candidate_policy:
  values:
    - 1
    - 2
    - 4
    - non_cpu0_count
    - all_allowed_cpu_count

candidate_order:
  primary: thread_count_ascending
  secondary: cpu_set_lexicographic

selection:
  rounds: candidate_count
  near_tie_relative_threshold: 0.01

benchmark:
  corpus_size: 20
  warmup_frames: 60
  minimum_measured_frames: 200
  minimum_measured_wall_ms: 10000
```

### 10.3 Resolved Protocol
每一个真实 C++ application attempt 或 campaign 都必须有：
resolved_protocol.yaml
公共字段：
attempt ID；
campaign ID；
run type；
runner kind；
executable 和 SHA；
RuntimeConfig 路径和 SHA；
ORT SHA；
model SHA；
contract SHA；
allowed/online CPUs；
application CPU set；
telemetry CPU set；
nvpmodel；
thermal Gate；
telemetry规则；
attempt directory；
output paths；
overwrite=false。
条件字段：
Candidate Semantic Precheck
包含：
候选列表；
每个候选CPU set；
-两个完整cycle；
Python Reference SHA；
-比较容差。
不要求尚未生成的 candidate expected SHA。
Candidate Sizing
包含：
单一候选；
CPU set；
candidate expected SHA；
warmup=60；
measured=200。
Selection Campaign
包含：
每个候选 measured frames；
每个候选 expected SHA；
-完整 rotation；
selection rounds；
near-tie rule。
Controlled/Tuned Formal
包含：
Profile；
-独立 sizing结果；
formal measured frames；
-五次run schedule；
Profile expected SHA。
Stability
包含：
Tuned Profile；
inherited expected SHA；
target cycles；
minimum wall time；
first/middle/last audit roles。
Python Reference
J5.1 使用单独的 Reference provenance/protocol记录：
Python interpreter和版本；
Python依赖；
script和source commit；
model、contract和corpus SHA；
Reference run count；
output paths。
Python Reference 不伪造 C++ RuntimeConfig 或 application_kind。

### 10.4 Resolved Protocol 生命周期
Candidate Semantic Precheck
生成 precheck campaign Resolved Protocol。
Candidate Sizing
每个 sizing attempt 使用独立 Resolved Protocol。
Selection Campaign
所有候选 precheck 和 sizing 完成后，生成最终 Selection Resolved Protocol。
Controlled/Tuned Formal
分别生成独立 Formal Resolved Protocol。
Stability
生成独立 Stability Resolved Protocol。
任何 campaign 开始后：
resolved_protocol SHA不得变化
若候选、CPU set、帧数、SHA、binary、ORT、配置、rotation 或 thermal 规则变化：
当前attempt/campaign作废
→ 新attempt
→ 新resolved protocol

### 10.5 路径与 executable 一致性
正式 Evidence 使用：
repo-relative；
attempt-relative。
禁止用户绝对路径。
必须验证：
实际生产推理executable
↔ application_kind=edge_ai_infer

stage_j_stability
↔ application_kind=stage_j_stability
生产 executable 的准确 target 和 output name在 J0 根据仓库事实写入 Template，不得使用示例名称代替。

## 11. CPU Profile 定义

### 11.1 Controlled 1-Core Application Profile
ORT_SEQUENTIAL
intra_op_threads = 1
inter_op_threads = 1
OpenCV threads = 1
ORT spinning enabled
固定单核process affinity
CPU 选择：
allowed_online_cpus =
sched_getaffinity ∩ online CPU set

若存在非CPU0：
    选择编号最高的非CPU0
否则：
    使用CPU0
用途：
受控单核结果；
Level A/B/C Validation Profile；
与 M5 单线程环境关系描述；
次要 CPU baseline。

### 11.2 Tuned k-Core Application Profile
候选：
unique({
  1,
  2,
  4,
  non_cpu0_count,
  all_allowed_cpu_count
})
删除：
<1；
大于 allowed CPU 数量；
重复；
无法构造 CPU set 的值。
当：
k <= non_cpu0_count
使用最高编号的 k 个非 CPU0 allowed CPU。
当：
k == all_allowed_cpu_count
使用全部 allowed CPU，包括 CPU0。

对于每个候选 `k`，进程内部参数固定为：

```yaml
execution_mode: sequential
graph_optimization_level: all
intra_op_threads: k
inter_op_threads: 1
intra_op_allow_spinning: true
inter_op_allow_spinning: true
cpu_arena_enabled: true
memory_pattern_enabled: true
opencv_num_threads: 1
```

不得将 `inter_op_threads` 设为 `k`。不得切换 `ORT_PARALLEL`。

### 11.3 结论边界
Tuned 结论只能表述为：
当前模型、20 图 workload、当前 JetPack、ORT build、MAXN_SUPER 和预注册候选集合中的最优 k-Core Application Profile。

不得表述为：
Jetson Orin Nano Super 普遍最优 ORT 线程数。


## 12. Affinity 控制与采样

### 12.1 控制时序
Application affinity 必须在：
child exec前
设置。
后续 ORT worker 继承该 mask。
Telemetry：
wrapper → CPU0
tegrastats child → CPU0
affinity sampler → CPU0

### 12.2 全生命周期采样
获得 application PID 后立即启动采样，直至 application 退出。
采样周期：
500 ms
读取：
/proc/<pid>/status
/proc/<pid>/task/<tid>/status
同时检查：
application；
telemetry wrapper；
tegrastats child。
记录：
CLOCK_MONOTONIC timestamp；
PID/TID；
thread name；
Cpus_allowed_list；
first seen；
last seen。

### 12.3 Gate
Application 任一被观测 TID：
observed_cpu_mask ⊆ profile_cpu_set
越界：
run invalid
持久线程：
至少两个连续采样中出现
持久线程只使用 profile set 的子集：
不判资源越界；
记录 persistent_subset_affinity_observed=true；
Deep Gate 人工检查 Profile 解释。
Telemetry 进程树必须：
observed_cpu_mask ⊆ {CPU0}
all-core candidate：
telemetry_application_cpu_overlap=true
报告只能声称：
所有被采样到的 application TID 均符合 affinity 约束。

不能声称绝对捕获了所有短生命周期线程。

## 13. Frame Trace

### 13.1 数据结构
struct FrameTraceRecord {
    std::size_t sequence_index;
    std::int64_t frame_start_monotonic_ns;
    std::int64_t pre_sink_end_monotonic_ns;
    std::int64_t sink_end_monotonic_ns;
    FrameTimings timings;
};

### 13.2 Observer
class IFrameTraceObserver {
public:
    virtual ~IFrameTraceObserver() = default;

    virtual core::Status on_frame_complete(
        const FrameTraceRecord& record) = 0;
};
成功 Status 的准确 API 名称按当前代码事实实现，不凭计划示例硬编码。

### 13.3 调用顺序
frame_start
→ source
→ preprocess
→ inference
→ postprocess
→ pre_sink_end
→ sink.write_frame()
→ sink_end
→ observer.on_frame_complete()
→ 检查Status
→ 下一帧
Observer 失败：
当前 Sink 已完成；
停止读取新帧；
Observer 错误为主错误；
执行既有 cleanup；
cleanup 错误进入 cleanup_diagnostics[]；
application 非零退出；
attempt FAIL。

### 13.4 FrameTraceRecorder
运行前：
reserve(total_frames)
回调仅允许：
sequence index 检查；
timestamp 顺序检查；
capacity 检查；
compact record 追加。
禁止：
I/O；
-锁；
-序列化；
-哈希；
-动态统计；
-控制台输出；
-运行中扩容。
Evidence Gate：
trace_reserved_capacity == total_frames
trace_record_count == processed_frame_count
trace_reallocation_count == 0
reserve 失败：
不进入SerialRunner
attempt FAIL
所有 J5/J6 正式性能运行均启用同一 Recorder。

### 13.5 时间域
统一：
clock_gettime(CLOCK_MONOTONIC)
unit = nanoseconds
UTC 只用于日志检索，不参与窗口计算。

## 14. Timing 指标

### 14.1 measured window
measured_start =
第一个measured frame的frame_start

measured_end =
最后一个measured frame的sink_end
measured_phase_wall_ms =
(measured_end - measured_start) / 1e6
缺少起止 marker：
run invalid

### 14.2 pre_sink
pre_sink_total_ms 是从 frame source 开始到 postprocess 结束的直接时间差，不通过各阶段求和替代。
pre_sink_fps =
measured_count /
(sum(pre_sink_total_ms) / 1000)
不包含：
Sink；
Trace Recorder；
帧间调度。

### 14.3 wall_fps
wall_fps =
measured_count /
(measured_phase_wall_ms / 1000)
包含：
中间 measured frame 的 Sink；
中间 measured frame 的 Trace Recorder 回调；
帧间应用调度。
不包含：
最后一个 measured frame 的 Trace Recorder 回调完成时间。
Stage T 正式比较必须使用相同 instrumentation 和定义。

### 14.4 backend_fps_equivalent
backend_fps_equivalent =
measured_count /
(sum(measured inference_ms) / 1000)
该指标只是 inference stage 的串行等效处理速率：
不是应用 wall throughput；
不包含 H2D/D2H 子阶段拆分；
不替代 pre_sink_fps 或 wall_fps。

## 15. Launcher 状态机
唯一正式入口：
tools/benchmark/run_stage_j.py --protocol <resolved_protocol.yaml>
不得接受覆盖协议语义的 CLI 参数。
允许：
--help
--validate-only

### 15.1 状态
CREATED
→ LOCK_ACQUIRED
→ PREFLIGHT_PASSED
→ THERMAL_GATE_PASSED
→ TELEMETRY_READY
→ APPLICATION_STARTED
→ MONITORING_ACTIVE
→ APPLICATION_EXITED
→ POSTFLIGHT_PASSED
→ VALIDATED
→ PASS / FAIL
Affinity 的最终验证发生在：
POSTFLIGHT_PASSED / VALIDATED
而不是 application 运行中提前宣告。
状态追加写入：
run_journal.jsonl

### 15.2 执行顺序
获取设备级互斥锁；
创建唯一 attempt directory；
验证所有目标不存在；
加载并校验 Resolved Protocol；
校验 RuntimeConfig、binary、ORT、model、contract SHA；
environment preflight；
读取 OC/UV counters；
Thermal Gate；
启动 telemetry wrapper 和 tegrastats；
等待 pre-roll 和首批 telemetry；
在 child exec 前设置 application affinity；
启动 application；
获得 PID 后立即启动 affinity sampler；
application 执行；
application 退出；
等待 post-roll；
停止 telemetry 和 sampler；
再次读取 OC/UV counters；
检查环境漂移、timeline、affinity、telemetry；
运行 analyzer 和 semantic checks；
生成 attempt status；
释放设备锁。

## 16. Thermal 与性能模式

### 16.1 MAXN_SUPER Gate
正常路径：
正确Super flash configuration
→ MAXN_SUPER可见
→ 可设置
→ 必要时reboot
→ nvpmodel验证
→ jetson_clocks --fan
→ jetson_clocks --show
→ 受控负载稳定
若不可用：
检查 SKU；
检查 flash configuration；
检查 QSPI/firmware；
检查 JetPack/L4T；
官方升级或重刷；
重新验证。
仍不可用：
J1 BLOCKED
不能自动降级普通模式并仍声称完成原 Stage J。

### 16.2 T_idle_ref
每个执行 set 独立建立：
Profile Semantic Precheck；
Candidate Sizing；
Selection Campaign；
Controlled Formal；
Tuned Formal；
Stability。
流程：
设置 nvpmodel、clocks、fan；
空闲至少 5 分钟；
连续采样 60 秒；
按 thermal zone type/name 选定相关 zone；
每个采样点取相关 zone 最大值；
序列中位数作为 T_idle_ref。
每个 run 前：
等待至少30秒
当前最大相关温度 <= T_idle_ref + 2°C
最近10秒温度range <= 1°C
最长等待：
600秒
超时：
当前set FAIL
以下情况重新建立：
reboot；
nvpmodel 变化；
重新执行 jetson_clocks；
风扇策略变化；
设备长时间停机；
室内条件明显变化；
OC/UV 或温度异常。
没有外部温度计：
ambient_temperature = unavailable

## 17. Telemetry

### 17.1 采集
requested_interval_ms = 1000
pre_roll_ms >= 3000
post_roll_ms >= 3000
每行：
UTC timestamp；
CLOCK_MONOTONIC timestamp；
raw tegrastats line。

### 17.2 包围样本
必须存在：
t_before_start <= measured_start <= t_after_start
t_before_end <= measured_end <= t_after_end
无包围样本：
run invalid
禁止外推。

### 17.3 Coverage
相邻样本 gap：
gap <= 2500 ms
才算有效覆盖区间。
coverage_ratio =
有效采样区间与measured window交集的并集长度
/
measured window总长度
硬 Gate：
coverage_ratio >= 0.90
maximum_gap_ms <= 2500
measured_window_sample_count >= floor(duration_seconds) - 2

### 17.4 Rail 统计
仅使用能包围 measured window 的 instantaneous rail samples。
报告：
sample mean；
time-weighted mean；
min；
max；
P50；
P95；
sample count。
正式 mean：
基于板载 telemetry 瞬时 rail 样本的分段线性、时间加权估计。

禁止称为：
插座功耗；
外部整机功耗；
精密能量计量。

### 17.5 OC/UV Gate
J1 冻结实际：
oc*_event_cnt
oc*_throt_en
路径和含义。
每次 sizing、selection、formal、stability 前后读取。
任一相关 counter 增加：
run invalid
停止并检查：
电源适配器；
供电线；
MAXN_SUPER；
温度；
板卡状态。

### 17.6 J1 待观测并冻结的平台规则

以下设备相关事实统一标记为 `to be observed and frozen in J1`，J0 不填入猜测值：

- 实际 thermal zone 路径和名称；
- 实际 CPU frequency sysfs 路径；
- MAXN_SUPER 对应 mode ID；
- OC/UV counter 路径与含义；
- sustained throttling 的设备相关目标频率；
- tegrastats 实际 rail 名称；
- 实际 allowed/online CPU set；
- Jetson 实际 GCC、OpenCV、CMake 和 Python 版本。

## 18. J4：Level A/B/C
统一 Validation Profile：
Controlled 1-Core
OpenCV threads = 1
ORT intra = 1
ORT inter = 1
ORT sequential
ORT spinning enabled
MAXN_SUPER
jetson_clocks --fan
相同binary / ORT / model / contract

### 18.1 Level A
复用 8 个冻结人工资产。
阈值：

| 类型 | MAE | max_abs |
| --- | --- | --- |
| exact | 1e-7 | 1e-7 |
| resize | 5e-4 | 2/255 + 1e-6 |


验证：
tensor；
shape；
dtype；
gain；
padding；
resized dimensions；
NaN/Inf。
不重新生成 Level A golden。

### 18.2 Level B
使用冻结 float32 输入 tensor：
[1,3,640,640]
little-endian
正式 Reference：
历史M2冻结Python ONNX Runtime 1.23.2
CPUExecutionProvider raw golden output
Stage J Gate：
overall MAE <= 1e-6
overall max_abs <= 1e-4
额外状态：
m2_strict_equivalent =
MAE <= 1e-6
and max_abs <= 1e-5
输出：
overall；
bbox group；
score group；
-逐通道；
-最大误差位置；
finite count；
NaN/Inf；
tensor SHA。
两次 Jetson separate-process raw output：
SHA256必须相同
不同则 J4 FAIL。

### 18.3 Level C
Corpus：
12 original
4 deterministic derived
共16张
Reference：
M5 canonical Python Reference run_1
容差：
confidence <= 1e-4
bbox每坐标 <= 0.01 px
匹配：
class-aware maximum bipartite matching
要求：
16/16 PASS
两次 Jetson canonical payload：
byte-identical
不同则 J4 FAIL。

## 19. J5 Benchmark Semantic Gate

### 19.1 20图 Python Reference
J5 开始前，在 M5 冻结的 x86 Python Reference 环境中，对 20 图 benchmark corpus 运行两次：
benchmark_python_reference_run_1.json
benchmark_python_reference_run_2.json
使用：
相同冻结 ONNX；
-相同 Python preprocessing；
-相同 Python postprocessing；
ONNX Runtime 1.23.2；
CPUExecutionProvider；
-冻结依赖和source commit。
要求：
strict JSON PASS；
canonical payload byte-identical；
SHA 相同；
20 图文件 SHA 与 benchmark manifest 一致。
得到：
benchmark_python_reference_sha256
该 Reference 是 20 图 workload 的独立正确性权威。
Jetson Python ORT 不是正式 Reference，仅可作为故障诊断。
若工具需扩展：
增加最小 manifest-driven 入口；
-复用现有推理、预处理、后处理；
-不得复制第二套 Reference pipeline。

### 19.2 每个候选 Profile 语义 Precheck
每个候选执行两个完整 20 图 cycle：
profile_<k>_precheck_1.canonical.json
profile_<k>_precheck_2.canonical.json
同 Profile 确定性
precheck_1 byte-identical precheck_2
SHA相同
得到：
profile_expected_cycle_sha256[k]

每个候选的两次 precheck 必须是两个 `separate-process application attempts`：每个进程重新创建 ORT Session，且每个进程只执行一个完整的 20 图 cycle。两个进程必须使用相同 binary、ORT、model、contract、RuntimeConfig 和 CPU Profile；两个 canonical payload 必须 byte-identical，且两个 SHA 必须一致。

不得在一个长期进程内连续执行两个 cycle 来替代该 Gate。

与 Python Reference 一致
使用：
20/20 PASS
confidence <= 1e-4
bbox每坐标 <= 0.01 px
class-aware maximum bipartite matching
任一候选失败：
Candidate Semantic Precheck Campaign FAIL
不得静默删除候选。
修复后重跑全部候选 precheck。

### 19.3 跨 Profile 关系
不同 Profile 不要求 byte-identical。
输出：
controlled_tuned_byte_identical
controlled_tuned_semantic_equivalent
若 SHA 不同，但两者分别通过 Python Reference：
controlled_tuned_byte_identical=false
controlled_tuned_semantic_equivalent=true
必须在最终限制中说明线程 Profile 产生了可容忍数值差异。

### 19.4 Performance Run 的 Cycle SHA 来源
edge_ai_infer 运行
Sizing、Selection、Controlled Formal 和 Tuned Formal：
application 使用标准 JsonSink；
application 输出完整 raw detection JSON；
run 完成后，由 launcher/analyzer 使用共享 canonical writer；
按每个完整 20 图 cycle 生成 canonical bytes和SHA；
SHA必须等于对应 profile_expected_cycle_sha256[k]。
不在 production application 中增加通用 Cycle Hash Sink。
stage_j_stability 运行
Stability 使用 CycleDetectionHashSink 在运行期增量计算 cycle canonical SHA。
J4、J5离线 canonicalizer 与 J6在线 Sink必须共享同一浮点格式、路径规范和 framing合同。

## 20. J5 Candidate Sizing
每个候选：
warmup = 60
measured = 200
根据：
sizing_wall_ms_per_frame =
measured_phase_wall_ms / 200
计算：
selection_measured_frames =
round_up_to_multiple_of_20(
  max(
    200,
    ceil(11000 / sizing_wall_ms_per_frame)
  )
)
Sizing 不进入候选比较。
每个完整 cycle：
cycle_sha == profile_expected_cycle_sha256[k]
Sizing失败时：
仅该候选的 sizing attempt 作废；
修复问题后重新执行该候选 sizing；
Selection Campaign 尚未开始，因此不需要重跑其他候选；
所有候选 measured frame 数全部冻结后，才能生成 Selection Resolved Protocol。

## 21. J5 Profile Selection

### 21.1 完整轮换
selection_rounds = candidate_count
候选 A～E：
R1 A B C D E
R2 B C D E A
R3 C D E A B
R4 D E A B C
R5 E A B C D
每个候选：
次数相同；
每个顺序位置一次。

### 21.2 每次运行
warmup = 60
measured = selection_measured_frames[k]
measured frames为20整数倍
measured wall >= 10000 ms
每个完整 cycle：
cycle_sha == profile_expected_cycle_sha256[k]

### 21.3 选择指标
每次 run：
mean pre_sink_total_ms
每个候选：
跨selection rounds取median
中位数：
奇数：中间值；
偶数：中间两值算术平均。
近似平局：
(candidate_median - best_median) / best_median <= 0.01
平局集合：
线程数更少；
不包含 CPU0；
CPU set 字典序。

### 21.4 单候选
candidate_count == 1
则：
profile_selection_status=trivial_single_candidate
若 Controlled 与 Tuned 完全相同：
只执行一套 Formal Sizing 和一套正式 Evidence；
Consolidation 建立双角色引用；
记录：
controlled_and_tuned_profiles_identical=true

### 21.5 Campaign 失败
任一正式 selection run 出现：
不足 10 秒；
crash；
telemetry 不完整；
OC/UV；
-环境漂移；
-affinity 越界；
-Thermal Gate；
-timeline；
-frame count；
-cycle hash；
则：
整个Selection Campaign作废
不得局部补跑或拼接 campaign。

## 22. J5 正式 Baseline

### 22.1 两套结果
Controlled 1-Core Formal Baseline
Tuned k-Core Formal Baseline
若两个 Profile 完全相同，则按第 21.4 节只执行一套。

### 22.2 Formal Sizing Pilot
每套不同 Profile 独立执行 sizing pilot。
pilot warmup = 60
pilot measured frames >= 200
formal minimum measured frames = 500
target measured duration = 33000 ms
minimum valid wall = 30000 ms
定义：
pilot_wall_ms_per_frame =
pilot_measured_phase_wall_ms /
pilot_measured_frame_count
正式 measured frames：
formal_measured_frames =
round_up_to_multiple_of_20(
  max(
    500,
    ceil(33000 / pilot_wall_ms_per_frame)
  )
)
若任何正式 run 的 measured wall 少于 30000 ms：
整套五run无效
→ 增加formal_measured_frames
→ 重新执行完整五run集合
Sizing pilot不进入正式统计。

### 22.3 正式 repetitions
每套：
5 separate-process repetitions
不是统计学意义上的完全独立样本。
每个 run：
preflight；
Thermal Gate；
telemetry；
affinity；
-完整 timeline；
-正确 cycle SHA；
-无样本删除；
-无 outlier 删除。
任何 run 无效：
整套五run重跑
不得拼接不同 attempt。

### 22.4 统计
每个 run：
count；
-mean；
-min；
-max；
-P50；
-P95；
-P99；
-sample standard deviation；
-pre_sink_fps；
-wall_fps；
-backend_fps_equivalent。
Percentile：
Type 7
跨五 run：
mean；
sample standard deviation；
median；
min；
max。
论文主要结果：
five-run mean ± sample standard deviation
次要：
auxiliary pooled frame-level statistics
不删除 outlier，不 Winsorize。

## 23. J6：30分钟稳定性

### 23.1 Profile
只使用：
最终Tuned k-Core Profile

### 23.2 Expected SHA
直接继承：
tuned_profile_expected_cycle_sha256
J6 不重新定义 expected。

### 23.3 Precheck
稳定性前运行两个完整 cycle：
cycle_precheck_1.canonical.json
cycle_precheck_2.canonical.json
要求：
byte-identical
SHA == tuned_profile_expected_cycle_sha256

### 23.4 Stability executable
stage_j_stability
复用：
DirectorySource；
Preprocessor；
OnnxRuntimeEngine；
PostProcessor；
SerialRunner；
CycleDetectionHashSink；
FrameTraceRecorder。
不增加通用 Sink Factory。

### 23.5 CycleDetectionHashSink
只负责：
sequence/path 检查；
canonical cycle bytes；
cycle SHA；
detection count；
per-class count。
不负责：
timing；
sink_end；
-逐帧 I/O。
唯一 hash 输入：
canonical cycle JSON完整UTF-8字节流
J4/J5/J6 必须共享同一 canonical writer。

### 23.6 Cycle 数量
从 Tuned Formal 五次结果计算每个 run 的：
measured_phase_wall_ms /
measured_complete_cycle_count
取五个结果中的最小值，定义为：
estimated_cycle_wall_ms
使用最快观测周期时间可以降低 30 分钟不足的风险。
target_cycles =
ceil(
  1.05 * 1800000 /
  estimated_cycle_wall_ms
)
要求：
只处理完整 20 图 cycle；
measured wall >= 1800000 ms。
不足：
本次稳定性attempt无效
→ 增加cycle数
→ 完整重跑

### 23.7 Audit payload
设总 cycle 数为 N：
first = 0
middle = floor((N-1)/2)
last = N-1
保存：
audit_cycle_first.canonical.json
audit_cycle_middle.canonical.json
audit_cycle_last.canonical.json
索引重合则保存一份并记录多角色。
所有 cycle：
cycle_sha == tuned_profile_expected_cycle_sha256
Deep Gate：
重算两个 precheck；
重算 first/middle/last；
其他 cycle 只验证运行期 hash manifest。

### 23.8 稳定性判定
硬检查：
无 crash；
无 OOM；
无 NaN/Inf；
无 cycle SHA 漂移；
telemetry 完整；
频率轨迹完整；
无 OC/UV；
无明确 sustained throttling。
报告：
前 20% mean/median/P95；
后 20% mean/median/P95；
变化百分比；
最大温度；
最大内存；
swap 变化；
rail telemetry；
频率轨迹。
默认失败调查阈值：
后20% median pre_sink latency
相对前20%增加 > 10%
超过 10% 时：
J6 FAIL
除非形成独立、可复现且非热原因的正式 remediation Decision，并完整重跑 J6。
Stage J 只能声称：
完成 30 分钟受控持续运行验证。

不能声称生产环境长期稳定。

## 24. ORT 1.23.2 AArch64 SDK

### 24.1 主路径
Official ONNX Runtime v1.23.2 source
Jetson native aarch64
Release
shared library
CPUExecutionProvider
禁止：
CUDA EP
TensorRT EP
XNNPACK
ACL/ArmNN
OpenMP
minimal build
reduced operator config
training
custom ops
LTO
人为-march=native

### 24.2 J2.0
在真实 v1.23.2 source 上执行：
./build.sh --help
根据实际帮助冻结唯一命令。
计划只冻结语义：
Release；
shared；
CPU-only；
skip upstream tests；
parallel=2，除非正式构建前重新冻结；
fixed build dir。
不存在的选项：
not_applicable
不得伪造关闭 flag。

### 24.3 OOM
正式构建前做开发验证。
若 OOM：
parallel=1 开发验证；
仍不足，可由用户确认启用最多 8GiB 临时 NVMe swap；
重新冻结最终正式构建参数；
clean source tree；
重新执行正式构建。
失败尝试保留在任务记录，不包装成正式成功 Evidence。

### 24.4 SDK 结构
third_party/onnxruntime/1.23.2/linux-aarch64/
├── include/
├── lib/
├── BUILD_MANIFEST.json
├── HEADER_SHA256SUMS.txt
├── FILE_SHA256SUMS.txt
├── LICENSE
└── THIRD_PARTY_NOTICES
要求：
完整公共 headers；
实际 runtime .so；
保留真实 symlink；
保留实际 SONAME；
记录 ARM/MLAS 实际 feature；
ldd；
readelf -h/-d；
runtime version；
library/header SHA。
应用必须在：
env -u LD_LIBRARY_PATH
条件下运行 smoke 成功，证明 RPATH 指向 Stage J SDK。

## 25. J3 回归与 Sanitizer

### 25.1 Release 回归
x86 Release
用于证明：
v1兼容；
-历史M5行为未破坏；
-新增v2没有污染历史路径。
要求：
Model Smoke OFF：portable_required全部PASS
Model Smoke ON：全部适用测试PASS
Jetson Release
使用 aarch64 ORT SDK：
Model Smoke OFF：portable_required全部PASS
Model Smoke ON：全部Jetson适用测试PASS
不得只按测试数量判断，必须比较冻结测试名称清单。
测试分类：
portable_required
model_asset_required
x86_only
jetson_only
sanitizer_required

### 25.2 Sanitizer
显式 CMake 选项：
EDGE_AI_ENABLE_ASAN
EDGE_AI_ENABLE_UBSAN
分别在 Jetson 上构建并执行。
硬 Gate：
ASan：model-independent portable C++ tests PASS
UBSan：model-independent portable C++ tests PASS
真实模型、正式 benchmark 和 stability 不要求 sanitizer。
只有明确的编译器、runtime或系统库证据才允许提出人工豁免。不能将普通配置错误标记为环境不支持。

## 26. Attempt 与 Evidence

### 26.1 Attempt
路径：
local_attempts/stage_j/<attempt_id>/
规则：
git-ignored；
不可覆盖；
保存原始命令、日志、失败原因和 local manifest；
至少保留到 J9 和外部备份完成。

### 26.2 Published Evidence
路径：
results/.../<evidence_id>/
只能来自：
一个完整PASS attempt或campaign
禁止：
拼接多个 attempt；
发布失败 campaign 的部分 run；
patch 旧 Evidence；
覆盖旧 Evidence。

### 26.3 Attempt Registry
Tracked位置：
results/consolidation/stage_j/<evidence_id>/attempt_registry.json
记录：
attempt ID；
attempt type；
status；
failure category；
source commit；
local manifest SHA；
superseded attempt；
triggered full rerun；
published evidence ID。
失败 attempt 的大型原始日志不进入 Git，但不得在 J9 和外部备份完成前删除。

## 27. Evidence 路径与预算
results/platform/jetson/environment/<evidence_id>/

results/build/onnxruntime_aarch64/<evidence_id>/

results/validation/jetson_ort_level_a/<evidence_id>/
results/validation/jetson_ort_level_b/<evidence_id>/
results/validation/jetson_ort_level_c/<evidence_id>/

results/benchmark/jetson_ort_cpu/python_reference/<evidence_id>/
results/benchmark/jetson_ort_cpu/profile_precheck/<evidence_id>/
results/benchmark/jetson_ort_cpu/profile_selection/<evidence_id>/
results/benchmark/jetson_ort_cpu/controlled_1t/<evidence_id>/
results/benchmark/jetson_ort_cpu/tuned/<evidence_id>/

results/stability/jetson_ort_cpu/tuned_30min/<evidence_id>/

results/consolidation/stage_j/<evidence_id>/

results/audit/stage_j_deep_gate/<evidence_id>/
Tracked Evidence 总量：
<= 25 MiB
建议预算：

| Evidence | 预算 |
| --- | --- |
| Environment | 1 MiB |
| Level A/B/C | 3 MiB |
| Profile selection与precheck | 4 MiB |
| Controlled 1T | 4 MiB |
| Tuned CPU | 4 MiB |
| Stability | 5 MiB |
| Consolidation | 2 MiB |
| Deep Gate与Reserve | 2 MiB |
| 总计 | 25 MiB |


不得通过删除关键 Evidence、失败信息索引或异常 run 记录满足限制。
正式运行前必须使用 development smoke 预估输出体积。

## 28. J7 Consolidation

### 28.1 Commit 角色
source_commit
evidence_commit
consolidation_source_commit
consolidation_commit
每套 Evidence 分别记录自己的 source/evidence commit关系。
Evidence 不回填尚不存在的 evidence commit SHA。
由 Consolidation index 建立关系。

### 28.2 固定文件
README.txt
evidence_index.json
verification_report.json
attempt_registry.json
provenance.json
commands.txt
sha256sums.txt

### 28.3 必检关系
commit ancestry；
模型和 contract SHA；
ORT SHA；
binary SHA；
RuntimeConfig SHA；
Resolved Protocol SHA；
J1 platform；
J4 A/B/C；
20图 Python Reference；
每 Profile expected SHA；
selection；
Controlled/Tuned formal；
stability；
nvpmodel/clocks/fan；
environment drift；
OC/UV；
attempt完整性；
当前 retention状态；
隐私和资产政策。
J7 允许运行 Consolidation 自校验，但不替代 J8 的独立重建审计。

### 28.4 `sha256sums.txt` 确定性生成规则

- `sha256sums.txt` 不包含自身；
- 输入文件按 repo-relative UTF-8 path byte order 排序；
- 输出行格式固定为 `<sha256><two spaces><relative_path>`；
- 行尾固定为 LF；
- 不允许绝对路径；
- 不允许 generated timestamp、PID、hostname 或无序 mapping 影响 byte-identical 重建。

## 29. J8 Deep Evidence Gate

### 29.1 性质
只读独立审计
“只读”含义：
不修改 J1～J7 Existing Evidence；
不 patch Consolidation；
不重新跑正式 benchmark；
不放宽容差。
J8 可以在新的不可变目录中生成独立审计输出：
results/audit/stage_j_deep_gate/<evidence_id>/
固定文件：
README.txt
deep_gate_report.json
reconstruction_report.json
provenance.json
commands.txt
sha256sums.txt
J8 FAIL 时不得进入 J9。
必须创建新的 remediation source commit和新的 Evidence ID，不能继续使用原失败 Evidence。

### 29.2 可重建文件
从 raw 输入确定性派生，要求 byte-identical：
J4 canonical payload；
Level A/B/C report；
Level B diagnostics；
20图 Python Reference canonical payload；
Profile precheck report；
per-run summaries；
aggregate/pooled summary；
telemetry summary；
Profile selection result；
precheck cycle SHA；
audit cycle SHA；
stability summary；
front/back 20% summary；
evidence index；
verification report；
-各Evidence sha256sums.txt。
要求 byte-identical 的文件禁止包含：
generated timestamp；
PID；
hostname；
-绝对路径；
-无序 mapping。

### 29.3 Raw 文件
只做：
SHA + strict parse + schema
包括：
raw tensor；
raw detections；
timing trace；
application raw JSON；
tegrastats；
affinity samples；
OC/UV；
interrupts；
run journal；
environment raw。

### 29.4 Cycle Hash 限制
Deep Gate：
从两个 precheck payload重算 expected SHA；
从 first/middle/last audit payload重算对应 SHA；
其他 cycle 仅验证 manifest hash 等于 expected；
验证 cycle index 连续、frame count=20、counts一致。
禁止声称：
所有稳定性 cycle hash 都已离线重建。

正确表述：
所有 cycle 的运行期 canonical hash 均与 expected 一致；first/middle/last 代表 cycle 通过保存的 canonical payload完成了独立重算。

### 29.5 `sha256sums.txt` 独立重建规则

J8 重建 `sha256sums.txt` 时必须执行第 28.4 节的相同合同：清单不包含自身；输入按 repo-relative UTF-8 path byte order 排序；每行固定为 `<sha256><two spaces><relative_path>` 并以 LF 结尾；不得使用绝对路径；generated timestamp、PID、hostname 或无序 mapping 不得影响 byte-identical 重建。


## 30. PASS/FAIL 矩阵

| 里程碑 | PASS 核心条件 | FAIL / BLOCKED 条件 |
| --- | --- | --- |
| J0 | 冻结计划、Decision、任务卡、Git起点和测试清单完成 | 文档冲突、HEAD或工作区不满足 |
| J1 | 正确设备、NVMe、JP/L4T、MAXN_SUPER、供电和风扇正常 | MAXN_SUPER无法恢复、硬件或系统异常 |
| J2 | 官方v1.23.2源码构建、SDK manifest、SHA、RPATH smoke通过 | 来源不可信、构建配置不明、动态库加载错误 |
| J3 | x86/Jetson Release回归、v1兼容、ASan/UBSan通过 | 测试缺失、v1行为变化、sanitizer硬错误 |
| J4 | Level A/B/C全部PASS、raw和canonical确定性PASS | 任一Level失败或输出不确定 |
| J5.1 | 20图Python Reference两次一致且provenance完整 | Reference或corpus不一致 |
| J5.2 | 所有候选自身确定且20/20语义PASS | 任一候选失败 |
| J5.3 | 所有候选Sizing有效并冻结measured frames | cycle SHA、timeline、telemetry等失败 |
| J5.4 | 完整平衡Selection Campaign有效并选出Profile | 任一selection run无效或campaign被拼接 |
| J5.5 | Controlled五run完整PASS，或与Tuned同Profile时建立合法共享引用 | 任一run无效 |
| J5.6 | Tuned五run完整PASS，或与Controlled同Profile时建立合法共享引用 | 任一run无效 |
| J5.7 | J5 Reference、precheck、selection、两套角色和Evidence关系全部通过 | 语义、统计、SHA或Evidence关系错误 |
| J6 | 30分钟、全部cycle SHA、telemetry、频率和内存PASS | crash、漂移、OC/UV、持续退化或不足30分钟 |
| J7 | Consolidation索引、自校验、SHA和attempt关系通过 | Evidence关系错误、输入缺失或不可解析 |
| J8 | 独立重建、byte comparison、raw parse和Deep Gate全部PASS | 任一独立Gate失败 |
| J9 | 仅修改允许文档，记录结论、限制和归档状态 | 修改production/Evidence、J8未PASS或备份未完成 |



## 31. Git 策略
J0 通过后从：
main
创建：
feature/jetson-onnxruntime
规则：
每个里程碑从 clean committed HEAD 开始；
实现与正式 Evidence 分开提交；
Evidence ID 基于正式运行 source commit；
Agent 禁止 push；
不 squash M5；
不修改历史 Evidence；
J8 不修改既有 Evidence；
J9 后由用户手工合并和 Tag。
建议 Tag：
stage-j-jetson-ort-cpu-baselines-v1
Tag 和 push 由用户手工执行。

## 32. J9 Closeout

### 32.1 必须修改的文档
docs/personal/STAGE_J_EXECUTION_PLAN.md
docs/personal/TASKS.md
docs/personal/DECISIONS.md

### 32.2 条件更新文档
仅当这些文档当前包含阶段状态、实验路线或环境事实时更新：
README.md
docs/personal/EXPERIMENT_PLAN.md
docs/personal/ENVIRONMENT.md
J0任务卡必须根据实际仓库路径确认准确文件名。

### 32.3 禁止修改
J9禁止修改：
production C++；
Python实现工具；
CMake逻辑；
RuntimeConfig schema；
-正式 raw Evidence；
Consolidation；
J8审计Evidence；
-测试阈值。
J9 完成后的最终目标状态（不是 J0.1 当前状态）：
J0 COMPLETE
J1 COMPLETE
J2 COMPLETE
J3 COMPLETE
J4 COMPLETE
J5 COMPLETE
J6 COMPLETE
J7 COMPLETE
J8 PASS
J9 COMPLETE
STAGE J CLOSED
Closeout 必须记录：
设备和 JetPack/L4T；
ORT 来源和构建；
Level A/B/C；
Controlled/Tuned CPU Profile；
-线程选择结论；
-五run结果；
-30分钟稳定性；
-温度、频率和 rail telemetry；
-OC/UV；
-Evidence；
-Deep Gate；
-失败attempt归档和备份状态；
-限制；
-Stage T 尚未开始。

## 33. 结论边界
Stage J 可以证明：
Jetson aarch64 上 C++ ONNX Runtime CPU Serial 应用正确运行；
预处理、raw inference 和最终检测在冻结 Gate 内一致；
当前 workload 下 Controlled 1-Core 和 Tuned k-Core CPU 性能；
受控 MAXN_SUPER 条件下的温度、频率和板载 rail telemetry；
Tuned Profile 30分钟受控持续运行结果。
Stage J 不证明：
TensorRT 性能；
Jetson 最终性能；
Pipeline 性能；
生产实时能力；
长期生产稳定性；
外部整机功耗；
跨设备 speedup；
普遍最优 CPU 线程数。
WSL 与 Jetson：
只做环境差异描述
不计算正式speedup
Stage T 才进行：
同一Jetson
同一模型
同一corpus
同一功耗/时钟/风扇Profile
相同Trace instrumentation和统计定义

ORT CPU Tuned
vs
TensorRT FP16

## 34. 冻结结论与下一步
开放式方案审查：CLOSED

Stage J总体路线：FROZEN

Stage J Plan v0.3：FROZEN

最终一致性审查：PASS

下一步：
执行J0 Planning Freeze任务

J0完成后：
从main创建feature/jetson-onnxruntime

随后：
等待设备到货并进入J1
未经正式 Decision，不得改变：
Stage J 范围；
-里程碑编号；
-RuntimeConfig与Protocol权威关系；
-J4/J5语义Gate；
-Profile选择规则；
-Thermal/Telemetry合同；
-Evidence和Deep Gate边界。

## 35. 模型与推理强度建议
J0/J1/J2规划、Gate审查与Evidence审查：
GPT-5.6 Sol
Reasoning：High

常规代码实现、测试补充和文档更新：
GPT-5.6 Terra
Reasoning：Medium

复杂失败定位、跨架构数值问题或Evidence矛盾：
GPT-5.6 Sol
Reasoning：High
