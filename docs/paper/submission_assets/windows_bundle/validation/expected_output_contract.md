# Expected Windows output contract

## Global acceptance

- Input bundle SHA256 verification passes before build.
- No scientific number, label, path order, aggregation rule, or interpretation changes.
- No Linux absolute path appears in a Windows script or generated project.
- Reference SVG/PNG assets remain visual references only and are not inserted as the sole graph/page object.
- Chinese text uses SimSun and Latin text uses Times New Roman at the specified target sizes.
- Native output previews are visually compared against both corresponding reference files.
- The output objects are inserted manually into the user's submission Word document; the scientific Word master is not rebuilt or modified.

## F1 — `Figure1_input_data_path_model.vsdx`

- Page is 160 mm × 79 mm (approximately the accepted 16 cm full-width geometry).
- Host domain, device domain, host-device boundary, all rectangles, five arrows/lines, and every text label are native Visio objects.
- Individual text, rectangles, line styles, arrowheads, and fills remain editable.
- The VSDX is not one embedded SVG, one image, a renamed archive, or a raster-only page.
- Exact labels include `P₀ / V0`, `P₂ / V2R`, `P₃ / V3R`, every `R/F/M/E` value, both hierarchy statements, and the full warning.
- `P₀ → P₂` changes `R、F、M` with `E` fixed; `P₂ → P₃` changes only `M` from Pageable to Pinned.
- Blue/orange/neutral colors retain their frozen semantic roles.

## F2 — `Figure2_E2E_performance.opju`

- OPJU contains native worksheets with the exact F2 aggregate data and native graph layers/plots.
- Three vertically stacked native layers are present.
- Panel (a): V0/V2R/V3R FPS mean and sample SD over five independent processes per path.
- Panel (b): pooled mean E2E latency for 5400 samples per path.
- Panel (c): pooled P95/P99 comparison with V0/V2R/V3R series.
- All axes, labels, error bars, bars, legends, annotations, and panel labels are native/editable.
- Accepted display strings include `54.600`, `122.122`, `127.097`, `18.273`, `8.140`, `7.812`, `2.24×`, `+4.07%`, `−55.45%`, and `−4.03%`.
- The page width is 66.4942 mm and remains below the 75 mm single-column limit.

## F3 — `Figure3_run_level_distribution.opju`

- OPJU contains a native worksheet with all 15 frozen process rows in execution order and native graph layers/plots.
- Two vertically stacked native layers are present.
- Panel (a): all five process-level FPS points per path plus mean/sample-SD summary marks.
- Panel (b): all V2R/V3R process-level mean/P95/P99 descriptors.
- Horizontal offsets only distinguish points and do not imply pairing.
- Tail annotation is exactly `P95 +0.15%; P99 −0.12%` and `方向相反` at accepted publication precision.
- All axes, symbols, error bars, legends, annotations, and panel labels are native/editable.
- The page width is 64.9956 mm and remains below the 75 mm single-column limit.

## Final human inspection

Open each VSDX/OPJU, select representative text/shape/data-plot objects individually, verify native worksheet cells against the CSV, export previews, compare them to the references, and save. Any Origin/Visio version-specific style repair must be presentation-only and must follow the JSON specification exactly.
