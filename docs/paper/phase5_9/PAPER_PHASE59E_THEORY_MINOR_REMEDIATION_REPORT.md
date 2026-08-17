# Paper Phase 5.9E — Theory Consistency Minor Remediation Report

## 1. Verdict

`PHASE59E_THEORY_MINOR_REMEDIATION_CANDIDATE`

`PHASE59D_MINOR_FINDINGS = CLOSED`

`THEORY_RECONSTRUCTION = COMPLETE`

`MINOR_REMEDIATION = COMPLETE`

`NO_FURTHER_THEORY_ENHANCEMENT_RECOMMENDED = YES`

`READY_FOR_SUPERVISOR_REREVIEW = YES`

The accepted theory architecture remains unchanged. This phase makes only the
six authorized consistency and publication-style remediations and introduces
no new theory, citation, experiment, figure, table, research question,
contribution, mechanism claim, or scientific result.

## 2. Repository baseline

Preflight was executed before any edit:

- branch: `main`;
- `HEAD`: `2ab7ab2390ab80941e764f2201e6a96f6ea808f8`;
- `origin/main`: `2ab7ab2390ab80941e764f2201e6a96f6ea808f8`;
- worktree/index: clean;
- unstaged and staged diff statistics: empty.

No reset, clean, amend, merge, rebase, push, or tag was performed.

## 3. F1 before/after

Before remediation, some publication-visible summaries described
`P0→P2` mainly through representation and tensor-formation-location changes,
while the accepted model requires `R`, `F`, and `M` to change and `E` to remain
fixed.

After remediation:

- the Chinese and English abstracts define `V0→V2R` as a path-level
  reconstruction containing representation, tensor-formation-location, and
  corresponding staging-organization changes under the already fixed
  sequential topology;
- Section 1.3, Section 4.2, and the Conclusion state explicitly that `R/F/M`
  change while `E` remains fixed;
- the `2.24× / −55.45%` response remains attributable only to the complete
  controlled `P0→P2` path reconstruction;
- no contribution was assigned separately to `R`, `F`, or `M`.

## 4. F2 before/after

Before remediation, Table 1 was titled as a structural-variable matrix and
its first column was `路径结构变量`, which could imply that the
preprocessing mapping and derived `B(P)` were independent coordinates.

After remediation:

- title: `三条输入数据路径的结构描述与派生量`;
- first-column header: `路径描述项`;
- all six rows, row order, path values, `B(P)`, and the path-model definition
  remain unchanged;
- the table manifest and the two DOCX postprocessing caption authorities were
  synchronized to the corrected title without changing layout logic.

## 5. F3 before/after

Before remediation, the Introduction stated that the three concerns were
often juxtaposed as implementation details and that a unified research object
was lacking.

After remediation, the claim is bounded to the edge-deployment literature
examined in this paper: existing work is described as mostly addressing model
optimization, preprocessing, or host-device memory behavior separately, with
relatively limited discussion of their joint organization in a unified E2E
path. The existing citations are retained; no novelty, field-wide absence, or
first/only/unique claim is made.

## 6. F4 before/after

Before remediation, the Chinese abstract used `显著的完整路径平均响应`,
and the abstract/conclusion implication could be read as a broad engineering
prescription.

After remediation:

- the Chinese abstract uses the non-statistical `较大的平均响应`;
- both abstracts attribute that response to the complete path-level
  reconstruction rather than an `R/F`-only change;
- the Chinese/English abstract and Conclusion scope the implication to this
  class of fixed-inference-object data-path evaluation;
- the existing single-platform, single-detector/Engine, single-workload,
  offline-replay, sequential-topology limitation remains explicit.

No number or statistical interpretation changed.

## 7. F5 before/after

Before remediation, Section 2 included lifecycle-governance wording and a
sentence announcing that internal thresholds and release procedures were not
part of the public method description.

After remediation, the reproducibility-relevant implementation statement is
compressed to ordinary publication language: relevant device buffers and the
execution context are reused within the process to avoid repeated per-frame
allocation or creation. The internal-omission announcement was deleted.

## 8. F6 before/after

Before remediation, Sections 2.4 and 3.2 used project-internal terms including
`确认比较身份` and `生命周期准入`.

After remediation, the same factual checks are described through ordinary
scientific terms: input order, processed count, frame-drop, and EOS checks
ensure execution integrity, inter-path comparability, and consistent
comparison conditions. No factual check was removed.

## 9. Figure 1 change

The existing deterministic Figure 1 geometry, dimensions, domain structure,
path topology, scientific relationships, and note were retained. Only the
`P0→P2` intervention label changed:

- before: `联合改变 R、F 及相应输入组织`;
- after: `改变 R、F、M；E 保持不变`.

The SVG, PDF, PNG, and grayscale PNG were regenerated using the existing
deterministic script. Historical Phase 5.7 assets were not modified.

Current Figure 1 hashes:

- SVG: `bc59b8ec01b7e2295088debf1d55be5aaf1aeabf5c71b9cd0d724a5157792ba1`;
- PDF: `b334ce03bd29962f5fbc3d0e8b78c6c45065846e9d6fe59d548c34cef5f45150`;
- PNG: `c1db57f38cdca96ae1bcb386fdc19547e126a17b0de03ef3cd5335fdf10621a1`;
- grayscale PNG: `c8a5e249e9cdc2a7c40ed4a6c3a8248b44b976a05cc2b22659eaa360bfac506f`.

## 10. Table 1 change

Table 1 now renders with the corrected conceptual title and `路径描述项`
header. It remains a header plus six rows and four columns. The preprocessing
row remains an implementation mapping related to `F`; `B(P)` remains a derived
structural descriptor and not an independent coordinate of `P`.

## 11. Scientific non-regression

The integration validator and source/rendered audits confirm the frozen values:

- V0: `54.600 FPS / 18.273 ms`;
- V2R: `122.122 FPS / 8.140 ms`;
- V3R: `127.097 FPS / 7.812 ms`;
- V0→V2R: `2.24× / −55.45%`;
- V2R→V3R: `+4.07% / −4.03%`;
- pooled tails: P95 `+0.15%`, P99 `−0.12%`;
- nominal payload: `4.9152 / 0.1200 MB/frame`, `40.96×`;
- correctness: `0.6913 / 0.6991 / 0.6476 / 0.3523`.

`P0→P2` changes `R/F/M` with fixed `E`; `P2→P3` changes only `M`;
`B(P)` is derived; `40.96×` is nominal only; mean and tail responses remain
separate dimensions. No stage-level causal attribution, new measurement, or
scientific-value change was introduced.

## 12. Equation/RQ/contribution inventory

- figures: `3`;
- tables: `3`;
- core display equations: `3` (`P=(R,F,M,E)`, `B(P)`, `T_E2E(P)`);
- research questions: `2`;
- contributions: `2`.

The section, figure, table, results/discussion, correctness-as-validity,
mean/tail, and limitations architectures remain unchanged.

## 13. Reference audit

- bibliography library entries: `27`;
- cited and rendered references: `22`;
- unresolved/dead rendered citations: `0`;
- retained uncited library entries: `5`;
- Full/Anonymous bibliography identity: `PASS`;
- unexpected orphaned reference: `NO`.

No citation was added, removed, or reassigned to a stronger claim.

## 14. Full/Anonymous pages

Both documents were rebuilt through the existing validated pipeline and
converted to mechanical PDFs:

| Variant | DOCX SHA256 | PDF SHA256 | Pages |
|---|---|---|---:|
| Full | `fb59970b33885ac138f4105540a1962db6d02a5973864f90538a8e750b9b300b` | `0f607570ac470f797d8134bda03b44707ae0c0ac988745d93fed739ba8f99b53` | 7 |
| Anonymous | `78f8509f2d416c4ae5c690e9178e30b3f505ca3c6ae33499fdb9b6380ffc0b6b` | `54cd1b997619fd3787859f538b14cc131f8412fbd666fd4fac73b2c03e15b154` | 7 |

Both page counts remain within the required 7–8-page budget.

## 15. Format validation

Official-format validation passed for Full and Anonymous: A4 page size,
margins, two-column body, front/body section transitions, fonts, font sizes,
line spacing, title typography, captions, tables, footers, equation treatment,
and reference typography. Both Chinese and English titles render on one line;
all body headings render without wrapping. No format optimization was made.

## 16. Mechanical QA

All 14 rendered pages were inspected. The revised Chinese/English abstracts,
Introduction citation flow, Table 1 title/header, Figure 1 intervention label,
Sections 2/3 terminology, equations, figures, conclusion, and references render
without clipping, overflow, broken column flow, strange whitespace, or heading
wrap. Figure 1 remains legible in the full-width placement. Full and Anonymous
retain scientific-body parity.

## 17. Finding closure matrix

| Finding | Closure |
|---|---|
| F1 formal-coordinate consistency | `CLOSED` |
| F2 Table 1 conceptual labeling | `CLOSED` |
| F3 literature-gap strength | `CLOSED` |
| F4 statistical/generalization wording | `CLOSED` |
| F5 governance-report tone | `CLOSED` |
| F6 internal-governance terminology | `CLOSED` |

Blocking findings: `0`. Major findings: `0`. No new blocking or major finding
was introduced.

## 18. Open submission-production exceptions

- MathType source conversion remains deferred until supervisor approval.
- Visio/Origin editable-object conversion remains deferred until supervisor
  approval.
- The PDFs are mechanical validation derivatives; final Windows Word and
  submission-production inspection remains downstream.

These are existing production exceptions, not scientific or Phase 5.9E
closure failures.

## 19. Commit SHA

`COMMIT_CONTAINING_THIS_REPORT`

This is a self-resolving reference to the one focused Phase 5.9E commit. The
exact immutable SHA is supplied in the final handoff; embedding a commit's own
SHA in its content would require an additional or amended commit, both outside
the one-commit/no-amend contract.

## 20. No push / clean worktree

Exactly one focused commit is produced for this phase. No push, tag, merge,
rebase, reset, clean, or amend is performed. The final worktree and index are
verified clean after the commit.

Final review posture:

`SUPERVISOR_MANUAL_STYLE_CONCERN = SUBSTANTIALLY_RESOLVED`

`THEORY_LEVEL = ADEQUATE_FOR_HFUT`

`PSEUDO_THEORY_RISK = LOW`
