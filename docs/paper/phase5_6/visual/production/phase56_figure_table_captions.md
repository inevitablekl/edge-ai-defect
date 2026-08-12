# Phase 5.6 Figure and Table Caption Freeze

Scope: caption text frozen for later Phase 5.6E integration. This file does not modify or integrate the manuscript.

## Figures

### F1

**V0、V2R和V3R受控数据路径及完整路径观测。** V0在主机侧形成FP32 NCHW输入张量，V2R/V3R将打包原始图像复制到设备并在GPU侧形成TensorRT输入；V3R仅将V2R的pageable暂存替换为pinned暂存。性能数字表示完整端到端路径比较，不归因于单一组件。输入复制载荷为名义值，不等同于实测总线流量。

### F2

**V2R/V3R的主机—设备内存域、缓冲区生命周期与单流执行语义。** 两条路径仅在主机侧pageable/pinned暂存类型上不同；`cudaMemcpy2DAsync`、融合CUDA预处理、`enqueueV3`及输出D2H沿同一TensorRT CUDA stream顺序执行，暂存区、设备原始图像缓冲区和后端输入缓冲区跨帧复用。图中不表示跨帧重叠或流水线。

### F3

**三条受控路径的端到端性能。** (a) 柱高为每条路径5个独立进程FPS的均值，误差棒为5个进程级FPS值的样本标准差；(b) 为每条路径合并5400个延迟样本得到的平均端到端延迟；(c) 为相同5400个pooled延迟样本的P95和P99。比较值描述完整路径差异，不构成对单一组件的因果归因。

### F4

**运行级分布与尾延迟。** (a) 展示每条路径5个独立进程的FPS及描述性均值与样本标准差；(b) 展示V2R/V3R各进程的平均、P95和P99延迟。各点为独立进程级描述量，横向偏移仅用于区分且不表示配对。正式pooled P95/P99仍为Level-A aggregate metrics，来自每路径5400个延迟样本；P95变化+0.15%、P99变化−0.12%，方向相反，判定为MIXED。

## Tables

### T1

**V0、V2R和V3R受控数据路径的特征矩阵。** 三条路径使用相同detector和TensorRT Engine；V0在主机侧形成FP32输入张量，V2R/V3R在设备侧形成输入张量，且后两者仅在pageable与pinned原始图像暂存类型上不同。三条路径均为单帧顺序执行，无跨帧流水线。

### T2

**平台、模型与统一基准协议。** 三条路径在相同Jetson平台、YOLOv8n、冻结TensorRT INT8混合精度Engine、固定测试工作负载和统一预热/测量协议下执行；表内仅保留复现实验所需的紧凑条件。

### T3

**V0、V2R和V3R的任务级正确性。** Precision、Recall、mAP50和mAP50-95均由冻结预测证据按统一评估口径获得；各路径的汇总指标一致，类别级AP50与Recall的最大路径间差异均为0。

### T4

**相关工作的研究属性定性比较。** 表中汇总所审阅工作明确报告的研究属性；“明确否”仅用于原文明确排除的情形，“未报告”不等同于“否”。该比较用于定性定位，不表示优越性、首次性或唯一性。
