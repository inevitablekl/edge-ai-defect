# Stage Q Commit Preparation

## Verdict

`Q8_COMMIT_PREPARATION_COMPLETE`

This document is a dry-run plan only. No `git add`, commit, deletion, cleanup,
merge, tag, push, or content change outside this report was performed.

## Repository

- branch: `feature/jetson-tensorrt-int8`
- HEAD: `d130217bf8ab72c6e4e3907cdaa80842d8dcc5da`
- staged changes before this report: none
- tracked modifications before this report: none
- candidate-review source: `docs/personal/STAGE_Q_COMMIT_CANDIDATE_REVIEW.md`

The candidate review contained 19 proposed additions, 45 local-only files, and
2 later-cleanup candidates. This preparation report is itself an additional
future commit candidate, giving 20 planned additions.

## Commit Candidate List

| Path | Action | Reason |
|---|---|---|
| `docs/personal/STAGE_Q_GIT_HYGIENE_REPORT.md` | ADD_TO_COMMIT | Stage Q Git hygiene audit |
| `docs/personal/STAGE_Q_COMMIT_CANDIDATE_REVIEW.md` | ADD_TO_COMMIT | Candidate classification record |
| `docs/personal/STAGE_Q_COMMIT_PREPARATION.md` | ADD_TO_COMMIT | This dry-run preparation record |
| `results/build/tensorrt/k2_fp32_engine_v1/manifest.json` | ADD_TO_COMMIT | Lightweight engine manifest metadata |
| `results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json` | ADD_TO_COMMIT | Formal calibration manifest metadata |
| `results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json` | ADD_TO_COMMIT | Precision audit summary |
| `results/build/tensorrt/strict_fp32_notf32_investigation_v1/manifest.json` | ADD_TO_COMMIT | Lightweight diagnostic manifest metadata |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_hashes.json` | ADD_TO_COMMIT | Reproducibility hash metadata |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_hashes.json` | ADD_TO_COMMIT | Reproducibility hash metadata |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_hashes.json` | ADD_TO_COMMIT | Reproducibility hash metadata |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_hashes.json` | ADD_TO_COMMIT | Reproducibility hash metadata |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_hashes.json` | ADD_TO_COMMIT | Reproducibility hash metadata |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_hashes.json` | ADD_TO_COMMIT | Reproducibility hash metadata |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_fp16_hashes.json` | ADD_TO_COMMIT | Pipeline reproducibility hash metadata |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_int8_hashes.json` | ADD_TO_COMMIT | Pipeline reproducibility hash metadata |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_fp16_hashes.json` | ADD_TO_COMMIT | Pipeline reproducibility hash metadata |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_int8_hashes.json` | ADD_TO_COMMIT | Pipeline reproducibility hash metadata |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_fp16_hashes.json` | ADD_TO_COMMIT | Pipeline reproducibility hash metadata |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_hashes.json` | ADD_TO_COMMIT | Pipeline reproducibility hash metadata |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_hashes.json` | ADD_TO_COMMIT | Confirmation cycle hash metadata |

Existing tracked Stage Q final reports, Evidence Index, plans, decision/task
records, summaries, configurations, and validation tools are already in HEAD
and require no preparation action.

## Local Only Preservation

The following remain `KEEP_LOCAL` and must not enter the planned commit:

- Q5 full Result JSON: `results/validation/stage_q/q5_accuracy_v1/fp16_result.json`, `int8_result.json`
- Q6 full Result JSON: `results/validation/stage_q/q6_serial_performance_v1/pair{1,2,3}_{fp16,int8}_result.json`
- Q6 sidecars: `results/validation/stage_q/q6_serial_performance_v1/pair{1,2,3}_{fp16,int8}_sidecar.json`
- Q7 sidecars: `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair{1,2,3}_{fp16,int8}_sidecar.json`
- Q7 confirmation sidecar: `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_sidecar.json`
- Q6 raw traces: `results/validation/stage_q/q6_serial_performance_v1/pair{1,2,3}_{fp16,int8}_trace.jsonl`
- Q7 raw traces: `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair{1,2,3}_{fp16,int8}_trace.jsonl`
- Q7 confirmation trace: `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_trace.jsonl`
- Q6 environment captures: `results/validation/stage_q/q6_serial_performance_v1/environment_*.txt`
- Q7 telemetry/environment: `results/validation/stage_q/q7_confirmation_v1/attempt_001/tegrastats.txt`,
  `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_fp16_formal.txt`,
  `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_int8.txt`
- raw layer inspection: `results/build/tensorrt/q3_int8_engine_v1/raw_engine_layer_info.json`

The 13 experiment sidecars, 8 full Result JSON files, 13 raw traces, and 10
telemetry/environment captures total 45 KEEP_LOCAL files.

## Later Cleanup Candidates

Do not remove now:

- `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1.txt`
- `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_fp16.txt`

These are superseded failed-attempt environment captures and are only
`REMOVE_LATER` candidates under separate authorization.

## Ignore Analysis

Recommendation: `MINIMAL_IGNORE_RECOMMENDATION`.

The current `.gitignore` already covers build directories, engine/model binary
extensions, `*.jsonl`, and `*.log`. It does not consistently cover Stage Q raw
Result JSON, experiment sidecars, or telemetry `.txt` files. A future minimal
scoped rule set could cover:

```gitignore
results/validation/stage_q/**/result*.json
results/validation/stage_q/**/sidecar.json
results/validation/stage_q/**/environment_*.txt
results/benchmark/stage_q/**/sidecar.json
results/benchmark/stage_q/**/environment_*.txt
results/validation/stage_q/**/tegrastats.txt
```

These are recommendations only. `.gitignore` was not modified, and hash files,
manifests, summaries, and reports remain explicitly reviewable commit
candidates.

## Planned Commit

Suggested commit message:

`docs(stage-q): finalize INT8 PTQ evaluation closeout`

This is a recommendation only; no commit was created.

## Verification

Read-only checks completed:

- `git status --short`: only untracked candidate files; no tracked modifications
- `git diff --check`: passed
- `git diff --name-only`: empty
- `git diff --cached --name-only`: empty
- protected paths `src/`, `include/`, `CMakeLists.txt`, `configs/`, `tests/`: unchanged
- no tracked engine/cache/ONNX/PT artifact
- no workspace file larger than 50 MiB

## Final Report

### Add Plan

20 files: the 19 candidates from the candidate review plus this preparation
report. The exact paths are listed above.

### Keep Local

45 raw/provenance files remain local-only and are listed above by evidence
group and exact path pattern.

### Ignore Recommendation

`MINIMAL_IGNORE_RECOMMENDATION`; propose only, do not apply.

### Commit Message

`docs(stage-q): finalize INT8 PTQ evaluation closeout`

## Scope Check

No add, commit, delete, cleanup, merge, tag, push, or `.gitignore` modification
was performed.

## Authorization

git add: `NOT AUTHORIZED`

commit: `NOT AUTHORIZED`

merge: `NOT AUTHORIZED`
