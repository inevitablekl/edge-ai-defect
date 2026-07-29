Stage K7 TensorRT Performance Benchmark v1
============================================

Verdict: K7_PERFORMANCE_COMPLETE

The frozen Stage K test split (180 images, SHA256 fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8) was replayed in
deterministic order for 100 warmup iterations and 5000 measured iterations in
each of three independent processes per backend.

Aggregate performance (15,000 measured samples per backend)
------------------------------------------------------------

                         mean inference ms   mean E2E ms   inference FPS   E2E FPS
  Strict FP32 noTF32     12.914213              18.813333       77.434062       53.153793
  Original FP16          11.164944              17.065202       89.566059       58.598780

  inference speedup (FP32 / FP16): 1.156675x
  E2E speedup (FP32 / FP16):       1.102438x

Timing definitions
------------------

Inference timing starts immediately before TensorRT enqueueV3 and ends after
the D2H cudaStreamSynchronize completes. H2D is recorded separately and is
excluded from inference timing. E2E timing starts before preprocessing and ends
after postprocessing; image decode and result serialization are excluded.

Environment and telemetry
-------------------------

The environment freeze is in environment.json. Each backend retains raw
1-second tegrastats output in tegrastats.log and per-process run directories.
If EMC or another field is absent from the raw tegrastats output, it is not
invented in this report.

Performance conclusion
----------------------

Compared with the strict FP32 TensorRT noTF32 baseline, the Original TensorRT
FP16 Engine changed measured inference latency by
13.545% and changed measured E2E latency by
9.292% (positive means reduction). These are
descriptive measurements from this frozen Jetson environment, not a universal
performance guarantee.

Accuracy limitation
-------------------

K5 task-level validation was TASK_LEVEL_FP16_ACCEPTED and K6 stability was
K6_STABILITY_PASS. This K7 benchmark does not claim bitwise raw-tensor
correctness; raw tensor correctness remains a documented limitation of the
prior validation evidence.

Artifacts
---------

  fp32_notf32/benchmark_report.json
  fp32_notf32/latency_samples.csv
  fp32_notf32/tegrastats.log
  fp32_notf32/manifest.json
  fp16_original/benchmark_report.json
  fp16_original/latency_samples.csv
  fp16_original/tegrastats.log
  fp16_original/manifest.json
  comparison_report.json
