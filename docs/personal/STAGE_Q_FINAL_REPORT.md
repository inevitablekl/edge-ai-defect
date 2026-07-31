# Stage Q Final Report

## 1. Research Question

TensorRT INT8 PTQ是否在保持检测精度条件下提升Jetson端推理性能。

Final classification:

`STAGE_Q_COMPLETE_INT8_RECOMMENDED`

## 2. Experimental Setup

- Device: Jetson Orin Nano Super
- TensorRT: 10.3
- Model: YOLOv8n frozen ONNX
- Batch: 1
- Host I/O: FP32
- INT8 mode: INT8 + FP16 mixed precision
- Runtime backends: TensorRT FP16 and TensorRT INT8
- Runtime modes: Serial and bounded Pipeline

## 3. Dataset Contract

`split_v1` is the historical split: train 1260, val 360, test 180, with the
historical train/val content duplicate retained as historical context.

`split_v2_deduplicated` is the Stage Q authority after split remediation:

| Split | Images | Boxes | Manifest SHA256 |
|---|---:|---:|---|
| train | 1260 | 2916 | `4e937507e0663ff76740b3fc6dd00552d82a3392a07a99fab17d816b7bc062b6` |
| val | 359 | 825 | `4be24ebe0a6b8c7e3b75840bd9bab8f67d72b1608e97c21172ce7eb9a6713dd9` |
| test | 180 | 442 | `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194` |

The remediation removed the duplicated-content validation entry while
preserving the test corpus used by Stage Q accuracy and performance evidence.
Path and image-content SHA isolation passed for the v2 manifests.

## 4. INT8 Build Result

- Engine SHA256: `8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee`
- Calibration cache SHA256: `05bc8175bbbf3d01d8dcf8250c94c4dd90f03cd632c3112a5a98d41c5470a0ba`
- Calibration manifest SHA256: `f436fd9d82267174f71c2afaf575b9beef09763aa9e4fed12f054eaedefb69d9`
- Calibration source: train, 1260 images, batch 1, seed 42, deterministic SHA256 ordering
- confirmed_int8_compute: `262`
- confirmed_fp16_compute: `6`
- confirmed_fp32_compute: `64`
- Q3 result: `Q3_INT8_ENGINE_BUILD_PASS`

## 5. Accuracy Result

Evaluated on 180 test images and 442 ground-truth boxes.

| Metric | FP16 | INT8 | FP16 − INT8 |
|---|---:|---:|---:|
| Precision | 0.634731 | 0.691275 | -0.056545 |
| Recall | 0.719457 | 0.699095 | 0.020362 |
| mAP50 | 0.656024 | 0.647625 | 0.008399 |
| mAP50-95 | 0.359550 | 0.352344 | 0.007205 |

| Class | FP16 AP50 | INT8 AP50 | FP16 Recall | INT8 Recall |
|---|---:|---:|---:|---:|
| crazing | 0.175984 | 0.203706 | 0.337838 | 0.310811 |
| inclusion | 0.628705 | 0.628752 | 0.716814 | 0.707965 |
| patches | 0.857681 | 0.846255 | 0.887500 | 0.862500 |
| pitted_surface | 0.805640 | 0.769865 | 0.848485 | 0.818182 |
| rolled-in_scale | 0.550053 | 0.563852 | 0.680000 | 0.666667 |
| scratches | 0.918082 | 0.873323 | 0.925373 | 0.895522 |

Accuracy conclusion: `ACCEPTABLE`.

## 6. Serial Performance

- Inference speedup: `1.269856`
- INT8/FP16 throughput ratio: `1.172850`
- Mean end-to-end latency ratio: `0.852194`
- P95 end-to-end latency ratio: `0.852066`
- Classification: `MATERIAL_INT8_INFERENCE_GAIN`
- End-to-end status: `NO_MATERIAL_END_TO_END_REGRESSION`

## 7. Pipeline Performance

- Frozen queue capacity: `1`
- Frozen drop policy: `block`
- INT8/FP16 paired throughput ratio: `1.012575`
- Runtime status: no crash, deadlock, inference failure, drop, queue lifecycle failure, or worker join failure
- Q7 classification: `Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION`

The required INT8 300-second confirmation passed with 126 complete cycles,
22680 processed frames, 319.674510239 active wall seconds, and zero partial
cycles. All complete-cycle hashes matched the Q5 INT8 authority.

## 8. Final Classification

`STAGE_Q_COMPLETE_INT8_RECOMMENDED`

## 9. Limitations

- The INT8 build uses TensorRT 10.3 legacy implicit INT8 calibration.
- This result does not represent the recommended TensorRT 11 route.
- QAT, ModelOpt, and Q-DQ were not tested.
- Dynamic shapes, batch sizes greater than 1, and DLA were not tested.
- The 300-second confirmation is not an industrial certification stability test.
- Thermal throttle status was unavailable in the formal serial evidence and is retained as a limitation.

## Evidence

See [STAGE_Q_EVIDENCE_INDEX.md](STAGE_Q_EVIDENCE_INDEX.md).

## Scope and Authorization

No new feature, experiment, benchmark, accuracy rerun, Pipeline rerun,
model/engine/calibration/threshold change, merge, tag, or push was performed
for Q8. Q8 is documentation-only closeout.

Merge: `NOT AUTHORIZED`

Tag: `NOT AUTHORIZED`
