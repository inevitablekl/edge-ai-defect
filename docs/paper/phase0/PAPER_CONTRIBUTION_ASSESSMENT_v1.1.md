Document:
PAPER_CONTRIBUTION_ASSESSMENT_v1.1

Review status:
ACCEPTED_BY_PAPER_PROJECT_MANAGER

Phase:
Paper Phase 0.3

# PAPER_CONTRIBUTION_ASSESSMENT_v1.1

## 1. Review Verdict

**PASS_WITH_REQUIRED_REFRAMING**

现有证据足以支撑电子信息硕士毕业论文和一篇工程应用型小论文，不需要新增模型、平台、量化路线、数据路径分支或工业级功能。

论文价值不能建立在“完成了训练、ONNX 转换、ONNX Runtime、TensorRT FP16、INT8、Pipeline 和 CUDA 开发”这一工程工作量本身之上，而应围绕以下研究链条组织：

1. 冻结模型、TensorRT Engine、数据集、前后处理、正确性判据和实验工作负载；
2. 建立 Jetson 端侧 ORT、FP16、INT8 和 bounded Pipeline 支撑链条；
3. 在当前 Jetson Orin Nano Super、YOLOv8n、TensorRT INT8、640×640、batch=1 和冻结工作负载下，分析推理计算加速后的数据路径优化机会；
4. 通过统一单线程 harness 排除 Stage R Attempt 1 的 runner topology 混杂；
5. 对 V0、V2、V3、V4 数据路径分支进行受控消融；
6. 联合分析任务精度、吞吐、mean/P95/P99/max latency 和 CPU 开销；
7. 保留 Gate FAIL、无显著增量、严重尾延迟和 OOM 等负向结果；
8. 形成 V0 correctness-first deployment point 与 V2 performance-first research trade-off 之间的多目标权衡。

最终仅保留两项 A 级核心贡献：

- INT8 后数据路径瓶颈分析与统一实验边界；
- 数据路径分支消融、负向结果和多目标权衡。

FP16、INT8 PTQ、Serial、Pipeline、分层正确性评价和证据治理均为 B 级重要支撑贡献，不得与两项核心贡献并列为主要创新。

冻结 PyTorch 模型和训练归档均已在外部路径保留并完成身份核验，不存在影响论文结论的训练资产缺口：

```text
Frozen PT path:
/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/models/pytorch/yolov8n_neudet_frozen.pt

Size:
6,259,683 bytes

SHA256:
5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7

Verification:
FROZEN_PT_VERIFIED

Phase 0 classification:
CANONICAL
EXTERNAL_LOCAL_ONLY
HASH_VERIFIED
RETENTION_CONFIRMED
```

训练归档也已通过归档 SHA256、tar/gzip 完整性和内部逐文件 manifest 核验。外部资产只需要常规异地备份，不需要重新训练、恢复或重新核验。

---

## 2. Recommended Central Research Question

### 推荐中心研究问题

**在当前 Jetson Orin Nano Super、YOLOv8n、TensorRT INT8、640×640、batch=1 和冻结工作负载下，推理计算加速后存在哪些输入预处理与数据路径优化机会；CUDA preprocessing、主机内存策略和有限 double buffering 分别如何影响任务精度、吞吐、平均延迟、尾延迟和 CPU 开销，并如何形成正确性优先部署点与性能优先研究点之间的多目标权衡？**

该中心问题必须保持以下边界：

- 研究对象是当前冻结平台、模型、Engine、输入尺寸、batch 和工作负载；
- 研究的是当前系统中可观测的数据路径优化机会；
- 不主张 INT8 优化后系统瓶颈必然或普遍迁移到输入数据路径；
- 不将单一 variant 的结果推广到其他模型、硬件、输入尺寸或执行形态；
- 不将常规 CUDA、pinned memory 或 double buffering 技术本身描述为算法创新。

### 研究价值

TensorRT INT8 已降低推理计算成本后，仅继续优化 TensorRT kernel 不一定能够解释完整端到端性能。

当前项目进一步研究：

- CPU/OpenCV preprocessing 的系统成本；
- Host 与 Device 之间的数据路径；
- CUDA fused preprocessing 的性能收益和精度代价；
- pageable 与 pinned raw staging 的边际差异；
- limited double buffering 对吞吐和尾延迟的影响；
- 速度提升与任务精度 Gate 之间的冲突；
- 负向优化分支对系统设计决策的意义。

该问题具有明确的系统研究对象、实验控制条件、可量化指标和限制边界，符合工程应用型硕士论文定位。

### 与已有资产的匹配程度

匹配程度高。

现有权威资产已覆盖：

- Stage Q INT8 精度和 Serial/Pipeline 基线；
- Stage R V0 component profiling；
- Attempt 2 统一单线程执行边界；
- V0、V2、V3、V4 分支；
- 每个分支五次交错独立进程运行；
- throughput、mean、P95、P99、max latency；
- CPU equivalent cores；
- V2 Gate D FAIL；
- V3 无有意义附加收益；
- V4 严重尾延迟和 OOM；
- 最终 V0/V2 两点 Pareto。

不需要构造新的实验对象或重新运行历史阶段。

### 硕士论文支撑能力

该主线可以形成完整的研究闭环：

1. 建立冻结实验对象；
2. 建立部署和正确性基线；
3. 完成 INT8 精度—性能评价；
4. 分析当前系统的数据路径优化机会；
5. 建立统一实验边界；
6. 开展数据路径消融；
7. 保留正向与负向结果；
8. 形成多目标权衡；
9. 明确适用边界。

其研究性明显强于单纯叙述“完成 Jetson TensorRT 部署”。

### 工程应用型小论文适配程度

适配程度高。

Stage R 已具备相对独立的：

- 研究问题；
- 实验基线；
- variant 定义；
- 统一执行协议；
- 正向结果；
- 负向结果；
- 精度约束；
- Pareto 结论。

因此可以直接形成一篇聚焦的数据路径研究小论文，而不是压缩整个毕业论文。

### 创新不足风险

风险中等，但可以通过正确的贡献表达控制。

CUDA preprocessing、pinned memory 和 double buffering 均为常见工程技术，不能依靠技术名称建立创新性。

论文贡献应来自：

- 固定任务中的系统问题识别；
- 统一 harness 下的受控消融；
- correctness 与 performance 联合评价；
- mean 与 tail latency 同时呈现；
- 无增益和有害分支的保留；
- correctness-first 与 performance-first 的权衡解释。

### 范围膨胀风险

只要范围保持为：

- 单一 Jetson Orin Nano Super；
- 单一 YOLOv8n；
- 单一 TensorRT INT8 Engine；
- 640×640；
- batch=1；
- 冻结 180 图工作负载；
- 已完成的 V0/V2/V3/V4；

范围膨胀风险可控。

不得继续扩展到 zero-copy、多模型、多平台、动态 shape、batch>1、多 ExecutionContext、GPU NMS 或产品级调度框架。

---

## 3. Alternative Research Line and Rejection Reason

### 备选研究主线

**基于 Jetson 的工业缺陷检测多精度部署与流水线优化研究：从 ONNX Runtime CPU、TensorRT FP16、TensorRT INT8 到 bounded Pipeline。**

### 可取之处

该主线能够完整展示：

- 模型训练和冻结；
- ONNX 转换；
- Jetson ORT CPU baseline；
- TensorRT FP16；
- TensorRT INT8 PTQ；
- Serial 与 Pipeline；
- 正确性、性能和稳定性评价。

适合作为硕士论文的总体技术链条。

### 不推荐作为中心研究问题的原因

#### 1. 常规部署流程占比过高

ORT、TensorRT FP16、INT8 PTQ 和 Pipeline 都是已有工程技术。

将其直接串联容易形成开发过程报告，而不是围绕明确研究问题组织的论文。

#### 2. 不同阶段 timing boundary 不统一

Stage J、K、P、Q、R 在以下方面存在差异：

- workload；
- warmup；
- measured frames；
- execution form；
- timing start/end；
- 是否包含 H2D；
- 是否包含 sink；
- 是否为 Serial 或 Pipeline。

因此不能将其组织成一个无边界说明的统一性能排行榜。

#### 3. 核心创新强度不足

多精度部署流程本身不足以构成强核心贡献。

其中真正具有论文价值的部分仍然是：

- FP16 raw correctness 与 task-level acceptance 分层；
- INT8 精度—性能权衡；
- Pipeline 吞吐与单帧延迟的边界；
- Stage R 数据路径消融；
- Stage R 负向结果；
- 多目标 Pareto。

#### 4. 容易引发不必要的补实验

如果将多阶段性能演进作为中心主线，容易进一步要求：

- 统一所有 timing boundary；
- 重跑 ORT、FP16、INT8 和 Pipeline；
- 补齐跨阶段资源和功耗；
- 重建统一 runtime。

这些工作会显著增加延期风险，但不会实质提升论文主线。

### 最终处理

该备选主线不作为中心研究问题。

ORT、FP16、INT8 PTQ 和 bounded Pipeline 保留为硕士论文的重要支撑链条，为 Stage R 核心研究提供：

- 基线；
- 正确性边界；
- 精度代价；
- 性能背景；
- 执行形态对照。

---

## 4. Contribution Classification

|Technical Asset|Grade|Contribution Type|Evidence|Paper Role|Restriction|
|---|---|---|---|---|---|
|模型训练与冻结|C|工程实现资产|9 组训练；seed 7 冻结；test P/R/mAP50/mAP50-95 = 0.724/0.728/0.769/0.431；冻结 PT 已完成大小和 SHA256 核验；训练归档完整性已核验|提供固定研究模型和可追溯训练输入|不得称为检测算法创新；三 seed 结果仅为描述性观察|
|ONNX 转换与一致性|C|工程实现资产|opset 17；静态 640；固定 FP32 输入输出；10 图 PT/ONNX raw 和 detection consistency PASS|建立跨后端模型契约和 TensorRT 输入|不得外推为全样本、全平台或 bitwise equivalence|
|ORT C++ CPU baseline|B|工程方法贡献|Jetson ORT CPU EP FP32；五次正式运行；约 97.12 ms inference、9.83 pre-sink FPS；约 30 分钟稳定性|提供 Jetson CPU 部署基线和后续 TensorRT 对照背景|不能与不同 timing boundary 的 K/P/Q/R 数值直接排名|
|TensorRT FP16|B|工程方法贡献；实验性发现|raw Level B 仅 1/16 PASS；task-level accepted；正式 Serial inference speedup 1.156675x，E2E speedup 1.102438x|说明 raw numerical correctness 与 task-level correctness 必须分层评价；提供 INT8 对照|不得称为原始张量等价；不得将 host roundtrip 表述为 GPU kernel-only|
|TensorRT INT8 PTQ|B|工程方法贡献；实验性发现|split v2；1260 图 calibration；180 图 accuracy；mAP50 下降 0.008399；mAP50-95 下降 0.007205；Serial inference speedup 1.269856x|建立 INT8 精度—性能基线和 Stage R 前置条件|不得称为无损量化或新量化算法；必须保留精度下降|
|bounded Pipeline|B|工程方法贡献；实验性发现|四 worker、三 bounded SPSC queue、capacity=1；Stage P 描述性吞吐比 4.165718x；Stage Q Pipeline ratio 1.012575|说明执行形态对吞吐的影响，并区分 Serial 与 Pipeline|4.165718x 不代表统计显著性、单帧延迟降低或实时相机普遍收益|
|INT8 后数据路径瓶颈分析与统一实验边界|A|学术贡献；工程方法贡献|固定模型、Engine、数据集和正确性边界；Attempt 2 统一单线程 harness；排除 Attempt 1 runner topology 混杂；V0 profiling|构成核心研究问题和实验方法基础|只能描述当前平台、模型和工作负载下的数据路径优化机会，不得普遍化|
|CUDA preprocessing 分支|B|工程方法贡献；实验性发现|V2 相对 V0：FPS 54.865→126.120；mean latency 18.168→7.870 ms；CPU 0.841→0.756；Gate D FAIL|构成核心消融中的主要正向性能分支|CUDA 技术本身不是创新；V2 不是 correctness-equivalent 或生产替代方案|
|pageable/pinned memory 分支|B|实验性发现|V3 相对 V2 仅 +0.70% FPS、mean latency -0.81%，CPU 增加；不同 set 方向翻转|构成内存策略消融，说明当前路径中附加 pinned staging 无有意义收益|不得推广为 pinned memory 普遍无效|
|limited double buffering 分支|B|实验性发现|V4 26.746 FPS；mean 32.278 ms；max 9324.231 ms；各正式运行有约 9–10 秒尾部；另有一次 OOM|构成关键负向消融|不得推广为 double buffering 普遍有害；不得在证据不足时断言根因|
|数据路径分支消融、负向结果和多目标权衡|A|学术贡献；工程方法贡献；实验性发现|V0/V2/V3/V4；精度、吞吐、mean/P95/P99/max、CPU；Gate D FAIL；V3 无有意义增量；V4 尾延迟和 OOM；V0/V2 Pareto|构成论文核心实验与主要结论|Pareto 仅适用于已执行分支；V2 必须保持 research-only 定位|
|correctness/evidence methodology|B|工程方法贡献|模型、split、配置和 hash 冻结；raw/task correctness；canonical hash；timing boundary；supersession；negative-result retention|作为实验可信度和可复现性方法学特色|不得独立包装为核心创新、形式化验证理论或通用证据平台|
|invalidated、superseded 和 rejected 资产|D|历史过程资产|invalidated K7、旧 P5 conclusion、split_v1、Stage R Attempt 1 横向结果等|仅用于说明方法修正、证据治理和失败过程|不得重新进入正式对比或支持最终数值结论|

---

## 5. Recommended Core Contributions

### Core Contribution 1

#### INT8 后数据路径瓶颈分析与统一实验边界

##### Contribution statement

在固定模型、TensorRT INT8 Engine、数据集、任务正确性判据和冻结工作负载的条件下，建立统一单线程数据路径实验 harness，排除 Stage R Attempt 1 中不同 runner topology 对横向比较造成的混杂，并分析当前 Jetson Orin Nano Super、YOLOv8n、640×640、batch=1 系统中的输入预处理与数据路径优化机会。

该贡献是系统级部署研究与受控实验方法贡献，不是新的检测算法、量化算法或 CUDA 算法。

##### Supporting evidence

- 固定 Jetson Orin Nano Super；
- 固定 YOLOv8n；
- 固定 TensorRT INT8 Engine；
- 固定 640×640；
- 固定 batch=1；
- 固定 180 图 test manifest；
- 固定前后处理和任务正确性判据；
- Attempt 2 使用统一 single-thread inline loop；
- CPU affinity 0–5；
- OpenCV threads=1；
- 60 warmup；
- 每次 1080 measured frames；
- 每个分支五次交错独立进程运行；
- 零 drop；
- V0、V2、V3、V4 使用相同执行边界；
- Attempt 1 因 V0 和其他分支 runner topology 不同，不再作为横向数值权威。

##### Allowed strength of claim

允许表述为：

> 在当前 Jetson Orin Nano Super、YOLOv8n、TensorRT INT8、640×640、batch=1 和冻结工作负载下，推理计算加速后，输入预处理和数据路径表现出进一步优化机会。

允许表述为：

> 统一单线程 harness 消除了 Attempt 1 中 runner topology 不一致带来的主要横向比较混杂。

允许表述为：

> Stage R 将评价对象从单独的 TensorRT inference time 扩展到受控端到端数据路径。

##### Required limitation

必须注明：

- 不主张 INT8 优化后瓶颈必然迁移；
- 不主张所有 Jetson、模型或工作负载均由输入数据路径主导；
- 结论仅适用于当前固定实验条件；
- 未覆盖 batch>1；
- 未覆盖动态 shape；
- 未覆盖多 ExecutionContext；
- 未覆盖多模型；
- 未覆盖 GPU NMS；
- 未建立统计显著性推断；
- Stage R Attempt 2 与 Stage P Pipeline 的执行形态不同，不能直接比较吞吐数值。

---

### Core Contribution 2

#### 数据路径分支消融、负向结果和多目标权衡

##### Contribution statement

在统一 INT8 执行边界下，对 CPU/OpenCV preprocessing、CUDA fused preprocessing、pageable/pinned raw staging 和 limited double buffering 进行受控分支消融，联合评价任务精度、吞吐、mean/P95/P99/max latency 和 CPU 开销，并通过保留 Gate FAIL、无有意义增量、严重尾延迟和 OOM 等负向结果，形成 correctness-first deployment point 与 performance-first research trade-off 之间的多目标权衡。

该贡献的价值不在于首次使用 CUDA、pinned memory 或 double buffering，而在于：

- 同一边界下的受控比较；
- 精度和性能联合评价；
- average 与 tail latency 联合评价；
- 负向分支的完整保留；
- 部署点和研究型性能点的明确区分。

##### Supporting evidence

###### V0：correctness-first deployment baseline

- CPU/OpenCV preprocessing；
- pageable FP32 HostTensor；
- TensorRT INT8；
- 54.865 FPS；
- mean latency 18.168 ms；
- P95 18.830 ms；
- P99 19.004 ms；
- max 19.234 ms；
- CPU 0.841 equivalent cores；
- Stage Q canonical correctness baseline。

###### V2：performance-first research trade-off

- pageable raw staging；
- CUDA fused preprocessing；
- device input；
- 126.120 FPS；
- mean latency 7.870 ms；
- P95 9.935 ms；
- P99 11.552 ms；
- max 12.686 ms；
- CPU 0.756 equivalent cores；
- 相对 V0：
  - FPS +129.87%；
  - mean latency -56.68%；
- Gate A/B/C PASS；
- Gate D FAIL；
- mAP50 drop 0.00537575，超过 0.005 阈值 0.00037575；
- max-class AP50 drop 0.02673348；
- max-class Recall drop 0.03030303。

###### V3：无有意义附加收益

- V2 + long-lived pinned raw staging；
- 127.005 FPS；
- mean latency 7.807 ms；
- CPU 0.837 equivalent cores；
- 相对 V2：
  - FPS +0.70%；
  - mean latency -0.81%；
  - CPU 增加 0.081 equivalent cores；
- 不同 set 的变化方向发生翻转；
- 不支持稳定、有意义的增量收益。

###### V4：负向消融

- V3 + two-slot limited double buffering；
- 26.746 FPS；
- mean latency 32.278 ms；
- P95 22.675 ms；
- P99 22.907 ms；
- aggregate max 9324.231 ms；
- CPU 1.001 equivalent cores；
- 每个正式运行均出现一次约 8.98–10.24 秒严重尾部；
- 一次进程返回 -9；
- kernel evidence 记录约 5.1 GiB anon RSS；
- 协议允许的一次重跑完成；
- 失败样本不进入正式 aggregate，但异常必须保留。

###### Pareto conclusion

最终保留两点：

- V0：correctness-first deployment point；
- V2：performance-first research trade-off。

V3 不构成新的 Pareto 点。

V4 被 V0、V2、V3 支配，并具有严重尾延迟和 OOM 风险记录。

##### Allowed strength of claim

允许表述为：

> 在当前受控系统中，CUDA fused preprocessing 相对 CPU/OpenCV baseline 获得了显著的描述性吞吐和平均延迟改善，但其任务精度未通过冻结 Gate D，因此只能作为 performance-first research trade-off。

允许表述为：

> 在当前 batch=1、单线程数据路径中，增加 pinned raw staging 未表现出有意义的附加收益。

允许表述为：

> 当前 limited double-buffer implementation 在吞吐、平均延迟和尾延迟方面均表现为负向分支，并伴随一次 OOM 异常。

允许表述为：

> 最终多目标结果不能简化为“FPS 最高者即最优部署方案”，而应区分 V0 的正确性优先属性与 V2 的性能优先属性。

##### Required limitation

必须注明：

- V2 不是 correctness-equivalent；
- V2 不得作为生产替代方案；
- Gate D FAIL 必须进入主要结果和结论；
- V3 结果不能推广为 pinned memory 普遍无效；
- V4 结果不能推广为 double buffering 普遍有害；
- V4 OOM 的具体因果根因尚未被正式证明；
- V3/V4 通过相同 detection SHA 继承 V2 任务结果，没有独立任务精度评价；
- 当前没有正式跨 variant GPU utilization、常态 RAM 和 rail/power 对比矩阵；
- 当前 Pareto 只覆盖 V0/V2/V3/V4；
- 未执行 V1 和 V5 不构成实验缺口，也不得假设其结果。

---

### Important Supporting Contributions

#### Supporting Contribution 1：FP16、INT8、Serial 与 Pipeline 的分层部署评价

该项为 B 级重要支撑贡献，不与两项核心贡献并列为主要创新。

##### Supporting role

它为 Stage R 提供：

- Jetson 部署基线；
- FP16 task-level correctness 边界；
- INT8 精度—性能基线；
- Serial 和 Pipeline 执行形态背景；
- INT8 后进一步研究数据路径的动机。

##### Supporting evidence

- FP16 raw Level B：FAIL，1/16 PASS；
- FP16 task-level：accepted；
- FP16 inference speedup 1.156675x；
- FP16 E2E speedup 1.102438x；
- INT8 相对 FP16：
  - mAP50 下降 0.008399；
  - mAP50-95 下降 0.007205；
  - Recall 下降；
  - Serial inference speedup 1.269856x；
  - pre-sink throughput ratio 1.172850；
- Stage Q Pipeline throughput ratio 1.012575；
- Q7 classification 为 no material regression；
- Stage P bounded Pipeline 在冻结离线工作负载中得到 4.165718x 描述性吞吐观测。

##### Allowed statement

可以表述为：

> FP16 未达到 raw tensor 等价，但在冻结测试集上达到 task-level acceptance。

可以表述为：

> INT8 以可量化的精度下降换取了 Serial 推理性能改善。

可以表述为：

> bounded Pipeline 显著提高了冻结离线 replay workload 的吞吐，但该观测不代表单帧延迟降低或实时相机中的普遍收益。

##### Limitation

- FP16 raw Level B FAIL 不得省略；
- INT8 精度下降不得省略；
- Q7 不支持大幅 Pipeline 提升；
- 4.165718x 不代表统计显著性；
- Stage P 不能外推到实时相机；
- 不同阶段 timing boundary 不得混用。

#### Supporting Contribution 2：分层正确性和证据方法

该项为 B 级工程方法贡献，可作为实验可信度的方法学特色，但不得作为独立核心创新。

##### Supporting role

用于保证：

- 研究输入可追溯；
- 实验结果与对应模型、Engine、split 和配置绑定；
- raw correctness 与 task correctness 不被混淆；
- 不同 timing boundary 不被混合；
- invalidated、superseded 和 negative evidence 不被误用或删除。

##### Supporting evidence

- 冻结 PT 已完成：
  - 路径确认；
  - 6,259,683 bytes；
  - SHA256 核验；
  - `FROZEN_PT_VERIFIED`；
  - `CANONICAL`；
  - `EXTERNAL_LOCAL_ONLY`；
  - `HASH_VERIFIED`；
  - `RETENTION_CONFIRMED`；
- 训练归档已通过：
  - 归档 SHA256；
  - tar/gzip 完整性；
  - 内部逐文件 manifest；
- ONNX identity 和 contract；
- split_v2 authority；
- Engine identity；
- runtime config；
- raw Level B 与 task-level 分层；
- canonical RUN/CYCLE/detection hash；
- frozen workload；
- timing boundary；
- repeated runs；
- invalidated K7 排除；
- Stage P old P5 conclusion 排除；
- Stage R Attempt 1 横向结果排除；
- V4 OOM 和尾延迟保留。

##### Allowed statement

可以表述为：

> 本研究采用分层正确性和可追溯证据方法，使模型身份、数据划分、执行配置、工作负载、时间边界和实验结论之间保持可核验对应关系。

##### Limitation

不得表述为：

- 新的形式化验证理论；
- 通用 Edge AI benchmark 标准；
- 产品级测试认证系统；
- 工业安全认证方法；
- 独立核心创新点。

---

## 6. Engineering Assets Not Counted as Innovation

以下内容可以进入系统设计、实现或实验准备章节，但不能单独称为论文主要创新：

1. 使用 YOLOv8n 训练 NEU-DET；
2. 比较九组训练记录；
3. 选择 seed 7；
4. 冻结 PyTorch 模型；
5. 保存训练归档；
6. 导出 ONNX；
7. 使用 opset 17；
8. 固定静态 640 输入；
9. 编写 ONNX Runtime C++ 推理；
10. 构建 TensorRT FP16 Engine；
11. 使用 TensorRT legacy calibrator 构建 INT8 Engine；
12. 调用 `enqueueV3`；
13. 实现 SerialRunner；
14. 实现 bounded Pipeline；
15. 实现 SPSC queue；
16. 实现 CUDA preprocessing kernel；
17. 调用 `cudaHostAlloc`；
18. 实现两个 buffer slot；
19. 使用 tegrastats 或 profiler；
20. 保存 JSON、CSV、manifest 和 SHA256；
21. 建立报告目录和 evidence index；
22. 执行 Git tag、commit 和资产冻结；
23. 记录失败、supersession 和 reclassification。

这些资产的重要性在于：

- 保证工程完整性；
- 支撑复现实验；
- 建立研究基线；
- 支撑求职项目展示；
- 证明结论来源于真实部署系统。

但常规工具和技术第一次应用于本项目，不自动构成创新。

可以形成论文贡献的是这些工程资产支持的：

- 明确研究问题；
- 统一实验边界；
- 受控消融；
- 定量结果；
- correctness/performance trade-off；
- tail latency 分析；
- 负向结果；
- 适用边界。

---

## 7. Experiment Sufficiency Assessment

### 总体结论

**SUFFICIENT_WITH_LIMITATIONS**

现有实验足以支撑推荐中心主线、两项 A 级核心贡献和 B 级支撑链条。

无 Must 级新增实验。

不存在需要通过新增模型、平台、量化路线、数据路径分支或工业级稳定性测试解决的关键缺口。

|Assessment Area|Verdict|Supporting Basis|Limitation|Required Treatment|
|---|---|---|---|---|
|精度—性能权衡|SUFFICIENT|FP16 task metrics、INT8 180 图 accuracy、Q6 Serial、Stage R V2 correctness/performance 完整|FP16 raw FAIL；INT8 和 V2 存在精度下降；无显著性推断|必须同时呈现精度代价和性能收益|
|ORT、FP16、INT8 部署路径|SUFFICIENT_WITH_LIMITATIONS|Stage J、K、Q 均有正式正确性、性能和稳定性证据|不同阶段 timing boundary 不同|按阶段分组报告，不形成统一性能排名|
|Serial 与 Pipeline 对比|SUFFICIENT_WITH_LIMITATIONS|Stage P paired comparison；Stage Q FP16/INT8 Pipeline comparison|冻结离线 replay；不代表单帧延迟或实时相机|将 4.165718x 限定为描述性吞吐观测|
|当前 INT8 系统的数据路径优化机会|SUFFICIENT_WITH_LIMITATIONS|R1 profiling；Attempt 2 统一 harness；V0/V2 差异|不能推导普遍瓶颈迁移规律|必须限定平台、模型、尺寸、batch 和 workload|
|数据路径分支消融|SUFFICIENT|V0/V2/V3/V4；每个分支五次交错独立进程运行；精度、吞吐、mean/P95/P99/max、CPU 和负向异常|V1/V5 未执行；V3/V4 无独立 task evaluation|只评价实际执行分支，不要求补实验|
|稳定性与资源约束|SUFFICIENT_WITH_LIMITATIONS|J/K/P 约 30 分钟；Q 约 300 秒；R 五次正式运行和 OOM 保留|Stage R 无正式 GPU、常态 RAM、功耗和长时间矩阵|不得提出功耗优化或工业长期稳定性结论|
|训练资产与可追溯性|SUFFICIENT|冻结 PT 大小和 SHA256 已核验；训练归档 SHA256、tar/gzip 和内部 manifest 已核验|资产为 EXTERNAL_LOCAL_ONLY|只需常规异地备份，不影响论文结论|

### Must

**无 Must 级新增实验。**

必须完成的仅是论文表述约束：

- 保留 FP16 raw Level B FAIL；
- 定量呈现 INT8 精度下降；
- 呈现 V2 Gate D FAIL；
- 明确 V2 research-only；
- 保留 V3 无有意义增量；
- 保留 V4 严重尾延迟和 OOM；
- 区分不同 timing boundary；
- 不进行普遍化推断。

### Should

**无 Should 级实验或资产恢复任务。**

冻结 PT 和训练归档已经完成保留与身份核验。

常规异地备份属于日常资产管理，不构成 Phase 0.3 缺口，也不影响当前结论。

### Optional

不提出新的实验性 Optional 项目。

可以使用已有结果完成：

- 表格统一；
- timing boundary 注释；
- Pareto 图；
- latency distribution 图；
- V4 tail event 可视化；
- correctness/performance trade-off 图。

这些属于论文数据整理和呈现，不属于新增实验。

---

## 8. Thesis Scope Recommendation

### 硕士毕业论文建议研究链条

#### 第一部分：研究对象与冻结实验边界

建议包括：

- 工业缺陷检测端侧部署问题；
- Jetson Orin Nano Super；
- YOLOv8n；
- NEU-DET；
- 640×640；
- batch=1；
- 模型、ONNX、Engine 和训练归档身份；
- split v2；
- 前后处理；
- test manifest；
- raw correctness；
- task-level correctness；
- timing boundary。

冻结 PT 和训练归档状态应准确表述为：

> 模型及训练归档均采用外部本地保留方式，已完成文件身份、归档完整性和内部 manifest 核验。

不得写成资产缺失或等待恢复。

#### 第二部分：ORT CPU 部署基线

建议包括：

- Jetson ORT CPU EP；
- FP32；
- Serial C++ pipeline；
- correctness；
- 正式性能；
- 稳定性；
- 作为 TensorRT 路线的工程基线。

不将其作为核心创新。

#### 第三部分：TensorRT FP16 部署与分层正确性

建议包括：

- FP16 Engine；
- raw Level B FAIL；
- task-level acceptance；
- K7 正式性能；
- raw correctness 与 task-level correctness 的区别。

该部分是重要支撑章节。

#### 第四部分：TensorRT INT8 PTQ 精度—性能评价

建议包括：

- split v2；
- calibration provenance；
- INT8 compute composition；
- FP16 与 INT8 accuracy；
- Serial performance；
- Pipeline no-material-regression；
- INT8 精度下降。

该部分为 Stage R 提供直接研究基础。

#### 第五部分：bounded Pipeline 执行形态

建议包括：

- 四 worker；
- 三 bounded SPSC queue；
- capacity=1；
- blocking drop policy；
- 单 inference worker；
- 4.165718x 的精确定义；
- 为什么不代表单帧延迟降低；
- 为什么不能推广到实时相机；
- Q7 中 INT8 Pipeline 的 no-material-regression。

该部分是系统执行形态支撑，不作为核心创新。

#### 第六部分：当前 INT8 系统的数据路径优化机会与统一实验边界

建议包括：

- V0 component profiling；
- 当前系统中的数据路径研究动机；
- Attempt 1 runner topology 混杂；
- Attempt 1 横向结果排除；
- Attempt 2 unified harness；
- 固定单线程执行边界；
- variant 控制变量。

该部分对应 Core Contribution 1。

#### 第七部分：数据路径分支消融

建议包括：

- V0；
- V2；
- V3；
- V4；
- correctness Gate；
- task accuracy；
- throughput；
- mean；
- P95；
- P99；
- max latency；
- CPU equivalent cores；
- tail latency；
- OOM；
- per-set consistency。

该部分对应 Core Contribution 2。

#### 第八部分：多目标权衡与负向结果

建议包括：

- V0 correctness-first deployment point；
- V2 performance-first research trade-off；
- Gate D FAIL；
- V3 无有意义增量；
- V4 dominated；
- V4 tail instability；
- V4 OOM anomaly；
- 为什么最高 FPS 不等于最佳部署方案；
- 适用边界。

### 硕士论文不应扩展为

- 新检测算法研究；
- 新量化算法研究；
- 通用推理框架；
- 多平台 benchmark；
- 多模型 benchmark；
- 产品级 Pipeline；
- 工业相机系统；
- ROS2/DeepStream 平台；
- 工业长期可靠性认证；
- 通用 CUDA memory framework；
- 多租户并发服务。

---

## 9. Engineering Paper Scope Recommendation

### 推荐聚焦主题

**面向 Jetson TensorRT INT8 工业缺陷检测的数据路径优化机会与分支消融：精度、吞吐和尾延迟的多目标权衡**

该主题聚焦 Stage R，不简单压缩毕业论文。

### 小论文研究对象

固定：

- Jetson Orin Nano Super；
- YOLOv8n；
- TensorRT INT8；
- 640×640；
- batch=1；
- 冻结 180 图工作负载；
- 统一单线程 harness；
- V0/V2/V3/V4。

### 小论文核心问题

1. 当前 INT8 系统中是否存在输入预处理和数据路径优化机会；
2. CUDA fused preprocessing 能带来何种性能变化；
3. 性能收益是否满足任务精度 Gate；
4. pinned raw staging 是否产生有意义增量；
5. limited double buffering 是否改善吞吐和尾延迟；
6. 如何在 correctness、throughput、mean latency、tail latency 和 CPU 开销之间选择部署点。

### 小论文必须使用的核心证据

#### Core Contribution 1 证据

- 固定实验对象；
- Attempt 1 topology confounding；
- Attempt 2 unified harness；
- V0 profiling；
- 统一 workload 和 timing boundary。

#### Core Contribution 2 证据

- V0/V2/V3/V4；
- 每个分支五次交错独立进程运行；
- FPS；
- mean/P95/P99/max；
- CPU equivalent cores；
- V2 Gate D FAIL；
- V3 无有意义增量；
- V4 severe tails；
- V4 OOM；
- V0/V2 Pareto。

### 小论文中的支撑证据

可简要纳入：

- Stage Q INT8 accuracy；
- Stage Q INT8 Serial performance；
- INT8 作为 Stage R baseline；
- raw/task correctness 分层方法；
- hash、manifest 和 timing boundary。

### 不应进入小论文主线的内容

- 九组模型训练详细过程；
- ORT CPU 全部实现细节；
- Stage J 完整性能表；
- Stage K 开发过程；
- Stage P Pipeline 完整架构；
- 4.165718x 作为核心结果；
- Stage Q Pipeline 大量细节；
- Git 和 evidence index 管理过程；
- 未实施 V1；
- 未实施 V5；
- zero-copy 讨论；
- 多平台和多模型扩展。

### 小论文允许的贡献表述

可以表述为：

- 在固定 Jetson INT8 工业缺陷检测系统中建立统一数据路径消融边界；
- 分析当前系统中的输入预处理和数据路径优化机会；
- 联合评价 accuracy、throughput、mean latency、tail latency 和 CPU；
- 揭示 V2 性能收益与 Gate D FAIL 之间的冲突；
- 发现当前 pinned staging 未产生有意义增量；
- 保留并分析 limited double buffering 的严重尾延迟和 OOM；
- 形成 correctness-first 与 performance-first 两点权衡。

不得表述为：

- 提出新的 CUDA preprocessing 算法；
- 提出新的 pinned-memory 方法；
- 提出新的 double-buffering 算法；
- 证明 INT8 后瓶颈普遍迁移；
- 实现无损 INT8；
- 实现生产级实时工业系统；
- 证明 V2 可替代 V0。

---

## 10. Overclaim and Review Risks

|Risk|Evidence Boundary|Required Control|
|---|---|---|
|把训练和部署实现称为主要创新|训练、ONNX、ORT、FP16、INT8 都是常规工程路线|只将其作为 C/B 级资产和支撑链条|
|将 CUDA preprocessing 本身称为创新|CUDA fused preprocessing 是已有技术|创新表述放在统一消融、定量发现和多目标权衡|
|宣称 INT8 后瓶颈普遍迁移|只研究一个 Jetson、一个模型、一个尺寸、batch=1|使用“当前系统中的数据路径优化机会”|
|宣称 FP16 raw 等价|raw Level B 仅 1/16 PASS|必须同时报告 raw FAIL 与 task-level acceptance|
|宣称 INT8 无损|mAP50、mAP50-95 和 Recall 均有下降|定量呈现精度代价|
|把 V2 写成部署推荐|V2 Gate D FAIL|始终标记为 performance-first research trade-off|
|隐藏 Gate D FAIL|V2 超过冻结阈值 0.00037575|进入摘要性结果、主表和结论限制|
|把 V3 写成 pinned 优化成功|仅 +0.70% FPS，set 方向翻转，CPU 增加|结论限定为无有意义附加收益|
|把 pinned memory 普遍判定无效|仅当前 batch=1、单线程路径|不得推广至其他系统|
|忽略 V4 负向结果|严重尾延迟、低吞吐和 OOM|必须进入主要消融和讨论|
|宣称 double buffering 普遍有害|只测试当前 V4 implementation|仅判定当前实现为负向分支|
|断言 V4 OOM 根因|现有证据为进程 -9、RSS 和重跑|只描述异常，不断言因果机制|
|把最高 FPS 当作最优部署|V2 Gate D FAIL|使用 V0/V2 多目标权衡|
|把 4.165718x 当统计结论|三组 paired 描述性观测|不得使用 statistically significant|
|把 4.165718x 当单帧延迟改善|指标是 wall throughput|明确吞吐与单帧 latency 不同|
|推广 Stage P 到实时相机|工作负载是 offline replay|限定为冻结离线 workload|
|把 Stage Q Pipeline 写成显著提升|ratio 1.012575|只支持 no material regression|
|混合 timing boundary|J/K/P/Q/R 时间边界不同|按阶段和 protocol 分组报告|
|宣称功耗优化|Stage R 缺少正式 rail/power 矩阵|不得提出功耗改善结论|
|宣称工业长期稳定|稳定性时长和场景有限|只称 bounded engineering evidence|
|把 evidence methodology 称为核心创新|属于项目可信度方法|保持 B 级方法学特色|
|错误描述 PT 缺失|冻结 PT 和训练归档已验证|统一表述为 external retained and verified|
|扩展为通用平台|当前范围为单平台、单模型、batch=1|明确停止扩展边界|

---

## 11. Scope Stop List

### 当前不应新增的实验

1. 不新增模型；
2. 不新增数据集；
3. 不新增 Jetson 型号；
4. 不新增 RK3588；
5. 不新增 x86 GPU；
6. 不新增多平台比较；
7. 不补 batch>1；
8. 不补动态 shape；
9. 不补其他输入尺寸；
10. 不进入 QAT；
11. 不进入 Q/DQ；
12. 不进入 TensorRT ModelOpt；
13. 不进入 TensorRT 11 重做；
14. 不增加 DLA；
15. 不增加 GPU NMS；
16. 不增加多 ExecutionContext；
17. 不增加多模型并发；
18. 不执行 V1；
19. 不执行 V5；
20. 不增加 mapped zero-copy；
21. 不继续优化 V4；
22. 不增加更多 stream；
23. 不增加更复杂异步调度；
24. 不重新统一运行 Stage J/K/P/Q/R；
25. 不补正式功耗矩阵；
26. 不补工业级长时间稳定性；
27. 不补实时相机以推广 Stage P；
28. 不因 FP16 raw FAIL 重建 FP16；
29. 不因 INT8 精度下降进入重训练；
30. 不因 V2 Gate D FAIL 进入 QAT；
31. 不因 V4 负向结果推翻 Stage R；
32. 不重新训练冻结模型；
33. 不重新核验已完成身份验证的冻结 PT 和训练归档。

### 当前不应实现的功能

1. 通用 BufferManager；
2. 通用 CUDA memory abstraction；
3. 通用多后端 runtime；
4. 多模型动态加载；
5. 工业相机接入框架；
6. ROS2 集成；
7. DeepStream 集成；
8. 通用视频流系统；
9. 自动 batch；
10. 动态 TensorRT profile；
11. 多租户推理；
12. 多 ExecutionContext 调度；
13. 产品级内存池；
14. 产品级自动故障恢复；
15. 工业监控和告警；
16. 远程部署；
17. OTA；
18. 配置热更新；
19. 通用 benchmark 平台；
20. 跨平台硬件抽象；
21. 通用 evidence management platform；
22. 生产级 zero-copy 框架；
23. 产品级长期资源生命周期系统。

### 当前不应提出的论文主张

1. 提出了新的检测算法；
2. 提出了新的 YOLO 结构；
3. 提出了新的量化算法；
4. 提出了新的 CUDA preprocessing 算法；
5. 提出了新的 pinned-memory 方法；
6. 提出了新的 double-buffering 算法；
7. 实现了无损 INT8；
8. FP16 与 FP32 raw tensor 等价；
9. INT8 后瓶颈必然迁移到输入路径；
10. INT8 后瓶颈普遍迁移到输入路径；
11. V2 与 V0 correctness-equivalent；
12. V2 可作为生产替代；
13. CUDA preprocessing 在所有 Jetson 上都更优；
14. pinned memory 普遍无效；
15. double buffering 普遍有害；
16. Pipeline 普遍获得 4.165718x；
17. Pipeline 降低单帧延迟；
18. offline replay 可以代表实时相机；
19. Stage Q Pipeline 获得显著提升；
20. Stage R 结果具有统计显著性；
21. 不同 stage 数字可以直接排名；
22. 系统达到工业级长期稳定；
23. 系统达到产品级可靠性；
24. 系统实现显著功耗改善；
25. 研究结论适用于多模型、多平台和多尺寸；
26. V4 OOM 根因已确定；
27. 项目形成通用 Edge AI 平台；
28. 冻结 PT 当前缺失；
29. 训练归档尚未核验；
30. 训练资产缺口影响论文可复现性。

---

## 12. Phase 0.3 Verdict

**PASS_WITH_REQUIRED_REFRAMING**

通过条件如下：

1. 论文中心主线保持为当前固定系统中的 INT8 后数据路径优化机会、统一实验边界、分支消融和多目标权衡；
2. 只保留两项 A 级核心贡献：
   - INT8 后数据路径瓶颈分析与统一实验边界；
   - 数据路径分支消融、负向结果和多目标权衡；
3. FP16、INT8、Serial、Pipeline 和证据方法保持为 B 级重要支撑贡献；
4. correctness/evidence methodology 不作为独立核心创新；
5. FP16 raw Level B FAIL 必须保留；
6. FP16 只允许表述为 task-level accepted；
7. INT8 精度下降必须定量呈现；
8. Stage P 4.165718x 只能作为冻结离线工作负载下的描述性吞吐观测；
9. Stage P 结果不代表单帧延迟降低；
10. Stage P 结果不推广到实时相机；
11. Stage Q Pipeline 只支持 no material regression；
12. Stage R Attempt 2 是横向消融权威；
13. Attempt 1 只保留为 runner topology 混杂和方法修正背景；
14. V2 必须标记为 performance-first research trade-off；
15. V2 不得表述为 correctness-equivalent；
16. V2 不得表述为生产替代方案；
17. Gate D FAIL 必须进入主要结果；
18. V3 只能表述为无有意义附加收益；
19. V4 必须作为严重尾延迟和 OOM 的负向消融；
20. 不混用不同 timing boundary；
21. 不新增模型、平台、量化路线、数据路径分支或工业级功能；
22. 冻结 PT 和训练归档应表述为外部保留、身份核验完成；
23. 不存在影响论文结论的训练资产缺口；
24. 外部训练资产只需常规异地备份，不需要重新训练、恢复或重新核验。

---

## 13. Recommended Next Actor

Paper Project Manager
