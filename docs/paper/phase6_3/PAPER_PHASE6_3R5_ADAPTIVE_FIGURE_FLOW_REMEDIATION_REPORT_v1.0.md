# Paper Phase 6.3R5 Adaptive Figure Flow Remediation Report v1.0

## 1. Verdict

`PHASE_6_3_ADAPTIVE_FIGURE_FLOW_REMEDIATION_IMPLEMENTED`

The format-only implementation, Full/Anonymous builds, structural validation, and scientific non-regression checks pass. Microsoft Word remains the pagination authority, so all page-flow and optical-centering outcomes remain pending Word visual review.

## 2. Baseline

- Branch: `main`.
- Required and observed `HEAD`: `32e29542293a5968f75ee6fddcea21f0e38e61d6`.
- Required and observed `origin/main`: `32e29542293a5968f75ee6fddcea21f0e38e61d6`.
- Baseline commit subject: `paper: remediate Phase 6.3 Word visual format findings`.
- Pre-edit worktree and index: clean.
- No later or unknown work required reconciliation.

## 3. User-confirmed findings

- `FMT-F07`: major Page 3 residual abnormal whitespace.
- `FMT-F08`: major Page 5 whitespace caused by Figure 2 flow.
- `FMT-F09R`: major Page 6 whitespace caused by the next-figure transition.
- `FMT-F10`: major Figure 2/3 optical-centering failure.
- `FMT-F11`: major Figure 2/3 excessive vertical geometry.
- `FMT-F12`: minor cross-column split `报|告` with no missing text.
- `FMT-F14`: major validation gap between valid OOXML and acceptable pagination.

Reference spacing remains closed and was not changed.

## 4. Independent-review findings reconciled

The repository inspection confirms the reviewer's causal model. An inline drawing is a body-order barrier: if it cannot fit, the drawing moves and later body paragraphs cannot pass it. The user-confirmed Page 6 symptom is therefore treated as genuine even though the earlier mechanical review described it as less severe. HFUT's `先文后图` rule is enforced as first-callout precedence, not immediate placement after the first callout.

## 5. Figure 1 pagination diagnosis

| Field | Finding |
|---|---|
| Actual source order | First callout, remaining §1.3 material, inline Figure 1/caption, Section 2 |
| Physical size | 16.00 cm × 7.92 cm; unchanged |
| Available text height | Approximately 25.30 cm per A4 text column from the governed top/bottom margins |
| Blocking property | Postprocessor moved Figure 1 immediately before Section 2 and applied `pageBreakBefore`; the one-column section transition then blocked Section 2 from using the preceding page |
| Why later prose could not flow | Figure 1 was physically ordered before all Section 2 prose |
| Candidate A | Keep immediate-before-Section-2 placement |
| Candidate B | Defer to a later semantic subsection boundary while preserving page-top/full-width placement |
| Candidate C | Use a floating page-relative drawing |
| Chosen solution | Candidate B: defer to immediately before §3.3; retain the page-top break and drawing-caption attachment |

Figure 1 was not resized or redrawn. Its first callout remains before the drawing; its new governed location allows all Section 2 and §§3.1–3.2 prose to flow first. Floating placement was rejected as more fragile across Word versions.

## 6. Figure 2 pagination diagnosis

| Field | Finding |
|---|---|
| Actual source order | §4.2 callout, inline Figure 2/caption, two remaining §4.2 body paragraphs |
| Physical size before | 7.50 cm × 18.18 cm |
| Available text height | Approximately 25.30 cm, reduced by preceding heading/callout prose and caption |
| Blocking property | Inline body order; the tall drawing could move, but the two later §4.2 paragraphs could not pass it |
| Why later prose could not flow | Drawing/caption physically preceded the remaining subsection discussion |
| Candidate A | Defer the existing figure to the end of §4.2 |
| Candidate B | Candidate A plus compact artist-tight geometry |
| Candidate C | Split FPS/mean-latency and tail-latency panels |
| Chosen solution | Candidate B; Figure 2 now occurs after the two post-callout §4.2 paragraphs and before §4.3 |

## 7. Figure 3 pagination diagnosis

| Field | Finding |
|---|---|
| Actual source order | §4.4 callout, inline Figure 3/caption, two remaining §4.4 body paragraphs |
| Physical size before | 7.50 cm × 14.36 cm |
| Available text height | Approximately 25.30 cm, reduced by preceding §4.3/§4.4 content and caption |
| Blocking property | Inline body order at the first-callout source location |
| Why later prose could not flow | Drawing/caption physically preceded the remaining §4.4 discussion |
| Candidate A | Defer the existing figure to the end of §4.4 |
| Candidate B | Candidate A plus compact artist-tight geometry |
| Candidate C | Split process-level FPS and latency-distribution panels |
| Chosen solution | Candidate B; Figure 3 now occurs after the two post-callout §4.4 paragraphs and before §4.5 |

## 8. Candidate placement strategies tested

1. Adaptive deferral with the original statistical assets removed the immediate source-order barrier but retained unnecessarily tall canvases.
2. Adaptive deferral plus compact artist-tight statistical assets produced stable structural composition and an eight-page supplementary LibreOffice render.
3. Figure 1 anchors before Section 3, §3.2, §3.3, and §2.3 were mechanically compared. The §3.3 boundary left the smallest ordinary preceding-page tail while preserving a semantic heading boundary; §2.3 recreated a large unused region.
4. Floating page-relative drawings were rejected because Word anchoring and wrap behavior are less deterministic than body-order scheduling.
5. Splitting was reserved as the fallback and was not required.

## 9. Selected adaptive placement model

The postprocessor now treats a figure as eligible after its first callout and relocates the complete drawing/caption pair to a governed later semantic boundary:

- Figure 1: immediately before §3.3;
- Figure 2: immediately before §4.3, after all §4.2 discussion;
- Figure 3: immediately before §4.5, after all §4.4 discussion.

Every drawing retains `keepNext` with its caption. Captions do not carry `keepNext`, so they do not block following prose. Only Figure 1 retains `pageBreakBefore` and the continuous two-column/one-column section contract.

## 10. Figure split decision

`FIGURE_SPLIT = NOT_REQUIRED`.

Adaptive deferral plus compactness reduced both statistical figures enough to avoid a new inventory. Figure numbers, callouts, captions, lifecycle rows, and source semantics remain unchanged.

## 11. If split: figure inventory/callout changes

Not applicable. No Figure 4 was created and no manuscript prose fragment changed.

## 12. Figure 2 optical-centering diagnosis and correction

Before correction, the 885 px canvas had 115 px left and 24 px right internal whitespace, an asymmetry of 0.1028 of canvas width. The generator now saves against the actual artist bounding box with symmetric 0.04 inch padding. The new 786 px canvas has 13 px left and 9 px right whitespace, asymmetry 0.0051, with bounding-box center offset 0.0025. The Word drawing paragraph remains geometrically centered and was not shifted.

## 13. Figure 3 optical-centering diagnosis and correction

Before correction, the 885 px canvas had 140 px left and 24 px right internal whitespace, an asymmetry of 0.1311. The new 768 px artist-tight canvas has 11 px left and 9 px right whitespace, asymmetry 0.0026, with bounding-box center offset 0.0013. The Word drawing paragraph remains geometrically centered and was not shifted.

## 14. Compactness before/after

| Figure | Width | Height before | Height after | Reduction | Internal font target |
|---|---:|---:|---:|---:|---:|
| Figure 2 | 7.50 cm | 18.18 cm | 15.49 cm | 14.8% | 7.5 pt unchanged |
| Figure 3 | 7.50 cm | 14.36 cm | 12.17 cm | 15.3% | 7.5 pt unchanged |

The Phase 6.3 validator records `FIGURE_PUBLICATION_COMPACTNESS` through a project review limit of 15.5 cm at 7.5 cm width. This is explicitly not represented as a universal HFUT figure-height rule.

## 15. FMT-F12 cross-column readability result

The adaptive-flow rebuild did not remove the `报|告` split in the supplementary LibreOffice render. A format-layer U+2060 word joiner is now inserted only into the generated OOXML phrase `每条路径报⁠告5个进程级FPS`; the Markdown sentence and visible characters are unchanged. LibreOffice ignores both U+2060 and the tested legacy U+FEFF for this CJK break. Paragraph-wide `keepLines` was rejected because it could recreate major whitespace. Result: `IMPLEMENTED_PENDING_WORD_REVIEW`.

## 16. Validator redesign

The Phase 6.3 validator now checks publication invariants rather than the old immediate-placement implementation:

- first callout precedes every drawing;
- each caption is immediately below its drawing;
- drawing/caption attachment and caption release of following prose;
- governed widths and Figure 1 page-top/full-width section contract;
- post-callout prose exists before deferred Figures 2/3;
- no forced page break on Figures 2/3;
- single-column project compactness review metadata;
- image-level non-background bounding box, padding, and visual-center tolerances;
- one scoped `报告` no-break guard;
- Full/Anonymous placement, geometry, and no-break parity.

The obsolete requirement that Figure 1 be immediately followed by Section 2 was removed from both the Phase 6.3 format validator and the scientific non-regression validator.

## 17. Global layout structural audit

PASS for Full and Anonymous OOXML:

- Figure 1: callout paragraph 38, drawing 66, caption 67 in Full; 16.00 × 7.92 cm; `keepNext`; page-top break; one-column continuous caption section.
- Figure 2: callout paragraph 76, drawing 79, caption 80 in Full; 7.50 × 15.49 cm; `keepNext`; no page break or section.
- Figure 3: callout paragraph 86, drawing 89, caption 90 in Full; 7.50 × 12.17 cm; `keepNext`; no page break or section.
- No caption carries `keepNext`.
- No empty ordinary body paragraph, stale callout, stale number, or extra figure exists.
- Tables, headings, equations, margins, and references pass their existing validators.
- Full/Anonymous structure and scientific-body parity pass.

## 18. Scientific non-regression

`SCIENTIFIC_NONREGRESSION = PASS`.

- Run-level Figure 2/3 data SHA-256: `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31`.
- Publication-summary SHA-256: `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655`.
- Experiment source hash, all numerical values, equations, RQ1/RQ2, three correctness rows, tables, reference metadata, results, conclusions, and limitation language are unchanged.
- All 18 watched claim terms remain legitimate negations or boundary statements.
- Non-regression artifact: `docs/paper/phase6_3/phase6_3_scientific_nonregression.json`.

## 19. Full build

PASS:

```text
bash scripts/paper/build_manuscript_docx.sh --build-full
```

All build-integrated validators pass.

## 20. Anonymous build

PASS:

```text
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Identity scan, scientific-body parity, figure-media parity, and Phase 6.3 parity pass.

## 21. Full DOCX path + SHA256

`docs/paper/manuscript/output/draft_full.docx`

SHA-256: `aa86b621a87c5123f57b1bb46285c27cebc075fe225c4b222a12ceb791499a54`.

## 22. Anonymous DOCX SHA256

`docs/paper/manuscript/output/draft_anonymous.docx`

SHA-256: `be085cffa74e1a07994cf67c9975ec16d48a30cb7a607793a317207e599bcb44`.

## 23. Mechanical render observations

Supplementary LibreOffice renders are eight A4 pages for both variants.

- Full PDF SHA-256: `5c3cf2782f5285a3dbd69cd6d6b3f6fed04dbceb437da42d7467c2d7a26e8c89`.
- Anonymous PDF SHA-256: `951104eabbd354f03a2d15df7de645c2e4f0d89d05c6ab6fc37ca27f6007a58a`.
- The page preceding Figure 1 is substantially filled; Figure 1 remains page-top, full-width, unclipped, and captioned below.
- Figures 2 and 3 are centered, compact, single-column, captioned below, and no longer create the former large transition regions in the supplementary render.
- U+2060 remains ignored by LibreOffice for `报告`; Microsoft Word review is required.
- Mechanical render and page count are supplementary evidence only, not Word pagination certification.

## 24. Changed files

- `docs/paper/phase5_6/visual/scripts/generate_phase56d_production_statistical.py`.
- Figure 2 SVG/PDF/PNG production assets.
- Figure 3 SVG/PDF/PNG production assets.
- `scripts/paper/postprocess_full_manuscript_docx.py`.
- `scripts/paper/validate_phase63_format.py`.
- `scripts/paper/validate_phase61_nonregression.py`.
- `docs/paper/phase6_3/phase6_3_scientific_nonregression.json`.
- This report.

Generated DOCX/PDF review artifacts remain in the ignored manuscript output tree.

## 25. Diff scope

The diff is format-only. No manuscript section, experiment source, reference file, table, equation, figure caption, figure callout, figure number, figure manifest row, production C++, or deployment architecture file changed. The regenerated statistical assets use the same frozen source data.

## 26. Deferred submission adaptations

Still open and not authorized in this work unit:

- Figure 1 Visio submission object;
- Figure 2/3 Origin submission objects;
- MathType conversion;
- Microsoft Word desktop visual QA;
- Anonymous Word/Document Inspector QA;
- final HFUT submission adaptation.

`HFUT_SUBMISSION_READY = NO`.

## 27. Commit

Exactly one commit is to be created with message:

```text
paper: stabilize adaptive figure flow for Word layout
```

The definitive commit SHA is returned in the handoff rather than self-embedded, avoiding an amend cycle. No push, tag, merge, reset, clean, rebase, or amend is performed.

## 28. Exact next action

Open the latest Full DOCX in Microsoft Word, allow Word to repaginate, and inspect Word pages 3–7 (page numbers may shift by Word version), specifically:

1. the page immediately before Figure 1 and the Figure 1 page: no large preceding blank region; Figure 1 remains page-top/full-width with no same-page body above and caption below;
2. the Figure 2 page and its immediately preceding column/page: no Page-5-style blank region and the chart is optically centered;
3. the Figure 3 page and its immediately preceding column/page: no Page-6-style blank region and the chart is optically centered;
4. the sentence containing `每条路径报告5个进程级FPS`: no `报|告` cross-column split or apparent missing line;
5. all remaining pages: no new heading orphan, figure/caption separation, clipping, margin overflow, or pagination regression.

Required state after this commit:

- `PAGE3_FLOW = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `PAGE5_FLOW = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `PAGE6_FLOW = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `FIGURE2_OPTICAL_CENTERING = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `FIGURE3_OPTICAL_CENTERING = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `FIGURE_COMPACTNESS = STRUCTURALLY_IMPROVED`;
- `SCIENTIFIC_NONREGRESSION = PASS`;
- `STRUCTURAL_FORMAT_VALIDATION = PASS`;
- `MICROSOFT_WORD_VISUAL_QA = PENDING`;
- `WORD_ARTIFACT_VISUAL_REVIEW_REQUIRED = YES`.
