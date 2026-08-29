# Figure 1 native Visio build specification

## Authority and freeze

The sole geometry authority is `figure1_reference.svg`, copied byte-for-byte from the manifest-selected Phase 5.9C SVG. `figure1_geometry.json` is its deterministic native-shape translation. The figure is conceptual: it contains no performance result and no component-level causal claim.

All visible labels, the three path identities (`P₀/V0`, `P₂/V2R`, `P₃/V3R`), the four path variables (`R`, `F`, `M`, `E`), both intervention arrows, both hierarchy statements, domain boundary, warning, fills, strokes, and semantic color roles are frozen.

## Coordinate conversion

The SVG declares `width="160mm"`, `height="79mm"`, and `viewBox="0 0 1600 790"`. Therefore:

```text
x_mm = x_svg / 10
y_mm = y_svg / 10
width_mm = width_svg / 10
height_mm = height_svg / 10
```

The JSON uses a top-left origin with positive y downward. Visio uses a bottom-left page origin and inches internally:

```text
x_visio_in = x_mm / 25.4
y_visio_in = (79 - y_mm) / 25.4
```

For a top-left rectangle `(x,y,w,h)`, its Visio edges are `(x, 79-y-h)` to `(x+w, 79-y)` before conversion to inches. No PNG coordinate is used.

## Native object contract

- Page: metric drawing, exactly `160 mm × 79 mm`.
- Rectangles and rounded rectangles: native Visio shapes with editable fill, stroke, and corner rounding.
- Lines/arrows: native Visio one-dimensional shapes with editable dash and arrowhead cells.
- Text: native text shapes, never outlined or rasterized. The script creates separate transparent text shapes so each label remains directly editable.
- Fonts: final Windows target is SimSun (`宋体`) for Chinese and Times New Roman for Latin. Internal text target is 8 pt under the Phase 7.1 HFUT submission specification. Mixed strings use SimSun as the shape font and retain Latin text as editable text; Windows-side final QA must apply Times New Roman to Latin runs if the installed Visio version exposes mixed-run formatting reliably.
- Colors: preserve exact sRGB hex values from `figure1_geometry.json`. Blue identifies the V2R/path-level intervention family; orange identifies the V3R/staging refinement family; neutral gray identifies shared/baseline structure and the host-device boundary.
- Layer/group metadata: objects receive a `User.SemanticGroup` ShapeSheet cell. Native grouping is intentionally not forced because grouping changes child coordinates in Visio; the semantic memberships remain explicit and can be selected/grouped without loss from the JSON.
- Z-order: creation follows the JSON `z_order` intent: page/domain fields, path shapes and arrows, then text.

## Windows output and visual QA

Run `build_figure1_visio.ps1` from this directory. It must save `Figure1_input_data_path_model.vsdx` here. Compare the full page against both reference previews. Confirm the output is not one imported SVG or raster, and that every rectangle, line, arrow, and text label is individually editable.

The proprietary VSDX is a submission object only. It must not replace the SVG scientific source of record.
