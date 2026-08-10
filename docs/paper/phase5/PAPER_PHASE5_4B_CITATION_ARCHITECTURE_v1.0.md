# Paper Phase 5.4B Citation Architecture v1.0

## 1. Scope and counts

- Starting bibliography library: `15` entries, `14` cited and rendered.
- Final bibliography library: `27` entries, `26` cited and rendered.
- New entries: `13` (`10` core and `3` supporting).
- Removed existing entry: `1`.
- Metadata upgrade: `1` logical source, retained under its existing citation key.
- Unused admitted entry: `reddi_et_al_2022_mlperf_mobile`, retained but not cited or rendered under the existing Phase 3 decision.

The architecture supports a theory-guided deployment/data-path optimization paper. It does not convert the manuscript into an improved-YOLO survey, quantization paper, or literature review.

## 2. Existing-source decisions

| Existing source | Decision | Citation role or reason |
|---|---|---|
| `song_yan_2013_neu_surface_defects` | RETAIN | NEU surface-defect data background. |
| `ultralytics_2023_yolov8_docs` | RETAIN | Official YOLOv8 model identity. |
| `shao_et_al_2024_td_net` | RETAIN | Representative algorithm-side lightweight defect detector. |
| `weiss_et_al_2024_realtime_component_inspection` | RETAIN | Industrial real-time inspection motivation. |
| `kim_lee_kim_2024_hyq` | RETAIN | Existing PTQ background, reused with primary quantization sources. |
| `tang_qian_2024_yolov8_jetson_orin` | RETAIN | Jetson deployment-stage framing. |
| `shin_kim_2022_jetson_yolo_frameworks` | RETAIN | Jetson framework/platform comparability boundary. |
| CUDA Programming Guide | RETAIN | CUDA API, stream and synchronization semantics. |
| CUDA Best Practices Guide | RETAIN | Pinned-memory guidance and resource boundary. |
| TensorRT 10.3 Release Notes | RETAIN | Historical INT8/calibrator interface status. |
| JetPack 6.2.2 | RETAIN | Official platform-stack correspondence. |
| `lema_et_al_2025_surface_defect_benchmark` | RETAIN | Reproducible surface-defect benchmark boundary. |
| `reddi_et_al_2019_mlperf_inference` | UPGRADE_METADATA | Same logical work upgraded from 2019 arXiv to ISCA 2020, pages 446–459, DOI `10.1109/ISCA45697.2020.00045`; key retained safely. |
| `reddi_et_al_2022_mlperf_mobile` | RETAIN_UNUSED | Prior admitted library source; no independent manuscript role beyond the formal MLPerf source. |
| `liu_zhang_ruan_2024_hfut_yolov5_embedded` | REMOVE | Its general embedded-YOLO role became redundant; target-journal provenance alone is not a valid citation reason. |

## 3. New-source decisions

| Key | Class | Distinct role | Decision |
|---|---|---|---|
| `lv_et_al_2020_metallic_defects` | CORE | Metallic-defect problem and NEU-DET evaluation background. | ADD |
| `stacker_et_al_2021_edge_runtime` | CORE | Edge deployment/runtime as a research object. | ADD |
| `kim_et_al_2025_concurrent_edge_detection` | CORE | Complete detection stages and runtime optimization without detector modification. | ADD |
| `lee_han_kim_2025_presto` | CORE | Preprocessing and data management as possible system-level constraints. | ADD |
| `hill_marty_2008_amdahl` | CORE | Generic optimization-coverage principle around T3 only. | ADD |
| `bateni_et_al_2020_integrated_memory` | CORE | Integrated CPU/GPU memory-policy dependence. | ADD |
| `rodriguez_et_al_2025_gpu_memory_allocation` | CORE | Allocation-policy workload/access dependence; no universal winner. | ADD |
| `jacob_et_al_2018_integer_inference` | CORE | Integer-inference motivation and accuracy/performance trade-off. | ADD |
| `nagel_et_al_2020_adaround` | CORE | PTQ perturbation and need for accuracy validation. | ADD |
| `dean_barroso_2013_tail_scale` | CORE | Mean versus tail/percentile rationale. | ADD |
| `chu_yu_rong_2024_strip_steel_yolov8` | SUPPORTING | Recent improved-YOLO strip-steel contrast. | ADD |
| `zhang_pang_jiang_2024_gdm_yolo` | SUPPORTING | Second recent architecture-changing YOLOv8 contrast with a distinct representative role. | ADD |
| `archet_et_al_2023_embedded_soc` | SUPPORTING | Embedded heterogeneous-SoC platform/configuration dependence. | ADD |

## 4. Dropped candidate sources

| Candidate | Decision | Reason |
|---|---|---|
| Clockwork | NOT_USED | Dean/Barroso plus MLPerf already close the tail/predictability prose; adding it would duplicate a datacenter-serving role. |
| “A Comparative Analysis of Modern Acceleration Frameworks” local PDF | DROP | SHA-256 `af2a0764...570745`; exact binary duplicate of the Kim concurrent-processing paper and title/contents mismatch. |
| “Benchmarking YOLOv8 Variants ... Jetson Orin NX” local PDF | DROP | Same SHA-256 and same mismatched Kim paper; no citation created from filename. |
| Duplicate Kim PDF copy | DROP_DUPLICATE | Same logical publication; only one bibliography record is retained. |
| Remaining downloaded defect papers and six HFUT benchmark papers | NOT_USED | No independent claim role was needed; download or target-journal origin is not admission evidence. |

## 5. Claim-to-citation map

| Claim ID | Manuscript location | Primary source | Secondary source | Wording boundary | Status |
|---|---|---|---|---|---|
| CN-01 | Introduction paragraphs 1–2 | Lv 2020; Song/Yan 2013 | Shao 2024; Chu 2024; GDM-YOLO 2024 | Representative landscape only; no exhaustive field claim and no runtime support. | CLOSED |
| CN-02 | Introduction paragraph 3; §1.2 | Stäcker 2021; Kim 2025 | Shin/Kim 2022; Tang/Qian 2024 | Deployment remains a system variable; no claim that deployment always dominates inference. | CLOSED |
| CN-03 | Introduction paragraph 3; §1.2–1.3; §4.2 | PRESTO 2025 | Stäcker 2021 | Other AI workloads establish possibility, not Jetson-YOLO dominance or the cause of `55.4519%`. | CLOSED |
| CN-04 | §1.3 immediately before T3 | Hill/Marty 2008 | — | No alpha estimate/order, fit, or speedup prediction. | CLOSED |
| CN-05 | §1.2; §2.3; §4.3 | Bateni 2020 | CUDA Best Practices | Host-Pinned policy is not identical to V3R staging and does not predict V3R gain. | CLOSED |
| CN-06 | §1.2; §2.3; §4.3 | Rodriguez 2025 | Archet 2023 | Zero-Copy/allocation studies are not V3R; only workload-dependence is transferred. | CLOSED |
| CN-07 | §1.4; §3.1; §3.3 | MLPerf Inference, ISCA 2020 | Lema 2025 | Methodological principles only; no MLPerf compliance claim. | CLOSED |
| CN-08 | §1.4; §3.3; §4.4 | Dean/Barroso 2013 | MLPerf Inference | Tail rationale only; datacenter causal mechanisms are not transferred to Jetson replay. | CLOSED |
| CN-09 | Introduction paragraph 4; §1.1 | Jacob 2018; Nagel 2020 | HyQ 2024; TensorRT release notes | Accuracy validation is required; neither AdaRound nor Jacob's training method was used by the project. | CLOSED |

## 6. Section citation architecture

### 6.1 Introduction

`12` distinct references. The order is: industrial problem and NEU background; three representative algorithm-side papers; official YOLOv8 identity; edge runtime; preprocessing systems; industrial inspection; PTQ correctness; TensorRT version boundary. MLPerf, memory-policy and detailed Jetson-framework sources are deferred to the sections whose claims they directly support.

### 6.2 Theory and problem definition

`18` distinct references across four subsections. They are distributed across different roles rather than dumped on one claim: platform/model identity in §1.1; deployment and memory evidence in §1.2; system-stage framing and Hill/Marty directly around T1/T3 in §1.3; tail and benchmark methodology in §1.4. T1 and T2 remain project conceptual abstractions, not literature-derived fitted models.

### 6.3 Method

`5` distinct references. Official CUDA guidance defines semantics; Bateni, Rodriguez and Archet bound the claim that pinned staging is a controlled variable rather than a guaranteed optimization. Host-Pinned, Zero-Copy and V3R are explicitly kept separate.

### 6.4 Experiment methodology

`4` distinct references. Shin/Kim bounds cross-platform comparison; formal MLPerf supports explicit workload/quality/metric boundaries; Lema supports reproducibility caution for defect benchmarks; Dean/Barroso supports P95/P99 as complementary tail indicators.

### 6.5 Results and discussion

`4` distinct references. PRESTO is placed after the project's V0→V2R observation; Bateni/Rodriguez are placed after the V2R→V3R observation; Dean/Barroso is used only for the general mean-versus-tail principle. No citation is attached so that it appears to source a project number.

## 7. Cross-platform extrapolation boundaries

- PRESTO: cloud/video AI inference evidence; it does not prove Jetson YOLO preprocessing dominance or assign the `2.236671×`/`55.4519%` result.
- Bateni: integrated-platform memory-policy context; its Host-Pinned configuration is not V3R.
- Rodriguez: allocation-strategy dependence; its Zero-Copy configuration is not V3R.
- Dean/Barroso: tail-metric rationale only; no datacenter queuing mechanism is used as a causal explanation.
- Jacob/Nagel: quantization correctness rationale only; neither method is claimed as the TensorRT calibration mechanism.
- Archet: platform/configuration dependence only; no power result is transferred and this project still reports no power measurement.

## 8. Remaining citation gaps

`NONE` within Phase 5.4B scope. Title/abstract/conclusion reconciliation remains Phase 5.4D work, not a citation gap.
