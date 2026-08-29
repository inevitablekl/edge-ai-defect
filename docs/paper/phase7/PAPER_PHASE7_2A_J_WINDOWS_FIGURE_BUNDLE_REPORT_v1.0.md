# Phase 7.2A-J Windows native figure bundle preparation report

## Verdict

```text
PHASE_7_2A_J_WINDOWS_FIGURE_BUNDLE_READY
```

This phase prepared a self-contained Windows transfer bundle. It did not create or claim proprietary Visio/Origin outputs on Linux and did not modify a Word manuscript.

## Baseline reconciliation

- Branch: `main`.
- Required baseline: `944bbb45da4d7675e1b80463358546e46e663b24`.
- Starting `HEAD`: `944bbb45da4d7675e1b80463358546e46e663b24`.
- Starting `origin/main`: `944bbb45da4d7675e1b80463358546e46e663b24`.
- Tracked working-tree and index differences at start: none.
- One pre-existing untracked file was present: `docs/paper/phase7/PAPER_PHASE7_2B_ALL_EQUATIONS_STANDARD_LATEX_v1.0.md`. Inspection showed legitimate later manual-submission documentation. It was preserved byte-for-byte, excluded from this phase's scope, and is not included in the Phase 7.2A-J commit.

No reset, clean, merge, rebase, amend, push, manuscript rebuild, or Word edit was performed.

## Sources inspected and frozen hashes

| Role | Source | SHA256 |
|---|---|---|
| Figure manifest | `docs/paper/manuscript/figures/figure_manifest.csv` | `3694e0bd01b698fb5f31c8d618a8eecd071ffac62082f76679c48067c640efab` |
| Phase 7.1 manual specification | `docs/paper/phase7/PAPER_PHASE7_1_MANUAL_SUBMISSION_ADAPTATION_SPEC_v1.0.md` | `c5414ff21277feab9b9117cc5415b05be90fcac7a646d6440997fe3fc6fb2765` |
| F1 semantic authority | `docs/paper/phase5_9/visual/FIGURE1_INPUT_DATA_PATH_MODEL_SPEC.md` | `5c2860e363779763693adc3d717e793e3c23cf0489a366cd1688430030888053` |
| F1 generator | `docs/paper/phase5_9/visual/scripts/generate_phase59c_figure1.py` | `af7a97b7ce017a0a1460ea19a55651d7320692880e127acb2f8b53c52dd3216a` |
| F1 accepted SVG | `docs/paper/phase5_9/visual/production/figures/fig1_input_data_path_model_phase59c.svg` | `464ec447d0b86b363c338274ba4f583de876b08aa30e7458481972bd0669c119` |
| F1 accepted PNG | `docs/paper/phase5_9/visual/production/figures/fig1_input_data_path_model_phase59c.png` | `c562d5a3f1b930177ccacf90cfb467470bca7dd6c2d7597d92b7fe58292537c7` |
| F2/F3 generator | `docs/paper/phase5_6/visual/scripts/generate_phase56d_production_statistical.py` | `3efc2828bc1aa4be5400c2874d1af5b5ebd2a00a6af9dbca83f11d3068987bfb` |
| F2/F3 run rows | `docs/paper/phase5_6/phase56b_run_level_metrics.csv` | `f6b22f6b5574d957d3b3d600a637e0033d1f43a5afd77dca4e4a518f89d60e31` |
| F2/F3 display/aggregate authority | `docs/paper/phase5_6/phase56b_publication_display_values.json` | `0468d9ed640e8e3ed55089b3e90945a61f577422c8e3dfa63297454f55408655` |
| F2 accepted SVG | `docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.svg` | `be3a5207bab8973c769e307acd5ac3834ef4c1d4efae355f46273a0a9c394ac4` |
| F2 accepted PNG | `docs/paper/phase5_6/visual/production/figures/fig3_main_e2e_phase56.png` | `30e0d1254c0505b1bc1bfdcf5adf60c47d911a7c02b0ee93b3d2991c295db938` |
| F3 accepted SVG | `docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.svg` | `f1c95f5b67800aff6a29c8ed242ee6bc0b707e8c598a9dcf1551c54c7ab2958a` |
| F3 accepted PNG | `docs/paper/phase5_6/visual/production/figures/fig4_run_level_distribution_phase56.png` | `2f077a25bfddb50a8aaa186567a466180ba61b0ce0f16b1e10928cf73e28e2c8` |

## Figure authorities and extracted definitions

### F1

The manifest-selected Phase 5.9C SVG and its generator are the geometry authority. The SVG's `160 mm × 79 mm` page and `1600 × 790` viewBox yield a deterministic `10 SVG units/mm` conversion. `figure1_geometry.json` records native rectangles, rounded rectangles, lines/arrows, text rectangles, semantic groups, and z-order. It preserves the host/device domains and boundary; P₀/V0, P₂/V2R, P₃/V3R; R/F/M/E; both hierarchy semantics; all labels; the complete warning; and exact semantic colors.

The PowerShell recipe creates native Visio shapes through COM. It does not import the SVG or PNG.

### F2

The current manifest selects Phase 5.6 production `fig3_main_e2e_phase56` as manuscript F2. The extracted CSV contains the exact three aggregate rows required for the current three-panel figure: five-process FPS mean/sample SD, pooled 5400-sample mean latency, and pooled P95/P99. The display JSON retains every accepted three-decimal label and percentage/ratio string. The structural JSON freezes the accepted three-layer physical geometry, axis ranges, data mapping, series order, error semantics, colors, hatches, legend, annotations, typography, and panel spacing.

### F3

The current manifest selects Phase 5.6 production `fig4_run_level_distribution_phase56` as manuscript F3. The extracted CSV preserves all 15 accepted process rows in frozen execution order and all process-level FPS/mean/P95/P99 measurements. The display/specification files retain the two-panel layout, five-point jitter, FPS mean/sample-SD summaries, V2R/V3R latency descriptors, and exact `P95 +0.15%; P99 −0.12%` / `方向相反` annotation.

## Bundle contents

Bundle directory:

```text
docs/paper/submission_assets/windows_bundle/
```

It contains:

- Windows build README, bundle manifest, and per-artifact SHA256 list.
- F1 accepted SVG/PNG references, full native geometry JSON, text manifest, Visio specification, and Windows COM PowerShell builder.
- F2 accepted SVG/PNG references, exact aggregate CSV, display JSON, complete Origin JSON specification, and Windows `originpro` builder.
- F3 accepted SVG/PNG references, exact 15-row CSV, display JSON, complete Origin JSON specification, and Windows `originpro` builder.
- Scientific authority/hash manifest and native-output acceptance contract.

Transfer archive:

```text
docs/paper/submission_assets/HFUT_NATIVE_FIGURE_WINDOWS_BUNDLE.zip
```

Archive SHA256:

```text
82c9a1719805f936821fc0d1684163cd61ce88b2c2beded2f3947967bfc991a8
```

The ZIP contains exactly one `windows_bundle/` directory tree. It is a transfer convenience, not a scientific source of record, and remains outside the source commit.

## Windows build expectations and dependencies

Expected outputs:

| Figure | Application | Native output |
|---|---|---|
| F1 | Microsoft Visio Desktop + COM | `Figure1_input_data_path_model.vsdx` |
| F2 | Origin Desktop + matching `originpro` | `Figure2_E2E_performance.opju` |
| F3 | Origin Desktop + matching `originpro` | `Figure3_run_level_distribution.opju` |

Windows must provide Visio, Origin, the Origin-configured Python environment, SimSun, and Times New Roman. Native preview export and 100% visual comparison are mandatory. Version-specific adjustments may repair presentation properties only and must follow the frozen JSON specifications; they must not alter data, labels, precision, aggregation, or interpretation.

## Validation and scientific non-regression

- All seven JSON files parsed successfully.
- All three CSV files parsed successfully: 24 F1 text records, 3 F2 aggregate rows, and 15 F3 process rows.
- Both Origin scripts passed Python bytecode syntax compilation on Linux; generated `__pycache__` files were removed from the bundle.
- A PowerShell parser was unavailable on the Jetson host, so the Visio script was reviewed statically but not executed or Windows-parser-validated. Windows execution remains required.
- Every bundled SVG/PNG reference is byte-identical to the manifest-selected source asset.
- The bundled F3 CSV is byte-identical to the complete authoritative 15-row CSV, including provenance fields.
- Every F2 aggregate numeric field equals the authoritative publication JSON value.
- Required F1/F2/F3 frozen labels were found in bundle definitions.
- The Phase 5.6 generator's embedded frozen source hashes match the actual CSV/JSON hashes.
- `SHA256SUMS.txt` verifies every bundle artifact other than itself.
- No Linux-only absolute path is embedded in a Windows build script.
- No tracked scientific source, manuscript Markdown, DOCX, PDF, MathType object, pagination, or scientific conclusion was modified.
- No VSDX/OPJU success is claimed on Linux.

## Exact next action

```text
TRANSFER BUNDLE TO WINDOWS AND RUN CODEX-W.
```
