# J2.3 Published Evidence: j2_sdk_v1

J2.3 SDK packaging and manifest evidence for the formal J2.2 v2 ONNX Runtime
1.23.2 aarch64 CPU-only SDK.

The evidence records static packaging, manifest, provenance, license, ELF,
dependency and privacy checks. The local SDK payload is intentionally excluded:
no shared objects or complete header payload are published here. The payload
can be restored from the formal v2 SDK identified in `provenance.json`.

The exact evidence files are `README.md`, `provenance.json`,
`verification_report.json`, `commands.txt`, and `sha256sums.txt`. Verify the
four evidence files with `sha256sum -c sha256sums.txt` from this directory.

J2.4 RPATH smoke and J2.5 Evidence gate remain pending. No binary execution,
runtime inference, CTest, benchmark, or J3 work is claimed by this evidence.
