<!-- MANUSCRIPT_SECTION: 2; TABLE: T1 -->

# 2 数据路径工程方法

三条受控路径的主要配置见表1。

**表1　三条受控路径的特征矩阵。检测器和TensorRT Engine相同；三条路径均为单帧顺序执行，无跨帧流水线。**

| 路径特征 | V0 | V2R | V3R |
|---|---:|---:|---:|
| CPU像素预处理 | 是 | 否 | 否 |
| CUDA预处理 | 否 | 是 | 是 |
| 主机FP32输入张量 | 是 | 否 | 否 |
| 额外打包原始图像暂存 | 否 | Pageable | Pinned |
| 原始图像H2D | 否 | 是 | 是 |
| 输入形成位置 / TRT直接输入 | 主机 / 否 | 设备 / 是 | 设备 / 是 |
| 执行拓扑 | 单帧顺序 | 同一TRT stream；单帧顺序 | 同一TRT stream；单帧顺序 |

## 2.1 V0：主机侧FP32张量形成

V0将数据源解码为主机侧`CV_8UC3` BGR图像，CPU/OpenCV使用`INTER_LINEAR`执行640×640 letterbox和常数114填充，再完成BGR→RGB、HWC→CHW与`1/255`归一化，在主机侧形成`1×3×640×640` FP32 NCHW输入并复制至设备；Engine推理后，输出回到主机进行检测框解码、置信度筛选和NMS。

## 2.2 V2R：pageable暂存与GPU输入形成

V2R保留主机图像读取与解码，将`CV_8UC3` BGR图像逐行复制到可复用的`std::vector<uint8_t>`，形成连续packed BGR暂存。冻结工作负载图像为200×200，有效行宽600 B；letterbox几何仍由主机按统一模型合同计算。

packed BGR图像通过`cudaMemcpy2DAsync`写入持久化设备原始图像缓冲区，随后一个融合CUDA核函数完成resize、padding、BGR→RGB、`1/255`归一化和HWC→NCHW布局转换，直接写入TensorRT管理的FP32 NCHW设备输入。该resize按V0的OpenCV 4.5.4 `INTER_LINEAR`预处理语义建立受控对齐合同，仅适用于本文冻结实现和工作负载，不构成通用CUDA/OpenCV等价性声明。CUDA预处理器、设备缓冲区、同一TensorRT CUDA stream和execution context均跨帧复用。

## 2.3 V3R：pinned原始图像暂存隔离变量

V3R与V2R共享packed BGR语义、`cudaMemcpy2DAsync`、融合CUDA预处理、TensorRT CUDA stream、Engine和下游拓扑，仅将主机暂存改为帧循环前由`cudaHostAlloc(..., cudaHostAllocDefault)`分配的长生命周期pinned缓冲区。该缓冲区在全部帧之间复用，运行器结束时由`cudaFreeHost`释放；每帧仍逐行复制`width×3`字节，不逐帧分配，也不静默回退到pageable暂存。内存配置效果具有平台和负载依赖性 [@bateni_et_al_2020_integrated_memory; @rodriguez_et_al_2025_gpu_memory_allocation]。

三条正式路径均为单帧顺序执行，不使用zero-copy、double buffering、multi-stream、跨帧流水线、显式传输/计算重叠或GPU NMS；这些边界仅限定本文受测实现，两条GPU路径关系见图2。

**图2　V2R/V3R主机—设备输入路径。两者仅pageable/pinned暂存不同；复制、融合CUDA预处理与`enqueueV3`沿同一TensorRT CUDA stream单帧顺序执行，不表示跨帧重叠。**

## 2.4 正确性与生命周期控制

三条路径使用相同的冻结180幅测试图像、模型、Engine、输入尺寸、置信度阈值0.25、IoU阈值0.45、`max_nms=30000`、`max_det=300`和class-aware单标签后处理。V2R在预设任务级差异门限下通过与V0的核验；V3R由同一评价程序对冻结预测结果确定性重算，并以张量与检测摘要、帧顺序、处理数量、丢帧、EOS和生命周期检查约束隔离变量身份。该正确性结论仅适用于本文冻结工作负载和评价口径。
