# Selective FP16 + Strict FP32 Investigation Report

## 1. Verdict

`SELECTIVE_MIXED_CORRECTNESS_FAIL`.

M2 built and inspected as a mixed engine, but failed the frozen TensorRT
Level B gate at `0/16`. No candidate was selected.

## 2. Git State

- Branch: `feature/jetson-tensorrt-fp16`
- M2 source/decision commit: `1fd3344f14e7f3d7a2c0b4bbdb4edfa102e10d4d`
- D065 commit: `1fd3344f14e7f3d7a2c0b4bbdb4edfa102e10d4d`
- No push, merge, or tag was performed.

## 3. Legacy C1/C2 Audit

Both legacy candidates had exact `--fp16 --noTF32 --precisionConstraints=obey`
commands, exact layer precision/output policies, and no observed TF32 tactic.
Classification: `LEGACY_CANDIDATES_ALREADY_NOTF32`.

## 4. D065 Decision

D065 was accepted in an independent decision commit. Python ORT remains the
correctness authority; Strict FP32 noTF32 is only the TensorRT-side baseline.
M1 was not rebuilt because K2R C1/C2 already covered the equivalent bbox-only
route. M2 was authorized as the complete `/model.22` Detect Head FP32 island.

## 5. Strict FP32 Baseline

The frozen Strict FP32 noTF32 engine SHA matched
`aaa37030ca1d24838e75ad6fd1a16bdeb74072d87302c1b2cef62faa3856d74f`.

## 6. Layer Mapping

The frozen ONNX `/model.22` graph contained 90 nodes; 70 floating-point nodes
were constrained for M2. 61 had detailed execution metadata, while 9 were
explicitly recorded as fused/elided parser identities. Backbone/Neck nodes
were not constrained.

## 7. Candidate Builds

M2 built successfully with TensorRT 10.3 using global FP16, `--noTF32`, obeyed
exact FP32 layer precision/output policies, workspace 4096M, static batch 1,
and FP32 I/O.

## 8. Actual Precision Inspection

Inspection passed: all 70 requested precision and output-type constraints were
accepted; 45 execution layers used FP16 tactics outside the Detect Head, and
the Detect Head had no FP16 tactic. No INT8, DLA, or custom plugin was observed.

## 9. Level B

Python ORT Reference comparison: `0/16 PASS`, `16/16 FAIL`. Maximum bbox
absolute error was `27.280731201171875`; maximum score absolute error was
`0.029098331928253174`.

## 10. Level C

Not executed because Level B failed.

## 11. Repeatability

`16/16` outputs were byte-identical across two independent raw runs.

## 12. Performance Precheck

Not executed because Level B failed.

## 13. Strict FP32 vs Mixed Comparison

The strict-vs-mixed file is auxiliary only; it is not a correctness gate.
Its maximum bbox absolute difference was `27.285369873046875`.

## 14. Selected Candidate

None. M2 is rejected by Level B.

## 15. Scope Audit

No production runtime, formal manifest, TensorRT backend source, Pipeline,
stability, K6, or formal benchmark was modified or started. Engine and raw
tensors remain local-only.

## 16. Next Authorization

`FORMAL_MIXED_ENGINE_FREEZE_NOT_READY`. Stop here; do not enter K6, stability,
Pipeline, or formal benchmarking.
