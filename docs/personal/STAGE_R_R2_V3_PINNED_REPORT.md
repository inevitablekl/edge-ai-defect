# Stage R R2.3 — V3 Pinned Raw Staging Ablation Path

## Verdict

`R2.3_V3_COMPLETE` — the V3 pinned raw staging path replaces only the raw
host staging memory type of the V2 pageable path (pageable → pinned). The
frozen 180-image manifest passes the frame contract, the tensor gate passes,
and V3 is numerically identical to V2 at the same code state (tensor digest,
detection SHA, and per-frame detection content). V3 task metrics are inherited
from V2 because the complete inference-result detection SHA is identical.

## Authorization

`D087 — Multi-Branch Ablation Reopening and Gate-D Metric Disposition`
recorded in `docs/personal/DECISIONS.md`. Stage R execution mode:
`MULTI_BRANCH_ABLATION_MODE`; V2 is `V2_ACCURACY_TRADE_OFF_BASELINE`; R2.3/V3
`AUTHORIZED`; V4 `AUTHORIZED AFTER V3 FUNCTIONAL VALIDATION`.

## Implementation

- `PinnedRawStaging` allocates one long-lived pinned buffer with
  `cudaHostAlloc` (default flags) at initialization, reuses it for every
  frame, and releases it in the destructor at shutdown. No per-frame
  `cudaHostAlloc`/`cudaFreeHost` occurs.
- Row-aware packed copy is preserved; non-contiguous `cv::Mat` inputs with
  padded stride are supported (verified by unit test and by the raw BGR cases
  of the tensor gate corpus).
- Allocation failure is an explicit `Status::failure`; there is no silent
  fallback to pageable V2 staging.
- `PinnedRunner` mirrors the V2 pageable runner frame flow (source → staging →
  CUDA preprocessing → `TensorRtDeviceInputCapability` → TensorRT INT8 →
  existing postprocess). V2 files are untouched.
- The pinned-memory abstraction does not spread to public interfaces; the
  V3-specific staging and runner live inside the Stage R / backend boundary.
- Guard relaxation (required enablement, no behavior change): the
  kV3/kV4 rejection introduced by the V2 closeout is reduced to kV4-only in
  `src/tensorrt_engine.cpp` and `src/inference_engine_factory.cpp`. V0 and V2
  behavior is unchanged; V4 remains rejected.

## Builds and Tests

- Release configure with CUDA 12.6.68 and TensorRT: PASS.
- `test_pinned_raw_staging`: PASS (row-aware copy, non-contiguous input,
  allocate/prepare lifecycle, pinned-host pointer attribute check, explicit
  failure without allocate, explicit failure on oversized input, no silent
  growth, idempotent re-allocation without realloc).
- `test_pageable_raw_staging`: PASS (V2 unchanged).
- `test_stage_r_cuda_preprocess`: PASS (V2/V3 shared foundation).
- `test_tensorrt_engine` with the frozen Stage Q INT8 engine, manifest and
  contract: PASS (run from the repository root).
- Stage K k4 `tensorrt_engine` ctest case: FAIL — pre-existing environment
  condition (fp16 engine plan built for a different device model; unrelated to
  V3; the test exercises kV0 fp16 and does not touch the V3 changes).

## Frame Contract

180-image frozen manifest (`results/validation/stage_k_task_eval_v2/split/test_manifest.json`,
SHA `fd978bea...`): frames 180, order PASS, relative paths PASS, dimensions
PASS, drop 0, EOS PASS, worker join PASS, Result JSON v4.

## V2/V3 Numerical Equivalence

Same code state, same engine (SHA `8d96eabd...`):

| Item | V2 (live) | V3 | Identical |
|---|---:|---:|---|
| tensor digest | `0a9b8ead...` | `0a9b8ead...` | YES |
| detection SHA | `0a668fd5...` | `0a668fd5...` | YES |
| per-frame content | — | — | YES (result JSONs differ only in incidental wall-clock summary fields) |
| tensor gate MAE | `0.000415586` | `0.000415586` | YES |

Conclusion: the staging memory type did not change any numerical result.

### Evidence-integrity finding (pre-existing, V2 closeout)

The frozen V2 hash fields recorded in
`results/validation/stage_r/r2_v2_pageable_correctness_v1/v2_task_accuracy_summary.json`
(`c0012851...` / `b4a7f173...`) are not reproducible at the current HEAD. Root
cause: those values correspond to the pre-remediation code state (commit
`abf9d24`); commit `488a608` applied the authorized 11-bit fixed-point CUDA
resize remediation, which slightly changed preprocessing numerics (tensor gate
MAE `0.000412164` → `0.000415586`). The V2 summary hash fields were not
refreshed when the remediation metrics were recorded. This is unrelated to V3
and to the staging memory type. The frozen V2 accuracy trade-off metrics
(mAP50 drop `0.00537575`, max class AP50 drop `0.02673348`, max class Recall
drop `0.03030303`) remain the accuracy source inherited by V3.

```text
V3 task metrics inherited from V2 because the complete
inference-result detection SHA is identical.
```

## Evidence

`results/validation/stage_r/r2_v3_pinned_correctness_v1/`:

- `v3_tensor_gate.json` — 16-case gate PASS (MAE `0.00041558645672675235`).
- `v3_hashes.json` — V3 detection SHA and tensor digest.
- `v3_run_manifest.json` — run-time record (commit, binary/config/engine/
  manifest SHA, frame contract, runtime path).
- `v3_result.json` — full 180-frame Result JSON v4.
- `v3_runtime_summary.json` — runtime summary and frame contract.
- `v3_v2_equivalence_summary.json` — equivalence record incl. frozen-value
  discrepancy finding.
- `artifact_sha256.txt` — SHA-256 of every evidence artifact.

## Scope Audit

```text
CUDA resize:      UNCHANGED
Gate D thresholds: UNCHANGED
V4:                NOT IMPLEMENTED
Double buffer:     NOT IMPLEMENTED
Formal benchmark:  NOT EXECUTED
Stage Q Evidence:  UNCHANGED
```

## Future Work

`R3/V4 READY` — with the V3 path functionally validated and numerically
equivalent to V2, the next round is the V4 limited double-buffer/overlap
implementation followed by the unified V0/V2/V3/V4 comparative benchmark
under D087.
