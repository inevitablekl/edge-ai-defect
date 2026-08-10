# Paper Phase 5.4C Manual Production Package v1.0

Status: `READY_FOR_MAIN_AI_REVIEW`; manual production must wait for review acceptance.

## 1. Files to produce

| Target | Tool/owner | Start from | Data authority | Deliverables |
|---|---|---|---|---|
| F1 implementation paths | Microsoft Visio / USER_MANUAL | `fig1_v0_v2r_v3r_data_paths_final.vsdx` | current path implementation + `fig1_visio_spec_v2.0_phase5.md` | `fig1_v0_v2r_v3r_data_paths_phase5_final.vsdx/.pdf/.svg` |
| F2 conceptual scopes | Microsoft Visio / USER_MANUAL | `fig2_e2e_intervention_scope_preview.svg` as layout reference; rebuild with native shapes | `fig2_e2e_intervention_scope_visio_spec_v1.0.md` | `fig2_e2e_intervention_scope_final.vsdx/.pdf/.svg` |
| F3 mean FPS | Origin / USER_MANUAL | new OPJU | `fig2_mean_fps_origin_data.csv` | `fig3_mean_fps_phase5_final.opju/.pdf/.svg/.png` |
| F4 latency | Origin / USER_MANUAL | new OPJU | `fig3_mean_tail_latency_origin_data.csv`; `fig4_v3r_v2r_latency_change_origin_data.csv` | `fig4_mean_tail_latency_phase5_final.opju/.pdf/.svg/.png` |

Do not overwrite current accepted sources/exports. Return candidate files for review under the intended filenames; repository authority changes only in a later integration task.

## 2. Shared styling

- V0: white, no hatch, solid black outline.
- V2R: white, diagonal hatch, solid black outline.
- V3R: white, cross-hatch, solid black outline.
- Equal luminance/weight; identity only, never better/worse.
- Chinese `宋体`, Latin/digits `Times New Roman` where available; effective print size at least `7.5 pt`.
- White background; no gradient, 3D, shadow, glossy decoration, or reliance on color.

## 3. Visio checklist

### F1

- Preserve the accepted execution topology and all frozen path semantics.
- Align three lanes and visually match shared stages.
- Show V2R/V3R CUDA nodes identically.
- Highlight only pageable versus pinned host raw staging for V2R→V3R.
- If shown, use one common end-to-end timing boundary; do not show independent stage measurements.
- Exclude zero-copy, mapped memory, double buffer, multi-stream, overlap, pipeline, GPU NMS, and a second CUDA algorithm.

### F2

- Use exactly the six component labels and two scope annotations from the spec.
- Include verbatim: `较宽/较窄仅描述受控变量覆盖的结构与配置范围，不表示 Amdahl α 大小，也不预测实际加速比。`
- Scope bands must have neutral equal-weight styling.
- Do not insert performance results or measured-stage notation.

For both figures, verify that SVG/PDF labels match the VSDX and that all shapes remain editable in the returned VSDX.

## 4. Origin checklist

### F3

- Import, do not retype/recalculate, the authoritative CSV.
- Values: `54.600±0.223`, `122.122±0.492`, `127.097±1.279` FPS.
- Error bars mean sample SD across five independent process-level runs only.
- Use a zero baseline and the shared variant encoding.

### F4

- Panel A exact values: V0 `18.273/18.854/19.068`; V2R `8.140/9.827/11.529`; V3R `7.812/9.842/11.515` ms for Mean/P95/P99.
- Panel B exact changes: Mean `-4.0349%`; P95 `+0.1514%` higher/slower; P99 `-0.1184%` lower/faster.
- Use explicit zero, symmetric `-5%` to `+5%`, and the label `负值=降低/更快；正值=升高/更慢`.
- Ensure the figure visibly supports `tail = MIXED`, not consistent improvement.

No broken axis, zoom inset, CI, SE, p-value, significance bracket, causal label, or derived/recomputed precision is allowed.

## 5. Export and return checks

For each figure:

1. Open the editable source and confirm every object/plot remains editable.
2. Export vector PDF and SVG; export PNG only for Origin print review.
3. Confirm fonts are embedded/outlined or render identically on a second machine.
4. Inspect at 100% and at intended journal column width in grayscale.
5. Confirm no clipping, overlapping text, missing hatch, rasterized labels, or substituted glyphs.
6. Compare all text and numbers character-for-character with the governing spec/CSV.
7. Report tool/version, page size, export settings, and any font substitution.
8. Do not insert the candidates into the manuscript or rename them over current accepted assets.

## 6. Table and integration handoff

USER_MANUAL does not need to create a separate table artwork file. After visual acceptance, the later integration task will materialize `table1_controlled_path_matrix_spec_v1.0.md` as a native three-line Word table, then apply the caption/renumbering map atomically to Full and Anonymous builds.
