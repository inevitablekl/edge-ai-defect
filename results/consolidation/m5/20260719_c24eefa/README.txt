Identity
========
Consolidation Evidence ID: 20260719_c24eefa
Source commit: c24eefa85bb77543e3267b7aaf797a0d1f02b846
Branch: feature/cpp-onnxruntime
Status: PASS

Purpose
-------
M5.5 associates and verifies existing Evidence only; no detection result or performance sample is generated.

Referenced Evidence
--------------------
- Level C: results/validation/level_c/20260719_1073fa8 (source 1073fa8be1644dd8562f5704ae31996121883dbb; evidence 011ac3c; sha256sums 14685b7253a4923239f6796fb173177126fa23f241861e6f696712a83e0379f3).
- Benchmark: results/benchmark/ort_cpu/20260719_850252b (source 850252b3c176622e3f4461e78f1b7e517e8b06b6; evidence 703c018; sha256sums 43eea81f79d2e0ee5310872cbb939ff783ff3dcb4a661c0ac2ff073cbd4b7e87).

Correctness Result
------------------
Level C: 16/16 PASS, 54 detections, per-class [4, 28, 7, 4, 5, 6]. Python and C++ outputs are deterministic. Maximum confidence error 4.980773571361397e-10; maximum bbox error 1.213119509202443e-05; tolerances 1e-4 and 0.01 pixel. Deterministic maximum bipartite matching is used; candidate_index is diagnostic only. This proves cross-language correctness, not performance.

Performance Baseline Result
---------------------------
WSL2 x86_64 ONNX Runtime CPU Engineering Baseline: 20-image workload, pilot 100/discard 20/analyze 80, five formal runs of 560 raw/50 warmup/510 measured, all valid over 30 seconds. Across-run median / minimum / maximum:
- inference_mean: 106.576986162745 / 106.396701656863 / 107.419273392157
- inference_p95: 110.33601375 / 109.2568074 / 115.3421842
- pre_sink_mean: 108.654977421569 / 108.47198617451 / 109.550945333333
- pre_sink_p95: 112.43494975 / 111.3694557 / 117.961325
- pre_sink_fps: 9.20344399980976 / 9.12817317054887 / 9.21897012553269
- backend_fps_equivalent: 9.3828887080085 / 9.30931636773679 / 9.3987875979941

Cross-Evidence Consistency
---------------------------
Both Evidence sets use ONNX SHA c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944 and ModelContract SHA 9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190, with matching tensor, class, postprocess and single-thread ORT CPU contracts. Benchmark source contains the Level C source and Gate commits. Benchmark entries 0-11 match Level C originals; entries 12-19 are additional originals. No image assets are copied.

Interpretation Boundaries
-------------------------
This is a WSL2 x86_64 CPU-only, single-logical-CPU, warm-cache result. Host load and CPU frequency were not frozen; caches were not dropped. It is not a Jetson result, not a TensorRT result, not final deployment performance, and cannot calculate cross-hardware speedup. The repeated 20-image workload is not a complete camera pipeline; backend_fps_equivalent is not complete application FPS.

Gate Readiness
--------------
SHA, ancestry, gzip/TSV/per-run/aggregate reconstruction, contract, corpus, privacy and retention checks PASS. Consolidation PASS does not equal M5.6 Deep Evidence Gate PASS. M5.6 remains PENDING and has not been executed; M5 is not CLOSED.
