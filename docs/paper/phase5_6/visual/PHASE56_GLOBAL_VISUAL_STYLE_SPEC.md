# Phase 5.6 Global Visual Style Specification

Status: `CANDIDATE / SPECIFICATION`
Scope: Figure 1–4 and Table 1–4 design contract for Phase 5.6D-B. This file is not manuscript or production-asset authority.

## Fixed journal envelope

- Actual manuscript page: A4 portrait, one column. The OOXML section is `11906 × 16838` twips with left/right margins `1304` twips; usable width is approximately `16.4 cm`.
- Official figure limits retained by the project: nominal single-column `7.5 cm`, full-width `16.0 cm`. Because the current manuscript is one-column, D-B should use full-width `16.0 cm` for F1–F4 unless a readability proof supports `7.5 cm`.
- Current inline extents are F1 `16.0 × 3.289 cm`, F2 `16.0 × 7.054 cm`, F3 `7.5 × 5.671 cm`, and F4 `16.0 × 6.585 cm`. These are inventory facts, not required future aspect ratios.
- Current tables are native Word tables: T1 approximately `16.002 cm`; T2/T3 approximately `7.761 cm`. D-B must remain within `16.0 cm` and prefer a compact three-line table.
- Captions remain manuscript-generated; no image-embedded `图1`/`Figure 1` caption is allowed. Current caption styles are centered, 7.5 pt, exact 16 pt line spacing, zero before/after spacing, Chinese 黑体 and Latin Times New Roman.
- Current body is 10.5 pt, Chinese 宋体 and Latin Times New Roman. Current table text is 7.5 pt, Chinese 宋体 and Latin Times New Roman.

## Typography

- Chinese labels: repository-available Noto Serif CJK (`Noto Serif CJK SC`, Matplotlib-resolved internal family `Noto Serif CJK JP`) as a compatible candidate-generation substitute. D-B must outline/embed or verify substitution in the final PDF.
- English, numbers, and API tokens: Liberation Serif in candidates; final DOCX remains Times New Roman through the manuscript style system.
- Code/API labels (`cudaMemcpy2DAsync`, `cudaHostAlloc`, `enqueueV3`) retain their exact Latin spelling. Do not duplicate every label bilingually.
- Minimum intended final-size text: 7.0 pt for ordinary labels and 6.5 pt for concise secondary notes. Panel titles may be 8.5–9.5 pt. Candidate watermark is not production content.

## Line and marker system

| Element | Candidate rule |
|---|---|
| Primary box border / main data path | 1.0–1.3 pt equivalent, dark neutral |
| Secondary annotation / divider | 0.7–0.9 pt equivalent |
| Arrow | 1.0–1.3 pt equivalent, filled visible head |
| Callout | 0.7–0.9 pt border, pale neutral fill |
| Error bar | at least 1.0 pt equivalent with visible caps |
| Marker outline | at least 0.9 pt equivalent |
| Table top/bottom rule | 1.0 pt |
| Table middle rule | 0.5 pt |

No gradients, 3-D effects, glossy fills, heavy shadows, or marketing-infographic decoration.

## Variant identity

| Variant | Fill | Redundant grayscale identity | Meaning guard |
|---|---|---|---|
| V0 | neutral gray | dotted hatch / square marker / explicit label | baseline path only |
| V2R | light blue | forward-slash hatch / circle marker / explicit label | pageable raw staging |
| V3R | light orange | back-slash hatch / triangle marker / explicit label | pinned raw staging |

Color never means “better” or “worse.” Every result panel must preserve at least one non-color cue: outline, hatch, marker, or explicit label.

## Functional domains

- HOST / CPU and DEVICE / GPU use different very light neutral domain fills and an explicit boundary.
- H2D arrows must visibly cross that boundary.
- Preprocessing, inference, and output may use restrained pale functional fills, but variant colors are reserved for variant identity.
- A shared downstream rail is preferred over duplicating identical V2R/V3R boxes.

## Statistical grammar

- F3 FPS: bar height = mean of five independent process-level FPS values; error bar = sample SD (`ddof=1`).
- F3 mean latency: pooled mean over 5400 frame-level samples per path.
- F3 P95/P99: pooled quantiles over 5400 frame-level samples per path, never the mean of five process percentiles.
- F4: individual process points with fixed deterministic horizontal offsets; no run-ID pairing and no connecting lines. Mean/error overlay is descriptive only.
- Display precision: absolute FPS/latency three decimals; comparisons `2.24×`, `−55.45%`, `+4.07%`, `−4.03%`, `+0.15%`, `−0.12%`.

## Output and determinism contract

- Structural candidates: Python standard library emits raw SVG; LibreOffice converts a copy to PDF; `pdftocairo -r 300` creates the inspection PNG.
- Statistical candidates: Python/Matplotlib reads frozen CSV/JSON and emits SVG/PDF; `pdftocairo -r 300` creates PNG.
- No network, uncontrolled randomness, hand-adjusted output, or manual bar heights. F4 uses fixed offsets.
- SVG is the editable vector candidate; PDF is print/vector compatibility payload; 300-DPI PNG is inspection/fallback only. Text must remain vector where the converter supports it.
- Every candidate carries `CANDIDATE / SPECIFICATION`; D-B must remove that mark only when producing reviewed manuscript authority.

## Raster inspection gates

At 16 cm width, each candidate must pass: no clipping; intact arrowheads; correct CJK and Latin glyphs; no label collisions that alter meaning; printable strokes; grayscale-decipherable variants; no embedded caption; and readable main labels. A 7.5 cm reduction is required only if D-B chooses single-column placement.
