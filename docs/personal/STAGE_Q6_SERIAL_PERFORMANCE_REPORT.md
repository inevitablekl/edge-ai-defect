# Q6 Serial Performance Report

## Verdict

`Q6_SERIAL_PERFORMANCE_EVIDENCE_VALID`

TensorRT INT8 PTQ produced a material serial inference gain and no material end-to-end regression under the frozen Q6 protocol.

## Git

- branch: `feature/jetson-tensorrt-int8`
- HEAD: `8d7e3a8806910c406e7d26a6829655e26114927a`

## Environment

- device: Jetson Orin Nano Super
- power mode: `MAXN_SUPER` (`nvpmodel -q`)
- CPU affinity: `0-5`
- OpenCV threads: `1`
- thermal samples: available through `tegrastats`; start/end samples are in the evidence directory
- `jetson_clocks --show`: unavailable without root; recorded verbatim
- `thermal_throttle_status`: `unavailable` (see `thermal_throttle_status.txt`)
- application binary SHA256: `737f2cc5986c925c80c7cb25367ebb04b4f44f848bceeed390e2c3788f5a3373`
- application library SHA256: `dc588a6b1608f267df6f22c5d2d6ffde026abf690757866049cef2d33db8456c`
- runner binary SHA256: `e4ac960e8d3aea3aef1e526298ce1f8b2c8df41f452544bff659364d12eac212`
- manifest SHA256: `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194`
- FP16 engine SHA256: `6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc`
- INT8 engine SHA256: `8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee`

## Runs

- Pair 1: FP16 → INT8 — PASS
- Pair 2: INT8 → FP16 — PASS
- Pair 3: FP16 → INT8 — PASS
- each process: 100 warmup, 5000 measured, 5100 accepted
- source: `CorpusReplaySource`, manifest order, cycle length 180, drop 0
- each backend: 28 complete cycles plus a 60-frame partial cycle

## Metrics

Arithmetic means across the three paired processes:

| Metric | FP16 | INT8 |
|---|---:|---:|
| Inference service mean (ms) | 13.849349 | 10.906217 |
| Pre-sink throughput (FPS) | 31.956232 | 37.478347 |
| End-to-end mean latency (ms) | 31.116138 | 26.515925 |
| End-to-end P50 (ms) | 31.176405 | 26.510330 |
| End-to-end P95 (ms) | 31.931430 | 27.207150 |
| End-to-end P99 (ms) | 32.124961 | 27.441396 |

Percentiles use Type-7 linear interpolation. The pre-sink window is the first measured source begin through the last measured postprocess end.

## Classification

- inference gain ratio: `1.269856` — `MATERIAL_INT8_INFERENCE_GAIN`
- throughput ratio INT8/FP16: `1.172850`
- mean latency ratio INT8/FP16: `0.852194`
- P95 latency ratio INT8/FP16: `0.852066`
- end-to-end result: `NO_MATERIAL_END_TO_END_REGRESSION`

All complete-cycle SHA values matched the corresponding Q5 expected SHA. The 60-frame partial digests were recorded separately and were not compared with the 180-frame expected SHA.

## Evidence

All evidence: `results/validation/stage_q/q6_serial_performance_v1/`

- `q6_serial_summary.json`
- `pair1_evaluation.json`, `pair2_evaluation.json`, `pair3_evaluation.json`
- six Result JSON files, six trace JSONL files, six hash files, and six sidecars
- `environment_pre_*.txt`, `environment_after_*.txt`, `environment_post.txt`
- `artifact_sha256.txt`, `source_sha256.txt`, `thermal_throttle_status.txt`

## Scope Check

Serial only. No Pipeline, queue adjustment, batch change, dynamic shape, INT8 rebuild, model/dataset/threshold change, GPU preprocessing, GPU NMS, or Q7 execution was performed. Relevant serial, hash, and frame-trace tests passed; `git diff --check` passed.

## Authorization

Q6: `Q6_SERIAL_PERFORMANCE_EVIDENCE_VALID`

Q7: `NOT AUTHORIZED UNTIL REVIEW`
