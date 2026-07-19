Identity
========
Consolidation Evidence ID: 20260719_da86e53
Source commit: da86e53d92c62ff03f4fe2aaf6328fb5f051519c
Branch: feature/cpp-onnxruntime
Status: PASS
State: active_consolidation_for_m5_6

Purpose
-------
This remediation packages and verifies existing Evidence only; no detection result or performance sample is generated.
The previous 20260719_c24eefa consolidation is historical_invalidated because its provenance contained 6/15 command records.

Referenced Evidence
-------------------
- Level C: results/validation/level_c/20260719_1073fa8 (unchanged).
- Benchmark: results/benchmark/ort_cpu/20260719_850252b (unchanged).

Correctness Result
------------------
Level C: 16/16 PASS, 54 detections, per-class [4, 28, 7, 4, 5, 6]. Python and C++ outputs are deterministic. Maximum
confidence error 4.980773571361397e-10 and maximum bbox error 1.213119509202443e-05; tolerances are 1e-4 and 0.01 pixel.
This proves cross-language correctness, not performance.

Performance Baseline Result
---------------------------
The existing WSL2 x86_64 ONNX Runtime CPU Engineering Baseline is referenced without rerunning benchmark, Pilot, or formal runs:
five valid runs with 560 raw / 50 warmup / 510 measured frames. This is not a new performance sample.

Cross-Evidence Consistency
---------------------------
The existing Level C and Benchmark Evidence retain the same ONNX, ModelContract, tensor, class, postprocess, ORT CPU,
corpus and asset contracts. All 15 remediation verification stages PASS.

Interpretation Boundaries
-------------------------
The referenced baseline is WSL2 x86_64 CPU-only and warm-cache. It is not a Jetson result, not a TensorRT result, not final
deployment performance, and does not support cross-hardware speedup claims. backend_fps_equivalent is not application FPS.

Gate Readiness
--------------
This new consolidation is the active version for M5.6. M5.6 Deep Evidence Gate remains PENDING; consolidation PASS does not
equal Gate PASS, and M5 is not CLOSED. Strict, ASan and UBSan remain Not configured.
