# Figure 1 — Controlled Data-Path Engineering Overview

Status: `CANDIDATE / SPECIFICATION`
Scientific role: hero figure after the introduction contributions. It absorbs the controlled-comparison content of the current Figures 1 and 2 without becoming an implementation dump.

## Required reading sequence

1. The upper two domains explicitly separate `HOST / CPU` from `DEVICE / GPU`.
2. V0 forms an FP32 NCHW tensor on the host and copies that tensor H2D.
3. V2R/V3R stage packed raw BGR pixels, copy raw pixels H2D, and form the FP32 NCHW tensor on the GPU.
4. V2R and V3R merge into one shared downstream CUDA/TensorRT path; only pageable versus pinned host staging changes.
5. The footer compares complete paths: V0→V2R is the major path restructuring; V2R→V3R isolates the marginal host-memory allocation type.

## Layout contract

- Full-width target: `16.0 cm`; landscape aspect ratio approximately 3.0–3.5:1.
- Layer A: HOST/CPU and DEVICE/GPU bands with an explicit vertical boundary.
- Layer B: V0 rail plus a V2R/V3R branch that merges before a single shared device path and a single shared Engine box.
- Layer C: detached `Observed complete-path E2E` footer. Performance values appear only inside comparison cards in this footer.
- A nominal-payload callout may sit beside the complete-path footer but must carry `名义值；非实测总线流量`.

## Annotation and causality contract

```text
PERFORMANCE_VALUES_ATTACH_TO_COMPARISON = YES
PERFORMANCE_VALUES_ATTACH_TO_COMPONENT = NO
```

Required display values: V0→V2R `2.24× FPS`, `平均延迟降低55.45%`; V2R→V3R `FPS +4.07%`, `平均延迟降低4.03%`; pooled tail `P95/P99变化均小于0.2%，方向相反`. No value may be attached to the H2D arrow, fused kernel, pinned-memory box, or Engine.

Nominal input-copy payload: V0 `4.915 MB/frame`; V2R/V3R `0.120 MB/frame`; ratio `40.96×`; qualifier `名义值；非实测总线流量`. Forbidden wording includes “40.96× transfer reduction” and “bandwidth reduction.”

## Structural evidence contract

| Visual element | Authority |
|---|---|
| Decoded BGR and CPU/OpenCV preprocessing | `src/serial_runner.cpp`; `src/preprocessor.cpp` |
| V0 host FP32 NCHW tensor and H2D | `src/preprocessor.cpp`; `src/tensorrt_engine.cpp` |
| V2R pageable staging | `stage_r/pageable_runner.cpp`; `backend_tensorrt/pageable_raw_staging.cpp` |
| V3R pinned staging / allocation before frame loop | `stage_r/pinned_runner.cpp`; `backend_tensorrt/pinned_raw_staging.cpp` |
| Raw-image H2D and fused CUDA preprocessing | `backend_tensorrt/cuda_preprocessor.cu` |
| Shared TensorRT-owned input and Engine | `stage_r/pageable_runner.cpp`; `stage_r/pinned_runner.cpp`; `src/tensorrt_engine.cpp` |
| Headline observations | `docs/paper/phase5_6/phase56b_publication_display_values.json` |
| Nominal payload | `docs/paper/phase5_6/phase56b_nominal_payload.json` |

The cell-level/arrow-level trace is frozen in `phase56_visual_evidence_map.csv`.

## Candidate caption

**V0、V2R和V3R受控数据路径及完整路径观测。** V0在主机侧形成FP32 NCHW输入张量，V2R/V3R将打包原始图像复制到设备并在GPU侧形成TensorRT输入；V3R仅将V2R的pageable暂存替换为pinned暂存。性能数字表示完整端到端路径比较，不归因于单一组件。输入复制载荷为名义值，不等同于实测总线流量。

## Candidate and D-B plan

- Candidate: `candidates/fig1_hero_data_path_phase56_candidate.{svg,pdf,png}`
- Generator: `scripts/generate_phase56d_structural_candidates.py`
- D-B output: reviewed manuscript-ready SVG/PDF/PNG, candidate watermark removed, content otherwise constrained by this spec.
- Validation: source/hash check, raw-SVG parse, 300-DPI raster inspection, causal attachment review, and manuscript-width proof.
- Integration target: after the introduction contributions; D-B may update cross-references only after explicit authorization.
