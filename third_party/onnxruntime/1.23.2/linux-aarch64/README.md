# ONNX Runtime 1.23.2 Jetson aarch64 CPU SDK

This is the Stage J Jetson aarch64 CPU-only SDK package for ONNX Runtime
1.23.2. It was copied from the formal J2.2 v2 SDK identified as
`j2.2-formal-v2/sdk`, using the `v1.23.2` source at commit
`a83fc4d58cb48eb68890dd689f94f28288cf2278`.

The `include/` and `lib/` payload is local-only because the binary and complete
header payload are not committed to Git. Restore those two directories from the
same formal SDK with a symlink-preserving directory copy. The tracked metadata
files describe and verify the payload:

- `BUILD_MANIFEST.json` records build, source, ELF, dependency and provenance facts.
- `HEADER_SHA256SUMS.txt` verifies every regular public header.
- `FILE_SHA256SUMS.txt` verifies regular SDK and metadata files.
- `LICENSE` and `THIRD_PARTY_NOTICES` are unchanged official source files.

From this SDK root, run `sha256sum -c HEADER_SHA256SUMS.txt` and
`sha256sum -c FILE_SHA256SUMS.txt` to verify the package.

The SDK is CPU-only and must not be described as a CUDA or TensorRT SDK. J2.4
runtime/RPATH smoke and J2.5 Evidence gate are not complete. This package does
not claim that upstream tests, the application, or inference have run, and it
does not claim that J2 is complete or J3 has started.
