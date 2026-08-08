# Figure 3 Origin Plotting Specification v1.0

## 1. Publication identity

- Figure: F3
- Figure type: grouped vertical bar chart
- Final authoring owner/tool: USER_MANUAL / Origin
- Authoritative import data: `fig3_mean_tail_latency_origin_data.csv`
- Existing deterministic preview: `fig3_mean_tail_latency.svg`
- Final Origin project and publication export: NOT CREATED

The CSV contains accepted three-decimal display values. Do not replace them
with recalculated or higher-precision values during plotting.

## 2. CSV mapping and mechanical reshape

The authoritative import layout is:

| CSV column | Meaning |
|---|---|
| `Variant` | Series identity: V0, V2R, V3R |
| `Mean_ms` | Pooled mean latency in ms |
| `P95_ms` | Pooled Type-7 P95 latency in ms |
| `P99_ms` | Pooled Type-7 P99 latency in ms |

For the required grouping, mechanically transpose/reshape the imported values
inside Origin to this plotting worksheet without applying a formula:

| Statistic (X) | V0 (Y) | V2R (Y) | V3R (Y) |
|---|---:|---:|---:|
| Mean | 18.273 | 8.140 | 7.812 |
| P95 | 18.854 | 9.827 | 9.842 |
| P99 | 19.068 | 11.529 | 11.515 |

The reshape changes only orientation, not values or statistical definitions.

## 3. Plot construction

1. Use `Mean`, `P95`, and `P99` as the categorical X groups in that order.
2. Within every group, plot the series in the order V0, V2R, V3R.
3. Set the Y-axis title to `Latency / ms`.
4. Set the Y-axis lower bound to exactly 0. Use a linear, unbroken axis.
5. Use one legend ordered V0, V2R, V3R.
6. Do not attach error bars to any series.

If data labels are used, display exactly three decimals and place them without
overlap. Labels must not introduce pairwise percentages.

## 4. Statistical and anti-exaggeration rules

- Mean, P95, and P99 are each computed from the pooled 5,400 per-frame latency
  samples for the corresponding variant.
- The three bars are distinct pooled statistics, not uncertainty intervals.
- Do not add confidence intervals, standard errors, significance markers,
  p-values, or comparison brackets.
- Do not use a broken axis, a zoomed inset, a magnified panel, or a secondary
  axis to emphasize the V2R/V3R tail differences.
- Preserve the mixed-tail interpretation: V3R P95 is slightly higher/slower
  than V2R, while V3R P99 is slightly lower/faster. The figure must not imply a
  consistent V3R tail-latency improvement.
- Avoid decorative 3D effects.

## 5. Publication styling and export

- Use three grayscale-safe fills/patterns that remain distinguishable in every
  group; do not rely on color alone.
- Keep gridlines minimal and lighter than axes/data.
- Match the manuscript typeface where Origin supports it; verify symbol and
  Chinese-font embedding after export.
- Preserve an editable Origin project during the USER_MANUAL step.
- Export a vector format accepted by the final DOCX workflow (prefer EMF for
  editable Windows/Word placement, with PDF/SVG as review copies if supported).
  Also create a journal-compliant raster export only after official DPI and
  width requirements are known.
- Inspect the final export at its actual manuscript placement size.

## 6. Caption source

Use the authoritative Chinese and English caption text in
`figure_captions_v1.0.md`. The pooled-sample sentence must remain attached to
the caption or figure note.

## 7. Authority

- `docs/paper/phase1/PAPER_PHASE1_METRIC_PROVENANCE_v1.0.csv`
- `docs/paper/phase3/PAPER_PHASE3_SECTION4_RESULT_DATA_v1.0.csv`
- `docs/paper/manuscript/sections/04_experiment.md`
- `docs/paper/manuscript/sections/05_results.md`
