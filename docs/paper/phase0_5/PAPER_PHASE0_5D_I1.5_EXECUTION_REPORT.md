# Paper Phase 0.5D-I1.5 Execution Report

## 1. Verdict

`COMPLETE`

已完成 timing-aligned 正式执行所需的最小 harness 能力补充。正式 15-run
benchmark 未执行。

## 2. Starting Git State

```text
Branch: main
HEAD: e9fd6aef98e9bcc22dd2483f3ae9dc144cc6e21e
Initial worktree: clean
```

## 3. Gap Analysis Summary

已有 harness 已支持 V0/V2R/V3R dispatch、统一配置、`timing.enabled=false`、
`profiling=off`、共享外部 timing boundary、schema/hash 校验和 3/16 preflight。
最小阻塞是 C++ runner 将 execution mode 固定为 `PREFLIGHT_ONLY`，并将 warmup
和 measured 上限固定为 3/16；其输出 identity 也固定标成 preflight。

本次只增加 `FORMAL_AUTHORITY` execution mode。正式模式接受并校验 YAML 冻结的
`warmup=60`、`measured=1080`，并将 metrics、hashes、run manifest 的 execution
identity 写为正式 evidence。preflight 限制保持不变。

## 4. Changed Files

- `tools/benchmark/stage_r_phase0_5d_timing_aligned_runner.cpp`
  - 增加 formal CLI mode；
  - 保留 preflight 3/16 限制；
  - formal mode 校验 `60/1080` 与 YAML 一致；
  - 动态写出 evidence class 和 execution mode。
- `CMakeLists.txt`
  - 仅修正专用 benchmark target 的注释，使其反映 preflight/formal 双模式。
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I1.5_GAP_ANALYSIS.md`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I1.5_EXECUTION_REPORT.md`

未修改生产 `src/`、`include/`、配置、模型、TensorRT engine、CUDA preprocessing、
Pipeline 或 V4。

## 5. Validation

### Build

PASS：

```bash
cmake --build /home/orin/edge-ai-local-build/paper_phase0_5d_i1 \
  --target stage_r_phase0_5d_timing_aligned_runner \
           stage_r_phase0_5d_config_validator -j2
```

两个专用 target 均成功构建。

### Existing tests

PASS，6/6：

```text
runtime_config
stage_r_runtime
stage_r_cuda_preprocess
stage_r_capture_control
result_sinks
serial_runner
```

### Capability validation

- Config validator：PASS；三份配置共同身份相等，variant 仅为
  `V0/V2R/V3R`，schedule positions 为 15。
- Formal CLI probe：使用 `FORMAL_AUTHORITY + warmup=60 + measured=1080`
  已通过 CLI 参数解析并进入配置加载阶段；未执行推理。
- Formal count guard probe：`59/1080` 被 formal contract 正确拒绝，证明
  正式模式不会接受偏离冻结配置的数量。
- 预期正式执行命令已在 gap analysis 中给出；按任务要求未执行正式 15-run
  benchmark，因此没有产生或声称任何正式性能数据。

## 6. Scope Compliance

确认本次没有修改：

```text
CUDA preprocessing
TensorRT implementation or engine
model / ONNX / calibration artifacts
Pipeline
V4 / double buffer
postprocess
```

没有引入 benchmark framework、通用调度系统、结果数据库或新统计模块。

## 7. Commit

```text
feat(stage-r): complete minimal timing aligned execution capability
```

## 8. Final Git Status

本次允许范围内的变更已提交；最终 worktree 为 clean；不 push、不 merge、不 tag。

## 9. Recommended Next Actor

`Paper Project Manager`
