# Phase 7.1R1 pagination regression diagnosis

## Finding

Microsoft Word reported abnormal white regions on pages 5 and 6 after Phase 7.1. The DOCX architecture confirms that Figures 2 and 3 are project-specific floating Word tables (`tblpPr`, `vertAnchor=text`, `horzAnchor=text`, `tblpY=1`, `tblOverlap=never`) whose logical anchors move when front-matter geometry changes.

## Root cause classification

`INTERACTION_BETWEEN_SOURCE_FORMAT_GEOMETRY_AND_PROJECT_FLOAT_MECHANISM`.

The official front-matter corrections are retained. The blank regions are not an HFUT rule: they are a Microsoft Word pagination outcome of the project float mechanism after preceding-flow geometry changed. Figure 3's historical Candidate-B one-body-paragraph anchor is therefore not presumed valid after Phase 7.1.

## Resolution state

No headless renderer is authoritative for Microsoft Word pagination. Generate bounded Figure-3 anchor candidates only after the deterministic run-level format build, then select in Microsoft Word. Preserve figures, captions, dimensions, Figure-1 behavior, and scientific text.

## Microsoft Word candidate files

`docs/paper/manuscript/output/phase71r1_candidate_A.docx` moves Figure 3 to the first callout (related-body offset 0). `phase71r1_candidate_B.docx` retains the current one-related-body offset. These ignored files differ only in the logical Figure-3 float anchor and require Microsoft Word page-5/page-6 review.
