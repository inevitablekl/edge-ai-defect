# Q4 Runtime Integration Report

## Verdict

`Q4_INT8_RUNTIME_INTEGRATION_PASS`

## Git

- branch: `feature/jetson-tensorrt-int8`
- Q4 entry HEAD: `8e0c105316070b7c68cf856ec1c7ae55bd89168f`
- Q4 commit: recorded by the commit containing this report

## Files Changed

- RuntimeConfig schema 5 parsing and `tensorrt_int8` dispatch
- TensorRT Manifest v1/v2 validation
- shared `TensorRtEngine` INT8 selection
- Result JSON v4 precision/calibration mapping
- Q4 focused tests and smoke configurations

No new TensorRT engine class, runner, postprocessor, or pipeline framework was
added.

## RuntimeConfig v5

PASS. `schema_version: 5` accepts `backend.type: tensorrt_int8`, preserves the
existing `tensorrt_fp16` path, and dispatches through the existing
`TensorRtEngine`, `InferenceEngineFactory`, and `SerialRunner`.

## Manifest

- v1: PASS; historical FP16 manifest loaded unchanged.
- v2: PASS; validation covered schema/backend, INT8 and FP16 fallback flags,
  FP32 host I/O, engine/ONNX/ModelContract/cache/audit SHA values, cache
  metadata, formal train calibration provenance, and positive INT8 compute.

Validated formal manifest:

`/home/orin/edge-ai-local-models/stage_q/formal/engine_manifest_v2.json`

## Result JSON v4

- FP16: historical Result JSON v3 behavior preserved; no `precision` or
  `calibration` object emitted.
- INT8: Result JSON v4 emitted `precision.engine_compute_mode`,
  `int8_enabled`, `fp16_enabled`, `host_io_dtype`, and calibration provenance
  including algorithm, train split, 1260 images, manifest/cache/cache-metadata
  SHA values.

## Tests

- `q4_runtime_integration_focused`: PASS
- `runtime_config`: PASS
- `result_sinks`: PASS
- historical `test_tensorrt_engine`: PASS
- INT8 one-image runtime smoke: PASS
- FP16 one-image historical runtime smoke: PASS

Smoke outputs:

- `/tmp/q4_int8_runtime_smoke_result.json`
- `/tmp/q4_fp16_runtime_smoke_result.json`

## Scope Check

No Q5 accuracy evaluation, Q6 benchmark, Q7 pipeline run, INT8 engine rebuild,
calibration modification, or dataset modification was performed.

## Authorization

Q4: `AUTHORIZED`

Q5: `NOT AUTHORIZED UNTIL REVIEW`
