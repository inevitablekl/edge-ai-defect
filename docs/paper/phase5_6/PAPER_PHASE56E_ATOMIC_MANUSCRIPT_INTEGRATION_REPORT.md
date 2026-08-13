# Paper Phase 5.6E — Atomic Manuscript Integration Report

## 1. Verdict

```text
PHASE56_INTEGRATION_CANDIDATE
```

This execution is **Phase 5.6E resumed from R1-corrected visual authority**.
The prior `L4T metadata blocker` is `CLOSED`. No new scientific or
format-contract blocker was found.

## 2. Repository State

The mandatory preflight recorded:

```text
repository = /home/orin/edge-ai/edge-ai-defect
branch = main
starting HEAD = 72b8fc838b67b5951e4a4ed16eba70900e719adf
starting origin/main = 72b8fc838b67b5951e4a4ed16eba70900e719adf
starting worktree = clean
starting index = clean
```

No reset, clean, push, tag, merge, or amendment was performed. The focused
Phase 5.6E commit is created after this report so that the report does not
contain a self-referential commit identifier.

## 3. R1 Blocker Closure

- Table 2 uses the corrected `L4T R36.5` production authority.
- `L4T 36.4.3` is absent from the active manuscript source and both rendered
  DOCX variants.
- The runtime qualifiers remain: `MAXN_SUPER`, `nvpmodel mode 2`,
  `jetson_clocks` not invoked, clock frequencies not independently archived,
  and pre/post temperature observations non-continuous.

## 4. Related-Work F1 Resolution

The old field-wide gap sentence ending in:

```text
仍缺少足够明确的受控工程证据。
```

was removed. The final publication wording is a scope/positioning statement:

> 现有相关工作分别从检测模型、量化与推理、边缘运行时、GPU预处理或系统级部署等角度讨论边缘检测性能。为减少模型和推理后端差异带来的混杂，本文进一步将研究范围收敛到固定detector与Engine条件下的输入形成位置、host representation、输入复制载荷以及pageable/pinned staging，并通过两级受控路径比较评价其完整E2E行为。

No first, unique, exhaustive-coverage, or field-wide absence claim was added.

## 5. Section 4.4 Resolution

The final title is:

```text
4.4 运行级分布与尾延迟
```

The body limits “运行级重复性” to the descriptive direction observed in five
independent processes and explicitly rejects paired-run and significance
semantics.

## 6. Figure 1–4 Integration

| Figure | Frozen production source | Manuscript location | DOCX payload | Cross-reference and caption |
|---|---|---|---|---|
| F1 | `fig1_hero_data_path_phase56` | after the two contributions in the Introduction | PNG | callout precedes the frozen F1 caption exactly once |
| F2 | `fig2_technical_implementation_phase56` | after §2.2 and before §2.3 | PNG | callout describes memory domains, buffer lifetime, and single-stream ordering |
| F3 | `fig3_main_e2e_phase56` | §4.2 | PNG | one unified FPS/mean E2E/P95/P99 figure and one frozen caption |
| F4 | `fig4_run_level_distribution_phase56` | §4.4 | PNG | independent process points; no paired-run semantics |

SVG was tested first. Pandoc embedded four SVG media parts, but LibreOffice 7.3
rendered blank figure areas. The build therefore uses the frozen production PNG
fallback for all four figures. This is a `PAYLOAD_COMPATIBILITY_CHANGE`; the
frozen SVG/PDF/PNG production assets and their hashes were not changed. The
complete R1 hash list passed `sha256sum -c`.

## 7. Table 1–4 Integration

All four tables use the existing native Word three-line-table pipeline.

- T1: 10 path-feature rows × V0/V2R/V3R, full width.
- T2: compact platform/model/protocol table; contains `L4T R36.5`, 1260-image
  calibration, `IInt8EntropyCalibrator2`, batch 1, and INT8 + FP16 fallback.
- T3: V0/V2R/V3R are all visible with Precision, Recall, mAP50, and mAP50-95;
  gate tolerance/pass-fail columns are absent.
- T4: 6 works × 7 attributes, full width; `是`, `明确否`, and `未报告` remain
  semantically distinct; no score or ranking was added.

## 8. Cross-Reference Reconciliation

The final semantic flow is:

```text
Introduction → Figure 1
Method → Table 1 / Figure 2
Experiment → Table 2
§4.1 → Table 3
§4.2 → Figure 3
§4.3 → nominal input-copy payload discussion
§4.4 → Figure 4
§4.5 → Table 4
§4.6 → limitations
Conclusion
```

Each Figure 1–4 and Table 1–4 caption appears exactly once, after a valid
preceding callout. No dangling, duplicated, or stale numbered reference remains.

## 9. Bibliography Reconciliation

```text
bibliography source entries = 27
cited/rendered entries = 26
unused admitted entries = 1
new bibliography entries = 0
duplicates = 0
orphans outside the admitted unused entry = 0
Full/Anonymous rendered-reference parity = PASS
```

The retained unused entry is `reddi_et_al_2022_mlperf_mobile`, as governed by
the existing admission decision.

## 10. Equation Inventory

Exactly five display equations remain, in this order:

1. `T_E2E` composition.
2. Process FPS `f_i`.
3. Mean FPS `mu_f`.
4. Type-7 `h/j/gamma` definition.
5. Type-7 `Q_p` definition.

```text
Display equations = 5
Amdahl equation = absent
```

## 11. Scientific Freeze Validation

The rendered manuscript retains:

```text
V0→V2R: 2.24× FPS; −55.45% mean latency
V2R→V3R: +4.07% FPS; −4.03% mean latency
P95: +0.15%
P99: −0.12%
Tail: MIXED
```

The nominal input-copy payload remains `4.9152 MB/frame` for V0,
`0.1200 MB/frame` for V2R/V3R, and `40.96×`, always qualified as nominal.
Table 3 retains 0.6913 Precision, 0.6991 Recall, 0.6476 mAP50, and 0.3523
mAP50-95 for all three paths. Class-level maximum AP50 and Recall differences
remain 0, limited to the frozen 180-image workload and governed evaluator.

Calibration wording retains forced cache miss, generation and archival of the
cache, and non-reuse of a pre-existing cache as formal-build input. No
cache-hit ambiguity or runtime-state overreach is present.

## 12. Format Protection

```text
Word style definitions = NO CHANGE
body/heading/equation/caption/table styles = NO CHANGE
fonts = NO CHANGE
margins/page size = NO CHANGE
line-spacing contract = NO CHANGE
journal template = NO CHANGE
global font reduction = NO
landscape page = NO
```

The journal-format validator passed for both variants. Wide-object section
transitions changed only as required to place the four 16 cm figures and the two
full-width native tables; the established one-/two-column strategy and A4 page
geometry remain unchanged.

## 13. Full Build

Command:

```bash
scripts/paper/build_manuscript_docx.sh --build-full
```

Result:

```text
PASS
DOCX = docs/paper/manuscript/output/draft_full.docx
DOCX size = 862551 bytes
DOCX SHA256 = 5d1e34b598e37e023ba8ec63cf784daa24cbbd1b8c6915375318bbd20f128b3a
mechanical pages = 10 A4
figures = 4
tables = 4
display equations = 5
rendered references = 26
```

## 14. Anonymous Build

Command:

```bash
scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Result:

```text
PASS
DOCX = docs/paper/manuscript/output/draft_anonymous.docx
DOCX size = 861860 bytes
DOCX SHA256 = 1c6a324985225d44378262d030685cce7b5592144a806f0287da2accee9b0a0c
mechanical pages = 10 A4
figures = 4
tables = 4
display equations = 5
rendered references = 26
identity scan = PASS
scientific parity = PASS
```

## 15. Mechanical Visual Inspection

LibreOffice 7.3 rendered both variants to 10-page A4 PDFs. Every page in both
variants was inspected.

- F1: no clipping; labels and nominal-payload guard readable.
- F2: API labels and all arrowheads preserved.
- F3: axes, legend, hatches, values, and P95/P99 readable.
- F4: all independent process points, markers, legend, and MIXED annotation readable.
- T1–T4: native three-line style retained; no overflow; T4 fits at full width.
- General: captions, headings, equations, references, and page flow are intact;
  no blank page or overlap was found.

The result is 10 pages, not 9. No formatting was changed to force a page count.

## 16. Validator Results

The following passed:

- Full manuscript structure/content validator.
- Anonymous privacy and Full/Anonymous scientific-parity validator.
- Static citation, bibliography, caption, and cross-reference validator.
- Word heading-numbering validator.
- Journal-format validator.
- Phase 5.6E integration validator.
- Python compilation, shell syntax, DOCX ZIP integrity, production-asset
  SHA256 list, and `git diff --check`.

The historical Phase 5.6D-B production validator intentionally freezes the
pre-integration manuscript source hash and is therefore not the Phase 5.6E
acceptance validator after authorized manuscript mutation. Its immutable
production assets were instead checked directly against the complete frozen
SHA256 list, with every entry passing.

## 17. Stale Semantic Scan

The active manuscript and rendered variants contain none of the eight forbidden
stale strings, including the four old captions, the old Table 3 title, the old
§4.4 title, the broad literature-gap wording, and `L4T 36.4.3`.

## 18. Final Inventory

```text
Figures = 4
Tables = 4
Display equations = 5
Contributions = 2
```

## 19. Files Changed

The focused changes cover:

- manuscript sections 01–05;
- Figure and Table manifests;
- the DOCX build filter and native-table/section postprocessors;
- the directly affected Full, Anonymous, citation, format, and heading validators;
- the new Phase 5.6E integration validator;
- this Phase 5.6E report.

Generated DOCX/PDF/raster inspection outputs remain ignored build artifacts and
are not committed.

## 20. Open Findings

1. LibreOffice 7.3 renders the direct SVG DOCX payloads blank; the frozen PNG
   compatibility route is required for the current mechanical workflow.
2. The mechanically rendered length is 10 pages. This is reported as observed
   and was not remediated through formatting changes.
3. Final Microsoft Word visual review remains an external submission-stage
   check; it is not a scientific or format-contract blocker for this candidate.

## 21. Commit

One focused local commit is required with message:

```text
paper: integrate phase 5.6 manuscript assets
```

Push, tag, merge, and amend remain prohibited. The final handoff records the
resulting commit SHA and clean-worktree verification.
