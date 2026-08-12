<!-- MANUSCRIPT_SECTION: 5; CONCLUSION -->

# 5 结论

本文面向Jetson端YOLOv8n TensorRT INT8混合精度部署，重构了输入形成与host-device数据路径：由CPU/OpenCV在主机侧形成FP32 NCHW张量并复制至设备，转为packed raw-image staging、`cudaMemcpy2DAsync`和融合CUDA预处理直接形成TensorRT设备输入。在冻结180幅测试集上保持任务级评价一致的条件下，V2R相对V0达到2.24× FPS，平均latency降低55.45%，表明完整输入形成路径重构构成本文受测配置中的主要E2E性能增量。

在GPU preprocessing、TensorRT stream、Engine和下游拓扑不变时，V3R只将pageable staging替换为pinned staging。其相对V2R的FPS变化为+4.07%，平均latency变化为−4.03%；该平均优势在5次独立进程的描述性分布中可见，并非由单一process独自产生。P95为+0.15%、P99为−0.12%，两项变化均低于0.2%且方向相反，tail behavior因此保持MIXED。当前证据只支持固定实现中的有限平均增量，不支持普适的pinned-memory收益或一致尾延迟改善。

上述结论限定于单一Jetson平台、detector/Engine、数据集和离线回放工作负载，且没有连续runtime telemetry、功耗测量、独立时钟频率记录或stage-level causal timing。后续工作可在保持统一正确性与计时边界的前提下，补充真实相机和长期运行评价，测量H2D、GPU preprocessing与实际内存流量，并在其他模型和边缘平台上检验数据路径重构的适用范围。
