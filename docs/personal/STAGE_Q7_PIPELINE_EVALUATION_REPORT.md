# Q7 Pipeline Evaluation Report

## Verdict

`Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION`

Q7 was executed under the frozen Pipeline contract. INT8/FP16 paired
throughput ratio was `1.012575`, above the `0.97` threshold. No runtime
failure or dropped frame was observed.

## Git

- branch: `feature/jetson-tensorrt-int8`
- HEAD: `8d7e3a8806910c406e7d26a6829655e26114927a`
- rebuilt experiment runner SHA256: `010c7f952914d168ffdbb368de8cee15f2ce3bb3725253f6102c5f90a485deea`

## Runs

- Pair 1: FP16 → INT8 — PASS, ratio `1.012476`
- Pair 2: INT8 → FP16 — PASS, ratio `1.008504`
- Pair 3: FP16 → INT8 — PASS, ratio `1.016745`
- each backend: 100 warmup, 5000 measured, 5100 accepted
- source: `CorpusReplaySource`; queue capacity `1`; drop policy `block`

## Cycle Verification

- FP16 expected complete-cycle SHA: `6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3`
- INT8 expected complete-cycle SHA: `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2`
- all runs: 28 matching complete cycles plus a 60-frame partial cycle
- partial digests were recorded only: FP16 `9caaad38d86be68fba5687a818bebc060ebf57bcc37287cf766692cdf9dd6d87`; INT8 `69d9801289dc87ee8185f80d52cec798dcd2d691e7d74505c83de68240ec20db`

## Metrics

| Metric | FP16 | INT8 |
|---|---:|---:|
| paired throughput mean (FPS) | 75.973863 | 76.929327 |
| end-to-end latency mean (ms) | 62.485602 | 59.059985 |
| end-to-end P95 (ms) | 71.585833 | 65.527168 |

Throughput ratio is `1.012575`; latency and P95 are arithmetic means across
the three paired processes, using the measured 5000-frame window.

## Pipeline Classification

`Q7_PIPELINE_EVIDENCE_VALID_NO_MATERIAL_REGRESSION`

## 300s Confirmation

- executed: yes
- result: PASS
- backend: INT8 Pipeline; queue capacity `1`; `AGGREGATE_ONLY`; cycle length `180`
- completed cycles: `126`
- processed frames: `22680`
- active wall seconds: `319.674510239`
- partial cycles: `0`
- all complete-cycle SHA values matched the Q5 INT8 expected SHA; workers
  drained and joined normally

## Scope Check

Pipeline topology, queue policy, queue capacity, worker count, engines,
calibration, model, thresholds, and benchmark windows were unchanged. The
experiment runner received only compatibility support for the existing v5
INT8 configuration and aggregate-only confirmation sink; PipelineRunner was
not modified.

Evidence:

- `results/benchmark/stage_q/q7_pipeline_v1/attempt_001/`
- `results/validation/stage_q/q7_confirmation_v1/attempt_001/`

## Authorization

Q7: `COMPLETE_PENDING_REVIEW`

Q8: `NOT AUTHORIZED UNTIL REVIEW`
