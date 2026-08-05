# Paper Phase 2.5 Journal Format Specification v1.0

## 1. Document Status

- Phase: `Paper Phase 2.5 Step 2 — Journal Specification Extraction`.
- Status: `STEP_2_COMPLETE_WITH_PENDING_ITEMS`.
- Extraction date: `2026-08-05` (Asia/Shanghai).
- Target journal: 《合肥工业大学学报（自然科学版）》.
- Machine-checkable authority: `PAPER_PHASE2_5_FORMAT_RULE_CROSSWALK_v1.0.csv`.
- Scope: submission, typography, equations, figures, tables, references, and
  anonymization requirements only.
- Excluded: `reference.docx`, formal manuscript project, Markdown-to-DOCX POC,
  manuscript prose, bibliography creation, CSL creation, and formal figures or
  tables.

The specification distinguishes:

- `TEXTUALLY_EXPLICIT_REQUIREMENT`: a requirement recoverable from source text;
- `STYLE_EMBEDDED_PENDING_STEP3`: a value possibly present only in Word styles,
  page settings, drawing objects, or lost equation objects;
- `VISUAL_EXAMPLE_ONLY`: an observation or example that is not an author-side
  mandatory rule.

## 2. Source Authority

Authority is applied in this order:

1. target-journal submission guide and journal attachments;
2. user-captured target-journal web requirements;
3. standards explicitly cited by the journal;
4. the user-provided GB/T copy;
5. published target-journal articles as visual examples only.

| Source ID | Classification used in Step 2 | Authority handling |
|---|---|---|
| `HFUT_FMT_DOC` | `OFFICIAL_JOURNAL_ATTACHMENT_CANDIDATE` | Official page ID 415 and matching title were reachable; download payload timed out, so no byte-for-byte official chain is claimed. |
| `HFUT_REF_DOC` | `OFFICIAL_JOURNAL_ATTACHMENT_CANDIDATE` | Official page ID 414 and matching title were reachable; payload chain remains unverified. |
| `HFUT_FIG_DOC` | `OFFICIAL_JOURNAL_ATTACHMENT_CANDIDATE` | Official page ID 413 and matching title were reachable; payload chain remains unverified. |
| `HFUT_TABLE_DOC` | `OFFICIAL_JOURNAL_ATTACHMENT_CANDIDATE` | Official page ID 412 and matching title were reachable; payload chain remains unverified. |
| `HFUT_WEB_EXCERPT_PDF` | `USER_CAPTURED_WEB_EXCERPT` | Textual evidence from the official guide page, but not an official template original. |
| `GBT7714_2025_PDF` | `USER_PROVIDED_STANDARD_COPY` | Not described as an official standard-body original; no extractable text was obtained. |
| `HFUT_ARTICLE_2026_5_2_PDF` | `OFFICIAL_JOURNAL_PUBLISHED_ARTICLE_VERIFIED` | `EXAMPLE_ONLY / VISUAL_REFERENCE_ONLY`. |
| `HFUT_ARTICLE_2026_1_3_PDF` | `OFFICIAL_JOURNAL_PUBLISHED_ARTICLE_VERIFIED` | `EXAMPLE_ONLY / VISUAL_REFERENCE_ONLY`. |

The eight raw files remained `READ_ONLY_EXTERNAL_SOURCE`. Their sizes and
SHA256 values were recomputed and all matched the Step 1 manifest.

## 3. Extraction Method

The external derivative root is:

```text
/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step2_spec_extraction_v1
```

The four OLE DOC files were read through LibreOffice 7.3.7.2 because
`antiword`, `catdoc`, and `wvText` were unavailable. LibreOffice produced plain
TXT derivatives only. Non-empty extracted lines were normalized as `P001`,
`P002`, and so on for locators. These derivatives are:

```text
TEXT_EXTRACTION_DERIVATIVE_ONLY
NOT_OFFICIAL_ORIGINAL
NOT_REFERENCE_DOCX
NOT_STYLE_AUTHORITY
```

No formal DOC-to-DOCX conversion or style inspection occurred. Poppler
`pdfinfo`/`pdftotext` 22.02.0 processed PDFs without OCR. The web excerpt has
extractable text. The 45-page GB/T PDF yielded only page breaks and therefore
has status `TEXT_EXTRACTION_PENDING / OCR_NOT_AUTHORIZED_IN_STEP_2`. The two
article PDFs contain a font collection that prevents reliable Chinese text
decoding; rendered sample pages were visually reviewed without OCR.

## 4. General Manuscript Requirements

The official-guide excerpt explicitly requires a clear, evidence-based,
readable manuscript containing the bilingual front matter, classification,
body, references, and author biography listed in `HFUT-WEB-001`.

Main limits and content rules are:

- the Chinese title is generally no more than 20 Chinese characters;
- a subtitle is generally not used;
- the manuscript is generally within 10,000 Chinese characters;
- the introduction addresses the research background, scope, literature,
  method, and main result, especially work from the latest 2 years;
- the conclusion follows from observed or experimental results and does not
  merely repeat them;
- non-common abbreviations are expanded at first use;
- quantities, legal units, case, upright/italic, weight, superscript, and
  subscript are checked explicitly.

Exact page size, margins, columns, body paragraph spacing, first-line indent,
and body line spacing are not present in the extracted text. They are
`STYLE_EMBEDDED_PENDING_STEP3` and must not be inferred from published pages.

## 5. Title, Author and Affiliation

- Chinese title: `HFUT-WEB-002` and `HFUT-FMT-001`. Both use 20 as the limit,
  but the web guide says “generally” while the attachment candidate is strict;
  see `CG-TITLE-LENGTH`.
- English title: meaning matches Chinese; capitalization uses sentence-initial
  and proper-noun capitals (`HFUT-WEB-004`, `HFUT-FMT-008`).
- Chinese affiliations include second-level unit, province, city, and postcode
  (`HFUT-FMT-002`).
- English author names use uppercase family names and initial-capital given
  names (`HFUT-FMT-009`).
- The guide requires an author biography in the first-page footer with name,
  birth year, sex, native place, degree, and professional title
  (`HFUT-WEB-025`).
- Funding type and project number are supplied only when a real funding project
  applies (`HFUT-WEB-026`). No funding data may be invented.

The author-side responsibility for the article number, document code `A`,
received date, and revised date is not established by the current text.
Published-page appearances of those fields are `VISUAL_EXAMPLE_ONLY`.

## 6. Chinese and English Abstracts

- The Chinese abstract is preferably report-style and covers purpose, method,
  result, and conclusion (`HFUT-WEB-005`).
- It is self-contained, generally at least 150 Chinese characters, uses third
  person, does not repeat title/introduction content, and avoids figure, table,
  equation, and reference numbers (`HFUT-WEB-006`–`007`).
- The format attachment recommends about 300 Chinese characters
  (`HFUT-FMT-004`); this is compatible with the 150-character general minimum.
- Chinese abstract label: small-five Heiti; abstract text: small-five Songti,
  14 pt line spacing (`HFUT-FMT-003`).
- The English abstract matches the Chinese meaning and uses five-size Times New
  Roman (`HFUT-WEB-008`, `HFUT-FMT-010`).

The Word style IDs, paragraph inheritance, before/after spacing, and exact
English line spacing remain Step 3 items.

## 7. Keywords and Classification

- At least 4 normalized Chinese keywords are required
  (`HFUT-WEB-009`).
- English keywords match Chinese keywords in meaning, count, and order; an
  abbreviation is introduced after its full English form
  (`HFUT-WEB-010`, `HFUT-FMT-011`).
- Keyword label: small-five Heiti; keyword content: small-five Songti; generic
  words are avoided (`HFUT-FMT-005`).
- The Chinese Library Classification number is mandatory
  (`HFUT-FMT-006`). The sample `TU 411.01` is not the classification of this
  paper.
- The sample document code `A` is `PENDING_VERIFICATION`; it must not be copied
  automatically (`HFUT-FMT-007`).

## 8. Heading and Body Formatting

The extracted text states:

| Element | Textually explicit setting |
|---|---|
| Body Chinese / Latin | five-size Songti / five-size Times New Roman |
| Introduction | numbered `0`; level-1 format; flush left |
| Level 1 | four-size Heiti; numeric form such as `1` |
| Level 2 | five-size Heiti; numeric form such as `1.1` |
| Level 3 | five-size Kaiti; numeric form such as `1.1.1` |
| All headings | do not wrap to a second line |

Rules: `HFUT-FMT-012`–`016`. Page geometry, columns, line/paragraph spacing,
and first-line indentation are deferred to Step 3. A complete general rule for
body punctuation, numeral writing, and foreign-letter treatment was also not
found beyond the explicit quantity/unit and upright/italic rules; see
`HFUT-FMT-029`.

## 9. Mathematical Expressions

Textually explicit requirements are:

- follow the journal-referenced GB/T 7713.2—2022 and GB 3102.11-93;
- enter and edit equations with MathType;
- italicize variables; use upright subscripts generally and italic subscripts
  when the subscript itself is a variable;
- except for function names and special physical quantities, use one letter per
  variable, with subscripts where needed;
- use bold italic letters for matrices and vectors;
- explain the meaning of letter symbols with the equation.

Rules: `HFUT-FMT-017`–`022`. The extracted formula bodies were lost. Equation
font, numbering position, body references, punctuation after equations, and
long-equation wrapping are `STYLE_EMBEDDED_PENDING_STEP3` under
`HFUT-FMT-023`. MathType conversion capability is deferred to the Step 6 POC;
it is not assumed that `reference.docx` alone can implement the requirement.

## 10. Figures

Textually explicit figure rules include:

- maximum width 7.5 cm for a single-column figure and 16.0 cm for a
  full-width figure;
- Chinese figure text in Songti; letters/digits in Times New Roman;
- after satisfying width limits, Visio figure text is 8 pt and other figure
  text is equivalent to Word six-size;
- figures are called out before placement and numbered continuously; subfigures
  use `(a)`, `(b)`, `(c)` and are cited as forms such as `图1a`;
- curve plots preferably use Origin; they are copied as a page into Word and
  must not be screenshots or flattened generated images;
- curve plots include curves, axes, ticks, values, quantities, and units, with
  background/fill removed;
- flowcharts/block diagrams use Visio and remain editable in Word; other
  text-bearing images use Visio text layers;
- coordinate axes include quantity names and standard units; variables are
  italic, units upright, slash-separated, with compound and angular units in
  parentheses;
- bar charts have category labels; vector/matrix notation and units in
  dimensioned or contour figures follow the rules in the crosswalk.

Figure-caption six-size Heiti/centering is an example-only observation pending
Step 3. File format, resolution, DPI, color mode, and general line width were
not found and must not be invented. General legend styling and whether bilingual
figure captions are required are also pending (`HFUT-FIG-020`). Map rules are
`NOT_APPLICABLE` to the current figure plan; they must be reactivated if a map
is later introduced.

## 11. Tables

Textually explicit table rules are:

- call out the table before placement and number tables continuously;
- use three-line tables throughout;
- top and bottom rules are 1 pt; the secondary rule is 0.5 pt;
- Chinese text is six-size Songti; letters/digits are six-size Times New Roman;
- quantity/unit headers use `quantity symbol or name / unit symbol`, with
  compound units parenthesized;
- every column has an accurate name;
- decimals in one column use a consistent number of places, padding display
  positions with zero when required;
- `－` means measured but not found, `0` means a measured zero, and blank means
  not applicable or not measured.

Table-caption six-size Heiti, units in the upper-right, auxiliary rules,
vertical-to-column conversion, and horizontal segmentation are examples only.
Alignment, cell padding, continuation-table handling, a general note style, and
any bilingual table-caption requirement remain pending Step 3/Windows review.

## 12. References

The journal guide requires sequential numeric citation order, with references
ordered by first occurrence, generally at least 8 real and read references,
including attention to recent 3-year domestic, international, and journal
literature.

The reference attachment candidate explicitly says to follow GB/T 7714—2025
and gives journal-specific typography: Chinese six-size Songti, letters/digits
six-size Times New Roman, 14 pt line spacing. It supplies textual field patterns
for journal articles `[J]`, books `[M]`, conference papers `[C]`, dissertations
`[D]`, standards `[S]`, preprints `[PP/OL]`, web resources `[EB/OL]`, patents
`[P]`, reports `[R]`, and maps `[CM]`. Exact rules are
`HFUT-REF-001`–`015`.

The following remain pending:

- the author-count threshold for `等` / `et al.`;
- a universal Chinese-reference English-translation requirement;
- whether DOI is mandatory for every entry where available;
- detailed GB/T 7714—2025 punctuation and edge cases not recoverable from the
  journal attachment patterns.

The 45-page GB/T copy produced zero non-whitespace text. OCR is not authorized.
The journal's explicit special requirements take precedence over any later
general-standard defaults, but no unextracted standard clause is invented.

## 13. Submission and Anonymization

- Submit through the journal's online system.
- Both the original and review versions are Word documents.
- The review version must delete author-related information.
- All authors' contact information is accurately entered in the submission
  platform.

The source does not enumerate whether “author-related information” includes
every instance of funding, acknowledgements, contact information, document
properties, comments, and tracked changes. These items must all be checked
conservatively in Windows Word, but their individual deletion is recorded as
`PENDING_VERIFICATION`, not falsely promoted to an explicit journal clause.
The exact allowed Word extension (`.doc` versus `.docx`) is also not stated.

## 14. Published-Article Visual Observations

`1003-5060-2026-5-2.pdf`:

- title: 一种基于通道图卷积的手势识别框架;
- column: 机器人与人工智能;
- Vol. 49 No. 5 (May 2026), pages 585–590;
- DOI: `10.3969/j.issn.1003-5060.2026.05.002`;
- Chinese/English title, author/affiliation, abstract, and keyword regions are
  present; sampled body/end pages show figures, equations, and references.

`1003-5060-2026-1-3.pdf`:

- title: 基于卷烟配送质效提升的单人单车技术研究;
- column: 机器人与人工智能;
- Vol. 49 No. 1 (January 2026), pages 22–27 and 35;
- DOI: `10.3969/j.issn.1003-5060.2026.01.003`;
- Chinese/English title, author/affiliation, abstract, and keyword regions are
  present; sampled body/end pages show figures, tables, equations, and
  references.

These observations are `EXAMPLE_ONLY / VISUAL_REFERENCE_ONLY`. They do not
establish author-side column count, margins, typography, submission-template
styles, or mandatory metadata. Neither article is automatically entered into
the current bibliography.

## 15. Conflicts and Pending Verification

| Conflict group | Sources | Conflicting values | Authority analysis | Proposed resolution | Resolution status |
|---|---|---|---|---|---|
| `CG-TITLE-LENGTH` | `HFUT_WEB_EXCERPT_PDF`; `HFUT_FMT_DOC` | same numeric 20, but `RECOMMENDED` versus `MANDATORY` wording | Guide excerpt is traceable official-guide text; DOC remains attachment candidate | Enforce 20 as the safe project limit while retaining the wording conflict record | `PAPER_PROJECT_AI_DECISION_REQUIRED` |
| `CG-FIG-TEXT-SIZE` | `HFUT_FMT_DOC`; `HFUT_FIG_DOC` | general six-size Songti versus Visio-specific 8 pt and other figures equivalent to six-size | Dedicated figure attachment is more specific, but both payload chains remain candidate-level | Use 8 pt for Visio and six-size-equivalent for other figures only after Step 3 visual/style confirmation | `PENDING_STEP3_STYLE_ANALYSIS` |
| `CG-FIG-EXAMPLE-NUMBER` | `HFUT_FIG_DOC` P009, P049-P050 | explicit continuous numbering; example says figure 11 then caption extracts as figure 9 | Textual general rule outranks an inconsistent example | Do not reproduce example number; validate continuous numbering | `RESOLVED_BY_AUTHORITY` |

Pending rather than value-conflicting:

- `CG-GBT-SOURCE-CHAIN`: the journal candidate explicitly names GB/T
  7714—2025, but the user-provided standard copy has no extractable text and no
  verified standard-body provenance. An accessible authoritative text or a
  separately authorized method is needed.
- Four DOC official page titles were verified online, but download payloads
  timed out; local files therefore remain attachment candidates.
- All layout parameters listed as `STYLE_EMBEDDED_PENDING_STEP3` require
  controlled conversion and style inspection.

## 16. Implementation Mapping

| Layer | Main rule responsibility |
|---|---|
| `MARKDOWN_SOURCE` | content fields, headings, terminology, units, citations, callout order, table data semantics |
| `PANDOC_BUILD` | generation of author/review Word candidates; capability not yet tested |
| `REFERENCE_DOCX` | page and paragraph styles, fonts, headings, abstract and reference styles after Step 3 evidence |
| `POST_BUILD_OOXML` | precise table borders, figure extents, and any proven deterministic fixes |
| `WORD_MANUAL` | pagination, no-wrap headings, placement, anonymization, final submission review |
| `MATHTYPE_MANUAL` | journal-required equation objects and typography; automation deferred to POC |
| `VISIO_MANUAL` | editable flowcharts, block diagrams, and text-bearing figures |
| `ORIGIN_MANUAL` | editable curve plots and chart-specific labels |
| `ZOTERO_BIBTEX` | verified bibliography metadata and reference inventory |
| `CSL` | sequential citations and reference rendering, subject to Step 6 POC |
| `NOT_YET_DECIDED` | requirements with missing source evidence or untested implementation |

No statement in this document assumes all requirements can be implemented by
`reference.docx`.

## 17. Step 3 Requirements

Step 3 must:

1. perform controlled DOC-to-DOCX conversion outside Git and outside `raw`;
2. record converter version, commands, logs, output hashes, and derivative
   status labels;
3. inspect page size, margins, section columns, header/footer, styles, fonts,
   sizes, line/paragraph spacing, indentation, tabs, numbering, and language;
4. inspect the lost formula examples and equation-number positioning without
   treating converted equations as new official originals;
5. inspect figure/table captions, drawing objects, table alignment/padding,
   continuation behavior, and the `CG-FIG-TEXT-SIZE` conflict;
6. compare controlled conversion visually in Windows Word and record any
   LibreOffice fidelity limitations;
7. preserve all Step 2 authority classifications and never overwrite raw
   inputs.

Step 3 may not create `reference.docx`; that remains Step 4.

## 18. Prohibited Assumptions

Do not assume or invent:

- page dimensions, margins, columns, spacing, indentation, or style inheritance;
- equation font, numbering position, punctuation, wrapping, or automatic
  MathType conversion;
- figure DPI, raster format, color mode, general line width, or caption style;
- table alignment, padding, continuation style, or caption style from examples;
- GB/T clauses that were not extracted;
- author-count thresholds, universal DOI inclusion, or bilingual-reference
  rules not stated in the attachment text;
- that published-page appearance is an author submission requirement;
- that received/revised dates, article number, or document code are author
  supplied;
- that either published article belongs in the bibliography;
- that the four local DOC payloads have been byte-matched to official downloads;
- that any untested checklist item has passed.
