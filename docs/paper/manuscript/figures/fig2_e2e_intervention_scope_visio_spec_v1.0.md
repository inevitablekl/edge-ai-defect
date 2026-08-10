# Target Figure 2 Visio Specification v1.0

Status: `PHASE5_PREPARATION_ONLY`; final production owner: `USER_MANUAL_VISIO`.
The SVG named below is a deterministic non-final preview, not publication artwork.

## Purpose and placement

- Target caption: `图2　端到端执行概念组成与受控干预范围`
- English source caption: `Fig. 2 Conceptual end-to-end execution composition and controlled intervention scopes.`
- Intended location: Section 1.3, after the conceptual decomposition and before the implementation-specific method.
- Purpose: connect common end-to-end composition, intervention coverage, and the two controlled comparisons. The boxes are conceptual components, not independently measured stage times.

## Page and layout

- Landscape, approximately `2.30:1`; white background; no visible figure title inside the publication artwork.
- One left-to-right row of six equal-height boxes, connected by single-headed arrows:
  1. `数据源获取/解码`
  2. `主机暂存/输入准备`
  3. `预处理`
  4. `必要数据移动`
  5. `TensorRT INT8推理与同步`
  6. `后处理/结果构造`
- Below the component row, add two braces/bands that share the same neutral line weight:
  - long dashed band spanning boxes 2–4: `V0→V2R：较宽的结构/配置干预`
  - short dotted band aligned only to box 2: `V2R→V3R：较窄的结构/配置干预（仅主机原始图像暂存分配类型）`
- Put `受控比较` at the left of both scope rows. The band lengths report structural/configuration coverage only.
- Bottom boundary note, verbatim:

  `较宽/较窄仅描述受控变量覆盖的结构与配置范围，不表示 Amdahl α 大小，也不预测实际加速比。`

## Visual contract

- Components: white fill, black `0.75 pt` outline, square corners, identical size.
- Common execution arrows: solid black `0.75 pt`.
- V0→V2R scope: neutral gray dashed outline, no arrowhead.
- V2R→V3R scope: neutral gray dotted outline, no arrowhead.
- Scope labels use the same font weight and luminance. Do not encode either scope as better, faster, preferred, or as a larger/smaller Amdahl fraction.
- Recommended fonts: Chinese `宋体`, Latin/digits `Times New Roman`; minimum effective print size `7.5 pt`.
- No gradients, 3D, shadows, traffic-light colors, speed icons, clocks, or numeric performance labels.

## Forbidden implications

- Do not label the six boxes as measured `T_k`, assign stage durations, or show a fitted performance model.
- Do not place `2.236671×`, `55.4519%`, `4.0738%`, or any result inside this conceptual graphic.
- Do not imply that broader scope has larger `α` or predicts greater speedup.
- Do not imply that narrower scope has smaller `α` or predicts a smaller effect.
- Do not add zero-copy, mapped memory, buffering, stream overlap, pipeline, or a second preprocessing algorithm.

## Manual Visio production

1. Reconstruct the six boxes and two scope bands as native editable Visio shapes.
2. Keep all component boxes aligned and distributed horizontally.
3. Group the component row, each scope band, and the boundary note separately.
4. Save the editable source as `fig2_e2e_intervention_scope_final.vsdx`.
5. Export `fig2_e2e_intervention_scope_final.pdf` and `fig2_e2e_intervention_scope_final.svg` with embedded/outlined fonts as appropriate.
6. Compare every visible label against this specification and verify grayscale legibility at manuscript column width.

## Deterministic preview

- Generator: `scripts/generate_fig2_e2e_intervention_scope_preview.py`
- Output: `fig2_e2e_intervention_scope_preview.svg`
- Governance: preview only; it must not replace current final publication assets or be inserted into the current manuscript during Phase 5.4C-A.
