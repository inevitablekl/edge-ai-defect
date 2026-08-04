# Paper Phase 2 Research Narrative v1.0

## 1. Article Positioning

The target is one bounded engineering application article on Jetson-side INT8
industrial defect detection data paths. It is not a detection-algorithm paper,
a quantization-method paper, a multi-platform comparison, or a stage-by-stage
project history.

The article's main evidence is the timing-aligned `V0/V2R/V3R` Stage R
ablation. Stage Q provides the INT8 PTQ prerequisite and task-level correctness
context. Training/model disclosure and bounded lifecycle evidence support
validity. Stages J, K, and P provide brief deployment background only.

## 2. Central Research Question

Under the frozen Jetson platform, INT8 Engine, industrial defect detection
model, replay workload, correctness contract, and common timing boundary, how
do CPU preprocessing, CUDA preprocessing with pageable host staging, and CUDA
preprocessing with pinned host staging affect frame rate, mean latency, and
tail latency?

## 3. Subquestions

1. Can V0, V2R, and V3R be compared under one identical external timing and
   lifecycle contract?
2. Does V2R preserve the accepted task-level correctness result and provide
   the primary observed average-performance benefit relative to V0?
3. What incremental effect does pinned staging in V3R provide relative to
   V2R, and is that effect consistent across mean, P95, and P99 latency?
4. Which conclusions remain bounded by the offline replay, single platform,
   frozen model/Engine, and missing resource/endurance evidence?

## 4. Exactly Two Core Contributions

### Contribution 1: controlled data-path ablation under one boundary

Establish a reproducible V0/V2R/V3R comparison using one frozen platform,
model, INT8 Engine, test workload, correctness contract, timing interval, and
run protocol. The contribution is an engineering measurement and evidence
boundary, not a new neural network, quantization, resize, or CUDA algorithm.

Phase 1 basis: `C1`, with `C2` supplying the accepted V2R correctness and
V2R/V0 comparison details.

### Contribution 2: average-performance and tail-latency trade-off

Show that V2R supplies the main observed average-performance benefit, whereas
V3R supplies only a limited incremental FPS and mean-latency benefit. The V3R
tail behavior is mixed: P95 is slightly higher and P99 is slightly lower than
V2R, so the evidence does not establish a consistent tail-latency benefit.

Phase 1 basis: `C2` and `C3`.

No third A-level contribution is admitted.

## 5. Evidence Roles

| Evidence family | Article role | Numeric-comparison rule |
|---|---|---|
| Stage R V0/V2R/V3R | Main controlled ablation | Direct comparison allowed only inside the common Stage R protocol. |
| Stage Q INT8 PTQ | Prerequisite/support | Accuracy and Q6 performance may be stated separately as bounded support; do not combine with Stage R ratios. |
| Training, split, model, ONNX | Reproducibility and disclosure | Use identity, split, and selection facts; summary-only historical values stay identified as such. |
| Stage J ORT CPU | Brief deployment background | No direct numeric comparison with Stage R. |
| Stage K TensorRT FP16 | Brief precision/backend background and raw-output limitation | K7 comparisons remain inside K7; no arithmetic with Q, P, or R. |
| Stage P Pipeline | Brief runtime background | Throughput-only observation; no single-frame latency inference and no Stage R figure. |
| Historical R Attempt 2 and V4 | Exclusion/guardrail history | No formal table, figure, abstract result, or conclusion value. |

## 6. Common Experimental Boundary

The formal interval starts before source pull/frame acquisition and ends after
preprocessing, TensorRT execution, postprocessing, and frame-result
construction, before result serialization/write.

Included:

- source pull/decode;
- raw staging and H2D transfer;
- CPU or CUDA preprocessing;
- TensorRT INT8 inference and required synchronization;
- D2H transfer, postprocessing, and frame-object construction.

Excluded:

- JSON serialization and file I/O;
- digest finalization;
- summary persistence.

The formal protocol is 60 warmup frames, 1080 measured frames, six measured
cycles, five independent processes per variant, 15 valid runs, zero observed
drops, and EOS/lifecycle pass. Internal timing is disabled and profiling mode
is off for all three branches.

## 7. Argument Chain

```text
Frozen deployment object and INT8 prerequisite
-> one timing/correctness/lifecycle contract
-> V0 versus V2R isolates the main CUDA-preprocessing path change
-> V2R versus V3R isolates the host-staging memory change
-> average and tail metrics are interpreted separately
-> conclusions are limited to the tested path and workload
```

Stages are provenance labels, not the article's chapter structure.

## 8. Claim Boundaries and Limitations

- Results are descriptive for Jetson Orin Nano Super, the frozen YOLOv8n/INT8
  Engine, 640x640 batch-1 input, and the 180-image replay workload.
- V2R correctness is accepted at the task-level Gate D under the frozen
  thresholds; it is not a general raw-tensor or bitwise identity statement.
- V3R correctness uses shared tensor/detection digests and lifecycle identity,
  not an independent Gate D evaluation.
- The five-run aggregates do not create an unplanned confidence interval or
  statistical-significance result.
- FPS, throughput, inference latency, and end-to-end latency remain separately
  named metrics.
- Resource, power, endurance, real-camera, and field-reliability conclusions
  are outside the Stage R evidence contract.
- The historical train/validation duplicate, unchanged test set, split-v2
  counts, and matched-control rank result must be disclosed.
- Historical Attempt 2 and V4 stay excluded from causal and formal performance
  conclusions.
- Ratios from independent J/K/Q/P/R protocols must never be multiplied or
  presented as one combined factor.

## 9. Candidate Titles

- Preferred: `Jetson端INT8缺陷检测数据路径优化`
- Alternate: `面向Jetson的缺陷检测数据路径优化`

Both candidates have no subtitle. Phase 2 does not finally freeze the title.

## 10. Derived Value Register

All experimental derived values used by the Phase 2 architecture are frozen
Phase 1 results, not new statistics. Status for every row:
`DERIVED_FROM_PHASE1`; tolerance recomputation: `PASS`.

| Use | Frozen value | Formula from frozen absolute values | Source metric ID |
|---|---:|---|---|
| V2R/V0 FPS ratio | 2.2366711557x | `122.1221922222 / 54.5999763574` | `M_R_V2R_V0_FPS_RATIO` |
| V2R/V0 mean-latency reduction | 55.4518555371% | `(18.2729918109 - 8.1402787896) / 18.2729918109 * 100` | `M_R_V2R_V0_LAT_REDUCTION` |
| V3R/V2R FPS increase | 4.0738428768% | `(127.0972584510 / 122.1221922222 - 1) * 100` | `M_R_V3R_V2R_FPS_INCREASE` |
| V3R/V2R mean-latency reduction | 4.0349% | `(8.1402787896 - 7.8118285628) / 8.1402787896 * 100` | `M_R_V3R_V2R_LAT_REDUCTION` |
| V3R/V2R P95 latency change | +0.1513864517% | `(9.84201130 - 9.82713435) / 9.82713435 * 100` | `M_R_V3R_V2R_P95_CHANGE` |
| V3R/V2R P99 latency change | -0.1183944591% | `(11.51533580 - 11.52898548) / 11.52898548 * 100` | `M_R_V3R_V2R_P99_CHANGE` |

Positive latency change means higher/slower latency; negative latency change
means lower/faster latency. The plot inputs for FPS mean/SD and latency
mean/P95/P99 are likewise copied only from their frozen Phase 1 metric rows and
remain marked `DERIVED_FROM_PHASE1` in the figure/table plan.
