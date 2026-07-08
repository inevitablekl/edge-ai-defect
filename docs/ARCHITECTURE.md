# ARCHITECTURE.md

## 1. Purpose

This document defines the stable, core, and global architecture for:

**Edge AI Industrial Defect Detection Deployment and Optimization**

Chinese name:

**边缘 AI 工业缺陷检测部署与优化项目**

This project is an engineering deployment project, not an AI algorithm research project.

It supports:

- NEU-DET industrial defect detection
- YOLOv8n training and ONNX export
- C++ ONNX Runtime baseline inference
- C++ TensorRT FP16 optimized inference
- Serial / Pipeline runtime comparison
- Profiling and reproducible experiment logs
- Thesis, small paper, and job-seeking portfolio

---

## 2. Architecture Principles

The architecture MUST follow these principles:

- Training and deployment are separated.
- Python and C++ responsibilities are separated.
- Configuration is driven by YAML.
- C++ deployment uses CMake.
- Inference backends are isolated behind a common interface.
- Runtime modes are selected by configuration.
- Experiment results are recorded as CSV / JSON logs.
- v1 does not include GUI.
- v1 does not introduce ROS2 runtime dependency.
- v1 does not implement INT8.
- All experiment data must be real measured data.

---

## 3. Fixed Architecture Decisions

| Item | Decision |
|---|---|
| Dataset | NEU-DET / NEU Surface Defect Database |
| Model | YOLOv8n |
| Dataset split | train / val / test = 70 / 20 / 10 |
| Input sizes | 320, 416, 640 |
| Training language | Python |
| Deployment language | C++ |
| Config format | YAML |
| Build system | CMake |
| Baseline backend | ONNX Runtime |
| Optimized backend | TensorRT FP16 |
| Main platform | NVIDIA Jetson |
| Runtime modes | Serial, Pipeline |
| v1 GUI | Not implemented |
| v1 ROS2 | Interface reservation only |
| INT8 | Optional future item only |
| Logs | CSV / JSON |

---

## 4. Overall System Architecture

The system has two major sides:

```text
Training / Export Side
        |
        v
Deployment / Experiment Side
```

Training / Export Side:

* implemented in Python
* prepares dataset
* trains YOLOv8n
* exports ONNX models
* generates training and export records

Deployment / Experiment Side:

* implemented in C++
* loads YAML configuration
* runs ONNX Runtime or TensorRT inference
* supports serial and pipeline modes
* saves detection results
* records profiling logs

---

## 5. Main Technical Route

```text
NEU-DET raw dataset
        |
        v
YOLO format conversion
        |
        v
YOLOv8n training
        |
        v
best.pt
        |
        v
ONNX export
        |
        v
ONNX model
        |
        v
TensorRT FP16 engine
        |
        v
C++ inference application
        |
        v
Serial / Pipeline experiments
        |
        v
CSV / JSON logs
        |
        v
Paper tables and figures
```

---

## 6. Repository Structure

Recommended top-level structure:

```text
edge-ai-defect/
├── AGENTS.md
├── README.md
├── CMakeLists.txt
├── configs/
├── docs/
├── scripts/
├── include/
├── src/
├── tests/
├── experiments/
├── models/
├── data/
└── paper/
```

Directory responsibilities:

* `configs/`: YAML configuration files.
* `docs/`: project documents.
* `scripts/`: Python scripts for dataset conversion, training, export, and analysis.
* `include/`: C++ header files.
* `src/`: C++ source files.
* `tests/`: tests.
* `experiments/`: experiment configs, logs, results, figures, and tables.
* `models/`: model artifact placeholders.
* `data/`: dataset placeholders.
* `paper/`: paper drafts, figures, tables, and references.

Large files should not be committed unless explicitly approved:

* raw datasets
* `.pt`
* `.onnx`
* `.engine`
* videos
* generated logs
* large result images

---

## 7. Training Side Architecture

Training side is implemented in Python.

Responsibilities:

* Convert NEU-DET to YOLO format.
* Split dataset into train / val / test = 70 / 20 / 10.
* Train YOLOv8n.
* Record validation metrics.
* Export ONNX models.
* Generate export records.

Expected outputs:

```text
models/pt/yolov8n_best.pt
models/onnx/yolov8n_320.onnx
models/onnx/yolov8n_416.onnx
models/onnx/yolov8n_640.onnx
training logs
validation metrics
export records
```

Training side MUST NOT become the deployment runtime.

---

## 8. Deployment Side Architecture

Deployment side is implemented in C++.

Main executable:

```text
edge_ai_defect
```

Expected usage:

```bash
./edge_ai_defect --config configs/infer_trt_serial.yaml
```

The executable should:

* parse command-line arguments
* load YAML configuration
* create core modules
* select inference backend
* select runtime mode
* run inference
* save results
* export logs

---

## 9. Core C++ Modules

| Module            | Responsibility                                |
| ----------------- | --------------------------------------------- |
| ConfigManager     | Load and validate YAML configuration          |
| FrameSource       | Read image sequence, video, optional camera   |
| Preprocessor      | Convert image frame to inference input buffer |
| InferenceEngine   | Abstract inference backend interface          |
| ONNXRuntimeEngine | ONNX Runtime baseline inference               |
| TensorRTEngine    | TensorRT FP16 optimized inference             |
| PostProcessor     | Decode YOLOv8 output, threshold, NMS          |
| Profiler          | Record latency, FPS, and resource metrics     |
| ResultSink        | Save visualized results and detection data    |
| SerialRunner      | Sequential baseline runtime                   |
| PipelineRunner    | Multi-thread runtime                          |
| common            | Shared data structures and utilities          |

Backend-specific details MUST stay inside backend modules.

Runner logic MUST NOT contain ONNX Runtime or TensorRT-specific implementation details.

---

## 10. Core Data Structures

Suggested frame structure:

```cpp
struct Frame {
    cv::Mat image;
    int64_t frame_index;
    double timestamp_ms;
    std::string source_id;
};
```

Suggested preprocess output:

```cpp
struct PreprocessOutput {
    std::vector<float> input_tensor;
    int input_width;
    int input_height;
    int original_width;
    int original_height;
    float scale;
    int pad_x;
    int pad_y;
};
```

Suggested detection result:

```cpp
struct Detection {
    int class_id;
    std::string class_name;
    float confidence;
    float x1;
    float y1;
    float x2;
    float y2;
};

struct DetectionResult {
    int64_t frame_index;
    double timestamp_ms;
    std::vector<Detection> detections;
};
```

These structures may be adjusted during implementation, but major changes should be recorded in `docs/DECISIONS.md`.

---

## 11. Configuration Architecture

The system uses YAML as the primary configuration format.

Configuration should control:

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

Core source code should not be modified just to switch experiments.

---

## 12. Inference Backend Architecture

The project uses an abstract inference interface.

Required backends:

```text
ONNX Runtime
TensorRT FP16
```

ONNX Runtime:

* baseline backend
* loads `.onnx` model
* runs C++ ONNX Runtime inference
* provides comparison target for TensorRT

TensorRT FP16:

* optimized backend
* loads `.engine` file
* runs C++ TensorRT inference
* used for final Jetson deployment experiments

Not included in v1:

* PyTorch runtime backend
* OpenVINO
* RKNN
* TensorFlow
* NCNN

---

## 13. Runtime Architecture

Serial mode is the baseline runtime:

```text
FrameSource
→ Preprocessor
→ InferenceEngine
→ PostProcessor
→ ResultSink
→ Profiler
```

Pipeline mode is the optimized runtime:

```text
Capture Thread
→ Inference Thread
→ Output Thread
```

Pipeline queue rules:

* queue size should be configurable
* recommended queue size is 1 or 2
* when full, drop old frames and keep the latest frame
* avoid stale frame processing
* avoid unbounded memory growth

Pipeline mode may improve throughput / FPS.

Pipeline mode does not necessarily reduce single-frame end-to-end latency.

---

## 14. Preprocessing and Postprocessing Architecture

Preprocessor responsibilities:

* resize
* optional letterbox
* BGR / RGB conversion
* normalization
* HWC / CHW conversion
* input buffer preparation

PostProcessor responsibilities:

* decode YOLOv8 output
* apply confidence threshold
* apply NMS
* restore bounding boxes to original image coordinates
* generate unified detection results

Preprocessing behavior must be consistent between ONNX Runtime and TensorRT.

YOLOv8 ONNX output shape must be verified before finalizing postprocessing logic.

---

## 15. Profiler and Output Architecture

Profiler must record:

* preprocessing latency
* inference latency
* postprocessing latency
* total latency
* FPS

Profiler should record when available:

* CPU usage
* GPU usage
* memory usage

If a metric is unavailable, record:

```text
Not available
```

Output formats:

```text
CSV
JSON
```

Recommended output locations:

```text
experiments/logs/
experiments/results/
experiments/figures/
experiments/tables/
```

Paper tables and figures should be derived from real logs.

---

## 16. Experiment Architecture

The architecture must support these experiment groups:

| Experiment               | Purpose                                         |
| ------------------------ | ----------------------------------------------- |
| E1 Model accuracy        | Record Precision, Recall, mAP@0.5, mAP@0.5:0.95 |
| E2 Backend comparison    | Compare ONNX Runtime and TensorRT FP16          |
| E3 Runtime comparison    | Compare Serial and Pipeline modes               |
| E4 Input size comparison | Compare 320, 416, and 640                       |
| E5 Stability test        | Record long-running stability behavior          |

Experiment conclusions must be based on measured data.

AI agents must not fabricate experiment results.

---

## 17. Build Architecture

The C++ project uses CMake.

Expected build flow:

```bash
mkdir -p build
cd build
cmake ..
make -j$(nproc)
```

Expected executable:

```text
build/edge_ai_defect
```

CMake should handle:

* main executable
* OpenCV
* yaml-cpp
* ONNX Runtime C++ API
* TensorRT
* CUDA Runtime if required
* optional tests

CMake minimum version is TBD.

---

## 18. Extension Constraints

v1 does not implement GUI.

Forbidden in v1 unless explicitly approved:

* Qt UI
* Web UI
* browser dashboard
* interactive frontend

v1 only reserves ROS2 interface.

Forbidden in v1 unless explicitly approved:

* ROS2 package
* ROS2 runtime dependency
* ROS2 topic publishing
* ROS2 launch files

INT8 is optional future work only.

Forbidden unless explicitly approved:

* INT8 calibration flow
* INT8 calibrator
* INT8 engine generation
* INT8-specific dependencies

---

## 19. Current TBD Items

The following items must be decided later and recorded in `docs/DECISIONS.md`:

| Item                              | Status |
| --------------------------------- | ------ |
| Specific Jetson model             | TBD    |
| JetPack version                   | TBD    |
| CUDA version                      | TBD    |
| TensorRT version                  | TBD    |
| ONNX Runtime C++ version          | TBD    |
| OpenCV version                    | TBD    |
| CMake minimum version             | TBD    |
| TensorRT engine generation method | TBD    |
| Resource monitoring method        | TBD    |

AI agents must not invent these values.

---

## 20. Architecture Summary

Training side:

```text
NEU-DET
→ YOLO format conversion
→ YOLOv8n training
→ ONNX export
```

Deployment side:

```text
YAML config
→ FrameSource
→ Preprocessor
→ InferenceEngine
   ├── ONNX Runtime baseline
   └── TensorRT FP16 backend
→ PostProcessor
→ ResultSink
→ Profiler
→ CSV / JSON logs
```

Runtime modes:

```text
SerialRunner
PipelineRunner
```

The final system should demonstrate that a trained YOLOv8n industrial defect detection model can be deployed to Jetson through a C++ inference pipeline, and that backend selection, runtime architecture, input size, and stability can be evaluated through reproducible experiments.
