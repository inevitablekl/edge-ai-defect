<!-- MANUSCRIPT_SECTION: 4; TABLE: T3; FIGURES: F3,F4 -->

# 4 结果与分析

## 4.1 正确性

表3保留V0/V2R正式任务正确性验收记录。在冻结的180幅测试集和统一evaluator下，两条路径的precision、recall、mAP50和mAP50-95分别为0.6913、0.6991、0.6476和0.3523，总体指标差异为0；类别级最大AP50和recall差异也均为0。

**表3　V0与V2R任务级正确性验证结果**

| 指标 | V0 | V2R | 绝对差异 | 允许差异 | 结果 |
|---|---:|---:|---:|---:|---|
| Precision | 0.6913 | 0.6913 | 0 | 0.010 | 通过 |
| Recall | 0.6991 | 0.6991 | 0 | 0.010 | 通过 |
| mAP50 | 0.6476 | 0.6476 | 0 | 0.005 | 通过 |
| mAP50-95 | 0.3523 | 0.3523 | 0 | 0.005 | 通过 |

V3R冻结predictions经同一评价协议得到precision 0.6913、recall 0.6991、mAP50 0.6476和mAP50-95 0.3523；相对V0和V2R的类别级最大AP50与recall差异均为0。由此，V0、V2R和V3R在该冻结工作负载上获得一致的任务级评价结果，说明本轮输入数据路径重构未改变该测试集上的检测评价。V3R结果来自冻结predictions的确定性分析，而非新的inference或第二次参数选择；上述一致性不扩展为数学等价、bitwise identity或未来输入上的普适结论。

## 4.2 整体E2E性能

V0→V2R形成主要E2E性能增量，而V2R→V3R仅进一步改善平均性能。V0的平均FPS为54.600，平均latency为18.273 ms；V2R分别为122.122 FPS和8.140 ms。V2R相对V0达到2.24× FPS，平均latency降低55.45%。

V3R的平均FPS为127.097，平均latency为7.812 ms。相对V2R，其FPS变化为+4.07%，平均latency变化为−4.03%。两级结果表明，主要平均性能变化对应从host-side FP32 tensor formation到raw-image H2D与GPU-side input formation的完整重构；pageable→pinned暂存是在该路径基础上的有限边际增量。

图3给出三条路径的平均FPS，误差棒为5次独立进程级FPS的样本标准差。V0、V2R和V3R的样本标准差分别为0.223、0.492和1.279 FPS。

**图3　V0、V2R和V3R平均帧率比较。误差棒表示5次独立进程级运行FPS的样本标准差。**

图4给出各路径的mean、P95和P99绝对latency以及V3R相对V2R的冻结变化；尾延迟方向在第4.4节单独解释。

**图4　V0、V2R和V3R平均及尾延迟比较。（a）各路径绝对延迟；（b）V3R相对V2R的冻结变化，其中负值表示降低/更快，正值表示升高/更慢。Mean、P95和P99均基于每种路径合并后的5400个逐帧延迟样本统计。**

## 4.3 数据路径分析

输入representation的变化可以用名义输入复制载荷（nominal input-copy payload）描述。V0在主机端形成`1×3×640×640`的FP32 NCHW张量后复制至设备，其名义载荷为

`1 × 3 × 640 × 640 × 4 = 4,915,200 B = 4.9152 MB/frame`。

V2R/V3R在冻结工作负载中复制200×200 packed BGR `uint8`图像，`cudaMemcpy2DAsync`的有效copy width为600 B、height为200，名义载荷为

`600 B × 200 = 120,000 B = 0.1200 MB/frame`。

两类路径的名义输入复制载荷比为40.96×。该确定性差异来自冻结图像几何和实现复制语义，表明输入形成位置与H2D representation发生了实质变化；它不等同于实际内存总线流量、带宽改善、H2D时间降低或40.96×传输加速，也不能单独解释测得的2.24× E2E FPS比。E2E结果仍是包含全部计时边界阶段的完整路径观察。

## 4.4 运行级稳定性与尾延迟

5次独立进程的描述性分布支持V3R平均性能优势具有运行级重复性，而不是由单一异常process独自产生。V2R的process-level FPS范围为121.443–122.759，V3R为125.595–128.301；对应的process mean latency范围分别为8.098–8.185 ms和7.740–7.894 ms。两个范围在本次5-run样本中没有重叠，但不同路径的进程不按运行次序建立逐次对应关系，本文也不据此进行显著性推断。

尾延迟没有形成相同方向。V2R的pooled P95和P99分别为9.827和11.529 ms，V3R分别为9.842和11.515 ms。V3R相对V2R的P95为+0.15%（略慢），P99为−0.12%（略快）。两项相对变化均低于0.2%且方向相反，因此tail verdict保持为MIXED，现有证据不支持一致的tail-latency改善。平均性能优势与尾部变化应分别解读，不把pinned staging描述为稳定降低尾延迟的机制。

## 4.5 相关工作定位

表面缺陷研究通常以检测器结构和任务精度为中心，而边缘部署研究还涉及框架、预处理、内存管理和完整流水线 [@shao_et_al_2024_td_net; @stacker_et_al_2021_edge_runtime; @lee_han_kim_2025_presto; @shin_kim_2022_jetson_yolo_frameworks]。本文与这些工作的区别在于固定YOLOv8n和同一TensorRT INT8混合精度Engine，把host-side FP32 tensor formation、GPU-side fused preprocessing和pageable/pinned raw-image staging组织成两级隔离比较，并同时报告统一工作负载下的任务正确性、E2E latency、process-level FPS和pooled tail behavior。

这一定位不表示GPU preprocessing或pinned memory从未被研究，也不以不同论文之间的FPS绝对值建立优劣结论。本文提供的是固定detector/Engine条件下的输入数据路径工程证据：V0→V2R用于观察完整输入形成重构，V2R→V3R用于观察主机暂存分配类型的边际变化。后续相关工作表应区分“未报告”与“未使用”，避免将文献没有给出的实现信息推断为否定事实。

## 4.6 局限性

本文证据来自单一Jetson Orin Nano Super、单一YOLOv8n TensorRT INT8混合精度Engine、单一NEU-DET数据集及固定180幅图像工作负载。输入采用离线文件回放，未覆盖真实相机、长期在线流或跨平台/跨模型泛化。运行状态只有非连续的前后温度观察；没有连续runtime telemetry、独立归档的时钟频率、功耗测量或稳定电源状态证据。

实验也没有stage-level causal timing decomposition。40.96×名义输入复制载荷由实现和冻结几何确定，但H2D time、preprocessing stage time、实际bus traffic与总DRAM traffic均未测量。因此，完整E2E差异不能分配为单个kernel、复制或像素操作的独立因果贡献。最后，5次独立进程只用于描述运行级分布，本文没有置信区间、假设检验或统计显著性推断。
