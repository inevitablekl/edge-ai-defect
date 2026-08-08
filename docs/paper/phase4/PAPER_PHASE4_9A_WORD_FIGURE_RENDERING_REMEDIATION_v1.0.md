# Paper Phase 4.9A Word Figure Rendering Remediation Report

## 1. Trigger

Real Microsoft Word Phase 4.9A review found that all three inline publication
figures were effectively invisible or clipped even though the DOCX opened,
saved, and reopened without repair warnings. The Word-exported PDF reproduced
the defect.

Phase 4.9 real Microsoft Word inspection invalidated the earlier automatic
assumption that figure presence implied figure visual visibility. This is a
newly discovered publication-layout defect; the historical Phase 4.8 evidence
is retained unchanged.

## 2. User Evidence

- First open: `PASS`.
- Repair warning: `NO`.
- Save: `PASS`.
- Close/reopen: `PASS`.
- Repair warning after reopen: `NO`.
- Word page count before repair: 9.
- Figure rendering: `FAIL` for F1, F2, and F3.

## 3. Root Cause

- `wp:inline`: 3.
- `wp:anchor`: 0.
- Embedded PNG media: intact at 961 × 205, 885 × 685, and 968 × 732 px.
- All drawing paragraphs used `BodyText`, based on `HFUTBody`.
- Drawing paragraphs had no direct line-spacing override and therefore
  inherited exact 16 pt (`line=320`, `lineRule=exact`).
- Large inline drawings could not expand the exact-height line box and were
  clipped/overlaid by Microsoft Word.
- Verdict: `FIGURE_PARAGRAPH_EXACT_LINE_SPACING_DEFECT`.
- `IMAGE_ASSET_CORRUPTION = NO`.
- `FLOATING_ANCHOR_WRAP_BUG = NO`.

## 4. Remediation

The common real-manuscript DOCX postprocessor now identifies the three direct
body paragraphs that structurally contain `w:drawing`. It requires exactly
three publication drawing paragraphs and applies only these direct properties:

```xml
<w:spacing w:before="0" w:after="0" w:line="320" w:lineRule="atLeast"/>
<w:ind w:firstLine="0"/>
<w:jc w:val="center"/>
```

No global style, inline extent, aspect ratio, image asset, anchor/wrapping
model, caption, scientific source, or section design changed.

The real-manuscript validator now enforces
`FIGURE_INLINE_EXACT_LINE_SPACING_FORBIDDEN` and verifies three inline/no-anchor
drawings, direct `atLeast 320` spacing, zero first-line indent, and centered
alignment.

## 5. Full Build

- Path: `docs/paper/manuscript/output/draft_full.docx`.
- SHA256: `95120ec6e9ccb851cc704b58f0ebd284b686452e9120574ca3227a11ec2f0ff6`.
- LibreOffice page count: 10.
- A4 conversion: PASS.
- Journal-format validation: PASS.
- ZIP/XML validation: PASS.

The page-count change is natural pagination after the figures acquired their
actual vertical line boxes; it is not treated as a failure.

## 6. Anonymous Build

- Path: `docs/paper/manuscript/output/draft_anonymous.docx`.
- SHA256: `3cd3dd3ff45c972d32a93b02e494a293ebc515abf5e4f05921ae8a1705e8a2f9`.
- LibreOffice page count: 9.
- A4 conversion: PASS.
- Anonymity scan: PASS.
- Full/Anonymous scientific parity: PASS.
- Journal-format validation: PASS.
- ZIP/XML validation: PASS.

## 7. Figure Validation

### F1

- Extent retained: 16.000 × 3.413 cm.
- Media retained: 961 × 205 px.
- Representation: `wp:inline`; no anchor.
- Drawing paragraph: direct `atLeast 320`, centered, first-line indent 0.
- LibreOffice rendered page: Full 4; Anonymous 3.
- Mechanical visual inspection: PASS. V0/V2R/V3R, image source/decoding,
  CPU/OpenCV preprocessing, pageable/pinned staging, H2D/D2H, CUDA
  preprocessing, TensorRT INT8 Engine, postprocessing/NMS, and frame-result
  construction are visible rather than a thin slice.
- Full places F1 on a mostly separate page:
  `F1_PAGINATION_WORD_MANUAL_CONFIRMATION_REQUIRED`.
- Raster sharpness remains a Word-manual item.

### F2

- Extent retained: 7.500 × 5.805 cm.
- Media retained: 885 × 685 px.
- Representation: `wp:inline`; no anchor.
- Drawing paragraph: direct `atLeast 320`, centered, first-line indent 0.
- LibreOffice rendered page: Full 8; Anonymous 7.
- Mechanical visual inspection: PASS. Three complete bars, error bars,
  54.600/122.122/127.097, and V0/V2R/V3R are visible.

### F3

- Extent retained: 7.500 × 5.671 cm.
- Media retained: 968 × 732 px.
- Representation: `wp:inline`; no anchor.
- Drawing paragraph: direct `atLeast 320`, centered, first-line indent 0.
- LibreOffice rendered page: Full 9; Anonymous 8.
- Mechanical visual inspection: PASS. All Mean/P95/P99 grouped bars and the
  V0/V2R/V3R legend are visible.

Mechanical visual PASS is based on direct inspection of rendered PNG pages,
not OOXML object count alone. Microsoft Word remains the authoritative retest.

## 8. Format Regression

- Biography in Full first-page footer exactly once: PASS.
- Anonymous biography absent: PASS.
- Section sequence `[1,2,1,2]`: PASS.
- PAGE fields and no restart: PASS.
- A4 geometry and margins: PASS.
- F1/F2/F3 extents and captions: PASS.
- T1/T2 rows and three-line borders: PASS.
- Reference typography and unnumbered heading: PASS.
- Phase 4.7 citation semantics and bibliography parity: PASS.

## 9. Scientific Freeze

- Scientific manuscript-source changes: NO.
- `2.236671×`, `55.4519%`, `4.0738%`, `4.0349%`, `0.1514%`, and
  `0.1184%`: retained.
- P95 direction: higher/slower.
- P99 direction: lower/faster.
- Tail behavior: `MIXED`.
- References, CSL, tables, captions, section 1.3, image assets, and frozen
  numbers: unchanged.
- Result: PASS.

## 10. Remaining Word Items

- Retest both untouched rebuilt DOCX files in real Microsoft Word.
- Confirm all three figures remain fully visible after save/close/reopen and PDF export.
- Confirm F1 real Word pagination and the mostly separate-page disposition in Full.
- Confirm F1 raster clarity at 16 cm.
- Confirm F2/F3 typography and font fallback.
- Confirm table wrapping/pagination, reference typography, PAGE refresh, and
  final Document Inspector results.

## 11. Recommendation

`PHASE_4_9A_WORD_RETEST_READY`
