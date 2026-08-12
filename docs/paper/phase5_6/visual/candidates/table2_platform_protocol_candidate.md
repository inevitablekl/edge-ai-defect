# Table 2 candidate — Platform / Model / Protocol

> **CANDIDATE / SPECIFICATION — not manuscript authority**

| Item | Setting |
|---|---|
| Platform | NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super |
| Software | L4T 36.4.3; CUDA 12.6; TensorRT 10.3; OpenCV 4.5.4 |
| Detector / input | YOLOv8n; 640 × 640; batch 1 |
| Engine | TensorRT INT8 mixed precision (INT8 + FP16 fallback); host input FP32 |
| Calibration | 1260 deduplicated training images; IInt8EntropyCalibrator2; batch 1; test split excluded |
| Workload | fixed 180-image test workload |
| Paths | V0 / V2R / V3R; single-frame sequential |
| Timing | 60 warm-up frames; 1080 measured frames/process; 5 independent processes/path |
| Formal timing | diagnostics and profiling disabled |

Allocation of additional facts: see `../table2_platform_protocol_spec.md` (`KEEP_IN_TABLE`, `KEEP_IN_TEXT`, `OMIT_AS_REDUNDANT`).
