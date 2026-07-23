# J2 Limitations

- Upstream ONNX Runtime tests were skipped by the formal build contract.
- J2 does not include model loading or inference.
- J2 does not include a complete project Jetson build.
- J2 does not include performance benchmarking.
- J2.0 and J2.1 are historical planning/feasibility records, not independent Published Evidence.
- J3.1 handles the complete project aarch64 build and CMake portability.
- J2 can claim only that the ONNX Runtime 1.23.2 aarch64 CPU SDK completed formal build, packaging, and an `LD_LIBRARY_PATH`-free runtime/RPATH smoke.
