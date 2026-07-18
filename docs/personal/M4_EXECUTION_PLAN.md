# M4 C++ ONNX Runtime Serial Baseline Execution Plan

状态：M4 `IN_PROGRESS`；M4.0 Planning Freeze、M4.1 Runtime Contracts, Config and CLI Parser、
M4.2 ImageSource and DirectorySource、M4.3 ResultSink System 和 M4.4 SerialRunner and Basic Timing 已完成；
M4.4 Shallow Gate 首次结果为 FAIL，test/documentation remediation 后的 Gate rerun 为 PASS；M4.4 COMPLETE，
M4.5 COMPLETE；M4.6 Standard Final Gate 首次结果为 FAIL，test/documentation remediation COMPLETE，Gate rerun PENDING。

M4 正式名称：**C++ ONNX Runtime Serial Baseline**。

本文档冻结 M4 新增的应用编排合同、阶段拆分与 Gate。通用编码规范见
`docs/CODING_RULES.md`，全局架构边界见 `docs/ARCHITECTURE.md`；既有模块合同分别见
`docs/personal/M1_EXECUTION_PLAN.md`、`docs/personal/M2_EXECUTION_PLAN.md` 和
`docs/personal/M3_EXECUTION_PLAN.md`。本文档不重新定义或修改 M1、M2、M3 语义。

## 1. M4.0 起点与 Git 事实

2026-07-18 在修改前验证：

- branch：`feature/cpp-onnxruntime`；
- HEAD：`87facf9c7693a64c5eaaa2397888837d587cb5bb`；
- HEAD subject：`docs: close M3 postprocessor`；
- worktree：clean；
- `@{upstream}...HEAD`：behind `0`、ahead `1`；
- `docs/personal/M3_EXECUTION_PLAN.md` 已明确标记 M3 `CLOSED`；
- M4 production code 在该起点尚未开始。

M4.0 是 planning/documentation only。本阶段不运行 CTest，不修改 production code、测试逻辑或
CMake target，不进入 M4.1。

## 2. 仓库现状审计（已验证事实）

以下均是对上述起点的仓库事实，不是 planned implementation：

| 审计项 | 当前事实 |
| --- | --- |
| M1 Preprocessor | 已存在 `edge_ai_defect::preprocess::Preprocessor`、`PreprocessedFrame`、`ImageTransformMetadata` 和 LetterBox；生产实现位于 `edge_ai_core`，输入要求非空 `CV_8UC3`，输出 owned contiguous `float32 NCHW` `HostTensor`。M4 直接复用，不修改合同。 |
| M2 inference | 已存在 backend-neutral `inference::IInferenceEngine` 与 production `backend_ort::OnnxRuntimeEngine`；接口为同步 `initialize()` / `run()`，输入输出均为 `HostTensor`。M4 Runner 只依赖接口。 |
| M3 PostProcessor | 已存在 concrete `postprocess::PostProcessor`、`PostprocessConfig` 和 ordered original-image continuous xyxy `Detection`；M4 直接复用，不重排输出。 |
| executable | CMake target 为 `edge_ai_infer`，`OUTPUT_NAME` 为 `edge_ai_defect`。`src/main.cpp` 当前只打印版本、runtime skeleton 和 inference 未初始化信息，未解析 CLI、YAML，也未运行推理。 |
| RuntimeConfig | 不存在 `RuntimeConfig`、runtime YAML loader 或完整 `ConfigManager`。现有 `ModelContractLoader` 只读取 frozen model contract，不能充当 runtime config loader。 |
| ImageSource | 不存在 `ImageItem`、`ImageSource`、`DirectorySource` 或其他 production frame/image source。 |
| ResultSink | 不存在 `IResultSink`、`ConsoleSink`、`JsonSink`、`CompositeSink` 或 production result writer。测试侧的最小 JSON 文本输出不属于 production sink。 |
| SerialRunner | 不存在。当前没有 production image loop 或 M1→M2→M3 application orchestration。 |
| Profiler/timing | 不存在 public `IProfiler`、Profiler 或运行时 timing result 结构。历史 validation 中的数值统计不属于 production profiling。 |
| JSON dependency | CMake/production C++ 未引入或使用 nlohmann/json、RapidJSON、JsonCpp 等 JSON 库。Python validation 使用标准库 `json`，CMake evidence 使用 `string(JSON)`，少量 C++ test 自行写固定 JSON；它们不是 production JSON dependency。M4 按固定 schema 规划最小 deterministic writer。 |
| targets/dependencies | production targets 为 `edge_ai_core`、`edge_ai_backend_ort`、`edge_ai_postprocess`、`edge_ai_infer`。`edge_ai_core` PUBLIC 依赖 OpenCV core/imgproc、PRIVATE 依赖 yaml-cpp；ORT target PRIVATE 依赖 core、ONNX Runtime、OpenSSL；postprocess PUBLIC 依赖 core。当前 executable 只链接 core 和 ORT，尚未链接 postprocess。 |
| tests/Model Smoke | CTest 由 `BUILD_TESTING` 控制；`EDGE_AI_ENABLE_MODEL_SMOKE` 默认 OFF。OFF 注册 core、M1、M2 contract、M3 与 ORT runtime smoke；ON 额外注册 frozen model contract/inference smoke、Engine initialization/run 和 Level B。M3 closeout 记录的真实回归为 OFF 17/17、ON 24/24。 |
| Strict/sanitizers | 当前 CMake 没有 strict、ASan 或 UBSan option/flags；三者当前真实状态均为 `Not configured`。 |
| config/assets | `configs/` 当前包含 training/export 和 frozen model contract 配置；没有 runtime config。`tools/validation/` 当前服务 ONNX export、M1 Level A、M2 Level B 和 M3 PostProcessor-only evidence；没有 M4 runtime validation tool。 |

后续 M4.x 需要扩展 `edge_ai_infer` 的真实功能并新增应用编排模块；`src/main.cpp` 的 skeleton 将在
M4.5 被替换。`edge_ai_backend_ort` 中空的 `src/backend_ort.cpp` 是现有占位 translation unit，
但真实 `OnnxRuntimeEngine` 已在独立 source 中完成；M4 不回改其合同。除这些事实外，不把 planned
类型、文件或测试描述为已存在。

## 3. M4 目标、证明边界与 M5 分界

### 3.1 M4 核心目标

建立完整、确定性、单线程的 C++ ONNX Runtime 功能基线：

```text
RuntimeConfig
→ DirectorySource
→ Preprocessor
→ IInferenceEngine
→ PostProcessor
→ ResultSink
```

M4 必须证明：

- 应用可从一份严格 YAML 配置启动；
- 目录图片按确定性顺序读取；
- M1、M2、M3 模块被正确组装；
- 每张图片产生保持 M3 顺序的 `Detection`；
- Console 和单个运行级 JSON 正常输出；
- 任一图片或任一阶段失败后立即终止；
- 可采集基础阶段耗时；
- Model Smoke ON 时实际 ORT 模型完成一次完整 C++ 串行 smoke。

### 3.2 M4 不证明

- Python/C++ 完整 image-to-detection 数值一致性或完整 Level C E2E；
- 正式 ORT 性能结论、benchmark 或论文性能证据；
- FPS、mean、median、P50、P95、P99；
- warmup、`min_frames`、`min_seconds` 或稳定性统计；
- TensorRT、CUDA、Jetson、Pipeline、多线程、ROS2、Qt、Web、Camera、RTSP；
- batch > 1、dynamic shape、通用多模型或 plugin framework。

### 3.3 M4 与 M5 冻结边界

M4 包含 RuntimeConfig、CLI、DirectorySource、ResultSink 体系、SerialRunner、基础阶段计时、
ORT 串行功能闭环、Model Smoke ON 实际模型集成，以及功能正确性和确定性测试。

M5 包含完整 Level C E2E、Python/C++ image-to-detection 一致性、正式 Profiler、warmup、
`min_frames`/`min_seconds`、mean/median/P95/P99、FPS、ORT CPU 正式性能基线、稳定性实验与论文
性能证据。M4 的 `FrameTimings` 只能作为功能性观测，不得表述为 benchmark 或性能结论。

## 4. 冻结运行数据合同（planned）

具体 namespace、头文件归属可在 M4.1/M4.2 按现有
`edge_ai_defect::<module>` 惯例确定，但以下字段、类型语义和阶段边界不得改变。

### 4.1 `ImageItem` 与 `ImageSource`

```cpp
struct ImageItem {
    std::size_t sequence_index;
    std::filesystem::path relative_path;
    cv::Mat image_bgr;
};

class ImageSource {
public:
    virtual ~ImageSource() = default;

    virtual core::Status next(
        std::optional<ImageItem>* output) = 0;
};
```

`ImageItem` 规则：

- `sequence_index` 从 0 开始，等于 DirectorySource 确定性排序后的序号；
- `relative_path` 相对于 input directory，输出时用 `generic_string()`，不携带绝对路径；
- `image_bgr` 非空且为 `CV_8UC3`；
- Source 不执行 resize、normalize 或其他预处理。

`ImageSource::next()` 规则：

- success + `ImageItem`：成功读取下一张；success + `nullopt`：正常 End of Stream；
- failure：枚举或解码失败，且 `output` 保持原值；
- null output pointer 返回 `kInvalidArgument`；
- 不提供 `reset()`、`size()`，不为 Camera/RTSP/ROS2 预设复杂接口。

`DirectorySource` 使用 factory 或等价完整初始化方式，例如：

```cpp
static core::Status create(
    const std::filesystem::path& root,
    std::unique_ptr<DirectorySource>* output);
```

### 4.2 `DirectorySource` 确定性语义

- 只枚举输入目录第一层，不递归；
- 跳过所有 symlink，包括指向 regular file 的 symlink；
- 只接受真实 regular file；
- 只支持 `.jpg`、`.jpeg`、`.png`、`.bmp`，扩展名 ASCII 大小写不敏感；
- 隐藏文件只要扩展名有效也处理；
- 按 `relative_path.generic_string()` 的字节序升序排序，不使用 filesystem 原始枚举顺序；
- 空目录或没有支持图片时 factory 失败；
- 初始化只保存有序路径，不预加载全部图片；每次 `next()` 只解码一张；
- 使用 `cv::imread(path, cv::IMREAD_COLOR)`，不主动应用 EXIF orientation；
- 解码失败、空图或最终不是 `CV_8UC3` 时 fail-fast，不跳过坏图片。

### 4.3 基础计时

```cpp
struct FrameTimings {
    double source_ms;
    double preprocess_ms;
    double inference_ms;
    double postprocess_ms;
    double pre_sink_total_ms;
};
```

- 使用 `std::chrono::steady_clock`，单位为 double milliseconds；
- `source_ms` 包含 `DirectorySource` 图片解码；
- `pre_sink_total_ms` 从调用 `source.next()` 前开始，到 PostProcessor 成功结束；
- `pre_sink_total_ms` 不要求严格等于 stage 值之和；
- 全部值必须 finite 且非负；
- 不记录当前 frame 的 `sink_ms`，不把 JsonSink 自身写入耗时回写当前 frame；
- 不 warmup、不丢弃前 N 张、不计算均值/百分位/FPS；
- `timing.enabled=false` 时 `FrameResult.timings=nullopt`，JSON 完全省略 `timing_ms`，
  Console 不输出 timing 字段；
- M4 不建立 public `IProfiler` 或复杂 Profiler framework。

### 4.4 运行结果

```cpp
struct RunMetadata {
    std::uint32_t schema_version;
    std::string backend_type;
    std::string model_filename;
    std::string model_sha256;
    std::string contract_filename;
    std::vector<std::string> class_names;
    postprocess::PostprocessConfig postprocess_config;
    bool timing_enabled;
};

struct FrameResult {
    std::size_t sequence_index;
    std::filesystem::path relative_path;
    int image_width;
    int image_height;
    std::vector<postprocess::Detection> detections;
    std::optional<FrameTimings> timings;
};

struct RunSummary {
    std::size_t processed_images;
    std::size_t total_detections;
};
```

`RunMetadata`：`schema_version` 固定为 1；backend 固定为 `onnxruntime_cpu`；只记录文件名，
不记录机器绝对路径；model SHA256 与 class 顺序来自 frozen `ModelContract`；不记录 wall-clock
timestamp、hostname、用户名或工作目录。M4 JSON 是功能输出，不是完整 provenance。

`FrameResult`：保持 PostProcessor 的 Detection 顺序和 M3 original-image continuous xyxy；不保存
`cv::Mat`、raw tensor、preprocessed tensor 或绝对路径。`RunSummary` 只含上述两个计数；不含
failed/skipped images、run total、FPS、stage statistics 或 warmup count。

## 5. ResultSink 合同（planned）

### 5.1 `IResultSink`

```cpp
class IResultSink {
public:
    virtual ~IResultSink() = default;

    virtual core::Status begin_run(const RunMetadata& metadata) = 0;
    virtual core::Status write_frame(const FrameResult& frame) = 0;
    virtual core::Status end_run(const RunSummary& summary) = 0;
};
```

生命周期固定为一次 `begin_run()` → 每张成功图一次 `write_frame()` → 全部成功后一次
`end_run()`。任一步失败立即返回，不处理后续图片；失败后不调用 `end_run()` 伪装成功，caller
`RunSummary` 保持原值。不增加 `abort()`，不做 dynamic plugin、thread-safe 或 async write。

### 5.2 `ConsoleSink`

目标输出：

```text
RUN backend=onnxruntime_cpu model=<filename>

IMAGE index=<n> path=<relative path> width=<w> height=<h> detections=<count>
DETECTION class_id=<id> confidence=<value> x1=<value> y1=<value> x2=<value> y2=<value> candidate_index=<index>

SUMMARY processed_images=<count> total_detections=<count>
```

正常输出到 stdout，应用错误到 stderr；路径用 `generic_string()`；不输出 timestamp；使用 classic
locale 和稳定 float 格式；保持 Detection 顺序。timing enabled 时在 IMAGE 行追加冻结的阶段耗时，
disabled 时完全不输出 timing 字段。Console 输出不是 M5 数值证据。

### 5.3 `JsonSink`

JsonSink 缓存 `RunMetadata` 和全部 `FrameResult`，只在 `end_run()` 一次性序列化完整运行级 JSON；
不使用 per-image JSON、JSON Lines，也不在运行中写出看似完整的最终文件。

提交流程：

```text
serialize complete JSON
→ write temporary file in target directory
→ flush/close
→ atomic rename
```

- temp 与目标文件位于同一目录；输出父目录必须预先存在，不自动创建；
- `overwrite=false` 且目标存在：在 run 开始前失败；
- `overwrite=true`：完整 run 成功前原文件保持不变，只有 `end_run()` 成功后原子替换；
- 任一失败删除 temp；当前只要求 Linux/WSL/Jetson POSIX semantics；
- 当前仓库无 production JSON library，因此实现固定 schema 的最小 deterministic writer，不新增大型 DOM
  dependency；必须测试 escaping、locale、finite validation 和 atomic commit。

### 5.4 `CompositeSink`

CompositeSink 拥有子 sink；应用组装顺序固定为：1. JsonSink；2. optional ConsoleSink。

- `begin_run`：正序；
- `write_frame`：正序；
- `end_run`：逆序，即 ConsoleSink 后 JsonSink 最终提交；
- 子 sink failure 原样传播，不做 rollback。Console 已输出内容不保证回滚；JsonSink 最终文件必须保持原子性；
- 不设计 dynamic registry 或 plugin system。

## 6. 冻结运行级 JSON schema

字段语义和顺序固定为：

```json
{
  "schema_version": 1,
  "backend": {
    "type": "onnxruntime_cpu"
  },
  "model": {
    "filename": "yolov8n_neudet_frozen.onnx",
    "sha256": "...",
    "contract_filename": "yolov8n_neudet_frozen.yaml",
    "classes": [
      "crazing",
      "inclusion",
      "patches",
      "pitted_surface",
      "rolled-in_scale",
      "scratches"
    ]
  },
  "postprocess": {
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45,
    "max_nms": 30000,
    "max_det": 300,
    "max_wh": 7680.0,
    "agnostic": false,
    "multi_label": false
  },
  "images": [
    {
      "sequence_index": 0,
      "relative_path": "a.jpg",
      "width": 200,
      "height": 200,
      "detections": [
        {
          "x1": 1.0,
          "y1": 2.0,
          "x2": 20.0,
          "y2": 30.0,
          "confidence": 0.91,
          "class_id": 5,
          "candidate_index": 123
        }
      ],
      "timing_ms": {
        "source": 0.1,
        "preprocess": 1.2,
        "inference": 15.0,
        "postprocess": 0.4,
        "pre_sink_total": 16.8
      }
    }
  ],
  "summary": {
    "processed_images": 1,
    "total_detections": 1
  }
}
```

冻结规则：不记录输入根、绝对路径或 timestamp；images 顺序等于 DirectorySource 顺序，detections
顺序等于 PostProcessor 输出；timing disabled 时省略 `timing_ms`，不用 null；field order 固定；
UTF-8，非 ASCII 原样保留，引号/反斜杠/控制字符正确 escape，末尾一个 LF；classic locale；
Detection float 使用足够 round-trip float32 的精度，timing double 使用足够 round-trip double 的精度；
所有数值 finite；不含 `sink_ms`、P50/P95/FPS。

## 7. RuntimeConfig YAML 与 CLI

### 7.1 冻结 YAML schema

```yaml
schema_version: 1

backend:
  type: onnxruntime_cpu

model:
  contract_path: ../../configs/model_contracts/yolov8n_neudet_frozen.yaml
  model_path: ../../models/onnx/yolov8n_neudet_frozen.onnx

input:
  type: directory
  directory: ../../tests/data/runtime_images

output:
  json_path: ../../results/runtime/ort_serial.json
  console: true
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
```

RuntimeConfigLoader 规则：

- 所有 top-level section、所有字段必填；无隐式默认；未知字段和 duplicate key 失败；
- `schema_version` 必须为 1，`backend.type` 只允许 `onnxruntime_cpu`，`input.type` 只允许 `directory`；
- path scalar 必须非空；配置文件 CLI 参数自身的相对路径按 process CWD 解析；配置内部相对路径相对
  配置文件所在目录解析；解析后 `lexically_normal()`；
- 不对尚不存在的输出文件要求 `canonical()`；允许运行使用绝对路径，但绝对路径不得写入 JSON；
- 不展开 `~` 或 environment variable；不支持 CLI overrides、YAML include；
- 不开放 M1 preprocess 参数或 M2 SessionOptions；
- postprocess 必须调用现有 `validate_postprocess_config()`；`timing.enabled` 必须为 bool；
- Loader 只解析和校验，不创建目录、不初始化模型、不打开输出文件；model/source/sink 各自在自己的
  create/initialize 阶段验证资源；
- load failure 保持 caller output 原值。

### 7.2 CLI 合同

唯一正常运行形式：`edge_ai_infer --config <runtime.yaml>`；帮助形式：`edge_ai_infer --help`。这里的
`edge_ai_infer` 是现有 CMake target 的逻辑名称；仓库现有 `OUTPUT_NAME=edge_ai_defect` 保持为实际构建
文件名，这属于既有命名惯例，不改变本节参数、帮助和退出码语义。

- `--config` 必须且只能出现一次；不支持 positional argument、额外 flag、`--model`/`--input` 或 YAML
  overrides；
- `--help` 单独出现退出 0；与任何其他参数同时出现失败；不支持 `-h`；
- main 不实现图片循环、preprocess 或 postprocess 逻辑。

退出码：

| code | 含义 |
| --- | --- |
| 0 | 成功，或单独 `--help` |
| 1 | 未分类异常或内部错误 |
| 2 | CLI、YAML parse 或 RuntimeConfig 错误 |
| 3 | component construction/initialization 失败 |
| 4 | SerialRunner 运行失败 |

ModelContract load、Engine initialize、DirectorySource create、JsonSink create/target preflight 失败映射 3；
image read、preprocess、inference、postprocess、sink write/end 失败映射 4。library 只返回 `Status`，main
负责 exit mapping；未预期 `std::exception` 返回 1；错误写 stderr。

## 8. SerialRunner 与应用组装（planned）

### 8.1 Runner contract

```cpp
class SerialRunner final {
public:
    SerialRunner(
        ImageSource& source,
        preprocess::Preprocessor& preprocessor,
        const core::TensorInfo& model_input_info,
        inference::IInferenceEngine& engine,
        postprocess::PostProcessor& postprocessor,
        IResultSink& sink);

    core::Status run(
        const RunMetadata& metadata,
        RunSummary* summary);
};
```

Runner 只依赖 `IInferenceEngine`，不依赖 concrete `OnnxRuntimeEngine`；借用 source、preprocessor、engine、
postprocessor 与 sink，且其生命期覆盖 Runner。构造时从已验证 `ModelContract.input.tensor_info` 注入
`model_input_info`，Runner 内部保存 `core::TensorInfo` 值副本并仅将该副本传给 Preprocessor；不从
RunMetadata 推导、不重新加载 ModelContract，也不要求 Engine 提供 metadata getter。Runner 不加载 YAML、解析
CLI、构造 Engine、打开目录或直接写 JSON；严格同步单线程，不修改 M1/M2/M3 合同。

流程：

```text
validate summary pointer
→ sink.begin_run(metadata)
→ loop:
    source.next()
    EOS → break
    preprocess (with injected model_input_info copy)
    engine.run
    postprocessor.process
    sink.write_frame
→ construct staged summary
→ sink.end_run(staged summary)
→ commit caller summary
```

Fail-fast：首个 stage failure 立即返回；不读下一张、不调用 `end_run()`；caller summary 原值不变；
JsonSink 最终目标不变；Console 先前输出不保证回滚；Status message 包含 stage，取得 ImageItem 后还必须
包含 `sequence_index` 与 `relative_path`。成功至少处理一张图；`processed_images` 等于成功
`write_frame()` 次数；`total_detections` 为这些 frame 的 Detection 总数；summary 只在
`end_run()` 成功后一次提交。

计时边界按第 4.3 节；timing disabled 时不创建 `FrameTimings`。图像尺寸从 `ImageItem.image_bgr`
在 preprocess 前取得；FrameResult 不保留 image/tensor。

### 8.2 application composition boundary

```text
parse CLI
→ RuntimeConfigLoader
→ ModelContractLoader
→ retain validated ModelContract.input.tensor_info for SerialRunner injection
→ construct DirectorySource
→ construct Preprocessor
→ construct OnnxRuntimeEngine
→ initialize Engine
→ construct PostProcessor
→ construct JsonSink
→ optional ConsoleSink
→ construct CompositeSink
→ create RunMetadata
→ construct SerialRunner with ModelContract.input.tensor_info
→ SerialRunner.run
→ map Status to exit code
```

composition layer 可以知道 concrete `OnnxRuntimeEngine` 以选择实际 backend。以下不得进入
SerialRunner public contract：`OnnxRuntimeEngine`、ORT Session、TensorRT 或 backend-specific tensor。

## 9. M4.0～M4.7 独立任务卡

每次只执行一张卡，完成后停止。所有 planned files 仅表示建议落点；实现时可按现有目录/namespace
惯例微调文件名，但不得改变本文件冻结语义和阶段边界。

### M4.0 — Planning Freeze

- **objective**：审计真实仓库；冻结本文件全部合同、M4/M5 边界、task cards 和 Gate；更新 TASKS，
  为长期稳定决策更新 DECISIONS；不开发代码。
- **starting facts**：M3 CLOSED；HEAD/branch/worktree/upstream 满足第 1 节；M1/M2/M3 可复用，应用层缺失。
- **allowed changes**：`docs/personal/M4_EXECUTION_PLAN.md`、`docs/personal/TASKS.md`，必要时
  `docs/personal/DECISIONS.md`。
- **forbidden scope**：production/test/CMake/config/tool/model/result 修改；M4.1、M5、push 及所有禁止技术域。
- **planned files/modules**：仅上述三份文档。
- **required contracts**：本文第 3～8 节和 M4.0～M4.7 卡完整、自洽且不改 M1/M2/M3。
- **required tests**：无需 CTest；执行 Git preflight、`git diff --name-only`、`git diff --check` 和范围审计。
- **acceptance criteria**：审计与仓库一致；只有允许文档变化；TASKS 为 M4 IN_PROGRESS/M4.1 pending；
  DECISIONS 无重复；本地 commit 创建。
- **expected commit message**：`docs: freeze M4 serial baseline execution plan`。
- **next step**：仅 M4.1 Runtime Contracts, Config and CLI Parser。
- **Gate**：无代码 Gate；文档提交前范围检查。

### M4.1 — Runtime Contracts, Config and CLI Parser

- **objective**：建立 `RuntimeConfig`/Loader、`RunMetadata`、`FrameTimings`、`FrameResult`、
  `RunSummary` 和 CLI parser；不组装真实应用或图片循环。
- **starting facts**：M4.0 committed；可复用 `Status`、yaml-cpp strict parsing pattern 与
  `validate_postprocess_config()`；当前不存在 runtime contracts/CLI parser。
- **allowed changes**：planned runtime/application public headers与sources、对应 tests、必要 CMake test/target
  接线和本卡状态文档；例如 `include/edge_ai_defect/runtime/`、`src/runtime_config.cpp`、
  `src/cli.cpp`、`tests/test_runtime_config.cpp`、`tests/test_cli.cpp`（均 planned）。
- **forbidden scope**：DirectorySource、sink、Runner、真实 main assembly、模型运行、M1/M2/M3 修改、M4.2+。
- **planned files/modules**：runtime data contracts、strict `RuntimeConfigLoader`、minimal CLI parse result。
- **required contracts**：第 4.3/4.4、7 节；path base/CWD 语义、unknown/duplicate/missing/type validation、
  transactional outputs、exit category information。
- **required tests**：完整/缺失 section/key、unknown/duplicate key、错误 YAML type、schema/backend/input、空 path、
  config-dir relative path 与 CWD 语义、postprocess validation、timing bool；合法 CLI、duplicate `--config`、
  missing value、extra flag、positional、help-only、help-with-other。
- **acceptance criteria**：严格 schema 无隐式默认；所有 failure 可定位且 output atomic；不触碰图片/模型/Runner。
- **expected commit message**：`feat: define serial runtime contracts`。
- **next step**：M4.2 ImageSource and DirectorySource。
- **Gate**：无独立 Gate；完成定向/完整适用 CTest 和 scope audit 后停止。

#### M4.1 实际结果（2026-07-18）

M4.1 已完成，且没有进入 M4.2。实际新增：

- `edge_ai_defect::runtime::RuntimeConfig` 与严格 `RuntimeConfigLoader`；Loader 只读 YAML、验证
  schema/字段并解析路径，不加载 model、不初始化 Engine、不打开目录或 sink；
- `FrameTimings`、`RunMetadata`、`FrameResult`、`RunSummary` runtime value contracts；
- `CliAction`、`CliOptions` 与 `parse_cli()`；parser 只接受 `--config <runtime.yaml>` 或单独
  `--help`，不返回 process exit code；
- 独立 `edge_ai_runtime` static target。它 public 依赖既有 postprocess value contracts，并 private
  使用既有 yaml-cpp；没有改变 `edge_ai_core`、M2 Engine 或 M3 PostProcessor 的 public contract。

`test_runtime_config` 覆盖 valid config、missing section/key、unknown/duplicate key、wrong type、
schema/backend/input、empty path、postprocess validation、timing type、config-CWD 与内部相对路径解析，
以及 loader output atomicity。`test_cli` 覆盖 valid `--config`、missing/duplicate value、extra/positional/
unsupported flag、standalone help、help-with-other 和 parser output atomicity；`test_runtime_types` 编译和
验证四个运行数据合同。

真实回归：Model Smoke ON 全量 CTest `27/27 PASS`；独立 Model Smoke OFF 全量 CTest `20/20 PASS`。
Strict、ASan、UBSan 仍为 `Not configured`，未运行也未表述为 PASS。M4.1 无 Gate；下一步仅为
M4.2 ImageSource and DirectorySource。

### M4.2 — ImageSource and DirectorySource

- **objective**：实现最小 `ImageSource`、`ImageItem`、deterministic `DirectorySource`、颜色图像解码与 EOS。
- **starting facts**：M4.1 contracts committed；OpenCV core/imgproc 已存在，但 `imread` 所需 imgcodecs target 尚未接入；
  repository 没有 source abstraction。
- **allowed changes**：planned source headers/sources、DirectorySource tests、必要 OpenCV imgcodecs/CMake 接线和本卡文档。
- **forbidden scope**：recursive/video/camera/RTSP、preprocess、sink、Runner、preload、M4.3+。
- **planned files/modules**：例如 `include/edge_ai_defect/runtime/image_source.hpp`、
  `include/edge_ai_defect/runtime/directory_source.hpp`、`src/directory_source.cpp`、
  `tests/test_directory_source.cpp`（planned）。
- **required contracts**：第 4.1/4.2 节全部语义，factory 完整初始化、EOS/failure output atomicity。
- **required tests**：extension/filter/case、byte-order、index/relative path、non-recursive、symlink、non-regular、hidden、
  empty/no-valid、bad image、EOS、failure atomicity、null output。
- **acceptance criteria**：初始化不解码全部图片；每次 next 解码一张；顺序与 filesystem enumeration 无关；坏图 fail-fast。
- **expected commit message**：`feat: add deterministic directory image source`。
- **next step**：M4.3 ResultSink System。
- **Gate**：无独立 Gate；完成定向/完整适用 CTest 和 scope audit 后停止。

#### M4.2 实际结果（2026-07-18）

M4.2 已完成，且没有进入 M4.3。实际新增：

- `runtime::ImageItem`、最小 `runtime::ImageSource` 和 `runtime::DirectorySource`；factory 在成功时
  完整持有输入根及路径列表，失败时保持 caller `unique_ptr` 原值；
- `DirectorySource` 只枚举输入目录第一层的真实 regular file，跳过 symlink、目录和其他非 regular
  entry；仅接受 `.jpg`、`.jpeg`、`.png`、`.bmp`（ASCII 大小写不敏感），以
  `relative_path.generic_string()` 字节序排序；
- `next()` 每次仅以 `cv::imread(path, cv::IMREAD_COLOR)` 解码当前图片，不 resize、normalize、
  颜色转换或调用 Preprocessor；成功的 `ImageItem` 使用从 0 连续递增的序号、相对路径和有效
  `CV_8UC3` BGR 图像；
- EOS 返回 success + `nullopt`，重复调用仍相同；解码失败为 fail-fast，cursor 不推进、caller output
  保持原值，因此重试会读取同一项；
- `edge_ai_runtime` 私有接入 OpenCV `imgcodecs`，未改变 M1、M2、M3 合同，也未触及 main、sink、
  Runner、ORT 或 benchmark。

`test_directory_source` 在运行时生成并清理临时图片，覆盖空/null/non-directory/no-valid factory
failure 及其 output atomicity，四种扩展名与大小写、隐藏文件、过滤、非递归、file/directory symlink、
Linux FIFO、字节序排序、index/relative path、按需单图解码、EOS/repeated EOS、损坏/删除后图片的
fail-fast 和 `next()` output atomicity；测试不依赖冻结 ONNX 模型。

真实回归：M4.2 定向及必要 runtime/core 回归 `8/8 PASS`；Model Smoke OFF 全量 CTest `21/21 PASS`；
Model Smoke ON 全量 CTest `28/28 PASS`。Strict、ASan、UBSan 仍为 `Not configured`，未运行也未表述为
PASS。M4.2 无 Gate；下一步仅为 M4.3 ResultSink System。

### M4.3 — ResultSink System

- **objective**：实现 `IResultSink`、Console/Json/CompositeSink、固定 JSON schema 与原子输出。
- **starting facts**：M4.1 result contracts committed；仓库无 production JSON library；不新增大型 DOM dependency。
- **allowed changes**：planned sink headers/sources、sink tests、必要 CMake 接线和本卡文档。
- **forbidden scope**：Runner、DirectorySource 改义、真实 ORT assembly、benchmark/profiler、plugin/async、M4.4+。
- **planned files/modules**：例如 `include/edge_ai_defect/runtime/result_sink.hpp`、各 concrete sink headers，
  `src/*_sink.cpp`、`tests/test_result_sinks.cpp`（planned）。
- **required contracts**：第 5/6 节；lifecycle state、finite/locale/precision/escaping、same-directory temp、overwrite、
  atomic commit、Composite 正/逆序。
- **required tests**：begin/write/end lifecycle 和非法顺序；Detection 顺序；timing on/off；field order；escaping/non-ASCII；
  classic locale；finite；float/double precision；missing parent；overwrite false/true；failure preserves original；temp cleanup；
  atomic end；Composite begin/write 正序、end 逆序、child failure；summary consistency。
- **acceptance criteria**：最终 JSON 仅在 successful `end_run()` 可见；失败不形成假完整文件；schema byte-deterministic。
- **expected commit message**：`feat: add serial result sinks`。
- **next step**：M4.4 SerialRunner and Basic Timing。
- **Gate**：无独立 Gate；M4.1～M4.3 不做 Gate。

#### M4.3 实际结果（2026-07-18）

M4.3 已完成，且没有进入 M4.4。实际新增：

- `IResultSink`、注入 `std::ostream` 的 `ConsoleSink`、factory 创建的 `JsonSink` 和拥有 child sink 的
  `CompositeSink`；所有 sink 严格执行 begin → write* → end 生命周期，输入验证失败不推进自身成功状态；
- 固定 schema 的最小 deterministic UTF-8 JSON writer：classic locale、固定字段顺序、完整 JSON escaping、
  非 ASCII 原样保留、float32/double round-trip 精度和末尾单个 LF；不引入 JSON DOM dependency；
- JsonSink 缓存 metadata 和 frames，仅在 `end_run()` 用同目录 `mkstemp` 临时文件完成 write/flush/close 后
  以 POSIX rename 提交；overwrite=true 的旧目标在提交前保持不变，所有失败及析构路径清理临时文件；
- CompositeSink 要求非空且无 null child，begin/write 正序、end 逆序；任一 child 失败立即停止，因而
  Console end 失败时 JsonSink 不会提交最终文件。

`test_result_sinks` 覆盖生命周期非法顺序、Console 固定输出/Detection 顺序/timing 开关/finite validation，
Json schema/字段顺序/escaping/UTF-8/尾 LF/timing/summary/sequence/path/finite validation、parent/overwrite/
late target/old-file preservation/temp cleanup/destructor，以及 Composite 正逆序、null/empty child、begin/write/end
中间失败停止和 Console end 对 JSON commit 的保护。测试使用临时目录和 memory stream，不依赖冻结 ONNX 模型。

真实回归：M4.3 runtime 定向 `5/5 PASS`；Model Smoke OFF 全量 CTest `22/22 PASS`；Model Smoke ON 全量
CTest `29/29 PASS`。Strict、ASan、UBSan 仍为 `Not configured`，未运行也未表述为 PASS。M4.3 无 Gate；下一步
仅为 M4.4 SerialRunner and Basic Timing。

### M4.4 — SerialRunner and Basic Timing

- **objective**：实现同步 SerialRunner 和 steady-clock 基础计时，用 fake/recording dependencies 验证 orchestration；
  不组装真实 ORT application。
- **starting facts**：M4.1～M4.3 committed；M1/M2/M3 interfaces 与 source/sink contracts 可注入。
  `Preprocessor::preprocess()` requires a `TensorInfo` while `IInferenceEngine` intentionally has no getter, so
  `ModelContract.input.tensor_info` is an explicit external execution dependency injected by value.
- **allowed changes**：planned Runner header/source、fake-based tests、必要 CMake 接线和本卡文档。
- **forbidden scope**：真实 main/ORT smoke assets、Profiler statistics、threads/pipeline、M4.5+、M1/M2/M3 contract changes。
- **planned files/modules**：例如 `include/edge_ai_defect/runtime/serial_runner.hpp`、`src/serial_runner.cpp`、
  `tests/test_serial_runner.cpp`（planned）。
- **required contracts**：第 4.3、8.1 节；borrowed lifetime、owned `model_input_info` value copy、IInferenceEngine-only、
  fail-fast、stage context、summary atomicity。
- **required tests**：正常多图、stage order、EOS、Detection order、injected `model_input_info` forwarding、timing on/off 与 finite/nonnegative；source/preprocess/
  inference/postprocess failures；sink begin/write/end failures；不处理下一张、不在失败后 end；caller summary atomicity；
  success summary；message stage/index/path。
- **acceptance criteria**：严格单线程；首次失败停止；成功后才提交 summary；无 ORT concrete/backend leakage。
- **expected commit message**：`feat: implement serial inference runner`。
- **next step**：执行一次只读 M4.4 Shallow Gate；PASS 后才进入 M4.5。
- **Gate**：必须 Shallow Gate，检查 interface dependency、backend leakage、ownership/lifetime、`model_input_info` 的外部注入和值副本、
  fail-fast、summary atomicity、sink sequence、timing boundary 和 M1/M2/M3 未改义。

#### M4.4 实际结果（2026-07-18）

M4.4 production implementation 已完成；M4.5 未开始。实际新增：

- `runtime::SerialRunner`，构造时借用 ImageSource、Preprocessor、IInferenceEngine、PostProcessor 与
  IResultSink，并保存 externally injected `ModelContract.input.tensor_info` 的 `core::TensorInfo` 值副本；
- 严格同步数据流：`sink.begin_run → source.next → preprocess → engine.run → postprocess.process →
  sink.write_frame → sink.end_run`；Runner 不依赖 concrete ORT、DirectorySource 或 concrete sink；
- 首次失败立即停止，保留底层 Status 并补充 stage、已取得图片时的 sequence index 与 relative path；不读下一帧、
  不调用 end_run，caller `RunSummary` 仅在 successful end_run 后一次提交；
- timing enabled 时用 `steady_clock` 在 write_frame 前填充 source/preprocess/inference/postprocess/
  pre_sink_total 五项功能性毫秒值；disabled 时保持 `FrameResult.timings=nullopt`，不写 sink timing 或统计。

`test_serial_runner` 使用真实 M1 Preprocessor、真实 M3 PostProcessor 以及 fake ImageSource/IInferenceEngine/
IResultSink。构造 Runner 后故意修改外部 TensorInfo，仍验证 Preprocessor 使用构造时 injected value copy；另以
无效注入 TensorInfo 证明 preprocess failure 在 engine/sink 前停止。测试不依赖冻结 ONNX 模型，也不构成
Level C。

真实回归：M4.4 runtime 定向 `6/6 PASS`；Model Smoke OFF 全量 CTest `23/23 PASS`；Model Smoke ON 全量
CTest `30/30 PASS`。Strict、ASan、UBSan 仍为 `Not configured`，未运行也未表述为 PASS。

#### M4.4 Shallow Gate remediation（2026-07-18）

首次只读 Shallow Gate 的 production implementation 审查为 PASS，但 Gate 判定为 FAIL：测试没有直接覆盖
`summary == nullptr`、一帧成功后的 source failure，且无效 injected TensorInfo 测试没有断言 M1 底层错误文本；
当时“已覆盖 null summary”的文档表述不准确。该失败只涉及测试证据和文档漂移，不改变 Runner、M1、M2 或 M3
生产合同。

本 remediation 在既有 `test_serial_runner` target 内新增/加强：

- null summary 在任何 observable side effect 前返回 `kInvalidArgument`；
- 一帧成功 write 后的 source failure：不读第三帧、不执行后续 engine/write/end，且 caller summary 不提交 partial progress；
- injected invalid TensorInfo 同时断言 `model_input_info.layout` 与 `NCHW`，证明 Runner 保留 M1 底层 Status message；
- 合法零 Detection frame 仍成功写入并形成 `processed_images=1`、`total_detections=0` summary；
- fake source、engine 和 sink 的共享 test-only event log 覆盖 `begin → source → engine → write → source/EOS → end`。

Preprocessor 与 PostProcessor 保持真实 final modules，未引入 production hook 或 test seam；其顺序由真实模块输出、
下游调用条件和 failure blocking 间接验证，不声称拥有不存在的 hook-level trace。M4.4 remediation complete。

#### M4.4 Shallow Gate rerun（2026-07-18）

只读 rerun 判定为 **PASS**。remediation commit 为
`0eb4bf3669ce1da1c8d0ce546adffc007c7a2bfe`（`test: close M4.4 serial runner gate gaps`）。

- production SerialRunner、M1/M2/M3 contracts、CMake dependency boundary 和 D033 均未修改；
- null summary coverage、partial-progress source failure coverage、TensorInfo 底层错误保留和 zero-Detection frame
  coverage 已全部关闭；
- test-only event log 不进入 production，且 fail-fast 与 summary atomicity 的副作用证据充分；
- M4 runtime 定向 `6/6 PASS`，Model Smoke OFF 全量 CTest `23/23 PASS`，Model Smoke ON 全量 CTest `30/30 PASS`；
- Strict、ASan、UBSan 仍为 `Not configured`；未执行 benchmark。

M4.4 状态为 **COMPLETE**。M4.5 状态为 **PENDING**，可由独立任务开始；M4 仍为 `IN_PROGRESS`，本结论不构成
Level C、formal Profiler 或 benchmark 证据。

### M4.5 — Application Assembly and Actual ORT Smoke

- **objective**：实现 `edge_ai_infer --config` composition，加入 tracked runtime smoke config 和 1～2 张输入图，完成实际 ORT 串行闭环。
- **starting facts**：M4.4 Shallow Gate PASS；所有 application components 已独立验证；当前 main skeleton 待替换。
- **allowed changes**：`src/main.cpp`/planned application composition、必要 production/CMake target 接线、runtime config、small tracked
  smoke images、assembly/smoke tests 和本卡文档。
- **forbidden scope**：Python detection parity、Level C、benchmark、M5 profiler、TensorRT/CUDA/Pipeline/ROS2/Qt/Camera/RTSP。
- **planned files/modules**：main/application assembly、`configs/runtime/`、`tests/data/runtime_images/`、assembly tests 与 actual model smoke test（planned）。
- **required contracts**：第 7/8.2 节、退出码、metadata 来源、同一已验证 ModelContract 的 input TensorInfo 同时用于
  Engine initialize 和 SerialRunner injection、Json→Console composition、relative-only output。
- **required tests**：Model Smoke OFF 覆盖 CLI/config/component initialization exit mapping 且不要求模型；Model Smoke ON 用 1～2 张
  tracked image 和 actual `OnnxRuntimeEngine` 跑完整链路，JSON 合法、顺序确定、Detection finite/字段合法；timing disabled 连续两次
  JSON byte-identical。不得比较 Python Detection，不称 Level C，不 benchmark。
- **acceptance criteria**：唯一 CLI 形式可完成 actual ORT functional smoke；所有错误正确写 stderr/映射；无范围越界。
- **expected commit message**：`feat: assemble ONNX Runtime serial baseline`。
- **next step**：M4.6 read-only Standard Final Gate。
- **Gate**：准备完整 OFF/ON evidence，随后必须执行 M4.6；M4.5 不自行关闭 M4。

#### M4.5 实际结果（2026-07-18）

M4.5 已完成，`edge_ai_defect` 不再是 skeleton，而是保持薄边界的 composition root：CLI parse 和 help、
RuntimeConfig load、组件组装、`SerialRunner::run()`、stderr 错误输出和五类 process exit code 映射只在
`src/main.cpp`。逐图循环、preprocess、`engine.run()`、postprocess 和 JSON serialization 仍分别由
SerialRunner、M1、M2、M3 和 ResultSink 负责。

- `ModelContractLoader` 只执行一次；同一已验证 contract 同时传给 `OnnxRuntimeEngine::initialize()`，并将其
  `input.tensor_info` 值注入 SerialRunner，且为 RunMetadata 提供 model filename/SHA、contract filename 和
  class 顺序，保持 D033；
- 组装顺序为 DirectorySource、Preprocessor、ORT Engine initialize、PostProcessor、JsonSink、optional
  ConsoleSink、CompositeSink 和 SerialRunner。Composite 子项固定 Json→Console；Json 永远存在；
- `tests/test_application_smoke.py` 通过真实 `edge_ai_defect` subprocess 覆盖 help、CLI/config errors 和
  initialization exit `2/3`（OFF）；ON 时在 build 临时目录确定性生成两张最小 24-bit BMP 和 strict runtime YAML，
  因而不污染 source tree，也不依赖 CWD 或固定 build path；
- ON smoke 使用 frozen model contract 和 ONNX 模型实际贯穿 RuntimeConfigLoader、ModelContractLoader、
  DirectorySource、Preprocessor、OnnxRuntimeEngine、PostProcessor、Composite/JsonSink 和 SerialRunner。它验证
  JSON schema/metadata/相对路径/图像排序/Detection finite and bounds/summary，且 `timing.enabled=false` 连续两次
  覆盖输出为 byte-identical（SHA256 `5fbc1847f54716c3e809ecefa4ee297d368c08d08b2d0964a8a479bf620f7071`）；
- Console smoke 验证 RUN、两条 IMAGE 和 SUMMARY 输出，无 timing 字段，且 JSON 仍原子提交；ON 同时覆盖 missing
  output parent 与 `overwrite=false` 的 initialization exit `3`；
- 实际回归：Model Smoke OFF `24/24 PASS`；Model Smoke ON `32/32 PASS`。Strict、ASan、UBSan 仍为
  `Not configured`；未执行 benchmark，未进行 Level C parity 或 M5 work。

M4.5 状态为 **COMPLETE**。M4 仍为 `IN_PROGRESS`，M4.6 read-only Standard Final Gate 为 **PENDING**；本结果不
关闭 M4，也不构成 Level C 或性能证据。

### M4.6 — M4 Final Gate

- **objective**：只读 Standard Final Gate，判定 M4 总体边界和证据是否 PASS。
- **starting facts**：M4.5 committed，worktree clean；OFF/ON regression commands/evidence 可复现。
- **allowed changes**：无；只读审查、build/test、Git/依赖/行为审计。
- **forbidden scope**：任何文件修改、remediation、commit、M4.7 closeout、M5。
- **planned files/modules**：无。
- **required contracts**：审查 strict RuntimeConfig、DirectorySource determinism、JSON schema/atomicity、Composite order、Runner DI、
  fail-fast、summary atomicity、timing boundary、M1/M2/M3 immutability、OFF/ON smoke 和范围。
- **required tests**：clean configure/build；Model Smoke OFF/ON 全量适用 CTest；必要 CLI/JSON deterministic rerun；记录 strict/ASan/UBSan
  的真实 configured 状态。
- **acceptance criteria**：输出 PASS 或带证据的 FAIL；确认未进入 Level C、formal Profiler/benchmark；不修改仓库。
- **expected commit message**：无。
- **next step**：PASS 后仅 M4.7；FAIL 时另行批准 remediation，不在 Gate 静默修改。
- **Gate**：Standard Final Gate；M4 不做 Deep Gate。

#### M4.6 第一次 Standard Final Gate 与 remediation（2026-07-18）

第一次只读 Standard Final Gate 判定为 **FAIL**。production architecture 审查为 PASS，Model Smoke OFF 全量
CTest `24/24 PASS`、Model Smoke ON 全量 CTest `32/32 PASS`；未发现 M1/M2/M3/M4.4 contract 漂移、ownership
问题、dependency leakage 或 M5 scope violation。FAIL 原因仅为 `tests/test_application_smoke.py` 的 subprocess
证据不完整：多数 exit `2/3` case 未统一断言 stdout/stderr，且缺少真实 executable 的 Runner exit `4` failure。

本轮已确认并冻结测试验收分层，不改变 D028～D033 或 production composition order：

- Model Smoke OFF executable 覆盖 help、CLI/RuntimeConfig/YAML errors，以及不依赖 frozen ONNX 可到达的
  component initialization failures；
- Model Smoke ON executable 覆盖 actual ORT serial flow、missing output parent、`overwrite=false`、Runner
  source decode failure exit `4`、deterministic JSON 和 Console；
- Model Smoke OFF `result_sinks` unit test 覆盖 output parent、overwrite、atomic rename、旧文件保留、temporary
  file cleanup 和 sink lifecycle。

因此 output preflight 固定为 **ON-only executable coverage**：不要求 OFF application subprocess 到达该阶段，
不将 JsonSink 移到 Engine initialize 前，不增加 fake backend、production test seam、Service Locator 或 DI container，
也不让 OFF 依赖 frozen ONNX。

remediation 已补强 application subprocess evidence：所有 exit `2/3/4` failure 统一断言 expected code、empty
stdout、non-empty/stable stderr context；真实 `broken.png` 在 DirectorySource create 成功后于
`SerialRunner → source.next()` decode fail-fast，断言 exit `4`、无 final JSON 与无 JsonSink temporary file；
`overwrite=false` 断言既有目标内容不变。M4.6 remediation 状态为 **COMPLETE**，但 Gate rerun 仍为
**PENDING**；M4 保持 `IN_PROGRESS`，M4.7 未开始。

### M4.7 — Documentation-only Closeout

- **objective**：在 M4 Final Gate PASS 后更新 M4 plan/TASKS，必要时 DECISIONS，记录真实回归并标记 M4 CLOSED。
- **starting facts**：M4.6 明确 PASS；M4 production commits 和验证结果已存在。
- **allowed changes**：`docs/personal/M4_EXECUTION_PLAN.md`、`docs/personal/TASKS.md`，仅确有长期新决策时更新 DECISIONS。
- **forbidden scope**：production/test/CMake/config/tool/assets 改动、补功能、M5 implementation、push。
- **planned files/modules**：仅 closeout 文档。
- **required contracts**：准确记录 OFF/ON、Strict/ASan/UBSan 真实状态、commit chain、未完成 M5 scope。
- **required tests**：不因 docs 重跑无关测试；复核 Gate evidence、`git diff --check` 和 docs-only scope。
- **acceptance criteria**：M4 `CLOSED`，下一阶段明确为 M5 Level C and ORT Baseline；无虚构 evidence。
- **expected commit message**：`docs: close M4 serial baseline`。
- **next step**：M5 planning/Level C and ORT Baseline，必须由独立任务启动。
- **Gate**：Documentation-only Closeout；前置必须是 M4.6 PASS。

## 10. Gate 策略

```text
M4.1 ┐
M4.2 ├─ no Gate
M4.3 ┘

M4.4 → read-only Shallow Gate
M4.5 → M4.6 read-only Standard Final Gate
M4.7 → Documentation-only Closeout
```

M4 不做 Deep Gate。M5 完成完整 Level C、formal Profiler 和 ORT performance baseline 后再执行 Deep Gate。

## 11. Codex Execution Protocol

后续每个执行对话只需输入：

```text
执行 M4.x。
```

事实权威：

- `AGENTS.md`
- `docs/personal/M4_EXECUTION_PLAN.md`
- `docs/personal/TASKS.md`

严格执行本文件对应 M4.x task card；不得进入下一阶段，不得 push。完成后输出：起点 Git 事实、修改文件、
核心合同、执行测试及结果、范围/Git 审计、local commit hash 和下一步状态。若仓库事实与冻结方案出现不可
调和冲突，停止修改和提交，报告冲突位置、影响及需要人工决定的问题，不得静默选择替代设计。

## 12. M4.0 完成结论

- repository audit 未发现冻结 M4 方案与现有 M1/M2/M3 contracts 的不可调和冲突；
- M4 production code 仍为未开始；本文所有新增 runtime/source/sink/runner 类型均标为 planned；
- M4.0 完成后 M4 总体状态为 `IN_PROGRESS`，M4.1 为 `pending`；
- 下一步且唯一允许的实现任务为 M4.1 Runtime Contracts, Config and CLI Parser。
