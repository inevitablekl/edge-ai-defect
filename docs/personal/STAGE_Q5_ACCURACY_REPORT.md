# Q5 Accuracy Report

## Verdict

`Q5_ACCURACY_EVIDENCE_VALID`

Accuracy classification: `ACCEPTABLE`.

## Git

- branch: `feature/jetson-tensorrt-int8`
- HEAD at invocation: `c24477c752fa24da280bff1b29fc01ac8a7f2287`

## Test Manifest

- path: `results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json`
- SHA256: `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194`
- image count: `180`
- source: `CorpusReplaySource`, manifest order, one cycle, maximum accepted frames 180

## Invocation

FP16 used the frozen Stage K engine:

`/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine`

INT8 used the formal Stage Q engine:

`/home/orin/edge-ai-local-models/stage_q/formal/yolov8n_neudet_trt10.3_int8_ptq_b1_640.engine`

Both invocations consumed 180/180 manifest entries with zero image failures. Timing collection was disabled; no benchmark or pipeline run was performed.

## Cycle SHA

| Backend | Expected cycle SHA | Run SHA |
|---|---|---|
| FP16 | `6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3` | `d0f5275824e2359cd80f6428bbfb7249e058eb72173bc9a124d8890bc30dd1a5` |
| INT8 | `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` | `133c44408738814a0f3dc44b443c15b1980b64643a661ae86825421a1de90532` |

## Metrics

Ground truth boxes: `442`; evaluated images: `180`; image failures: `0`; non-finite values: `0`.

| Metric | FP16 | INT8 | FP16 - INT8 |
|---|---:|---:|---:|
| Precision | 0.634731 | 0.691275 | -0.056545 |
| Recall | 0.719457 | 0.699095 | 0.020362 |
| mAP50 | 0.656024 | 0.647625 | 0.008399 |
| mAP50-95 | 0.359550 | 0.352344 | 0.007205 |
| Detection count | 501 | 447 | 54 |

Per-class AP50 / Recall:

| Class | FP16 AP50 | INT8 AP50 | Drop | FP16 Recall | INT8 Recall | Drop |
|---|---:|---:|---:|---:|---:|---:|
| crazing | 0.175984 | 0.203706 | -0.027722 | 0.337838 | 0.310811 | 0.027027 |
| inclusion | 0.628705 | 0.628752 | -0.000047 | 0.716814 | 0.707965 | 0.008850 |
| patches | 0.857681 | 0.846255 | 0.011426 | 0.887500 | 0.862500 | 0.025000 |
| pitted_surface | 0.805640 | 0.769865 | 0.035775 | 0.848485 | 0.818182 | 0.030303 |
| rolled-in_scale | 0.550053 | 0.563852 | -0.013799 | 0.680000 | 0.666667 | 0.013333 |
| scratches | 0.918082 | 0.873323 | 0.044759 | 0.925373 | 0.895522 | 0.029851 |

The maximum measured class AP50 drop was `0.044759`, and the maximum class Recall drop was `0.030303`; all required ACCEPTABLE limits passed.

## Evidence

All Q5 evidence is under:

`results/validation/stage_q/q5_accuracy_v1/`

- `fp16_result.json`
- `int8_result.json`
- `expected_fp16_cycle_sha.json`
- `expected_int8_cycle_sha.json`
- `metrics_summary.json`
- `classification_report.json`
- `evaluator_config.json`

## Scope Check

No threshold, NMS, model, engine, or dataset was modified. The invocation used the frozen test manifest and existing frozen engines. No Q6 benchmark or Q7 pipeline execution was performed.

## Authorization

Q6: `NOT AUTHORIZED UNTIL REVIEW`
