Stage J CPU Baseline Evidence Consolidation

Status: PASS
Evidence ID: stage_j_cpu_baseline_v1
Consolidation scope: J5.1-J6 published Evidence
Consolidation source commit: 209b81aaf943984445bce674b4077414a8be6820

Objective
Establish a reproducible Jetson ONNX Runtime CPU-only serial baseline for the
frozen YOLOv8n NEU-DET deployment contract. This consolidation indexes the
accepted J5.1-J5.6 benchmark chain and the research-grade J6 tuned stability
campaign. It does not create new inference samples or replace the underlying
Evidence manifests.

Platform and runtime
Jetson Orin Nano Super Developer Kit; aarch64; JetPack 6.2.2 / L4T R36.5;
MAXN_SUPER; active fan; ONNX Runtime 1.23.2 CPUExecutionProvider; FP32;
Serial runtime.

Profiles and results
- Controlled profile: k1, CPU 5, ORT intra/inter 1/1.
- Tuned profile: k5, CPU 1-5, ORT intra/inter 5/1.
- J5.5: PASS_WITH_DOCUMENTED_LIMITATION. Five independent k1 formal runs
  passed; whole-process timing was available, while per-frame timing
  distributions and independently reconstructable raw telemetry were not.
- J5.6: PASS. Five independent k5 formal runs passed.
- J6: PASS_WITH_RESEARCH_GRADE_EVIDENCE. One continuous 30-minute window
  measured 1800.0649718600034 seconds, 743 cycles, 14860 frames and zero
  failures. Correctness passed and cycle hash drift was false.

Current limitations
The J5.5 limitation remains documented. In J6, VDD_IN and EMC frequency were
unavailable, one initial CPU-utilization sample and the final VmRSS sample were
unavailable, and cv0/cv1/cv2 thermal zones were unavailable. These interfaces
are recorded as unavailable; no values are inferred or fabricated.

Gate boundary
J7 consolidation self-validation is PASS. J8 is READY_FOR_AUDIT but was not
executed. J9 is NOT_STARTED. Stage T, TensorRT, CUDA EP, FP16, INT8 and
deployment-readiness claims are outside this consolidation and remain
NOT_AUTHORIZED.
