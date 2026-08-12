# 平台、模型与统一基准协议

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

Source trace: `../../../phase56b_runtime_state.json`、`../../../phase56b_calibration_provenance.json`、`../../../phase56b_run_level_metrics.csv`、`../../../../phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`、`../../../../phase0_5/evidence/timing_aligned_harness_preflight_v1/environment.json`与`../../table2_platform_protocol_spec.md`。
