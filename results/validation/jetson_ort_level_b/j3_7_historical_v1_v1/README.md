# J3.7 Historical v1 regression

Status: PASS

This is an evidence-only validation card. No source, CMake, test-name,
inventory, model contract, preprocess, postprocess or inference-engine file
was modified.

The existing `runtime_config` regression test accepted the historical v1 and
current v2 fixtures, rejected the v1 fixture with the v2-only `onnxruntime`
section, and preserved v1/v2 schema isolation. The v1 startup branch remains
the legacy path in `src/main.cpp`; the v2-only `PortableControlSession` does
not replace it.

No model was loaded and no inference, benchmark, TensorRT, CUDA, ROS2 or camera
operation was performed.
