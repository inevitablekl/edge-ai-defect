# Paper Phase 0.5B-R Execution Report

## 1. Verdict

COMPLETE_WITH_LIMITATIONS

## 2. Selection Decision

SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL

Seed7 is rank 1 on reconstructed matched split v1 (mAP50-95 0.428) and rank 1 on split v2 (0.427). Removing the duplicate validation image does not change the winner. Common-sample image/XML identities and generated/canonical labels are exact.

## 3. Environment and Provenance

- Repository HEAD: `e3ffe83a1753aff4166b3bd57cf4193a72fecc75`
- Branch: `main`
- Formal environment: `.venv`, Python 3.10.12, PyTorch 2.3.1+cu118, CUDA 11.8, Ultralytics 8.4.50.
- GPU: NVIDIA GeForce GTX 1050 Ti, batch=16, no OOM.
- Phase 0.5B source result: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/results/validation/paper_phase0_5/checkpoint_selection_sensitivity_v1`.
- Relevant hashes: metrics `a964318f9a458f6e9a3c60ea01e4721f1a6d1a63333e4de44317f73ecb5f0ed8`; evaluation contract `bb701e9e878c6f6cd0dac3e925614b3c5c2ab9bbdead320092081a1f0612c966`; generation record `3a17aac47a8b9959488c6aeba48d2455e4c1db15ffe47db8d0d4fb5daf8fe4e4`; XML→YOLO reference `dd11664ba52d1d411df392d20825a532f24c41441ae1538e1d079c8e577d8f6a`.
- No dependency install/upgrade, training, test selection, ONNX, or TensorRT.

## 4. Historical Split Contract

- Historical split authority: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/results/validation/stage_k_task_eval_v2/split/val_manifest.json`; SHA256 `d7de5f3ee47353144ac8a11706cd8cfcfe89285fe08ab01b7ee60f0a2d757ebf`; 360 images / 828 boxes.
- Split v2 reference: `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/results/validation/stage_q/split_v2_deduplicated/val_manifest_v2.json`; SHA256 `4be24ebe0a6b8c7e3b75840bd9bab8f67d72b1608e97c21172ce7eb9a6713dd9`; 359 images / 825 boxes.
- v1 has exactly one additional entry: `IMAGES/patches_105.jpg`, duplicate of train `IMAGES/patches_101.jpg`, contributing 3 boxes.
- Train and test membership remained exactly unchanged between historical and v2 manifests. Test was not evaluated for selection.
- Staging was generated deterministically from manifest order in `/tmp`; raw data was not modified.

## 5. Label Equivalence Audit

- Common samples: 359.
- Image identity exact: 359/359; XML annotation identity exact: 359/359.
- Generated v1 vs generated v2 labels: exact 359/359; numeric-equivalent-only 0; numeric mismatch 0.
- Generated labels vs canonical validation labels: exact 359/359; numeric-equivalent-only 0; numeric mismatch 0.
- Missing/extra box totals on common samples: 0.

## 6. Matched Split-v1 Metrics

|Run|P|R|mAP50|mAP50-95|Rank|
|---|---:|---:|---:|---:|---:|
|seed=7|0.697|0.705|0.751|0.428|1|
|V1 baseline|0.716|0.697|0.758|0.424|2|
|seed=42 deterministic|0.716|0.697|0.758|0.424|2|
|V6 no warmup|0.694|0.705|0.744|0.417|3|
|V3 no mosaic|0.702|0.695|0.754|0.414|4|
|V4 AdamW|0.703|0.686|0.737|0.413|5|
|V5 cosine LR|0.700|0.681|0.730|0.411|6|
|seed=123|0.671|0.712|0.737|0.409|7|
|V2 extended|0.672|0.695|0.719|0.401|8|

Per-class P, R, AP50 and AP50-95 are recorded in `split_v1_metrics_by_checkpoint.json` and `.csv`.

## 7. Matched Split-v1 vs Split-v2

|Run|v1 mAP50-95|v2 mAP50-95|Delta|v1 Rank|v2 Rank|
|---|---:|---:|---:|---:|---:|
|seed=7|0.428|0.427|+0.001|1|1|
|V1 baseline|0.424|0.423|+0.001|2|2|
|seed=42 deterministic|0.424|0.423|+0.001|2|2|
|V6 no warmup|0.417|0.416|+0.001|3|3|
|V3 no mosaic|0.414|0.413|+0.001|4|4|
|V4 AdamW|0.413|0.412|+0.001|5|5|
|V5 cosine LR|0.411|0.410|+0.001|6|6|
|seed=123|0.409|0.408|+0.001|7|7|
|V2 extended|0.401|0.400|+0.001|8|8|

All nine v1→v2 ranks are unchanged; displayed mAP50-95 delta is +0.001 for every checkpoint. Seed7 remains the winner.

## 8. Historical Metric Reconciliation

|Run|Reconstructed v1 mAP50-95|Historical mAP50-95|Delta|
|---|---:|---:|---:|
|seed=7|0.428|0.45085|-0.02285|
|V1 baseline|0.424|0.44983|-0.02583|
|seed=42 deterministic|0.424|0.44983|-0.02583|
|V6 no warmup|0.417|0.44147|-0.02447|
|V3 no mosaic|0.414|0.43675|-0.02275|
|V4 AdamW|0.413|0.43769|-0.02469|
|V5 cosine LR|0.411|0.44381|-0.03281|
|seed=123|0.409|0.44017|-0.03117|
|V2 extended|0.401|0.44091|-0.03991|

Reconstructed split-v1 metrics differ from historical recorded metrics for all checkpoints. This is not automatically attributed to the removed duplicate. Verified contracts include checkpoint identity, labels, manifests, `.venv`, package versions, GPU, batch, and validation parameters. Remaining differences include historical RTX 3090 versus current GTX 1050 Ti, unavailable historical raw predictions/exact metric serialization, and lack of a retained byte-identical historical invocation.

## 9. Seed-7 Final Assessment

SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL

- Matched split v1: seed7 rank 1, mAP50-95 0.428.
- Split v2: seed7 rank 1, mAP50-95 0.427.
- Duplicate removal did not change the winner or any displayed rank.
- No unresolved label/staging difference can affect the matched-control conclusion.
- Historical absolute metric reconciliation remains a documented limitation; primary sensitivity uses matched reconstructed v1 versus v2.

## 10. Downstream Impact

- No retraining, re-freezing, ONNX re-export, TensorRT Engine rebuild, or downstream experiment rerun is required from this matched-control result.
- The paper should disclose the historical duplicate, Phase 0.5B sensitivity review, and unresolved historical absolute-metric reconciliation.

## 11. Files Created

- `environment.json`
- `historical_split_contract.json`
- `label_equivalence_audit.json`
- `evaluation_contract.json`
- `split_v1_metrics_by_checkpoint.json`
- `split_v1_metrics_by_checkpoint.csv`
- `matched_split_comparison.json`
- `matched_split_comparison.csv`
- `historical_metric_reconciliation.json`
- `artifact_sha256.txt`
- `PAPER_PHASE0_5B_MATCHED_CONTROL_REPORT.md`
- `evaluation_logs/` (nine validation-only console logs; no raw evaluation directories copied)

## 12. Git Status

- No tracked modifications; no commit, push, or tag.
- New files are confined to `results/validation/paper_phase0_5/checkpoint_selection_sensitivity_control_v1/`.
- Pre-existing untracked build/test artifacts remain outside this task output.

## 13. Recommended Next Actor

Paper Project Manager
