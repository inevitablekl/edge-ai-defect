# Figure 1 Visio Construction Specification v1.0

## 1. Publication identity

- Figure: F1
- Chinese caption: `图1　V0、V2R和V3R数据路径示意`
- English source caption: `Fig. 1 Schematic of the V0, V2R, and V3R data paths.`
- Final authoring owner/tool: USER_MANUAL / Microsoft Visio
- Existing deterministic preview:
  `fig1_v0_v2r_v3r_data_paths.svg`
- Final `.vsdx` and publication export: NOT CREATED

This sheet governs manual construction of the publication figure. The SVG is
a deterministic preview only and must not be presented as the final
publication figure.

## 2. Canvas and reading order

- Use a landscape canvas and a left-to-right reading direction.
- Use three equal-height horizontal lanes ordered from top to bottom: V0, V2R,
  V3R.
- Place the lane identifier at the far left and keep all three paths aligned
  to common vertical columns where their operations are shared.
- Keep sufficient outer margin for the journal's final figure-number and
  caption handling. Set the final width only after the official DOCX template
  width is confirmed.

## 3. Frozen node and arrow content

Use single-headed horizontal arrows between every adjacent node. Do not add
unlisted processing nodes.

### V0 lane

`图像源/解码` → `CPU/OpenCV预处理` → `TensorRT INT8 Engine` →
`后处理/NMS` → `帧结果构造`

### V2R lane

`图像源/解码` → `pageable host staging` → `H2D` → `CUDA预处理` →
`TensorRT INT8 Engine` → `D2H` → `后处理/NMS` → `帧结果构造`

### V3R lane

`图像源/解码` → `pinned host staging` → `H2D` → `CUDA预处理` →
`TensorRT INT8 Engine` → `D2H` → `后处理/NMS` → `帧结果构造`

## 4. Grouping and isolated-variable annotation

- Optionally place a light bracket above the aligned V2R and V3R
  `CUDA预处理` nodes labeled `相同CUDA预处理语义`.
- Optionally place a narrow comparison bracket between the V2R and V3R host
  staging nodes labeled `唯一隔离变量：主机暂存内存类型`.
- Shared-operation boxes must use the same size, border, fill/pattern, and type
  treatment across lanes. In particular, do not style the V3R CUDA node as a
  different algorithm.
- Keep the execution order visually serial within each frame; arrows must not
  bypass, fork around, or loop between nodes.

## 5. Optional common timing boundary

If the timing boundary is shown, use one thin dashed enclosure spanning all
three lanes:

- Start: before `图像源/解码`, immediately before source pull/frame
  acquisition.
- End: after `帧结果构造`, before serialization/write.
- Boundary label: `逐帧外部延迟：source-to-pre-sink`.
- Outside-boundary note: `不含JSON序列化、文件I/O、汇总持久化和digest终结`.

The boundary is optional; omitting it does not change the path definition.

## 6. Monochrome publication treatment

- Design for grayscale printing first. Differentiate the three lane labels by
  text and, if needed, light hatch patterns rather than color alone.
- Use black or dark-gray text and strokes on white; maintain strong contrast
  after grayscale conversion.
- Use one typeface family and consistent node dimensions. Keep English memory
  and transfer terms unbroken where practical.
- Use solid arrows for the data path and reserve dashed strokes only for an
  optional timing boundary or explanatory bracket.
- Avoid gradients, shadows, bevels, decorative icons, and 3D effects.

## 7. Forbidden visual elements and implications

The final figure must not depict or imply:

- V4 or any historical Attempt 2 path;
- double buffering;
- zero-copy or mapped memory;
- cross-frame overlap or a pipeline;
- multi-stream inference;
- asynchronous transfer/inference overlap;
- a second CUDA preprocessing algorithm for V3R;
- a change to the TensorRT Engine between variants.

All three tested paths retain the frozen single-frame sequential execution
semantics.

## 8. Manual completion checklist

- [ ] Three lanes appear in V0, V2R, V3R order.
- [ ] Every label and arrow matches Section 3 exactly.
- [ ] V2R and V3R CUDA preprocessing is visually identical.
- [ ] Only pageable versus pinned host staging is highlighted for V2R→V3R.
- [ ] Any timing boundary uses the inclusion/exclusion rules in Section 5.
- [ ] Grayscale print preview is legible.
- [ ] Final Visio source remains editable.
- [ ] Publication export is visually inspected at final placement size.

## 9. Authority

- `docs/paper/manuscript/sections/03_method.md`
- `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths_spec.md`
- `docs/paper/phase1/PAPER_PHASE1_CLAIM_EVIDENCE_MAP_v1.0.md`
