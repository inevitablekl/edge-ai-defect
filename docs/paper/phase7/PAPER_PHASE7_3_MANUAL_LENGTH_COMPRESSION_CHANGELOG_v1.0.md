# Paper Phase 7.3-J Manual Length Compression Changelog v1.0

## 1. Purpose and metric

This ledger is the complete manual-application record for the Phase 7.3-J
textual compression. `00_title_abstract.md` is byte-identical to baseline:
`ABSTRACT_UNCHANGED`.

The integer character counts below count non-whitespace Unicode source
characters in the exact original/revised replacement text. The accompanying
CJK-weighted estimate counts non-ASCII characters as 1 and ASCII characters
as 0.5; it is an engineering approximation for manual Word pagination, not an
exact Word page count. Citation keys are included equally before and after and
their occurrence sequence is unchanged.

## 2. Change summary

| ID | Section | Before chars | After chars | Saved chars | CJK-weighted saved | Risk | Manual priority |
|---|---|---:|---:|---:|---:|---|---|
| C01 | 0 引言 | 232 | 213 | 19 | 19.0 | LOW | TIER 2 |
| C02 | 0 引言 | 502 | 462 | 40 | 40.0 | LOW-MEDIUM | TIER 1 |
| C03 | 0 引言 | 446 | 377 | 69 | 64.0 | LOW-MEDIUM | TIER 1 |
| C04 | 0 引言 | 228 | 181 | 47 | 47.0 | MEDIUM | TIER 2 |
| C05 | 1.1 固定推理对象与系统边界 | 242 | 120 | 122 | 78.0 | LOW | TIER 1 |
| C06 | 1.2 路径描述符与名义复制载荷 | 158 | 106 | 52 | 52.0 | LOW | TIER 1 |
| C07 | 1.3 层级受控比较、正确性条件与评价问题 | 165 | 100 | 65 | 58.0 | LOW-MEDIUM | TIER 2 |
| C08 | 2.1 V0基线路径 | 299 | 230 | 69 | 65.0 | LOW-MEDIUM | TIER 1 |
| C09 | 2.2 V2R路径级重构 | 336 | 241 | 95 | 85.0 | LOW-MEDIUM | TIER 1 |
| C10 | 3.2 运行与正确性协议 | 227 | 175 | 52 | 49.5 | LOW | TIER 1 |
| C11 | 3.3 E2E、FPS与尾延迟指标 | 280 | 252 | 28 | 24.5 | LOW-MEDIUM | TIER 1 |
| C12 | 4.1 正确性约束验证 | 167 | 138 | 29 | 29.0 | LOW | TIER 1 |
| C13 | 4.2 路径级重构的E2E响应 | 368 | 215 | 153 | 136.5 | MEDIUM | TIER 1 |
| C14 | 4.3 暂存策略的增量响应 | 210 | 149 | 61 | 53.0 | MEDIUM | TIER 2 |
| C15 | 5 结论（第1段） | 189 | 130 | 59 | 56.0 | LOW-MEDIUM | TIER 3 |
| C16 | 5 结论（第3段） | 105 | 73 | 32 | 29.5 | MEDIUM | TIER 3 |
| **Total** | **Sections 0–5** | **3954** | **2962** | **992** | **886.0** | — | — |

The summary total covers only the 16 replaced text units. Whole-body counts,
which also include unchanged headings, equations, captions and tables, are in
the validation report.

## 3. Complete change ledger

### C01

- **SECTION:** 0 引言
- **PARAGRAPH ANCHOR:** `检测模型研究通过轻量化骨干`
- **ORIGINAL TEXT:**

  检测模型研究通过轻量化骨干、注意力机制和多尺度特征融合改善精度与复杂度权衡 [@shao_et_al_2024_td_net; @chu_yu_rong_2024_strip_steel_yolov8; @zhang_pang_jiang_2024_gdm_yolo]，YOLOv8也提供了训练、推理和导出链路 [@ultralytics_2023_yolov8_docs]。这类工作定义了检测器及其网络结构，为边缘执行提供推理基础，却不能单独描述模型入口之前的数据组织。

- **REVISED TEXT:**

  检测模型通过轻量化骨干、注意力机制和多尺度特征融合改善精度与复杂度权衡 [@shao_et_al_2024_td_net; @chu_yu_rong_2024_strip_steel_yolov8; @zhang_pang_jiang_2024_gdm_yolo]，YOLOv8也提供训练、推理和导出链路 [@ultralytics_2023_yolov8_docs]；这些工作为边缘执行提供推理基础，但不能描述模型入口前的数据组织。

- **NET CHARACTER REDUCTION:** 19 source characters; 19.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `NARRATIVE_COMPRESSION`
- **RATIONALE:** Merge detector-background and inference-basis statements while retaining the research gap at the model entrance.
- **SCIENTIFIC FACTS PRESERVED:** Lightweight/model research role, YOLOv8 toolchain, and inability to determine pre-model data organization.
- **CITATIONS PRESERVED:** YES — all four keys remain in the same order and support the same claims.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C02

- **SECTION:** 0 引言
- **PARAGRAPH ANCHOR:** `完整边缘检测链同时包含数据获取`
- **ORIGINAL TEXT:**

  完整边缘检测链同时包含数据获取、预处理、模型执行、后处理与数据管理 [@stacker_et_al_2021_edge_runtime]，CPU与GPU之间的预处理调度会改变运行时路径 [@lee_han_kim_2025_presto]，工业现场应用也要求在设备附近完成端到端处理 [@weiss_et_al_2024_realtime_component_inspection]。低精度部署可进一步压缩网络侧计算与存储开销，但量化误差仍须受到任务正确性约束 [@jacob_et_al_2018_integer_inference; @nagel_et_al_2020_adaround]。本文据此固定检测器、输入、TensorRT INT8混合精度Engine、工作负载与后处理语义；TensorRT 10.3的传统隐式INT8量化及calibrator接口具有明确版本边界 [@nvidia_tensorrt_10_3_release_notes]，相关部署研究也强调性能比较应维持任务行为 [@kim_lee_kim_2024_hyq]。然而，固定网络与Engine只定义了推理对象，并不唯一决定其输入数据路径。

- **REVISED TEXT:**

  完整边缘检测链涵盖数据获取、预处理、模型执行、后处理与数据管理 [@stacker_et_al_2021_edge_runtime]；CPU与GPU间的预处理调度会改变运行时路径 [@lee_han_kim_2025_presto]，现场应用也要求在设备附近完成端到端处理 [@weiss_et_al_2024_realtime_component_inspection]。低精度虽可压缩网络侧开销，量化误差仍须受任务正确性约束 [@jacob_et_al_2018_integer_inference; @nagel_et_al_2020_adaround]。因此本文固定检测器、输入、TensorRT INT8混合精度Engine、工作负载与后处理语义；TensorRT 10.3传统隐式INT8量化及calibrator接口存在版本边界 [@nvidia_tensorrt_10_3_release_notes]，性能比较应维持任务行为 [@kim_lee_kim_2024_hyq]。但固定网络与Engine仍不唯一决定输入数据路径。

- **NET CHARACTER REDUCTION:** 40 source characters; 40.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `NARRATIVE_COMPRESSION`
- **RATIONALE:** Remove repeated modifiers and compress transitions without deleting any literature-supported concept.
- **SCIENTIFIC FACTS PRESERVED:** Complete edge chain, CPU/GPU scheduling relevance, E2E requirement, low-precision correctness constraint, frozen inference object, TensorRT 10.3 boundary, and non-uniqueness of the input path.
- **CITATIONS PRESERVED:** YES — all eight keys remain in identical occurrence order.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C03

- **SECTION:** 0 引言
- **PARAGRAPH ANCHOR:** `在推理对象固定后，输入路径仍须作出四类结构决策`
- **ORIGINAL TEXT:**

  在推理对象固定后，输入路径仍须作出四类结构决策：以何种表示跨越主机—设备边界，模型输入张量在何处形成，额外打包原始图像采用何种主机暂存组织，以及各处理阶段采用何种执行拓扑。Jetson检测部署已有多种端到端组织 [@tang_qian_2024_yolov8_jetson_orin]；主机内存类型与异步复制具有特定适用条件 [@nvidia_cuda_best_practices_12_6]，集成CPU-GPU系统和GPU内存分配研究表明内存策略响应取决于平台、工作负载和访问方式 [@bateni_et_al_2020_integrated_memory; @rodriguez_et_al_2025_gpu_memory_allocation]，其执行语义还受流与复制规则约束 [@nvidia_cuda_programming_guide_12_6]。并发或流水化研究则说明执行拓扑本身构成另一类系统选择 [@kim_et_al_2025_concurrent_edge_detection]。

- **REVISED TEXT:**

  推理对象固定后，输入路径仍需决定跨边界表示、输入张量形成位置、额外打包原始图像的主机暂存组织和执行拓扑。Jetson检测部署已有多种端到端组织 [@tang_qian_2024_yolov8_jetson_orin]；主机内存与异步复制有特定适用条件 [@nvidia_cuda_best_practices_12_6]，内存策略响应取决于平台、工作负载和访问方式 [@bateni_et_al_2020_integrated_memory; @rodriguez_et_al_2025_gpu_memory_allocation]，并受流与复制规则约束 [@nvidia_cuda_programming_guide_12_6]；并发或流水化研究还表明执行拓扑本身是系统选择 [@kim_et_al_2025_concurrent_edge_detection]。

- **NET CHARACTER REDUCTION:** 69 source characters; 64.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `NARRATIVE_COMPRESSION`
- **RATIONALE:** Replace four parallel interrogative clauses and repeated attribution language with the same four-variable statement.
- **SCIENTIFIC FACTS PRESERVED:** All four structural decisions, platform/workload/access dependence, stream/copy constraints, and execution topology as a separate choice.
- **CITATIONS PRESERVED:** YES — all six keys remain in the same order and claim locations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C04

- **SECTION:** 0 引言
- **PARAGRAPH ANCHOR:** `为解决这一评价对象与知识组织上的缺口`
- **ORIGINAL TEXT:**

  为解决这一评价对象与知识组织上的缺口，本文将固定推理对象下的输入数据路径表示为结构描述符\(P=(R,F,M,E)\)，并以任务正确性保持作为性能比较的逻辑准入条件。在此基础上提出两个研究问题：其一，在固定推理对象、工作负载和任务语义时，路径级耦合重构对完整E2E平均响应产生何种影响；其二，在其余结构变量、GPU预处理语义及下游结构固定时，主机暂存策略的单变量变化是否产生额外平均响应，以及P95/P99是否呈现一致改善。两项问题的形式化表述见1.3节。

- **REVISED TEXT:**

  为填补该缺口，本文以结构描述符\(P=(R,F,M,E)\)表示固定推理对象下的输入数据路径，并以任务正确性保持为性能比较准入条件。据此研究：固定推理对象、工作负载和任务语义时，路径级耦合重构对完整E2E平均响应的影响；其余结构变量、GPU预处理语义及下游结构固定时，主机暂存策略的单变量变化是否带来额外平均响应及一致的P95/P99改善。形式化表述见1.3节。

- **NET CHARACTER REDUCTION:** 47 source characters; 47.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `NARRATIVE_COMPRESSION`
- **RATIONALE:** Compress the RQ preview while retaining the descriptor, admission condition, two motivations, and the formal RQ cross-reference.
- **SCIENTIFIC FACTS PRESERVED:** \(P=(R,F,M,E)\), correctness admission, coupled path response, M-only incremental response, and P95/P99 consistency question.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C05

- **SECTION:** 1.1 固定推理对象与系统边界
- **PARAGRAPH ANCHOR:** `本文将检测器、Engine、输入尺寸`
- **ORIGINAL TEXT:**

  本文将检测器、Engine、输入尺寸、工作负载与后处理语义的组合记为固定推理对象。具体对象为YOLOv8n、640×640输入、batch size 1和同一TensorRT INT8混合精度Engine；该Engine启用INT8与FP16 fallback并保持FP32 I/O。工作负载固定为NEU-DET split-v2的180幅测试图像，置信度阈值、IoU阈值、候选框上限和class-aware单标签后处理在全部路径中不变。平台与软件版本属于实验条件，列于表2，不作为路径结构变量。

- **REVISED TEXT:**

  本文将检测器、Engine、输入尺寸、工作负载与后处理语义的组合记为固定推理对象，具体配置与工作负载见表2。三条路径的置信度阈值、IoU阈值、候选框上限和class-aware单标签后处理均不变；平台与软件版本仅为实验条件，不属于路径变量。

- **NET CHARACTER REDUCTION:** 122 source characters; 78.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `TABLE_PROSE_DEDUPLICATION`
- **RATIONALE:** Table 2 already lists YOLOv8n, 640×640, batch 1, INT8+FP16 fallback, FP32 Engine input, and the frozen workload; prose retains the logical definition and controls not fully enumerated by the table.
- **SCIENTIFIC FACTS PRESERVED:** Complete fixed-inference-object definition, unchanged postprocessing semantics, and platform/software as experimental rather than path variables; all omitted configuration facts remain verbatim in Table 2.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C06

- **SECTION:** 1.2 路径描述符与名义复制载荷
- **PARAGRAPH ANCHOR:** `固定推理对象只约束网络执行及任务语义`
- **ORIGINAL TEXT:**

  固定推理对象只约束网络执行及任务语义，并不唯一确定模型输入如何到达Engine。其输入路径仍须决定四类结构关系：跨越主机—设备边界的表示、模型输入张量的形成位置、任何额外打包原始图像的主机暂存组织，以及各阶段的执行拓扑。三条路径的总体结构及层级受控比较关系见图1。基于这四类仍未被固定的决策，将一条输入数据路径表示为

- **REVISED TEXT:**

  固定推理对象不唯一决定模型输入如何到达Engine，输入路径仍需决定跨边界表示、输入张量形成位置、额外打包原始图像的主机暂存组织和执行拓扑。三条路径的总体结构及层级受控比较关系见图1。基于这四类决策，将路径表示为

- **NET CHARACTER REDUCTION:** 52 source characters; 52.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `NARRATIVE_COMPRESSION`
- **RATIONALE:** Remove duplicated statements about what the fixed object constrains while keeping the four variables and governed Figure 1 early callout verbatim.
- **SCIENTIFIC FACTS PRESERVED:** Input-path non-uniqueness, all four descriptor dimensions, Figure 1 cross-reference, and transition to Equation (1).
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C07

- **SECTION:** 1.3 层级受控比较、正确性条件与评价问题
- **PARAGRAPH ANCHOR:** `性能响应进入路径比较之前还必须满足正确性条件`
- **ORIGINAL TEXT:**

  性能响应进入路径比较之前还必须满足正确性条件：三条路径使用同一工作负载、评价器、模型/Engine、输入和后处理语义；V2R通过预定义的任务级核验，V3R由同一评价器确定性重算；汇总任务指标一致，类别级AP50与Recall最大路径间差异为0。该准入条件只保证冻结工作负载和评价口径内的可比性，不表示逐位相等或对未来输入普适等价。

- **REVISED TEXT:**

  性能比较以同一工作负载、评价器、模型/Engine、输入与后处理语义下的任务正确性保持为准入条件，核验结果见4.1节。该条件只保证冻结工作负载和评价口径内的可比性，不表示逐位相等或对未来输入普适等价。

- **NET CHARACTER REDUCTION:** 65 source characters; 58.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `TABLE_PROSE_DEDUPLICATION`
- **RATIONALE:** Retain the correctness admission rule and scope boundary while moving duplicated outcome narration to Section 4.1.
- **SCIENTIFIC FACTS PRESERVED:** Common controls, correctness as admission, frozen-workload-only comparability, and no bitwise/universal equivalence claim; V2R/V3R protocol and zero category differences remain in Section 4.1.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C08

- **SECTION:** 2.1 V0基线路径
- **PARAGRAPH ANCHOR:** `V0实现\(P_0\)的主机张量路径`
- **ORIGINAL TEXT:**

  V0实现\(P_0\)的主机张量路径，其路径语义是由主机形成模型输入，并由FP32 NCHW张量跨越主机—设备边界。该路径中\(F\)为主机、\(R\)为FP32 NCHW、\(M\)无额外打包原始图像暂存，\(E\)保持为单帧顺序执行。

  作为上述结构语义的实现映射，数据源解码为BGR图像后，CPU/OpenCV采用`INTER_LINEAR`完成640×640 letterbox与常数114填充，并完成BGR→RGB、HWC→CHW及\(1/255\)归一化，在主机侧形成`1×3×640×640` FP32 NCHW张量后执行FP32 H2D复制。这些具体操作用于复现\(P_0\)，不作为独立研究对象。

- **REVISED TEXT:**

  V0实现\(P_0\)的主机张量路径：数据源解码为BGR图像后，CPU/OpenCV以`INTER_LINEAR`完成640×640 letterbox和常数114填充，再执行BGR→RGB、HWC→CHW及\(1/255\)归一化，主机侧形成`1×3×640×640` FP32 NCHW张量后进行FP32 H2D复制。因此\(F\)为主机、\(R\)为FP32 NCHW、\(M\)无额外打包原始图像暂存，\(E\)为单帧顺序执行；这些操作仅用于复现\(P_0\)。

- **NET CHARACTER REDUCTION:** 69 source characters; 65.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `IMPLEMENTATION_COMPRESSION`
- **RATIONALE:** Merge structural semantics and implementation mapping into one reproducible paragraph.
- **SCIENTIFIC FACTS PRESERVED:** CPU/OpenCV, `INTER_LINEAR`, 640×640 letterbox, fill 114, BGR→RGB, HWC→CHW, 1/255, FP32 NCHW host tensor, FP32 H2D, and \(P_0\) descriptor values.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C09

- **SECTION:** 2.2 V2R路径级重构
- **PARAGRAPH ANCHOR:** `V2R实现\(P_2\)的设备张量形成路径`
- **ORIGINAL TEXT:**

  V2R实现\(P_2\)的设备张量形成路径，其路径语义是packed BGR uint8表示跨越边界，并在设备侧形成TensorRT输入。相对\(P_0\)，\(R\)与\(F\)发生变化，\(M\)被引入为pageable暂存，而\(E\)仍为单帧顺序执行。

  作为该结构变化的实现映射，冻结工作负载的200×200源图像在主机侧形成连续的600 B行宽packed BGR pageable暂存，经二维H2D复制后，由设备侧融合预处理直接写入TensorRT管理的FP32 NCHW输入。二维复制采用`cudaMemcpy2DAsync`；融合处理完成resize、padding、BGR→RGB、归一化与布局变换。该API及融合核函数用于实现\(P_2\)，本身不是路径级研究贡献。

- **REVISED TEXT:**

  V2R实现\(P_2\)的设备张量形成路径：200×200源图像在主机侧形成连续的600 B行宽packed BGR uint8 pageable暂存，经`cudaMemcpy2DAsync`二维H2D复制后，设备侧融合完成resize、padding、BGR→RGB、归一化和布局变换，直接写入TensorRT管理的FP32 NCHW输入。相对\(P_0\)，\(R,F\)改变，\(M\)引入pageable暂存，\(E\)仍为单帧顺序；该API与融合核函数仅是\(P_2\)的实现映射。

- **NET CHARACTER REDUCTION:** 95 source characters; 85.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `IMPLEMENTATION_COMPRESSION`
- **RATIONALE:** Merge V2R structural semantics and implementation mapping without turning the method into an API narrative.
- **SCIENTIFIC FACTS PRESERVED:** 200×200 source, packed BGR uint8, 600 B row width, pageable staging, `cudaMemcpy2DAsync`, device-fused resize/padding/color/normalization/layout, TensorRT FP32 NCHW input, and unchanged sequential \(E\).
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C10

- **SECTION:** 3.2 运行与正确性协议
- **PARAGRAPH ANCHOR:** `性能实验使用同一manifest限定的split-v2`
- **ORIGINAL TEXT:**

  性能实验使用同一manifest限定的split-v2固定180幅测试图像及顺序。每个独立进程预热60帧，同步并重置测量窗口后测量1080帧；每条路径执行5个独立进程，形成5400个逐帧延迟样本，三条路径共15个进程和16200个样本，路径间不构造运行配对。

  15个独立进程按预先设定的交错顺序执行。全部进程均处理1080个测量帧、丢帧为0，且输入顺序与EOS检查通过，确保执行完整性和比较条件一致；逐帧diagnostics与profiling保持关闭。

- **REVISED TEXT:**

  性能实验按同一manifest顺序回放split-v2固定180幅测试图像，预热和测量帧数见表2。每条路径的5个独立进程形成5400个逐帧延迟样本，三条路径共15个进程和16200个样本，不构造运行配对。15个进程按预定交错顺序执行，均完成1080个测量帧、丢帧0，并通过输入顺序与EOS检查；逐帧diagnostics与profiling保持关闭。

- **NET CHARACTER REDUCTION:** 52 source characters; 49.5 CJK-weighted equivalents.
- **CHANGE TYPE:** `TABLE_PROSE_DEDUPLICATION`
- **RATIONALE:** Refer repeated warmup/measurement settings to Table 2 and merge process-integrity narration.
- **SCIENTIFIC FACTS PRESERVED:** Frozen ordered 180-image replay, 60 warmup and 1080 measured frames via Table 2, 5 processes/path, 5400 samples/path, 15 processes, 16200 samples, no pairing, interleaving, zero drops, order/EOS checks, and diagnostics/profiling off.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C11

- **SECTION:** 3.3 E2E、FPS与尾延迟指标
- **PARAGRAPH ANCHOR:** `正确性采用冻结测试集和统一评价器`
- **ORIGINAL TEXT:**

  正确性采用冻结测试集和统一评价器，报告Precision、Recall、mAP50、mAP50-95及类别级AP50/Recall。性能指标沿用式（3）的source-to-pre-sink边界；第\(i\)个独立进程的FPS按\(f_i=N/T_i\)计算，其中\(N=1080\)，\(T_i\)为完整测量阶段wall time，故FPS不是逐帧延迟的倒数。每条路径报告5个进程级FPS的均值与样本标准差，并合并5400个逐帧样本计算平均延迟、P95和P99；百分位采用Type-7线性插值。所有统计均为描述性结果，不进行置信区间、假设检验或统计显著性推断。

- **REVISED TEXT:**

  正确性采用冻结测试集和统一评价器，报告Precision、Recall、mAP50、mAP50-95及类别级AP50/Recall。性能沿用式（3）的source-to-pre-sink边界；进程级FPS按\(f_i=N/T_i\)计算（\(N=1080\)，\(T_i\)为测量阶段wall time），不是逐帧延迟的倒数。每条路径报告5个进程级FPS的均值与样本标准差，并合并5400个样本计算平均延迟及Type-7线性插值的P95/P99。所有结果均为描述性统计，不作置信区间、假设检验或显著性推断。

- **NET CHARACTER REDUCTION:** 28 source characters; 24.5 CJK-weighted equivalents.
- **CHANGE TYPE:** `NARRATIVE_COMPRESSION`
- **RATIONALE:** Compact metric definitions and statistical boundary without dropping protocol semantics.
- **SCIENTIFIC FACTS PRESERVED:** Correctness metrics, Equation (3) boundary, FPS definition, N=1080, wall-time denominator, FPS/latency distinction, 5-process mean/SD, pooled 5400 samples, mean/P95/P99, Type-7, and descriptive-only inference.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C12

- **SECTION:** 4.1 正确性约束验证
- **PARAGRAPH ANCHOR:** `性能响应只有在任务行为保持时`
- **ORIGINAL TEXT:**

  性能响应只有在任务行为保持时才具有路径比较意义。三条路径在冻结180幅测试图像和统一评价程序下获得相同的汇总任务指标，类别级最大AP50与Recall路径间差异均为0，结果见表3。V2R通过预定义任务级核验，V3R由同一评价器对冻结预测结果确定性重算；因此后续比较处于同一冻结任务行为约束内，但不扩展为逐位相等或未来输入上的普适结论。

- **REVISED TEXT:**

  任务行为保持是性能比较的准入条件。在冻结180幅测试图像和统一评价程序下，V2R通过预定义核验，V3R由同一评价器确定性重算；三条路径的汇总指标相同，类别级AP50与Recall最大差异均为0（表3）。该结果只确立冻结任务行为下的可比性，不表示逐位相等或未来输入上的普适等价。

- **NET CHARACTER REDUCTION:** 29 source characters; 29.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `TABLE_PROSE_DEDUPLICATION`
- **RATIONALE:** Keep every correctness result and boundary while avoiding a second full prose rendering of Table 3.
- **SCIENTIFIC FACTS PRESERVED:** Frozen 180-image task, unified evaluator, V2R predefined check, V3R deterministic recomputation, identical aggregate metrics, category AP50/Recall maximum difference 0, and no bitwise/universal claim.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C13

- **SECTION:** 4.2 路径级重构的E2E响应
- **PARAGRAPH ANCHOR:** `从结构上看，这项观测是耦合路径级干预`
- **ORIGINAL TEXT:**

  从结构上看，这项观测是耦合路径级干预的完整E2E响应：跨边界表示由FP32 NCHW张量变为packed BGR uint8，输入张量形成位置由主机移至设备，并引入相应的pageable原始图像暂存组织，即\(R,F,M\)发生变化而\(E\)保持不变。它回答的是重构后完整路径如何响应，而不是各变化项分别贡献多少。

  式（2）给出的名义输入复制载荷由4.9152 MB/frame降至0.1200 MB/frame，形成40.96×结构对比；该量只是重构路径的一项表示派生属性，不是实测带宽、流量、H2D时间或独立控制变量。由于未进行阶段插桩或总线/DRAM流量测量，2.24× E2E响应只能归属于完整\(P_0\rightarrow P_2\)路径，不能分解为GPU预处理、H2D、CUDA核函数或表示变化的贡献，也不能解释为40.96×传输加速。

- **REVISED TEXT:**

  该观测是\(R,F,M\)改变而\(E\)不变的耦合路径级E2E响应。式（2）的名义输入复制载荷由4.9152 MB/frame降至0.1200 MB/frame，形成40.96×结构对比，但该量不是实测带宽、流量或H2D时间。由于无阶段插桩及总线/DRAM流量测量，2.24×只能归属于完整\(P_0\rightarrow P_2\)路径，不能分解为GPU预处理、H2D、CUDA核函数或表示变化的贡献，也不表示40.96×传输加速。

- **NET CHARACTER REDUCTION:** 153 source characters; 136.5 CJK-weighted equivalents.
- **CHANGE TYPE:** `BOUNDARY_CONSOLIDATION`
- **RATIONALE:** Merge repeated intervention-scope and no-attribution statements while retaining every numerical result and causal boundary.
- **SCIENTIFIC FACTS PRESERVED:** \(R,F,M\) changed, \(E\) unchanged, 4.9152/0.1200 MB/frame, 40.96× nominal structural contrast, 2.24× complete-path response, no stage timing, no traffic measurement, no component attribution, and no 40.96× transfer-speed claim.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C14

- **SECTION:** 4.3 暂存策略的增量响应
- **PARAGRAPH ANCHOR:** `这项观测对应\(M\)的单变量局部细化`
- **ORIGINAL TEXT:**

  这项观测对应\(M\)的单变量局部细化：\(R,F,E\)、GPU预处理语义、Engine、stream和下游结构均保持不变，只把额外打包原始图像的主机暂存由pageable改为pinned。在受测系统中，其平均响应幅度明显小于此前同时改变\(R,F,M\)的耦合路径级干预。

  上述幅度差异仅描述本文受控系统内两种干预范围的响应，不表示组件重要性，也不推出约4%的改善是pinned内存在其他平台、模型或负载下的普遍收益。

- **REVISED TEXT:**

  该观测仅将额外打包原始图像的主机暂存由pageable改为pinned，\(R,F,E\)、GPU预处理语义、Engine、stream和下游结构均不变。其平均响应小于耦合路径级干预，但这仅描述受测系统内两种干预范围，不表示组件重要性，也不推出pinned内存在其他平台、模型或负载下具有普遍收益。

- **NET CHARACTER REDUCTION:** 61 source characters; 53.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `BOUNDARY_CONSOLIDATION`
- **RATIONALE:** Merge the M-only intervention interpretation and generalization boundary.
- **SCIENTIFIC FACTS PRESERVED:** Only pageable→pinned changes, all other path semantics remain controlled, mean response is smaller than the coupled intervention, and there is no universal pinned-memory or component-importance claim.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C15

- **SECTION:** 5 结论（第1段）
- **PARAGRAPH ANCHOR:** `固定推理对象并不能唯一确定其输入数据路径`
- **ORIGINAL TEXT:**

  固定推理对象并不能唯一确定其输入数据路径。本文以\(P=(R,F,M,E)\)描述跨边界表示、输入张量形成位置、额外打包原始图像暂存策略和执行拓扑，从而把同时改变\(R,F,M\)且保持\(E\)不变的耦合路径级干预，与仅改变\(M\)的单变量暂存策略细化区分为两类评价对象。在这一结构下，平均响应和尾部响应必须分别解释：局部策略产生平均改善，并不等同于P95与P99同步改善。

- **REVISED TEXT:**

  固定推理对象不唯一决定输入数据路径。本文以\(P=(R,F,M,E)\)描述跨边界表示、输入张量形成位置、额外打包原始图像暂存策略和执行拓扑，以区分\(R,F,M\)变化而\(E\)不变的路径级重构与仅改变\(M\)的暂存策略细化；并将平均与尾部响应分别评价。

- **NET CHARACTER REDUCTION:** 59 source characters; 56.0 CJK-weighted equivalents.
- **CHANGE TYPE:** `CONCLUSION_COMPRESSION`
- **RATIONALE:** Condense the research object and hierarchical evaluation principle already established in Sections 1–4.
- **SCIENTIFIC FACTS PRESERVED:** Descriptor meaning, coupled path-level versus M-only intervention, and separate mean/tail evaluation.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

### C16

- **SECTION:** 5 结论（第3段）
- **PARAGRAPH ANCHOR:** `上述数值和认识仅适用于本文单一Jetson平台`
- **ORIGINAL TEXT:**

  上述数值和认识仅适用于本文单一Jetson平台、检测器/Engine、数据集、离线回放与单帧顺序配置。完整E2E响应不能由单个API或名义载荷直接解释，本文也不作阶段级因果、统计显著性或跨平台、跨模型普适推断。

- **REVISED TEXT:**

  上述结论仅适用于本文单一Jetson平台、检测器/Engine、数据集、离线回放与单帧顺序配置，不作阶段级因果、统计显著性或跨平台/模型普适推断。

- **NET CHARACTER REDUCTION:** 32 source characters; 29.5 CJK-weighted equivalents.
- **CHANGE TYPE:** `CONCLUSION_COMPRESSION`
- **RATIONALE:** Consolidate the conclusion scope sentence; the API/nominal-payload interpretation boundary remains explicit in Section 4.2.
- **SCIENTIFIC FACTS PRESERVED:** Single-platform/detector/Engine/dataset/offline/sequential scope, no stage causality, no significance claim, and no cross-platform/model generalization.
- **CITATIONS PRESERVED:** N/A — neither version contains citations.
- **MANUAL WORD ACTION:** `REPLACE ORIGINAL WITH REVISED`

## 4. Recommended manual application order

Apply edits in the exact order below, then inspect the manually formatted HFUT
Word manuscript after each group. Stop as soon as the final reference column
collapses into the preceding page.

### TIER 1 — apply first

Order: `C05 → C10 → C12 → C06 → C08 → C09 → C02 → C03 → C11 → C13`.

- Source-character saving: **709**.
- CJK-weighted saving: **623.5 equivalents**.
- Reason: safest table/prose deduplication and implementation merging first,
  followed by the high-yield but carefully bounded Section 4.2 consolidation.

### TIER 2 — only if more space is needed

Order: `C01 → C07 → C14 → C04`.

- Additional source-character saving: **192**.
- Additional CJK-weighted saving: **177.0 equivalents**.
- Cumulative CJK-weighted saving after Tier 2: **800.5 equivalents**.

### TIER 3 — reserve only

Order: `C15 → C16`.

- Additional source-character saving: **91**.
- Additional CJK-weighted saving: **85.5 equivalents**.
- Cumulative CJK-weighted saving after all tiers: **886.0 equivalents**.

Do not infer an exact Word page reduction from these Markdown metrics. The
manual HFUT Word document remains the pagination authority.
