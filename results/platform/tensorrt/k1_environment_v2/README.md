# Stage K1-R2 Package Repair and Platform Re-attempt

## Disposition

```text
K1 BLOCKED
D062 NOT_AUTHORIZED
```

Previous K1 v1 was blocked because `libnvdla_compiler.so` was absent. K1-R1
classified the cause as `C_ABSENT_MATCHING_PACKAGE_AVAILABLE`. This attempt
was authorized to install exactly:

```text
nvidia-l4t-dla-compiler=36.5.0-20260115194252
```

The first Codex invocation was not authenticated and has been preserved in
`package_install_stdout.log`, `package_install_stderr.log`, and
`package_install_exit_code.txt` with exit code `1`. The user then executed the
same exact authorized command manually. `/var/log/apt/history.log` records
only `nvidia-l4t-dla-compiler:arm64` at the authorized version, and dpkg
confirms it is installed.

The package installed the AArch64 ELF
`/usr/lib/aarch64-linux-gnu/nvidia/libnvdla_compiler.so` with SONAME
`libnvdla_compiler.so`. However, the dynamic linker still reports
`libnvdla_compiler.so => not found` for `libnvinfer.so.10` and the smoke
binary. Manual `ldconfig`, loader configuration changes, symlinks, and
library copying were prohibited, so K1 remains blocked.

The smoke source was copied unchanged from K1 v1 and compiled with the exact
ordinary `g++` contract. Compilation succeeded, but smoke-binary `ldd` and
execution failed because the same dependency remained unresolved. CUDA and
TensorRT discovery, `trtexec --help`, `trtexec` loader inspection, and a
bounded `tegrastats` sample were recorded. `trtexec --version` returned `1`
because this build treats the missing model as an error; no model or engine
operation was attempted.

No Engine build, ONNX parsing, D062 decision, K2 work, production source
change, power/clock change, loader repair, push, merge, tag, or Stage P work
was performed.
