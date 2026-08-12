# Table 3 — Task-Level Correctness

Status: `CANDIDATE / SPECIFICATION`
Scientific role: publish task metrics, not an internal pass/fail gate. Target width: `7.5–8.0 cm` if readable, maximum `16.0 cm`; native three-line Word table in D-B.

## Required schema

| Path | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| V0 | source-derived | source-derived | source-derived | source-derived |
| V2R | source-derived | source-derived | source-derived | source-derived |
| V3R | source-derived | source-derived | source-derived | source-derived |

Input authority: `docs/paper/phase5_6/phase56b_correctness_table_source.csv`, exactly three rows and columns `Path,Precision,Recall,mAP50,mAP50-95,AuthorityType`. Candidate display uses four decimals; values are read by the generator and never retyped. Governance thresholds, “允许差异,” and “结果=通过” are excluded from the manuscript table.

Six-class metrics remain Level-B evidence. A concise table note or nearby sentence may state `max class AP50 difference = 0` and `max class Recall difference = 0`; do not add all class rows to T3.

## Candidate caption

**V0、V2R和V3R的任务级正确性。** Precision、Recall、mAP50和mAP50-95均由冻结预测证据按统一评估口径获得；各路径的汇总指标一致，类别级AP50与Recall的最大路径间差异均为0。

## Candidate and D-B plan

- Candidate: `candidates/table3_correctness_candidate.md`
- Generator: `scripts/generate_phase56d_table_candidates.py`
- D-B: regenerate from the frozen CSV, create a native three-line table, and validate displayed values against the CSV/hash before integration.
