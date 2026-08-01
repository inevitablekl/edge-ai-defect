# Stage Q Local Evidence Ignore Proposal

## Current Status

- branch: `feature/jetson-tensorrt-int8`
- HEAD: `1218b3bef55a1d78d96512076cd00f9d01c13808`
- untracked count at audit start: `34`
- current commit: `docs(stage-q): finalize INT8 PTQ evaluation closeout`

The untracked set consists of one Q8 report, raw Q5 result JSON, Q6 result and
sidecar/environment evidence, and Q7 sidecar/environment/telemetry evidence.
The existing `.gitignore` does not cover these Stage Q raw evidence patterns.

## Candidate Ignore Rules

| Pattern | Reason | Risk | Recommendation |
|---|---|---|---|
| `results/validation/stage_q/**/*_result.json` | Ignore large raw replay Result JSON files | Could hide a future curated result if it uses this suffix | Recommend; keep curated summaries separately named |
| `results/validation/stage_q/**/**_sidecar.json` | Ignore local runtime sidecars | Sidecar may contain useful provenance if naming is reused | Recommend only for raw invocation directories |
| `results/validation/stage_q/**/environment_*.txt` | Ignore environment snapshots from repeated runs | May hide a future required environment record | Recommend for local evidence only |
| `results/validation/stage_q/**/tegrastats.txt` | Ignore raw telemetry capture | Could hide a future curated telemetry artifact | Recommend only for raw evidence |
| `results/benchmark/stage_q/**/*_sidecar.json` | Ignore Q7 raw pipeline sidecars | Could hide a future reviewable sidecar | Recommend for attempt directories only |
| `results/benchmark/stage_q/**/environment_*.txt` | Ignore Q7 raw environment captures | May hide diagnostic provenance | Recommend for attempt directories only |

The patterns should be added only as a later, separately authorized minimal
`.gitignore` change. They must not be applied during this proposal stage.

## Must NOT Ignore

The following remain explicitly trackable:

- Stage Q reports and closeout documents under `docs/personal/`
- formal calibration and engine manifests
- precision audit summaries
- metrics summaries and classification reports
- Evidence Index and fact inventories
- reproducibility hash metadata (`*_hashes.json`)
- commit preparation and Git hygiene reports

The proposed patterns do not target these artifact classes.

## Final Recommendation

`MINIMAL_IGNORE_UPDATE_REQUIRED`

Apply only the scoped raw-evidence rules above in a later authorized change.
Do not use broad rules such as `results/`, `results/validation/`, or
`results/benchmark/`, because those would risk hiding manifests, summaries,
reports, and reviewable hash metadata.

## Scope Check

- Existing source, include, CMake, tests, configs, and tracked documentation were not modified.
- `.gitignore` was not modified.
- No `git add`, `git commit`, `git rm`, `git clean`, merge, tag, or push was executed.
- This proposal report is the only file created/updated by this task.

## Authorization

Ignore modification: `NOT AUTHORIZED`

Commit: `NOT AUTHORIZED`
