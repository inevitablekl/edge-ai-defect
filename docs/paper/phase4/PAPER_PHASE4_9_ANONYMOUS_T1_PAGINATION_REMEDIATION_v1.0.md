# Paper Phase 4.9 Anonymous Table 1 Pagination Remediation Report

## 1. Verdict

`PHASE_4_9_ANONYMOUS_T1_RETEST_READY`

The Anonymous-only pagination remediation is mechanically and visually ready
for the final Microsoft Word retest.

## 2. Trigger

`P4.9-T1-03` — `ANONYMOUS_TABLE1_ORPHAN_FRAGMENT_PAGE_SPLIT`

The real Microsoft Word retest placed the Table 1 caption, repeated/initial
header, and only the first data row at the end of one page. The next page began
with the correctly repeated header and the remaining rows. This was a
publication-pagination defect, not table corruption or a repeat-header defect.

## 3. Diagnosis

The Anonymous T1 caption had neither `w:pageBreakBefore` nor another explicit
page/column transition. Removing Full-only identity material changes the
available Anonymous page flow, so Word used the small remaining area for the
caption, header, and first body row, then continued the valid multi-page table
on the next page.

The table has 18 total rows: one header plus 17 data rows. Its initial header
correctly retains `w:tblHeader`; individual rows do not use `w:cantSplit`.
Existing LibreOffice evidence confirmed that the entire accepted table fits in
one column when it starts sufficiently high on the following page.

## 4. Remediation

The publication-table postprocessor now accepts the narrow command-line flag
`--anonymous-t1-page-break`. When present, it adds
`w:pageBreakBefore` to the caption whose exact text is
`表1　平台、模型、数据集和统一运行协议`.

Only the Anonymous build passes this flag. The Full build does not. The Full
validator asserts that its T1 caption has no page break, while the Anonymous
validator asserts that its T1 caption has the selected page break. Both also
retain the existing caption-count, table-content, row-count, border, and
paragraph-indent checks.

No table text, width, font, line spacing, border, wrapped-cell indentation,
repeat-header setting, or Table 2 behavior changed.

## 5. Full Regression

PASS.

- Full `word/document.xml` SHA256 before and after this remediation:
  `5f3fb86a8f1f324e761307778285ff2287d098a53ce93d45568667ed7ca3f76b`.
- Full T1 caption has no `w:pageBreakBefore`.
- Full remains 9 A4 pages.
- Full F1 remains on page 4 with section 1.3 below it.
- Full T1 remains complete and visually unchanged on page 6.
- Full structure, citations, references, fields, figures, T1 borders, and T1
  continuation indentation: PASS.

## 6. Anonymous Result

- Build: `docs/paper/manuscript/output/draft_anonymous.docx`
- SHA256:
  `ca577b1d7ada73e375f3d4771d1ad47a7ea9e47a8d4f130c31d94f3b8fc990b3`
- Page count: 9 A4 pages.
- T1 page: 6.
- Caption count: 1.
- Data-row count: 17.
- Table split status in LibreOffice render: not split.
- Page 6 order: caption, initial header, all 17 body rows, then the existing
  following paragraph and section 3.2 content.
- No duplicated title, unnecessary rendered repeated header, or blank page.
- Three-line borders and the `单次测量` continuation alignment remain PASS.

## 7. Anonymity / Parity

PASS.

- `ANONYMITY_SCAN_PASS`
- `PARITY_PASS`
- Full/Anonymous bibliography identity: PASS.
- Anonymous creator remains empty and `lastModifiedBy` remains absent.
- No comments, revisions, revision authors, package identity hits, or email
  material are present.

Scientific parity is content parity; the authorized pagination difference is
not a parity failure.

## 8. Scientific Freeze

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

No manuscript Markdown, figure, bibliography, CSL, table content, or scientific
claim changed.

## 9. Required Final Word Retest

Only Anonymous Table 1 pagination.

Confirm in Microsoft Word that the caption, header, and all 17 data rows remain
together without a one-row fragment or a new blank page.

## 10. Recommendation

`PHASE_4_9_ANONYMOUS_T1_RETEST_READY`
