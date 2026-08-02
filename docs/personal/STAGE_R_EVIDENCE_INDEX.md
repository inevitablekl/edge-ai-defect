# Stage R Evidence Index

## Authority and Final Classification

```text
Stage: R
Final classification: STAGE_R_COMPLETE_NEGATIVE_RESULT_STAGE_Q_BASELINE_RETAINED
Selected candidate: Stage Q INT8 V0
V2: EXPERIMENTAL_RESULT_ONLY — NOT SELECTED
V3: SKIPPED
V4: SKIPPED
Performance claim for V2: NOT ESTABLISHED FOR V2
Result JSON: v4
Stage Q Evidence: unchanged
```

All listed repository artifacts are tracked unless marked otherwise. Hashes
below are SHA-256 values calculated during R6 read-only audit.

## R0 Planning Freeze

| Path | Purpose | SHA-256 | Status | Authority |
|---|---|---|---|---|
| `results/validation/stage_r/r0_planning_freeze_v1/pre_r0_baseline_manifest.json` | Baseline manifest | `b457204d1adeca59126f72649be72fb1e2c505ee0cf577c0a10629b464b474ab` | tracked | formal planning authority |
| `results/validation/stage_r/r0_planning_freeze_v1/pre_r0_environment_manifest.json` | Environment manifest | `8c8bd6954a91b2a68d54fb6eac9b139a6a2f8277faa520f45b4faf2ee5442ba2` | tracked | formal planning authority |
| `docs/personal/STAGE_R_EXECUTION_PLAN.md` | Frozen execution authority | `aef3690af8df7f41425006fd96d8eb334a40317108802408e4a2ba534edfe81e` | tracked | plan authority |
| `docs/personal/STAGE_R_TASK_CARDS.md` | Frozen task-boundary authority | `e88911fd64b0de0f4b195f793b269f851a43528cf2f226d498e5b7e8184f46d0` | tracked | task authority |

## R1 Baseline and Profiling

| Path | Purpose | SHA-256 | Status | Authority |
|---|---|---|---|---|
| `results/validation/stage_r/r1_baseline_profiling_v1/profiling_summary.json` | V0 profiling facts | `ff487acc782104c303368b367b81f9c359cdf9f95630324ab3b58cd849f9f5e7` | tracked | formal V0 profiling authority |
| `results/validation/stage_r/r1_baseline_profiling_v1/baseline_equivalence_summary.json` | V0 v5/v6 equivalence | `ada2a6253080205cb4b65b8c49542116b1228c56b84582fca3578fa74a9482e0` | tracked | formal correctness authority |
| `docs/personal/STAGE_R_R1_BASELINE_PROFILING_REPORT.md` | R1 interpretation and scope | `f4eb59c2a7f9b7704a5fb438e71a9058e38079df101bb1ebe64e51c3dfcf91fd` | tracked | report authority |

## R1 Nsight Remediation

| Path | Purpose | SHA-256 | Status | Authority |
|---|---|---|---|---|
| `results/validation/stage_r/r1_baseline_profiling_v1/nsight_capture_summary.json` | Bounded capture summary | `19dee1beae01b6a367b340e5d06d9e1ef976f3dbaca2a1c1d9e60535532130ec` | tracked | observation-only, not performance authority |
| `results/validation/stage_r/r1_baseline_profiling_v1/nsight_summary.json` | Historical/control summary | `a33f1b8c2549ae85986de73483b030332aeac839aee5d92d9010625fe34a321b` | tracked | historical/control record |

No `/tmp` or other unretained local file is used as the sole authority for a
final conclusion.

## R2.1 CUDA Preprocessing Foundation

| Path | Purpose | SHA-256 | Status | Authority |
|---|---|---|---|---|
| `results/validation/stage_r/r2_1_cuda_preprocess_v1/tensor_gate.json` | 16-image tensor and geometry gate | `f6b276a9c2c7c50fb06d65c95225e80b8cd1a1e9c40730dfc005c46aef5f284a` | tracked | formal Gate B foundation evidence |

## R2.2 V2 Integration

| Path | Purpose | SHA-256 | Status | Authority |
|---|---|---|---|---|
| `results/validation/stage_r/r2_v2_pageable_correctness_v1/v0_regression_summary.json` | V0 regression and canonical authority check | `dce1d77e2533a63146a98a8db0dee64fe4a174c1a0a54af894a342912056eb49` | tracked | formal Gate C evidence |
| `results/validation/stage_r/r2_v2_pageable_correctness_v1/v2_tensor_gate_summary.json` | V2 tensor gate summary | `cb117851c0c4266ecb4d4743a91333259ca625fffbf72f2e138e5a62a8b25014` | tracked | formal Gate B evidence |
| `results/validation/stage_r/r2_v2_pageable_correctness_v1/v2_task_accuracy_summary.json` | V2 task-level accuracy | `e573ef8b113c7d4b13f5ef049e8abbf4cad58075f595428c082a3b28816e7651` | tracked | formal Gate D evidence |
| `docs/personal/STAGE_R_R2_V2_PAGEABLE_REPORT.md` | V2 implementation and negative-result report | `6c9f80d822b3164288eeb4d4d5b46cd2950a9a3e6996766b353ce5a75f603a6e` | tracked | report authority |

## Minimal Remediation

| Path | Purpose | SHA-256 | Status | Authority |
|---|---|---|---|---|
| `results/validation/stage_r/r2_v2_pageable_correctness_v1/v2_minimal_remediation_summary.json` | 11-bit fixed-point remediation result | `ca71697c6f557b8c44c607c83de01985b7a3fca1825bfa490985b6e5f045916b` | tracked | formal negative-result evidence |

## Negative-Result Disposition

| Item | Status | Authority |
|---|---|---|
| Gate A | PASS | R2.2 report and tracked R2.2 evidence |
| Gate B | PASS | tensor gate summary |
| Gate C | PASS | V0 regression summary |
| Gate D | FAIL | task accuracy summary and remediation summary |
| V2 selection | NOT SELECTED | D085 and R2.2 report |
| V3 | SKIPPED | D085 / D086 and R2.2 report |
| V4 | SKIPPED | D085 / D086 and R2.2 report |
| R3 | SKIPPED_BY_NEGATIVE_RESULT_DISPOSITION | D086 and final report |
| R4 | NOT APPLICABLE | D086 and final report |
| R5 | SKIPPED — V0 retained | D086 and final report |

## R6 Closeout

| Path | Purpose | Status | Authority |
|---|---|---|---|
| `docs/personal/STAGE_R_FINAL_REPORT.md` | Final negative-result report | tracked by R6 closeout | final report |
| `docs/personal/STAGE_R_EVIDENCE_INDEX.md` | Evidence inventory and authority map | tracked by R6 closeout | evidence index |
| `results/validation/stage_r/r6_closeout_v1/stage_r_final_status.json` | Machine-readable final status | tracked by R6 closeout | final status |
| `results/validation/stage_r/r6_closeout_v1/artifact_sha256.txt` | Closeout artifact hashes | tracked by R6 closeout | integrity record |

## Integrity Boundaries

- Stage Q INT8 Evidence and canonical detection SHA are unchanged.
- No V0-vs-V2 performance Evidence exists or is claimed.
- Local-only raw Nsight artifacts, if absent, are not backfilled or assigned
  invented hashes.
- The R6 artifacts are documentation/evidence closeout artifacts only.

---

## D087 Reopening Addendum (2026-08-02, read-only append)

Previous closeout:

```text
valid as the replacement-selection disposition at b008af7
```

Current research status:

```text
REOPENED_FOR_MULTI_BRANCH_ABLATION under D087
```

```text
Stage R:
REOPENED_FOR_MULTI_BRANCH_ABLATION

V0:
FORMAL_BASELINE

V2:
V2_ACCURACY_TRADE_OFF_BASELINE

R2.3 / V3:
AUTHORIZED

V4:
AUTHORIZED AFTER V3 FUNCTIONAL VALIDATION

R3:
PENDING V3/V4 AVAILABILITY
```

The integrity boundaries above remain valid for the historical closeout
evidence and are not rewritten.

---

## R2.3 V3 Pinned Evidence (D087)

| Path | Purpose | Authority |
|---|---|---|
| `results/validation/stage_r/r2_v3_pinned_correctness_v1/v3_tensor_gate.json` | 16-case tensor gate | formal Gate B evidence (V3) |
| `results/validation/stage_r/r2_v3_pinned_correctness_v1/v3_hashes.json` | V3 detection SHA and tensor digest | formal equivalence evidence |
| `results/validation/stage_r/r2_v3_pinned_correctness_v1/v3_run_manifest.json` | Run-time record and frame contract | formal runtime evidence |
| `results/validation/stage_r/r2_v3_pinned_correctness_v1/v3_result.json` | 180-frame Result JSON v4 | raw result evidence |
| `results/validation/stage_r/r2_v3_pinned_correctness_v1/v3_runtime_summary.json` | Runtime summary | formal runtime authority |
| `results/validation/stage_r/r2_v3_pinned_correctness_v1/v3_v2_equivalence_summary.json` | V2/V3 equivalence incl. frozen-value finding | formal equivalence authority |
| `results/validation/stage_r/r2_v3_pinned_correctness_v1/artifact_sha256.txt` | Evidence artifact hashes | integrity record |
| `docs/personal/STAGE_R_R2_V3_PINNED_REPORT.md` | R2.3 implementation report | report authority |

V3 tensor digest and detection SHA are identical to the live V2 run at the
same code state; V3 task metrics are inherited from V2. The frozen V2 hash
fields correspond to the pre-remediation code state (see the equivalence
summary for the root cause).
