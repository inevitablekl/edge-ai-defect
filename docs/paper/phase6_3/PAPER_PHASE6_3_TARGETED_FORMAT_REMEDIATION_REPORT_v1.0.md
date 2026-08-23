# Paper Phase 6.3 Targeted HFUT Format Remediation Report v1.0

## 1. Verdict

`PHASE_6_3_IMPLEMENTED_AWAITING_FORMAT_REVIEW`

The authorized automated review-state remediation is complete. This verdict is not a submission-readiness claim.

## 2. Phase 6.2 gate evidence

The user-supplied current-authority addendum records:

- `PHASE_6_1_CONTENT_ARCHITECTURE = ACCEPTED`;
- `PHASE_6_2_INDEPENDENT_REVIEW = SATISFIED`;
- `IR-F01 = CLOSED` and `IR-F02 = CLOSED`;
- `SCIENTIFIC_NONREGRESSION = PASS`;
- `CONTENT_RECONSTRUCTION_GATE = CLOSED`;
- `PHASE_6_3_TARGETED_FORMAT_REMEDIATION = AUTHORIZED`.

No academic narrative reconstruction was performed. The only prose-level change is the mechanical equation-reference closure `式中` -> `式（1）中`; the Table 1 quantity/unit presentation was mechanically normalized without changing values.

## 3. Repository baseline

The required pre-edit checks passed on 2026-08-23:

- repository: `inevitablekl/edge-ai-defect`;
- branch: `main`;
- `HEAD`: `7ca5ca2ef4b3e3d57bb91ff34b09a3e04a1fb2ae`;
- `origin/main`: `7ca5ca2ef4b3e3d57bb91ff34b09a3e04a1fb2ae`;
- direct parent stated by the addendum: `729dc62ca47e53f144b5882d6a28749a10906dcb`;
- baseline status, worktree diff, and cached diff: empty.

## 4. Changed files

The intended scope is classified as follows.

- `FIGURE_SOURCE_OR_LAYOUT`: `docs/paper/phase5_9/visual/scripts/generate_phase59c_figure1.py`; `docs/paper/phase5_6/visual/scripts/generate_phase56d_production_statistical.py`; `scripts/paper/full_manuscript_filter.lua`.
- `TABLE_FORMAT_SOURCE`: `docs/paper/manuscript/sections/02_problem_definition.md`; `scripts/paper/postprocess_publication_tables.py`.
- `EQUATION_NUMBERING`: `docs/paper/manuscript/equations/equation_manifest.csv`; `scripts/paper/postprocess_full_manuscript_docx.py`.
- `INLINE_MATH_FORMAT`: `scripts/paper/postprocess_full_manuscript_docx.py`; `scripts/paper/postprocess_publication_tables.py`.
- `BIBTEX_METADATA`: `docs/paper/manuscript/references/references.bib`.
- `CSL`: `docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl`.
- `DOCX_STYLE_OR_OOXML`: `scripts/paper/postprocess_full_manuscript_docx.py`; `scripts/paper/postprocess_publication_tables.py`.
- `FIGURE_MANIFEST`: `docs/paper/manuscript/figures/figure_manifest.csv`.
- `VALIDATOR`: `scripts/paper/validate_anonymous_manuscript_docx.py`; `scripts/paper/validate_final_references.py`; `scripts/paper/validate_full_manuscript_docx.py`; `scripts/paper/validate_phase59c_integration.py`; `scripts/paper/validate_phase61_nonregression.py`; `scripts/paper/validate_phase63_format.py`.
- `BUILD_CONFIG`: `scripts/paper/build_manuscript_docx.sh`.
- `GENERATED_ARTIFACT`: the tracked SVG/PDF/PNG Figure 1 assets and tracked SVG/PDF/PNG Figure 2/3 assets under the existing Phase 5.9 and Phase 5.6 production directories; `docs/paper/phase6_3/phase6_3_scientific_nonregression.json`.
- `PHASE_REPORT`: this report.

Generated DOCX/PDF review builds remain under the existing ignored `docs/paper/manuscript/output/` production-output tree and are not committed.

## 5. Figure 1 remediation status

PASS for the automated review state.

- Scientific design and semantic tokens `P0/P2/P3`, `V0/V2R/V3R`, `R/F/M/E`, host/device, boundary, and intervention hierarchy are preserved.
- The prohibited floating fixed-object sentence remains absent.
- DOCX width is `5,759,999` EMU (nominal 16 cm full width).
- A deterministic next-page one-column section places Figure 1 at the top of page 4; the two-column body resumes below its caption.
- Caption is immediately below the figure; no body text appears above it on the same page; rendered inspection found no clipping.
- Chinese uses the repository-authorized Songti-compatible review fallback, Latin/digits use the Times-compatible review fallback, and mathematical variables use scoped italic mathematical glyphs while prose and representation names remain upright.
- Review PNG is 1893 x 937 at approximately 300 dpi.

## 6. Figure 2/3 remediation status

PASS for the automated review state.

- Both figures use single-column width (`2,699,999` EMU, nominal 7.5 cm).
- Figure 2 is a three-panel vertical layout and Figure 3 a two-panel vertical layout; `(a)/(b)/(c)` labels are below panels.
- Internal review typography is 7.5 pt with Times/Songti-compatible Linux fallbacks; axes use inward ticks and upright units.
- Rendered captions are below the main figures and the figures remain legible in the right column on pages 6 and 7.
- Figure 2/3 data authorities are unchanged: run CSV SHA-256 `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31`; summary JSON SHA-256 `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655`.

## 7. Table remediation

PASS.

- All three captions remain above native editable Word tables.
- The existing three-line table behavior is preserved.
- Table 1 now carries the quantity/unit form `名义输入复制载荷 B(P)/(MB/frame)` in the header and numeric cells contain only `4.9152`, `0.1200`, and `0.1200`; no measured value changed.
- Table inline OMML runs are coordinated to six-size (7.5 pt) table text.
- Table 3 uses a keep-with-next row chain and rendered intact at the top of page 6.

## 8. Equation-number closure

PASS.

- The manifest remains the number authority: `E1 -> 1`, `E2 -> 2`, `E3 -> 3`.
- The DOCX postprocessor deterministically consumes the manifest and renders one inline OMML object plus a right-aligned visible number in each `HFUTEquation` paragraph.
- Full and Anonymous DOCX contain three visible equation numbers: `（1）`, `（2）`, `（3）`.
- Body references `式（1）`, `式（2）`, and `式（3）` are present and consistent.
- Mathematical expressions are unchanged.

## 9. Inline math sizing

PASS at automated and mechanical-render level.

- Display OMML runs receive Times New Roman/Songti-compatible 10.5 pt formatting.
- Table OMML runs receive 7.5 pt formatting.
- Existing `HFUTEquation` spacing remains `320` twips, `atLeast`, before `0`, after `0`.
- Rendered pages 3 and 4 show no equation clipping or abnormal line expansion.

## 10. Reference `et al./等` result

PASS.

- All 27 admitted BibTeX records now carry explicit `language = {en}` metadata.
- English records with four or more authors render `et al.`.
- No English rendered reference contains `等`.
- The CSL retains the Chinese `等` term for a future Chinese-language record.

## 11. DOI-policy result

PASS.

- DOI is suppressed for final journal and conference records.
- DOI remains rendered for the admitted online-first journal record.
- Official online resources retain their governed URL/access-date behavior.

## 12. Conference metadata result

PASS.

Every cited conference record is source-complete for conference title, publisher, place, year, and pages. Phase 6.3 added verified place/publisher fields for ICCVW 2021 (Online/IEEE), MobiSys 2025 (Anaheim/ACM), IJCAI 2024 (Jeju/IJCAI Organization), RTAS 2020 (Sydney/IEEE), CVPR 2018 (Salt Lake City/IEEE), ICML 2020 (Online/PMLR), and PARMA-DITAM 2025 (Dagstuhl/Schloss Dagstuhl). The rendered-field validator checks every required source field against each produced entry.

## 13. Reference alignment

PASS.

`HFUTReferenceEntry` and Pandoc `Bibliography` styles are both Songti + Times New Roman, 7.5 pt, exact 14 pt line spacing, and justified. Twenty-two cited references render sequentially; the five admitted but uncited library records remain unrendered by design.

## 14. Figure-lifecycle result

PASS.

The figure manifest now distinguishes:

- scientific master: deterministic generator/specification or frozen statistical data;
- review payload: current PNG inserted in automated DOCX;
- submission object: `VISIO:TBD_NOT_CREATED` for Figure 1 and `ORIGIN:TBD_NOT_CREATED` for Figures 2/3;
- scientific status: `FROZEN`;
- submission status: `OPEN`.

No PNG/SVG review artifact is labeled as the final editable HFUT submission object.

## 15. Validator-semantics result

PASS.

The new Phase 6.3 validator distinguishes `MANUSCRIPT_BUILD_PASS` from the required `HFUT_SUBMISSION_NOT_READY` lifecycle result. It checks A4/two-column structure, figure width and caption adjacency, Figure 1 section boundaries, native-table placement, Table 1 unit form, Table 3 pagination chain, manifest-driven visible equation numbers, body equation references, and justified reference styles. Full/Anonymous parity is checked for figure layout and equation numbering.

## 16. Full build

PASS using the authoritative command:

```text
bash scripts/paper/build_manuscript_docx.sh --build-full
```

Output: `docs/paper/manuscript/output/draft_full.docx`, SHA-256 `3b09ec38606b96f5c8b071f149f040dc97fde1fcd6a820ee02ed7b44ea34a3a7`.

## 17. Anonymous build

PASS using the authoritative command:

```text
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Output: `docs/paper/manuscript/output/draft_anonymous.docx`, SHA-256 `79b5b2cdeba7dc9dcfbecf2fc057d75caca9ab3fcf2ac3c5dffa01d58f9c3bfe`. Automated identity scan and scientific-body parity both pass. This is not a Word Document Inspector claim.

## 18. PDF/render inspection

PASS for mechanical LibreOffice review.

- Full PDF: 9 A4 pages, 709,982 bytes, SHA-256 `20026b4bf311e774cf64d6c38d0902a18e22378d48ea3ecb03d6aaeddaa62483`.
- Anonymous PDF: 9 A4 pages, 697,951 bytes, SHA-256 `bc06143abc32b3c851f10464ee73b742344099dff1dde1d7cf45cbd8abcdbec8`.
- Figure 1 is page-top/full-width on page 4, with its caption below and no clipping.
- Figures 2 and 3 are readable one-column figures on pages 6 and 7; panel labels are below panels.
- Table 3 is unsplit; displayed equations and numbers are visible; no observed image or table overflow.
- References render across pages 8-9 with justified paragraph styling.

## 19. Scientific non-regression

PASS.

`docs/paper/phase6_3/phase6_3_scientific_nonregression.json` confirms:

- frozen experiment source SHA-256 `20f45e645dce7f76c47aa7369e69b580ff64a6ceb8a09b5b67074d173afef5aa`;
- frozen Figure 2/3 source-data hashes unchanged;
- three equations, RQ1/RQ2, and three correctness rows preserved;
- both DOCX builds contain three figures, three native tables, and three display equations;
- all 18 watched overclaim terms remain legitimate negations or boundary statements;
- zero non-regression errors.

Title, research object, path definitions, values, results, claims, limitations, and bibliography set are unchanged. Bibliography differences are metadata/format corrections only.

## 20. Deferred Visio/Origin/MathType status

Intentionally open for the later submission-production phase:

- Figure 1 Visio editable submission object: OPEN;
- Figure 2/3 Origin editable submission objects: OPEN;
- MathType conversion: `DEFERRED_FINAL_MATHTYPE`;
- final Microsoft Word Desktop QA: OPEN;
- final Anonymous Word Desktop QA and Document Inspector: OPEN;
- final HFUT submission adaptation and portal validation: OPEN.

## 21. Open blockers

No blocker remains for the Phase 6.3 automated review-state objective. The deferred items in section 20 block any future `HFUT_SUBMISSION_READY` claim and require explicit later authorization and manual tooling.

## 22. Git diff summary

The final intended changeset contains 29 files with 1,481 insertions and 558 deletions (binary deltas reported separately by Git). All changes map to the authorized classifications in section 4; no unrelated source, experimental result, production C++, pipeline, TensorRT implementation, or project architecture file is included.

## 23. Commit

Authorized commit message:

```text
paper: apply Phase 6.3 HFUT format remediation
```

This report is part of that commit. The definitive commit SHA is recorded in the final handoff rather than self-embedded here, which avoids a prohibited amend cycle.
