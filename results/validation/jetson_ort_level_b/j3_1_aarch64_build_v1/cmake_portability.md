# CMake portability record

The original CMake logic assumed a flat ONNX Runtime include directory and
hardcoded the `linux-x64` example path.

J3.1 now selects a platform-aware example from `CMAKE_SYSTEM_PROCESSOR`:
`linux-aarch64` for aarch64/arm64, `linux-x64` for x86_64/AMD64, and a
processor-derived fallback for other systems.

Header detection checks the flat layout first and the nested layout second.
Each candidate directory must contain both C++ and C API headers. The imported
target remains `onnxruntime::onnxruntime`, uses the SDK `lib/libonnxruntime.so`,
and retains the SDK library RUNPATH. No production C++ include statements or
runtime/model semantics changed.

The Jetson validation selected the nested aarch64 layout and the
`include/onnxruntime` directory. Flat-layout support is retained but x86
runtime regression is deferred to J3.7.
