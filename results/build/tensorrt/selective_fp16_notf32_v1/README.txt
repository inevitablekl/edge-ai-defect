Stage K Selective FP16 + Strict FP32 Detect-Head Investigation
============================================================

Verdict: SELECTIVE_MIXED_CORRECTNESS_FAIL

Legacy audit: C1/C2 were already --fp16 --noTF32 --precisionConstraints=obey
with complete exact identities; route classification is
LEGACY_CANDIDATES_ALREADY_NOTF32. M1 was therefore not rebuilt.

M2 constrains the complete floating-point /model.22 Detect Head to FP32 while
leaving Backbone and Neck unconstrained under global --fp16. TensorRT 10.3
build and independent inspection passed, with actual FP16 tactics retained
outside the Detect Head.

Level B against Python ORT Reference: 0/16 PASS. Repeatability: 16/16.
Level C and performance precheck were not executed.
