# Target Figure 4 Origin Specification v2.0

Status: `PHASE5_PREPARATION_ONLY`; final production owner: `USER_MANUAL_ORIGIN`.

## Recommendation

Use a two-panel figure. Panel A preserves absolute magnitude and comparability with the current grouped-bar figure. Panel B exposes the frozen V3R/V2R directions around an explicit zero without a broken axis or magnifying inset. A symmetric `-5%` to `+5%` range keeps the 4.0349% mean change and the near-zero tail changes on one honest scale; exact labels preserve the small mixed-tail directions without implying significance.

## Panel A: absolute latency

Authority: `fig3_mean_tail_latency_origin_data.csv`, imported without recalculation.

| Statistic | V0 (ms) | V2R (ms) | V3R (ms) |
|---|---:|---:|---:|
| Mean | 18.273 | 8.140 | 7.812 |
| P95 | 18.854 | 9.827 | 9.842 |
| P99 | 19.068 | 11.529 | 11.515 |

- X groups: Mean, P95, P99. Within each group: V0, V2R, V3R.
- Y title: `延迟/ms`; start at zero; no error bars or inferential annotation.
- Shared variant identity: V0 white/no hatch; V2R white/diagonal hatch; V3R white/cross-hatch, with equal outlines/luminance.

## Panel B: frozen V3R relative to V2R changes

Authority: `fig4_v3r_v2r_latency_change_origin_data.csv`.

| Metric | Change (%) | Required reading |
|---|---:|---|
| Mean | -4.0349 | lower/faster |
| P95 | +0.1514 | higher/slower |
| P99 | -0.1184 | lower/faster |

- Plot three neutral bars about an explicit horizontal zero line.
- Y title: `V3R相对V2R的延迟变化/%`; fixed symmetric range `-5` to `+5`.
- State near the axis: `负值=降低/更快；正值=升高/更慢`.
- Exact visible labels must retain sign and four decimals.
- All Panel B bars use the same neutral style because they are metrics from the same V3R/V2R comparison, not separate variants.
- Do not use green/red, improvement arrows, significance symbols, CI, p-values, zoom inset, or causal mechanism labels.

The mandatory interpretation is `mean improves; P95 is slightly higher/slower; P99 is slightly lower/faster; tail = MIXED`. Panel B must not be captioned as a consistent latency improvement.

Target caption: `图4　V0、V2R和V3R平均及尾延迟比较。（a）各路径绝对延迟；（b）V3R相对V2R的冻结变化，其中负值表示降低/更快，正值表示升高/更慢。Mean、P95和P99均基于每种路径合并后的5400个逐帧延迟样本统计。`

Target outputs: `fig4_mean_tail_latency_phase5_final.opju`, `.pdf`, `.svg`, and print-review `.png`. These remain candidates until later acceptance/integration.
