# Paper Phase 5.4C-C Figure/Table Integration v1.0

Status: `FIGURE_TABLE_INTEGRATION_COMPLETE`; final Microsoft Word visual
review: `PENDING_USER_MANUAL`.

## 1. Starting state

- Branch: `main`.
- Starting HEAD: `c1712bf00d2414218ba2fdd529d0bf46562c9787`.
- Starting subject: `docs(paper): generate phase5 figures 3 and 4`.
- Starting worktree and index: clean.

## 2. Manual staging intake

Staging directory:
`/home/orin/paper-external-inputs/phase5_4c_manual_figures/`.

| Target | Staged file | Bytes | SHA-256 | Intake validation |
|---|---|---:|---|---|
| F1 | `fig1_v0_v2r_v3r_data_paths_phase5_final.vsdx` | 32792 | `a10b4f333a2c27ae939b08443fdb152751b1e6d0b91e9695dd4d9f82d43053c4` | VSDX ZIP integrity PASS |
| F1 | `fig1_v0_v2r_v3r_data_paths_phase5_final.pdf` | 97361 | `90bb4f93a2265a4ef3c981ca818c140294b478255ccb36824b0b05ace4a9614e` | one-page PDF geometry/render PASS |
| F1 | `fig1_v0_v2r_v3r_data_paths_phase5_final.svg` | 24037 | `9c53ff8243dd402d81fc63fb3c65f1e83cb967cb36aa90030200702f0044b12e` | XML/geometry/render PASS |
| F2 | `fig2_e2e_intervention_scope_final.vsdx` | 30653 | `63ec86949f79cca98bfa2f953bd4d20dc2feb1d6dc82861c06cc768c77ee90d1` | VSDX ZIP integrity PASS |
| F2 | `fig2_e2e_intervention_scope_final.pdf` | 138344 | `634c0d19be145e310108fe16c21b85298f42a8ca9ea76e61a7c38a5e3926952e` | one-page PDF geometry/render PASS |
| F2 | `fig2_e2e_intervention_scope_final.svg` | 12535 | `3233ee910c8b81944a5608c1acadcb68bde3dff0ca9e5c55fdbc18f5c8ec3db0` | XML/geometry/render PASS |

Accepted repository destinations are:

- `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths_phase5_final.vsdx`;
- `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths_phase5_final.pdf`;
- `docs/paper/manuscript/figures/fig1_v0_v2r_v3r_data_paths_phase5_final.svg`;
- `docs/paper/manuscript/figures/fig2_e2e_intervention_scope_final.vsdx`;
- `docs/paper/manuscript/figures/fig2_e2e_intervention_scope_final.pdf`;
- `docs/paper/manuscript/figures/fig2_e2e_intervention_scope_final.svg`.

These repository copies are byte-identical to all six staged files. Historical
Phase 4 assets and the deterministic Figure 2 preview/specification remain
retained.

F1 visible-content review confirmed the V0 CPU/OpenCV path, V2R pageable raw
staging path, V3R pinned raw staging path, identical V2R/V3R CUDA-preprocessing
nodes, common E2E boundary, and the isolated host raw-staging allocation-type
callout. No forbidden zero-copy, overlap, pipeline, GPU NMS, or second V3R
algorithm appears.

F2 visible-content review confirmed all six conceptual components, the broader
V0→V2R scope, the narrower V2R→V3R host-staging scope, and the mandatory
Amdahl/speedup boundary. No measured stage time, performance prediction, or
causal mechanism appears.

## 3. DOCX compatibility route

The accepted manual PDF/SVG/VSDX files remain authority. LibreOffice's SVG
rasterizer omitted valid Visio marker arrowheads during intake inspection, while
the PDFs retained the approved arrows. The deterministic DOCX build therefore
uses `pdftoppm` at 150 DPI to generate compatibility PNGs for F1 and F2 under
`docs/paper/manuscript/output/phase5_4c_assets/`.

This intermediate route is recorded in the build output and preserves the
original PDF/SVG/VSDX authority. F3 and F4 use their committed deterministic PNG
exports directly. VSDX is never used as a DOCX image payload.

## 4. Final figure architecture

| ID | Caption | Location | Source authority | State |
|---|---|---|---|---|
| F1 | `图1　V0、V2R和V3R数据路径示意` | Section 1.2 | `fig1_v0_v2r_v3r_data_paths_phase5_final.vsdx/.pdf/.svg` | `FINAL_ACCEPTED_INTEGRATED` |
| F2 | `图2　端到端执行概念组成与受控干预范围` | Section 1.3 | `fig2_e2e_intervention_scope_final.vsdx/.pdf/.svg` | `FINAL_ACCEPTED_INTEGRATED` |
| F3 | `图3　V0、V2R和V3R平均帧率比较。误差棒表示5次独立进程级运行FPS的样本标准差。` | Section 4.2 | `fig3_mean_fps_phase5_final.svg/.pdf/.png` | `FINAL_ACCEPTED_INTEGRATED` |
| F4 | `图4　V0、V2R和V3R平均及尾延迟比较。（a）各路径绝对延迟；（b）V3R相对V2R的冻结变化，其中负值表示降低/更快，正值表示升高/更慢。Mean、P95和P99均基于每种路径合并后的5400个逐帧延迟样本统计。` | Sections 4.2–4.4; one figure instance | `fig4_mean_tail_latency_phase5_final.svg/.pdf/.png` | `FINAL_ACCEPTED_INTEGRATED` |

F3 candidate hashes:

- SVG: `5438d61eeff785d850929809755e34ab42c35f1f122ebe2639bd2c434f19128a`.
- PDF: `74b05f78d43b7883d06f9bcc381db93fdce8c9d6016a0f161a1c81866a6fff88`.
- PNG: `d33ec800d58fde8e9639c1bde4e1962f04616a58ea2e9ea6d2b51a975c4d7325`.

F4 candidate hashes:

- SVG: `672fc9d5ed235195ecc75b6a86f7d0dfadd7f6fd7929b636258607e31ce87af6`.
- PDF: `e6311442c0ad2dd8940cc15d3de8e641956dc27bfdfd58ee711257941c2dd22a`.
- PNG: `2436fddee6cbd4b20099ae79bae97e32ffa4ad5a5be45b4b0ceaf3a37fdeb84c`.

F1, F2, and F4 span the full text width. F3 remains a single-column figure.
All drawings are inline, centered, unclipped, and paired with their captions.

## 5. Final table architecture

| ID | Caption | Location | Authority | Content status |
|---|---|---|---|---|
| T1 | `表1　V0、V2R和V3R受控数据路径配置与比较变量` | beginning of Section 2 | `table1_controlled_path_matrix_spec_v1.0.md` | exact governed contents integrated |
| T2 | `表2　平台、模型、数据集和统一运行协议` | Section 3.1 | former T1 | scientific content byte-identical at Markdown table-row level |
| T3 | `表3　V0与V2R任务级正确性验证结果` | Section 4.1 | former T2 | scientific content byte-identical at Markdown table-row level |

T1 uses a native full-width three-line Word table. T2 and T3 retain their
existing native three-line treatment. V3R companion identity remains prose only.

## 6. Numbering and cross-reference migration

- Current F1 → target F1; publication source upgraded; primary role retained in Section 1.2.
- New conceptual asset → F2 in Section 1.3.
- Former F2 → F3 in Section 4.2.
- Former F3 → F4 in Sections 4.2–4.4.
- New controlled-path matrix → T1 at the beginning of Section 2.
- Former T1 → T2 in Section 3.1.
- Former T2 → T3 in Section 4.1.

Source and rendered validators confirm exactly one caption for each F1–F4 and
T1–T3, valid preceding callouts, sequential caption order, no orphan callouts,
and no stale out-of-range figure/table identities.

## 7. Figure 4 panel audit

- Panel A: absolute Mean/P95/P99 latency for V0/V2R/V3R.
- Panel B: frozen V3R changes relative to V2R.
- Panel B range: fixed `-5%` to `+5%`.
- Explicit zero line: present.
- Exact labels: `-4.0349%`, `+0.1514%`, `-0.1184%`.
- Tail interpretation: `MIXED`.
- No broken axis, zoom, significance, causal attribution, red/green semantics,
  or consistent-tail-improvement implication.

## 8. Scientific regression

The formal results remain unchanged:

1. V2R/V0 FPS ratio: `2.236671×`.
2. V2R/V0 mean-latency reduction: `55.4519%`.
3. V3R/V2R FPS: `+4.0738%`.
4. V3R/V2R mean latency: `-4.0349%`.
5. V3R/V2R P95: `+0.1514%`, higher/slower.
6. V3R/V2R P99: `-0.1184%`, lower/faster.

Tail remains `MIXED`. Contribution count remains exactly `2`. No new
scientific fact, experiment, metric, protocol, mechanism, or contribution was
introduced. Title, abstracts, keywords, conclusion, bibliography, citation
architecture, and all display-equation source blocks remain unchanged.

## 9. Build and validation

Full:

- Build: `PASS`.
- DOCX SHA-256: `5e0e8781ca3e85329b6080d3c973cd109463196cc52806e07f9ee266590d400b`.
- LibreOffice PDF render: `12` A4 pages.

Anonymous:

- Build: `PASS`.
- DOCX SHA-256: `deccf6446516af3473c033e2755d13213300fab0e8575c365860c0b2306030e9`.
- LibreOffice PDF render: `12` A4 pages.

Passed checks:

- six manual files present, non-empty, hashed, structurally valid, and renderable;
- staged/repository manual-asset byte identity;
- F1/F2 scientific-scope and prohibited-mechanism inspection;
- F1–F4 current authority and exact caption/callout validation;
- T1 exact specification identity;
- former T1→T2 and former T2→T3 table-content identity;
- Full and Anonymous authoritative builds;
- citation source and rendered bibliography validation;
- Full/Anonymous bibliography identity;
- anonymous identity scan and scientific-body parity;
- journal-format mechanical validation;
- four inline figure relationships and three native tables;
- DOCX ZIP/XML integrity;
- eight display OMML equations in each build;
- T1/T2/T3 equation-block identity;
- six frozen results and directionality;
- tail `MIXED` and contribution count `2`;
- rendered 12-page A4 flow review for clipping, sizing, caption pairing, and
  table integrity;
- `git diff --check`.

## 10. Remaining manual review

Final Microsoft Word visual review of integrated F1–F4 and T1–T3 remains
`USER_MANUAL` before Phase 5.4C closes. The review should open the final Full and
Anonymous DOCX files in Microsoft Word, update fields if requested, inspect at
100% and print width, then save/close/reopen without altering scientific content.
