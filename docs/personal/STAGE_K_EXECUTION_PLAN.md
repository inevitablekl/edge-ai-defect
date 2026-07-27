Document status: FINAL
Planning baseline commit: e49f28dd60a49493538d1fd65e5e8fd81676e277
Planning baseline tag: stage-j-complete-v1.0
Stage J status: COMPLETE
K0 authorization: AUTHORIZED
K1 authorization: NOT_AUTHORIZED_UNTIL_K0_FREEZE_COMMIT

Stage K Execution Plan v1.1 FINAL

Jetson TensorRT FP16-Enabled Mixed-Precision Serial Backend

本版本取代：

Stage K Execution Plan v1.0
FINAL_CONSISTENCY_CHECK_PENDING

文档状态：

Stage J:
COMPLETE
K-DR1:
COMPLETE
K-DR2:
COMPLETE
K-DR3:
COMPLETE
Stage K Execution Plan v1.1:
FINAL
K0 Planning Freeze:
AUTHORIZED
K1 Platform Acceptance:
NOT_AUTHORIZED_UNTIL_K0_FREEZE_COMMIT
TensorRT Engine Build:
NOT_AUTHORIZED_BEFORE_K1_PASS_AND_D062_ACCEPTED
Stage P Pipeline Implementation:
NOT_AUTHORIZED_BEFORE_STAGE_K_CLOSEOUT

⸻

1. 阶段定位

Stage K 的目标是：

在 Jetson Orin Nano Super 上实现直接基于 TensorRT C++ Runtime API 的串行推理后端，使用离线构建并启用 FP16 builder mode 的混合精度 Engine，并在相同设备、模型、数据、预处理、后处理和代码版本条件下，与 ONNX Runtime CPU k5 基线完成正确性、性能和稳定性比较。

Stage K 服务于：

* 研究生毕业设计；
* 工程应用型小论文；
* Edge AI Deployment 求职项目展示。

Stage K 采用：

论文级验证
+
学生级完整工程闭环
+
可控交付周期

不采用工业量产级交付标准。

Stage K 不证明：

* 工业产品已经 Production Ready；
* 所有网络层均使用 FP16；
* TensorRT 在所有模型或硬件上普遍优于 ORT；
* 系统已经完成 Pipeline、GPU preprocessing 或 GPU NMS；
* 系统已通过工业认证级稳定性验证。

⸻

2. 事实源与文档优先级

Stage K 执行期间的事实优先级为：

当前 HEAD 的真实源码和测试
    >
本 Stage K Final Plan
    >
Accepted Decisions
    >
Stage K Task Cards
    >
正式 Evidence
    >
TASKS / EXPERIMENT_PLAN live status
    >
历史计划和历史 snapshot

历史文档不得删除，但历史 snapshot 不能覆盖当前状态。

本计划在 K0 freeze commit 后冻结。后续技术合同变化必须：

STOP
→ 保存实际事实
→ 追加新 Decision
→ 修改后续未执行任务

不得静默改写本计划或旧 Decision。

⸻

3. 核心研究问题

Stage K 回答：

1. 冻结的 YOLOv8n ONNX 模型能否在 Jetson TensorRT 10.3 环境中构建可执行的 FP16-enabled mixed-precision Engine？
2. TensorRT Backend 能否在不改变 Preprocessor、PostProcessor、Detection 和 SerialRunner 语义的情况下替换 ORT Backend？
3. TensorRT 相对同机、same-commit ORT CPU k5 能降低多少 backend host-roundtrip latency 和 serial pre-sink latency？
4. TensorRT 串行运行能否在 30 分钟连续测试中保持输出、内存、温度和运行状态稳定？

核心自变量：

Inference Backend:
ONNX Runtime CPU
        ↓
TensorRT FP16-enabled mixed precision

Stage K 不同时修改 Runtime Scheduling，避免 TensorRT backend substitution 与 Pipeline scheduling 两个变量混杂。

⸻

4. Stage J、Stage T、Stage K 和 Stage P

正式阶段关系：

Stage J
Jetson ORT CPU Serial Baseline
        ↓
COMPLETE
Stage K
TensorRT FP16-Enabled Serial Backend
        ↓
Engine + Correctness + Serial Benchmark + Stability
        ↓
COMPLETE
Stage P
Student-Grade TensorRT Pipeline Optimization
        ↓
TensorRT Serial vs TensorRT Pipeline
        ↓
Project Experimental Closure

命名规则：

* Stage K 是 TensorRT Serial Backend 的正式实施阶段。
* 历史 Stage T 是未实施的 TensorRT 占位名称。
* Stage T 历史记录不删除、不回写，但不再作为独立实施阶段。
* Stage P 是 Pipeline 的正式历史名称。
* 不使用 Stage L 指代 Pipeline。

Stage J 的关闭状态、接受限制和最终 Evidence 保持有效。

Stage K：

* 不重新打开 Stage J；
* 不修改 Stage J Evidence；
* 不修改冻结 ONNX、ModelContract、Preprocessor 或 PostProcessor 数值语义；
* 不重新执行已经被最终关闭方案取代的 Stage J 草案 Gate；
* 在性能比较中重新执行 same-commit ORT k5 control；
* 不直接使用 Stage J 历史性能数字计算 Stage K 正式 speedup。

Stage P 已确定为项目必做范围，但在 Stage K 关闭前不得实施。

⸻

5. 阶段范围

5.1 Stage K 包含

* TensorRT Platform Acceptance；
* 离线 Engine 构建和冻结；
* Engine Manifest；
* RuntimeConfig v3；
* TensorRT Result JSON schema v2；
* Optional TensorRT CMake support；
* TensorRtEngine；
* Backend Factory；
* 16-tensor Level B validation；
* 16-image Level C validation；
* same-commit C++ ORT regression control；
* 20-image benchmark workload semantic preflight；
* ORT CPU k5 与 TensorRT 串行性能比较；
* TensorRT 30 分钟稳定性测试；
* 研究级 Evidence consolidation；
* Stage K Final Report。

5.2 Stage K 排除

CUDA preprocessing
pinned host staging optimization
GPU NMS
custom CUDA kernel
multiple CUDA streams
multiple TensorRT execution contexts
pipeline concurrency
dynamic batching
batch > 1
dynamic shape
INT8
DLA
camera
ROS 2
DeepStream
TensorRT Execution Provider
model retraining
ONNX re-export

上述项目不得以“顺便优化”为由进入 Stage K。

⸻

6. 已验证起点

6.1 Git 起点

计划起点：

Branch:
main
Commit:
e49f28dd60a49493538d1fd65e5e8fd81676e277
Tag:
stage-j-complete-v1.0

K0 开始前必须验证：

* 当前 main 指向上述 commit；
* tag 指向 Stage J 关闭起点；
* worktree clean；
* 无未纳入计划的本地修改；
* 无未说明的 ahead/behind 状态影响起点。

起点发生变化时：

STOP
→ 记录新 HEAD
→ 对比 stage-j-complete-v1.0
→ 判断变化是否只属于已接受的文档或合并操作

不得静默从不同起点创建开发分支。

6.2 开发分支

正式分支：

feature/jetson-tensorrt-fp16

创建顺序：

完成 K0 正式计划文件
        ↓
追加 D055–D061
        ↓
完成必要 live-status 文档修订
        ↓
创建 K0 freeze commit
        ↓
从该 commit 创建 feature/jetson-tensorrt-fp16
        ↓
授权 K1

Codex 不执行：

* push；
* merge；
* tag。

6.3 平台

已知：

Device:
Jetson Orin Nano Super
Architecture:
aarch64
Jetson Linux:
L4T R36.5
JetPack:
6.2.2
CUDA path:
/usr/local/cuda-12.6
TensorRT:
10.3.0.30
cuDNN:
9
Power mode:
MAXN_SUPER

nvcc: command not found 只表示 shell PATH 中未找到 nvcc。

Stage K 不编写 .cu 文件，因此：

* nvcc 不在 PATH 不单独阻塞；
* CUDA Runtime headers、libcudart、TensorRT headers 或 runtime 无法被普通 C++ 编译、链接或运行才阻塞。

6.4 冻结模型

ONNX:
models/onnx/yolov8n_neudet_frozen.onnx
ONNX SHA256:
c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944
ModelContract SHA256:
9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190
Input:
float32 [1,3,640,640] NCHW
Output:
float32 [1,10,8400] BCN
Batch:
1

禁止：

* 重新导出 ONNX；
* 修改 ModelContract 适配 TensorRT；
* 重新训练；
* 修改类别顺序；
* 修改 Preprocessor 或 PostProcessor 数值语义。

⸻

7. TensorRT 技术路线

Frozen ONNX
    ↓
official trtexec offline build
    ↓
Fixed serialized Engine
    ↓
TensorRtEngine : IInferenceEngine
    ↓
Existing CPU Preprocessor
    ↓
Existing CPU PostProcessor
    ↓
Existing SerialRunner

采用：

Direct TensorRT C++ Runtime API

排除：

ONNX Runtime TensorRT EP
ORT provider fallback
runtime ONNX parsing
runtime Engine build

理由：

* 不重新构建 ORT GPU SDK；
* 避免 TensorRT、CUDA 和 CPU fallback 造成性能归因不清；
* 符合现有 IInferenceEngine；
* 能体现 Runtime、Engine、ExecutionContext、CUDA stream 和 buffer 生命周期管理；
* 符合端侧 AI 部署岗位能力展示。

⸻

8. FP16 表述

“TensorRT FP16”表示：

FP16 builder mode enabled

不表示：

所有层强制使用 FP16
所有算子使用 FP16
全部内部计算均为 FP16

正式报告使用：

TensorRT 在启用 FP16 builder mode 后，根据算子支持和 tactic selection 生成混合精度执行计划，Host I/O 保持 FP32。

Engine 合同：

FP16 builder mode:
enabled
Engine precision:
mixed precision allowed
Host input dtype:
FP32
Host output dtype:
FP32
Input shape:
[1,3,640,640]
Output shape:
[1,10,8400]
Batch:
1
Dynamic shape:
disabled
INT8:
disabled
DLA:
disabled
Custom plugin:
disabled
Embedded NMS:
disabled

Engine I/O 实际变为 FP16 时：

STOP
→ 保存 Engine inspection
→ 新增 Decision

不得在 TensorRtEngine 内静默改变公开 HostTensor dtype 合同。

⸻

9. Engine 离线构建

Engine 必须通过 trtexec 离线构建。

生产应用：

* 不读取实际 ONNX 文件；
* 不调用 ONNX Parser；
* 不执行 tactic selection；
* 不构建或覆盖 Engine；
* 只验证 Engine 和 Manifest；
* 只反序列化并执行固定 Engine。

9.1 D062

K1 完成后、K2 正式构建前，追加：

D062 — Freeze Exact TensorRT Engine Build Contract

D062 记录：

* trtexec 实际路径；
* TensorRT 和 trtexec 版本；
* 实际 trtexec --help 语义；
* exact build command；
* memory-pool/workspace 参数名；
* memory-pool 数值；
* FP16 flag；
* FP32 input/output format 参数；
* saveEngine 语义；
* skipInference 语义；
* loadEngine smoke 命令；
* Engine 输出路径；
* build log 路径；
* Engine inspection 方法。

D062 接受前：

K2 formal build:
NOT_AUTHORIZED

9.2 Build 与 Smoke 分离

Build command
    ↓
Engine artifact
    ↓
Complete build log
    ↓
Engine inspection
    ↓
Independent load-engine smoke

Build 语义包括：

source ONNX
FP16 builder mode
static batch=1
static input shape
serialized Engine
skip build-time inference
explicit memory-pool limit
explicit FP32 I/O when supported

随后用独立 load-engine 命令执行 smoke。

⸻

10. Engine Manifest

.engine 文件 local-only，不提交 Git。

建议本地目录：

/home/orin/edge-ai-local-models/stage_k/

仓库跟踪：

models/tensorrt/README.md
models/tensorrt/<engine-id>.manifest.json

Manifest 至少记录：

schema_version
artifact_kind
engine_id
engine_sha256
engine_size_bytes
source_onnx_sha256
model_contract_sha256
TensorRT version
CUDA version
L4T version
Jetson model
SoC/GPU architecture
compute capability when available
build device description
FP16 builder mode
memory-pool limit
input/output tensor names
input/output shapes
input/output dtypes
batch
exact build command semantics
build log SHA256
source Git commit
plugin usage
limitations

失效条件：

* ONNX 变化；
* ModelContract 变化；
* Engine SHA 变化；
* I/O contract 变化；
* TensorRT Runtime 不兼容；
* GPU architecture 或平台类别变化；
* precision、shape、memory-pool 或正式构建参数变化。

设备序列号、UUID 和具体物理设备身份不作为硬失效条件。

Engine 不要求 byte-identical rebuild。

正式规则：

一次正式构建
→ 冻结一个 Engine SHA
→ K5/K6/K7/K8 使用同一 Engine

⸻

11. TensorRtEngine 合同

公开接口：

Status run(
    const HostTensor& input,
    HostTensor* output);

不引入公开 DeviceTensor。

内部顺序：

validate HostTensor
    ↓
ordered H2D on one stream
    ↓
setTensorAddress
    ↓
enqueueV3
    ↓
ordered D2H on same stream
    ↓
cudaStreamSynchronize
    ↓
validate output
    ↓
commit owned HostTensor

inference_ms：

backend host-roundtrip latency
=
H2D
+
TensorRT execution
+
D2H
+
synchronization

不得称为纯 GPU Kernel Latency。

CUDA Event device execution time可以记录，但只是辅助诊断指标。

初始化：

* 验证 Engine Manifest；
* 验证 Engine SHA；
* 验证实际 ModelContract SHA；
* 验证 Manifest source ONNX SHA 与 ModelContract expected ONNX SHA；
* 创建 TensorRT Runtime；
* 反序列化 Engine；
* 创建一个 ExecutionContext；
* 创建一个 CUDA stream；
* 枚举 TensorRT 10.x named I/O tensors；
* 验证 tensor name、mode、shape 和 dtype；
* 一次性分配 persistent CUDA device buffers；
* 准备必要的内部 host staging storage。

运行期间禁止：

* 每帧 cudaMalloc/cudaFree；
* 每帧创建 stream；
* 每帧创建 ExecutionContext；
* 多 stream；
* 多 ExecutionContext；
* ORT fallback；
* 隐藏 CUDA/TensorRT error；
* 修改 tensor shape；
* 异步公开 API。

不要求：

所有 HostTensor 输出都零 allocation

现有合同仍允许为调用方返回独占 HostTensor。硬 Gate 只禁止每帧 CUDA resource allocation 和 backend resource reconstruction。

失败时：

* 返回明确 Status；
* 不替换调用方既有 output；
* 不提交部分结果。

⸻

12. RuntimeConfig v3

schema_version: 3
backend:
  type: tensorrt_fp16
tensorrt:
  engine_path: /path/to/model.engine
  engine_manifest_path: /path/to/engine_manifest.json
  device_id: 0
runtime:
  opencv_num_threads: 1
model:
  contract_path: /path/to/model_contract.yaml
input:
  type: directory
  directory: /path/to/corpus
output:
  json_path: /path/to/result.json
  console: false
  overwrite: false
postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680
  agnostic: false

字段命名继承 RuntimeConfig v2 的 conf_threshold 语义；v2 parser 将 multi_label 固定为 false，因此 v3 不新增可配置 multi_label。

明确不包含：

model.source_onnx_path
onnxruntime
timing
benchmark
pipeline

源 ONNX 的身份只存在于：

* Engine Manifest；
* ModelContract；
* K2/K5/K7 preflight；
* Evidence provenance。

12.1 Parser

parse schema_version
        ↓
version-aware dispatch
    ├── v1 legacy ORT
    ├── v2 Jetson ORT CPU
    └── v3 TensorRT

要求：

* v1/v2 行为不变；
* v3 只接受 tensorrt_fp16；
* v2 拒绝 TensorRT section；
* v3 拒绝 onnxruntime section；
* 未知、缺失、重复字段 fail-fast；
* 禁止环境变量覆盖；
* 公共 input/output/postprocess/path helper 可复用；
* 不复制完整 v2 parser；
* 不建设通用 backend plugin 配置框架。

RuntimeConfig schema 和 Result JSON schema 是独立命名空间：

RuntimeConfig v3
can produce
Result JSON v2

二者版本号不要求一致。

⸻

13. Result JSON schema v2

ORT 保持 Result JSON schema v1。

TensorRT 使用 Result JSON schema v2。

定义：

Result JSON v2
=
v1 image/detection/postprocess/timing/summary body
+
TensorRT backend and model metadata

示意：

{
  "schema_version": 2,
  "backend": {
    "type": "tensorrt_fp16"
  },
  "model": {
    "artifact_kind": "tensorrt_engine",
    "filename": "model.engine",
    "sha256": "<engine-sha256>",
    "source_onnx_sha256": "<onnx-sha256>",
    "engine_manifest_filename": "<manifest-filename>",
    "contract_filename": "<contract-filename>",
    "classes": []
  }
}

必须继续复用：

* image identity；
* sequence index；
* image width/height；
* detection entries；
* postprocess parameters；
* per-frame timing；
* summary；
* deterministic field/order semantics；
* atomic final commit。

内部：

* 共用 JsonSink 主体；
* 共用 Detection serializer；
* backend-specific metadata branch；
* 不新增大型 JsonSinkV2 平行实现；
* 不建设 schema registry；
* 不引入大型 JSON DOM dependency。

现有 metadata 与 sink 当前严格绑定 schema v1 和 onnxruntime_cpu，因此 v2 是必要的最小扩展，而不是重新建设结果系统。

⸻

14. candidate_index

现有 Detection 和 Result JSON 已包含 candidate_index。

规则：

1. Stage J Detection 不修改。
2. ORT Result JSON v1 不修改。
3. TensorRT Result JSON v2 保留 candidate_index。
4. 它是 raw BCN candidate dimension 的零基索引。
5. 不参与常规 Level C compatibility edge 构造。
6. 不单独证明 threshold crossing。
7. Boundary classification 必须结合 raw confidence、raw bbox 和最终结果。
8. 不新增第二套 public candidate identity API。

⸻

15. CMake

新增：

option(
    EDGE_AI_ENABLE_TENSORRT
    "Enable TensorRT backend"
    OFF
)

OFF：

* 不搜索 CUDA；
* 不搜索 TensorRT；
* 不编译 TensorRT backend；
* WSL/x86 ORT build 和 tests 保持不变。

ON 硬依赖：

cuda_runtime_api.h
libcudart.so
NvInfer.h
libnvinfer.so

条件依赖：

NvInferPlugin.h
libnvinfer_plugin.so

Plugin 默认仅记录。K2 Engine inspection 证明 Engine 需要 plugin 时：

STOP
→ 保存事实
→ 新增 Decision
→ 升级为运行时依赖

构建：

edge_ai_backend_trt

建议最小文件：

tensorrt_engine.cpp
tensorrt_engine_manifest.cpp
tensorrt_logger.cpp
cuda_status.cpp

继续使用：

project(... LANGUAGES CXX)

不启用 CMake CUDA language，不编写 .cu。

TensorRT-enabled Jetson Release build必须同时支持：

onnxruntime_cpu
tensorrt_fp16

正式 ORT/TRT 比较使用同一 executable SHA。

⸻

16. Backend Factory

Status create_inference_engine(
    const RuntimeConfig& config,
    const ModelContract& contract,
    std::unique_ptr<IInferenceEngine>* output);

分派：

onnxruntime_cpu
    → OnnxRuntimeEngine
tensorrt_fp16
    → TensorRtEngine

规则：

* SerialRunner 不出现 TensorRT/CUDA 类型；
* Preprocessor、PostProcessor、DirectorySource 不感知 backend；
* Sink 不感知具体推理实现；
* 不实现动态注册；
* 不实现自动 fallback；
* TensorRT 初始化失败直接返回明确错误；
* 初始化失败后 Sink 不提交结果。

当前 application 直接构造 OnnxRuntimeEngine，Stage K 只将这一点替换为最小 factory，不重构整个 application。

⸻

17. Correctness Authority

Python ORT explicit Reference
        >
C++ ORT same-commit regression control
        >
TensorRT candidate

TensorRT tolerance 不得反向修改 ORT control。

需要区分：

ORT Level B cross-architecture control
ORT Level C strict semantic control
TensorRT mixed-precision candidate tolerance

⸻

18. 16-tensor Reference Bundle

名称：

stage_k_level_b_reference_v1

来源：

Stage J frozen 16-image correctness corpus
+
existing explicit Python preprocessing
+
frozen ONNX
+
Python ONNX Runtime 1.23.2

16-image corpus固定使用 J4.3 v2 的：

12 JPG + 4 derived BMP
corpus manifest SHA:
687682f37d1affbe8813a9e7287b42dc28a9a8b9ea8d67f8b85175960f3e2dcd

Stage J 已验证该 corpus 为 16 图，并完成 16/16 Level C。

18.1 生成环境

使用 Stage J 已验证的 WSL Reference 环境：

WSL2 x86_64
Python 3.10.12
ONNX Runtime 1.23.2
OpenCV 4.10.0
NumPy 1.26.4

该环境和版本已有正式记录。

不要求在 Jetson 安装 Python ORT。

流程：

WSL verified corpus
    ↓
generate 16 input tensors and Python raw outputs
    ↓
freeze manifest and SHA
    ↓
archive canonical bundle
    ↓
copy to Jetson
    ↓
verify every SHA on Jetson

WSL 缺少 prepared corpus 时，可以：

* 根据冻结 manifest 从原始 NEU-DET 恢复；或
* 从现有已验证 Jetson corpus 反向复制到 WSL。

无论采用哪条路径，都必须先验证 corpus manifest、文件 SHA 和尺寸；不得使用未验证的近似图片。

18.2 内容

每张图：

FP32 NCHW input:
[1,3,640,640]
Python ORT FP32 raw output:
[1,10,8400]

格式：

little-endian float32 raw binary

18.3 Manifest

至少记录：

schema_version
bundle_id
artifact_kind
generator script and SHA
source Git commit
source corpus manifest SHA
model ONNX SHA
ModelContract SHA
Python version
ONNX Runtime version
OpenCV version
NumPy version
preprocess contract identity
tensor contracts
creation timestamp
limitations
entries

每个 entry：

image_id
corpus-relative identity
source image SHA
original width/height
input tensor filename/SHA/size/dtype/shape/layout
Python raw-output filename/SHA/size/dtype/shape/layout

18.4 Retention

不提交：

* 16 input tensors；
* 16 Python raw outputs；
* TensorRT raw outputs。

Git 跟踪：

* README；
* bundle manifest；
* SHA list；
* generator identity；
* generation report；
* archive provenance。

Jetson位置：

/home/orin/edge-ai-local-evidence/stage_k/reference/
stage_k_level_b_reference_v1/

不要求 byte-identical regeneration。

⸻

19. C++ ORT Same-Commit Control

19.1 Level B：两层判定

比较：

WSL Python ORT FP32
vs
same-commit Jetson C++ ORT FP32

每个 tensor首先计算 strict Gate：

shape exact
element count exact
finite exact
overall MAE <= 1e-6
overall max_abs <= 1e-4

但 strict Gate 不是唯一合法关闭路径，因为 Stage J 已确认 WSL→Jetson ORT 存在已接受的跨架构数值差异。

如果任一 tensor未通过 strict Gate，则使用 Stage K 的 D048-derived cross-architecture Gate：

shape exact
element count exact
finite exact
overall MAE <= 1e-5
overall max_abs <= 0.01
bbox max_abs <= 0.01
score max_abs <= 1e-4

同时要求：

* 每个 tensor执行两次独立 Jetson C++ ORT inference；
* 两次输出 byte-identical；
* 两次输出 SHA 一致；
* 记录并冻结每个 tensor 的 Jetson C++ ORT canonical SHA；
* 16/16 tensors通过 D048-derived Gate。

ORT Level B disposition：

ORT_CONTROL_PASS_STRICT

或：

ORT_CONTROL_PASS_WITH_INHERITED_CROSS_ARCH_NUMERICAL_LIMITATION

否则：

ORT_CONTROL_FAIL

该 inherited limitation 必须在 K5/K9 报告中披露，但它不属于 TensorRT FP16 boundary variation。

19.2 Level C

比较：

J4.3 frozen 16-image Python detection Reference
vs
same-commit C++ ORT result

使用 Stage J strict Gate：

class exact
detection count exact
confidence abs error <= 1e-4
each bbox coordinate error <= 0.01 original-image px
16/16 PASS

现有 Stage J comparator继续用于 ORT control，不修改其 backend 和 tolerance。现有历史 J4.3 正是以这一 Gate 完成 16 图最大匹配验证。

⸻

20. TensorRT Level B Gate

Raw output：

[1,10,8400]
channels 0–3:
cx, cy, w, h
channels 4–9:
class scores

所有指标逐 tensor 计算，16/16 PASS。

20.1 Score

Score MAE <= 2e-3
Score Type-7 P99 absolute error <= 5e-3
Score max absolute error <= 2e-2

同时：

shape exact
element count exact
finite exact

20.2 Bbox

在 640×640 model-input quantity space 中：

BBox MAE <= 0.5
BBox Type-7 P99 absolute error <= 1.5
BBox max absolute error <= 4.0

同时：

shape exact
element count exact
finite exact

20.3 Percentile

P99：

Hyndman–Fan Type 7

项目现有 benchmark helper 已冻结使用 Type 7 percentile 和 n-1 sample standard deviation。

Aggregate 和 per-channel metrics记录，但不能替代逐 tensor Gate。

⸻

21. TensorRT Level C Gate

坐标：

inverse LetterBox
+
clipping
→
original-image xyxy

匹配：

class-separated deterministic maximum bipartite matching

每个 matched detection：

class_id exact
confidence abs error <= 1e-2
x1 error <= 1.0 original-image px
y1 error <= 1.0 original-image px
x2 error <= 1.0 original-image px
y2 error <= 1.0 original-image px

IoU、center distance 和平均 bbox error可记录，但不替代逐坐标 Gate。

新增：

stage_k_level_c_compare.py

可复用：

* Stage J maximum matching；
* adversarial matching tests；
* strict JSON helpers；
* tolerance-independent geometry helpers。

不得：

* 修改 Stage J comparator；
* 让 Stage J comparator 接受 TensorRT；
* 动态放宽 tolerance；
* 只依赖 final JSON判断 threshold crossing。

⸻

22. Threshold-Boundary Policy

confidence threshold:
0.25
boundary band:
[0.245,0.255]

只有全部满足才是 boundary variation：

1. 一侧存在 unmatched final detection；
2. 另一侧不存在；
3. 其他 detections 正常匹配；
4. detection-count 差值与 case 数一致；
5. candidate index 已知；
6. 双方检查相同 raw candidate；
7. argmax class一致；
8. 不用空间相似的其他 candidate替代；
9. 一侧 confidence >0.25；
10. 另一侧 <=0.25；
11. 两侧均在 [0.245,0.255]；
12. confidence error <=0.01；
13. raw width/height有效；
14. raw cx,cy,w,h 各分量 error <=1.0；
15. restored x1,y1,x2,y2 各坐标 error <=1.0 px；
16. 缺失侧在 confidence filter 阶段被丢弃。

不能归类为 boundary variation：

both sides pass threshold
NMS suppression difference
max_nms difference
max_det difference
class change
candidate replacement
invalid bbox
non-finite value
clipping-induced semantic disappearance

数量：

maximum across 16-image corpus:
2
maximum per image:
1

⸻

23. Targeted Diagnostics

默认保存：

* Python ORT raw outputs；
* TensorRT raw outputs；
* Python final detections；
* TensorRT final detections；
* Level B report；
* Level C report。

只在 mismatch 或疑似 boundary case 时生成 targeted diagnostic：

image_id
candidate_index
Python raw cx/cy/w/h
TensorRT raw cx/cy/w/h
Python class scores
TensorRT class scores
Python argmax class/confidence
TensorRT argmax class/confidence
threshold decision
Python restored bbox
TensorRT restored bbox
final presence
classification reason

不预建：

all-candidate NMS trace
suppression graph
full replay database
generic provenance framework

⸻

24. K5 状态

临时状态：

K5 INVESTIGATION_REQUIRED

触发：

unmatched detection found
AND
classification not completed

最终状态：

K5 PASS

ORT Level B control accepted
ORT Level C strict PASS
TensorRT Level B 16/16 PASS
TensorRT matched Level C PASS
boundary cases = 0
unexplained divergence = 0

K5 PASS_WITH_REPORTED_NUMERICAL_BOUNDARY_VARIATION

ORT controls accepted
TensorRT Level B PASS
matched detections PASS
boundary cases = 1 or 2
max 1 per image
all cases satisfy boundary policy
unexplained divergence = 0

K5 FAIL

任一：

ORT_CONTROL_FAIL
ORT Level C regression
any TensorRT Level B tensor failure
non-finite output
shape failure
class change
matched confidence/bbox failure
unexplained unmatched detection
more than 2 boundary cases
more than 1 case per image
NMS divergence
candidate replacement
post-confidence-filter divergence

ort_control_disposition 作为独立字段记录：

STRICT
or
INHERITED_CROSS_ARCH_LIMITATION

不额外扩张 K5 最终状态枚举。

⸻

25. Stage K Profile Runner

现有 stage_j_profile_runner 不修改，因为它明确只接受 RuntimeConfig v2 和 onnxruntime_cpu。

新增薄封装：

stage_k_profile_runner

它：

* 接受 RuntimeConfig v2 ORT；
* 接受 RuntimeConfig v3 TensorRT；
* 使用同一 application backend factory；
* 复用 RunOptions.timing_enabled_override；
* 复用 TraceRecorder；
* 输出既有 FrameTrace JSONL；
* 不在 RuntimeConfig 增加 benchmark section；
* 不在 production CLI 增加 benchmark mode。

不得建设：

* 新通用 Profiler；
* 新 Benchmark Framework；
* 第二套 runtime；
* 第二套 preprocess/postprocess。

⸻

26. 20-image Benchmark Semantic Preflight

正式 benchmark corpus：

tests/data/m5/manifests/benchmark_corpus.json
SHA256:
235b062cb82166709e2ff800ec71bf92396d5348508281f822ef116d5f0962ab

权威 detection reference：

results/benchmark/jetson_ort_cpu/python_reference/
j5_1_python_reference_v1/
Reference SHA256:
1c31cfd41b4377c989baf35d57352280bb84f26b1942a8e26ac60076e61392a7

该 Reference 的环境已记录为 WSL x86_64、Python ORT 1.23.2，且 corpus manifest和 reference SHA均冻结。

K6/K7 前必须执行：

ORT application control

J5.1 Python Reference
vs
same-commit ORT k5 application

使用 Stage J Level C strict tolerance。

TensorRT application control

J5.1 Python Reference
vs
TensorRT application

使用 Stage K TensorRT Level C matched tolerances和 boundary policy。

出现 20-image unmatched detection：

K6 INVESTIGATION_REQUIRED
→ 仅为对应图片生成 Python/TRT raw output
→ targeted diagnosis

不为 20 图预先建设第二套完整 Level B bundle。

Semantic preflight完成后冻结：

TensorRT 20-image canonical detection-cycle SHA

K7 和 K8 使用该 SHA检查 cycle drift。

⸻

27. K7 Formal Benchmark

27.1 条件

Device:
same Jetson
Executable:
same binary SHA
Source commit:
same
TensorRT Engine:
same frozen SHA
ModelContract:
same SHA
Corpus:
same frozen 20 images
Runtime:
Serial
Preprocessor:
same
PostProcessor:
same
OpenCV threads:
1
CPU affinity:
CPU 1–5 for both
Power mode:
MAXN_SUPER
jetson_clocks:
enabled
Fan:
fixed and identical
Batch:
1

ORT：

backend:
onnxruntime_cpu
intra:
5
inter:
1

TensorRT：

backend:
tensorrt_fp16
ExecutionContext:
1
CUDA stream:
1

27.2 Config identity

不得要求配置 SHA 相同。

要求：

* ORT v2 canonical template有冻结 SHA；
* TensorRT v3 canonical template有冻结 SHA；
* 每个 resolved run config有准确 SHA；
* output/trace路径导致 SHA 不同是允许的；
* backend-specific 字段允许不同；
* shared runtime semantics必须等价。

RuntimeConfig shared-field validator至少检查：

input corpus identity and ordering
ModelContract identity
OpenCV thread count
confidence/iou thresholds
max_nms
max_det
max_wh
agnostic
output console policy

Timing stage definitions不属于 v2/v3 YAML shared fields，由以下事实独立验证：

same stage_k_profile_runner
same executable SHA
same TraceRecorder schema
same timing field definitions

Preflight分别输出：

config_integrity:
PASS
shared_runtime_semantics:
PASS
runner_timing_semantics:
PASS

不得输出虚假的：

config_sha_equal:
PASS

27.3 规模

每个 backend：

5 independent processes
60 warmup frames
500 measured frames
25 measured corpus cycles

顺序：

Pair 1: ORT → TRT
Pair 2: TRT → ORT
Pair 3: ORT → TRT
Pair 4: TRT → ORT
Pair 5: ORT → TRT

每个 run独立：

* output；
* trace；
* telemetry；
* run ID；
* resolved config。

27.4 Preflight

每个 process前验证：

source commit
executable SHA
platform
power mode
jetson_clocks
fan policy
start temperature
CPU affinity
ModelContract SHA
ONNX or Engine SHA
corpus manifest SHA
runtime config SHA
shared semantics
runner timing semantics
no conflicting target process

记录 start/end temperature。

不建设自动 cooldown controller。

明确 thermal throttling：

invalidate run
→ preserve run record
→ repeat only that run

不要求起始温度小数值完全相同。

27.5 Timing

source_ms
preprocess_ms
inference_ms
postprocess_ms
pre_sink_total_ms
wall FPS

TensorRT：

inference_ms = backend host-roundtrip latency

辅助：

CUDA Event device execution
trtexec GPU compute

辅助 GPU timing不得与 host-roundtrip混用。

27.6 统计

独立单位：

one process run

Primary：

* 每 run mean/P50/P95/P99；
* 5 个 run summary 的 mean；
* sample SD，n-1；
* 5 个 paired backend speedups；
* 5 个 paired pre-sink speedups；
* 5 对是否同方向。

Secondary：

* pooled 2,500-frame distribution；
* pooled percentile；
* histogram。

Pooled frames不能当作 2,500 个独立重复。

Percentile：

Hyndman–Fan Type 7

27.7 Speedup

paired_backend_speedup_i =
ORT paired-run backend P50
/
TRT paired-run backend P50
paired_serial_speedup_i =
ORT paired-run pre-sink P50
/
TRT paired-run pre-sink P50

不得：

* backend latency 对比 E2E latency；
* FPS ratio与 latency ratio混写；
* 用 Stage J 历史数字计算正式 speedup。

27.8 状态

COMPLETE_WITH_LOWER_MEASURED_LATENCY

条件：

mean(TRT run-level backend P50)
<
mean(ORT run-level backend P50)
AND
mean(TRT run-level pre-sink P50)
<
mean(ORT run-level pre-sink P50)

否则：

COMPLETE_WITHOUT_LOWER_MEASURED_LATENCY

报告必须给出实际数值，不写“显著提升”或“统计显著”。

最低 Gate：

zero correctness failure
zero application failure
non-zero GPU activity
all 10 runs valid
formal ORT/TRT data complete

不预设 2×、5×门槛。

⸻

28. K8 TensorRT Stability

执行：

TensorRT SerialRunner
20-image repeated corpus
duration >= 1800 seconds
one formal continuous run

不重新执行 ORT 30 分钟 stability。

复用 Stage J J6 的：

* wall-clock规则；
* cycle/frame计数；
* canonical cycle hash；
* hash drift；
* VmRSS采样与分析；
* temperature/frequency采集；
* unavailable分类；
* failure记录；
* analyzer和报告语义。

不重新设计新的 memory-growth 或 thermal模型。

新增：

Engine SHA
CUDA error count
TensorRT error count
GPU utilization
GPU frequency
TensorRT canonical cycle SHA

必须记录：

duration
cycles
frames
failed frames/cycles
canonical detection hash
hash drift
VmRSS timeline
CPU/GPU utilization
temperature
CPU/GPU frequency

可选：

VDD_IN
rail power
EMC metrics

可选缺失：

unavailable_on_platform

Gate：

duration >= 1800 s
0 crash
0 failed frame
0 failed cycle
0 hash drift
Stage J J6-compatible VmRSS verdict PASS
no recorded thermal-throttling event
mandatory telemetry valid under inherited J6 rules

允许继承 J6 已接受的 isolated startup/final-sample缺失语义，但必须披露。

不得声称功耗改善，除非 power telemetry真实可用并支持该结论。

⸻

29. Evidence

正式 Evidence：

K1 Platform Acceptance
K2 Engine Build
K5 Correctness
K7 Benchmark
K8 Stability
K9 Consolidation

工程实施记录：

K3 Build/Config
K4 TensorRtEngine
K6 Application Integration

K3/K4/K6仅保存：

* source commit；
* commands；
* tests；
* short report；
* limitations。

正式 Evidence 最低包含：

README
report
provenance
verification result
commands
sha256 list

保留：

* Engine build log；
* raw correctness metrics；
* per-frame timings；
* telemetry；
* formal failure records；
* environment snapshot。

不要求：

* Engine byte-identical rebuild；
* 所有中间文件永久保留；
* 多层审计链；
* Artifact Database；
* 工业认证语义。

⸻

30. Attempt Retention

必须保留：

* 正式 K2 attempts；
* 正式 K5 attempts；
* 正式 K7 attempts；
* 正式 K8 attempts；
* 导致 Decision 或计划变化的失败。

可清理：

* scratch build；
* 编译中间目录；
* CLI 拼写错误；
* 临时路径错误；
* 未进入正式 attempt 的调试输出；
* 重复非正式 Reference Bundle。

正式 attempt：

immutable
non-overwriting
retry uses new ID

Tooling bug和实验失败分开分类。

⸻

31. K0 Test Inventory

configs/stage_k/test_inventory.yaml 不完整复制 Stage J inventory。

它包含：

schema_version
inventory_kind
status
source commit
Stage J inventory path/SHA
fresh K0 baseline CTest counts
TensorRT OFF inherited regression classes
planned Stage K capability tests
platform classification
planned/not-yet-registered status

规则：

1. 当前已存在测试按 fresh configure事实记录。
2. 尚未实现的 Stage K 测试标记为 planned_requirement。
3. 不为 planned tests虚构 CTest name、source line或 PASS 状态。
4. K3/K4 后可生成实现后的 verification snapshot，但不回写冻结 K0 inventory。
5. Stage J inventory不修改。

⸻

32. 里程碑

K0 — Planning Freeze

输出：

docs/personal/STAGE_K_EXECUTION_PLAN.md
docs/personal/STAGE_K_TASK_CARDS.md
configs/stage_k/test_inventory.yaml
D055–D061

同时最小修订 live-status 文档：

docs/personal/TASKS.md
docs/personal/EXPERIMENT_PLAN.md
docs/PROJECT_BRIEF.md current-stage boundary
README.md current status when present

对 ARCHITECTURE.md、REQUIREMENTS.md、ENVIRONMENT.md、AGENTS.md 只做 focused consistency scan；仅在存在 Stage K/Stage T/Stage P live-status冲突时局部修改。

禁止：

* 重写稳定全局文档；
* 删除历史 snapshot；
* 修改 Stage J final reports或 Evidence。

K0 操作：

verify starting HEAD
write final plan
write task cards
write compact test inventory
append D055–D061
update live status minimally
run focused consistency check
record plan/task/inventory SHA
create K0 freeze commit
create feature branch from freeze commit

K0 不执行：

* Jetson TensorRT command；
* compile/link smoke；
* trtexec；
* Engine build；
* production code changes。

Gate：

K0 COMPLETE
K1 READY

K1 — Platform Acceptance

确认：

readlink -f /usr/local/cuda
/usr/local/cuda/bin/nvcc --version
cuda_runtime_api.h
libcudart.so
NvInfer.h
libnvinfer.so
trtexec path/version/help
tegrastats

最小 host-only C++ smoke：

g++
→ query CUDA device
→ create/destroy CUDA stream
→ create/destroy TensorRT Runtime
→ report runtime version

规则：

* nvcc 不在 PATH不阻塞；
* runtime/header/link失败才阻塞；
* 未经授权不安装或升级包；
* CUDA suffix差异记录，通过真实 smoke判断；
* plugin仅记录。

输出：

results/platform/tensorrt/k1_environment_v1/

Gate：

K1 PASS
D062 READY

D062 — Exact Build Contract

基于 K1 的真实 trtexec --help 冻结 exact command和 memory pool。

Gate：

D062 ACCEPTED
K2 READY

K2 — Engine Build and Freeze

执行：

* 验证 ONNX/Contract；
* formal attempt；
* exact build；
* 保存 stdout/stderr；
* Engine SHA；
* tensor inspection；
* independent load-engine smoke；
* Engine Manifest；
* identity freeze。

Gate：

parser/build PASS
deserialization PASS
input/output FP32
static shapes exact
tensor names exact
FP16 builder mode confirmed
INT8/DLA disabled
plugin dependency inspection complete
no plugin dependency under frozen contract
smoke PASS
Engine/Manifest verified

检测到 plugin dependency：

STOP
→ Decision

输出：

results/build/tensorrt/k2_fp16_engine_v1/

K3 — Build and Schema Foundation

实现：

* optional TensorRT CMake；
* RuntimeConfig v3；
* Result JSON v2 minimal extension；
* Manifest parser；
* Factory skeleton；
* logger/status；
* .engine ignore。

K4 — TensorRtEngine

实现：

* Runtime/Engine/Context/stream；
* named tensor API；
* persistent device buffers；
* synchronous HostTensor；
* finite/output checks；
* failure atomicity；
* RAII。

测试重点：

uninitialized/null input failures
contract mismatch
Engine/Manifest mismatch
I/O mismatch
no per-frame cudaMalloc/cudaFree
no per-frame stream/context construction
finite output
caller output unchanged on failure
cleanup

K3/K4可同一开发迭代。

K5 — Correctness

K5.1 16-tensor Reference Bundle
K5.2 same-commit ORT controls
K5.3 TensorRT Level B
K5.4 TensorRT Level C
K5.5 targeted investigation only when needed
K5.6 Correctness Gate

Gate：

K5 PASS
or
K5 PASS_WITH_REPORTED_NUMERICAL_BOUNDARY_VARIATION

K6 — Application and Benchmark Integration

实现：

* ORT v2 production path；
* TensorRT v3 production path；
* Stage K profile runner；
* TraceRecorder reuse；
* telemetry reuse；
* shared config semantics validator；
* benchmark analyzer adaptation；
* 20-image Python Reference preflight；
* TensorRT canonical cycle SHA。

Gate：

ORT v2 regression PASS
TensorRT v3 application PASS
20-image ORT semantic control PASS
20-image TensorRT semantic preflight PASS
timing trace PASS
telemetry PASS
benchmark preflight PASS

K7 — Formal Benchmark

输出：

results/benchmark/jetson_tensorrt_fp16/
k7_serial_backend_comparison_v1/

Gate：

10 valid runs
correctness intact
telemetry complete
statistics complete
descriptive performance status assigned

K8 — Stability

输出：

results/benchmark/jetson_tensorrt_fp16/stability/
k8_tensorrt_stability_v1/

Gate：

K8 COMPLETE

失败事实必须保留，不得缩短时间或更换 corpus。

K9 — Closeout

输出：

results/consolidation/stage_k/
stage_k_tensorrt_fp16_serial_v1/
docs/personal/STAGE_K_FINAL_REPORT.md

Consolidation：

README.txt
evidence_index.json
verification_report.json
attempt_registry.json
provenance.json
commands.txt
sha256sums.txt

更新：

TASKS.md
EXPERIMENT_PLAN.md
ENVIRONMENT.md
ARCHITECTURE.md
REQUIREMENTS.md
DECISIONS.md
PROJECT_BRIEF.md when required
README.md

状态：

Stage K:
COMPLETE
Stage P:
READY_FOR_PLANNING_REVIEW
Stage P implementation:
NOT_YET_AUTHORIZED

不得声明：

Production ready
Industrial validated
INT8 complete
Pipeline complete
GPU end-to-end complete

建议 tag：

stage-k-tensorrt-fp16-v1.0

由项目负责人执行。

⸻

33. D055–D061 FINAL

D055 — Resolve Stage K and Historical Stage T Naming

Stage K is the formal TensorRT serial backend stage.
Historical Stage T remains a non-executed placeholder.
Stage J closure, accepted limitations and final Evidence remain
historical facts.
Stage K does not reopen superseded Stage J draft gates.
Stage P remains the formal required downstream Pipeline stage.

D056 — Use Direct TensorRT C++ Runtime API

TensorRT candidate backend uses the direct TensorRT C++ Runtime API.
ONNX Runtime TensorRT EP, provider fallback and ORT GPU rebuild
are excluded.

D057 — Freeze Offline FP16-Enabled Engine Build

The Engine is built offline with trtexec.
FP16 builder mode is enabled.
The Engine is mixed precision; all-layer FP16 is not claimed.
Host I/O remains FP32.
Batch=1 and static 640×640 shape are frozen.
An explicit memory-pool limit and exact command must be frozen
by D062 after K1 and before formal K2 execution.

D058 — Preserve Synchronous HostTensor Backend Boundary

TensorRtEngine implements IInferenceEngine.
The public API remains synchronous HostTensor input/output.
inference_ms is backend host-roundtrip latency.
Execution uses one CUDA stream with ordered H2D, enqueueV3,
D2H and synchronization.
Persistent CUDA device buffers are required. Per-frame CUDA
allocation and per-frame stream or ExecutionContext creation are
prohibited. Caller-owned output remains an owned HostTensor, so
the Decision does not claim zero host allocation.
CUDA preprocessing, pinned-buffer optimization, GPU NMS,
multi-stream and Pipeline are excluded from Stage K.

D059 — Introduce RuntimeConfig v3 and Result Metadata v2

RuntimeConfig v3 accepts only tensorrt_fp16.
v1/v2 behavior remains unchanged.
v3 runtime requires Engine, Engine Manifest and ModelContract.
The actual source ONNX file is not a runtime dependency.
TensorRT support is optional through CMake.
ORT Result JSON schema v1 remains unchanged.
TensorRT Result JSON schema v2 is a minimal metadata extension
of the existing v1 image, detection, postprocess, timing and
summary body semantics.
The existing candidate_index field remains for compatibility and
diagnostic candidate identity, but it is not a normal matching
criterion or sufficient boundary evidence by itself.
The implementation reuses the existing sink and detection
serialization path and does not introduce a schema registry or
parallel sink framework.
RuntimeConfig and Result JSON schema versions are independent
version namespaces.

D060 — Freeze Correctness Authority and Numerical Policy

Python ORT explicit Reference remains authoritative.
C++ ORT is the same-commit regression control.
TensorRT is the candidate backend.
C++ ORT Level C retains the Stage J strict detection tolerances.
C++ ORT Level B first evaluates the Stage J strict raw-output Gate.
When that strict Gate is not met solely because of the already
accepted WSL-to-Jetson cross-architecture numerical behavior,
a D048-derived per-tensor Gate may close the control with an
explicit inherited cross-architecture limitation. The Jetson C++
ORT output must be repeatable and its per-tensor canonical SHA
must be recorded.
Level B uses 16 frozen image-derived tensors and per-tensor MAE,
Type-7 P99 where applicable, and max-absolute-error metrics.
The derivative Reference Bundle is generated in the existing
validated WSL Python ORT environment and transferred to Jetson
with SHA verification.
Level C uses original-image coordinates and deterministic maximum
matching.
Threshold-boundary variation requires exact candidate identity
and raw-output evidence. A targeted diagnostic record is generated
only when an actual mismatch or boundary case occurs.
A full all-candidate postprocess provenance or replay framework
is not a Stage K requirement.

D061 — Freeze Benchmark, Stability, Evidence and Downstream Scope

Formal comparison reruns ORT k5 and TensorRT from the same source
commit and the same executable SHA.
The backends use separately frozen configuration files and
configuration SHA values. Shared RuntimeConfig fields are verified
semantically equivalent. Timing-stage equivalence is verified
through the common Stage K profile runner, executable and trace
schema rather than configuration SHA equality.
Five independent runs per backend, 60 warmup and 500 measured
frames are sufficient. Run-level statistics and paired speedups
are primary; pooled frames are descriptive only.
TensorRT receives one 30-minute stability run using the inherited
Stage J J6 stability and telemetry semantics.
K0–K9 are logical gates and do not require separate full evidence
packages, separate commits or separate implementation cycles.
Stage P Pipeline optimization remains required downstream project
scope, but is outside Stage K and is not authorized before Stage K
closeout.
Evidence remains research-grade and does not claim industrial
certification. Only formal or decision-relevant failures require
retention.

⸻

34. 预计周期

K0:       1 day
K1:       0.5–1 day
K2:       1–2 days
K3 + K4:  4–7 days
K5:       2–4 days
K6:       1–3 days
K7:       1–2 days
K8:       1 day
K9:       1–2 days

总周期：

约 2–4 周兼职开发

主要延期风险：

1. TensorRT resource lifecycle bug；
2. Config/Result schema重构失控；
3. diagnostics过度建设；
4. Evidence重复建设；
5. 提前实现 Pipeline。

控制：

* Result v2最小扩展；
* diagnostics只在 mismatch触发；
* K3/K4/K6无完整 Evidence package；
* K0–K9仅逻辑 Gate；
* Stage P不进入 Stage K；
* 不因性能数字不理想扩大实验。

⸻

35. Stage P 下游边界

Stage P 是必做阶段，但只做学生级闭环。

最小架构：

Source + CPU Preprocess
        ↓
bounded queue
        ↓
one TensorRT ExecutionContext
one CUDA stream
        ↓
bounded queue
        ↓
CPU Postprocess + Result collection

研究：

cross-frame stage parallelism
TensorRT Serial vs TensorRT Pipeline

不研究：

multi-stream per frame
multiple ExecutionContexts
dynamic batching
GPU preprocessing
GPU NMS
lock-free framework
industrial scheduler
camera/ROS2/DeepStream

Stage P Planning Freeze在 K9 后单独进行。

⸻

36. 最终授权

Stage K Execution Plan:
FINAL
K0 Planning Freeze:
AUTHORIZED
K0 documentation and freeze commit:
AUTHORIZED
Feature branch creation:
AUTHORIZED_AT_K0_CLOSEOUT
K1 Jetson Platform Acceptance:
AUTHORIZED_AFTER_K0_COMPLETE
D062:
AUTHORIZED_AFTER_K1_PASS
K2 Engine Build:
AUTHORIZED_AFTER_D062_ACCEPTED
Production code modification:
AUTHORIZED_FROM_K3
Stage P implementation:
NOT_AUTHORIZED_BEFORE_STAGE_K_CLOSEOUT

下一步：

Write K0 formal artifacts
        ↓
append D055–D061
        ↓
minimally reconcile live-status documents
        ↓
create K0 freeze commit
        ↓
create feature/jetson-tensorrt-fp16
        ↓
enter K1

该计划现在可以作为其他 AI 的正式继承上下文。
