<!-- MANUSCRIPT_SECTION: FRONT_MATTER; TITLE_ABSTRACT -->

# 题名与摘要

## 中文题名

面向Jetson端TensorRT INT8工业缺陷检测的输入数据路径重构

## 中文摘要

针对Jetson端工业缺陷检测中网络低精度化不能直接消除输入形成与主机—设备数据移动开销的问题，本文在固定YOLOv8n和TensorRT INT8混合精度Engine的条件下，将CPU/OpenCV侧形成FP32 NCHW张量并复制至设备的基线路径，重构为packed BGR原始图像暂存、二维主机到设备复制以及GPU侧融合CUDA预处理直接形成TensorRT设备输入的路径。在统一的任务正确性、逐帧E2E延迟、进程级FPS和合并样本P95/P99评价口径下，实验通过V0→V2R与V2R→V3R两级受控比较，分别考察完整输入形成路径重构和pageable→pinned主机暂存变化。三条路径在冻结的180幅测试集上获得一致的任务级指标。V2R相对V0达到2.24× FPS，平均延迟降低55.45%，构成主要E2E性能增量；V3R相对V2R的FPS变化为+4.07%，平均延迟变化为−4.03%，P95变化为+0.15%、P99变化为−0.12%，两个尾延迟指标变化均低于0.2%且方向相反。结果表明，在本文固定Jetson平台、实现和离线回放工作负载下，完整输入形成与数据移动路径重构带来主要平均性能收益，pinned暂存只提供有限的平均增量，尚无一致的尾延迟改善证据。

## 中文关键词

Jetson；工业缺陷检测；INT8混合精度推理；CUDA预处理；主机—设备数据路径

## English Title

Input Data-Path Reconstruction for TensorRT INT8 Industrial Defect Detection on Jetson

## English Abstract

For Jetson-based industrial defect detection, reducing network precision does not by itself remove the costs of input formation and host-device data movement. With a fixed YOLOv8n detector and TensorRT INT8 mixed-precision Engine, this study restructures a baseline path that forms an FP32 NCHW tensor through CPU/OpenCV and copies it to the device into a path based on packed BGR raw-image staging, two-dimensional host-to-device copying, and fused CUDA preprocessing that directly forms the TensorRT device input. A unified protocol evaluates task correctness, source-to-pre-sink per-frame latency, process-level FPS, and pooled P95/P99 through two controlled comparisons: V0→V2R for the complete input-formation restructuring and V2R→V3R for pageable-to-pinned host staging. All three paths produce identical task-level metrics on the frozen 180-image test set. Relative to V0, V2R achieves 2.24× FPS and 55.45% lower mean latency, representing the principal end-to-end performance gain. Relative to V2R, the V3R changes are +4.07% in FPS and −4.03% in mean latency; the P95 and P99 changes are +0.15% and −0.12%, respectively, with both tail changes below 0.2% and in opposite directions. Under the fixed Jetson platform, implementation, and offline replay workload evaluated here, the complete input-formation and data-movement restructuring provides the main average-performance gain, whereas pinned staging adds only a limited mean improvement and does not provide evidence of consistent tail-latency improvement.

## English Keywords

Jetson; industrial defect detection; INT8 mixed-precision inference; CUDA preprocessing; host-device data path
