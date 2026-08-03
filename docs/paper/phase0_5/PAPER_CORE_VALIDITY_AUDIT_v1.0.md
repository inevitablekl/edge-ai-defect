# Paper Core Validity Audit v1.0

## 1. Audit Verdict

`REMEDIATION_REQUIRED`

The audit found two evidence-validity problems that affect the current Stage R
performance claim boundary: V4 is buffer rotation with serialized execution,
not the authorized cross-frame overlap implementation; and Attempt 2 enables
V0 internal timing instrumentation while V2/V3/V4 disable it. The dataset
issue is bounded and already has a content-deduplicated validation split. The
V2 Gate D failure has a supported preprocessing attribution, but the evidence
does not justify expanding that attribution to unrelated preprocessing or
postprocessing semantics.

## 2. Repository State

- Audit scope was read-only source, config, evidence, manifest, report, and
  static call-graph inspection. No benchmark, training, formal accuracy run,
  Engine generation, or implementation change was performed.
- Current repository state at audit time: clean worktree, `HEAD`
  `4b13f87` (`paper-phase0-complete-v1.0`). Historical Stage R evidence cites
  its own production/evidence commits; those identities are retained as
  provenance and are not silently substituted for the current source fact.
- Main authorities consulted include:
  `stage_r/double_buffer_runner.cpp`,
  `src/tensorrt_engine.cpp`,
  `tools/benchmark/stage_r_r3_ablation_runner.cpp`, the V0/V2/V3/V4 configs,
  `results/benchmark/stage_r/r3_v0_v2_v3_v4_ablation_v2/`, Stage R R2/R3/R5
  reports, split-v2 evidence, training evidence, and existing V2 correctness
  evidence.

## 3. V4 Implementation Audit

### Verdict

`PARTIAL_BUFFER_ROTATION_NOT_TRUE_OVERLAP`

### Findings

| Required property | Static evidence | Finding |
|---|---|---|
| Two independent host/device slots | `DoubleBufferRunner` owns two `PinnedRawStaging` objects, two `CudaPreprocessor` objects, and two input pointers. Slot 1 is separately allocated with `cudaMalloc`; each preprocessor owns its own device raw buffer. | Confirmed: two resource sets exist. |
| Ownership/lifecycle | Slots are allocated before the frame loop, selected by `frame_index % 2`, and freed by RAII/destructors. Reuse is counted after the first two frames. | Lifecycle is bounded and deterministic, but no asynchronous ownership state/event is present. |
| H2D/preprocess/enqueue/D2H cross-frame overlap | `CudaPreprocessor::preprocess()` queues H2D and the kernel on the engine stream; `copy_output_to_host()` queues D2H and immediately calls `cudaStreamSynchronize()`. The next call to `source_.next()` occurs only after postprocess and `sink_.write_frame()` for the previous frame. | Not implemented. The next frame does not start before prior frame completion. |
| Independent streams/events | Both V4 preprocessors receive `engine_.cuda_stream_handle()`. The engine exposes one stream; V4 creates no stream or event. | Not implemented. |
| Inference overlap | `run_device_input_slot()` calls `enqueueV3()` on the same stream and then `cudaStreamSynchronize()` before host output construction and D2H; it synchronizes D2H again before returning. | Not implemented. |
| Global/per-frame synchronization | V4 records two synchronization counts per processed frame: preprocessing D2H synchronization and TensorRT output synchronization. The R2 manifest records `synchronization_count: 360` for 180 frames. | Explicit serialization is part of the path. |
| Result collection | Postprocess, frame construction, `sink_.write_frame()`, and digest accumulation all occur before the loop advances to the next frame. | Result collection prevents any possible overlap in this implementation. |

The implementation therefore satisfies “two fixed buffers/resources” and
“fixed alternation”, but not the predetermined limited overlap contract of
`preprocess(N+1)` with `inference(N)`. The R2 V4 manifest itself describes the
path as `limited ownership alternation` and `single CUDA stream serialized by
explicit slot reuse synchronization`, which is consistent with the source
finding and is not evidence of overlap.

### OOM causality

The OOM event is established as an event: `failure.json` records `set_01_v4`
with return code `-9`, and the Attempt 2 reports record a kernel OOM kill with
approximately 5.1 GiB anonymous RSS on a 7.4 GiB system. The event occurred in
the V4 run and was rerun once under the frozen anomaly rule.

The implementation also contains V4-specific memory pressure: two large
pinned/device staging paths, a second device input slot, and a retained
`digest_bytes` reservation for 180 tensors (approximately 884,736,000 bytes
from the source constants). These facts make V4-specific memory pressure a
credible causal contributor, but the available evidence does not provide an
allocator or memory timeline that isolates one allocation as the root cause.
The defensible statement is therefore “V4 incurred a recorded OOM event”; the
stronger statement “double buffering itself caused the OOM” is not proven.

## 4. Timing Instrumentation Audit

### Verdict

`TIMING_MISMATCH_REQUIRES_RERUN`

### Effective values

| Variant | Config file | Config `timing.enabled` | Attempt 2 harness effective `timing_enabled` | Result |
|---|---|---:|---:|---|
| V0 | `configs/stage_r/runtime_v6_v0_off.yaml` | `true` | `true` | Internal frame timings emitted |
| V2 | `configs/stage_r/runtime_v6_v2_pageable.yaml` | `false` | `false` | Internal frame timings omitted |
| V3 | `configs/stage_r/runtime_v6_v3_pinned.yaml` | `false` | `false` | Internal frame timings omitted |
| V4 | `configs/stage_r/runtime_v6_v4_double_buffer.yaml` | `false` | `false` | Internal frame timings omitted |

The effective values are not inferred from the V0 filename: the Attempt 2
harness explicitly sets `const bool timing_enabled = variant == V0` and passes
that value into `RunMetadata`.

### Extra operations when timing is enabled

For V0, `SerialRunner` additionally computes five elapsed durations per frame,
validates them, stores `FrameTimings`, and causes the Result JSON serializer to
emit the timing object. The runner already makes ordinary stage clock calls for
its control/trace boundaries, but the timing-enabled branch adds duration
calculation, validation, optional-object assignment, and timing-field output.

No CUDA event instrumentation is active in Attempt 2. The benchmark configs use
profiling mode `off`, and the harness does not call
`TensorRtEngine::set_diagnostic_profiling(true)`. Consequently, the
diagnostic CUDA events and their `cudaEventElapsedTime` calls are not part of
this Attempt 2 measurement. The engine’s normal CUDA stream synchronizations
are execution behavior, not timing-toggle instrumentation.

The common benchmark `TimingSource` does use host `steady_clock` calls for all
variants. It records the source-pull start and reads elapsed time immediately
before `FanoutSink::write_frame()`. Thus the external per-frame latency covers
source pull through preprocessing, inference, postprocess, and the V0 timing
object construction that precedes the sink call. It excludes JSON/hash sink
serialization itself. The full `run_wall_ms`/throughput path does include result
serialization; V0 emits larger per-frame JSON because its timing fields are
present.

There is no active frame-trace observer or trace append in the Attempt 2
harness. The timing mismatch is therefore not an event/trace mismatch; it is a
V0-only internal timing computation and result-field generation mismatch inside
the measured process.

Because the V0-only work occurs before the common external latency timestamp is
consumed, it can affect throughput and the external latency mean, P95, P99, and
maximum. The existing evidence does not isolate its magnitude. The Attempt 2
claim `COMPLETE_UNIFIED_HARNESS_COMPARABLE` is therefore too broad for a clean
four-way timing claim. V2/V3/V4 share the same disabled internal-timing policy,
but the published four-way table, especially V0-versus-V2/V3/V4 deltas, needs a
matched timing rerun before it is used as final horizontal performance
evidence.

## 5. Dataset Split and Model-Selection Audit

### Duplicate and split identity

The historical `split_v1_historical` contains one content duplicate:

- train entry 935: `IMAGES/patches_101.jpg`;
- val entry 187: `IMAGES/patches_105.jpg`;
- image SHA256 for both: `4d2de82731b86cdbc7a66f2a9bfb01074bb4cb65e47bccf06b66470d53857071`;
- annotations are different files/SHA values, but annotation identity does not
  remove the image-content overlap.

The test split is completely unchanged at the entry level: the historical and
`split_v2_deduplicated` test manifests have the same 180 entries, paths, image
SHA values, and annotation identities. Their manifest SHA values differ only
because the v2 manifest is a versioned artifact with remediation metadata. The
duplicate group has no test member.

### Model-selection authority

The original training/validation authority was the historical `val` split in
`data/yolo/neu_det/dataset.yaml`; the recorded validation command uses
`model.val(..., split='val', imgsz=640, batch=16, device=0)`. Test was used only
after model selection and was not a selection/tuning authority.

The documented selection rule is executable from the archived evidence:

1. priority 1: highest validation mAP50-95;
2. priority 2: recall as the engineering tiebreak for equivalent candidates;
3. retain deterministic/repeatability and observed-variation context without
   claiming statistical significance.

The selected seed=7 checkpoint has recorded validation mAP50-95 `0.450849`
and recall `0.744685`. The seed=42 deterministic result is `0.449830`, and the
three-seed observed mAP50-95 standard deviation is about `0.00589`. The
duplicate can make a validation score for any checkpoint slightly optimistic
for that one image and can affect ranking when candidates are close; the
current evidence cannot determine the direction or size of the ranking change.

### Split-v2 and checkpoint sensitivity

`split_v2_deduplicated` already exists and removes only the val copy, producing
1260 train, 359 val, and 180 test images with zero path and content-SHA overlap
across all split pairs. No retraining has been performed.

The training evidence records nine unique archived `best.pt` SHA256 values,
their effective arguments, validation metrics, and the original selection
metadata. The checkpoint archive is external/local-only rather than a tracked
repository artifact, so re-evaluation is possible subject to access to that
archive; the repository evidence is sufficient to identify all nine inputs and
to re-run the original selection rule after evaluation. A full retraining is not
required merely to answer whether the frozen choice is sensitive to the
duplicate.

The minimum valid next check is therefore a checkpoint-only evaluation of all
nine `best.pt` files on the existing v2 validation manifest, followed by the
same mAP50-95/recall selection rule. Conditions for escalation are:

- if seed=7 remains selected and the result is not materially changed, retain
  the frozen model and record the split limitation/remediation sensitivity;
- if another existing checkpoint becomes selected, re-freeze the model choice
  and rerun every model-dependent downstream artifact from ONNX onward;
- retraining is needed only if a clean split-trained model is required for the
  claim, or if checkpoint-only sensitivity cannot provide a defensible choice;
- if test membership changes, downstream test/accuracy evidence must be rerun;
  that condition is not present here.

## 6. V2 Correctness Audit

### Gate status and confirmed finding

The existing V2 evidence shows:

- tensor/geometry Gate B: PASS, with finite output and bounded MAE/P99/max
  error;
- V0 regression Gate C: PASS;
- task-level Gate D: FAIL after the bounded 11-bit fixed-point resize
  remediation;
- remediated mAP50 absolute drop `0.00537575`, above the frozen `0.005` limit
  by `0.00037575`.

The strongest supported and already recorded causal finding is a CUDA resize
interpolation numerical-contract difference relative to OpenCV CPU
`INTER_LINEAR`. The source confirms separate implementations: CPU uses
`cv::resize`, while CUDA uses a custom half-pixel bilinear kernel with explicit
coefficient quantization, clamping, and integer accumulation. The first bounded
11-bit coefficient remediation improved the task delta but did not pass Gate D.

### Differential audit

| Candidate semantic | Audit status | Evidence-based disposition |
|---|---|---|
| Resize interpolation | **已证实差异** | Confirmed as the supported source of the bounded tensor/task mismatch; the 11-bit remediation changed the tensor result and improved but did not close Gate D. |
| Letterbox rounding | 尚无差异证据 | V0 and V2 use the same CPU `compute_letterbox_geometry`; no separate CUDA rounding is recomputed. |
| Padding | 尚无差异证据 | Geometry is shared; both paths use pad metadata and normalized value 114. |
| BGR/RGB | 尚无差异证据 | Both paths consume BGR and write RGB channel order. |
| Normalization | 尚无差异证据 | Both paths use float32 values divided by 255. |
| HWC/CHW | 尚无差异证据 | Both paths produce float32 RGB NCHW `[1,3,640,640]`. |
| FP32/FP16 intermediate type | 尚无差异证据 | The preprocessing contract and CUDA output are FP32; no V2 FP16 preprocessing path is evidenced. |
| Coordinate transform | 尚无差异证据 | The same geometry metadata reaches the existing postprocessor transform. |
| CUDA edge handling | 有证据支持的候选差异，但未独立隔离 | The custom kernel clamps edge coordinates; this is part of the resize implementation and is not separately quantified from the overall interpolation mismatch. |
| Postprocess contract | 尚无差异证据 | Existing postprocess is shared; V2 frame/integration checks pass. |
| Calibration/input distribution mismatch | 尚无差异证据 | V0 and V2 use the same frozen INT8 Engine; the evidence points to preprocessing output numerics, not a changed calibration source. |

The following remain unsupported guesses: a standalone letterbox-padding bug,
BGR/RGB swap, normalization error, layout error, FP16 preprocessing error,
coordinate-transform error, postprocess error, or calibration mismatch.

A bounded correctness-aligned remediation is technically suitable only as a
future, explicitly authorized task: replace the custom resize with a verified
OpenCV-compatible implementation, then run the existing bounded tensor and
task gates. It is not necessary to relabel the current V2 result, and it must
not be described as already completed. Current Stage R closeout decisions
explicitly prohibit further resize remediation without a new authorization.

## 7. Claim Impact

### Remain valid

- V0 remains the correctness-first deployment baseline and the Stage Q
  correctness authority.
- V2 Gate D is FAIL under the frozen threshold; V2 is not a
  correctness-equivalent replacement.
- The V2/V3/V4 same-family detection identity recorded in Attempt 2 remains a
  valid observed result for the tested code/evidence identity.
- The train/val content duplicate and the fact that test membership is
  unchanged remain valid historical/data-integrity findings.
- A V4 OOM-kill event and severe observed latency tail occurred; these are
  retained anomaly observations, not an identified root cause.

### Require numerical refresh

- The four-way Attempt 2 FPS and external latency table, including mean, P95,
  P99, and maximum comparisons involving V0, requires a matched timing rerun.
- Any derived V0-versus-V2/V3/V4 performance percentage used as final paper
  evidence requires refresh from that rerun.
- The checkpoint selection metrics and ranking require refresh on the existing
  deduplicated validation split before claiming the frozen choice is robust to
  split remediation.

### Must be withdrawn

- “V4 implemented the planned limited double-buffer overlap” or any claim of
  demonstrated cross-frame H2D/preprocess/inference overlap.
- “Attempt 2 is fully timing-identical across all four variants” as a literal
  instrumentation claim.
- “Double buffering caused the OOM” as a proven root-cause claim.

### May remain as limitation only

- The historical model-selection result may remain as a historical result with
  the one-image train/val content-overlap limitation, provided the checkpoint
  sensitivity check is reported or the limitation is explicit.
- The V4 result may remain as a negative serialized two-slot-alternation
  ablation with recorded tail/OOM observations, not as an overlap-performance
  result.
- The V2 resize numerical mismatch may remain as a bounded trade-off
  limitation, not as a general claim that all CUDA preprocessing semantics
  differ.

## 8. Minimal Remediation Plan

### Must

- Perform one timing-aligned Attempt 2 rerun with the same external latency
  boundary and the same timing-enabled/disabled policy for every variant, or
  disable internal timing for all four variants. Refresh only the affected
  performance summaries and derived comparisons.
- Correct the Stage R/V4 claim boundary in the paper evidence layer: describe
  the current implementation as serialized fixed two-slot rotation, and retain
  OOM as an event without assigning an unproven root cause.
- Re-evaluate the nine archived checkpoints on
  `split_v2_deduplicated` validation and apply the original selection rule.

### Conditional

- If the checkpoint winner changes, re-freeze that existing checkpoint and
  rerun model-dependent ONNX/Engine/accuracy/performance evidence.
- If a strict clean-split-trained model claim is required, authorize retraining
  on the deduplicated split; this is not implied by the current audit alone.
- If a correctness-equivalent V2 replacement is required, authorize one
  bounded OpenCV-compatible resize remediation and repeat the existing tensor
  and task gates. Do not change Gate D thresholds.

### Not Required

- Full-chain retraining solely because of the one train/val duplicate when
  checkpoint sensitivity confirms the same frozen choice.
- Re-running test accuracy solely for the split issue while test entries remain
  identical.
- Re-running V2/V3/V4 correctness merely to rediscover the already supported
  resize interpolation finding.
- Implementing TensorRT, Pipeline, UI, ROS2, INT8, GPU NMS, or unrelated
  production changes as part of this audit.

## 9. Files Created

- `docs/paper/phase0_5/PAPER_CORE_VALIDITY_AUDIT_v1.0.md`

No other repository file was modified.

## 10. Recommended Next Actor

Paper Project Manager
