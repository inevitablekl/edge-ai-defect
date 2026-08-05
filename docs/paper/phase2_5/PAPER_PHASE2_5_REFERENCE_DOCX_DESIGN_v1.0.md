# Paper Phase 2.5 Step 4 Reference DOCX Design v1.0

## 1. Scope and identity

This document defines the design of the Step 4 reference DOCX candidate. It is
not a journal template reconstruction and it does not define manuscript
prose. The candidate carries these document-property markers:

```text
DERIVED_REFERENCE_DOCX_CANDIDATE
NOT_OFFICIAL_JOURNAL_TEMPLATE
NOT_FINAL_SUBMISSION_FILE
PENDING_PANDOC_POC
PENDING_MICROSOFT_WORD_REVIEW
```

The canonical filename is
`hfut_journal_reference_v1.0.docx`. The canonical repository path is
`docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx`.

The external specimen is virtual content only. It is not a manuscript and is
not committed to the repository.

## 2. Base document strategy

Pandoc and `python-docx` were unavailable in the controlled environment.
LibreOffice 7.3.7.2 was available and was used only for headless rendering
validation. The build therefore uses a small, fixed OOXML baseline assembled
with the Python standard library. This avoids copying any converted DOCX and
fixes ZIP timestamps, package-part order, relationship IDs, and core-property
values.

The builder is `scripts/paper/build_hfut_reference_docx.py`. It creates the
canonical candidate, the external specimen, the external derivative-tree
directories, and the Style Map. It reads no personal identity data and does
not use the Step 3 converted DOCX as a source template.

## 3. Page and section design

The candidate uses the Step 3 page evidence as controlled OOXML values:

| Property | Candidate value |
|---|---:|
| Paper | A4 portrait |
| Page size | 11906 × 16838 twips; 21.0 × 29.7 cm |
| Top margin | 1361 twips; approximately 2.4 cm |
| Bottom margin | 1134 twips; approximately 2.0 cm |
| Left/right margins | 1304 twips; approximately 2.3 cm |
| Gutter | 0 |
| Default language | `zh-CN`; Latin runs `en-US` |
| Header | no formal journal header |
| Footer | PAGE field only |
| Candidate column gap | 425 twips; approximately 0.748 cm |

The default section is a one-column front-matter candidate. The intended body
layout is two columns. A reference DOCX cannot safely infer the semantic point
at which front matter ends and body text begins, so the canonical file does
not copy the source document's multiple section breaks. A later Pandoc build,
OOXML post-processing step, or Word review must create the semantic section
boundary and apply two columns to the body. This boundary is recorded in
custom document properties and is intentionally pending.

## 4. Semantic style system

The build creates stable ASCII style IDs for all required HFUT roles:

`HFUTTitleCN`, `HFUTTitleEN`, `HFUTAuthorsCN`, `HFUTAuthorsEN`,
`HFUTAffiliationCN`, `HFUTAffiliationEN`, `HFUTAbstractLabelCN`,
`HFUTAbstractBodyCN`, `HFUTAbstractLabelEN`, `HFUTAbstractBodyEN`,
`HFUTKeywordsLabelCN`, `HFUTKeywordsBodyCN`, `HFUTKeywordsLabelEN`,
`HFUTKeywordsBodyEN`, `HFUTClassification`, `HFUTBody`, `HFUTHeading1`,
`HFUTHeading2`, `HFUTHeading3`, `HFUTEquation`, `HFUTFigureCaption`,
`HFUTTableCaption`, `HFUTTableContent`, `HFUTReferenceHeading`,
`HFUTReferenceEntry`, `HFUTAuthorBiography`, `HFUTFunding`, and
`HFUTAcknowledgement`.

Pandoc-compatible styles are also present: `Normal`, `BodyText` (display name
`Body Text`), `Title`, `Subtitle`, `Author`, `Abstract`, `Heading1`/`Heading2`/
`Heading3` (display names `Heading 1`/`Heading 2`/`Heading 3`), `Caption`,
`Table`, and `Bibliography`. Their mappings to HFUT styles are recorded in
`PAPER_PHASE2_5_REFERENCE_STYLE_MAP_v1.0.csv`.

Confirmed and derived candidate settings are separated in the Style Map:

- body: Chinese Songti, Latin Times New Roman, 10.5 pt, justified;
- body line spacing: 16 pt exact candidate;
- body first-line indent: 200 twips candidate;
- level 1: Heiti, 14 pt candidate, left, keep-next;
- level 2: Heiti, 10.5 pt candidate, left, keep-next;
- level 3: Kaiti, 10.5 pt candidate, left, keep-next;
- figure/table captions: 7.5 pt Heiti, centered candidate;
- table content: 7.5 pt Songti/Times New Roman candidate;
- references: 7.5 pt Songti/Times New Roman, 14 pt exact candidate.

The implementation uses named paragraph styles as the default. Direct
formatting is reserved for cases that a later source paragraph may need to
distinguish inside one paragraph, such as a bilingual label or a variable.
The candidate itself does not use source-document direct formatting.

## 5. Heading and numbering design

The candidate numbering definitions contain:

```text
Level 1: 1, 2, 3, ...
Level 2: 1.1, 1.2, ...
Level 3: 1.1.1, 1.1.2, ...
Introduction candidate: 0
```

Three designs were considered:

| Option | Description | Risk |
|---|---|---|
| A | Use a separate introduction numbering definition displaying `0`; use a second multilevel definition whose level 1 starts at `1` | Requires Word/Pandoc update and restart testing |
| B | Generate all numbers as source text | Stable appearance but weak semantic editing and cross-reference behavior |
| C | Use one Word multilevel list and restart rules to make introduction `0` | Restart behavior is sensitive to Word list state and is not established by Step 3 |

Option A is the POC candidate. The styles do not copy the source document's
hand-typed `0`, `1.1`, or `1.1.1` text. The specimen exercises the numbering
definitions, but automatic numbering is not claimed to have passed Microsoft
Word update testing.

## 6. Formula boundary

`HFUTEquation` is a centered equation-paragraph style candidate. No MathType
object is created, embedded, or claimed. No equation number is positioned by
spaces. MathType object creation, variable typography, equation numbering,
right-side alignment, long-equation wrapping, and editability remain POC or
manual Word/MathType work.

## 7. Figure and table styles

`HFUTFigureCaption` and `HFUTTableCaption` are separate named styles even
though the current candidate values are the same. This prevents figure/table
captions from falling into `Normal` and keeps later semantic changes local.
Figure dimensions, DPI, object editability, Visio/Origin internals, and
bilingual caption policy are not invented by this candidate.

`HFUTThreeLineTable` is a named table style and the specimen contains one
controlled table. OOXML border sizes use eighths of a point:

- top: `sz=8` = 1 pt;
- secondary horizontal rule: `sz=4` = 0.5 pt;
- bottom: `sz=8` = 1 pt;
- inside vertical borders: `nil`;
- left/right cell margins: 108 twips = 5.4 pt;
- top/bottom cell margins: 0 twips.

Merged-cell behavior, continuation tables, unit placement, and Word rendering
remain `PENDING_POC` or `PENDING_WINDOWS_CHECK`.

## 8. Reference style

`HFUTReferenceEntry` and `Bibliography` use 7.5 pt Songti/Times New Roman and
14 pt exact line spacing. The selected hanging-indent candidate is 360 twips
(18 pt), with a matching left indent. Step 3 observed inconsistent source
values from 227 to 396 twips; 360 twips is selected because it provides a
single controlled candidate with enough space for `[1]`, `[12]`, and `[123]`
while remaining inside the observed range. This is a POC choice, not a claim
that the journal universally specifies 360 twips.

Citation order, CSL rendering, GB/T 7714—2025 edge cases, author truncation,
DOI rules, and Chinese-reference English counterparts remain outside this
template-only step.

## 9. Page number and document properties

The footer contains a `PAGE` field, not a fixed page-number paragraph. Word is
configured to update fields on open. The canonical file contains no formal
received/revised date, funding, acknowledgement, biography, contact, or real
author data.

## 10. Determinism and inspection

The build writes package entries in sorted order with fixed DOS timestamps and
fixed XML/property values. The inspection script checks ZIP integrity, OOXML
parts, page geometry, margins, styles, fonts/sizes, heading candidates,
caption/bibliography mappings, numbering, PAGE, three-line borders, identity
markers, and forbidden source/real-content markers.

Byte-level determinism is a tested property of the current builder: two
consecutive builds from the same inputs produced the same SHA256. This claim
applies to the current standard-library package builder and not to later Word
or LibreOffice save operations.
