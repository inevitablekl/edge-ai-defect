# Figure 2 — Technical Implementation and Memory Domains

Status: `CANDIDATE / SPECIFICATION`
Scientific role: implementation/data-path credibility figure for §2.2–§2.3. It explains ownership, lifecycle, and stream semantics of the GPU paths; it is not a performance figure.

## Layout and content contract

- Full-width target: `16.0 cm`; left-to-right host/device flow.
- Required sequence: host decoded `CV_8UC3 BGR` → pageable/pinned packed staging → `cudaMemcpy2DAsync` across the domain boundary → persistent device raw buffer → fused preprocessing kernel → TensorRT-owned FP32 NCHW device input → `enqueueV3` → output D2H → CPU decode/confidence filtering/NMS.
- V2R/V3R branch only at staging allocation type and rejoin before the same `cudaMemcpy2DAsync`/CUDA semantics.
- A single stream rail must connect `cudaMemcpy2DAsync`, the fused kernel, `enqueueV3`, and output D2H. It denotes ordering on the same TensorRT CUDA stream, not overlap.
- Lifecycle notes: staging allocated before the frame loop and reused; device raw buffer persistent/reused; TensorRT device input owned/reused by the backend.
- Concise exclusion note: `单 stream、单帧顺序路径；无跨帧 overlap / pipeline`. Do not depict multi-stream or a fabricated overlap timeline.
- `NO PERFORMANCE NUMBERS`: no `2.24×`, `55.45%`, `4.07%`, `40.96×`, FPS, or latency values.

## Structural evidence contract

| Visual element | Authority |
|---|---|
| Pageable packed staging/reuse | `backend_tensorrt/pageable_raw_staging.cpp`; `stage_r/pageable_runner.cpp` |
| Pinned `cudaHostAlloc`/reuse/free | `backend_tensorrt/pinned_raw_staging.cpp`; `stage_r/pinned_runner.cpp` |
| External TensorRT input and stream binding | `stage_r/pageable_runner.cpp`; `stage_r/pinned_runner.cpp`; `backend_tensorrt/cuda_preprocessor.cu` |
| `cudaMemcpy2DAsync` and fused kernel | `backend_tensorrt/cuda_preprocessor.cu` |
| `enqueueV3` and output D2H on engine stream | `src/tensorrt_engine.cpp` |
| CPU decode/filter/NMS | `src/postprocessor_decode.cpp`; `src/postprocessor_nms.cpp`; `src/serial_runner.cpp` |

The precise visual-element trace is in `phase56_visual_evidence_map.csv`. Actual code terminology overrides planning shorthand.

## Candidate caption

**V2R/V3R的主机—设备内存域、缓冲区生命周期与单流执行语义。** 两条路径仅在主机侧pageable/pinned暂存类型上不同，原始图像复制、融合CUDA预处理、TensorRT输入形成、`enqueueV3`及输出复制均沿同一TensorRT CUDA stream顺序执行；暂存区、设备原始图像缓冲区和后端输入缓冲区跨帧复用。图中不表示跨帧重叠或流水线。

## Candidate and D-B plan

- Candidate: `candidates/fig2_technical_implementation_phase56_candidate.{svg,pdf,png}`
- Generator: `scripts/generate_phase56d_structural_candidates.py`
- D-B output: reviewed SVG/PDF/PNG with candidate mark removed.
- Validation: source call-site check, forbidden-performance-token scan, vector/raster inspection, and `16.0 cm` readability proof.
- Integration target: §2.2–§2.3.
