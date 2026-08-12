# Paper Phase 5.6 Level-B Evidence Addendum v1.0

## 1. Authority Model

Level A is the unchanged formal E2E benchmark authority. Level B is deterministic evidence derived from frozen predictions, raw benchmark records, code, workload manifests, and provenance. Every Level-B item records `alters_level_a_authority = false`.

## 2. V3R Task-Level Correctness

V3R Precision `0.6912751677852349`, Recall `0.6990950226244343`, mAP50 `0.647625463793534`, and mAP50-95 `0.3523443910494967` were produced by deterministic execution of the governed evaluator over the frozen prediction artifact.

| Class | AP50 | Recall |
|---|---:|---:|
| crazing | 0.2037064778274966 | 0.3108108108108108 |
| inclusion | 0.6287516497993013 | 0.7079646017699115 |
| patches | 0.8462547740623322 | 0.8625 |
| pitted_surface | 0.769864959184994 | 0.8181818181818182 |
| rolled-in_scale | 0.563851931912887 | 0.6666666666666666 |
| scratches | 0.8733229899741927 | 0.8955223880597015 |

All maximum absolute V3R class AP50/Recall differences versus both V0 and V2R are exact zero. This is not new inference, a new benchmark, a second selection gate, or a new Gate D.

## 3. Nominal Input-Copy Payload

V0 is 4,915,200 B (4.9152 decimal MB) and V2R/V3R are 120,000 B (0.1200 decimal MB), giving a 40.96× nominal input-copy payload ratio. For V2R/V3R the effective `cudaMemcpy2DAsync` width is 600 B and height is 200. This is not measured bus traffic or a transfer/E2E acceleration factor.

## 4. Five-Run Evidence

The source CSV contains 15 independent accepted processes, five per variant, with 1,080 measured samples per process. Formal tail percentiles pool 5,400 samples per variant; process percentiles remain run-level descriptors. Runs are not paired or matched, and no inferential statistics were performed.

## 5. Runtime-State Provenance

Recorded facts are the Jetson platform, MAXN_SUPER/mode 2, no invoked clock-setting command, no independently archived clock-frequency evidence, and non-continuous pre/post temperature observations. Fixed clocks, no throttling, fixed fan speed, continuous thermal stability, and stable power are not proven.

## 6. Calibration Provenance

Formal calibration consumed 1,260 deduplicated train images and excluded the test split. It used `IInt8EntropyCalibrator2`, batch 1, 640×640, production-equivalent `production_Preprocessor:BGR-LetterBox640-RGB-NCHW-FP32/255`, INT8+FP16 builder flags, TensorRT 10.3, and FP32 I/O. Cache mode was force-miss; all 1,260 batches ran; the cache was generated afterward and archived; no pre-existing cache was reused as formal-build input. The Engine is a TensorRT INT8 mixed-precision Engine.

## 7. Publication Precision

Exact authority values map to `2.24×`, `55.45%`, `+4.07%`, `-4.03%`, `+0.15%`, and `-0.12%`. Exact and display precision are separate layers. Absolute FPS and latency candidates use three decimals.

## 8. Scientific Boundaries

The 40.96× ratio is not measured traffic/bandwidth/H2D time and cannot alone explain E2E speedup. V3R metrics are frozen-prediction analysis. Runs are independent, not paired. Tail is `MIXED`; there is no consistent tail-latency improvement evidence. Temperature observations are not continuous telemetry. Calibration claims are limited to direct repository provenance.

## 9. Scientific Change Control History

D-01 is closed by adopting precise forced-cache-miss wording. The historical discrepancy report is retained unchanged as governance history. The resolution is a wording correction, not experiment invalidation or scope change.

## 10. Source / SHA Manifest

`phase56b_evidence_manifest.json` maps each claim to frozen sources, deterministic transformation, tool, output SHA, and the explicit statement that Level A is not altered. `phase56b_sha256.txt` is the artifact checksum list.
