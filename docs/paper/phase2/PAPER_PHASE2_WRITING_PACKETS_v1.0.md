# Paper Phase 2 Writing Packets v1.0

## 1. Global Writing Contract

These packets prepare evidence-aware drafting. They do not contain completed
article prose.

Internal length target: approximately `8,200-9,000` Chinese characters for the
planned article, leaving margin below the journal's general 10,000-character
ceiling for later layout and editorial revision. The percentages below are
internal planning allocations, not journal requirements.

Global controls:

- Core evidence is V0/V2R/V3R under one Stage R boundary.
- Core contribution count is exactly two.
- Every numeric statement must cite a Phase 1 metric ID in the drafting notes.
- `DERIVED_FROM_PHASE1` must accompany any frozen ratio/increase/reduction in
  the working crosswalk.
- Accuracy, FPS, throughput, inference latency, end-to-end latency, mean, P95,
  and P99 remain distinct.
- J/K/P are brief background; Q is a prerequisite; R is the controlled result.
- Historical Attempt 2 and V4 are excluded from formal results.
- No new experiment, statistic, confidence interval, hypothesis test, or
  reference entry may be invented.

## 2. Packet: 题名与摘要

### 写作目标

Select a compact title and later produce paired Chinese/English report-style
abstracts that answer purpose, method, result, and conclusion without expanding
the frozen claim boundary.

### 必须回答的问题

- What deployment object and data-path factor are studied?
- What is the common experimental/correctness boundary?
- What is the principal V2R observation?
- What is the limited V3R observation, including mixed tail behavior?
- What tested conditions limit the conclusion?

### 允许使用的事实

- Preferred title candidate: `Jetson端INT8缺陷检测数据路径优化`.
- Alternate title candidate: `面向Jetson的缺陷检测数据路径优化`.
- V0/V2R/V3R common-boundary comparison.
- V2R accepted task-level correctness and frozen V2R/V0 results.
- V3R limited average increment and mixed P95/P99 direction.
- Frozen Jetson/model/Engine/workload constraints.

### Phase 1 claim IDs

`C1`, `C2`, `C3`; prerequisite context `C4`; limitation/guardrail `C8`, `C9`.

### metric IDs

`M_R_V2R_V0_FPS_RATIO`, `M_R_V2R_V0_LAT_REDUCTION`,
`M_R_V3R_V2R_FPS_INCREASE`, `M_R_V3R_V2R_LAT_REDUCTION`,
`M_R_V3R_V2R_P95_CHANGE`, `M_R_V3R_V2R_P99_CHANGE`.

### 证据文件

- `docs/paper/phase1/PAPER_PHASE1_CLAIM_EVIDENCE_MAP_v1.0.md`
- `docs/paper/phase1/PAPER_PHASE1_METRIC_PROVENANCE_v1.0.csv`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`
- `docs/paper/phase0_5/PAPER_V2R_GATE_D_DISPOSITION_v1.0.md`

### 必需图表

None inside the abstract. Do not use figure/table/equation/reference numbers in
the abstract.

### 论证顺序

Purpose -> frozen comparison method -> primary V2R result -> incremental V3R
result -> bounded conclusion.

### 推荐段落结构

- Chinese abstract: one report-style paragraph with purpose/method/result/
  conclusion functions.
- English abstract: meaning-aligned counterpart, not a word-by-word mechanical
  translation.
- Keywords: 4-6 Chinese terms with one-to-one English counterparts.

### 术语要求

Use `INT8 post-training quantization (PTQ)` at first English use; distinguish
`frame rate (FPS)` from `throughput`; use `mean latency`, `P95 latency`, and
`P99 latency` explicitly.

### 禁止表述

No novelty superlative, universal hardware conclusion, zero-cost quantization
claim, combined cross-stage factor, uniform tail-benefit claim, or product
reliability claim.

### 引用需求

Abstract contains no reference numbers. Title/keyword terms must remain
consistent with L1-L9 literature vocabulary after the search stage.

### 未解决问题

- Final title choice.
- English title wording.
- Final 4-6 keywords.
- Official attachment typography settings: `OFFICIAL_ATTACHMENT_EXTRACTION_PENDING`.

### 完成标准

- Chinese title satisfies the official length rule and has no subtitle.
- Chinese abstract is at least 150 characters, self-contained, third-person,
  and evidence-bounded.
- Chinese/English abstracts and keywords correspond semantically.
- Every number has a Phase 1 metric crosswalk in drafting notes.

### 建议篇幅占比

`7%` (internal planning only).

## 3. Packet: 0 引言

### 写作目标

Motivate the industrial edge-deployment problem, identify the controlled
data-path evidence gap, and state one research question plus exactly two core
contributions.

### 必须回答的问题

- Why can deployment data paths remain important after model/precision choice?
- What do existing industrial detection, TensorRT, GPU preprocessing, and host
  memory studies establish?
- What comparison/evidence boundary is insufficiently addressed for this
  deployment object?
- What does this article measure, and what does it deliberately not study?

### 允许使用的事实

- Engineering deployment positioning and fixed project route.
- Stage Q establishes the INT8 prerequisite.
- Stage R V0/V2R/V3R provides the main same-protocol evidence.
- Stages J/K/P are prior deployment background only.
- The two frozen contributions in the research narrative.

### Phase 1 claim IDs

`C1-C4`, with `C8-C9` for scope/disclosure.

### metric IDs

Use few or no numbers in the introduction. If one bounded result is previewed,
use only IDs already assigned to `C2-C3`; do not create a second result table in
prose.

### 证据文件

- Phase 0 v1.1 contribution assessment and final freeze.
- Phase 1 claim map and final freeze.
- Phase 2 research narrative and literature requirements.

### 必需图表

None.

### 论证顺序

Industrial task -> edge inference constraint -> data-path issue -> literature
gap -> central question -> two contributions -> article structure.

### 推荐段落结构

1. Industrial surface-defect detection and edge inference context.
2. Model/precision deployment work and the remaining host/device path question.
3. Literature gap around common timing/correctness boundaries and tail metrics.
4. Research object/question, two contributions, and scope.

### 术语要求

Define YOLOv8, NEU-DET, TensorRT, PTQ, CUDA, pageable memory, pinned memory,
end-to-end latency, and tail latency on first substantive use.

### 禁止表述

No unsupported priority claim, broad applicability claim, superiority over
unsearched prior methods, or implication that stages form cumulative speedups.

### 引用需求

L1-L9; especially L7 recent 2024-2026 work, L8 target-journal 2023-2026 work,
and primary/official sources for platform APIs.

### 未解决问题

Actual literature entries remain `TODO_SEARCH_AND_VERIFY`; no bibliography is
created by this packet.

### 完成标准

- At least one real source supports every external background assertion.
- Recent and target-journal literature are represented.
- The gap leads directly to the central question.
- Exactly two contributions are stated and match the frozen wording boundary.

### 建议篇幅占比

`13%` (internal planning only).

## 4. Packet: 1 系统对象与问题定义

### 写作目标

Define the frozen deployment object, INT8 data-path components, controlled
variables, and common measurement interval before describing methods.

### 必须回答的问题

- What model, dataset, Engine, platform, input, and runtime are frozen?
- What are V0, V2R, and V3R at a system level?
- Which operations are included/excluded by the common interval?
- Why are J/K/P background and Q prerequisite rather than parallel results?

### 允许使用的事实

- Jetson Orin Nano Super; L4T R36.5; CUDA/TensorRT/OpenCV recorded versions.
- YOLOv8n, 640x640, batch 1, INT8 Engine identity.
- Split-v1/split-v2 counts, unchanged 180-image test set, seed-7 rank result.
- Stage R common boundary and 60/1080/five-process protocol.
- Stage Q accuracy/performance trade-off as prerequisite context.

### Phase 1 claim IDs

`C1`, `C4`, `C8`; background disposition for `C5-C7`; guardrail `C9`.

### metric IDs

`M_TRAIN_SEED7_RANK`, `M_TRAIN_SPLIT_V1_COUNTS`,
`M_TRAIN_SPLIT_V2_COUNTS`, `M_Q_INT8_PRECISION`, `M_Q_INT8_RECALL`,
`M_Q_INT8_MAP50`, `M_Q_INT8_MAP5095`, `M_Q_INT8_MAP5095_DELTA`,
`M_Q_SERIAL_INFERENCE_SPEEDUP`, `M_Q_SERIAL_THROUGHPUT_RATIO`.

The two Q6 metrics are protocol-local Stage Q prerequisite context only. They
must remain separate from Stage R metrics and must not establish an independent
Stage Q result line in Section 4.

### 证据文件

- `docs/paper/phase1/PAPER_PHASE1_EXPERIMENT_MATRIX_v1.0.csv`
- `docs/paper/phase1/PAPER_PHASE1_METRIC_PROVENANCE_v1.0.csv`
- `docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/manifest.json`
- `docs/personal/STAGE_Q_FINAL_REPORT.md`
- `docs/paper/phase0_5/PAPER_DATASET_SPLIT_SENSITIVITY_FINAL_v1.0.md`

### 必需图表

Figure 1; Table 1 is introduced here or at Section 3.1 without duplication.

### 论证顺序

Deployment object -> INT8 prerequisite -> three paths -> common interval ->
research variables/questions.

### 推荐段落结构

- 1.1: model/dataset/platform object and disclosure.
- 1.2: host/device INT8 path and three controlled variants.
- 1.3: timing boundary, included/excluded operations, and subquestions.

### 术语要求

Use `V0`, `V2R`, `V3R` only after first full definitions. Use `pageable host
memory` and `pinned host memory`; do not abbreviate both to generic host memory.

### 禁止表述

No direct J/K/P/R numeric comparison; no statement that V3R overlaps frames;
no silent replacement of historical split-v1 by split-v2; no independent Stage
Q result line in the results section.

### 引用需求

L2-L6 and L9 for external concepts; repository evidence for project-specific
facts.

### 未解决问题

Final Figure 1 visual style and table typography await official attachments.

### 完成标准

- A reader can identify the single factor changed between V2R and V3R.
- Timing start/end and exclusions are unambiguous.
- Dataset history and model selection are disclosed without overclaiming.
- No result interpretation is duplicated from Section 4.

### 建议篇幅占比

`15%` (internal planning only).

## 5. Packet: 2 数据路径优化方法

### 写作目标

Explain the three data paths and their correctness/lifecycle controls at enough
engineering depth for reproduction while preserving backend and evidence
boundaries.

### 必须回答的问题

- How does V0 preprocess and supply TensorRT input?
- How does V2R stage pageable raw data and apply correctness-aligned CUDA
  preprocessing?
- How does V3R change staging memory while retaining the V2R semantic?
- How are geometry, ownership, synchronization, results, and correctness
  checked?

### 允许使用的事实

- Frozen variant definitions in the Phase 1 experiment matrix.
- V2R Gate D contract and four aggregate task metrics.
- V3R tensor/detection digest and lifecycle identity evidence.
- Formal path includes required synchronization and excludes unsupported
  cross-frame behavior.

### Phase 1 claim IDs

`C1-C3`; guardrail `C9`.

### metric IDs

`M_R_V2R_GATE_D_PRECISION`, `M_R_V2R_GATE_D_RECALL`,
`M_R_V2R_GATE_D_MAP50`, `M_R_V2R_GATE_D_MAP5095`.

### 证据文件

- Phase 1 experiment matrix and claim map.
- `docs/paper/phase0_5/PAPER_V2R_GATE_D_DISPOSITION_v1.0.md`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_task_metrics.json`
- `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v3r_identity_check.json`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`

### 必需图表

Figure 1. Table 2 may be referenced at the end of the correctness subsection.

### 论证顺序

Shared contract -> V0 -> V2R isolated change -> V3R isolated change ->
correctness and lifecycle controls.

### 推荐段落结构

- 2.1: V0 sequence and role as baseline.
- 2.2: V2R staging, CUDA preprocessing, TensorRT device input, synchronization.
- 2.3: V3R pinned allocation/ownership and identical preprocessing semantic.
- 2.4: Gate D, identity digests, frame order, zero drop, EOS, and result schema.

### 术语要求

Differentiate preprocessing output semantics from raw memory allocation;
differentiate task-level equality from tensor/digest identity; describe
synchronization where it is part of the measured path.

### 禁止表述

No algorithm novelty claim, no assertion of asynchronous cross-frame execution,
no V4 method subsection, and no universal equivalence statement.

### 引用需求

L3-L5 and L9 for TensorRT/CUDA/memory concepts; repository source authority for
the implemented path.

### 未解决问题

Decide during drafting how much pseudocode is necessary; no code listing is
currently required.

### 完成标准

- Each variant has a reproducible path description.
- V2R/V3R isolated factors are explicit.
- Correctness layers and lifecycle evidence are separated correctly.
- Figure 1 matches the prose and contains no unsupported overlap.

### 建议篇幅占比

`21%` (internal planning only).

## 6. Packet: 3 实验设计

### 写作目标

Make the comparison reproducible by freezing platform/model/data/protocol,
metric definitions, aggregation rules, and validity checks before results.

### 必须回答的问题

- What exact hardware/software/model/Engine/test identities apply?
- How are warmup, measured frames, cycles, processes, and schedule defined?
- How are FPS mean/SD and pooled mean/P95/P99 latency defined?
- How are task correctness and V3R identity assessed?

### 允许使用的事实

- Environment and artifact identities in the formal report/manifest.
- Five interleaved processes per variant; 15 valid processes.
- 60 warmup, 1080 measured, six measured cycles, zero drops, EOS pass.
- FPS sample SD over five run FPS values; pooled 5400-frame latency statistics.
- Type-7 P95/P99 as frozen in Phase 1/formal evidence.

### Phase 1 claim IDs

Evidence contract for `C1-C4`, `C8`.

### metric IDs

All direct `M_R_V0_*`, `M_R_V2R_*`, and `M_R_V3R_*` FPS/SD/latency rows;
four V2R Gate D rows; split count rows.

### 证据文件

- Phase 1 experiment matrix and metric provenance.
- Phase 0.5D formal execution report and compact manifest.
- V2R Gate D task metrics/decision and V3R identity JSON.
- Stage Q final report for prerequisite configuration only.

### 必需图表

Table 1; metric definitions prepare Table 2/Figures 2-3 but do not reveal
result interpretation early.

### 论证顺序

Platform/model -> dataset/replay -> schedule/lifecycle -> timing interval ->
correctness metrics -> performance metrics -> derivation/tolerance rule.

### 推荐段落结构

- 3.1: Table 1 and artifact identities.
- 3.2: dataset, manifest, replay, warmup/measured counts, schedule.
- 3.3: correctness definitions, FPS/latency definitions, aggregation and
  derivation rules.

### 术语要求

Use `sample SD` only for five-run FPS SD; use `pooled` for latency mean/P95/P99;
state units at first definition and in every table/axis.

### 禁止表述

No newly calculated interval estimate or significance test; no substitution of
throughput for FPS; no resource-utilization inference from process CPU time.

### 引用需求

L6 for metric definitions and percentile/latency terminology; L9 for official
runtime semantics; project evidence for actual protocol values.

### 未解决问题

Official formula/table typography remains pending attachment extraction.

### 完成标准

- Table 1 values are traceable to evidence files.
- Every result metric has a definition, unit, sample set, and aggregation.
- Timing exclusions and derivation policy are explicit.
- A reader can reproduce the comparison without consulting stage chronology.

### 建议篇幅占比

`18%` (internal planning only).

## 7. Packet: 4 结果与分析

### 写作目标

Answer the central question once: first establish correctness, then analyze the
primary V2R benefit, the limited V3R increment, and the mixed tail result with
bounded applicability.

### 必须回答的问题

- Did V2R satisfy the accepted task-level correctness contract?
- What main FPS/mean/tail changes occur from V0 to V2R?
- What additional FPS/mean change occurs from V2R to V3R?
- Why does the V3R P95/P99 direction prevent a consistent tail conclusion?
- Which limitations constrain engineering use?

### 允许使用的事实

- Table 2 Gate D metrics/deltas and V3R identity/lifecycle facts.
- Frozen direct FPS/SD and latency mean/P95/P99 values.
- Frozen pairwise ratios/increases/reductions in Phase 1 provenance.
- Five-run/5400-sample aggregation facts and stated evidence limitations.

### Phase 1 claim IDs

`C1-C3`; supporting `C4`, `C8`; guardrail `C9`.

### metric IDs

- Correctness: four `M_R_V2R_GATE_D_*` rows.
- Figure 2: three `*_FPS` and three `*_FPS_SD` rows.
- Figure 3: nine direct `*_LAT_MEAN`, `*_P95`, `*_P99` rows.
- Comparisons: `M_R_V2R_V0_FPS_RATIO`,
  `M_R_V2R_V0_FPS_INCREASE`, `M_R_V2R_V0_LAT_REDUCTION`,
  `M_R_V2R_V0_P95_REDUCTION`, `M_R_V2R_V0_P99_REDUCTION`, and four
  `M_R_V3R_V2R_*` rows.

### 证据文件

- Phase 1 metric provenance and claim map.
- Phase 0.5D formal execution report.
- V2R Gate D compact evidence and V3R identity evidence.
- Phase 1 gap register for limitations.

### 必需图表

Table 2, Figure 2, Figure 3.

### 论证顺序

Correctness gate -> direct absolute values -> V2R/V0 primary comparison ->
V3R/V2R increment -> separate P95/P99 interpretation -> limitations.

### 推荐段落结构

- 4.1: correctness and identity results.
- 4.2: Figure 2/Figure 3 absolute values and V2R/V0 interpretation.
- 4.3: V3R/V2R incremental average metrics.
- 4.4: mixed tail result, boundary conditions, and excluded evidence.

### 术语要求

Use `frame-rate ratio`, `FPS increase`, `mean-latency reduction`, and `latency
change` according to each metric formula. For V3R/V2R P95/P99, state both
direction and magnitude.

### 禁止表述

No cross-stage arithmetic, no all-metric improvement claim, no causal statement
from V4 history, no statistical significance language, and no field/endurance
reliability inference.

### 引用需求

External citations support interpretation/mechanism context only; measured
project values cite the article's own table/figure and retain the internal
metric crosswalk.

### 未解决问题

- Render Figures 2-3 after official attachment requirements are available.
- Decide whether pairwise percentages appear in prose or figure annotations;
  do not duplicate them in both without purpose.

### 完成标准

- Each paragraph answers one subquestion.
- All displayed values pass the Phase 1 metric crosswalk.
- Figure 2 uses only frozen FPS SD.
- P95 and P99 directions are correct and interpreted separately.
- Stage P and V4 values are absent from the result figures.

### 建议篇幅占比

`21%` (internal planning only).

## 8. Packet: 5 结论

### 写作目标

Answer the central question in two evidence-bounded points, state applicable
conditions, and close without introducing new results or a third contribution.

### 必须回答的问题

- What did the controlled V0/V2R/V3R comparison establish?
- What is the main V2R observation?
- What is the limited V3R observation and tail caveat?
- Under which conditions do these answers apply?

### 允许使用的事实

Only facts already established in Sections 1-4 and mapped to `C1-C3`, plus the
guardrail/limitations in `C8-C9`.

### Phase 1 claim IDs

`C1-C3`, `C9`.

### metric IDs

Prefer at most the central `C2-C3` metric IDs; do not repeat every absolute
value or invent a combined summary score.

### 证据文件

Phase 1 claim map/final freeze, Phase 2 claim architecture, and the completed
article Sections 3-4 after crosswalk validation.

### 必需图表

None.

### 论证顺序

Controlled boundary -> main V2R finding -> limited V3R/tail finding -> tested
conditions and future validation needs.

### 推荐段落结构

One compact conclusion section: two result-linked conclusions followed by one
scope/future-work sentence or short paragraph.

### 术语要求

Match the exact metric and variant names used in Section 4. Use conditional
phrasing tied to the tested configuration.

### 禁止表述

No new metric, new contribution, broad deployment recommendation, cumulative
factor, product certification implication, or simple list of all result values.

### 引用需求

Normally no new literature citation; do not cite a source not already discussed
in the article.

### 未解决问题

Final wording waits until Sections 3-4, figures, and literature citations are
complete.

### 完成标准

- Directly answers the central question.
- Contains exactly the two frozen contribution outcomes.
- Preserves mixed tail direction and all tested conditions.
- Introduces no unsupported claim or new number.

### 建议篇幅占比

`5%` (internal planning only).

## 9. Allocation Check

| Packet | Internal allocation |
|---|---:|
| 题名与摘要 | 7% |
| 0 引言 | 13% |
| 1 系统对象与问题定义 | 15% |
| 2 数据路径优化方法 | 21% |
| 3 实验设计 | 18% |
| 4 结果与分析 | 21% |
| 5 结论 | 5% |
| Total | 100% |
