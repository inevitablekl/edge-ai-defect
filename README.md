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

Status contract: `M0–M5 CLOSED`; `Stage J J0–J3 COMPLETE`; `J3 COMPLETE_WITH_ACCEPTED_THIRD_PARTY_LIMITATION`; `J4 COMPLETE_WITH_ACCEPTED_J4_2_LIMITATION`; `J4.1 COMPLETE`; `J4.2 COMPLETE_WITH_ACCEPTED_CROSS_ARCH_NUMERICAL_LIMITATION`; `J4.3 COMPLETE`; `J4.4 PASS_WITH_ACCEPTED_J4_2_LIMITATION`; `D048 Accepted`. Current HEAD: `ee2ff2546736c8349d0e34cffe547f1f68690cb6`. Stage T (TensorRT FP16) and Stage P (Pipeline) have not started.

The training and ONNX export stages are complete: nine formal training experiments were recorded, the final model was frozen, held-out test evaluation and offline archiving were completed, and the frozen ONNX model was validated. Model weights and training archives are intentionally excluded from Git; frozen deployment artifacts are identified by SHA256 in the project evidence and model contract.

The training, frozen model, ONNX export, and PyTorch/ORT validation are complete. The C++ ONNX Runtime CPU Serial Baseline M0–M5 is CLOSED; WSL2 Level A/B/C validation and the WSL2 x86_64 ORT CPU engineering baseline are complete.

Stage J Plan v0.3 is FROZEN and J0 Planning Freeze is COMPLETE. Jetson hardware execution has completed J1–J4, including the formal ONNX Runtime 1.23.2 aarch64 CPU SDK build, native application build, RuntimeConfig v2, ORT options, OpenCV policy, trace, portable-control validation, and J4 evidence consolidation. J4.2 retains its strict cross-architecture numerical limitation under Accepted D048. The next authorized task is `J5.1 Benchmark Python Reference Preparation`; TensorRT FP16 belongs to later Stage T, and Pipeline belongs to later Stage P.

## Documentation

- [Project brief](docs/PROJECT_BRIEF.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Training final report](docs/TRAINING_FINAL_REPORT.md)
- [Model freeze record](docs/MODEL_FREEZE_RECORD.md)
- [Training archive index](docs/TRAINING_ARCHIVE_INDEX.md)
