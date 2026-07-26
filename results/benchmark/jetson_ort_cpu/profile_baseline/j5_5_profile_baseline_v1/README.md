# J5.5 CPU Profile Benchmark Baseline

Status: COMPLETE

Only the frozen Controlled profile `k1` was executed. Tuned `k5` was not executed and remains reserved for J5.6.

Protocol: 60-frame pilot; 60 warmup frames plus 500 measured frames (560 processed frames total); five independent processes; every formal process exceeded 30 seconds. The reported latency metric is process-wall time for the complete 560-frame invocation because the frozen schema-v2 benchmark configuration does not enable per-frame timing fields.

All five processes used CPU affinity 5, ONNX Runtime CPUExecutionProvider, sequential execution, graph optimization `all`, intra-op 1, inter-op 1, spinning enabled, CPU arena enabled, memory pattern enabled, and OpenCV threads 1.

No model, corpus, profile, ORT configuration, source code, or DECISIONS.md was modified. No push was performed. J5.6, TensorRT, CUDA EP, pipeline, ROS2, camera, and stability testing were not executed.
