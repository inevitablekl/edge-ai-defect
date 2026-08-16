# Paper Phase 5.7E — Targeted Scientific Restoration Report

## 1. Verdict

`PHASE57E_TARGETED_RESTORATION_CANDIDATE`

- Full mechanical manuscript: 7 A4 pages.
- Anonymous mechanical manuscript: 8 A4 pages.
- The hard `FINAL_MECHANICAL_PAGES <= 8` gate passes.
- All five Phase 5.7D D-class findings are closed; E-class findings remain zero.

## 2. Repository and authority state

- Starting branch: `main`.
- Starting `HEAD = origin/main`: `63c6a23a1412f9954da9e3ca14fe8fff8afb9fd9`.
- Starting worktree and index: clean.
- Phase 5.6 historical paths changed: none (`git diff -- docs/paper/phase5_6` is empty).
- Phase 5.7B remains the compression checkpoint; its report and manifest were not modified.
- No experiment, inference, benchmark, profiling, literature-search, or scientific-data generation was performed.

## 3. Targeted restorations

### D1 / R1 — V2R interpolation contract

Section 2.2 now states that GPU resize semantics were aligned against the V0 OpenCV 4.5.4 `INTER_LINEAR` preprocessing contract. The statement is explicitly bounded to the frozen implementation and workload and does not claim general CUDA/OpenCV equivalence.

### D2 / R2 — Reproduction parameters and V2R gate outcome

Section 2.4 restores confidence threshold 0.25, IoU threshold 0.45, `max_nms=30000`, `max_det=300`, and class-aware single-label processing. It also explicitly states that V2R passed the predefined task-level difference-threshold check. The six publication-hidden internal gate values remain absent. The frozen-workload, deterministic V3R recomputation, and identity/lifecycle provenance chain remains present.

### D3 / R3 — Complete Type-7 definition

Section 3.3 now defines the sorted samples, `p=0.95/0.99`, `h=1+(n-1)p`, `j=floor(h)`, `gamma=h-j`, and `Q_p=(1-gamma)x_(j)+gamma x_(j+1)` with boundary semantics, all in inline prose. Mean FPS remains the arithmetic mean of five independent process-level values; error bars remain their sample standard deviation; latency statistics remain descriptive mean/P95/P99 over 5400 pooled samples per path, without confidence intervals, hypothesis tests, or significance inference.

### D4 / R4 — Process-level repeated observation

Section 4.4 now explains that the V2R/V3R FPS ranges and corresponding mean-latency ranges do not overlap, so the approximately 4% mean difference is repeated across five independent processes rather than generated solely by one anomalous process. It immediately preserves the independent, unpaired design and the prohibition on significance inference.

### D5 / R5 — Related-work positioning depth

Section 4.5 now explains why GPU preprocessing, host staging, complete E2E coverage, task correctness, and percentile tail latency are the five relevant positioning dimensions. It relates only the five already governed works to their complementary scopes and preserves the existing classification rule and qualitative-positioning boundary. No first, only, unique, superiority, or cross-paper performance-ranking claim was added.

## 4. Figure, table, and caption non-mutation

- Figures remain 4; tables remain 4.
- F1–F4 image assets are unchanged. F2 remains 160×62 mm and its PNG SHA-256 remains `d0cd2496420fa46eb1950bdef33af170891ffb043dd87f8f13e6d08238b07563`.
- T1–T4 data and structure are unchanged; Table 3 remains the accepted compact two-column representation and Table 4 remains the accepted six-column qualitative comparison.
- All F1–F4 and T1–T4 caption text is unchanged; caption non-whitespace characters remain 383.
- One pagination-only source adjustment moved the unchanged Figure 2 callout/caption block from immediately after Section 2.2 to the end of Section 2.3. This removed an avoidable page imbalance without changing the figure asset, caption text, scientific content, styles, or geometry.

Frozen/accepted asset authorities:

| Item | SHA-256 |
|---|---|
| F1 PNG | `9fcd9388b6d12bfc027adfb7c0a1aac8690a324f7b987efe6229b7109e4fcb05` |
| F2 PNG | `d0cd2496420fa46eb1950bdef33af170891ffb043dd87f8f13e6d08238b07563` |
| F3 PNG | `dfa125e8d20c28c93cb8a210417d72103988057cfd2bca371f2bd1c17a802ea9` |
| F4 PNG | `c30ee465b6707064819504994c569d48a01067602b19c5a4c79b4b90fe296e96` |
| T1 source | `e04ebb50827e5c996d284de8e535707b7996b4d2b02b1cf8a27b2f078b78938c` |
| T4 source | `7273b89b42bf340e79ca16b9e429c4ec9a297b8a4adb9808cd4525edaecd2f16` |
| Caption authority | `5094c03c4646f1d61ce1434101383469582bad793aca0c1e5be62f17625acc84` |

## 5. References and equations

- Bibliography library: 27 entries; cited/rendered: 23; unresolved: 0; uncited library entries: 4.
- No dead rendered reference is present, and none of the three references removed in Phase 5.7B was restored.
- The related-work restoration uses only already-rendered references.
- Display equations remain exactly 2: the complete E2E boundary and process-level FPS definition.
- The restored Type-7 definition remains inline and creates no third display equation.

## 6. Scientific non-regression

All frozen numerical results are unchanged:

| Quantity | Frozen value |
|---|---|
| FPS, V0 / V2R / V3R | 54.600 / 122.122 / 127.097 |
| Mean latency (ms), V0 / V2R / V3R | 18.273 / 8.140 / 7.812 |
| V0→V2R | 2.24× FPS; −55.45% mean latency |
| V2R→V3R | +4.07% FPS; −4.03% mean latency |
| P95 / P99 | +0.15% / −0.12% |
| Nominal input-copy payload | 4.9152 / 0.1200 MB per frame; 40.96× |
| Correctness tuple | 0.6913 / 0.6991 / 0.6476 / 0.3523 |

The 40.96× quantity remains a nominal payload ratio, not measured traffic or component-level causal attribution. E-class scientific findings remain zero.

## 7. Official-format non-regression

The official HFUT DOCX validator passes for A4 page geometry, official margins and columns, 10.5-pt body text, 438-twip first-line indent, 907-twip footer distance, heading/table styles, and abstract/keyword layout. The Chinese title remains one unclipped centered line in 22-pt bold SimSun, with the automatic line-box and `snapToGrid=false` fix intact. The frozen reference DOCX SHA-256 remains `31b65361f50262240630d1453637218e2455b150dadc653edfa8e535439c55c0`.

## 8. Build and output hashes

- Full build: PASS.
- Anonymous build: PASS.
- Full/anonymous scientific-body and bibliography parity: PASS.
- Anonymous identity scan: PASS.
- DOCX ZIP validation: PASS.
- Phase 5.7E targeted-restoration validator: PASS.

| Output | SHA-256 |
|---|---|
| Full DOCX | `b2081813530e115dcaa3ee633e76434eef89d4ea17468665b05ff47bb8f7a5ac` |
| Anonymous DOCX | `41b2cbd0982eb4d5b40646bfde639d2abbe2ed698c59005c9c6b23aa09f2eff1` |
| Full mechanical PDF | `ce8cdb6ec43fc80dc1a6ab3e031486ccc7884ad72870e8f58a660a23e7ef0de9` |
| Anonymous mechanical PDF | `0806892deb5b9651a1cef49dada65b62ee4b1e6e33aa16340c67049aa03e7dab` |

## 9. Mechanical QA

Every page of both final PDFs was raster-inspected. No heading wrap, overfull line, formula clipping, table overflow, awkward orphan paragraph, or column-transition regression was observed. The restored Section 3.3 inline formula wraps under the existing adaptive Word-safe paragraph contract without clipping or abnormal line expansion. Table 4 remains readable and references remain balanced in the Full manuscript.

The Anonymous manuscript retains the pre-existing `--anonymous-t4-page-break` rendering-integrity guard: page 6 has intentional lower-page whitespace before Table 4 begins on page 7, and references continue onto page 8. This is expected, remains inside the page gate, and is not a new format or scientific-content change.

## 10. Before/after restoration metrics

| Metric | Phase 5.7B | Phase 5.7E | Change |
|---|---:|---:|---:|
| Full mechanical A4 pages | 7 | 7 | 0 |
| Anonymous mechanical A4 pages | 7 | 8 | +1 |
| Body-source CJK characters | 3404 | 3578 | +174 |
| Body prose paragraphs | 42 | 42 | 0 |
| Display equations | 2 | 2 | 0 |
| Rendered references | 23 | 23 | 0 |
| Figures | 4 | 4 | 0 |
| Tables | 4 | 4 | 0 |
| Caption non-whitespace characters | 383 | 383 | 0 |

Metric method is unchanged from Phase 5.7B: Sections 01–06, excluding HTML comments/front matter; CJK counts include visible headings, captions, and table content; prose paragraph counts exclude headings, Markdown table rows, and display-equation blocks.

Approximate restoration footprint in source/rendering:

| Location | Added/restored source footprint | Approximate rendered footprint |
|---|---:|---:|
| 2.2 | 88 characters; 41 CJK | about 4 double-column lines |
| 2.4 | 86 characters; 31 CJK | about 5 double-column lines |
| 3.3 | 132 characters; 29 CJK | about 5–6 double-column lines |
| 4.4 | 92 characters; 81 CJK | about 4–5 double-column lines |
| 4.5 | 259 characters; 139 CJK | about 7–8 double-column lines |

These local source-footprint figures include compact inline notation/citations where applicable and are descriptive, not independent manuscript totals.

## 11. Phase 5.7D closure matrix

| Finding | Required closure | Status |
|---|---|---|
| D1 | V2R OpenCV 4.5.4 `INTER_LINEAR` alignment contract | CLOSED |
| D2 | Task postprocessing parameters and explicit V2R gate outcome | CLOSED |
| D3 | Complete inline Type-7 definition | CLOSED |
| D4 | Process-level repeated-observation explanation | CLOSED |
| D5 | Related-work positioning depth | CLOSED |
| E-class | No scientific-integrity error | ZERO |

## 12. Open findings and submission exceptions

- `SUBMISSION_EXCEPTION_MATHTYPE = OPEN` (unchanged).
- `SUBMISSION_EXCEPTION_VISIO_ORIGIN = OPEN` (unchanged).
- Mechanical page count and raster QA use LibreOffice PDF rendering; final Microsoft Word Desktop visual recheck remains required before submission.
- No push, tag, merge, or amend is part of this phase.
