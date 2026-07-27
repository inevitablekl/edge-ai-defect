# K1 Platform Acceptance Evidence

## Purpose

This is the non-overwriting `k1_environment_v1` attempt for Stage K K1 — Jetson TensorRT Platform Acceptance. It verifies the frozen Jetson platform contract, CUDA/TensorRT runtime discovery, `trtexec` help/version availability, telemetry sampling, and the authorized host-only `g++` CUDA + TensorRT runtime smoke.

## Scope and starting point

- Branch: `feature/jetson-tensorrt-fp16`
- Starting commit: `865b3c0060a7c6ae5aea05b9f52bf79c4c344c59` (K0 freeze)
- Device: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super
- Architecture: `aarch64`
- Observed Jetson Linux: L4T `R36.5.0`
- Target/contract JetPack: `6.2.2`; the `nvidia-jetpack` meta-package was not installed, so this correlation is disclosed in the evidence.

## Verdict

**K1 BLOCKED**

The mandatory host-only smoke could not link with ordinary `g++ -lnvinfer`. `libnvinfer.so.10.3.0` declares `libnvdla_compiler.so` as a required dependency, but no such library was present in the searched system paths or package database. The compiler therefore stopped before an executable could be produced; CUDA calls and TensorRT Runtime creation were not run.

The observed CUDA headers, `libcudart`, TensorRT headers, TensorRT libraries, `trtexec`, and `tegrastats` facts are retained for diagnosis. No package was installed or upgraded, and no system configuration was changed.

## Mandatory checks

The complete check matrix is in `verification_result.json`. The blocking facts are in `smoke_compile_stderr.log` and `smoke_ldd.log`.

## Non-blocking limitations

- `nvcc` is not in shell `PATH`; `/usr/local/cuda/bin/nvcc` is present and runs. K1 does not use nvcc.
- `jetson_release` is unavailable.
- Non-interactive sudo is unavailable; `nvpmodel -q` still reported `MAXN_SUPER`, while `jetson_clocks --show` reported that root is required without changing state.
- `trtexec --version` prints TensorRT `v100300` but returns 1 because this build also reports “Model missing”; `--help` returns 0 and is complete.
- The tegrastats sample exposes RAM, CPU utilization/frequency, GPU utilization, temperatures, and power rails. EMC was not present in the sample and is recorded as optional/unavailable.
- `NvInferPlugin.h` and `libnvinfer_plugin.so` are present; plugins were not initialized or invoked.

## Explicit non-actions

No TensorRT Engine was built, no ONNX was read or parsed, no production C++/CMake/header/source/test file was modified, D062 was not appended, K2/K3/Stage P work was not started, and nothing was pushed, merged, or tagged.
