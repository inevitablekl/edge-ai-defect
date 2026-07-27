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

Status contract: `M0–M5 CLOSED`; Stage J `COMPLETE`; Stage K Execution Plan `FINAL`; K0 Planning Freeze `COMPLETE_AT_THE_COMMIT_CONTAINING_THIS_CHANGESET`; K1 Platform Acceptance `READY_AFTER_K0_FREEZE_COMMIT`. Current planning baseline: `e49f28dd60a49493538d1fd65e5e8fd81676e277`; Stage P remains required downstream scope and is not authorized before Stage K closeout.

The training and ONNX export stages are complete: nine formal training experiments were recorded, the final model was frozen, held-out test evaluation and offline archiving were completed, and the frozen ONNX model was validated. Model weights and training archives are intentionally excluded from Git; frozen deployment artifacts are identified by SHA256 in the project evidence and model contract.

The training, frozen model, ONNX export, and PyTorch/ORT validation are complete. The C++ ONNX Runtime CPU Serial Baseline M0–M5 is CLOSED; WSL2 Level A/B/C validation and the WSL2 x86_64 ORT CPU engineering baseline are complete.

Stage J Plan v0.3 is FROZEN and Stage J is COMPLETE, with its accepted limitations and final Evidence retained. Stage K K0 has frozen the TensorRT FP16 serial execution plan; K1 has not executed, and no TensorRT Engine or backend has been implemented. TensorRT Engine Build is not authorized before K1 PASS and D062 acceptance. Stage K production implementation is not authorized before K3; Stage P Pipeline remains downstream and unauthorized before Stage K closeout.

## Documentation

- [Project brief](docs/PROJECT_BRIEF.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Training final report](docs/TRAINING_FINAL_REPORT.md)
- [Model freeze record](docs/MODEL_FREEZE_RECORD.md)
- [Training archive index](docs/TRAINING_ARCHIVE_INDEX.md)
