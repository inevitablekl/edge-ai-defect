Stage K8 Final Experiment Summary v1
====================================

Status: COMPLETE
Scope: evidence consolidation and decision freeze only
Date: 2026-07-29

The final deployment candidate is the Original TensorRT FP16 Engine. K8 did
not run a new benchmark, accuracy experiment, precision search, or runtime
experiment. The values below are consolidated from the existing Stage K5,
K6, and K7 evidence.

1. Project objective
--------------------

Validate a Jetson serial TensorRT deployment path for the frozen YOLOv8n
industrial defect detection model, using task accuracy, continuous stability,
and measured performance as the deployment decision criteria.

2. Deployment pipeline
----------------------

PyTorch
  -> ONNX
  -> ONNX Runtime baseline
  -> TensorRT FP32 reference
  -> TensorRT FP16 optimization
  -> task validation
  -> stability
  -> performance

The selected deployment candidate is the Original TensorRT FP16 Engine.

3. Accuracy comparison
----------------------

The frozen task-level evaluator reported the following results:

Backend                 Precision  Recall    mAP50     mAP50-95
Strict FP32             0.631474   0.717195  0.654858  0.359086
Original TensorRT FP16  0.634731   0.719457  0.656024  0.359550

Task-level verdict: TASK_LEVEL_FP16_ACCEPTED.

4. TensorRT optimization
------------------------

K7 compared the Original TensorRT FP16 Engine with the Strict FP32 TensorRT
reference on the same frozen Jetson serial benchmark protocol:

Metric                 Strict FP32       Original FP16     Speedup
Inference mean         12.914213 ms      11.164944 ms      1.156675x
E2E mean               18.813333 ms      17.065202 ms      1.102438x

The values are formal K7 benchmark values and are not newly measured by K8.

5. Raw numerical limitation
---------------------------

TensorRT FP16 raw-tensor correctness remains:

  Level B: FAIL

The retained reason is bbox-dominated raw tensor numerical deviation. The raw
tensor failure is retained and is not rewritten, hidden, or converted into a
bitwise-equality pass by this summary.

6. Task-level acceptance
------------------------

The deployment decision is:

  TASK_LEVEL_FP16_ACCEPTED

Acceptance is based on the frozen task-level accuracy result together with
the inherited stability and formal performance evidence. It does not claim
strict raw tensor equality.

7. Stability validation
-----------------------

K6 stability evidence:

  Frames: 84420
  Duration: 1802.819 s
  Success: 100% (84420 / 84420)
  Verdict: K6_STABILITY_PASS

8. Performance benchmark
------------------------

Formal K7 benchmark verdict: K7_PERFORMANCE_COMPLETE.

  Strict FP32 inference mean: 12.914213 ms
  Original FP16 inference mean: 11.164944 ms
  Inference speedup: 1.156675x
  Strict FP32 E2E mean: 18.813333 ms
  Original FP16 E2E mean: 17.065202 ms
  E2E speedup: 1.102438x

9. Final conclusion
-------------------

The Original TensorRT FP16 Engine is accepted as the final Stage K serial
deployment candidate. The acceptance is an engineering deployment decision
supported by task accuracy, 30-minute stability, and formal K7 performance.
The raw numerical Level B limitation remains an explicit known boundary.

10. Known limitations
---------------------

* Raw TensorRT FP16 Level B equality failed because of bbox-dominated raw
  tensor numerical deviation.
* This is task-level deployment acceptance, not bitwise raw-tensor equality.
* Stage K validates serial execution; Pipeline optimization remains downstream
  work and was not executed here.
* No industrial certification or universal TensorRT performance guarantee is
  claimed.
* K8 performed no new experiment and did not modify the Engine, ONNX,
  ModelContract, runtime implementation, comparator tolerance, benchmark
  result, or existing Evidence.

Evidence sources
----------------

  results/validation/stage_k_task_eval_v2/metrics/
  results/validation/stage_k6/stability_v1/
  results/validation/stage_k7/performance_v1/

