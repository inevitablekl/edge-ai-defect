# Stage K Full Task-Level Evaluation Report

## 1. Verdict

`TASK_LEVEL_FP16_ACCEPTED`

`ORIGINAL_FP16_TASK_TIMING_FASTER`

The Original Stage K FP16 Engine is the optimization candidate. M3 remains a
diagnostic-only control because its inspected actual FP16 tactic count is zero
(`M3_DEGENERATED_TO_FP32`). No FP16 speedup is inferred from M3.

## 2. Git State

Evaluation was started at HEAD `99320d69eb10112348d792283b008eadd5517e21`.
Existing unrelated worktree changes were preserved. No reset, stash, push,
merge, tag, K6, K7, or K8 operation was performed.

## 3. Dataset and Split Identity

  source: `data/raw/NEU-DET`
  source tree SHA256: `5e0f688fb5400406533e7c8d0406bfd29d2674011a657210de18740fe161b283`
  test split: 180 images
  test manifest SHA256: `fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8`
  annotation: Pascal VOC XML
  classes: crazing, inclusion, patches, pitted_surface, rolled-in_scale, scratches

## 4. Ground Truth Conversion

Ground truth conversion passed for 180/180 image containers. The frozen test
split contains 442 raw and 442 deduplicated bbox rows; no duplicate bbox row
was present in this split. Full dataset source file hashes were verified
against the frozen source tree manifest. XML and image bytes were not modified,
and no pseudo-labels were generated.

## 5. Engine Identity

| Backend | Role | Engine SHA256 | Manifest SHA256 |
|---|---|---|---|
| TRT FP32 noTF32 | baseline | `aaa37030ca1d24838e75ad6fd1a16bdeb74072d87302c1b2cef62faa3856d74f` | `86549f894802afab06221e32bab46e89d69e97eb8059befa8771d2728b2ee1a5` |
| TRT FP16 Original Stage K | optimization candidate | `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc` | `39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63` |
| TRT M3 | diagnostic control | `83e7100b01b9bb0c04dd4c41e52d6d5f61ee61d07cef82dffee173a1c692266b` | `16f5f8bb68f95c564fc5f21b8809302bd226e0ce6a9fdd138038b659cbe7e11a5` |

All three used TensorRT 10.3.0.30 and the existing frozen preprocessing and
postprocessing configuration.

## 6. Inference Completion

  FP32 noTF32: 180/180 success
  Original FP16: 180/180 success
  M3 diagnostic: 180/180 success
  NaN/Inf: PASS for all artifacts

Original FP16 was run once. Existing FP32 and M3 artifacts were integrity
validated and were not rerun.

## 7. Dataset-Level Metrics

These are project-local evaluator results using the frozen contract; bitwise
equivalence to Ultralytics metrics is not claimed.

| Backend | Precision | Recall | mAP50 | mAP50-95 | TP | FP | FN | Predictions | GT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FP32 noTF32 | 0.631474 | 0.717195 | 0.654858 | 0.359086 | 317 | 185 | 125 | 502 | 442 |
| Original FP16 | 0.634731 | 0.719457 | 0.656024 | 0.359550 | 318 | 183 | 124 | 501 | 442 |
| M3 diagnostic | 0.631474 | 0.717195 | 0.654858 | 0.359086 | 317 | 185 | 125 | 502 | 442 |

Original FP16 minus FP32 deltas:

  precision: +0.003256
  recall: +0.002262
  mAP50: +0.001166
  mAP50-95: +0.000464

## 8. Classwise Metrics

Classwise results are retained in `classwise_metrics.json`. No class crossed
the descriptive risk trigger (>0.10 AP50 or recall absolute drop), so no
classwise-risk suffix was required.

## 9. FP32 vs Original FP16 Detection Comparison

  exact-class matched detections: 500
  FP32-only detections: 2
  Original FP16-only detections: 1
  class mismatches: 0
  mean IoU: 0.997356
  minimum IoU: 0.919460
  IoU P5/P50/P95: 0.994606 / 0.998512 / 0.999609
  confidence MAE: 0.001927
  bbox coordinate MAE: 0.041922
  bbox coordinate max absolute error: 3.793319

## 10. M3 Diagnostic Control

M3 metrics are identical to the FP32 metrics in this evaluator output. This
is consistent with its prior inspection result, but M3 is not treated as an
effective FP16 deployment candidate and no M3 speedup is reported.

## 11. Descriptive Timing

| Backend | mean inference ms | median inference ms | P95 inference ms | mean E2E ms | median E2E ms | P95 E2E ms |
|---|---:|---:|---:|---:|---:|---:|
| FP32 noTF32 | 19.923535 | 18.164710 | 25.034766 | 26.215933 | 24.891137 | 32.038113 |
| Original FP16 | 12.542225 | 12.367949 | 12.460645 | 18.843641 | 18.580690 | 19.447301 |
| M3 diagnostic | 20.111881 | 18.048969 | 25.022173 | 26.530107 | 24.865557 | 31.932825 |

Original FP16 / FP32 mean timing ratios are
1.588517x for inference and
1.391235x for E2E. These are
task-evaluation timing evidence, not formal K7 benchmark conclusions.

## 12. Raw Level B vs Task-Level Interpretation

Raw Level B correctness evidence and any K5 raw failure remain unchanged.
Task-level acceptance does not erase raw numerical failure. This evaluation
adds dataset-level evidence only.

## 13. Scope Audit

No Engine, ONNX, ModelContract, production runtime, comparator tolerance, or
K5 gate was modified. Existing 16-image historical evidence was preserved.
Engine files, dataset files, and raw tensors are not part of this commit.

## 14. Next Authorization

Original FP16 passed this experimental task-level accuracy decision and may
enter formal candidate review. K7 remains the authority for formal performance
benchmarking; K6/K8 remain according to the frozen Stage K plan. This task is
complete and stops here.
