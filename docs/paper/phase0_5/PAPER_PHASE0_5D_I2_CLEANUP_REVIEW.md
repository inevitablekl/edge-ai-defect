# Phase 0.5D-I2 Cleanup Review

## 1. Git status summary

Read-only review baseline:

```text
Branch: main
HEAD: 6885dc5c8d1099c34f1cd8d10c4b30426df61daf
Tracked source/config modifications: none
```

`git status --short` reported:

```text
?? docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md
?? results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/
```

Expanded read-only inventory found:

```text
15 formal run directories
75 formal-run JSON artifacts (15 × hashes/metrics/result/run_manifest/warmup_result)
30 formal stdout/stderr logs
1 preserved pre-fix partial run with 3 JSON artifacts
4 preserved pre-fix/setup logs
```

No file was deleted, moved, rewritten, or committed during this review.

## 2. Evidence classification

|Path|Category|Reason|
|---|---|---|
|`docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`|`TRACK_TO_GIT`|Compact paper execution report containing the 15-run verdict, schedule, aggregate metrics, latency statistics, CPU measurement, identity checks, and limitations.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_runs/`|`ARCHIVE_LOCAL`|75 raw formal artifacts from all 15 valid runs. These are primary audit evidence and should not be deleted or rewritten.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_runs/*/result.json`|`ARCHIVE_LOCAL`|Per-frame detection results; large raw evidence, not suitable for routine Git tracking.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_runs/*/warmup_result.json`|`ARCHIVE_LOCAL`|Warmup lifecycle evidence for each formal process. Required to audit the 60-frame warmup contract.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_runs/*/metrics.json`|`ARCHIVE_LOCAL`|Raw per-frame latency and process-wall/CPU measurements used to derive the report.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_runs/*/hashes.json`|`ARCHIVE_LOCAL`|Per-run detection identity and digest evidence.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_runs/*/run_manifest.json`|`ARCHIVE_LOCAL`|Per-run configuration, artifact identity, timing/profiling, lifecycle, and validity metadata.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/formal_logs/`|`ARCHIVE_LOCAL`|30 formal process stdout/stderr logs; stderr is empty for successful runs, while stdout records runner PASS identity.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/runs/set_01_p01_v0/`|`ARCHIVE_LOCAL`|Preserved pre-fix blocked attempt: partial V0 result, warmup result, and `failure.json`. It documents the 180/1080 source-cycle defect and must remain available.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/logs/`|`ARCHIVE_LOCAL`|Four logs from the preserved pre-fix/setup attempts, including the stale-binary probe and measured-count failure.|
|`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/`|`ARCHIVE_LOCAL`|Container for both the valid formal evidence and historical failure evidence; do not apply broad cleanup to this root.|
|No identified path|`SAFE_REMOVE`|No build product, duplicate, or safely disposable file was identified in the requested scope.|

The raw JSON and logs are intentionally local archive material. Some log files
are ignored by repository rules, but being ignored does not make them safe to
delete: they are part of the reproducibility and failure audit trail.

## 3. Recommended action

No cleanup action should be executed automatically in this task.

Recommended next actor: **Paper Project Manager**.

The Project Manager should approve the evidence disposition in two separate
decisions:

1. Track the compact formal execution report in Git, optionally together with a
   small reviewed artifact/hash manifest.
2. Preserve the complete raw result root in a named local evidence archive or
   separately backed-up evidence storage. Raw `result.json`, `warmup_result.json`,
   `metrics.json`, `hashes.json`, `run_manifest.json`, and logs should remain
   recoverable even if they are not tracked by Git.

After that approval, either the user manually or Codex under a new explicit task
may stage the compact report and perform an approved archive operation. No
`git clean`, deletion, move, commit, or result rewrite is authorized by this
review.
