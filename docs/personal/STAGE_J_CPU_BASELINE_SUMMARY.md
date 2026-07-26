# Stage J CPU Baseline Summary

## 1. Objective

记录 Jetson Orin Nano Super 上冻结模型、冻结 corpus 和 ONNX Runtime
CPUExecutionProvider 的 Stage J CPU baseline 当前事实。D052 后该链为
`PARTIALLY_COMPLETE`，J5.6 Tuned formal baseline 尚待补齐。

## 2. Frozen environment

- Hardware: Jetson Orin Nano Super Developer Kit。
- Architecture: aarch64。
- JetPack: 6.2.2；L4T R36.5。
- Runtime: ONNX Runtime 1.23.2，CPUExecutionProvider。
- Mode: Serial；MAXN_SUPER；active fan。
- Controlled profile: k1，CPU affinity 5，intra/inter threads 1/1。
- Tuned profile: k5，CPU affinity 1-5，intra/inter threads 5/1。

## 3. Model contract

- Model: models/onnx/yolov8n_neudet_frozen.onnx
- Model SHA256: c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944
- J5 corpus manifest SHA256: 235b062cb82166709e2ff800ec71bf92396d5348508281f822ef116d5f0962ab
- J5.1 reference SHA256: 1c31cfd41b4377c989baf35d57352280bb84f26b1942a8e26ac60076e61392a7

## 4. J5.1–J5.6 results

| Task | Result | Evidence |
|---|---|---|
| J5.1 Reference | COMPLETE | j5_1_python_reference_v1 |
| J5.2 Semantic validation | COMPLETE | j5_2_candidate_semantic_precheck_v2 |
| J5.3 Candidate sizing | COMPLETE | j5_3_candidate_sizing_v1 |
| J5.4 Profile freeze | COMPLETE; k1/k5 frozen | j5_4_profile_selection_v1 |
| J5.5 Controlled baseline | COMPLETE; k1 | j5_5_profile_baseline_v1 |
| J5.6 Tuned formal baseline | MISSING / READY_FOR_REMEDIATION | Not generated |
| Historical 30-minute k5 run | HISTORICAL_PRE_J6_STABILITY_RUN | j5_6_profile_stability_v1 |

现有六个历史 Evidence 目录均通过各自已发布 SHA256 manifest 校验；这不构成
J5.6 Tuned formal baseline、J5.7、J6、J7 或 J8 PASS。

## 5. Controlled profile result

Controlled k1 used CPU5 and ORT intra/inter threads 1/1. The five-run baseline measured approximately 2.31 FPS, with semantic output matching the frozen expected SHA and byte-identical deterministic payloads.

## 6. Historical tuned-profile stability fact

Tuned k5 used CPU1-5 and ORT intra/inter threads 5/1. The 30-minute continuous stability run processed 15420 frames across 771 cycles, with 0 failures. All cycles matched the frozen semantic output SHA; no NaN or Inf was detected.

该目录按 D052 分类为 `HISTORICAL_PRE_J6_STABILITY_RUN`。它不是冻结计划中的
J5.6 Tuned formal baseline，也不是完整 J6 Evidence。

## 7. Known limitation

D048 cross-architecture numerical limitation remains accepted: cross-architecture floating-point differences limit direct byte-level numerical equivalence claims. The J5 semantic checks use the frozen contract and accepted comparison boundary.

## 8. Current live status

- J5.1–J5.5：`COMPLETE`。
- J5.6 Tuned formal baseline：`MISSING / READY_FOR_REMEDIATION`。
- J5.7：`BLOCKED_BY_J5.6`。
- J6：`NOT_COMPLETE`。
- J7：`NOT_STARTED`。
- J8 original frozen v0.3：`FAIL`。
- Stage J CPU chain：`PARTIALLY_COMPLETE`。
- Stage T：`NOT_AUTHORIZED`；只有新的 research-grade final audit PASS 后才可规划。

## 9. Research-Grade J5 Gate v2

D053 is `Accepted`. The original J5.7 v1 result remains
`BLOCKED under the original frozen v0.3 contract` and its Evidence is
unchanged.

J5.5 is classified as the `Controlled 1-Core Resource and Reproducibility
Reference`. Its deterministic supplement does not invent per-frame timing:
latency scope is explicitly `whole_process_wall_time`; measured-window
per-frame latency distributions, per-frame sample standard deviation and
independently reconstructable raw telemetry remain unavailable.

J5.6 v3 is the `Tuned k5 Formal CPU Performance Baseline`, with five PASS
formal processes and complete measured-window statistics, correctness,
determinism, telemetry and SHA evidence.

The research-grade J5 Gate v2 verdict is
`PASS_WITH_DOCUMENTED_J5_5_LIMITATION`.

- J6：`READY`，但本任务未执行 J6。
- Stage T：`NOT_AUTHORIZED`。
- J7/J8/J9：未执行；不得声称 J8 PASS、J9 COMPLETE 或 Stage J CLOSED。
