# Paper Phase 2 Article Outline v1.0

## 1. Status

This is the formal candidate outline for one engineering application article.
It specifies questions and evidence placement; it is not article prose.

## 2. Candidate Directory

```text
0 引言

1 系统对象与问题定义
  1.1 工业缺陷检测部署对象
  1.2 INT8推理数据路径
  1.3 研究问题与统一计时边界

2 数据路径优化方法
  2.1 CPU预处理基线路径
  2.2 CUDA预处理路径
  2.3 Pinned内存数据路径
  2.4 正确性约束与资源生命周期

3 实验设计
  3.1 实验平台与模型配置
  3.2 数据集与统一运行协议
  3.3 正确性和性能指标

4 结果与分析
  4.1 正确性验证结果
  4.2 CUDA预处理的主要性能收益
  4.3 Pinned内存的增量收益
  4.4 尾延迟与适用范围讨论

5 结论
```

## 3. Section Contracts

### 0 引言

- Define the industrial edge-inference problem and distinguish model accuracy
  from deployment data-path cost.
- Review literature needs L1-L9, emphasizing work from 2024-2026 and relevant
  papers from the target journal.
- Identify the gap as a controlled comparison of preprocessing/staging paths
  under one correctness and timing contract.
- End with one central question and exactly two contributions.
- Do not present result tables or a stage chronology.

Claims: `C1-C4`, with limitations from `C8-C9`.

### 1 系统对象与问题定义

#### 1.1 工业缺陷检测部署对象

- Describe the frozen YOLOv8n/NEU-DET/Jetson deployment object.
- Disclose historical split-v1 and current split-v2, the unchanged test set,
  and the engineering checkpoint-selection rule.
- Keep training and ONNX export as supporting provenance.

Claims: `C8`.

#### 1.2 INT8推理数据路径

- Establish Stage Q INT8 PTQ as a prerequisite, keeping its task accuracy and
  performance observations separate.
- Define host raw staging, H2D, preprocessing, TensorRT inference, D2H, and
  postprocessing.
- Briefly position ORT CPU, TensorRT FP16, and Pipeline as background without a
  cross-protocol number chain.

Claims: `C4`; background handling of `C5-C7`.

#### 1.3 研究问题与统一计时边界

- State the central question and the V0/V2R/V3R controlled factors.
- Define interval start/end, included/excluded operations, lifecycle, and run
  counts.
- Introduce Figure 1.

Claims: `C1`, `C9`.

### 2 数据路径优化方法

#### 2.1 CPU预处理基线路径

- Define V0: source/decode, CPU/OpenCV preprocessing, host-input TensorRT path,
  and common postprocessing.
- Treat V0 as the comparison baseline, not as a separate paper result family.

#### 2.2 CUDA预处理路径

- Define V2R: pageable raw staging and correctness-aligned CUDA preprocessing.
- State the frozen task-level Gate D contract and backend-neutral interface
  boundary.
- Avoid claiming a new preprocessing algorithm.

#### 2.3 Pinned内存数据路径

- Define V3R as pinned raw staging with the same CUDA preprocessing semantic as
  V2R.
- Make the isolated factor explicit: staging memory type.
- State that this path does not imply cross-frame overlap.

#### 2.4 正确性约束与资源生命周期

- Describe frame order, geometry, result schema, zero-drop, EOS, worker join,
  tensor/detection digest, and resource ownership.
- Separate task-level Gate D for V2R from V3R identity evidence.
- Keep V4 outside the formal method and result set.

Claims for Section 2: `C1-C3`, guardrail `C9`.

### 3 实验设计

#### 3.1 实验平台与模型配置

- Use Table 1 for Jetson, L4T/CUDA/TensorRT/OpenCV, model/Engine, input, batch,
  thresholds, and power mode.
- Use only recorded environment facts; do not infer clock or resource state.

#### 3.2 数据集与统一运行协议

- Describe the 180-image split-v2 test replay, six cycles, warmup/measured
  counts, five processes per variant, and interleaved schedule.
- Disclose the split history without turning it into a result subsection.

#### 3.3 正确性和性能指标

- Correctness: precision, recall, mAP50, mAP50-95, lifecycle, and digest
  identity.
- Performance: FPS mean and frozen sample SD; pooled mean/P95/P99 latency.
- Define ratio, increase, and reduction formulas only where Phase 1 already
  froze the derived result.
- No new hypothesis test, confidence interval, or metric fusion.

Claims for Section 3: evidence contracts for `C1-C4` and `C8`.

### 4 结果与分析

#### 4.1 正确性验证结果

- Use Table 2 for V2R task metrics, zero deltas against V0, Gate D pass, and
  V3R identity/lifecycle evidence.
- Keep INT8/FP16 Stage Q accuracy as prerequisite context, not a second result
  track.

Claims: `C2`, supporting `C4`.

#### 4.2 CUDA预处理的主要性能收益

- Use Figure 2 for V0/V2R/V3R FPS mean with frozen FPS SD.
- Use Figure 3 for mean/P95/P99 latency.
- Interpret V2R versus V0 under the shared boundary and state conditions.

Claims: `C1`, `C2`.

#### 4.3 Pinned内存的增量收益

- Compare V3R only with V2R to isolate staging memory.
- Report the frozen incremental FPS and mean-latency effects.
- Characterize the benefit as limited and workload-bound.

Claims: `C3`.

#### 4.4 尾延迟与适用范围讨论

- Interpret P95 and P99 separately; the V3R result is mixed.
- Discuss offline replay, single platform/model/input/batch, missing
  power/resource/endurance evidence, and identity-inheritance limitations.
- Reinforce the exclusion of Attempt 2/V4 and cross-protocol arithmetic.

Claims: `C3`, `C8`, `C9`.

### 5 结论

- Answer the central question in the same order as the two contributions.
- State V2R's main observed benefit and V3R's limited average increment with
  mixed tail behavior.
- Restate tested conditions and limitations without introducing a new result,
  recommendation, or contribution.
- Do not simply repeat all numeric results.

Claims: `C1-C3`; guardrail `C9`.

## 4. Structural Exclusions

- Do not organize the article as J -> K -> P -> Q -> R.
- Do not create separate main-results chapters for ORT CPU, TensorRT FP16, or
  Pipeline.
- Do not add a third A-level contribution.
- Do not include V4 in a formal method, result, Pareto, abstract, or conclusion
  claim.
- Do not turn writing preparation into a thesis outline or a completed article.
