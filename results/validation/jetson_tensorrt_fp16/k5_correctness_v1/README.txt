Stage K K5 correctness campaign Evidence

Verdict: K5_FAILED
Formal status: K5 FAIL
Final gate reason: ORT_CONTROL_FAIL. ORT Level B repeatability passed, but both strict and cross-architecture controls failed; downstream ORT Level C and TensorRT formal gates were stopped.

Implementation commit: ca8393556689b738ac8991530f5eabb11696d560
Invalidated implementation attempts: dcb10a55909b78928fef95fa825c51514ec0e512 and c54020c18c98dbee408131f6642680f44d3ab433; see local attempt_001.
Formal local attempt: /home/orin/edge-ai-local-evidence/stage_k/correctness/k5_correctness_v1/attempt_002/
Tracked Evidence: results/validation/jetson_tensorrt_fp16/k5_correctness_v1/

Reference Bundle: stage_k_level_b_reference_v1
Archive SHA256: fed5755ce630d0902449f3052fcbb915592245583df19bf924ec867d1c1e1e29
Corpus manifest SHA256: 687682f37d1affbe8813a9e7287b42dc28a9a8b9ea8d67f8b85175960f3e2dcd

ORT Level B: run 1 and run 2 each completed 16/16; repeatability was 16/16 byte-identical. Strict was 0/16 for both runs. Cross-architecture was 4/16 for both runs. Worst overall MAE was 0.000020134160237857, above the frozen 0.00001 cross-architecture limit.

TensorRT raw outputs were produced by the grouped pre-control command but are retained local-only and excluded from formal K5.3 comparison. No TensorRT Level C, boundary investigation, benchmark, stability, Pipeline or K6 result is claimed.

The K4 Engine load smoke passed separately; its warning about GPU compute variance is not a performance conclusion.
