# Phase 5.9C Figure 1 Authority

## Role

Figure 1 is the conceptual authority for the fixed-object input data-path model and hierarchical controlled interventions. It is not an implementation lifecycle diagram and contains no performance result.

## Required content

- Host and device domains separated by an explicit boundary.
- Three path instances: `P0/V0`, `P2/V2R`, and `P3/V3R`.
- For each path: H2D representation `R`, TensorRT-input formation location `F`, additional packed raw-image staging policy `M`, and common sequential topology `E`.
- `P0 -> P2` identified as path-level reconstruction that changes `R`, `F`, and `M` while holding `E` fixed.
- `P2 -> P3` identified as staging-policy-level refinement.
- A note that intervention scope does not imply gain size or component-level causality.

## Exclusions

No API lifecycle, allocator release, execution-context lifecycle, output D2H detail, result number, bandwidth, transfer-speed, overlap, or pipeline claim is shown.

## Production

Run:

```bash
python3 docs/paper/phase5_9/visual/scripts/generate_phase59c_figure1.py
```

The script deterministically generates SVG, PDF, PNG, and grayscale inspection assets under `visual/production/figures/`. The PNG is embedded in the mechanical DOCX because the existing LibreOffice path has an established SVG blank-render limitation. Visio conversion remains deferred.
