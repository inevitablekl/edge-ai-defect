Stage K6 TensorRT FP16 Stability Validation v1

Verdict: K6_STABILITY_PASS

1. Engine identity

- Engine: Original TensorRT FP16 Engine
- Engine path: /home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine
- Engine SHA256: 6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc
- Manifest path: /home/orin/edge-ai/edge-ai-defect/models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json
- Manifest SHA256: 39caa8df46b23210e836d88132696dce055f86fe95b8ba4aa7d46ba40f982d63
- Split manifest SHA256: fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8

2. Environment

- TensorRT (manifest): 10.3.0.30
- CUDA runtime (manifest): 12.6.68
- JetPack/L4T (manifest): R36.5.0
- Jetson model (manifest): NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super
- Observed environment details: environment.json

3. Test protocol

- Frozen test split: 180 images
- Repeat inference for target duration: 30 minutes
- Runtime: single serial inference process at a time, single-thread OpenCV policy, batch=1
- Input: fixed local test split via hard links; no dataset files are copied to evidence
- Monitoring: tegrastats at 1 second; raw log is tegrastats.log

4. Runtime result

- Total frames: 84420
- Success count: 84420
- Failure count: 0
- Runner crashes: 0
- Runtime duration seconds: 1802.819
- Success rate: 100.000000%

5. Latency statistics

- Inference: latency_summary.json (`mean`, `median`, `p95`, `max`)
- E2E: latency_summary.json (`mean`, `median`, `p95`, `max`)
- Per-inference records: inference_records.jsonl
- Growth check: continuous growth means all ten equal-count window means strictly increase; see latency_summary.json.

6. tegrastats summary

- Samples: 1791
- Summary: system_monitor_summary.json

7. Verdict

The machine-readable verdict is K6_STABILITY_PASS. Verification checks are in verification_report.json.
No Engine, ONNX, ModelContract, RuntimeConfig, comparator tolerance, K5 evidence, watchdog,
ROS2, camera streaming, multi-thread pipeline, or DeepStream component was modified by this task.
