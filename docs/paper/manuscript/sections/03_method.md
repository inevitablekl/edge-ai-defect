<!-- MANUSCRIPT_SECTION: 2 -->

# 2 受控输入数据路径重构

## 2.1 V0基线路径

V0实现\(P_0\)的主机张量路径：数据源解码为BGR图像后，CPU/OpenCV以`INTER_LINEAR`完成640×640 letterbox和常数114填充，再执行BGR→RGB、HWC→CHW及\(1/255\)归一化，主机侧形成`1×3×640×640` FP32 NCHW张量后进行FP32 H2D复制。因此\(F\)为主机、\(R\)为FP32 NCHW、\(M\)无额外打包原始图像暂存，\(E\)为单帧顺序执行；这些操作仅用于复现\(P_0\)。

## 2.2 V2R路径级重构

V2R实现\(P_2\)的设备张量形成路径：200×200源图像在主机侧形成连续的600 B行宽packed BGR uint8 pageable暂存，经`cudaMemcpy2DAsync`二维H2D复制后，设备侧融合完成resize、padding、BGR→RGB、归一化和布局变换，直接写入TensorRT管理的FP32 NCHW输入。相对\(P_0\)，\(R,F\)改变，\(M\)引入pageable暂存，\(E\)仍为单帧顺序；该API与融合核函数仅是\(P_2\)的实现映射。

GPU resize按V0的OpenCV 4.5.4 `INTER_LINEAR`语义建立受控对齐，letterbox几何和填充值保持一致。该约束服务于三条路径的输入语义一致性，不构成通用CUDA/OpenCV等价性声明。相关设备缓冲区和执行上下文在进程内复用，以避免逐帧重复分配或创建。

## 2.3 V3R暂存策略细化

V3R实现\(P_3\)的局部暂存策略细化，其路径语义是在V2R基础上只将\(M\)由pageable改为pinned。跨边界表示\(R\)、张量形成位置\(F\)和执行拓扑\(E\)均保持不变，GPU融合预处理语义、二维复制拓扑、CUDA stream、Engine和全部下游处理也受到控制。

作为\(M=\mathrm{pinned}\)的实现映射，V3R使用`cudaHostAlloc`建立跨帧复用的pinned暂存。该分配API不改变复制内容和每帧有效几何，也不构成独立于\(M\)的结构变量。

## 2.4 共同控制与正确性约束

三条路径共用同一Engine、CUDA stream语义、推理同步、输出回传以及CPU检测框解码、置信度筛选和NMS，执行拓扑均为单帧顺序。后处理配置固定为置信度阈值0.25、IoU阈值0.45、`max_nms=30000`、`max_det=300`和class-aware单标签语义。V2R通过预定义任务级核验；V3R由相同评价程序对冻结预测结果确定性重算，并通过输入顺序、处理数量、丢帧和EOS检查确保执行完整性及路径间可比性。
