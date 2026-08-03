# Paper Timing-Aligned Rerun Plan v1.0

## 1. Plan Status

- Plan status: `READY_FOR_PROJECT_MANAGER_REVIEW`
- Scope: freeze the Phase 0.5D-I timing-aligned formal rerun protocol for V0, V2R, and V3R.
- This document is a protocol freeze only. It authorizes no implementation, build, benchmark, Gate D rerun, paper正文 update, tag, push, or merge.
- Required authorization: `PHASE_0_5D_I_NOT_AUTHORIZED_PENDING_PROJECT_MANAGER_REVIEW`
- Next actor: Paper Project Manager.

The preflight baseline is clean on `main` at `de7e24bda073275293bd6a62c3a858fc72a628a5`, which contains the V2R remediation freeze commit `4815a9d129fca1bce6d69926792c05a52f3b3530`. The historical Stage R Attempt 2 evidence remains immutable and is not replaced by this plan.

## 2. Purpose and Validity Problem

The formal rerun exists to remove the known timing asymmetry in the historical Stage R Attempt 2 comparison. The old V0 path effectively enabled internal per-frame timing while V2/V3/V4 did not. Consequently, the historical `+129.87% FPS` and `-56.68% mean latency` claims, the old V0/V2/V3/V4 table, and the old V0/V2 Pareto numbers are suspended pending a matched rerun.

The rerun will compare one correctness baseline and two semantically matched CUDA preprocessing variants under one workload, one output schema, one sink policy, one external timing boundary, and one predeclared interleaved schedule. It will not combine new metrics with Stage P, Stage Q, or historical Attempt 2 metrics.

## 3. Frozen Formal Variant Set

Only these variants are in scope:

| Variant | Raw staging | Preprocessing | Inference input | Role |
|---|---|---|---|---|
| V0 | Host source / host tensor path | CPU OpenCV path | TensorRT INT8 device input contract | correctness-first baseline |
| V2R | pageable host raw staging | OpenCV 4.5.4-aligned fixed-contract CUDA preprocessing | TensorRT INT8 device input | accepted pageable remediation |
| V3R | pinned host raw staging | the same OpenCV 4.5.4-aligned fixed-contract CUDA preprocessing as V2R | TensorRT INT8 device input | accepted pinned companion |

V2R is the accepted Gate D correctness path recorded in `PAPER_V2R_GATE_D_DISPOSITION_v1.0.md`; V3R is its accepted pinned-memory companion with the same preprocessing semantics. Historical V2, V3, and V4, V1, V5, zero-copy, Pipeline, new double-buffer, multi-stream, and multi-context variants are excluded. Their evidence remains historical evidence.

## 4. Timing Boundary

### 4.1 Primary metric: external per-frame service latency

For every variant, the primary clock starts immediately before source pull/frame acquisition and ends after preprocessing, inference, postprocessing, and frame-result construction, immediately before sink serialization or write. It includes:

- source pull and image decode;
- raw staging, including pageable or pinned host staging;
- host-to-device transfer;
- CUDA preprocessing;
- TensorRT enqueue and synchronization;
- device-to-host transfer where required;
- postprocessing, NMS, and detection/frame-object construction.

It excludes JSON serialization, file I/O, digest-file writing/finalization, and run-summary persistence. The boundary must be implemented once in the dedicated 0.5D harness and must be identical for V0, V2R, and V3R.

### 4.2 Secondary metric: process-wall throughput

Throughput is `measured_frames / measured_process_wall_time`. The wall interval covers the same measured workload and the same sink, serialization, digest, and output policy, with one variant per process. The process-wall interval and its start/end markers must be recorded explicitly; a wrapper-only subprocess duration is not sufficient as the primary authority.

### 4.3 Timing exclusions and implementation rule

All three configurations must set `timing.enabled: false`, and profiling mode must be `off`. No internal timing objects, TensorRT diagnostic timing, CUDA-event timing, trace observer, or variant-specific per-frame timing fields may be created or serialized. The resulting JSON must have the same schema and field set for all variants, with no per-frame `timing_ms` field. Effective `false` must be asserted from the parsed configuration, runner metadata, serializer/result inspection, and run manifest—not inferred from YAML text alone.

## 5. Common Runtime and Workload Contract

The following values are frozen and must be identical unless a later protocol amendment is approved:

| Item | Frozen value |
|---|---|
| Dataset | `NEU-DET` test split represented by `test_manifest_v2.json` |
| Input manifest | `results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json` |
| Manifest SHA256 | `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194` |
| Frozen image set | 180 images, same order and six complete 180-image measured cycles |
| Warmup | 60 frames, through the same source/inference/postprocess/sink path, excluded from metrics |
| Measured frames | 1080 per run |
| Runs | 5 independent runs per variant, 15 independent processes total |
| Execution topology | one variant per process, one inline sequential path; no PipelineRunner or cross-variant process |
| Queue/drop contract | no frame drop; processed count must equal requested count; `drop_count=0` |
| Batch | 1 |
| Input size | 640, using the frozen model contract |
| Confidence / IoU | `0.25` / `0.45` |
| NMS contract | `max_nms=30000`, `max_det=300`, `max_wh=7680`, class-agnostic `false` |
| Engine | existing frozen TensorRT INT8 engine; no rebuild or recalibration |
| Engine manifest SHA256 | `67f6ce3337d9c28c4aa2b32ba62554eaaa028f096c448041c063ec695f3b981c` |
| Model contract SHA256 | `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190` |
| OpenCV contract | OpenCV 4.5.4-aligned preprocessing semantics for V2R/V3R |
| Output | identical Result schema, fields, serialization, detection hash, digest, and output policy |

Warmup must finish with queues empty and all required synchronization complete. Counters and measured-window markers must be reset before measured frames begin. End-of-stream, final synchronization, and sink completion must be checked before a run is accepted.

## 6. Platform and Environment Freeze

The execution record must capture, before and during each run where applicable:

- Jetson board identity, architecture, JetPack/L4T, CUDA, TensorRT, and OpenCV versions;
- model, engine, engine-manifest, model-contract, test-manifest, binary, config, and harness hashes;
- power mode, `MAXN_SUPER` state, clock state, CPU affinity, OpenCV thread count, swap/zram state;
- thermal/cooling state, temperatures, fan state, background load, and process start/end times.

The previous Attempt 2 environment observed Jetson Orin Nano Super, aarch64, CUDA 12.6, `MAXN_SUPER` mode 2, CPU affinity 0–5, and OpenCV thread count 1; these are reference observations, not permission to assume an unverified future environment. JetPack 6.2.2/L4T 36.5 remains a planned target pending platform acceptance. Missing or inconsistent environment identity is a validity failure, not a value to infer. No dependency upgrade, engine rebuild, calibration change, model/input change, batch change, threshold change, or postprocess change is allowed.

## 7. Timing-Aligned Configuration Identity

The future rerun must use three new independent configuration files:

- `configs/stage_r/runtime_v6_v0_timing_aligned.yaml`
- `configs/stage_r/runtime_v6_v2r_timing_aligned.yaml`
- `configs/stage_r/runtime_v6_v3r_timing_aligned.yaml`

Their public identity diff must be recorded at execution time:

| Field | V0 / V2R / V3R requirement |
|---|---|
| schema, backend, engine, manifest, model contract | identical; TensorRT INT8 and frozen external identities |
| source, manifest, input size, batch, thresholds, NMS | identical |
| runtime topology, sink, serialization, digest, output policy | identical |
| warmup, measured count, repetitions, ordering policy | identical |
| `timing.enabled` | `false` in all three |
| `profiling.mode` | `off` in all three |
| OpenCV threads, affinity, power/clock policy | identical execution contract |
| `data_path_variant` and implementation path | only intentional variant difference: V0, V2R, or V3R |

The configuration files must not encode a hidden timing or profiling exception. Their hashes, effective parsed values, binary identity, and external artifact identities must be written into every run manifest.

## 8. Harness Assessment and Future Harness Requirements

The current Attempt 2 harness is **not safe to reuse unchanged**. It hardcodes effective timing on V0, dispatches unrecognized V2R/V3R values to the historical V4 path, and does not expose all required effective timing, result-field, remediation-identity, and process-wall assertions. The old four-variant schedule and output directory must remain untouched.

The future 0.5D harness may reuse verified source/sink/result/hash components only after explicit checks. It must:

1. accept only V0, V2R, and V3R;
2. select the existing production V2R/V3R dispatches and accepted semantic identity;
3. remove variant-based timing behavior and assert `timing_enabled=false` everywhere;
4. use one shared external timing boundary and one shared serialization/digest path;
5. record effective configuration, result schema/field-set identity, binary/engine/config/manifest hashes, remediation identity, and process-wall markers;
6. preserve every failed attempt and never overwrite historical or prior-run evidence;
7. write only to the dedicated 0.5D result directory.

No generic benchmark framework, asynchronous runner, Pipeline implementation, V4 path, power benchmark, or production optimization is authorized by this plan.

## 9. Formal Interleaved Run Schedule

The workload order is fixed before execution and must not be changed in response to interim results. Each schedule row is one set of three independent processes; each variant appears once per set and occupies balanced positions across the five sets:

| Set | Process 1 | Process 2 | Process 3 |
|---|---|---|---|
| 1 | V0 | V2R | V3R |
| 2 | V3R | V2R | V0 |
| 3 | V2R | V0 | V3R |
| 4 | V0 | V3R | V2R |
| 5 | V2R | V3R | V0 |

Each process performs 60 warmup frames followed by exactly 1080 measured frames from the same 180-image cycle. There is no random order, skip, replacement, multiple-variant process, or result-dependent reordering. A process failure does not silently change the schedule; it is retained as a failed attempt and may be retried only under the explicit rule in Section 12.

## 10. Per-Run Evidence and Result Schema

The dedicated result root is:

`results/benchmark/stage_r/phase0_5d_v0_v2r_v3r_timing_aligned_v1/`

At minimum it must contain:

```text
protocol.json
environment.json
execution_identity.json
run_schedule.json
run_manifest.json
runs/
aggregate_metrics.json
aggregate_metrics.csv
pairwise_comparison.json
pairwise_comparison.csv
validity_summary.json
artifact_sha256.txt
PAPER_PHASE0_5D_TIMING_ALIGNED_REPORT.md
```

Each run must preserve raw result output, run manifest, metrics, logs, process-wall markers, and hashes. The manifest must include run identity, variant, schedule position, config/binary/engine/model/test-manifest hashes, effective timing/profiling values, schema and field-set identity, warmup/measured counts, processed/drop counts, EOS and synchronization state, detection SHA, tensor/output digest, status, and failure classification. The future compact paper evidence root is `docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/`; it is not created by this planning phase.

The existing `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/` directory must not be overwritten, renamed, or used as the new result root.

## 11. Correctness and Identity Protection

Every run must prove:

- exactly 60 warmup and 1080 measured frames;
- processed count equals requested count, zero drops, preserved manifest order, and successful EOS;
- identical result schema and field set with no `timing_ms` field;
- effective timing disabled in configuration, runner metadata, result inspection, and manifest;
- accepted V0 correctness identity;
- V2R Gate D accepted identity and V3R pinned companion identity;
- matching engine, model, test-manifest, binary, harness, and configuration identities;
- finite metrics and complete latency samples;
- detection SHA compatibility with the accepted variant identity.

If a V2R or V3R detection SHA differs from its accepted identity, the run is `RUN_INVALID` and is excluded from aggregate metrics. It must not be repaired by editing output or by silently substituting another run.

## 12. Validity, Failure, and Retry Rules

Run classes are:

- `RUN_VALID`: return code 0, complete counts, zero drops, EOS/synchronization pass, finite and complete metrics, identity hashes pass, and schema/field-set checks pass.
- `RUN_INVALID`: a protocol, identity, count, ordering, schema, timing-disabled, detection, or data-integrity violation.
- `ENVIRONMENTAL_FAILURE`: an explicitly documented non-metric environment failure, such as an external process kill or unavailable platform condition.
- `IMPLEMENTATION_FAILURE`: harness, dispatch, serialization, synchronization, or other implementation defect.

Retry is allowed only for a documented non-metric environmental failure or incomplete result, using the exact same predeclared identity and schedule position. The first failure remains preserved. Poor FPS, high latency, lack of V3R gain, OOM, thermal behavior, or any other performance outcome is never a reason to retry or discard a run. OOM/kill records remain in the manifest and validity summary.

## 13. Metrics and Aggregation

For each valid run, report measured-frame count, drop count, detection SHA, process-wall FPS, primary latency mean/P50/P95/P99/max, and CPU equivalent-core usage when the uniform existing measurement contract is available. Per-variant aggregates over five valid runs must include per-run FPS, mean FPS, standard deviation, latency aggregates, CPU equivalent, counts, drops, and detection SHA.

The pairwise report must include:

- V2R versus V0;
- V3R versus V0;
- V3R versus V2R;
- FPS ratio and percentage delta;
- mean-latency ratio and delta;
- P95 and P99 latency deltas;
- CPU-equivalent delta when valid.

All results are descriptive. The report must not claim statistical significance, universality, guaranteed improvement, or production-grade stability. GPU utilization, power, and industrial stability claims are excluded unless a single uniform measured contract is explicitly frozen and satisfied for all three variants.

## 14. Decision and Claim Boundary

The formal decision values are:

- `TIMING_ALIGNED_RERUN_PASS`: all required variants have five valid runs and all identity/contract checks pass;
- `COMPLETE_WITH_LIMITATIONS`: the protocol completes with explicitly documented non-blocking limitations approved by the project manager;
- `RERUN_INVALID`: results cannot support comparison because a validity condition failed;
- `BLOCKED`: execution cannot begin or continue because an authorization, platform, identity, or required artifact is missing.

Until a valid rerun is accepted, suspend the historical `+129.87% FPS`, `-56.68% mean latency`, old V0/V2/V3/V4 table, and old V0/V2 Pareto numbers. A valid rerun may support V2R/V0, V3R/V0, V3R/V2R, and the V0 baseline comparison. V2R is no longer treated as research-only for correctness claims because Gate D acceptance is already recorded. V4 remains excluded.

## 15. Stop Conditions

Stop and classify the run or protocol as invalid/blocked if any of the following occurs: worktree or commit identity changes; an unauthorized source/config/engine/model change; missing or changed manifest; timing becomes effective for any variant; a per-frame timing field appears; process topology differs; processed count or order differs; any frame is dropped; EOS or synchronization fails; hashes or schema differ; the engine or calibration is rebuilt; V2R/V3R semantic identity is not the accepted identity; or the environment cannot be recorded uniformly.

No result may be promoted to paper evidence when a stop condition is present. The raw failed attempt and reason must remain available for audit.

## 16. Future Authorized File and Artifact Scope

After explicit project-manager authorization, the implementation scope may include only:

- the three timing-aligned YAML files in `configs/stage_r/`;
- a dedicated 0.5D runner/orchestrator/validator/aggregator under `tools/benchmark/`;
- minimal build-target registration in `CMakeLists.txt` only if required;
- the dedicated result root in Section 10;
- compact evidence under `docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/` only after valid execution and evidence review.

Production `src/` and `include/` behavior, historical Attempt 2 files, the old result root, paper正文, and unrelated documentation are out of scope. No implementation file is modified by this plan.

## 17. Execution Gate

Phase 0.5D-I may start only after the Paper Project Manager reviews this protocol and explicitly authorizes it. Before the first run, the authorized actor must re-check the worktree/HEAD, compile only the approved harness if needed, capture the environment and artifact identities, verify effective timing is false for all variants, and confirm the exact schedule and output root.

No experiment, build, benchmark, accuracy run, Gate D rerun, result generation, evidence copy, paper update, tag, push, or merge is authorized before that review.

## 18. Recommended Next Actor

**Paper Project Manager**

Review this plan, confirm the timing boundary and 3-variant schedule, and decide whether to grant:

`PHASE_0_5D_I_NOT_AUTHORIZED_PENDING_PROJECT_MANAGER_REVIEW`

Only an explicit subsequent authorization may transition the work to Phase 0.5D-I execution.
