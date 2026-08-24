# Paper Phase 6.3R10 Candidate-B Production and Figure-1 Callout Report v1.0

## 1. Verdict

`PHASE_6_3_CANDIDATE_B_AND_F1_CALLOUT_IMPLEMENTED`.

Candidate B is production-selected, the Figure 3 production anchor uses one
related body-paragraph offset, and the authorized Section 1.2 Figure 1 overview
callout is present in both production DOCX artifacts. Structural and scientific
gates pass. Final visual closure remains pending review of the exact Full DOCX
in Microsoft Word 2019.

## 2. Baseline

- Branch: `main`.
- Initial `HEAD`: `f46daffcd0c32727ffd2e52a4fdee98f810b3c47`.
- Initial `origin/main`: `f46daffcd0c32727ffd2e52a4fdee98f810b3c47`.
- Initial commit subject: `paper: archive Figure 3 Word anchor candidates`.
- Initial worktree and index: clean.
- Baseline reconciliation: `PASS`; no rollback was required.

## 3. Independent-review finding

The authoritative independent Word review accepted Candidate B and all other
format/scientific areas. The only open manuscript-format item was `FMT-F01 /
HFUT-FIG-009`: the first visible textual Figure 1 callout occurred after the
page-top figure. No other closed area was reopened.

## 4. Candidate-B production promotion

The normal production postprocessor now defines
`FIGURE3_PRODUCTION_RELATED_BODY_OFFSET = 1`. Placement is calculated from the
first Figure 3 callout, counts the next nonempty `HFUTBody` paragraph, and stops
at the next `HFUTHeading*` paragraph. It does not search for or name Section
4.5. Production builds no longer require the archived candidate generator.

This is a manuscript-specific production decision. It is explicitly not an
HFUT rule or a universal Figure 3 placement rule.

## 5. Figure-3 production anchor verification

Direct inspection of each generated `word/document.xml` established:

| Artifact | First Figure 3 callout child | Figure 3 float child | Intervening nonempty `HFUTBody` | Intervening heading |
|---|---:|---:|---:|---:|
| Full | 85 | 87 | 1 | 0 |
| Anonymous | 79 | 81 | 1 | 0 |

The intervening paragraph is the next related Section 4.4 discussion
paragraph. The Figure 3 float subtree SHA-256 remains
`23efec28f6b065a886861520c306c4eab18291fd074cb44cd38ebe669593cace`,
and its PNG payload remains
`0205e472b2017f202c2c3fde071c4396f93e0aa5789a7dd19095f103b697abc8`.
The caption, drawing, dimensions, relationship, and exact positioning metadata
are unchanged: `vertAnchor=text`, `horzAnchor=text`, `tblpXSpec=center`, and
`tblpY=1`, with all text distances zero.

`PROJECT_MANUSCRIPT_PRODUCTION_LOCK = PASS`.

## 6. Figure-1 FMT-F01 remediation

Exactly one short overview callout was added to the opening Section 1.2
paragraph after the four structural relations and before the formal path
descriptor. The existing detailed Section 1.3 callout beginning `如图1所示`
was retained.

`FMT_F01_IMPLEMENTATION = COMPLETE`.

## 7. Exact authorized prose delta

Added exactly once in
`docs/paper/manuscript/sections/02_problem_definition.md`:

```text
三条路径的总体结构及层级受控比较关系见图1。
```

No other manuscript prose changed.

## 8. Figure-1 structural order

In Full `word/document.xml`, the new overview callout occurs at body child 28,
the retained detailed callout at child 39, and the Figure 1 float at child 40.
In Anonymous, the corresponding positions are 22, 33, and 34. The governed
overview sentence occurs exactly once in each artifact and logically precedes
Figure 1.

`FIGURE1_EARLY_CALLOUT_STRUCTURAL = PASS`.

## 9. Figure-1 visual-order gate

OOXML establishes logical order but cannot prove Microsoft Word pagination.
The automated end state is therefore:

```text
HFUT_FIG009_IMPLEMENTED_PENDING_WORD_REVIEW
FIGURE1_VISUAL_FIRST_CALLOUT_ORDER=PENDING_MICROSOFT_WORD_REVIEW
```

No claim of visual closure is made from OOXML or LibreOffice.

## 10. Figure 1/2/3 non-regression

The production floats were compared with the archived Candidate-A/R7
production artifacts. All three complete float subtree hashes are unchanged:

| Figure | Float subtree SHA-256 | Image payload SHA-256 |
|---|---|---|
| Figure 1 | `e00d7bd5a365a49b62e111755599a3afedebe0c2f605015440d34439ddadc426` | `c562d5a3f1b930177ccacf90cfb467470bca7dd6c2d7597d92b7fe58292537c7` |
| Figure 2 | `d3c2471a5b8bde3ace387558d7b0f07a57863f9becb749b536fad24b79e13d57` | `00130111de0133f868d156bff9810c7e9387ea0a32c2ee000e804f7d2f27cbe1` |
| Figure 3 | `23efec28f6b065a886861520c306c4eab18291fd074cb44cd38ebe669593cace` | `0205e472b2017f202c2c3fde071c4396f93e0aa5789a7dd19095f103b697abc8` |

Figure 1 remains full-width, centered, page-margin-top anchored, caption-below,
non-splitting, and without a forced page break. Figures 2 and 3 retain their
single-column widths and accepted float geometry.

## 11. Table/equation/reference non-regression

- All three native Word table subtrees match the archived production baseline.
- All three display-equation paragraph subtrees match the baseline and visible
  numbering remains `（1）` through `（3）`.
- The 22 rendered references remain sequential and their text SHA-256 remains
  `cc271cc81cc89342ef7652d8a51f81f25c431617d1da6b235faa72cca0c5ccef`.
- `references.bib`, CSL, equation manifest, table source/specification files,
  and scientific table values are unchanged.

`TABLE_EQUATION_REFERENCE_NONREGRESSION = PASS`.

## 12. Scientific non-regression

`validate_phase61_nonregression.py` reports
`PHASE61_SCIENTIFIC_NONREGRESSION=PASS`. The frozen experiment-source hash,
Figure 2/3 data hashes, three equations, RQ1/RQ2, three correctness rows,
experimental values, results, limitations, conclusion boundaries, and all 18
legitimate negation/boundary matches remain accepted.

The only authorized source delta is the Figure 1 overview callout in Section
1.2. `P=(R,F,M,E)`, `B(P)`, `T_E2E(P)`, V0/V2R/V3R semantics, experimental
configuration, and every reported performance/correctness value are unchanged.

`SCIENTIFIC_NONREGRESSION = PASS`.

## 13. Validator changes

`validate_phase63_format.py` now:

- requires exactly one governed early Figure 1 overview callout in the
  authoritative Section 1.2 source and each generated DOCX;
- verifies that callout logically precedes the Figure 1 float;
- reports structural passage separately from pending Microsoft Word review;
- enforces the Figure 3 offset-one state as
  `PROJECT_MANUSCRIPT_PRODUCTION_LOCK`, explicitly not an HFUT requirement;
- compares Full/Anonymous offset and heading-boundary semantics without
  incorrectly requiring identical absolute child positions.

## 14. Full build

Command:

```bash
bash scripts/paper/build_manuscript_docx.sh --build-full
```

Result: `FULL_BUILD = PASS`. Heading numbering, citations, final references,
Full manuscript structure, Phase 5.9C integration, and Phase 6.3 structural
format validation all passed.

## 15. Anonymous build

Command:

```bash
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Result: `ANONYMOUS_BUILD = PASS`. The anonymity scan, bibliography identity,
scientific-body parity, Phase 5.9C integration, and Phase 6.3 structural format
validation all passed.

## 16. Full/Anonymous parity

`FULL_ANONYMOUS_PARITY = PASS`. Figure widths/placement, Figure 1 callout
presence, Figure 3 production offset, equations, tables, references, scientific
body, and governed lexical behavior are consistent. Absolute child positions
differ only by the six Full-only front-matter paragraphs removed by the
anonymous production path.

## 17. Full DOCX path + SHA256

```text
docs/paper/manuscript/output/draft_full.docx
ab8d3d4132549b00be468fd615230fdd4814187f078e2b73498e4ce8a0c614c3
```

## 18. Anonymous DOCX path + SHA256

```text
docs/paper/manuscript/output/draft_anonymous.docx
b18836acbf35f05d9fa866aaa57a5ff508ced63779ed77398eeaed207beda648
```

## 19. Mechanical-render observation

LibreOffice 7.3 mechanically rendered the Full artifact to an eight-page A4
PDF for gross regression only. The render contains all three figures, three
tables, three numbered equations, and the references; no blank page, missing
object, clipping, or gross overlap was observed. Mechanical text extraction
places the new Figure 1 callout on page 2 and the Figure 1 caption at page 3
top. Figure 3 remains visually intact, and the accepted final page has its
normal empty right column.

This observation is not Microsoft Word evidence and does not close
HFUT-FIG-009 visually.

## 20. Files changed

- `docs/paper/manuscript/sections/02_problem_definition.md` — one authorized
  Figure 1 overview sentence.
- `scripts/paper/postprocess_full_manuscript_docx.py` — production-native
  Candidate-B Figure 3 story offset.
- `scripts/paper/validate_phase63_format.py` — narrow R10 structural gates and
  explicit evidence boundaries.
- `docs/paper/phase6_3/phase6_3_scientific_nonregression.json` — regenerated
  PASS phase label; scientific evidence is unchanged.
- This report.

The required Full and Anonymous DOCX outputs were regenerated in their ignored
production-output paths. The archived A/B/C candidate evidence remains intact.

## 21. Git diff

The final audit requires a clean index before staging, no unexpected file
category, and a clean `git diff --check`. The intended tracked diff is limited
to the five files listed above. Explicit classification:

```text
ABSTRACT_CHANGED = NO
INTRODUCTION_CHANGED = NO
METHOD_CHANGED = NO
EXPERIMENT_CHANGED = NO
RESULTS_CHANGED = NO
CONCLUSION_CHANGED = NO
SECTION_1_CHANGE = ONE_AUTHORIZED_F1_CALLOUT_SENTENCE_ONLY
FIGURE_DATA_CHANGED = NO
TABLE_DATA_CHANGED = NO
REFERENCES_CHANGED = NO
EQUATION_CONTENT_CHANGED = NO
```

## 22. Remaining manual Word QA

Open the exact Full DOCX identified above in Microsoft Word 2019, export a new
PDF, and verify only:

1. page 2 visibly contains the first `见图1` callout;
2. Figure 1 subsequently appears at page 3 top;
3. Figure 1 remains full-width, caption-below, unclipped, and without sandwich
   layout;
4. accepted Candidate-B Figure 3 remains unchanged;
5. no global pagination regression appears.

`HFUT_FIG009_VISUAL = PENDING_MICROSOFT_WORD_REVIEW`.

## 23. Commit

Exactly one controlled commit is authorized with subject:

```text
paper: finalize Candidate B and Figure 1 callout order
```

The report is itself part of that commit, so the commit cannot embed its own
SHA without changing its tree. The exact resulting SHA is returned in the
external handoff. No push, tag, merge, reset, clean, rebase, or amend is
performed.

## 24. Exact next action

Stop after the single controlled commit. The user should open the exact latest
`draft_full.docx` in Microsoft Word 2019, export PDF, perform only the five
checks in Section 22, and return the DOCX/PDF plus this report to the Main
Project AI for final Phase-6 format-gate closure.

```text
CANDIDATE_B = PRODUCTION_SELECTED
FIGURE3_ANCHOR = PRODUCTION_OFFSET_1
FMT_R8_01 = CLOSED
FMT_F01_IMPLEMENTATION = COMPLETE
HFUT_FIG009_STRUCTURAL = PASS
HFUT_FIG009_VISUAL = PENDING_MICROSOFT_WORD_REVIEW
CONTENT_GATE = REMAINS_FROZEN
PHASE6_SUPERVISOR_REREVIEW_READY = PENDING_FINAL_WORD_CONFIRMATION
HFUT_SUBMISSION_READY = NO
```
