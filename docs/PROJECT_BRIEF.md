## 1. Project Name

English name:

**Edge AI Industrial Defect Detection Deployment and Optimization**

Chinese name:

**边缘 AI 工业缺陷检测部署与优化项目**

Repository name:

```text
edge-ai-defect
```

---

## 2. Project Background

This project is created for:

* Electronic Information graduate thesis.
* Small engineering paper.
* Job-seeking portfolio.

The project owner has a background in:

* embedded software
* semiconductor / equipment software
* Qt / device-side software
* basic YOLO edge deployment exposure

Target career direction:

```text
Embedded Software Engineer | Edge AI Deployment
```

Chinese positioning:

```text
嵌入式软件工程师｜边缘 AI 部署方向
```

This project does not position the owner as a core AI algorithm researcher.

It focuses on engineering deployment, inference acceleration, runtime architecture, profiling, and reproducible experiments.

---

## 3. Core Positioning

The project is:

> A Jetson-based edge AI deployment and real-time inference optimization system for industrial visual defect detection.

The project emphasizes:

* industrial defect detection
* YOLOv8n training and export
* ONNX Runtime baseline
* TensorRT FP16 optimized inference
* C++ deployment pipeline
* serial / pipeline runtime comparison
* latency, FPS, and resource profiling
* paper-oriented experiment design

The project does not emphasize:

* novel detection algorithm
* self-designed neural network
* large-scale data annotation
* GUI-heavy application
* full robotics system
* RK3588 / RKNN dual-platform route
* VLA / embodied intelligence system

---

## 4. Project Motivation

Industrial visual inspection is a typical edge AI scenario.

A trained model alone is not enough for real deployment.

A deployable edge AI system must handle:

* model format conversion
* inference backend integration
* target hardware deployment
* preprocessing and postprocessing
* runtime scheduling
* performance profiling
* experiment logging
* stability verification

Therefore, this project builds a complete engineering path from YOLOv8n training to Jetson TensorRT FP16 deployment.

---

## 5. Main Objectives

### 5.1 Graduation Project Objective

Build a runnable, demonstrable, and explainable edge AI industrial defect detection system.

The system should support:

* NEU-DET dataset preparation
* YOLOv8n training
* ONNX export
* C++ inference application
* ONNX Runtime baseline
* TensorRT FP16 inference
* serial runtime mode
* pipeline runtime mode
* performance profiling
* CSV / JSON logs
* image / video result output
* command-line execution

---

### 5.2 Small Paper Objective

Produce a small engineering paper around:

```text
Edge AI deployment and real-time inference optimization for industrial defect detection
```

The paper should focus on:

* Jetson edge deployment
* TensorRT FP16 acceleration
* ONNX Runtime vs TensorRT comparison
* serial mode vs pipeline mode comparison
* input size comparison
* latency, FPS, and resource usage
* basic stability testing

The paper should not claim:

* novel algorithm design
* new network architecture
* state-of-the-art performance
* universal superiority

---

### 5.3 Job-Seeking Objective

The project should support applications for:

* Embedded Software Engineer
* Edge AI Deployment Engineer
* Industrial Vision Software Engineer
* Semiconductor Equipment Software Engineer
* Robotics Perception Engineer
* Jetson / TensorRT / C++ deployment-related roles

The project should demonstrate ability to:

* train and export a lightweight detection model
* deploy model on edge hardware
* use ONNX Runtime as baseline
* use TensorRT FP16 for acceleration
* implement a C++ inference pipeline
* compare runtime modes
* measure and analyze latency, FPS, and resource usage
* explain engineering trade-offs

---

## 6. Fixed Technical Decisions

| Item                 | Decision                              |
| -------------------- | ------------------------------------- |
| Main dataset         | NEU-DET / NEU Surface Defect Database |
| Main model           | YOLOv8n                               |
| Dataset split        | train / val / test = 70 / 20 / 10     |
| Input sizes          | 320, 416, 640                         |
| Training language    | Python                                |
| Deployment language  | C++                                   |
| Configuration format | YAML                                  |
| Build system         | CMake                                 |
| Baseline backend     | ONNX Runtime                          |
| Optimized backend    | TensorRT FP16                         |
| Main platform        | NVIDIA Jetson                         |
| Runtime modes        | Serial, Pipeline                      |
| v1 GUI               | Not implemented                       |
| v1 ROS2              | Interface reservation only            |
| INT8                 | Optional future optimization only     |
| Logs                 | CSV / JSON                            |

---

## 7. Hardware Context

### 7.1 Local Development PC

GPU:

```text
GTX1050Ti
```

Purpose:

* code development
* C++ compilation
* basic ONNX Runtime verification
* lightweight local testing

It is not the final paper experiment platform.

---

### 7.2 Cloud Training Resource

GPU:

```text
RTX 3090
```

Purpose:

* YOLOv8n training
* model validation
* ONNX export
* training record generation

It is not the edge deployment experiment platform.

---

### 7.3 Jetson Device

Purpose:

* final TensorRT FP16 deployment
* backend comparison
* serial / pipeline comparison
* input size comparison
* stability testing
* paper-level performance data collection

Current status:

```text
Specific Jetson model: TBD
JetPack version: TBD
CUDA version: TBD
TensorRT version: TBD
```

---

## 8. Main Technical Route

```text
NEU-DET dataset
→ YOLO format conversion
→ YOLOv8n training with Python
→ best.pt
→ ONNX export
→ C++ ONNX Runtime baseline
→ C++ TensorRT FP16 optimized inference
→ Jetson real-time inference
→ Serial / Pipeline comparison
→ CSV / JSON experiment logs
→ Paper tables and figures
```

The project separates:

* Python training side
* C++ deployment side
* YAML configuration
* experiment logs
* paper outputs

---

## 9. Dataset Scope

Main dataset:

```text
NEU-DET / NEU Surface Defect Database
```

Reasons:

* industrial defect detection scenario
* manageable data scale
* suitable for object detection
* fits thesis and paper narrative
* avoids anomaly detection / segmentation complexity

Dataset split:

```text
train / val / test = 70 / 20 / 10
```

The split must be reproducible.

---

## 10. Model Scope

Main model:

```text
YOLOv8n
```

Reasons:

* lightweight
* mature ecosystem
* suitable for Jetson deployment
* easy to train and export
* appropriate for engineering project positioning

Expected artifacts:

* `best.pt`
* `.onnx`
* `.engine`
* training logs
* validation metrics
* export records

---

## 11. Deployment Scope

Deployment language:

```text
C++
```

The deployment application should support:

* YAML configuration loading
* image sequence input
* video file input
* preprocessing
* ONNX Runtime inference
* TensorRT FP16 inference
* YOLOv8 postprocessing
* serial runtime mode
* pipeline runtime mode
* profiling
* result output
* command-line execution

v1 does not depend on GUI or ROS2.

---

## 12. Runtime Scope

Serial mode is the baseline:

```text
Frame input
→ Preprocess
→ Inference
→ Postprocess
→ Output
→ Log
```

Pipeline mode is the optimized runtime:

```text
Capture Thread
→ Inference Thread
→ Output Thread
```

Pipeline rules:

* queue size should be configurable
* recommended queue size is 1 or 2
* when full, drop old frames and keep the latest frame
* avoid stale frame processing
* avoid unbounded memory growth

Important:

Pipeline mode may improve throughput / FPS.

Pipeline mode does not necessarily reduce single-frame end-to-end latency.

---

## 13. Experiment Scope

The project should support:

1. Model accuracy experiment.
2. ONNX Runtime vs TensorRT FP16 comparison.
3. Serial mode vs pipeline mode comparison.
4. Input size comparison.
5. Stability test.

Key metrics:

* Precision
* Recall
* mAP@0.5
* mAP@0.5:0.95
* average latency
* p50 latency
* p95 latency
* FPS
* memory usage
* abnormal exit status

All experiment data must be real measured data.

---

## 14. v1 Must Have

v1 must include:

* dataset conversion
* YOLOv8n training
* ONNX export
* C++ command-line application
* YAML configuration
* ONNX Runtime backend
* TensorRT FP16 backend
* SerialRunner
* PipelineRunner
* Profiler
* CSV / JSON logs
* image / video result output
* basic experiment data

---

## 15. v1 Not Included

v1 does not include:

* Qt GUI
* Web UI
* full ROS2 package
* ROS2 topic publishing
* INT8 quantization
* RK3588 / RKNN
* self-designed detection model
* SLAM
* navigation
* robotic arm control
* full embodied intelligence system

---

## 16. Success Criteria

Engineering success:

* command-line inference works
* YAML configuration works
* ONNX Runtime backend works
* TensorRT FP16 backend works on Jetson
* serial and pipeline modes can switch
* result images can be saved
* CSV / JSON logs can be exported

Experiment success:

* accuracy metrics are recorded
* backend comparison is completed
* runtime mode comparison is completed
* input size comparison is completed
* stability test is recorded

Paper success:

* architecture is clear
* experiments are reproducible
* data is real
* claims are cautious and engineering-oriented

Job-seeking success:

* owner can explain the full route
* owner can explain TensorRT FP16
* owner can explain serial / pipeline
* owner can explain FPS vs latency
* owner can explain experiment conclusions

---

## 17. Main Risks

| Risk                         | Control                                   |
| ---------------------------- | ----------------------------------------- |
| TensorRT C++ complexity      | Build ONNX Runtime baseline first         |
| Jetson environment mismatch  | Record JetPack / CUDA / TensorRT versions |
| YOLOv8 output decoding error | Verify ONNX output shape                  |
| Pipeline metric confusion    | Separate FPS and latency                  |
| Codex overengineering        | Use small tasks and review diffs          |
| Fake experiment data         | Use only real logs                        |
| Scope expansion              | Keep GUI / ROS2 / INT8 outside v1         |

---

## 18. Current TBD Items

| Item                              | Timing                   |
| --------------------------------- | ------------------------ |
| Jetson model                      | After local baseline     |
| JetPack version                   | After Jetson selected    |
| CUDA version                      | After JetPack known      |
| TensorRT version                  | After JetPack known      |
| ONNX Runtime C++ version          | Before C++ integration   |
| OpenCV version                    | Before C++ skeleton      |
| CMake minimum version             | Before C++ skeleton      |
| TensorRT engine generation method | Before Jetson deployment |
| Resource monitoring method        | Before experiments       |

---

## 19. Final Summary

The core value of this project is:

> Deploy a trained YOLOv8n industrial defect detection model to Jetson with C++ and TensorRT FP16, and evaluate backend, runtime architecture, input size, and stability through reproducible experiments.

The project should remain small, real, measurable, and explainable.
