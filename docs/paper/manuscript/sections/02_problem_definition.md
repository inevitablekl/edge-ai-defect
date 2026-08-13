<!-- MANUSCRIPT_SECTION: 1; FIGURES: F1,F2 -->

# 1 系统对象与问题定义

## 1.1 模型、数据集与部署环境

本文研究对象为部署于NVIDIA Jetson Orin Nano Super边缘平台的YOLOv8n工业缺陷检测模型。实际记录的软件环境为L4T R36.5、CUDA 12.6和TensorRT 10.3，模型输入固定为640×640、batch size为1。NVIDIA官方资料显示，JetPack 6.2.2所含Jetson Linux 36.5、CUDA 12.6和TensorRT 10.3与上述组件版本相对应；本文仍以实际记录的组件版本而非JetPack meta-package推断作为环境身份 [@nvidia_jetpack_6_2_2]。

数据采用NEU-DET目标检测标注及去重后的split-v2。原始数据库包含6类钢材表面缺陷和1800幅200×200图像；去重后训练集、验证集和测试集分别包含1260、359和180幅图像，测试集成员保持不变。后续部署评价固定使用同一组180幅测试图像。固定推理对象由既有YOLOv8n通过校准式后训练量化构建；量化部署需要同时评价计算实现与任务性能 [@kim_lee_kim_2024_hyq]，因此本文只将该Engine作为数据路径研究的共同前提。

正式校准使用去重训练集的1260幅图像并排除测试集，采用`IInt8EntropyCalibrator2`、batch size 1和640×640输入。校准数据经过与生产CPU `Preprocessor`一致的BGR letterbox、RGB/NCHW与FP32/255预处理；构建同时启用INT8与FP16，并在支持位置保持FP32 I/O，故本文统一称其为TensorRT INT8混合精度Engine。正式构建采用强制cache miss，1260个校准batch全部执行；校准完成后生成并归档cache，未将既有cache复用为正式构建输入。

## 1.2 E2E数据路径与受控变量

完整部署路径不仅包含固定输入张量进入TensorRT Engine后的网络计算，还包括图像获取与解码、主机暂存、输入形成、必要的数据移动、推理与同步、后处理和结果构造。Jetson检测部署通常同样区分预处理、模型推理和后处理 [@tang_qian_2024_yolov8_jetson_orin]。本文用下式表示统一计时边界内各执行阶段共同构成E2E耗时：

\[
T_{\mathrm{E2E}}
=
\sum_{k=1}^{m}T_k .
\]

该式只说明本文统计完整pipeline，而非network-only TensorRT inference time；各个\(T_k\)未被独立插桩或测量。

V0将解码后的BGR图像在主机侧形成640×640 FP32 RGB/NCHW张量，再把该张量复制到TensorRT设备输入。V2R/V3R先暂存packed BGR `uint8`原始图像，通过`cudaMemcpy2DAsync`复制到device raw buffer，再由一个融合CUDA kernel完成resize、padding、BGR→RGB、归一化和layout conversion，并直接写入TensorRT-owned FP32 NCHW设备输入。V2R与V3R复用同一TensorRT stream、相同CUDA预处理和相同下游拓扑；两者之间唯一隔离变量是raw-image host staging的allocation type。

锁页内存能够支持更直接的异步主机—设备复制，但它是有限资源，实际收益需要在具体实现中测量 [@nvidia_cuda_best_practices_12_6]。集成CPU/GPU和GPU内存分配研究也表明，内存策略的表现取决于平台、工作负载和访问特征 [@bateni_et_al_2020_integrated_memory; @rodriguez_et_al_2025_gpu_memory_allocation]。本文因此把pageable→pinned暂存作为独立变量，而不预设其收益。CUDA stream与异步复制的通用语义参照CUDA官方文档 [@nvidia_cuda_programming_guide_12_6]；当前实现仍为单帧顺序路径，不包含跨帧重叠。

V0→V2R覆盖主机FP32张量形成到raw-image H2D与GPU输入形成的完整重构；V2R→V3R仅替换主机暂存分配类型。完整检测系统与GPU预处理研究均提示，局部数据路径变化必须放回E2E执行边界评价 [@kim_et_al_2025_concurrent_edge_detection]。局部优化对E2E性能的实际贡献取决于其在完整执行路径中的占比及瓶颈位置，因此组件级变化不能直接等价为完整系统加速 [@hill_marty_2008_amdahl]。

## 1.3 统一计时边界与研究问题

推理系统的延迟、吞吐率与尾延迟描述不同性能属性，平均延迟不能替代分布尾部 [@dean_barroso_2013_tail_scale]。系统基准也需要针对具体场景分别定义延迟和吞吐率边界 [@reddi_et_al_2019_mlperf_inference]。本文采用固定离线回放协议，不采用MLPerf的查询生成、样本数或统计推断规则。

逐帧latency采用统一的source-to-pre-sink外部边界：计时从获取数据源帧之前开始，包含图像获取与解码、路径对应的主机暂存和输入形成、H2D、TensorRT推理与同步、必要的D2H、CPU后处理/NMS及结果对象构造，在结果序列化和写文件之前结束。process-wall FPS则以每个独立进程的1080个测量帧除以完整measured-run wall time得到，包含协议中统一的sink/output processing。两类指标采用不同边界，FPS不由逐帧latency取倒数获得。

基于上述定义，本文只回答两个研究问题。RQ1：在固定模型、Engine和工作负载下，将主机FP32张量形成路径重构为raw-image H2D与GPU融合预处理，对完整E2E性能产生多大影响？RQ2：在GPU预处理、CUDA stream和下游拓扑保持不变时，将pageable raw staging替换为pinned staging，是否进一步带来稳定的平均性能和tail-latency收益？
