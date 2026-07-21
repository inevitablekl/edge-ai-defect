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

Status contract: `M0–M5 CLOSED`; `Stage J Plan v0.3 FROZEN`; `J0 IN PROGRESS`; `Stage J PENDING`; `Device-observed facts: pending J1`. Stage T and Stage P have not started.

The training and ONNX export stages are complete: nine formal training experiments were recorded, the final model was frozen, held-out test evaluation and offline archiving were completed, and the frozen ONNX model was validated. Model weights and training archives are intentionally excluded from Git; frozen deployment artifacts are identified by SHA256 in the project evidence and model contract.

The training, frozen model, ONNX export, and PyTorch/ORT validation are complete. The C++ ONNX Runtime CPU Serial Baseline M0–M5 is CLOSED; WSL2 Level A/B/C validation and the WSL2 x86_64 ORT CPU engineering baseline are complete.

Stage J Plan v0.3 is FROZEN and J0 Planning Freeze is IN PROGRESS. Jetson hardware execution has not started. The next stage is Jetson Orin Nano Super ONNX Runtime CPU Baselines; TensorRT FP16 belongs to later Stage T, and Pipeline belongs to later Stage P. Stage J implementation and production changes have not started.

## Documentation

- [Project brief](docs/PROJECT_BRIEF.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Training final report](docs/TRAINING_FINAL_REPORT.md)
- [Model freeze record](docs/MODEL_FREEZE_RECORD.md)
- [Training archive index](docs/TRAINING_ARCHIVE_INDEX.md)
