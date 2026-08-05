# Paper Phase 2.5 Step 3 Controlled Conversion and Style Analysis Result

## 1. Verdict

`STEP_3_COMPLETE_WITH_PENDING_ITEMS`

The four authorized DOC files were converted through independent, logged LibreOffice profiles; the resulting DOCX packages passed ZIP and required-part validation. Machine-assisted page comparison found matching page counts and A4 dimensions and retained the visible formulas, figures, tables, and references. Pending items are limited to Microsoft Word/application editability checks, a reference-DOCX POC, and source questions that Step 2 intentionally left unresolved.

## 2. Repository State

- Repository: `/home/orin/edge-ai/edge-ai-defect`
- Branch at gate: `main`
- Starting HEAD: `72f5d0c841bcf6defe27b925f7c5bbd5edb0af92`
- Worktree/index at gate: clean
- `git diff --check` at gate: PASS
- Phase 2 tag type: annotated `tag`
- `paper-phase2-complete-v1.0^{}`: `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`

No reset, restore, checkout, stash, clean, merge, rebase, push, or tag modification was performed. No Phase 0, Phase 1, Phase 2, or Step 2 authority file was modified.

## 3. Inputs and Hash Verification

All four raw files remained in `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/raw` and matched the Step 1 manifest before conversion.

| source_id | bytes | SHA-256 | detected type | result |
|---|---:|---|---|---|
| `HFUT_FMT_DOC` | 283136 | `e29119e21dfd567f79a018049d95193f409229fd1470322554aa2492f1d0594d` | OLE Composite Document V2 / Word DOC | PASS |
| `HFUT_FIG_DOC` | 25105920 | `160960cdfcc73896cb443a1b7eeec91e9ad419febc4710bafff5b1882636138a` | OLE Composite Document V2 / Word DOC | PASS |
| `HFUT_TABLE_DOC` | 61952 | `1764dd6bb74e4ea850aad2fd71f87a1a92badfd7d6854edd8ff9db7d09a0f009` | OLE Composite Document V2 / Word DOC | PASS |
| `HFUT_REF_DOC` | 49664 | `5ef440b270b73bad6a57ade6a68e35032c6a5e9829dbd45c05b4574dabb0f651` | OLE Composite Document V2 / Word DOC | PASS |

The GB/T PDF, web-excerpt PDF, and two published-paper PDFs were not converted. No OCR was run.

## 4. Conversion Environment

- LibreOffice: `7.3.7.2 30(Build:2)`
- PDF tools: Poppler `22.02.0`
- ZIP validation: UnZip `6.00` plus Python `zipfile`
- OOXML parser: Python standard library (`zipfile`, `xml.etree.ElementTree`, `csv`, `hashlib`, `pathlib`)
- Existing auxiliary libraries: `olefile 0.46`, Pillow `9.0.1`
- `python-docx`: unavailable and not installed
- ImageMagick: unavailable and not installed

Each of the 12 conversion runs used its own `temporary_profiles/<source_id>_<stage>` profile. The only recurring stderr message was `Warning: failed to launch javaldx - java may not function correctly`; every conversion returned 0 and produced the expected output. Commands, times, return codes, hashes, sizes, and full logs are retained outside Git under the Step 3 derivative root.

All converted DOCX files have the status: `CONTROLLED_CONVERSION_DERIVATIVE`, `NOT_OFFICIAL_ORIGINAL`, `NOT_REFERENCE_DOCX`, `NOT_FINAL_TEMPLATE`, and `NOT_SUBMISSION_FILE`.

## 5. Conversion Manifest

| source_id | DOCX bytes | DOCX SHA-256 | original-DOC PDF bytes | converted-DOCX PDF bytes | run results |
|---|---:|---|---:|---:|---|
| `HFUT_FMT_DOC` | 115846 | `e26cbd73c866a1cd37469036c1581bd8899a84674877e1246740cf11e4c5445d` | 517132 | 501493 | 0 / 0 / 0 |
| `HFUT_FIG_DOC` | 8781422 | `4986a020b4ef9a0447be99765e87d8e0209c340a434e810685d0a4882165cc5f` | 642991 | 645464 | 0 / 0 / 0 |
| `HFUT_TABLE_DOC` | 11769 | `65ecdc7c980c7c962c9e9598e70ed6a9c812a7f4e8ad7a9f250311957716106e` | 112561 | 112620 | 0 / 0 / 0 |
| `HFUT_REF_DOC` | 12170 | `f8d2224e3dd119be68c1c5426c474b930fa62f9a02ae3e12fa4a8b36fa227e47` | 195029 | 194150 | 0 / 0 / 0 |

`run results` lists DOC→DOCX / DOC→PDF / DOCX→PDF return codes. The repository conversion manifest records all PDF hashes, exact external paths, optional-package parts, page comparison, blank-page diagnosis, warning text, and representative PNG paths.

## 6. DOCX Package Validation

All four packages passed `file`, SHA-256 calculation, `unzip -t`, and Python ZIP member testing. Every package contains `[Content_Types].xml`, `word/document.xml`, `word/styles.xml`, `word/settings.xml`, and `word/numbering.xml`. No package contains a theme or header, which is recorded as an optional absence rather than a failure.

| source_id | footer parts | media | embeddings | required parts | ZIP test |
|---|---:|---:|---:|---|---|
| `HFUT_FMT_DOC` | 2 | 12 | 12 | PASS | PASS |
| `HFUT_FIG_DOC` | 0 | 12 | 12 | PASS | PASS |
| `HFUT_TABLE_DOC` | 0 | 0 | 0 | PASS | PASS |
| `HFUT_REF_DOC` | 0 | 0 | 0 | PASS | PASS |

The extracted OOXML, package inventory, parser, summaries, and raw conversion logs remain only in the external derivative root and are not submission artifacts.

## 7. Page and Section Analysis

Every section in all four DOCX files is portrait A4: `11906 × 16838 twips`, corresponding to `21.001 × 29.700 cm`. All sections use top `1361 twips / 2.401 cm`, bottom `1134 twips / 2.000 cm`, and left/right `1304 twips / 2.300 cm` margins. Gutter is zero.

| source_id | sections | section column sequence | column gap | first-page/footer evidence |
|---|---:|---|---|---|
| `HFUT_FMT_DOC` | 2 | 1 → 2 | 424 twips / 0.748 cm | `titlePg`; first/default footers; footer distance 907 twips / 1.600 cm |
| `HFUT_FIG_DOC` | 5 | 1 → 2 → 1 → 2 → 1 | 424 twips / 0.748 cm | no header/footer reference |
| `HFUT_TABLE_DOC` | 3 | 1 → 2 → 1 | 424 twips / 0.748 cm | no header/footer reference |
| `HFUT_REF_DOC` | 2 | 1 → 2 | 424 twips / 0.748 cm | `titlePg`; no header/footer reference |

The FMT first-page footer contains collection/revision date, fund, and author-profile examples. `titlePg` and the many alternating sections are source/conversion evidence, not a complete template blueprint: several section breaks exist to lay out examples. Step 4 should adopt the stable A4/margin/single-to-double-column facts but redesign section boundaries deliberately.

## 8. Style Inventory

The inventory contains 117 styles: 61 FMT, 19 FIG, 23 TABLE, and 14 REF. Relevant reusable candidates are:

- FMT `Normal`: 宋体/SimSun for East Asian text, Times New Roman for Latin text, 10.5 pt, justified.
- FMT `Style19` (`正文样式`): based on Normal, 200-twip first-line indent and exact 320-twip / 16-pt line spacing.
- FMT `Heading1`: 12 pt bold, centered, exact 18 pt, keep-next; it does not match the actual 14-pt direct-formatted body level-1 headings.
- FMT `New1` (`公式样式_new_1`): 宋体/SimSun and Times New Roman, 10 pt; actual displayed formulas do not consistently use it.
- FIG `Style17` (`图题注`): 7.5 pt bold 黑体/SimHei and centered; most actual captions still use Normal plus direct formatting.
- TABLE `Style16` (`图表名`): 7.5 pt bold 黑体/SimHei, centered, exact 16 pt; `Style17` (`图表内容`) is 7.5 pt 宋体/Times New Roman and centered.
- REF has no dedicated reference-entry style; entries predominantly use Normal plus direct size, spacing, and hanging indents.

The TABLE Normal style has Calibri as its Latin font, unlike the source's Times New Roman requirement. A future reference DOCX must use dedicated table styles rather than allowing that Normal inheritance.

## 9. Direct Formatting Analysis

The parser observed 451 paragraphs. Of these, 443 are `MIXED_FORMATTING` and only 8 are `NAMED_STYLE_FORMATTING`; no document provides a clean, consistently applied semantic style system.

| source_id | paragraphs | named style only | mixed | mixed share |
|---|---:|---:|---:|---:|
| `HFUT_FMT_DOC` | 154 | 1 | 153 | 99.35% |
| `HFUT_FIG_DOC` | 82 | 4 | 78 | 95.12% |
| `HFUT_TABLE_DOC` | 162 | 2 | 160 | 98.77% |
| `HFUT_REF_DOC` | 53 | 1 | 52 | 98.11% |

The title, authors, affiliations, Chinese/English abstracts, keywords, actual section headings, formula lines, most captions, most table cells, and reference entries rely on direct run or paragraph properties. Consequently, the converted DOCX is evidence to analyze, not a style template to copy. Step 4 must normalize the confirmed properties into explicit named styles and retain separate content checks.

## 10. Heading and Numbering Analysis

Actual heading observations in FMT are:

- Introduction and level 1: Normal plus direct 14-pt 黑体/SimHei, left aligned; visible `0`/`1` is text.
- Level 2: Normal plus direct 黑体/SimHei, inherited 10.5 pt; visible `1.1` is text.
- Level 3: Normal plus direct 楷体, inherited 10.5 pt; visible `1.1.1` is text.

All four numbering parts contain a generic Heading-linked abstract definition whose levels 0–8 use `numFmt=none` and no level text. FMT adds a single-level decimal `%1`; TABLE adds a single-level decimal `%1）`. No existing definition supports the required `0`, `1`, `1.1`, `1.1.1` hierarchy. The visible heading numbers must therefore not be reported as an established automatic multilevel list. Step 4 requires a purpose-built numbering POC with keep-next, no-wrap behavior, cross-references, and update testing.

## 11. Formula and Embedded Object Analysis

FMT raw DOC has 13 ObjectPool storages: 10 identifiable MathType candidates, 1 generic equation-OLE candidate, 1 Origin candidate, and 1 Visio candidate. Its converted DOCX has 12 `w:object` OLE containers (10 MathType, 1 Origin, 1 Visio) plus 1 `m:oMath` node. FIG has the same 13→12+1 pattern: the raw file has 1 generic equation-OLE candidate, 9 Visio candidates, and 3 Origin candidates; the DOCX has 9 Visio and 3 Origin OLE containers plus 1 `m:oMath` node.

This count reconciliation supports an inference that each generic equation-OLE item was transformed to OMML, while the identifiable OLE objects were retained. It is not proof of semantic equivalence or Word editability. LibreOffice left OOXML ProgID values blank, although embedded compound-file signatures identify MathType 6.0 Equation, Visio, and Origin candidates. The report therefore uses `EDITABLE_OLE_PRESERVED_CANDIDATE`, never “confirmed editable.” OMML is not treated as MathType.

Both FMT and FIG contain 12 VML shapes, 12 embedded OLE files, and 12 WMF/EMF preview relationships; neither contains `w:drawing`. No evidence shows that the 12 identifiable OLE objects were replaced solely by flat raster images. TABLE and REF contain no objects in either raw ObjectPool or converted OOXML.

FMT displayed equation paragraphs P030–P034 use Normal plus direct right alignment. Equation labels `(1)`–`(4)` are ordinary text in the same paragraph; no tab, field, or table structure was detected. Formula-related formatting is therefore mixed/direct and the current space-based positioning must not be copied into the reference DOCX.

## 12. Figure Analysis

FIG provides real OLE-preservation candidates: 9 Visio and 3 Origin containers after conversion, each with a WMF/EMF preview. Internal object text fonts and sizes cannot be reliably read from WordprocessingML, so the rule remains explicitly split: Visio object text is 8 pt; other figure text follows the separate six-size requirement. No unification is authorized.

The document includes both single- and double-column sections, but the written limits—single-column width ≤7.5 cm and full-width ≤16.0 cm—remain the governing values; example object dimensions are not promoted to new limits. FIG caption style evidence supports a 7.5-pt bold 黑体/SimHei centered candidate, while the actual captions mostly use direct formatting.

Rendered pages retain all visible flowcharts, plots, exploded diagrams, simulation contours, and maps. The OLE plus preview structure is not equivalent to a screenshot-only insertion, but application editability still needs Word plus Visio/Origin checks. No generic DPI, color-mode, image-format, or line-width requirement was recovered.

The geological-map conflict is visible in both XML and the rendered page: P049 refers to 图11 while P050 captions it 图9. Under the project decision, this remains `RESOLVED_BY_AUTHORITY`: continuous numbering takes precedence over the erroneous example number.

## 13. Table Analysis

Seven tables were parsed in total: 2 embedded in FMT and 5 in TABLE. TABLE's examples confirm ordinary three-line construction through direct cell borders. Regular evidence includes 1-pt top/bottom and 0.5-pt secondary rules; example-specific exceptions include a 1.5-pt bottom rule, a 0.25-pt double top rule, and the vertical-table example's 0.5-pt double internal vertical borders. Those exceptions must not be promoted to the common rule.

Dedicated table-name/content styles specify 7.5-pt 黑体 or 宋体/Times New Roman. Actual cells are direct-formatted and include 6.5- and 7.5-pt runs. Table alignment varies between start and center; table captions also include centered, end-aligned, and 9-pt examples. All tables use 108-twip / 5.4-pt start/end cell margins and zero top/bottom cell margins. Merging evidence includes `gridSpan=2` twice and eight vertical-merge markers across the TABLE examples.

No true continuation-table example was detected. The note after table 5 is outside the table. Step 4 should implement the confirmed 1/0.5/1-pt three-line style and 7.5-pt content, then separately test page continuation, notes, merged cells, unit placement, and horizontal segmentation.

## 14. Reference Style Analysis

Reference entries are 7.5 pt, use 宋体/SimSun for Chinese and Times New Roman for Latin text where explicitly set or inherited, and generally use exact 280-twip / 14-pt line spacing. They use hanging indents, but converted values vary by example from 227 to 396 twips (11.35–19.8 pt); the rule-description paragraph uses 440 twips / 22 pt. Paragraph spacing before/after is not consistently defined.

Entry numbers such as `[1]` are ordinary paragraph text. No `numPr` evidence establishes automatic reference numbering. There is no dedicated reference-entry named style, and mixed direct formatting dominates. Step 4 should create one controlled reference style and test a selected hanging indent with one-, two-, and three-digit numbers, long URLs, mixed Chinese/English text, and double-column flow.

The attachment text names GB/T 7714—2025, but this step neither OCRed the provided standard copy nor created a source chain. Author truncation thresholds, mandatory DOI rules, and whether Chinese references need English counterparts remain unresolved.

## 15. Conversion Fidelity

| source_id | pages DOC / DOCX | page size | blank pages DOC / DOCX | representative visual result |
|---|---|---|---|---|
| `HFUT_FMT_DOC` | 4 / 4 | A4 / A4 | none / none | formulas, charts, tables, references retained; minor text raster-position differences |
| `HFUT_FIG_DOC` | 4 / 4 | A4 / A4 | none / none | all figure examples retained; layout visually stable |
| `HFUT_TABLE_DOC` | 2 / 2 | A4 / A4 | page 2 / page 2 | page 1 tables retained; source near-blank page 2 is pixel-identical |
| `HFUT_REF_DOC` | 2 / 2 | A4 / A4 | none / none | entries retained; visual layout stable with small text-position differences |

All 12 page pairs rendered to `993 × 1404` pixels at 120 dpi. A Pillow diagnostic found no dimension mismatch. Mean absolute channel difference ranged from 0 to 10.870718; changed-pixel ratio above a grayscale difference threshold of 3 ranged from 0 to 0.09653543. These numbers are `CONVERSION_DIAGNOSTIC`, not `VISUAL_FIDELITY_CERTIFICATION`.

The first, last, and all formula/figure/table representative pages were rendered and inspected. No obvious content disappearance or new page-count change was found. The TABLE near-blank page 2 exists in both render paths and is not a conversion-introduced blank page. Microsoft Word manual acceptance was not performed.

Representative PNGs and full metrics are under `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step3_docx_style_analysis_v1/rendered_pages` and `metadata/render_fidelity_metrics.csv`.

## 16. Step 2 Pending-Rule Disposition

The Step 3 disposition contains 32 targeted rows and does not duplicate the full 121-rule Step 2 crosswalk. It covers rules with page/style/object/layout evidence, explicit Step 3 routing, conflicts, and pending items.

Key results:

- `CG-TITLE-LENGTH`: project implementation uses no more than 20 Chinese characters while retaining source wording differences.
- `CG-FIG-TEXT-SIZE`: not unified; 8 pt Visio and six-size other-figure rules remain separate.
- `CG-FIG-EXAMPLE-NUMBER`: resolved by authority; continuous numbering wins over the 图11/图9 sample error.
- `CG-GBT-SOURCE-CHAIN`: remains pending; no OCR or invented source chain.
- Page geometry, Normal/body properties, heading appearance, caption candidates, three-line table borders, and reference font/size/line spacing now have OOXML evidence.
- Automatic multilevel heading numbering, equation numbering, reference numbering, OLE editability, generic figure delivery parameters, bilingual caption needs, continuation-table behavior, and selected reference details still require POC, Windows checks, or source confirmation.

## 17. Unresolved Items

1. Open each converted DOCX in Microsoft Word on Windows and compare representative pages at normal and print-layout zoom.
2. Test the 10 MathType, 10 Visio, and 4 Origin OLE candidates with their native applications; confirm double-click editing, saving, and reopening. Also inspect the two OMML conversions.
3. Resolve the raw equation-OLE→OMML inference by object-level Windows comparison; no object loss is currently demonstrated.
4. Build and test, in Step 4 only, semantic styles for page sections, titles, abstracts, body, headings, captions, tables, formulas, references, and the first-page footer.
5. Confirm article-number/date responsibility, figure DPI/format/color/line-width parameters, bilingual caption/legend policy, continuation-table rules, and reference source-chain questions.

## 18. Files Created

The only repository outputs are:

1. `PAPER_PHASE2_5_DOC_CONVERSION_MANIFEST_v1.0.csv`
2. `PAPER_PHASE2_5_WORD_STYLE_INVENTORY_v1.0.csv`
3. `PAPER_PHASE2_5_PARAGRAPH_FORMAT_OBSERVATIONS_v1.0.csv`
4. `PAPER_PHASE2_5_OBJECT_INVENTORY_v1.0.csv`
5. `PAPER_PHASE2_5_STEP3_RULE_DISPOSITION_v1.0.csv`
6. `PAPER_PHASE2_5_STYLE_ANALYSIS_REPORT_v1.0.md`

Converted DOCX/PDF files, PNG previews, extracted OOXML, logs, temporary profiles, and analysis metadata remain outside Git in the designated derivative root.

## 19. Validation

Automated validation checks:

- six required repository outputs exist;
- all four source IDs occur in the conversion manifest and object inventory;
- all required input/output hashes have 64 hexadecimal characters;
- all converted DOCX packages pass ZIP testing and required-part checks;
- style and paragraph inventories are nonempty;
- rule disposition has unique rule IDs and only allowed status enums;
- raw SHA-256 values still match the Step 1 manifest;
- no Phase 0/1/2 authority file is changed;
- no `reference.docx`, POC DOCX, paper body, BibTeX, CSL, preview, extracted OOXML, or log is added to Git;
- repository diff contains only the six specified outputs;
- `git diff --check` passes.

## 20. Step 4 Readiness

`READY_WITH_PENDING_WINDOWS_CHECKS`

There is sufficient evidence to design a controlled reference DOCX and its POC, but the converted files themselves must not be used as the reference DOCX or final template. Step 4 should treat Step 2 text rules as authoritative, use the Step 3 style evidence as implementation input, and explicitly test every conversion-ambiguous or direct-formatting-only behavior.

## 21. Next Executor

`PAPER_PROJECT_AI`
