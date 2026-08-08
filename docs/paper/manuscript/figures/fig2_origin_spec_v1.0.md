# Figure 2 Origin Plotting Specification v1.0

## 1. Publication identity

- Figure: F2
- Figure type: ordinary vertical bar chart with Y error bars
- Final authoring owner/tool: USER_MANUAL / Origin
- Authoritative import data: `fig2_mean_fps_origin_data.csv`
- Existing deterministic preview: `fig2_mean_fps.svg`
- Final Origin project and publication export: NOT CREATED

The CSV contains accepted three-decimal display values. Do not replace them
with recalculated or higher-precision values during plotting.

## 2. CSV column assignment

| CSV column | Origin designation | Meaning |
|---|---|---|
| `Variant` | X, categorical | V0, V2R, V3R in this order |
| `Mean_FPS` | Y | Mean of five independent process-level FPS samples |
| `Sample_SD_FPS` | Y Error | Sample standard deviation of the same five FPS samples |

## 3. Plot construction

1. Import the CSV without numeric transformation or automatic recalculation.
2. Set `Variant` as categorical X in the preserved V0, V2R, V3R order.
3. Plot `Mean_FPS` as one ordinary vertical-bar series.
4. Attach `Sample_SD_FPS` as symmetric Y error bars.
5. Set the Y-axis title to `FPS`.
6. Set the Y-axis lower bound to exactly 0. Use a linear, unbroken axis and an
   upper bound that leaves the V3R error bar and optional labels unobstructed.

## 4. Labels, legend, and statistical note

- Recommended data labels: show each mean above its bar with exactly three
  decimals: `54.600`, `122.122`, `127.097`.
- A legend is unnecessary because the X labels identify all bars. If the
  publication template requires one, use only `平均FPS` and do not encode an
  additional grouping variable.
- Required error-bar meaning: the sample standard deviation of FPS across five
  independent runs. It is descriptive and must not be relabeled as another
  uncertainty measure or used for an inferential annotation.
- It is not a confidence interval, standard error, population standard
  deviation, or significance interval.
- Do not add comparison brackets, significance markers, p-values, or
  decorative 3D effects.

## 5. Publication styling and export

- Prefer one grayscale-safe fill treatment with black error-bar caps; do not
  rely on color to identify variants.
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
`figure_captions_v1.0.md`. The error-bar sentence must remain attached to the
caption or figure note.

## 7. Authority

- `docs/paper/phase1/PAPER_PHASE1_METRIC_PROVENANCE_v1.0.csv`
- `docs/paper/phase3/PAPER_PHASE3_SECTION4_RESULT_DATA_v1.0.csv`
- `docs/paper/manuscript/sections/04_experiment.md`
- `docs/paper/manuscript/sections/05_results.md`
