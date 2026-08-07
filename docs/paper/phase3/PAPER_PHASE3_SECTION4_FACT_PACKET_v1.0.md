# Section 4 Fact Packet

## 1. Section Contract

- Title: `结果与分析`
- Subsections: `4.1`; `4.2`; `4.3`; `4.4`
- Claims: `C1`; `C2`; `C3`
- Supporting claims: `C4`; `C8`
- Guardrail: `C9`
- Artifact status: results preparation only; manuscript prose not authorized

## 2. Correctness Results

### V0 authority and V2R task-level Gate D

| Metric | Phase 1 metric ID | V0 authority (formal evidence) | V2R (formal evidence) | Phase 1 frozen V2R value | Delta | Allowed absolute difference | Status |
|---|---|---:|---:|---:|---:|---:|---|
| Precision | `M_R_V2R_GATE_D_PRECISION` | 0.6912751677852349 | 0.6912751677852349 | 0.6912751678 | 0.0 | 0.010 | PASS |
| Recall | `M_R_V2R_GATE_D_RECALL` | 0.6990950226244343 | 0.6990950226244343 | 0.6990950226 | 0.0 | 0.010 | PASS |
| mAP50 | `M_R_V2R_GATE_D_MAP50` | 0.647625463793534 | 0.647625463793534 | 0.6476254638 | 0.0 | 0.005 | PASS |
| mAP50-95 | `M_R_V2R_GATE_D_MAP5095` | 0.3523443910494967 | 0.3523443910494967 | 0.3523443910 | 0.0 | 0.005 | PASS |

- Maximum class AP50 delta: `0.0`; allowed absolute difference: `0.020`; status: `PASS`.
- Maximum class recall delta: `0.0`; allowed absolute difference: `0.030`; status: `PASS`.
- Threshold status: `PASS`.
- Gate D decision: `V2R_CORRECTNESS_ACCEPTED`.

### V3R companion identity facts

| Check | Frozen fact |
|---|---|
| processed images | 180 |
| frame order | PASS |
| image paths | PASS |
| geometry | PASS |
| zero drop | PASS |
| EOS | PASS |
| worker join | PASS |
| tensor digest equality | PASS; V3R and V2R `da2b2bba8d71a25b9bafce988ee838e184666369bbd94bcecc73c6a513d6abb6` |
| detection digest equality | PASS; V3R and V2R `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` |
| detection count equality | PASS; V3R = 447 and V2R = 447 |
| result contract | PASS |
| identity pass | TRUE |
| independent Gate D | FALSE |

V3R has no independent Gate D evaluation row and no independent precision,
recall, mAP50, or mAP50-95 result.

## 3. Direct Performance Results

### FPS and frozen sample SD

| Variant | Mean FPS metric ID | Raw frozen value | Planned display | FPS SD metric ID | Raw frozen value | Planned display |
|---|---|---:|---:|---|---:|---:|
| V0 | `M_R_V0_FPS` | 54.5999763574 | 54.600 FPS | `M_R_V0_FPS_SD` | 0.2233775769 | 0.223 FPS |
| V2R | `M_R_V2R_FPS` | 122.1221922222 | 122.122 FPS | `M_R_V2R_FPS_SD` | 0.4918299468 | 0.492 FPS |
| V3R | `M_R_V3R_FPS` | 127.0972584510 | 127.097 FPS | `M_R_V3R_FPS_SD` | 1.2792256601 | 1.279 FPS |

- Aggregation: FPS mean and sample SD over five process-level FPS values per
  variant.
- Error-bar meaning for Figure 2: frozen FPS sample SD; not CI, SE, or min-max.

### Mean and tail latency

| Variant | Statistic | Metric ID | Raw frozen value | Planned display |
|---|---|---|---:|---:|
| V0 | mean | `M_R_V0_LAT_MEAN` | 18.2729918109 | 18.273 ms |
| V0 | P95 | `M_R_V0_P95` | 18.8541178 | 18.854 ms |
| V0 | P99 | `M_R_V0_P99` | 19.06830438 | 19.068 ms |
| V2R | mean | `M_R_V2R_LAT_MEAN` | 8.1402787896 | 8.140 ms |
| V2R | P95 | `M_R_V2R_P95` | 9.82713435 | 9.827 ms |
| V2R | P99 | `M_R_V2R_P99` | 11.52898548 | 11.529 ms |
| V3R | mean | `M_R_V3R_LAT_MEAN` | 7.8118285628 | 7.812 ms |
| V3R | P95 | `M_R_V3R_P95` | 9.8420113 | 9.842 ms |
| V3R | P99 | `M_R_V3R_P99` | 11.5153358 | 11.515 ms |

- Aggregation: each mean, P95, and P99 is a distinct frozen statistic over the
  pooled 5400 measured-frame samples for its variant.

## 4. V2R vs V0

`PRIMARY OBSERVED BENEFIT`

Only frozen Phase 1 derived rows are used.

| Comparison metric | Metric ID | Raw frozen value | Planned display | Direction |
|---|---|---:|---:|---|
| FPS ratio | `M_R_V2R_V0_FPS_RATIO` | 2.2366711557 x | 2.236671 x | higher FPS ratio |
| FPS increase | `M_R_V2R_V0_FPS_INCREASE` | 123.6671% | 123.6671% | higher FPS |
| Mean-latency reduction | `M_R_V2R_V0_LAT_REDUCTION` | 55.4518555371% | 55.4519% | lower/faster mean latency |
| P95 reduction | `M_R_V2R_V0_P95_REDUCTION` | 47.8780% | 47.8780% | lower/faster P95 |
| P99 reduction | `M_R_V2R_V0_P99_REDUCTION` | 39.5385% | 39.5385% | lower/faster P99 |

## 5. V3R vs V2R

Only frozen Phase 1 derived rows are used.

| Comparison metric | Metric ID | Raw frozen value | Planned display | Direction |
|---|---|---:|---:|---|
| FPS increase | `M_R_V3R_V2R_FPS_INCREASE` | 4.0738428768% | +4.0738% | positive improvement |
| Mean-latency reduction | `M_R_V3R_V2R_LAT_REDUCTION` | 4.0349% | 4.0349% | lower/faster mean latency |
| P95 change | `M_R_V3R_V2R_P95_CHANGE` | 0.1513864517% | +0.1514% | HIGHER / SLOWER |
| P99 change | `M_R_V3R_V2R_P99_CHANGE` | -0.1183944591% | -0.1184% | LOWER / FASTER |

- `AVERAGE BENEFIT: LIMITED POSITIVE`
- `TAIL: MIXED`

## 6. Allowed Result Claims

- `C1`: V2R task-level correctness accepted under the frozen Gate D contract.
- `C2`: V2R provides the primary observed average-performance benefit versus
  V0 under the common Stage R protocol.
- `C3`: V3R provides only limited incremental FPS/mean benefit versus V2R.
- `C3`: V3R does not show consistent tail-latency benefit; P95 and P99 have
  opposite directions.
- `C4` and `C8`: supporting prerequisite and dataset/model disclosures remain
  bounded to their frozen evidence roles.

## 7. Forbidden Claims

- `statistically significant`
- `lossless`
- `raw equivalent`
- `universal CUDA dominance`
- `universal pinned benefit`
- `V3R tail improvement`
- `V3R overlap`
- `total project speedup`
- multiplication of independent `J/K/Q/P/R` ratios
- `industrial reliability`

These phrases are exclusions, not positive findings.

## 8. Result-to-Artifact Mapping

| Artifact | Content | Frozen metric IDs / evidence |
|---|---|---|
| T2 | V0/V2R task-level correctness and V3R companion identity | Four `M_R_V2R_GATE_D_*` rows plus formal Gate D/V3R JSON |
| F2 | V0/V2R/V3R mean FPS with FPS sample SD error bars | Six `M_R_*_FPS` / `M_R_*_FPS_SD` rows |
| F3 | V0/V2R/V3R mean, P95, and P99 latency | Nine direct frozen latency rows |

## 9. Limitations

- Single Jetson platform.
- Fixed YOLOv8n INT8 Engine.
- 640 x 640 input.
- Batch size 1.
- 180-image offline replay.
- Five processes per variant.
- Descriptive statistics only.
- No power, resource, or endurance result.
- No real-camera result.
- No significance test.
- V3R has no independent Gate D.
