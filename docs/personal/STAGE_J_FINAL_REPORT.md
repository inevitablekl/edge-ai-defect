# Stage J Final Report — Jetson ONNX Runtime CPU Research Baseline

## 1. Objective

Stage J establishes a Jetson Orin Nano Super ONNX Runtime CPU baseline for the
YOLOv8n NEU-DET industrial defect detection deployment. The baseline provides
a reproducible CPU reference for later TensorRT/GPU optimization planning.

## 2. System Configuration

Hardware: Jetson Orin Nano Super Developer Kit, aarch64。

Software: JetPack 6.2.2 / Jetson Linux L4T R36.5, Ubuntu 22.04-based system,
ONNX Runtime 1.23.2 with CPUExecutionProvider, FP32, Serial runtime,
MAXN_SUPER and active fan。

Model: YOLOv8n trained for the NEU-DET surface-defect classes, exported to the
frozen ONNX model and executed under the C++ deployment application。

## 3. Pipeline

```text
PyTorch
  ↓
ONNX export
  ↓
ONNX Runtime CPUExecutionProvider
  ↓
C++ inference application
```

## 4. Completed Experiments

- J5.1 Reference：`COMPLETE`。
- J5.2 Semantic validation：`COMPLETE`。
- J5.3 Candidate sizing：`COMPLETE`。
- J5.4 Profile selection：`COMPLETE`。
- J5.5 Controlled baseline：`PASS_WITH_DOCUMENTED_LIMITATION`。
- J5.6 Tuned baseline：`COMPLETE_WITH_RESEARCH_GRADE_EVIDENCE`。
- J5.7 Research-grade gate：`PASS_WITH_DOCUMENTED_J5_5_LIMITATION`。
- J6 Stability：`COMPLETE_WITH_RESEARCH_GRADE_EVIDENCE`。
- J7 Consolidation：`COMPLETE`。
- J8 Lightweight Audit：`COMPLETE`。

The original frozen J8 Deep Evidence Gate was not executed as part of the
lightweight audit and is not claimed as passed。

## 5. Final Profiles

Controlled profile:

- Profile: k1
- CPU affinity: CPU 5
- ORT intra/inter threads: 1/1

Tuned profile:

- Profile: k5
- CPU affinity: CPU 1-5
- ORT intra/inter threads: 5/1

## 6. Main Findings

Measured profile selection showed that tuned k5 provides a useful latency
improvement over controlled k1 while retaining a defensible resource tradeoff;
k6 was not selected because its additional resource cost did not justify the
incremental measured benefit. The formal k5 baseline and the continuous
stability campaign completed successfully. The frozen model, reference,
contract and expected-cycle semantics remained consistent across the completed
Evidence chain.

## 7. Limitations

- J5.5 is limited to process-wall statistics; independently reconstructable
  per-frame timing distributions and raw telemetry were unavailable.
- Part of the J6 power telemetry, including VDD_IN, was unavailable and is
  recorded as unavailable rather than inferred.
- TensorRT/GPU backend optimization was not executed in Stage J。
- Production validation and industrial certification-level validation were not
  performed or claimed。
- The original J8 Deep Evidence Gate remains a separate failed historical gate;
  the J8 lightweight audit does not replace it。

## 8. Final Status

Stage J Research Baseline: `COMPLETE`。

Stage K Planning: `READY_FOR_PLANNING`。

Stage T remains not started and requires separate next-stage planning and
governance authorization before implementation or execution。
