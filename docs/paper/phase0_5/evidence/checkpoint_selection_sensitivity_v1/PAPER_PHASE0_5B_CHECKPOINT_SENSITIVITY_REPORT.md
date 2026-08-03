# Paper Phase 0.5B Execution Report

## 1. Verdict

COMPLETE_WITH_LIMITATIONS

## 2. Selection Decision

SEED7_SELECTION_CONFIRMED

Seed 7 remains rank 1 by the primary deduplicated validation mAP50-95 (0.427). E1/V1 and E9/seed42 deterministic are tied at 0.423. The historical “equivalent candidate” threshold is not formally defined; no threshold was invented, and Recall is reported as the secondary comparison.

## 3. Repository and Environment

- Repository root: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect`
- Branch: `main`
- HEAD: `e3ffe83a1753aff4166b3bd57cf4193a72fecc75`
- Formal Python: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/.venv/bin/python` / 3.10.12
- Formal stack: PyTorch `2.3.1+cu118`, CUDA `11.8`, Ultralytics `8.4.50`
- GPU: `NVIDIA GeForce GTX 1050 Ti`, driver `582.28`, 4096 MiB
- Formal controlled environment usable: yes; no install or upgrade was performed.
- Default `/usr/bin/python3` environment was not used for formal evaluation because NumPy 2.2.6/system matplotlib 3.5.1 ABI failure was observed during the first preflight.
- Batch 16 succeeded on GTX 1050 Ti; no OOM and no batch reduction.

## 4. Split-v2 Validation Contract

- Required validation: split_v2_deduplicated, 359 images, 825 boxes.
- Validation manifest: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/results/validation/stage_q/split_v2_deduplicated/val_manifest_v2.json`; SHA256 `4be24ebe0a6b8c7e3b75840bd9bab8f67d72b1608e97c21172ce7eb9a6713dd9`.
- Train manifest: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/results/validation/stage_q/split_v2_deduplicated/train_manifest_v2.json`; SHA256 `4e937507e0663ff76740b3fc6dd00552d82a3392a07a99fab17d816b7bc062b6`; train/val path overlap 0 and content SHA overlap 0.
- Test manifest: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json`; SHA256 `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194`; 180 images and exact membership match to historical test: `True`.
- Duplicate resolution: removed validation entry `IMAGES/patches_105.jpg` because it duplicated train `IMAGES/patches_101.jpg` by content SHA256; annotation/image mapping and generated YOLO box count were valid.
- Staging: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/results/validation/paper_phase0_5/checkpoint_selection_sensitivity_v1/staging_dataset_v2/`; generated deterministically from the manifest using read-only image symlinks and XML-to-YOLO labels; YAML/list/generation record are hashed in `artifact_sha256.txt`.

## 5. Checkpoint Inventory

|Run|Path|Size|SHA256|Historical Metrics|
|---|---|---:|---|---|
|E1_V1_BASELINE|`checkpoints/v1_baseline/best.pt`|6259683|`390a377a57ec7339633d8c5e47d32c2ddaabe46317f9cdc60c9145f8733bfbee`|mAP50-95 0.44983; P 0.73268; R 0.73257|
|E2_V2_EXTENDED|`checkpoints/v2_extended/best.pt`|6267491|`dcac254f51c75e4c43da551d92b894d46c7986f786d91989e27905e2cb66fff8`|mAP50-95 0.44091; P 0.72533; R 0.71047|
|E3_V3_NO_MOSAIC|`checkpoints/v3_no_mosaic/best.pt`|6259683|`9240d3fd59a5da3c801b450138671175cd48d26a26a31446d9e1ab90ca3f3b23`|mAP50-95 0.43675; P 0.71163; R 0.73328|
|E4_SEED7|`checkpoints/seed7/best.pt`|6259683|`5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7`|mAP50-95 0.45085; P 0.69223; R 0.74469|
|E5_SEED123|`checkpoints/seed123/best.pt`|6259683|`badee99e9a5462aa5fb225ef9ca2a3c45ad082393d48657f3165c5ac82d06ed7`|mAP50-95 0.44017; P 0.67694; R 0.76089|
|E6_V4_ADAMW|`checkpoints/v4_adamw/best.pt`|6259683|`f72dc4908cb8ca2d6c252b1c5f2a6911561f7a816baf2b7270a1b48ff7345ffc`|mAP50-95 0.43769; P 0.65529; R 0.75971|
|E7_V5_COSLR|`checkpoints/v5_coslr/best.pt`|6259683|`39168666ccbdb29549ec20618e7bc64a5e050fda54e13b253f395ce68c803b0f`|mAP50-95 0.44381; P 0.71953; R 0.70318|
|E8_V6_NO_WARMUP|`checkpoints/v6_no_warmup/best.pt`|6259683|`060892697313ee47b99bc3e9aaa53c62712d7018b430b07e889f2f345e9e00e5`|mAP50-95 0.44147; P 0.73712; R 0.70795|
|E9_SEED42_DET|`checkpoints/seed42_deterministic/best.pt`|6259747|`6ee529faaeea5596e99c76257031e82c4e2d4fb00996050c460716431edb2672`|mAP50-95 0.44983; P 0.73268; R 0.73257|

All nine SHA256 and size checks matched the checkpoint archive manifest. The seed7 archive member SHA256 matches the frozen PT SHA256.
The table path is the verified archive member; the exact temporary extracted paths used for validation are recorded in `checkpoint_inventory.json` under `extracted_path`.

## 6. Evaluation Contract

- One validation-only run per checkpoint; no training, test selection, ONNX, TensorRT, Jetson, or downstream Stage R work.
- Uniform parameters: `imgsz=640`, `split=val`, `batch=16`, `device=0`, `workers=4`, `rect=false`, `conf=null` (Ultralytics effective default), `iou=0.7`, `max_det=300`, `half=false`, `augment=false`, no TTA, same six classes and post-processing contract.
- All nine formal runs returned 0 on the controlled `.venv`; no retry was needed.
- Formal metric values below are recorded at the three-decimal precision emitted by the Ultralytics validation summary.

## 7. Deduplicated Validation Metrics

|Run|P|R|mAP50|mAP50-95|Rank|
|---|---:|---:|---:|---:|---:|
|seed=7|0.697|0.704|0.751|0.427|1|
|V1 baseline|0.716|0.698|0.758|0.423|2|
|seed=42 deterministic|0.716|0.698|0.758|0.423|2|
|V6 no warmup|0.694|0.705|0.744|0.416|3|
|V3 no mosaic|0.701|0.694|0.754|0.413|4|
|V4 AdamW|0.702|0.685|0.737|0.412|5|
|V5 cosine LR|0.701|0.680|0.730|0.410|6|
|seed=123|0.670|0.711|0.737|0.408|7|
|V2 extended|0.672|0.695|0.719|0.400|8|

Per-class P, R, AP50, and AP50-95 for every checkpoint are in `metrics_by_checkpoint.json` and `metrics_by_checkpoint.csv`.

## 8. Historical vs Deduplicated Ranking

|Historical rank|Run|Historical mAP50-95|Deduplicated rank|Deduplicated mAP50-95|Deduplicated R|
|---:|---|---:|---:|---:|---:|
|1|seed=7|0.45085|1|0.427|0.704|
|2|V1 baseline|0.44983|2|0.423|0.698|
|2|seed=42 deterministic|0.44983|2|0.423|0.698|
|3|V5 cosine LR|0.44381|6|0.410|0.680|
|4|V6 no warmup|0.44147|3|0.416|0.705|
|5|V2 extended|0.44091|8|0.400|0.695|
|6|seed=123|0.44017|7|0.408|0.711|
|7|V4 AdamW|0.43769|5|0.412|0.685|
|8|V3 no mosaic|0.43675|4|0.413|0.694|

The primary winner is unchanged: seed7 was historical rank 1 and is deduplicated rank 1. The exact numeric ordering changed for several non-winning checkpoints, but no existing checkpoint surpassed seed7 on the primary metric.

## 9. Seed-7 Selection Assessment

SEED7_SELECTION_CONFIRMED

- Seed7 deduplicated validation: mAP50-95 0.427, mAP50 0.751, P 0.697, R 0.704.
- E1/V1 and E9/seed42 deterministic: mAP50-95 0.423, R 0.698.
- Because the primary metric ranks seed7 first at the reported precision, the undefined historical equivalence threshold does not alter the defensible decision. This remains a limitation of the historical rule specification, not an unresolved evaluation.

## 10. Downstream Impact

- No retraining is needed.
- No re-freezing is needed.
- No ONNX re-export is needed.
- No FP16/INT8 TensorRT Engine rebuild is needed.
- No downstream experiment rerun is needed solely because of the split issue.
- The paper must disclose the historical content duplication and this deduplicated checkpoint-selection sensitivity review.

## 11. Files Created

- `environment.json`
- `checkpoint_inventory.json`
- `split_contract.json`
- `evaluation_contract.json`
- `metrics_by_checkpoint.json`
- `metrics_by_checkpoint.csv`
- `ranking_comparison.json`
- `artifact_sha256.txt`
- `PAPER_PHASE0_5B_CHECKPOINT_SENSITIVITY_REPORT.md`
- `staging_dataset_v2/` (YAML, image list, generation record, labels, read-only symlink staging)
- `evaluations_formal/` (nine validation-only Ultralytics result directories)
- `evaluation_logs/` (eight redirected run logs and seed7 execution record)

## 12. Git Status

- Initial repository snapshot: branch `main`, HEAD `e3ffe83a1753aff4166b3bd57cf4193a72fecc75`; no tracked modifications observed, with pre-existing untracked `build-p1r-wsl` artifacts.
- This task added files only under `results/validation/paper_phase0_5/checkpoint_selection_sensitivity_v1/`.
- No commit, push, or tag was made.

## 13. Recommended Next Actor

Paper Project Manager
