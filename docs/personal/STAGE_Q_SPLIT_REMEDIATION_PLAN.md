# Stage Q Split Remediation Plan

Status: `Q1_REMEDIATION_DESIGN_COMPLETE`
Execution status: design only; no split repair was executed.

## 1. Problem Statement

The current historical split has one cross-split content duplicate:

```text
train ∩ val content SHA overlap = 1
train ∩ test content SHA overlap = 0
val ∩ test content SHA overlap = 0
```

The duplicate is:

```text
train: IMAGES/patches_101.jpg
val:   IMAGES/patches_105.jpg
SHA256: 4d2de82731b86cdbc7a66f2a9bfb01074bb4cb65e47bccf06b66470d53857071
```

Path isolation remains zero-overlap, but path identity is insufficient for
dataset isolation. The remediation target is content-level isolation.

## 2. Frozen Historical Split

The current split is designated:

```text
split_v1_historical
```

Its physical files remain at
`results/validation/stage_k_task_eval_v2/split/`. They must be preserved,
must not be overwritten, and remain the identity source for explaining
historical Stage K/P evidence.

| Split | Manifest SHA256 | Image count | Schema | Path domain |
|---|---|---:|---:|---|
| train | `82687d1b969ac7b9af2a759ea0c39fbf68f71161a13765f3ceb27443c67c8591` | 1260 | 1 | `IMAGES/*` |
| val | `d7de5f3ee47353144ac8a11706cd8cfcfe89285fe08ab01b7ee60f0a2d757ebf` | 360 | 1 | `IMAGES/*` |
| test | `fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8` | 180 | 1 | `IMAGES/*` |

The current artifact kind is `stage_k_task_eval_v2_split_manifest`. Every
`image_sha256` is a lowercase 64-character hexadecimal SHA256 string.

## 3. New Split Contract

The proposed new contract is:

```text
split_v2_deduplicated
```

Proposed assets:

```text
train_manifest_v2.json
val_manifest_v2.json
test_manifest_v2.json
```

These are design targets only; no files have been created.

Required invariants:

```text
path isolation PASS
AND
content SHA isolation PASS
```

For every pair of splits, both normalized relative paths and `image_sha256`
values must have empty intersection. Each entry must retain its image path,
image SHA256, annotation path, annotation SHA256, class list, and bbox count.
The v2 metadata must record its generator version, source corpus identity,
deduplication policy, ordering, seed, counts, and all resulting manifest
SHA256 values.

## 4. Deduplication Policy

Duplicate identity is defined exclusively by the binary image content:

```text
duplicate identity = SHA256(image bytes)
```

The implementation design must:

1. Read all candidate image entries before split assignment.
2. Normalize relative paths only for path identity and reporting.
3. Group entries by lowercase `image_sha256`.
4. Require each content group to be assigned to at most one split.
5. Validate both path and content intersections after assignment.

The following are not valid duplicate criteria:

- filename equality or filename similarity;
- relative path equality;
- manual visual inspection;
- annotation equality alone.

Annotation differences do not override identical image-content identity.

## 5. Duplicate Resolution Policy

For `patches_101.jpg` and `patches_105.jpg`, the design decision is:

```text
REQUIRES REVIEW
```

No split is selected automatically, and no entry is deleted in this task.
The review must decide whether to:

- retain `patches_101.jpg` in train and remove `patches_105.jpg` from val;
- retain `patches_105.jpg` in val and remove `patches_101.jpg` from train; or
- apply a documented source-priority rule after reviewing annotation
  semantics and dataset provenance.

The review must also decide whether the test split is frozen. The current
duplicate is not in test, so freezing test would preserve the current Stage
K/P corpus identity. A full v2 regeneration could change test membership and
would then require explicit impact review.

### Count targets

The current 1,800 entries contain 1,799 unique image-content SHA values after
collapsing this one duplicate group. Therefore exact counts of 1260/360/180
cannot be promised from deduplication alone without either:

- accepting one fewer v2 entry in the affected train/val allocation; or
- selecting a replacement from an explicitly verified source inventory and
  documenting why it is not already represented.

Replacement selection is also `REQUIRES REVIEW`. It must not be invented or
performed by the remediation design task.

## 6. Versioning

`split_v1_historical` remains immutable and continues to explain historical
manifest references.

The new logical asset set is `split_v2_deduplicated`:

```text
train_manifest_v2.json
val_manifest_v2.json
test_manifest_v2.json
```

The v2 files must be published alongside, not over, v1. Their metadata must
include a `source_split_version`, source manifest SHA values, source dataset
root identity, and a clear statement that content-level deduplication was
applied before assignment.

## 7. Impact Analysis

### Training

Status:

```text
PENDING VERIFICATION
```

The historical training provenance does not directly bind the frozen model
to the current manifest SHA values. If the historical training input used the
same train/val allocation, changing the training or validation membership can
change model-selection evidence and validation metrics. A retraining decision
must therefore follow v2 generation and provenance comparison; no retraining
is authorized by this design.

### Stage K

The identified duplicate is train/val only, and the current Stage K task-level
evaluation uses the 180-image test manifest. If v2 freezes the current test
membership, the Stage K test manifest and corpus remain unchanged. This is a
design assumption requiring review, not a new verification result.

If v2 changes test membership, all dependent Stage K correctness/accuracy
evidence becomes historical and a separately authorized evaluation would be
required. Existing Stage K results must not be modified.

### Stage P

Stage P uses the same frozen 180-image test corpus. Under a reviewed
test-freeze policy, the Stage P corpus remains unchanged. If test membership
changes, existing P4/P5/P7 evidence remains historical and cannot be silently
reused as v2 evidence. No pipeline benchmark is authorized here.

### Stage Q

The intended future calibration source is:

```text
split_v2 train
```

This means the v2 train set must pass content and path isolation before it can
be accepted as a calibration source. A calibration manifest, cache, calibrator,
or engine must not be generated as part of this design.

## 8. Explicit Non-Execution Boundary

This task did not and must not:

- delete or move images;
- modify or regenerate manifests;
- generate new dataset SHA files;
- retrain or modify the model;
- modify the model freeze record;
- modify Stage K or Stage P results;
- generate a calibration manifest;
- enter Q2 or execute Q1-B implementation.

## 9. Review Gate Before Execution

Before any authorized v2 execution, the project owner must decide:

1. Which duplicate representative is retained, or which source-priority rule
   applies.
2. Whether the current test split is frozen.
3. Whether exact counts remain mandatory or a 1,799-entry total is accepted.
4. Whether a verified replacement source exists.
5. Whether historical training/model-selection evidence requires retraining.

Until these decisions are recorded, the status remains
`Q1_BLOCKED_PENDING_SPLIT_DECISION`.

## 10. Q1-B Execution Result

Q1-B was subsequently authorized and executed using the frozen policy. The
historical split files were preserved and the v2 manifests were generated
without reshuffling:

```text
results/validation/stage_q/split_v2_deduplicated/
```

The same-SHA group retained `train/IMAGES/patches_101.jpg` and removed
`val/IMAGES/patches_105.jpg` because the normalized train path sorts first in
UTF-8 byte order. Resulting counts are train `1260`, val `359`, test `180`,
total `1799`; all six classes remain present in every split.

v2 manifest SHA256 values:

- train: `4e937507e0663ff76740b3fc6dd00552d82a3392a07a99fab17d816b7bc062b6`
- val: `4be24ebe0a6b8c7e3b75840bd9bab8f67d72b1608e97c21172ce7eb9a6713dd9`
- test: `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194`

Both path isolation and image-content SHA256 isolation passed for all split
pairs. This is a Q1-B remediation result only; training, calibration,
benchmark, accuracy work, and Q2 remain unauthorized.
