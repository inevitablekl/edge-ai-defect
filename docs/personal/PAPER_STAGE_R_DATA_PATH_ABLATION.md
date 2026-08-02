# 论文实验章节草稿 — INT8 推理数据路径优化与消融实验

> **状态**：论文材料草稿（Paper-Ready Draft）。本节所有数值均直接读取自冻结的
> Stage R Attempt 2 统一消融 Evidence 与 R5 Pareto 收尾 Evidence，未手工录入。
> 数据溯源见文末「数据溯源」附录；机器可读表格见
> `results/paper/stage_r/`（CSV 与 `metadata.json`）。
>
> **禁止引用范围**：Attempt 1
> （`results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v1/`）为
> `R3_ATTEMPT_1_NONCOMPARABLE_HARNESS`，仅可作为 PipelineRunner 并发背景
> （见 §10），不得进入本节任何横向性能表格。

---

## 1. 研究动机

在 TensorRT INT8 量化显著降低 GPU 计算成本之后，CPU 侧预处理、Host 侧数据搬运
与同步等待成为可观测的系统开销来源。本实验的目标是：在保持检测任务正确性约束
的前提下，对推理数据路径（preprocessing → staging → H2D → TensorRT INT8 →
postprocess）进行受控消融，量化各路径增量机制的性能-精度权衡。

Stage R R1 基线剖析（V0 路径实测均值，来源
`results/validation/stage_r/r1_baseline_profiling_v1/profiling_summary.json`，
SHA-256 `ff487acc…f9f5e7`）：

| 数据路径组件 | 均值 (ms) |
|---|---:|
| CPU source | 0.932768 |
| CPU preprocessing | 3.652910 |
| Synchronous host inference roundtrip | 3.762928 |
| TensorRT CUDA | 2.806861 |
| H2D | 0.690427 |
| D2H | 0.099916 |
| Host output construction | 0.034835 |
| Pre-sink total | 8.628215 |

在 8.63 ms 的 pre-sink 总耗时中，CPU 预处理（3.65 ms）与同步 Host 推理往返
（3.76 ms）合计约占 86%，而 TensorRT CUDA 仅占 2.81 ms。这支持以下动机：
INT8 计算被压低后，CPU 预处理与 Host 侧同步数据搬运构成该路径的主要开销，
值得以 CUDA 融合预处理与不同的 raw staging 机制进行实验验证。

> 限定：以上为 V0 路径实测观测，不构成对 V2/V3/V4 收益的预测；跨变体结论仅由
> §5 统一消融表提供。

## 2. 实验变体

| 变体 | 定义 |
|---|---|
| V0 | CPU/OpenCV preprocessing baseline（pageable FP32 HostTensor → TensorRT INT8） |
| V2 | pageable raw staging + CUDA fused preprocessing（device input） |
| V3 | V2 + long-lived pinned raw staging |
| V4 | V3 + limited double-buffer path（两个 pinned raw/device slot，固定交替） |

编号说明：V1 未进入最终消融矩阵。编号序列继承自 Stage R 执行计划
（V1 为计划中的中间增量，未实现为可测变体），主表中不存在 V1 行不构成缺失实验；
V2/V3/V4 是冻结的最终消融分支。机制编号与报告历史保持一致，不在本节重新编号。

## 3. 正确性评价

正确性轴为继承数据，不在消融采样中重算（R3 仅确认 detection SHA 等价）。

| 变体 | 正确性状态 |
|---|---|
| V0 | Stage Q correctness baseline（canonical detection SHA `12bdb792…513de2`） |
| V2 | Gate A / B / C PASS；Gate D FAIL（超出冻结限值，见下） |
| V3 / V4 | detection SHA 与 V2 完全一致（`0a668fd5…81f5ed`），因此继承 V2 task metrics |

精确数值（R2 remediated 结果，冻结）：

```text
mAP50 absolute drop:
    0.00537575
    约 0.54 个百分点

超出冻结 Gate D 限值（0.005）的数额:
    0.00037575
    约 0.038 个百分点

max class AP50 drop:
    0.02673348

max class Recall drop:
    0.03030303
```

Gate D 结论为 FAIL，冻结限值 0.005 未作任何修改。不得将上述数值表述为
「0.05% accuracy loss」「accuracy-neutral」或「Gate D PASS」。

## 4. 实验协议

统一协议（Attempt 2，`R3_ATTEMPT_2_UNIFIED_HARNESS`）：

- 统一 single-thread harness：单一 benchmark-only 可执行文件驱动全部四个变体，
  V0 经 `runtime::SerialRunner` 适配、V2/V3/V4 经各自 Stage R runner，同一
  单线程内联循环，同一 pre-sink 端到端计时边界；任何变体均不使用
  `PipelineRunner`。
- 同一 manifest：冻结的 `test_manifest_v2.json`（SHA-256
  `ea7616df…1b194`，180 张图）。
- 同一 Engine：Stage Q TensorRT INT8 engine。
- 同一 postprocess：Stage Q PostProcessor，Result JSON schema v4。
- 每变体 5 次独立运行，共 20 次，全部 PASS，drop count 均为 0。
- 每次运行 warmup 60 帧（discarding sink），实测 1080 帧（6 个固定 180 帧循环）。
- 确定性交错顺序（set01 V0,V2,V3,V4 | set02 V4,V3,V2,V0 | set03 V2,V0,V4,V3 |
  set04 V3,V4,V0,V2 | set05 V0,V3,V2,V4），配对差异在同一交错运行集上计算。
- Result JSON v4；每 run 生成独立的 manifest、hash 与 tegrastats 采样。
- CPU equivalent cores 定义：对每次运行的同区间 tegrastats 采样，逐行解析
  `CPU [n%@…]` 各核 busy 百分比并求和为等效核数，再对全程样本取均值
  （benchmark 工具逻辑，`tools/benchmark/run_stage_r_r3_ablation.py`）。
- 环境：Jetson Orin Nano Super，MAXN_SUPER mode 2，CPU affinity 0–5，
  OpenCV threads 1，batch=1，640×640，queue capacity 1 / block。

必须说明：

```text
Attempt 1 used different runner semantics and was excluded from
the formal ablation table.
```

Attempt 1 中 V0 经 `PipelineRunner`（四工作线程）调度，而 V2/V3/V4 走专用
单线程 runner，线程模型与预取行为不同，跨变体差异被混淆；因此 Attempt 1 分类为
`R3_ATTEMPT_1_NONCOMPARABLE_HARNESS`，仅保留为诊断与并发背景（§10）。

## 5. 消融结果主表

聚合均值（5 次交错运行；单位：FPS = frames/s，latency = ms，CPU cores 无量纲，
mAP50 Δ 为绝对值分数）。

| Variant | FPS | Mean latency | P95 | P99 | CPU cores | mAP50 Δ | 结论 |
|---|---:|---:|---:|---:|---:|---:|---|
| V0 | 54.865 | 18.168 | 18.830 | 19.004 | 0.841 | 0 | Correctness-first baseline |
| V2 | 126.120 | 7.870 | 9.935 | 11.552 | 0.756 | −0.00537575 | Best controlled trade-off |
| V3 | 127.005 | 7.807 | 9.894 | 11.220 | 0.837 | −0.00537575 | No meaningful increment |
| V4 | 26.746 | 32.278 | 22.675 | 22.907 | 1.001 | −0.00537575 | Negative ablation result |

增量表（同一交错运行集上的配对差异）：

| Comparison | FPS change | Mean latency change | P95 change | P99 change | CPU change |
|---|---:|---:|---:|---:|---:|
| V2 vs V0 | +71.255 (+129.87%) | −10.298 (−56.68%) | −8.895 | −7.452 | −0.084 |
| V3 vs V2 | +0.885 (+0.70%) | −0.064 (−0.81%) | −0.041 | −0.332 | +0.081 |
| V4 vs V3 | −100.259 (−78.94%) | +24.471 (+313.47%) | +12.781 | +11.686 | +0.163 |
| V4 vs V0 | −28.119 (−51.25%) | +14.110 (+77.66%) | +3.845 | +3.902 | +0.160 |

实现增量：V2 = CUDA fused preprocessing with pageable raw staging；V3 =
V2 + long-lived pinned raw staging；V4 = V3 + two-slot limited fixed
alternation；V4 vs V0 = 完整 V0→V4 数据路径增量。

在统一 harness 语义下：V2 吞吐约为 V0 的 2.3 倍（126.12 / 54.87 ≈ 2.30）；
pinned staging（V3）相对 pageable（V2）近似中性；双缓冲路径（V4）显著慢于
V0 与 V2/V3。每变体仅 5 次运行，以下差异均为观测差异，未作显著性检验。

## 6. V2 分析

```text
V2 is the best controlled performance-accuracy trade-off.
```

- FPS 约提升 129.9%（54.865 → 126.120）；
- mean latency 约降低 56.7%（18.168 → 7.870 ms）；
- CPU equivalent cores 未增加（V2 0.756 vs V0 0.841，配对差 −0.084；
  逐 set 差异符号在运行内波动内存在方向性，不作强断言）；
- 存在约 0.54 个百分点的 mAP50 下降（0.00537575），并超出冻结 Gate D 限值
  0.00037575（约 0.038 个百分点）；
- 该结论限定在统一单线程消融协议内，不是对现有完整 PipelineRunner 的
  直接生产替换结论（见 §10、§12）。

## 7. V3 分析

结论限定为：

```text
在当前 batch=1、640×640、统一单线程 Jetson 路径下，
Pinned Raw Staging 未表现出具有实际意义的增量收益。
```

- FPS 约 +0.7%（+0.885）；
- mean latency 约 −0.8%（−0.064 ms）；
- P95 变化很小（−0.041 ms）；P99 配对差 −0.332 ms；
- CPU equivalent cores 反而增加（+0.081，0.756 → 0.837）；
- 五组配对结果存在符号翻转：FPS per-set 差异
  （+3.08, −1.31, +0.38, +1.94, +0.33）与 CPU cores per-set 差异
  （+0.571, −0.225, +0.088, −0.009, −0.020）均跨零翻转，增量效应小于
  运行级波动。

不得推广为「Pinned Memory 在 Jetson 上无效」；该结论仅覆盖所测
batch-1、640×640、单线程路径与长期 pinned raw staging 机制。

## 8. V4 分析

保留完整负结果（DOMINATED_NEGATIVE_ABLATION_RESULT）：

- FPS 下降：相对 V3 −78.94%（−100.259），相对 V0 −51.25%（−28.119）；
- mean latency 增加：相对 V3 +313.47%（+24.471 ms），相对 V0 +77.66%
  （+14.110 ms）；
- 每次正式运行均存在约 8.98–10.24 秒的单帧长尾（per-run latency_max：
  10236.582、8976.955、9173.937、8991.817、9241.866 ms；中位约 22.1 ms）；
- 正式运行集内发生一次 OOM kill（return code −9，记录于
  `failure.json`），按冻结规则重跑一次后 PASS；
- precision/detection 未改变：detection SHA 与 V2/V3 完全一致，非精度问题；
- 当前同步模型下没有观察到有效收益。

长尾异常值按实保留在主统计中（mean 32.278 ms、latency_max 9324.231 ms），
未删除、未截断、未标记无效。P95（22.675 ms）/P99（22.907 ms）看似稳定但会
掩盖极端长尾，报告时必须并列 latency_max 与 latency_stddev（约 275–313 ms/run）。
本节不推测超出证据的具体根因；已记录的范围是：被评估的受限双缓冲实现引入严重
尾部延迟与稳定性代价，在测试同步模型下未提供可测性能收益。

## 9. Pareto 结论

双点结论，不存在单一「整体最优」：

```text
V0:  correctness-first deployment point
V2:  performance-first research trade-off point
```

- V0：通过冻结正确性契约，Stage Q Evidence 完整，为正式部署基线。
- V2：统一单线程条件下观测收益最大，CPU 占用未增加（观测方向），精度代价
  明确且可复现，工程复杂度低于 V3/V4；但未满足 correctness-equivalent
  replacement 门槛。
- V3、V4 不进入 Pareto 前沿：V3 增量收益相对新增机制不足；V4 被 V2/V3
  支配且受严重尾部不稳定性影响。

## 10. PipelineRunner 背景

```text
Attempt 1 中 PipelineRunner V0 约 231.9 FPS，
说明并行执行框架可以显著提高系统吞吐，
但由于其 runner 和线程模型与统一消融实验不同，
该数值不参与 V0/V2/V3/V4 横向比较。
```

该数值被明确分类为 `CONTEXT ONLY`，且与统一单线程消融
`NOT COMPARABLE`。同一 V0 数据路径在统一单线程 harness 下测得 54.9 FPS，
与 Attempt 1 的 231.9 FPS 之差主要由 pipeline 拓扑（四工作线程 + 预取）解释
（约 4.2×），该拓扑因素不属于数据路径消融的变量。论文中不得将 231.9 FPS 与
V2 的 126.1 FPS 直接比较并得出部署优劣。

## 11. 论文贡献总结

三项克制的贡献：

1. **INT8 后数据路径瓶颈定位**：在统一单线程协议下量化 CPU 预处理与 Host 侧
   同步搬运相对 TensorRT 计算的主导性（V0 路径 pre-sink 组成，§1），以及
   CUDA 融合预处理带来的吞吐/延迟变化。
2. **CUDA 融合预处理的性能—精度 Trade-off 验证**：V2 相对 V0 约 +129.9% 吞吐、
   −56.7% 平均延迟、CPU 占用未增加，同时量化约 0.54 个百分点的 mAP50 代价；
   明确未达到 correctness-equivalent 替换门槛。
3. **Pinned Memory 与 Double Buffer 的增量消融与负结果分析**：V3 增量收益
   小于运行级波动；V4 双缓冲路径出现 8.98–10.24 秒级长尾与 OOM 事件，观测为
   负结果；均保留原始数据，未删除异常值。

本节不声称提出了新的检测算法；检测模型（YOLOv8n INT8）与任务指标继承自
Stage Q。

## 12. Limitations

- 单设备：Jetson Orin Nano Super（MAXN_SUPER mode 2）；
- 单模型：YOLOv8n TensorRT INT8；
- 单输入尺寸：640×640；
- batch=1；
- 统一单线程消融不能代表完整 PipelineRunner 部署吞吐（§10）；
- V2 未满足 correctness-equivalent replacement 门槛（Gate D FAIL，
  超出限值 0.00037575）；
- V4 未进一步定位长尾根因（超出已测同步模型的根因未建立）；
- V5（以及 zero-copy）未实施；
- 每变体 5 次运行，差异为观测差异，未作显著性检验；
- 精度轴为继承数据：V3/V4 通过 identical detection SHA 继承 V2 task metrics，
  未在任务级独立测量 pinned staging 与 double buffering 的增量精度效应。

---

## 答辩表述

Stage R 是在 INT8 量化已把 TensorRT 计算成本压低之后，验证 CPU 预处理与
Host 侧数据搬运是否成为新的系统开销，并回答「是否值得用 CUDA 融合预处理与
不同 raw staging 机制替换现有数据路径」。统一单线程消融显示 V2 在约 0.54 个
百分点的 mAP50 代价内把吞吐提升约 129.9%、平均延迟降低约 56.7%，这验证了
该方向存在真实但需要精度折衷的性能空间；V3 的 pinned staging 增量小于运行级
波动、V4 双缓冲出现秒级长尾与 OOM 风险，故未继续沿这两条分支投入，避免在
没有可测收益的方向上增加复杂度。最终选择是双点策略：部署侧保留通过完整正确性
契约的 V0，研究侧把 V2 作为性能-精度权衡点；两值均未声称与多线程 PipelineRunner
部署吞吐可直接比较。

## 简历表述

```text
在 Jetson Orin Nano 上完成 TensorRT INT8 数据路径消融，实现 CUDA 融合
预处理、Pinned Memory 与双缓冲路径；在统一单线程实验中，CUDA 预处理相对
CPU 基线将吞吐量提升约 129.9%、平均延迟降低约 56.7%，并量化约 0.54 个
百分点 mAP50 代价；通过消融确认 Pinned 增益有限及双缓冲长尾风险。
（限定：batch=1、640×640、统一单线程消融协议，不代表多线程 PipelineRunner
部署吞吐；V2 未满足 correctness-equivalent 替换门槛。）
```

---

## 附录：数据溯源

本节数字的来源文件及其 SHA-256：

| 用途 | 路径 | SHA-256 |
|---|---|---|
| 聚合指标 | `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/aggregate_metrics.json` | `5f0c1148…cb3` |
| 配对差异 | `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/comparison_matrix.json` | `ac72fa48…e53c` |
| 性能-精度矩阵 | `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/performance_accuracy_tradeoff.json` | `0e047c03…0b6e` |
| 逐 run 指标 | `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/per_run_metrics.json` | `a2cc1c59…0bc8` |
| 协议/环境 | `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/experiment_manifest.json` | `c4d3b997…0ec3` |
| OOM 记录 | `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/failure.json` | `a63cc226…e68e0d` |
| Pareto 汇总 | `results/validation/stage_r/r5_pareto_closeout_v1/stage_r_pareto_summary.json` | `ba95aa09…fc38` |
| 最终状态 | `results/validation/stage_r/r5_pareto_closeout_v1/stage_r_final_status.json` | `c8be41bc…573a29b` |
| R1 剖析 | `results/validation/stage_r/r1_baseline_profiling_v1/profiling_summary.json` | `ff487acc…f9f5e7` |

机器可读表格（由上述 JSON 直接生成，数值零手工录入）：

```text
results/paper/stage_r/stage_r_ablation_table.csv
results/paper/stage_r/stage_r_incremental_comparison.csv
results/paper/stage_r/stage_r_accuracy_tradeoff.csv
results/paper/stage_r/stage_r_fps_latency_plot.csv
results/paper/stage_r/stage_r_pareto_plot.csv
results/paper/stage_r/stage_r_tail_latency_plot.csv
results/paper/stage_r/metadata.json
```

Attempt 1 证据（`r3_v0_v2_v3_v4_ablation_v1/`）为
`R3_ATTEMPT_1_NONCOMPARABLE_HARNESS`，本节任何横向数值均不来自该目录。
