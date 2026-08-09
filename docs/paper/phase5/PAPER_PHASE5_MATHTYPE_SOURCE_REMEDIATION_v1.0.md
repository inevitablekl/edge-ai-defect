# Paper Phase 5.0A-1 OMML Source Remediation Report

## 1. Scope and Authority

- Starting Phase 4 commit: `a612d60ad30fca8a09b6ed212b5e7f496a7edb57`
- Phase 4 tag: `paper-phase4-complete-v1.0`
- Phase 5.0A-0 verdict: `SOURCE_REPAIR_REQUIRED_BEFORE_MATHTYPE`
- Scientific authority: Phase 4 frozen manuscript source and results
- MathType conversion: not performed

## 2. Root Cause

The authoritative Markdown uses Pandoc's single-backslash TeX delimiters:
`\(...\)` for inline math and `\[...\]` for display math.

Both actual Pandoc invocations in `scripts/paper/build_manuscript_docx.sh`
used `--from=markdown`. In Pandoc 3.10.1, the effective Markdown extension
set reported `-tex_math_single_backslash`. The baseline AST therefore emitted
literal bracket/text nodes and `RawInline(Format "tex")` fragments instead of
`Math InlineMath` / `Math DisplayMath` nodes. DOCX generation consequently
produced ordinary `w:t` text and lost formula structure.

The confirmed minimal repair was to enable the existing parser extension:
`--from=markdown+tex_math_single_backslash`.

## 3. Files Modified

Tracked files modified:

- `scripts/paper/build_manuscript_docx.sh`
- `docs/paper/phase5/PAPER_PHASE5_MATHTYPE_SOURCE_REMEDIATION_v1.0.md`

The authoritative Markdown sections were not changed. Phase 4 governance files
were not changed.

## 4. Remediation

The `--from` option was changed in both Full and Anonymous build paths from:

```text
markdown
```

to:

```text
markdown+tex_math_single_backslash
```

No equation content, notation, punctuation, metric definition, or scientific
result was changed.

## 5. Formula Regression Matrix

| ID | Source | Before | After | Mathematical content preserved | Result |
|---|---|---|---|---|---|
| EQ-001 | `04_experiment.md:49-55`; `f_i=\frac{N}{T_i}` | Plain text `[ f_i=, ]` | `OMML_DISPLAY`; `m:f`, `m:sSub` | Variables, fraction, comma | PASS |
| EQ-002 | `04_experiment.md:57-61`; `\bar f=\frac{1}{5}\sum_{i=1}^{5}f_i` | Plain text with lost bar/fraction/sum | `OMML_DISPLAY`; overbar accent, `m:f`, `m:nary`, indices | All preserved | PASS |
| EQ-003 | `04_experiment.md:63-67`; sample-SD expression | Plain text `[ s_f= . ]` | `OMML_DISPLAY`; `m:rad`, `m:f`, `m:nary`, superscript | Root, fraction, sum, exponent | PASS |
| EQ-004 | `04_experiment.md:71-77`; Type-7 intermediate definitions | Plain text with lost floor/gamma | `OMML_DISPLAY`; structured display text with `⌊h⌋` and `γ` | All three definitions preserved | PASS |
| EQ-005 | `04_experiment.md:79-83`; interpolation expression | Plain text with lost gamma terms | `OMML_DISPLAY`; `m:sSub`, structured gamma terms | Variables, subscripts, interpolation | PASS |
| EQ-006 | `04_experiment.md:55`; `N=1080` | Plain Word text | `OMML_INLINE` | Value and variable preserved | PASS |
| EQ-007 | `04_experiment.md:71`; `n=5400` | Plain Word text | `OMML_INLINE` | Value and variable preserved | PASS |
| EQ-008 | `04_experiment.md:85`; `p=0.95` | Plain Word text | `OMML_INLINE` | Value and variable preserved | PASS |
| EQ-009 | `04_experiment.md:85`; `p=0.99` | Plain Word text | `OMML_INLINE` | Value and variable preserved | PASS |

Associated variable-only inline math in the same contexts (`i`, `T_i`,
`x_{(1)},\ldots,x_{(n)}`, and `p`) is also represented as OMML inline math.

## 6. Full DOCX

- Build: `PASS` — `scripts/paper/build_manuscript_docx.sh --build-full`
- Output: `docs/paper/manuscript/output/draft_full.docx`
- Semantic formula result: 5 display equations and 4 inline formal equations found
- OMML result: 5 `m:oMathPara`, 13 `m:oMath`; no formula-only plain-text output
- Malformed patterns remaining: 0 occurrences
- SHA256: `5945c5b34b2d8d9e8f2e37c0e9b0fef3d723497ada93c8c6e84d8e9fb1a042a4`
- Git state: generated DOCX is ignored and untracked

## 7. Anonymous DOCX

- Build: `PASS` — `scripts/paper/build_manuscript_docx.sh --build-anonymous`
- Output: `docs/paper/manuscript/output/draft_anonymous.docx`
- Semantic formula result: 5 display equations and 4 inline formal equations found
- OMML result: 5 `m:oMathPara`, 13 `m:oMath`; no formula-only plain-text output
- Malformed patterns remaining: 0 occurrences
- SHA256: `87409a77db1a315008a8edd26ff6f633f3d71be7891480eff650f6d01eb40bd3`
- Git state: generated DOCX is ignored and untracked

## 8. Full / Anonymous Formula Parity

- Count/content parity: PASS
- Representation parity: PASS; corresponding formulas use the same OMML types
- Anonymization-induced mathematical divergence: NONE
- Result: `FORMULA_PARITY_PASS`

## 9. Document Validation

- Full build: PASS
- Anonymous build: PASS
- ZIP integrity: PASS for both DOCX files
- XML parsing / repository custom DOCX validators: PASS
- OpenXmlValidator: unavailable in the environment; no replacement claim made
- Journal-format mechanical validation: PASS
- Cross-reference and citation validation: PASS
- Anonymity validation: PASS
- Full/Anonymous scientific body parity: PASS
- LibreOffice mechanical PDF rendering: PASS; both outputs are 9-page A4 PDFs
- Microsoft Word GUI validation: `USER_MANUAL_PENDING`

The existing journal-format validator still prints the historical
`FORMAL_EQUATION_REQUIREMENT=NOT_APPLICABLE_TO_CURRENT_MANUSCRIPT` marker;
that historical validator output was not modified by this remediation and is
not used as the OMML acceptance result.

## 10. Scientific Freeze Check

- Frozen central results changed: NO
- Contribution count: 2
- Metric semantics changed: NO
- Comparison object changed: NO
- Experimental protocol changed: NO
- Citations, figures, tables, and conclusions changed: NO
- Excluded evidence restored: NO
- Scientific impact: NONE

## 11. Phase 5 Governance Asset

- Path: `docs/paper/phase5/PAPER_PHASE5_MATHTYPE_SOURCE_REMEDIATION_v1.0.md`
- Result: CREATED
- Generated DOCX artifacts remain local and ignored.
- MathType OLE conversion has NOT yet been performed.

## 12. Remaining Publication Step

The current DOCX files are ready for the later user-manual Microsoft Word +
MathType conversion step. This executor stopped at valid Pandoc-generated OMML
and did not create or convert MathType objects.
