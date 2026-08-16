<!-- MANUSCRIPT_SECTION: 1; FIGURES: F1,F2 -->

# 1 系统对象与问题定义

## 1.1 模型、数据集与部署环境

本文研究部署于NVIDIA Jetson Orin Nano Super的YOLOv8n工业缺陷检测模型，输入为640×640、batch size为1。数据采用NEU-DET目标检测标注及去重后的split-v2，固定测试工作负载为180幅图像。TensorRT Engine使用排除测试集的1260幅去重训练图像校准，采用`IInt8EntropyCalibrator2`、batch size 1和与生产CPU `Preprocessor`一致的BGR letterbox、RGB/NCHW及FP32/255预处理；构建启用INT8与FP16并保持FP32 I/O，本文称其为TensorRT INT8混合精度Engine。量化部署需同时检验任务性能 [@kim_lee_kim_2024_hyq]，三条路径共用该Engine，软件版本见表2。

## 1.2 E2E数据路径与受控变量

完整路径包括图像获取与解码、主机暂存、输入形成、必要的数据移动、推理与同步、后处理和结果构造，Jetson检测部署也通常区分预处理、推理和后处理 [@tang_qian_2024_yolov8_jetson_orin]。统一计时边界内的E2E耗时表示为

\[
T_{\mathrm{E2E}}
=
\sum_{k=1}^{m}T_k .
\]

该式定义完整计时边界，而非仅指TensorRT网络推理；各阶段未独立插桩，因此不用于阶段级归因。

V0复制主机侧640×640 FP32 RGB/NCHW输入；V2R/V3R则复制packed BGR原始图像，并在设备侧融合完成输入形成。两条GPU路径使用相同CUDA预处理、CUDA stream和下游拓扑，唯一差异是pageable或pinned主机暂存。锁页内存的效果取决于平台、工作负载和访问特征 [@nvidia_cuda_best_practices_12_6; @bateni_et_al_2020_integrated_memory; @rodriguez_et_al_2025_gpu_memory_allocation]；本文依据CUDA stream与复制语义 [@nvidia_cuda_programming_guide_12_6]，在单帧顺序路径内把暂存分配类型作为独立变量。局部路径变化仍需在完整E2E边界评价 [@kim_et_al_2025_concurrent_edge_detection]。

## 1.3 统一计时边界与研究问题

平均延迟、吞吐率和尾延迟描述不同性能属性，平均值不能替代分布尾部 [@dean_barroso_2013_tail_scale]。逐帧延迟采用source-to-pre-sink边界，从获取数据源帧前开始，包含图像获取与解码、路径对应的暂存和输入形成、H2D、TensorRT推理与同步、必要的D2H、CPU后处理/NMS及结果构造，在序列化和写文件前结束。进程级FPS以每个独立进程的1080个测量帧除以完整测量阶段wall time得到，包含统一的结果输出处理，不由逐帧延迟取倒数。

本文回答两个问题。RQ1：在固定模型、Engine和工作负载下，将主机FP32张量形成路径重构为原始图像H2D与GPU融合预处理，对完整E2E性能产生多大影响？RQ2：在GPU预处理、CUDA stream和下游拓扑保持不变时，将pageable原始图像暂存替换为pinned暂存，是否进一步改善平均性能，以及P95/P99是否呈现一致的尾延迟改善？
