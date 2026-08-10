# Paper Phase 5.4B Literature and Citation Integration v1.0

## 1. Verdict

`LITERATURE_CITATION_INTEGRATION_COMPLETE`

## 2. Starting state

- Branch: `main`.
- Starting HEAD: `9e672244df70056b8b09c4e1b13387a09cbe499e`.
- Starting subject: `docs(paper): refine theory boundaries after independent review`.
- Worktree/index: clean.

## 3. Verification method

Each admitted source was checked against the local PDF's internal title/DOI and at least one formal publication authority where available: DOI/Crossref publisher metadata, IEEE Xplore/official proceedings, CVF, PMLR, ACM DOI metadata, MDPI article pages, Dagstuhl/DROPS, or DBLP as a metadata cross-check. Filenames alone were never treated as publication identity.

The Bateni intake required special reconciliation. The local proceedings PDF footer displays `.00029`, while the registered DOI `10.1109/RTAS48715.2020.00007` resolves to IEEE Xplore document `9113098`; Crossref and DBLP associate that registered DOI with the Bateni title and pages `310–323`. The bibliography therefore uses the registered DOI required by the task, while the conflicting local footer is recorded as an intake risk.

## 4. Bibliography before and after

- Before: `15` library entries; `14` cited/rendered.
- After: `27` library entries; `26` cited/rendered.
- Added: `13`.
- Removed: `1` (`liu_zhang_ruan_2024_hfut_yolov5_embedded`).
- Upgraded metadata: `1` (`reddi_et_al_2019_mlperf_inference`, arXiv 2019 → ISCA 2020 under the same logical key).
- Retained existing records: `13`, including the retained-unused MLPerf Mobile record.

## 5. Added citation keys and exact roles

| Citation key | Role |
|---|---|
| `lv_et_al_2020_metallic_defects` | Metallic-defect/NEU problem background. |
| `chu_yu_rong_2024_strip_steel_yolov8` | Recent improved-YOLO strip-steel contrast. |
| `zhang_pang_jiang_2024_gdm_yolo` | Recent YOLOv8 architecture-change contrast. |
| `stacker_et_al_2021_edge_runtime` | Edge DNN deployment and runtime optimization. |
| `kim_et_al_2025_concurrent_edge_detection` | Complete detection stages and runtime optimization without detector modification. |
| `lee_han_kim_2025_presto` | Preprocessing/data-management bottleneck possibility. |
| `hill_marty_2008_amdahl` | Generic optimization-coverage principle. |
| `bateni_et_al_2020_integrated_memory` | Integrated CPU/GPU memory-policy dependence. |
| `rodriguez_et_al_2025_gpu_memory_allocation` | GPU allocation-policy workload dependence. |
| `jacob_et_al_2018_integer_inference` | Integer inference and accuracy/performance trade-off. |
| `nagel_et_al_2020_adaround` | PTQ perturbation and validation requirement. |
| `dean_barroso_2013_tail_scale` | Mean-versus-tail rationale. |
| `archet_et_al_2023_embedded_soc` | Embedded heterogeneous-SoC configuration dependence. |

## 6. Manuscript locations changed

- `01_introduction.md`: compact industrial/algorithm landscape, deployment-system role, preprocessing role, PTQ correctness boundary; `12` distinct references.
- `02_problem_definition.md`: PTQ support, system-path support, memory-policy boundary, Amdahl citation and benchmark/tail rationale.
- `03_method.md`: pinned-staging non-universality and non-equivalence to Host-Pinned/Zero-Copy studies.
- `04_experiment.md`: Jetson comparability, reproducible benchmark boundary, formal MLPerf methodology and tail metrics.
- `05_results.md`: citations placed after project observations and separated from all project numbers.

No edit was made to `00_title_abstract.md`, `06_conclusion.md`, figures or tables.

## 7. Sources intentionally not cited

- Clockwork: redundant with Dean/Barroso plus MLPerf for the final prose.
- Two mislabeled local PDFs: exact duplicates of the Kim concurrent-processing paper; both have SHA-256 `af2a0764058a5ee56c3d646167dfa0543b0ff294715ee6a2ba595752cf570745`.
- Duplicate Kim PDF copy: one logical publication retained.
- Other downloaded defect/HFUT papers: no independent manuscript claim role.
- MLPerf Mobile: retained as a prior admitted library entry but intentionally not rendered; the formal ISCA MLPerf source fills the active role.

## 8. CN closure

| CN | Status | Primary support | Locations |
|---|---|---|---|
| CN-01 | CLOSED | Lv; Song; Shao; Chu; GDM-YOLO | Introduction |
| CN-02 | CLOSED | Stäcker; Kim | Introduction; §1.2–1.3 |
| CN-03 | CLOSED | PRESTO; Stäcker | Introduction; §1.2–1.3; §4.2 |
| CN-04 | CLOSED | Hill/Marty | §1.3, directly around T3 |
| CN-05 | CLOSED | Bateni; CUDA Best Practices | §1.2; §2.3; §4.3 |
| CN-06 | CLOSED | Rodriguez; Archet | §1.2; §2.3; §4.3 |
| CN-07 | CLOSED | MLPerf ISCA 2020; Lema | §1.4; §3.1; §3.3 |
| CN-08 | CLOSED | Dean/Barroso; MLPerf | §1.4; §3.3; §4.4 |
| CN-09 | CLOSED | Jacob; Nagel; HyQ | Introduction; §1.1 |

## 9. Citation-risk audit

- PRESTO numbers transferred: `NO`.
- PRESTO used to prove project cause: `NO`.
- Host-Pinned/Zero-Copy conflated with V3R: `NO`.
- Pinned memory described as universal winner: `NO`.
- Dean/Barroso datacenter mechanism transferred: `NO`.
- MLPerf compliance claimed: `NO`.
- AdaRound/TensorRT calibration conflated: `NO`.
- External citation made to appear as source of a project number: `NO`.

## 10. Duplicate and metadata audit

- Duplicate DOI: `NONE`.
- Duplicate normalized title: `NONE`.
- Duplicate logical publication: `NONE` in the bibliography.
- Mislabeled candidates: `2`, dropped by identical SHA-256 and title/content mismatch.
- MLPerf disposition: one ISCA 2020 record under the existing logical key; no duplicate arXiv record.
- Bateni DOI: `10.1109/RTAS48715.2020.00007`.
- Fabricated fields: `NONE`.

## 11. Scientific-diff audit

| Item | Result |
|---|---|
| Frozen results changed | NO |
| Metric definitions changed | NO |
| Experimental protocol changed | NO |
| Correctness conditions changed | NO |
| Contribution count | `2` |
| New experimental fact | NONE |
| Excluded evidence restored | NO |

Frozen results retained exactly:

1. V2R/V0 FPS ratio: `2.236671×`.
2. V2R/V0 mean latency reduction: `55.4519%`.
3. V3R/V2R FPS: `+4.0738%`.
4. V3R/V2R mean latency: `-4.0349%`.
5. V3R/V2R P95: `+0.1514%`, higher/slower.
6. V3R/V2R P99: `-0.1184%`, lower/faster.

Tail remains `MIXED`.

## 12. Formula/theory audit

- T1: unchanged conceptual E2E decomposition; no stage timing added.
- T2: unchanged `T_shared,v + T_specific,v` abstraction; no equal-time assumption added.
- T3: unchanged Amdahl-type equation with Hill/Marty citation placed immediately around it.
- Amdahl alpha estimate: `NONE`.
- Amdahl alpha ordering: `NONE`.
- Performance prediction: `NONE`.
- Display equations: `8` Full and `8` Anonymous, retained as OMML.

## 13. Build validation

Full:

- Build: PASS.
- LibreOffice pagination: `11` pages, A4.
- SHA-256: `63005c3355bc333c720b8ed9317c29d95988398a1a95f44a1e57753d3f4ae637`.

Anonymous:

- Build: PASS.
- LibreOffice pagination: `12` pages, A4.
- SHA-256: `319658602d1cf892eea359759583b0b900acef8ca430566d6fa5a690a17bbe41`.

The one-page pagination difference results from the different front-matter identity package; the authoritative scientific-body parity validator passes.

## 14. Validation summary

- Citation source validator: PASS (`27` entries, `26` cited, zero unresolved, one governed unused entry).
- Final-reference validator: PASS for Full and Anonymous.
- Deterministic first-citation order and rendered type validation: PASS.
- Duplicate DOI/title validation: PASS.
- Static figure/table cross-references: PASS.
- Full manuscript validator: PASS.
- Anonymous identity and scientific-body parity: PASS.
- Journal-format mechanical validator: PASS.
- ZIP/XML integrity: PASS.
- OMML count and equation parity: PASS.
- A4 pagination: PASS, within the expected `11–13` page range.
- Numerical-preservation scan: PASS.
- `git diff --check`: PASS before governance report creation and required again before commit.

## 15. Governance assets

- `PAPER_PHASE5_4B_CITATION_ARCHITECTURE_v1.0.md`.
- `PAPER_PHASE5_4B_LITERATURE_CITATION_INTEGRATION_v1.0.md`.
- Updated `literature_matrix.csv` and `citation_final_audit.csv` provide row-level source and rendered-reference traceability.

## 16. Recommendation

`READY_FOR_5_4C_MAIN_AI_REVIEW`

No visual work, title/abstract/conclusion work, push, merge or tag is authorized by this phase.
