Stage K Selective FP16 + Strict FP32 Detect-Head Investigation
============================================================

Verdict: SELECTIVE_MIXED_CORRECTNESS_FAIL
Candidate: M2 complete /model.22 Detect Head FP32 island

Python ORT Reference Bundle remains the correctness authority. Strict FP32
noTF32 is only the TensorRT-side baseline. M1 was not rebuilt because K2R
C1/C2 already tested the equivalent bbox-only/noTF32 route.

M2 build and inspection passed. Actual FP16 tactics remain in Backbone/Neck;
Detect Head execution is FP32. Raw output shape is [1,10,8400], FP32 BCN.

Level B: 0/16 PASS; max bbox absolute error 27.280731201171875.
Repeatability: 16/16 byte-identical. Level C and performance precheck were
not executed because Level B failed. No production manifest or runtime path
was changed.
