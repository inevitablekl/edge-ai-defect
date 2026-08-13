<!-- MANUSCRIPT_SECTION: 2; TABLE: T1 -->

# 2 数据路径工程方法

三条受控路径的主要配置及比较变量见表1。

**表1　V0、V2R和V3R受控数据路径的特征矩阵。三条路径使用相同检测器和TensorRT Engine；V0在主机侧形成FP32输入张量，V2R/V3R在设备侧形成输入张量，且后两者仅在pageable与pinned原始图像暂存类型上不同。三条路径均为单帧顺序执行，无跨帧流水线。**

| 路径特征 | V0 | V2R | V3R |
|---|---:|---:|---:|
| Detector / Engine | 相同 | 相同 | 相同 |
| CPU像素预处理 | 是 | 否 | 否 |
| CUDA预处理 | 否 | 是 | 是 |
| 主机FP32输入张量 | 是 | 否 | 否 |
| 打包原始图像暂存 | 否 | Pageable | Pinned |
| 原始图像H2D | 否 | 是 | 是 |
| 张量形成位置 | 主机 | 设备 | 设备 |
| 直接形成TRT设备输入 | 否 | 是 | 是 |
| 复用TRT CUDA stream | — | 是 | 是 |
| 跨帧流水线 | 否 | 否 | 否 |

## 2.1 V0：主机侧FP32张量形成

V0首先将数据源图像解码为主机侧`CV_8UC3` BGR图像。CPU/OpenCV随后执行640×640 letterbox：使用`INTER_LINEAR`完成resize，以常数114填充，并依次进行BGR→RGB、HWC→CHW和`1/255`归一化，最终在主机侧形成FP32 NCHW张量。该`1×3×640×640`张量再通过TensorRT后端复制到设备输入缓冲区，Engine完成推理后将输出复制回主机并执行检测框解码、置信度筛选和NMS。

V0的关键系统属性不是笼统的“CPU预处理”，而是主机侧FP32张量形成：像素变换、布局转换和浮点张量构造均在主机完成，H2D输入对象也是完整FP32 NCHW张量。该路径保留既有OpenCV语义，作为后续输入形成位置和主机侧数据表示重构的受控基线。

## 2.2 V2R：pageable原始图像暂存与GPU输入形成

V2R保留主机侧图像读取与解码，并将解码后的`CV_8UC3` BGR图像逐行复制到可复用的`std::vector<uint8_t>`，形成连续packed BGR原始图像暂存。对冻结工作负载中的200×200图像，暂存区的有效行宽为600 B。Letterbox几何参数仍由主机按照统一模型合同计算，不在GPU端重新决定缩放比例或padding位置。

packed BGR原始图像通过`cudaMemcpy2DAsync`执行二维H2D复制，写入持久化设备原始图像缓冲区。随后，一个融合CUDA预处理核函数在同一次launch内完成resize、padding、BGR→RGB、`1/255`归一化和HWC→NCHW布局转换，并直接写入TensorRT管理的FP32 NCHW设备输入。该resize实现针对固定Jetson平台、`CV_8UC3`输入和OpenCV 4.5.4 `INTER_LINEAR`行为建立对齐合同，不构成通用OpenCV GPU实现。

CUDA预处理器在帧循环前建立，复用TensorRT Engine的CUDA stream及其持久化设备输入缓冲区；TensorRT推理沿用同一CUDA stream和单一execution context。V2R由此把V0的主机FP32张量形成与FP32 H2D路径，重构为原始图像暂存、通过`cudaMemcpy2DAsync`执行二维H2D复制以及设备侧输入形成。该实现是输入数据路径工程，不引入新的检测、量化或TensorRT算法。

V2R/V3R的主机—设备内存域、缓冲区生命周期与单流执行语义见图2。

**图2　V2R/V3R的主机—设备内存域、缓冲区生命周期与单流执行语义。两条路径仅在主机侧pageable/pinned暂存类型上不同；`cudaMemcpy2DAsync`、融合CUDA预处理、`enqueueV3`及输出D2H沿同一TensorRT CUDA stream顺序执行，暂存区、设备原始图像缓冲区和后端输入缓冲区跨帧复用。图中不表示跨帧重叠或流水线。**

## 2.3 V3R：pinned原始图像暂存隔离变量

V3R与V2R共享相同的packed BGR语义、`cudaMemcpy2DAsync`、融合CUDA预处理核函数、TensorRT CUDA stream、Engine、后处理和下游执行拓扑。差异仅在于主机侧原始图像暂存：V3R在帧循环前通过`cudaHostAlloc(..., cudaHostAllocDefault)`分配一个长生命周期锁页缓冲区，在全部帧之间复用，并在运行器生命周期结束时通过`cudaFreeHost`释放。每帧仍按行复制`width×3`字节，不发生逐帧锁页内存分配，也不存在失败后静默回退到pageable暂存。

因此，V3R相对V2R的唯一隔离变量为原始图像主机暂存的分配类型。该受控关系使pageable与pinned暂存的观测差异不与第二套CUDA预处理、不同Engine或并发拓扑混合。既有嵌入式异构SoC研究同样说明内存与运行配置效果具有平台和负载依赖性 [@archet_et_al_2023_embedded_soc]，本文据此只评价当前固定实现中的边际变化。

三条正式路径均不使用zero-copy、double buffering、multi-stream、跨帧流水线、显式传输/计算重叠或GPU NMS。上述共同排除项只用于界定当前单帧顺序实现，不用于推断未测机制的性能。

## 2.4 正确性与生命周期控制

三条路径使用同一180幅测试图像、模型、Engine、输入尺寸、置信度阈值0.25、IoU阈值0.45、`max_nms=30000`、`max_det=300`和class-aware单标签后处理。V0提供既有任务正确性基线；V2R沿用正式任务级评价，指标包括precision、recall、mAP50、mAP50-95以及类别级AP50和recall。总体mAP50-95、mAP50、precision和recall的允许绝对差异分别为0.005、0.005、0.010和0.010，类别级最大AP50和recall差异阈值分别为0.020和0.030。

V3R的任务指标来自对冻结预测结果的确定性统一评价，而非新的推理或第二次参数选择。该评价与V0/V2R使用相同的冻结工作负载和评价程序；V2R/V3R之间的张量摘要校验值、检测结果摘要校验值、帧顺序、处理数量、丢帧计数和EOS状态进一步验证了唯一隔离变量身份。由此，三条路径均给出任务级评价结果，同时生命周期证据继续约束V3R的实现身份。正确性相等只针对本文冻结工作负载及评价口径，不扩展为任意未来输入上的普适等价。
