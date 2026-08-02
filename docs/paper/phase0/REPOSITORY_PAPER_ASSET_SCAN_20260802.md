# Project Asset Scan

Status: Historical Phase 0.1 scan snapshot.
Final evidence classification is governed by PAPER_EVIDENCE_AUTHORITY_MAP_v1.0.md.

Scan date: 2026-08-02  
Scan scope: current working tree of `edge-ai-defect`  
Method boundary: repository/path/filename inventory only. No experiment was rerun and no metric was inferred. “Paper Value” describes possible evidentiary use, not a paper conclusion.

## 1. Repository Overview

### 1.1 Filtered repository structure

The structure below excludes `.git/`, `build/`, `build_r3/`, `CMakeFiles/`, Python caches, and pytest caches. Repeated run directories are grouped with `{...}`; raw NEU-DET image/XML filenames are summarized by count rather than expanded 3,600 times.

```text
edge-ai-defect/
├── AGENTS.md
├── CMakeLists.txt
├── J5.1_CORPUS_RECOVERY_REPORT.md
├── README.md
├── environment_snapshot.txt
├── requirements.txt
├── requirements-lock.txt
├── backend_tensorrt/
│   ├── cuda_preprocessor.{cu,hpp}
│   ├── pageable_raw_staging.{cpp,hpp}
│   └── pinned_raw_staging.{cpp,hpp}
├── configs/
│   ├── dataset/.gitkeep
│   ├── export/yolov8n_neudet_frozen.yaml
│   ├── model_contracts/yolov8n_neudet_frozen.yaml
│   ├── stage_j/{test_inventory.yaml,j5_3_local/}
│   ├── stage_k/{selective_fp16_notf32_m3.yaml,selective_fp16_notf32_v1.yaml,test_inventory.yaml}
│   ├── stage_q/{runtime_fp16_v4_smoke.yaml,runtime_int8_v5_smoke.yaml,runtime_q6_*.yaml,runtime_q7_*.yaml}
│   ├── stage_r/{cuda_preprocess_corpus_v1.yaml,runtime_v5_v0_compat.yaml,runtime_v6_*.yaml}
│   └── train/{training_evidence_manifest.json,yolov8n_neudet_*.yaml}
├── data/
│   ├── interim/.gitkeep
│   ├── processed/.gitkeep
│   ├── yolo/.gitkeep
│   └── raw/NEU-DET/
│       ├── IMAGES/                 (1,800 JPG source images)
│       └── ANNOTATIONS/            (1,800 XML annotations)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── BASELINE_TRAINING.md
│   ├── CODING_RULES.md
│   ├── MODEL_FREEZE_RECORD.md
│   ├── PROJECT_BRIEF.md
│   ├── REQUIREMENTS.md
│   ├── TRAINING_ARCHIVE_INDEX.md
│   ├── TRAINING_FINAL_REPORT.md
│   └── personal/
│       ├── DECISIONS.md
│       ├── ENVIRONMENT.md
│       ├── EXPERIMENT_PLAN.md
│       ├── TASKS.md
│       ├── J2_2_V2_EVIDENCE_RECONCILIATION.md
│       ├── J4_2_CROSS_ARCH_NUMERICAL_INVESTIGATION.md
│       ├── J5.1_ENTRY_REPORT.md
│       ├── J5_1_CORPUS_RECOVERY_RESOLUTION.md
│       ├── J8_PRE_REMEDIATION_DIAGNOSTIC.md
│       ├── M{1..5}_EXECUTION_PLAN.md
│       ├── STAGE_J_{CPU_BASELINE_SUMMARY,EXECUTION_PLAN,FINAL_REPORT,J4_ENTRY_BRIEF,J5_6_PREFLIGHT_REMEDIATION,TASK_CARDS}.md
│       ├── STAGE_K_{EXECUTION_PLAN,TASK_CARDS,TASK_EVALUATION_PROTOCOL}.md
│       ├── STAGE_P_{BASELINE_REPORT,EVIDENCE_INDEX,EXECUTION_PLAN,FINAL_REPORT,TASK_CARDS}.md
│       ├── STAGE_Q*.md             (plan, task cards, evidence index, Q2–Q8 reports, closeout/audit reports)
│       └── STAGE_R*.md             (plan, task cards, evidence index, R0–R5 reports, final report, paper-data note)
├── experiments/
│   ├── configs/.gitkeep
│   ├── figures/.gitkeep
│   ├── logs/.gitkeep
│   ├── results/.gitkeep
│   ├── tables/.gitkeep
│   └── training/
│       ├── README.md
│       └── yolov8n_neudet_smoke_{20260711_160810,20260711_173444,smoke_20260711_160521}/
│           ├── command.txt
│           ├── config.yaml
│           ├── environment.txt
│           ├── git_commit.txt
│           ├── start_time.txt
│           ├── end_time.txt
│           └── summary.json
├── include/edge_ai_defect/
│   ├── application/
│   ├── backend_ort/
│   ├── backend_tensorrt/
│   ├── core/
│   ├── inference/
│   ├── model/
│   ├── postprocess/
│   ├── preprocess/
│   ├── runtime/
│   └── stage_q/
├── models/
│   ├── engine/.gitkeep
│   ├── onnx/{.gitkeep,yolov8n_neudet_frozen.onnx}
│   ├── pretrained/.gitkeep
│   ├── pt/.gitkeep
│   ├── pytorch/.gitkeep
│   └── tensorrt/{.gitkeep,yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json}
├── results/
│   ├── archive/stage_k_diagnostics_v1/
│   │   ├── archive_manifest.json
│   │   ├── configs/stage_k/
│   │   ├── tools/diagnostic/
│   │   └── results/validation/{jetson_tensorrt_fp32,jetson_tensorrt_strict_fp32_notf32,stage_k_task_eval_v1}/
│   ├── audit/stage_j_lightweight_audit/stage_j_audit_v1/
│   ├── benchmark/
│   │   ├── ort_cpu/20260719_850252b/{pilot,run_01,run_02,run_03,run_04,run_05}/
│   │   ├── jetson_ort_cpu/
│   │   │   ├── python_reference/j5_1_python_reference_v1/
│   │   │   ├── profile_precheck/j5_2_candidate_semantic_precheck_v2/
│   │   │   ├── profile_sizing/j5_3_candidate_sizing_v1/{raw_runs,telemetry}/
│   │   │   ├── profile_selection/j5_4_profile_selection_v1/
│   │   │   ├── profile_baseline/j5_5_profile_baseline_v1/k1/
│   │   │   ├── controlled_supplement/j5_5_controlled_supplement_v1/
│   │   │   ├── profile_stability/j5_6_profile_stability_v1/telemetry/
│   │   │   ├── tuned/j5_6_tuned_formal_baseline_v3/runs/
│   │   │   ├── stability/j6_tuned_stability_v1/
│   │   │   ├── j5_7_evidence_gate_v1/
│   │   │   └── j5_7_research_grade_gate_v2/
│   │   ├── stage_p/p5_serial_vs_pipeline_v1/
│   │   ├── stage_q/q7_pipeline_v1/attempt_001/
│   │   └── stage_r/
│   │       ├── r3_unified_validation/runs/{set_01_v0,set_01_v2,set_01_v3,set_01_v4}/
│   │       ├── r3_v0_v2_v3_v4_ablation_v1/runs/{set_01..05}_{v0,v2,v3,v4}/
│   │       └── r3_v0_v2_v3_v4_ablation_v2/runs/{set_01..05}_{v0,v2,v3,v4}/
│   ├── consolidation/
│   │   ├── m5/{20260719_c24eefa,20260719_da86e53}/
│   │   └── stage_j/stage_j_cpu_baseline_v1/
│   ├── onnx_export/{environment_provenance.txt,export_metadata.json,onnxruntime_smoke_test.json,pt_onnx_compare.json}
│   ├── paper/stage_r/{metadata.json,stage_r_*.csv}
│   ├── platform/
│   │   ├── jetson/environment/j1_baseline_v1/
│   │   └── tensorrt/{d062_contract_v1,k1_environment_v1,k1_environment_v2,k1_environment_v3,k1_environment_v4}/
│   ├── training/
│   │   ├── training_experiment_summary.{csv,json}
│   │   └── evidence/{effective_args,EXPERIMENT_PROVENANCE.json,frozen_test_metrics.*,validation_metrics_by_experiment.*,commands/environment}
│   └── validation/
│       ├── preprocess_level_a/
│       ├── postprocessor_only/{case_no_padding,case_odd_padding,case_odd_vertical_padding}/
│       ├── onnx_runtime_engine_level_b/
│       ├── level_c/20260719_1073fa8/
│       ├── jetson_ort_level_b/{j3_1,j3_3,j3_4,j3_5,j3_6,j3_7,j3_8,j3_9,j3_10}_*/
│       ├── jetson_ort_level_c/{j4_1_level_a_v1,j4_2_level_b_v2,j4_3_level_c_v1,j4_3_level_c_v2,j4_evidence_gate_v1}/
│       ├── jetson_ort_level_j3_9_remediation_investigation_v1/
│       ├── jetson_tensorrt_fp16/{k5_correctness_v1,k5_correctness_v2,k5_correctness_v3}/
│       ├── jetson_tensorrt_selective_fp16_notf32_{m3,v1}/
│       ├── jetson_tensorrt_task_level_v1/
│       ├── stage_k_level_b_reference/stage_k_level_b_reference_v1/
│       ├── stage_k_task_eval_v2/{ground_truth,ground_truth_audit,inference,metrics,protocol,split}/
│       ├── stage_k6/{stability_smoke,stability_smoke2,stability_smoke3,stability_v1}/
│       ├── stage_k7/performance_v1/{fp16_original,fp32_notf32}/
│       ├── stage_k8/final_summary_v1/
│       ├── stage_k_{cleanup_audit_v1,status_audit_v1}/
│       ├── stage_p/{p6_video_v1,p7_stability_v1/attempt_001}/
│       ├── stage_q/{q1_platform_asset_preflight_v1,q5_accuracy_v1,q6_serial_performance_v1,q7_confirmation_v1,split_v2_deduplicated}/
│       └── stage_r/{r0_planning_freeze_v1,r1_baseline_profiling_v1,r2_1_cuda_preprocess_v1,r2_v2_pageable_correctness_v1,r2_v3_pinned_correctness_v1,r2_v4_double_buffer_v1,r5_pareto_closeout_v1,r6_closeout_v1}/
├── scripts/{convert_neudet_to_yolo.py,export_onnx.py,generate_evidence_patch.py,train_yolo.py}
├── src/                         (C++ runtime, ORT, TensorRT, Serial, Pipeline, sinks and Stage Q implementation)
├── stage_r/                     (pageable, pinned and double-buffer experimental runners)
├── tests/
│   ├── cmake/
│   ├── data/{m5,postprocessor_reference,preprocess_level_a}/
│   ├── smoke/
│   └── test_* / stage_j_*       (unit, smoke, validation and experiment-tool tests)
├── third_party/onnxruntime/1.23.2/linux-aarch64/{include,lib,manifests,licenses}
└── tools/
    ├── benchmark/               (ORT, Stage J/K/R benchmark runners and analyzers)
    ├── diagnostic/              (TensorRT precision diagnostics)
    └── validation/              (reference generation, cross-backend comparison and Stage K/P/Q/R evaluators)
```

### 1.2 Asset-oriented summary

|Location|Observed contents|Inventory note|
|---|---|---|
|`experiments/training/`|3 smoke-run folders|Each has config, command, environment, timestamps, commit and summary JSON; formal training runs referenced by reports are not present here.|
|`results/training/`|21 files|Training summaries, effective arguments, validation metrics, frozen-test metrics and provenance.|
|`results/onnx_export/`|4 files|Export metadata, PT/ONNX comparison, ORT smoke result and environment provenance.|
|`results/benchmark/ort_cpu/`|37 files|Five-run ORT CPU timing set plus pilot.|
|`results/benchmark/jetson_ort_cpu/`|212 files|Jetson ORT reference, profile selection, baseline, stability, telemetry and evidence gates.|
|`results/validation/jetson_ort_level_b/`|80 files|Jetson ORT build/options/threading/trace/regression/sanitizer evidence.|
|`results/validation/jetson_ort_level_c/`|55 files|Cross-implementation and task-level validation evidence.|
|`results/platform/tensorrt/`|137 files|TensorRT environment, contract and engine-build logs/reports.|
|`results/validation/jetson_tensorrt_fp16/`|29 files|FP16 correctness and provenance.|
|`results/validation/stage_k6/`, `stage_k7/`, `stage_k8/`|83 files total|FP16 stability, performance samples/comparison and final experiment summary.|
|`results/validation/stage_k_task_eval_v2/`|38 files|Ground truth, split, detections, latency, classwise/backend metrics and verification.|
|`results/validation/stage_q/`|60 files|INT8 preflight, split remediation, accuracy, serial performance and confirmation.|
|`results/benchmark/stage_q/`|23 files|FP16/INT8 Pipeline paired-run results and traces.|
|`results/benchmark/stage_p/`, `results/validation/stage_p/`|21 files total|Serial/Pipeline comparison, video validation and long stability summary.|
|`results/benchmark/stage_r/`, `results/validation/stage_r/`|450 files total|INT8 data-path profiling, correctness gates and multi-branch ablation runs.|
|`results/paper/stage_r/`|7 files|Six CSV datasets plus metadata JSON prepared for tables/plots; no rendered figure files.|
|`docs/**/*REPORT*.md`, evidence indexes|Report/index assets|Human-readable status and links; evidentiary value depends on referenced machine-readable files.|

Filtered working-tree totals are 338 directories and 5,507 files. This includes the local raw NEU-DET dataset. Outside filtered build/cache paths the main requested formats comprise 790 JSON, 18 CSV and 155 `.log` files. No PNG/JPEG/SVG/PDF paper figure exists outside `data/raw/`; the 1,800 JPG files under `data/raw/NEU-DET/IMAGES/` are source dataset images, not prepared paper figures.

## 2. Stage Asset Mapping

|Stage|Files|Purpose|Paper Value|
|---|---|---|---|
|training|`configs/train/*.yaml`; `configs/train/training_evidence_manifest.json`; `experiments/training/*`; `results/training/*`; `docs/BASELINE_TRAINING.md`; `docs/TRAINING_FINAL_REPORT.md`; `docs/TRAINING_ARCHIVE_INDEX.md`; `docs/MODEL_FREEZE_RECORD.md`|Training configuration, smoke-run provenance, nine-experiment metric summary, frozen-test metrics, model selection/freeze record|High for training setup, validation/test metrics and reproducibility; lower for visual presentation because referenced training plots are absent from the current tree.|
|ONNX|`configs/export/yolov8n_neudet_frozen.yaml`; `configs/model_contracts/yolov8n_neudet_frozen.yaml`; `models/onnx/yolov8n_neudet_frozen.onnx`; `results/onnx_export/*`; `tools/validation/compare_pt_onnx.py`; export/compare tests|Export contract, model artifact, PT-vs-ONNX comparison and ORT smoke validation|High for export traceability and functional equivalence. The ONNX file exists locally but is ignored/untracked, so portable audit relies on metadata unless the external artifact is supplied.|
|ORT|`results/benchmark/ort_cpu/*`; `results/benchmark/jetson_ort_cpu/*`; `results/consolidation/{m5,stage_j}/*`; `results/validation/{onnx_runtime_engine_level_b,level_c,jetson_ort_level_b,jetson_ort_level_c}/*`; Stage J reports/indexes|C++ ONNX Runtime correctness, CPU baseline, profile selection, repeat runs, stability, resource telemetry and evidence gates|Very high for the CPU baseline and reproducibility. Contains raw timing TSV/JSON, summaries, commands, environment and provenance.|
|TensorRT FP16|`configs/stage_k/*`; FP16 manifest under `models/tensorrt/`; `results/platform/tensorrt/*`; `results/validation/jetson_tensorrt_fp16/*`; `jetson_tensorrt_selective_fp16_notf32_*`; `jetson_tensorrt_task_level_v1/*`; `stage_k_task_eval_v2/*`; `stage_k6/*`; `stage_k7/*`; `stage_k8/*`; Stage K reports/protocols|Platform acceptance, engine provenance, raw/task correctness, stability and FP32-vs-FP16 performance|Very high for FP16 deployment evaluation. Important limitation: raw Level B comparison failed and task-level acceptance is the stated basis.|
|TensorRT INT8|`configs/stage_q/*int8*`; `results/validation/stage_q/{q1,q5,q6,q7,split_v2_deduplicated}/*`; `results/benchmark/stage_q/q7_pipeline_v1/*`; Stage Q reports/index; Stage R configs/results/reports; `results/paper/stage_r/*`|INT8 PTQ build/calibration record, FP16-vs-INT8 accuracy, serial/pipeline performance, confirmation, and later data-path ablation|Very high for INT8 accuracy/performance and negative-result analysis. Stage R paper CSVs are directly reusable as table/plot inputs, but rendered plots are absent.|
|Pipeline|`configs/stage_q/runtime_q7_*_pipeline_v1.yaml`; `results/benchmark/stage_p/p5_serial_vs_pipeline_v1/*`; `results/validation/stage_p/{p6_video_v1,p7_stability_v1}/*`; `results/benchmark/stage_q/q7_pipeline_v1/*`; Stage P/Q Pipeline reports and evidence indexes|Bounded Pipeline correctness, Serial/Pipeline paired comparison, video path, 1,800-second stability, FP16/INT8 Pipeline comparison|Very high for throughput and bounded-runtime evidence. Latency and throughput must remain separate claims; some raw traces/telemetry are documented as local-only.|

## 3. Experiment Data Inventory

|Experiment|Data Location|Format|
|---|---|---|
|Training smoke runs (3)|`experiments/training/yolov8n_neudet_smoke_*/`|YAML, JSON, TXT|
|Formal training comparison and three-seed baseline|`results/training/training_experiment_summary.*`; `results/training/evidence/validation_metrics_by_experiment.*`; `effective_args/`|CSV, JSON, YAML, TXT|
|Frozen-model held-out test|`results/training/evidence/frozen_test_metrics.*`; provenance/command/environment files in the same directory|CSV, JSON, TXT|
|ONNX export and PT/ONNX comparison|`results/onnx_export/`|JSON, TXT|
|ORT CPU five-run baseline|`results/benchmark/ort_cpu/20260719_850252b/`|JSON, TSV, TXT, GZ|
|Jetson ORT reference/profile sizing/selection|`results/benchmark/jetson_ort_cpu/{python_reference,profile_precheck,profile_sizing,profile_selection}/`|JSON, JSONL, TXT, stdout/stderr|
|Jetson ORT controlled and tuned baselines|`results/benchmark/jetson_ort_cpu/{profile_baseline,controlled_supplement,tuned}/`|JSON, JSONL, TXT, Markdown|
|Jetson ORT stability and evidence gates|`results/benchmark/jetson_ort_cpu/{profile_stability,stability,j5_7_*}/`; `results/consolidation/stage_j/`|JSON, TXT, Markdown|
|ORT Level B/Level C correctness|`results/validation/{onnx_runtime_engine_level_b,level_c,jetson_ort_level_b,jetson_ort_level_c}/`|JSON, F32LE, YAML, TXT, Markdown|
|TensorRT environment and engine-build evidence|`results/platform/tensorrt/`|JSON, LOG, TXT, YAML, Markdown, C++ snapshots|
|TensorRT FP16 correctness|`results/validation/jetson_tensorrt_fp16/`; `jetson_tensorrt_selective_fp16_notf32_*`|JSON, TXT, Markdown|
|TensorRT FP16 task-level evaluation|`results/validation/stage_k_task_eval_v2/`; `jetson_tensorrt_task_level_v1/`|JSON, TXT|
|TensorRT FP16 stability|`results/validation/stage_k6/stability_v1/`|JSON, JSONL, LOG, TXT|
|TensorRT FP32-vs-FP16 performance|`results/validation/stage_k7/performance_v1/`|CSV, JSON, LOG, TXT|
|TensorRT FP16 final consolidation|`results/validation/stage_k8/final_summary_v1/`|JSON, TXT|
|INT8 platform/calibration preflight and split remediation|`results/validation/stage_q/{q1_platform_asset_preflight_v1,split_v2_deduplicated}/`; Stage Q Q2/Q3 reports|JSON, Markdown|
|FP16-vs-INT8 accuracy|`results/validation/stage_q/q5_accuracy_v1/`|JSON|
|FP16-vs-INT8 Serial performance, 3 paired runs|`results/validation/stage_q/q6_serial_performance_v1/`|JSON, TXT|
|FP16-vs-INT8 Pipeline performance, 3 paired runs|`results/benchmark/stage_q/q7_pipeline_v1/attempt_001/`|JSON, JSONL, TXT|
|INT8 300-second Pipeline confirmation|`results/validation/stage_q/q7_confirmation_v1/attempt_001/`|JSON|
|FP16 Serial-vs-Pipeline comparison|`results/benchmark/stage_p/p5_serial_vs_pipeline_v1/`|Markdown summaries/reports|
|Pipeline video validation|`results/validation/stage_p/p6_video_v1/`|Markdown report|
|Pipeline 1,800-second stability|`results/validation/stage_p/p7_stability_v1/attempt_001/`|CSV, JSON/JSONL, LOG, YAML, TXT, Markdown|
|INT8 V0 profiling|`results/validation/stage_r/r1_baseline_profiling_v1/`|JSON, TXT|
|CUDA preprocessing/pageable/pinned/double-buffer correctness gates|`results/validation/stage_r/r2_1_cuda_preprocess_v1/`; `r2_v2_*`; `r2_v3_*`; `r2_v4_*`|JSON, TXT|
|INT8 V0/V2/V3/V4 multi-branch ablation|`results/benchmark/stage_r/r3_*`|JSON, LOG, Markdown|
|Stage R paper table/plot source data|`results/paper/stage_r/`|CSV, JSON|

### 3.1 Table and image data

Table/plot source files found:

- `results/paper/stage_r/stage_r_ablation_table.csv`
- `results/paper/stage_r/stage_r_accuracy_tradeoff.csv`
- `results/paper/stage_r/stage_r_incremental_comparison.csv`
- `results/paper/stage_r/stage_r_fps_latency_plot.csv`
- `results/paper/stage_r/stage_r_pareto_plot.csv`
- `results/paper/stage_r/stage_r_tail_latency_plot.csv`
- `results/training/training_experiment_summary.csv`
- `results/training/evidence/frozen_test_metrics.csv`
- `results/training/evidence/validation_metrics_by_experiment.csv`
- `results/validation/stage_k7/performance_v1/**/latency_samples.csv` (8 files)
- `results/benchmark/ort_cpu/20260719_850252b/run_*/timings.tsv` (5 files)
- `results/validation/postprocessor_only/*/cpp_detections.tsv` (3 files)
- `tests/data/postprocessor_reference/*/python_golden_detections.tsv` (3 files; test-reference data rather than experiment results)
- `results/validation/stage_p/p7_stability_v1/attempt_001/telemetry/process_resources.csv`

Image inventory:

- Dataset images: `data/raw/NEU-DET/IMAGES/` contains 1,800 JPG files.
- Prepared paper figures or experiment visualizations: none found in PNG, JPG, JPEG, SVG or PDF format outside the raw dataset.
- `experiments/figures/` contains only `.gitkeep`.

## 4. Missing Evidence

1. Rendered paper figures are absent. The repository contains CSV inputs for Stage R plots/tables, but no generated PNG/SVG/PDF figures.
2. Training visual artifacts referenced by `docs/TRAINING_FINAL_REPORT.md`—confusion matrices, PR/F1/P/R curves, prediction previews and `predictions.json` under `experiments/evaluation/...`—are not present in the current working tree.
3. The formal training run directories and `best.pt` checkpoints referenced by the training report are not present in `experiments/training/` or `models/pytorch/`; the report points to an external/offline checkpoint archive. Machine-readable aggregate metrics and provenance are present under `results/training/evidence/`.
4. The frozen ONNX file exists locally at `models/onnx/yolov8n_neudet_frozen.onnx` but is ignored/untracked. Its export metadata and comparison evidence are tracked; the binary itself is not portable through the repository alone.
5. The TensorRT FP16 engine binary and INT8 engine/calibration artifacts are not represented as committed binaries. Manifests, hashes, logs and reports exist, but binary reinspection requires the corresponding local/external artifacts.
6. Stage J records that J5.5 lacks independently reconstructable per-frame timing distributions/raw telemetry, parts of J6 power telemetry (including VDD_IN) were unavailable, and the original deep evidence gate was not passed.
7. Stage P states that raw traces, telemetry, generated video and other large runtime artifacts are local-only. The committed summaries support reported aggregates but do not include every raw sample.
8. Thermal-throttle evidence is explicitly unavailable in the Stage P P5 result and Stage Q formal serial evidence. These absences must remain visible wherever thermal stability is discussed.
9. `experiments/logs/`, `experiments/results/` and `experiments/tables/` contain only `.gitkeep`; actual evidence is stored under `results/`, so these nominal experiment locations do not provide an independent inventory.
10. No single repository-wide evidence manifest links all six paper stages. Stage-specific evidence indexes exist for J/P/Q/R, while training and K use separate reports/manifests.

## 5. Risk

|Risk|Observed basis|Impact on paper asset use|
|---|---|---|
|Report/evidence mismatch|Some Markdown reports reference external, ignored or local-only artifacts.|A report cannot be treated as a complete audit bundle without checking its referenced files and hashes.|
|Generated figure gap|No rendered experiment figure exists outside raw dataset images.|Plot/table claims can be traced to CSV/JSON, but publication-ready visual assets are currently absent.|
|Binary artifact portability|Frozen ONNX is ignored/untracked; PT and TensorRT engine binaries are absent from the committed tree.|Reproduction from repository checkout alone may stop at metadata/hash verification.|
|Mixed evidence maturity|Smoke runs, historical failed gates, formal runs, audits and closeout summaries coexist under `results/`.|Files must be selected by final status/evidence index, not merely by a matching stage name.|
|Known TensorRT FP16 raw mismatch|Stage K final summary retains a failed raw Level B comparison while accepting FP16 at task level.|Any asset use must distinguish raw numerical equivalence from task-level acceptance.|
|Historical split duplication|Stage Q documents a historical train/validation content duplicate and a deduplicated v2 split.|Metrics must identify the split contract; results from different split authorities should not be silently combined.|
|Incomplete environment telemetry|Power and thermal fields are unavailable in several formal runs.|No unsupported power-efficiency or no-throttling claim can be derived from these assets.|
|Pipeline interpretation|Pipeline assets include throughput and end-to-end latency under bounded queues.|Higher throughput must not be presented as proof of lower single-frame latency.|
|Stage R status chronology|The Stage R final report contains an earlier negative-result closeout plus a later reopening addendum; newer R3 ablation and paper CSV assets also exist.|Paper asset selection must use the latest accepted status/decision and avoid treating the earlier closeout as the sole current authority.|
|Raw-data volume and repository noise|The working tree includes 1,800 JPG and 1,800 XML source files plus archived diagnostics and repeated run logs.|Automated inventories can overcount source/diagnostic files as paper evidence unless paths are filtered by evidence authority.|
