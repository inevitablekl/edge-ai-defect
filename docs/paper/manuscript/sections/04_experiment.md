<!-- MANUSCRIPT_SECTION: 3; TABLE: T2 -->

# 3 实验协议

## 3.1 实验平台与模型配置

平台、固定推理对象和统一协议见表2。软件版本、功耗模式和工作负载是复现实验的条件，不参与路径描述符定义。

**表2　平台、模型与统一基准协议。**

| 项目 | 设置 |
|---|---|
| 平台 | NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super |
| 软件栈 | L4T R36.5；CUDA 12.6；TensorRT 10.3；OpenCV 4.5.4 |
| Detector / 输入 | YOLOv8n；640 × 640；batch 1 |
| Engine | TensorRT INT8混合精度（INT8 + FP16 fallback）；Engine输入张量：FP32 |
| 校准 | 1260张去重训练图像；IInt8EntropyCalibrator2；batch 1；排除test split |
| 工作负载 | 固定180张test图像 |
| 路径 | V0 / V2R / V3R；单帧顺序执行 |
| 计时协议 | 60帧预热；每进程1080帧；每路径5个独立进程 |
| 正式计时 | 关闭diagnostics与profiling |

正式运行采用`MAXN_SUPER`电源模式（`nvpmodel` mode 2），未调用`jetson_clocks`，频率未独立归档。运行前温度约46.8–47.1 ℃，运行后约48.7–49.6 ℃；这些非连续观察不用于判断持续温度、运行时降频或功耗状态。

## 3.2 运行与正确性协议

性能实验使用同一manifest限定的split-v2固定180幅测试图像及顺序。每个独立进程预热60帧，同步并重置测量窗口后测量1080帧；每条路径执行5个独立进程，形成5400个逐帧延迟样本，三条路径共15个进程和16200个样本，路径间不构造运行配对。

15个独立进程按预先设定的交错顺序执行。全部进程均处理1080个测量帧、丢帧为0，并通过输入顺序、EOS和生命周期准入；逐帧diagnostics与profiling保持关闭。

## 3.3 E2E、FPS与尾延迟指标

正确性采用冻结测试集和统一评价器，报告Precision、Recall、mAP50、mAP50-95及类别级AP50/Recall。性能指标沿用式（3）的source-to-pre-sink边界；第\(i\)个独立进程的FPS按\(f_i=N/T_i\)计算，其中\(N=1080\)，\(T_i\)为完整测量阶段wall time，故FPS不是逐帧延迟的倒数。每条路径报告5个进程级FPS的均值与样本标准差，并合并5400个逐帧样本计算平均延迟、P95和P99；百分位采用Type-7线性插值。所有统计均为描述性结果，不进行置信区间、假设检验或统计显著性推断。
