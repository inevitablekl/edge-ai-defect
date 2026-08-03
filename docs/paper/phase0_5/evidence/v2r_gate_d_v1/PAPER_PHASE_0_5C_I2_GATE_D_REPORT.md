# Paper Phase 0.5C-I2 V2R Gate D Report

## Verdict

`V2R_CORRECTNESS_ACCEPTED`

## Frozen execution identity

- Implementation commit: `4815a9d129fca1bce6d69926792c05a52f3b3530`
- Branch: `main`
- V2R: pageable raw staging with the frozen OpenCV 4.5.4-aligned CUDA resize semantic.
- V3R: pinned raw staging with the same resize semantic; companion identity only.
- Frozen INT8 Engine SHA256: `8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee`
- Engine manifest SHA256: `67f6ce3337d9c28c4aa2b32ba62554eaaa028f096c448041c063ec695f3b981c`
- Model contract SHA256: `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190`
- Source ONNX SHA256: `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944`
- Frozen 180-image manifest SHA256: `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194`

I1 did not retain a Gate-D task executable. The I1 build contract and frozen
source/config identities were verified, so one same-directory Release rebuild
was performed. The resulting V2R and V3R binary hashes are recorded in
`execution_identity.json`. No dependency was installed or changed.

The rebuild used a validation-only temporary guard/dispatch adaptation so the
existing task harness could select V2R/V3R; it did not alter the frozen
production implementation. Both validation sources were restored to their
original SHA256 before formal execution and the tracked worktree remained free
of source modifications.

## Gate D contract and V2R result

The formal V2R task run was executed once on the frozen 180-image test split,
with `conf=0.25`, `iou=0.45`, `max_nms=30000`, `max_det=300`,
`agnostic=false`, `multi_label=false`, batch 1, and input 640x640.

| Item | V0 authority | V2R | Absolute drop |
|---|---:|---:|---:|
| Precision | 0.6912751677852349 | 0.6912751677852349 | 0.0000000000 |
| Recall | 0.6990950226244343 | 0.6990950226244343 | 0.0000000000 |
| mAP50 | 0.6476254637935340 | 0.6476254637935340 | 0.0000000000 |
| mAP50-95 | 0.3523443910494967 | 0.3523443910494967 | 0.0000000000 |

V2R processed 180 images, produced 447 detections across 6 classes, had zero
drops, and reached EOS with the expected result contract. The result JSON SHA
is `fb18d7afabd08406697749fb2a033be5455c2af989dc1bb4087310e54c2a4aaa`.
Per-class AP50 and recall values and deltas are in
`v2r_per_class_metrics.csv`.

## Gate-by-gate decision

All six Gate D checks PASS:

- mAP50-95 drop: `0.0000000000 <= 0.005`
- mAP50 drop: `0.0000000000 <= 0.005`
- precision drop: `0.0000000000 <= 0.010`
- recall drop: `0.0000000000 <= 0.010`
- maximum per-class AP50 drop: `0.0000000000 <= 0.020`
- maximum per-class recall drop: `0.0000000000 <= 0.030`

## V3R companion identity

V3R independently replayed the same frozen 180-image sequence. Frame order,
image paths, geometry, processed count, zero-drop behavior, EOS, and result
contract all PASS. V2R and V3R have identical tensor digest
`da2b2bba8d71a25b9bafce988ee838e184666369bbd94bcecc73c6a513d6abb6`, identical
detection SHA `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2`,
and identical detection count 447. V3R was not used as a second Gate D
parameter evaluation.

## Stop-condition compliance

- Formal Gate D: executed exactly once; no metric-triggered retry.
- V3R identity: executed once as the pinned companion check.
- Post-Gate-D kernel modification: `NONE`.
- Second remediation: `PROHIBITED`; not performed.
- Phase 0.5D performance benchmark: `NOT RUN`.
- Historical V2/V3 evidence: not overwritten.

No performance claim is made from these correctness runs.
