# Paper Evidence Authority Map v1.0

## 1. Repository State

This reconciliation is a read-only evidence review. It did not run training,
inference, correctness validation, benchmarks, Engine builds, or figure
generation, and it did not copy or alter source evidence.

| Item | Recorded value |
|---|---|
| Repository root | `/home/orin/edge-ai/edge-ai-defect` (resolved with `git rev-parse --show-toplevel`) |
| Branch | `main` |
| HEAD | `e3ffe83a1753aff4166b3bd57cf4193a72fecc75` |
| Worktree at entry | `?? Repository_Paper_Asset_Scan.md` (pre-existing user asset; preserved) |
| Visible tags | `m5-onnxruntime-baseline-v1`; `stage-j-complete-v1.0`; `stage-k-tensorrt-fp16-complete-v1.0`; `stage-p-bounded-pipeline-complete-v1.0`; `stage-q-int8-complete-v1.0`; `stage-r-multi-branch-ablation-complete-v1.0`; `v0.2-training-frozen` |
| Local evidence root | `/home/orin/edge-ai-local-evidence` exists |
| Scan time | `2026-08-02 20:13:43 CST +0800` (`Asia/Shanghai`) |

The local evidence root contains Stage J, Stage K, Stage P and only Stage R
`pre_r0`; it has no Stage Q directory and no post-R0 Stage R evidence. Absence
therefore means `LOCAL_ONLY not present`, not `MISSING_GLOBAL`.

## 2. Authority Rules

Authority is resolved in this order:

1. latest formal Final Report or effective append-only Addendum;
2. Evidence Index;
3. machine-readable result explicitly cited by that report;
4. matching configuration, environment, manifest, and hash records;
5. repository canonical results;
6. supplemental raw data under `/home/orin/edge-ai-local-evidence`;
7. historical, diagnostic, rejected, failed, or invalidated attempts.

A timestamp or a filename containing `final` is insufficient. An experiment is
`CANONICAL` only when status, machine result, and its contract/configuration can
be joined. The only asset-state vocabulary used by this reconciliation is:
`CANONICAL`, `SUPPLEMENTAL`, `HISTORICAL_VALID`, `HISTORICAL_INVALID`,
`MISSING_GLOBAL`, `EXTERNAL_REQUIRED`, `NOT_REQUIRED_FOR_PAPER`, and
`UNRESOLVED`.

## 3. Stage-by-Stage Authority

### Training

**Current final status:** `COMPLETE`.

**Authority document:** `docs/TRAINING_FINAL_REPORT.md`, supplemented by
`docs/MODEL_FREEZE_RECORD.md` and `docs/TRAINING_ARCHIVE_INDEX.md`.

**Canonical result paths:**

- `results/training/evidence/validation_metrics_by_experiment.json`
- `results/training/evidence/frozen_test_metrics.json`
- `results/training/evidence/experiment_effective_args_summary.json`
- `results/training/evidence/effective_args/`
- `configs/train/yolov8n_neudet_baseline_seed7.yaml`

Frozen model identity: `yolov8n_neudet_frozen.pt`, SHA-256
`5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7`,
selected from deterministic seed 7. Canonical validation metrics are mAP50
`0.76660`, mAP50-95 `0.45085`, precision `0.69223`, and recall `0.74469`.
Canonical held-out test metrics over 180 images are mAP50 `0.769`, mAP50-95
`0.431`, precision `0.724`, and recall `0.728`.

**Supplemental external paths:** the frozen model binary is retained at
`/home/ros2/wangkl/edge-ai-defect/edge-ai-defect/models/pytorch/yolov8n_neudet_frozen.pt`
(6,259,683 bytes; SHA-256
`5e36ae9ec419a71d6cf726624450dc528f85fed39e398c07085eaf82dba8bbb7`).
The three archives indexed by `docs/TRAINING_ARCHIVE_INDEX.md` are retained
under `/mnt/f/毕设项目/yolov8n训练结果/`. All four assets are
`EXTERNAL_LOCAL_ONLY`; their recorded hashes were verified. The archives also
passed gzip/tar integrity, per-file internal-manifest, path-safety, and
symlink-safety checks.

- `edge-ai-defect_training_checkpoints_patch_20260712.tar.gz`: SHA-256
  `a50525dc3e68a569e81d6319b9bf9d9cc43f9db26c5df3d87e09f48b8a765847`
- `edge-ai-defect_training_evidence_patch_20260712.tar.gz`: SHA-256
  `7c44f5ad992a6b539027d29e249e9f87717661b6750552b33f0a2a8015ac8341`
- `edge-ai-defect_training_stage_20260712.tar.gz`: SHA-256
  `a8b62be94e08f1d3e41c6e589f2171b001490cf772b0ab13ca60fa4d41660756`

**Invalid or superseded paths:** the smoke runs in `experiments/training/` are
not formal training-result authority. Other V1-V6/seed checkpoints are valid
historical candidates but are not the frozen deployment model.

**Accepted limitations:** external training assets are not tracked by Git.
Their verified archives contain all nine formal `best.pt` files, all nine
`results.csv` files, effective/configuration evidence, validation and
frozen-test metrics, training plots, seed-7 confusion/PR/F1/P/R visuals, and
frozen-test confusion/PR/F1/P/R visuals, prediction previews, and
`predictions.json`. The original frozen-test directory name was not retained
verbatim, but README/provenance records, logical paths, and file hashes provide
an acceptable origin chain. `last.pt`, optimizer state, intermediate
checkpoints, `labels_correlogram.jpg`, and files named exactly `results.json`
or `metrics.json` are not required for the current paper. The three-seed sample
is not a general statistical bound.

**Allowed paper claims:** the recorded nine-run comparison; deterministic
three-seed observed variation; frozen-model selection rule and identity;
validation and held-out-test metrics; class-specific weaknesses.

**Prohibited paper claims:** statistically significant superiority of seed 7;
cross-platform bitwise training reproducibility; claims that exceed the
verified archive provenance or measured training/test evidence.

**Unresolved issues:** none affecting the reported metrics or retained training
assets. Retraining is not required or recommended.

### ONNX

**Current final status:** export, runtime smoke, and PT/ONNX comparison
`PASS`; frozen ONNX identity established.

**Authority document:** `results/onnx_export/export_metadata.json`, interpreted
with `configs/export/yolov8n_neudet_frozen.yaml` and
`configs/model_contracts/yolov8n_neudet_frozen.yaml`.

**Canonical result paths:**

- `results/onnx_export/export_metadata.json`
- `results/onnx_export/pt_onnx_compare.json`
- `results/onnx_export/onnxruntime_smoke_test.json`
- `configs/export/yolov8n_neudet_frozen.yaml`
- `configs/model_contracts/yolov8n_neudet_frozen.yaml`

Frozen identity: `models/onnx/yolov8n_neudet_frozen.onnx`, SHA-256
`c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944`,
12,242,487 bytes, fixed FP32 NCHW `[1,3,640,640]` input and FP32 BCN
`[1,10,8400]` output. PT/ONNX comparison records `consistency_pass=true`.

**Supplemental local paths:** the ONNX binary currently exists at the canonical
repository path and its observed SHA matches metadata, but `.gitignore`
excludes `models/**/*.onnx`; it is untracked/local-only.

**Invalid or superseded paths:** none selected.

**Accepted limitations:** a clean Git checkout does not contain the ONNX
binary. The ten-image PT/ONNX comparison supports the stated frozen contract,
not universal equivalence over arbitrary inputs.

**Allowed paper claims:** fixed export contract, identity, successful ORT smoke,
and the measured ten-image consistency result under its stated tolerances.

**Prohibited paper claims:** bitwise identity, dynamic-shape support, or
repository-portable binary availability.

**Unresolved issues:** none.

### Stage J

**Current final status:** Stage J Research Baseline `COMPLETE`; J5.7 research
gate `PASS_WITH_DOCUMENTED_J5_5_LIMITATION`; J6
`COMPLETE_WITH_RESEARCH_GRADE_EVIDENCE`.

**Authority document:** `docs/personal/STAGE_J_FINAL_REPORT.md` and
`results/consolidation/stage_j/stage_j_cpu_baseline_v1/evidence_index.json`.

**Canonical result paths:**

- semantic precheck: `results/benchmark/jetson_ort_cpu/profile_precheck/j5_2_candidate_semantic_precheck_v2/`
- controlled k1 reference: `results/benchmark/jetson_ort_cpu/profile_baseline/j5_5_profile_baseline_v1/`
- tuned k5 formal baseline: `results/benchmark/jetson_ort_cpu/tuned/j5_6_tuned_formal_baseline_v3/aggregate.json`
- research gate: `results/benchmark/jetson_ort_cpu/j5_7_research_grade_gate_v2/research_grade_gate_report.json`
- stability: `results/benchmark/jetson_ort_cpu/stability/j6_tuned_stability_v1/stability_report.json`
- consolidation: `results/consolidation/stage_j/stage_j_cpu_baseline_v1/`

The primary tuned k5 aggregate records mean inference `97.116892314 ms`, mean
pre-sink total `101.721759652 ms`, mean pre-sink FPS `9.830805772`, backend
FPS-equivalent `10.296947224`, and process-wall FPS `9.748320559`. J6 records
`1800.06497186 s`, 14,860 frames, 743 cycles, zero failures, and correctness
PASS. J5.2 v2 is the final semantic precheck.

**Supplemental local paths:** `/home/orin/edge-ai-local-evidence/stage_j/`
contains raw attempts, corpora, telemetry, and workload material marked
`LOCAL_ONLY`; use for audit, not as the final numerical source.

**Invalid or superseded paths:** J5.2 v1; J5.6 v1/v2 failed attempts; historical
`j5_6_profile_stability_v1`; original J5.7 v1 `BLOCKED`; original deep J8
`FAIL`. These are not overturned by the lightweight audit.

**Accepted limitations:** J5.5 only supports whole-process-wall statistics and
lacks reconstructable per-frame measured-window distributions/sample SD/raw
telemetry. Some J6 telemetry, including VDD_IN, was unavailable. Accepted
cross-architecture floating-point limitations remain.

**Allowed paper claims:** k5 Jetson ORT CPU formal performance under the frozen
timing contract; semantic correctness; 30-minute k5 stability; k1 as a
controlled resource/reproducibility reference with its stated limitation.

**Prohibited paper claims:** treating J5.5 process-wall milliseconds as
per-frame latency; power claims from unavailable J6 fields; original deep J8
PASS; cross-device speedup or byte-level cross-architecture equivalence.

**Unresolved issues:** none affecting k5 baseline use.

### Stage K

**Current final status:** Stage K `COMPLETE`; Original TensorRT FP16 Engine
accepted at task level; raw TensorRT FP16 Level B remains `FAIL`.

**Authority document:** `results/validation/stage_k8/final_summary_v1/README.txt`
and `final_experiment_summary.json`, with accepted Decision D066.

**Canonical result paths:**

- task accuracy: `results/validation/stage_k_task_eval_v2/metrics/backend_metrics.json`
- task contract: `results/validation/stage_k_task_eval_v2/metrics/evaluation_contract.json`
- stability: `results/validation/stage_k6/stability_v1/stability_report.json`
- performance: `results/validation/stage_k7/performance_v1/comparison_report.json`
- performance protocol/environment: `results/validation/stage_k7/performance_v1/protocol.json` and `environment.json`
- final consolidation: `results/validation/stage_k8/final_summary_v1/final_experiment_summary.json`
- Engine manifest: `models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json`

The repository `performance_v1` is formal canonical data and replaces the
local invalidated output-allocation copy. Allowed K7 values are: strict FP32
inference mean `12.914213 ms` / `77.434062 FPS`; Original FP16 inference mean
`11.164944 ms` / `89.566059 FPS`; inference speedup `1.156675x`; strict FP32
end-to-end mean `18.813333 ms` / `53.153793 FPS`; FP16 end-to-end mean
`17.065202 ms` / `58.598780 FPS`; end-to-end speedup `1.102438x`. K6 records
84,420/84,420 successful frames over `1802.819 s`.

**Supplemental local paths:** `/home/orin/edge-ai-local-evidence/stage_k/`
contains raw correctness/reference/diagnostic material marked `LOCAL_ONLY`.
The FP16 Engine is retained at
`/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine`
(8,928,756 bytes; SHA-256
`6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc`),
matching the repository Engine manifest. It is `EXTERNAL_LOCAL_ONLY` and must
not enter Git.

**Invalid or superseded paths:** the entire
`/home/orin/edge-ai-local-evidence/stage_k7/performance_v1_invalidated_output_allocation/`
tree is `HISTORICAL_INVALID` and excluded, even though internal files retain an
old `K7_PERFORMANCE_COMPLETE` string. Selective-precision investigations are
not the selected deployment result.

**Accepted limitations:** Level B raw tensor comparator passed only 1/16 for
the original FP16 Engine; bbox-dominated raw numerical deviation remains. This
`FAIL` is current canonical negative correctness evidence, not historical
invalid evidence. It must qualify task-level acceptance, may be cited in the
paper's correctness analysis or limitations, and cannot support raw equality.
Task-level metrics did not overturn it, but nevertheless met D066 acceptance:
strict FP32
P/R/mAP50/mAP50-95 `0.631474/0.717195/0.654858/0.359086`, FP16
`0.634731/0.719457/0.656024/0.359550`. The `.engine` binary is externally
retained and hash verified; binary retention is no longer unresolved.

**Allowed paper claims:** task-level FP16 deployment acceptance; frozen K6
stability; formal K7 FP32-vs-FP16 descriptive latency/FPS/speedup under the
specified Jetson serial protocol.

**Prohibited paper claims:** raw tensor equality or bitwise equivalence;
universal TensorRT speedup; use of local invalidated K7 values; equating
`inference_ms` with GPU-only kernel time.

**Unresolved issues:** none.

### Stage P

**Current final status:** `STAGE_P_COMPLETE_PIPELINE_RECOMMENDED`.

**Authority document:** `docs/personal/STAGE_P_FINAL_REPORT.md` and
`docs/personal/STAGE_P_EVIDENCE_INDEX.md`; P5 is governed by the P5R protocol
amendment and `P5_FINAL_RECLASSIFICATION_REPORT.md`.

**Canonical result paths:**

- P4 correctness: local raw attempt 009, indexed by `docs/personal/STAGE_P_EVIDENCE_INDEX.md`
- P5 final status/numbers: `results/benchmark/stage_p/p5_serial_vs_pipeline_v1/P5_FINAL_RECLASSIFICATION_REPORT.md`
- P6: `results/validation/stage_p/p6_video_v1/P6_VIDEO_VALIDATION_REPORT.md`
- P7: `results/validation/stage_p/p7_stability_v1/attempt_001/`

P5 is valid. The `4.165718x` paired Pipeline/Serial throughput ratio is a
formal measured **descriptive** value under the corrected frozen protocol
(sample SD `0.007915`), not statistical significance or a general guarantee.
There was no later P5 benchmark rerun: P5R reclassified the existing
attempt_001 after correcting the invalid cross-window RUN-SHA rule. P7 is a
formal stability result: `1800.006143093 s`, 410,691 processed frames, 2,281
matching complete cycles, zero drops/errors, normal queue drain and worker
join.

**Supplemental local paths:** `/home/orin/edge-ai-local-evidence/stage_p/`
contains P4/P5/P6/P7 raw attempts, traces, telemetry, and video marked
`LOCAL_ONLY`. They support audit; final status comes from the repository
reports/index.

**Invalid or superseded paths:** the historical P5 attempt report's invalid
conclusion under the cross-window RUN-SHA rule is superseded by P5R. Earlier
P4 failed/incomplete attempts are historical invalid; attempt 009 is accepted.

**Accepted limitations:** thermal throttle status is unavailable; Pipeline
throughput improvement does not prove lower single-frame end-to-end latency;
the run is bounded-memory engineering evidence, not industrial leak
certification; Stage K raw Level B limitation is inherited.

**Allowed paper claims:** a formal throughput increase of `4.165718x` for the
frozen offline workload, explicitly labeled descriptive; selected queue
capacity 1; P4 exact detection identity; P6 video-path validation; P7
30-minute bounded Pipeline stability. A formal Pipeline throughput/speedup
claim is currently usable with these restrictions.

**Prohibited paper claims:** statistical significance, universal/real-time
camera speedup, lower single-frame latency inferred from throughput, no
thermal throttling, industrial memory/leak certification, or raw Level B
equivalence.

**Unresolved issues:** none affecting the bounded throughput claim.

### Stage Q

**Current final status:** `STAGE_Q_COMPLETE_INT8_RECOMMENDED`.

**Authority document:** `docs/personal/STAGE_Q_FINAL_REPORT.md` and
`docs/personal/STAGE_Q_EVIDENCE_INDEX.md`.

**Canonical result paths:**

- split v2: `results/validation/stage_q/split_v2_deduplicated/`
- calibration/build summaries: `results/build/tensorrt/q3_int8_engine_v1/`
- accuracy: `results/validation/stage_q/q5_accuracy_v1/metrics_summary.json`
- Serial: `results/validation/stage_q/q6_serial_performance_v1/q6_serial_summary.json`
- Pipeline: `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/q7_pipeline_summary.json`
- confirmation: `results/validation/stage_q/q7_confirmation_v1/attempt_001/q7_confirmation_summary.json`
- configs: `configs/stage_q/runtime_q6_*.yaml` and `runtime_q7_*_pipeline_v1.yaml`

Q5 is the accuracy authority: FP16 vs INT8 mAP50-95
`0.359550` vs `0.352344`, mAP50 `0.656024` vs `0.647625`, accuracy
classification `ACCEPTABLE`. Q6 is the Serial authority: inference speedup
`1.269856x`, pre-sink throughput ratio `1.172850x`, mean/P95 end-to-end ratios
`0.852194/0.852066`. Q7 is the Pipeline authority: throughput ratio
`1.012575x`, classification `NO_MATERIAL_REGRESSION`; the 300-second
confirmation processed 22,680 frames in `319.674510239 s` with all 126 cycles
matching.

**Supplemental local paths:** no Stage Q directory exists in the scanned local
evidence root. This does not affect the repository canonical summaries.

**Invalid or superseded paths:** `split_v1` is historical because one
train/validation content duplicate existed. `split_v2_deduplicated` is the
authority (train/val/test 1260/359/180); its test set is unchanged, so the
canonical Q5-Q7 test results remain usable.

**Accepted limitations:** the INT8 Engine (4,825,956 bytes; SHA-256
`8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee`)
and calibration cache (10,655 bytes; SHA-256
`05bc8175bbbf3d01d8dcf8250c94c4dd90f03cd632c3112a5a98d41c5470a0ba`)
are retained under `/home/orin/edge-ai-local-models/stage_q/formal/`, together
with cache metadata, build summary, formal calibration manifest, and Engine
manifest v2. They are `EXTERNAL_LOCAL_ONLY` and must not enter Git. Binary
retention is verified and no longer unresolved. The formal calibration
manifest SHA-256 is
`f436fd9d82267174f71c2afaf575b9beef09763aa9e4fed12f054eaedefb69d9`;
its source corpus manifest SHA-256 is
`4e937507e0663ff76740b3fc6dd00552d82a3392a07a99fab17d816b7bc062b6`.
Some metadata/manifest files
lack a separately recorded expected hash for the metadata file itself; this is
a metadata-integrity limitation, not grounds to rebuild the Engine. The exact
Stage Q CUDA, L4T, architecture, and platform identity remains governed by
`results/validation/stage_q/q1_platform_asset_preflight_v1/platform_summary.json`;
the less-specific cache metadata does not erase that authority. Legacy
TensorRT 10.3 implicit calibration was used; QAT/Q-DQ, dynamic shape, batch >1,
DLA, and industrial-duration stability were not tested. Q6 thermal throttle
status was unavailable.

**Allowed paper claims:** the stated FP16-vs-INT8 accuracy trade-off; formal
Serial performance gain; Pipeline no-material-regression result; bounded
300-second confirmation; calibration provenance and layer precision counts.

**Prohibited paper claims:** using historical split_v1 as the current dataset
authority; TensorRT 11/QAT/Q-DQ conclusions; no-throttling or industrial
stability claims; large Pipeline gain from the `1.012575x` observation.

**Unresolved issues:** none affecting binary retention or tracked paper
metrics. Rebuilding the Engine is not required or recommended.

### Stage R

**Current final status:** `STAGE_R_COMPLETE_MULTI_BRANCH_ABLATION`.

**Authority document:** the append-only R3/R5 addendum in
`docs/personal/STAGE_R_FINAL_REPORT.md`, plus
`results/validation/stage_r/r5_pareto_closeout_v1/stage_r_final_status.json`.
The plan authority remains `docs/personal/STAGE_R_EXECUTION_PLAN.md`.

**Canonical result paths:**

- harness validation: `results/benchmark/stage_r/r3_unified_validation/validation_summary.json`
- formal ablation: `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/`
- Pareto closeout: `results/validation/stage_r/r5_pareto_closeout_v1/`
- paper inputs: all six CSV files under `results/paper/stage_r/`, governed by `metadata.json`
- configs: `configs/stage_r/runtime_v6_v0_off.yaml`, `runtime_v6_v2_pageable.yaml`, `runtime_v6_v3_pinned.yaml`, and `runtime_v6_v4_double_buffer.yaml`

Ablation v2/Attempt 2 is authoritative; v1/Attempt 1 is not comparable. The
earlier negative closeout remains valid only as the historical replacement-
selection record and is superseded for current research status by the D087
reopening and R3/R5 addendum. V0 remains the correctness-first deployment
baseline. V2 is only the best controlled research trade-off, V3 is not
selected, and V4 is a negative ablation result.

All of the following CSVs may directly feed paper tables/plots when their
metadata and restrictions travel with them:

- `stage_r_ablation_table.csv`
- `stage_r_accuracy_tradeoff.csv`
- `stage_r_fps_latency_plot.csv`
- `stage_r_incremental_comparison.csv`
- `stage_r_pareto_plot.csv`
- `stage_r_tail_latency_plot.csv`

**Supplemental local paths:** `/home/orin/edge-ai-local-evidence/stage_r/pre_r0/`
is `LOCAL_ONLY` pre-R0 provenance only. Its lack of R1-R6 does not imply global
absence.

**Invalid or superseded paths:** Attempt 1
`r3_v0_v2_v3_v4_ablation_v1/` is `HISTORICAL_VALID` only as a diagnostic
sampling record and is prohibited from final cross-variant tables. The
original `r6_closeout_v1` negative classification is a superseded historical
replacement-selection record. The retained Attempt 2 `set_01_v4` OOM failure
record is current `SUPPLEMENTAL` anomaly evidence, not
`HISTORICAL_INVALID`. The protocol-authorized rerun supplies the formal sample;
the failed run is excluded from aggregate performance samples but must remain
visible in limitations and anomaly disclosure.

**Accepted limitations:** five runs per variant do not establish statistical
significance; the unified single-thread harness is not comparable with the
multi-thread PipelineRunner; V2/V3/V4 accuracy is inherited through identical
detection SHA; Gate D remains `FAIL` (V2 mAP50 drop `0.00537575` exceeds
`0.005` by `0.00037575`); V4 has severe 8.98-10.24 s tail events and an OOM
event; no causal root cause beyond the tested design was established.

**Allowed paper claims:** Attempt 2 observed V2-vs-V0 `+129.87%` FPS and
`-56.68%` mean latency under the unified harness, paired with the accuracy
trade-off; V3's observed incremental benefit is about `+0.70%` FPS and is not
meaningful under the project rule; V4 is dominated and tail-unstable; V0 is
the deployment baseline and V2 is research-only.

**Prohibited paper claims:** V2 as correctness-equivalent or production
replacement; Attempt 1's ~231.9 FPS in a final comparison table; statistical
significance; pinned memory as a proven general benefit; V4 root-cause or
reliability generalizations; any untested V5/zero-copy result.

**Unresolved issues:** none affecting current Stage R table/plot inputs.

## 4. Cross-Stage Timing Definition Map

| Term | Boundary in this project | Where authoritative | Comparison rule |
|---|---|---|---|
| preprocess latency | preprocessing service/call begin to return; CPU OpenCV in V0/J/K/P, fused CUDA path in R V2-V4 | Stage J/K `preprocess_ms`; Stage P `preprocess_service_ms`; Stage R unified harness | Compare only with the same service boundary and harness. |
| inference latency | Stage K: immediately before `enqueueV3` through D2H stream synchronization, excluding separately recorded H2D; Stage J: backend host call; Stage Q calls it `inference_service_ms` | K7 protocol; J5.6 aggregate; Q6 summary | Host-roundtrip/service time is not GPU kernel-only time. |
| `backend_run_ms` | Backend API call/host-roundtrip timing where this legacy/diagnostic name appears | Result schema/diagnostic records | Treat as backend service only; do not relabel as full processing or GPU compute. |
| processing latency / `pre_sink_total` | Source service begin to postprocess service end; direct timestamp difference | J plan and P/Q/R trace contracts | In Pipeline it includes queue residence; excludes sink write. Serial and Pipeline rows must be labeled. |
| end-to-end latency | Source service begin to outer sink `write_frame` completion in P/Q; K7 E2E is preprocess begin through postprocess end and excludes image decode/result serialization | P/Q contracts; K7 README | K7 `e2e` and P/Q sink-inclusive E2E are different boundaries and cannot share an unlabeled column. |
| throughput | Frames divided by a specified measured wall window; J `pre_sink_fps` uses sum of per-frame pre-sink totals, J `wall_fps` uses measured wall; P/Q formal throughput uses first measured source begin to last measured postprocess end | stage-specific protocol/result | Always name window, runtime mode, warmup, measured count, and drop policy. |
| FPS | Reciprocal-latency equivalents (for example backend FPS) and wall-throughput FPS both exist | each machine result | Never treat reciprocal inference latency as application throughput. |
| queue residence | queue item publication/enqueue to next-stage service begin | Stage P Pipeline trace contract | Pipeline-only; it is part of Pipeline pre-sink processing latency, not service time. |
| stability duration | elapsed monotonic/source-active wall duration of a continuous campaign | J6, K6, P7, Q7 confirmation | Report duration with frames/cycles/failures; do not infer industrial lifetime. |

No cross-stage performance table may combine these metrics without an explicit
timing-boundary column. In particular, Stage J k5, Stage K K7, Stage P P5,
Stage Q Q6/Q7, and Stage R R3 use different runtimes and/or harness boundaries.

## 5. Global Canonical Asset Set

The minimum global paper authority set is:

- Training: final report, freeze record, archive index, validation/test JSON,
  effective args, selected training YAML, frozen-model SHA.
- ONNX: export metadata, model contract, PT/ONNX comparison, smoke result,
  ONNX SHA; the ignored binary is required only for execution/reinspection.
- Stage J: final report, consolidation index, J5.2 v2, J5.6 v3 aggregate,
  research gate v2, J6 stability and their protocol/environment/hash records.
- Stage K: K8 summary, task-level evaluation v2, canonical negative raw Level B
  evidence, K6 stability, repository K7 `performance_v1`,
  protocol/environment, FP16 Engine manifest, and retained Engine identity.
- Stage P: final report/index, P4 attempt 009 identity, P5R amendment/final
  reclassification, P6 report, and P7 report/config/runtime summaries.
- Stage Q: final report/index, split v2 manifests, formal calibration summary,
  retained Engine/cache identities, Q1 platform summary, Q5 accuracy, Q6
  Serial, Q7 Pipeline, confirmation, configs and hashes.
- Stage R: Final Report addendum, R3 Attempt 2, R5 Pareto closeout, runtime
  configs, paper CSVs and `metadata.json`.

Every primary candidate claim above has an authority document, a machine-
readable result, and a config or frozen experiment contract. The companion
CSV manifest is the row-level index.

## 6. Assets Explicitly Excluded from Paper

- local invalidated K7 output-allocation data;
- Stage R Attempt 1 cross-variant metrics and its ~231.9 FPS V0 value;
- Stage R V4 failed OOM attempt from aggregate performance samples; retain it
  as current supplemental anomaly/limitation evidence;
- Stage J failed J5.6 v1/v2, original blocked J5.7 v1, and original deep J8;
- Stage P historical P5 invalid conclusion and failed/incomplete P4 attempts;
- Stage Q split_v1 as the current split authority;
- smoke, diagnostic, selective-precision, rejected, or failed attempts as
  final numerical sources;
- external binary bytes as Git-tracked assets, or unavailable telemetry as if
  it had been inspected/measured.

## 7. Reconciliation Verdict

`COMPLETE_WITH_DOCUMENTED_LIMITATIONS`

Stage Q and Stage R are globally present and canonical despite their absence
from the local evidence root. Repository K7 `performance_v1` is canonical and
the local invalidated K7 copy is excluded. P5 is valid under P5R without a
rerun; P7 is formally complete. Stage R Attempt 2/v2 is the current paper
authority and the earlier negative closeout is only partially retained as a
historical replacement-selection disposition.

No metric conflict or global missing asset affecting the current main paper
claims remains unresolved. Frozen PT, training archives, Stage Q Engine/cache,
and Stage K Engine retention are hash verified; the binary reproducibility
assessment is `FULL_BINARY_RETENTION_CONFIRMED`. No retraining, TensorRT Engine
rebuild, or mandatory rerun is required. Publication-unified visualizations
have not yet been produced, and metadata files without a recorded self-hash
remain a documented integrity limitation.
