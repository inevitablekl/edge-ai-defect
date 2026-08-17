# Paper Phase 5.9H — Final Symbol Remediation and Supervisor Package Report

## 1. Verdict

`PHASE59H_FINAL_SUPERVISOR_PACKAGE_CANDIDATE`

The sole Phase 5.9G minor finding, m-01, is closed. Table 3 now uses explicit
metric names, the manuscript was rebuilt through the existing validated
pipeline, and a new supervisor package was generated. No other scientific or
narrative content was changed.

Governance state:

- `PHASE59G_MINOR_FINDING_m01 = CLOSED`;
- `PHASE59G_FINAL_SCIENTIFIC_REVIEW = PASS_PENDING_TARGETED_WORD_QA`;
- `POST_M01_WORD_DESKTOP_QA = PENDING_USER_VISUAL_CHECK`.

## 2. Repository baseline

Preflight matched the known Phase 5.9F package commit:

- branch: `main`;
- `HEAD`: `281172ac658463c55640265166f33d6ee7ea0f83`;
- `origin/main`: `281172ac658463c55640265166f33d6ee7ea0f83`;
- worktree/index: clean.

No reset, clean, amend, merge, rebase, push, or tag was performed.

## 3. Phase 5.9G review state

Phase 5.9G reported `PHASE59G_PASS_WITH_MINOR_FIXES` with zero blocking,
zero major, and one minor finding. All other scientific checks passed:

- scientific non-regression: `PASS`;
- path-model/implementation consistency: `PASS`;
- RQ-method-result closure: `PASS`;
- contribution-evidence closure: `PASS`;
- citation-claim non-regression: `PASS`;
- causal-strength non-regression: `PASS`;
- reproducibility: `ADEQUATE`;
- narrative coherence: `COHERENT`;
- new experiment required: `NO`.

## 4. m-01 exact defect

The accepted theory already uses `P` for the path descriptor and `R` for the
cross-boundary representation in `P=(R,F,M,E)`. Table 3 nevertheless used
`P / R / mAP50 / mAP50-95` for Precision and Recall, creating a local symbol
collision.

## 5. Exact source repair

Only the Table 3 header in
`docs/paper/manuscript/sections/05_results.md` was changed:

```text
Path | P / R / mAP50 / mAP50-95
→
Path | Precision / Recall / mAP50 / mAP50-95
```

No abbreviation fallback was needed. No row label, value, caption, theory
symbol, equation, result, reference, or other prose was modified.

## 6. Table 3 before/after

Before:

`Path | P / R / mAP50 / mAP50-95`

After:

`Path | Precision / Recall / mAP50 / mAP50-95`

The three rows remain V0, V2R, and V3R, each with
`0.6913 / 0.6991 / 0.6476 / 0.3523`.

## 7. Scientific non-regression

The frozen publication values remain unchanged:

- V0: `54.600 FPS`, `18.273 ms`;
- V2R: `122.122 FPS`, `8.140 ms`;
- V3R: `127.097 FPS`, `7.812 ms`;
- V0→V2R: `2.24×`, `−55.45%`;
- V2R→V3R: `+4.07%`, `−4.03%`;
- P95: `+0.15%`;
- P99: `−0.12%`;
- nominal payload: `4.9152 MB/frame`, `0.1200 MB/frame`, `40.96×`;
- correctness: `0.6913 / 0.6991 / 0.6476 / 0.3523`.

`SCIENTIFIC_NONREGRESSION = PASS`

## 8. Path-model non-regression

The accepted architecture remains `P=(R,F,M,E)`, with `B(P)` as the derived
nominal input-copy payload descriptor and `T_E2E(P)` as the direct
source-to-pre-sink measured response. No symbols were renamed. `P0→P2`
continues to change `R/F/M` with fixed `E`; `P2→P3` changes only `M`.

`PATH_MODEL_IMPLEMENTATION_CONSISTENCY = PASS`

`RQ_METHOD_RESULT_CLOSURE = PASS`

`CONTRIBUTION_EVIDENCE_CLOSURE = PASS`

`CAUSAL_STRENGTH_NONREGRESSION = PASS`

## 9. Citation/reference non-regression

The rebuild reports 27 bibliography entries, 22 cited/rendered references,
zero unresolved/dead citations, and Full/Anonymous parity `PASS`. No citation,
reference, or claim attachment changed.

## 10. Full/Anonymous build

The existing validated build pipeline passed for both variants. The Full and
Anonymous DOCX artifacts were rebuilt, then corresponding mechanical PDFs were
generated. Anonymous artifacts are validation-only and are not included in the
supervisor package.

## 11. Page count

- Full: `7` pages, A4;
- Anonymous: `7` pages, A4.

No official format compression or page-count optimization was performed.

## 12. Mechanical QA

All 14 rendered pages were inspected. Table 3 is on page 5; `Precision / Recall`
is visible on one line, with no clipping, overlap, table displacement, row
misalignment, or change to mAP50/mAP50-95. The remaining pages show no
unintended reflow, heading wrap, figure problem, equation problem, or reference
problem.

`MECHANICAL_QA = PASS`

## 13. m-01 closure

Publication-visible source and PDF searches confirm that correctness metrics no
longer use isolated `P` and `R` labels. The theory symbols remain available in
their accepted path-model meanings.

`m-01_SYMBOL_COLLISION = CLOSED`

## 14. Old Phase 5.9F package preservation

The historical directory
`docs/paper/phase5_9/supervisor_rereview_package/` was not modified. It remains
the pre-m-01 Phase 5.9F package.

## 15. New package directory

`docs/paper/phase5_9/supervisor_rereview_package_post59g/`

Supervisor-facing files:

- `Jetson端工业缺陷检测的输入数据路径重构_导师复审稿.docx`;
- `Jetson端工业缺陷检测的输入数据路径重构_导师复审稿.pdf`.

The directory also contains the internal package manifest. Anonymous files,
source code, raw evidence, and internal review documents are not included in
the supervisor-facing delivery set.

## 16. DOCX/PDF source hashes

| Artifact | Size | SHA256 |
|---|---:|---|
| Full DOCX | 492905 bytes | `35590824402653e96a87f339f9566684bbfa975c4aae6e32d60e9f981a5d3371` |
| Full PDF | 751469 bytes | `5ded970dd72297998f709805909e42f382fdeb249196f030df7dac4c79ec5908` |
| Anonymous DOCX | 492209 bytes | `2bcfbb2deb77d7d29bbd9e72efb8da2c6884a9705ff40a82e0c95036734546cd` |
| Anonymous PDF | 740362 bytes | `af920a2f74dd51e5805098d6b5477e9f3ec3ab67e3d51eddd2e80de9f8d89f38` |

## 17. Package hashes

- packaged DOCX SHA256: `35590824402653e96a87f339f9566684bbfa975c4aae6e32d60e9f981a5d3371`;
- packaged PDF SHA256: `5ded970dd72297998f709805909e42f382fdeb249196f030df7dac4c79ec5908`.

## 18. Byte identity

Direct `cmp` and SHA256 checks passed:

- package DOCX = rebuilt Full DOCX: `PASS`;
- package PDF = rebuilt Full PDF: `PASS`.

`PACKAGE_BYTE_IDENTITY = PASS`

## 19. PDF freshness verification

The PDF was regenerated from the new Full DOCX and read-only inspected. It is
7-page A4, contains 3 figures, 3 tables, 3 equations, 22 references, the
accepted path model, and the post-m-01 `Precision / Recall` header. The old
`P / R / mAP50 / mAP50-95` header is absent.

`PDF_FRESHNESS = PASS`

## 20. Word Desktop QA status

- `PREVIOUS_PHASE59_WORD_DESKTOP_QA = PASS`;
- `POST_M01_WORD_DESKTOP_QA = PENDING_USER_VISUAL_CHECK`.

The new DOCX has not been represented as having passed a new Word Desktop
inspection.

## 21. Open submission-production exceptions

- `SUBMISSION_EXCEPTION_MATHTYPE = OPEN`;
- `SUBMISSION_EXCEPTION_VISIO_ORIGIN = OPEN`.

Both remain deferred until supervisor approval for submission. No MathType,
Visio, or Origin conversion was performed.

## 22. Commit SHA

`COMMIT_CONTAINING_THIS_REPORT`

The exact immutable SHA is supplied after the single focused commit. Embedding
a commit's own SHA would require an amend or second commit.

## 23. No push / clean worktree

One focused commit will contain the authorized Table 3 source repair, rebuilt
derived artifacts, report, and new package. No push, tag, merge, rebase, reset,
clean, or amend is performed.

## 24. User's only remaining action

Open the new packaged DOCX in Microsoft Word Desktop and inspect Table 3 only.
Confirm that `Precision / Recall` displays normally and that there is no
clipping, wrapping, or table displacement. No complete manuscript rereview is
required.

If that targeted check passes, record:

`MICROSOFT_WORD_DESKTOP_PHASE59H_TARGETED_QA = PASS`

Then the governance state may be upgraded to:

`PHASE59G_FINAL_SCIENTIFIC_REVIEW = PASS`

`READY_FOR_SUPERVISOR_REREVIEW = YES`
