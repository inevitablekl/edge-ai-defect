# Paper Dataset Split Sensitivity Final Disposition v1.0

## 1. Verdict

`CLOSED_WITH_DISCLOSURE`

## 2. Historical Issue

The historical train/validation split contained an image-content duplicate. The
test split was not affected. The original 1,800 image files correspond to
1,799 unique image contents.

## 3. Evaluation Scope

- Nine existing `best.pt` checkpoints were evaluated.
- Matched split v1 contained 360 validation images; deduplicated split v2 contained 359.
- Phase 0.5B and Phase 0.5B-R used the same controlled environment, validation
  parameters, deterministic staging procedure, and XML-to-YOLO label generation.
- The test split was not used for model selection.
- No training or checkpoint modification was performed.

## 4. Selection Result

Seed 7 ranked first on matched split v1 with mAP50-95 `0.428` and ranked first
on split v2 with mAP50-95 `0.427`. All nine checkpoint ranks were unchanged.
Removing the duplicate item therefore did not change the selected model.

The controlled selection decision is:

`SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL`

## 5. Downstream Decision

The split issue does not require:

- retraining;
- model re-freeze;
- ONNX re-export;
- TensorRT Engine rebuild;
- downstream rerun caused by the split issue.

## 6. Historical Metric Reconciliation Limitation

Reconstructed split-v1 absolute metrics differ from the historical recorded
metrics. The cause was not determined. This difference is not attributed to
the single duplicate image, and GPU differences are not claimed as a confirmed
cause.

The matched-control conclusion relies only on the same-contract comparison of
split v1 against split v2. Historical metrics remain contemporaneous records;
they are not byte-identically reproduced metrics.

## 7. Allowed Paper Statement

The historical dataset split contained one image-content duplicate between
train and validation. A matched-control evaluation of the nine existing
checkpoints showed that removing the duplicate changed seed-7 validation
mAP50-95 from `0.428` to `0.427` while preserving all checkpoint ranks and the
selected checkpoint. The test split was unchanged and was not used for model
selection.

## 8. Prohibited Claims

- Do not state that the original split was completely duplicate-free.
- Do not state that removing one image caused all historical metrics to decline.
- Do not state that the historical metrics have been precisely reproduced.
- Do not use this issue as a reason to require full-pipeline retraining.

## 9. Evidence Paths

- `docs/paper/phase0_5/evidence/checkpoint_selection_sensitivity_v1/`
- `docs/paper/phase0_5/evidence/checkpoint_selection_sensitivity_control_v1/`

These directories contain only the compact authoritative evidence files
specified for Phase 0.5B and Phase 0.5B-R. Staging datasets, image trees,
checkpoint binaries, complete evaluation directories, and console-log
directories are not included.

## 10. Final Status

`DATASET_SPLIT_REMEDIATION_COMPLETE`
