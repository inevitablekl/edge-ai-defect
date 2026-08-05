# Paper Phase 2.5 Markdown-to-DOCX POC Plan v1.0

## 1. Status and boundary

This plan governs Paper Phase 2.5 Step 6 only. Its status is
`TOOLCHAIN_POC_ONLY / SYNTHETIC_CONTENT / NOT_PAPER_CONTENT /
NOT_FORMAL_REFERENCE_DATA / NOT_SUBMISSION_MANUSCRIPT /
PHASE_3_NOT_AUTHORIZED`.

The POC validates a Markdown-to-DOCX authoring path without writing formal
manuscript prose, using formal experiment values, adding real literature, or
introducing real identity data. The canonical reference DOCX and all existing
Phase 0, Phase 1, Phase 2, and Phase 2.5 authority files remain read-only.

## 2. Inputs

- Pandoc executable: `/home/orin/.local/bin/pandoc`.
- Canonical format candidate:
  `docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx`.
- CSL source: Zotero official Style Repository candidate for China National
  Standard GB/T 7714-2025 numeric, Chinese locale.
- Source content: short synthetic bilingual front matter, headings, formulas,
  one deterministic figure, one synthetic table, and five synthetic reference
  types generated outside Git.
- Full and anonymous POC metadata profiles generated outside Git.

## 3. Isolation design

All generated sources, CSL bytes, media, DOCX files, PDFs, logs, extracted
metadata, inspection JSON, and temporary files are placed below:

```text
/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step6_markdown_docx_poc_v1
```

The external tree contains `source/`, `csl/`, `figures/`, `output/`,
`rendered/`, `inspection/`, `logs/`, `metadata/`, and `temporary/`. No POC
source or binary output is copied into the formal manuscript source tree.

## 4. Build design

The runner shall:

1. verify the canonical reference DOCX SHA256;
2. generate only visibly synthetic POC inputs;
3. download the CSL without changing its bytes and record its provenance;
4. parse and validate CSL XML, title, numeric category, and metadata;
5. invoke Pandoc with standalone Markdown input, reference DOCX, citeproc,
   POC BibTeX, POC CSL, resource path, metadata profile, and Lua filter;
6. record the exact command, timestamps, duration, return code, stdout, and
   stderr separately for full and anonymous builds;
7. apply deterministic OOXML corrections for semantic sections, heading
   numbering, image display fallback, three-line table borders/width, formula
   paragraph style, and generic document properties;
8. inspect both packages and render non-authoritative LibreOffice previews.

## 5. Semantic style strategy

The Lua filter maps front matter and headings to the named `HFUT*` styles.
The inspector verifies paragraph-level style use in `word/document.xml`, not
only style definitions in `word/styles.xml`. Anonymous output intentionally
does not use identity-specific styles.

Pandoc-native tables use the compatibility `Table` style and no direct
three-line borders. Post-processing therefore applies `HFUTThreeLineTable`,
`HFUTTableContent`, and 1/0.5/1 pt direct borders. The first section remains
single-column; a continuous semantic boundary terminates it and the final
body section is set to two columns with 425-twip spacing.

## 6. Test classifications

- Heading numbering: validate visible output separately from paragraph
  `numPr`, `numId`, and `abstractNum` relationships.
- Formula representation: distinguish OMML from images; do not infer MathType
  acceptance from OMML.
- Formula, figure, and table numbering/cross-references: classify static text
  separately from Word fields.
- Figure representation: retain the downloaded/generated SVG package member
  and record any raster display fallback explicitly.
- Anonymous copy: scan document, headers, footers, comments, notes, properties,
  relationships, embedded files, file names, and build records, while reserving
  Microsoft Word Document Inspector acceptance for Step 7.

## 7. Acceptance criteria

The automated run passes only if both DOCX files are valid ZIP packages; the
required OOXML parts, A4 geometry, margins, 1/2-column sections, named-style
use, OMML, figure media, table structure/borders, PAGE field, numeric citations,
five references, numbering relationships, and identity boundaries pass. Both
LibreOffice previews must be two to four pages and must not be treated as
Microsoft Word evidence.

Tool or journal-specific gaps are reported rather than converted into false
passes. MathType, Word field refresh, Word Document Inspector, Visio, Origin,
and HFUT-specific CSL edge cases remain explicit manual or future work.
