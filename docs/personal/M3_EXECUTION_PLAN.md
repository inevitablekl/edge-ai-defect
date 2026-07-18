# M3 PostProcessor Execution Plan

状态：`IN_PROGRESS`（design frozen，2026-07-18）。M3.0～M3.5 实现已完成；当前处于 M3 Deep
Gate remediation。M3 仍未关闭；完成 evidence 修复后必须重新执行只读 Deep Gate。M3.4 已完成
metadata-driven inverse LetterBox、continuous clipping 与 public `PostProcessor::process()`
integration。

## 1. 目标与边界

M3 的目标是把 M2 已验证、backend-neutral 的 frozen raw output 转换成确定、可复查的
`Detection` list：

```text
core::HostTensor raw output [1,10,8400]
  ↓
YOLOv8 candidate decode + confidence filter
  ↓
class-aware NMS
  ↓
inverse LetterBox + clip
  ↓
std::vector<Detection>（original-image coordinates）
```

M3 只实现 frozen `yolov8n_neudet_frozen` 的单图、静态 contract；不是通用多模型
解析框架。它消费 `IInferenceEngine::run()` 的 `HostTensor`，但不修改 Engine contract、
不调用 ONNX Runtime，也不管理图像文件或 runner。

M3 不实现：

- 图像读取、`DirectorySource`、`FrameSource`、`SerialRunner`、`ResultSink`、JSON
  业务输出、Profiler、benchmark；
- TensorRT、CUDA、GPU EP、ROS2、Qt、Pipeline；
- batch > 1、dynamic shape、arbitrary output layout、device tensor、embedded NMS 或
  通用多模型/plugin abstraction；
- `IPostProcessor` 抽象基类、`InferenceOutput` 或对 M2 `IInferenceEngine` 的任何改动。

完整 E2E Level C 仍属于 M5，不在 M3 混入 Engine/Preprocessor/Runner 或性能测量。

## 2. 审计事实与语义核对

### 2.1 已由当前 Git 资产验证的事实

- `configs/model_contracts/yolov8n_neudet_frozen.yaml` 冻结 output 为 `output0`、
  `float32`、`BCN`、`[1,10,8400]`，且 class count 为 6；类别顺序是 `crazing`、
  `inclusion`、`patches`、`pitted_surface`、`rolled-in_scale`、`scratches`。
- M2 Level B 的 tracked raw assets 与 provenance 也记录相同 `float32 BCN
  [1,10,8400]` contract、84000 elements 和同一 frozen ONNX SHA256。
- `tools/validation/compare_pt_onnx.py` 把 raw tensor 交给 Ultralytics 8.4.50
  `non_max_suppression(..., nc=6)`。该实现对 `BCN` tensor 的前四个 channels 调用
  `xywh2xyxy`，并将 channels `4:10` 当作六个类别分数；`multi_label` 默认 `False`。
- 对 `[1,10,8400]`，Ultralytics 的 end-to-end / embedded-NMS 分支条件
  `prediction.shape[-1] == 6` 不成立。因此该模型没有 objectness 独立 channel，也没有
  embedded NMS 输出。
- `ImageTransformMetadata` 已由 M1 的 `Preprocessor`/LetterBox 生成，含原图尺寸、
  target 尺寸、gain 与四侧 padding；它足以在不读取图像的前提下恢复坐标。

结论：以下 M3 语义与当前 model contract、Python reference path 和 C++ core contracts
一致：raw output 是六类 YOLOv8 `cx, cy, w, h, class_scores[6]`，没有 objectness。

### 2.2 现有 reference 的限制（非语义冲突）

现有 `compare_pt_onnx.py` 是 PT/ONNX export evidence：它对两方调用同一 Ultralytics
NMS，随后将 detection 按 `(-confidence, class_id)` 排序。Ultralytics NMS 对 score
调用 descending `argsort`，但未为相同 score 指定 candidate-index tie-break；该脚本也不
记录 candidate index，并在 NMS 后把框恢复到原图。因此它不能作为 M3 独立
PostProcessor-only validation 的 reference，不能证明 C++ decode/NMS 正确。

这不是模型输出语义冲突。M3 将新增独立 Python reference，明确实现本文件的 canonical
排序、candidate index、raw-model-space NMS 和 inverse LetterBox 规则；不得复用 C++
helper，也不得以现有 shared-NMS PT/ONNX report 替代 M3 evidence。

`ARCHITECTURE.md` 的 Detection（含 `class_name`）是 suggested future application
structure，`REQUIREMENTS.md` 也只说 class name `SHOULD` included；M3 的最小
`Detection` 保留 stable `class_id`，class name 继续由 frozen `ModelContract` 在 M4
application/presentation 层映射，不构成 contract 冲突。

## 3. 冻结 public contract

建议 M3.1 新增：

```cpp
namespace edge_ai_defect::postprocess {

struct Detection {
    float x1 = 0.0F;
    float y1 = 0.0F;
    float x2 = 0.0F;
    float y2 = 0.0F;
    float confidence = 0.0F;
    int class_id = 0;
    std::size_t candidate_index = 0;
};

struct PostprocessConfig {
    float confidence_threshold = 0.25F;
    float iou_threshold = 0.45F;
    std::size_t max_nms = 30000U;
    std::size_t max_det = 300U;
    float max_wh = 7680.0F;
    bool agnostic = false;
    bool multi_label = false;
};

class PostProcessor final {
public:
    explicit PostProcessor(PostprocessConfig config = {});

    [[nodiscard]] core::Status process(
        const core::HostTensor& raw_output,
        const preprocess::ImageTransformMetadata& transform,
        std::vector<Detection>* output) const;
};

}  // namespace edge_ai_defect::postprocess
```

没有 `IPostProcessor`：当前只有 frozen YOLOv8 decoder，尚无第二个 backend-independent
postprocess implementation 的真实需求。`PostprocessConfig` 是 in-process 的小型
validated value object，不新增 YAML、plugin 或 runtime tuning surface。

坐标合同冻结为 **original-image xyxy space**。`process()` 必须接收
`ImageTransformMetadata`，因为 M1 已经产生它且架构/需求要求恢复 bounding box。M3 在
model input space 完成 decode/filter/NMS，再对保留框执行：

```text
x_original = (x_model - pad_left) / gain
y_original = (y_model - pad_top)  / gain
```

inverse LetterBox 必须直接使用 metadata 已保存的 `gain`、`pad_left` 和 `pad_top`，不得
在 `PostProcessor` 内依据尺寸重新推导 gain 或 padding。最后分别 clip 到闭区间
`[0, original_width]`、`[0, original_height]`。xyxy 使用连续浮点几何：
`width=max(0,x2-x1)`、`height=max(0,y2-y1)`，面积为 `width*height`，不使用 inclusive
pixel 的 `+1` 语义。为与固定 Ultralytics 8.4.50 的
`scale_boxes() -> clip_boxes()` 对齐，clip 只做 clamp：不做 post-clip degeneracy 或
minimum-size filter。最终 `Detection` 可以有零宽或零高，但坐标必须 finite，且满足
`0 <= x1 <= x2 <= original_width`、`0 <= y1 <= y2 <= original_height`。M3 不读取图像、
不推断 transform，也不把坐标恢复延后到 Runner。

## 4. 冻结 decode、过滤和确定性语义

输入在任何解析前必须通过 `core::validate_host_tensor()`，并严格匹配：`float32`、
`BCN`、rank 3、`[1,10,8400]`、84000 elements。生产路径必须扫描所有 raw elements 的
finite 性；任何 NaN 或 Inf 都是 input failure，而非静默跳过 candidate。

BCN contiguous storage 的读取索引是 `channel * 8400 + candidate_index`。每个 candidate
按如下规则处理：

1. channels 0～3 分别为 `cx, cy, w, h`；channels 4～9 为 class ids 0～5 的分数。
2. `multi_label=false`：只选择最大 class score；分数完全相等时选择较小 `class_id`。
3. 仅在 `confidence > 0.25F` 时保留；恰为 `0.25F` 必须丢弃。
4. 所有 raw fields 已 finite 后，`w <= 0` 或 `h <= 0` 的 candidate 丢弃（正常过滤，
   不是整次 process 失败）。
5. 转换为 model-input-space bbox：
   `x1=cx-w/2`、`y1=cy-h/2`、`x2=cx+w/2`、`y2=cy+h/2`。M3 不在 NMS 前 clip，以保持
   与现有 Ultralytics reference 的 decode/NMS 顺序一致。
6. 每个保留候选永久携带原始 `candidate_index`（0～8399）。

canonical pre-NMS order 和 final output order 均为：`confidence` 降序、`class_id`
升序、`candidate_index` 升序。必须用显式 comparator；不得依赖 `std::sort` 对等价元素
的未规定顺序。该 canonical tie-break 是 M3 新增的确定性约束，弥补现有 Python export
comparison 未冻结 equal-score 顺序的缺口。

## 5. 冻结 NMS

- NMS 是 class-aware：`agnostic=false`，不同 class 不会互相抑制。
- 实现采用与当前 Ultralytics reference 一致的 class-offset：
  `offset = class_id * max_wh`，固定 `max_wh=7680.0F`；对 offset 后的 xyxy box 做 NMS。
  M3 只接受 640×640 frozen model output，`max_wh` 是冻结 reference constant，不是通用
  coordinate policy。
- IoU 和 bbox arithmetic 使用 `float`，与 raw `float32`/Ultralytics tensor path 对齐；
  candidate 已按 canonical order 处理。
- 仅当 `IoU > 0.45F` 才抑制；`IoU == 0.45F` 不抑制。
- `max_nms=30000`：若 confidence-filtered candidate 超过上限，先使用 canonical
  pre-NMS order 截断到 30000；随后 NMS。`max_det=300`：NMS keep list 按 canonical order
  取前 300，再恢复坐标/clip。
- NMS 前的零/负面积框已由 decode 丢弃；这与 post-clip degeneracy 不同。固定
  Ultralytics 8.4.50 的 `scale_boxes()` 只在恢复后调用 `clip_boxes()`，无后续退化框或
  minimum-size filter；M3 因而保留 clip 后零宽/零高 `Detection`。实现不得调用 OpenCV
  DNN NMS、embedded NMS 或 CUDA NMS。

## 6. 错误、metadata 与原子性

不新增 M3 专用 `ErrorCode`。现有 `core::Status` 足够表达该阶段的输入和配置错误：

| 条件 | ErrorCode |
| --- | --- |
| `output == nullptr`、非法 `PostprocessConfig`、非法 transform、raw non-finite | `kInvalidArgument` |
| rank/batch/channel/candidate shape 不匹配 | `kInvalidShape` |
| 非 float32 raw tensor | `kUnsupportedDataType` |
| 非 BCN raw tensor | `kUnsupportedLayout` |
| `validate_host_tensor()` data count 不一致 | `kDataSizeMismatch` |

transform 必须具有正 original/target/resized dimensions、finite positive gain、非负 pads，
且 `resized_width + pad_left + pad_right == target_width`、
`resized_height + pad_top + pad_bottom == target_height`；target 必须为 640×640。

`process()` 使用 local candidate/detection vector，只有完整成功后才 move-assign
`*output`。所有 failure（包括 null output 不可写的情况）必须保持调用方既有 output
不变。无有效 detection 是成功且返回空 vector；decode 阶段的负/零 `w/h` 是候选过滤，
而 clip 后零面积框必须保留，不是 failure。

## 7. 模块与文件归属

M3.1 预计新增：

```text
include/edge_ai_defect/postprocess/detection.hpp
include/edge_ai_defect/postprocess/postprocess_config.hpp
include/edge_ai_defect/postprocess/postprocessor.hpp
src/postprocess_config.cpp
src/postprocessor.cpp
tests/test_postprocessor_contract.cpp
```

为保持 backend independence，建议新增 `edge_ai_postprocess` static target：public headers
依赖 `edge_ai_core` 和已存在的 `ImageTransformMetadata` declaration；implementation 仅链接
`edge_ai_core`，不链接 `edge_ai_backend_ort`、ONNX Runtime、OpenCV DNN、CUDA 或 TensorRT。
`edge_ai_infer`、Runner 和任何 application composition 不在 M3 修改范围。

## 8. 测试与一致性验证

### 8.1 A：人工 raw tensor unit tests

`test_postprocessor` 至少覆盖：

- 单 candidate、`confidence == 0.25F`、`confidence` 略大于 0.25F；
- 同类别重叠框、不同类别重叠框、IoU 恰为 0.45；
- `max_nms` 截断和 `max_det=300`；
- canonical score/class/candidate tie、class-score tie 选较小 class、candidate index 保留；
- inverse LetterBox、final continuous clip、clip 后零宽/零高 Detection 保留；
- 非 finite、负/零宽高、raw shape/layout/dtype/data-size、invalid transform/config；
- `nullptr` output 和每一种 failure 的 output 原子性。

测试中的 IoU 精确边界应使用可审计的 float fixture，不得通过扩大 threshold 容差掩盖
比较运算符错误。finite scan 只要 M3 production 已实现即可由同一测试验证，不另建
test-only semantic bypass。

### 8.2 B：M3 PostProcessor-only Python/C++ validation

早期计划中的 `postprocessor_level_b` 名称和路径已被取代，不再是有效资产或测试名称。正式
名称是 **PostProcessor-only Validation**，使用以下实际、Git-tracked 路径：

```text
tests/data/postprocessor_reference/
results/validation/postprocessor_only/
tools/validation/generate_postprocessor_reference_assets.py
tools/validation/postprocessor_reference.py
tools/validation/generate_postprocessor_reference_provenance.py
tests/test_postprocessor_reference.cpp
```

输入为 headerless little-endian `float32 BCN [1,10,8400]` synthetic raw tensor。每个 case
独立记录 raw、metadata、config、Python TSV golden 和 manifest；C++ validator 对同一 raw asset
仅调用 public `PostProcessor::process()`，比较完整有序 Detection。验证不经过 C++ preprocessing、
不调用 `OnnxRuntimeEngine`、不读取图像，也不产生 benchmark。

### 8.3 Gate

M3 Deep Gate 要求：clean Git scope audit；适用的 Model Smoke OFF/ON 回归；M3 unit/negative
tests；PostProcessor-only evidence 的 SHA/provenance 和 Python/C++ 全 Detection comparison 通过。
strict、ASan/UBSan 仅在项目已配置时执行；目前均为 `Not configured`，不得写作通过。Level C
complete pipeline / benchmark 继续留给后续 Serial Baseline 阶段。

## 9. 推荐提交拆分

1. `docs: freeze M3 postprocessor execution plan`
2. `feat: add detection and postprocessor contracts`
3. `feat: decode YOLO raw output candidates`
4. `feat: implement class-aware NMS`
5. `feat: integrate postprocessor pipeline`
6. `test: validate postprocessor against Python reference`
7. `docs: close M3 postprocessor`

每个步骤结束后只验证本步骤边界；不自动进入下一阶段，不混入 M4 Runner 或 M5 benchmark。

## 10. M3.1 Contract 实际结果

M3.1 已创建：

- `Detection`：original-image continuous xyxy、`float confidence`、`int class_id`、
  `std::size_t candidate_index`；不含 class name、frame/time、OpenCV/ORT/TensorRT 类型或
  serialization。
- `PostprocessConfig`：默认值严格为 0.25/0.45/30000/300/7680、`agnostic=false`、
  `multi_label=false`；`validate_postprocess_config()` 使用既有 `kInvalidArgument` 拒绝
  non-finite/越界 threshold、非法 limits/max_wh，以及 M3 禁止的 agnostic/multi-label。
- concrete `PostProcessor`：保存 value-type config，保持默认 copy/move，声明
  `process(const HostTensor&, const ImageTransformMetadata&, vector<Detection>*) const`。
  M3.1 未提供 `process()` definition，contract test 只验证 signature，不以 stub 模拟
  decode 成功或空输出。
- `edge_ai_postprocess` static target：只显式依赖 `edge_ai_core`；不链接
  `edge_ai_backend_ort`、ONNX Runtime、TensorRT、CUDA 或 OpenCV DNN。由于现有
  `ImageTransformMetadata` header 属于 `edge_ai_core` 的 OpenCV-backed preprocess
  contract，OpenCV core/imgproc 仅通过既有 `edge_ai_core` PUBLIC dependency 传递，M3.1
  未新增 OpenCV component。

M3.1 contract test 不创建 8400 candidates、不调用 `process()`，也不实现/测试 decode、
IoU、NMS、inverse LetterBox 或 clipping。Model Smoke OFF configure/build 成功；新增
`postprocessor_contract` 与 `test_core` 定向 CTest 为 2/2 PASS，当前完整 CTest 为
12/12 PASS。strict 与 ASan/UBSan 仍为 `Not configured`，未写成通过。下一步为 M3.2
candidate decode。

## 11. M3.2 Candidate Decode 实际结果

M3.2 新增 internal-only `src/postprocess_detail.hpp`：

```cpp
namespace edge_ai_defect::postprocess::detail {

struct DecodedCandidate {
    float x1;
    float y1;
    float x2;
    float y2;
    float confidence;
    int class_id;
    std::size_t candidate_index;
};

core::Status decode_candidates(
    const core::HostTensor& raw_output,
    const PostprocessConfig& config,
    std::vector<DecodedCandidate>* output);

}  // namespace edge_ai_defect::postprocess::detail
```

该 header 仅供 `src/postprocessor_decode.cpp` 和 M3.2 test 使用，不属于 public include
API。helper 在写入 output 前完成 `validate_postprocess_config()`、
`validate_host_tensor()`、固定 `float32 BCN [1,10,8400]` / 84000-element contract 与全量
finite scan；任何 NaN、`+Inf` 或 `-Inf` 返回 `kInvalidArgument`，不产生部分候选且保持
caller output 不变。

BCN 读取固定为 `data[channel * 8400 + candidate_index]`。每个 valid candidate 保留
model-input continuous xyxy：先跳过 `w <= 0` 或 `h <= 0`，然后按 class id 0～5 递增扫描，
仅当 `score > current_best` 才更新，因此 score tie 选择最小 class id；仅当
`confidence > config.confidence_threshold` 才保留。decode 不 round、clip、inverse
LetterBox、添加 class offset 或产生 public `Detection`。若 raw fields 虽 finite 但 float
xyxy 运算溢出为 non-finite，则该 candidate 作为非法 geometry 跳过，不影响其他候选。

pre-NMS candidates 以完整 comparator 排序：confidence 降序、class id 升序、candidate
index 升序，随后保留前 `min(size, config.max_nms)` 项；`max_det`、`max_wh`、agnostic 与
multi_label 在本阶段不参与 NMS。`PostProcessor::process()` 继续没有 definition。

`test_postprocessor_decode` 覆盖 BCN/BNC distinguishability、阈值严格边界、argmax ties、
continuous xyxy、deterministic ordering、max_nms、invalid geometry、empty success、all
required contract failures 和 output atomicity。Model Smoke OFF configure/build 成功；
`postprocessor_contract` / `postprocessor_decode` / `test_core` 为 3/3 PASS，完整 CTest
为 13/13 PASS。strict 与 ASan/UBSan 仍为 `Not configured`。下一步为 M3.3 IoU 与
class-aware NMS。

## 12. M3.3 IoU / Class-aware NMS 实际结果

M3.3 保持 `DecodedCandidate` 为 internal-only model-input continuous xyxy 表示，并在
`src/postprocessor_nms.cpp` 新增两个 detail helpers：

```cpp
float continuous_iou(const DecodedCandidate& lhs,
                     const DecodedCandidate& rhs,
                     float lhs_offset = 0.0F,
                     float rhs_offset = 0.0F) noexcept;

core::Status apply_class_aware_nms(
    const std::vector<DecodedCandidate>& sorted_candidates,
    const PostprocessConfig& config,
    std::vector<DecodedCandidate>* output);
```

`continuous_iou()` 使用 `max(0, min(x2) - max(x1))` 与 `max(0, min(y2) - max(y1))`
计算交集，面积没有 inclusive-pixel `+1`。零/负 union 或任一中间几何计算为 non-finite 时
返回 `0.0F`；这不是 public error path。NMS 在调用前验证实际参与的 candidates：class id
必须在 frozen `[0,6)`，coordinate/confidence 必须 finite，且连续 xyxy 面积为正；不满足时
返回 `kInvalidArgument`，且 caller output 不变。

NMS 消费 M3.2 已 canonical-sorted 的 candidates，不重新排序。它至多处理前
`min(size, max_nms)` 项（M3.2 正常路径已经完成同一上限截断），按顺序贪婪保留当前未抑制
candidate，并将其与后续未抑制 candidates 比较。比较时只临时将四个 xyxy coordinate 加上
`class_id * max_wh`；因此同类别按原几何竞争，不同类别被 class-offset 分离，返回的
`DecodedCandidate` 坐标从不含 offset。仅 `IoU > iou_threshold` 抑制；相等不抑制。达到
`max_det` 个 retained candidates 立即停止，因而 retained order 保持 M3.2 canonical order。
最坏时间复杂度为 `O(K^2)`，其中 `K = min(sorted_candidates.size(), max_nms)`；本阶段没有
buffer reuse、parallel NMS 或任何性能声明。

`test_postprocessor_nms` 覆盖 disjoint/identical/partial/touching/zero-area IoU、无 `+1`
语义、non-finite offset、严格 threshold 边界、same/cross-class behavior、保留顺序、
`max_nms`/`max_det`、invalid config/candidate、empty success 与 failure atomicity。Model
Smoke OFF configure/build 成功；`test_core` / `postprocessor_contract` /
`postprocessor_decode` / `postprocessor_nms` 定向 CTest 为 4/4 PASS，完整 CTest 为
14/14 PASS。strict 与 ASan/UBSan 仍为 `Not configured`，不能写作通过。

M3.3 未修改 M3.2 decode/排序语义、Preprocessor、Engine 或任何 public header；没有 inverse
LetterBox、clipping、public `Detection` conversion、`PostProcessor::process()` definition、
OpenCV DNN NMS、CUDA/TensorRT/ORT/Runner/Pipeline 或 benchmark。下一步仅可进入 M3.4，完成
metadata-driven inverse LetterBox、clip 与 `process()` integration，再安排独立 M3 Level B
evidence。

## 13. M3.4 Transform / Clip / Public Process 实际结果

M3.4 在此前发现的 reference conflict 后，按人工架构决定和 D027 修订为与本地固定
Ultralytics 8.4.50 parity 一致的语义：其 `scale_boxes()` 做 inverse transform 后调用
`clip_boxes()`，后者仅 clamp 四个 xyxy coordinate 并直接返回。C++ 因而不做 post-clip
degeneracy 或 minimum-size filter；零宽/零高 `Detection` 保留，供后续显式业务策略决定
是否过滤。该选择不改变 M3.2 对 raw `w <= 0` / `h <= 0` 的 skip，也不改变其 finite raw
和 xyxy-overflow policy。

实际 metadata 是 M1 `ImageTransformMetadata` 的以下字段：`original_width`、
`original_height`、`target_width`、`target_height`、`resized_width`、`resized_height`、
`double gain` 与 `pad_left/right/top/bottom`。detail validator 要求 original/resized dimensions
为正、target 正好为 frozen 640×640、gain finite positive、padding 非负，且
`resized_width + pad_left + pad_right == target_width`、
`resized_height + pad_top + pad_bottom == target_height`。它不从 image dimensions 重新推导
gain 或 padding。

`transform_and_clip_detections()` 对 NMS retained candidates 的每个坐标直接使用：

```text
x_original = (x_model - pad_left) / gain
y_original = (y_model - pad_top)  / gain
```

随后 x clamp 到 `[0, original_width]`，y clamp 到 `[0, original_height]`，不 round、不转
integer、无 `+1`。所有恢复中间值及最终 `float` coordinate 必须 finite，否则返回
`kInvalidArgument`，且 caller output 保持原值。成功结果保留 NMS accepted order、
confidence、class id 与 candidate index；不重新排序、不重新运行 NMS，也不向实际坐标写入
class offset。

`PostProcessor::process()` 已有真实完整行为：检查 `output`、验证 config、验证 transform、
调用 `decode_candidates()`、调用 `apply_class_aware_nms()`、调用 transform/clip helper，最后
才 move-assign caller output。每一失败路径均保持 caller output，空 candidate result 成功并
提交 empty vector。它没有改动 Engine、Preprocessor、M3.2 decode 或 M3.3 NMS。

新增 `test_postprocessor_process` 覆盖 identity 和 padded inverse transform、M1 odd asymmetric
padding（使用保存的 `pad_left=80` 而非重新推导 half padding）、continuous boundary clipping、
left/top/right/bottom clip 后退化框保留及 provenance/order、NMS-before-transform、class-aware
public integration、strict confidence、`max_nms`/`max_det`、raw/config/metadata failures、null
output、failure atomicity 和 empty success。Model Smoke OFF configure/build 成功；定向 CTest
`test_core` / `postprocessor_contract` / `postprocessor_decode` / `postprocessor_nms` /
`postprocessor_process` 为 5/5 PASS，完整 CTest 为 15/15 PASS。strict 与 ASan/UBSan 仍为
`Not configured`，不能写作通过。

M3.4 implementation complete。下一步为 M3.4 shallow Gate 的只读范围/行为审查；通过后才可
执行 M3.5 独立 Python/C++ PostProcessor-only Level B validation。未实现 Runner、Pipeline、
benchmark、TensorRT、CUDA 或任何 Python/C++ golden validation。

## 14. M3.5 PostProcessor-only Validation 冻结规则

M3.5 的正式名称是 **PostProcessor-only Validation**，不是 Level C。它使用 Git-tracked
synthetic raw `float32 BCN [1,10,8400]`、固定 `ImageTransformMetadata` 和冻结
`PostprocessConfig`，将独立 Python reference 的完整、有序 `Detection` 与 C++ public
`PostProcessor::process()` 输出逐项比较。它不调用 ONNX Runtime、Preprocessor、Engine、
Runner 或任何 C++ detail helper；完整 E2E Level C 仍留给后续 Serial Baseline 阶段。

冻结资产目录为 `tests/data/postprocessor_reference/`，初始 cases 为：

- `case_no_padding`：decode argmax/threshold/order、same-class suppression、cross-class
  retention、candidate-index tie-break 和 ordinary retained box；
- `case_odd_padding`：M1 已验证的 horizontal odd padding，`gain=640/641`、`pad_left=80`、
  `pad_right=81`，覆盖 inverse transform、四向 clipping 与 post-clip zero-width/zero-height
  Detection retain；
- `case_odd_vertical_padding`：M1 已验证的 vertical odd padding，`gain=640/641`、
  `pad_top=80`、`pad_bottom=81`，独立证明实际 `pad_top` 被使用。

独立 Python reference 只依赖 Python standard library 和 NumPy；不得 import Ultralytics、
ONNX Runtime、Torch、OpenCV DNN、project C++ binding 或 C++ output。它直接按 frozen BCN
index、argmax、strict thresholds、canonical sort、float32 class-offset IoU、greedy NMS、
metadata-driven inverse LetterBox 和 clamp-only clipping 实现语义。NMS/IoU 所有 candidate
arithmetic 显式落在 `numpy.float32`，与 C++ `float` 运算对齐；transform 将 float32
candidate coordinate 先提升为 Python `float`（对应 C++ `double`），与 integer padding 作
double subtraction/division，再在 clamp 后显式 cast 回 `numpy.float32`（对应最终 Detection
coordinate）。

每个 case 包含 little-endian `raw_output.f32le`、`metadata.json`、`config.json`、Python
`python_golden_detections.tsv` 与 `manifest.json`。结果目录冻结为
`results/validation/postprocessor_only/`，每个 case 记录 `cpp_detections.tsv` 和
`comparison_report.json`，共同记录 `provenance.json`。TSV 固定 UTF-8/LF，列为
`x1,y1,x2,y2,confidence,class_id,candidate_index`；float 以能 round-trip float32 的精度输出。

验收规则冻结如下，禁止根据比较结果放宽：

| 项目 | 规则 |
| --- | --- |
| Detection count、顺序、`class_id`、`candidate_index` | 必须完全一致 |
| `confidence` | 每项 `abs(python-cpp) <= 1e-6` |
| bbox 的每个 `x1/y1/x2/y2` | 每项 `abs(python-cpp) <= 1e-4` |
| finite | 双方全部 Detection 字段必须 finite |

comparison report 必须记录 count/exact-field pass、confidence `max_abs`/`mean_abs`/最大误差
detection index，以及 bbox 全坐标 `max_abs`/`mean_abs`/最大误差 detection index 和 coordinate
name。任一 exact 或 float 规则失败即 FAIL；保留 report，定位首个不同 Detection，不修改
golden、不删除 case、不放宽阈值。M3.5 通过后下一步为 M3 Deep Gate，仍不关闭 M3。

## 15. M3.5 PostProcessor-only Validation 实际结果

M3.5 新增 `tools/validation/generate_postprocessor_reference_assets.py` 与
`tools/validation/postprocessor_reference.py`。两者只依赖 Python standard library 和 NumPy；
reference 不 import Ultralytics、ONNX Runtime、Torch、OpenCV 或 project C++ binding，不读取
C++ output，且独立实现 frozen decode、float32 IoU/class-offset greedy NMS、double transform
promotion、float32 final coordinate cast 与 clamp-only clipping。资产生成器只写 deterministic
synthetic BCN input/metadata/config/description；reference 独立读取它们并生成 TSV golden 与
SHA-bearing manifest。

tracked data 位于 `tests/data/postprocessor_reference/`，evidence 位于
`results/validation/postprocessor_only/`：

- `case_no_padding`：7 detections。覆盖同类高 IoU suppression、不同类同框 retain、严格
  `confidence > 0.25`、class-score tie 选择小 class id、same confidence/class 的 candidate
  index order 和不重叠 ordinary box；
- `case_odd_padding`：5 detections。使用 M1 horizontal odd padding
  (`original=480×641`、`gain=640/641`、`pad_left/right=80/81`)，覆盖 inverse transform、
  partial four-side clip 和 zero-width/zero-height retain；
- `case_odd_vertical_padding`：5 detections。使用 M1 vertical odd padding
  (`original=641×480`、`gain=640/641`、`pad_top/bottom=80/81`)，独立验证实际 `pad_top`
  使用。

`test_postprocessor_reference` 仅构造 public `HostTensor` 并调用
`PostProcessor::process()`；它不调用 detail API。它读取 raw/metadata/config/Python TSV，写出
C++ TSV 和 per-case report，并逐项检查 count/order、class id、candidate index、finite、
confidence 和 bbox。三个 case 的 exact fields 全部一致；confidence `max_abs=0`、
`mean_abs=0`，bbox coordinate `max_abs=0`、`mean_abs=0`，均在冻结的 `1e-6` / `1e-4` 限制内。

首轮 M3.5 evidence 的详尽 provenance/validator hardening 需要按本计划的 remediation protocol
刷新；刷新前不得将其当作 Deep Gate closure evidence。M3.5 implementation complete；当前下一步是
完成 remediation 后重新执行 M3 Deep Gate。仍未实现 Runner、Pipeline、benchmark、TensorRT、CUDA
或 Level C。

## 16. M3 Deep Gate remediation protocol（进行中）

TSV validator 必须精确接受一行 header，且每条 Detection record 只能有七个非空字段、六个 TAB、
无 leading/trailing delimiter，并完整解析 finite float、`class_id` 与 `candidate_index`。CTest
negative driver 必须在 build 临时目录复制 golden，验证 trailing/extra/missing field、duplicate
header、corrupt float/integer、NaN、Inf、missing/extra record 和中间 blank line 都被 validator
拒绝；negative CTest 在拒绝发生时自身 PASS，不能修改 tracked goldens 或结果目录。

provenance 采用 source/evidence 两提交协议：Commit A 固定验证器、CTest 和文档后，必须从 clean
Commit A 记录完整 `source_commit`、`source_branch` 和 `source_worktree_clean=true`，再重新生成
evidence。evidence 进入随后的 Commit B；它有意不引用尚未存在的 evidence commit，以避免自引用
循环。公共 provenance 同时记录 Python/NumPy、validator/CMake/reference/asset-generator/
provenance-generator SHA256、每个 case 的全部 evidence SHA、detection count、case PASS/FAIL、
overall PASS 和验证命令；固定 Ultralytics 8.4.50 仅为 semantic reference，不是 runtime dependency。

当前阈值保持不变：Detection count/order/`class_id`/`candidate_index` 必须 exact，confidence
`abs <= 1e-6`，bbox coordinate `abs <= 1e-4`，全部字段 finite。历史限制必须保留：阈值和首轮
结果在 `4437d84` 中同时首次进入 Git，历史无法单独证明“阈值先冻结、再执行”；当前误差均为零且
未发现阈值放宽，但该时间顺序不能由已有 Git 历史倒推。remediation 完成后仍只可重跑 Deep Gate，
不得标记 M3 CLOSED。
