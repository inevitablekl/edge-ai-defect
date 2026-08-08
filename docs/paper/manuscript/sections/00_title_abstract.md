<!--
STATUS: STRUCTURE_ONLY
NO_MANUSCRIPT_PROSE
PHASE_3_NOT_AUTHORIZED
WRITING_PACKET: WP_TITLE_ABSTRACT
CLAIMS: C1;C2;C3;C4;C8;C9
FIGURES_TABLES: NONE
-->

# 题名与摘要

## 中文题名

Jetson端工业缺陷检测的INT8推理数据路径优化

## 中文摘要

针对Jetson端工业缺陷检测INT8推理中不同数据路径配置的完整部署性能差异，在固定YOLOv8n模型、TensorRT INT8 Engine、640×640输入、batch size为1、测试工作负载、正确性判据和计时边界的条件下，构建CPU/OpenCV预处理基线路径V0、由可分页主机内存暂存与CUDA预处理组成的V2R，以及由锁页主机内存暂存与相同CUDA预处理语义组成的V3R。每种路径执行5次独立进程，帧率基于5个进程级FPS样本统计，平均延迟及P95、P99则基于5次运行合并得到的5400个逐帧延迟样本统计。结果表明，在V2R满足既定任务级正确性判据的前提下，其相对于V0的帧率比达到2.236671×，平均延迟降低55.4519%，主要观测性能收益集中于V2R完整受测路径。V3R相对于V2R的帧率进一步提高4.0738%，平均延迟降低4.0349%，但P95增加0.1514%，P99降低0.1184%，两个尾延迟指标变化方向不一致。因此，在本文固定Jetson Orin Nano Super平台和离线文件回放工作负载下，现有证据支持上述完整数据路径配置之间的性能差异：V2R承担主要观测性能收益，V3R在保持相同CUDA预处理语义的条件下仅表现出有限的平均性能增量，不能据此得到一致改善尾延迟的结论。

## 中文关键词

Jetson；工业缺陷检测；INT8推理；CUDA预处理；数据路径优化

## English Title

Data-Path Optimization for INT8 Inference in Jetson-Based Industrial Defect Detection

## English Abstract

To evaluate how complete data-path configurations differ in deployment performance for INT8 inference in Jetson-based industrial defect detection, three controlled configurations were constructed under a fixed YOLOv8n model, TensorRT INT8 Engine, 640×640 input, batch size of 1, test workload, correctness criteria, and timing boundary: V0 with CPU/OpenCV preprocessing, V2R with pageable host-memory staging and CUDA preprocessing, and V3R with pinned host-memory staging and the same CUDA preprocessing semantics. Each configuration was evaluated in five independent process-level runs. FPS was summarized from the five process-level FPS samples, whereas mean latency, P95, and P99 were computed from 5,400 pooled per-frame latency samples across those runs. V2R satisfied the predefined task-level correctness criteria. Relative to V0, its FPS was 2.236671× that of V0 and its mean latency decreased by 55.4519%, with the primary observed performance gain corresponding to the complete V2R configuration as tested. Relative to V2R, V3R further increased FPS by 4.0738% and reduced mean latency by 4.0349%; however, P95 increased by 0.1514%, whereas P99 decreased by 0.1184%, indicating opposite directions in the two tail-latency metrics. Therefore, under the fixed Jetson Orin Nano Super platform and offline file-replay workload used in this study, the evidence supports performance differences among the evaluated complete data-path configurations: V2R exhibits the primary observed performance gain, whereas V3R provides only a limited improvement in average performance under the same CUDA preprocessing semantics and does not support a conclusion of consistent tail-latency improvement.

## English Keywords

Jetson; industrial defect detection; INT8 inference; CUDA preprocessing; data-path optimization
