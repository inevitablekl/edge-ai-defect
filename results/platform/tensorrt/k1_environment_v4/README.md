# K1-R4 Dynamic Linker Cache Refresh

## Verdict

```text
K1 BLOCKED
D062 NOT_AUTHORIZED
```

The user completed the one authorized system-maintenance action,
`sudo ldconfig`. No sudo command was executed again by Codex. The refreshed
cache now contains `libnvdla_compiler.so` at
`/usr/lib/aarch64-linux-gnu/nvidia/libnvdla_compiler.so`.

`libnvinfer.so.10` and the host-only smoke binary now have complete dynamic
dependencies. The unchanged smoke source compiled and ran successfully:
CUDA Runtime/Driver queries, one CUDA device, device properties, stream
creation/destruction, and TensorRT Runtime creation/cleanup all passed.

`trtexec --help` returned `0` and `ldd` was clean. The requested
`trtexec --version` invocation printed TensorRT `v100300` but returned `1`
with `Model missing or format not recognized`, because this build does not
treat `--version` as a model-independent exit path. Under the K1 mandatory
version/help gate this remains a failure, so K1 is not accepted and D062/K2
remain unauthorized.

No package operation, loader configuration edit, symlink, library copy,
Engine build, ONNX parsing, production code change, or power/clock change was
performed.
