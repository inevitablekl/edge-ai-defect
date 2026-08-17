# Paper Phase 5.9C — Theory-Oriented Manuscript Reconstruction Report

## 1. Verdict

`PHASE59C_THEORY_RECONSTRUCTION_CANDIDATE`

The manuscript has been reconstructed around a fixed-object input data-path system model without new experiments, new citations, or changes to frozen scientific evidence.

## 2. Baseline reconciliation

Requested historical baseline: `b0a20b97c42c8d67579827243ed301f757a5d7e2`.

Accepted Phase 5.9C baseline: `7a5db56c7b0d9cde4d1ba47dc320b1c61f2f15e8`, with `main = origin/main` and a clean worktree/index at preflight.

Exactly one intervening commit existed: `7a5db56 paper: prepare supervisor rereview package`. Its four file changes classify as follows:

| File | Classification |
|---|---|
| `docs/paper/phase5_7/PAPER_PHASE57H_SUPERVISOR_REREVIEW_PACKAGE_REPORT.md` | REPORT_ONLY |
| `docs/paper/phase5_7/supervisor_rereview_package/*_导师复审稿.docx` | DELIVERY_PACKAGE_ONLY |
| `docs/paper/phase5_7/supervisor_rereview_package/*_导师复审稿.pdf` | DELIVERY_PACKAGE_ONLY |
| `docs/paper/phase5_7/supervisor_rereview_package/SUPERVISOR_REREVIEW_PACKAGE_MANIFEST.md` | DELIVERY_PACKAGE_ONLY |

No intervening `MANUSCRIPT_SOURCE_CHANGE`, `FIGURE_TABLE_SOURCE_CHANGE`, `FORMAT_PIPELINE_CHANGE`, or bibliography change was found. Therefore `PHASE59C_BASELINE = CURRENT_HEAD` was applied; no checkout or reset occurred.

## 3. Starting commit

`7a5db56c7b0d9cde4d1ba47dc320b1c61f2f15e8`.

## 4. New research-object definition

The paper now studies a fixed-object input data-path system. The fixed object combines detector, Engine, input size, workload, and task/postprocessing semantics. A path describes how input data are represented, formed, staged, and executed inside that fixed context. V0, V2R, and V3R are path instances rather than API collections or software-version labels.

## 5. Path-model implementation

The descriptor is `P=(R,F,M,E)`:

- `R`: representation crossing the host-device boundary;
- `F`: TensorRT input-tensor formation location;
- `M`: additional packed raw-image host staging policy;
- `E`: execution topology.

`P0/V0` uses FP32 NCHW, host formation, no additional packed raw staging, and sequential single-frame execution. `P2/V2R` uses packed BGR uint8, device formation, pageable staging, and the same topology. `P3/V3R` differs from `P2` only by pinned staging. `P0→P2` is a path-level reconstruction; `P2→P3` is a staging-policy-level refinement.

## 6. Equations

The final display inventory is exactly three:

1. `P=(R,F,M,E)` — experiment-specific path descriptor.
2. `B(P)=H_R(P)W_R(P)C_R(P)s_R(P)` — derived nominal input-copy payload; numerical instantiations follow inline.
3. `T_E2E(P)=t_pre-sink(P)-t_source(P)` — directly measured source-to-pre-sink response boundary.

The former additive stage-sum formula was retired because no stage times were independently measured. FPS is defined inline in Section 3.3; Type-7 is concise prose.

## 7. Introduction reconstruction

The Introduction now follows: industrial defect task → model optimization → complete edge runtime/preprocessing → quantization/correctness context → host/device representation and memory movement → unresolved research object → RQ1/RQ2 → exactly two contributions. API-centered path narration and result-checklist framing were removed.

## 8. Related-work migration

The old standalone related-work Table 4 and Results subsection were removed. Its useful sources were moved into three attributed Introduction streams: detector/model optimization, edge runtime/preprocessing/E2E, and host/device memory/data movement. All 22 existing cited sources remain scientifically attached to a claim or protocol role. No new source was added.

## 9. Method reconstruction

Section 2 now leads with architecture and changed structural variables, then gives only the implementation mapping required for reproduction and semantic identity. V0 retains OpenCV `INTER_LINEAR`, letterbox/114, BGR→RGB, HWC→CHW, normalization, host FP32 NCHW formation, and FP32 H2D. V2R retains packed BGR, effective geometry, two-dimensional H2D, fused device preprocessing, and direct TensorRT-owned input. V3R states that only `M` changes from pageable to pinned.

## 10. Figure 1 replacement

New Figure 1 is generated deterministically by `docs/paper/phase5_9/visual/scripts/generate_phase59c_figure1.py` and governed by `FIGURE1_INPUT_DATA_PATH_MODEL_SPEC.md`. It shows host/device domains, `R/F/M/E` for all paths, and the two intervention levels. It contains no performance number, API lifecycle, output-path detail, or causal arrow. SVG, PDF, PNG, and grayscale inspection assets were generated; the PNG remains the mechanical DOCX payload under the established LibreOffice compatibility route.

## 11. Old Figure 2 removal

`F2_REMOVAL_SAFE = YES`.

The removed implementation figure's scientifically necessary information is preserved by new Figure 1, the structural Table 1, and Section 2's compact implementation mapping: representation, tensor-formation location, pageable/pinned isolation, same stream semantics, and sequential/no-overlap scope. Historical Phase 5.7 assets were not modified or deleted.

## 12. Table reconstruction

Final inventory:

1. Table 1 — six-row structural-variable matrix for `R`, `F`, preprocessing mapping, `M`, derived `B(P)`, and `E`.
2. Table 2 — platform, fixed inference object, and benchmark protocol.
3. Table 3 — correctness constraint evidence.

Old Table 4 remains only as a historical asset outside the publication source.

## 13. Experiment compression/repositioning

Section 3 retains Jetson Orin Nano Super, L4T/CUDA/TensorRT/OpenCV identities, `MAXN_SUPER`, `nvpmodel mode 2`, no `jetson_clocks`, 180 images, 60 warmup frames, 1080 measured frames/process, five processes/path, 15 total processes, 5400 latency samples/path, interleaving, disabled diagnostics/profiling, and the non-continuous temperature observation boundary. Type-7 and FPS definitions are concise and descriptive-only.

## 14. Results/discussion reconstruction

- 4.1 treats correctness as the admission condition for comparison.
- 4.2 answers RQ1 using the complete `P0→P2` intervention and separates the 40.96× structural payload contrast from the measured 2.24×/−55.45% response.
- 4.3 answers the mean-response part of RQ2 under the isolated `M` change (+4.07% FPS, −4.03% mean latency).
- 4.4 answers the tail part of RQ2: P95 +0.15% and P99 −0.12% have opposite directions, so mean and tail are separate response dimensions.
- 4.5 bounds the interpretation to the tested system and descriptive protocol.

## 15. Conclusion reconstruction

The Conclusion now uses three layers: frozen measured responses; system-level separation of joint path reconstruction from local staging policy; and the bounded implication that representation, tensor-formation location, staging policy, mean response, and tail response should be controlled separately. API narration was removed.

## 16. Citation/reference audit

- Bibliography library: 27 verified entries.
- Cited and rendered: 22.
- Unresolved/dead rendered citations: 0.
- Uncited library entries retained by prior admission/governance: 5.
- Rendered count remains above the 18-reference review gate.
- Full/Anonymous bibliography identity: PASS.

`citation_final_audit.csv` was regenerated from the reconstructed citation order; all first occurrences are now in the Introduction.

## 17. Frozen scientific non-regression

All frozen values are present and validator-checked: V0 `54.600 FPS / 18.273 ms`; V2R `122.122 FPS / 8.140 ms`; V3R `127.097 FPS / 7.812 ms`; raw/publication comparisons `2.236671× / 2.24×`, `−55.4519% / −55.45%`, `+4.0738% / +4.07%`, `−4.0349% / −4.03%`, P95 `+0.1514% / +0.15%`, P99 `−0.1184% / −0.12%`; payloads `4.9152/0.1200 MB/frame` and `40.96×`; correctness `0.6913/0.6991/0.6476/0.3523`, with classwise maximum difference 0. No Phase 5.6 or Phase 5.7 historical scientific asset changed. No benchmark, inference, profiling, telemetry, or other measurement was run.

## 18. Page count

Both mechanical PDFs are 7 A4 pages. Full page map: page 1 front matter/Introduction; page 2 Introduction and 1.1–1.2; page 3 Table 1, 1.3, Figure 1, and start of Section 2; page 4 remainder of Section 2 and Section 3; page 5 correctness, Figure 2, and 4.2–4.4; page 6 Figure 3, 4.4–4.5, Conclusion, and reference start; page 7 references. Anonymous pagination differs locally after identity removal but remains 7 pages with no overflow.

## 19. Full/Anonymous build

- Full DOCX: `docs/paper/manuscript/output/draft_full.docx`, SHA256 `719c5373f9131f3ebe7144464b70d4109f269f34aefb22d76c741cfe2ea664f6`.
- Anonymous DOCX: `docs/paper/manuscript/output/draft_anonymous.docx`, SHA256 `f4758a850b5f13cb548539b12a12d8eeb6a1262c50c8b4831e6f43eba2e320a2`.
- Full mechanical PDF: `docs/paper/manuscript/output/pdf/draft_full.pdf`, SHA256 `134a1796bebbade7e280622bd76f9d9ecf3017da2190cea21847b29ef017d003`.
- Anonymous mechanical PDF: `docs/paper/manuscript/output/pdf/draft_anonymous.pdf`, SHA256 `ab35917b910dcb41185220e3f08a43eee853d284af9f6e131bf81c2880ed547c`.

DOCX ZIP validity, Full/Anonymous scientific parity, anonymous identity, three-figure media identity, three-table content identity, three OMML equations, and 22-entry bibliography rendering all pass.

## 20. HFUT format non-regression

The official-format validator passes for Full and Anonymous: A4 geometry, margins, two-column body, front/body section transitions, body/heading/caption/table/reference styles, first-line indentation, footers, title typography, three-line tables, and equation paragraph treatment. Both Chinese and English titles render on one line; no heading wraps. Manual page-image inspection found no clipped equation, figure, table, or body text after the E2 single-column correction.

## 21. Claim-boundary audit

`PAPER_PHASE59C_CLAIM_EVIDENCE_MAP.md` admits only T1 directly supported and T2 derivable-without-new-experiment central claims. The manuscript does not claim a new theory/algorithm, stage-level causality, measured traffic/bandwidth, 40.96× transfer acceleration, pinned tail/stability improvement, significance, or cross-platform/model generalization.

## 22. Before/after narrative statistics

The full mapping is in `PAPER_PHASE59C_RECONSTRUCTION_COMPARISON.md`. Key changes are: Introduction 1324→2052 characters and 4→7 scientific prose paragraphs; Section 1 1564→2447 characters (+56.5%); Section 2 1920→1162 characters (−39.5%); selected implementation/API mentions 10→2 (−80%); equations 2→3; figures 4→3; tables 4→3. The shift increases research-object and response-mechanism discussion while reducing procedure/lifecycle narration.

## 23. Open findings

- MathType source conversion and Visio/Origin editable-object conversion remain documented submission exceptions and are deferred until scientific approval.
- Mechanical PDFs are validation derivatives; final Word/Windows submission inspection remains a downstream publication step.
- The paper deliberately makes no stronger inference than supported by the frozen single-platform, single-model, offline descriptive experiment.

## 24. Commit SHA

`COMMIT_CONTAINING_THIS_REPORT` — self-resolving reference to the single focused Phase 5.9C commit. The exact immutable SHA is reported in the final handoff after commit creation; embedding that commit's own SHA in its content would be recursively impossible without an additional/amended commit.

No push, tag, merge, rebase, reset, or amend is authorized or performed.
