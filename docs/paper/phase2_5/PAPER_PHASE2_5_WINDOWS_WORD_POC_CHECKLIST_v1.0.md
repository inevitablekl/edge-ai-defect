# Paper Phase 2.5 Windows Word POC Checklist v1.0

## 1. Scope

Use this checklist for the two Step 6 POC files only. They are
`TOOLCHAIN_POC_ONLY`, `SYNTHETIC_CONTENT`, `NOT_PAPER_CONTENT`, and
`NOT_SUBMISSION_MANUSCRIPT`. Do not use POC results to approve a formal
submission manuscript.

Acceptance must use Microsoft Word on Windows. WPS or LibreOffice observations
may be recorded as supplementary evidence but cannot close a Microsoft Word
item. Begin with clean copies of `poc_full.docx` and `poc_anonymous.docx`.

## 2. Manual checklist

| ID | Check | Method and pass condition | Result |
|---|---|---|---|
| W01 | Microsoft Word authority | Open both files in desktop Microsoft Word; do not close this item with WPS. | `PENDING_USER_MANUAL` |
| W02 | Open without repair | Neither file displays a corruption, recovery, compatibility, or repair prompt. | `PENDING_USER_MANUAL` |
| W03 | Page geometry | Confirm A4 portrait and margins: top about 2.4 cm, bottom about 2.0 cm, left/right about 2.3 cm. | `PENDING_USER_MANUAL` |
| W04 | Section columns | Confirm bilingual front matter is one column and body is two columns with about 0.748 cm spacing. | `PENDING_USER_MANUAL` |
| W05 | Section boundary and pagination | Confirm body begins after the semantic front-matter boundary, page numbers continue, and no blank page is introduced. | `PENDING_USER_MANUAL` |
| W06 | Named styles | Inspect Chinese/English titles, authors/affiliations in full, abstracts, keywords, classification, body, captions, table text, and references for the intended `HFUT*` styles. | `PENDING_USER_MANUAL` |
| W07 | Multilevel numbering | Verify visual `0`, `1`, `1.1`, and `1.1.1`; inspect list linkage and confirm the introduction/body restart behavior. | `PENDING_USER_MANUAL` |
| W08 | Field refresh | Press Ctrl+A and F9; verify headings and PAGE remain correct and no unexpected field text appears. | `PENDING_USER_MANUAL` |
| W09 | PAGE field | Confirm visible page numbers are continuous and are fields rather than fixed text. | `PENDING_USER_MANUAL` |
| W10 | Editable Word formulas | Select the inline and two display formulas and confirm they are editable Word equations without being pictures. | `PENDING_USER_MANUAL` |
| W11 | Formula typography | Inspect fractions, sum, superscripts/subscripts, upright/italic behavior, and formula line layout. Do not infer compliance from OOXML alone. | `PENDING_USER_MANUAL` |
| W12 | MathType | Test whether MathType can recognize or convert the OMML formulas. If unavailable, record `TOOL_NOT_AVAILABLE / DEFERRED_PUBLICATION_ASSET_CHECK`, not PASS. | `PENDING_USER_MANUAL` |
| W13 | Formula numbering/cross-reference | Confirm the displayed “（1）” and “式（1）” are static test text, not dynamic fields; record the chosen future Word/manual workflow. | `PENDING_USER_MANUAL` |
| W14 | Figure display | Confirm the synthetic three-bar figure displays, fits within 7.5 cm, follows its first callout, and uses `HFUTFigureCaption`. | `PENDING_USER_MANUAL` |
| W15 | Figure object boundary | Confirm the DOCX uses a PNG display fallback while retaining an SVG package copy; do not claim Origin/Visio editability. | `PENDING_USER_MANUAL` |
| W16 | Figure numbering/cross-reference | Confirm “图1” is static test text and no SEQ/REF field is falsely present. | `PENDING_USER_MANUAL` |
| W17 | Three-line table | Confirm three columns and three data rows, all values/notes, no vertical lines, top/bottom 1 pt, and header rule 0.5 pt. | `PENDING_USER_MANUAL` |
| W18 | Table style and fit | Confirm `HFUTThreeLineTable`/`HFUTTableContent`, single-column fit, and no clipping or overlap. | `PENDING_USER_MANUAL` |
| W19 | Table numbering/cross-reference | Confirm “表1” and its first callout are static test text, not dynamic fields. | `PENDING_USER_MANUAL` |
| W20 | Citations | Confirm first-occurrence numeric order `[1]`, `[2,3]`, `[4]`, `[5]`, with no unresolved citation key. | `PENDING_USER_MANUAL` |
| W21 | Reference list | Inspect all five synthetic entries. Record that the standard currently renders `[Z]`, not the HFUT attachment's `[S]`, and do not approve HFUT-specific CSL conformance. | `PENDING_USER_MANUAL` |
| W22 | Full identity | Confirm only the obvious POC test identity/contact/funding/biography/acknowledgement fields appear in the full copy. | `PENDING_USER_MANUAL` |
| W23 | Anonymous visible content | Search for all full-copy test identity/contact/funding/biography/acknowledgement strings; none may appear. | `PENDING_USER_MANUAL` |
| W24 | Document Inspector | Run File → Info → Check for Issues → Inspect Document on the anonymous copy; remove or record properties, comments, revisions, hidden content, and identity carriers. | `PENDING_USER_MANUAL` |
| W25 | Save/reopen | Save each checked copy under a new local name, close Word, reopen, and confirm no repair prompt or layout loss. | `PENDING_USER_MANUAL` |
| W26 | Export PDF | Export both checked copies from Microsoft Word and compare page count, columns, numbering, formulas, figure, table, references, and page numbers. | `PENDING_USER_MANUAL` |

## 3. Publication-asset tools

MathType, Visio, and Origin were not available in the Linux POC environment:

```text
TOOL_NOT_AVAILABLE
DEFERRED_PUBLICATION_ASSET_CHECK
```

If any tool is also unavailable on the Windows review host, retain those exact
statuses. Absence is not a PASS and does not block recording the remaining
Microsoft Word observations.

## 4. Completion record

Record Microsoft Word version, Windows version, inspection date, reviewer,
full/anonymous SHA256 values, saved-copy paths, exported-PDF hashes, each item
result, and screenshots for failures. The anonymous copy remains
`NOT_WORD_DOCUMENT_INSPECTOR_VERIFIED` until W24 is completed by the user.
