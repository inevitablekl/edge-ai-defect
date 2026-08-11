# Phase 5 Target Caption and Renumbering Map v1.0

Status: `PHASE5_INTEGRATED`. The target numbering and captions in this map are
now current manuscript authority.

Production route: Figure 1 and Figure 2 are accepted `USER_MANUAL` Visio
assets; Figure 3 and Figure 4 are accepted `VSCODE_CODEX` deterministic assets.
All four figures are integrated. Table 1 is integrated from its governed
specification, and the former Tables 1 and 2 are current Tables 2 and 3.

## Figure migration

| Current authority | Target identity | Target caption |
|---|---|---|
| Current Figure 1, implementation paths | Figure 1 | `图1　V0、V2R和V3R数据路径示意` |
| New conceptual asset | Figure 2 | `图2　端到端执行概念组成与受控干预范围` |
| Current Figure 2, mean FPS | Figure 3 | `图3　V0、V2R和V3R平均帧率比较。误差棒表示5次独立进程级运行FPS的样本标准差。` |
| Current Figure 3, latency | Figure 4 | `图4　V0、V2R和V3R平均及尾延迟比较。（a）各路径绝对延迟；（b）V3R相对V2R的冻结变化，其中负值表示降低/更快，正值表示升高/更慢。Mean、P95和P99均基于每种路径合并后的5400个逐帧延迟样本统计。` |

English source captions:

- `Fig. 1 Schematic of the V0, V2R, and V3R data paths.`
- `Fig. 2 Conceptual end-to-end execution composition and controlled intervention scopes.`
- `Fig. 3 Comparison of mean FPS for V0, V2R, and V3R. Error bars indicate the sample standard deviation of FPS across five independent process-level runs.`
- `Fig. 4 Comparison of mean and tail latency for V0, V2R, and V3R. (a) Absolute latency for each path. (b) Frozen V3R changes relative to V2R, where negative means lower/faster and positive means higher/slower. Mean, P95, and P99 are computed from 5,400 pooled per-frame latency samples for each variant.`

## Table migration

| Current authority | Target identity | Target caption |
|---|---|---|
| New controlled-path matrix | Table 1 | `表1　V0、V2R和V3R受控数据路径配置与比较变量` |
| Current Table 1 | Table 2 | `表2　平台、模型、数据集和统一运行协议` |
| Current Table 2 | Table 3 | `表3　V0与V2R任务级正确性验证结果` |

## Completed cross-reference operations

1. Target Figure 2 was inserted in Section 1.3 and target Table 1 near the start of Section 2.
2. Figure 1 publication authority migrated to the accepted Phase 5 manual export while retaining its Section 1.2 implementation-path role.
3. The former Figures 2 and 3 were replaced and renumbered as Figures 3 and 4.
4. The former Tables 1 and 2 were renumbered as Tables 2 and 3 without content changes.
5. Callouts, captions, metadata, manifests, DOCX assembly, postprocessing, and validators were migrated atomically.
