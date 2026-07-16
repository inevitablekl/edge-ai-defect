# M1 Execution Plan

## 1. M1 目标

M1 建立正式核心数据合同、冻结模型合同读取能力、CPU `Preprocessor`，并完成
Python/C++ Level A 预处理一致性验证。

M1 不包含：

- 正式 `OnnxRuntimeEngine` 或生产 `Session::Run`；
- postprocess/NMS、`SerialRunner`、`ResultSink`、`Profiler`；
- benchmark、Pipeline、TensorRT、ROS2、Qt；
- GPU preprocessing、dynamic shape、batch inference。

## 2. 已确认环境与仓库事实

- M0 closed at commit `52e7165`。
- CMake minimum/current：`3.16` / `3.22.1`。
- GCC/G++：`11.4.0`；语言标准：C++17。
- OpenCV C++：`4.5.4`，C++17 include/compile/link/run probe PASS。
- yaml-cpp：`0.7.0`，C++17 `YAML::Load`、标量和序列 probe PASS。
- Python reference：`tools/validation/compare_pt_onnx.py::preprocess_image`。
- Python reference 环境：OpenCV `4.10.0`、Ultralytics `8.4.50`、NumPy `1.26.4`。
- 当前 `include/` 只有 `.gitkeep`；`src/` 只有 M0 的三个骨架源文件。
- `edge_ai_core` 只包含 `src/core.cpp`；`edge_ai_backend_ort` 是占位 target；
  `edge_ai_infer` 只链接前两者并运行骨架 main。
- M0 ORT API 和 helper 只位于 `tests/smoke/`；`edge_ai_ort_smoke_support`
  只服务测试。
- 当前没有正式 C++ `Status`、`TensorInfo`、`HostTensor`、`ModelContract`、
  `Preprocessor` 或 ORT backend。
- 当前没有 Git 跟踪、可供 C++ 读取的正式 model contract 文件。
- 当前没有独立 Level A golden generator、manifest、人工 synthetic images、
  tensor/metadata golden 或 Level A report。

M1 保持最小 target 结构：核心合同、model contract loader 和 CPU preprocessor
均归属 `edge_ai_core`；没有证据表明需要单独 preprocessing library。

## 3. 权威模型合同与 Python 参考语义

### 3.1 Model Contract

正式 contract 的唯一冻结路径：

```text
configs/model_contracts/yolov8n_neudet_frozen.yaml
```

该文件在 M1.2 创建并由 Git 跟踪，不依赖被 `.gitignore` 排除的
`data/yolo/neu_det/dataset.yaml`。严格 schema 冻结为：

```yaml
schema_version: 1
model:
  sha256: c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944
input:
  name: images
  dtype: float32
  layout: NCHW
  shape: [1, 3, 640, 640]
output:
  name: output0
  dtype: float32
  layout: BCN
  shape: [1, 10, 8400]
class_count: 6
classes:
  - crazing
  - inclusion
  - patches
  - pitted_surface
  - rolled-in_scale
  - scratches
```

权威关系：

- ONNX 是运行时 tensor 结构事实；
- Model Contract 是冻结项目语义、模型 SHA256 和类别顺序的权威；
- runtime YAML 只提供运行参数，不承担类别名、shape 或模型语义权威；
- 后续生产 runtime 必须同时读取 ONNX 和 contract，并在一致性验证通过后继续。

### 3.2 Python preprocessing reference

当前实际语义冻结为：

- `cv2.imread(path)` 默认读取，输出 BGR；未传
  `IMREAD_IGNORE_ORIENTATION`，因此存在 EXIF 时会应用 orientation；
- target shape 当前为 `(640, 640)`；C++ 生产代码必须改由已验证 model
  contract 提供，禁止硬编码 640；
- `LetterBox(new_shape=(640,640), auto=False, stride=32)`；当前依赖默认值为
  `scale_fill=false`、`scaleup=true`、`center=true`、padding `114`、
  `INTER_LINEAR`；
- resize size 使用 Python `round`（ties-to-even），两侧 padding 使用
  `round(value - 0.1)` / `round(value + 0.1)`；
- BGR→RGB、HWC→CHW、增加 batch dimension；
- `np.ascontiguousarray(..., dtype=np.float32)` 后除以 `255.0`；
- 输出为连续 `float32 [1,3,640,640]`。

Level A generator 必须显式传入所有 LetterBox 参数并记录 Python/OpenCV/
Ultralytics 版本，不能依赖未来版本的默认参数。人工 synthetic assets 不携带
EXIF；若后续增加 orientation case，Python 与 C++ loader 必须显式使用相同策略。

## 4. M1 阶段

### M1.1 Core Contracts

目标：实现 `ErrorCode`、`Status`、`TensorDataType`、`TensorLayout`、
`TensorInfo`、拥有连续 CPU `float32` buffer 的 `HostTensor`，以及防
`size_t` 溢出的 checked element count。

边界：仅标准库；不接 OpenCV、yaml-cpp 或生产 ORT API；不实现
`ModelContract`、`Preprocessor` 或未来模块。

测试：成功/失败 `Status`；空 shape；零维；`-1` dynamic dimension；小于
`-1` 的非法负维；element count 溢出；data size/shape mismatch；dtype/layout
基础语义。空 shape 在本项目中不是 scalar，必须拒绝。

推荐提交：`feat: add core tensor and status contracts`

Gate：快速 Gate。

### M1.2 Frozen Model Contract

目标：创建上述 Git-tracked contract，实现 `ModelContract` 和严格的
`ModelContractLoader`，接入 yaml-cpp，验证 SHA256、输入输出合同和类别顺序。

严格规则：所有 mapping 的未知字段均拒绝；缺字段、错误 YAML 类型、非法
dtype/layout/shape、非 64 位小写十六进制 SHA、类别数量不一致、空类别或重复
类别均失败。输出 `BCN` 只表达 frozen output metadata，不扩大 M1 preprocessing
对 NCHW input 的支持。

边界：不实现完整 `ConfigManager`；不解析 runtime 路径；不读取或运行 ONNX；
不引入生产 ORT API。

推荐提交：`feat: add frozen model contract loader`

Gate：深度 Gate 1。

### M1.3 LetterBox Geometry

目标：验证输入图像，依据已验证的 input `TensorInfo`/`ModelContract` 计算并执行
Python-compatible resize/padding，输出 BGR letterboxed image 和
`ImageTransformMetadata`。

规则：只接受非空 `CV_8UC3`；target shape 不硬编码；padding value `114`；
resize 为 `INTER_LINEAR`；实现确定性的 ties-to-even helper，不以
`std::round` 代替 Python `round`。

测试至少覆盖：`200×200`、`640×360`、`360×640`、`641×480`、
`480×641`、`37×53`、ties-to-even 边界、gain/resize size/四边 padding。

边界：暂不做 RGB/CHW/float normalization、GPU 或 inference。

推荐提交：`feat: implement letterbox geometry`

Gate：快速 Gate。

### M1.4 Full CPU Preprocessor

目标：实现 `Preprocessor`、`ImageTransformMetadata`、`PreprocessedFrame`：

```text
BGR → LetterBox → RGB → HWC to CHW → float32 → /255
    → HostTensor [1,3,H,W]
```

要求：输入 `cv::Mat` 只读；输出 vector capacity 可跨调用复用；严格验证
shape/dtype/layout；空图、错误 channel/type 和无效 contract 明确失败。

边界：不做 batch、dynamic shape、GPU、pinned memory、buffer pool 或 inference。

推荐提交：`feat: implement CPU image preprocessing`

Gate：深度 Gate 2。

### M1.5 Level A Validation

目标：建立 synthetic image generator、manifest、image SHA256、Python golden
generator、C++ validation executable、metadata/tensor comparison 和 validation
report，并依据实测冻结容差。

资产路径冻结为：

- 生成器：`tools/validation/generate_preprocess_level_a.py`；
- 小型输入和 manifest：`tests/assets/preprocessing/`，允许 Git 跟踪；
- 大型 tensor/golden 临时输出：`build/m1_level_a/`，不得进入 Git；
- 轻量验证报告：`results/preprocessing/level_a_validation.json`，经深度 Gate
  审核后允许 Git 跟踪。

覆盖：正方形、横图、竖图、奇数 padding、小图、RGB 色块、棋盘/锐利边缘。
现有 `pt_onnx_compare.json` 只是历史 PyTorch/ONNX evidence，不是 Level A golden。

候选门槛：无 resize 或人工精确用例 `max abs <= 1e-7`；发生 resize 时
`MAE <= 5e-4` 且 `max abs <= 2/255 + 1e-6`。这些只是假设；失败时先分析
像素、round、padding、interpolation 和 OpenCV 版本，禁止直接放宽阈值。

推荐提交：`test: validate C++ preprocessing against Python reference`

Gate：深度 Gate 3。

### M1.6 Closeout

目标：clean build、CTest、Level A/model contract/M0 smoke 全量回归，执行边界和
Git 审计，更新必要文档并创建本地 checkpoint。

边界：不增加功能、不重构、不进入 M2。

推荐提交：`docs: close M1 core preprocessing`

Gate：最终回归。

## 5. Gate 规则

- M1.1、M1.3：快速 Gate；
- M1.2、M1.4、M1.5：分别为深度 Gate 1、2、3；
- M1.6：最终回归。

快速 Gate 只检查范围、构建、测试、负向测试、Git 状态和阻断项。深度 Gate
额外检查 public API、所有权和生命周期、错误传播、数值语义、测试误报风险及
过度设计风险。

## 6. 通用执行规则与结果模板

- 每次只执行一个子阶段，完成后停止，不自动进入下一阶段；
- 全部提交只保存在本地；Codex 禁止执行 `git push`，由用户手动 push；
- archive/model SHA 仅在依赖、模型或环境变化时重验；
- 每阶段只更新必要文档；`ENVIRONMENT.md` 和 `TASKS.md` 主要在重要 Gate 或
  阶段关闭时更新；
- build、SDK、模型和大型 golden 不得进入 Git；
- 不为未来模块创建空壳接口，不用放宽阈值掩盖差异。

每个子阶段报告固定为：起点、修改文件、核心设计、执行命令、测试与负向测试、
范围检查、Git 结果、未解决问题。

## 7. M1.1 精确边界

允许创建：

- `include/edge_ai_defect/core/status.hpp`
- `include/edge_ai_defect/core/tensor.hpp`

允许修改：

- `src/core.cpp`
- `tests/test_core.cpp`
- `CMakeLists.txt`
- 必要时 `docs/personal/TASKS.md`

target 归属：生产代码只进入现有 `edge_ai_core`；测试只使用现有 `test_core`；
不新增 production library 或 test framework。

最小 public API/行为：

- `ErrorCode` 至少区分 OK、invalid argument、unsupported、overflow、shape/data
  mismatch；
- `Status` 提供 OK/error 构造、`ok()`、`code()` 和只读 message；
- `TensorDataType` 当前只有 `float32`；
- `TensorLayout` 表达 NCHW；可表达 frozen output 的 BCN metadata，但
  `HostTensor`/`Preprocessor` 在 M1 只接受 NCHW batch=1；
- `TensorInfo` 使用 `std::vector<int64_t>` shape，不硬编码通用 tensor shape；
- checked element count 使用 `size_t`，乘法前检查溢出；
- `HostTensor` 只拥有连续 `std::vector<float>` CPU buffer，不设计 device tensor、
  CUDA、zero-copy、pinned memory、multi-dtype variant 或任意 rank 运算框架；
- shape 必须非空、静态且全为正数；当前 NCHW input 必须 rank=4、batch=1；
  HostTensor data size 必须精确等于 checked element count。

明确禁止：OpenCV、yaml-cpp、ORT production API、`ModelContract`、
`ConfigManager`、`Preprocessor`、inference interface/backend 及其他未来模块。

验收命令：

```bash
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DONNXRUNTIME_ROOT="$PWD/third_party/onnxruntime/1.23.2/linux-x64" \
  -DEDGE_AI_ENABLE_MODEL_SMOKE=OFF
cmake --build build --target edge_ai_core test_core --parallel
ctest --test-dir build --output-on-failure -R '^test_core$'
./build/test_core
```

推荐本地提交：`feat: add core tensor and status contracts`

## 8. 问题分级

### BLOCKER

- 无。

### PREREQUISITE

- 无外部 prerequisite；OpenCV C++ 与 yaml-cpp 已可用。
- M1.5 深度 Gate 前必须在 generator/manifest 中显式冻结 image orientation、
  LetterBox 全参数和 Python/C++ OpenCV 版本；这是 M1.5 验收内容，不阻断 M1.1。

### MINOR

- C++ OpenCV `4.5.4` 与 Python OpenCV `4.10.0` 不同；不升级，先由 Level A
  实测判断 interpolation 差异。
- 当前 dataset YAML 被忽略且不是正式 contract；M1.2 按冻结路径解决。
- `ARCHITECTURE.md` 的 `PreprocessOutput` 是可调整示例；M1 正式名称冻结为
  `PreprocessedFrame` 和 `ImageTransformMetadata`。
- 文档中存在 `InferenceEngine`/`IInferenceEngine`、`ONNXRuntimeEngine`/
  `OnnxRuntimeEngine` 历史命名差异；M1 不实现这些类型，留到 M2 前统一。
- `TASKS.md` 的部分早期 TODO/TBD 表格已落后于 M0 事实；不影响 M1.1。
