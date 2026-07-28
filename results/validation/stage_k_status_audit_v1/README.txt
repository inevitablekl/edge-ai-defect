Stage K Status Audit Before Dataset Evaluation

STATUS_AUDIT_REPORT
-------------------

Audit scope
-----------

This is a read-only audit of the frozen Stage K plan/task boundaries, live
status records, current Git state and existing Stage K evidence. No official
Stage K document was modified. No full-dataset inference, formal benchmark or
stability run was executed.

Repository state
----------------

  branch: feature/jetson-tensorrt-fp16
  HEAD at audit: 622523933edad60aee6aa29f32b4b242613d0651
  initial audit report commit: 1b26dcfe0fbddc4e10b24c6752088d2db68e2cee
  tracked changes: none
  untracked entries: 104, pre-existing local diagnostics/evidence retained

The current HEAD contains the independent K5.4 task-level evidence commit.
The untracked files were not staged, changed or removed by this audit.

Authoritative-document observation
----------------------------------

`STAGE_K_EXECUTION_PLAN.md` is FINAL and frozen. Its formal K5 structure is
raw correctness followed by K6 integration and K7/K8 downstream gates; the
plan's K5.4 label is TensorRT Level C, not a dataset mAP acceptance stage.

`STAGE_K_TASK_CARDS.md` is frozen at K0 and records card-boundary statuses such
as K1/K2/K3/K4/K5 as planned authorization states. It does not contain the
later execution results and must not be silently rewritten.

`TASKS.md` and `README.md` contain later live-status summaries and record K1
PASS, D062 accepted, K2/K3/K4 complete, K5 raw failure and K6/K7/K8 not
executed. They do not yet formalize the independent K5.4 task-level result.

`DECISIONS.md` records D055–D065. D064 bounded the precision-remediation
scope; D065 authorized M2 as the maximum selective investigation under its
then-current audit. M3 is retained as later exploratory evidence and requires
an explicit temporary governance addendum before it is treated as a formal
plan step.

`EXPERIMENT_PLAN.md` preserves the project rule that all accuracy and
performance values must be real and uses TBD when evidence is unavailable.

Planned vs actual execution
---------------------------

| Stage | Original Goal | Actual Result | Status |
|---|---|---|---|
| K0 | Planning Freeze | Freeze completed. | COMPLETE |
| K1 | Platform Acceptance | Initial attempts blocked, later runtime/help disposition accepted. | PASS with retained attempt history |
| K2 | Engine Build | Original FP16 mixed-precision Engine frozen; K2R C0/C1/C2 all failed raw gate. | Historical Engine COMPLETE; K2R FAIL |
| K3 | Config/Foundation | RuntimeConfig v3, manifest/result foundation and optional build target complete. | COMPLETE |
| K4 | TensorRT Backend | Synchronous TensorRtEngine lifecycle and focused validation complete. | COMPLETE |
| K5.1 | Reference Bundle | 16/16 inputs and 16/16 Python ORT outputs verified. | COMPLETE |
| K5.2 | ORT Control | Strict raw gate failed; inherited cross-architecture limitation accepted by D063; semantic Level C passed. | Limitation accepted; strict gate FAIL |
| K5.3 | TensorRT Raw Correctness | Original FP16 1/16 pass; K2R candidates failed. | FAIL |
| K5.4 | TensorRT Level C / task-level boundary | 54/54 detection matches, 0 class mismatches, mean IoU 0.99495; mAP/Recall/Precision TBD. | Supplemental, incomplete |
| K6 | Application Integration | Formal K6 preflight not executed; existing app runs do not close K6. | NOT READY |
| K7 | Benchmark | No formal benchmark; K5.4 profile is non-formal evidence. | NOT STARTED |
| K8 | Stability | No stability run. | NOT STARTED |

Experimental reality
--------------------

Strict FP32 noTF32 passed the raw Level B diagnostic control with bbox
max_abs approximately 0.0115 in the retained report. The original FP16 raw
Level B failed, while the independent application-level comparison found
54/54 detections matched, zero category mismatches, mean IoU 0.99495 and E2E
speed ratio 1.2273x. The independent dataset evaluator could not compute
Precision/Recall/mAP because the frozen corpus has no validation boxes.

Does this invalidate the original Stage K assumption?
-------------------------------------------------------

Yes, it invalidates the narrower assumption that a raw TensorRT Level B
failure alone proves final detection-task failure. It does not invalidate the
raw Level B gate itself: raw tensor correctness remains a separate numerical
contract and its FP16 failure must remain recorded. The task-level evidence is
promising but not sufficient for acceptance without real validation-set
metrics.

PLAN_CHANGE_RECOMMENDATION
--------------------------

Classification: B — Need additional Task-level validation stage.

Recommended flow:

  K5 raw correctness investigation
       ↓
  temporary task-level validation addendum with real NEU-DET annotations
       ↓
  governance review and final plan update
       ↓
  K6 application integration
       ↓
  K7 formal benchmark
       ↓
  K8 stability

This separates raw numerical correctness from final detection-task quality
without rewriting the historical K5 failure or changing tolerances.

NEXT_EXECUTION_STEP
-------------------

OPTION_C: Create temporary execution addendum, run dataset evaluation, then
freeze final plan update.

This is a recommendation only; no addendum or official plan change was made
by this audit. The addendum should define the annotation source, paired FP32
reference/FP16 evaluation, unchanged preprocessing/postprocessing, accuracy
metrics, provenance and stop conditions. After real results exist, freeze any
necessary official plan adjustment. Do not proceed directly to full evaluation
under an implicit gate change.

Existing evidence directories inspected
---------------------------------------

  results/platform/tensorrt/k1_environment_v1..v4/
  results/platform/tensorrt/d062_contract_v1/
  results/build/tensorrt/k2_fp16_engine_v1/
  results/build/tensorrt/k2r_precision_remediation_v1/
  results/build/tensorrt/strict_fp32_notf32_investigation_v1/
  results/build/tensorrt/selective_fp16_notf32_v1/
  results/build/tensorrt/selective_fp16_notf32_m3/
  results/validation/stage_k_level_b_reference/
  results/validation/jetson_tensorrt_fp16/k5_correctness_v1..v3/
  results/validation/jetson_tensorrt_strict_fp32_notf32/
  results/validation/jetson_tensorrt_selective_fp16_notf32_v1/
  results/validation/jetson_tensorrt_selective_fp16_notf32_m3/
  results/validation/jetson_tensorrt_task_level_v1/

See `status_audit.json` for the structured record and complete fact table.
