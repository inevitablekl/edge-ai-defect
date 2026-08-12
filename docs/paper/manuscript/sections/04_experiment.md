<!-- MANUSCRIPT_SECTION: 3; TABLE: T2 -->

# 3 实验设计

## 3.1 实验平台与模型配置

实验在NVIDIA Jetson Orin Nano Super平台上完成。实际记录的软件环境为L4T R36.5、CUDA 12.6.11（runtime 12.6.68）、TensorRT 10.3.0.30和OpenCV 4.5.4。已有Jetson检测框架评估表明，框架与平台条件会影响部署性能，因此本文不进行跨研究的绝对FPS比较 [@shin_kim_2022_jetson_yolo_frameworks]。检测模型固定为YOLOv8n，输入尺寸为640×640、batch size为1，推理对象为第1节所述TensorRT INT8混合精度Engine。三条路径不重新构建或校准Engine，也不改变模型、检测阈值和后处理配置。

实验将工作负载、正确性条件、计时边界和统计口径作为统一条件。该设计与表面缺陷基准研究强调明确数据和评价边界的取向一致 [@lema_et_al_2025_surface_defect_benchmark]，但不声称遵循其他基准的正式规范。平台、模型和协议见表2。

**表2　平台、模型、数据集和统一运行协议**

| 项目 | 配置 |
|---|---|
| 边缘平台 | NVIDIA Jetson Orin Nano Super |
| L4T | R36.5 |
| CUDA | 12.6.11，runtime 12.6.68 |
| TensorRT | 10.3.0.30 |
| OpenCV | 4.5.4 |
| 检测模型 | YOLOv8n |
| 推理对象 | 冻结 TensorRT INT8 混合精度 Engine |
| 输入尺寸 | 640×640 |
| Batch size | 1 |
| 数据集 | NEU-DET，去重后的 split-v2 |
| 测试集 | 固定 180 幅图像 |
| 正式比较路径 | V0、V2R、V3R |
| 单次预热 | 60 帧 |
| 单次测量 | 1080 帧，即 180 幅图像完整回放 6 个周期 |
| 独立运行次数 | 每种路径 5 次，共 15 个独立进程 |
| 内部诊断计时 | 关闭 |
| Profiling | 关闭 |

正式运行使用`MAXN_SUPER`电源模式（`nvpmodel` mode 2），未调用`jetson_clocks`。时钟频率没有独立归档，因而不作为固定频率条件。运行前温度约为46.8–47.1 ℃，运行后约为48.7–49.6 ℃；这些仅是非连续的前后观察，不用于判断持续温度、运行时降频或功耗状态。

## 3.2 数据集与统一运行协议

性能实验采用split-v2固定测试集的180幅图像。输入成员和顺序由同一manifest限定，每次独立运行先预热60帧，完成同步并重置测量窗口，再测量1080帧，即连续回放6个完整周期。每条路径执行5个独立进程，V0、V2R和V3R各形成5400个逐帧latency样本，三条路径合计16200个样本。5次运行均为独立process，不在不同路径之间构造逐次对应关系。

15个进程按照运行前确定的交错顺序执行：V0–V2R–V3R、V3R–V2R–V0、V2R–V0–V3R、V0–V3R–V2R和V2R–V3R–V0。全部15个进程均处理1080个测量帧、丢帧为0，并通过输入顺序、EOS和生命周期准入。内部逐帧诊断计时与profiling保持关闭，避免不同路径采用不同测量机制。

## 3.3 正确性与性能指标

正确性评价采用冻结的180幅测试集和统一evaluator。V0/V2R沿用正式precision、recall、mAP50、mAP50-95及类别级AP50/recall authority；V3R通过同一evaluator对冻结predictions进行确定性评价，并结合V2R/V3R digest与生命周期身份检查。V3R评价不是新的inference或第二次参数选择gate。

性能指标包括process-level FPS、逐帧平均latency以及P95、P99。对第\(i\)个独立运行，FPS定义为

\[
f_i=\frac{N}{T_i},
\]

其中\(N=1080\)，\(T_i\)为该进程的measured process-wall时间（s）。每条路径的平均FPS由5个进程级FPS算术平均得到：

\[
\mu_f=\frac{1}{5}\sum_{i=1}^{5}f_i .
\]

FPS离散程度以这5个值的样本标准差表示，采用样本均值\(\mu_f\)并以\(5-1=4\)为方差分母。该标准差是运行级描述量，不是置信区间。逐帧latency采用source-to-pre-sink外部边界，每条路径合并5次运行的5400个样本后计算mean、P95和P99。百分位采用Type-7线性插值。设升序样本为\(x_{(1)},\ldots,x_{(n)}\)，对于概率\(p\)，令

\[
h=1+(n-1)p,\qquad
j=\lfloor h\rfloor,\qquad
\gamma=h-j,
\]

则内部位置的百分位数为

\[
Q_p=(1-\gamma)x_{(j)}+\gamma x_{(j+1)} .
\]

分别取\(p=0.95\)和\(p=0.99\)得到P95与P99。本文只报告上述固定工作负载下的描述性统计，不进行置信区间、假设检验或统计显著性推断。
