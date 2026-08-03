# Paper Phase 0.5D-I1.5 Gap Analysis

## A. 当前能力

审查基线为 `main` branch，HEAD
`e9fd6aef98e9bcc22dd2483f3ae9dc144cc6e21e`。本报告只审查 timing-aligned
实验执行闭环，不扩大为通用 benchmark framework。

### 已完成能力

- 专用 C++ runner 已存在：
  `tools/benchmark/stage_r_phase0_5d_timing_aligned_runner.cpp`。
- `run_selected()` 已明确只接受 `V0`、`V2R`、`V3R`：
  `V0` 走 `SerialRunner`，`V2R` 走 pageable runner，`V3R` 走 pinned
  runner；没有引入 Pipeline 或 V4。
- 三份 timing-aligned YAML 已存在：
  `configs/stage_r/runtime_v6_v0_timing_aligned.yaml`、
  `runtime_v6_v2r_timing_aligned.yaml`、
  `runtime_v6_v3r_timing_aligned.yaml`。
- 三份 YAML 的共同实验字段已经冻结为 TensorRT INT8、batch 1、input 640、
  threshold 0.25、NMS IoU 0.45、OpenCV threads 1、warmup 60、measured
  1080；唯一 variant 差异是 `data_path.variant`。
- `timing.enabled=false` 和 `profiling.mode=off` 已由配置 validator 与
  runner 配置检查；metadata 也固定记录 `timing_enabled=false`。
- 外部 timing boundary 已存在，且 sink 会拒绝内部 timing object；结果 JSON
  不包含 per-frame timing 字段。
- 现有 config validator 已验证 V0/V2R/V3R 的共同身份和固定 15-position
  交错 schedule。
- CMake 已注册专用 runner 与 config validator target。

### 已验证能力

HEAD 所带的 I1 preflight evidence 已证明三 variant 可各运行 3 warmup + 16
measured，结果 schema、EOS、drop count、检测 hash 和外部 timing sample
contract 均满足 preflight 规则。该 evidence 明确不是正式性能 evidence。

本次 I1.5 修改后的验证另见
`PAPER_PHASE0_5D_I1.5_EXECUTION_REPORT.md`；本次没有执行正式 15-run
benchmark。

### 已存在代码入口

```text
Build target:
  stage_r_phase0_5d_timing_aligned_runner
  stage_r_phase0_5d_config_validator

Preflight launcher:
  tools/benchmark/run_stage_r_phase0_5d_preflight.py

Config validator:
  tools/benchmark/stage_r_phase0_5d_config_validator.cpp

Runtime configs:
  configs/stage_r/runtime_v6_v0_timing_aligned.yaml
  configs/stage_r/runtime_v6_v2r_timing_aligned.yaml
  configs/stage_r/runtime_v6_v3r_timing_aligned.yaml
```

## B. 最小缺口

### 必须修改

1. **正式 execution mode 未被 CLI 接受。** Runner 原先只接受
   `--execution-mode PREFLIGHT_ONLY`。
2. **preflight frame 上限阻塞正式规模。** 原先无论场景如何都限制
   `warmup <= 3`、`measured <= 16`。
3. **正式输出身份会被误标为 preflight。** metrics、hashes 和 run manifest
   原先硬编码 `PREFLIGHT_ONLY` / `NOT_FORMAL_PERFORMANCE_EVIDENCE`，即使
   放宽数量也不能形成可审计的正式 run artifact。

因此最小必要修改是只扩展该 benchmark runner：保留 preflight 的 3/16
保护；新增 `FORMAL_AUTHORITY`；正式模式要求 CLI 的 warmup/measured 与
YAML 的 `phase0_5d` 值一致，并按 execution mode 写出对应 evidence identity。

### 可以不修改

- 不需要修改三份 YAML；它们已经声明 V0/V2R/V3R、`timing=false`、
  `profiling=off` 和 `60/1080`。
- 不需要修改 `src/`、`include/`、生产 runner、backend dispatch、CUDA
  preprocessing、TensorRT engine 或 postprocess。
- 不需要重新设计 runner；现有 runner 已具备统一 warmup、measured、sink、
  hash 和外部 timing boundary。
- 不需要增加通用调度系统。正式实验可由 Paper Project Manager 手工执行每个
  variant 五次，使用独立的新 output directory。
- 不需要新增统计模块、结果数据库或自动 15-task orchestrator。每个正式 run
  已输出 latency samples、metrics、hashes 和 run manifest；正式结果汇总仍可
  在真实 runs 完成后进行。
- 不需要修改 Pipeline、V4 或任何后续优化路径。

## C. 推荐最小方案

已采用的最小方案如下：

```text
PREFLIGHT_ONLY:
  保持 warmup <= 3、measured <= 16
  保持 NOT_FORMAL_PERFORMANCE_EVIDENCE

FORMAL_AUTHORITY:
  接受 warmup=60、measured=1080
  要求与 phase0_5d YAML 的 60/1080 一致
  输出 FORMAL_PERFORMANCE_EVIDENCE 和 FORMAL_AUTHORITY identity
```

正式执行仍由同一个专用 runner 完成，调用形式为：

```bash
stage_r_phase0_5d_timing_aligned_runner \
  --config configs/stage_r/runtime_v6_v0_timing_aligned.yaml \
  --manifest results/validation/stage_q/split_v2_deduplicated/test_manifest_v2.json \
  --output-dir <new-output-dir> \
  --warmup-frames 60 \
  --measured-frames 1080 \
  --execution-mode FORMAL_AUTHORITY
```

将配置和 variant 替换为 `V2R`、`V3R` 即可。每次运行必须使用新的 output
directory；正式 15-run schedule、环境记录、真实数据汇总和论文结论仍属于后续
明确授权的实验执行，不属于本次 I1.5。

结论：当前 harness 原本距离可信论文性能对比只差正式 execution mode 的
最小 CLI/metadata 补充，不差 variant、timing boundary、配置公平性或生产
runner 重构。
