# Figure 1 deterministic specification

## Identity

- Candidate: `F1`
- Chinese title: `V0、V2R和V3R数据路径及统一计时边界`
- English title: `V0, V2R, and V3R Data Paths with the Common Timing Boundary`
- Artifact type: schematic
- Numeric result values: none

## Shared object

All three paths use the frozen YOLOv8n deployment object, 640 × 640 input,
batch 1, NEU-DET replay workload, TensorRT INT8 Engine, output/correctness
contract, and common external timing boundary.

## Variant identity

| Variant | Raw staging/path | Preprocessing | Inference input | Role |
|---|---|---|---|---|
| V0 | Host source / host tensor path | CPU/OpenCV preprocessing path | TensorRT INT8 device input contract | correctness-first baseline |
| V2R | pageable host raw staging | OpenCV 4.5.4-aligned fixed-contract CUDA preprocessing | TensorRT INT8 device input | accepted pageable remediation |
| V3R | pinned host raw staging | the same OpenCV 4.5.4-aligned fixed-contract CUDA preprocessing semantics as V2R | TensorRT INT8 device input | accepted pinned companion |

The isolated V2R-to-V3R factor is host staging memory/allocation type. The
preprocessing semantics, Engine identity, workload, output contract, and
downstream path remain shared.

## Common timing boundary

- START: immediately before source pull / frame acquisition.
- INCLUDED: source pull/decode; variant-specific staging/path; CPU or CUDA
  preprocessing as applicable; host-to-device transfer where applicable;
  TensorRT INT8 execution; required synchronization; device-to-host transfer
  where required; postprocessing/NMS; frame-result construction.
- END: after frame-result construction, immediately before result
  serialization/write.
- EXCLUDED: JSON serialization; file I/O; digest finalization/writing; summary
  persistence.

The schematic uses a common downstream block where lower-level copy placement
is not required to establish the frozen variant identity.

## Source authority

- `docs/paper/phase0_5/PAPER_TIMING_ALIGNED_RERUN_PLAN_v1.0.md`
- `docs/paper/phase2/PAPER_PHASE2_FIGURE_TABLE_PLAN_v1.0.csv`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`

## Generation

The SVG is emitted by `scripts/paper/generate_phase3_fig1.py` from this fixed
specification. No experimental values are recomputed.
