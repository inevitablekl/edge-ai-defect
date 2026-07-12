# Edge AI Industrial Defect Detection

This project develops a reproducible industrial defect-detection deployment pipeline for NVIDIA Jetson. It uses NEU-DET and YOLOv8n as the training baseline, then focuses on ONNX Runtime, TensorRT FP16, C++ inference, and serial/pipeline performance experiments.

## Technical Route

```text
NEU-DET → YOLOv8n → frozen PyTorch model → ONNX
→ C++ ONNX Runtime baseline → TensorRT FP16 → Jetson
→ serial/pipeline profiling
```

## Current Status

The training stage is complete: nine formal experiments were recorded, the final model was frozen, and held-out test evaluation and offline archiving were completed. Model weights and training archives are intentionally excluded from Git. The canonical local model is `models/pytorch/yolov8n_neudet_frozen.pt`, identified by the SHA256 recorded in the freeze documentation.

The current next stage is ONNX export followed by PyTorch/ONNX Runtime consistency validation and the ONNX Runtime deployment baseline.

## Documentation

- [Project brief](docs/PROJECT_BRIEF.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Training final report](docs/TRAINING_FINAL_REPORT.md)
- [Model freeze record](docs/MODEL_FREEZE_RECORD.md)
- [Training archive index](docs/TRAINING_ARCHIVE_INDEX.md)
