Stage K Full Task-Level Evaluation v1 — inference phase
============================================================

Verdict
-------

READY_FOR_TASK_METRIC_EVALUATION

This phase generated final detections and per-image latency artifacts only.
No ground-truth metric was calculated.

Dataset split
-------------

  split: test
  image count: 180
  test manifest SHA256: fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8

Backend identity
----------------

  Backend                         Engine SHA256                                      TRT
  TRT FP32 noTF32                aaa37030ca1d24838e75ad6fd1a16bdeb74072d87302c1b2cef62faa3856d74f  10.3.0.30
  TRT FP16 selective M3           83e7100b01b9bb0c04dd4c41e52d6d5f61ee61d07cef82dffee173a1c692266b  10.3.0.30

  FP32 engine manifest SHA256: 86549f894802afab06221e32bab46e89d69e97eb8059befa8771d2728b2ee1a5
  FP16 engine manifest SHA256: 16f5f8bb68f95c564fc5f21b8809302bd226e0ce6a9fdd138038b659cbe7e11a

Execution validation
--------------------

  FP32 success: 180/180 (100.00%)
  FP16 success: 180/180 (100.00%)
  output schema identical: True
  NaN/Inf validation: PASS

Latency summary (application per-image timing)
-----------------------------------------------

  Backend                         mean TRT inference ms   mean E2E ms
  TRT FP32 noTF32                19.923535              26.215933
  TRT FP16 selective M3           20.111881              26.530107

Artifacts
---------

  fp32_notf32/detections.json
  fp32_notf32/latency.json
  fp32_notf32/inference_manifest.json
  fp16_selective/detections.json
  fp16_selective/latency.json
  fp16_selective/inference_manifest.json

The raw TensorRT Engine files, dataset images, and XML annotations were not
copied into the repository output.  The task runner used temporary hard links
to the frozen test images and removed them after completion.

The selective M3 identity is preserved exactly as built.  Its existing
inspection evidence classified actual execution as M3_DEGENERATED_TO_FP32;
this report does not reinterpret that engine identity.
