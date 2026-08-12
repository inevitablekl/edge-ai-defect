# Paper Phase 5.6B Controlled Evidence Promotion Report

## Verdict

`PHASE56_DERIVED_EVIDENCE_FROZEN`

## Scope and authority

This evidence-only work unit performed deterministic reanalysis without new inference, benchmark, timing, telemetry, or power runs. Existing Level-A E2E authority and provenance are unchanged. The outputs in this directory are Level-B derived evidence.

## D-01 resolution

`D-01 = CLOSED`. Scientific Change Control adopted the precise wording: `calibration cache generated and archived after forced cache miss; not reused as formal-build input`. The unqualified candidate wording was retired. This is a provenance-wording correction, not experiment invalidation.

## V3R correctness

The governed wrapper `tools/validation/stage_r_v2_task_accuracy.py` reuses `tools/validation/evaluate_stage_k_task_metrics.py`. Frozen prediction SHA256: `3e04478c181a697ccffbf63f5405ab8eecfce61a8fe2db885b2ce81045514678`; 180 images; 447 detections.

| Precision | Recall | mAP50 | mAP50-95 |
|---:|---:|---:|---:|
| 0.6912751677852349 | 0.6990950226244343 | 0.647625463793534 | 0.3523443910494967 |

All four maximum absolute class AP50/Recall differences versus V0/V2R are exact zero. This is new deterministic analysis of frozen predictions, not new inference, a second parameter-selection gate, or a new Gate D. Under this frozen workload and governed protocol, the three paths have identical reported task and class AP50/Recall values; no universal or future-input equivalence is claimed.

## Nominal input-copy payload

- V0: `1 × 3 × 640 × 640 × 4 = 4,915,200 B = 4.9152 MB/frame`.
- V2R/V3R: `600 copy-width bytes × 200 rows = 120,000 B = 0.1200 MB/frame`.
- Ratio: `4,915,200 / 120,000 = 40.96×`.

This is derived from frozen workload geometry and implementation copy semantics. It is not measured bus/DRAM/PCIe traffic, bandwidth, H2D duration, transfer acceleration, or an E2E causal factor.

## Five-run evidence

Each row is an independent accepted process. Similar run identifiers do not imply pairing.

| Variant | Run | Order | FPS | Mean ms | Process P95 ms | Process P99 ms |
|---|---|---:|---:|---:|---:|---:|
| V0 | set_01_p01_v0 | 1 | 54.483647 | 18.312398 | 18.827171 | 19.078366 |
| V2R | set_01_p02_v2r | 2 | 122.395437 | 8.122075 | 9.830715 | 11.454000 |
| V3R | set_01_p03_v3r | 3 | 128.063790 | 7.754151 | 9.791978 | 11.767867 |
| V3R | set_02_p01_v3r | 4 | 125.595420 | 7.893921 | 9.684053 | 10.665399 |
| V2R | set_02_p02_v2r | 5 | 122.001616 | 8.148400 | 9.818336 | 11.629180 |
| V0 | set_02_p03_v0 | 6 | 54.846229 | 18.191605 | 18.761105 | 19.064099 |
| V2R | set_03_p01_v2r | 7 | 121.443228 | 8.185215 | 9.857622 | 11.553727 |
| V0 | set_03_p02_v0 | 8 | 54.288995 | 18.377309 | 18.910193 | 19.102413 |
| V3R | set_03_p03_v3r | 9 | 128.301034 | 7.739958 | 9.866199 | 11.471802 |
| V0 | set_04_p01_v0 | 10 | 54.612029 | 18.268237 | 18.840152 | 19.029209 |
| V3R | set_04_p02_v3r | 11 | 125.845563 | 7.892667 | 9.984501 | 11.500614 |
| V2R | set_04_p03_v2r | 12 | 122.011910 | 8.147580 | 9.849646 | 11.494716 |
| V2R | set_05_p01_v2r | 13 | 122.758770 | 8.098124 | 9.767627 | 11.506529 |
| V3R | set_05_p02_v3r | 14 | 127.680486 | 7.778446 | 9.846982 | 11.520883 |
| V0 | set_05_p03_v0 | 15 | 54.768981 | 18.215410 | 18.850611 | 19.054798 |

There are five processes and 5,400 samples per variant, 16,200 total. Formal P95/P99 are pooled variant-level percentiles, not the mean of process percentiles. No paired differences, p-values, confidence intervals, or significance tests were produced.

## Level-A reconciliation and tail

Verification reproduced `2.236671×`, `55.4519%`, `+4.0738%`, `-4.0349%`, `+0.1514%`, and `-0.1184%` at authority precision. Tail remains `MIXED`: P95 and P99 relative changes are both below 0.2% and have opposite directions.

## Runtime state

Provenance supports the named Jetson platform, MAXN_SUPER/mode 2, no invoked clock-setting command, absent independently archived clock-frequency evidence, approximate pre/post observations of 46.8–47.1 °C and 48.7–49.6 °C, and non-continuous temperature observation. It does not prove fixed frequencies, no throttling, fixed fan speed, continuous thermal stability, or stable power.

## Calibration

The frozen facts are 1,260 deduplicated training images with test exclusion, `IInt8EntropyCalibrator2`, batch 1, 640×640, production-equivalent CPU `Preprocessor` identity `BGR-LetterBox640-RGB-NCHW-FP32/255`, INT8+FP16 flags, TensorRT 10.3, and FP32 host I/O. The safe term is `TensorRT INT8 mixed-precision Engine`; pure/all-INT8 terminology is unsupported. Calibration uses the production CPU Preprocessor identity; this does not claim that it uses the V2R/V3R CUDA implementation.

## Publication precision

Authority precision is retained in machine-readable evidence. Display mapping is `2.24×`, `55.45%`, `+4.07%`, `-4.03%`, `+0.15%`, `-0.12%`; candidate absolute precision is three decimals for FPS and latency. No manuscript was modified.

## Outputs and mutation boundary

Machine-readable sources, the Level-B addendum, manifest, and SHA list are colocated here. Level A, manuscript sources, DOCX, PDF, figures, tables, styles, equations, captions, bibliography, and journal templates were not modified.
