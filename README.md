# Edge AI Industrial Defect Detection

This project develops a reproducible industrial defect-detection deployment pipeline for NVIDIA Jetson. It uses NEU-DET and YOLOv8n as the training baseline, then focuses on ONNX Runtime, TensorRT FP16, C++ inference, and serial/pipeline performance experiments.

## Technical Route

```text
NEU-DET → YOLOv8n → frozen PyTorch model → ONNX
→ C++ ONNX Runtime baseline (M0–M5 CLOSED)
→ Stage J Jetson ONNX Runtime CPU Baselines
→ Stage T TensorRT FP16
→ Stage P Serial / Pipeline profiling
```

## Current Status

Status contract: `M0–M5 CLOSED`; Stage J `COMPLETE`; Stage K Execution Plan `FINAL`; K0 Planning Freeze `COMPLETE`; K1 Platform Acceptance `PASS`; D062 `ACCEPTED`; K2/K3/K4 `COMPLETE`; K5 `FAILED_BY_GATE_REVIEW_PENDING_D063`; D063 `ADDED`. Stage K formal correctness campaign remains failed; K6 is not ready and Stage P remains required downstream scope and is not authorized before Stage K closeout.

The training and ONNX export stages are complete: nine formal training experiments were recorded, the final model was frozen, held-out test evaluation and offline archiving were completed, and the frozen ONNX model was validated. Model weights and training archives are intentionally excluded from Git; frozen deployment artifacts are identified by SHA256 in the project evidence and model contract.

The training, frozen model, ONNX export, and PyTorch/ORT validation are complete. The C++ ONNX Runtime CPU Serial Baseline M0–M5 is CLOSED; WSL2 Level A/B/C validation and the WSL2 x86_64 ORT CPU engineering baseline are complete.

Stage J Plan v0.3 is FROZEN and Stage J is COMPLETE, with its accepted limitations and final Evidence retained. Stage K has a frozen TensorRT FP16 serial execution plan, a verified platform/engine contract, and a completed K4 serial backend. The K5 tooling slice provides a backend-neutral raw tensor runner and Level B comparator; it does not close K5 or claim a formal correctness result. Stage P Pipeline remains downstream and unauthorized before Stage K closeout.

## Documentation

- [Project brief](docs/PROJECT_BRIEF.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Training final report](docs/TRAINING_FINAL_REPORT.md)
- [Model freeze record](docs/MODEL_FREEZE_RECORD.md)
- [Training archive index](docs/TRAINING_ARCHIVE_INDEX.md)
