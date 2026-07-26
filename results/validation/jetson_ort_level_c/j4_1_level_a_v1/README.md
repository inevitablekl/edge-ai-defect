# J4.1 Level A Correctness

Verdict: **PASS**.

This Published Evidence records the formal Stage J controlled Level A
Preprocessor validation from two independent processes. Both processes used
the same Release AArch64 wrapper, frozen eight-case manifest/data, process
affinity to control CPU 5, and `env -u LD_LIBRARY_PATH`.

Both runs returned exit code 0, passed all 8/8 cases, and produced
byte-identical reports. Exact and resize tolerance gates, metadata, tensor
shape/dtype/layout, element count, and finite-value checks all passed.

The historical Level A validator and five historical guards passed unchanged.
No model loading, ORT inference, postprocess validation, benchmark, latency or
FPS campaign, TensorRT, CUDA EP, ROS2, camera, Pipeline, Level B or Level C
operation was performed.
