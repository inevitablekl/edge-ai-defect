# Paper Phase 6.3R1 Reference Metadata Remediation Report v1.0

## 1. Verdict

`PHASE_6_3_REFERENCE_REMEDIATION_IMPLEMENTED`

`FMT-F01 = CLOSED`; `FMT-F02 = CLOSED`; `SCIENTIFIC_NONREGRESSION = PASS`; `LATEST_FULL_DOCX_READY = YES`; `READY_FOR_PHASE_6_3R_RE_REVIEW = YES`.

This is not an `HFUT_SUBMISSION_READY` claim.

## 2. Independent-review findings addressed

- `FMT-F01 / MAJOR`: conference event locations were separated from publisher/publication places for every cited conference record.
- `FMT-F02 / MINOR`: the Lema article was updated from online-first metadata to the official final journal issue metadata.
- No scientific narrative, figure, table, equation, experimental value, or claim boundary was changed.

## 3. Baseline

The mandated pre-edit checks passed on 2026-08-23:

- branch: `main`;
- `HEAD`: `8d73e83f54e4d04522720894079a11301d3bf5a1`;
- `origin/main`: `8d73e83f54e4d04522720894079a11301d3bf5a1`;
- worktree and index: clean;
- baseline reconciliation: exact, with no rollback required.

## 4. Cited conference set

Seven currently cited conference records were audited: ICCVW 2021, MobiSys 2025, IJCAI 2024, RTAS 2020, CVPR 2018, ICML 2020, and PARMA-DITAM 2025. The machine-readable authority is `phase6_3r1_conference_metadata_audit.json`; all seven statuses are `CORRECTED_VERIFIED` or `UNCHANGED_VERIFIED`, with zero `UNRESOLVED` records.

## 5. Per-conference publisher-place verification

| Citation key | Event location | Verified publisher-place : publisher | Result |
|---|---|---|---|
| `stacker_et_al_2021_edge_runtime` | Online / virtual | Piscataway, NJ, USA : IEEE | Corrected |
| `lee_han_kim_2025_presto` | Anaheim, CA, USA | New York, NY, USA : Association for Computing Machinery | Corrected |
| `kim_lee_kim_2024_hyq` | Jeju, Korea | Menlo Park, CA, USA : International Joint Conferences on Artificial Intelligence Organization | Corrected |
| `bateni_et_al_2020_integrated_memory` | Sydney, NSW, Australia | Piscataway, NJ, USA : IEEE | Corrected |
| `jacob_et_al_2018_integer_inference` | Salt Lake City, UT, USA | Piscataway, NJ, USA : IEEE | Corrected |
| `nagel_et_al_2020_adaround` | Virtual / online | Cambridge, MA, USA : PMLR | Corrected |
| `rodriguez_et_al_2025_gpu_memory_allocation` | Barcelona, Spain | Dagstuhl, Germany : Schloss Dagstuhl -- Leibniz-Zentrum für Informatik | Unchanged and verified |

Primary evidence includes the [IEEE Reference Guide](https://journals.ieeeauthorcenter.ieee.org/wp-content/uploads/sites/7/IEEE_Reference_Guide.pdf), ACM's publisher-place/event-location reference model and the paper's [ACM reference format](https://ina.kaist.ac.kr/assets/bibliography/Presto.pdf), the official [IJCAI article/BibTeX](https://www.ijcai.org/proceedings/2024/0474) and [IJCAI bylaws](https://www.ijcai.org/sites/default/files/IJCAI_ByLAWS_Aug_2013.pdf), the official [PMLR record](https://proceedings.mlr.press/v119/nagel20a.html) plus the [ISSN authority record](https://portal.issn.org/resource/ISSN-L/2640-3498), and the official [DROPS record](https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.PARMA-DITAM.2025.1). Per-record URLs are retained in the authority artifact.

## 6. FMT-F01 remediation

`FMT-F01 = CLOSED`.

`references.bib` now uses `address` only for the verified publication place rendered by CSL. Event location is retained separately in the non-rendered audit artifact. A negative validator test confirmed that restoring Anaheim as PRESTO's `address` is rejected.

## 7. Lema current official metadata

The official [Springer article record](https://link.springer.com/article/10.1007/s10845-025-02672-8) and [Volume 37, Issue 7 page](https://link.springer.com/journal/10845/volumes-and-issues/37-7) establish:

- title and four authors: unchanged;
- journal: `Journal of Intelligent Manufacturing`;
- year: `2026`;
- volume/issue: `37(7)`;
- pages: `3001--3018`;
- DOI: `10.1007/s10845-025-02672-8`;
- issue date: July 2026;
- publication status: final issue-assigned journal article.

## 8. FMT-F02 remediation

`FMT-F02 = CLOSED`.

The stable internal key `lema_et_al_2025_surface_defect_benchmark` was preserved. Its rendered type changed from `[J/OL]` to `[J]`; the authoritative DOI remains in BibTeX but is suppressed in the final-journal rendering.

## 9. BibTeX changes

- Corrected six conference publisher-place fields and expanded `ACM` to `Association for Computing Machinery` for PRESTO.
- Verified the unchanged DROPS `Dagstuhl, Germany` publisher place.
- Added Lema volume `37`, issue `7`, pages `3001--3018`, and final year `2026`; retained its DOI.
- Updated the Lema year/note in `literature_matrix.csv` without changing the citation set.

## 10. CSL changes

`CSL_CHANGE_REQUIRED = NO`.

The existing CSL already maps BibTeX `address` to CSL `publisher-place`, renders `publisher-place : publisher`, suppresses DOI for final journals/conferences, and retains governed online behavior. No CSL churn was introduced.

## 11. Validator changes

`validate_final_references.py` now consumes the Phase 6.3R1 authority JSON and checks the exact cited conference set per record for proceedings title, publisher, publisher place, year, and pages. It rejects unresolved metadata and event-location/publisher-place equivalence, validates Lema's exact final Springer fields, classifies every rendered citation for DOI policy, and writes the updated reference audit.

Source validation and the intentional negative semantic test both passed.

## 12. Rendered 22-reference audit

PASS for Full and Anonymous DOCX:

- sequential numbering `[1]` through `[22]`;
- 22 cited references and five intentionally unrendered library records;
- authors, titles, type markers, containers, years, volumes/issues, pages/article numbers, URL behavior, and all seven publisher-place/publisher pairs verified;
- Full and Anonymous bibliography paragraphs identical;
- Lema renders as `Journal of Intelligent Manufacturing，2026，37（7）：3001-3018` with `[J]`.

## 13. DOI policy audit

All 22 rendered records were classified in `citation_final_audit.csv`:

- `FINAL_JOURNAL = 11`: no rendered DOI;
- `FINAL_CONFERENCE = 7`: no rendered DOI;
- `ONLINE_FIRST_JOURNAL = 0` after Lema closure;
- `OFFICIAL_WEB_RESOURCE = 4`: governed URL/access-date behavior retained.

Source DOI metadata was not mechanically deleted.

## 14. `et al.` regression check

PASS. English records with four or more authors render `et al.`; no rendered English record contains `等`. The CSL's Chinese `等` behavior remains available and unchanged.

## 15. Scientific non-regression

PASS using `validate_phase61_nonregression.py`:

- experiment source SHA-256 unchanged: `20f45e645dce7f76c47aa7369e69b580ff64a6ceb8a09b5b67074d173afef5aa`;
- Figure 2/3 authority hashes unchanged: `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` and `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655`;
- three equations, RQ1/RQ2, three identical correctness rows, all frozen metrics, and all claim-boundary/overclaim checks passed;
- manuscript content files changed: `0`.

## 16. Full build

PASS:

```text
bash scripts/paper/build_manuscript_docx.sh --build-full
```

The active citation, reference, Full DOCX, Phase 5.9c integration, and Phase 6.3 format validators passed.

## 17. Anonymous build

PASS:

```text
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

The active citation, reference, anonymity, Full/Anonymous parity, Phase 5.9c integration, and Phase 6.3 format validators passed.

## 18. Full DOCX output path and SHA-256

`LATEST_FULL_DOCX_READY_FOR_USER_WORD_PDF_EXPORT = YES`

- Full: `docs/paper/manuscript/output/draft_full.docx`
- Full SHA-256: `c6b4ec7493d273ccc46f88f206e88bedd14ac8c474672a5e8687801e96bd269a`
- Anonymous: `docs/paper/manuscript/output/draft_anonymous.docx`
- Anonymous SHA-256: `35bfe08d6efd27b54f531531be6296caa94e007d9c341a18c271827730291e33`

## 19. Mechanical render status

Basic no-catastrophic-regression checking passed: LibreOffice produced two nine-page A4 PDFs, and extracted text contains all corrected publisher places plus Lema's final pagination.

- Full mechanical PDF SHA-256: `a642c3a92405bc3c0ef3983d20905d46699bf9ea4c50f01f540adbcaf33c6c9c`;
- Anonymous mechanical PDF SHA-256: `1055cb34c2625bb46c4168ae4fb4a0670a522071ae7751c6f50f1282e5252acc`.

The historical Phase 4.8 format validator was run diagnostically but is not an active gate; it reports stale pre-Phase-6.3 style/section/figure/equation expectations and was not modified because those accepted visual architectures are frozen in this work unit. Mechanical PDFs do not replace Microsoft Word PDF evidence.

## 20. Files changed

- `docs/paper/manuscript/references/references.bib` — bibliographic metadata;
- `docs/paper/manuscript/references/literature_matrix.csv` — Lema final-year source evidence;
- `docs/paper/manuscript/references/citation_final_audit.csv` — regenerated classification/validation audit;
- `docs/paper/phase6_3/phase6_3r1_conference_metadata_audit.json` — per-record authority and venue/place traceability;
- `scripts/paper/validate_final_references.py` — evidence-based validation;
- this report.

Generated DOCX/PDF review outputs remain in the established ignored output tree.

## 21. Git diff scope

The final intended tracked diff is limited to `BIBTEX_METADATA`, `REFERENCE_METADATA_AUDIT`, `REFERENCE_VALIDATOR`, `REFERENCE_VALIDATION_ARTIFACT`, and `PHASE_REPORT`. `CSL_ONLY_IF_REQUIRED` was not triggered. No manuscript narrative, figure, table, equation, experimental code/data, production C++, TensorRT, or Pipeline file is present.

## 22. Deferred submission adaptations

Intentionally open: Visio, Origin, MathType, Microsoft Word Desktop final QA, Anonymous Word QA, Document Inspector, HFUT submission adaptation, and submission-portal validation.

## 23. Commit

Exactly one controlled commit uses:

```text
paper: close Phase 6.3 reference metadata findings
```

This report is part of that commit. The definitive commit SHA is recorded in the final handoff to avoid an amend cycle. No push, tag, merge, rebase, or amend is authorized.

## 24. Exact next action

STOP.

Return the Phase 6.3R1 remediation report and commit to the Main Project AI.

Do not perform any additional manuscript or format modification.

The user will manually push the commit.

After pushing, the user will take the latest Full DOCX from the authoritative output directory, open it in Microsoft Word, and manually export/save it as PDF.

The Full DOCX and the Word-generated PDF will then be supplied together to an independent format-review AI for artifact-level re-review.
