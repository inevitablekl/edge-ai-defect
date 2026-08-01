# Q3 Formal Calibration Report

## Verdict

`Q3_INT8_ENGINE_BUILD_PASS`

The formal TensorRT 10.3 INT8 PTQ build completed atomically. The engine was
deserialized and checked against the frozen ModelContract before publication.

## Git

- branch: `feature/jetson-tensorrt-int8`
- HEAD before this Q3 commit: `cfae3fe832b8071e88846c0a8d6d21c76796c548`
- worktree was clean at Q3 entry

## Calibration

- manifest: `results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json`
- source: `results/validation/stage_q/split_v2_deduplicated/train_manifest_v2.json`
- SHA: `f436fd9d82267174f71c2afaf575b9beef09763aa9e4fed12f054eaedefb69d9`
- source manifest SHA: `4e937507e0663ff76740b3fc6dd00552d82a3392a07a99fab17d816b7bc062b6`
- count: `1260`
- successful batches: `1260`
- images consumed: `1260`
- unreadable/skipped/failed: `0/0/0`
- batch size: `1`

Ordering is `sha256_key_permutation_v1`, seed `42`, source split `train`.

## Engine

- path: `/home/orin/edge-ai-local-models/stage_q/formal/yolov8n_neudet_trt10.3_int8_ptq_b1_640.engine`
- SHA: `8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee`

## Cache

- SHA: `05bc8175bbbf3d01d8dcf8250c94c4dd90f03cd632c3112a5a98d41c5470a0ba`
- metadata: `/home/orin/edge-ai-local-models/stage_q/formal/calibration_cache.meta.json`

Metadata includes ONNX, ModelContract, formal manifest, source manifest,
TensorRT, CUDA/L4T identity, builder flags, builder executable SHA, builder
artifact identity SHA, calibration counts, and engine/cache SHA values.

## Precision Audit

- raw layer info: `results/build/tensorrt/q3_int8_engine_v1/raw_engine_layer_info.json`
- summary: `results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json`
- confirmed_int8_compute: `262`
- confirmed_fp16_compute: `6`
- confirmed_fp32_compute: `64`
- reformat_or_copy: `124`
- mixed_or_unclassified: `30`
- inspector_visible_layers: `486`
- classification: `Q3_INT8_ENGINE_BUILD_PASS`

TensorRT `ProfilingVerbosity::kDETAILED` was enabled during the build.

## Manifest v2

- path: `/home/orin/edge-ai-local-models/stage_q/formal/engine_manifest_v2.json`
- validation: PASS
- `artifact_kind`: `tensorrt_engine`
- `backend_type`: `tensorrt_int8`
- `int8_enabled`: `true`
- `fp16_fallback_enabled`: `true`
- `host_io_dtype`: `FP32`

## Evidence

- `results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json`
- `results/build/tensorrt/q3_int8_engine_v1/raw_engine_layer_info.json`
- `results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json`
- `/home/orin/edge-ai-local-models/stage_q/formal/calibration_cache.meta.json`
- `/home/orin/edge-ai-local-models/stage_q/formal/build_summary.json`
- `/home/orin/edge-ai-local-models/stage_q/formal/engine_manifest_v2.json`

Focused CTest and independent metadata/hash validation passed.

## Scope Check

No RuntimeConfig v5, Result JSON v4, production runtime integration, accuracy
evaluation, benchmark, or Pipeline work was performed. Q2 smoke artifacts were
not used as the formal calibration cache and were not modified.

## Authorization

Q3: `AUTHORIZED`

Q4: `NOT AUTHORIZED UNTIL REVIEW`
