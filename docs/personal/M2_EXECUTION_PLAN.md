# M2 Execution Plan

状态：`IN_PROGRESS`（2026-07-18）。M2.1 inference contract、M2.2 Session
initialization 与 M2.3 synchronous Run path 已完成；Level B 尚未开始。

## 1. 目标和边界

M2 的唯一目标是在现有 M1 core contracts、frozen `ModelContract` 和 CPU
`Preprocessor` 之上，实现可验证的 production `OnnxRuntimeEngine`。M2 只覆盖
ONNX Runtime CPU 的同步单次执行，不构成完整 C++ Serial Baseline，也不产生性能
结论。

M2 实现：

- production `OnnxRuntimeEngine`；
- `CPUExecutionProvider`；
- synchronous inference；
- `HostTensor` input/output；
- `ModelContract` validation；
- ORT `Session` metadata validation；
- Level B Engine-only validation。

M2 不实现：

- `PostProcessor`、NMS、`Detection`；
- `SerialRunner`、`Pipeline`；
- TensorRT、CUDA、GPU Execution Provider；
- ROS2、Qt；
- benchmark、warm-up、FPS、latency 或资源数据；
- batch inference、dynamic shape、async、device tensor、plugin。

当前 frozen contract 是 `float32 NCHW [1,3,640,640]` input 和 `float32 BCN
[1,10,8400]` output。M2 必须从已加载的 `ModelContract` 取得这些语义，不得在
production C++ 中硬编码 tensor name、shape、类别或模型 SHA256。

## 2. 已确认前置事实

- 当前 production `edge_ai_core` 已提供 `Status`、`HostTensor`、严格
  `ModelContractLoader`、LetterBox 和 CPU `Preprocessor`。
- `edge_ai_backend_ort` 仍是空 placeholder target；不存在 production ORT API、
  `OnnxRuntimeEngine`、`IInferenceEngine`、`InferenceOutput` 或
  `SessionOptionsConfig`。
- M0 smoke 已在 ONNX Runtime C++ `1.23.2` 上验证 CPU provider、`Ort::Env`、
  `Ort::SessionOptions`、Session metadata、CPU `Ort::Value`、`Session::Run` 和
  output reading。M0 helper 仅限 test，不迁入 production。
- Model Contract 是模型 SHA256、文件大小、input/output tensor 语义和类别顺序的
  权威；ONNX metadata 是运行时结构事实。两者必须一致。
- 当前 WSL2 开发环境只用于 CPU 功能验证；不作为 TensorRT 或性能实验平台。

## 3. 冻结接口设计

### 3.1 `IInferenceEngine`

M2 引入 backend-neutral 的 `IInferenceEngine`。这是架构要求的最小抽象，供后续
`SerialRunner` 和 TensorRT backend 依赖，而不暴露 ONNX Runtime 类型。

冻结的最小职责为：

```text
initialize()
run()
```

`initialize()` 接收模型路径和已通过 `ModelContractLoader` 校验的
`ModelContract`，在成功返回前完成完整 ready validation。`run()` 接收已拥有的
`HostTensor` input，并通过 output 参数返回已拥有的 `HostTensor`。两者均以
`core::Status` 表达可恢复失败；不引入 `StatusOr` 或异常穿透 public API。

M2.1 已冻结 interface copy 与 move 均删除。具体 `OnnxRuntimeEngine` 后续由
`std::unique_ptr` 管理；该选择避免在尚未实现 ORT resource 时暴露或猜测移动后的
ready/session 语义。

接口禁止出现：async、batch、device tensor、dynamic shape、plugin、ORT types、
CUDA/TensorRT types 或 postprocess types。

### 3.2 Output contract

M2 output 固定使用 `core::HostTensor`，不创建 `InferenceOutput`。

理由：现有 `HostTensor` 已能表达 `float32`、`BCN` 和 owned contiguous CPU
buffer；在 M2 没有 frame metadata、detection 或 backend-specific metadata 需要
承载。输出的 `TensorInfo` 必须来自 validated output contract，data size 必须通过
`validate_host_tensor`。M2 产出的 output 归调用方独占。

## 4. `OnnxRuntimeEngine` 设计

`OnnxRuntimeEngine` 实现 `IInferenceEngine`，并只属于
`edge_ai_backend_ort`。ORT-specific logic 不得进入 `edge_ai_core`、Runner 或
main。

冻结成员语义：

- `Ort::Env`；
- `Ort::SessionOptions`；
- `Ort::Session`；
- 已验证的 `ModelContract`；
- input/output `core::TensorInfo`；
- 已复制并稳定存储的 input/output node name。

生命周期冻结如下：

```text
Ort::Env create
  ↓
Ort::SessionOptions configure
  ↓
Ort::Session create/use/destroy
  ↓
Ort::Env destroy
```

`Ort::Env` 必须覆盖 `Ort::Session` 的整个生命周期；成员声明、构造及析构顺序必须
保证该关系。Engine 删除 copy 和 move；通过 factory/owned pointer 管理，避免
复制 ORT resource 或形成部分初始化对象。

## 5. Model 验证与 ready 流程

初始化必须按以下固定顺序执行；任一步失败即不 ready，且不得继续运行：

```text
model file
  ↓
file existence/readability + size + SHA256 validation
  ↓
validated ModelContract
  ↓
Ort::Session create
  ↓
Session input/output count and metadata compare
  ↓
ready
```

SHA256 和 size 必须与 `ModelContract.expected_onnx_sha256`、
`expected_onnx_size_bytes` 精确匹配，并在创建 Session 前验证。Session validation
必须检查恰好一个 input 和一个 output，以及各自的 ONNX tensor type、node name、
element type、rank、全正静态 dimensions 和完整 shape。模型 metadata 与 contract
任一不符均是初始化失败。

失败类别至少应可区分：

- invalid argument 或 null output；
- model file I/O failure；
- file size/SHA256 integrity mismatch；
- invalid or internally inconsistent ModelContract；
- ORT Env/SessionOptions/Session initialization failure；
- input/output count、name、type、dtype、rank、static dimension 或 shape mismatch；
- 非 ready 状态的 `run()`、input validation failure、ORT run failure、output
  validation failure。

M2.1 已冻结并新增 `kModelContractMismatch`、`kBackendInitializationError` 和
`kBackendRuntimeError`。不新增 `kIntegrityMismatch`：model SHA256/size failure 是
ModelContract 一致性失败，使用 `kModelContractMismatch`。既有错误码继续覆盖一般
argument、I/O、shape、dtype/layout、data-size 和 schema 错误。

## 6. `SessionOptions` 策略

M2 固定使用 CPU execution path：

```text
CPUExecutionProvider
execution mode: ORT_SEQUENTIAL
graph optimization: ORT_ENABLE_ALL
intra_op_num_threads: 1
inter_op_num_threads: 1
```

这些选项仅用于固定 M2 的执行语义和减少并行调度的不确定性；它们不是性能优化，
不构成 benchmark 配置，也不得据此声明 latency/FPS 结论。M2 不引入通用
`SessionOptionsConfig`、YAML tuning、EP selection、thread tuning 或 provider
fallback。若 ORT API/SDK 不支持上述某个选项，初始化必须明确失败，不得静默改变
语义。

## 7. Run 路径

M2 的 `run()` 固定为：

```text
HostTensor input
  ↓
validate_host_tensor + compare validated input TensorInfo
  ↓
CPU Ort::Value wrapping caller-owned input buffer
  ↓
Session::Run
  ↓
validate returned output tensor
  ↓
copy to owned HostTensor
```

input `HostTensor` 的 buffer、shape 和 node-name storage 必须覆盖
`Session::Run`。返回 ORT output 只能在其 `Ort::Value` 存活时读取；M2 必须复制到
独立 owned `HostTensor` 后返回。M2 不做 output buffer reuse、borrowed output、
buffer pool、zero-copy、pinned memory 或跨 run cache。output type、shape、element
count、data pointer 和 finite values 都必须验证；任何失败不得修改调用方既有 output。

## 8. Level B Engine-only validation

Level B 验证 production `OnnxRuntimeEngine`，而非 M0 smoke、Preprocessor、
PostProcessor 或完整 runner。

参考路径：

```text
fixed HostTensor input → Python ONNX Runtime golden
                       ↘ C++ OnnxRuntimeEngine output
```

比较项目固定为：shape、element count、MAE、max_abs、finite count，并同时确认
NaN/+Inf/-Inf 均为零。输入资产、Python ORT version、model SHA256、contract 和
golden digest 必须记录为可复现 evidence。

Level B 阈值已作为当前环境冻结为：`MAE <= 1e-6`、`max_abs <= 1e-5`，且 finite
count 必须等于完整 element count。任何失败先定位
模型、input、contract、provider、ORT version 或 copy/shape 问题；禁止为使结果
通过而放宽阈值。若需要更改阈值，必须停止 M2、提供差异证据并经人工架构审查后以
新的决策和计划修订冻结。

Level B 不测 warm-up、latency、FPS、吞吐、CPU/GPU usage 或稳定性时长。

## 9. 提交与 Gate 计划

每个子阶段完成后停止，执行范围/Git 审计与相应验证，不自动进入下一阶段。所有
提交只保存在本地；不得 `git push`。

1. `docs: freeze M2 execution plan`
   - 本文件；仅冻结 M2 边界与设计。

2. `feat: define inference engine contract`
   - 最小 backend-neutral `IInferenceEngine`、ORT Engine public contract、错误码
     决策和 contract-level tests。

3. `feat: initialize ORT session`
   - model integrity、SessionOptions、Env/Session lifecycle、metadata validation。
   - M2.2 使用系统已安装的 OpenSSL EVP SHA-256 API；仅链接
     `OpenSSL::Crypto` 到 `edge_ai_backend_ort`，不自实现 hash 算法。
   - 已完成：production `OnnxRuntimeEngine` 在 Session 创建前验证文件存在性、
     size 与 SHA256；固定 CPU provider、`ORT_SEQUENTIAL`、`ORT_ENABLE_ALL` 与
     intra/inter-op thread=1；随后验证单 input/output 的 name、float32、static
     shape 和 contract layout。`run()` 仍只返回 `kBackendRuntimeError`。

4. `feat: implement ORT run path`
   - `HostTensor` wrapping、synchronous `Session::Run`、owned output 和失败事务语义。
   - 已完成：run 先以 existing core validation 检查 input 的 dtype/layout/shape/
     element count/data size；用 caller-owned buffer 创建 CPU `Ort::Value`，以
     已保存 node name 同步调用 Session；检查单 float32 output、shape、element count
     与 finite values 后复制到独立 `HostTensor`。失败时不会修改 caller output。

5. `test: add M2 validation`
   - Engine unit/negative tests 与 Level B Python/C++ evidence；不删除 M0/M1 tests。

6. `docs: close M2`
   - 真实验证命令和结果、环境/asset provenance、剩余边界及下一阶段说明。

M2 completion gate 至少要求：干净 Git 审计、model smoke OFF/ON 适用回归、strict
与 ASan/UBSan 适用回归、Engine initialization/run negative cases、Level B evidence
全部通过。M2 完成后仍不代表 PostProcessor、SerialRunner 或正式性能 baseline
已经完成。

## 10. M2 完成判定

只有当 production Engine 已验证 CPU synchronous HostTensor in/out、model file
integrity、contract/metadata consistency 与 Level B numerical evidence，并完成上述
closeout 文档时，M2 才可标记 `CLOSED`。否则保持 `FROZEN` 或 `IN_PROGRESS`，不得
以 M0 smoke 或单次手工 `Session::Run` 代替 M2 验收。
