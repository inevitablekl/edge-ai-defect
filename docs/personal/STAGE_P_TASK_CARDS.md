# Stage P Task Cards v1.0 FROZEN

Authority: [Stage P Execution Plan v1.2 FINAL](STAGE_P_EXECUTION_PLAN.md). These
cards define stage boundaries only; they do not create a third workflow. All
RuntimeConfig v4, Result JSON v3, exact identity, timing, queue, Evidence,
invalidation, and authorization contracts are inherited verbatim from the plan.

## P0 — Planning Freeze and Baseline Authority

- **Objective:** Freeze v1.2, task boundaries, decisions, baseline, and branch.
- **Execution environment:** WSL Codex.
- **Entry prerequisites:** Full authoritative v1.1 body supplied; clean/known
  worktree; local main, origin/main, and peeled annotated Stage K tag all equal
  `c6890d86e7534500cfe31c40dd73f151d77d5362`; Stage P branch absent.
- **Authorized files/components:** P0 Markdown allowlist only.
- **Required actions:** Fetch refs without pull; externally archive confirmed old
  planning audit with pre/post SHA; create exact-baseline branch; freeze plan,
  cards, baseline report, D067–D071 and current status; create one freeze commit.
- **Explicit exclusions:** Production/header/CMake/test/config changes; TensorRT
  build; formal Evidence/benchmark/stability; push/merge/rebase/tag.
- **Tests or Evidence:** Read-only Git checks, asset/inventory hashes,
  `git diff --check`, allowlist and unchanged-tree checks. No build or runtime test.
- **Gate:** `P0_PASS`.
- **Failure states:** `P0_BLOCKED_PLAN_BODY_MISSING`,
  `P0_BLOCKED_DIRTY_WORKTREE`, `P0_BLOCKED_BASELINE_OR_TAG_MISMATCH`,
  `P0_BLOCKED_EXISTING_STAGE_P_BRANCH`, `P0_BLOCKED_DECISION_CONFLICT`,
  `P0_BLOCKED_PLAN_INCONSISTENCY`.
- **Next authorized stage:** P1 only after user reviews the P0 commit.

## P1 — Contract Implementation

- **Objective:** Implement compatibility-preserving Stage P data/config/result,
  canonical hash, trace, and shared Serial application contracts.
- **Execution environment:** WSL Codex, TensorRT OFF.
- **Entry prerequisites:** Reviewed P0 commit and explicit P1 authorization.
- **Authorized files/components:** RuntimeConfig v4 strict union; optional v3
  metadata/summary/timing carriers; Result JSON v3; packet/timing types;
  canonical LE serializer/hash; ConcurrentFrameTraceRecorder; minimal internal
  `run_with_components` Serial seam; focused tests and necessary CMake entries.
- **Required actions:** Preserve v1–v3 config and Result v1/v2 bytes/semantics;
  implement RUN/CYCLE independent domains and `RUN_AND_CYCLE`; validate
  finite/ranges/overflow; cover EOS source-only trace semantics.
- **Explicit exclusions:** P1 does not implement BoundedQueue, worker threads,
  PipelineRunner, CorpusReplaySource, real TensorRT smoke, or Jetson experiments.
- **Tests or Evidence:** Parser/result regressions; synthetic v3 Serial/Pipeline
  serialization; strict unions; fixed canonical vector; +0/-0; NaN/Inf rejection;
  overlapping trace intervals and callback failures.
- **Gate:** `P1_CONTRACT_IMPLEMENTATION_PASS`.
- **Failure states:** Contract regression, schema ambiguity, canonical vector
  mismatch, trace lifecycle failure, or unauthorized scope expansion.
- **Next authorized stage:** P2 after P1 gate review.

## P2 — Bounded Queue and Cancellation Primitives

- **Objective:** Implement and prove bounded SPSC queue and first-error primitives.
- **Execution environment:** WSL Codex, TensorRT OFF.
- **Entry prerequisites:** `P1_CONTRACT_IMPLEMENTATION_PASS`.
- **Authorized files/components:** BoundedQueue, queue statistics/timestamps,
  OPEN/CLOSED/CANCELLED state machine, first-error state, focused tests, and
  explicit `Threads::Threads` integration needed by these primitives.
- **Required actions:** FIFO; capacity/blocking; close/drain; cancellation
  dominance; wakeups; high-water/residence metrics; partial thread-start
  protection; repeated join/stress proof.
- **Explicit exclusions:** P2 does not implement complete PipelineRunner,
  production v4 pipeline dispatch, CorpusReplaySource, experiment runner, or
  Jetson execution.
- **Tests or Evidence:** Deterministic unit/stress tests; TSan optional if
  available; all created threads joined.
- **Gate:** `P2_QUEUE_PRIMITIVES_PASS`.
- **Failure states:** Deadlock, unjoined thread, incorrect drain/cancel behavior,
  HWM above capacity, timestamp/statistics corruption, first-error overwrite.
- **Next authorized stage:** P3 after P2 gate review.

## P3 — Pipeline and Experiment Integration

- **Objective:** Integrate the fixed four-worker runtime and experiment seams.
- **Execution environment:** WSL Codex, `EDGE_AI_ENABLE_TENSORRT=OFF`.
- **Entry prerequisites:** P1 and P2 gates pass.
- **Authorized files/components:** Four-worker PipelineRunner, v4 dispatch,
  DirectorySource pipeline, CorpusReplaySource, StagePExperimentRunner,
  CanonicalHashSink, TimedJsonSink, queue stats, minimal internal/test seams,
  focused tests and Threads CMake integration.
- **Required actions:** Four workers/three queues; one inference worker;
  `max concurrent engine.run()=1`; normal close propagation; first-error and
  trace-callback cancellation; atomic summary; empty-source parity; replay
  1100/5100 counts; correct Sink order and dual-scope hashing.
- **Explicit exclusions:** WSL v4 smoke uses fake engine and is component/internal
  application-seam evidence only. It is not a real TensorRT production v4 CLI
  PASS. No public DI framework, thread pool, plugin registry, videoio, benchmark,
  stability, or Jetson formal Evidence.
- **Tests or Evidence:** Normal EOS; empty source (one probe, no end_run, unchanged
  summary, no wall-time fabrication); every component/Sink/trace failure; partial
  thread creation; active-service cancellation; no post-cancel enqueue; FIFO;
  queue terminal states; engine concurrency maximum one; v1–v3 regression.
- **Gate:** `P3_PIPELINE_IMPLEMENTATION_PASS`.
- **Failure states:** Semantic divergence, deadlock, leak/unjoined worker,
  component cross-thread ownership, summary mutation on failure, false real-CLI claim.
- **Next authorized stage:** P4 on a clean committed source HEAD.

## P4 — Jetson Exact Correctness

- **Objective:** First real TensorRT production v4 CLI smoke and exact
  Serial/Pipeline Detection correctness.
- **Execution environment:** Jetson Codex, TensorRT ON.
- **Entry prerequisites:** `P3_PIPELINE_IMPLEMENTATION_PASS`; clean committed
  source; frozen Engine/manifest/contract/corpus identities.
- **Authorized files/components:** Unique local configs/outputs, production CLI
  smoke, experiment runner and P4 Evidence path only.
- **Required actions:** Real v4 Serial/Pipeline CLI end-to-end smoke; Serial ×1,
  Pipeline ×3 at capacity 2/block; shared-semantics preflight; each run uses
  `RUN_AND_CYCLE`; freeze expected RUN and complete 180-frame CYCLE SHA.
- **Explicit exclusions:** Engine rebuild, semantic changes, benchmark claims,
  queue-capacity selection, or raw TensorRT Level B reinterpretation.
- **Tests or Evidence:** 180 accepted/processed, zero drop, finite, exact
  sequence/path/detections, four identical RUN SHA, complete CYCLE identity,
  joined workers, all queues CLOSED/drained and none CANCELLED.
- **Gate:** `P4_PIPELINE_CORRECTNESS_PASS`.
- **Failure states:** `P4_INVESTIGATION_REQUIRED` or
  `P4_PIPELINE_CORRECTNESS_FAIL`; invalid preflight/attempt retained separately.
- **Next authorized stage:** P5 only after P4 PASS.

## P5 — Queue Pilot and Formal Benchmark

- **Objective:** Select capacity and measure paired Serial/Pipeline throughput.
- **Execution environment:** Jetson Codex under frozen power/fan/affinity policy.
- **Entry prerequisites:** `P4_PIPELINE_CORRECTNESS_PASS`.
- **Authorized files/components:** P5 pilot/formal Evidence paths, capacities
  1/2/4, CorpusReplaySource, identical Sink/trace composition and telemetry.
- **Required actions:** Pilot each capacity in an independent 1100-frame process;
  gate complete CYCLE hashes against P4 expected CYCLE SHA and select the
  smallest capacity within 95% of best throughput. Then execute the exact
  3-pair/6-process 5100-frame formal order and freeze selection.
- **Explicit exclusions:** No capacity change after formal benchmark, outlier
  removal, per-worker affinity, significance claim, runtime semantic change, or
  optimization outside Stage P.
- **Tests or Evidence:** Every run `RUN_AND_CYCLE`; pilot 1000 and formal 5000
  complete measured traces; formal window frame 100 source begin through frame
  5099 outer Sink end; all hashes/counts/drop/thermal validity; Type-7
  percentiles; paired ratios, mean and sample SD.
- **Gate:** P5 complete only when queue capacity is selected/frozen **and** the
  formal benchmark protocol is complete. Classification is ≥1.10 material,
  0.95–<1.10 no material change, <0.95 regression.
- **Failure states:** Invalid thermal attempt, incomplete measured trace,
  hash/count mismatch, deadlock/crash/non-finite, invalid shared-semantics preflight.
- **Next authorized stage:** P6 only after the complete P5 gate.

## P6 — VideoFileSource

- **Objective:** Add deterministic offline video-file input without changing
  block-only semantics.
- **Execution environment:** WSL implementation/non-formal codec smoke; Jetson
  formal asset generation, codec preflight, and validation.
- **Entry prerequisites:** P5 capacity selected/frozen **and** P5 formal benchmark
  complete.
- **Authorized files/components:** VideoFileSource, RuntimeConfig v4
  `video_file` union already frozen by P1, OpenCV `videoio` dependency,
  focused tests, local frozen video asset and P6 Evidence.
- **Required actions:** `cv::VideoCapture`; zero-based frames; exact dimensions;
  normal EOF/decode fail-fast; identity
  `video_path.filename().generic_u8string()/frame_000000`; production CLI
  smoke; Serial ×1/Pipeline ×1 exact runs using selected capacity and RUN scope.
- **Explicit exclusions:** No RuntimeConfig `input.max_frames`; constructor-only
  max_frames control; no formal frame limit; nominal FPS is descriptive sidecar
  metadata only; no Directory-vs-video pixel/detection comparison; no codec
  fallback, GStreamer, camera, or RTSP.
- **Tests or Evidence:** Jetson MJPG AVI write/reopen/full-decode preflight;
  sidecar records FPS/count/FourCC/resolution identities; decoded=generated;
  continuous indexes/paths; zero drop; finite; equal Serial/Pipeline RUN SHA;
  Result v3; queues CLOSED/drained.
- **Gate:** `P6_VIDEO_SOURCE_PASS`.
- **Failure states:** `P6_VIDEO_SOURCE_FAIL` or
  `P6_BLOCKED_CODEC_PREFLIGHT`. WSL encoder absence alone is not global failure.
- **Next authorized stage:** P7 after P6 disposition and P5 prerequisites remain frozen.

## P7 — Pipeline Stability

- **Objective:** Prove one bounded Pipeline lifecycle for at least 1800 seconds.
- **Execution environment:** Jetson Codex.
- **Entry prerequisites:** P4 correctness, P5 selected capacity/formal completion,
  and P6 disposition complete.
- **Authorized files/components:** CorpusReplaySource, CanonicalHashSink in CYCLE
  mode, ConcurrentFrameTraceRecorder AGGREGATE_ONLY, telemetry and P7 Evidence.
- **Required actions:** One lifecycle; block-only; normal EOS then drain; validate
  every complete cycle against P4 expected CYCLE SHA; record partial cycle frame
  count and partial digest without comparing it as a full 180-frame cycle.
- **Explicit exclusions:** P7 does not use JsonSink, full per-frame trace, retained
  full Detection list, live drop policy, watchdog, recovery, or industrial leak
  certification.
- **Tests or Evidence:** ≥1800 s source-active duration; zero crash/deadlock/
  non-finite/inference error/drop; source_frames=processed_images; monotonic
  global sequence; joined workers; queues CLOSED/drained/not CANCELLED/HWM within
  capacity/zero remaining; RSS/stage/queue/thermal aggregates.
- **Gate:** `P7_PIPELINE_STABILITY_PASS`.
- **Failure states:** `P7_PIPELINE_STABILITY_FAIL`; thermal/telemetry limitation
  disclosed under the plan; partial cycle never upgraded to full PASS.
- **Next authorized stage:** P8 after P4–P7 dispositions are complete.

## P8 — Consolidation and Closeout

- **Objective:** Consolidate real P4–P7 Evidence and select final runtime guidance.
- **Execution environment:** WSL/Jetson documentation consolidation as applicable.
- **Entry prerequisites:** All P4–P7 dispositions complete; Evidence identities and
  invalidation audit pass.
- **Authorized files/components:** Final report, evidence index, paper tables/
  figures from real logs, and approved status documents.
- **Required actions:** Summarize exact correctness, pilot, paired benchmark,
  video, stability, Stage K raw Level B retained limitation, trade-offs and
  known limitations; verify SHAs and invalidation boundaries.
- **Explicit exclusions:** Fabricated metrics, rewritten historical Evidence,
  retroactive Engine/contract/corpus changes, push/merge/tag without authorization.
- **Tests or Evidence:** Evidence matrix/index, SHA verification, reproducible
  calculations and status-document consistency.
- **Gate:** `STAGE_P_COMPLETE_PIPELINE_RECOMMENDED`,
  `STAGE_P_COMPLETE_SERIAL_RETAINED`, or `STAGE_P_FAILED` under v1.2.
- **Failure states:** Unclosed exact correctness, irreparable invalid Evidence,
  unaccepted video platform failure, or stability failure.
- **Next authorized stage:** None automatically; closeout requires user review.
