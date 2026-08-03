# Paper V2R Gate D Disposition v1.0

## 1. Verdict

`V2R_CORRECTNESS_ACCEPTED`

## 2. Frozen Execution Identity

Implementation commit:
`4815a9d129fca1bce6d69926792c05a52f3b3530`

V2R uses pageable raw staging and the frozen OpenCV 4.5.4-aligned fixed
contract CUDA resize. V3R uses pinned raw staging and the identical resize
semantic. The frozen INT8 Engine, Engine manifest, model/ONNX contract, and
180-image test manifest are recorded in the compact evidence package at
`docs/paper/phase0_5/evidence/v2r_gate_d_v1/`.

Post-Gate-D kernel modification:
`NONE`

Second remediation:
`PROHIBITED`

## 3. Gate D Contract

The single formal V2R evaluation used the existing V0 authority, frozen
split-v2 test manifest, 640x640 input, batch 1, `conf=0.25`, `iou=0.45`,
`max_nms=30000`, `max_det=300`, `agnostic=false`, and `multi_label=false`.
The unchanged limits were mAP50-95 `0.005`, mAP50 `0.005`, precision `0.010`,
recall `0.010`, maximum class AP50 `0.020`, and maximum class recall `0.030`.

## 4. V2R Task Metrics

V2R processed 180 images, produced 447 detections across 6 classes, and had
zero drops. Precision `0.6912751677852349`, recall `0.6990950226244343`, mAP50
`0.647625463793534`, and mAP50-95 `0.3523443910494967` exactly matched the V0
authority. The absolute delta for each aggregate metric was `0.0`. Per-class
metrics are in the compact CSV evidence.

## 5. Gate-by-Gate Decision

All six Gate D checks are `PASS`; every observed drop was `0.0`. The formal
V2R result JSON SHA256 is
`fb18d7afabd08406697749fb2a033be5455c2af989dc1bb4087310e54c2a4aaa`.

## 6. V3R Companion Identity

V3R replayed the same 180-image sequence with frame order, paths, geometry,
count, zero-drop, EOS, and result contract all passing. V2R and V3R tensor
digest SHA256 is
`da2b2bba8d71a25b9bafce988ee838e184666369bbd94bcecc73c6a513d6abb6`; their
detection SHA256 is
`12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2`.
V3R was not used as an independent Gate D parameter-selection run.

## 7. Test-Set Separation Compliance

The frozen 180-image test split was used only for this I2 Gate D execution and
the corresponding V3R identity replay. I1 evidence and historical V2/V3
evidence were not overwritten.

## 8. Final Correctness Decision

`V2R_CORRECTNESS_ACCEPTED`

## 9. Allowed Claims

V2R is correctness-accepted under the frozen platform, model, Engine,
preprocessing semantic, postprocess contract, thresholds, and 180-image test
protocol. V3R may accompany V2R as a pinned identity-equivalent companion.

## 10. Prohibited Claims

Do not generalize this bounded result to all OpenCV versions, dimensions,
types, platforms, models, or engines. Do not claim a performance gain from this
correctness run, raw universal bitwise equivalence, or a second remediation.

## 11. Phase 0.5D Eligibility

V2R and its pinned V3R companion are eligible for Phase 0.5D after Paper
Project Manager review. Phase 0.5D was not run in this task.

## 12. Recommended Next Actor

`Paper Project Manager`
