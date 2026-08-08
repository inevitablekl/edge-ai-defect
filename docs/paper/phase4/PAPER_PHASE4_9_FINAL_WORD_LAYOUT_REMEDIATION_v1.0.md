# Paper Phase 4.9 Final Word Layout Remediation Report

## 1. Verdict

`PHASE_4_9_FINAL_RETEST_READY`

The remediation is limited to the three frozen manual findings. Mechanical,
structural, anonymity, parity, and LibreOffice visual checks pass. Microsoft
Word remains the final authority for the three remaining manual retests.

## 2. Manual Findings Frozen

- `P4.9-F1` — `F1_WORD_PAGINATION_EXCESSIVE_WHITESPACE`
- `P4.9-T1-01` — `TABLE1_THREE_LINE_RULE_VISIBILITY_DEFECT`
- `P4.9-T1-02` — `TABLE1_WRAPPED_CELL_CONTINUATION_ALIGNMENT_DEFECT`

No additional publication-improvement scope was opened.

## 3. F1 Diagnosis

The paragraph section ending before F1 and the one-column F1 section both had
`w:type="continuous"`. The final two-column body section after the F1 caption,
however, had no `w:type`; OOXML therefore gave that section the default
next-page behavior. This forced section 1.3 to a new page even when usable space
remained below F1.

The postprocessor now sets the final two-column body section to
`w:type="continuous"`. The F1 callout, drawing, caption, 16.0 cm by 3.413 cm
extent, source asset, and section 1.3 text are unchanged. No floating anchor,
text box, or generic layout engine was introduced.

- Full: F1 and section 1.3 now share page 4; page count changed from 10 to 9.
- Anonymous: F1 and section 1.3 share page 3; page count remains 9.
- LibreOffice visual result: PASS for both builds and the immediately adjacent
  pages.

## 4. Table 1 Border Diagnosis

The table-level border state already specified 1 pt top and bottom rules and
nil internal rules. Cell-level borders conflicted with that state: first-row
cells had a nil top border, and the final-row cells had a nil bottom border.
Microsoft Word border resolution could therefore suppress the intended outer
rules.

The common table helper now receives the row index and final-row index and
emits explicit cell-boundary rules:

- first row: 1 pt top and 0.5 pt bottom;
- middle rows: nil top and bottom;
- final row: nil top and 1 pt bottom;
- every row: nil left and right;
- table level: nil inside-horizontal and inside-vertical rules.

The same boundary redundancy is applied to Table 2 without changing its
three-line visual appearance. The validators now inspect cell-level boundaries,
not only `tblBorders`.

## 5. Table 1 Wrap Alignment

`HFUTTableContent` inherits from `Normal`, whose reference-style paragraph has
a first-line indent. The prior table postprocessor set style and alignment but
did not neutralize the inherited indentation directly.

Every Table 1 cell paragraph now has direct `left="0"`, `right="0"`, and
`firstLine="0"`; hanging and character-based indent overrides are removed, as
are unexpected paragraph tabs. Header paragraphs remain centered, while both
body columns remain left-aligned. Font, size, and line spacing are unchanged.

The exact existing cell text
`1080 帧，即 180 幅图像完整回放 6 个周期` occurs once in each build and is
unchanged. Its continuation line begins at the configuration-column paragraph
boundary in both rendered Table 1 pages.

## 6. Full Build

- Path: `docs/paper/manuscript/output/draft_full.docx`
- SHA256: `a72e17f46687f731a2b54d4933623757e6923bfee4b949f77d609673e3988b11`
- Page count: 9, A4
- Build command: `scripts/paper/build_manuscript_docx.sh --build-full`
- Citation, static cross-reference, rendered bibliography, reference
  typography, manuscript structure, and narrow Table 1 validation: PASS.

## 7. Anonymous Build

- Path: `docs/paper/manuscript/output/draft_anonymous.docx`
- SHA256: `81d4769094fd47d026143d280b0005ed60d33e5efba71072f1a9566eae79a31d`
- Page count: 9, A4
- Build command: `scripts/paper/build_manuscript_docx.sh --build-anonymous`
- `ANONYMITY_SCAN_PASS`
- `PARITY_PASS`
- Citation, rendered bibliography, reference typography, structure, and
  narrow Table 1 validation: PASS.

## 8. Visual QA

- Full F1: pages 3–5 inspected; F1 and section 1.3 share page 4 with no F1-only
  page or excessive lower-page whitespace.
- Full Table 1: page 6 inspected; top, header-bottom, and bottom rules are
  visible; no body gridlines are visible; the wrapped measurement cell aligns.
- Anonymous F1: pages 2–4 inspected; F1 and section 1.3 share page 3 and the
  surrounding two-column flow is intact.
- Anonymous Table 1: page 6 inspected; all three rules and wrapped-cell
  alignment pass.
- Table 2: page 7 in both builds inspected; appearance remains a clean
  three-line table.
- Figures 2 and 3: Full page 8 and Anonymous pages 7–8 inspected; visibility
  and labels remain intact.

LibreOffice-generated PDF and 150 dpi page PNG review: PASS. Microsoft Word
pagination remains the final manual authority.

## 9. Regression

- Full first-page biography package count: 1; Anonymous: 0.
- PAGE fields: 2 in each build; no page-number restart introduced.
- Section column sequence: `[1, 2, 1, 2]` in both builds.
- F1/F2/F3: three inline drawings, unchanged media extents and no anchors.
- Table 2: content and rendered appearance unchanged.
- References: 14 rendered entries from 15 bibliography records; Full and
  Anonymous bibliography parity PASS.
- Anonymous creator is empty, `lastModifiedBy` is absent, and comments,
  revisions, revision authors, and identity package hits are absent.
- `scripts/paper/build_manuscript_docx.sh --check`: PASS.
- `validate_journal_format_docx.py`: PASS.
- Python compilation, shell syntax, and `git diff --check`: PASS.

The historical pre-authoring `validate_manuscript_assets.py` and
`validate_manuscript_sources.py` gates still demand a skeleton-only manuscript
and an empty generated-output directory. They are not final-manuscript
acceptance validators and predictably reject the already-authorized Phase 4
prose/assets/outputs. The historical format-regression audit likewise pins old
DOCX SHA256 values. These legacy results do not identify a change in this
remediation.

## 10. Scientific Freeze

PASS.

- `2.236671×`
- `55.4519%`
- `4.0738%`
- `4.0349%`
- `0.1514%`
- `0.1184%`
- P95: higher/slower
- P99: lower/faster
- Tail: `MIXED`

No manuscript Markdown, references, CSL, figure assets, table content
specifications, or scientific claims changed.

## 11. Remaining Manual Retest

Only:

- Full F1 pagination;
- Full Table 1;
- Anonymous Table 1.

## 12. Recommendation

`PHASE_4_9_FINAL_RETEST_READY`
