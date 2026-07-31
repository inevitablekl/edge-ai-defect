# Q2 Builder Implementation Report

## Verdict

`Q2_BUILDER_AND_SMOKE_PASS`

The Stage Q-specific TensorRT 10.3 implicit INT8 builder compiled and completed
an independent four-image calibration smoke. The smoke engine was serialized,
deserialized, hashed, and published only after those checks completed.

## Git

- branch: `feature/jetson-tensorrt-int8`
- HEAD: recorded by the Q2 commit containing this report

## Files Changed

- `include/edge_ai_defect/stage_q/stage_q_int8_builder.hpp`
- `src/stage_q_int8_builder.cpp`
- `tools/stage_q_int8_builder.cpp`
- `tests/test_stage_q_builder.py`
- `CMakeLists.txt`
- this report

## Builder

path: `build-q2/stage_q_int8_builder` (local build output, not committed)

The builder accepts the frozen ONNX, ModelContract, and split_v2 train
manifest. It is restricted to `--artifact-purpose smoke` and
`--cache-mode force-miss`, uses batch 1, and reuses the production
`Preprocessor` for BGR/LetterBox-640/RGB/NCHW/FP32-255 input.

## Calibration

- manifest: `results/validation/stage_q/split_v2_deduplicated/train_manifest_v2.json`
- smoke manifest: `/home/orin/edge-ai-local-models/stage_q/smoke/smoke_manifest.json`
- image count: 4
- split: `train`

Manifest image SHA identities were checked before TensorRT calibration. A
duplicate-SHA and missing/invalid identity fail before build.

## Smoke Artifact

- engine: `/home/orin/edge-ai-local-models/stage_q/smoke/stage_q_smoke_int8.engine`
- cache: `/home/orin/edge-ai-local-models/stage_q/smoke/calibration.cache`
- metadata: `/home/orin/edge-ai-local-models/stage_q/smoke/calibration_cache.meta.json`
- build summary: `/home/orin/edge-ai-local-models/stage_q/smoke/build_summary.json`

Metadata includes schema version, smoke purpose, cache/engine/ONNX/contract/
manifest SHA256 values, TensorRT identity, builder flags, and builder
executable SHA256. Independent post-build verification confirmed the recorded
cache, engine, and executable hashes.

## Tests

- `cmake --build build-q2 --target stage_q_int8_builder -j2` — PASS
- `ctest --test-dir build-q2 -R stage_q_builder_focused --output-on-failure` — PASS
- focused tests: manifest parsing, duplicate SHA rejection, metadata key
  presence, and failure-path non-publication — PASS

## Validation

The smoke builder reported `Q2_BUILDER_AND_SMOKE_PASS`. Engine deserialize
passed before publication. No benchmark or accuracy measurement was run.

## Forbidden Scope Check

No formal 1260-image calibration, production runtime integration, RuntimeConfig
v5, Result JSON v4, Pipeline, benchmark, accuracy experiment, or Q3 artifact
generation was performed. Frozen ONNX, split_v2 manifests, FP16 Engine, and
ModelContract were not modified.

## Authorization

Q2: `AUTHORIZED`

Q3: `NOT AUTHORIZED UNTIL REVIEW`
