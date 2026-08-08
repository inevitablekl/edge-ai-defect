# Paper Phase 4.7 Citation, Bibliography and Cross-Reference Report v1.0

## 1. Verdict

`PHASE_4_7_CITATION_BIBLIOGRAPHY_CROSS_REFERENCE_FINALIZATION_COMPLETE_WITH_DECLARED_PUBLICATION_LIMITATIONS`

The manuscript source now has 15 admitted bibliography records, 14 real cited
records in sequential first-occurrence order, zero unresolved citation keys,
and one deliberately retained unused admitted-library record. The Full and
Anonymous DOCX builds use the same final BibTeX and local CSL derivative.

## 2. Evidence and scope

The audit used the admitted bibliography and literature matrix, the manuscript
section sources, Phase 2.5 journal/POC records, the Phase 3 admission record,
and the verified local external source package. No source was added, no
scientific claim was rewritten, and no frozen experiment evidence was changed.

The verified local materials supplied the missing final fields for Song, Shao,
Weiss, Shin, Liu, and the CUDA manuals; the official local webpage captures
supplied the retained official URLs/access dates for Ultralytics and JetPack.

## 3. Citation inventory

| Measure | Result |
| --- | ---: |
| Bibliography input entries | 15 |
| Distinct cited entries | 14 |
| Uncited entries | 1 |
| Unresolved citation keys | 0 |
| Abstract/title citation keys | 0 |
| Manual numeric markers in Markdown | 0 |
| Rendered Full bibliography entries | 14 |
| Rendered Anonymous bibliography entries | 14 |

The first-occurrence sequence is Song, Shao, Lema, Ultralytics, Weiss, Shin,
Tang, Liu, Kim, TensorRT 10.3, CUDA Best Practices, Reddi 2019, JetPack 6.2.2,
and CUDA Programming Guide. Entries 1–12 first occur in
`01_introduction.md`; entries 13–14 first occur in
`02_problem_definition.md`.

`docs/paper/manuscript/references/citation_final_audit.csv` is the row-level,
15-entry audit record. Every cited entry is `PASS` or `REMEDIATED`; there are
no `REFERENCE_METADATA_INPUT_REQUIRED` rows.

## 4. Uncited entry disposition

`reddi_et_al_2022_mlperf_mobile` (A15, supplementary L6, no formal P ID) is
retained as `PRE_DRAFT_ADMITTED_SOURCE_RETAINED`. It is not cited and is not
rendered. This implements the Phase 3 admission rule that a pre-draft admitted
but unused library entry is not an error; it was not cited merely to increase
the reference count.

## 5. Reference metadata audit

| Key(s) | Result | Disposition |
| --- | --- | --- |
| Song; Shao | REMEDIATED | Added locally verified final volume/pages. |
| Lema | PASS | Retained online-first state; final volume/issue/pages were not invented. |
| Ultralytics; JetPack | REMEDIATED | Official webpage URL and local-capture access date recorded. |
| Weiss; Shin; Liu | REMEDIATED | Added locally verified article-number/pagination fields. |
| Tang; Kim | PASS | Existing admitted final/conference metadata confirmed locally. |
| CUDA Programming; CUDA Best Practices | PASS | Local official PDFs confirm 2024 Release 12.6 manual metadata. |
| TensorRT 10.3 | PASS | Phase 3 approved no-year limitation retained; no year was invented. |
| Reddi 2019 | REMEDIATED | Explicit preprint marker and canonical arXiv URL permit `[PP/OL]`. |
| Reddi 2022 Mobile | PASS | Retained unused A15 library record; not rendered. |

All DOI values are syntactically checked, and all recorded URLs use `https`.

## 6. CSL decision

The upstream official Zotero GB/T 7714—2025 numeric candidate was not used
unchanged because it rendered final DOI-bearing journal and conference records
as `[J/OL]` and `[C/OL]` solely due to the DOI. That conflicts with the HFUT
type patterns for final articles and conference papers.

The adopted local derivative is
`docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl`. Its final
SHA256 is:

```text
207ef94434816d601281b4fd940c92428e3e21b9dc97abe4204359d0e7ce3818
```

The exact upstream source, SHA256, CC BY-SA 3.0 license, demonstrated
incompatibility, and limited derivative behavior are recorded in
`PAPER_PHASE4_CSL_DECISION_v1.0.md`. The Phase 2.5 synthetic `[Z]` versus
`[S]` observation remains unmodified because no actual standard is cited.

## 7. Rendered bibliography validation

The rendered marker order is:

```text
1 J; 2 J; 3 J/OL; 4 EB/OL; 5 J; 6 J; 7 J; 8 J;
9 C; 10 M; 11 M; 12 PP/OL; 13 EB/OL; 14 M.
```

The Full and Anonymous bibliography paragraphs are identical. The validator
also confirms that neither document contains an unrendered `@citation_key` and
that no `[Z]` marker appears.

The OOXML style check confirms `HFUTReferenceEntry` and `Bibliography` specify
Songti for East Asian text, Times New Roman for Latin text, six-size (7.5 pt),
and exact 14 pt line spacing. This is a structural DOCX validation, not a
claim of Windows Word visual inspection.

## 8. Figure and table cross-reference validation

`STATIC_CROSS_REFERENCE_VALIDATED`

The source and both DOCX builds contain exactly the accepted captions for F1,
F2, F3, T1, and T2. Each has a preceding body callout; figures are sequential
F1–F3 and tables are sequential T1–T2. No stale Figure 4+/Table 3+ prototype
labels were found. The cross-references are static text rather than dynamic
Word REF/SEQ fields.

## 9. Full and Anonymous rebuild

Both builds were rerun from the final BibTeX and CSL inputs.

| Build | Output | SHA256 |
| --- | --- | --- |
| Full | `docs/paper/manuscript/output/draft_full.docx` | `f874cc5e39468f1cca312f02bf541a132f3ebb7f19dcc52efc7d3ba7cc51dd94` |
| Anonymous | `docs/paper/manuscript/output/draft_anonymous.docx` | `8e4bd9e888764d52913ab71d921b44a241eb024c655de34587c8d92035eae73a` |

The Phase 4.6 identity scan, scientific-body parity check, figure/table
counts, and reference-count checks remained `PASS` on the anonymous rebuild.
Generated DOCX files remain outside Git.

## 10. Automatic validation

The following all passed:

```text
scripts/paper/build_manuscript_docx.sh --build-full
scripts/paper/build_manuscript_docx.sh --build-anonymous
scripts/paper/build_manuscript_docx.sh --check
python3 scripts/paper/validate_final_references.py \
  --docx docs/paper/manuscript/output/draft_anonymous.docx \
  --compare-full docs/paper/manuscript/output/draft_full.docx --write-audit
bash -n scripts/paper/build_manuscript_docx.sh
python3 -m py_compile scripts/paper/validate_citations.py \
  scripts/paper/validate_final_references.py
git diff --check
```

## 11. Scientific freeze check

No manuscript section prose, frozen results, figures, tables, front matter,
corresponding-author information, or experiment artifacts changed in this
phase. The changes are confined to bibliography metadata, CSL/build/validation
tooling, governance reports, and the generated audit CSV.

## 12. Files changed

- `.gitignore`
- `docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl`
- `docs/paper/manuscript/references/references.bib`
- `docs/paper/manuscript/references/citation_final_audit.csv`
- `scripts/paper/build_manuscript_docx.sh`
- `scripts/paper/validate_final_references.py`
- `docs/paper/phase4/PAPER_PHASE4_CSL_DECISION_v1.0.md`
- this report

## 13. Git result

The source/governance/tooling change set is ready for the authorized commit
`docs(paper): finalize citations and references`. No generated DOCX/PDF,
external PDFs, private metadata, tags, branches, or remote operations are part
of the change set.

## 14. Open publication limitations

- A Windows Word visual pass is still required for final publication typography
  and page-level layout acceptance.
- TensorRT 10.3 Release Notes has no approved publication year in the admitted
  source metadata.
- The JetPack official webpage has no admitted publication year; it is recorded
  with its verified access date.
- The Lema article remains online-first in the verified local source; its final
  volume, issue, and pages must not be supplied without new verified evidence.
- Static figure/table cross-references are validated; dynamic Word REF/SEQ
  field behavior is outside this phase.

## 15. Recommendation

`READY_FOR_GOVERNED_PUBLICATION_HANDOFF`

Use the rebuilt Full DOCX for author review and the rebuilt Anonymous DOCX for
review submission, subject to the declared Windows Word visual review and the
existing Phase 4.6 publication limitations.
