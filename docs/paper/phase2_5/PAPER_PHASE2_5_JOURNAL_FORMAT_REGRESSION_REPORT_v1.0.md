# Paper Phase 2.5 Journal-Format Regression Audit Report v1.0

## 1. Audit verdict

`FORMAT_REMEDIATION_REQUIRED`

The canonical reference DOCX and both v6 packages have the expected SHA256
values, valid ZIP packages, zero frozen official OpenXmlValidator errors, and
matching Full/Anonymous non-identity formatting. Those facts do not establish
journal-format acceptance or Microsoft Word acceptance.

Phase 2.5 cannot close yet because:

1. both v6 reference headings retain an unauthorized direct `numPr` and render
   as `2 参考文献`;
2. the explicit first-page-footer author-biography requirement was not tested;
3. the validated equation and table implementation contracts are not
   synchronized with their governance files;
4. the Design field-update statement is stale; and
5. untouched v6 Microsoft Word first-open and save/reopen acceptance has not
   been performed.

No remediation was made in this audit. Phase 3 prose remains unauthorized.

## 2. Source authority

Authority was kept separate throughout the matrix:

1. target-journal guide text and attachment-candidate text;
2. target-journal source style evidence from controlled conversion;
3. validated Microsoft Word/manual evidence;
4. project-derived reference/POC candidates;
5. published-journal visual examples only.

The principal text authority is
`PAPER_PHASE2_5_FORMAT_RULE_CROSSWALK_v1.0.csv`. Page, paragraph, and object
evidence is subordinate to textually explicit requirements. Published-paper
appearance was never promoted to a submission requirement.

## 3. Audit method

The standard-library script
`scripts/paper/audit_hfut_format_regression.py` performs a read-only audit. It:

- verifies the canonical and v6 hashes before analysis;
- reads the 42-row Style Map separately from actual OOXML values;
- parses page, margin, section, column, header/footer, PAGE, settings, HFUT
  styles, paragraph style use, direct numbering, formulas, drawings, tables,
  core/custom properties, and package parts;
- reads the frozen official OpenXmlValidator JSON results;
- compares exact non-identity package-part hashes and normalized common
  paragraph structure between Full and Anonymous;
- writes this audit's 37-row regression matrix and a detailed external JSON;
  and
- returns nonzero for an unauthorized or unresolved Phase 2.5 blocker.

Automatic, visual, schema, source-authority, and Windows results occupy
separate matrix columns. Pending checks are not defaulted to pass.

## 4. Word and schema acceptance

The official frozen `DocumentFormat.OpenXml` 3.5.1 validator results are:

| Package | Office 2019 errors | Status |
|---|---:|---|
| Canonical reference | 0 | schema pass |
| Full v6 | 0 | schema pass |
| Anonymous v6 | 0 | schema pass |

The custom reference and POC inspectors also pass. This proves neither
first-open acceptance nor visual correctness. v5 first-open failed in Word;
v6 was created to address the official schema findings but has not received a
fresh untouched-file Word test.

Status: `WINDOWS_FINAL_REQUIRED`.

## 5. Page and section

Both v6 files contain two sections with identical geometry:

| Property | Actual |
|---|---|
| Page | A4 portrait, `11906 × 16838` twips |
| Margins | top `1361`, right `1304`, bottom `1134`, left `1304` twips |
| Gutter | `0` |
| Front matter | one column, gap candidate `425` twips |
| Body | two columns, gap candidate `425` twips |
| Transition | `continuous` section break |
| Explicit `w:br type=page` | none |
| Page-number restart | none |

Page geometry is `PASS_STYLE_EVIDENCE_CONFIRMED`. The semantic one-to-two
column transition is `PASS_PROJECT_DERIVED_CANDIDATE`, not a textually
explicit journal requirement.

## 6. Front matter

The bilingual title, abstract, keyword, and classification roles are used in
both variants. Full uses the synthetic author and affiliation roles;
Anonymous omits them. The Chinese abstract styles carry the explicit 9-pt
Heiti/Songti and exact 14-pt spacing contract. English semantic equivalence,
real title length, keywords, and the real classification remain
`FINAL_CONTENT_PENDING`.

The Full POC inserts funding, author biography, and acknowledgement as ordinary
body paragraphs. Its footer contains PAGE only. Therefore the explicit
`HFUT-WEB-025` first-page-footer biography placement was not tested:
`POC_NOT_COVERED`. This finding does not assert that the funding or
acknowledgement must share the biography's footer location.

## 7. Body and headings

`HFUTBody` has Songti/Times New Roman at 10.5 pt. Its 200-twip first-line
indent and exact 16-pt spacing are confirmed project style evidence rather
than a textually explicit journal value.

The POC uses distinct introduction, level-1, level-2, and level-3 roles. The
numbering definitions and preview produce `0`, `1`, `1.1`, and `1.1.1`. The
heading fonts and sizes match the frozen text/style evidence, and all three
styles carry keep-next/keep-lines candidates. Final Word no-wrap, list edit,
restart, and pagination behavior still require Windows review.

## 8. Equations

The POC contains three OMML nodes, including two display equations. OMML is
not MathType, so the textually explicit MathType rule remains
`WINDOWS_FINAL_REQUIRED` for final publication equations.

The Style Map says:

```text
HFUTEquation: exact 16 pt; before 0; after 0
```

Both v6 packages actually use:

```text
lineRule=atLeast; line=480 twips; before=80 twips; after=80 twips
```

Word v3 manual evidence found no clipping or overlap and explicitly closed the
equation-layout issue without authorizing another style change. No frozen
journal text requires exact 16-pt equation-paragraph height. The v6 setting is
therefore `VALIDATED_PROJECT_DERIVED_CANDIDATE` plus `GOVERNANCE_DRIFT`.
It must be preserved; restoring the stale exact setting is not proposed.

The Style Map, Reference DOCX Design/Report, and Markdown-DOCX POC report need
a later focused description sync.

## 9. Figures

The single drawing extent is approximately `7.2 cm`, below the explicit
single-column `7.5 cm` maximum. The first callout precedes the image and the
semantic figure-caption style is used. The caption appearance remains a
style-evidence candidate.

The POC uses a PNG compatibility fallback. It does not test editable Origin
or Visio delivery, figure-internal font rules, or final publication assets.
Those items remain `POC_NOT_COVERED`/`WINDOWS_FINAL_REQUIRED`; PNG visibility
is not equivalent to native-object editability.

## 10. Tables

Both v6 tables have:

- direct `tblW=4400 dxa`;
- direct grid widths `1400/1400/1600` twips;
- direct top/bottom `sz=8` borders;
- direct header-cell bottom `sz=4` borders; and
- no vertical borders.

This satisfies the explicit 1/0.5/1-pt three-line contract for the POC. The
7.5-pt Songti/Times New Roman content style is present.

The current layout has no `tblLayout`. The canonical table style has
`basedOn=TableNormal`, but Pandoc does not provide that parent in the final
style set, so both v6 table styles intentionally have no `basedOn`. The stable
v6 result depends on direct `tblW`, `gridCol`, and borders, not on inherited or
fixed layout. The Style Map and design narrative still describe earlier
assumptions and require governance reconciliation. Reintroducing inheritance
or fixed layout solely to match stale documentation is not proposed.

## 11. References

The reference-entry style correctly uses 7.5-pt Songti/Times New Roman, exact
14-pt spacing, and the documented 360-twip project hanging-indent candidate.
The synthetic citation order is sequential; real content and all special CSL
rules remain pending.

The `参考文献` paragraphs in both v6 files:

- use `HFUTReferenceHeading`;
- retain direct `numPr` with `ilvl=0`, `numId=1`;
- resolve visually as `2 参考文献`; and
- conflict with the Style Map's blank `numbering_level`.

No frozen journal source authorizes a numbered reference heading. This is
`REFERENCE_HEADING_NUMBERING_DRIFT` and a format regression, even if the
visual result appears acceptable. It is the direct DOCX-format remediation
blocker for both Phase 2.5 and Phase 3.

## 12. Full/Anonymous

The packages have identical member sets. Exact hashes match for every common
part except the expected identity-bearing parts:

```text
word/document.xml
docProps/core.xml
docProps/custom.xml
```

After removing synthetic identity/status paragraphs, normalized common
paragraph structure and formatting are equal. All non-identity package parts
match byte-for-byte. Anonymous has no Full-only semantic identity styles in
actual use. Final Microsoft Word Document Inspector remains required after
the final Word save.

## 13. Governance drift

The separate drift register contains four open items:

| Drift | Classification | Minimal direction |
|---|---|---|
| `GDR-001` | reference-heading numbering | remove only direct heading `numPr`, add an inspector prohibition, rebuild/retest |
| `GDR-002` | equation Style Map stale | retain safe v6 spacing and synchronize governance |
| `GDR-003` | Design field policy stale | state that `updateFields` is absent and refresh is manual |
| `GDR-004` | table inheritance/layout stale | document absent inheritance/fixed layout and direct table-property dependency |

For field policy, the Reference DOCX Report and actual canonical/v6 settings
agree: open-time field updating is disabled. Only the earlier Design statement
is stale, so this is `DESIGN_DOCUMENT_STALE`, not a DOCX defect.

## 14. POC-not-covered items

- author biography in the first-page footer;
- untouched v6 Microsoft Word first-open result;
- v6 save/close/reopen result;
- final Document Inspector result;
- MathType final equation objects;
- Visio/Origin editable final objects;
- dynamic equation/figure/table numbering and cross-references;
- final-content bilingual equivalence, classification, citation inventory,
  and GB/T/HFUT special-reference rules; and
- final pagination, heading no-wrap, table continuation, and native-asset
  behavior.

## 15. Phase 2.5 blockers

The audit script reports these blocking rows:

```text
JFR-008  first-page-footer biography POC gap
JFR-018  validated equation contract governance drift
JFR-024  table contract governance drift
JFR-026  unauthorized reference-heading numbering
JFR-033  v6 first-open not tested
JFR-034  v6 save/reopen not tested
JFR-036  stale Design field-policy statement
```

Only `JFR-026` is a confirmed v6 formatting regression that requires DOCX
generation remediation. The others require narrowly scoped governance sync or
manual/POC acceptance. The distinction is preserved in the matrix.

## 16. Phase 3 deferred checks

Real title length and bilingual meaning, abstracts, keywords, classification,
author/affiliation content, real funding applicability, figure/table content,
real citation order, at least eight real/read references, recent-literature
coverage, final units/symbols, and final layout remain content-dependent.

The first-page body-flow observation is not a Phase 3 content rule. In the
frozen v6 LibreOffice preview, front matter fills page 1 and body begins on
page 2. OOXML contains a continuous section conversion and no explicit page
break. Content length and keep/column behavior explain the candidate result;
no frozen textual source requires the body to start on page 1.

## 17. Proposed minimal remediation

Subject to Paper Project AI approval, the smallest coherent follow-up is:

1. remove direct `numPr` only when the paragraph is the semantic reference
   heading;
2. make the POC inspector fail if `HFUTReferenceHeading` has direct `numPr`;
3. retain the validated v6 equation spacing;
4. synchronize only the four registered governance contracts;
5. add a minimal first-page-footer biography POC without inventing identity;
6. rebuild Full/Anonymous candidates and rerun hash/format/schema regression;
7. perform untouched Microsoft Word first-open and save/reopen tests; and
8. run Document Inspector and record identity-property handling.

This proposal does not authorize changing the canonical reference DOCX,
Style Map, Design, reports, or POC scripts in this audit commit. It does not
authorize Phase 3 writing.

## 18. Next executor

`PAPER_PROJECT_AI`

Paper Project AI should decide whether the four governance updates and the
first-page-footer POC are grouped with, or sequenced around, the narrow
reference-heading remediation. The following execution must remain small,
reviewable, schema-validated, and Windows-retested.
