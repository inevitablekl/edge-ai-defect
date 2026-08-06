# Paper Phase 2.5 Journal Format Remediation Result

## 1. Verdict

`FORMAT_REMEDIATION_CANDIDATE_READY_FOR_WORD`

Step 7G closes the five automatic/governance findings selected from Step 7F.
Only the explicitly manual v7 Microsoft Word checks remain.

## 2. Repository State

The gate passed on branch `main` at starting commit
`2b26f219319c27c94582003e9a0ea232f6dcc000`, with a clean worktree/index and
`git diff --check` passing. Evidence for the remediation is the commit
containing this changeset and the files named below.

## 3. v6 Manual Acceptance Record

`PAPER_PHASE2_5_WORD_V6_MANUAL_ACCEPTANCE_v1.0.md` records exactly:

```text
WORD_V6_FIRST_OPEN = PASS
WORD_V6_VISIBLE_LAYOUT = PASS
WORD_V6_SAVE_REOPEN = NOT_TESTED
ANONYMOUS_DOCUMENT_INSPECTOR = NOT_TESTED
```

These results do not accept v7.

## 4. Reference Heading Fix

The v7 postprocessor maps the unique `参考文献` paragraph to
`HFUTReferenceHeading` and removes only its direct `w:numPr`. The inspector
fails with `REFERENCE_HEADING_NUMBERING_DRIFT` if numbering returns. Full and
Anonymous v7 retain body numbering 0/1/1.1/1.1.1, while the visible reference
heading is unnumbered.

## 5. Equation Contract Reconciliation

Canonical, Style Map, and v7 now agree on `HFUTEquation`:

```text
lineRule=atLeast
line=480 twips (24 pt)
spaceBefore=80 twips (4 pt)
spaceAfter=80 twips (4 pt)
authority=VALIDATED_PROJECT_DERIVED_CANDIDATE
```

The inline-formula paragraph remains `atLeast` 360 twips. This is a Microsoft
Word POC-validated project-derived value, not journal-text line spacing and not
a substitute for final MathType processing. The obsolete exact 16 pt and 0/0
contract is not restored.

## 6. Field Update Contract

Canonical and both v7 packages omit `w:updateFields`, retain `PAGE`, and use a
controlled Microsoft Word `Ctrl+A`/`F9` refresh policy. No open-time update
behavior is claimed or reintroduced.

## 7. Table Contract Reconciliation

The governance layer now distinguishes:

- canonical: `HFUTThreeLineTable` may retain `basedOn=TableNormal`;
- Pandoc/postprocessor v7: missing `basedOn` is intentionally absent;
- final v7 layout: direct `tblW=4400`, grid `1400/1400/1600`, verified cell
  margins, top/header/bottom borders 1/0.5/1 pt, no vertical borders, and no
  `tblLayout=fixed`.

Neither TableNormal inheritance nor fixed layout is attributed to journal
text.

## 8. First-Page Footer Biography POC

Full v7 enables `titlePg`, relates a first footer and a default footer, and
places the unique exact synthetic string
`TOOLCHAIN TEST 虚拟作者简介，仅用于首页页脚能力验证` in the first footer using
`HFUTAuthorBiography`; that footer also contains `PAGE`. The default footer
contains `PAGE`. The former body biography is absent.

Anonymous v7 enables the same first-footer mechanism but contains only `PAGE`
there, contains no biography string in any package part, and retains `PAGE` in
the default footer. Synthetic funding remains a body-role test only; no
journal footer-location rule is claimed for funding or acknowledgement.

## 9. Canonical Reference Changes

Current canonical:

```text
docs/paper/manuscript/template/hfut_journal_reference_v1.0.docx
SHA256=416e881fbd6c79963a0b18fc6bcbd490134d12a5b8e88fe5deb91146803ca1a7
custom inspector errors=0
OpenXmlValidator errors=0
```

Two consecutive rebuilds from identical inputs produce the same bytes. The
changed package contract is limited to the approved equation spacing and
removal of the specimen's unused fixed-layout marker.

## 10. POC v7 Outputs

The derived outputs remain outside Git:

| Variant | External path | SHA256 | Pages |
|---|---|---|---:|
| Full v7 | `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step7g_journal_format_remediation_v1/poc/output/poc_full_v7.docx` | `1af8d83fca4fec3ebd051936ab7c9551167fd33a2f4396ebb99383cb057894fc` | 2 |
| Anonymous v7 | `/home/orin/paper-external-inputs/hfut-journal/phase2_5_source_v1/derived/step7g_journal_format_remediation_v1/poc/output/poc_anonymous_v7.docx` | `c29189954e4953039432fdea21bbab6fb70dc32d8412a2e15061531fe94127c6` | 2 |

Both preserve A4, margins, front-matter single column, body two columns with a
425-twip gap, figure, table, sequential citations, and continuous PAGE fields.

## 11. OpenXmlValidator

DocumentFormat.OpenXml 3.5.1 returned zero errors for the canonical, Full v7,
and Anonymous v7 packages. JSON evidence is under the external Step 7G
`validation/` directory.

## 12. Format Regression v1.1

`PAPER_PHASE2_5_JOURNAL_FORMAT_REGRESSION_MATRIX_v1.1.csv` contains 37 unique
rows. JFR-008, JFR-018, JFR-024, JFR-026, and JFR-036 pass with `NO_DRIFT`.
The audit verdict is `FORMAT_REMEDIATION_CANDIDATE_READY_FOR_WORD`; it has no
automatic blocking audit IDs. JFR-031, JFR-033, and JFR-034 remain the allowed
Windows-manual pending rows.

## 13. Governance Drift Closure

`PAPER_PHASE2_5_GOVERNANCE_DRIFT_REGISTER_v1.1.csv` preserves GDR-001 through
GDR-004 and marks each `CLOSED` with file and commit-range evidence. The v1.0
matrix, report, and drift register remain unchanged as historical Step 7F
evidence.

## 14. Automated Validation

Passed: deterministic canonical rebuild, all three OpenXmlValidator runs,
canonical and v7 custom inspectors, v1.1 regression audit, reference-heading
guard, body numbering, footer identity boundary, PAGE fields, approved
equation spacing, table contract, section/column geometry, two-page previews,
structure-only manuscript source validation, empty formal bibliography,
protected Phase 0/1/2 boundary, and `git diff --check`.

No real manuscript content, experiment result, MathType/Visio/Origin result,
or publication claim was created.

## 15. Windows Final Acceptance Required

The following remain deliberately unaccepted:

```text
WINDOWS_V7_FIRST_OPEN_REQUIRED
WINDOWS_V7_SAVE_REOPEN_REQUIRED
ANONYMOUS_DOCUMENT_INSPECTOR_REQUIRED
```

These are manual acceptance gates, not automatic format regressions.

## 16. Phase 2.5 Freeze Readiness

`READY_FOR_FINAL_WINDOWS_ACCEPTANCE`

## 17. Next Executor

`USER_MANUAL`
