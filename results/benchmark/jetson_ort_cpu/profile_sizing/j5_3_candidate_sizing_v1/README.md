# Stage J J5.3 Candidate Sizing v1

Status: PASS. This is candidate sizing only, not a formal performance baseline.

The frozen candidates are k1, k2, k4, k5, and k6. Each has two independent application processes, and each process loaded an ONNX Runtime CPU session and processed the frozen 20-image corpus. The published raw output SHA256 for every run equals the J5.2 expected cycle SHA for its profile.

`cycle_total_ms` is the measured process-invocation wall interval. Under the frozen v2 RuntimeConfig application, stage timing fields are not exposed; `inference_ms`, `preprocess_ms`, and `postprocess_ms` are therefore recorded as unavailable and are not inferred from cycle time.

Telemetry contains raw before/during/after tegrastats captures and `/proc/self/status` VmRSS samples. EMC was not reported in the observed tegrastats lines. The `jetson_clocks --show` state was not observed because the command required root; no device state was changed.

The published tree contains no images, hostname, IP address, credentials, or user paths.
