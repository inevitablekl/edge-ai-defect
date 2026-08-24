# Paper Phase 6.3R8 Word Float Anchor Optimization Report v1.0

## 1. Verdict

`STOP_FLOAT_ANCHOR_SOLUTION_UNRESOLVED`.

The exact R7 Full DOCX was audited, the R7 backfill assumption was retired,
and a bounded A/B/C Figure 3 logical-anchor candidate pack was generated for
Full and Anonymous. All candidates pass available structural and scientific
checks. The user subsequently reported no significant visual problem and no
perceptible visual difference between B and C. That observation does not
identify a winning anchor or establish that the Page-6 reserve changed, so no
candidate is selected and no production anchor is changed. All six candidates
are retained in Git for follow-up human/AI comparative review.

`MICROSOFT_WORD_PAGINATION_STATUS = USER_VISUAL_REVIEW_REPORTED_SELECTION_UNRESOLVED`.

## 2. Baseline

- Repository branch: `main`.
- Baseline `HEAD`: `84c92d687ff5bef55b19eca005b76a74b559362d`.
- Baseline `origin/main`: `84c92d687ff5bef55b19eca005b76a74b559362d`.
- Expected parent: `643163125a96a9bbbf3d0d87d527995416511b4b`.
- Baseline worktree: clean.
- Baseline index: clean.
- Baseline reconciliation: `PASS`.
- Push status: `PENDING_GITHUB_AUTHENTICATION`. The initial HTTPS push attempt
  returned `could not read Username for 'https://github.com'`; this execution
  environment has no configured HTTPS credential, GitHub CLI session, token,
  or SSH private key.
- Commit created: `YES`; it records an unresolved review pack, not production
  anchor acceptance.

## 3. Exact R7 artifact identity

The Microsoft-Word-reviewed Full artifact is:

```text
docs/paper/manuscript/output/draft_full.docx
SHA-256 3279ac1e8319fcfe850379f0c5d344aa795188f8e13a2b92f6101f85c3a81809
```

This exactly matches the identity supplied for Phase 6.3R8. The current
Anonymous R7 artifact is:

```text
docs/paper/manuscript/output/draft_anonymous.docx
SHA-256 18cd20181b4628a45e6d1a2a600b3ae9e884476468f5bbdae4dbf321076a846d
```

## 4. Pagination-QA classification

These categories are project diagnostic terms, not HFUT requirements:

- `ACCEPTABLE_TYPOGRAPHIC_RESERVE`;
- `WIDOW_ORPHAN_RESERVE`;
- `HEADING_KEEP_WITH_NEXT_RESERVE`;
- `FLOAT_ANCHOR_FLOW_DEFECT`;
- `UNKNOWN_LAYOUT_DEFECT`.

OOXML can establish pagination-related structure but cannot prove how
Microsoft Word used page or column space. Page classifications therefore use
the supplied Word-review observations, not an inferred residual-space limit.

## 5. Page 1 classification

`PAGE1_SMALL_RESERVE = ACCEPTED_NOT_A_DEFECT`.

The approximately one-line lower-left-column reserve is classified as
`ACCEPTABLE_TYPOGRAPHIC_RESERVE`. No body-font, line-spacing, widow/orphan, or
content-balancing change is authorized for it.

## 6. Page 3 classification

`PAGE3_SMALL_RESERVE = ACCEPTED_NOT_A_DEFECT`.

The approximately two-line reserve, followed on the next page by the final
approximately two lines of the same paragraph, is classified as
`WIDOW_ORPHAN_RESERVE`. No remediation is applied.

## 7. Page 5 classification

`PAGE5_SMALL_RESERVE = ACCEPTED_NOT_A_DEFECT`.

The approximately one-line reserve, followed on the next page by the final two
lines of the same scientific paragraph, is classified as
`WIDOW_ORPHAN_RESERVE`. No Figure 2 movement or paragraph manipulation is
applied.

## 8. Page 6 diagnosis

`FMT-R8-01`, severity `MAJOR`, remains open in the R7 baseline.

The materially large unused lower-left-column region is classified as
`FLOAT_ANCHOR_FLOW_DEFECT`. Figure 3 is physically in the following/right
column float region while later Section 4.4 and 4.5 prose remains after its
logical main-story anchor. The refined causal hypothesis is
`FLOAT_ANCHOR_STORY_ORDER_BARRIER`.

## 9. Widow/orphan audit

The exact Full DOCX was inspected at `word/styles.xml` and
`word/document.xml` before any edit.

| Style | Style-chain value for `widowControl` | Effective behavior | `keepNext` | `keepLines` | `pageBreakBefore` |
|---|---|---|---|---|---|
| `HFUTBody` | omitted in `HFUTBody`, `Normal`, and document defaults | on by OOXML terminal default | off/omitted | off/omitted | off/omitted |
| `HFUTHeading1` | omitted in `HFUTHeading1`, `Normal`, and document defaults | on by OOXML terminal default | on | on | off/omitted |
| `HFUTHeading2` | omitted in `HFUTHeading2`, `Normal`, and document defaults | on by OOXML terminal default | on | on | off/omitted |
| `HFUTHeading3` | omitted in `HFUTHeading3`, `Normal`, and document defaults | on by OOXML terminal default | on | on | off/omitted |

The omitted `widowControl` result follows ISO/IEC 29500 behavior reproduced in
[Microsoft's Open XML documentation](https://learn.microsoft.com/en-us/dotnet/api/documentformat.openxml.wordprocessing.widowcontrol?view=openxml-3.0.1):
when it is never specified in the style hierarchy, widow/orphan prevention
applies. The project does not add or remove the property because the current
behavior is already defined and consistent with the required policy.

Direct-paragraph audit:

- 49 `HFUTBody` paragraphs inspected;
- direct `widowControl`: 0;
- direct `keepNext`: 0;
- direct `keepLines`: 0;
- direct `pageBreakBefore`: 0.

`ACCIDENTAL_HFUTBODY_KEEP_CHAIN = NOT_FOUND`.

## 10. Heading pagination audit

The exact Full DOCX contains 6 `HFUTHeading1`, 15 `HFUTHeading2`, and no
instantiated `HFUTHeading3` paragraphs. Their direct paragraphs do not add
pagination overrides. The named styles preserve `keepNext=on` and
`keepLines=on`; none enables `pageBreakBefore`.

`HEADING_KEEP_WITH_NEXT_POLICY = PRESERVED`.

## 11. R7 float inventory

Indices below are one-based direct `w:body` child positions in the exact Full
DOCX.

| Figure | First callout | Float | Caption | `tblpPr` | Logical anchor | Physical intent |
|---|---:|---:|---|---|---|---|
| F1 | 39 | 40 | editable inside float | `vertAnchor=margin`; `horzAnchor=margin`; `tblpXSpec=center`; `tblpYSpec=top`; all text distances 0 | immediately after first callout | full-width, page/margin top |
| F2 | 76 | 77 | editable inside float | `vertAnchor=text`; `horzAnchor=text`; `tblpXSpec=center`; `tblpY=1`; all text distances 0 | immediately after first callout | centered in manuscript column near Section 4.2 discussion |
| F3 | 85 | 86 | editable inside float | `vertAnchor=text`; `horzAnchor=text`; `tblpXSpec=center`; `tblpY=1`; all text distances 0 | immediately after first callout in Section 4.4 | centered single-column float in the following/right-column region |

Each figure uses one top-level floating `w:tbl` with `w:tblpPr`, one
`w:cantSplit` row, one cell, an inline drawing payload, and its editable
caption below the drawing. Each uses `w:tblOverlap w:val="never"`. No governed
figure remains a top-level `wp:inline` story barrier.

The exact captions remain:

- F1: `图1　输入数据路径抽象及层级受控比较。图中层级表示结构变量的干预范围，不表示收益大小或组件级因果关系。`
- F2: `图2　三条路径的端到端性能。(a) 为5个独立进程FPS的均值±样本标准差；(b)(c) 为每条路径合并5400个延迟样本的均值、P95和P99。`
- F3: `图3　运行级分布与尾延迟。各点为独立进程级描述量，横向偏移仅用于区分，不表示运行配对。`

## 12. R7 assumption retired

The following implication is retired:

```text
w:tblpPr exists
→ all remaining earlier column space can be filled by later prose
```

The active model is:

```text
TEXT_WRAP_AROUND_FLOAT = SUPPORTED
BACKFILL_BEFORE_LOGICAL_FLOAT_ANCHOR = NOT_GUARANTEED
```

The Phase 6.3 validator and the figure-layout authority ledger now express
that evidence boundary. Actual page-space utilization requires Microsoft Word
pagination evidence.

## 13. Figure 3 current logical anchor

The first Figure 3 callout is Full body child 85. The R7 Figure 3 floating
table is child 86, immediately after that callout and before both remaining
Section 4.4 body paragraphs. Section 4.5 follows those two paragraphs.

This is a story-order observation, not a named-heading placement rule.

## 14. Candidate architecture definitions

The bounded candidate set changes only the count of related `HFUTBody`
paragraphs between the first Figure 3 callout and its floating table:

| Candidate | Offset from first callout | Full callout/float | Anonymous callout/float | Positioning metadata |
|---|---:|---|---|---|
| A | 0 related body paragraphs | 85 / 86 | 79 / 80 | R7 control: paragraph/text-relative vertical, column-centered horizontal |
| B | 1 related body paragraph | 85 / 87 | 79 / 81 | same as A |
| C | 2 related body paragraphs | 85 / 88 | 79 / 82 | same as A |

The offset is computed from the first callout and stops at the next heading;
the generator does not search for or name Section 4.5. Candidate A is an
exact byte-for-byte control. Candidate B places the logical anchor after the
next related Section 4.4 paragraph. Candidate C places it after both remaining
related Section 4.4 paragraphs.

## 15. Candidate OOXML differences

- Candidate A: no package difference from the corresponding R7 artifact.
- Candidate B: only `word/document.xml` differs; the existing F3 floating
  table is moved by one related-body offset.
- Candidate C: only `word/document.xml` differs; the existing F3 floating
  table is moved by two related-body offsets.
- F3 `tblpPr` is identical in A/B/C:
  `leftFromText=0`, `rightFromText=0`, `topFromText=0`,
  `bottomFromText=0`, `vertAnchor=text`, `horzAnchor=text`,
  `tblpXSpec=center`, `tblpY=1`.
- Figure 1 and Figure 2 story positions and float metadata are unchanged.
- No page break, section, named-heading anchor, overlap, or new drawing object
  is introduced.

The set deliberately isolates logical anchor offset while retaining Word's
supported paragraph/text-relative vertical reference and column-relative
horizontal centering. No unbounded position search was performed.

## 16. Microsoft Word availability

`MICROSOFT_WORD_DESKTOP_AVAILABLE = NO`.

The environment is Linux/aarch64. No `WINWORD.EXE`, Windows COM automation, or
other native Microsoft Word object model is available. LibreOffice 7.3 exists
but is not treated as equivalent pagination evidence.

## 17. Word-PDF geometry audit

`WORD_PDF_GEOMETRY_AUDIT = NOT_RUN_INPUT_UNAVAILABLE`.

The request states that a Word 2019 PDF was supplied, but no PDF is exposed in
the task attachment directory. The only current Full PDF in the repository's
ignored output directory reports `Creator: Writer` and
`Producer: LibreOffice 7.3`, SHA-256
`1baba96d9adaa9a477bd5f70bac13dcdc3b27dc77b7ccb6b25a6e9e41d351f87`.
It is not promoted to Word evidence. No arbitrary residual-space threshold or
HFUT requirement was added.

## 18. Selected candidate or candidate-review stop

No candidate is selected. The user visually inspected the candidates and
reported:

```text
NO_SIGNIFICANT_VISUAL_PROBLEM_OBSERVED
B_C_VISUAL_DIFFERENCE_NOT_PERCEPTIBLE
```

This is a valid review observation, but it does not identify which story
offset should become the production rule and does not specifically confirm
that the Page-6 lower-left reserve was materially reduced. Candidate A remains
the exact R7 control. B and C therefore remain parallel diagnostic candidates
for later human/AI comparison; neither is silently promoted from structural
evidence alone.

`PAGE6_LARGE_RESERVE = CANDIDATE_REVIEW_PENDING`.

## 19. Figure 1 non-regression

Figure 1 is unchanged across A/B/C:

- full-width DrawingML extent remains approximately 16.0 cm;
- page/margin-top and centered positioning metadata is unchanged;
- first callout remains before the figure;
- drawing and editable caption remain in one non-splitting float row;
- no figure-only section and no `pageBreakBefore` is introduced.

`FIGURE1_STRUCTURAL_NONREGRESSION = PASS`.

## 20. Figure 2 non-regression

Figure 2 is unchanged across A/B/C:

- single-column DrawingML width remains approximately 7.50 cm;
- first callout remains before the figure;
- paragraph/text-relative vertical and column-centered horizontal placement is
  unchanged;
- drawing and editable caption remain in one non-splitting float row;
- no attempt was made to consume the accepted Page-5 one-line reserve.

`FIGURE2_STRUCTURAL_NONREGRESSION = PASS`.

## 21. Figure 3 scientific non-regression

Figure 3's drawing, caption text, dimensions, relationship, and positioning
metadata are unchanged. Its PNG payload SHA-256 remains:

```text
0205e472b2017f202c2c3fde071c4396f93e0aa5789a7dd19095f103b697abc8
```

The only candidate variable is the logical top-level story position of the
existing floating table.

`FIGURE3_SCIENTIFIC_NONREGRESSION = PASS`.

## 22. Full/Anonymous structural validation

For candidates A, B, and C:

- DOCX ZIP/CRC integrity: `PASS`;
- Phase 6.3 structural format validation: `PASS`;
- Full manuscript structure/content validation: `PASS`;
- Anonymous identity scan: `PASS`;
- Full/Anonymous scientific-body parity: `PASS`;
- Phase 5.9C integration: `PASS`;
- float/caption association and non-overlap: `PASS`;
- first callout before Figure 3: `PASS`;
- Full/Anonymous candidate offset parity: `PASS`.

## 23. Scientific non-regression

`SCIENTIFIC_NONREGRESSION = PASS` for A, B, and C.

`validate_phase61_nonregression.py` passed for every corresponding
Full/Anonymous pair. The frozen experiment-source hash, Figure 2/3 data,
formal RQs, equations, correctness rows, metrics, directionality, limitations,
and conclusion tokens remain unchanged. All 18 overclaim-term matches remain
legitimate negation or boundary language.

Additional scientific media hashes are unchanged:

- F1: `c562d5a3f1b930177ccacf90cfb467470bca7dd6c2d7597d92b7fe58292537c7`;
- F2: `00130111de0133f868d156bff9810c7e9387ea0a32c2ee000e804f7d2f27cbe1`;
- F3: `0205e472b2017f202c2c3fde071c4396f93e0aa5789a7dd19095f103b697abc8`.

`MANUSCRIPT_MARKDOWN_CHANGED = 0`.

### Candidate build and verification commands

Candidate build input is the exact R7 Full/Anonymous DOCX pair; the production
Pandoc build is intentionally not rerun or overwritten on the Path B stop.

```text
python3 scripts/paper/generate_phase63r8_figure3_candidates.py \
  --input docs/paper/manuscript/output/draft_full.docx \
  --output docs/paper/manuscript/output/draft_full_r8_candidate_B.docx \
  --body-paragraph-offset 1

python3 scripts/paper/validate_phase63_format.py \
  --docx docs/paper/manuscript/output/draft_anonymous_r8_candidate_B.docx \
  --compare-full docs/paper/manuscript/output/draft_full_r8_candidate_B.docx

python3 scripts/paper/validate_phase61_nonregression.py \
  --full-docx docs/paper/manuscript/output/draft_full_r8_candidate_B.docx \
  --anonymous-docx docs/paper/manuscript/output/draft_anonymous_r8_candidate_B.docx \
  --output-json /tmp/phase63r8_B_scientific_nonregression.json \
  --report-phase "Paper Phase 6.3R8 candidate B"
```

The same commands were run with offsets 0/A and 2/C. Expected input is one
valid R7 Full or Anonymous DOCX containing exactly one marked Figure 3 float.
Expected output is one ignored candidate DOCX and a printed SHA-256. Structural
and scientific validators must both print `PASS`.

## 24. Files changed

Tracked working-tree changes:

- `scripts/paper/generate_phase63r8_figure3_candidates.py` — bounded,
  offset-based candidate generator;
- `scripts/paper/validate_phase63_format.py` — paragraph pagination audit,
  diagnostic taxonomy, and corrected float/backfill evidence semantics;
- `docs/paper/phase6_3/PAPER_PHASE6_3_FIGURE_LAYOUT_AUTHORITY_LEDGER_v1.0.md`
  — retired the false R7 backfill implication;
- `docs/paper/phase6_3/PAPER_PHASE6_3R7_INLINE_FIGURE_BARRIER_ELIMINATION_REPORT_v1.0.md`
  — added the R8 superseding clarification and removed guaranteed-backfill
  wording from its validator inventory;
- `docs/paper/phase6_3/PAPER_PHASE6_3R8_WORD_FLOAT_ANCHOR_OPTIMIZATION_REPORT_v1.0.md`
  — this report.

Generated candidate artifacts explicitly retained for external AI review:

- `docs/paper/manuscript/output/draft_full_r8_candidate_{A,B,C}.docx`;
- `docs/paper/manuscript/output/draft_anonymous_r8_candidate_{A,B,C}.docx`.

These generated files are normally ignored. They are force-added in this work
unit only because the user explicitly requested that every candidate be pushed
for follow-up review. They remain review evidence, not manuscript source.

Production `draft_full.docx`, production `draft_anonymous.docx`, the DOCX
postprocessor, manuscript Markdown, scientific assets, tables, equations, and
references are unchanged.

## 25. Git diff

The source diff is format-tooling/governance only. It adds one candidate
generator and this report, updates one validator, and corrects the R7 report
and authority ledger. Six generated DOCX review candidates are included by
explicit user authorization. `git diff --check` is required to remain clean
before handoff.

The commit records the unresolved candidate pack and diagnostic tooling; it is
not a production anchor-remediation claim. The production postprocessor and
production DOCX pair remain unchanged.

## 26. DOCX candidate SHA-256 values

| Candidate | Full SHA-256 | Anonymous SHA-256 |
|---|---|---|
| A | `3279ac1e8319fcfe850379f0c5d344aa795188f8e13a2b92f6101f85c3a81809` | `18cd20181b4628a45e6d1a2a600b3ae9e884476468f5bbdae4dbf321076a846d` |
| B | `ef444a1f6689431701c4747da8bbc0f661db1035a8448d1a49dedaaf0f0021f8` | `b732172875d8d5bbb04b6555b4bb0ac667ffc0671bcd83281e6ec5d96c9f1879` |
| C | `abcffc618b96933189c6bb301d6f925c000c539dd1ace95ceb264633e35dad34` | `aac77b8d523848868c03d2bb4f4990375b4cd8c63141b58abcb7c9c6f2f0193c` |

## 27. End-state classification

```text
PAGE1_SMALL_RESERVE = ACCEPTED_NOT_A_DEFECT
PAGE3_SMALL_RESERVE = ACCEPTED_NOT_A_DEFECT
PAGE5_SMALL_RESERVE = ACCEPTED_NOT_A_DEFECT
PAGE6_LARGE_RESERVE = HUMAN_AI_COMPARATIVE_REVIEW_PENDING
INLINE_FIGURE_BARRIER = CLOSED
FLOAT_ANCHOR_STORY_ORDER_MODEL = CORRECTED
SCIENTIFIC_NONREGRESSION = PASS
MANUSCRIPT_CONTENT = UNCHANGED
HFUT_SUBMISSION_READY = NO
```

## 28. External AI review handoff

Upload this report and the three Full candidates to the external AI reviewer.
The reviewer must compare the actual logical story order, not merely package
hashes:

- A: Figure 3 float immediately after its first callout;
- B: Figure 3 float after one subsequent related Section 4.4 body paragraph;
- C: Figure 3 float after two subsequent related Section 4.4 body paragraphs.

The scientific image, caption, size, wrap metadata, horizontal placement, and
vertical-reference metadata are identical. Consequently, B and C can look
identical when Word chooses the same physical float position. That outcome is
consistent with the experiment and must not be misreported as proof that their
OOXML story order is identical.

The reviewer should determine whether B or C has a clearer and more stable
logical association while preserving callout precedence and the observed Word
pagination. If visual output remains identical, prefer no production change
until a concrete stability or story-order criterion is accepted.

## 29. Exact next action

Provide the external AI reviewer with this report and the three Full
candidates. If screenshots or a Word-exported PDF are available, provide them
as well because generic DOCX rendering is not equivalent to Word pagination.
Ask the reviewer to verify:

1. the Page-6 large lower-left blank is materially removed;
2. Figure 3 is visually after its first callout and remains near Section 4.4;
3. no text overlaps, clips, appears behind the figure, or separates from its
   caption;
4. no new large whitespace or unexpected page-count increase appears;
5. the Page-1, Page-3, and Page-5 small reserves remain accepted and are not
   optimized;
6. Figure 1 and Figure 2 retain their accepted placement.

Return either a reasoned B/C recommendation tied to story order and Word
pagination, or the conclusion that no production change is justified. Only a
later explicit task may promote an accepted candidate into the production
postprocessor and rebuild the production Full/Anonymous pair.

Do not continue into Visio, Origin, MathType, Document Inspector, or final
submission production.
