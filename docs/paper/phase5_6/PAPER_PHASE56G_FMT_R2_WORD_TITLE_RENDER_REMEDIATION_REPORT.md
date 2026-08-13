# Paper Phase 5.6G-FMT-R2 — Microsoft Word Chinese Title Render Remediation Report

## 1. Trigger

Microsoft Word Desktop human QA found `WORD_TITLE_VERTICAL_CLIPPING_REAL_DEFECT` in the supervisor-review candidate at commit `c32651950727afa0010bc0e119bfcb936feb370b`: the Chinese title was horizontally correct and remained one line, but the upper portions of its Chinese glyphs were visibly clipped. LibreOffice/PDF did not reproduce the defect.

This R2 task changes no title wording, font size, margins, scientific content, figures, tables, equations, or references.

## 2. Microsoft Word screenshot finding

The user-reported Word observation is authoritative for the trigger:

- title: `Jetson端工业缺陷检测的输入数据路径重构`;
- one line and horizontally fitted;
- visible clipping at the upper glyph boundary;
- classification: `WORD_TITLE_VERTICAL_CLIPPING_REAL_DEFECT`.

No screenshot file was added to the repository. The defect is explained by the generated OOXML cascade below.

## 3. Official-title OOXML authority

Authority: the controlled DOCX conversion of `《合肥工业大学学报（自然科学版）》排版格式及相关要求.doc`.

The official title paragraph has:

- paragraph style `Normal`;
- no `w:spacing`, `w:line`, or `w:lineRule` on the paragraph;
- no line-spacing constraint in official `Normal` or `docDefaults`;
- `w:jc w:val="center"`;
- `w:snapToGrid w:val="false"`;
- title runs at `w:sz w:val="44"` (22 pt), bold, with SimSun/宋体 font naming;
- no `w:position` or `w:vertAlign`.

Therefore the official vertical-spacing semantics are automatic line height, not an exact point-height line box, with the title opted out of the document grid.

## 4. Old generated-title OOXML

The R1 generated title had:

- `HFUTTitleCN` based on `Normal`;
- title font size `44` half-points = 22 pt = 440 twips;
- title style `w:spacing` containing only `before=0` and `after=0`;
- `Normal` containing `w:line="320" w:lineRule="exact"`;
- no direct title-paragraph spacing override;
- no title `snapToGrid=false` override;
- no run position or vertical-alignment override.

The effective Word title line box was consequently inherited as exact 320 twips (16 pt), smaller than the 440-twip 22 pt title font.

## 5. Root cause

`TITLE_CLIPPING_ROOT_CAUSE_STYLE_INHERITANCE`

The source was `scripts/paper/build_hfut_reference_docx.py`: `HFUTTitleCN` inherited the body style's exact line-height attributes through `Normal`. Pandoc emitted only the `HFUTTitleCN` paragraph style, and neither manuscript postprocessor changed title spacing. This was not a direct paragraph override.

## 6. Corrected generation property

Only `HFUTTitleCN` now adds:

```xml
<w:snapToGrid w:val="false"/>
<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>
```

For `lineRule="auto"`, `line="240"` is the OOXML single-line multiplier, not a 12 pt exact line height. Word computes the physical line box from the 22 pt SimSun glyph metrics. This explicitly prevents inheritance of `Normal`'s exact 320-twip body line box while matching the official automatic-spacing semantics.

No visual fudge factor, font reduction, condensation, margin change, run positioning, or direct final-DOCX patch was used. The English title style was not changed.

## 7. Template/source files changed

- `scripts/paper/build_hfut_reference_docx.py`: title auto-spacing/grid source of truth.
- `docs/paper/phase2_5/PAPER_PHASE2_5_REFERENCE_STYLE_MAP_v1.0.csv`: regenerated title contract/evidence.
- `docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx`: deterministically regenerated reference.
- `scripts/paper/validate_journal_format_docx.py`: inherited/direct line-box resolution and clipping-risk validation.
- `docs/paper/phase5_6/phase56_final_freeze_manifest.json`: R2 hashes, verdict, and Word gate.
- This report.

Reference-package comparison against R1 found only `word/styles.xml` changed; within that part, the only changed style ID was `HFUTTitleCN`.

## 8. Final Full/Anonymous artifacts

| Artifact | SHA-256 | Pages |
|---|---|---:|
| Full DOCX | `7595ac410d8f554db18c97a2699b04b4838bbc7dd8c2aec1787dd7905e1f256d` | 10 |
| Full LibreOffice PDF | `997956417b1ddce24e483cc827bd4fe237355ec7001c04ce31ad86805b76fd40` | 10 |
| Anonymous DOCX | `7ed7c671968514b6b983668b73d485c5ba4b28d816c41164077ba8c744ae9bc2` | 10 |
| Anonymous LibreOffice PDF | `49277fc2fd39fef12f150e9c267b6b8415594e3faaccabc485312eb0ec32a6b5` | 10 |

Reference DOCX SHA-256: `31b65361f50262240630d1453637218e2455b150dadc653edfa8e535439c55c0`.

## 9. Automated title-line-box validator

Both final variants report:

```text
CHINESE_TITLE_FONT=SimSun
CHINESE_TITLE_SIZE=22_pt
CHINESE_TITLE_BOLD=YES
CHINESE_TITLE_ALIGNMENT=CENTER
CHINESE_TITLE_RENDERED_LINES=1
TITLE_LINE_RULE=auto
TITLE_LINE_HEIGHT=240_AUTO_SINGLE_LINE_MULTIPLIER
TITLE_LINE_BOX_SMALLER_THAN_FONT=NO
TITLE_VERTICAL_CLIPPING_RISK=NO
ENGLISH_TITLE_STYLE_MUTATION=NO
```

The validator resolves paragraph direct formatting, the paragraph-style based-on chain, document defaults, character/run styles, and direct run sizing. Any effective `exact` line box smaller than the maximum effective title run size fails validation.

A regression probe using the R1 reference style resolved `exact / 320 twips` against the effective 440-twip title font and emitted `TITLE_VERTICAL_CLIPPING_RISK`; the probe passed by rejecting that old contract.

## 10. Page-1 mechanical QA

LibreOffice 7.3.7.2 mechanical rendering confirms:

- Chinese title text unchanged, one line, 14.686 cm wide within 16.401 cm;
- 22 pt bold Songti/SimSun source style remains centered;
- no visible clipping, overlap, or abnormal title/author separation;
- Chinese authors, affiliation, corresponding author, English front matter, abstracts, and keywords are unchanged;
- the Full abstract start moved naturally from PDF y=130.751 pt to y=146.551 pt because the corrected automatic title line box is taller;
- Anonymous identity removal remains intact;
- both variants remain 10 A4 pages.

The expected first-page vertical change causes ordinary reflow through pages 1–4. Pages 5–10 are raster-identical to the fully inspected R1 mechanical proof in both variants. R2 pages 1–4 were inspected in both variants; no clipping, overlap, broken figure/table, unexpected heading wrap, or pagination defect was found.

LibreOffice PASS cannot close a Word-only defect; it establishes only mechanical non-regression.

## 11. Scientific and format non-regression

- Manuscript sections, bibliography, table scientific sources, figures, and visual-production assets are unchanged from `c326519`.
- Contributions/figures/tables/display equations remain `2 / 4 / 4 / 5`.
- All frozen FPS, latency, tail-latency, payload, and task-metric values remain unchanged.
- Figure SVG/PDF/PNG hashes are unchanged; no figure or table source was touched.
- Full and Anonymous build, citation, reference, heading, table, anonymity, scientific-parity, and Phase 5.6 integration validators pass.
- Footer distance, body formatting, abstract layout, headings, tables, equations, page fields, and column transitions remain unchanged.

## 12. Open submission exceptions and Word gate

Unrelated submission-production exceptions remain:

- `SUBMISSION_EXCEPTION_MATHTYPE = OPEN`.
- `SUBMISSION_EXCEPTION_VISIO_ORIGIN = OPEN`.

Final R2 status:

```text
PHASE56_WORD_TITLE_RENDER_FIX_CANDIDATE
WORD_DESKTOP_RECHECK_REQUIRED = YES
```

The user must reopen the regenerated Full DOCX in Microsoft Word Desktop and verify that the Chinese title glyph tops are no longer clipped. The manuscript is not declared frozen by this automated task.
