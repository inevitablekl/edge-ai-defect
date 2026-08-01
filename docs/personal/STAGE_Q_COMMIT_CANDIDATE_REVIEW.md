# Stage Q Commit Candidate Review

## Verdict

`Q8_COMMIT_CANDIDATE_REVIEW_COMPLETE`

This is a read-only candidate review. No file was staged, committed, removed,
cleaned, moved, or ignored by this task.

## Repository

- branch: `feature/jetson-tensorrt-int8`
- HEAD: `d130217bf8ab72c6e4e3907cdaa80842d8dcc5da`
- upstream: `origin/feature/jetson-tensorrt-int8`
- branch relation: up to date
- staged changes: none
- tracked modifications: none

The candidate universe contains 64 existing untracked files under the Stage Q
validation/benchmark/build evidence roots plus the two Stage Q audit reports.
Eighteen
of the evidence/build files are ignored by Git and therefore do not appear in
ordinary `git status --short`; they are included below.

## Candidate Table

### COMMIT candidates

| Path | Category | Recommendation | Reason |
|---|---|---|---|
| `docs/personal/STAGE_Q_GIT_HYGIENE_REPORT.md` | TRACK | COMMIT | Stage Q hygiene audit record |
| `docs/personal/STAGE_Q_COMMIT_CANDIDATE_REVIEW.md` | TRACK | COMMIT | This candidate review record |
| `results/build/tensorrt/k2_fp32_engine_v1/manifest.json` | TRACK | COMMIT | Lightweight engine manifest metadata |
| `results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json` | TRACK | COMMIT | Formal calibration manifest metadata |
| `results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json` | TRACK | COMMIT | Precision audit summary |
| `results/build/tensorrt/strict_fp32_notf32_investigation_v1/manifest.json` | TRACK | COMMIT | Lightweight diagnostic manifest metadata |

The following hash files are small reproducibility metadata and are candidates
for a future authorized commit:

| Path | Category | Recommendation | Reason |
|---|---|---|---|
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_fp16_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_int8_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_fp16_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_int8_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_fp16_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_hashes.json` | TRACK | COMMIT | Run/cycle reproducibility hashes |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_hashes.json` | TRACK | COMMIT | Confirmation cycle hashes |

### KEEP_LOCAL candidates

#### Experiment sidecars

All sidecars are generated during experiments and remain local-only:

| Path | Category | Recommendation | Reason |
|---|---|---|---|
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_fp16_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_int8_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_fp16_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_int8_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_fp16_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_sidecar.json` | LOCAL_ONLY | KEEP_LOCAL | Experiment-generated provenance sidecar |

#### Full Result JSON

| Path | Category | Recommendation | Reason |
|---|---|---|---|
| `results/validation/stage_q/q5_accuracy_v1/fp16_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw accuracy result dump |
| `results/validation/stage_q/q5_accuracy_v1/int8_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw accuracy result dump |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw benchmark output |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw benchmark output |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw benchmark output |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw benchmark output |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw benchmark output |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_result.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw benchmark output |

#### Raw traces

| Path | Category | Recommendation | Reason |
|---|---|---|---|
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw timing trace |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw timing trace |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw timing trace |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw timing trace |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw timing trace |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw timing trace |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw confirmation trace |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_fp16_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw pipeline trace |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_int8_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw pipeline trace |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_fp16_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw pipeline trace |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_int8_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw pipeline trace |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_fp16_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw pipeline trace |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_trace.jsonl` | LOCAL_ONLY | KEEP_LOCAL | Raw pipeline trace |

| `results/build/tensorrt/q3_int8_engine_v1/raw_engine_layer_info.json` | LOCAL_ONLY | KEEP_LOCAL | Full raw layer inspection output |

#### Telemetry and environment captures

| Path | Category | Recommendation | Reason |
|---|---|---|---|
| `results/validation/stage_q/q6_serial_performance_v1/environment_after_pair1_fp16.txt` | LOCAL_ONLY | KEEP_LOCAL | Environment capture |
| `results/validation/stage_q/q6_serial_performance_v1/environment_after_pair2_int8_pre_fp16.txt` | LOCAL_ONLY | KEEP_LOCAL | Environment capture |
| `results/validation/stage_q/q6_serial_performance_v1/environment_after_pair3_fp16_pre_int8.txt` | LOCAL_ONLY | KEEP_LOCAL | Environment capture |
| `results/validation/stage_q/q6_serial_performance_v1/environment_post.txt` | LOCAL_ONLY | KEEP_LOCAL | Environment capture |
| `results/validation/stage_q/q6_serial_performance_v1/environment_pre_pair1.txt` | LOCAL_ONLY | KEEP_LOCAL | Environment capture |
| `results/validation/stage_q/q6_serial_performance_v1/environment_pre_pair2.txt` | LOCAL_ONLY | KEEP_LOCAL | Environment capture |
| `results/validation/stage_q/q6_serial_performance_v1/environment_pre_pair3.txt` | LOCAL_ONLY | KEEP_LOCAL | Environment capture |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/tegrastats.txt` | LOCAL_ONLY | KEEP_LOCAL | Confirmation telemetry |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_fp16_formal.txt` | LOCAL_ONLY | KEEP_LOCAL | Pipeline environment capture |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_int8.txt` | LOCAL_ONLY | KEEP_LOCAL | Pipeline environment capture |

## REMOVE_LATER candidates

These are marked only; no deletion was performed.

| Path | Category | Recommendation | Reason |
|---|---|---|---|
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1.txt` | DELETE_CANDIDATE | REMOVE_LATER | Superseded failed-attempt environment capture |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_fp16.txt` | DELETE_CANDIDATE | REMOVE_LATER | Superseded failed-attempt environment capture |

## Verify Tracked Risk

`git ls-files` found no tracked `.engine`, `.cache`, `.onnx`, `.pt`, `.pth`,
`.plan`, or `.bin` artifact. No tracked JSON larger than 5 MiB was found, and
`find . -type f -size +50M` returned no files.

No current `TRACKING_RISK` exists in the Git index. The five ignored build
metadata candidates require explicit review before any future force-add.

## Final Report

### Commit Candidates

19 candidates are suitable for a future authorized commit: the two audit
reports, four lightweight build manifests/audit summaries, and thirteen hash
metadata files. Existing tracked Stage Q final reports, Evidence Index, plans, decision
records, task records, summaries, configurations, and validation tools remain
already committed at HEAD.

### Local Only

45 candidates remain local-only: 13 experiment sidecars, 8 full Result JSON
dumps, 13 raw traces, and 10 telemetry/environment captures.

### Cleanup Candidates

2 files are optional later cleanup candidates. They were not removed.

### Scope Check

No `git add`, commit, deletion, `git rm`, `git clean`, `.gitignore` change,
merge, tag, push, or source/config/test modification was performed.

## Authorization

Commit: `NOT AUTHORIZED`

Merge: `NOT AUTHORIZED`
