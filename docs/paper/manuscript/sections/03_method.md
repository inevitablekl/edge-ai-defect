<!-- MANUSCRIPT_SECTION: 2 -->

# 2 受控输入数据路径重构

## 2.1 V0基线路径

V0实现\(P_0\)的主机张量路径。数据源解码为BGR图像后，CPU/OpenCV采用`INTER_LINEAR`完成640×640 letterbox与常数114填充，并完成BGR→RGB、HWC→CHW及\(1/255\)归一化，在主机侧形成`1×3×640×640` FP32 NCHW张量后执行FP32 H2D复制。其科学语义是“主机形成模型输入、张量表示跨越边界”，具体操作仅用于复现该路径实例。

## 2.2 V2R路径级重构

V2R实现\(P_2\)，将跨边界表示由FP32 NCHW张量改为packed BGR uint8，并将输入张量形成位置由主机移至设备。冻结工作负载的源图像为200×200，因此主机侧只额外形成连续的600 B行宽packed BGR pageable暂存；该表示经二维H2D复制后，由设备侧融合预处理直接写入TensorRT管理的FP32 NCHW输入。实现中二维复制映射为`cudaMemcpy2DAsync`，融合处理完成resize、padding、BGR→RGB、归一化与布局变换。

GPU resize按V0的OpenCV 4.5.4 `INTER_LINEAR`语义建立受控对齐，letterbox几何和填充值保持一致。该约束服务于三条路径的输入语义一致性，不构成通用CUDA/OpenCV等价性声明。相关设备缓冲区和执行上下文在进程内复用，以避免逐帧重复分配或创建。

## 2.3 V3R暂存策略细化

V3R实现\(P_3\)，在V2R基础上只将额外打包原始图像的主机暂存策略由pageable改为pinned。跨边界表示、设备侧张量形成、GPU融合预处理、二维复制拓扑、CUDA stream、Engine和全部下游处理均保持不变。实现上使用`cudaHostAlloc`建立跨帧复用的pinned暂存；其分配方式只是\(M\)的实现映射，不改变复制内容和每帧有效几何。

## 2.4 共同控制与正确性约束

三条路径共用同一Engine、CUDA stream语义、推理同步、输出回传以及CPU检测框解码、置信度筛选和NMS，执行拓扑均为单帧顺序。后处理配置固定为置信度阈值0.25、IoU阈值0.45、`max_nms=30000`、`max_det=300`和class-aware单标签语义。V2R通过预定义任务级核验；V3R由相同评价程序对冻结预测结果确定性重算，并通过输入顺序、处理数量、丢帧和EOS检查确保执行完整性及路径间可比性。
