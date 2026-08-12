# Paper Phase 5.6B Material Discrepancy Report

## Verdict

`PHASE56B_MATERIAL_DISCREPANCY_NEEDS_MAIN_AI_DECISION`

Scientific promotion stopped at the mandatory Material Discrepancy gate. No
Phase 5.6 Level-B authority, evidence addendum, publication table source, or
run-level figure source was frozen.

## Repository preflight

```text
repository path: /home/orin/edge-ai/edge-ai-defect
branch: main
starting HEAD: 9002c5ece26d93b54b89bffc88fa9fb361bf2d00
git status --short: clean
git diff --stat: empty
git diff --cached --stat: empty
```

There was no existing user work in the worktree or index.

## Discrepancy D-01: formal calibration-cache semantics

### Planned claim

The Phase 5.6B calibration-provenance candidate list includes:

```text
calibration cache used
```

In ordinary TensorRT evidence terminology, this can be read as saying that an
existing calibration cache was read and used as an input to the formal Engine
build.

### Repository fact

The formal Q3 builder accepts only `--cache-mode force-miss`. It creates a new
temporary publication directory, places `calibration.cache` inside that new
directory, runs all 1260 calibration batches, requires the cache to have been
produced, and only then publishes the directory. The retained metadata records
1260 successful batches and 1260 consumed images.

The repository therefore directly supports:

```text
the formal build generated and archived a calibration cache after a forced
cache miss
```

It does not directly support:

```text
an existing calibration cache was read and reused to build the formal Engine
```

The `IInt8EntropyCalibrator2` implementation does expose both
`readCalibrationCache` and `writeCalibrationCache`, but the formal build's new
temporary cache path and complete calibration-batch accounting show that this
formal build did not take a cache-hit/reuse path.

### Exact sources

1. `src/stage_q_int8_builder.cpp`
   - lines 93 and 105-106: CLI contract requires `force-miss`;
   - lines 118-170: `IInt8EntropyCalibrator2`, batch size 1, cache read/write
     callbacks, and successful-batch accounting;
   - lines 294-303: a new temporary directory and cache path are created;
   - lines 323-332: the calibrator is attached, all batches run, and a newly
     produced non-empty cache plus full batch accounting are required;
   - lines 354-358: cache SHA and calibration counts are recorded in metadata.
   - SHA256:
     `0ad26b57ee00ebac4399dd0ce3fcb93192b4e4645cfd125f8684bdbdbe740f41`

2. `/home/orin/edge-ai-local-models/stage_q/formal/calibration_cache.meta.json`
   - `successful_calibration_batches = 1260`;
   - `images_consumed = 1260`;
   - `unreadable_images = 0`, `skipped_images = 0`, `failed_images = 0`;
   - `cache_sha256 = 05bc8175bbbf3d01d8dcf8250c94c4dd90f03cd632c3112a5a98d41c5470a0ba`.
   - SHA256:
     `587c285326864f6eeaefe1eb67505a9d893c0eb725a3519eedfea93e7fa6eb1f`

3. `docs/personal/STAGE_Q3_FORMAL_CALIBRATION_REPORT.md`
   - lines 18-28: 1260 images and 1260 successful batches;
   - lines 35-42: the produced cache and its metadata are retained.
   - SHA256:
     `c6b3d0eb8b10b3a404332c1b92bdb08c4345dd35d309db59a70d083d8efe52af`

4. `/home/orin/edge-ai-local-models/stage_q/formal/build_summary.json`
   - `image_count = 1260`;
   - `preprocessing_identity = production_Preprocessor:BGR-LetterBox640-RGB-NCHW-FP32/255`.
   - SHA256:
     `3ef05932c6ead4978c23fc0e9fef42cad0045412d207fba89cf3bb621e691a5b`

### Scientific consequence

Freezing the unqualified phrase `calibration cache used` could imply a cache
hit that bypassed full calibration, while the preserved formal provenance
records a forced cache miss followed by 1260 successful calibration batches
and cache generation. That changes how the Engine-build provenance is
interpreted and therefore falls under the Phase 5.6B calibration-provenance
material-discrepancy stop rule.

This discrepancy does not invalidate the retained Engine, the generated cache,
the 1260-image calibration, or any existing Level-A E2E authority. It blocks
only the wording and promotion of the Phase 5.6 Level-B calibration claim until
the authority owner decides its intended semantics.

### Recommended options for Main AI decision

1. Approve the precise claim: `calibration cache generated and archived after
   forced cache miss; not reused as a formal-build input`.
2. Provide separate frozen provenance proving that an existing cache was read
   and used for the authoritative formal Engine build, if such provenance
   exists.
3. Explicitly define `calibration cache used` as referring only to use of the
   TensorRT calibration-cache mechanism (including cache generation), then
   authorize publication-safe wording that cannot be mistaken for a cache hit.

This report does not select among those options.

## Other discovery checks completed before the stop

- V3R prediction authority is
  `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v3r_result.json`, SHA256
  `3e04478c181a697ccffbf63f5405ab8eecfce61a8fe2db885b2ce81045514678`,
  Result JSON schema 4, 180 images, 447 detections. Its frozen companion
  identity, workload identity, tensor digest, detection digest, zero-drop, EOS,
  and lifecycle evidence were located and checked.
- The governed correctness path was located at
  `tools/validation/stage_r_v2_task_accuracy.py`, which normalizes Result JSON
  v4 and reuses `tools/validation/evaluate_stage_k_task_metrics.py` for the
  frozen class-aware one-to-one IoU and 101-point AP semantics. A read-only
  deterministic check confirmed that the frozen V3R predictions produce the
  same complete metrics and classwise values as the frozen V0/V2R predictions.
  No derived authority output was published.
- Current and frozen source identities support V0 FP32 NCHW host input and
  4,915,200-byte H2D semantics, and V2R/V3R packed BGR `cudaMemcpy2DAsync`
  semantics. The frozen test manifest has 180 entries and the aligned Result
  JSON geometry is 200 by 200 for all 180 images, supporting a 120,000-byte
  logical/effective copy size. No payload evidence was frozen because the gate
  stopped promotion.
- The 15 archived formal processes and their 16,200 latency samples were found.
  Read-only verification reproduced the supplied Level-A ratios and changes;
  no Level-A file or provenance was changed.
- Runtime-state records support the named Jetson platform, MAXN_SUPER mode 2,
  no invoked clock-setting command, non-archived independent clock-frequency
  evidence, and non-continuous pre/post temperature observations. No runtime
  metadata authority was frozen because the gate stopped promotion.

## Scope and mutation statement

- Inference rerun: `NO`
- Formal benchmark rerun: `NO`
- New timing/telemetry/power capture: `NO`
- Level-A mutation: `NO`
- Manuscript/DOCX/PDF/figure/table mutation: `NO`
- Push/tag/merge/reset/clean: `NO`
- Commit: `NO`
