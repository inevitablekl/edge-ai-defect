# Split Remediation Analysis

Status: `Q1_BLOCKED_PENDING_SPLIT_DECISION`

This document is analysis only. No dataset, image, manifest, SHA file, model,
training archive, production code, benchmark, or accuracy result was modified
or regenerated.

## 1. Finding

The frozen split manifests contain two different relative paths with identical
image content:

| Split | Manifest entry | Image path | Image SHA256 | Annotation SHA256 | BBoxes |
|---|---:|---|---|---|---:|
| train | 935 | `IMAGES/patches_101.jpg` | `4d2de82731b86cdbc7a66f2a9bfb01074bb4cb65e47bccf06b66470d53857071` | `052f875873e9fbbbdb823fc5f3975a462cf80209c61edd3704dbcf137003192d` | 3 |
| val | 187 | `IMAGES/patches_105.jpg` | `4d2de82731b86cdbc7a66f2a9bfb01074bb4cb65e47bccf06b66470d53857071` | `05eafff1fdc2aa894a359ede9c6552dfe535a5a75dba4d9f8b77eb8ae71aaaa0` | 3 |

The two local raw files both exist under `data/raw/NEU-DET`. They have the
same 19,829-byte size and the same 200x200 JPEG dimensions. Their annotations
are different files with different SHA256 values. Normalized relative paths
do not overlap; content SHA256 isolation does overlap once (`train ∩ val = 1`).

Detailed machine-readable evidence is in
`results/validation/stage_q/q1_platform_asset_preflight_v1/duplicate_sample_analysis.json`.

## 2. Root Cause

### Confirmed

1. The duplicate image content is already present in the local raw input
   corpus, before any manifest consumer or runtime evaluation.
2. The split contract sorts XML paths and applies `random.Random(42).shuffle`.
   The manifest metadata records duplicate-bbox removal, but not
   content-level image deduplication before split assignment.
3. The two distinct source paths were assigned to different splits. Thus the
   cross-split leakage is caused by splitting an input corpus that contains a
   content duplicate without a content-level isolation gate.

### Not verified

Whether the upstream, originally distributed NEU-DET dataset itself contains
these two byte-identical files is `NOT VERIFIED`. The repository contains no
authoritative upstream archive or provenance record sufficient to distinguish
an upstream duplicate from a duplicate introduced during local dataset
import. It is therefore not valid to attribute the duplicate to upstream
NEU-DET with certainty.

The split generator is deterministic: `split_metadata.json` records matching
repeat manifest SHA256 values for seed 42. This confirms reproducibility, not
that the split is content-isolated.

## 3. Impact

### Training

The historical training records use the NEU-DET dataset and document a
70/20/10 split with seed 42. The frozen model record points to the historical
training experiment and its `data/yolo/neu_det/dataset.yaml`; the current
Stage K v2 manifest SHA values are not directly recorded in the training
archive provenance. Therefore whether the historical training process used
these exact current manifest files is `NOT VERIFIED`.

If the same 1,800-image allocation was used, the model-selection validation
set contains content identical to one training image. This can make the
validation result slightly optimistic for that sample and weakens the claim
of strict train/validation independence. It does not justify changing any
reported metric without a separately authorized rerun.

### Stage K

Stage K task-level evaluation explicitly references the frozen 180-image
`test_manifest.json` with SHA256
`fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8`.
The duplicate is train/val only; no content SHA overlap with test was found.
Therefore the specific duplicate is not present in the Stage K test corpus,
and existing Stage K test results are not shown by this analysis to have a
duplicate test image. However, the global split contract is not clean, so
the Stage K evidence should retain its historical identity and not be
relabelled as proof of a globally content-isolated split.

### Stage P

Stage P correctness and performance evidence references the same frozen
180-image test corpus and the same test manifest SHA256. No train/val image is
used by the cited P4/P5/P7 corpus according to the recorded provenance, and
the duplicate SHA is absent from test. The duplicate therefore does not
directly contaminate the cited Stage P runtime corpus. Stage P evidence still
inherits the Q1 split-integrity limitation and must not be silently upgraded
to a clean global split claim.

### Stage Q

Q1 remains blocked. The correct status is:

`Q1_BLOCKED_PENDING_SPLIT_DECISION`

No Q2 work is authorized. In particular, calibration data isolation cannot be
accepted while the train/val content overlap is unresolved; no calibrator,
cache, engine, benchmark, or accuracy experiment was started.

## 4. Possible Remediation

These are proposals only. None was executed in this task.

### Option A — Remove one duplicate from one split

Remove one of the two entries according to an approved deterministic policy,
then update the affected split allocation and all dependent SHA/provenance.
This is small in scope, but it changes the frozen manifest and may alter
class balance, counts, training inputs, and validation interpretation.

### Option B — Regenerate the split with content-level deduplication

Build a new versioned split from the raw corpus by grouping identical image
content before assignment, preserving the 70/20/10 intent as far as possible,
then revalidate normalized paths, image content SHA256, counts, annotations,
and deterministic reproducibility. This is the strongest long-term option,
but any changed train/val allocation requires a separately authorized
training/model-evaluation impact assessment. Existing Stage K/P artifacts must
remain historical unless their corpus identity is intentionally changed.

### Option C — Accept the limitation

Keep the current manifests and explicitly document that path isolation passed
but content isolation failed once between train and val. This avoids changing
historical artifacts, but it does not satisfy the strict Q1 split-isolation
gate and is unsuitable if Q1 is intended to authorize isolated calibration.

## 5. Recommendation

Recommend **Option B** for the next authorized dataset-decision task:
content-level deduplication must happen before deterministic split assignment,
with a new versioned manifest set and explicit provenance. It provides the
clearest calibration and thesis-quality isolation contract and avoids making
an arbitrary choice between two differently annotated names for identical
pixels.

Until that decision is approved and executed, retain the current manifests and
all Stage K/P artifacts unchanged as historical, identity-frozen evidence.

## Q1-B Follow-up

The approved content-level remediation was executed later under Q1-B. The
original manifests remain unchanged as `split_v1_historical`. The generated
`split_v2_deduplicated` set contains 1260 train, 359 val, and 180 test images;
the duplicate group retained `IMAGES/patches_101.jpg` and removed
`IMAGES/patches_105.jpg` by normalized UTF-8 path order. Path and content-SHA
isolation both pass. No training, calibration, benchmark, accuracy experiment,
or Q2 action was performed.
The original `Q1_BLOCKED_SPLIT_ISOLATION_FAILURE` remains the historical
preflight result. Q1 final gate closure is now recorded separately as
`Q1_PLATFORM_AND_ASSET_PASS_WITH_SPLIT_REMEDIATION`; final review is required
before Q2 authorization.

Final impact statement:

```text
Training impact: PENDING VERIFICATION.
Stage K/P: test corpus unchanged.
Stage Q: uses split_v2_deduplicated.
```

## Evidence References

- `results/validation/stage_k_task_eval_v2/split/train_manifest.json`
- `results/validation/stage_k_task_eval_v2/split/val_manifest.json`
- `results/validation/stage_k_task_eval_v2/split/test_manifest.json`
- `results/validation/stage_k_task_eval_v2/split/split_metadata.json`
- `docs/MODEL_FREEZE_RECORD.md`
- `docs/TRAINING_ARCHIVE_INDEX.md`
- `docs/personal/STAGE_Q_FACT_INVENTORY.md`
- `results/validation/stage_k_task_eval_v2/metrics/verification_report.json`
- `docs/personal/STAGE_P_EVIDENCE_INDEX.md`
