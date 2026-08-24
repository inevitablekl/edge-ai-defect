# Paper Phase 6.3R7 Inline Figure Barrier Elimination Report v1.0

## 1. Verdict

`PHASE_6_3_INLINE_FIGURE_BARRIERS_ELIMINATED`.

The three source-order body barriers were replaced by Word-native floating
table containers. Each container holds the scientific drawing and editable
caption in one non-splitting row. Microsoft Word visual acceptance remains
external and pending.

Superseding Phase 6.3R8 clarification: the containers support text wrapping,
but Microsoft Word review established that backfill before a logical float
anchor is not guaranteed. Any earlier statement implying guaranteed backfill
is retired.

## 2. Baseline

- Repository branch: `main`.
- Baseline `HEAD`: `643163125a96a9bbbf3d0d87d527995416511b4b`.
- Baseline `origin/main`: `643163125a96a9bbbf3d0d87d527995416511b4b`.
- Baseline worktree: clean.
- Baseline index: clean.
- Higher integrated authority search: no
  `PAPER_PHASE6_INTEGRATED_REVISION_BASIS_v1.0` exists.
- Authority reconciliation: `PASS`.

## 3. Uploaded/current artifact identity

The user-inspected and pre-implementation Full artifact was
`docs/paper/manuscript/output/draft_full.docx`, SHA-256
`437846dff79b348937afd04a712235b035183223c81280bdc8adf52ab5099e27`.
The local baseline matched that identity exactly.

The mandatory pre-implementation inventory is recorded in
`phase6_3r7_preimplementation_figure_flow_diagnosis.json`.

## 4. Page 3 diagnosis

The current Figure 1 block was a top-level `wp:inline` drawing followed by its
caption. It was also moved to a later `HFUTHeading1` boundary, preceded by a
continuous two-column section end, followed by a one-column figure section,
and forced with `pageBreakBefore`. Word balanced the prematurely ended
two-column section and abandoned usable Page 3 height.

## 5. Page 5 diagnosis

Figure 2 was a tall top-level `wp:inline` drawing/caption block immediately
after the first callout. When it could not fit in the Page 5 right column, Word
moved it forward while later Section 4.2 prose remained trapped behind its
fixed document-order position.

## 6. Page 6 diagnosis

Figure 3 had the same ordering barrier. When the block could not fit, later
Section 4.4 prose, Section 4.5, and the conclusion could not use the remaining
Page 6 flow area before the figure.

## 7. Common root cause

`INLINE_FIGURE_FLOW_BARRIER` is confirmed for Figures 1, 2, and 3. A
top-level `wp:inline` object is an indivisible source-order object, not a
publication float.

## 8. Figure-1 special root cause

The additional cause was:

`FULL_WIDTH_SECTION_TRANSITION + pageBreakBefore + CONTINUOUS_SECTION_BALANCING`.

The `defer_page_top_figure_after_eligible_section_prose()` implementation still
depended on the next `HFUTHeading1`; changing literal heading text to a style
search did not remove the heading-semantic placement heuristic.

## 9. Current wp:inline/wp:anchor inventory

Pre-implementation inventory:

| Figure | Callout child | Drawing child | Caption child | `wp:inline` | `wp:anchor` | `keepNext` | `pageBreakBefore` | Extent EMU | Relationship target |
|---|---:|---:|---:|---|---|---|---|---|---|
| F1 | 39 | 45 | 46 | yes | no | yes | yes | 5759999 × 2851093 | `media/rId13.png` |
| F2 | 77 | 78 | 79 | yes | no | yes | no | 2699999 × 5575190 | `media/rId16.png` |
| F3 | 87 | 88 | 89 | yes | no | yes | no | 2699999 × 4380468 | `media/rId19.png` |

Post-implementation, each drawing remains `wp:inline` only *inside* a governed
`w:tblpPr` floating container. No figure drawing remains a top-level inline
body barrier. `wp:anchor` is not used because the selected container itself
provides the non-blocking float semantics and caption attachment.

## 10. R6 assumption retired

“A source-order `wp:inline` drawing/caption block behaves as a publication
float and later prose can pass it” is
`RETIRED_INCORRECT_IMPLEMENTATION_ASSUMPTION`.

## 11. Candidate figure-flow architectures considered

1. A `wp:anchor` image plus a separately anchored caption was rejected because
   it did not establish an inseparable, editable image/caption unit.
2. A DrawingML textbox/group containing image and text was rejected as more
   complex and less compatible with the existing Pandoc DrawingML payload.
3. A one-cell Word floating table was selected because `w:tblpPr` explicitly
   removes the table from main text flow while a single `w:cantSplit` row keeps
   drawing and editable caption together.
4. A manuscript-specific production marker fallback for Figure 1 was not
   needed; no semantic heading anchor remains.

## 12. Selected Figure-2/3 floating architecture

Figures 2 and 3 use one-column-width floating tables:

- width: 4252 dxa; drawing width remains 7.50 cm;
- `vertAnchor=text`, `horzAnchor=text`;
- `tblpXSpec=center`, `tblpY=1` (Word's serialized zero-distance behavior);
- all text distances: zero;
- `tblOverlap=never`;
- fixed table layout and zero cell margins;
- logical position immediately after the first callout;
- later ordinary prose remains in the main flow and can wrap past the float.

This is an active project implementation, not an HFUT rule.

## 13. Figure/caption attachment design

Each float contains exactly one row and one cell. The cell contains exactly:

```text
drawing paragraph
caption paragraph
```

The row has `w:cantSplit`; the drawing paragraph retains `keepNext`; the
caption remains `HFUTFigureCaption` editable text and does not gain
`keepNext`. Captions were not rasterized and no filler paragraphs were added.

## 14. Selected Figure-1 architecture

Figure 1 uses the same floating-container design at 9071 dxa table width with
the accepted 16.0 cm DrawingML extent. Its position is
`vertAnchor=margin`, `horzAnchor=margin`, `tblpXSpec=center`, and
`tblpYSpec=top`. It remains logically after its first callout, full-width, at
the page-margin top, captioned below, non-overlapping, and outside the main text
flow.

No `HFUTHeading1` search, named-heading map, production anchor manifest, or
figure-only section transition is used.

## 15. Figure-1 column-balancing diagnosis

`COLUMN_BALANCING_CAUSAL = YES`.

The baseline placed a continuous section end immediately before Figure 1,
which created a Word column-balance point. The new Figure 1 container carries
no section break. The final Full DOCX has three direct section boundaries
(front matter/body and the existing wide-table mechanism), rather than the
baseline five; the two Figure-1-only boundaries are gone.

## 16. pageBreakBefore disposition

`pageBreakBefore` was removed from Figure 1 and is absent from all three
floating figure drawing paragraphs. Page-top behavior is now expressed by the
Figure 1 floating-table vertical position, not a paragraph break.

## 17. Continuous-section disposition

The Figure-1 continuous two-column → one-column transition was removed. Other
continuous sections used for the established front-matter/body and wide-table
layout remain unchanged and are not part of this remediation.

## 18. Validator redesign

`validate_phase63_format.py` now:

- emits `INLINE_FIGURE_FLOW_BARRIER` if a governed float is absent;
- reports `placement_type=FLOATING` for each figure;
- requires exactly one marked `w:tblpPr` container per figure;
- validates width, position references, horizontal centering, non-overlap,
  image relationship, callout precedence, absence of `pageBreakBefore` and
  figure-specific sections, and Full/Anonymous parity;
- requires one inline drawing inside the float and no unexpected `wp:anchor`;
- requires the editable caption immediately after the drawing in one
  `w:cantSplit` row;
- reports structural text-wrap support without inferring that Microsoft Word
  will backfill space before every logical float anchor;
- emits only `IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW` for Pages 3, 5, and 6.

The Full, Anonymous, Phase 5.9C, final-reference, and Phase 6.1
non-regression validators were narrowly taught to distinguish the three
floating figure-container tables from the three scientific manuscript tables.

Global Full-DOCX figure-flow audit:

| Figure | First callout / float child | Placement / anchor paragraph | Association | Size / width mode | Text wrapping / earlier-space backfill | Section / break | Mechanism authority |
|---|---|---|---|---|---|---|---|
| F1 | 39 / 40 | Floating table; next regular anchor begins “性能响应进入路径比较之前…”; page-margin top/center | Drawing then editable caption in one `cantSplit` row | 5759999 × 2851093 EMU; 16.0 cm full width | supported / not guaranteed | no figure section; no `pageBreakBefore` | Supervisor page-top/full-width invariant; project implementation |
| F2 | 76 / 77 | Floating table; next regular anchor begins “从结构上看…”; text-column relative/centered | Drawing then editable caption in one `cantSplit` row | 2699999 × 5575190 EMU; 7.50 cm single column | supported / not guaranteed | none; no `pageBreakBefore` | HFUT width/caption invariants; project implementation |
| F3 | 85 / 86 | Floating table; next regular anchor begins “进程级均值范围均不重叠…”; text-column relative/centered | Drawing then editable caption in one `cantSplit` row | 2699999 × 4380468 EMU; 7.50 cm single column | supported / not guaranteed | none; no `pageBreakBefore` | HFUT width/caption invariants; project implementation |

Full/Anonymous image hashes, float properties, caption association, widths,
and relationship targets are identical. Anonymous child positions differ only
by the six removed identity paragraphs: F1 33/34, F2 70/71, F3 79/80.

## 19. Authority-ledger update

The ledger now explicitly records:

- `wp:inline figure block as a publication float` =
  `RETIRED_INCORRECT_IMPLEMENTATION_ASSUMPTION`;
- `Word floating figure/container` =
  `ACTIVE_PROJECT_IMPLEMENTATION_NOT_A_JOURNAL_RULE`;
- the one-row floating table, Figure 1 page-top positioning, and Figure 2/3
  column-relative positioning are implementation mechanisms, not publication
  authority;
- the heading anchor, Figure 1 `pageBreakBefore`, and figure-only continuous
  transition are removed mechanisms.

## 20. Manuscript-content change statement

`MANUSCRIPT_MARKDOWN_CHANGED = 0`.

No abstract, introduction, Section 1–5 prose, experiment description, result,
conclusion, bibliography source, CSL, table, equation manifest, or equation
content changed.

## 21. Figure-science non-regression

`STATISTICAL_GENERATOR_CHANGED = 0` and
`FIGURE_SCIENTIFIC_DATA_CHANGED = 0`.

The scientific PNG relationships and image hashes match between Full and
Anonymous:

- F1: `c562d5a3f1b930177ccacf90cfb467470bca7dd6c2d7597d92b7fe58292537c7`;
- F2: `00130111de0133f868d156bff9810c7e9387ea0a32c2ee000e804f7d2f27cbe1`;
- F3: `0205e472b2017f202c2c3fde071c4396f93e0aa5789a7dd19095f103b697abc8`.

F1 remains 16.0 cm; F2/F3 remain 7.50 cm. No figure was redrawn, resized,
split, or added.

## 22. Scientific non-regression

`SCIENTIFIC_NONREGRESSION = PASS`.

The frozen experiment-source hash, Figure 2/3 data hashes, formal RQ count,
equation inventory, correctness rows, metrics, directionality, limitation
language, and conclusion tokens passed
`validate_phase61_nonregression.py`. All 18 overclaim-term matches remain
legitimate negation or boundary language.

## 23. Full build

Command:

```text
bash scripts/paper/build_manuscript_docx.sh --build-full
```

Result: `FULL_BUILD = PASS`; active validators, citation checks, heading
numbering, Phase 5.9C integration, structural format validation, and DOCX ZIP
integrity passed.

## 24. Anonymous build

Command:

```text
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Result: `ANONYMOUS_BUILD = PASS`; anonymity scan, scientific body parity,
reference parity, figure-flow parity, and structural format validation passed.

## 25. Mechanical-render observations

LibreOffice 7.3 produced an 8-page Full PDF and 7-page Anonymous PDF. The
mechanical Full render showed all three drawings and captions without missing
content, overlap, clipping, corrupted sections, lost text, or blank pages.
Mechanically, F1 appeared at Page 3 top, F2 in the Page 5 right column, and F3
in the Page 6 left column while later prose continued in available flow.

These are gross checks only. No LibreOffice pagination result is promoted to a
Microsoft Word visual pass.

Mechanical PDF hashes:

- Full: `1baba96d9adaa9a477bd5f70bac13dcdc3b27dc77b7ccb6b25a6e9e41d351f87`;
- Anonymous: `2f5bb4b8a589517008c80e29f86f785ff35abe940cc645a941a210cd733dcc78`.

## 26. Latest Full DOCX path + SHA256

Path: `docs/paper/manuscript/output/draft_full.docx`.

SHA-256: `3279ac1e8319fcfe850379f0c5d344aa795188f8e13a2b92f6101f85c3a81809`.

## 27. Latest Anonymous DOCX path + SHA256

Path: `docs/paper/manuscript/output/draft_anonymous.docx`.

SHA-256: `18cd20181b4628a45e6d1a2a600b3ae9e884476468f5bbdae4dbf321076a846d`.

## 28. Changed files

- `scripts/paper/postprocess_full_manuscript_docx.py`;
- `scripts/paper/validate_phase63_format.py`;
- `scripts/paper/validate_phase61_nonregression.py`;
- `scripts/paper/validate_phase59c_integration.py`;
- `scripts/paper/validate_full_manuscript_docx.py`;
- `scripts/paper/validate_anonymous_manuscript_docx.py`;
- `scripts/paper/validate_final_references.py`;
- `docs/paper/phase6_3/PAPER_PHASE6_3_FIGURE_LAYOUT_AUTHORITY_LEDGER_v1.0.md`;
- `docs/paper/phase6_3/phase6_3_scientific_nonregression.json`;
- `docs/paper/phase6_3/phase6_3r7_preimplementation_figure_flow_diagnosis.json`;
- this report.

Generated DOCX/PDF artifacts remain ignored and are not committed.

## 29. Diff scope

The diff is format-only. It replaces the figure-placement mechanism, updates
validators that must understand the new container, records the authority
change, and records validation evidence. No Markdown manuscript section,
reference database, CSL, scientific figure asset/data, statistical generator,
table content, equation manifest, or deployment source is changed.

## 30. Microsoft Word QA targets

The required state is:

- `PAGE3_FLOW = IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW`;
- `PAGE5_FLOW = IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW`;
- `PAGE6_FLOW = IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW`;
- `MICROSOFT_WORD_VISUAL_QA = PENDING`;
- `HFUT_SUBMISSION_READY = NO`.

Open the exact latest Full DOCX in Microsoft Word and verify:

1. Page 3 ordinary prose uses the former blank area and Figure 1 remains at a
   page top with no body text above it on that page.
2. Figure 1 remains 16.0 cm full-width, centered, unclipped, captioned below,
   and has no two-column/full-width/two-column sandwich above and below it.
3. Page 5 later Section 4.2 prose can use the area that was previously blank;
   Figure 2 remains after its first callout, 7.50 cm wide, readable, centered,
   unclipped, and attached to its caption.
4. Page 6 later Section 4.4 prose can use the area that was previously blank;
   Figure 3 remains after its first callout, 7.50 cm wide, readable, centered,
   unclipped, and attached to its caption.
5. No figure overlaps text, crosses a margin, loses its anchor, or separates
   from its caption after Word repaginates and saves the document.
6. No unrelated page, table, equation, heading, or reference regresses.

## 31. Commit

Exactly one commit is to be created with message:

```text
paper: replace inline figure barriers with Word floats
```

The definitive commit SHA is returned in the handoff rather than
self-embedded, avoiding an amend cycle. No push, tag, merge, reset, clean,
rebase, or amend is performed.

## 32. Exact next action

After the user manually pushes the single commit, open
`docs/paper/manuscript/output/draft_full.docx` with SHA-256
`3279ac1e8319fcfe850379f0c5d344aa795188f8e13a2b92f6101f85c3a81809`
in Microsoft Word, allow complete repagination, export a Word PDF, and inspect
the six QA targets above. Report the resulting Word DOCX/PDF hashes and the
actual Page 3, Page 5, and Page 6 composition. Do not treat the LibreOffice
render as final evidence.
