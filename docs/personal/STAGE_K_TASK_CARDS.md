# Stage K Task Cards

Document status: FROZEN_AT_K0_FREEZE
Parent protocol: `docs/personal/STAGE_K_EXECUTION_PLAN.md` — Stage K Execution Plan v1.1 FINAL
Planning baseline commit: `e49f28dd60a49493538d1fd65e5e8fd81676e277`
Planning baseline tag: `stage-j-complete-v1.0`

These cards are task-boundary records derived from the frozen Stage K plan.
They do not claim implementation, test registration, PASS results, Engine
artifacts, or Evidence for tasks that have not executed.

## K0 — Planning Freeze

- Task ID: K0
- Title: Stage K Planning Freeze
- Status: `IN_PROGRESS_UNTIL_FREEZE_COMMIT`
- Authorization: `AUTHORIZED`
- Prerequisites: main at the verified Stage J closeout baseline; clean worktree and index.
- Objective: Freeze the final Stage K protocol, task boundaries, K0 inventory, Decisions D055–D061, and consistent live status in one local main commit.
- In Scope:
  - Write the complete Stage K Execution Plan v1.1 FINAL.
  - Derive these Task Cards and the compact K0 test inventory.
  - Append D055–D061 without modifying D001–D054.
  - Make only focused current-status corrections in live documents.
  - Validate YAML, numbering, names/statuses, diff scope, and fresh CTest registration.
  - Create one local freeze commit and then `feature/jetson-tensorrt-fp16`.
- Out of Scope: K1 hardware acceptance; TensorRT/CUDA commands; trtexec; Engine build; compile/link smoke; production C++ or CMake changes; RuntimeConfig v3; TensorRtEngine; Stage P; package installation or upgrade.
- Inputs: verified starting commit/tag; current source facts; Stage K Execution Plan v1.1 FINAL attachment; Stage J inventory.
- Expected Files or Artifacts: Stage K plan; Task Cards; K0 inventory; D055–D061; focused live-status updates; one K0 freeze commit; feature branch.
- Required Checks: exact starting-state verification; `git diff --check`; YAML parse and duplicate-key check; decision numbering; naming/status scan; fresh CTest OFF=34 and ON=42; allowed-scope audit.
- Gate: `K0 COMPLETE`; `K1 READY`.
- Stop Conditions: any starting-state mismatch; worktree/index change outside this task; fresh CTest count differs from 34/42; validation failure; unexpected production or Stage J historical change.
- Evidence Retention: commit, SHA256 values, validation outputs and final execution report; no unrequested Stage K runtime Evidence.
- Completion Report Requirements: report starting state, files, Decisions, inventory counts, validation, four SHA values, Git result, explicit non-actions, and only the next authorized step K1.

## K1 — Jetson TensorRT Platform Acceptance

- Task ID: K1
- Title: Jetson TensorRT Platform Acceptance
- Status: `NOT_AUTHORIZED_UNTIL_K0_COMPLETE`
- Authorization: `AUTHORIZED_AFTER_K0_COMPLETE`; not authorized in K0.
- Prerequisites: K0 freeze commit and feature branch; Jetson target available; no package installation unless separately authorized.
- Objective: Verify the observed CUDA/TensorRT runtime, headers, libraries, trtexec semantics and minimal host-only CUDA/TensorRT runtime smoke.
- In Scope: read-only platform/toolchain checks; `nvcc` path/version observation; CUDA/TensorRT header/library checks; trtexec path/version/help; tegrastats; minimal C++ host-only runtime/stream smoke.
- Out of Scope: Engine build; `trtexec` build execution; production code; CMake TensorRT support; RuntimeConfig v3; TensorRtEngine; Pipeline; package installation/upgrades.
- Inputs: Jetson platform; frozen ONNX and ModelContract identities; K0 branch.
- Expected Files or Artifacts: `results/platform/tensorrt/k1_environment_v1/` with commands, outputs, environment snapshot and disposition.
- Required Checks: CUDA runtime/header/link availability; TensorRT runtime/header/link availability; trtexec help semantics; explicit unavailable classifications.
- Gate: `K1 PASS`; `D062 READY`.
- Stop Conditions: required runtime/header/link failure; contradictory platform fact; package change needed without authorization; any Engine build or production implementation request.
- Evidence Retention: formal K1 attempt, commands, raw outputs, environment facts and SHA manifest; preserve failures.
- Completion Report Requirements: actual paths/versions/help semantics, smoke result, limitations, K1 Gate and D062 readiness; no invented values.

## D062 — Exact TensorRT Engine Build Contract

- Task ID: D062
- Title: Freeze Exact TensorRT Engine Build Contract
- Status: `NOT_AUTHORIZED_UNTIL_K1_PASS`
- Authorization: `AUTHORIZED_AFTER_K1_PASS`; not authorized in K0.
- Prerequisites: K1 PASS and real `trtexec --help` semantics.
- Objective: Freeze the exact offline Engine build command and its platform-specific options before K2.
- In Scope: trtexec path/version/help; exact source ONNX, FP16, static shape, batch, memory-pool/workspace, FP32 I/O, saveEngine and skipInference semantics; load-engine smoke; output/log/inspection paths.
- Out of Scope: executing the formal K2 build; changing the plan; implementing runtime code; broad build-framework design.
- Inputs: K1 platform Evidence; frozen ONNX SHA; ModelContract SHA.
- Expected Files or Artifacts: accepted D062 Decision and exact build-contract record.
- Required Checks: every command option must be supported by observed help semantics; K2 remains unauthorized until acceptance.
- Gate: `D062 ACCEPTED`; `K2 READY`.
- Stop Conditions: missing or ambiguous trtexec semantics; unsupported requested option; plugin dependency requiring a new Decision.
- Evidence Retention: K1-derived help output, contract record, command and acceptance rationale.
- Completion Report Requirements: exact command semantics and accepted limitations; no unobserved parameter names or values.

## K2 — Engine Build and Freeze

- Task ID: K2
- Title: Offline TensorRT FP16-Enabled Engine Build and Freeze
- Status: `NOT_AUTHORIZED_UNTIL_D062_ACCEPTED`
- Authorization: `AUTHORIZED_AFTER_D062_ACCEPTED`; not authorized in K0.
- Prerequisites: K1 PASS; D062 ACCEPTED; feature branch.
- Objective: Build, inspect, load-smoke and freeze one fixed TensorRT mixed-precision Engine and Manifest.
- In Scope: formal trtexec build; complete logs; Engine SHA/size; tensor inspection; independent load-engine smoke; manifest identity and provenance.
- Out of Scope: production application loading implementation; runtime ONNX parsing; runtime build/tactic selection; Engine byte-identical rebuild claim; TensorRtEngine; Pipeline.
- Inputs: frozen ONNX, ModelContract, D062 exact command, Jetson platform.
- Expected Files or Artifacts: local-only `.engine`; tracked `models/tensorrt` README/manifest; `results/build/tensorrt/k2_fp16_engine_v1/`.
- Required Checks: static batch/input/output contract; FP16 builder mode; FP32 host I/O; INT8/DLA disabled; plugin inspection; independent load smoke.
- Gate: parser/build PASS; deserialization PASS; exact I/O; no unaccepted plugin dependency; Engine/Manifest verified.
- Stop Conditions: any contract mismatch, plugin dependency, failed load smoke, non-finite/unsupported I/O, or need to alter frozen ONNX/ModelContract.
- Evidence Retention: immutable formal attempts, build logs, inspection, smoke, Engine/Manifest SHA chain and failure records.
- Completion Report Requirements: actual Engine and Manifest identities, command/log paths, inspection and smoke results, limitations.

## K3 — Build and Schema Foundation

- Task ID: K3
- Title: Optional TensorRT Build and Schema Foundation
- Status: `NOT_STARTED`
- Authorization: `AUTHORIZED_FROM_K3` only after K2 prerequisites and implementation review.
- Prerequisites: K2 Gate; production implementation authorization.
- Objective: Add the minimum optional CMake/build, RuntimeConfig v3, Result JSON v2, Manifest parser, factory skeleton and status/logging foundation.
- In Scope: TensorRT OFF regression; optional TensorRT target/dependencies; v3 parser with v1/v2 regressions; minimal Result v2 extension; Manifest parser; backend factory skeleton; `.engine` ignore.
- Out of Scope: TensorRtEngine execution lifecycle; Pipeline; CUDA preprocessing/NMS; INT8; dynamic registration/fallback; production code before authorization.
- Inputs: K2 Manifest and exact contracts; existing v1/v2 code and tests.
- Expected Files or Artifacts: implementation source/tests and focused build/test results, only when authorized.
- Required Checks: OFF build remains TensorRT-free; v1/v2 behavior unchanged; v3 rejects invalid sections/fields; Result v1 unchanged; factory preserves backend-neutral runner.
- Gate: K3 implementation checks PASS.
- Stop Conditions: schema duplication/refactor expansion; backend leakage into runners; dependency mismatch; any need to change Stage J semantics.
- Evidence Retention: source commit, commands, tests, short report and limitations; no oversized Evidence package.
- Completion Report Requirements: changed implementation files, checks, actual test names/results and known limitations.

## K4 — TensorRtEngine

- Task ID: K4
- Title: TensorRtEngine Runtime Lifecycle and Contract
- Status: `NOT_STARTED`
- Authorization: `AUTHORIZED_AFTER_K3` and only under an approved K4 implementation task.
- Prerequisites: K3 foundation; verified Engine/Manifest; TensorRT development dependencies.
- Objective: Implement the synchronous HostTensor TensorRT backend with persistent resources, ordered one-stream execution and failure atomicity.
- In Scope: Runtime/Engine/Context/stream initialization; named I/O validation; persistent device buffers; H2D→enqueueV3→D2H synchronization; finite/output checks; RAII; caller-output preservation.
- Out of Scope: public DeviceTensor/asynchronous API; per-frame CUDA allocation; per-frame stream/context creation; multiple streams/contexts; GPU preprocessing/NMS; Pipeline; fallback.
- Inputs: Engine Manifest; ModelContract; IInferenceEngine; HostTensor contract.
- Expected Files or Artifacts: TensorRtEngine implementation and focused tests, only after authorization.
- Required Checks: null/uninitialized input; Manifest/Engine/ModelContract/I/O mismatch; failure atomicity; finite output; no per-frame resource reconstruction; cleanup.
- Gate: K4 contract and lifecycle checks PASS.
- Stop Conditions: hidden CUDA/TensorRT error; changed HostTensor dtype contract; resource recreation; output mutation on failure; unsupported dynamic behavior.
- Evidence Retention: source commit, commands, focused tests, short report and limitations.
- Completion Report Requirements: lifecycle contract, resource ownership, error handling, checks and actual limitations.

## K5 — Correctness

- Task ID: K5
- Title: ORT Control, TensorRT Level B/C Correctness
- Status: `NOT_STARTED`
- Authorization: `AUTHORIZED_AFTER_K4` and only under an approved K5 task.
- Prerequisites: K4 PASS; frozen Stage J J4.3 corpus/manifest and J5.1 tracked benchmark assets; K5 harness implementation authorization.
- Objective: Compare Python ORT Reference → same-commit C++ ORT control → TensorRT candidate without changing shared preprocessing/postprocessing semantics.
- In Scope:
  - Backend-neutral harness: raw FP32 little-endian input → IInferenceEngine-selected backend → raw FP32 little-endian output → shape/dtype/element-count/byte-size/SHA manifest.
  - Extend the existing Level B comparator with Hyndman–Fan Type 7 P99 while retaining MAE, max_abs and bbox/score channel metrics.
  - Run the same harness for ORT and TensorRT; apply the frozen Level B/C and threshold-boundary policies.
  - Retain only targeted mismatch diagnostics.
- Out of Scope: Artifact Database; Replay Framework; full-candidate NMS provenance system; second full reference framework; changing Stage J comparator/tolerances; implementing this harness during K0.
- Inputs: Stage J J4.3 16-image local-only corpus/manifest; tracked Stage J J5.1 20-image reference/corpus manifest; frozen model/contract; K4 backend.
- Expected Files or Artifacts: K5 local Evidence, manifests/reports and focused comparator/harness tests when implemented.
- Required Checks: ORT Level B disposition; ORT Level C strict regression; TensorRT Level B 16/16; matched Level C; finite/exact shapes; boundary policy.
- Gate: `K5 PASS` or `K5 PASS_WITH_REPORTED_NUMERICAL_BOUNDARY_VARIATION`.
- Stop Conditions: ORT control fail; any TensorRT Level B failure; class/NMS/post-filter divergence; unexplained mismatch; excessive boundary cases; missing raw identity.
- Evidence Retention: formal attempts, raw metrics, manifests, targeted diagnostics only when triggered, source/provenance and failure records.
- Completion Report Requirements: disposition, per-tensor metrics, ORT limitation status, Level C result, boundary classification and actual retained artifacts.

## K6 — Application and Benchmark Integration

- Task ID: K6
- Title: Production Application and Benchmark Integration
- Status: `NOT_STARTED`
- Authorization: `AUTHORIZED_AFTER_K5` and only under an approved K6 task.
- Prerequisites: K5 Gate; K3/K4 implementation; shared application contract review.
- Objective: Replace direct ORT construction with the minimum backend factory path and add Stage K profile/semantic preflight integration.
- In Scope: ORT v2 and TensorRT v3 application paths; Stage K profile runner; TraceRecorder/telemetry reuse; shared config semantics validator; analyzer adaptation; 20-image semantic preflight and TensorRT canonical cycle SHA.
- Out of Scope: modifying Stage J profile runner; production benchmark mode; new profiler/framework; Pipeline; camera/ROS2; GPU preprocessing/NMS.
- Inputs: K5 correctness; frozen 20-image tracked corpus/reference; RuntimeConfig v2/v3; Engine/Manifest.
- Expected Files or Artifacts: implementation/test changes and K6 short report/commands/limitations.
- Required Checks: ORT v2 regression; TensorRT v3 application; 20-image ORT/TRT semantic preflight; timing trace; telemetry; benchmark preflight.
- Gate: all K6 preflight checks PASS.
- Stop Conditions: backend-specific runner leakage; changed v1/v2/Result v1 semantics; cycle hash drift; config semantic mismatch; application failure.
- Evidence Retention: source commit, commands, tests, short report and limitations; preserve formal preflight failures.
- Completion Report Requirements: actual factory/profile/analyzer behavior, test results, semantic SHA and limitations.

## K7 — Formal Benchmark

- Task ID: K7
- Title: TensorRT Serial Benchmark
- Status: `NOT_STARTED`
- Authorization: `AUTHORIZED_AFTER_K6` and only under an approved K7 task.
- Prerequisites: K6 Gate; same device/executable/corpus/pre/postprocess controls; frozen Engine and config identities.
- Objective: Measure ORT CPU k5 versus TensorRT serial backend under the frozen paired five-run protocol.
- In Scope: five independent processes per backend; 60 warmup; 500 measured frames; 25 corpus cycles; timing/telemetry; Type 7 statistics; paired speedups; validity and descriptive status.
- Out of Scope: using Stage J historical numbers for formal speedup; E2E/backend metric conflation; pooled-frame independence claims; Pipeline or performance threshold invention.
- Inputs: same Jetson, executable SHA, source commit, Engine SHA, ModelContract, corpus, config semantics and runner timing semantics.
- Expected Files or Artifacts: `results/benchmark/jetson_tensorrt_fp16/k7_serial_backend_comparison_v1/`.
- Required Checks: ten valid runs; correctness/application success; non-zero GPU activity; complete telemetry and statistics; thermal invalidation semantics.
- Gate: `COMPLETE_WITH_LOWER_MEASURED_LATENCY` or `COMPLETE_WITHOUT_LOWER_MEASURED_LATENCY`, based only on real data.
- Stop Conditions: correctness/application failure; invalid run; incomplete formal data; thermal invalidation; missing provenance.
- Evidence Retention: all formal attempts, raw traces/telemetry, configs, reports, SHA lists and failures.
- Completion Report Requirements: actual run values, distributions, paired results, validity, descriptive status and no fabricated performance claim.

## K8 — TensorRT Stability

- Task ID: K8
- Title: TensorRT Serial Stability
- Status: `NOT_STARTED`
- Authorization: `AUTHORIZED_AFTER_K7` and only under an approved K8 task.
- Prerequisites: K7/K6 contracts; frozen Engine/cycle SHA; inherited Stage J J6 analyzer semantics.
- Objective: Run one formal continuous TensorRT serial stability campaign for at least 1800 seconds.
- In Scope: repeated 20-image corpus; wall-clock/cycle/frame counts; canonical cycle hash; hash drift; VmRSS; CPU/GPU utilization/frequency; temperature; TensorRT/CUDA error counts; inherited unavailable classification.
- Out of Scope: rerunning ORT stability; new memory/thermal model; cooldown controller; power-improvement claim without real telemetry; Pipeline.
- Inputs: Stage J J6 stability semantics, analyzers and telemetry rules; K6 canonical cycle SHA; K7 Engine.
- Expected Files or Artifacts: `results/benchmark/jetson_tensorrt_fp16/stability/k8_tensorrt_stability_v1/`.
- Required Checks: ≥1800 s; zero crash/failed frame/failed cycle/hash drift; J6-compatible VmRSS PASS; no thermal throttle; valid mandatory telemetry.
- Gate: `K8 COMPLETE`.
- Stop Conditions: crash/failure/hash drift; thermal throttling; invalid mandatory telemetry; corpus or Engine drift.
- Evidence Retention: formal run, raw telemetry, analyzer outputs, failure records and SHA manifest.
- Completion Report Requirements: actual duration/counts/hash/memory/telemetry verdict and inherited limitations.

## K9 — Closeout

- Task ID: K9
- Title: Stage K Evidence Consolidation and Closeout
- Status: `NOT_STARTED`
- Authorization: `AUTHORIZED_AFTER_K8` and only under an approved K9 task.
- Prerequisites: K1, D062, K2, K5, K6, K7 and K8 gates; owner review.
- Objective: Consolidate research-grade Stage K Evidence and freeze the downstream Stage P boundary.
- In Scope: fixed consolidation files; provenance and SHA chain; final report; minimal live-status updates; Stage P planning boundary.
- Out of Scope: Stage P implementation; production-ready/industrial validation claims; INT8; Pipeline execution; modifying Stage J final reports/Evidence/Accepted Decisions.
- Inputs: formal K1/K2/K5/K7/K8 Evidence and K3/K4/K6 implementation records.
- Expected Files or Artifacts: `results/consolidation/stage_k/stage_k_tensorrt_fp16_serial_v1/`; `docs/personal/STAGE_K_FINAL_REPORT.md`.
- Required Checks: Evidence index/provenance/attempt registry/verification/SHA validation; all claims trace to real data; limitations retained.
- Gate: Stage K `COMPLETE`; Stage P `READY_FOR_PLANNING_REVIEW`; Stage P implementation remains unauthorized.
- Stop Conditions: missing formal Evidence; broken SHA chain; fabricated result; historical Stage J mutation; premature Stage P implementation.
- Evidence Retention: immutable formal and decision-relevant attempts; fixed consolidation seven-file contract; preserve failures.
- Completion Report Requirements: actual consolidated files/SHA, Gate disposition, limitations and explicit Stage P authorization boundary.

## Downstream Boundary

- Stage P status: `REQUIRED_DOWNSTREAM_SCOPE`
- Stage P authorization: `NOT_AUTHORIZED_BEFORE_STAGE_K_CLOSEOUT`
- No Stage P implementation, Pipeline runner, concurrency, camera, ROS2, GUI, INT8 or GPU preprocessing/NMS is authorized by these cards.
