# Phase 7.1R2 reference-heading authority reconciliation

## Verdict

`R1_REFERENCE_HEADING_AUTHORITY_CONCLUSION = WRONG`

The statement that the supplied HFUT sources contained no actual manuscript
reference-heading specimen is superseded. The missed source is the formatting
document itself, not the separate reference-example document.

## Four-source search

The raw/converted records for all four supplied DOC files were searched for
`参考文献`, `参 考 文 献`, bracketed variants, full-width brackets, and Chinese
bracket variants.

| Source ID | Source file | Result |
| --- | --- | --- |
| HFUT_FMT_DOC | 《合肥工业大学学报（自然科学版）》排版格式及相关要求.doc | `P097 [参 考 文 献]` found |
| HFUT_FIG_DOC | 《合肥工业大学学报（自然科学版）》插图要求及示例.doc | no manuscript-tail reference-heading specimen |
| HFUT_TABLE_DOC | 《合肥工业大学学报（自然科学版）》表格要求及示例.doc | no manuscript-tail reference-heading specimen |
| HFUT_REF_DOC | 《合肥工业大学学报（自然科学版）》参考文献要求及示例.doc | body-format instructions/examples; no bracketed manuscript-tail heading |

## Located source object

The authoritative object is `HFUT_FMT_DOC P097` (raw OOXML body paragraph
index 113 in the LibreOffice conversion record). Its immediately preceding
nonempty paragraph is the final manuscript-style prose conclusion (`P096`),
and the next paragraph (`P098`) is red instructional reference text. This
context classifies it as:

`MANUSCRIPT_SPECIMEN_REFERENCE_HEADING`

It is not the format document's own heading and not a red instructional
annotation.

| Field | Raw-source record |
| --- | --- |
| Literal | `[参 考 文 献]` |
| Paragraph alignment | `center` |
| Left/right indent | absent (no positive indent) |
| Line/space before/after | no direct value |
| Paragraph style | `Normal` |
| Paragraph run count | 3 black runs |
| Run 1 | `[`; SimHei/黑体 direct font; no direct bold/size |
| Run 2 | `参 考 文 献`; SimHei/黑体; bold; 10.5 pt effective/source `szCs=21` |
| Run 3 | `]`; SimHei/黑体; bold; 10.5 pt/source `szCs=21` |
| Black/red separation | P097 is black; P098 begins the red instruction/example sequence |

The output contract deliberately materializes the source's literal three-run
structure. The opening bracket has explicit non-bold output so that the
project's former bold `HFUTReferenceHeading` style cannot silently override
the observed source distinction. The heading remains a separate paragraph
immediately before the first `Bibliography` entry.

## R1 reconciliation

R1's reference-body findings remain unchanged: six-size (7.5 pt), Songti /
Times New Roman intent, exact 14 pt spacing, left alignment, 22 rendered
entries, and the project-stable 360-twip hanging-indent implementation.

R1 missed P097 because the reference-heading search and semantic-role review
were concentrated on `HFUT_REF_DOC`; the black specimen in `HFUT_FMT_DOC` was
not classified as the manuscript-tail object that its surrounding conclusion
and following red instructions demonstrate. This is a source-role
classification failure, not new bibliographic evidence.
