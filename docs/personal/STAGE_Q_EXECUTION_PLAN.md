Stage Q Execution Plan v0.3 FINAL

> Q0 Pre-freeze Consistency Normalization
>
> Before the first Git freeze, existing Stage P decision records were preserved and the Stage Q decision references were allocated to D074–D080. The output0 layout label was corrected from CHW to BCN. These are numbering and layout-label corrections only; the Stage Q route, thresholds, scope, gates, and authorization chain are unchanged.

TensorRT INT8 Post-Training Quantization Evaluation

TensorRT INT8后训练量化与精度—性能权衡评估

文档状态：

PROJECT_AI_FINAL_CONSISTENCY_CHECK:
PASS
Stage Q Plan:
FINAL
Q0 Planning Freeze:
AUTHORIZED
Q1:
NOT AUTHORIZED BEFORE Q0_PASS
Production implementation:
NOT AUTHORIZED BEFORE ITS MILESTONE GATE
Asset recovery:
NOT REQUIRED YET

后续不得重新讨论以下路线：

TensorRT 10.3 legacy implicit PTQ
IInt8EntropyCalibrator2
全部1260张train images
FP32 Host I/O
INT8 builder flag + FP16 fallback
Q2 smoke / Q3 formal build分离
RuntimeConfig v5
Engine Manifest v2
Result JSON v4
same-runtime-build FP16 control
Serial主性能实验
条件式Pipeline实验
300秒条件确认
zero INT8 compute早停
不进入QAT、ModelOpt、Q/DQ或calibration-size ablation

⸻

1. Authority and Baseline

Repository：

inevitablekl/edge-ai-defect

权威起点：

branch:
main
commit:
630822c7aeec471cc1f82b019d97bc431855045e

Stage P annotated tag：

stage-p-bounded-pipeline-complete-v1.0

Peeled commit：

630822c7aeec471cc1f82b019d97bc431855045e

Q0必须验证：

local refs/heads/main
=
refs/remotes/origin/main
=
stage-p-bounded-pipeline-complete-v1.0^{}
=
630822c7aeec471cc1f82b019d97bc431855045e

并验证：

git cat-file -t stage-p-bounded-pipeline-complete-v1.0
=
tag

拟创建分支：

feature/jetson-tensorrt-int8

必须从上述exact commit创建，不得从旧feature分支创建。

当前预期唯一未跟踪文件：

docs/personal/STAGE_Q_FACT_INVENTORY.md

Q0必须先确认它是唯一工作区变化，再切换到Stage Q分支提交。不得先将其单独提交到main。

任一基线条件不满足：

Q0_BLOCKED_BASELINE_OR_TAG_MISMATCH
STOP

⸻

2. Stage Positioning

Stage Q研究问题：

在保持同一冻结YOLOv8n ONNX、同一Jetson平台、同一FP32 Host I/O、同一前处理、同一后处理和同一任务评价方法的条件下，TensorRT INT8后训练量化能否以可接受的检测精度损失换取实际推理性能收益？

实验自变量：

TensorRT engine compute precision:
Original FP16 builder-mode Engine
vs
INT8-enabled PTQ Engine with FP16 fallback

主实验：

FP16 Serial
vs
INT8 Serial

条件实验：

FP16 Pipeline
vs
INT8 Pipeline

Stage Q不重新研究：

模型训练
ONNX导出
模型结构
检测算法
Pipeline拓扑
queue capacity
动态shape
batch size
GPU前处理
GPU后处理

INT8结果不优于FP16本身不构成Stage失败。

⸻

3. Quantization Route

冻结：

Post-Training Quantization
PTQ
TensorRT 10.3 implicit INT8 calibration
IInt8EntropyCalibrator2
BuilderFlag::kINT8
BuilderFlag::kFP16
FP32 Host I/O
static batch = 1
static input = [1,3,640,640]
static output = [1,10,8400]

正式Engine描述：

TensorRT INT8-enabled mixed-precision Engine

或：

INT8 + FP16 + FP32 mixed-precision Engine

不得在没有完整审计证据时描述为：

pure INT8
full INT8
all-layer INT8

版本边界冻结为：

Stage Q deliberately adopts the deprecated TensorRT 10.3 implicit INT8 calibration workflow as a version-bound project decision. This is not presented as the recommended workflow for new TensorRT projects or as a TensorRT 11-compatible implementation.

未来TensorRT版本迁移属于Future Work，不进入Stage Q。

⸻

4. Scope

4.1 必须完成

Stage Q Plan、Task Cards、D074—D080
平台与资产预检
split isolation检查
全train calibration manifest
calibrator和专用INT8 builder
4-image独立smoke build
1260-image权威full calibration和Engine build
calibration cache provenance
Engine Manifest v2
详细layer precision audit
RuntimeConfig v5
Result JSON v4
INT8 production runtime接入
same-runtime-build FP16/INT8 accuracy
FP16/INT8 Serial benchmark
条件式Pipeline benchmark
条件式300秒confirmation
机械化最终分类
Final Report和Evidence Index

4.2 明确排除

QAT
NVIDIA ModelOpt
ONNX Q/DQ rewrite
INT8 Host I/O
INT8 preprocessing
新模型训练
新数据集
calibration-size ablation
多个calibrator
calibration算法比较
per-layer fallback search
manual precision tuning
custom CUDA
GPU preprocessing
GPU NMS
DLA
batch > 1
dynamic shape
新Pipeline拓扑
queue retuning
30分钟INT8稳定性
camera
RTSP
ROS2
DeepStream
通用量化平台
工业认证

⸻

5. Stage Q Decisions

D074 — Baseline, scope and authority

冻结：

* main@630822c7...；
* Stage P annotated tag；
* Stage Q分支起点；
    -研究问题和范围；
* Q0—Q8授权链；
    -负结果不等于Stage失败。

D075 — TensorRT 10.3 version-bound legacy PTQ

冻结：

* IInt8EntropyCalibrator2；
* implicit calibration；
* INT8 builder flag；
* FP16 fallback；
* FP32 Host I/O；
* static batch 1；
    -不引入QAT、ModelOpt、Q/DQ；
    -不声称TensorRT 11兼容；
    -不声称这是新项目推荐路线。

D076 — Calibration data isolation and ordering

冻结：

calibration:
1260 train images only
forbidden:
val
test
Stage K/P evaluation corpus
Level B corpus
P6 video

Split互斥必须同时按：

normalized relative path
image content SHA256

验证。

正式ordering采用：

sha256_key_permutation_v1
seed = 42

D077 — Builder, cache and artifact authority

冻结：

* stage_q_int8_builder是唯一formal builder；
* Q2仅4-image smoke；
* Q3一次build完成1260-image calibration、cache和Engine；
* formal首次构建强制cache miss；
* cache复用必须验证metadata；
* trtexec只作load和inspection；
* formal artifacts必须原子发布。

D078 — Manifest, runtime and result mapping

冻结：

* RuntimeConfig v5；
* Manifest v2仅用于INT8；
* Result JSON v4；
    -历史schema行为不变；
* precision在运行时仅来自validated Manifest；
* Manifest v2由Q3 audit sidecar和SHA形成构建期provenance；
* FP16结果不得输出空calibration对象。

D079 — Accuracy, hash and Serial performance authority

冻结：

* same-runtime-build FP16 control；
* frozen test manifest；
* Q5通过CorpusReplaySource生成accuracy Result和expected cycle hash；
* evaluator消费同一Result JSON；
* accuracy每backend一次；
* Serial三组paired process；
    -固定metric、drop、ratio、percentile公式；
* FP16与INT8之间不要求Detection hash相同；
    -同一backend必须cycle deterministic。

D080 — Conditional Pipeline and final disposition

冻结：

* Pipeline进入条件；
* Q7五种互斥状态；
* 300秒confirmation的正常EOS语义；
    -最终互斥决策树；
* zero INT8 compute早停；
* Pipeline有效负结果导致FP16保留，而非自动Stage失败。

⸻

6. Frozen Assets

Source ONNX：

models/onnx/yolov8n_neudet_frozen.onnx
SHA256:
c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944

Original FP16 Engine：

/home/orin/edge-ai-local-models/stage_k/
yolov8n_neudet_trt10.3_fp16_b1_640.engine
SHA256:
6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc

FP16 Manifest：

models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json
SHA256:
39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63

ModelContract：

configs/model_contracts/yolov8n_neudet_frozen.yaml
SHA256:
9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190

不存在独立preprocess contract文件，因此禁止创造：

preprocess_contract_sha256

前处理身份通过：

ModelContract SHA
Preprocessor implementation identity
calibration manifest SHA
builder artifact identity

追溯。

⸻

7. Dataset Contract

train:
1260 images
val:
360 images
test:
180 images
442 GT boxes
6 classes

Manifest路径：

results/validation/stage_k_task_eval_v2/split/
train_manifest.json
val_manifest.json
test_manifest.json

Test manifest SHA：

fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8

Q1必须证明：

train ∩ val = 0
train ∩ test = 0
val ∩ test = 0

检查域：

normalized path
image content SHA256

任一交集非空：

Q1_BLOCKED_SPLIT_ISOLATION_FAILURE

⸻

8. Calibration Manifest and Ordering

Formal manifest：

{
  "schema_version": 1,
  "purpose": "formal_int8_calibration",
  "source_split": "train",
  "selection": "all_train_images",
  "ordering_algorithm": "sha256_key_permutation_v1",
  "seed": 42,
  "image_count": 1260,
  "source_train_manifest_sha256": "...",
  "images": []
}

排序算法严格定义为：

1. 将normalized relative paths按UTF-8字节序升序排序。
2. 对每个path计算：

SHA256(
  "stage_q_calibration_order_v1\n"
  + decimal_seed
  + "\n"
  + normalized_relative_path
)

3. 以：

(ordering_key, normalized_relative_path)

按字节序升序排列。

所有1260张图均参与，算法只决定顺序，不执行selection。

每张图片记录：

calibration_index
normalized relative path
image SHA256
decoded width
decoded height
ordering_key

正式calibration：

batch_size = 1
successful_calibration_batches = 1260
images_consumed = 1260

最终终止性的getBatch()调用不计入成功batch。

⸻

9. Calibration Preprocessing and Failure Policy

必须复用production Preprocessor：

BGR
LetterBox 640×640
INTER_LINEAR
padding 114
BGR → RGB
HWC → CHW
FP32 / 255.0
NCHW [1,3,640,640]

任一情况必须fail-fast：

图片不存在
decode失败
image SHA不匹配
shape非法
preprocess失败
HostTensor合同不匹配
CUDA allocation失败
CUDA copy失败
calibrator callback异常

禁止跳过图片后继续生成cache或Engine。

⸻

10. Artifact Identity Model

不得再以完整Git HEAD变化作为机械失效条件。冻结三类身份。

10.1 Repository commit

repository_commit

用途：

-完整provenance；
-说明生成artifact时的仓库状态。

它本身不自动触发实验失效。

10.2 Builder artifact identity

至少包括：

builder executable SHA256
builder-relevant source manifest SHA256
Preprocessor implementation manifest SHA256
ModelContract SHA256
compiler/build configuration SHA256
ONNX SHA256
calibration manifest SHA256
TensorRT/CUDA/L4T identity
builder flags
workspace

builder-relevant source manifest必须列出所有参与builder、calibrator、manifest generation和Preprocessor实现的tracked source path及其SHA。

10.3 Runtime experiment identity

至少包括：

application executable SHA256
experiment runner executable SHA256
evaluator source SHA256
evaluator configuration SHA256
RuntimeConfig SHA256
Engine SHA256
Engine Manifest SHA256
test manifest SHA256
postprocess configuration SHA256

“same-commit FP16 control”的准确含义：

FP16和INT8正式对照必须使用同一Stage Q runtime/evaluator source HEAD和同一组runtime/evaluation binaries。

它不要求历史FP16 Engine的source_git_commit等于INT8 Engine的构建commit。

Q8文档commit不会使既有硬件实验自动失效。

⸻

11. Stage Q INT8 Builder

新增：

stage_q_int8_builder

它是Stage Q专用工具，不是通用builder framework。

职责：

读取ONNX和ModelContract
验证calibration manifest
复用Preprocessor
实现IInt8EntropyCalibrator2
管理device calibration buffer
管理cache及metadata
构建serialized Engine
设置ProfilingVerbosity=DETAILED
输出build summary和logs
准备Manifest v2数据
支持smoke/formal模式
原子发布artifact

模式：

--artifact-purpose smoke
--artifact-purpose formal
--cache-mode force-miss
--cache-mode validated-reuse

Q3首次formal build必须：

artifact-purpose = formal
cache-mode = force-miss

⸻

12. Q2 and Q3 Build Boundary

12.1 Q2 smoke

Q2只允许：

4-image calibration smoke

独立路径：

/home/orin/edge-ai-local-models/stage_q/smoke/

Smoke manifest必须：

purpose = smoke
image_count = 4

产物：

smoke Engine
smoke cache
smoke cache metadata
smoke build summary

所有smoke artifacts必须带：

artifact_purpose = smoke

Q3 formal builder必须拒绝任何smoke artifact。

Q2不得执行1260-image正式calibration。

12.2 Q3 formal build

首次正式build必须强制cache miss。

同一个权威builder invocation完成：

1260-image calibration
→ final calibration cache
→ final serialized Engine

必须记录：

successful_calibration_batches = 1260
images_consumed = 1260
unreadable_images = 0
skipped_images = 0
failed_images = 0
batch_size = 1
cache_read = false

Engine、cache、cache metadata、Manifest v2、audit和summary必须属于同一：

attempt ID
builder artifact identity
calibration manifest
TensorRT environment
builder invocation

⸻

13. Calibration Cache Provenance

Binary cache：

local-only

Sidecar：

calibration_cache.meta.json

至少包含：

{
  "schema_version": 1,
  "artifact_purpose": "formal",
  "cache_sha256": "...",
  "cache_size_bytes": 0,
  "source_onnx_sha256": "...",
  "model_contract_sha256": "...",
  "calibration_manifest_sha256": "...",
  "algorithm": "IInt8EntropyCalibrator2",
  "batch_size": 1,
  "image_count": 1260,
  "tensorrt_version": "10.3.0.30",
  "cuda_version": "12.6",
  "l4t_version": "36.5",
  "builder_flags": {
    "int8": true,
    "fp16": true,
    "workspace_mib": 4096
  },
  "repository_commit": "...",
  "builder_executable_sha256": "...",
  "builder_artifact_identity_sha256": "..."
}

Validated reuse时逐项验证。

任一不匹配：

CACHE_REJECTED_PROVENANCE_MISMATCH

随后允许重新calibration，不得静默使用错误cache。

Metadata缺失时cache必须被拒绝。

⸻

14. Atomic Publication

Formal artifacts先写入同一文件系统中的attempt临时目录。

只有以下全部成功后才发布：

1260-image calibration完成
cache写入成功
Engine serialization成功
Engine反序列化成功
Engine load smoke成功
SHA计算成功
detailed inspection成功
precision audit成功
Manifest v2生成并验证成功
metadata和summary生成成功

失败时：

-不得留下正式路径上的半成品；
-不得将临时Engine或cache标为正式；
-保留失败attempt的日志和disposition；
-不得覆盖既有attempt。

⸻

15. Engine Build Contract

TensorRT:
10.3.0.30
source ONNX:
c88ac014...
input:
images FP32 [1,3,640,640] CHW
output:
output0 FP32 [1,10,8400] BCN
BuilderFlag:
INT8 enabled
FP16 enabled
workspace:
4096 MiB
batch:
1
DLA:
disabled
custom plugins:
none
Host I/O:
FP32

建议local路径：

/home/orin/edge-ai-local-models/stage_q/formal/
yolov8n_neudet_trt10.3_int8_ptq_b1_640.engine

不提交Engine或cache binary。

⸻

16. Precision Audit

Build时：

ProfilingVerbosity = DETAILED

保留：

raw_engine_layer_info.json
layer_precision_audit_summary.json

Summary：

{
  "schema_version": 1,
  "classification_contract_version": 1,
  "confirmed_int8_compute": 0,
  "confirmed_fp16_compute": 0,
  "confirmed_fp32_compute": 0,
  "reformat_or_copy": 0,
  "mixed_or_unclassified": 0,
  "inspector_visible_layers": 0
}

原则：

-不要求每层都能唯一分类；

* reformat/copy不计compute；
* output datatype本身不足以证明INT8 compute；
* raw inspector output为审计基础；
* summary为派生结果。

最低INT8有效判定：

至少一个非reformat/copy computational layer的详细inspector信息明确显示INT8 activation datatype/format，或明确显示INT8 compute tactic。

结果：

confirmed_int8_compute > 0
→ Q3_INT8_ENGINE_BUILD_PASS
confirmed_int8_compute == 0
→ Q3_EARLY_DISPOSITION_FP16_RETAINED
→ Q4–Q7 SKIPPED
→ Q8 negative-result closeout

Zero INT8 compute不是Stage失败。

⸻

17. Engine Manifest v2 and Audit Authority

Manifest v1：

仅用于历史FP16 Engine

Manifest v2：

仅用于Stage Q INT8 Engine

Manifest v2必须包含：

{
  "schema_version": 2,
  "artifact_kind": "tensorrt_engine",
  "backend_type": "tensorrt_int8",
  "precision_mode": "INT8+FP16+FP32 mixed precision",
  "int8_enabled": true,
  "fp16_fallback_enabled": true,
  "host_io_dtype": "FP32",
  "calibration": {},
  "layer_precision_summary": {},
  "precision_audit": {
    "profiling_verbosity": "DETAILED",
    "raw_engine_layer_info_sha256": "...",
    "audit_summary_sha256": "...",
    "classification_contract_version": 1
  }
}

并继承Manifest v1的平台、Engine、ONNX、shape、I/O、workspace、command、log和plugin字段。

Q3发布前必须验证：

Manifest v2.layer_precision_summary
==
layer_precision_audit_summary.json对应字段

并验证：

Manifest v2.precision_audit.raw_engine_layer_info_sha256
==
raw file SHA
Manifest v2.precision_audit.audit_summary_sha256
==
summary file SHA

部署时：

Result JSON v4 precision source
=
validated Engine Manifest only

Audit sidecar是Manifest构建时的provenance authority，不是production runtime dependency。

⸻

18. RuntimeConfig / Manifest / Result Mapping

RuntimeConfig v3/v4

tensorrt_int8:
rejected
historical Result:
unchanged

RuntimeConfig v5 + tensorrt_fp16

Manifest:
v1 required
Result:
v4
precision:
required
calibration:
absent

RuntimeConfig v5 + tensorrt_int8

Manifest:
v2 required
Result:
v4
precision:
required
calibration:
required

Manifest v2不得用于FP16 backend。

RuntimeConfig v5支持：

backend.type:
tensorrt_fp16
tensorrt_int8

其余serial/pipeline和directory/video union继承v4。

⸻

19. Result JSON v4

Precision字段：

"precision": {
  "engine_compute_mode": "...",
  "int8_enabled": true,
  "fp16_enabled": true,
  "host_io_dtype": "FP32"
}

FP16来源：

validated Manifest v1

Q4必须扩展Manifest v1 C++ loader，实际读取和验证：

precision_mode
fp16_builder_mode
int8_enabled

不能只修改Result writer。

INT8来源：

validated Manifest v2

Calibration字段仅INT8存在：

"calibration": {
  "algorithm": "IInt8EntropyCalibrator2",
  "source_split": "train",
  "image_count": 1260,
  "manifest_sha256": "...",
  "cache_sha256": "...",
  "cache_metadata_sha256": "..."
}

FP16：

calibration key absent

不得输出空对象。

历史Result v1/v2/v3字节输出不得变化。

⸻

20. Runtime Integration

复用：

TensorRtEngine
InferenceEngineFactory
SerialRunner
PipelineRunner
ApplicationRunner
StagePExperimentRunner的最小composition能力

不得新增：

TensorRtInt8Engine
Int8PipelineRunner
Int8PostProcessor
通用runner framework

Factory新增：

tensorrt_int8

INT8加载时验证：

config backend = tensorrt_int8
Manifest schema = 2
Manifest backend一致
int8_enabled = true
confirmed_int8_compute > 0
calibration provenance完整
precision audit SHA绑定完整
Engine SHA一致
ONNX SHA一致
ModelContract SHA一致
Host I/O = FP32
tensor name/shape/layout一致
no unexpected plugin dependency

部署运行不要求cache binary和audit sidecar存在。

⸻

21. Q5 Accuracy and Expected CYCLE SHA Authority

21.1 Formal invocation authority

FP16和INT8各执行一次正式invocation。

唯一authority：

Source:
CorpusReplaySource
image root:
frozen test image root
manifest:
frozen test_manifest.json
cycles:
1
max accepted frames:
180
ordering:
exact manifest entry order
relative_path:
exact normalized manifest image_path value
runtime:
Serial
sink composition:
TimedJsonSink wrapping Result JSON v4
+
CanonicalHashSink(CYCLE, cycle_length=180)

Accuracy evaluator必须消费该invocation生成的同一份Result JSON v4。

禁止：

使用DirectorySource枚举生成accuracy Result
使用另一种source单独生成expected hash
从evaluator summary反向构造canonical hash
改变relative-path domain

Q6/Q7必须复用相同：

test manifest
image root
manifest ordering
relative-path domain
cycle length

Q5冻结：

FP16 expected CYCLE SHA
INT8 expected CYCLE SHA

FP16与INT8之间不要求相等。

21.2 Evaluator provenance

记录：

evaluator source path
evaluator source SHA256
evaluator configuration SHA256
test manifest SHA256
runtime experiment identity

Accuracy无需重复运行。

21.3 Evidence Gate

必须：

evaluated_images = 180
ground_truth_boxes = 442
image_failures = 0
non_finite_detection_values = 0
non_finite_metrics = 0
all six classes have non-zero GT support
FP16 evaluator PASS
INT8 evaluator PASS

任一失败：

Q5_ACCURACY_EVIDENCE_INVALID

不得进入数值分类。

21.4 Metrics

Precision
Recall
mAP50
mAP50-95
per-class AP50
per-class Recall
detection count

统一定义：

drop(metric) =
max(0, FP16_metric - INT8_metric)

Signed delta：

INT8_metric - FP16_metric

Detection count只作诊断，不单独触发classification。

不得在结果产生后临时增加Detection count阈值。

21.5 Classification

ACCEPTABLE

mAP50-95 drop <= 0.020
mAP50 drop <= 0.020
Precision drop <= 0.030
Recall drop <= 0.030
each class AP50 drop <= 0.050
each class Recall drop <= 0.100

TRADEOFF

不满足ACCEPTABLE，但全部满足：

mAP50-95 drop <= 0.040
mAP50 drop <= 0.040
Precision drop <= 0.060
Recall drop <= 0.060
each class AP50 drop <= 0.100
each class Recall drop <= 0.200

UNACCEPTABLE

超过任一TRADEOFF数值边界

删除所有主观兜底条款。

Q5完成状态：

Q5_ACCURACY_EVIDENCE_VALID
+
ACCEPTABLE / TRADEOFF / UNACCEPTABLE

⸻

22. Q6 Serial Performance

Q6前提：

Q3_INT8_ENGINE_BUILD_PASS
Q4_INT8_RUNTIME_INTEGRATION_PASS
Q5_ACCURACY_EVIDENCE_VALID

即使accuracy为UNACCEPTABLE，Q6仍执行，用于形成完整accuracy—performance负结果。

顺序：

Pair 1: FP16 → INT8
Pair 2: INT8 → FP16
Pair 3: FP16 → INT8

每process：

100 warmup
5000 measured
5100 accepted
CorpusReplaySource
cycle length = 180
drop = 0

必须显式处理：

5100 = 28 × 180 + 60

因此每run：

28 complete cycles:
必须匹配该backend的Q5 expected CYCLE SHA
final partial cycle:
60 frames
记录frame count和partial digest状态
不得与180-frame expected SHA比较
不得计为完整cycle PASS

22.1 Formulas

Mean inference service：

sum(5000 measured inference_service_ms) / 5000

Paired inference speedup：

FP16 mean inference_service_ms
/
INT8 mean inference_service_ms

Measured pre-sink wall：

first measured source-service begin
→
last measured postprocess-service end

Pre-sink throughput：

5000 / measured pre-sink wall seconds

Paired throughput ratio：

INT8 pre-sink throughput
/
FP16 pre-sink throughput

End-to-end latency：

source-service begin
→
outer sink write completion

报告：

mean
P50
P95
P99

Percentile：

Type-7 linear interpolation

最终primary分类使用：

arithmetic mean of three paired inference speedup ratios

并报告三个原始ratio和sample SD，n-1。

22.2 Performance classification

>= 1.10
MATERIAL_INT8_INFERENCE_GAIN
1.03–1.10
SMALL_INT8_INFERENCE_GAIN
0.97–1.03
NO_MATERIAL_INT8_GAIN
< 0.97
INT8_INFERENCE_REGRESSION

边界按左闭右开执行，最后一项除外。

22.3 End-to-end regression

使用三个paired ratio的算术平均。

全部满足：

mean paired pre-sink throughput ratio >= 0.97
mean paired mean-latency ratio <= 1.03
mean paired P95-latency ratio <= 1.05

则：

NO_MATERIAL_END_TO_END_REGRESSION

否则：

MATERIAL_END_TO_END_REGRESSION

22.4 Environment

记录：

运行方向
起始/结束温度
power mode
clocks/fan probe
affinity
OpenCV threads
Engine SHA
Manifest SHA
application executable SHA
experiment runner SHA
config SHA
thermal probe

明确throttling：

RUN_INVALID_THERMAL_THROTTLING

接口不可用：

thermal_throttle_status = unavailable

作为限制，不自动判无效。

⸻

23. Q7 Conditional Pipeline

进入条件：

accuracy = ACCEPTABLE or TRADEOFF
AND
mean paired Serial inference speedup >= 1.05

否则：

Q7_PIPELINE_SKIPPED_BY_FROZEN_GATE

固定：

queue_capacity = 1
drop_policy = block

顺序：

FP16 → INT8
INT8 → FP16
FP16 → INT8

每run：

100 warmup
5000 measured
5100 accepted

每run同样存在：

28 complete cycles
+
60-frame partial cycle

处理规则与Q6完全一致。

23.1 Q7互斥状态

Q7必须且只能输出以下之一：

1. Skipped

Q7_PIPELINE_SKIPPED_BY_FROZEN_GATE

仅在entry gate不满足时使用。

2. Valid, no material regression

Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION

要求：

all required runs valid
no reproducible runtime failure
mean paired INT8/FP16 Pipeline throughput ratio >= 0.97

3. Valid material regression

Q7_PIPELINE_VALID_MATERIAL_REGRESSION

要求：

Evidence valid
mean paired INT8/FP16 Pipeline throughput ratio < 0.97

4. Valid negative runtime result

Q7_PIPELINE_VALID_NEGATIVE_RUNTIME_RESULT

用于可重复的：

crash
deadlock
non-finite
inference failure
drop
queue lifecycle failure
worker join failure
300-second confirmation runtime failure

这是有效负结果，不是Evidence invalid。

5. Evidence invalid

Q7_PIPELINE_EVIDENCE_INVALID

用于：

provenance不完整
测量窗口不可验证
必要文件损坏
attempt不可复核
环境合同冲突
无法区分runtime failure与测试基础设施失败

Q7 Evidence invalid在Q7属于必需路径时导致Stage失败。

⸻

24. 300-second Confirmation

仅当全部满足时执行：

accuracy = ACCEPTABLE
Serial speedup >= 1.05
NO_MATERIAL_END_TO_END_REGRESSION
Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION
准备形成INT8_RECOMMENDED

固定：

INT8 Pipeline
queue_capacity = 1
AGGREGATE_ONLY
CanonicalHashSink
cycle length = 180

停止语义：

1. 只在完成完整180-frame cycle后检查active wall time。
2. 若active wall time < 300s，开始下一完整cycle。
3. 若active wall time >= 300s，不再开始新cycle。
4. Source正常返回EOS。
5. Pipeline正常drain。
6. 所有workers join。

禁止：

SIGTERM
中途cancel
在cycle中间停止

必须记录：

completed_cycles
processed_frames
active_wall_seconds
partial_cycles = 0

Gate：

crash = 0
deadlock = 0
inference error = 0
non-finite = 0
drop = 0
all complete cycles match INT8 Q5 expected SHA
queues CLOSED/drained
workers joined
RSS无无法解释的持续单调增长

失败若为真实可重复runtime失败：

Q7_PIPELINE_VALID_NEGATIVE_RUNTIME_RESULT

不得描述为工业稳定性认证。

⸻

25. Milestones

Q0 — Planning Freeze

执行环境：

Jetson Codex

Actions：

-验证main/origin/tag；
-确认Fact Inventory是唯一工作区变化；
-创建Stage Q分支；
-提交Fact Inventory；
-写入v0.3 FINAL；
-生成Task Cards；
-追加D074—D080；
-更新必要状态文档；
-记录当前CMake/test inventory；
-不修改production代码、CMake、schema和tests；
-创建Q0 freeze commit。

Gate：

Q0_PASS

Q0完成后：

Q1_NOT_AUTHORIZED_PENDING_USER_REVIEW

Q1 — Platform and Asset Preflight

执行环境：

Jetson Codex

验证：

ONNX文件和SHA
1260/360/180图片及manifest
split isolation
FP16 Engine和SHA
TensorRT builder/parser/runtime
CUDA Runtime
INT8 builder capability
trtexec load/inspection
磁盘空间
smoke/formal目录

资产处置：

ONNX或train images缺失

Q1_BLOCKED_ASSET_RECOVERY_REQUIRED

需要用户介入。

FP16 Engine缺失

恢复优先级：

1. 从Stage K/P本地Evidence或local model目录恢复。
2. 使用冻结ONNX和Stage K权威build command在同平台重建。
3. 验证是否恢复至冻结SHA。

只有上述路径均不可执行或无法恢复冻结SHA时，才请求用户介入。

Gate：

Q1_PLATFORM_AND_ASSET_PASS

Q2 — Builder Implementation and Smoke

执行环境：

Jetson Codex

实现：

calibration manifest generator
split checker
calibrator
cache metadata validator
artifact identity manifests
atomic publication
stage_q_int8_builder
focused tests
4-image smoke

不得执行formal calibration。

Gate：

Q2_BUILDER_AND_SMOKE_PASS

Q3 — Formal Calibration, Build and Audit

执行环境：

Jetson Codex

执行：

formal manifest validation
force cache miss
1260-image calibration
final cache
final Engine
cache metadata
detailed inspector output
audit summary
Manifest v2
load smoke
20-image inference preflight
atomic publication

结果：

confirmed_int8_compute > 0
→ Q3_INT8_ENGINE_BUILD_PASS

或：

confirmed_int8_compute == 0
→ Q3_EARLY_DISPOSITION_FP16_RETAINED
→ Q8

Q4 — Runtime Integration

执行环境：

Jetson Codex

实现：

RuntimeConfig v5
Manifest v1 loader扩展
Manifest v2 loader
Result JSON v4
schema mapping
tensorrt_int8 factory
TensorRtEngine validation
Serial/Pipeline dispatch
historical compatibility
TensorRT OFF/ON build
production smoke

Gate：

Q4_INT8_RUNTIME_INTEGRATION_PASS

Q5 — Accuracy and Hash Authority

执行环境：

Jetson Codex

执行：

CorpusReplaySource single-cycle FP16 formal invocation
CorpusReplaySource single-cycle INT8 formal invocation
Result JSON v4
per-backend expected CYCLE SHA
same Result JSON evaluator
metrics和classification

Gate：

Q5_ACCURACY_EVIDENCE_VALID

或：

Q5_ACCURACY_EVIDENCE_INVALID

Q6 — Serial Performance

执行环境：

Jetson Codex

执行三组paired Serial实验、cycle correctness、telemetry和性能分类。

Gate：

Q6_SERIAL_PERFORMANCE_EVIDENCE_VALID

Q7 — Conditional Pipeline and Recommendation

执行环境：

Jetson Codex

输出五种互斥状态之一，必要时执行300秒confirmation。

Gate：

Q7_DISPOSITION_COMPLETE

其中：

Q7_PIPELINE_EVIDENCE_INVALID

不构成成功的disposition。

Q8 — Consolidation and Closeout

执行环境：

Jetson Codex

入口：

normal Q4–Q7 completion
or
Q3 zero-INT8 early disposition

生成：

Stage Q Final Report
Evidence Index
accuracy/performance tables
trade-off chart data
known limitations
final classification
必要的项目文档更新
local-only Evidence分类
release readiness report

仅修改与Stage Q真实结论有关的章节。

禁止：

全局文档重写
新功能
自动merge
自动tag
自动push

Gate：

Q8_COMPLETE_READY_FOR_MAIN_MERGE

⸻

26. Evidence Directories

results/build/tensorrt/q2_int8_smoke_v1/
results/build/tensorrt/q3_int8_engine_v1/
results/validation/stage_q/q4_runtime_v1/
results/validation/stage_q/q5_accuracy_v1/
results/benchmark/stage_q/q6_serial_v1/
results/benchmark/stage_q/q7_pipeline_v1/
results/validation/stage_q/q7_confirmation_v1/
results/validation/stage_q/q8_final_v1/

重复：

attempt_001
attempt_002
...

不得覆盖。

Git tracked：

calibration manifest
cache metadata
Engine manifest
artifact identity manifests
SHA manifest
build summary
audit summary
config
statistical summary
Final Report
Evidence Index
必要的小型日志摘要

Local-only：

ONNX
Engine
cache binary
dataset
full raw Result JSON
full trace
raw telemetry
temporary build artifacts

⸻

27. Invalidation Rules

Q2/Q3 builder artifacts

根据相关artifact identity判断，而不是单独根据HEAD判断。

失效条件包括：

ONNX SHA变化
ModelContract变化
train manifest/image SHA变化
calibration ordering变化
Preprocessor implementation变化
calibrator变化
builder-relevant source manifest变化
builder executable变化
compiler/build config变化
TensorRT/CUDA/L4T变化
builder flags/workspace变化
cache或metadata变化

Q4 runtime integration

schema mapping变化
Manifest loader变化
factory/engine validation变化
I/O合同变化
Engine/Manifest变化
application binary变化

Q5 accuracy

test manifest或GT变化
relative-path domain变化
CorpusReplaySource semantics变化
evaluator source/config变化
postprocess变化
Engine变化
Result JSON input变化
metric/drop/threshold变化
runtime/evaluator binaries变化

Q6/Q7

warmup/measured window变化
source/cycle semantics变化
Sink/trace语义变化
power/clocks/fan/affinity策略变化
统计公式变化
queue capacity变化
Engine变化
per-backend expected hash变化
runtime experiment identity变化

Repository documentation-only commit不自动使实验失效。

⸻

28. Final Classification

最终决策按顺序机械执行。

1. Required Evidence invalid

只检查当前授权路径中的必需Evidence。

required Evidence invalid or unreproducible
→ STAGE_Q_FAILED

Q3 zero-INT8早停路径中，Q4—Q7不是必需Evidence，不得因其缺失判失败。

2. Zero INT8 compute

confirmed_int8_compute == 0
→ STAGE_Q_COMPLETE_FP16_RETAINED

3. Accuracy unacceptable

accuracy = UNACCEPTABLE
→ STAGE_Q_COMPLETE_FP16_RETAINED

4. Insufficient Serial gain

mean paired Serial inference speedup < 1.05
→ STAGE_Q_COMPLETE_FP16_RETAINED

5. Pipeline valid negative result

Q7_PIPELINE_VALID_MATERIAL_REGRESSION
or
Q7_PIPELINE_VALID_NEGATIVE_RUNTIME_RESULT
→ STAGE_Q_COMPLETE_FP16_RETAINED

6. INT8 trade-off only

全部满足：

accuracy = TRADEOFF
Serial speedup >= 1.05
NO_MATERIAL_END_TO_END_REGRESSION
Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION

结果：

STAGE_Q_COMPLETE_INT8_TRADEOFF_ONLY

7. INT8 recommended

全部满足：

accuracy = ACCEPTABLE
Serial speedup >= 1.05
NO_MATERIAL_END_TO_END_REGRESSION
Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION
300-second confirmation valid

结果：

STAGE_Q_COMPLETE_INT8_RECOMMENDED

8. Fallback

其他Evidence有效但不满足上述推荐条件：

STAGE_Q_COMPLETE_FP16_RETAINED

⸻

29. Git and Authorization Rules

默认执行环境：

Jetson Codex

除非明确证明Jetson无法完成必要任务，否则不切换WSL。

Codex允许：

-修改当前授权阶段范围内的文件；
-运行对应测试和实验；
-创建阶段commit。

Codex禁止：

push
merge
rebase
tag

除非用户单独明确授权。

Gate链：

Q0
 ↓
Q1
 ↓
Q2
 ↓
Q3
 ├── zero INT8 → Q8
 └── non-zero INT8
       ↓
      Q4
       ↓
      Q5
       ↓
      Q6
       ↓
      Q7
       ↓
      Q8

⸻

30. Final Authorization

Stage Q Execution Plan v0.3:
FINAL
Project-AI consistency check:
PASS
Q0 Planning Freeze:
AUTHORIZED
Q1:
NOT AUTHORIZED UNTIL Q0_PASS
Q2:
NOT AUTHORIZED UNTIL Q1_PASS
Q3:
NOT AUTHORIZED UNTIL Q2_PASS
Q4:
NOT AUTHORIZED UNTIL Q3_INT8_ENGINE_BUILD_PASS
Q5:
NOT AUTHORIZED UNTIL Q4_PASS
Q6:
NOT AUTHORIZED UNTIL Q5_ACCURACY_EVIDENCE_VALID
Q7:
NOT AUTHORIZED UNTIL Q6_SERIAL_PERFORMANCE_EVIDENCE_VALID
Q8:
AUTHORIZED ONLY AFTER:
Q7 disposition complete
or
Q3_EARLY_DISPOSITION_FP16_RETAINED
