# D062 Exact TensorRT Engine Build Contract

## Verdict

```text
D062 ACCEPTED
K2 READY
```

This contract is frozen from the real Jetson TensorRT 10.3 environment and
the captured `trtexec --help` output. No Engine build, ONNX parsing,
`--saveEngine`, `--loadEngine`, or K2 execution was performed.

Frozen source identity:

- ONNX: `models/onnx/yolov8n_neudet_frozen.onnx`
- ONNX SHA256: `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944`
- ModelContract: `configs/model_contracts/yolov8n_neudet_frozen.yaml`
- ModelContract SHA256:
  `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190`

Frozen build semantics:

- TensorRT 10.3 `trtexec`: `/usr/src/tensorrt/bin/trtexec`
- FP16 builder mode: enabled with `--fp16`; mixed precision only
- Static batch/input: batch 1, `[1,3,640,640]`; dynamic profile flags omitted
- Host input/output: explicit `fp32:chw`
- Memory pool: `--memPoolSize=workspace:4096M`
- Build-time inference: disabled with `--skipInference`
- INT8, DLA, custom plugins and Engine build-time inference: disabled/not used
- TensorRT 8.x `--workspace` syntax: not accepted; it is absent from the
  observed TensorRT 10.3 help and must not be used

Engine artifacts are local-only under
`/home/orin/edge-ai-local-models/stage_k/`. The tracked repository records
only the manifest under `models/tensorrt/` after K2 produces and verifies a
real Engine.
