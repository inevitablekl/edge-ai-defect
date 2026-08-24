# Paper Phase 6.3R6 Non-Authoritative Placement Constraint Removal Report v1.0

## 1. Verdict

`PHASE_6_3_NONAUTHORITATIVE_PLACEMENT_CONSTRAINTS_REMOVED`.

The named-heading placement map, mandatory intervening-body gate, and 15.5 cm
publication-height failure have been removed. The replacement is figure
eligibility plus governed geometry/association invariants. Microsoft Word
visual acceptance remains pending.

## 2. Baseline

- Branch: `main`.
- Starting `HEAD`: `fa6e9525d5bad4b04f61a92c35ed7cdc11ec231d`.
- Starting `origin/main`: `fa6e9525d5bad4b04f61a92c35ed7cdc11ec231d`.
- Starting commit: `paper: stabilize adaptive figure flow for Word layout`.
- Worktree and index: clean.
- Integrated authority search: `PAPER_PHASE6_INTEGRATED_REVISION_BASIS_v1.0`
  was not present; no authority conflict required reconciliation.

No rollback, reset, clean, rebase, merge, amend, push, or tag was performed.

## 3. Microsoft Word findings

The user-provided real Word evidence is the visual authority: Figure 1's first
callout was on manuscript Page 3 while the drawing was delayed to Page 5;
Page 4 ended early because of that schedule; Page 5 also retained visible
unused lower-page space before Figure 2. No scientific-content or Figure 2/3
optical-centering defect was identified.

## 4. Current placement rules discovered

At baseline, `FIGURE_PLACEMENT_BEFORE` mapped Figure 1 to Section 3.3,
Figure 2 to Section 4.3, and Figure 3 to Section 4.5. The Phase 6.3 validator
also required an intervening `HFUTBody` paragraph before Figures 2/3 and
failed a single-column drawing above `MAX_SINGLE_COLUMN_HEIGHT_CM = 15.5`.

These were implementation policies created by the project, not HFUT rules.

## 5. Authority classification

The machine-readable-by-table authority record is
`PAPER_PHASE6_3_FIGURE_LAYOUT_AUTHORITY_LEDGER_v1.0.md`. It distinguishes:

- HFUT/academic invariants: callout precedence, captions below associated
  drawings, numbering, width compatibility, readability, and manuscript bounds;
- supervisor invariant: full-width Figure 1 remains at page top without a
  same-page two-column/full-width/two-column sandwich;
- project heuristics: named-heading adjacency, mandatory intervening prose,
  15.5 cm height cutoff, and optical QA thresholds.

## 6. Rules retained

The builds still require exactly three governed figure identities, first
callout before drawing, caption immediately below drawing, drawing/caption
attachment, sequential identity, Figure 1 at 16.00 cm full width, Figures 2/3
at 7.50 cm single-column width, a coherent Figure 1 one-column section,
no accidental Figure 2/3 full-width section, no Figure 2/3 page break,
scientific data hashes, optical QA diagnostics, lifecycle state, and
Full/Anonymous parity.

## 7. Rules removed

- `FIGURE_PLACEMENT_BEFORE` and all three named text anchors.
- Figure 1 adjacency to Section 3.3.
- Figure 2 adjacency/barrier before Section 4.3.
- Figure 3 adjacency/barrier before Section 4.5.
- Mandatory intervening `HFUTBody` prose before Figures 2/3.
- Any validator interpretation that a particular heading adjacency is a
  publication requirement.

Repository search after the rebuild found no obsolete placement-map symbol,
named placement text, or intervening-body failure message in the active paper
postprocessor/validator.

## 8. Rules downgraded to diagnostics

The 15.5 cm value is now `ADVISORY_SINGLE_COLUMN_HEIGHT_CM`; it is reported in
the figure layout contract but never fails the build. Optical bounding-box and
centering thresholds remain project QA heuristics. Callout proximity is a new
diagnostic and has no arbitrary rejection threshold.

## 9. Figure 1 placement redesign

Figure 1 becomes eligible after its first callout. Because it is governed as a
page-top full-width figure, the postprocessor permits the remaining ordinary
prose in the current top-level section to flow before it, locating the figure
at the next structural top-level boundary without matching any heading text.
The implementation then retains `pageBreakBefore`, `keepNext`, the 2-column →
1-column continuous-section transition, the 16.00 × 7.92 cm drawing, and the
caption below it.

This structural eligibility mechanism is an implementation choice, not a new
publication rule or named semantic anchor. The supplementary render places the
callout on Page 3 and Figure 1 at Page 4 top while filling Page 3 naturally.
Word status: `IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW`.

## 10. Figure 2 placement redesign

Figure 2 stays in source order immediately after its first callout. It is no
longer moved before Section 4.3 and no prose-distance proof is required. Word
may move the indivisible inline drawing/caption block to its next feasible
column/page while later prose uses subsequent available flow. It remains
7.50 × 15.49 cm, single-column, centered, captioned below, and has no forced
page break or section transition.

Status: `IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW`.

## 11. Figure 3 placement redesign

Figure 3 likewise stays in source order immediately after its first callout,
with no Section 4.5 barrier and no required intervening paragraph. It remains
7.50 × 12.17 cm, single-column, centered, captioned below, and has no forced
page break or section transition.

Status: `IMPLEMENTED_PENDING_MICROSOFT_WORD_REVIEW`.

## 12. Figure callout-proximity audit

Full DOCX OOXML positions are one-based body-child positions:

| Figure | First callout | Drawing | Intervening headings | Intervening `HFUTBody` paragraphs |
|---|---:|---:|---:|---:|
| Figure 1 | 39 | 45 | 0 | 4 |
| Figure 2 | 77 | 78 | 0 | 0 |
| Figure 3 | 87 | 88 | 0 | 0 |

Anonymous positions are 33→39, 71→72, and 81→82 respectively, with identical
intervening counts. No figure crosses a heading between first callout and
drawing. This diagnostic establishes reasonable document-order proximity but
does not assert Microsoft Word page numbers.

## 13. 15.5 cm rule disposition

`15_5_CM_HEIGHT_RULE = ADVISORY_NOT_PUBLICATION_REQUIREMENT`.

The accepted compact Figure 2/3 assets were not enlarged, regenerated, or
otherwise changed. Their measured heights remain 15.49 cm and 12.17 cm.

## 14. Validator changes

`validate_phase63_format.py` now:

- reports callout/drawing positions and intervening heading/body counts;
- accepts both callout→figure and callout→ordinary prose→figure;
- records 15.5 cm as advisory metadata rather than a build failure;
- continues enforcing actual caption, width, section, page-break, lifecycle,
  scientific-hash, optical-QA, and Full/Anonymous invariants;
- explicitly prints that Microsoft Word visual QA is pending.

The regenerated non-regression artifact records phase `PAPER_PHASE_6_3R6`.

## 15. Content-change statement

- `MANUSCRIPT_MARKDOWN_CHANGED = 0`.
- `BIBTEX_CHANGED = 0`.
- `CSL_CHANGED = 0`.
- `SCIENTIFIC_FIGURE_DATA_CHANGED = 0`.
- `TABLE_DATA_CHANGED = 0`.
- `EQUATION_CONTENT_CHANGED = 0`.
- `SCIENTIFIC_PROSE_CHANGED = 0`.

No abstract, introduction, Section 1–5 prose, experiment number, table,
equation, reference, caption, callout, or figure scientific asset changed.

## 16. Scientific non-regression

`SCIENTIFIC_NONREGRESSION = PASS` using
`validate_phase61_nonregression.py`.

- Experiment source SHA-256:
  `20f45e645dce7f76c47aa7369e69b580ff64a6ceb8a09b5b67074d173afef5aa`.
- Figure 2/3 run-level data SHA-256:
  `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31`.
- Figure 2/3 publication-values SHA-256:
  `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655`.
- Three equations, RQ1/RQ2, three correctness rows, Figure 1 semantics, all
  numerical tokens, boundary statements, tables, and references passed.
- All 18 watched overclaim matches remain legitimate negations/boundaries.

Artifact: `docs/paper/phase6_3/phase6_3_scientific_nonregression.json`.

## 17. Full build

PASS:

```text
bash scripts/paper/build_manuscript_docx.sh --build-full
```

All build-integrated heading, citation, reference, Full-manuscript,
Phase 5.9C, and Phase 6.3 structural validators passed.

## 18. Anonymous build

PASS:

```text
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Identity scan, scientific-body parity, reference parity, figure layout parity,
and the Phase 6.3 structural validator passed.

## 19. Mechanical-render observations

LibreOffice produced two eight-page A4 supplementary PDFs:

- Full: 677,839 bytes; SHA-256
  `ae67cc3356fa330e001a1a7388111015182e6e6e6d84372979fb6018ee0a4024`.
- Anonymous: 665,821 bytes; SHA-256
  `427ff011edf64bd24dd72049310f6c3ec095bcc4b58a4f2903d2e3323445118a`.

Gross inspection found no blank page, missing figure/caption, clipping,
overlap, lost content, or broken section. Page 3 uses both columns naturally;
Figure 1 is full-width at Page 4 top with its caption below and two-column body
resuming below. Page 5 is naturally filled before Figure 2; Figure 2 appears
single-column on Page 6 while Sections 4.3/4.4 use available flow. Figure 3 is
single-column on Page 7 without a Section 4.5 barrier.

These are supporting observations only. They do not prove Microsoft Word
pagination, typography, page count, or artifact acceptance.

## 20. Full DOCX path + SHA256

Path: `docs/paper/manuscript/output/draft_full.docx`.

SHA-256: `437846dff79b348937afd04a712235b035183223c81280bdc8adf52ab5099e27`.

## 21. Anonymous DOCX path + SHA256

Path: `docs/paper/manuscript/output/draft_anonymous.docx`.

SHA-256: `e8a7ae8440f0057c6057f2e38aa4d699359fbc3a9f064e96ccf20149a617cc57`.

## 22. Files changed

- `scripts/paper/postprocess_full_manuscript_docx.py`.
- `scripts/paper/validate_phase63_format.py`.
- `docs/paper/phase6_3/PAPER_PHASE6_3_FIGURE_LAYOUT_AUTHORITY_LEDGER_v1.0.md`.
- `docs/paper/phase6_3/phase6_3_scientific_nonregression.json`.
- This report.

Generated DOCX/PDF files remain ignored and are not committed.

## 23. Git diff

The complete unstaged diff was reviewed before commit. It contains only the
placement postprocessor, validator semantics/diagnostics, authority ledger,
R6 validation phase label, and this report. There is no staged pre-existing
change and no diff in Markdown manuscript sections, BibTeX, CSL, scientific
figure data/assets, table data, equations, or production deployment code.

## 24. Microsoft Word QA still required

`MICROSOFT_WORD_VISUAL_QA = PENDING` and `HFUT_SUBMISSION_READY = NO`.

The headless pipeline cannot certify the Page 3→4 Figure 1 transition or exact
Word pagination. No claim such as `PAGE4_BLANK_FIXED`, `PAGE5_BLANK_FIXED`, or
`FIGURE1_DISTANCE_FIXED` is made from LibreOffice evidence.

## 25. Commit

Exactly one commit is to be created with message:

```text
paper: remove rigid figure placement heuristics
```

The definitive commit SHA is returned in the handoff rather than self-embedded,
avoiding an amend cycle. No push is performed.

## 26. Exact next action

Open the exact latest Full DOCX in Microsoft Word, allow Word to repaginate,
export the Word PDF, and inspect:

1. Figure 1 first callout versus drawing distance (bad baseline Page 3→Page 5;
   desired substantially closer, preferably Page 3→Page 4 top).
2. The page immediately before Figure 1 for no large artificial lower-page blank.
3. The page immediately before Figure 2 for no large artificial lower-page blank.
4. Figure 1 remains page-top, full-width, captioned below, with no same-page
   two-column/full-width/two-column sandwich.
5. Figure 2 remains readable and optically centered.
6. Figure 3 has no visual or pagination regression.
7. All other pages have no new clipping, overlap, orphaned caption/heading,
   margin overflow, lost content, or reference regression.

Required handoff state:

- `PROJECT_HEADING_ANCHORS = REMOVED`;
- `MANDATORY_INTERVENING_BODY_RULE = REMOVED`;
- `15_5_CM_HEIGHT_RULE = ADVISORY_NOT_PUBLICATION_REQUIREMENT`;
- `FIGURE1_PAGE_FLOW = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `FIGURE2_PAGE_FLOW = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `FIGURE3_PAGE_FLOW = IMPLEMENTED_PENDING_WORD_REVIEW`;
- `FIGURE1_CALL_OUT_PROXIMITY = IMPROVED_PENDING_WORD_REVIEW`;
- `SCIENTIFIC_NONREGRESSION = PASS`;
- `STRUCTURAL_FORMAT_VALIDATION = PASS`;
- `MICROSOFT_WORD_VISUAL_QA = PENDING`;
- `HFUT_SUBMISSION_READY = NO`.
