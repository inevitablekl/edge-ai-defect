# Paper Phase 5.6G-FMT-R1 — Official Format Remediation Report

## 1. Verdict and repository baseline

Verdict: `PHASE56_SUPERVISOR_REVIEW_FREEZE_CANDIDATE`.

- Baseline: `1fde334f44e11e7aa355efd275a56e41f70426b8` (`HEAD = origin/main`, clean worktree/index).
- Scope: source-level format remediation, deterministic rebuild, validation, and mechanical QA only.
- Scientific content: frozen; no experiment, benchmark, inference, profiling, or result change.
- Submission status: `SUPERVISOR_REVIEW_FORMAT = READY`; `STRICT_SUBMISSION_FORMAT = NOT_YET_CLAIMED`.

## 2. Title decision applied

The previous Chinese title failed the official 22 pt single-line gate: it rendered as two lines, with an estimated overflow of 5.673 cm. Main AI therefore replaced the title pair as a positioning refinement:

- Chinese: `面向Jetson端TensorRT INT8工业缺陷检测的输入数据路径重构` → `Jetson端工业缺陷检测的输入数据路径重构`.
- English: `Input Data-Path Reconstruction for TensorRT INT8 Industrial Defect Detection on Jetson` → `Input Data-Path Reconstruction for Industrial Defect Detection on Jetson`.

The new Chinese title contains 16 Chinese characters plus the retained Latin token `Jetson`, satisfying the official “generally no more than 20 Chinese characters” rule. TensorRT INT8 remains present in the abstract, keywords, introduction, environment/model disclosure, methods, experiments, Table 2, results, and conclusion.

## 3. Title mechanical render gate

The real pipeline was used: reference DOCX → Pandoc → Lua filter → DOCX postprocessors → final DOCX → LibreOffice PDF.

| Item | Official source style | Available width | Rendered lines | Maximum rendered line width | Break | Result |
|---|---|---:|---:|---:|---|---|
| Chinese title | 22 pt, bold, SimSun, centered | 16.401 cm | 1 | 14.686 cm | No | PASS |
| English title | 14 pt, bold, Times New Roman, centered | 16.401 cm | 1 | 15.486 cm | No | PASS |

The Linux mechanical environment substitutes Noto Serif CJK SC for SimSun and Liberation Serif for Times New Roman. The OOXML source contract retains the official font names. Final Microsoft Word Desktop rendering remains a human QA action.

## 4. Official template remediation

The deterministic reference builder, generated reference DOCX, and style map now implement:

- Chinese title: 22 pt, bold, SimSun/宋体, centered.
- Chinese authors: 14 pt, KaiTi/楷体, centered, non-bold.
- English title: 14 pt, bold, Times New Roman, centered.
- English authors: 10.5 pt, bold, Times New Roman, centered, matching the extracted effective style.
- Footer distance: 907 twips. A4 and margins remain 1361/1134/1304/1304 twips (top/bottom/right/left); header distance remains unchanged.
- Body and compatibility body styles: first-line indent 438 twips, with the existing exact 16 pt line-spacing contract retained.
- Abstract/keyword labels and bodies: one paragraph per semantic item, with label typography carried by run-level character styles.

Official-format authority SHA-256 values:

- Reference requirements: `5ef440b270b73bad6a57ade6a68e35032c6a5e9829dbd45c05b4574dabb0f651`.
- Format requirements: `e29119e21dfd567f79a018049d95193f409229fd1470322554aa2492f1d0594d`.
- Figure requirements: `160960cdfcc73896cb443a1b7eeec91e9ad419febc4710bafff5b1882636138a`.
- Table requirements: `1764dd6bb74e4ea850aad2fd71f87a1a92badfd7d6854edd8ff9db7d09a0f009`.
- Converted format-authority DOCX: `e26cbd73c866a1cd37469036c1581bd8899a84674877e1246740cf11e4c5445d`.
- Generated reference DOCX: `abb24745a345e21c69e5d3a4c1fb1763c5eaeb8093adc699a4455be100cd1d2e`.

## 5. Heading wrap remediation

The heading was shortened as authorized:

`2.2 V2R：pageable原始图像暂存与GPU输入形成` → `2.2 V2R：pageable暂存与GPU输入形成`.

PDF bounding-box validation inspected 23 rendered heading lines, including the unnumbered reference heading. Wrapped headings: zero in both Full and Anonymous proofs. The 2.2 heading is one line.

## 6. Abstract, body, and footer remediation

- Chinese and English abstract/keyword labels now share their body paragraph and retain distinct label fonts/boldness at run level.
- Chinese abstract length remains 317 Chinese characters; Chinese and English keyword counts remain five.
- All relevant body styles use the official extracted 438-twip first-line indent.
- Every manuscript section uses the official 907-twip footer distance; page geometry and alternating single/two-column transitions are unchanged.
- Full first-page author biography remains in the first-page footer; Anonymous contains no author identity or biography residue. Both variants retain two PAGE fields.

## 7. Table remediation

- Tables 3 and 4 now use 108-twip left/right cell margins.
- Every row in all four tables is protected with `cantSplit`.
- The first row of every table is marked as a repeating header; the Table 4 repeat-header contract is preserved.
- Three-line borders, table widths, row counts (10/9/3/6 data rows), pagination, and content are unchanged.

## 8. NVIDIA reference final records

The cited objects are real official online NVIDIA documentation, so the three incomplete `[M]` records were converted to journal-compliant `[EB/OL]` entries. The governed access date is 2026-08-07.

| Record | Source carrier | Final type | Verified metadata | Access date | Official URL/source |
|---|---|---|---|---|---|
| TensorRT 10.3 Release Notes | Official NVIDIA online PDF | `[EB/OL]` | NVIDIA Corporation; exact title/version; 2024 release year | 2026-08-07 | `https://docs.nvidia.com/deeplearning/tensorrt/archives/tensorrt-1030/pdf/TensorRT-Release-Notes.pdf` |
| CUDA C++ Best Practices Guide: Release 12.6 | Official NVIDIA archived HTML documentation; archived official PDF evidence dated 2024-11-14 | `[EB/OL]` | NVIDIA Corporation; exact title/release; 2024 | 2026-08-07 | `https://docs.nvidia.com/cuda/archive/12.6.0/cuda-c-best-practices-guide/index.html` |
| CUDA C++ Programming Guide: Release 12.6 | Official NVIDIA archived HTML documentation; archived official PDF evidence dated 2024-08-01 | `[EB/OL]` | NVIDIA Corporation; exact title/release; 2024 | 2026-08-07 | `https://docs.nvidia.com/cuda/archive/12.6.0/cuda-c-programming-guide/index.html` |

No publication place, publisher location, or unsupported date was invented. The source and rendered-reference validators require URL/access-date completeness for every `[EB/OL]` item and a verified year for these three records. Full and Anonymous bibliographies are identical.

## 9. Validator governance

`validate_journal_format_docx.py` no longer pins an obsolete reference-DOCX hash or old project assumptions. It verifies official title/author styles, footer distance, body indent, same-paragraph front matter, run-level label styles, table margins and pagination properties, title/heading PDF layout, five equations, figures, geometry, page fields, biography/anonymity, and section transitions.

The validator reports, exactly:

```text
SUBMISSION_EXCEPTION_MATHTYPE=DOCUMENTED_SUBMISSION_EXCEPTION
SUBMISSION_EXCEPTION_VISIO_ORIGIN=DOCUMENTED_SUBMISSION_EXCEPTION
```

It does not report either exception as PASS or NOT_APPLICABLE.

## 10. Submission-production exceptions

- `SUBMISSION_EXCEPTION_MATHTYPE = OPEN`: five equations remain visually correct OMML. Literal MathType-object conversion is deferred to submission production and does not block supervisor review.
- `SUBMISSION_EXCEPTION_VISIO_ORIGIN = OPEN`: F1/F2 retain deterministic structural SVG/PDF authority, F3/F4 retain deterministic Matplotlib SVG/PDF authority, and DOCX uses frozen high-resolution PNG compatibility payloads. No redraw or manual figure edit was performed.

## 11. Builds and hashes

| Artifact | SHA-256 | Pages/result |
|---|---|---|
| Full DOCX | `a018a6eca35b7c36fb52ec64744b4263edb403f920f28961882ce0917b87fb0c` | Build PASS |
| Anonymous DOCX | `5a001f2c3fe87bc3401e07ca43b04794fc85815e1a31e4483299fd9ce185cc6c` | Build/anonymity/parity PASS |
| Full mechanical PDF | `fe65d8f2b958bbd11e384e096dcdcad6ef45c2ddc84e281d85d2825a7d84e843` | 10 pages, A4 |
| Anonymous mechanical PDF | `17908a4c028c97a35198747a79545dd8bb71a1be066950db9c2409f7c3b8d4f9` | 10 pages, A4 |

Page count remained 10 naturally; no compression was applied to force it.

## 12. Mechanical QA

All 20 pages were visually inspected. The check covered both titles, full and anonymous front matter, Chinese/English author areas, abstracts, keywords, first-line indents, all headings, Figures 1–4, Tables 1–4, five equations, references, author biography/footer, page numbers, and column transitions. No clipping, overlap, blank figure, broken table, unintended heading wrap, or title wrap was observed.

## 13. Scientific non-regression

The frozen claims remain unchanged:

- V0/V2R/V3R FPS: `54.600 / 122.122 / 127.097`.
- Mean latency: `18.273 / 8.140 / 7.812 ms`.
- V0→V2R: `2.24× / −55.45%`.
- V2R→V3R: `+4.07% / −4.03%`; P95 `+0.15%`; P99 `−0.12%`.
- Nominal copy payload: `4.9152 / 0.1200 MB/frame`; ratio `40.96×`.
- Precision `0.6913`; Recall `0.6991`; mAP50 `0.6476`; mAP50-95 `0.3523`.
- Contributions: 2; figures: 4; tables: 4; display equations: 5.

## 14. Remaining format matrix and open findings

All mandatory automated items are `MATCH` or `EQUIVALENT`: title/author styles, body indent, footer distance, same-paragraph abstract/keywords, unwrapped headings, T3/T4 cell margins, table pagination, and complete online reference metadata.

Open findings are limited to:

1. Microsoft Word Desktop human QA pending.
2. MathType literal-object submission-production exception.
3. Visio/Origin literal-software submission-production exception/editor acceptance decision.

The updated freeze manifest is `docs/paper/phase5_6/phase56_final_freeze_manifest.json`. A single focused local commit contains the remediation; no push, tag, merge, or amend is performed.
