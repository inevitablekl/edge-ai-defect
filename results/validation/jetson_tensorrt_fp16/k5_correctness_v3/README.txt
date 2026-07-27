Stage K K5.3 TensorRT Level B Correctness Evaluation

Attempt: k5_correctness_v3
Source commit: 38aac68b1e603bc10de290a6ee65c7164c5437c8
Engine: yolov8n_neudet_trt10.3_fp16_b1_640
Engine SHA256: 6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc
Reference Bundle SHA256: fed5755ce630d0902449f3052fcbb915592245583df19bf924ec867d1c1e1e29

The frozen TensorRT Engine produced 16/16 raw output tensors. All outputs
had the exact [1, 10, 8400] FP32 BCN contract and finite element counts.

The frozen `tensorrt_fp16` Level B policy comparison produced 1/16 PASS and
15/16 FAIL. The failure is retained without changing any tolerance:

- overall maximum MAE: 0.08525302849461636
- bbox maximum MAE: 0.2131305621777262
- bbox maximum Type-7 P99: 1.9310302734375
- bbox maximum absolute error: 23.29144287109375 (limit 4.0)
- score maximum absolute error: 0.021184921264648438 (limit 0.02)

Final result: TENSORRT_LEVEL_B_FAIL

TensorRT Level C, boundary investigation, benchmark, stability, Pipeline,
and K6 were not executed.
