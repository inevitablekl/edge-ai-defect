# Stage J CPU Baseline Summary

## 1. Objective

完成 Jetson Orin Nano Super 上冻结模型、冻结 corpus 和 ONNX Runtime CPUExecutionProvider 的 J5.1–J5.6 CPU-only baseline chain，形成可复核的 Controlled baseline 与 Tuned stability evidence。

## 2. Frozen environment

- Hardware: Jetson Orin Nano Super Developer Kit。
- Architecture: aarch64。
- JetPack: 6.2.2；L4T R36.5。
- Runtime: ONNX Runtime 1.23.2，CPUExecutionProvider。
- Mode: Serial；MAXN_SUPER；active fan。
- Controlled profile: k1，CPU affinity 5，intra/inter threads 1/1。
- Tuned profile: k5，CPU affinity 1-5，intra/inter threads 5/1。

## 3. Model contract

- Model: models/onnx/yolov8n_neudet_frozen.onnx
- Model SHA256: c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944
- J5 corpus manifest SHA256: 235b062cb82166709e2ff800ec71bf92396d5348508281f822ef116d5f0962ab
- J5.1 reference SHA256: 1c31cfd41b4377c989baf35d57352280bb84f26b1942a8e26ac60076e61392a7

## 4. J5.1–J5.6 results

| Task | Result | Evidence |
|---|---|---|
| J5.1 Reference | COMPLETE | j5_1_python_reference_v1 |
| J5.2 Semantic validation | COMPLETE | j5_2_candidate_semantic_precheck_v2 |
| J5.3 Candidate sizing | COMPLETE | j5_3_candidate_sizing_v1 |
| J5.4 Profile freeze | COMPLETE; k1/k5 frozen | j5_4_profile_selection_v1 |
| J5.5 Controlled baseline | COMPLETE; k1 | j5_5_profile_baseline_v1 |
| J5.6 Tuned stability | COMPLETE; k5 | j5_6_profile_stability_v1 |

All six Evidence directories passed their published SHA256 verification.

## 5. Controlled profile result

Controlled k1 used CPU5 and ORT intra/inter threads 1/1. The five-run baseline measured approximately 2.31 FPS, with semantic output matching the frozen expected SHA and byte-identical deterministic payloads.

## 6. Tuned profile result

Tuned k5 used CPU1-5 and ORT intra/inter threads 5/1. The 30-minute continuous stability run processed 15420 frames across 771 cycles, with 0 failures. All cycles matched the frozen semantic output SHA; no NaN or Inf was detected.

## 7. Known limitation

D048 cross-architecture numerical limitation remains accepted: cross-architecture floating-point differences limit direct byte-level numerical equivalence claims. The J5 semantic checks use the frozen contract and accepted comparison boundary.

## 8. Future work

TensorRT/GPU backend work is future scope. TensorRT, CUDA EP, FP16, ROS2 and related GPU optimization were not started by this consolidation.
