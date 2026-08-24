# Paper Phase 6.3R11 Selective Chinese Figure Localization Report v1.0

## 1. Verdict

`PHASE_6_3_CHINESE_FIGURE_LOCALIZATION_IMPLEMENTED`.

Figure 2 and Figure 3 now use Chinese-dominant descriptive annotations while
retaining standard scientific abbreviations and identifiers. Their accepted
R10 raster/vector canvases, Word drawing extents, float geometry, and logical
placement are unchanged. Scientific and build gates pass. Microsoft Word 2019
pagination and display confirmation remains pending.

## 2. Baseline

- Branch: `main`.
- Initial `HEAD`: `1adb42aaefa9e7de7a24e4454d514eb3e43b32b7`.
- Initial `origin/main`: `1adb42aaefa9e7de7a24e4454d514eb3e43b32b7`.
- Initial commit subject: `paper: finalize Candidate B and Figure 1 callout order`.
- Worktree and index before editing: clean.
- Baseline Full DOCX SHA-256:
  `ab8d3d4132549b00be468fd615230fdd4814187f078e2b73498e4ce8a0c614c3`.
- Baseline Anonymous DOCX SHA-256:
  `b18836acbf35f05d9fa866aaa57a5ff508ced63779ed77398eeaed207beda648`.
- Baseline reconciliation: `PASS`.

The manuscript Figure 2 and Figure 3 assets are respectively named
`fig3_main_e2e_phase56` and `fig4_run_level_distribution_phase56` in the
historical Phase 5.6 production directory.

## 3. Supervisor preference

For this Chinese journal manuscript, descriptive natural-language figure text
should use Chinese where reasonably appropriate. Full translation is neither
required nor desirable when an English abbreviation, identifier, symbol, or
unit is already standard.

## 4. Translation policy

Only descriptive plot labels were localized. `FPS`, `E2E`, `P95`, `P99`,
`V0`, `V2R`, `V3R`, `ms`, and `n` remain unchanged. Numerical values,
percentages, marker semantics, data, captions, tables, equations, references,
and manuscript prose were not changed. Localized strings use the existing
`Noto Serif CJK SC` review family; no font or font size was added or reduced.

## 5. Figure-2 text before/after

| Before | After |
|---|---|
| `mean ± sample SD; 5 processes / path` | `均值±样本SD；每路径5进程` |
| `E2E latency / ms` | `E2E 延迟 / ms` |
| `pooled n = 5400 / path` | `合并 n=5400/路径` |
| `latency / ms` | `延迟 / ms` |

## 6. Figure-3 text before/after

| Before | After |
|---|---|
| `process-level FPS` | `进程级 FPS` |
| `points: independent processes` | `点：独立进程` |
| `bar/error: mean ± sample SD` | `横线/误差：均值±样本SD` |
| `Mean` | `均值` |
| `process-level latency / ms` | `进程级延迟 / ms` |
| `opposite directions` | `方向相反` |

## 7. Terms intentionally retained in English

`FPS`, `E2E`, `P95`, `P99`, `V0`, `V2R`, `V3R`, `ms`, `n`, and `SD` are
retained as standard abbreviations, identifiers, units, or statistical
notation. All displayed numerical values and percentages are retained exactly.

## 8. Baseline geometry

Content bounding boxes use PNG pixel coordinates `[left, top, right, bottom]`
after suppressing near-white antialiasing noise. Aspect ratio is `width/height`.

| Item | Figure 2 | Figure 3 |
|---|---:|---:|
| PNG canvas | 786 × 1623 px | 768 × 1246 px |
| Aspect ratio | 0.4842883549 | 0.6163723917 |
| SVG `viewBox` | `0 0 188.487562 389.492914` | `0 0 184.239562 298.994344` |
| PDF page | 188.488 × 389.493 pt | 184.240 × 298.994 pt |
| Content bounding box | `[13, 9, 777, 1612]` | `[11, 9, 759, 1235]` |
| Left/right padding | 13 / 9 px | 11 / 9 px |
| Horizontal padding asymmetry | 0.0050890585 | 0.0026041667 |
| Bounding-box center offset | 0.0025445293 | 0.0013020833 |
| Word drawing extent | 2699999 × 5575190 EMU | 2699999 × 4380468 EMU |
| Word rendered size | 7.499997 × 15.486639 cm | 7.499997 × 12.167967 cm |

## 9. Post-change geometry

The generator now exports into explicit governed R10 vector boxes and exact
R10 PNG pixel canvases instead of allowing localized text to recalculate a
tight bounding box.

| Item | Figure 2 | Figure 3 |
|---|---:|---:|
| PNG canvas | 786 × 1623 px | 768 × 1246 px |
| Aspect ratio | 0.4842883549 | 0.6163723917 |
| SVG `viewBox` | `0 0 188.487562 389.492914` | `0 0 184.239562 298.994344` |
| PDF page | 188.488 × 389.493 pt | 184.240 × 298.994 pt |
| Content bounding box | `[10, 10, 777, 1612]` | `[6, 10, 759, 1235]` |
| Left/right padding | 10 / 9 px | 6 / 9 px |
| Horizontal padding asymmetry | 0.0012722646 | 0.0039062500 |
| Bounding-box center offset | 0.0006361323 | 0.0019531250 |
| Word drawing extent | 2699999 × 5575190 EMU | 2699999 × 4380468 EMU |
| Word rendered size | 7.499997 × 15.486639 cm | 7.499997 × 12.167967 cm |

Both optical measurements remain below the governed asymmetry and center-offset
limits. Direct full-resolution inspection found no label overlap or clipping.
Two consecutive final regenerations produced identical SVG/PDF/PNG hashes.

## 10. Word drawing extent comparison

| Figure | R10 baseline extent | R11 Full extent | R11 Anonymous extent | Result |
|---|---:|---:|---:|---|
| Figure 1 | 5759999 × 2851093 EMU | 5759999 × 2851093 EMU | 5759999 × 2851093 EMU | unchanged |
| Figure 2 | 2699999 × 5575190 EMU | 2699999 × 5575190 EMU | 2699999 × 5575190 EMU | unchanged |
| Figure 3 | 2699999 × 4380468 EMU | 2699999 × 4380468 EMU | 2699999 × 4380468 EMU | unchanged |

The complete floating-object subtree hashes are also unchanged from R10:

- Figure 1: `e00d7bd5a365a49b62e111755599a3afedebe0c2f605015440d34439ddadc426`.
- Figure 2: `d3c2471a5b8bde3ace387558d7b0f07a57863f9becb749b536fad24b79e13d57`.
- Figure 3: `23efec28f6b065a886861520c306c4eab18291fd074cb44cd38ebe669593cace`.

`WORD_GEOMETRY_NONREGRESSION = PASS`.

## 11. Candidate-B non-regression

Full retains first Figure 3 callout child 85, Figure 3 float child 87, and one
intervening nonempty `HFUTBody` paragraph. Anonymous retains the corresponding
children 79 and 81 with the same offset. Both retain zero intervening headings,
`vertAnchor=text`, `horzAnchor=text`, `tblpXSpec=center`, `tblpY=1`, and zero
text distances.

`CANDIDATE_B = UNCHANGED`.

## 12. Figure-1 non-regression

Figure 1 source, payload, placement logic, and callout prose are unchanged. Its
payload SHA-256 remains
`c562d5a3f1b930177ccacf90cfb467470bca7dd6c2d7597d92b7fe58292537c7`,
and its complete floating-object subtree hash and drawing extent match R10.
Full retains overview callout child 28 and float child 40; Anonymous retains
children 22 and 34.

`FIGURE1 = UNCHANGED`.

## 13. Scientific non-regression

- Frozen run-level source SHA-256 remains
  `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31`.
- Frozen publication-summary SHA-256 remains
  `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655`.
- Baseline/current visible SVG numerical-token multisets are identical for both
  figures.
- Generator data loading, bars, error bars, scatter points, fixed jitter,
  numerical annotation formatting, thresholds, axes limits, and path
  identifiers are unchanged.
- `validate_phase61_nonregression.py` reports
  `PHASE61_SCIENTIFIC_NONREGRESSION=PASS` with 18 legitimate boundary matches.

`SCIENTIFIC_NONREGRESSION = PASS`.

## 14. Full build

Command:

```bash
bash scripts/paper/build_manuscript_docx.sh --build-full
```

Result: `FULL_BUILD = PASS`. Heading numbering, citations, references, full
manuscript structure, Phase 5.9C integration, and Phase 6.3 format validation
all passed.

## 15. Anonymous build

Command:

```bash
bash scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Result: `ANONYMOUS_BUILD = PASS`. Anonymity scan, scientific-body parity,
bibliography identity, integration, and structural validation all passed.

## 16. Full/Anonymous parity

`FULL_ANONYMOUS_PARITY = PASS`. Both packages contain the same localized Figure
2/3 payloads, drawing extents, float properties, Figure 3 related-body offset,
equations, tables, references, and scientific body. Their expected absolute
child-position difference remains the six Full-only front-matter paragraphs.

## 17. Full DOCX SHA256

```text
docs/paper/manuscript/output/draft_full.docx
4063d23f50f296d466e45fffba9f5759f39797cf6df64ac8a85a24d1f0844df5
```

## 18. Anonymous DOCX SHA256

```text
docs/paper/manuscript/output/draft_anonymous.docx
e21fe576538acd2b17dfe753748f58d39be69750280c566ab11dd2c5d1706ac1
```

## 19. Files changed

- `generate_phase56d_production_statistical.py`: localized only governed
  natural-language labels, applied the existing CJK review font, and froze the
  accepted export canvases.
- Figure 2 production SVG/PDF/PNG triplet: deterministically regenerated.
- Figure 3 production SVG/PDF/PNG triplet: deterministically regenerated.
- `validate_phase63_format.py`: added exact R10 PNG canvas, SVG `viewBox`, and
  Word drawing-height gates; existing width and optical gates remain active.
- `phase6_3_scientific_nonregression.json`: regenerated PASS artifact with the
  R11 phase label.
- This report.

No manuscript Markdown, Figure 1 asset, table, equation, reference, CSL,
postprocessor, figure-placement rule, experiment source, or statistical source
was modified. `TABLE_LOCALIZATION_CHANGE = NONE`.

## 20. Git diff

The intended tracked diff contains ten files: the statistical generator, six
Figure 2/3 assets, the narrow Phase 6.3 validator, the regenerated scientific
non-regression artifact, and this report. `git diff --check` passes. No
unexpected file category is present, and the index was clean before final
staging.

```text
MANUSCRIPT_MARKDOWN_CHANGED = NO
FIGURE1_CHANGED = NO
TABLES_CHANGED = NO
EQUATIONS_CHANGED = NO
REFERENCES_CHANGED = NO
EXPERIMENTAL_DATA_CHANGED = NO
STATISTICAL_VALUES_CHANGED = NO
FIGURE_PLACEMENT_CODE_CHANGED = NO
```

## 21. Word QA still required

Automated evidence establishes implementation and OOXML/asset geometry, not
Microsoft Word pagination. The accurate end state is:

```text
FIGURE_CHINESE_LOCALIZATION = IMPLEMENTED
WORD_GEOMETRY_NONREGRESSION = PASS
MICROSOFT_WORD_PAGINATION = PENDING_FINAL_CONFIRMATION
```

The user should inspect only Figure 2, Figure 3, overall page count/major
pagination, and unchanged Figure 1 in Microsoft Word 2019. LibreOffice is not
used to claim `PAGINATION_VISUAL_PASS`.

## 22. Commit

Exactly one controlled commit is created with subject:

```text
paper: localize statistical figure labels for Chinese journal
```

This report belongs to that commit, so it does not embed its own resulting
commit SHA. The SHA is returned in the external handoff. No push, tag, merge,
reset, clean, rebase, or amend is performed.

## 23. Exact next action

Open the exact Full DOCX from Section 17 in Microsoft Word 2019 and verify:

1. Figure 2 Chinese labels display correctly, without overlap or clipping, at
   the same location/page.
2. Figure 3 Chinese labels display correctly, without overlap or clipping, at
   the same accepted Candidate-B location.
3. Page count and major pagination are unchanged.
4. Figure 1 is unchanged.

Return the Word QA result to the Main Project AI. Until that confirmation:

```text
FIGURE1 = UNCHANGED
FIGURE2 = CHINESE_DOMINANT_LABELING
FIGURE3 = CHINESE_DOMINANT_LABELING
STANDARD_ABBREVIATIONS = RETAINED
TABLES = UNCHANGED
CANDIDATE_B = UNCHANGED
WORD_DRAWING_GEOMETRY = UNCHANGED
SCIENTIFIC_NONREGRESSION = PASS
MICROSOFT_WORD_VISUAL_CONFIRMATION = PENDING
HFUT_SUBMISSION_READY = NO
```
