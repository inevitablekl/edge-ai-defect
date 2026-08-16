<!-- MANUSCRIPT_SECTION: 3; TABLE: T2 -->

# 3 实验设计

## 3.1 实验平台与模型配置

平台、模型和统一协议见表2。平台与框架条件会影响部署性能 [@shin_kim_2022_jetson_yolo_frameworks]，本文据此不作跨研究绝对FPS比较，并遵循明确数据与评价边界的基准取向 [@lema_et_al_2025_surface_defect_benchmark]。

**表2　平台、模型与统一基准协议。**

| 项目 | 设置 |
|---|---|
| 平台 | NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super |
| 软件栈 | L4T R36.5；CUDA 12.6；TensorRT 10.3；OpenCV 4.5.4 |
| Detector / 输入 | YOLOv8n；640 × 640；batch 1 |
| Engine | TensorRT INT8混合精度（INT8 + FP16 fallback）；host input FP32 |
| 校准 | 1260张去重训练图像；IInt8EntropyCalibrator2；batch 1；排除test split |
| 工作负载 | 固定180张test图像 |
| 路径 | V0 / V2R / V3R；单帧顺序执行 |
| 计时协议 | 60帧预热；每进程1080帧；每路径5个独立进程 |
| 正式计时 | 关闭diagnostics与profiling |

正式运行采用`MAXN_SUPER`电源模式（`nvpmodel` mode 2），未调用`jetson_clocks`，频率未独立归档。运行前温度约46.8–47.1 ℃，运行后约48.7–49.6 ℃；这些非连续观察不用于判断持续温度、运行时降频或功耗状态。

## 3.2 数据集与统一运行协议

性能实验使用同一manifest限定的split-v2固定180幅测试图像及顺序。每个独立进程预热60帧，同步并重置测量窗口后测量1080帧；每条路径执行5个独立进程，形成5400个逐帧延迟样本，三条路径共15个进程和16200个样本，不在路径间构造运行配对。

15个独立进程按预先设定的交错顺序执行。全部进程均处理1080个测量帧、丢帧为0，并通过输入顺序、EOS和生命周期准入；逐帧diagnostics与profiling保持关闭。

## 3.3 正确性与性能指标

正确性采用冻结测试集和统一评价器，报告Precision、Recall、mAP50、mAP50-95及类别级AP50/Recall；V3R对冻结预测结果确定性重算，并结合V2R/V3R摘要校验与生命周期身份检查。

对第\(i\)个独立进程，FPS定义为

\[
f_i=\frac{N}{T_i},
\]

其中\(N=1080\)，\(T_i\)为测量阶段wall time。每条路径的平均FPS为5个独立进程级FPS的算术平均，误差棒为这5个值的样本标准差。逐帧延迟采用source-to-pre-sink边界，每条路径合并5400个样本计算均值、P95和P99。百分位采用Type-7线性插值：将延迟样本升序记为\(x_{(1)}\leq\cdots\leq x_{(n)}\)，对本文\(p=0.95\)或\(p=0.99\)，令\(h=1+(n-1)p\)、\(j=\lfloor h\rfloor\)、\(\gamma=h-j\)，则内部位置的\(Q_p=(1-\gamma)x_{(j)}+\gamma x_{(j+1)}\)。所有统计均为描述性结果，不进行置信区间、假设检验或统计显著性推断。
