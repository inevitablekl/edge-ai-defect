# K2 TensorRT Engine Build and Freeze

## Verdict

```text
K2 COMPLETE
K3 READY
```

The D062 frozen command built the first formal TensorRT Engine successfully.
The Engine was inspected and independently loaded/executed successfully.

Engine:

- Path: `/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine`
- Size: `8928756` bytes
- SHA256: `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc`
- Build exit code: `0`
- Inspection exit code: `0`
- Independent load smoke exit code: `0`

Inspection confirmed:

- Input `images`: `1x3x640x640`, FP32 CHW
- Output `output0`: `1x10x8400`, FP32 CHW
- Static profile min/opt/max all `1x3x640x640`
- Build precision: `FP32+FP16`
- Workspace pool: `4096 MiB`
- INT8 disabled
- DLA disabled
- No custom or dynamic plugin dependency observed

The tracked manifest is
`models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json`. The Engine
itself remains local-only and is not committed.

The independent one-second smoke emitted a GPU compute variance warning. It
passed and is retained as load/execution evidence, not as a formal performance
benchmark.
