# Target Figure 1 Visio Upgrade Specification v2.0

Status: `PHASE5_PREPARATION_ONLY`. Production owner: `USER_MANUAL_VISIO`.
Starting source: `fig1_v0_v2r_v3r_data_paths_final.vsdx` (accepted current editable source). Do not overwrite it.

## Frozen role

Target Figure 1 remains the implementation-validated V0/V2R/V3R data-path figure. It must show actual tested paths, not the conceptual scope model reserved for target Figure 2.

## Required lanes

- V0: `图像源/解码 → CPU/OpenCV预处理 → TensorRT INT8 Engine → 后处理/NMS → 帧结果构造`
- V2R: `图像源/解码 → pageable host raw staging → H2D → CUDA预处理 → TensorRT INT8 Engine → D2H → 后处理/NMS → 帧结果构造`
- V3R: `图像源/解码 → pinned host raw staging → H2D → CUDA预处理 → TensorRT INT8 Engine → D2H → 后处理/NMS → 帧结果构造`

V2R and V3R CUDA-preprocessing nodes must be visually identical. The only highlighted V2R→V3R difference is `pageable` versus `pinned` host raw-image staging. The common timing boundary, if retained, starts before source pull and ends after frame-result construction; it is one common end-to-end boundary, not stage timing.

## Visual upgrade operations

1. Use the accepted VSDX as the base and preserve its topology and labels.
2. Create three equal-height lanes in V0, V2R, V3R order; align common semantic stages vertically even where V0 has fewer explicit transfer nodes.
3. Give common stages identical geometry, outline, and typography across lanes.
4. Apply the global variant identity contract:
   - V0 lane tag: white fill, solid outline, no hatch.
   - V2R lane tag: white fill, solid outline, 45-degree diagonal hatch.
   - V3R lane tag: white fill, solid outline, cross-hatch.
   Node fills remain neutral and do not inherit a better/worse darkness scale.
5. Add one narrow comparison callout between the V2R/V3R staging nodes: `唯一隔离变量：主机原始图像暂存分配类型`.
6. If the timing boundary is shown, use one thin neutral dashed enclosure covering the same start/end semantics for all lanes and label it `统一逐帧端到端计时边界`.
7. Improve print readability: minimum effective `7.5 pt`, `0.75 pt` outlines, no gradients/shadows, and verify at journal column width.

## Forbidden nodes and claims

Do not add zero-copy, mapped memory, pinned output, double buffering, multiple streams, transfer-compute overlap, asynchronous overlap, cross-frame pipeline, GPU NMS, or a second V3R CUDA algorithm. Do not place FPS/latency gains or mechanism claims on path nodes. Do not present V0 host allocation as the V2R/V3R raw-staging allocation variable.

## Target outputs

- Editable: `fig1_v0_v2r_v3r_data_paths_phase5_final.vsdx`
- Exports: `fig1_v0_v2r_v3r_data_paths_phase5_final.pdf` and `.svg`
- These outputs become publication authority only after scientific/visual review and the later manuscript-integration step.
