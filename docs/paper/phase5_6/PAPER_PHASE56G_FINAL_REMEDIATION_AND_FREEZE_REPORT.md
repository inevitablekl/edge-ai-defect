# Paper Phase 5.6G — Final Minor Remediation and Manuscript Freeze Candidate

## 1. Starting authority and repository state

- Starting commit: `332fabdf34ac377b7242193872fb9b9029ac937e`.
- Starting branch: `main`; local `HEAD` equaled `origin/main` and the worktree/index were clean.
- Work was limited to manuscript wording, the Table 4 evidence audit, Figure 4 annotation, build/validation support, and freeze records. No experiment, benchmark, inference, or profiling run was performed.

## 2. Review inputs

The review inputs were the Phase 5.6F minor findings plus external independent minor-review findings. Verification used the existing manuscript sources, frozen evidence, local full-text related-work sources, journal-format rule, CSL decision, and three locally archived NVIDIA manuals. The external review text is not reproduced and no external review copy was created.

## 3. Final titles

- Chinese: `面向Jetson端TensorRT INT8工业缺陷检测的输入数据路径重构`
- English: `Input Data-Path Reconstruction for TensorRT INT8 Industrial Defect Detection on Jetson`

Both titles occur exactly once in Full and Anonymous DOCX outputs; the superseded titles are absent from publication-facing content.

## 4. Async/H2D wording correction

Publication-facing wording no longer infers actual asynchronous execution merely from the API name. The principal corrections were:

- `异步二维主机到设备复制` → `二维主机到设备复制`.
- `异步二维H2D复制` → `通过 cudaMemcpy2DAsync 执行二维H2D复制`.
- `asynchronous two-dimensional host-to-device copying` → `two-dimensional host-to-device copying`.
- V2R is described as pageable source storage and V3R as pinned source storage; both use the `cudaMemcpy2DAsync` API, remain single-frame sequential paths, and do not use cross-frame transfer/compute overlap.
- The conditional CUDA fact is retained narrowly: pinned memory can support qualifying asynchronous transfer/compute overlap, but benefit and actual execution depend on the implementation.

## 5. Publication-facing internal-language cleanup

Counts were measured over manuscript sections, publication manifests/captions, production SVG text, and production table sources.

| Term | Before | After |
|---|---:|---:|
| `authority` | 8 | 0 |
| `artifact` | 1 | 0 |
| `manuscript-visible` | 1 | 0 |
| `Level-A` | 3 | 0 |
| `Level-B` | 0 | 0 |
| standalone `MIXED` | 6 | 0 |

Machine-readable validator records remain internal build evidence and are not manuscript content.

## 6. Contribution 2

Final wording:

> 2）在统一的任务正确性、E2E延迟、进程级FPS与合并样本P95/P99评价口径下，通过V0→V2R和V2R→V3R两级受控比较，区分完整输入路径重构的主要性能收益与pinned暂存的有限平均增量，并利用5次独立进程考察运行级分布和尾延迟行为。

This presents controlled evidence rather than claiming protocol innovation.

## 7. Neutral RQ2

Final wording:

> RQ2：在GPU预处理、CUDA stream和下游拓扑保持不变时，将pageable原始图像暂存替换为pinned暂存，是否进一步改善平均性能，以及P95/P99是否呈现一致的尾延迟改善？

## 8. Chinese terminology cleanup

The Chinese abstract now uses publication-facing Chinese evaluation terms and the corrected non-assertive H2D description. Mixed internal/implementation shorthand was normalized where it appeared in Chinese prose: detector, host representation, raw-image staging, evaluator, inference artifact, pooled latency, runtime telemetry, and stage-level causal timing now use clear academic Chinese or a Chinese term followed by the necessary API/technical token. `cudaMemcpy2DAsync`, pageable, pinned, TensorRT, CUDA stream, H2D, and E2E remain where technically useful. The English abstract received only the required title and async wording correction. Quantitative claims and scientific scope were preserved.

## 9. Table 4 criteria

The manuscript now defines all seven attributes immediately before Table 4:

1. Edge deployment: actual deployment and reported experiments on an embedded or edge device.
2. Fixed model: compared configurations do not vary detector structure, weights, or model parameters.
3. GPU preprocessing: explicit GPU/CUDA execution of image preprocessing before model inference.
4. Host-memory strategy: explicit study or configuration of host allocation, pinned/pageable, managed, or equivalent strategy.
5. Complete E2E: boundary covers at least preprocessing, model execution, and postprocessing or result handling.
6. Task correctness: task-level detection correctness for the compared deployment/system configuration.
7. Tail latency: P95, P99, or another explicit percentile tail-latency statistic, not merely a mean or maximum.

## 10. Table 4 42-cell audit result

All 6 works × 7 attributes were re-audited using the controlled vocabulary `YES`, `NO_IF_EXPLICIT`, `NOT_REPORTED`, and `NOT_APPLICABLE`. Result: 41 cells unchanged and one conservative downgrade:

- `PRESTO (2025)` × `Complete E2E evaluation`: `YES` → `NOT_REPORTED`.

Reason: PRESTO explicitly defines reported total latency as preprocessing plus GPU model execution; the reviewed text does not establish inclusion of postprocessing or result handling required by the final criterion. The four existing `NO_IF_EXPLICIT` decisions remain supported by explicit exclusions. No unsupported negative inference was added.

## 11. Reference-type audit

The local journal rule and Phase 4 CSL decision specify that archived official manual PDFs render as `[M]`, whereas official webpages render as `[EB/OL]`. The three audited local manuals therefore remain:

- TensorRT 10.3 Release Notes: `[M]`.
- CUDA C++ Best Practices Guide 12.6: `[M]`, 2024.
- CUDA C++ Programming Guide 12.6: `[M]`, 2024.

No unverified TensorRT publication year or date was invented. The rendered bibliography and citation audit both pass.

## 12. Figure 4 textual remediation

The publication annotation changed from internal verdict terminology to:

> P95 +0.15%，P99 −0.12%；变化方向相反

The caption states that the two changes are opposite and do not form consistent tail-latency improvement evidence. Data, geometry, axes, and run-level points were not changed.

New F4 hashes:

- SVG: `9f975e880d220b73b80fcd4ed4b1aecb7969a143eb55192b6d9f363e6a718570`
- PDF: `fccd8310b045abd00fc2b0b531d8b802f33a062092d7fd5c68b40973ae3fcace`
- PNG: `c30ee465b6707064819504994c569d48a01067602b19c5a4c79b4b90fe296e96`

F1–F3 SVG/PDF/PNG hashes are unchanged from the starting commit.

## 13. Scientific non-regression

All frozen results remain unchanged:

- V0/V2R/V3R mean FPS: `54.600 / 122.122 / 127.097`.
- V0/V2R/V3R mean latency: `18.273 / 8.140 / 7.812 ms`.
- V0→V2R: `2.24× FPS`, `55.45%` lower mean latency.
- V2R→V3R: `+4.07% FPS`, `−4.03%` mean latency, `+0.15% P95`, `−0.12% P99`.
- Nominal input-copy payload: `4.9152 / 0.1200 MB/frame`, ratio `40.96×`; it is not reported as measured traffic, bandwidth, H2D time, or causal speedup.
- Task metrics for all paths: Precision `0.6913`, Recall `0.6991`, mAP50 `0.6476`, mAP50-95 `0.3523`.
- Calibration/runtime qualifiers remain: forced cache miss, newly generated and archived cache, no reuse of a pre-existing cache as formal build input, MAXN_SUPER/nvpmodel mode 2, no `jetson_clocks`, no independently archived frequency, and only non-continuous before/after temperature observations.

## 14. Full/Anonymous build

- Output: `docs/paper/manuscript/output/draft_full.docx`.
- SHA-256: `b5fb54d144c12df3ef14bd34686aece91ed3ff8a1b0cd7e08af8b268dd0a7367`.
- Full content, heading numbering, citation source, static cross-reference, rendered bibliography, reference typography, Phase 5.6G freeze-candidate, and journal-format validations: `PASS`.
- Output: `docs/paper/manuscript/output/draft_anonymous.docx`.
- SHA-256: `3cd2343be084affb3145f931ef7397785a50858289db01283e2a85b6232079d4`.
- Anonymous identity scan: `PASS`; Full/Anonymous scientific-body and bibliography parity: `PASS`; Phase 5.6G freeze-candidate and journal-format validations: `PASS`.

## 15. Mechanical visual QA

LibreOffice 7.3.7.2 generated A4 mechanical proofs:

- Full PDF: 10 pages, SHA-256 `d2774dd37609d62d1992b1eea2406c7887d5716eb91e67d2d977b77f780a98eb`.
- Anonymous PDF: 10 pages, SHA-256 `6caf13eb402ec874b840b48ac10ae44e21058384444cda3b74701f7c7bbe6c4e`.

All 20 rendered pages were visually inspected. Titles, abstracts, two-column transitions, four figures, four tables, five equations, repeated Table 4 header, references, page numbering, and anonymity presentation are legible with no clipping, blank figure, overlap, or overflow. The 16 cm and grayscale F4 inspection renders also pass.

## 16. Format protection

The existing Word style contract was preserved with no global format change: 22 heading paragraphs, alternating single/two-column section structure, 4 inline PNG figure fallbacks, 5 formal equations, and 2 page fields. The Chinese title has 18 Chinese characters; the Chinese abstract has 315 Chinese characters; Chinese and English keyword counts are both 5.

## 17. Final inventory

- Figures: 4.
- Tables: 4.
- Display equations: 5.
- Contributions: 2.

## 18. Freeze manifest

The machine-readable freeze record is `docs/paper/phase5_6/phase56_final_freeze_manifest.json`. It records source/build hashes, frozen values, validator outcomes, output hashes, inventory, and the starting commit. Its final-commit field is deliberately self-resolving as the commit containing the manifest; the exact commit is reported after creation of the single local commit.

## 19. Open findings

The only open item is Microsoft Word Desktop human visual QA. There is no unresolved repository-solvable scientific, Table 4, reference-type, or format blocker.

```text
Phase 5.6X Limited Diagnostics = SKIPPED
new experiment = NO
new benchmark = NO
new inference = NO
new profiling = NO
```

## 20. Commit

A single focused local commit contains this report and all authorized changes. Its exact SHA is the commit containing this self-referential report and manifest and is reported in the final handoff. No amend, push, merge, or tag is performed.
