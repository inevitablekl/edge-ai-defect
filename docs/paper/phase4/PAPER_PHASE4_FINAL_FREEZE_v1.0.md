# Paper Phase 4 Final Freeze

## 1. Verdict

`COMPLETE_MANUSCRIPT_DRAFT_CANDIDATE`

Paper Phase 4 is complete as a full-manuscript draft candidate. This freeze
does not assert publication acceptance or submission-ready metadata closure.

## 2. Repository Authority

- Branch: `main`.
- Starting HEAD: `f8f408a3a6596c4d7f62bbfcd5969583defd4b3d`.
- Starting subject: `fix(paper): keep anonymous table 1 together`.
- Remote verification: `origin/main` resolved to the same starting commit.
- Final HEAD: the freeze commit containing this report; its exact object ID is
  recorded by Git and by the final execution handoff because a commit cannot
  contain its own object ID.
- Starting worktree: clean.
- Starting index: clean.
- Final worktree/index requirement: clean after the freeze commit.
- Phase 3 authority: the accepted manuscript sections, review log, and section
  status matrix frozen at
  `08fb3dac62f6c234b888ae5cef579d88926d3e02`.
- Phase 4 final build authority: the current manuscript sources, final
  publication assets, CSL, build/validation tooling, and Phase 4.9 remediation
  state at `f8f408a3a6596c4d7f62bbfcd5969583defd4b3d`.

## 3. Final Manuscript Artifacts

Full:

- Path: `docs/paper/manuscript/output/draft_full.docx`.
- Size: `130019` bytes.
- SHA256: `1c6e59e802ff8084bdd415128bb8b64d7c8e0d056b163c969eee7b2b93c23768`.

Anonymous:

- Path: `docs/paper/manuscript/output/draft_anonymous.docx`.
- Size: `129334` bytes.
- SHA256: `ca577b1d7ada73e375f3d4771d1ad47a7ea9e47a8d4f130c31d94f3b8fc990b3`.

Both whole-DOCX hashes were recomputed from the actual current files and match
the reported final-candidate hashes. No rebuild or ZIP-metadata normalization
was performed. The producing repository state is
`f8f408a3a6596c4d7f62bbfcd5969583defd4b3d`.

Generated manuscript artifacts remain local and ignored according to
`docs/paper/manuscript/output/.gitignore`; they are not force-added to Git.

## 4. Phase 4 Completion Matrix

| Phase | Status |
| --- | --- |
| 4.0 | `COMPLETE` |
| 4.1 | `COMPLETE` |
| 4.2 | `COMPLETE` |
| 4.3 | `COMPLETE_WITH_METADATA_LIMITATION` |
| 4.4 | `COMPLETE` |
| 4.5 | `COMPLETE` |
| 4.6 | `COMPLETE` |
| 4.7 | `COMPLETE` |
| 4.8 | `COMPLETE` |
| 4.9 | `COMPLETE` |

Overall: `COMPLETE_MANUSCRIPT_DRAFT_CANDIDATE`.

## 5. Scientific Freeze

The six frozen comparisons remain:

| Comparison | Frozen value | Interpretation |
| --- | ---: | --- |
| V2R/V0 FPS ratio | `2.236671×` | higher/faster |
| V2R/V0 mean-latency reduction | `55.4519%` | lower/faster |
| V3R/V2R FPS change | `+4.0738%` | higher/faster |
| V3R/V2R mean-latency change | `-4.0349%` | lower/faster |
| V3R/V2R P95 change | `+0.1514%` | higher/slower |
| V3R/V2R P99 change | `-0.1184%` | lower/faster |

- Tail interpretation: `MIXED`.
- Contribution count: `2`.
- V4: absent.
- Historical Attempt 2: absent.
- Cross-stage acceleration multiplication: absent.
- Statistical-significance claim: absent; significance appears only in
  explicit non-inferential limitation statements.
- V3R independent task-level Gate D: absent. V3R remains companion-identity
  evidence under the accepted V2R CUDA preprocessing semantics.

## 6. Figures / Tables

- F1: `FINAL_ACCEPTED`.
- F2: `FINAL_ACCEPTED`.
- F3: `FINAL_ACCEPTED`.
- T1: `FINAL_ACCEPTED`.
- T2: `FINAL_ACCEPTED`.
- Microsoft Word real-environment manual review: `PASS`.

## 7. Citations / References

- Bibliography source records: `15`.
- Rendered references: `14`.
- Intentionally uncited records: `1`
  (`reddi_et_al_2022_mlperf_mobile`).
- Unresolved citation keys: `0`.
- Final CSL:
  `docs/paper/manuscript/csl/hfut_gbt7714_2025_numeric_v1.0.csl`.
- Final CSL SHA256:
  `207ef94434816d601281b4fd940c92428e3e21b9dc97abe4204359d0e7ce3818`.
- Full/Anonymous rendered-bibliography parity: `PASS`.
- Static F1/F2/F3 and T1/T2 cross-reference validation: `PASS`.

## 8. Full / Anonymous

- Full structural validation: `PASS`.
- Anonymous structural validation: `PASS`.
- Scientific-content parity: `PASS` (`PARITY_PASS`).
- Automated anonymity scan: `PASS` (`ANONYMITY_SCAN_PASS`).
- Microsoft Word visual review: `PASS` for Full and Anonymous.
- Anonymous visual anonymity: `PASS`.
- Word Document Inspector: reviewed for Full and Anonymous; comments,
  revisions, hidden content, and invisible content: `NONE`; only expected
  document-property/footer categories were observed.

## 9. Phase 4.9 Findings Closure

- `P4.9-F1`: `CLOSED`.
- `P4.9-T1-01`: `CLOSED`.
- `P4.9-T1-02`: `CLOSED`.
- `P4.9-T1-03`: `CLOSED`.
- Open Word-layout findings: `0`.

The completed real-environment Microsoft Word review records:

- Full open/save/reopen: `PASS`; no repair warning.
- Front matter: `PASS`.
- Biography/footer: `PASS`.
- Body, headings, and columns: `PASS`.
- F1/F2/F3: `PASS`.
- T1/T2: `PASS`.
- References: `PASS`.
- Controlled `Ctrl+A`/`F9`: `PASS`.
- Anonymous visual anonymity: `PASS`.
- Word Document Inspector: reviewed with the disposition recorded above.

## 10. Accepted Publication Limitation

`CORRESPONDING_EMAIL_PENDING_FINAL_METADATA_FREEZE`

The real corresponding-author email has not yet been supplied. No email was
fabricated, and this does not block the Phase 4 complete-manuscript draft
candidate. The actual submission-ready Full metadata package cannot be
finalized until the real email is supplied. Front matter is not reopened by
this freeze.

## 11. Readiness

`READY_FOR_SUPERVISOR_OR_JOURNAL_PRE_SUBMISSION_REVIEW`

This status is not:

- `PUBLICATION_READY`;
- `READY_FOR_ACCEPTANCE`;
- `ACCEPTANCE_EXPECTED`.

## 12. Reopen Conditions

Phase 4 may be reopened only for:

- a confirmed factual error;
- a scientific or citation inconsistency;
- a supervisor- or journal-required substantive revision;
- real submission-metadata closure;
- reproducible artifact corruption.

Phase 4 is not reopened for unlimited cosmetic optimization.

## 13. Final Governance Validation

The existing final candidates passed:

- `scripts/paper/build_manuscript_docx.sh --check`;
- final-reference validation for Full and Anonymous;
- journal-format validation;
- Anonymous identity validation;
- Full/Anonymous scientific and rendered-bibliography parity;
- Full manuscript structural validation;
- static figure/table cross-reference validation;
- `git diff --check` and index whitespace validation.

Known historical skeleton/pre-authoring validators and historical pinned-hash
audits were not treated as active Phase 4 final gates. No manuscript artifact
was rebuilt or modified during final governance validation.
