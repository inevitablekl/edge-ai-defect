# J2.4 Published Evidence: j2_rpath_smoke_v1

This evidence records the Stage J J2.4 RPATH smoke for the formal ONNX Runtime
1.23.2 aarch64 CPU-only SDK. A minimal external consumer was configured and
built; it loaded the SDK without `LD_LIBRARY_PATH` and ran the existing runtime
smoke without loading a model or performing inference.

The evidence contains no binary, SDK payload, build directory, or private
absolute path. J2.5 remains pending and J3 has not started.

Verify the six non-manifest files with `sha256sum -c sha256sums.txt` from this
directory.
