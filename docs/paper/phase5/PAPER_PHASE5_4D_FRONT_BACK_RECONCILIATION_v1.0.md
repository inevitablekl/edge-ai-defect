# Paper Phase 5.4D Front/Back Matter Reconciliation v1.0

## 1. Verdict

`FRONT_BACK_RECONCILIATION_COMPLETE`

## 2. Starting state

- Branch: `main`.
- Starting HEAD: `2777c9727de777daa38e0fdffe6d9ebb66f30e90`.
- Starting subject: `docs(paper): integrate phase5 figures and tables`.
- Starting worktree: clean.
- Starting index: clean.
- Phase state: 5.4A, 5.4B and 5.4C complete; final visual architecture fixed at four figures and three tables; Microsoft Word/PDF final visual review passed before this work unit.

## 3. Reconciliation audit

The front/back matter was compared with the complete stabilized manuscript and
the Phase 5.4A--5.4C governance reports. The audit found that the titles,
abstracts and keyword sets already express the fixed detector and Engine, the
complete tested data paths, the two-level V0/V2R/V3R comparison, the primary
V0--V2R observation, the limited V2R--V3R average increment and the mixed tail
result. They were therefore retained.

The conclusion had one genuine residual mismatch. Its opening framed the object
as the effect of two implementation variables, and its second paragraph could
be read as assigning the measured average increment directly to pinned staging.
The stabilized body instead treats both comparisons as differences between
complete tested configurations and explicitly prohibits interpreting the
`4.0349%` result as an independently measured pinned-memory saving. Two narrow
conclusion edits corrected that mismatch. No scientific-body section was
reopened.

| Item | Verdict | Audit result |
|---|---|---|
| Chinese title | `RETAINED` | Concise Jetson/industrial-defect/INT8/data-path scope; no detector, quantization or generic-framework novelty claim. |
| English title | `RETAINED` | Natural semantic counterpart of the Chinese title with the same bounded scope. |
| Chinese abstract | `RETAINED` | Already states complete configuration comparison, common conditions, result hierarchy and opposite P95/P99 directions. |
| English abstract | `RETAINED` | Semantically aligned with the Chinese abstract and no stronger claim. |
| Chinese keywords | `RETAINED` | Five terms cover Jetson, industrial defect detection, INT8 inference, CUDA preprocessing and data-path optimization. |
| English keywords | `RETAINED` | Five one-to-one semantic counterparts of the Chinese terms. |
| Conclusion | `REVISED` | Complete-configuration object made explicit and independent pinned-memory attribution expressly excluded. |

## 4. Chinese title

Verdict: `RETAINED`.

Before and after:

`Jetson端工业缺陷检测的INT8推理数据路径优化`

Rationale: the title identifies the Jetson context, industrial defect-detection
task, INT8 inference and data-path optimization without implying a new detector,
quantization algorithm, CUDA-kernel algorithm or universal framework. No scope
correction was required.

## 5. English title

Verdict: `RETAINED`.

Before and after:

`Data-Path Optimization for INT8 Inference in Jetson-Based Industrial Defect Detection`

Rationale: it is a natural semantic counterpart of the retained Chinese title
and does not strengthen the novelty or generality claim.

## 6. Chinese abstract

Verdict: `RETAINED`.

The current abstract already follows the required problem/objective, controlled
method, key results and bounded-conclusion sequence. It identifies V0, V2R and
V3R as complete configurations under fixed model, Engine, workload,
correctness and timing conditions. It assigns the primary observed gain to the
complete V2R path, describes V3R as a limited average increment, preserves P95
higher and P99 lower, and rejects a consistent tail-improvement conclusion. It
does not report significance, causal stage timing, lossless INT8 or an
independent pinned-memory saving.

## 7. English abstract

Verdict: `RETAINED`; Chinese/English semantic parity: `PASS`.

The English text conveys the same controlled configurations, statistical
bases, frozen results, result hierarchy, platform/workload boundary and mixed
tail behavior as the Chinese text. Terminology is consistent (`complete
data-path configurations`, `TensorRT INT8 Engine`, `pageable host-memory
staging`, `pinned host-memory staging`, `mean latency`, `P95` and `P99`). It
does not make a stronger causal or universal claim.

## 8. Keywords

Verdict: `RETAINED`.

- Chinese: `Jetson；工业缺陷检测；INT8推理；CUDA预处理；数据路径优化`.
- English: `Jetson; industrial defect detection; INT8 inference; CUDA preprocessing; data-path optimization`.

The five-keyword structure remains semantically aligned and accurately covers
the paper without unsupported search-breadth terms.

## 9. Conclusion reconciliation

Verdict: `REVISED`.

### Change 1 -- research object

Before:

`针对 Jetson 边缘端 INT8 工业缺陷检测中预处理执行位置与主机暂存方式对系统性能的影响`

After:

`针对 Jetson 边缘端 INT8 工业缺陷检测中不同完整数据路径配置的部署性能差异`

This aligns the conclusion with the stabilized complete-E2E-path research
object and the controlled-configuration language in Sections 1--4. It narrows
causal implication rather than strengthening the scientific claim.

### Change 2 -- V2R/V3R attribution boundary

Before summary: V3R was said to provide an average increment after replacing
pageable staging with pinned staging, and the closing sentence described that
increment as support for pinned staging in the current path.

After summary: the conclusion identifies V3R as the complete tested
configuration, states that the result is an E2E observed difference between two
complete tested configurations, expressly denies interpreting `4.0349%` as an
independent pinned-memory saving, and limits the conclusion to V3R's observed
average increment.

This wording is supported directly by Sections 4.3--4.4. It adds no result or
mechanism and preserves P95 higher/slower, P99 lower/faster and `Tail = MIXED`.
The third paragraph's platform/workload limitations and bounded future work were
retained unchanged.

## 10. Claim-boundary and semantic-parity audit

- New detector, model architecture or loss function: `NONE`.
- New quantization, TensorRT or CUDA-kernel algorithm: `NONE`.
- Stage-level causal decomposition: `NONE`.
- Independent pinned-memory saving claim: `NONE`; explicitly rejected.
- Statistical significance or confidence interval: `NONE`.
- Zero-copy, overlap, pipeline or cross-stage multiplication claim: `NONE`.
- Universal/cross-platform performance claim: `NONE`.
- New contribution or theoretical contribution: `NONE`.
- Chinese/English title parity: `PASS`.
- Chinese/English abstract parity: `PASS`.
- Chinese/English keyword parity: `PASS`.

## 11. Frozen-result audit

1. V2R/V0 FPS ratio: `2.236671×`.
2. V2R/V0 mean-latency reduction: `55.4519%`.
3. V3R/V2R FPS: `+4.0738%`.
4. V3R/V2R mean latency: `-4.0349%`.
5. V3R/V2R P95: `+0.1514%`, higher/slower.
6. V3R/V2R P99: `-0.1184%`, lower/faster.

Tail: `MIXED`.

Contribution count: exactly `2`.

New scientific fact: `NONE`.

The read-only scientific body, bibliography, equations, figures and tables are
unchanged relative to the starting HEAD.

## 12. Build and validation

Full manuscript:

- Authoritative build: `PASS`.
- DOCX SHA-256: `d6fc3bbf9905fb83d603f94093429c4488a41f2891c82d47355bca1e0bdd6f61`.
- LibreOffice render: `PASS`, `12` A4 pages.

Anonymous manuscript:

- Authoritative build: `PASS`.
- DOCX SHA-256: `2bece2e3fd93f2e78714ad6ecb3cc11ad22680cb3e257c2e474c8398b70c788a`.
- LibreOffice render: `PASS`, `12` A4 pages.

Pagination remains 12 pages for both builds; front/back-matter reconciliation
caused no page-count change relative to the accepted Phase 5.4C build.

Passed checks:

- Full build and Full structural/content validation;
- Anonymous build, identity scan and scientific-body parity;
- citation-source validation: 27 entries, 26 cited, zero unresolved and one governed unused entry;
- rendered bibliography validation and Full/Anonymous bibliography identity;
- static cross-reference validation: F1--F4 and T1--T3;
- journal-format mechanical validation;
- figure count `4` and native table count `3` in both builds;
- DOCX ZIP/XML integrity;
- `8` display OMML equations in each build and Full/Anonymous equation parity;
- six frozen-result values, comparison directions and mixed-tail wording;
- contribution count exactly `2`;
- read-only scientific-body, bibliography, equation, figure and table authority unchanged;
- `git diff --check`.

## 13. Files changed

- `docs/paper/manuscript/sections/06_conclusion.md`.
- `docs/paper/phase5/PAPER_PHASE5_4D_FRONT_BACK_RECONCILIATION_v1.0.md`.

`docs/paper/manuscript/sections/00_title_abstract.md` was audited and retained
byte-for-byte. No metadata/build support edit was necessary.

## 14. Git disposition

- One focused commit is required for this changeset.
- Required subject: `docs(paper): reconcile title abstract and conclusion`.
- Push: `NO`; the user will push manually.

## 15. Open risks

`NONE`.
