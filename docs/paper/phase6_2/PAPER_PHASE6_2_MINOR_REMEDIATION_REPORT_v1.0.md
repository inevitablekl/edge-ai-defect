# Paper Phase 6.2M — Minor Academic Remediation Report

## 1. Verdict

`PHASE_6_2_MINOR_REMEDIATION_IMPLEMENTED`

The two minor independent-review findings are closed through three strictly
localized language edits. Phase 6.1 scientific and narrative architecture is
unchanged.

Final content-gate state:

- `IR-F01 = CLOSED`;
- `IR-F02 = CLOSED`;
- `BLOCKING = 0`;
- `MAJOR = 0`;
- `MINOR = 0`;
- `PHASE_6_1_CONTENT_ARCHITECTURE = ACCEPTED`;
- `PHASE_6_2_INDEPENDENT_REVIEW = SATISFIED`;
- `SCIENTIFIC_NONREGRESSION = PASS`;
- `CONTENT_RECONSTRUCTION_GATE = CLOSED`;
- `READY_FOR_PHASE_6_3_TARGETED_FORMAT_REMEDIATION`.

This does not mean `HFUT_SUBMISSION_READY`.

## 2. Independent-review source verdict

The governing independent-review disposition was:

- final verdict: `PASS_WITH_MINOR_REMEDIATION`;
- blocking findings: 0;
- major findings: 0;
- minor findings: 2;
- return to Phase 6.1: no;
- new experiments: no;
- new theory/formulas: no.

Only IR-F01 and IR-F02 were authorized. No additional academic remediation was
inferred.

## 3. Baseline

The mandated preflight matched the expected pushed Phase 6.1 baseline:

- repository: `/home/orin/edge-ai/edge-ai-defect`;
- branch: `main`;
- initial `HEAD`: `729dc62ca47e53f144b5882d6a28749a10906dcb`;
- initial `origin/main`: `729dc62ca47e53f144b5882d6a28749a10906dcb`;
- initial worktree: clean;
- initial index: clean;
- baseline commit message: `paper: reconstruct Phase 6.1 academic narrative`.

No reset, checkout, restore, clean, rebase, merge, push, tag, or amend was
performed.

## 4. IR-F01 remediation

Only the first sentence of each abstract was replaced.

Revised Chinese sentence:

> 在边缘工业缺陷检测中，低精度部署可以降低网络侧开销，但即使推理对象已经固定，输入数据路径仍不能由此唯一确定，输入形成及主机—设备数据移动开销也不会自动消除。

Revised English sentence:

> In edge-based industrial defect detection, low-precision deployment can reduce network-side cost; even after the inference object is fixed, however, the input data path is not uniquely determined, and input-formation and host-device data-movement costs are not automatically eliminated.

The edit separates three propositions that were previously compressed into an
imprecise predicate structure: low-precision deployment can reduce
network-side cost; fixing the inference object does not uniquely determine the
input path; input-formation and host-device data-movement costs are not
automatically eliminated.

No other Chinese or English abstract sentence changed.

## 5. IR-F02 remediation

The single Introduction phrase was changed:

```text
由此产生的知识组织问题
→
由此产生的核心评价问题
```

The paragraph structure and its scientific meaning remain unchanged: the gap
is not inadequate technical combination, but the absence of a unified
evaluation object that distinguishes a correctness-preserving coupled
path-level intervention from a single-variable local refinement under one E2E
boundary.

## 6. Exact manuscript files changed

- `docs/paper/manuscript/sections/00_title_abstract.md`;
- `docs/paper/manuscript/sections/01_introduction.md`.

Additional reporting file:

- `docs/paper/phase6_2/PAPER_PHASE6_2_MINOR_REMEDIATION_REPORT_v1.0.md`.

No other tracked file was modified.

## 7. Diff-scope verification

Before the report was added, the exact manuscript diff was:

```text
2 files changed, 3 insertions(+), 3 deletions(-)
```

Manual diff inspection confirmed:

- Chinese abstract: first sentence only;
- English abstract: first sentence only;
- Introduction: one localized terminology replacement only.

Sections 1–5 after the Introduction, references, CSL, all figures, figure
generators, tables, equations, builders, OOXML postprocessors, validators,
data, and implementation code were not changed.

## 8. Chinese/English abstract semantic alignment

`ABSTRACT_BILINGUAL_ALIGNMENT = PASS`

Both revised sentences communicate the same scientific sequence:

```text
low-precision deployment reduces network-side cost
-> fixed inference object does not uniquely determine input data path
-> path-related input/data-movement costs are not automatically removed
```

The alignment is scientific rather than word-for-word. Neither sentence adds
V0/V2R/V3R, new technical names, numerical evidence, theory, or claims.

## 9. Scientific non-regression

The existing Phase 6.1 validator passed before and after the production build:

`PHASE61_SCIENTIFIC_NONREGRESSION = PASS`

Preserved without change:

- `P=(R,F,M,E)`, `B(P)`, `T_E2E(P)`, and FPS definition;
- P0-to-P2 and P2-to-P3 semantics;
- correctness admission condition;
- RQ1 and RQ2;
- model, Engine, workload, task metrics, FPS, latency, percentages, P95/P99;
- experimental protocol;
- causal, statistical, and generalization boundaries;
- Sections 1–5 outside the one Introduction phrase;
- Figures 1–3 scientific content.

The overclaim audit again classified all 18 matches as legitimate
negation/boundary language and found zero violations.

## 10. Full build

Command:

```bash
scripts/paper/build_manuscript_docx.sh --build-full
```

Result: `PASS`.

- output: `docs/paper/manuscript/output/draft_full.docx`;
- size: 469843 bytes;
- SHA256: `73bbcd2f51a7ea65f349c2d345ac606a67a49c444f71bed64deebd122f2802a4`.

## 11. Anonymous build

Command:

```bash
scripts/paper/build_manuscript_docx.sh --build-anonymous
```

Result: `PASS`.

- output: `docs/paper/manuscript/output/draft_anonymous.docx`;
- size: 469145 bytes;
- SHA256: `ae6ad31d84b2d4e1e3b8355a3c655802a7f88d03c6373cdb90d85d7cf9def5a6`.

## 12. Validators

The production path reported:

- heading validation: `PASS`;
- citation validation: `PASS` — 27 bibliography entries, 22 cited, zero
  unresolved;
- static cross-reference validation: `PASS`;
- rendered bibliography validation: `PASS`;
- structural reference typography validation: `PASS`;
- Full manuscript validation: `PASS`;
- anonymity scan: `PASS`;
- Full/Anonymous scientific parity: `PASS`;
- Phase 5.9C integration: `PASS`;
- Phase 6.1 scientific non-regression: `PASS`.

Mechanical Full and Anonymous PDFs were regenerated. Both remain eight-page
A4 documents, Figure 1 remains on page 4, and the revised abstract renders
readably without catastrophic reflow.

Mechanical PDF hashes:

- Full: `fcb323e713b8d662fce17dc8a12640e1d183e9b5dc5cde486a91213839e3d045`;
- Anonymous: `ed0b71b50c568a320a6fc2501decc0a549dcf5e4c2bc93cff078d9030455fecf`.

Generated DOCX/PDF files remain ignored derived artifacts, not manuscript
source.

## 13. Open Phase 6.3 format issues

The following known issues remain deliberately untouched:

- Table 3 pagination;
- Figure 2/3 final layout;
- visible equation numbering;
- global reference formatting, DOI policy, and `等 -> et al.` treatment;
- final HFUT figure typography;
- Visio, Origin, and MathType conversion;
- Microsoft Word Desktop and Document Inspector workflow.

No Phase 6.3 work was executed.

## 14. Git status

Before the single commit, the only tracked changes are the two authorized
manuscript files and this report. There are no unexplained changes.

`UNEXPECTED_DIFF = NONE`

## 15. Commit

Authorized commit message:

```text
paper: close Phase 6.2 minor academic findings
```

Commit identity in this self-contained report:
`COMMIT_CONTAINING_THIS_REPORT`.

The immutable commit SHA is supplied in the external handoff because embedding
the commit's own SHA would require an amend or a second commit.

## 16. Next action

STOP.

Return the Phase 6.2M report and commit information to the Main Project AI.

Do not execute any additional academic reconstruction.

The manuscript content gate is ready to advance to
Phase 6.3 Targeted HFUT Format Remediation.
