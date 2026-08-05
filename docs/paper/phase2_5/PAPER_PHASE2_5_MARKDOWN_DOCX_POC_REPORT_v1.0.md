# Paper Phase 2.5 Step 6 Result

## 1. Verdict

`POC_PASS_WITH_LIMITATIONS`

The Markdown-to-DOCX path generated and structurally validated full and
anonymous two-page POC documents. Semantic styles, OMML formulas, sequential
numeric citations, heading numbering, continuous PAGE fields, a one-column to
two-column section transition, a visible synthetic figure, and a three-line
table all reached inspectable DOCX output.

The result is not a journal-compliance or submission acceptance claim. Dynamic
formula/figure/table numbering and cross-references were not implemented; the
figure requires a PNG display fallback; the CSL renders the synthetic standard
as `[Z]` rather than the journal attachment's `[S]`; and Microsoft Word,
Document Inspector, MathType, Visio, and Origin checks remain open.

## 2. Repository State

- Required branch and starting HEAD: `main` at
  `b7695789b151ddc8c20593e0ed06da9d32be2a77`.
- Starting worktree/index: clean; starting `git diff --check`: PASS.
- Phase 2 tag type: `tag`.
- Phase 2 peeled commit:
  `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`.
- Canonical reference DOCX SHA256 before and after the POC:
  `c3d78034b37c82d5cc2416fc85854a8a3960ad8999db1c56de9661adcb1d2d71`.
- No reset, restore, checkout, stash, clean, merge, rebase, push, tag change,
  package installation, or Phase 0/1/2 modification was performed.

## 3. Environment

| Tool | Observed version | Role |
|---|---|---|
| Pandoc | 3.10.1, Lua 5.4 | Markdown, citeproc, OMML and DOCX generation |
| Python | 3.10.12 | Standard-library deterministic OOXML processing and inspection |
| LibreOffice | 7.3.7.2 | SVG-to-PNG fallback generation and non-authoritative PDF preview |
| curl | 7.81.0 | Official Zotero CSL retrieval |
| unzip | Info-ZIP 6.00 | DOCX ZIP integrity check |
| pdfinfo | 22.02.0 | Preview page and A4 check |
| file | 5.41 | Output type check |

MathType, Visio, and Origin returned `TOOL_NOT_AVAILABLE`. No dependency was
installed.

## 4. CSL Candidate

Classification:

```text
OFFICIAL_ZOTERO_STYLE_REPOSITORY_CANDIDATE
POC_ONLY
NOT_YET_VALIDATED_AGAINST_HFUT_SPECIAL_RULES
```

| Field | Result |
|---|---|
| Download/final URL | `https://www.zotero.org/styles/china-national-standard-gb-t-7714-2025-numeric` |
| HTTP status | `200` |
| Download time | `2026-08-06T01:00:40+08:00` |
| Size | 17,228 bytes |
| SHA256 | `4df240a008123cb070dfd5224f45514f868e1fb27fb2dc678edc6b01fd314900` |
| Title | `China National Standard GB/T 7714-2025 (numeric, 中文)` |
| ID | `http://www.zotero.org/styles/china-national-standard-gb-t-7714-2025-numeric` |
| Updated | `2026-05-10T01:39:45+00:00` |
| Citation format | `numeric` |
| CSL version | `1.0` |
| Rights/license | CC BY-SA 3.0 text and license URL present |
| XML/title/numeric checks | PASS |
| Pandoc load | PASS in both complete builds |

The downloaded CSL bytes were not changed and remain outside Git. The source
manifest is the only CSL-derived repository record. Rendering exposed one
HFUT-specific gap: the synthetic `@standard` entry is output with `[Z]` rather
than the attachment's required `[S]`. The candidate therefore is not accepted
as HFUT-special-rule compliant.

## 5. POC Inputs

External derivative root:

```text
/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1
```

The external inputs are `source/poc_article.md`, `source/poc_full.yaml`,
`source/poc_anonymous.yaml`, `source/poc_references.bib`,
`figures/poc_figure.svg`, and the downloaded CSL. All contain or inherit the
required POC classification. The bibliography contains five synthetic types:
Chinese journal, English journal, book, standard, and web resource. Every
title contains `TOOLCHAIN TEST`; no real DOI, paper title, literature source,
author identity, funding record, or experiment value is used.

## 6. Build Commands

Both builds used the required Pandoc command. The only profile-specific paths
are shown explicitly below:

```text
/home/orin/.local/bin/pandoc --standalone --from=markdown --to=docx \
  --reference-doc=/home/orin/edge-ai/edge-ai-defect/docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx \
  --citeproc \
  --bibliography=/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1/source/poc_references.bib \
  --csl=/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1/csl/china-national-standard-gb-t-7714-2025-numeric.csl \
  --resource-path=/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1/source:/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1/figures \
  --metadata-file=.../source/poc_full.yaml \
  --lua-filter=/home/orin/edge-ai/edge-ai-defect/scripts/paper/phase2_5_poc_styles.lua \
  --output=.../temporary/poc_full_raw.docx \
  .../source/poc_article.md

/home/orin/.local/bin/pandoc --standalone --from=markdown --to=docx \
  --reference-doc=/home/orin/edge-ai/edge-ai-defect/docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx \
  --citeproc \
  --bibliography=.../source/poc_references.bib \
  --csl=.../csl/china-national-standard-gb-t-7714-2025-numeric.csl \
  --resource-path=.../source:.../figures \
  --metadata-file=.../source/poc_anonymous.yaml \
  --lua-filter=/home/orin/edge-ai/edge-ai-defect/scripts/paper/phase2_5_poc_styles.lua \
  --output=.../temporary/poc_anonymous_raw.docx \
  .../source/poc_article.md
```

The external `pandoc_full_command.log` and `pandoc_anonymous_command.log`
contain fully expanded commands, timestamps, nanosecond durations, return code
0, and stdout/stderr paths. Pandoc warned that `rsvg-convert` was unavailable
and that three zh-CN translation terms were absent; neither warning left an
unresolved source marker. The documented PNG fallback addresses display of the
test SVG.

## 7. Full DOCX

- Path: external `output/poc_full.docx`.
- Size: 26,809 bytes.
- SHA256:
  `da0ded8249f8fc248b81a5a436417d4dfffe453667bcd5b0d57d86e0b8642731`.
- `file`: Microsoft OOXML.
- `unzip -t`: PASS.
- OOXML inspector: PASS.
- Contains only the obvious synthetic full-copy fields `POC测试作者`,
  `POC测试单位`, `poc@example.invalid`, and marked synthetic funding,
  biography, and acknowledgement fields.

## 8. Anonymous DOCX

- Path: external `output/poc_anonymous.docx`.
- Size: 26,394 bytes.
- SHA256:
  `3f9799288a0953ab666c630a7c8372e45eb75dd7236cf8190069fa36591e12f2`.
- `file`: Microsoft OOXML.
- `unzip -t`: PASS.
- OOXML inspector: PASS.
- Status: `ANONYMIZED_POC_CANDIDATE` and
  `NOT_WORD_DOCUMENT_INSPECTOR_VERIFIED`.

## 9. Style Mapping

Paragraph-level usage was found in `word/document.xml`, not merely in
`styles.xml`. The full copy uses every requested semantic role:

```text
HFUTTitleCN, HFUTTitleEN,
HFUTAuthorsCN, HFUTAuthorsEN,
HFUTAffiliationCN, HFUTAffiliationEN,
HFUTAbstractLabelCN, HFUTAbstractBodyCN,
HFUTAbstractLabelEN, HFUTAbstractBodyEN,
HFUTKeywordsLabelCN, HFUTKeywordsBodyCN,
HFUTKeywordsLabelEN, HFUTKeywordsBodyEN,
HFUTClassification, HFUTBody,
HFUTHeading1, HFUTHeading2, HFUTHeading3,
HFUTEquation, HFUTFigureCaption, HFUTTableCaption,
HFUTReferenceHeading, HFUTReferenceEntry
```

`HFUTIntroHeading` implements the separate introduction definition.
`HFUTTableContent` is used in all 12 cells. The full copy also uses
`HFUTFunding`, `HFUTAuthorBiography`, and `HFUTAcknowledgement`. The anonymous
copy correctly omits identity-specific styles while using every applicable
common style.

## 10. Heading and Numbering

Conclusion: `NUMBERING_POC_PASS_CANDIDATE`.

- LibreOffice visual text: `0`, `1`, `1.1`, `1.1.1`.
- Each heading paragraph contains an explicit `w:numPr`.
- Introduction: `ilvl=0`, `numId=2`, mapped to `abstractNumId=1`, text `0`.
- Body levels: `numId=1`, mapped to `abstractNumId=0`, formats `%1`, `%1.%2`,
  `%1.%2.%3`.
- The generated visual text does not contain hand-typed heading numbers.
- The Lua filter maps heading semantics; deterministic post-processing adds the
  explicit paragraph numbering relationship.
- LibreOffice demonstrated the intended restart candidate. Microsoft Word
  Ctrl+A/F9 and edit/restart behavior still require Step 7 confirmation.

## 11. Formula Results

- Inline formula: one OMML `m:oMath` representation of `\bar{t}`.
- Display formulas: two `m:oMathPara` nodes; three `m:oMath` nodes total.
- Fractions, summation, subscripts, multiplication, and percent constructs are
  present in OMML and visible in the LibreOffice preview.
- Formula representation is `PANDOC_NATIVE`; it is not an image.
- Formula paragraph style is `HFUTEquation` after deterministic mapping.
- Formula number: `STATIC_TEXT_ONLY`.
- Formula cross-reference: `STATIC_TEXT_ONLY / POSTPROCESS_CANDIDATE`.
- Dynamic Word formula numbering/cross-reference:
  `WORD_FIELD_POSTPROCESS_FUTURE` or `WORD_MANUAL`.
- MathType status: `WORD_MANUAL_REQUIRED`; OMML is not claimed to satisfy the
  journal's MathType requirement. Unit and upright/italic rules also remain a
  Word/MathType manual check.

## 12. Figure Results

- Source: deterministic `poc_figure.svg`, containing three synthetic groups,
  `Variant`, `Synthetic Value / a.u.`, and
  `SYNTHETIC TOOLCHAIN TEST DATA`.
- Requested width: 7.2 cm; OOXML extent `cx=2591999` EMU, below the 7.5 cm
  single-column limit.
- Package media: `word/media/rId16.svg` and
  `word/media/poc_figure_fallback.png`.
- Pandoc preserved the SVG but could not create its raster fallback because
  `rsvg-convert` is unavailable. LibreOffice generated a deterministic PNG;
  post-processing uses it as the visible relationship and retains the SVG
  package copy. Classification:
  `PNG_FALLBACK_WITH_SVG_PACKAGE_COPY / SUPPORTED_WITH_POSTPROCESS`.
- The LibreOffice PDF visibly renders all three bars and labels.
- Caption style: `HFUTFigureCaption`.
- First callout precedes the figure.
- Figure number and cross-reference: `STATIC_TEXT_ONLY`.
- No Origin, Visio, editable publication object, or final-publication claim is
  made.

## 13. Table Results

- Source: three columns, one header row, and three synthetic data rows.
- All values `1.20`, `2.345`, `3.0` and bilingual notes are present in OOXML.
- Pandoc raw output used compatibility style `Table` and no direct borders:
  `POSTPROCESS_REQUIRED`.
- Final table uses `HFUTThreeLineTable`; all cell paragraphs use
  `HFUTTableContent`.
- Direct borders: top 1 pt (`sz=8`), header bottom 0.5 pt (`sz=4`), bottom
  1 pt (`sz=8`), no internal vertical rule, no internal horizontal body rule.
- Width is constrained to 4,400 twips and visibly fits one body column.
- Caption style: `HFUTTableCaption`; first callout precedes the table.
- Table number and cross-reference: `STATIC_TEXT_ONLY`.
- Conclusion: `SUPPORTED_WITH_POSTPROCESS`; final Word border rendering remains
  a manual check.

## 14. Citation and Bibliography Results

Citation keys were used in Markdown; no manual bibliography numbering was
maintained. Citeproc produced first-occurrence numeric order `[1]`, `[2,3]`,
`[4]`, `[5]`. The document contains no unresolved `@POC_*` key. Five
`HFUTReferenceEntry` paragraphs appear after an `HFUTReferenceHeading`.

The Chinese/English journals use `[J]`, the book uses `[M]`, and the web
resource uses `[EB/OL]`. The synthetic standard renders `[Z]`, not `[S]`.
Accordingly sequential citation is `SUPPORTED`, while complete HFUT reference
formatting is `WORD_MANUAL_REQUIRED` pending a validated CSL remediation or
journal-specific bibliography workflow. The official CSL download was not
edited.

## 15. Page and Column Results

Conclusion: `SECTION_POSTPROCESS_PASS_CANDIDATE`.

- Section count: 2.
- Section 1: one column, 425-twip spacing candidate.
- Section 2: two columns, 425-twip spacing candidate, about 0.748 cm.
- Boundary: one continuous section break at the removed semantic marker.
- Both sections retain A4 `11906 × 16838` twips and margins
  `1361/1304/1134/1304` twips (top/right/bottom/left).
- No `w:pgNumType` restart occurs.
- PAGE fields display continuously as 1 and 2 in the LibreOffice preview.
- No blank page is present.
- The 7.2 cm figure and 4,400-twip table fit the left body column; body content
  then flows to the right column.

## 16. Anonymization Results

The anonymous package was scanned across `word/document.xml`, header/footer
parts, empty comments, footnotes/endnotes if present, core/custom properties,
relationships, embedded files, package member names, output name, inspection
JSON, and anonymous build logs. No occurrence of the full-copy author, unit,
email, funding, biography, or acknowledgement test strings was found.

There are zero comment nodes, zero tracked-change nodes, and zero embedded
files. Generic core properties identify only the POC and variant. An external
relationship to `example.invalid` belongs to the synthetic web reference and
contains no identity. This is `ANONYMIZED_POC_CANDIDATE`, not a claim that
Microsoft Word Document Inspector has passed.

## 17. Capability Matrix

| 功能 | Markdown表达 | Pandoc生成 | OOXML检查 | 后处理 | 需Word确认 | 结论 |
|---|---|---|---|---|---|---|
| 中英文题名 | custom-style Div | DOCX段落 | 两种title style实际使用 | 无 | 字体/换行 | SUPPORTED |
| 摘要关键词 | 双语语义段落 | DOCX段落 | 8种label/body style实际使用 | 无 | 最终视觉 | SUPPORTED |
| 标题样式 | 三级Header | Lua语义映射 | HFUTHeading1/2/3实际使用 | 编号属性修复 | 编辑行为 | SUPPORTED_WITH_POSTPROCESS |
| 多级编号 | 无手写编号 | 保留层级语义 | numPr/numId/abstractNum通过 | Option A显式映射 | Ctrl+A/F9及重启 | SUPPORTED_WITH_WORD_REFRESH |
| 行内公式 | LaTeX `$...$` | OMML | oMath存在、非图片 | 无 | Word可编辑性 | SUPPORTED |
| 独立公式 | LaTeX `$$...$$` | OMML | 2个oMathPara | 公式段落样式 | Word可编辑性 | SUPPORTED_WITH_POSTPROCESS |
| 公式编号 | 静态候选文本 | 普通文本 | 无SEQ域 | 未实现 | 动态编号 | WORD_MANUAL_REQUIRED |
| 公式交叉引用 | 静态“式（1）” | 普通文本 | 无REF域 | 未来候选 | 动态引用 | WORD_MANUAL_REQUIRED |
| 图片嵌入 | SVG路径 | SVG-only drawing并告警 | SVG和PNG均在media | PNG显示回退 | Word显示 | SUPPORTED_WITH_POSTPROCESS |
| 图编号 | 静态“图1” | 普通文本 | 无SEQ域 | 未实现 | 动态编号 | WORD_MANUAL_REQUIRED |
| 图交叉引用 | 静态首次引用 | 普通文本 | 无REF域 | 未来候选 | 动态引用 | WORD_MANUAL_REQUIRED |
| 三线表 | Pipe table | Table样式、无直接边框 | 结构和数据存在 | 1/0.5/1 pt及无竖线 | Word边框 | SUPPORTED_WITH_POSTPROCESS |
| 表编号 | 静态“表1” | 普通文本 | 无SEQ域 | 未实现 | 动态编号 | WORD_MANUAL_REQUIRED |
| 表交叉引用 | 静态首次引用 | 普通文本 | 无REF域 | 未来候选 | 动态引用 | WORD_MANUAL_REQUIRED |
| 顺序编码引用 | Pandoc citation keys | citeproc numeric | `[1] [2,3] [4] [5]` | 无 | 最终视觉 | SUPPORTED |
| 参考文献格式 | 五类synthetic BibTeX | 5条列表 | 样式/顺序通过；standard为`[Z]` | 未改官方CSL | HFUT特规 | WORD_MANUAL_REQUIRED |
| 单栏/双栏 | 语义marker | 初始单节 | 最终2节、1/2栏 | continuous section | Word分页 | SUPPORTED_WITH_POSTPROCESS |
| 页码 | reference footer | PAGE域保留 | PAGE存在、无重启 | 无 | Ctrl+A/F9 | SUPPORTED_WITH_WORD_REFRESH |
| Full版本 | full metadata | 虚拟身份注入 | 必需字段扫描通过 | 属性清理 | 视觉确认 | SUPPORTED_WITH_POSTPROCESS |
| Anonymous版本 | anonymous metadata | 不注入身份 | 禁止字符串扫描通过 | 通用属性清理 | Document Inspector | WORD_MANUAL_REQUIRED |
| MathType | LaTeX源 | OMML | 非图片 | 未转换 | 必须 | WORD_MANUAL_REQUIRED |
| Visio/Origin | 未表达 | 未生成 | 不声称可编辑对象 | 无 | 工具不可用 | NOT_TESTED |

## 18. LibreOffice Preview

Both `poc_full_preview.pdf` and `poc_anonymous_preview.pdf` were generated.
Each is A4 and has two pages. The preview shows page numbers 1/2, the intended
column transition, 0/1/1.1/1.1.1 numbering, editable-equation rendering,
visible three-bar fallback image, complete three-column table, and numeric
references. The anonymous front matter contains only its two status markers.

```text
NON_AUTHORITATIVE_LIBREOFFICE_PREVIEW
MICROSOFT_WORD_RENDERING_NOT_VERIFIED
```

LibreOffice formula glyph spacing and the compact two-column bibliography are
observations only, not Microsoft Word or journal acceptance evidence.

## 19. Files Created

Exactly eight repository files belong to this step:

1. `scripts/paper/run_phase2_5_docx_poc.sh`
2. `scripts/paper/postprocess_phase2_5_poc_docx.py`
3. `scripts/paper/inspect_phase2_5_poc_docx.py`
4. `scripts/paper/phase2_5_poc_styles.lua`
5. `docs/paper/phase2_5/PAPER_PHASE2_5_CSL_SOURCE_MANIFEST_v1.0.csv`
6. `docs/paper/phase2_5/PAPER_PHASE2_5_MARKDOWN_DOCX_POC_PLAN_v1.0.md`
7. `docs/paper/phase2_5/PAPER_PHASE2_5_MARKDOWN_DOCX_POC_REPORT_v1.0.md`
8. `docs/paper/phase2_5/PAPER_PHASE2_5_WINDOWS_WORD_POC_CHECKLIST_v1.0.md`

All Markdown/YAML/BibTeX/CSL/SVG/PNG/DOCX/PDF/log/inspection derivatives
remain outside Git. The canonical reference DOCX was not changed.

## 20. Validation

Passed checks include:

- shell syntax and both Python bytecode compilations;
- Lua filter load;
- CSL XML/title/numeric/Pandoc-load validation;
- two Pandoc return codes of 0 with complete logs;
- post-processing and both OOXML inspections;
- `file`, SHA256, and `unzip -t` for both DOCX files;
- required OOXML parts, A4 geometry, margins, sections, columns, style use,
  OMML, media, table structure/borders, PAGE, numbering, citations, and
  reference list;
- full/anonymous identity boundary scan;
- two LibreOffice PDF previews, each two A4 pages;
- formal `references.bib` remains the six-line empty exchange library;
- all seven formal chapter files remain `STRUCTURE_ONLY`;
- reference DOCX hash remains the required value;
- POC source uses only synthetic values and identities;
- `git diff --check`: PASS.

The Pandoc SVG and zh-CN translation warnings are retained in external stderr
logs. No warning was hidden or promoted to PASS.

## 21. Windows Manual Checks Required

The separate Windows checklist requires Microsoft Word open/repair checks,
page geometry, column boundary, named styles, numbering update/restart,
Ctrl+A/F9, PAGE display, editable equations, MathType compatibility, figure
fallback and caption, table borders and fit, citations/references, full and
anonymous identity review, Document Inspector, save/close/reopen, and Word PDF
export.

MathType, Visio, and Origin are:

```text
TOOL_NOT_AVAILABLE
DEFERRED_PUBLICATION_ASSET_CHECK
```

The status must not be converted to PASS without the tools and manual evidence.

## 22. Step 7 Readiness

`READY_WITH_NONBLOCKING_LIMITATIONS`

The two POC files are ready for Microsoft Word acceptance. The Windows review
must preserve the disclosed limitations and must not treat the CSL standard
type, static cross-references, PNG fallback, or OMML as final publication
solutions.

## 23. Next Executor

`USER_MANUAL`
