# Stage Q Evidence Index

## Final status

- Q1: `Q1_PLATFORM_AND_ASSET_PASS_WITH_SPLIT_REMEDIATION`
- Q2: `Q2_BUILDER_AND_SMOKE_PASS`
- Q3: `Q3_INT8_ENGINE_BUILD_PASS`
- Q4: `Q4_INT8_RUNTIME_INTEGRATION_PASS`
- Q5: `Q5_ACCURACY_EVIDENCE_VALID`, accuracy `ACCEPTABLE`
- Q6: `MATERIAL_INT8_INFERENCE_GAIN`, `NO_MATERIAL_END_TO_END_REGRESSION`
- Q7: `Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION`
- Q8: `Q8_COMPLETE_READY_FOR_MAIN_MERGE`
- Final: `STAGE_Q_COMPLETE_INT8_RECOMMENDED`

## Evidence paths

| Stage | Build / validation / benchmark / report evidence |
|---|---|
| Q1 | `results/validation/stage_q/q1_platform_asset_preflight_v1/`; `results/validation/stage_q/split_v2_deduplicated/`; `docs/personal/STAGE_Q_SPLIT_REMEDIATION_PLAN.md` |
| Q2 | `results/build/tensorrt/q2_int8_smoke_v1/`; `docs/personal/STAGE_Q2_BUILDER_IMPLEMENTATION_REPORT.md` |
| Q3 | `results/build/tensorrt/q3_int8_engine_v1/`; `docs/personal/STAGE_Q3_FORMAL_CALIBRATION_REPORT.md` |
| Q4 | `docs/personal/STAGE_Q4_RUNTIME_INTEGRATION_REPORT.md`; Q4 focused tests and runtime smoke provenance in that report |
| Q5 | `results/validation/stage_q/q5_accuracy_v1/`; `docs/personal/STAGE_Q5_ACCURACY_REPORT.md` |
| Q6 | `results/validation/stage_q/q6_serial_performance_v1/`; `docs/personal/STAGE_Q6_SERIAL_PERFORMANCE_REPORT.md` |
| Q7 | `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/`; `results/validation/stage_q/q7_confirmation_v1/attempt_001/`; `docs/personal/STAGE_Q7_PIPELINE_EVALUATION_REPORT.md` |
| Q8 | `docs/personal/STAGE_Q_FINAL_REPORT.md`; this index |

## Frozen identities

| Artifact | SHA256 |
|---|---|
| INT8 Engine | `8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee` |
| INT8 calibration cache | `05bc8175bbbf3d01d8dcf8250c94c4dd90f03cd632c3112a5a98d41c5470a0ba` |
| calibration manifest | `f436fd9d82267174f71c2afaf575b9beef09763aa9e4fed12f054eaedefb69d9` |
| Stage Q test manifest | `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194` |
| FP16 expected cycle SHA | `6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3` |
| INT8 expected cycle SHA | `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` |

## Tracked versus local-only

Tracked closeout material includes the final reports, this index, small
classification/summary JSON artifacts, Stage Q configuration and validation
tools, and source-level provenance needed to understand the authorized runs.

Local-only material includes raw datasets, ONNX and Engine binaries,
calibration cache, full per-frame Result JSON, full JSONL traces, raw
`tegrastats` logs, temporary build outputs, and other large generated runtime
artifacts. Local-only evidence remains at the paths above for audit and is not
part of the documentation closeout commit.

No evidence in this index is fabricated; unavailable measurements remain
explicit limitations in the final report.
