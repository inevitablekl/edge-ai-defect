## 1. Purpose

This document defines the global rules for AI coding agents working on this repository.

Project name:

**Edge AI Industrial Defect Detection Deployment and Optimization**

Chinese name:

**边缘 AI 工业缺陷检测部署与优化项目**

This project serves:

- Electronic Information graduate thesis.
- Small engineering paper.
- Job-seeking portfolio for embedded / edge AI deployment roles.

This is an engineering deployment project, not an AI algorithm research project.

---

## 2. Core Positioning

The project is:

> A Jetson-based edge AI deployment and real-time inference optimization system for industrial visual defect detection.

The project focuses on:

- Industrial defect detection.
- YOLOv8n training and export.
- ONNX Runtime baseline.
- TensorRT FP16 optimized inference.
- C++ deployment pipeline.
- Serial / pipeline runtime comparison.
- Profiling and reproducible experiments.

The project does not focus on:

- Novel detection algorithm design.
- New neural network architecture.
- Large-scale data annotation.
- Full robotics system.
- GUI-heavy application.
- Multi-platform deployment.

---

## 3. Fixed Decisions

| Item | Decision |
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
| Main deployment platform | NVIDIA Jetson |
| Runtime modes | Serial, Pipeline |
| v1 GUI | Not implemented |
| v1 ROS2 | Interface reservation only |
| INT8 | Optional future optimization only |
| Log formats | CSV / JSON |

---

## 4. Main Technical Route

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

Python is used for:

* Dataset conversion.
* Dataset split.
* Training.
* ONNX export.
* Experiment result summary.
* Paper table / figure generation.

C++ is used for:

* YAML configuration loading.
* Frame input.
* Preprocessing.
* ONNX Runtime inference.
* TensorRT inference.
* YOLOv8 postprocessing.
* Profiling.
* Result output.
* SerialRunner.
* PipelineRunner.
* Command-line deployment.

Python must not become the main deployment runtime.

---

## 5. Repository Structure

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
* `scripts/`: Python scripts for dataset, training, export, and analysis.
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

## 6. Core C++ Modules

The deployment system should be organized around these modules:

| Module            | Responsibility                                |
| ----------------- | --------------------------------------------- |
| ConfigManager     | Load and validate YAML configuration          |
| FrameSource       | Read image sequence, video, optional camera   |
| Preprocessor      | Resize, normalize, layout conversion          |
| InferenceEngine   | Abstract inference backend interface          |
| ONNXRuntimeEngine | ONNX Runtime baseline inference               |
| TensorRTEngine    | TensorRT FP16 inference                       |
| PostProcessor     | Decode YOLOv8 output, threshold, NMS          |
| Profiler          | Record latency, FPS, resource usage           |
| ResultSink        | Save detection results and visualized outputs |
| SerialRunner      | Sequential baseline runtime                   |
| PipelineRunner    | Multi-thread runtime                          |

Backend-specific logic must stay inside backend modules.

Runner logic must not contain ONNX Runtime or TensorRT-specific implementation details.

---

## 7. Runtime Rules

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

* Queue size should be configurable.
* Recommended queue size is 1 or 2.
* When the queue is full, drop old frames and keep the latest frame.
* Avoid stale frame processing.
* Avoid unbounded memory growth.

Important:

Pipeline mode may improve throughput / FPS.

Pipeline mode does not necessarily reduce single-frame end-to-end latency.

Do not claim that pipeline mode always reduces latency.

---

## 8. Configuration Rules

The project uses YAML as the primary configuration format.

Core behavior should be controlled by configuration, not hardcoded source changes.

Configurable items should include:

* backend
* runtime mode
* model path
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

Invalid configuration must fail with clear error messages.

---

## 9. v1 Scope

v1 must include:

* NEU-DET dataset conversion.
* YOLOv8n training.
* ONNX export.
* C++ command-line inference application.
* YAML configuration.
* ONNX Runtime backend.
* TensorRT FP16 backend.
* SerialRunner.
* PipelineRunner.
* Profiler.
* CSV / JSON logs.
* Image / video result output.

v1 must not include unless explicitly approved:

* Qt GUI.
* Web UI.
* Full ROS2 package.
* ROS2 runtime dependency.
* ROS2 topic publishing.
* INT8 calibration.
* INT8 engine generation.
* RK3588 / RKNN deployment.
* Self-designed detection model.
* SLAM.
* Navigation.
* Robotic arm control.
* Full embodied intelligence system.

---

## 10. Experiment Integrity

Experimental data must be real.

AI agents must never fabricate:

* Precision.
* Recall.
* mAP.
* FPS.
* Latency.
* CPU usage.
* GPU usage.
* Memory usage.
* Power usage.
* Stability results.
* Paper tables.
* Paper figures.

If data is unavailable, write:

```text
TBD: real experiment data required
```

or:

```text
Not measured yet
```

All paper conclusions must be based on real measured logs.

---

## 11. Codex Working Rules

Codex must work in small, reviewable tasks.

A good task is:

```text
Implement ConfigManager to load YAML and validate required fields.
```

A bad task is:

```text
Build the whole project.
```

Each coding task should include:

* changed files
* build command
* run command
* expected input
* expected output
* verification method

Codex must not:

* rewrite unrelated files
* perform large refactors without approval
* introduce heavy dependencies without explanation
* invent experiment results
* add GUI / ROS2 / INT8 / RKNN by itself
* silently change architecture
* mix training logic into deployment runtime

The project owner must review diffs and understand key modules.

---

## 12. Documentation Priority

Priority order:

```text
AGENTS.md
> docs/DECISIONS.md
> docs/PROJECT_BRIEF.md
> docs/ARCHITECTURE.md
> docs/REQUIREMENTS.md
> docs/TASKS.md
> README.md
```

Major technical decisions must be recorded in:

```text
docs/DECISIONS.md
```

---

## 13. Current TBD Items

The following items must not be invented by AI agents:

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

When finalized, these items should be recorded in `docs/DECISIONS.md`.

---

## 14. Final Rule

Keep the project:

```text
small enough to finish
real enough to defend
technical enough for thesis
practical enough for interviews
```

Prefer:

* working system over large unfinished design
* real logs over fake tables
* clear engineering over vague AI terminology
* reproducible experiments over one-time demo
* understandable code over clever code
