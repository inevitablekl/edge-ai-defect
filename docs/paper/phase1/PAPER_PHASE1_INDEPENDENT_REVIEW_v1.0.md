# Paper Phase 1 Independent Review Report

## 1. Verdict

**PASS**

当前五份 Phase 1 修订稿已经达到：

`PHASE_1_FREEZE_READY`

允许进入：

- Paper Phase 1 Final Freeze
- Paper Phase 2 Writing Preparation

本次复核未发现数据错误、核心 provenance 缺失、claim 越界、实验分类错误或需要新增实验的问题。

---

## 2. Review Scope

本次独立复核覆盖：

- `PAPER_PHASE1_EXPERIMENT_MATRIX_v1.0_DRAFT.csv`
- `PAPER_PHASE1_METRIC_PROVENANCE_v1.0_DRAFT.csv`
- `PAPER_PHASE1_CLAIM_EVIDENCE_MAP_v1.0_DRAFT.md`
- `PAPER_PHASE1_GAP_REGISTER_v1.0_DRAFT.md`
- `PAPER_PHASE1_EVIDENCE_FREEZE_REPORT_v1.0_DRAFT.md`
- Paper Phase 1 Review Remediation Result
- F1–F6 原始审查发现及其修订结果
- 材料中引用的 Phase 0 v1.1 与 Phase 0.5 authority 边界

本轮重点复核：

1. Gate D provenance；
2. V3R metric ownership；
3. metric-to-claim crosswalk；
4. C2 correctness evidence；
5. G7 affected-claim 映射；
6. K Raw Level B FAIL 的保留方式；
7. metric、experiment 和 evidence-status 统计同步；
8. Phase 1 freeze readiness。

本报告完成的是所提供五份文件的内容级独立审查。仓库文件物理存在性及 SHA256 的再次命令行计算未在本审查环境中重新执行，其状态依据提供的 Codex 自动检查和冻结 authority 记录。

---

## 3. Critical Findings

| ID | Finding | Severity | Status |
|----|----|----|----|
| F1 | Gate D 四项任务级指标已改为 Level 1 compact JSON provenance，并提供精确 JSON 字段、commit 和 SHA256。 | NONE | CLOSED |
| F2 | 所有 V3R 相对 V2R 的派生指标已统一归属 `R_V3R`。 | NONE | CLOSED |
| F3 | V3R/V0 四项指标已从 C2 移除并正确映射至 C1。 | NONE | CLOSED |
| F4 | C2 已显式列出四条 Gate D metric ID，metric 行亦反向支持 C2。 | NONE | CLOSED |
| F5 | G7 已移除错误的 C8 映射，并覆盖 C1、C2、C3、C4、C5、C7。 | NONE | CLOSED |
| F6 | K Raw Level B `FAIL` 已保留为 C6 limitation evidence，只有正向 raw/bitwise equivalence claim 被排除。 | NONE | CLOSED |
| F7 | Experiment、metric、status 和 reproducibility 统计已同步。 | NONE | CLOSED |
| F8 | 未发现新的 claim 越界、跨阶段 speedup 乘法或工业产品级范围膨胀。 | NONE | CLOSED |

当前：

- `BLOCKER`: 0
- `MAJOR`: 0
- `MINOR`: 0
- Open finding: 0

---

## 4. Evidence Integrity Review

### 4.1 Evidence Authority Review

**Result: PASS**

确认以下 authority 边界继续成立：

- Phase 0 v1.1 是当前治理与证据范围 authority。
- Phase 0.5 formal、compact 和 verified raw archive 支撑 Stage R 正式结果。
- Frozen PT 被记录为 `VERIFIED_EXTERNAL_ASSET`，未被描述为 Git-tracked asset。
- Historical matched-control absolute metrics 仍为 `SUMMARY_ONLY`。
- Historical R Attempt 2 未进入正式性能聚合。
- V4 formal performance、Pareto、double-buffer overlap 和 causal OOM claim 均保持排除。
- K Raw Level B `FAIL` 是已验证失败证据，不是 `CONFLICTED`，也未被从审计链中删除。

未发现历史失效证据被提升为正式 paper claim。

### 4.2 Experiment Matrix

**Result: PASS**

实验矩阵共 16 行，分类正确：

- `INCLUDE`: 2
  - `R_V0`
  - `R_V2R`
- `INCLUDE_WITH_LIMITATION`: 2
  - `R_V3R`
  - `K_TRT_FP16`
- `SUPPORTING_ONLY`: 9
- `EXCLUDE`: 3
- `REMEDIATION_REQUIRED`: 0

确认：

- `experiment_id` 未发现重复。
- 每个 experiment 均具有 evidence、paper role、allowed claim、prohibited claim 和 limitation。
- Stage R V0/V2R/V3R 是核心同协议对比。
- K、Q、P、J、Training 和 ONNX 保持 supporting 或 boundary evidence。
- 未将 J/K/Q/P/R 合并为单一 benchmark。
- 未形成跨阶段总加速倍率。
- Pipeline 仅支持 throughput。
- V4 不支持 overlap 或 double-buffer claim。

### 4.3 Metric Provenance

**Result: PASS**

#### Gate D provenance

四条 Gate D 指标现已具有有效的 Level 1 来源：

| Metric ID | Source field |
|---|---|
| `M_R_V2R_GATE_D_PRECISION` | `metrics.v2r.precision` |
| `M_R_V2R_GATE_D_RECALL` | `metrics.v2r.recall` |
| `M_R_V2R_GATE_D_MAP50` | `metrics.v2r.mAP50` |
| `M_R_V2R_GATE_D_MAP5095` | `metrics.v2r.mAP50_95` |

共同来源：

`docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_task_metrics.json`

记录 SHA256：

`910c81dd3cd1f1749377cfb632f0a3471615949c70bf1f863edbf18def6e7a2e`

原先错误引用 FPS/latency 字段的问题已经关闭。

#### Metric ownership

以下全部归属 `R_V3R`：

- `M_R_V3R_V2R_FPS_INCREASE`
- `M_R_V3R_V2R_LAT_REDUCTION`
- `M_R_V3R_V2R_P95_CHANGE`
- `M_R_V3R_V2R_P99_CHANGE`

ownership 规则现已一致。

#### Claim mapping

V3R/V0 指标现在支持 C1：

- `M_R_V3R_V0_FPS_RATIO`
- `M_R_V3R_V0_LAT_REDUCTION`
- `M_R_V3R_V0_P95_REDUCTION`
- `M_R_V3R_V0_P99_REDUCTION`
- `M_R_V3R_V0_FPS_INCREASE`

它们不再错误支持仅描述 V2R/V0 的 C2。

#### Counts

Metric 总数：

`87`

Evidence status：

- `VERIFIED`: 43
- `DERIVED_VERIFIED`: 40
- `SUMMARY_ONLY`: 1
- `MISSING`: 2
- `EXCLUDED`: 1
- `CONFLICTED`: 0

总和：

`43 + 40 + 1 + 2 + 1 = 87`

Experiment metric counts：

- `R_V2R`: 14
- `R_V3R`: 14

完整 experiment row count 总和为 87，与 CSV 总行数一致。

Reproducibility：

- `yes`: 83
- `no`: 4

四个 `no` 分别对应：

- missing training archive；
- summary-only sensitivity metrics；
- missing J5.5 per-frame latency；
- excluded V4 metric。

统计同步通过。

### 4.4 Claim–Evidence Map

**Result: PASS**

#### C1

C1 正确保留为：

- V0/V2R/V3R common-boundary ablation；
- frozen Jetson/model/workload；
- Stage R tested path；
- bounded CUDA preprocessing observation。

V3R/V0 指标已经正确纳入 C1。

C1 未声称：

- CUDA preprocessing universally dominates；
- 跨硬件普适；
- total-system acceleration；
- V3R 独立通过 Gate D。

#### C2

C2 已完整闭环。

C2 显式引用：

- `M_R_V2R_GATE_D_PRECISION`
- `M_R_V2R_GATE_D_RECALL`
- `M_R_V2R_GATE_D_MAP50`
- `M_R_V2R_GATE_D_MAP5095`
- `M_R_V2R_V0_FPS_RATIO`
- `M_R_V2R_V0_LAT_REDUCTION`
- `M_R_V2R_V0_FPS_INCREASE`
- `M_R_V2R_V0_P95_REDUCTION`
- `M_R_V2R_V0_P99_REDUCTION`

correctness 已严格限定为：

> accepted task-level Gate D

未扩大为：

- raw tensor equivalence；
- bitwise equivalence；
- universal correctness；
- total-system acceleration。

#### C3

C3 正确表述：

- FPS：`+4.0738%`
- Mean latency：`-4.0349%`
- P95：`+0.1514%`，略有恶化
- P99：`-0.1184%`，略有改善
- Tail conclusion：mixed

未出现：

- “P95/P99 both worse”
- “tail latency improved”
- “V3R improves every latency metric”

#### Supporting claims

C4–C8 保持 supporting 或 limitation-aware claim，没有升级为核心创新。

C9 正确保留：

- Attempt 2 exclusion；
- V4 exclusion；
- cross-stage multiplication prohibition。

### 4.5 Gap Register

**Result: PASS**

九个 gap 的 category、impact、disposition、paper treatment 和 remediation decision 均已闭合。

确认：

- 无 `CORE_BLOCKER`。
- 无 `remediation_required=YES`。
- Frozen PT 保持 external verified asset。
- Historical archive 缺失属于 accepted limitation。
- K Raw Level B FAIL 保留为 limitation。
- J5.5 不支持 per-frame latency。
- Thermal/resource telemetry 不支持 power、no-throttle 或 industrial reliability claim。
- Stage R 不被解释为 endurance 或 power campaign。
- Attempt 2 和 V4 保持 excluded。

G7 已正确关联：

- C1
- C2
- C3
- C4
- C5
- C7

C8 已被正确移除。

C6 未纳入 G7，并明确给出理由：当前审阅 authority 未建立独立 Stage K thermal/resource gap。该处理符合“不凭空扩展 limitation”的审查原则。

### 4.6 Evidence Freeze Report

**Result: PASS**

Freeze Report 已同步：

- 87 条 metric；
- `R_V2R=14`；
- `R_V3R=14`；
- status count；
- reproducibility count；
- Gate D crosswalk；
- V3R tail direction；
- G7 mapping；
- K Raw Level B FAIL 语义。

第 7 节现已明确区分：

- 被排除的是 positive raw-equivalence、bitwise-equivalence 和 raw-output-equality-passed claims；
- verified Stage K Raw Level B `FAIL` 本身继续作为 C6 limitation evidence 保留。

该表述消除了原有歧义。

---

## 5. Numerical Verification

### Stage R direct metrics

| Metric | Confirmed value |
|---|---:|
| V0 FPS | 54.5999763574 FPS |
| V0 mean latency | 18.2729918109 ms |
| V2R FPS | 122.1221922222 FPS |
| V2R mean latency | 8.1402787896 ms |
| V3R FPS | 127.0972584510 FPS |
| V3R mean latency | 7.8118285628 ms |

### V2R versus V0 FPS ratio

\[
\frac{122.1221922222}{54.5999763574}
=2.2366711557
\]

确认：

- FPS ratio：`2.236671x`
- FPS increase：`123.6671%`

### V2R versus V0 mean-latency reduction

\[
\frac{18.2729918109-8.1402787896}
{18.2729918109}\times100
=55.4518555371\%
\]

确认：

- Mean latency reduction：`55.4519%`

### V3R versus V2R FPS gain

\[
\left(
\frac{127.0972584510}{122.1221922222}-1
\right)\times100
=4.0738428768\%
\]

确认：

- FPS gain：`+4.0738%`

### V3R versus V2R mean-latency reduction

\[
\frac{8.1402787896-7.8118285628}
{8.1402787896}\times100
\approx4.0349\%
\]

确认：

- Mean latency reduction：`4.0349%`

### V3R tail behavior

P95：

\[
\frac{9.84201130-9.82713435}
{9.82713435}\times100
=+0.1513864517\%
\]

结论：

- P95 latency 略有增加；
- P95 略有恶化。

P99：

\[
\frac{11.51533580-11.52898548}
{11.52898548}\times100
=-0.1183944591\%
\]

结论：

- P99 latency 略有降低；
- P99 略有改善。

最终表述：

> V3R shows mixed tail latency behavior: P95 is slightly worse, while P99 is slightly better.

### K Raw Level B

确认：

- Raw Level B：`FAIL`
- Evidence status：`VERIFIED`
- Task-level acceptance：PASS
- Raw tensor equivalence：FAIL

两者属于不同 correctness layer，可以同时成立。

---

## 6. Scope Control Review

**Result: PASS**

项目没有发生从论文级工程研究向工业产品级验证的范围膨胀。

当前文件没有要求：

- 更多硬件平台；
- 更多模型；
- 工业生产线验证；
- 百万帧 endurance test；
- 多 GPU；
- 云端部署；
- 商业系统设计；
- 工业可靠性认证；
- 重做 V4 overlap；
- 补做新的 Stage K/Q/P/R 实验。

所有现存 limitation 均通过论文披露、claim 限定或 evidence exclusion 处理，不需要新增实验。

### Automatic prohibited-claim checks

| Check | Result |
|---|---|
| J × K × Q × P × R speedup multiplication | PASS — 未作为正式结论出现 |
| “total acceleration” | PASS — 仅作为禁止表述出现 |
| “lossless INT8” | PASS — 明确禁止 |
| “bitwise FP16 equivalence” | PASS — 明确禁止 |
| “Pipeline reduces latency” | PASS — Pipeline 仅支持 throughput |
| “V4 proves double-buffer overlap” | PASS — V4 claim 已排除 |
| “V3R uniformly improves tail latency” | PASS — 明确记录 mixed result |

---

## 7. Remaining Limitations

以下内容不是 Phase 1 blocker，但必须在论文中继续披露：

1. Frozen PT 是外部 verified asset，不是 Git-tracked repository asset。
2. Historical raw checkpoint archive 当前无法在本机重新检查。
3. Historical matched-control absolute metrics 仅为 `SUMMARY_ONLY`。
4. Stage K 没有单一 dedicated final report，需要联合引用 K5/K6/K7/K8 authority。
5. Stage K Raw Level B tensor equivalence 是 verified FAIL。
6. Task-level acceptance 不等于 raw-output 或 bitwise equivalence。
7. J5.5 不提供 per-frame latency distribution。
8. J5.5 whole-process FPS 与 J5.6 pre-sink FPS 不得混用。
9. Stage P 与 Q Pipeline 仅支持 throughput，不支持 single-frame latency reduction。
10. Stage R 是 common-boundary performance ablation，不是 endurance、power 或 field-reliability campaign。
11. Thermal/resource telemetry 不完整，不能支持 no-throttle、power-efficiency 或 industrial reliability claim。
12. V3R 增益有限，且 tail latency 呈 mixed behavior。
13. V3R 没有独立 Gate D，其 correctness identity 依赖共享 digest 和 lifecycle evidence。
14. Historical Attempt 2 与 V4 不得进入正式 aggregation。
15. J/K/Q/P/R 的 ratio 不得相乘形成 total-system acceleration。

---

## 8. Freeze Decision

**Phase 1 Freeze: AUTHORIZED**

本轮确认：

- F1–F6 全部关闭；
- 关键数值正确；
- provenance 可定位；
- claim crosswalk 完整；
- experiment classification 正确；
- Gap Register 无 remediation blocker；
- historical invalid evidence 保持排除；
- paper wording 边界充分；
- 无需新增实验；
- 无工业产品级范围膨胀。

因此当前证据已经足以支撑一篇：

- 证据真实；
- 指标可追溯；
- 实验边界明确；
- 结论不过度；
- 具有可复现工程价值；

的电子信息硕士工程应用型论文。

最终状态：

`PHASE_1_FREEZE_READY`

允许执行：

1. 将五份 `v1.0_DRAFT` 文件转为正式冻结版本；
2. 将 Evidence Freeze Report 的 verdict 更新为最终冻结状态；
3. 保存本 Independent Review Report；
4. 进入 `Paper Phase 2 Writing Preparation`。

不需要再次进行证据修订或实验补充。
