# REQUIREMENTS.md

## 1. Purpose

This document defines the core requirements for:

**Edge AI Industrial Defect Detection Deployment and Optimization**

Chinese name:

**边缘 AI 工业缺陷检测部署与优化项目**

This project is used for:

- Electronic Information graduate thesis.
- Small engineering paper.
- Job-seeking portfolio for embedded / edge AI deployment roles.

This is an engineering deployment project.

It is not an AI algorithm research project.

---

## 2. Requirement Keywords

| Keyword | Meaning |
|---|---|
| MUST | Required for v1 |
| SHOULD | Strongly recommended |
| MAY | Optional |
| MUST NOT | Forbidden unless explicitly approved |
| TBD | Not decided yet |

---

## 3. Fixed Requirements

| Item | Requirement |
|---|---|
| Main dataset | NEU-DET / NEU Surface Defect Database |
| Main model | YOLOv8n |
| Dataset split | train / val / test = 70 / 20 / 10 |
| Input sizes | 320, 416, 640 |
| Training language | Python |
| Deployment language | C++ |
| Configuration format | YAML |
| Build system | CMake |
| Baseline backend | ONNX Runtime |
| Optimized backend | TensorRT FP16 |
| Main platform | NVIDIA Jetson |
| Runtime modes | Serial, Pipeline |
| v1 GUI | Not implemented |
| v1 ROS2 | Interface reservation only |
| INT8 | Optional future optimization only |
| Logs | CSV / JSON |

---

## 4. v1 Scope

v1 MUST include:

- NEU-DET dataset preparation.
- YOLOv8n training.
- ONNX export.
- C++ command-line inference application.
- YAML configuration loading.
- ONNX Runtime inference backend.
- TensorRT FP16 inference backend.
- Serial runtime mode.
- Pipeline runtime mode.
- YOLOv8 postprocessing.
- Performance profiling.
- CSV / JSON experiment logs.
- Image sequence input.
- Video file input.
- Detection result output.

v1 SHOULD include:

- Reproducible dataset split.
- Reproducible ONNX export records.
- Clear error messages.
- Experiment configuration templates.
- Basic tests for config, preprocessing, and profiler.
- Model and dataset README files.

v1 MUST NOT include unless explicitly approved:

- Qt GUI.
- Web UI.
- Full ROS2 package.
- ROS2 runtime dependency.
- ROS2 topic publishing.
- INT8 calibration.
- INT8 engine generation.
- RK3588 / RKNN deployment.
- Self-designed detection model.
- SLAM.
- Navigation.
- Robotic arm control.
- Full embodied intelligence system.

### Current C++ baseline phase

The active implementation phase is limited to a C++17 ONNX Runtime CPU Serial Baseline with the frozen static ONNX contract `float32 [1,3,640,640] -> float32 [1,10,8400]`. TensorRT, Pipeline, ROS2, Qt, INT8, and GPU optimizations are not implementation scope for this phase.

---

## 5. Dataset Requirements

The project MUST use:

```text
NEU-DET / NEU Surface Defect Database
```

The dataset conversion process MUST:

* Convert NEU-DET to YOLO format.
* Use Python.
* Generate train / val / test split.
* Use split ratio 70 / 20 / 10.
* Keep the split reproducible.
* Record class names.
* Record image and label counts.
* Report missing or invalid annotations clearly.

The conversion process MUST NOT:

* Mix train, val, and test data.
* Silently modify labels.
* Generate fake labels.
* Evaluate paper results on training data.

Expected processed dataset structure:

```text
data/processed/neu_det_yolo/
├── images/train/
├── images/val/
├── images/test/
├── labels/train/
├── labels/val/
├── labels/test/
└── dataset.yaml
```

---

## 6. Training Requirements

Training MUST use:

```text
YOLOv8n
```

Training scripts MUST be implemented in Python.

Training SHOULD run on:

```text
RTX 3090 cloud GPU
```

Training MUST produce or record:

* `best.pt`
* training configuration
* training command
* validation metrics
* class names
* dataset configuration
* software versions where available

Training metrics MUST include:

* Precision.
* Recall.
* mAP@0.5.
* mAP@0.5:0.95.

All training metrics MUST come from real training or validation results.

AI tools MUST NOT invent metrics.

---

## 7. ONNX Export Requirements

The project MUST provide a Python script to export YOLOv8n `.pt` to ONNX.

The export process MUST support:

```text
320 × 320
416 × 416
640 × 640
```

Expected ONNX files:

```text
models/onnx/yolov8n_320.onnx
models/onnx/yolov8n_416.onnx
models/onnx/yolov8n_640.onnx
```

The export process MUST record:

* Source `.pt` path.
* Output `.onnx` path.
* Input size.
* YOLO version.
* Opset version.
* Static or dynamic shape setting.
* Export command.
* Export time.
* Success status.

---

## 8. C++ Deployment Requirements

The deployment-side application MUST be implemented in C++.

Python MUST NOT be used as the main deployment runtime.

The C++ application MUST support command-line execution.

Expected usage:

```bash
./edge_ai_defect --config configs/infer_trt_serial.yaml
```

The application MUST load behavior from YAML configuration.

The application MUST NOT require source code changes to switch:

* Backend.
* Runtime mode.
* Model path.
* Input size.
* Input source.
* Output path.
* Log path.

---

## 9. Configuration Requirements

The project MUST use YAML as the primary configuration format.

Configuration files SHOULD be placed under:

```text
configs/
```

The following items MUST be configurable:

* backend
* runtime mode
* ONNX model path
* TensorRT engine path
* input source
* source type
* input size
* confidence threshold
* NMS threshold
* output directory
* log directory
* precision mode
* warmup frames
* measured frames
* pipeline queue size
* pipeline drop policy

Invalid configuration MUST fail with clear error messages.

---

## 10. Inference Backend Requirements

The project MUST define an abstract inference interface.

Required backends:

* ONNX Runtime.
* TensorRT FP16.

ONNX Runtime is the baseline backend.

TensorRT FP16 is the optimized backend.

Backend-specific logic MUST stay inside backend modules.

Runner logic MUST NOT contain ONNX Runtime or TensorRT-specific implementation details.

v1 MUST NOT implement these backends unless explicitly approved:

* PyTorch runtime.
* OpenVINO.
* RKNN.
* TensorFlow.
* NCNN.

---

## 11. Preprocessing and Postprocessing Requirements

Preprocessing MUST support:

* Resize.
* Optional letterbox if needed.
* BGR / RGB conversion.
* Normalization.
* HWC / CHW conversion.
* Input buffer preparation.

Preprocessing MUST be consistent between ONNX Runtime and TensorRT.

Postprocessing MUST support:

* YOLOv8 output decoding.
* Confidence threshold filtering.
* NMS.
* Bounding box coordinate restoration.
* Unified detection result output.

Each detection SHOULD include:

* class id
* class name
* confidence
* bounding box
* frame index
* timestamp if available

---

## 12. Runtime Requirements

Serial mode MUST be implemented as the baseline runtime.

Serial flow:

```text
Frame input
→ Preprocess
→ Inference
→ Postprocess
→ Output
→ Log
```

Pipeline mode MUST be implemented as the optimized runtime.

Initial pipeline design:

```text
Capture Thread
→ Inference Thread
→ Output Thread
```

Pipeline queue size MUST be configurable.

Recommended queue size:

```text
1 or 2
```

Pipeline mode SHOULD support:

```text
drop_oldest
```

Meaning:

```text
when the queue is full, drop old frames and keep the latest frame
```

Documentation MUST distinguish:

* FPS / throughput.
* Single-frame latency.
* End-to-end latency.

Pipeline mode MUST NOT be described as always reducing latency.

---

## 13. Profiler and Log Requirements

The Profiler MUST record:

* preprocessing latency
* inference latency
* postprocessing latency
* total latency
* FPS

The Profiler SHOULD record:

* CPU usage
* GPU usage
* memory usage

If a metric is unavailable, record:

```text
Not available
```

The Profiler MUST export:

```text
CSV
JSON
```

Logs SHOULD include:

* timestamp
* git commit
* device
* backend
* runtime mode
* model name
* input size
* precision mode
* source type
* warmup frames
* measured frames
* latency statistics
* FPS
* resource metrics
* notes

Warmup frames SHOULD be excluded from final statistics.

---

## 14. Result Output Requirements

The system MUST support:

* visualized detection image output
* detection result data output
* experiment log output

The system MAY support:

* video output
* camera input

The system MUST NOT depend on GUI in v1.

The system MUST reserve a future ROS2 extension point but MUST NOT introduce ROS2 runtime dependency in v1.

Future direction:

```text
DetectionResult
→ ROS2 publisher
→ vision_msgs/msg/Detection2DArray
```

---

## 15. Experiment Requirements

The project MUST support the following experiment groups.

### E1: Model Accuracy

Metrics:

* Precision.
* Recall.
* mAP@0.5.
* mAP@0.5:0.95.

### E2: Backend Comparison

Compare:

```text
ONNX Runtime
TensorRT FP16
```

Metrics:

* average latency
* p50 latency
* p95 latency
* FPS
* memory usage

### E3: Runtime Mode Comparison

Compare:

```text
Serial mode
Pipeline mode
```

Metrics:

* FPS
* total latency
* p95 latency
* CPU usage
* GPU usage
* memory usage

### E4: Input Size Comparison

Compare:

```text
320 × 320
416 × 416
640 × 640
```

Metrics:

* mAP
* latency
* FPS

### E5: Stability Test

Durations SHOULD include:

```text
10 minutes
30 minutes
60 minutes
```

Metrics:

* average FPS
* maximum memory usage
* abnormal exit status
* performance degradation

---

## 16. Experiment Integrity Requirements

Experimental data MUST be real.

AI agents and scripts MUST NOT fabricate:

* Precision.
* Recall.
* mAP.
* FPS.
* latency.
* CPU usage.
* GPU usage.
* memory usage.
* stability results.
* paper tables.
* paper figures.

If data is missing, write:

```text
TBD: real experiment data required
```

or:

```text
Not measured yet
```

Paper conclusions MUST be based on real measured logs.

---

## 17. Build and Dependency Requirements

The C++ project MUST use CMake.

The project SHOULD use C++17.

Likely C++ dependencies:

* OpenCV
* yaml-cpp
* ONNX Runtime C++ API
* TensorRT
* CUDA Runtime

Likely Python dependencies:

* ultralytics
* torch
* opencv-python
* numpy
* pyyaml
* pandas
* matplotlib

Heavy new dependencies MUST require explicit approval.

---

## 18. Acceptance Criteria

Minimum engineering acceptance:

* Dataset conversion works.
* YOLOv8n training works.
* ONNX export works.
* C++ YAML config works.
* C++ ONNX Runtime inference works.
* C++ TensorRT FP16 inference works on Jetson.
* Serial and pipeline modes can switch.
* Detection results can be saved.
* CSV / JSON logs can be exported.

Minimum experiment acceptance:

* Accuracy experiment completed.
* Backend comparison completed.
* Runtime mode comparison completed.
* Input size comparison completed.
* Stability test recorded.

Minimum thesis / paper acceptance:

* Architecture is clear.
* Deployment path is complete.
* Experiments are reproducible.
* Data is real.
* Claims are cautious and engineering-oriented.

---

## 19. Current TBD Items

The following items are not fixed yet:

| Item                              | Timing                            |
| --------------------------------- | --------------------------------- |
| Jetson model                      | after local ONNX Runtime baseline |
| JetPack version                   | after Jetson selected             |
| CUDA version                      | after JetPack known               |
| TensorRT version                  | after JetPack known               |
| ONNX Runtime C++ version          | before C++ integration            |
| OpenCV version                    | before C++ skeleton               |
| CMake minimum version             | before C++ skeleton               |
| TensorRT engine generation method | before Jetson deployment          |
| Resource monitoring method        | before experiments                |

Final decisions should be recorded in:

```text
docs/personal/DECISIONS.md
```

---

## 20. Final Statement

The project requirements should remain focused on:

```text
YOLOv8n industrial defect detection
→ ONNX export
→ C++ ONNX Runtime baseline
→ C++ TensorRT FP16 deployment
→ serial / pipeline comparison
→ reproducible profiling logs
→ thesis, paper, and job-seeking evidence
```
