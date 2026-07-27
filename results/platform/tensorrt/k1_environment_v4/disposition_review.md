# K1 Disposition Review

## Decision

```text
K1 PASS
D062 READY
```

The original raw `trtexec --version` output and exit code remain unchanged in
`trtexec_version.txt` and `trtexec_exit_codes.txt`. The invocation printed
`TensorRT v100300`, then reported `Model missing or format not recognized`
and returned exit code `1` because this build does not provide a
model-independent version-only execution path for the requested invocation.

This is classified as:

```text
non-blocking CLI behavior limitation
```

The limitation does not invalidate platform acceptance: `trtexec --help`
returned `0` with the required option semantics, `ldd trtexec` passed, and the
host-only smoke independently validated the actual TensorRT Runtime version,
creation/cleanup, CUDA Runtime/Driver, device and stream lifecycle.

TensorRT Runtime validation supersedes the `trtexec --version` command exit
status for K1 platform acceptance. No Engine build, ONNX parsing, D062
execution, or K2 action was performed.
