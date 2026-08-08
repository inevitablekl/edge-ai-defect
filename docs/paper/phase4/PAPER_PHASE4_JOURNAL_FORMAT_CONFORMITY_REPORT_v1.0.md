# Paper Phase 4.8 Journal Format Conformity Report

## 1. Verdict

`JOURNAL_FORMAT_CANDIDATE_READY_FOR_WORD`

The final Full and Anonymous candidates pass the available structural, identity,
scientific-parity, reference, ZIP/XML, and LibreOffice mechanical-rendering checks.
This is a candidate for Phase 4.9 Windows Microsoft Word inspection, not a
submission-ready declaration.

## 2. Repository State

- Starting HEAD: `d133694dbd42db1be3d0c48ff94642100d70e6bc`.
- Final HEAD authority: the commit containing this report.
- Branch: `main`.
- Starting worktree/index: clean.
- Final committed worktree/index: required clean; recorded in the executor handoff.

## 3. Authority

- Canonical reference DOCX SHA256:
  `416e881fbd6c79963a0b18fc6bcbd490134d12a5b8e88fe5deb91146803ca1a7`.
- The canonical reference DOCX was not modified.
- Phase 2.5 specification, Style Map, regression matrix, remediation report,
  final freeze, and Phase 4.7 citation report were retained as authorities.
- Textually explicit journal requirements remain distinguished from
  style-evidence/project-derived geometry, spacing, indentation, and layout
  candidates.

### F1 caption authority reconciliation

- Record: `F1_CAPTION_AUTHORITY_RECONCILIATION`.
- Classification:
  `STALE_PHASE3_MANUSCRIPT_CAPTION_SYNCHRONIZED_TO_PHASE4_FINAL_FIGURE_AUTHORITY`.
- F1 caption authority: `RESOLVED_TO_PHASE4_FINAL_AUTHORITY`.
- Final F1 caption: `图1　V0、V2R和V3R数据路径示意`.
- Stale manuscript caption: `REMOVED`.
- Section 1.3 timing-boundary definition: `UNCHANGED`.
- Final Figure 1 artifact: `UNCHANGED`.
- Scientific impact: `NONE`.
- Cross-reference validation: `PASS`.

Phase 4.7 validated stale integration text; its historical report was not
rewritten. Phase 4.8 synchronized only the authorized callout sentence and F1
caption to the already accepted Phase 4 figure authority. The study's timing
boundary remains defined in Section 1.3.

## 4. Page / Section Geometry

- A4 portrait: `11906 × 16838 twips`.
- Margins: top `1361`, right `1304`, bottom `1134`, left `1304`; gutter `0`.
- Column gap: `425 twips`.
- Final transitions: front matter 1 column; body 2 columns; F1 span 1 column;
  body immediately returns to 2 columns (`[1,2,1,2]`).
- All transitions are continuous; no page-number restart is present.
- These exact values are retained frozen style-evidence/project candidates,
  not promoted to universal textual journal requirements.

## 5. Front Matter

- Chinese title: accepted text, `HFUTTitleCN`, 16 Chinese characters under the
  project safe limit of 20.
- English title: accepted text, `HFUTTitleEN`.
- Full authors/affiliations use the accepted semantic styles; Anonymous omits them.
- Chinese abstract count: 340 Chinese characters.
- Chinese keywords: 5; English keywords: 5.
- Abstract, keyword, and classification semantic-style usage: PASS.
- Corresponding author remains 王琦 / WANG Qi.
- `CORRESPONDING_EMAIL_PENDING_FINAL_METADATA_FREEZE`; accepted email omission
  is not a Phase 4.8 format blocker.

## 6. Biography

- Full: accepted biography appears exactly once in the package, in the
  first-page footer, using `HFUTAuthorBiography`; body duplication is zero.
- Full first footer and later/default footer each retain a PAGE field.
- Anonymous: biography count is zero in body, footer, and package.
- Anonymous first/default footer PAGE mechanism matches Full without identity.

## 7. Body / Headings

- `HFUTBody`: Songti / Times New Roman, 10.5 pt, justified, 200-twip
  first-line indent, exact 16 pt project candidate.
- `HFUTHeading1/2/3`: frozen 14/10.5/10.5 pt and Heiti/Heiti/Kaiti contracts;
  keep-next/keep-lines candidate behavior retained.
- Introduction and body heading hierarchy remain intact.
- `参考文献` uses `HFUTReferenceHeading`, has no direct `w:numPr`, and remains
  visibly unnumbered in the mechanical render.
- Formal display equations found: zero.
- `FORMAL_EQUATION_REQUIREMENT = NOT_APPLICABLE_TO_CURRENT_MANUSCRIPT`.

## 8. Figures

| Figure | Final asset in DOCX | Placement | DOCX extent | PNG pixels | Effective density | Residual limitation |
|---|---|---|---|---:|---:|---|
| F1 | accepted PNG fallback from frozen final SVG | full width | 16.000 × 3.413 cm | 961 × 205 | 60.1 px/cm (about 153 ppi) | `RASTER_CLARITY_MANUAL_CONFIRMATION_REQUIRED` |
| F2 | accepted final PNG | single column | 7.500 × 5.805 cm | 885 × 685 | 118.0 px/cm (about 300 ppi) | `TYPOGRAPHY_MANUAL_CONFIRMATION_REQUIRED` |
| F3 | accepted final PNG | single column | 7.500 × 5.671 cm | 968 × 732 | 129.1 px/cm (about 328 ppi) | `TYPOGRAPHY_MANUAL_CONFIRMATION_REQUIRED` |

All three keep their aspect ratios. Callouts precede drawings, captions follow
drawings, F1 returns immediately to two-column body flow, and F2/F3 extents are
unchanged. No universal mandatory DPI threshold is claimed.

## 9. Tables

- T1: 17 frozen data rows.
- T2: 4 frozen data rows; V0/V2R only; V3R absent.
- Both retain 1 pt top/bottom rules, 0.5 pt header-bottom rules, no vertical
  rules, and no internal body-row gridlines.
- Content uses the 7.5 pt Songti / Times New Roman candidate.
- LibreOffice rendering showed no obvious overflow; final wrapping and page
  break judgment remains a Word-manual item.

## 10. References

- Phase 4.7 citation semantics, `references.bib`, and CSL semantics remain frozen.
- 14 cited entries render in sequential first-occurrence order; the one admitted
  unused library entry remains unrendered by design.
- `HFUTReferenceEntry / Bibliography`: Songti / Times New Roman, 7.5 pt,
  exact 14 pt; 360-twip hanging-indent project candidate retained.
- Reference heading remains unnumbered.
- Result: `STRUCTURAL_REFERENCE_TYPOGRAPHY_PASS`; no Windows typography pass is claimed.

## 11. Full / Anonymous

- Full build: PASS; SHA256
  `a7fa057fffbfb9989cc779dddb41716e325ca311a6d17d0093b4b3d452357a5c`.
- Anonymous build: PASS; SHA256
  `f79222e7335551d5a37d92b90ff8102c9e6eff947f59383d3b5c5e96a9805fbd`.
- Scientific body parity: PASS.
- Rendered bibliography parity: PASS.
- Anonymous identity scan: PASS.
- Page geometry, styles, figures, tables, captions, references, section logic,
  and page-number mechanism are structurally aligned apart from authorized identity content.

## 12. Mechanical Rendering

- LibreOffice 7.3 conversion: PASS for Full and Anonymous.
- Full: 9 pages, A4 (`595.304 × 841.89 pt`).
- Anonymous: 9 pages, A4 (`595.304 × 841.89 pt`).
- Every page contains extracted non-whitespace text; no obvious blank page.
- F1 appears on page 3; F2/F3 and T2 appear on page 7; references reach page 9.
- No obviously missing figure, cropping, table overflow, or broken section transition
  was observed in the mechanical page review.
- LibreOffice rendering is not asserted to be visually equivalent to Microsoft Word.

## 13. Scientific Freeze

- Prose changed outside the two authorized F1 synchronizations: NO.
- Frozen values changed: NO.
- CSL semantics changed: NO.
- Bibliography metadata changed: NO.
- Figure/table scientific artifacts changed: NO.
- Timing-boundary definition changed: NO.
- Final F1 artifact changed: NO.
- Six frozen result values and P95-higher/P99-lower mixed-tail direction remain present.

## 14. Open Word-Manual Items

- First-open and save/close/reopen without repair warning.
- Title and heading wrapping.
- First-page biography/footer and PAGE-field visual behavior.
- F1 raster sharpness and actual readability at 16 cm.
- F2/F3 Liberation Serif fallback and label readability.
- Table wrapping/pagination and final reference typography.
- `Ctrl+A`/`F9` controlled field refresh.
- Full and Anonymous Word Document Inspector passes.
- Final page and no-blank-page confirmation in Word.

Use `PAPER_PHASE4_WORD_MANUAL_REVIEW_CHECKLIST_v1.0.md`; record failures before
making any Word-side correction.

## 15. Recommendation

`PHASE_4_9_WORD_REVIEW_READY`
