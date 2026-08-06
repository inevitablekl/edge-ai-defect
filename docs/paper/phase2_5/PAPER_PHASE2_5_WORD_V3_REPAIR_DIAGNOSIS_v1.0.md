# Paper Phase 2.5 Word v3 Repair Diagnosis

## 1. Diagnostic verdict

```text
ROOT_CAUSE_FOUND
CANONICAL_REFERENCE_OOXML_DEFECT
GENERATOR_REMEDIATION_REQUIRED
```

The remaining v3 repair prompt is explained by two schema-invalid structures
in the canonical reference DOCX. The equation layout is not involved.

## 2. Minimum repair-relevant differential

Both original v3 packages contain four invalid numbering structures:

```xml
<w:lvl>
  ...
  <w:rPr><w:rPr>...</w:rPr></w:rPr>
</w:lvl>
```

`w:lvl/w:rPr` is already the run-properties container; a second direct
`w:rPr` child is illegal. Both Word-saved derivatives flatten all four cases
to one valid `w:rPr`. The same four malformed nodes are present in the
pre-remediation canonical reference and are emitted by
`build_hfut_reference_docx.py`, which wrapped the complete `rpr()` element a
second time.

The canonical three-line table style also emits this invalid property order:

```text
tblLayout, tblBorders, tblCellMar
```

WordprocessingML requires `tblBorders` before `tblLayout`. Word rewrites the
style as `tblBorders, tblCellMar`; v4 retains the intended fixed-layout feature
using the valid order `tblBorders, tblLayout, tblCellMar`.

These are the smallest concrete schema violations shared by Full and Anonymous
and rewritten by Word. v4 has zero nested numbering `w:rPr` nodes and zero
style-level `tblPr` order violations.

## 3. Package normalization that is not the root cause

Each original has 16 parts and its Word-saved derivative has 18. Word adds
`word/endnotes.xml`, `word/footer2.xml`, and `word/media/image1.png`, and removes
the old media name `word/media/poc_figure_fallback.png`. The PNG bytes are
identical before and after the rename (SHA256
`a7c91214a52a116e0e17da244e43574b0b6989c936656108aa962485fdba5fb6`).

Word also renumbers relationships and numbering IDs, expands application,
font, theme and settings metadata, adds compatibility namespaces and
`mc:Ignorable`, splits mixed-script runs, and duplicates the PAGE footer for
the second section. These changes are normal Word save serialization and are
not used alone as root-cause evidence.

The detailed normalized comparison is in
`PAPER_PHASE2_5_WORD_V3_REPAIR_DIFF_v1.0.csv`.

## 4. Content and feature preservation

For both variants, original and Word-saved `word/document.xml` retain the same
counts of paragraphs, tables, sections, drawings, hyperlinks, bookmarks and
OMML objects. Full retains 59 paragraphs; Anonymous retains 53. Both retain one
table, two sections, one drawing, one hyperlink, 11 bookmarks, three
`m:oMath`, and two `m:oMathPara`. Word splits text runs and normalizes the minus
glyph inside OMML, but the manual PDF evidence confirms the visible content and
layout remain basically normal.

The only field before save is `PAGE` in `footer1.xml`; after save it is `PAGE`
in `footer1.xml` and the duplicated `footer2.xml`. Neither package enables
`updateFields`, and no INCLUDE, LINK, DDE or local-path field exists.

## 5. Other checks

- No duplicate style, numbering, relationship, bookmark or drawing IDs exist
  in original v3.
- No dangling internal relationship or content-type override exists.
- No `AlternateContent`, linked image, embedded object or absolute local path
  exists.
- Both section structures remain A4, single-column then double-column, with
  425-twip column spacing and no page-number restart.
- Word's compatibility namespace expansion is serialization, not a requirement
  to copy all current Word-version namespaces into generated OOXML.

## 6. Canonical reference disposition

The canonical reference was repaired because the defect originates there. Its
pre-remediation SHA256 was
`c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71`;
the deterministic repaired SHA256 is
`98d96d4eafac104c0972bf4e90c2b97db89d8fb35f98f8570eb3ca2ef9024e1e`.
The reference inspector now rejects nested numbering run properties and
invalid three-line-table property order.

## 7. Phase boundary

v3 remains failed evidence. The diagnosis authorizes only v4 Windows retest;
it does not establish Microsoft Word acceptance and does not authorize Phase 3.
