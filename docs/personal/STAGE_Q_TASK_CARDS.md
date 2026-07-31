# Stage Q Task Cards

Stage Q Execution Plan: v0.3 FINAL
Execution environment for every card: `Jetson Codex`

Decision authority: `D074–D080`. Existing Stage P decisions are preserved.

## Q0 — Planning Freeze

- **Objective:** Freeze the Stage Q v0.3 FINAL execution plan, task boundaries, facts, decisions, and authorization chain.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Exact Stage P baseline verified; Stage Q branch exists at `630822c7aeec471cc1f82b019d97bc431855045e`; unique Fact Inventory is present.
- **Authorized files/components:** `docs/personal/STAGE_Q_*.md`, `docs/personal/DECISIONS.md`, `docs/personal/TASKS.md`; read-only CMake/test inventory.
- **Required actions:** Apply the D074–D080 allocation and BCN label correction; complete Fact Inventory; record Q0 decisions; update status minimally; run allowlist and consistency checks; create the Q0 freeze commit.
- **Explicit exclusions:** No Q1 platform/asset verification, production code, CMake/schema/tests/config changes, asset recovery, Engine build, calibration, benchmark, push, merge, rebase, or tag.
- **Tests/Evidence:** Git baseline records, Fact Inventory SHA, `git diff --check`, decision-ID uniqueness, plan completeness, CMake/test inventory.
- **Gate:** `Q0_PASS`.
- **Failure states:** `Q0_BLOCKED_BASELINE_OR_TAG_MISMATCH`, `Q0_BLOCKED_DIRTY_WORKTREE`, `Q0_BLOCKED_PLAN_INCONSISTENCY`, or another explicitly recorded Q0 blocker.
- **Next authorized stage:** `Q1_NOT_AUTHORIZED_PENDING_USER_REVIEW`; Q1 only after user review of the Q0 commit.

## Q1 — Platform and Asset Preflight

- **Objective:** Verify the Jetson platform, frozen ONNX/FP16 assets, dataset manifests, split isolation, TensorRT/CUDA capability, and storage prerequisites.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Q0_PASS and explicit user review of the Q0 commit.
- **Authorized files/components:** Read-only platform tools, frozen assets, manifests, TensorRT/trtexec inspection, and Q1 Evidence paths.
- **Required actions:** Verify artifact existence and SHA256; verify train/val/test counts and path/content disjointness; inspect platform/toolchain and smoke/formal directories; record real PASS, FAIL, or NOT VERIFIED outcomes.
- **Explicit exclusions:** No builder/calibrator implementation, Engine generation, formal calibration, production changes, or asset recovery without the Q1 gate rules.
- **Tests/Evidence:** Q1 platform and asset preflight report and split-isolation evidence.
- **Gate:** `Q1_PLATFORM_AND_ASSET_PASS`.
- **Failure states:** `Q1_BLOCKED_ASSET_RECOVERY_REQUIRED`, `Q1_BLOCKED_SPLIT_ISOLATION_FAILURE`, or a recorded platform/toolchain failure.
- **Next authorized stage:** Q2 only after `Q1_PLATFORM_AND_ASSET_PASS`.

## Q2 — Builder Implementation and Smoke

- **Objective:** Implement the Stage Q-specific INT8 PTQ builder and validate it with an isolated four-image smoke calibration.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Q1_PLATFORM_AND_ASSET_PASS.
- **Authorized files/components:** Stage Q builder, calibration manifest/checker, calibrator, cache metadata validator, artifact identity and atomic-publication tooling, focused tests, and smoke Evidence.
- **Required actions:** Implement the frozen TensorRT 10.3 implicit PTQ route; reuse production preprocessing; enforce fail-fast behavior; produce only smoke artifacts from four images.
- **Explicit exclusions:** No 1260-image formal calibration, formal Engine publication, runtime integration, benchmark, Pipeline, INT8 production backend, or Q3 Evidence.
- **Tests/Evidence:** Focused builder tests, four-image smoke manifest/cache/summary, and smoke Engine load evidence.
- **Gate:** `Q2_BUILDER_AND_SMOKE_PASS`.
- **Failure states:** Builder contract failure, calibration callback failure, cache provenance failure, smoke load failure, or any accidental formal-calibration execution.
- **Next authorized stage:** Q3 only after the Q2 gate.

## Q3 — Formal Calibration, Build and Audit

- **Objective:** Perform one authoritative 1260-image calibration/build attempt, publish the formal INT8 Engine atomically, and audit layer precision.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Q2_BUILDER_AND_SMOKE_PASS and validated formal manifest.
- **Authorized files/components:** Formal builder invocation, train calibration manifest, cache metadata, formal Engine/Manifest v2, raw layer inspection, audit summary, and Q3 Evidence.
- **Required actions:** Force cache miss; consume all 1260 train images in frozen order; build, reload, inspect, audit, hash, and atomically publish the formal artifacts.
- **Explicit exclusions:** No use of val/test or evaluation corpora for calibration; no cache shortcut; no INT8 claim without detailed audit evidence; no Q4 runtime work before the gate.
- **Tests/Evidence:** Calibration counts, cache provenance, Engine load smoke, detailed layer audit, Manifest v2 consistency, and build summary.
- **Gate:** `Q3_INT8_ENGINE_BUILD_PASS` when confirmed INT8 compute is non-zero, or `Q3_EARLY_DISPOSITION_FP16_RETAINED` when it is zero.
- **Failure states:** Formal build/calibration failure, cache mismatch, atomic-publication failure, audit inconsistency, or required Evidence invalidity.
- **Next authorized stage:** Q4 after `Q3_INT8_ENGINE_BUILD_PASS`; otherwise skip Q4–Q7 and proceed to Q8 closeout.

## Q4 — Runtime Integration

- **Objective:** Add validated INT8 Engine selection and Result JSON v4 provenance while preserving FP16 and historical behavior.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Q3_INT8_ENGINE_BUILD_PASS.
- **Authorized files/components:** RuntimeConfig v5, Manifest v1/v2 loaders, Result JSON v4 mapping, TensorRtEngine/factory validation, Serial/Pipeline dispatch, and focused production tests.
- **Required actions:** Validate Manifest/Engine/ONNX/ModelContract/calibration/audit identities; expose `tensorrt_int8`; preserve FP32 Host I/O and historical schemas.
- **Explicit exclusions:** No new INT8 runner/postprocessor framework, no calibration rerun, no Pipeline redesign, no INT8 Host I/O, and no benchmark before Q5/Q6 gates.
- **Tests/Evidence:** TensorRT OFF/ON builds as authorized, schema/loader/factory tests, production smoke, and runtime provenance evidence.
- **Gate:** `Q4_INT8_RUNTIME_INTEGRATION_PASS`.
- **Failure states:** Schema mismatch, invalid Manifest provenance, Engine/ONNX hash mismatch, unsupported plugin, or historical compatibility regression.
- **Next authorized stage:** Q5 only after the Q4 gate.

## Q5 — Accuracy and Hash Authority

- **Objective:** Generate one formal FP16 and one formal INT8 Serial Result JSON v4 from the frozen test replay and classify accuracy.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Q4_INT8_RUNTIME_INTEGRATION_PASS and frozen test manifest.
- **Authorized files/components:** CorpusReplaySource, SerialRunner, TimedJsonSink, CanonicalHashSink, Result JSON v4 evaluator, test manifest, and Q5 Evidence.
- **Required actions:** Use exactly 180 test images, one cycle per backend, identical source/path/order semantics; validate six-class GT support, hashes, finite values, metrics, and frozen thresholds.
- **Explicit exclusions:** No DirectorySource substitution, no separately fabricated expected hash, no post-hoc threshold or metric changes, and no repeated accuracy invocation for convenience.
- **Tests/Evidence:** Two valid evaluator outputs, per-backend expected CYCLE SHA, 180 images, 442 GT boxes, and accuracy classification.
- **Gate:** `Q5_ACCURACY_EVIDENCE_VALID` plus `ACCEPTABLE`, `TRADEOFF`, or `UNACCEPTABLE`.
- **Failure states:** `Q5_ACCURACY_EVIDENCE_INVALID` or any source, hash, finite-value, provenance, or evaluator failure.
- **Next authorized stage:** Q6 after valid Q5 Evidence, including the UNACCEPTABLE classification.

## Q6 — Serial Performance

- **Objective:** Compare FP16 and INT8 under the frozen three-pair Serial performance protocol and classify inference/end-to-end performance.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Q3_INT8_ENGINE_BUILD_PASS, Q4_INT8_RUNTIME_INTEGRATION_PASS, and Q5_ACCURACY_EVIDENCE_VALID.
- **Authorized files/components:** Serial experiment runner, CorpusReplaySource, frozen test manifest, timing/hash sinks, telemetry probes, evaluator, and Q6 Evidence.
- **Required actions:** Run three paired processes with 100 warmup and 5000 measured frames; validate 28 complete cycles plus a 60-frame partial cycle; compute frozen ratios, percentiles, and classifications.
- **Explicit exclusions:** No changed warmup/window, source order, cycle semantics, statistics, power policy, or Engine; no Pipeline run in Q6.
- **Tests/Evidence:** Six backend runs, expected cycle hashes, telemetry, latency/throughput summaries, and paired performance classification.
- **Gate:** `Q6_SERIAL_PERFORMANCE_EVIDENCE_VALID`.
- **Failure states:** Invalid thermal throttling, cycle/hash mismatch, dropped/failed frames, incomplete provenance, or unverifiable measurement window.
- **Next authorized stage:** Q7 only when the Q6 Evidence gate passes.

## Q7 — Conditional Pipeline and Recommendation

- **Objective:** Run the frozen conditional Pipeline comparison and, only when all recommendation gates pass, the 300-second INT8 confirmation.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Valid Q5/Q6 Evidence; Pipeline entry additionally requires acceptable/tradeoff accuracy and Serial speedup at least 1.05.
- **Authorized files/components:** Existing bounded PipelineRunner, queue capacity 1, block policy, replay source, timing/hash sinks, telemetry, and Q7 Evidence.
- **Required actions:** Execute the three paired Pipeline runs when eligible; preserve the five mutually exclusive Q7 dispositions; execute normal-EOS 300-second confirmation only for the recommendation path.
- **Explicit exclusions:** No queue retuning, new topology, drop policy change, mid-cycle cancellation, SIGTERM, or claim of industrial stability certification.
- **Tests/Evidence:** Pipeline cycle hashes, runtime lifecycle evidence, throughput/regression summary, and confirmation cycle/EOS/drain/join evidence where required.
- **Gate:** One of the frozen Q7 dispositions; required-path Evidence invalid is not a successful disposition.
- **Failure states:** `Q7_PIPELINE_SKIPPED_BY_FROZEN_GATE`, `Q7_PIPELINE_VALID_NEGATIVE_RUNTIME_RESULT`, or `Q7_PIPELINE_EVIDENCE_INVALID` as applicable.
- **Next authorized stage:** Q8 after disposition completion or a valid early/negative result.

## Q8 — Consolidation and Closeout

- **Objective:** Consolidate the authorized Stage Q Evidence and mechanically produce the final disposition without inventing results.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** Normal Q7 disposition completion or `Q3_EARLY_DISPOSITION_FP16_RETAINED`.
- **Authorized files/components:** Stage Q Final Report, Evidence Index, tables/figure data, closeout documentation, local-only Evidence classification, and release-readiness report.
- **Required actions:** Apply the frozen decision tree; document real limitations and results; retain local-only artifacts; update only conclusions supported by Evidence.
- **Explicit exclusions:** No new feature, rerun, global documentation rewrite, automatic merge, tag, or push.
- **Tests/Evidence:** Final report, Evidence Index, classification trace, and artifact retention/provenance review.
- **Gate:** `Q8_COMPLETE_READY_FOR_MAIN_MERGE`.
- **Failure states:** Required Evidence invalid, unreproducible attempt, inconsistent classification, or fabricated/missing result provenance.
- **Next authorized stage:** User-controlled review and any separately authorized merge/release action.
