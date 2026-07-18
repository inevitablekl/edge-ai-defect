# M3 PostProcessor Execution Plan

状态：`FROZEN`（2026-07-18）。M3.0 只完成仓库事实审计、语义核对和设计冻结；
production `PostProcessor`、decode、NMS、`Detection` 和 M3 tests 均尚未实现。

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

最后分别 clip 到 `[0, original_width]`、`[0, original_height]`。clip 后宽或高不正的框
丢弃。M3 不读取图像、不推断 transform，也不把坐标恢复延后到 Runner。

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
- NMS 前的零/负面积框已丢弃；任何 clip 后零/负面积框也丢弃。实现不得调用
  OpenCV DNN NMS、embedded NMS 或 CUDA NMS。

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
不变。无有效 detection 是成功且返回空 vector；单个负宽高或 clip 后零面积框是候选过滤，
不是 failure。

## 7. 模块与文件归属

M3.1 预计新增：

```text
include/edge_ai_defect/postprocess/detection.hpp
include/edge_ai_defect/postprocess/postprocessor.hpp
src/postprocessor.cpp
tests/test_postprocessor.cpp
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
- inverse LetterBox、final clip 和 clip 后零面积 discard；
- 非 finite、负/零宽高、raw shape/layout/dtype/data-size、invalid transform/config；
- `nullptr` output 和每一种 failure 的 output 原子性。

测试中的 IoU 精确边界应使用可审计的 float fixture，不得通过扩大 threshold 容差掩盖
比较运算符错误。finite scan 只要 M3 production 已实现即可由同一测试验证，不另建
test-only semantic bypass。

### 8.2 B：M3 PostProcessor-only Python/C++ validation

验证名冻结为 `postprocessor_level_b`，资产目录冻结为：

```text
tests/data/postprocessor_level_b/
results/validation/postprocessor_level_b/
tools/validation/generate_postprocessor_level_b_reference.py
tools/validation/generate_postprocessor_level_b_provenance.py
tests/test_postprocessor_level_b.cpp
```

输入是一个 Git-tracked、headerless little-endian `float32 BCN [1,10,8400]` fixed raw
tensor。优先复制并冻结 M2 已生成的 `python_golden_output.f32le` 为 M3 的独立 input
asset；M3 manifest 必须记录 source evidence、model SHA256、input SHA256、dtype、layout、
shape、element count、PostprocessConfig、完整 `ImageTransformMetadata` 和生成 command。
复制后 M3 asset 的 SHA256、`SHA256SUMS`/CTest verifier 与 manifest 必须独立维护，不能
在 validation 时读取/调用 C++ ORT Engine 或 C++ Preprocessor。

独立 Python reference 必须直接从该 raw binary 实现本文件的 decode/filter/canonical
sort/class-offset NMS/inverse LetterBox/clip，不调用 Ultralytics NMS。它输出 JSON
detections（含 `x1,y1,x2,y2,confidence,class_id,candidate_index`）；C++ test 对同一 raw
asset 调用 `PostProcessor`，比较 count、顺序、class id、candidate index，及每个 bbox/
confidence 的冻结容差。manifest、Python reference output、C++ output、comparison report
和 provenance 都要有 SHA256。阈值和容差必须在 M3.4 前冻结，不得为通过而放宽。

这条验证不经过 C++ preprocessing、不调用 `OnnxRuntimeEngine`、不读取图像、不产生
benchmark；因此前级错误不能相互抵消。

### 8.3 Gate

M3 gate 要求：clean Git scope audit；Model Smoke OFF/ON 的适用回归；M3 unit/negative
tests；`postprocessor_level_b` evidence 的 SHA/provenance 和 Python/C++ 全 detection
comparison 通过。strict、ASan/UBSan 仅在项目已配置的情况下执行；若未配置必须如实记录
`Not configured`，不得写作通过。Level C complete pipeline / benchmark 继续留给 M5。

## 9. 推荐提交拆分

1. `docs: freeze M3 postprocessor execution plan`
2. `feat: add detection and postprocessor contracts`
3. `feat: decode YOLO raw output candidates`
4. `feat: implement class-aware NMS`
5. `test: validate postprocessor against Python reference`
6. `docs: close M3 postprocessor`

每个步骤结束后只验证本步骤边界；不自动进入下一阶段，不混入 M4 Runner 或 M5 benchmark。
