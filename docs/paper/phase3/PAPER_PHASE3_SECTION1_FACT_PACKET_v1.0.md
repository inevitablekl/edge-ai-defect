# Section 1 Fact Packet

Deterministic evidence packet only; not manuscript prose. Facts are extracted
from frozen Phase 0.5, Phase 1, Phase 2, and Stage Q authority files.

## 1. Section Contract

- Title: `系统对象与问题定义`
- Subsections: `1.1`, `1.2`, `1.3`
- Research question: “Under the frozen Jetson platform, INT8 Engine,
  industrial defect detection model, replay workload, correctness contract,
  and common timing boundary, how do CPU preprocessing, CUDA preprocessing
  with pageable host staging, and CUDA preprocessing with pinned host staging
  affect frame rate, mean latency, and tail latency?”
- Claims: `C1; C4; C8`; background `C5-C7`; guardrail `C9`.

## 2. Deployment Object Facts

| ID | Fact | Authority | Status |
|---|---|---|---|
| F01 | Device: Jetson Orin Nano Super | `docs/personal/STAGE_Q_FINAL_REPORT.md` §2 | FROZEN |
| F02 | Jetson variant: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super | `PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md` §3 Board | FROZEN |
| F03 | L4T R36.5 | `PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md` §3 L4T | FROZEN |
| F04 | CUDA 12.6.11 / runtime 12.6.68 | same §3 CUDA row | FROZEN |
| F05 | TensorRT 10.3.0.30 | same §3 TensorRT row | FROZEN |
| F06 | OpenCV 4.5.4 | same §3 OpenCV row | FROZEN |
| F07 | Frozen YOLOv8n ONNX; ONNX SHA256 `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944`; model-contract SHA256 `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190` | Phase 1 experiment matrix; timing manifest identity | FROZEN |
| F08 | Input 640 × 640; batch 1 | Phase 1 `R_V0`, `R_V2R`, `R_V3R` rows | FROZEN |
| F09 | TensorRT INT8 + FP16 mixed precision; Engine SHA256 `8d96eabd182df392db08bb0f15e1c9ffc9941276965090b0cdebfb4e8c25a8ee` | Stage Q §4; timing manifest identity | FROZEN |
| F10 | split-v2 NEU-DET test replay; test-manifest SHA256 `ea7616df7d59a8389c2afff4ba50cf43a6a5f683860f67e68a8d79d57101b194` | Stage Q Dataset Contract; timing manifest | FROZEN |
| F11 | Test workload: 180 images; Stage Q task evaluation has 442 ground-truth boxes | Stage Q §5 | FROZEN |
| F12 | Clock state, instantaneous power, and unrecorded hardware mode are not Section 1 facts | Phase 0.5D §10 limitations | GUARDRAIL |

The ONNX artifact SHA and frozen model-contract SHA are retained as distinct
authority fields.

## 3. Dataset and Model Disclosure

| ID | Fact | Authority | Status |
|---|---|---|---|
| D01 | Historical split-v1 train/val/test = `1260/360/180` | `M_TRAIN_SPLIT_V1_COUNTS`; split-sensitivity report | HISTORICAL |
| D02 | One train/validation image-content duplicate existed; 1800 files represented 1799 unique image contents | split-sensitivity report §2 | FROZEN |
| D03 | Current split-v2-deduplicated train/val/test = `1260/359/180`; test membership unchanged | `M_TRAIN_SPLIT_V2_COUNTS`; Stage Q §3 | FROZEN |
| D04 | Duplicate validation entry removed; no retraining, re-freeze, ONNX export, or Engine rebuild required | split-sensitivity report §§4–5 | FROZEN |
| D05 | Seed 7 ranked first on matched split-v1 and split-v2; all nine checkpoint ranks unchanged | split-sensitivity report §4; `M_TRAIN_SEED7_RANK` | FROZEN |
| D06 | Matched-control validation mAP50-95 changed 0.428 → 0.427; historical absolute metrics are not byte-identically reproduced | split-sensitivity report §§4,6–7 | SUMMARY_ONLY |

Both split identities and the unchanged test set must be disclosed; split-v1
must not be silently replaced by split-v2.

## 4. INT8 Prerequisite

Stage Q values are prerequisite context, not Stage R comparison values, and
must not be multiplied with Stage R values.

| Item | Frozen value | Metric/authority |
|---|---:|---|
| PTQ role | TensorRT INT8 post-training quantization; INT8 + FP16 mixed precision; calibration train 1260, batch 1, seed 42 | Stage Q §§2,4; `Q_TRT_INT8_ACCURACY` |
| Precision | 0.6912751678 | `M_Q_INT8_PRECISION` |
| Recall | 0.6990950226 | `M_Q_INT8_RECALL` |
| mAP50 | 0.6476254638 | `M_Q_INT8_MAP50` |
| mAP50-95 | 0.3523443910 | `M_Q_INT8_MAP5095` |
| mAP50-95 delta | INT8 − FP16 = -0.0072051299 | `M_Q_INT8_MAP5095_DELTA` |
| Serial inference context | FP16-over-INT8 inference speedup = 1.2698563804 | `M_Q_SERIAL_INFERENCE_SPEEDUP` |
| Serial throughput context | INT8/FP16 throughput ratio = 1.1728497476 | `M_Q_SERIAL_THROUGHPUT_RATIO` |

## 5. Variant Definitions

| Variant | Raw staging/path | Preprocessing | Inference input | Role |
|---|---|---|---|---|
| V0 | Host source / host tensor path | CPU/OpenCV preprocessing path | TensorRT INT8 device input contract | correctness-first baseline |
| V2R | pageable host raw staging | OpenCV 4.5.4-aligned fixed-contract CUDA preprocessing | TensorRT INT8 device input | accepted pageable remediation |
| V3R | pinned host raw staging | the same OpenCV 4.5.4-aligned fixed-contract CUDA preprocessing semantics as V2R | TensorRT INT8 device input | accepted pinned companion |

- V0 → V2R: tested CPU/OpenCV host-tensor path versus accepted pageable
  staging plus CUDA preprocessing under shared object identity.
- V2R → V3R: host staging memory/allocation type only.
- V3R has no cross-frame or asynchronous-path claim.

## 6. Common Timing Boundary

- START: immediately before source pull / frame acquisition.
- INCLUDED: source pull/decode; raw staging/path; CPU or CUDA preprocessing;
  host-to-device transfer where applicable; TensorRT INT8 execution; required
  synchronization; device-to-host transfer where required; postprocessing/NMS;
  frame-result construction.
- END: after frame-result construction, immediately before serialization/write.
- EXCLUDED: JSON serialization; file I/O; digest finalization/writing; summary
  persistence.
- Authority: Phase 2 research narrative §6 and Phase 0.5D I2 report §7.

## 7. Protocol Facts

| Item | Value | Authority |
|---|---:|---|
| warmup | 60 frames/run | timing manifest; I2 §9 |
| measured | 1080 frames/run | timing manifest; I2 §9 |
| measured cycles | 6 | I2 formal protocol and replay count |
| independent processes/variant | 5 | I2 formal report §§3,5 |
| valid runs | 15 | timing manifest `run_count` |
| drops | 0/run | I2 §9 |
| EOS/lifecycle | PASS/run | I2 §9 |
| internal timing | disabled | I2 §§7,9 |
| profiling | off/disabled | I2 §§7,9 |

## 8. Literature Mapping for Section 1

Only admitted sources suitable for Section 1 are listed.

| Citation key | supports | does_not_support | recommended_subsection |
|---|---|---|---|
| `song_yan_2013_neu_surface_defects` | NEU surface-defect source and class context | later annotation-format attribution without evidence | 1.1 |
| `ultralytics_2023_yolov8_docs` | YOLOv8 identity and official task/export information | direct A100-to-Jetson comparison | 1.1 |
| `nvidia_tensorrt_10_3_release_notes` | TensorRT 10.3 and historical INT8 calibrator limitation | current recommended TensorRT 11 route | 1.1; 1.2 |
| `nvidia_jetpack_6_2_2` | explicitly documented JetPack/L4T/CUDA/TensorRT stack facts | unrecorded hardware, clock, or power facts | 1.1 |
| `nvidia_cuda_programming_guide_12_6` | CUDA memory/stream/synchronization semantics | project-specific V3R behavior | 1.2 |
| `nvidia_cuda_best_practices_12_6` | pageable/pinned transfer guidance and timing terminology | universal pinned-memory benefit | 1.2; 1.3 |
| `tang_qian_2024_yolov8_jetson_orin` | deployment pipeline and Jetson/TensorRT context | direct FPS comparison or V3R semantic import | 1.2 |
| `reddi_et_al_2019_mlperf_inference` | latency/throughput distinction, percentile terminology, boundary importance | MLPerf compliance or protocol substitution | 1.3 |

## 9. Allowed Conclusions

- common-boundary comparability;
- controlled-variable framing;
- tested-object disclosure.

## 10. Forbidden Conclusions

- no performance superiority result yet;
- no significant improvement;
- no universal pinned-memory benefit;
- no V3R overlap claim;
- no cumulative J/K/Q/P/R acceleration;
- no MLPerf compliance;
- no industrial-production reliability.

## 11. Open Publication Items

- Figure 1 final visual style;
- final journal typography;
- later Word pagination.

No new experiment or literature-search task is opened by this packet.
