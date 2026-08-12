# Paper Phase 5.6D-A — Visual Architecture Report

## 1. Verdict

```text
PHASE56_VISUAL_ARCHITECTURE_READY_FOR_REVIEW
```

Figure 1–4 and Table 1–4 now have candidate architecture, source/caption contracts, evidence traces, deterministic generation plans, and reviewable previews. These are explicitly `CANDIDATE / SPECIFICATION`, not manuscript authority.

## 2. Repository State

Starting audit:

```text
repository = /home/orin/edge-ai/edge-ai-defect
branch = main
HEAD = fa3697e2bcfd36e7a99764bfe21900b22db55b91
origin/main = fa3697e2bcfd36e7a99764bfe21900b22db55b91
git status --short = empty
git diff --stat = empty
git diff --cached --stat = empty
```

The starting baseline matched the requested frozen narrative commit. No pre-existing user change was encountered.

## 3. Current Figure/Table Audit

### Figures

| ID | Current source / generation | Payloads and geometry | SHA256 (current final assets) | DOCX insertion |
|---|---|---|---|---|
| F1 | manual Visio authority; `fig1_v0_v2r_v3r_data_paths_phase5_final.vsdx/.svg/.pdf` | SVG `14.6583 × 3.01155 in`; PDF `1055.28 × 216.72 pt` | SVG `9c53ff8243dd402d81fc63fb3c65f1e83cb967cb36aa90030200702f0044b12e`; PDF `90bb4f93a2265a4ef3c981ca818c140294b478255ccb36824b0b05ace4a9614e` | PDF converted to 150-DPI PNG by `build_manuscript_docx.sh`; inserted at 16 cm |
| F2 | manual Visio authority plus `scripts/generate_fig2_e2e_intervention_scope_preview.py`; final SVG/PDF | SVG `9.58579 × 4.22356 in`; PDF `690.12 × 304.08 pt` | SVG `3233ee910c8b81944a5608c1acadcb68bde3dff0ca9e5c55fdbc18f5c8ec3db0`; PDF `634c0d19be145e310108fe16c21b85298f42a8ca9ea76e61a7c38a5e3926952e` | PDF converted to 150-DPI PNG; inserted at 16 cm |
| F3 | `scripts/generate_fig3_mean_fps_phase5.py`, frozen CSV, Matplotlib | SVG/PDF `232.441 × 175.748 pt`; PNG `968 × 732 px` | SVG `5438d61eeff785d850929809755e34ab42c35f1f122ebe2639bd2c434f19128a`; PDF `74b05f78d43b7883d06f9bcc381db93fdce8c9d6016a0f161a1c81866a6fff88`; PNG `d33ec800d58fde8e9639c1bde4e1962f04616a58ea2e9ea6d2b51a975c4d7325` | committed PNG inserted at 7.5 cm |
| F4 | `scripts/generate_fig4_mean_tail_latency_phase5.py`, frozen CSVs, Matplotlib | SVG/PDF `481.89 × 198.425 pt`; PNG `2007 × 826 px` | SVG `672fc9d5ed235195ecc75b6a86f7d0dfadd7f6fd7929b636258607e31ce87af6`; PDF `e6311442c0ad2dd8940cc15d3de8e641956dc27bfdfd58ee711257941c2dd22a`; PNG `2436fddee6cbd4b20099ae79bae97e32ffa4ad5a5be45b4b0ceaf3a37fdeb84c` | committed PNG inserted at 16 cm |

The authoritative inventory is `docs/paper/manuscript/figures/figure_manifest.csv`. Existing F1/F2 use Chinese Songti/Latin Times rules through manual assets; current reproducible F3/F4 use Liberation Serif plus Noto Serif CJK fallback. D-A did not alter any of these assets or scripts.

### Tables

- Current T1 is the controlled path/configuration table, full width about `16.002 cm`.
- Current T2 is the platform/model/dataset/protocol table, about `7.761 cm`.
- Current T3 is the V0/V2R correctness gate-style table, about `7.761 cm`.
- T4 does not exist in the production manifest or manuscript.
- All three current tables are native three-line Word tables. D-A created only Markdown candidates in a separate directory.

## 4. Journal Layout Constraints

Read-only OOXML inspection of the current `draft_full.docx` established A4 portrait (`11906 × 16838` twips), margins left/right `1304` twips and top/bottom `1361/1134` twips, and one actual column. The text area is approximately `16.4 cm`.

```text
FIGURE_SINGLE_COLUMN_WIDTH = 7.5 cm
FIGURE_DOUBLE_COLUMN_WIDTH = not active in the current one-column DOCX; project full-width limit = 16.0 cm
CURRENT_FIGURE_PAYLOAD_FORMAT = F1/F2 150-DPI PDF-derived PNG; F3/F4 committed PNG
CURRENT_VECTOR_SUPPORT_STATUS = SVG/PDF are retained as source/final assets, but DOCX insertion currently uses PNG compatibility payloads
TABLE_WIDTH_CONSTRAINT = <= 16.0 cm; native three-line table preferred
```

Current inline extents: F1 `16.0 × 3.289 cm`, F2 `16.0 × 7.054 cm`, F3 `7.5 × 5.671 cm`, F4 `16.0 × 6.585 cm`. Caption style is centered 7.5 pt, exact 16 pt line spacing, zero before/after, Chinese 黑体 and Latin Times New Roman. Table text is 7.5 pt Chinese 宋体/Latin Times New Roman. No layout/style mutation was made.

## 5. Global Visual Style

`PHASE56_GLOBAL_VISUAL_STYLE_SPEC.md` freezes typography, minimum size, line weights, functional domains, statistical grammar, output formats, and raster gates. Variant identity is neutral gray/dotted/square for V0, light blue/slash/circle for V2R, and light orange/backslash/triangle for V3R. Color is never the only identity and never encodes better/worse. Candidates use existing Noto Serif CJK and Liberation Serif availability; no new font dependency was introduced.

## 6. Figure 1 Architecture

F1 is a three-layer hero figure: explicit host/device domains; V0 and a branching/merging V2R/V3R path; and a detached complete-path observation footer. It makes the shared downstream GPU path and single shared Engine visible. Nominal payload values carry the non-bus-traffic qualifier.

```text
PERFORMANCE_VALUES_ATTACH_TO_COMPARISON = YES
PERFORMANCE_VALUES_ATTACH_TO_COMPONENT = NO
```

Candidate: `candidates/fig1_hero_data_path_phase56_candidate.{svg,pdf,png}`.
Spec: `fig1_hero_data_path_phase56_spec.md`.

## 7. Figure 2 Architecture

F2 is a host/device implementation figure for V2R/V3R. It shows pageable/pinned staging, `cudaMemcpy2DAsync`, persistent raw storage, the fused CUDA kernel, TensorRT-owned input, `enqueueV3`, output D2H, and CPU postprocessing. A single rail represents the same TensorRT CUDA stream and sequential ordering; it does not depict transfer/compute overlap. Lifecycle notes state allocation before the loop and cross-frame reuse. `NO PERFORMANCE NUMBERS` is enforced.

Candidate: `candidates/fig2_technical_implementation_phase56_candidate.{svg,pdf,png}`.
Spec: `fig2_technical_implementation_phase56_spec.md`.

## 8. Figure 3 Architecture

F3 has three nonredundant panels: process-level FPS mean ± sample SD; pooled mean E2E latency; and absolute pooled P95/P99. The generator reads frozen CSV/JSON, verifies 15 rows, five processes/path, 1080 frames/process, recomputes FPS statistics, and checks the frozen aggregate authority. No bar height is manually entered and no tiny tail delta is visually magnified.

Candidate: `candidates/fig3_main_e2e_phase56_candidate.{svg,pdf,png}`.
Spec: `fig3_main_e2e_phase56_spec.md`.

## 9. Figure 4 Architecture

F4 uses individual process points: five FPS points for each path and five Mean/P95/P99 latency points for V2R/V3R. Fixed offsets are descriptive only; no point is paired or connected. The separate formal callout identifies the pooled 5400-sample/path tail authority and `MIXED` verdict. The figure supports descriptive run-level repeatability, not significance or long-term/thermal/frequency stability.

Candidate: `candidates/fig4_run_level_distribution_phase56_candidate.{svg,pdf,png}`.
Spec: `fig4_run_level_distribution_phase56_spec.md`.

## 10. Table 1 Specification

T1 is a 10-row path-feature matrix. All 30 V0/V2R/V3R cells are mapped separately to implementation authority in `phase56_visual_evidence_map.csv`; V0 stream reuse uses an em dash because GPU-preprocessing stream reuse is not applicable. It avoids platform/protocol duplication.

Candidate: `candidates/table1_path_feature_matrix_candidate.md`.
Spec: `table1_path_feature_matrix_spec.md`.

## 11. Table 2 Specification

T2 keeps the compact platform/software/model/Engine/calibration/workload/timing envelope. Runtime qualifications about power mode, clocks, and non-continuous temperatures remain in text; hashes, long paths, and governance prose are omitted. The exact `KEEP_IN_TABLE`, `KEEP_IN_TEXT`, and `OMIT_AS_REDUNDANT` allocation is frozen in `table2_platform_protocol_spec.md`.

Candidate: `candidates/table2_platform_protocol_candidate.md`.

## 12. Table 3 Specification

T3 is upgraded architecturally to three path rows and four scientific task metrics: Precision, Recall, mAP50, and mAP50-95. The candidate is generated directly from `phase56b_correctness_table_source.csv`; it excludes gate tolerances and pass/fail wording. Class-level evidence remains Level-B, with only the maximum zero differences suitable for a concise note.

Candidate: `candidates/table3_correctness_candidate.md`.
Spec: `table3_correctness_spec.md`.

## 13. Table 4 Full-Text Evidence Audit

Bibliographic identities were resolved from `docs/paper/manuscript/references/references.bib`, not from abbreviations. All five external PDFs are available under `/home/orin/paper-external-inputs/hfut-journal/phase3_literature_v1/`; external full texts were read but not copied into the repository.

Existing local analysis/register paths are `docs/paper/manuscript/references/literature_matrix.csv` and `docs/paper/manuscript/references/citation_final_audit.csv` for all five works; Tang & Qian and Shin & Kim also have admission records in `docs/paper/phase3/PAPER_PHASE3_LITERATURE_ADMISSION_REGISTER_v1.0.csv`. The exact full-title/author/year identity comes from `references.bib`, while the new attribute judgments come from the full texts and are traced in the D-A evidence CSV.

| Work | Full text | Attributes resolved | Unresolved |
|---|---|---:|---|
| Kim et al. (2025), concurrent multi-frame edge detection | available, 12 pages | 7/7 | none; absent reports classified `NOT_REPORTED` |
| PRESTO (2025), hybrid CPU-GPU preprocessing | available, 6 pages | 7/7 | none |
| Tang & Qian (2024), YOLOv8 railway inspection deployment | available, 9 pages | 7/7 | none |
| Shin & Kim (2022), Jetson YOLO framework evaluation | available, 19 pages | 7/7 | none |
| Bateni et al. (2020), integrated CPU/GPU memory management | available, 14 pages | 7/7 | none |

The seven fair, independently relevant dimensions are edge deployment, fixed model within comparison, GPU preprocessing, explicit host-memory strategy, complete E2E evaluation, task correctness, and tail latency. All 42 external/this-work cells carry a source, page/section, short paraphrase, and confidence in `phase56_related_work_attribute_evidence.csv`. `NOT_REPORTED` remains distinct from `NO_IF_EXPLICIT`.

Candidate: `candidates/table4_related_work_candidate.md`.
Spec: `table4_related_work_spec.md`.

## 14. F1 Literature-Gap Resolution

```text
LITERATURE_GAP_AUDIT = PARTIAL_PRECEDENT_ONLY
DIRECT_MATCH_STATUS = NO_DIRECT_MATCH_IN_AUDITED_SET
F1_SUPPORT_STATUS = PARTIALLY_SUPPORTED
```

The audited works separately cover edge deployment, GPU preprocessing, host-memory policies, E2E timing, or correctness, but none is a direct match for the complete controlled combination. This scoped local audit is not an exhaustive field search and cannot support “no prior work exists.”

Publication-safe candidate, not integrated:

> 在本文审阅的相关边缘部署与预处理/内存管理工作中，尚未见在固定detector/Engine下同时隔离输入形成位置、host representation、名义输入复制载荷与pageable/pinned staging，并以统一任务正确性和完整E2E口径比较的报告。

Recommended placement: put the grouped citations to all five audited works immediately after that scoped sentence.

## 15. F2 Terminology Resolution

Future target terminology is frozen as:

```text
运行级分布与尾延迟
```

The manuscript was not modified. “运行级稳定性” and stronger long-term/statistical/thermal/frequency stability implications are excluded from the candidate spec.

## 16. Evidence Maps

- `phase56_visual_evidence_map.csv`: more than 80 trace records covering every F1/F2 box/arrow/callout, F3/F4 statistical roles, every T1 data cell, and T2–T4 data authorities.
- `phase56_related_work_attribute_evidence.csv`: exactly 42 rows, six works × seven attributes, with allowed vocabulary, source path, page/section, paraphrase, and confidence.

## 17. Candidate Visual Inspection

All SVG/PDF candidates were rasterized at 300 DPI and their PNGs were inspected at original resolution.

| Candidate | Result | Inspection summary |
|---|---|---|
| F1 | PASS | domains, branch/merge, arrowheads, CJK/API glyphs, payload guard, and detached performance footer readable; no component attribution |
| F2 | PASS | stream rail, memory boundary, lifecycle notes, exclusions, and CPU output leg readable; no performance number |
| F3 | PASS | all bars/values/error bars visible; pooled versus process semantics legible; grayscale hatches present |
| F4 | PASS | all process points visible, no pairing/lines, tail callout unclipped, marker redundancy present |

No embedded figure caption is present. The automated record and raster dimensions are in `phase56_candidate_validation.json`. Final single/full-width proof remains a D-B integration gate; current candidates are designed for 16 cm full width.

## 18. D-B Production Plan

| Asset | Tool | Source data | Spec | Expected output | Validation | Integration target |
|---|---|---|---|---|---|---|
| F1 | Python raw SVG | implementation + Level-B payload/display values | F1 spec | SVG/PDF/PNG | evidence/hash/raster/causality/16-cm proof | after introduction contributions |
| F2 | Python raw SVG | implementation call sites | F2 spec | SVG/PDF/PNG | call-site/forbidden-token/raster/width proof | §2.2–§2.3 |
| F3 | Python + Matplotlib | run CSV + frozen display JSON | F3 spec | SVG/PDF/PNG | schema/hash/recompute/determinism/raster | aggregate results |
| F4 | Python + Matplotlib | run CSV + frozen display JSON | F4 spec | SVG/PDF/PNG | schema/hash/no-pairing/determinism/raster | 运行级分布与尾延迟 |
| T1 | native Word table | implementation evidence map | T1 spec | three-line table | 30-cell trace + width proof | path definition |
| T2 | native Word table | runtime/calibration/protocol evidence | T2 spec | three-line table | allocation/provenance/width proof | experimental setup |
| T3 | generated values + native Word table | correctness CSV | T3 spec | three-line table | CSV/hash/value proof | correctness results |
| T4 | generated classifications + native Word table | full-text evidence CSV | T4 spec | three-line table | 42-cell trace/fairness/citation/width proof | related work |

## 19. Mutation Check

```text
authoritative manuscript Markdown modified = NO
production Figure 1–4 replaced = NO
production Table 1–3 replaced = NO
Table 4 integrated = NO
DOCX modified = NO
journal formatting modified = NO
Level-A modified = NO
Level-B modified = NO
```

Automated comparison against `fa3697e2…` also finds no diff in authoritative sections, production figures/tables, or tracked DOCX files.

## 20. Generated Files / SHA256

Generated artifacts are confined to `docs/paper/phase5_6/visual/`: one global style spec, eight asset specs, two evidence CSVs, three generator scripts, one validator, 12 figure candidate payloads, four Markdown table candidates, this report, a validation JSON, and a SHA256 manifest.

The exhaustive per-file hashes are recorded in `phase56_candidate_sha256.txt`. Candidate figure triplets are additionally recorded inside `phase56_candidate_validation.json`. The manifest intentionally excludes itself and the validation JSON; it includes this report after the final validation rerun.

## 21. Validation

Command:

```bash
python3 docs/paper/phase5_6/visual/scripts/validate_phase56d_visual_candidates.py
```

Validated gates: four frozen input hashes; four complete SVG/PDF/PNG triplets; candidate watermarks; no embedded captions; F1 required causality/payload guards; F2 forbidden performance-token absence; valid PNG/PDF geometry; all four candidate table warnings; 42-cell literature matrix and vocabulary; F1–F4/T1–T4 evidence coverage; protected-path and DOCX zero mutation; and byte-identical deterministic regeneration of all 12 figure payloads.

## 22. Open Findings

1. F1 support is deliberately `PARTIALLY_SUPPORTED`: the five full texts justify scoped wording only, not an exhaustive novelty claim.
2. D-B must decide final full-width placements and prove legibility in the then-current DOCX without changing the fixed journal format contract.
3. D-B must remove candidate marks, create production authority, update manifests/cross-references/captions, and perform final Word/PDF visual inspection; none of those integration actions is authorized here.
4. The current manuscript is actually one-column. Future work must not describe 16 cm as an active double-column span unless the template changes under separate authority.

## 23. Commit

One focused commit is required with message `paper: specify phase 5.6 visual architecture`. The commit SHA is the commit containing this self-referential report (`git rev-parse HEAD`) and is recorded exactly in the final handoff. Push is prohibited; the final worktree/index must be clean.
