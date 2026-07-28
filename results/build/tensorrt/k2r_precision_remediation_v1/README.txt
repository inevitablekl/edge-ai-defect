Stage K K2R Sensitivity-Aware TensorRT Precision Remediation
=============================================================

Verdict: K2R_COMPLETE_LEVEL_B_FAIL
Date: 2026-07-28
Branch: feature/jetson-tensorrt-fp16
Source commit for candidates: ac53fe71006445a826730d520233a00873639d3c

This tracked summary records the bounded D064 remediation. The original
TensorRT engine, original K5.3 failure, ONNX, ModelContract, Reference Bundle,
comparator policy, tolerances, and historical evidence are unchanged. Raw
tensors, build logs, layer dumps, and all candidate .engine files remain in
the local-only evidence/model roots listed in provenance.json.

C0 disabled TF32 only and was diagnostic. C1 constrained the terminal BBox,
DFL and decode path. C2 added the complete traced BBox regression branches.
Both formal sensitivity candidates failed the frozen 16-image Level B gate;
there is no selected engine. K4 and a new formal K5.3 rerun were therefore not
executed. K5.4 remains NOT READY.

No Level C, K6, benchmark, stability, Pipeline, GPU preprocessing/NMS, INT8,
DLA, ONNX rewrite, C++ Builder, Polygraphy, package, push, merge, or tag work
was performed.
