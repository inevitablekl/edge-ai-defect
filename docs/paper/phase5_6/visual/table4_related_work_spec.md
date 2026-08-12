# Table 4 — Related-Work Qualitative Comparison

Status: `CANDIDATE / SPECIFICATION`
Scientific role: position the controlled data-path study using independently relevant dimensions. It is not a cross-paper FPS ranking and must not convert “not reported” into “no.” Target: full width `16.0 cm`, native three-line Word table in D-B.

## Candidate works resolved from bibliography

| Citation key | Bibliographic identity | Local full text |
|---|---|---|
| `kim_et_al_2025_concurrent_edge_detection` | Seunghwan Kim et al., “Improving Performance of Real-Time Object Detection in Edge Device Through Concurrent Multi-Frame Processing,” 2025 | available |
| `lee_han_kim_2025_presto` | Jihyuk Lee, Dongsu Han, and Jaehong Kim, “PRESTO: Hybrid CPU-GPU Preprocessing Framework for Video-based AI Inference System,” 2025 | available |
| `tang_qian_2024_yolov8_jetson_orin` | Youzhi Tang and Yu Qian, “High-speed railway track components inspection framework based on YOLOv8 with high-performance model deployment,” 2024 | available |
| `shin_kim_2022_jetson_yolo_frameworks` | Dong-Jin Shin and Jeong-Joon Kim, “A Deep Learning Framework Performance Evaluation to Use YOLO in Nvidia Jetson Platform,” 2022 | available |
| `bateni_et_al_2020_integrated_memory` | Soroush Bateni et al., “Co-Optimizing Performance and Memory Footprint Via Integrated CPU/GPU Memory Management, an Implementation on Autonomous Driving Platform,” 2020 | available |
| — | This work | repository implementation and frozen Phase 5.6 evidence |

Exact paths, page locators, paraphrases, and confidence for all 42 cells are authority in `phase56_related_work_attribute_evidence.csv`.

## Seven columns and fairness rationale

| Attribute | Independent scientific relevance |
|---|---|
| Edge deployment | distinguishes deployment conditions from server-only evaluation |
| Detector/model fixed within comparison | controls whether runtime differences are confounded by model changes |
| GPU preprocessing | locates tensor/image transformation work |
| Explicit host-memory strategy | identifies deliberate pageable/pinned/unified host-memory handling |
| Complete E2E evaluation | determines whether preprocessing, inference, and postprocessing are included |
| Task correctness | checks whether deployment changes preserve task output quality |
| Tail latency | exposes behavior not captured by means/throughput |

These dimensions are useful for evaluating deployment studies independently of whether this work scores “是.” Optional “quantized deployment” and “explicit controlled path comparison” were rejected to limit width and avoid a taxonomy optimized for this paper.

## Classification contract

Internal vocabulary is exactly `YES`, `NO_IF_EXPLICIT`, `NOT_REPORTED`, `NOT_APPLICABLE`. D-B display mapping: `是`, `明确否`, `未报告`, `不适用`. A `NO_IF_EXPLICIT` cell requires explicit full-text exclusion or an evaluation boundary that excludes the attribute. `NOT_REPORTED` is never silently converted to “no.”

## Full-text audit result

All five external full texts are locally available and all seven attributes are resolved. None reports the complete combination of fixed detector/Engine, isolated input-formation location, host representation, nominal input-copy payload, pageable/pinned staging, unified task correctness, and complete E2E evaluation. The audited set contains partial precedents, not a direct match.

```text
LITERATURE_GAP_AUDIT = PARTIAL_PRECEDENT_ONLY
DIRECT_MATCH_STATUS = NO_DIRECT_MATCH_IN_AUDITED_SET
F1_SUPPORT_STATUS = PARTIALLY_SUPPORTED
```

This scoped result does not establish that no prior work exists outside the audited set.

## Publication-safe wording candidate and citation placement

Candidate only; do not edit the manuscript in D-A:

> 在本文审阅的相关边缘部署与预处理/内存管理工作中，尚未见在固定detector/Engine下同时隔离输入形成位置、host representation、名义输入复制载荷与pageable/pinned staging，并以统一任务正确性和完整E2E口径比较的报告。

Place the grouped citations to Kim, PRESTO, Tang & Qian, Shin & Kim, and Bateni immediately after this scoped sentence. Do not attach them only to the following sentence and do not replace “在本文审阅的” with a field-wide absence claim.

## Candidate caption

**相关边缘部署、预处理与内存管理工作的定性比较。** “是”表示全文明确报告该维度，“明确否”表示全文明确排除或评估边界明确不包含该维度，“未报告”表示审阅全文未找到足以判定的报告；“未报告”不等同于“否”。比较用于说明研究设计覆盖范围，不用于跨论文性能排名。

## Candidate and D-B plan

- Candidate: `candidates/table4_related_work_candidate.md`
- Generator: `scripts/generate_phase56d_table_candidates.py`
- D-B: regenerate from the evidence CSV, retain terminology note, use compact headers/footnotes, create a full-width native three-line table, and integrate only with the scoped literature sentence and verified citation keys.
