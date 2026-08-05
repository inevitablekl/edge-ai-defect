# Paper Phase 2.5 Step 2 Specification Extraction Result

## 1. Verdict

`STEP_2_COMPLETE_WITH_PENDING_ITEMS`

Step 2 extracted traceable textual requirements from the four external DOC
attachment candidates and the captured official-guide excerpt, classified
published-paper observations as examples only, and recorded all unavailable or
style-dependent values as pending. No requirement was reconstructed from
`strings`, OCR, published-page measurements, or unsupported assumptions.

## 2. Repository State

- Required branch: `main`; observed: `main`.
- Required starting HEAD: `74514d77d76634ba7dae0ebe22571db8ef0f27e8`;
  observed: exact match.
- Starting worktree/index: clean.
- Starting `git diff --check`: pass.
- `paper-phase2-complete-v1.0` type: `tag`.
- Peeled tag commit: `09277fa0b6cec4bc812e6fa75c4d8f94de397ff0`;
  required and observed values match.
- Phase 0, Phase 1, and Phase 2 files modified: `NO`.

No reset, restore, checkout, stash, clean, merge, rebase, push, or tag
modification was performed.

## 3. Sources Processed

All eight manifest inputs were processed under their Step 1 authority classes.
Actual size and SHA256 were recomputed for every raw file; all eight matched the
existing manifest exactly.

| Source ID | Role in Step 2 | Result |
|---|---|---|
| `HFUT_FMT_DOC` | journal format attachment candidate | text extracted; official page title verified online; payload chain remains candidate |
| `HFUT_FIG_DOC` | journal figure attachment candidate | text extracted; official page title verified online; payload chain remains candidate |
| `HFUT_TABLE_DOC` | journal table attachment candidate | text extracted; official page title verified online; payload chain remains candidate |
| `HFUT_REF_DOC` | journal reference attachment candidate | text extracted; official page title verified online; payload chain remains candidate |
| `GBT7714_2025_PDF` | user-provided standard copy | 45 pages; no extractable text; OCR not authorized |
| `HFUT_WEB_EXCERPT_PDF` | captured official-guide excerpt | 2 pages; text extracted successfully |
| `HFUT_ARTICLE_2026_5_2_PDF` | published visual reference | identity/column/layout roles checked; not a mandatory-rule source |
| `HFUT_ARTICLE_2026_1_3_PDF` | published visual reference | identity/column/layout roles checked; not a mandatory-rule source |

The four official landing pages were reachable and displayed titles matching
the local DOC names. Direct download payload requests timed out, so Step 2 does
not claim byte-for-byte official attachment verification.

## 4. Extraction Tools

| Tool | Availability/version | Use |
|---|---|---|
| `file` | 5.41 | input type confirmation |
| `antiword` | unavailable | not used |
| `catdoc` | unavailable | not used |
| `wvText` | unavailable | not used |
| LibreOffice / `soffice` | 7.3.7.2 | direct OLE DOC to derivative TXT extraction |
| `pdftotext` | Poppler 22.02.0 | PDF text extraction without OCR |
| `pdfinfo` | Poppler 22.02.0 | PDF page/version/encryption metadata |
| `pdftoppm` | Poppler 22.02.0 | published-article visual samples without OCR |
| `mutool` | unavailable | not used |
| Python | 3.10.12 | manifest and CSV validation only |

No package installation command was run. LibreOffice logged a `javaldx`
warning but converted all four DOC inputs successfully.

## 5. DOC Extraction Results

Derivative root:

```text
/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step2_spec_extraction_v1
```

All derivatives are `TEXT_EXTRACTION_DERIVATIVE_ONLY`,
`NOT_OFFICIAL_ORIGINAL`, `NOT_REFERENCE_DOCX`, and `NOT_STYLE_AUTHORITY`.

| Source | Lines / bytes | Raw TXT SHA256 | Normalized TXT SHA256 | Result |
|---|---:|---|---|---|
| format DOC | 153 / 10,672 | `2dd838b2c1d94fe5c8bb97ff8b94f73e4b52499c199f77b6d102c15d8d987fe5` | `e7cb5b6e6a5f5b0b5fd4329b2d2e47ad4f01a7bd26b012e3feb60c4bc7c578cc` | reliable textual requirements; embedded styles pending Step 3 |
| figure DOC | 78 / 4,656 | `bcc91405602d12e4467ae52e8975f78db3c527535fadba83db5789a9d8679328` | `e714becf5cd9006f81e2cbed5fa6281197b06dfa3d419f06d89d8496870968fc` | reliable textual requirements; visual examples not promoted |
| table DOC | 160 / 1,995 | `8ac7da7f5dd703caa97b5b20a249106561f4be47c1972593eef0c50cd6120298` | `d7d64bf2979e42670dbdf455ba6df839f1e48540bd642b6698aa3a287cb7d9ca` | reliable textual requirements; example-only layout retained |
| reference DOC | 52 / 6,203 | `f90b20aea56ea4e3749ceddfd09dfd49c3bc4fe247f17e8647d183b4623b561c` | `f1572da1b67b72d9142dba3d8962196f3e2b84a37c4c5bb108f436527ce68c9e` | reliable textual requirements and entry patterns |

No DOCX was generated and no Word style was parsed.

## 6. PDF Extraction Results

| PDF | Metadata | Text result | Derivative text SHA256 | Handling |
|---|---|---|---|---|
| GB/T 7714—2025 copy | PDF 1.7; 45 pages; unencrypted | zero non-whitespace text | `31143c04bf94919546ef4881874288f7fa8e854f74c2797ece2f9df0e3e04152` | `TEXT_EXTRACTION_PENDING`; `OCR_NOT_AUTHORIZED_IN_STEP_2` |
| web excerpt | PDF 1.4; 2 pages; unencrypted | complete guide excerpt text | `38a99cef4a056db5ef36e97356c0cc0f0ee48b3e4a6d2a3d1c391047326b5a62` | textual requirements extracted by page/section |
| article 2026-5-2 | PDF 1.7; 6 pages; unencrypted | text bytes produced but Chinese decoding unreliable due embedded collection `JoinusRIP-748` | `9d83afadfc09559b612a88a59ee4ca824b6e727217160d32d6759adbb9c96baf` | identity from source records/official issue page; rendered visual samples only |
| article 2026-1-3 | PDF 1.7; 7 pages; unencrypted | text bytes produced but Chinese decoding unreliable due embedded collection `JoinusRIP-748` | `f7809ad68d6bd5822f3023fe69bccb7e0a0d7eae2ba52a27baf2805bccfad9cb` | identity from source records/official page; rendered visual samples only |

No OCR was performed. The article files were not added to `references.bib` and
no such file was created.

## 7. Rule Counts

| Requirement level | Count |
|---|---:|
| `MANDATORY` | 82 |
| `RECOMMENDED` | 11 |
| `EXAMPLE_ONLY` | 10 |
| `PENDING_VERIFICATION` | 15 |
| `NOT_APPLICABLE` | 3 |
| **Total** | **121** |

## 8. Rules by Category

| Category | Count |
|---|---:|
| `GENERAL_MANUSCRIPT` | 4 |
| `TITLE_AUTHOR_AFFILIATION` | 10 |
| `ABSTRACT` | 7 |
| `KEYWORDS_CLASSIFICATION` | 6 |
| `HEADING_BODY` | 10 |
| `MATHEMATICAL_EXPRESSIONS` | 7 |
| `FIGURE` | 25 |
| `FIGURE_TABLE` | 1 |
| `TABLE` | 14 |
| `REFERENCES` | 24 |
| `SUBMISSION_ANONYMIZATION` | 5 |
| `PUBLISHED_VISUAL` | 8 |
| **Total** | **121** |

## 9. Source Authority Resolution

- Journal guide text and journal attachment text control journal-specific
  requirements.
- The official page titles support the identity of the four candidate roles but
  do not prove the local bytes equal current official download payloads.
- The journal reference attachment's explicit special requirements take
  precedence over general standard defaults.
- The GB/T PDF remains a user-provided copy; provenance and content extraction
  are not upgraded.
- Published articles generate only `EXAMPLE_ONLY` and
  `VISUAL_REFERENCE_ONLY` observations.

## 10. Conflicts

| Group | Issue | Proposed handling | Resolution status |
|---|---|---|---|
| `CG-TITLE-LENGTH` | Both sources give 20; web wording is general and format attachment wording is strict | retain conflict record and use 20 as safe project ceiling | `PAPER_PROJECT_AI_DECISION_REQUIRED` |
| `CG-FIG-TEXT-SIZE` | general format says six-size; figure attachment specifies Visio 8 pt and other figures six-size-equivalent | apply type-specific value only after style/visual confirmation | `PENDING_STEP3_STYLE_ANALYSIS` |
| `CG-FIG-EXAMPLE-NUMBER` | map example prose says figure 11 but extracted caption says figure 9 | explicit continuous-numbering rule overrides inconsistent example | `RESOLVED_BY_AUTHORITY` |

`CG-GBT-SOURCE-CHAIN` is a provenance/extraction gap rather than a conflicting
numeric value. It requires an accessible authoritative text or explicit later
authorization; current Step 2 does not resolve it.

## 11. Items Deferred to Step 3

- page size, margins, columns, header/footer, body spacing, indentation, and
  Word style inheritance;
- exact abstract, heading, body, figure-caption, table-caption, and reference
  style realization;
- lost equation objects, numbering position, equation font, and long-formula
  layout;
- drawing-object/editability inspection and Visio 8 pt versus six-size mapping;
- body punctuation/numeral details and figure-legend/bilingual-caption status;
- table alignment, padding, auxiliary rules, continuation, and note layout;
- the inconsistent map-example number;
- controlled-conversion fidelity and Windows visual comparison.

## 12. Items Deferred to POC

- Markdown/Pandoc production of two Word copies;
- MathType object creation or conversion feasibility;
- sequential citation and each reference-type rendering through CSL;
- automatic figure/table numbering and first-callout placement;
- deterministic OOXML checks/fixes for table borders and figure extents.

No POC artifact was generated in Step 2.

## 13. Items Requiring Windows Manual Validation

- Word style/paragraph measurements and no-wrap heading behavior;
- MathType object type, editability, typography, numbering, and display;
- Visio/Origin object editability and figure labels;
- final figure/table placement and caption appearance;
- font substitution and mixed Chinese/Latin runs;
- author/review copy opening, pagination, and print preview;
- anonymous-copy content plus Document Inspector checks for properties,
  comments, tracked changes, hidden data, funding, acknowledgements, and
  contacts.

## 14. Files Created

Only these Git deliverables were created:

1. `docs/paper/phase2_5/PAPER_PHASE2_5_JOURNAL_FORMAT_SPEC_v1.0.md`
2. `docs/paper/phase2_5/PAPER_PHASE2_5_FORMAT_RULE_CROSSWALK_v1.0.csv`
3. `docs/paper/phase2_5/PAPER_PHASE2_5_FORMAT_CHECKLIST_v1.0.md`
4. `docs/paper/phase2_5/PAPER_PHASE2_5_SPEC_EXTRACTION_REPORT_v1.0.md`

Text, logs, metadata, and rendered visual samples are external derivatives and
are not Git inputs. No `reference.docx`, manuscript chapter, `references.bib`,
CSL file, POC DOCX, or formal figure/table was created.

## 15. Validation

- Required-file and crosswalk schema validation: `PHASE2_5_STEP2_STRUCTURE_PASS`.
- Rule rows: 121; allowed levels only; unique rule IDs.
- Rule-count and category-count totals: consistent at 121.
- Checklist current status values: allowed values only; no `PASS` status.
- `git diff --check`: pass.
- Change scope versus starting HEAD: exactly the four authorized deliverables.
- Final worktree/index after commit: clean.

## 16. Step 3 Readiness

`READY_WITH_PENDING_SPEC_ITEMS`

The DOC text is sufficient to enter controlled conversion and style analysis.
Pending GB/T content, attachment payload provenance, and explicitly deferred
values remain visible and do not block Step 3, because Step 3 does not require
inventing or silently resolving them.

## 17. Next Executor

`PAPER_PROJECT_AI`
