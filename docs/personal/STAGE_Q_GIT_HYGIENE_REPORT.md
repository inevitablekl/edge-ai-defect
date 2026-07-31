# Stage Q Git Hygiene Audit Report

## Verdict

`Q8_GIT_HYGIENE_AUDIT_COMPLETE`

This is a read-only audit. No cleanup, staging, deletion, commit, merge, tag,
push, `.gitignore` edit, source edit, configuration edit, or test edit was
performed.

## 1. Repository State

- branch: `feature/jetson-tensorrt-int8`
- HEAD: `d130217bf8ab72c6e4e3907cdaa80842d8dcc5da`
- upstream: `origin/feature/jetson-tensorrt-int8`
- branch relation: up to date before this report was created
- recent commits:
  - `d130217 docs(stage-q): consolidate Q8 closeout`
  - `8d7e3a8 stage-q: add Q5 accuracy and hash authority`
  - `c24477c stage-q: integrate INT8 runtime manifest and result metadata`
  - `8e0c105 stage-q: complete formal INT8 build and audit`
  - `cfae3fe stage-q: implement INT8 builder smoke`
- tracked modified files: none
- staged files: none
- Git-visible untracked files at audit start: 46
- ignored-but-present Stage Q evidence files: 18
- audit report created by this task: one additional TRACK candidate

The final audit universe is therefore 65 untracked files: 64 evidence/build
files plus this report. The 18 ignored files were explicitly enumerated rather
than omitted from the audit because ordinary `git status --short` hides them.

## 2. File Classification

Classification meanings:

- `TRACK`: candidate for a future user-authorized `git add` and commit.
- `LOCAL_ONLY`: retain locally as raw/reproducibility evidence; do not commit.
- `DELETE_CANDIDATE`: possible redundant or failed-attempt output; only mark,
  never remove during this audit.

### Tracked modified files

None.

### Untracked TRACK candidates

| Path | Status | Classification | Recommended Action |
|---|---|---|---|
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_fp16_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_fp16_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_int8_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_int8_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_fp16_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_fp16_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_int8_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_int8_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_fp16_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_fp16_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_hashes.json` | untracked | TRACK | future `git add` + commit |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_sidecar.json` | untracked | TRACK | future `git add` + commit |
| `results/build/tensorrt/k2_fp32_engine_v1/manifest.json` | ignored/untracked | TRACK | future review, then `git add -f` only if approved |
| `results/build/tensorrt/q3_int8_engine_v1/formal_calibration_manifest.json` | ignored/untracked | TRACK | future review, then `git add -f` only if approved |
| `results/build/tensorrt/q3_int8_engine_v1/layer_precision_audit_summary.json` | ignored/untracked | TRACK | future review, then `git add -f` only if approved |
| `results/build/tensorrt/q3_int8_engine_v1/raw_engine_layer_info.json` | ignored/untracked | TRACK | future review, then `git add -f` only if approved |
| `results/build/tensorrt/strict_fp32_notf32_investigation_v1/manifest.json` | ignored/untracked | TRACK | future review, then `git add -f` only if approved |
| `docs/personal/STAGE_Q_GIT_HYGIENE_REPORT.md` | untracked | TRACK | future `git add` + commit |

### Untracked LOCAL_ONLY files

| Path | Status | Classification | Recommended Action |
|---|---|---|---|
| `results/validation/stage_q/q5_accuracy_v1/fp16_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q5_accuracy_v1/int8_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_result.json` | untracked | LOCAL_ONLY full result dump | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_fp16_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair1_int8_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_fp16_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair2_int8_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_fp16_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/pair3_int8_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/int8_confirmation_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_fp16_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair1_int8_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_fp16_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair2_int8_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_fp16_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/pair3_int8_trace.jsonl` | ignored/untracked | LOCAL_ONLY raw trace | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/environment_after_pair1_fp16.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/environment_after_pair2_int8_pre_fp16.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/environment_after_pair3_fp16_pre_int8.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/environment_post.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/environment_pre_pair1.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/environment_pre_pair2.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/validation/stage_q/q6_serial_performance_v1/environment_pre_pair3.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/validation/stage_q/q7_confirmation_v1/attempt_001/tegrastats.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_fp16_formal.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_int8.txt` | untracked | LOCAL_ONLY telemetry/environment | retain locally |

### Untracked DELETE_CANDIDATE files

| Path | Status | Classification | Recommended Action |
|---|---|---|---|
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1.txt` | untracked | DELETE_CANDIDATE redundant failed-attempt telemetry | optional cleanup only after separate authorization |
| `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/environment_pre_pair1_fp16.txt` | untracked | DELETE_CANDIDATE superseded failed-attempt telemetry | optional cleanup only after separate authorization |

## 3. Git Tracking Check

`git ls-files` found no tracked `.engine`, `.onnx`, `.pt`, `.pth`, `.plan`,
`.bin`, or `calibration.cache` artifact.

Tracking risk: `TRACKING_RISK` applies to the five ignored build manifest/audit
candidates listed above if they are later force-added without review. The
current index does not track them.

## 4. Large File Check

Command: `find . -type f -size +50M`

Result: zero files over 50 MiB in the workspace at audit time. No deletion or
relocation was performed.

## 5. Evidence Directory Audit

- `results/validation/stage_q/`: curated split manifests, Q1/Q5 summaries and
  Q6 summaries are tracked candidates; full Q5/Q6 Result JSON, traces,
  sidecars, hashes, and environment captures are classified above.
- `results/benchmark/stage_q/`: Q7 summary is already tracked; Q7 raw traces,
  sidecars, hashes, and environment captures are classified above.
- `results/build/tensorrt/`: formal manifests and audit summaries are useful
  tracking candidates, but the parent build tree is currently ignored and the
  five listed candidates require explicit future review.

## 6. `.gitignore` Analysis

Current rules correctly cover build directories, model binaries, `*.jsonl`,
`*.log`, and several generated artifact classes. However, generic generated
JSON result dumps, sidecars/hashes, telemetry `.txt`, and Stage Q result
directories are not uniformly ignored; this is why the audit finds both
visible and ignored/unignored raw evidence.

Recommendation: `ADD_IGNORE_RULE` for raw Stage Q trace/result/telemetry
patterns, with explicit negation rules for approved small summaries and
manifests. Do not apply that recommendation in this audit; `.gitignore` was
not modified.

## 7. Classification Summary

Snapshot counts before adding this report:

- TRACK: `31`
- LOCAL_ONLY: `31`
- DELETE_CANDIDATE: `2`
- tracked modified: `0`
- staged: `0`

After this report is created, the report itself is an additional TRACK
candidate. No file was staged or committed.

## 8. Recommended Actions

- Future user-authorized `git add` + commit: small hashes, sidecars, approved
  manifests/audits, and this report.
- Remain local-only: full Result JSON, raw JSONL traces, telemetry, environment
  captures, and other generated runtime outputs.
- Optional cleanup candidates: the two redundant/failed-attempt environment
  files, but only under a later explicit cleanup authorization.
- No action was executed by this audit.

## Scope Check

This audit performed no source modification, deletion, move, reset, checkout,
`.gitignore` change, `git add`, commit, push, merge, or tag. `src/`, `include/`,
`CMakeLists.txt`, `configs/`, and `tests/` were not modified.

## Authorization

Cleanup: `NOT AUTHORIZED`

Commit: `NOT AUTHORIZED`

Merge: `NOT AUTHORIZED`

Tag: `NOT AUTHORIZED`
