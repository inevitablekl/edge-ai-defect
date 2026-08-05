# Paper Phase 2.5 Word Repair Diagnosis v1.0

## 1. Diagnostic verdict

```text
ROOT_CAUSE_IDENTIFIED
GENERATOR_SIDE_OOXML_COMPATIBILITY_DEFECT
CANONICAL_REFERENCE_DOCX_NOT_MODIFIED
```

The primary unreadable-content cause is a combination of duplicate `styleId`
definitions and two schema-order violations introduced in the generated DOCX.
The external-field warning risk is separate: `w:updateFields=true` requested
automatic field refresh on open even though the only Word field is `PAGE`.

## 2. Package inventory

Both originals contain the same 19 package parts:

```text
[Content_Types].xml
_rels/.rels
docProps/app.xml
docProps/core.xml
docProps/custom.xml
word/_rels/document.xml.rels
word/_rels/footnotes.xml.rels
word/comments.xml
word/document.xml
word/fontTable.xml
word/footer1.xml
word/footnotes.xml
word/media/poc_figure_fallback.png
word/media/rId16.svg
word/numbering.xml
word/settings.xml
word/styles.xml
word/theme/theme1.xml
word/webSettings.xml
```

Both Word-repaired packages contain the same 18 parts:

```text
[Content_Types].xml
_rels/.rels
docProps/app.xml
docProps/core.xml
docProps/custom.xml
word/_rels/document.xml.rels
word/document.xml
word/endnotes.xml
word/fontTable.xml
word/footer1.xml
word/footer2.xml
word/footnotes.xml
word/media/image1.png
word/numbering.xml
word/settings.xml
word/styles.xml
word/theme/theme1.xml
word/webSettings.xml
```

Added by Word: `word/endnotes.xml`, `word/footer2.xml`, and
`word/media/image1.png`. Removed by Word:
`word/_rels/footnotes.xml.rels`, `word/comments.xml`, the fallback PNG under
its original name, and the SVG. The image bytes were preserved under
`image1.png`; this was a package rewrite, not figure deletion.

All common retained XML parts except `docProps/custom.xml` were normalized or
rewritten by Word. `docProps/custom.xml` is canonically unchanged.

## 3. XML element-count differential

Counts below are XML elements, not byte counts. The full and anonymous deltas
are identical except for `word/document.xml`.

| Part | Full original | Full repaired | Delta | Anonymous original | Anonymous repaired | Delta |
|---|---:|---:|---:|---:|---:|---:|
| `[Content_Types].xml` | 19 | 18 | -1 | 19 | 18 | -1 |
| `_rels/.rels` | 5 | 5 | 0 | 5 | 5 | 0 |
| `docProps/app.xml` | 9 | 17 | +8 | 9 | 17 | +8 |
| `docProps/core.xml` | 10 | 11 | +1 | 10 | 11 | +1 |
| `docProps/custom.xml` | 27 | 27 | 0 | 15 | 15 | 0 |
| `word/_rels/document.xml.rels` | 13 | 13 | 0 | 13 | 13 | 0 |
| `word/document.xml` | 910 | 1327 | +417 | 848 | 1245 | +397 |
| `word/fontTable.xml` | 16 | 45 | +29 | 16 | 45 | +29 |
| `word/footer1.xml` | 9 | 16 | +7 | 9 | 16 | +7 |
| `word/footnotes.xml` | 9 | 13 | +4 | 9 | 13 | +4 |
| `word/numbering.xml` | 128 | 156 | +28 | 128 | 156 | +28 |
| `word/settings.xml` | 21 | 58 | +37 | 21 | 58 | +37 |
| `word/styles.xml` | 926 | 1134 | +208 | 898 | 1106 | +208 |
| `word/theme/theme1.xml` | 41 | 227 | +186 | 41 | 227 | +186 |
| `word/webSettings.xml` | 3 | 2 | -1 | 3 | 2 | -1 |

Large positive deltas are normal Word serialization expansion and are not, by
themselves, defect evidence. The minimum repair-relevant structures are listed
below.

## 4. Styles diagnosis

### 4.1 Duplicate style IDs

The full original has 103 `w:style` nodes but only 77 distinct IDs; 26 HFUT
IDs are duplicated. The anonymous original has 96 nodes and the same 77
distinct IDs; 19 HFUT IDs are duplicated. The first definitions come from the
canonical reference and contain the intended `w:pPr`/`w:rPr`. Pandoc appends
second definitions with the same IDs, generally containing only `w:name`,
`w:basedOn`, and `w:qFormat`.

Word makes the IDs unique. For example:

```text
HFUTTitleCN (formatted canonical definition) remains HFUTTitleCN
HFUTTitleCN (Pandoc placeholder) becomes HFUTTitleCN0
the title paragraph pStyle becomes HFUTTitleCN0
```

The same pattern affects the bilingual titles, authors, affiliations,
abstracts, keywords, classification, body, captions, and headings as
applicable to each variant. The introduction collision is normalized
differently: the formatted definition becomes `HFUTIntroductionHeading`, while
the placeholder retains `HFUTIntroHeading` and remains the paragraph target.

### 4.2 Invalid inheritance

After duplicate removal, some definitions still refer to nonexistent styles:
`DefaultParagraphFont`, `TableNormal`, or Pandoc's `VerbatimChar`. There are no
`basedOn` cycles and no illegal style types. The remediation removes only
unresolvable `basedOn` nodes; it retains each style's own formatting.

### 4.3 First-page regression answers

- Word did not delete all custom styles.
- Word did not clear paragraph style references.
- Word did not literally change the affected paragraphs to `Normal`.
- Word renamed the duplicate placeholder styles and retargeted paragraphs to
  them. Those placeholders inherit a body-text/Normal cascade and contain no
  intended local title/author/abstract formatting.
- The regression therefore spans both `styles.xml` and `document.xml`.
- The trigger is the illegal duplicate style definition, not a defect in the
  paragraph text or direct formatting.

The original affected paragraphs have only `w:pStyle` in `w:pPr`; therefore
the wrong style target is sufficient to explain the visible degradation.

## 5. Document and schema-order diagnosis

The body has one nested continuous `sectPr` and one final body `sectPr`; the
final section is the last body child. Bookmark IDs and drawing `docPr` IDs are
unique. There is one valid final section and no page-number restart.

Two generated child sequences are invalid:

```text
continuous sectPr: type, footerReference, pgSz, pgMar, cols, docGrid
table tblPr:       tblStyle, tblW, tblLook, tblBorders
```

Word rewrites them as:

```text
continuous sectPr: footerReference, type, pgSz, pgMar, cols, docGrid
table tblPr:       tblStyle, tblW, tblInd, tblBorders, tblLook
```

The first order came from inserting `w:type` at index zero. The second came
from appending `w:tblBorders` after an existing `w:tblLook`. Paragraph `pPr`,
run properties, cell properties, and border-edge order show no additional
repair-relevant violation in the inspected structures.

## 6. Numbering, section, and field diagnosis

The originals contain three unique `abstractNumId` values and three unique
`numId` values, with valid references. Word renumbers the package definitions
but preserves heading levels and visible `0 / 1 / 1.1 / 1.1.1` behavior. No
duplicate numbering IDs or missing abstract numbering targets were found.

Field scanning across every Word XML part found only:

```text
word/footer1.xml: PAGE
```

No `INCLUDEPICTURE`, `INCLUDETEXT`, `LINK`, `DDE`, `DDEAUTO`, `RD`, `SEQ`, or
`REF` field is present. The original `word/settings.xml` nevertheless contains
`w:updateFields w:val="true"`; Word removes it in both repaired files. The
remediation likewise removes it, retaining the `PAGE` field for manual/F9
refresh without open-time automatic updating.

## 7. Relationship and image diagnosis

All original internal relationship targets exist and relationship IDs are
unique. The document has one permitted external HTTP hyperlink to
`https://example.invalid/toolchain-test`; this is a normal text hyperlink, not
an automatically updated field or linked object. No `file://`, local absolute
path, network share, linked image, or external embedded object exists.

The visible drawing already points to the embedded PNG. The SVG relationship
and SVG part are unused after postprocessing, and the separate footnotes
hyperlink relationship is also unused. There is no `mc:AlternateContent` and
no remaining `asvg:svgBlip` in the original final POC. Word removes both unused
paths and retains/raster-normalizes the PNG. The v2 remediation emits a single
internal PNG relationship and removes dangling explicit relationships.

## 8. Minimum root cause

The minimum structures that require generator repair are:

1. duplicate HFUT `styleId` definitions and unresolved `basedOn` references;
2. invalid `sectPr` and `tblPr` child order;
3. open-time `updateFields=true`;
4. unused SVG and footnote-hyperlink relationships.

The first two explain Word's unreadable-content repair. The third explains the
field-update risk. The fourth is package hygiene visible in Word's normalized
derivative. No evidence requires changing the canonical reference DOCX; its
SHA256 remains
`c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71`.
