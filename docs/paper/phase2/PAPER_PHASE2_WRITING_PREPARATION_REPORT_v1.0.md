# Paper Phase 2 Artifact Preparation Result

## 1. Verdict

`COMPLETE_WITH_INPUT_GAPS`

The eight required writing-preparation assets are complete. The only external
input gap is the inaccessible payload of the four official 2025-02-25 format
attachments. Their unresolved parameters are explicitly marked
`OFFICIAL_ATTACHMENT_EXTRACTION_PENDING`; no layout value was guessed.

## 2. Repository State

- Branch: `main`
- Starting HEAD: `68dce90c084c7f54199966791a0a0ebcea258817`
- Independent-review remediation base:
  `4e2b1266663c08ae53ef025cfa2d96f42f5f8272`
- Final HEAD: `SELF` — the commit containing this report, with message
  `docs(paper): remediate phase 2 F1 crosswalk`
- Starting worktree/index: clean
- Final worktree/index target: clean after the Phase 2-only commit
- Phase 1 ancestor check: PASS

## 3. Inputs Read

### Mandatory Phase 0

- `docs/paper/phase0/PAPER_PHASE0_FINAL_FREEZE_v1.1.md`
- `docs/paper/phase0/PAPER_CONTRIBUTION_ASSESSMENT_v1.2.md`
- `docs/paper/phase0/PAPER_EVIDENCE_AUTHORITY_MAP_v1.1.md`
- `docs/paper/phase0/PAPER_ASSET_MANIFEST_v1.1.csv`
- `docs/paper/phase0/PAPER_PHASE0_GAP_REGISTER_v1.1.md`

### Mandatory Phase 1

- `docs/paper/phase1/PAPER_PHASE1_EXPERIMENT_MATRIX_v1.0.csv`
- `docs/paper/phase1/PAPER_PHASE1_METRIC_PROVENANCE_v1.0.csv`
- `docs/paper/phase1/PAPER_PHASE1_CLAIM_EVIDENCE_MAP_v1.0.md`
- `docs/paper/phase1/PAPER_PHASE1_GAP_REGISTER_v1.0.md`
- `docs/paper/phase1/PAPER_PHASE1_EVIDENCE_FREEZE_REPORT_v1.0.md`
- `docs/paper/phase1/PAPER_PHASE1_INDEPENDENT_REVIEW_v1.0.md`
- `docs/paper/phase1/PAPER_PHASE1_FINAL_FREEZE_v1.0.md`

### Phase 0.5 formal and compact authority

- `docs/paper/phase0_5/PAPER_CORE_VALIDITY_AUDIT_v1.0.md`
- `docs/paper/phase0_5/PAPER_DATASET_SPLIT_SENSITIVITY_FINAL_v1.0.md`
- `docs/paper/phase0_5/PAPER_V2R_GATE_D_DISPOSITION_v1.0.md`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_G_EXECUTION_REPORT.md`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`
- `docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/manifest.json`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_task_metrics.json`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_gate_d_decision.json`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v3r_identity_check.json`
- `docs/paper/phase0_5/evidence/checkpoint_selection_sensitivity_control_v1/matched_split_comparison.json`

### Stage Q supporting authority

- `docs/personal/STAGE_Q_FINAL_REPORT.md`
- `docs/personal/STAGE_Q_EVIDENCE_INDEX.md`
- `docs/personal/STAGE_Q5_ACCURACY_REPORT.md`
- `docs/personal/STAGE_Q6_SERIAL_PERFORMANCE_REPORT.md`
- `results/validation/stage_q/q1_platform_asset_preflight_v1/platform_summary.json`
- `results/validation/stage_q/q5_accuracy_v1/metrics_summary.json`
- `results/validation/stage_q/q6_serial_performance_v1/q6_serial_summary.json`

### Stage R historical/exclusion inspection

- `docs/personal/STAGE_R_FINAL_REPORT.md`
- `results/paper/stage_r/metadata.json`
- `results/paper/stage_r/stage_r_ablation_table.csv`
- `results/paper/stage_r/stage_r_fps_latency_plot.csv`
- `results/paper/stage_r/stage_r_tail_latency_plot.csv`

The last four `results/paper/stage_r` assets belong to the superseded Attempt 2
package and were inspected only to ensure they are not reused. Current article
numbers come from Phase 1 provenance and the Phase 0.5D timing-aligned authority.

### Official journal pages

- `https://xbzzs.hfut.edu.cn/xbzk/default/page.html?id=13`
- `https://xbzzs.hfut.edu.cn/xbzk/downloads/list.html`
- `https://xbzzs.hfut.edu.cn/xbzk/downloads/index.html?id=415`
- `https://xbzzs.hfut.edu.cn/xbzk/downloads/index.html?id=414`
- `https://xbzzs.hfut.edu.cn/xbzk/downloads/index.html?id=413`
- `https://xbzzs.hfut.edu.cn/xbzk/downloads/index.html?id=412`

## 4. Journal Requirements

Verified from the official submission guide:

- Chinese title generally no more than 20 Chinese characters and generally no
  subtitle.
- Chinese/English title, abstract, keywords, and related front matter required.
- Chinese abstract normally at least 150 characters.
- At least 4 Chinese keywords with corresponding English terms.
- Article generally within 10,000 Chinese characters.
- Explicit quantities/units in figures and tables; three-line tables.
- Sequential numeric references, generally at least 8, with recent domestic,
  international, and target-journal work considered.
- Original and review versions are Word; the review file removes author-related
  information.

The preferred title has 11 Han characters (21 total Unicode code points) and no
subtitle. It meets the stated Chinese-character count criterion; Latin/digit
treatment remains a manual editorial check. The alternate has 13 Han characters
and 19 total code points.

The download list verifies the four titles, 2025-02-25 update date, and displayed
sizes. Payload download failed, so actual filenames, file types, exact byte
counts, SHA256, fonts, sizes, dimensions, DPI, and rule widths remain
`OFFICIAL_ATTACHMENT_EXTRACTION_PENDING`.

## 5. Research Narrative

- Central question: under the frozen Jetson/model/INT8 Engine/workload,
  correctness contract, and common timing interval, how do V0 CPU
  preprocessing, V2R pageable staging plus CUDA preprocessing, and V3R pinned
  staging plus the same CUDA preprocessing affect FPS, mean latency, P95, and
  P99?
- Subquestions: common-boundary validity; V2R correctness and main benefit;
  V3R incremental average effect; mixed tail behavior and applicability.
- Core contribution 1: controlled V0/V2R/V3R ablation under one frozen
  experimental boundary.
- Core contribution 2: V2R provides the main observed average benefit; V3R
  provides a limited average increment without a consistent tail benefit.
- Limitations: one platform/model/Engine/input/batch and offline replay;
  serialization/I/O excluded; no power/resource/endurance/real-camera claim;
  V3R uses identity inheritance; no cross-protocol arithmetic.

## 6. Article Structure

```text
0 引言
1 系统对象与问题定义
  1.1 工业缺陷检测部署对象
  1.2 INT8推理数据路径
  1.3 研究问题与统一计时边界
2 数据路径优化方法
  2.1 CPU预处理基线路径
  2.2 CUDA预处理路径
  2.3 Pinned内存数据路径
  2.4 正确性约束与资源生命周期
3 实验设计
  3.1 实验平台与模型配置
  3.2 数据集与统一运行协议
  3.3 正确性和性能指标
4 结果与分析
  4.1 正确性验证结果
  4.2 CUDA预处理的主要性能收益
  4.3 Pinned内存的增量收益
  4.4 尾延迟与适用范围讨论
5 结论
```

## 7. Claim Coverage

- Phase 1 experiment count: 16 (unchanged).
- Phase 1 metric count: 87 (unchanged).
- Phase 1 claim count: 9 (`C1-C9`).
- Article core claims: `A1->C1`, `A2->C2`, `A3->C3`.
- Supporting claims: `A4->C4` for protocol-local INT8 prerequisite context and
  `A5->C8` for dataset/model disclosure. A4 is prose-only
  (`figure_or_table=NONE`) and does not establish a Stage Q result line.
- Background/limitation support: `C5` Pipeline and `C7` ORT CPU, with no Stage R
  numeric comparison.
- Limitation support/background: `C6` TensorRT FP16 correctness-layer context,
  with its verified raw-output failure retained.
- Guardrail: `G1->C9` excludes Attempt 2/V4 and cross-protocol ratio products.
- Unsupported article claims: 0.
- New A-level contributions: 0; total remains exactly 2.

## 8. Figure and Table Plan

- Figure 1: V0/V2R/V3R data paths and common timing interval; sources are the
  experiment matrix, claim map, and Phase 0.5D formal report.
- Table 1: platform/model/dataset/run protocol; claim binding is limited to A1
  and A5. Sources are the experiment matrix, metric provenance, compact
  manifest, formal report, and Stage Q final report.
- Table 2: Stage R task-level correctness and V3R identity evidence; claim
  binding is limited to A1, A2, and A3. Sources are the four Gate D metric rows
  and compact Gate D/V3R JSON.
- Figure 2: V0/V2R/V3R mean FPS with only the frozen sample SD; sources are six
  Phase 1 metric rows.
- Figure 3: V0/V2R/V3R mean/P95/P99 latency in ms; sources are nine Phase 1
  metric rows.

No plotting script or preview was created because official figure parameters
remain pending. Deterministic generation paths and formulas are recorded for a
later drafting task. Superseded Stage R CSV and Stage P throughput are excluded.

## 9. Literature Requirements

- L1 industrial defect detection and edge-deployment background.
- L2 YOLOv8 and NEU-DET related work.
- L3 TensorRT FP16/INT8 PTQ principles and deployment.
- L4 GPU preprocessing and inference data-path research.
- L5 pageable/pinned host memory and H2D transfer.
- L6 inference/E2E latency, throughput/FPS, and tail-latency definitions.
- L7 2024-2026 edge-vision and industrial-detection work.
- L8 2023-08-04 to 2026-08-04 target-journal work.
- L9 version-aware NVIDIA/CUDA/TensorRT official documentation.

No reference entry, author, title, DOI, or venue was fabricated.

## 10. Files Created

- `docs/paper/phase2/PAPER_PHASE2_JOURNAL_REQUIREMENTS_v1.0.md`
- `docs/paper/phase2/PAPER_PHASE2_RESEARCH_NARRATIVE_v1.0.md`
- `docs/paper/phase2/PAPER_PHASE2_ARTICLE_OUTLINE_v1.0.md`
- `docs/paper/phase2/PAPER_PHASE2_CLAIM_ARCHITECTURE_v1.0.csv`
- `docs/paper/phase2/PAPER_PHASE2_FIGURE_TABLE_PLAN_v1.0.csv`
- `docs/paper/phase2/PAPER_PHASE2_WRITING_PACKETS_v1.0.md`
- `docs/paper/phase2/PAPER_PHASE2_LITERATURE_REQUIREMENTS_v1.0.md`
- `docs/paper/phase2/PAPER_PHASE2_WRITING_PREPARATION_REPORT_v1.0.md`

No thesis outline, manuscript body, completed abstract, completed introduction,
completed conclusion, external template, result asset, configuration, model,
source, include, or test file was created or changed.

## 11. Validation

- Required artifact structure: PASS (`PHASE2_ARTIFACT_STRUCTURE_PASS`).
- CSV parse: PASS; both CSV files are non-empty and have unique candidate/claim
  IDs.
- Metric crosswalk: PASS; every referenced metric ID exists in the 87-row Phase
  1 provenance file.
- Claim crosswalk: PASS; every article claim maps to one of `C1-C9`; all core
  claims include Phase 1 claim and metric IDs.
- F1 claim/display crosswalk: PASS; A4 has `figure_or_table=NONE`, and neither
  T1 nor T2 lists A4. Q6 inference-speedup and throughput-ratio metrics remain
  protocol-local prerequisite context in the writing packet only.
- Frozen-count check: PASS; 16 experiments, 87 metrics, `C1-C3` core, `C4-C9`
  supporting/limitation/guardrail.
- Numeric provenance/tolerance check: PASS; all Phase 2 numeric tokens used as
  research evidence match frozen Phase 1 values or official website metadata;
  no Phase 1 change request is required.
- Cross-stage product scan: PASS.
- V4 positive-result scan: PASS.
- Prohibited wording scan: PASS.
- Long-form manuscript scan: PASS; planning packets only.
- Fabricated-reference scan: PASS; no bibliography entries exist.
- `git diff --check`: PASS.

## 12. Unresolved Issues

- `OFFICIAL_ATTACHMENT_EXTRACTION_PENDING`: the four 2025-02-25 official
  attachment payloads were not downloadable in this execution environment.
  Actual filename, type, exact bytes, SHA256, and detailed layout/figure/table
  parameters must be verified before Word typesetting.

No experiment, Phase 1 evidence, claim, metric, or article-architecture blocker
remains.

## 13. Recommended Next Executor

`REVIEW_AI`
