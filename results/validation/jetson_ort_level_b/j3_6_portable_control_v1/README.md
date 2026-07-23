# J3.6 Portable control utilities

Status: PASS

Source commit: `94576b6fe81e2f853c30c41826d039d016e093b0`

`PortableControlSession` is a startup wrapper for RuntimeConfig v2. It loads
and validates configuration, creates the ORT options record, applies and
records the OpenCV thread policy, normalizes executable/config/model/evidence/
trace paths, and writes a deterministic control evidence record on request.

The formal attempt built the native aarch64 C++17 targets and passed the
existing `runtime_config` and `serial_runner` tests. No model was loaded and
no inference, benchmark, camera, TensorRT, CUDA or ROS2 operation was run.
