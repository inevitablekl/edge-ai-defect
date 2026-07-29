# K1-R4 Dynamic Linker Cache Refresh

## Verdict

```text
K1 PASS
D062 READY
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
treat `--version` as a model-independent exit path. This is retained as a
`non-blocking CLI behavior limitation`; TensorRT Runtime validation supersedes
the version-command exit status for K1 platform acceptance.

No package operation, loader configuration edit, symlink, library copy,
Engine build, ONNX parsing, production code change, or power/clock change was
performed. D062 is ready but was not executed or accepted; K2 remains
unauthorized.
