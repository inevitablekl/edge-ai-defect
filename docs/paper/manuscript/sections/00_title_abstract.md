<!-- MANUSCRIPT_SECTION: FRONT_MATTER; TITLE_ABSTRACT -->

# 题名与摘要

## 中文题名

Jetson端工业缺陷检测的输入数据路径重构

## 中文摘要

在边缘工业缺陷检测中，低精度部署可以降低网络侧开销，但即使推理对象已经固定，输入数据路径仍不能由此唯一确定，输入形成及主机—设备数据移动开销也不会自动消除。为明确固定推理对象之外仍待评价的系统关系，本文将输入数据路径作为独立结构对象，研究不同范围的路径干预如何对应完整端到端响应。方法上，以跨边界表示、输入张量形成位置、额外打包原始图像暂存策略和执行拓扑描述路径，通过路径级重构与单变量暂存细化形成层级受控比较，并以任务正确性保持作为性能比较准入条件，分别评价完整端到端均值与尾部响应。冻结180幅图像的离线回放结果表明，三条路径的任务级指标一致；路径级重构使FPS达到2.24×、平均端到端延迟降低55.45%，其后的暂存策略细化仅带来约4%的平均改善，且未形成一致的P95/P99改善。因而，在本文受测平台与配置内，路径级结构决策应先与局部暂存策略分离，平均响应也不能替代尾部响应评价。

## 中文关键词

Jetson；工业缺陷检测；输入数据路径；端到端推理；受控比较

## English Title

Input Data-Path Reconstruction for Industrial Defect Detection on Jetson

## English Abstract

In edge-based industrial defect detection, low-precision deployment can reduce network-side cost; even after the inference object is fixed, however, the input data path is not uniquely determined, and input-formation and host-device data-movement costs are not automatically eliminated. To make the remaining system relation explicit, this study treats the input data path under a fixed inference object as a separate structural evaluation object and examines how interventions of different scopes correspond to complete end-to-end responses. A path is described by the representation crossing the host-device boundary, the location where the input tensor is formed, the policy for additional packed raw-image host staging, and the execution topology. Hierarchical controlled comparisons separate path-level reconstruction from single-variable staging refinement; performance comparison is admitted only when task correctness is preserved, and mean and tail responses are evaluated separately. Offline replay of the frozen 180-image workload yields identical task-level metrics across all three paths. The path-level reconstruction reaches 2.24× FPS and reduces mean end-to-end latency by 55.45%; the subsequent staging-policy refinement provides an approximately 4% mean improvement but no consistent P95/P99 improvement. Within the tested platform and configuration, path-level structural decisions should therefore be separated from local staging policies, and mean response should not substitute for tail-response evaluation.

## English Keywords

Jetson; industrial defect detection; input data path; end-to-end inference; controlled comparison
