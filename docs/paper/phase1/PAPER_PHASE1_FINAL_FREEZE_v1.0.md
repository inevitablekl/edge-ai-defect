# Paper Phase 1 Final Freeze v1.0

## 1. Final Status

`PHASE_1_COMPLETE`

## 2. Freeze Authorization

- Independent review: PASS
- Freeze authorized: YES
- Experimental remediation required: NO
- New experiments required: NO
- Phase 2 authorized: YES

## 3. Authority Basis

- Phase 0 v1.1 governance.
- Phase 0.5 formal, compact, and verified raw evidence.
- The five formal Phase 1 evidence files.
- The Phase 1 independent review report.

## 4. Final File Set

| File | SHA256 |
|---|---|
| `PAPER_PHASE1_EXPERIMENT_MATRIX_v1.0.csv` | `38adc94e068da4489b68e21ae430d6c64b07e50ee42689f41f2008c70c870b5f` |
| `PAPER_PHASE1_METRIC_PROVENANCE_v1.0.csv` | `2f9c3af57730e7e81c28159cdf3d164abd0d51dca1dd6221ee16bfbd75e12a2d` |
| `PAPER_PHASE1_CLAIM_EVIDENCE_MAP_v1.0.md` | `c01206b4ef1f89f926ae9d1d7b8450caf2a98fd2a568086040046a083ca5e5e8` |
| `PAPER_PHASE1_GAP_REGISTER_v1.0.md` | `1e0119f0e16d31dc45237a8ff974bb329b5a7ca6ea2d30c7848a17a3a8ad3621` |
| `PAPER_PHASE1_EVIDENCE_FREEZE_REPORT_v1.0.md` | `5c30beba9657dff32d609cf9ad51ed0d552b64a662c22506facdf28e20faf11b` |
| `PAPER_PHASE1_INDEPENDENT_REVIEW_v1.0.md` | `8117882912a71bcb97d0bb14040b32670c189a0576316b246e90747834df5468` |
| `PAPER_PHASE1_FINAL_FREEZE_v1.0.md` | SELF — governed by Git commit and annotated tag |

## 5. Final Evidence Counts

- Experiments: 16
- INCLUDE: 2
- INCLUDE_WITH_LIMITATION: 2
- SUPPORTING_ONLY: 9
- EXCLUDE: 3
- REMEDIATION_REQUIRED: 0
- Metrics: 87
- VERIFIED: 43
- DERIVED_VERIFIED: 40
- SUMMARY_ONLY: 1
- MISSING: 2
- EXCLUDED: 1
- CONFLICTED: 0
- Reproducible yes: 83
- Reproducible no: 4
- Gap Register gaps: 9
- CORE_BLOCKER: 0
- remediation_required=YES: 0

## 6. Core Frozen Claims

All claims below are limited to the frozen Jetson/model/workload/timing contract:

- Stage R V0/V2R/V3R common-boundary ablation.
- V2R/V0: 2.236671x FPS.
- V2R/V0 mean latency reduction: 55.4519%.
- V3R/V2R FPS increase: +4.0738%.
- V3R/V2R mean latency reduction: 4.0349%.
- V3R tail result is mixed:
  - P95: +0.1514% worse.
  - P99: -0.1184% better.

## 7. Frozen Prohibitions

- No cross-stage speedup multiplication.
- No total-system acceleration claim.
- No lossless INT8 claim.
- No positive raw/bitwise FP16 equivalence claim.
- No Pipeline single-frame latency reduction claim.
- No V4 overlap/double-buffer claim.
- No thermal, power, endurance, or industrial-reliability claim.
- Do not describe the external PT as a Git-tracked asset.

## 8. Accepted Limitations

Accepted limitations and exclusions are governed by `PAPER_PHASE1_GAP_REGISTER_v1.0.md`, including external PT/archive status, summary-only historical metrics, Stage K Raw Level B `FAIL`, missing J5.5 per-frame latency, throughput-only Pipeline evidence, incomplete thermal/resource telemetry, and excluded Attempt 2/V4 evidence.

## 9. Git Freeze Marker

Authoritative annotated tag:

`paper-phase1-complete-v1.0`

The authoritative frozen commit is the commit peeled from this annotated tag.

## 10. Phase 2 Handoff

Phase 2 is authorized for:

- Paper structure planning.
- Figure and table design.
- Experimental chapter organization.
- Claim-aware writing preparation.

Phase 2 must not:

- Change frozen numerical values without authorization.
- Restore excluded evidence.
- Generate a cross-stage total acceleration ratio.
- Add experiments without authorization.
