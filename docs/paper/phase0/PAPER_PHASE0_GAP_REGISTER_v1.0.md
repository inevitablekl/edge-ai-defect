# Paper Phase 0 Gap Register v1.0

## 1. Confirmed Global Missing Assets

There is no `MISSING_GLOBAL` asset affecting the existing principal paper
claims. Training confusion matrices, PR/F1/P/R curves, prediction previews,
and `predictions.json` were found in verified external archives. Stage Q and
post-R0 Stage R formal evidence is present, and Stage K K7 repository evidence
is authoritative. No mandatory rerun, retraining, or TensorRT Engine rebuild is
required.

## 2. External Retained Assets

**Retention status:** `RETENTION_CONFIRMED`.

| Asset | Authority/reference | Verified retention | Handling |
|---|---|---|---|
| Three training archives | `docs/TRAINING_ARCHIVE_INDEX.md` | Located under `/mnt/f/毕设项目/yolov8n训练结果/`; external hashes, gzip/tar integrity, internal manifests, and path safety passed | `EXTERNAL_LOCAL_ONLY`; retain with recorded hashes |
| Frozen PyTorch model | `docs/MODEL_FREEZE_RECORD.md` | `/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/models/pytorch/yolov8n_neudet_frozen.pt`; 6,259,683 bytes; SHA-256 verified | `EXTERNAL_LOCAL_ONLY`; canonical binary identity |
| Stage Q INT8 Engine/cache and supporting metadata | `docs/personal/STAGE_Q3_FORMAL_CALIBRATION_REPORT.md` | Engine and cache exist at formal paths and match expected hashes; manifests and summaries are present | `EXTERNAL_LOCAL_ONLY`; metadata self-hash omissions are documented only |
| Stage K FP16 Engine binary | Stage K Engine manifest and K6/K7 reports | `/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine`; manifest identity and SHA-256 verified | `EXTERNAL_LOCAL_ONLY`; no rebuild required |

The frozen ONNX binary is not external at scan time: it exists locally at its
canonical repository path and matches the expected hash, but it is ignored and
untracked. It should be treated as a local-only supplemental binary, not as a
portable Git asset.

## 3. Missing Paper Visualizations

Original training and frozen-test visualization assets exist in the verified
external archives. Unified final paper-style rendering remains a
paper-production gap, not an experiment-evidence gap.

| Candidate visualization | Existing canonical input | Status |
|---|---|---|
| Training variant and seed comparison | `results/training/evidence/validation_metrics_by_experiment.csv` | Missing rendered figure/table layout |
| Frozen-model per-class test performance/confusion view | `frozen_test_metrics.csv`; verified external confusion/curve/prediction assets | Original assets retained; unified paper-style rendering not generated |
| ORT CPU vs TensorRT FP16 vs INT8 deployment comparison | Stage J J5.6, Stage K K7, Stage Q Q6 summaries | Missing; timing boundaries must be separated rather than merged naively |
| Serial vs Pipeline throughput | Stage P P5R report | Missing rendered table/figure |
| Stage R ablation, Pareto, FPS-latency, and tail latency | six canonical CSVs under `results/paper/stage_r/` | Inputs ready; rendered figures missing |

No visualization is generated in Phase 0.2R.

## 4. Evidence Restrictions

- Stage J J5.5 has whole-process-wall statistics only; no per-frame latency
  distribution or sample SD may be reconstructed.
- Stage J J6 has unavailable power fields including VDD_IN.
- Stage K FP16 raw Level B is `FAIL`; task-level acceptance does not convert it
  to raw equivalence. It is current canonical negative correctness evidence,
  not historical invalid evidence, and must qualify task-level acceptance.
- Local K7 `performance_v1_invalidated_output_allocation` is excluded in full.
- Stage P P5 `4.165718x` is a formal descriptive observation, not significance,
  universal speedup, or lower single-frame latency. Thermal status is
  unavailable.
- Stage P P7 is bounded-memory engineering stability, not leak certification.
- Stage Q uses deduplicated split v2 as authority. Historical split_v1 may only
  explain the remediation; the test set was unchanged.
- Stage Q Q6 thermal status is unavailable; Q7 `1.012575x` supports no material
  regression, not a large Pipeline benefit.
- Stage R Attempt 1 cannot enter final cross-variant tables. Attempt 2 uses a
  unified single-thread harness and is not directly comparable to Pipeline
  throughput.
- Stage R Gate D remains `FAIL`; V2 is research trade-off only. V3/V4 accuracy
  is inherited via identical detection SHA, not independently re-evaluated.
- Stage R V4 P95/P99 must be accompanied by maximum/tail behavior and the OOM
  anomaly. The OOM record is current supplemental evidence retained for
  limitation disclosure and excluded from aggregate performance samples.
- No metric with different timing boundaries may share an unlabeled comparison
  column.

## 5. Candidate Experiments Potentially Requiring Rerun

### None required for the currently allowed primary claims

- **Why needed:** Not applicable. The authority chain supports the current
  Training, ONNX, Stage J, K, P, Q, and R claims with real tracked summaries,
  contracts/configs, and hashes.
- **Existing evidence:** See `PAPER_EVIDENCE_AUTHORITY_MAP_v1.0.md` and
  `PAPER_ASSET_MANIFEST_v1.0.csv`.
- **Paper impact:** Current restricted claims can proceed without new
  experiments.
- **Priority:** Optional.
- **Whether existing data may already be sufficient:** Yes; it is sufficient
  for the claims explicitly allowed by the authority map.

No retraining is needed. No TensorRT Engine rebuild is needed. Missing
`last.pt`, optimizer state, intermediate checkpoints, `labels_correlogram.jpg`,
exactly named `results.json`/`metrics.json`, or the original frozen-test
directory name are not paper gaps.

Potential future reruns should be opened only if the paper manager chooses to
make a claim currently prohibited. Examples are an independently instrumented
J5.5 per-frame distribution, thermal-throttle-qualified P5/Q6 comparisons, or
an independent V3/V4 task-accuracy evaluation. Each would answer a new or
stronger claim rather than repair the current canonical evidence, so none is
`Must` in Phase 0.2R.
