# Table 2 Correctness Data

Drafting asset only. This file is not Section 4 manuscript prose.

### V0 / V2R Task-Level Correctness

| Metric | V0 authority | V2R | Delta | Allowed abs diff | Status |
|---|---:|---:|---:|---:|---|
| Precision | 0.6913 | 0.6913 | 0.0000 | 0.010 | PASS |
| Recall | 0.6991 | 0.6991 | 0.0000 | 0.010 | PASS |
| mAP50 | 0.6476 | 0.6476 | 0.0000 | 0.005 | PASS |
| mAP50-95 | 0.3523 | 0.3523 | 0.0000 | 0.005 | PASS |

Exact formal evidence values before display rounding:

| Metric | Phase 1 metric ID | V0 authority | V2R | Delta |
|---|---|---:|---:|---:|
| Precision | `M_R_V2R_GATE_D_PRECISION` | 0.6912751677852349 | 0.6912751677852349 | 0.0 |
| Recall | `M_R_V2R_GATE_D_RECALL` | 0.6990950226244343 | 0.6990950226244343 | 0.0 |
| mAP50 | `M_R_V2R_GATE_D_MAP50` | 0.647625463793534 | 0.647625463793534 | 0.0 |
| mAP50-95 | `M_R_V2R_GATE_D_MAP5095` | 0.3523443910494967 | 0.3523443910494967 | 0.0 |

- Maximum class AP50 delta: `0.0`; allowed absolute difference: `0.020`;
  status: `PASS`.
- Maximum class recall delta: `0.0`; allowed absolute difference: `0.030`;
  status: `PASS`.
- Overall threshold status: `PASS`.
- Gate D decision: `V2R_CORRECTNESS_ACCEPTED`.
- Phase 1 values are frozen to ten decimal places in the metric provenance;
  the exact values above are copied from the formal Gate D JSON.

### V3R Companion Identity

| Check | Result |
|---|---|
| processed images | 180 |
| frame order | PASS |
| image paths | PASS |
| geometry | PASS |
| zero drop | PASS |
| EOS | PASS |
| worker join | PASS |
| tensor digest identity | PASS; `da2b2bba8d71a25b9bafce988ee838e184666369bbd94bcecc73c6a513d6abb6` |
| detection digest identity | PASS; `12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` |
| detection count | PASS; V3R = 447 and V2R = 447 |
| result contract | PASS |
| identity pass | TRUE |
| independent Gate D | NO |

V3R is an identity-supported pinned companion. It has no independent Gate D
row and no independent precision, recall, mAP50, or mAP50-95 result.

Sources:

- `docs/paper/phase1/PAPER_PHASE1_METRIC_PROVENANCE_v1.0.csv`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_task_metrics.json`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_gate_d_decision.json`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v3r_identity_check.json`
