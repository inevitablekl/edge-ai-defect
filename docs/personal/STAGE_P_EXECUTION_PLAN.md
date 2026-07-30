# Stage P Execution Plan v1.2 FINAL

Jetson TensorRT Bounded Pipeline Runtime and Video Input
Jetson TensorRT 有界流水线运行时与视频输入

## v1.2 execution-contract normalization authority

本 v1.2 完整保留 v1.1 的第 1—35 节及其技术路线，只整合 execution-contract
normalization；路线不变：4 workers、3 bounded SPSC queues、single inference
worker、maximum concurrent `engine.run() = 1`、TensorRT-only RuntimeConfig v4、
`drop_policy = block`、DirectorySource + VideoFileSource、canonical exact
Detection identity、queue capacity pilot 1/2/4、formal 3-pair benchmark、1.10×
material-throughput classification、30-minute Pipeline stability，以及 P0→P8
授权链。

以下 normalization 与第 1—35 节具有同等且更具体的执行约束；若 v1.1 原文存在
更宽泛表述，以本节的精确合同为准，但不得据此改变路线。

### N1. CanonicalHashSink scope contract

`CanonicalHashSink` supports `RUN`、`CYCLE`、`RUN_AND_CYCLE`。
`RUN_AND_CYCLE` 必须维护两个相互独立的 canonical byte streams：

```text
RUN stream:   canonical_scope = 1
CYCLE stream: canonical_scope = 2
```

不得拼接两个域后只计算一个 SHA。P4 使用 `RUN_AND_CYCLE`；P5 pilot 与 formal
均使用 `RUN_AND_CYCLE`，pilot Gate 只用 complete CYCLE hashes 与 P4 expected
CYCLE SHA 比较；P6 使用 `RUN`；P7 使用 `CYCLE`。Partial cycle 必须记录
frame count 和 partial digest 状态，不得与完整 180-frame expected CYCLE SHA
比较或伪造完整 cycle PASS。

### N2. source_frames, EOS, and empty input

`source_frames` 是 successful run 中 successfully returned non-EOS frames 的
数量。final EOS probe、failed source call、source-only EOS trace、cancelled
pending item、discarded post-cancellation output 均不计入。block-only successful
run 必须满足 `source_frames == processed_images`。

保留 SerialRunner 语义：first accepted frame 之前 immediate EOS 为 run failure。
P3 empty-source 测试必须证明 Serial/Pipeline 一致：`begin_run` 可已成功，source
只 probe 一次，无 frame processed，`end_run` 不调用，caller summary unchanged，
不得伪造 `run_processing_wall_ms`，不得创建成功的零帧 Result JSON v3。

### N3. WSL v4 smoke evidence boundary

WSL、`EDGE_AI_ENABLE_TENSORRT=OFF` 的 v4 Serial/Pipeline smoke 只能是使用 fake
engine 的 component-level 或 internal application-seam smoke。它只证明 v4 metadata
construction、Serial/Pipeline dispatch、component ownership、runner integration 和
Result v3 synthetic behavior；不得声称 real TensorRT production v4 CLI PASS。首次
真实 TensorRT production CLI v4 Serial/Pipeline end-to-end smoke 位于 P4 Jetson。
如需覆盖 thread creation partial failure 或 component injection，只允许最小
internal/test seam，不建设 public DI framework、thread pool 或 plugin registry。

### N4. VideoFileSource identity and codec evidence

```text
video_filename = video_path.filename().generic_u8string()
relative_path = <video_filename>/frame_<zero-padded minimum width 6 index>
example = frozen_test_video.avi/frame_000000
```

`max_frames` 只作为 VideoFileSource constructor/test/experiment control，不新增
RuntimeConfig v4 `input.max_frames`；P6 formal run 不设置 frame limit。
`CAP_PROP_FPS`、`CAP_PROP_FRAME_COUNT`、requested FourCC、可用时 observed
FourCC、decoded/expected frame count 与 resolution 只写 P6 asset/codec sidecar。
Nominal FPS 仅为 descriptive metadata，不是 pacing/timing authority，也不是
production Result JSON v3 字段。WSL codec smoke 只是非正式能力检查；正式 asset
生成与 codec preflight 平台固定为 Jetson。WSL 缺少 MJPG encoder 但 Jetson preflight
通过，不构成 P6 全局失败；Jetson MJPG preflight 失败则
`P6_BLOCKED_CODEC_PREFLIGHT`，不得静默换 codec、引入 GStreamer 或扩 scope。

### N5. P6 entry dependency

所有 Gate/Authorization 统一为：P6 仅在 P5 queue capacity 已 selected and frozen，
并且 P5 formal benchmark protocol complete 后授权。严格链为
`P4 → P5 complete → P6`。

### N6. Trace callback/write failure semantics

任何 `IFrameTraceObserver` callback failure 都是 first error：store first error、
cancel all queues、join all workers、不得调用 `end_run`，caller summary unchanged。
`BUFFERED_RECORDS` 在 runner 成功后写 trace 失败时，该 Evidence attempt invalid，
sidecar 不得作为 valid 发布；已 atomic committed 的 production JSON 不回滚，且必须
披露失败。

### N7. Canonical exact identity and measured-window clarification

Stage P exact identity 是同一 accepted FP16 Engine 与同一 pre/postprocess 语义下，
不同 runtime scheduling 的最终 Detection identity；D066 的 raw TensorRT Level B
`FAIL — retained known limitation` 保持不变。P5 measured-window throughput 只以
完整 frame 100—5099 的 trace 边界计算；EOS/source-only 或不完整 lifecycle 不进入
5000-frame measured statistics。

Stage P Execution Plan v1.2 FINAL
Jetson TensorRT Bounded Pipeline Runtime and Video Input
Jetson TensorRT 有界流水线运行时与视频输入
文档状态：
PROJECT_AI_CONSISTENCY_CHECK:
PASS_WITH_EXECUTION_CONTRACT_NORMALIZATIONS_INTEGRATED

Stage P Plan:
FINAL

P0 Planning Freeze:
COMPLETE_AT_THE_COMMIT_CONTAINING_THIS_CHANGESET

P1:
NOT_AUTHORIZED_UNTIL_P0_COMMIT_IS_REVIEWED

Production implementation:
NOT AUTHORIZED BEFORE P0_PASS

Jetson P4–P7 execution:
NOT AUTHORIZED BEFORE THEIR PREREQUISITE GATES
本计划不再需要第四轮架构审查。后续审查只针对具体阶段实现与 Evidence，不重新讨论四线程拓扑、Pipeline是否必做、block-only、TensorRT-only或1.10×性能分类阈值。
1. Authority and Baseline
Repository：
inevitablekl/edge-ai-defect
权威起点：
branch:
main

commit:
c6890d86e7534500cfe31c40dd73f151d77d5362
Stage K annotated tag：
stage-k-tensorrt-fp16-complete-v1.0
远端 tag ref 与上述提交当前比较结果为 identical；P0仍必须在本地验证 tag对象确实为 annotated tag，并验证 peeled commit。
P0必须满足：
local refs/heads/main
=
refs/remotes/origin/main
=
stage-k-tensorrt-fp16-complete-v1.0^{}
=
c6890d86e7534500cfe31c40dd73f151d77d5362
本地还必须验证：
git cat-file -t stage-k-tensorrt-fp16-complete-v1.0
=
tag
任一条件不满足：
P0_BLOCKED_BASELINE_OR_TAG_MISMATCH
STOP
禁止：
自动执行不受控的 git pull；
自动 fast-forward本地main；
移动、删除或重建tag；
从旧Stage K feature分支建立Stage P；
在验证前创建Stage P分支；
将旧分支上的未跟踪planning audit直接提交。
2. Stage Positioning
Stage P研究问题：
在保持同一TensorRT FP16 Engine、同一Preprocessor、同一PostProcessor和最终Detection bit-exact identity的条件下，通过固定、有界、可取消的跨帧阶段重叠，提高Jetson上的持续处理吞吐量，并补齐Video File Input。

实验自变量：
runtime scheduling:
Serial
vs
Bounded Pipeline
Stage P不重新研究：
FP32与FP16任务精度；
TensorRT raw Level B；
Engine build；
TensorRT tactic；
selective precision；
-模型训练；
ONNX导出；
-检测算法。
继承Stage K：
Original TensorRT FP16:
TASK_LEVEL_FP16_ACCEPTED

Serial stability:
K6_STABILITY_PASS

Formal serial performance:
K7_PERFORMANCE_COMPLETE

Raw Tensor Level B:
FAIL — retained known limitation
D066继续有效，其接受依据是task-level accuracy、stability和formal serial performance，不是raw tensor equality。
Stage P的exact identity只证明：
同一accepted FP16 Engine
-
同一计算语义
-
不同runtime scheduling
=
相同最终Detection
它不得被表述为FP16 raw numerical correctness已经通过。
3. Required Runtime Architecture
DirectorySource / VideoFileSource
                │
                ▼
          Source Worker
                │
       Bounded SPSC Queue 1
                │
                ▼
        Preprocess Worker
                │
       Bounded SPSC Queue 2
                │
                ▼
   Single Inference Worker
                │
       Bounded SPSC Queue 3
                │
                ▼
    Postprocess + Sink Worker
固定：
4 workers
3 bounded SPSC queues
1 TensorRT ExecutionContext
1 CUDA stream
maximum concurrent engine.run() = 1
batch = 1
CPU preprocessing
CPU postprocessing
Postprocess and Sink in the same worker
不实现可配置worker数量或独立Sink worker。
4. Scope
4.1 必须完成
Stage P Plan、Task Cards和D067–D071；
RuntimeConfig v4；
Result JSON v3；
RunMetadata/RunSummary兼容扩展；
packet和timing合同；
BoundedQueue；
OPEN/CLOSED/CANCELLED状态机；
PipelineRunner；
ConcurrentFrameTraceRecorder；
production v4 Serial/Pipeline dispatch；
DirectorySource Pipeline；
VideoFileSource；
canonical LE binary serializer/hash；
StagePExperimentRunner；
CorpusReplaySource；
CanonicalHashSink；
TimedJsonSink；
queue capacity pilot；
formal Serial/Pipeline benchmark；
30分钟Pipeline stability；
final consolidation。
4.2 明确排除
ORT Pipeline production mode
multiple TensorRT contexts
multiple CUDA inference streams
batch > 1
dynamic shape
CUDA preprocessing
GPU NMS
pinned-memory专项优化
zero-copy
INT8
DLA
camera
RTSP
DeepStream
GStreamer专项优化
ROS2 runtime
Qt GUI
thread pool
MPMC queue
lock-free queue
live drop policy
watchdog
automatic recovery
industrial certification
不得因为Pipeline收益不足而引入上述项目补救。
5. Stage P Decisions
P0追加以下Decision。
D067 — Stage P baseline, scope and execution authority
冻结：
main@c6890d86...；
Stage K annotated tag；
Stage P范围；
P0→P8授权链；
-只有P0 PASS后才允许production implementation。
D068 — Four-worker topology and single-inference boundary
冻结：
Source；
Preprocess；
single Inference；
Postprocess+Sink；
-三个bounded SPSC queues；
-最多一个并发engine.run()。
D068必须明确：
D012关于Serial+Pipeline路线的决策继续有效；D068仅取代D012理由中历史性的“三线程pipeline”实现细节，不改写D012的runtime-mode主决策。

D069 — RuntimeConfig v4, Result JSON v3 and compatibility
冻结：
RuntimeConfig v4为TensorRT-only；
Result JSON v3为独立schema；
v4映射到Result schema v3；
v1/v2/v3配置及Result v1/v2保持历史行为；
internal optional v3 metadata/summary carrier。
D070 — Exact correctness, timing and benchmark contract
冻结：
canonical LE binary；
RUN/CYCLE domain separation；
concurrent trace；
measured window；
queue pilot规则；
paired benchmark统计；
bounded-memory stability。
D071 — Offline block-only sources and deferred live-stream scope
冻结：
drop_policy=block；
Directory和Video File均无损backpressure；
camera、RTSP、drop_oldest/drop_newest和ROS2延后；
VideoFileSource为次级功能Gate。
6. RuntimeConfig v4
RuntimeConfig schema与Result JSON schema保持独立。RuntimeConfig v4通过明确桥接规则生成Result JSON v3，不因为版本号数值相近而形成通用耦合。
6.1 Pipeline Directory完整示例
schema_version: 4

backend:
  type: tensorrt_fp16

tensorrt:
  engine_path: /local/path/model.engine
  engine_manifest_path: /local/path/model.manifest.json
  device_id: 0

model:
  contract_path: /local/path/model_contract.yaml

runtime:
  mode: pipeline
  opencv_num_threads: 1
  pipeline:
    queue_capacity: 2
    drop_policy: block

input:
  type: directory
  directory: /local/path/images

output:
  json_path: /local/path/results.json
  console: false
  overwrite: false

postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680
  agnostic: false

timing:
  enabled: true
6.2 Serial Directory完整示例
schema_version: 4

backend:
  type: tensorrt_fp16

tensorrt:
  engine_path: /local/path/model.engine
  engine_manifest_path: /local/path/model.manifest.json
  device_id: 0

model:
  contract_path: /local/path/model_contract.yaml

runtime:
  mode: serial
  opencv_num_threads: 1

input:
  type: directory
  directory: /local/path/images

output:
  json_path: /local/path/results.json
  console: false
  overwrite: false

postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680
  agnostic: false

timing:
  enabled: true
6.3 Video输入
input:
  type: video_file
  video_path: /local/path/frozen_test_video.avi
6.4 Strict union
runtime.mode = serial
→ runtime.pipeline forbidden

runtime.mode = pipeline
→ runtime.pipeline required

input.type = directory
→ input.directory required
→ input.video_path forbidden

input.type = video_file
→ input.video_path required
→ input.directory forbidden

backend.type
→ exactly tensorrt_fp16

runtime.pipeline.drop_policy
→ exactly block

runtime.pipeline.queue_capacity
→ integer 1–16

timing
→ required section

timing.enabled
→ required boolean
继续要求：
unknown field fail-fast；
duplicate key fail-fast；
missing field fail-fast；
invalid union fail-fast；
relative path按现有配置目录语义解析；
v1–v3 parser regression PASS。
正式P4–P6配置使用：
output.console = false
output.overwrite = false
所有run使用唯一输出路径。
7. Runtime Metadata and Summary Carrier
当前公共IResultSink::end_run(const RunSummary&)保持不变，不引入第二套Sink接口。
7.1 RunMetadata兼容扩展
现有字段保持。
新增：
struct PipelineMetadataV3 {
    std::uint32_t queue_capacity;
    std::string drop_policy;
};

struct RuntimeMetadataV3 {
    std::string runtime_mode;   // serial | pipeline
    std::string input_type;     // directory | video_file
    std::optional<PipelineMetadataV3> pipeline;
};

struct RunMetadata {
    // existing fields unchanged
    std::optional<RuntimeMetadataV3> runtime_v3;
};
规则：
Result schema v1/v2:
runtime_v3 absent

Result schema v3:
runtime_v3 required
Pipeline模式必须有pipeline metadata；Serial必须没有。
7.2 RunSummary兼容扩展
保留现有：
processed_images
total_detections
新增：
struct PipelineSummaryV3 {
    std::array<std::size_t, 3> queue_high_water_marks;
};

struct RunSummaryV3 {
    std::size_t source_frames;
    double run_processing_wall_ms;
    std::optional<PipelineSummaryV3> pipeline;
};

struct RunSummary {
    std::size_t processed_images;
    std::size_t total_detections;
    std::optional<RunSummaryV3> runtime_v3;
};
不独立存储：
processed_frames
dropped_frames
run_processing_throughput_fps
这些值由serializer确定性派生：
processed_frames =
processed_images

dropped_frames =
source_frames - processed_images

run_processing_throughput_fps =
processed_images / (run_processing_wall_ms / 1000)
这样避免重复字段彼此漂移。
校验：
schema v1/v2：runtime_v3必须缺失；
schema v3：runtime_v3必须存在；
source_frames >= processed_images；
block-only成功run要求两者相等；
wall time必须finite且正数；
pipeline metadata和summary必须与runtime mode匹配；
-所有计数执行overflow检查。
历史v1/v2 JSON输出不得因新增默认字段而变化。
8. Result JSON v3
Result JSON v3保持现有TensorRT model、Detection、postprocess和image body语义，但使用新的runtime和summary表达。
建议固定结构：
{
  "schema_version": 3,
  "backend": {},
  "model": {},
  "runtime": {
    "mode": "pipeline",
    "input_type": "directory",
    "pipeline": {
      "queue_capacity": 2,
      "drop_policy": "block"
    }
  },
  "postprocess": {},
  "images": [],
  "summary": {
    "processed_frames": 180,
    "total_detections": 500,
    "source_frames": 180,
    "dropped_frames": 0,
    "run_processing_wall_ms": 1234.5,
    "run_processing_throughput_fps": 145.8,
    "queue_high_water_marks": {
      "source_to_preprocess": 2,
      "preprocess_to_inference": 2,
      "inference_to_postprocess": 1
    }
  }
}
Serial模式：
runtime.pipeline缺失；
queue_high_water_marks缺失。
v1/v2仍使用历史processed_images字段。v3使用processed_frames，不同时输出两个同义字段。
不进入production JSON：
formal measured-window throughput
paired speedups
paired sample SD
sink_finalize_ms
tegrastats
RSS timeline
full trace
thermal classification
experiment_source_mode
这些进入benchmark/stability sidecar。
9. Per-frame Timing Carrier
现有FrameTimings基础字段保持：
source
preprocess
inference
postprocess
pre_sink_total
新增可选Pipeline queue timing：
struct PipelineQueueTimings {
    double source_to_preprocess_wait_ms;
    double preprocess_to_inference_wait_ms;
    double inference_to_postprocess_wait_ms;
};

struct FrameTimings {
    // historical fields unchanged
    std::optional<PipelineQueueTimings> pipeline_queue;
};
校验：
Result v1/v2:
pipeline_queue absent

Result v3 Serial:
pipeline_queue absent

Result v3 Pipeline + timing.enabled=true:
pipeline_queue required
pre_sink_total在Pipeline中定义为：
source service begin
→
postprocess service end
因此包含queue residence，但不包含sink write。
Result JSON v3 Pipeline的timing_ms增加最小嵌套字段：
"queue_residence": {
  "source_to_preprocess": 0.1,
  "preprocess_to_inference": 0.2,
  "inference_to_postprocess": 0.1
}
sink_write_service_ms和完整frame pipeline latency进入trace sidecar，不回写同一FrameResult。
10. Queue Contract
三条队列均为：
bounded
single producer
single consumer
mutex + condition_variable
状态：
OPEN
CLOSED
CANCELLED
转换：
OPEN → CLOSED
OPEN → CANCELLED
CLOSED → CANCELLED
CANCELLED → terminal
CLOSED
-拒绝新push；
-继续drain已入队元素；
-drain后pop返回normal EOS；
close()幂等；
-唤醒全部waiter。
CANCELLED
-优先于CLOSED；
-拒绝push；
-pop立即返回cancelled；
-不继续drain；
-清除待处理item；
cancel()幂等；
-唤醒全部waiter。
Enqueue timestamp
Queue在item真正获得容量并发布前记录：
template <typename T>
struct DequeuedItem {
    T value;
    std::uint64_t enqueued_ns;
};
Consumer在stage service实际开始时计算：
queue residence =
service_begin_ns - enqueued_ns
Worker把该per-frame值写入下游packet，并调用queue aggregate statistics更新接口。
Queue aggregate statistics：
push_count
push_block_total_ns
residence_count
residence_total_ns
residence_max_ns
high_water_mark
final_state
remaining_items
high_water_mark不得超过capacity。
11. Cancellation and Lifecycle
Normal EOS：
Source closes Q1
Preprocess drains Q1 and closes Q2
Inference drains Q2 and closes Q3
Postprocess/Sink drains Q3 and exits
First error：
store first error once
cancel all queues
wake all workers
discard pending items
join all started workers
正在同步调用组件的worker：
allow current call to return
check cancellation
discard newly produced output
do not enqueue
exit
Orchestrator：
sink.begin_run
→ start workers
→ join workers
→ if no error: sink.end_run
→ if end_run succeeds: commit caller summary
任何失败：
caller summary unchanged
如果begin_run()失败，不启动worker。
如果部分线程创建失败：
record first error
cancel queues
join already-started threads
return failure
end_run()失败时summary不提交。
12. Thread Ownership
ImageSource:
Source Worker only

Preprocessor:
Preprocess Worker only

IInferenceEngine:
Inference Worker only

PostProcessor:
Postprocess/Sink Worker only

IResultSink:
Postprocess/Sink Worker only
允许共享：
-三个queues；
-cancellation state；
-immutable config；
-immutable ModelContract；
-concurrent recorder；
-read-only experiment contract。
禁止同一个production component被多个worker并发调用。
13. Packet Contracts
SourcePacket
sequence_index
relative_path
image_bgr
source_begin_ns
source_end_ns
PreprocessedPacket
sequence_index
relative_path
original dimensions
HostTensor input
LetterBox transform
source timestamps
queue-1 residence
preprocess timestamps
InferencePacket
sequence_index
relative_path
original dimensions
LetterBox transform
raw HostTensor output
previous timing
queue-2 residence
inference timestamps
Postprocess input
sequence_index
relative_path
original dimensions
transform
raw output
previous timing
queue-3 residence
Source identity统一为：
relative_path.generic_u8string()
不增加重复的public source_identity。
成功入队后，生产者不得修改packet或其可变数据。
14. Concurrent Trace and Measurement
历史TraceRecorder保持不变。
新增：
ConcurrentFrameTraceRecorder
继续实现现有IFrameTraceObserver。
Active key：
(global sequence index, FrameTraceStage)
支持模式：
BUFFERED_RECORDS
AGGREGATE_ONLY
BUFFERED_RECORDS
用于P4/P5：
-允许stage重叠；
-不逐record flush；
-run结束后一次写出；
Serial和Pipeline使用同一schema和buffering policy；
trace write失败使attempt无效。
AGGREGATE_ONLY
用于P7：
-不保留所有per-frame record；
-只保留stage count、sum、min、max等aggregate；
-保留active interval map；
-不生成30分钟完整trace。
每个record：
cycle_id
stage
start_ns
end_ns
duration_ns
在Stage P中：
cycle_id =
runner-assigned expected global sequence index
Source返回非EOS frame后必须验证：
ImageItem.sequence_index == cycle_id
最终EOS probe可能产生一个source-only interval。分析器只将同时具有完整accepted-frame生命周期的cycle纳入frame count和measured statistics；EOS source-only record不得计为frame。
15. Timing Definitions
Service time：
component call begin
→
component call return
包括：
source_service_ms
preprocess_service_ms
inference_service_ms
postprocess_service_ms
Queue residence：
next-stage service begin
-
queue-owned enqueued timestamp
Sink write service：
outer IResultSink composition write_frame begin
→
outer IResultSink composition write_frame return
Frame pipeline latency：
source service begin
→
outer sink composition write_frame completion
Full-run processing wall：
first accepted frame source begin
→
last successfully processed frame outer sink completion
Sink finalize：
inner JsonSink.end_run begin
→
inner JsonSink.end_run return
sink_finalize_ms只写benchmark sidecar。
16. Canonical Correctness Format
Authority：
SHA-256 over canonical little-endian binary
固定header：
magic:
8 ASCII bytes = "EAICANON"

canonical_schema_version:
uint32 LE = 1

canonical_scope:
uint32 LE
Scope：
1 = RUN
2 = CYCLE
Frame：
uint64 sequence_or_frame_index
uint32 relative_path_byte_length
UTF-8 generic relative path bytes
int32 image_width
int32 image_height
uint32 detection_count
Detection：
uint64 candidate_index
int32 class_id
uint32 confidence_bits
uint32 x1_bits
uint32 y1_bits
uint32 x2_bits
uint32 y2_bits
Trailer：
uint64 frame_count
uint64 total_detection_count
规则：
-显式LE写入；
-不得hash native struct memory；
-C++17通过memcpy提取float bits；
sizeof(float)==4；
std::numeric_limits<float>::is_iec559；
-所有float finite；
-保留+0.0/-0.0区别；
-保持Detection原始顺序；
-所有整数转换前检查范围；
-path length和detection count必须可表示为uint32。
17. Hash Scopes
RUN Hash
用于P4、P5和P6：
global sequence_index
relative_path
dimensions
ordered detections
CYCLE Hash
用于P7：
frame_index_in_cycle
corpus-relative path
dimensions
ordered detections
排除：
global sequence_index
cycle_id
timing
P4 Serial 180-frame结果同时生成：
RUN expected SHA；
CYCLE expected SHA。
P7每个完整cycle必须匹配P4冻结的CYCLE expected SHA。
18. Production and Experiment Composition
提取一个最小共享入口：
application::run_with_components(
    const RuntimeConfig& config,
    ImageSource& source,
    IResultSink& sink,
    const RunOptions& options);
或语义等价的internal API。
该入口负责复用：
OpenCV thread policy；
ModelContract loader；
TensorRT Manifest loader；
Engine factory；
Preprocessor；
PostProcessor；
SerialRunner/PipelineRunner选择；
metadata construction。
Production ApplicationRunner：
creates DirectorySource / VideoFileSource
creates JsonSink
calls run_with_components()
Experiment runner：
creates DirectorySource / VideoFileSource / CorpusReplaySource
creates experiment Sink composition
creates trace recorder
calls the same run_with_components()
冻结experiment-only executable：
stage_p_experiment_runner
它不进入production CLI，不扩展RuntimeConfig source/sink registry，不建设通用DI framework。
P5/P7 sidecar必须记录：
experiment_source_mode = corpus_replay
cycle_length = 180
production Result JSON的input_type仍表示底层资产类型：
directory
19. Sink Composition
统一名称：
TimedJsonSink
它是benchmark-only decorator，包装JsonSink，只测量inner end_run()时间并把结果保存在内存中供experiment runner写sidecar。
P4/P5/P6正式exact run的CompositeSink：
write order:
1. TimedJsonSink
2. CanonicalHashSink

end order:
1. CanonicalHashSink
2. TimedJsonSink / inner JsonSink
当前CompositeSink已经支持逆序end_run()，不得为Stage P修改这一公共语义。
结果：
hash finalize失败时JSON尚未atomic commit；
JsonSink commit是最终production commit点；
Serial/Pipeline使用相同composition；
sidecar在整个run成功后写出；
sidecar写失败使Evidence attempt无效，但不回写已提交JSON。
P7只使用：
CanonicalHashSink
20. Build and Test Inventory
20.1 Thread dependency
P2前增加：
find_package(Threads REQUIRED)
edge_ai_runtime或承载PipelineRunner的target显式链接：
Threads::Threads
20.2 Video dependency
P6增加OpenCV component：
find_package(
    OpenCV 4 REQUIRED
    COMPONENTS core imgproc imgcodecs videoio
)
并链接：
opencv_videoio
20.3 Existing tests to extend
test_runtime_config.cpp
test_runtime_types.cpp
test_result_sinks.cpp
test_serial_runner.cpp
test_application_smoke.py
这些测试目标当前已经存在于CMake inventory。
20.4 New focused tests
最多新增：
test_concurrent_frame_trace
test_canonical_detection_hash
test_bounded_queue
test_pipeline_runner
test_corpus_replay_source
test_video_file_source
test_stage_p_experiment_runner
不拆成大量微型test targets。
20.5 Platform matrix
WSL：
EDGE_AI_ENABLE_TENSORRT=OFF
backend-neutral build
fake-engine unit tests
RuntimeConfig/Result/Queue/Pipeline tests
v4 Serial/Pipeline smoke仅为fake-engine component-level或internal application-seam smoke；
只证明v4 metadata construction、Serial/Pipeline dispatch、component ownership、
runner integration和Result v3 synthetic behavior，不得声明real TensorRT production v4 CLI PASS。
首次真实TensorRT production CLI v4 Serial/Pipeline end-to-end smoke位于P4 Jetson。
thread creation partial failure或application component injection仅允许最小internal/test seam，
不得建设public DI framework、thread pool或plugin registry
Jetson：
EDGE_AI_ENABLE_TENSORRT=ON
real Engine smoke
P4–P7 execution
videoio codec preflight
TensorRT OFF build必须继续编译全部backend-neutral Stage P代码。
21. Shared-semantics Preflight
Serial和Pipeline配置分别记录自己的exact config SHA。
允许差异：
runtime.mode
runtime.pipeline section
output.json_path
trace path
telemetry path
sidecar path
run ID
必须一致：
schema_version = 4
backend.type
Engine content SHA
Manifest content SHA
ModelContract content SHA
input corpus / manifest identity
postprocess values
OpenCV thread count
timing.enabled
console policy
overwrite policy
experiment source mode
cycle length
Sink implementation
serializer semantics
decorator composition
P4/P5/P6生成machine-readable：
shared_semantics_preflight.json
preflight失败时禁止使用该run形成正式比较。
22. CorpusReplaySource
Experiment-only。
输入：
Stage K frozen 180-image test manifest
属性：
deterministic order；
-global sequence单调；
-cycle length 180；
cycle_id = sequence_index / 180；
frame_index_in_cycle = sequence_index % 180；
-默认每cycle重新decode；
-不默认缓存完整decoded corpus；
-不重建Runner；
fixed-frame mode；
minimum-duration mode。
P5 formal：
warmup:
0–99

measured:
100–5099

total accepted frames:
5100
P5 pilot：
warmup:
0–99

measured:
100–1099

total accepted frames:
1100
固定帧模式结束后，Source执行一次正常EOS返回；EOS probe不计入accepted frame count。
23. P0 — Planning Freeze and Baseline Authority
执行环境：
WSL Codex
Actions
git fetch origin --prune；
git fetch origin --tags；
3.检查旧未跟踪planning audit：
   -不得提交；
   -如需保留，移动到repo外本地evidence目录并记录SHA；
   -清理后worktree和index必须clean；
4.验证local main、origin/main、annotated tag和baseline；
5.确认feature/jetson-pipeline-runtime不存在；
6.从exact baseline创建：
feature/jetson-pipeline-runtime
7.写入：
docs/personal/STAGE_P_EXECUTION_PLAN.md
docs/personal/STAGE_P_TASK_CARDS.md
docs/personal/STAGE_P_BASELINE_REPORT.md
8.追加D067–D071；
9.更新：
docs/PROJECT_BRIEF.md
docs/REQUIREMENTS.md
docs/ARCHITECTURE.md
docs/personal/TASKS.md
docs/personal/EXPERIMENT_PLAN.md
   -必要的README.md当前阶段说明；
10.记录当前CMake target和relevant test inventory；
11.不修改source、CMake、config schema或tests；
12.创建P0 freeze commit；
13.验证commit后worktree clean。
建议commit：
docs(stage-p): freeze bounded pipeline execution plan
Gate
P0_PASS
失败状态：
P0_BLOCKED_BASELINE_OR_TAG_MISMATCH
P0_BLOCKED_DIRTY_WORKTREE
P0_BLOCKED_EXISTING_STAGE_P_BRANCH
P0_BLOCKED_DECISION_CONFLICT
P0_BLOCKED_PLAN_INCONSISTENCY
P0期间禁止push、merge和tag。
24. P1 — Contract Implementation
执行环境：
WSL Codex
实现：
RuntimeConfig v4；
strict union；
RunMetadata v3 carrier；
RunSummary v3 carrier；
Result JSON v3；
per-frame optional pipeline queue timing；
packet/timing types；
canonical serializer；
RUN/CYCLE hash；
ConcurrentFrameTraceRecorder；
shared run_with_components() serial seam；
focused tests。
P1不实现：
BoundedQueue；
worker threads；
PipelineRunner；
CorpusReplaySource；
Jetson experiment。
Gate：
P1_CONTRACT_IMPLEMENTATION_PASS
必须证明：
v1/v2/v3 config regression；
Result v1/v2 regression；
v3 Serial/Pipeline synthetic serialization；
strict field union；
canonical fixed test vector；
+0/-0区分；
NaN/Inf拒绝；
RUN/CYCLE domain separation；
overlapping trace intervals；
EOS source-only trace不会被计为完整frame。
25. P2 — Bounded Queue and Cancellation
执行环境：
WSL Codex
实现和测试：
BoundedQueue；
Queue-owned enqueue timestamp；
OPEN/CLOSED/CANCELLED；
producer/consumer blocking；
normal drain；
cancellation dominance；
first-error state；
high-water mark；
residence aggregate；
partial thread start protection；
stress and join。
必须覆盖：
FIFO；
capacity边界；
producer阻塞；
consumer阻塞；
close后drain；
close幂等；
cancel清空并终止；
CLOSED→CANCELLED；
cancel唤醒所有waiter；
first error只保存一次；
residence timestamp有效；
high-water不越界；
repeated stress；
14.所有线程join。
TSan：
OPTIONAL_IF_AVAILABLE
Gate：
P2_QUEUE_PRIMITIVES_PASS
26. P3 — Pipeline and Experiment Integration
执行环境：
WSL Codex
实现：
fixed four-worker PipelineRunner；
normal close propagation；
first-error cancellation；
component ownership；
worker join；
atomic summary；
v4 Serial/Pipeline dispatch；
DirectorySource Pipeline；
StagePExperimentRunner；
CorpusReplaySource；
CanonicalHashSink；
TimedJsonSink；
queue statistics；
fake failure tests；
CMake Threads integration。
测试：
normal EOS；
empty source；
source/preprocess/inference/postprocess/sink failure；
begin_run/end_run failure；
partial thread creation failure；
cancel during active service；
no enqueue after cancel；
summary unchanged on failure；
end_run only on success；
FIFO exact；
concurrent Engine call maximum=1；
final queue states；
v4 Serial smoke；
v4 Pipeline smoke；
v1-v3 application regression；
replay exact 1100/5100 count。
Gate：
P3_PIPELINE_IMPLEMENTATION_PASS
P2和P3可以位于同一开发迭代，但P4前必须有clean committed source HEAD。
27. P4 — Jetson Exact Correctness
执行环境：
Jetson Codex
前提：
P3_PIPELINE_IMPLEMENTATION_PASS
对象：
Original TensorRT FP16 Engine
SHA256:
6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc
输入：
Stage K frozen 180-image test split
manifest SHA256:
fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8
配置：
RuntimeConfig v4
queue_capacity = 2
drop_policy = block
timing.enabled = true
先执行最小production CLI Serial/Pipeline smoke，验证v4 application composition。
正式run通过StagePExperimentRunner执行：
Serial ×1
Pipeline ×3
每个run：
-唯一config；
-唯一JSON；
-唯一trace；
-唯一sidecar；
-唯一run ID；
config SHA；
executable SHA；
Engine/Manifest/Contract SHA；
shared-semantics preflight。
Gate：
180/180 accepted
180/180 processed
dropped = 0
finite
sequence exact
relative_path exact
four RUN SHA values identical
Pipeline workers joined
Pipeline queues CLOSED and drained
no queue CANCELLED
冻结：
expected RUN SHA
expected CYCLE SHA
Verdict：
P4_PIPELINE_CORRECTNESS_PASS
P4_INVESTIGATION_REQUIRED
P4_PIPELINE_CORRECTNESS_FAIL
P4未PASS，不得进入P5。
28. P5 — Queue Pilot and Formal Benchmark
执行环境：
Jetson Codex
28.1 Environment control
记录：
MAXN_SUPER
jetson_clocks
fan policy
process CPU affinity
OpenCV threads = 1
JetPack/L4T
CUDA
TensorRT
Engine SHA
executable SHA
start/end temperature
tegrastats
thermal/throttle probes
不使用per-worker affinity。
若权威throttle接口可用且发现throttling：
RUN_INVALID_THERMAL_THROTTLING
保留attempt，人工cooldown后重跑。
若接口不可用：
thermal_throttle_status = unavailable
保留探测命令和输出，不声称“无throttling PASS”；run可以继续，但最终报告必须保留该限制。
28.2 Queue pilot
容量：
1
2
4
每个capacity：
one independent process
100 warmup
1000 measured
1100 accepted frames
single Pipeline lifecycle
CorpusReplaySource
same Sink composition
buffered trace
有效配置要求：
exact cycle hashes；
drop=0；
-finite；
-no crash/deadlock；
-no thermal invalidation；
-measured trace count=1000。
选择：
best =
highest measured throughput

eligible =
throughput >= 0.95 × best

selected =
smallest queue capacity in eligible
P95只报告，不参与选择。
正式benchmark后禁止改选。
28.3 Formal benchmark
两组都使用：
RuntimeConfig v4
CorpusReplaySource
TimedJsonSink + CanonicalHashSink
ConcurrentFrameTraceRecorder BUFFERED_RECORDS
5100 accepted frames
运行顺序：
Pair 1:
Serial → Pipeline

Pair 2:
Pipeline → Serial

Pair 3:
Serial → Pipeline
每个process：
warmup:
0–99

measured:
100–5099

accepted total:
5100
正式throughput：
5000 /
(
last complete frame 5099 outer sink end
-
complete frame 100 source begin
)
要求：
Source不接受sequence 5100；
-EOS source-only trace不计入frame；
complete measured traces正好5000；
all six RUN hashes一致；
complete cycle hashes匹配P4 expected；
no outlier removal；
invalid attempts单独保留。
Paired ratio定义：
pipeline_throughput_fps
/
serial_throughput_fps
Primary：
6个run throughput；
3个paired ratios；
paired-ratio arithmetic mean；
sample SD，n-1；
3对方向。
Secondary：
frame latency P50/P95/P99；
-stage service P50/P95/P99；
-queue residence P50/P95/P99；
-inference service；
-sink write service；
-sink finalize；
-queue push blocking；
-high-water marks；
-RAM/CPU/GPU/EMC/temperature。
Percentile采用Type-7线性插值。Pooled 15000-frame分布只作描述性结果。
分类：
mean paired ratio >= 1.10
→ MATERIAL_MEASURED_THROUGHPUT_INCREASE

0.95 <= mean paired ratio < 1.10
→ NO_MATERIAL_MEASURED_CHANGE

mean paired ratio < 0.95
→ MEASURED_THROUGHPUT_REGRESSION
不得称为统计显著性。
Result JSON中的run_processing_throughput_fps覆盖完整5100-frame run，只作描述性指标，不替代formal 5000-frame measured throughput。
29. P6 — VideoFileSource
执行环境：
WSL Codex:
implementation and codec smoke

Jetson Codex:
formal validation
Entry dependency:
P5 queue capacity has been selected and frozen
AND
P5 formal benchmark protocol is complete
实现：
cv::VideoCapture；
-zero-based frame index；
-width/height；
-nominal FPS metadata；
-normal EOF；
-decode error fail-fast；
-optional max frames；
-deterministic relative path：
<video-basename>/frame_000000
P6加入CMake OpenCV videoio依赖。
source identity冻结为：
video_filename = video_path.filename().generic_u8string()
relative_path = <video_filename>/frame_<zero-padded minimum width 6 index>
例如：frozen_test_video.avi/frame_000000
max_frames仅为VideoFileSource constructor/test/experiment control，不得新增RuntimeConfig v4 input.max_frames。
P6 formal run不设置frame limit。Nominal FPS只作为descriptive metadata，不是pacing authority、
timing authority或production Result JSON v3字段。
Codec preflight
VideoWriter opens requested codec
→ write and close
→ VideoCapture reopens
→ decode complete file
→ record expected source count
→ record decoded count
→ record CAP_PROP_FRAME_COUNT
→ record requested codec
→ record observed FourCC when available
建议：
MJPG AVI
如MJPG不可用：
P6_BLOCKED_CODEC_PREFLIGHT
不得静默替换codec。
正式视频只表示：
一次生成成功后冻结SHA的本地测试资产
不声称跨OpenCV或codec环境重新生成时byte-identical。
仓库不提交视频。
正式资产记录：
video SHA；
source image manifest SHA；
-generation command；
-requested codec；
-observed codec；
-resolution；
-expected generated frame count；
-decoded frame count；
-reported frame count。
正式Gate以：
decoded frame count
=
expected generated frame count
为准。容器reported count只作描述性数据。
Formal validation
使用P5选择的queue capacity。
先执行production CLI Video Serial/Pipeline smoke。
正式exact run通过StagePExperimentRunner执行：
same frozen video
Serial ×1
Pipeline ×1
Gate：
decoded count exact；
-frame index连续；
-relative path连续；
-width/height exact；
-EOS normal；
-decode error=0；
-drop=0；
-finite；
-Serial/Pipeline RUN SHA exact；
-Result JSON v3成功；
-Pipeline queues CLOSED and drained。
不得比较：
directory source pixels
vs
decoded video pixels
也不得比较directory detections与video detections。
Verdict：
P6_VIDEO_SOURCE_PASS
P6_VIDEO_SOURCE_FAIL
P6_BLOCKED_CODEC_PREFLIGHT
30. P7 — Pipeline Stability
执行环境：
Jetson Codex
配置：
TensorRT FP16 Pipeline
P5 selected capacity
drop_policy = block
CorpusReplaySource
CanonicalHashSink
ConcurrentFrameTraceRecorder AGGREGATE_ONLY
协议：
one Pipeline lifecycle
source replay active duration >= 1800 seconds
Source行为：
record first source-service begin
→ replay frames
→ when monotonic elapsed reaches 1800 seconds,
  finish current source item decision
→ return normal EOS at next source boundary
→ Pipeline drains normally
因此：
source replay active duration >= 1800 s
total runner duration >= source replay active duration
不使用JsonSink，不保留完整per-frame trace或完整Detection列表。
Gate：
crash = 0
deadlock = 0
non-finite = 0
inference error = 0
drop = 0
source_frames = processed_frames
all complete CYCLE SHA match P4 expected
global sequence monotonic
all workers joined

Q1 = CLOSED and drained
Q2 = CLOSED and drained
Q3 = CLOSED and drained
no queue = CANCELLED

high-water <= selected capacity
remaining queue items = 0
最终partial cycle：
-记录frame count；
-不参与complete-cycle Gate；
-其中accepted frames仍必须processed。
系统记录：
tegrastats；
-RSS；
-stage aggregates；
-queue aggregates；
-temperature；
-throttle probe；
-first/last identity；
-total frames；
-complete cycle count；
-partial cycle count。
内存判断继承Stage K稳定性方法：
-允许启动期allocator增长；
-允许正常RSS波动；
-不制定工业级leak certification阈值；
-不得出现无法解释的持续单调增长。
Verdict：
P7_PIPELINE_STABILITY_PASS
P7_PIPELINE_STABILITY_FAIL
31. P8 — Consolidation and Closeout
汇总：
P4 exact correctness；
-P5 pilot；
-P5 formal benchmark；
-P6 video；
-P7 stability；
-Stage K raw Level B inherited limitation；
-final runtime recommendation。
生成：
Stage P Final Report
experiment matrix
evidence index
SHA verification
architecture diagram source
queue pilot table
Serial/Pipeline benchmark table
throughput/latency trade-off
resource table
stability table
known limitations
更新：
README.md
docs/PROJECT_BRIEF.md
docs/REQUIREMENTS.md
docs/ARCHITECTURE.md
docs/personal/DECISIONS.md
docs/personal/TASKS.md
docs/personal/EXPERIMENT_PLAN.md
最终状态：
STAGE_P_COMPLETE_PIPELINE_RECOMMENDED
条件：
P4 PASS；
-P5 evidence valid；
-P5分类为material increase；
-P6 PASS；
-P7 PASS。
STAGE_P_COMPLETE_SERIAL_RETAINED
条件：
P4 PASS；
-P5 evidence valid；
-P5无material increase或发生regression；
-P6 PASS；
-P7 Pipeline仍PASS；
-final deployment recommendation保留Serial。
STAGE_P_FAILED
条件：
exact correctness无法关闭；
-P5 evidence无效且无法修复；
-P6失败且没有单独接受的平台限制；
-P7 stability失败。
Pipeline没有加速本身不构成Stage P失败。
32. Evidence Policy
固定目录：
results/validation/stage_p/p4_correctness_v1/
results/benchmark/stage_p/p5_queue_pilot_v1/
results/benchmark/stage_p/p5_serial_vs_pipeline_v1/
results/validation/stage_p/p6_video_v1/
results/validation/stage_p/p7_stability_v1/
results/validation/stage_p/p8_final_v1/
重复执行使用：
attempt_001
attempt_002
...
不得覆盖既有attempt。
正式Evidence从P4开始。
P1–P3只保留：
source commit；
commands；
-focused tests；
-short report；
-known limitations。
禁止提交：
TensorRT Engine；
-数据集；
-generated video；
-30分钟完整Detection；
-巨大per-frame trace；
-无必要的raw tensor。
P5大体积JSON和trace：
-可保留本地；
-仓库提交manifest、SHA、summary和统计；
-只有在体积合理且明确批准时才跟踪raw文件。
正式实验必须在：
clean committed source HEAD
上运行。
33. Invalidation Rules
P4失效条件：
Engine、Manifest、ModelContract变化；
-pre/postprocess变化；
-corpus变化；
-Pipeline scheduling变化；
-canonical schema变化；
-Detection结构或顺序变化。
P5失效条件还包括：
queue selection规则；
-measured window；
-Sink composition；
-trace semantics；
-affinity、power或fan policy；
-percentile或ratio定义；
-warmup/measured count。
P6失效条件：
video SHA；
-codec；
-decoded count；
-VideoFileSource semantics；
-canonical schema。
P7失效条件：
selected capacity；
-CorpusReplaySource cycle semantics；
-CanonicalHashSink；
-duration protocol；
-memory classification方法。
Documentation-only变化不自动使实验失效。
34. Git and Authorization Rules
Codex允许：
-在当前授权阶段修改对应范围；
-运行对应测试；
-创建阶段commit。
Codex禁止：
push
merge
tag
除非用户单独明确授权。
P2/P3可以共用开发迭代，不强制一任务一commit；但P4前必须：
clean worktree
committed source HEAD
P3 Gate PASS
Gate依赖：
P0
 ↓
P1
 ↓
P2
 ↓
P3
 ↓
P4
 ↓
P5
 ↓
P6
 ↓
P7
 ↓
P8
35. Final Authorization
Stage P Execution Plan v1.2:
FINAL

Project-AI consistency check:
PASS

P0 Planning Freeze:
COMPLETE_AT_THE_COMMIT_CONTAINING_THIS_CHANGESET

P1:
NOT_AUTHORIZED_UNTIL_P0_COMMIT_IS_REVIEWED

P2–P3 implementation:
NOT AUTHORIZED UNTIL THEIR PREDECESSOR GATES PASS

P4:
NOT AUTHORIZED UNTIL P3_PASS

P5:
NOT AUTHORIZED UNTIL P4_PASS

P6:
NOT AUTHORIZED UNTIL P5 queue capacity has been selected and frozen
AND
P5 formal benchmark protocol is complete

P7:
NOT AUTHORIZED UNTIL P6 disposition is complete
AND P5 formal protocol is complete
AND the selected capacity is frozen

P8:
NOT AUTHORIZED UNTIL P4–P7 dispositions are complete

## P5R Protocol Amendment and Evidence Reclassification

日期：`2026-07-31`

本节是对 P5 validity interpretation 的文档修正，不删除或改写历史 P5
protocol、attempt_001 raw Evidence 或历史 invalid report。P5R 不重新运行
benchmark，不修改 runtime/source/test/config/Engine，不生成新的实验数据。

原规则 `P5 RUN SHA == P4 RUN SHA` 不成立：P4 是 180-frame single-cycle run，
P5 pilot/formal 分别是 1100/5100 accepted-frame extended runs，RUN domain
输入长度不同。P4 RUN SHA 只保留为 single-cycle reference。

P5 RUN SHA 定义为该 run 全部 accepted frames 的 hash；六个 formal run 必须
互相一致。P5 CYCLE SHA 继续继承 P4 expected CYCLE SHA：每个完整 180-frame
cycle 必须匹配；partial cycle 只记录，不参与 PASS。

P5R thermal rule：检测到 throttling 才产生
`RUN_INVALID_THERMAL_THROTTLING`；thermal interface unavailable 只记录
`thermal_throttle_status=unavailable` 并作为 known limitation，不得声称
no-throttling PASS。

基于既有 P5 attempt_001 Evidence 的 reclassification：

- 六个 formal RUN SHA identical；
- 完整 CYCLE SHA 全部匹配 P4 expected；
- accepted/processed=5100/5100，dropped=0，complete measured trace=5000；
- queue selection 按 `throughput >= 0.95 * best` 选择最小 eligible capacity 1；
- paired ratio mean `4.165718`，sample SD `0.007915`；
- classification `MATERIAL_MEASURED_THROUGHPUT_INCREASE`；
- final status `P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE`。

P6 在本任务中未执行。详细 amendment、Evidence index 和 final report 位于
`results/benchmark/stage_p/p5_serial_vs_pipeline_v1/`。
