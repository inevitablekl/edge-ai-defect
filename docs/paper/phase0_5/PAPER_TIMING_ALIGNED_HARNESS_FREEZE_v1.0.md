# Paper Timing-Aligned Harness Freeze v1.0

## 1. Verdict

`HARNESS_READY_FOR_FORMAL_RUN`

The dedicated V0/V2R/V3R harness, configuration identity checks, shared
external timing boundary, schema checks, and three short preflights passed.

Formal 15-run benchmark:
`NOT RUN`

Preflight metrics:
`NOT FORMAL PERFORMANCE EVIDENCE`

Phase 0.5D-I2:
`NOT AUTHORIZED BY THIS FILE`

## 2. Frozen Git and Binary Identity

The preflight started from clean `main` at
`961669fae539968daf9900b31b5d3eac0d27bf27`. The preflight executable was
built from the corresponding working-tree source and had SHA-256
`6b74ffa4564606181f35e2083490bf60565beb4df3a9cd651fe1fc41de0de6f0`.

The post-test rebuild used for freeze handoff has executable SHA-256
`c02af9954075635163f3f30cbd5bdef9b50e387466156890ab0a681098712c50` and
config-validator SHA-256
`e7e85780992b3fc4f9e3b1cf11f43b70ba7ee7c056ca92af635729a622cee661`.

No model, ONNX, TensorRT Engine, calibration, CUDA preprocessing, postprocess,
or historical result artifact was modified.

## 3. Formal Variant Set

Only `V0`, `V2R`, and `V3R` are accepted. V0 dispatches to the existing
CPU/OpenCV HostTensor path. V2R and V3R dispatch to the existing production
pageable/pinned runners with
`ResizeSemantic::kOpenCv454AlignedFixedContract`. V1, historical V2/V3, V4,
V5, Pipeline, zero-copy, and double buffering are rejected or out of scope.

## 4. Timing Boundary

The one harness boundary starts immediately before
`TimingSource::inner_.next()` at runner source line 217 and is sampled in the
shared `FanoutSink::write_frame()` before `JsonSink::write_frame()` at line
257. It includes source pull/decode, staging, H2D, CUDA preprocessing,
TensorRT synchronization, D2H, postprocess, and frame-result construction. It
excludes JSON serialization, file writing, digest finalization, and summary
persistence. No internal timing object or CUDA-event timing is enabled.

## 5. Configuration Equality

All three configs use schema v6, TensorRT INT8, batch 1, input 640,
confidence 0.25, IoU 0.45, max NMS 30000, max detections 300, agnostic false,
multi-label false, warmup 60, measured 1080, OpenCV threads 1, and
`timing.enabled=false` / `profiling.mode=off`. Machine-readable comparison
found no hidden differences; only `data_path.variant` differs.

Config hashes and parsed identity are in
`docs/paper/phase0_5/evidence/timing_aligned_harness_preflight_v1/`.

## 6. Schema and Field Equality

All three preflight results are Result schema v4 with identical top-level
fields and per-frame fields:
`sequence_index`, `relative_path`, `width`, `height`, `detections`.
No `timing_ms` or other internal timing field is present. The shared JSON sink,
serialization identity, and canonical detection hash sink are used for all
variants.

## 7. Schedule Identity

The frozen five-set schedule contains 15 positions, with each variant appearing
once in every set and five times overall. Schedule SHA-256:
`bd3818db70dc552a8f06bfc875a7a990418f0b6672d9a43482871d35bdb5dcd7`.
The schedule was not executed in I1.

## 8. Build Results

External build directory:
`/home/orin/edge-ai-local-build/paper_phase0_5d_i1/`

Configure passed with CUDA 12.6 compiler discovery, TensorRT enabled, and
Stage R CUDA preprocessing enabled. The dedicated runner and config validator
built successfully. Focused existing tests passed: runtime config, result
sinks, serial runner, Stage R runtime, and Stage R CUDA preprocessing.

## 9. Runtime Preflight Results

Each variant ran exactly 3 warmup and 16 measured frames in
`PREFLIGHT_ONLY` mode. All returned 0, processed 16 frames, dropped 0, reached
EOS, produced 16 finite external latency samples, and recorded complete
identity metadata. V0, V2R, and V3R produced the same preflight detection SHA
`3872f9c25c78b42a56c6c821b6acba33747fcecd56280e5d7af2042ea3d6f59a`.

These observations are preflight checks only and are not formal performance
evidence or a performance ranking.

## 10. CPU Measurement Disposition

CPU equivalent cores use the same `CLOCK_PROCESS_CPUTIME_ID` measurement over
the measured process-wall window for every variant. The values are retained
only in external preflight raw output and are not used for a paper conclusion.

## 11. Environment Readiness

The capability snapshot recorded board identity, aarch64, L4T 36.5, CUDA
12.6, TensorRT 10.3, OpenCV 4.5.4, MAXN_SUPER mode 2, CPU affinity 0-5,
OpenCV threads 1, zram/swap, temperatures, fan state, background load, and
per-run start/end markers. JetPack was not independently exposed by the
available command and remains an explicit environment-record gap; no value was
invented. No new thermal threshold was selected.

## 12. Historical Evidence Preservation

The historical Attempt 2 result root remained untouched. New raw preflight
output is outside the repository at
`/home/orin/edge-ai-local-evidence/stage_r/phase0_5d_harness_preflight_v1/`.
Earlier setup failures are preserved under sibling `*_failed_setup` roots.

## 13. Formal Run Authorization State

`HARNESS_READY_FOR_FORMAL_RUN` means the harness is ready for a later explicit
project-manager-authorized formal run. It does not authorize I2, the 15-process
schedule, Gate D rerun, or paper performance aggregation.

## 14. Recommended Next Actor

`Paper Project Manager`
