# Edge AI Industrial Defect Detection

This project develops a reproducible industrial defect-detection deployment pipeline for NVIDIA Jetson. It uses NEU-DET and YOLOv8n as the training baseline, then focuses on ONNX Runtime, TensorRT FP16, C++ inference, and serial/pipeline performance experiments.

## Technical Route

```text
NEU-DET → YOLOv8n → frozen PyTorch model → ONNX
→ C++ ONNX Runtime baseline (M0–M5 CLOSED)
→ Stage J Jetson ONNX Runtime CPU Baselines (COMPLETE)
→ Stage K TensorRT FP16 Serial Deployment (COMPLETE)
→ Stage P Bounded Serial / Pipeline Runtime (P0 freeze)
```

## Current Status

Status contract: `M0–M5 CLOSED`; Stage J `COMPLETE`; Stage K `COMPLETE`;
Original TensorRT FP16 is the accepted serial deployment candidate based on
task-level accuracy, K6 stability, and K7 formal serial performance. Raw
TensorRT Level B remains `FAIL — retained known limitation` under D066.
Stage P Execution Plan v1.2 is `FINAL`; P0 Planning Freeze completes in the
commit containing this changeset. P1 is
`NOT_AUTHORIZED_UNTIL_P0_COMMIT_IS_REVIEWED`.

The training and ONNX export stages are complete: nine formal training experiments were recorded, the final model was frozen, held-out test evaluation and offline archiving were completed, and the frozen ONNX model was validated. Model weights and training archives are intentionally excluded from Git; frozen deployment artifacts are identified by SHA256 in the project evidence and model contract.

The training, frozen model, ONNX export, and PyTorch/ORT validation are complete. The C++ ONNX Runtime CPU Serial Baseline M0–M5 is CLOSED; WSL2 Level A/B/C validation and the WSL2 x86_64 ORT CPU engineering baseline are complete.

Stage J Plan v0.3 is FROZEN and Stage J is COMPLETE, with its accepted
limitations and final Evidence retained. Stage K is complete and its
historical Evidence remains unchanged. Stage P is the next bounded execution
route: four workers, three bounded SPSC queues, one inference worker,
`drop_policy=block`, deterministic Directory/VideoFile input, and exact final
Detection identity. No Stage P production implementation has started.

## Documentation

- [Project brief](docs/PROJECT_BRIEF.md)
- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Stage P Execution Plan v1.2](docs/personal/STAGE_P_EXECUTION_PLAN.md)
- [Stage P Task Cards](docs/personal/STAGE_P_TASK_CARDS.md)
- [Training final report](docs/TRAINING_FINAL_REPORT.md)
- [Model freeze record](docs/MODEL_FREEZE_RECORD.md)
- [Training archive index](docs/TRAINING_ARCHIVE_INDEX.md)

## Stage K Final Status

Stage K is final and frozen at commit
`d4b50739c2f5f1db9ba7b48e653618b2af9cd98a`. The final deployment candidate is
the Original TensorRT FP16 Engine, accepted using task-level accuracy,
stability, and performance while retaining the raw TensorRT Level B
limitation. Post-finalization cleanup is recorded in
`results/validation/stage_k_cleanup_audit_v1/`; diagnostic investigations are
preserved under `results/archive/stage_k_diagnostics_v1/`. The Stage K8 final
summary is at `results/validation/stage_k8/final_summary_v1/`.

## Stage P P0 Status

P0 freezes documentation, baseline identities, and the
`feature/jetson-pipeline-runtime` branch only. It does not modify production
source, headers, CMake, tests, configs, Engine, or historical Evidence. The
next possible step is P1 contract implementation after explicit user review
and authorization.
