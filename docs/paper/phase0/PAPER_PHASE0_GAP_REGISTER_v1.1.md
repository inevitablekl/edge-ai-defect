# Paper Phase 0 Gap Register v1.1

Previous version: `docs/paper/phase0/PAPER_PHASE0_GAP_REGISTER_v1.0.md`

Supersedes: Paper Phase 0 gap register v1.0.

Supersession reason: closes the six Phase 0.5 validity and retention gaps and
re-freezes the remaining work as paper production only.

Effective authority date: `2026-08-04`.

Basis: Paper Phase 0.5 validity remediation.

## 1. Final Gap Verdict

```text
Open Must gaps: NONE
Open Should experimental gaps: NONE
Further experiment: NOT REQUIRED
Paper-production gaps: figures, tables, chapter drafting and literature mapping only
```

External raw-archive backup remains an asset-management recommendation, not a
paper-blocking gap.

## 2. Closed Remediation Gaps

| Gap | Closure evidence | Final status | Paper handling |
|---|---|---|---|
| Train/validation image-content duplicate | `docs/paper/phase0_5/PAPER_DATASET_SPLIT_SENSITIVITY_FINAL_v1.0.md`; matched-control JSON | CLOSED_WITH_DISCLOSURE | Disclose one duplicate; test 180 entries unchanged |
| Seed-7 selection sensitivity | `docs/paper/phase0_5/evidence/checkpoint_selection_sensitivity_control_v1/matched_split_comparison.json` | SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL | Seed 7 rank 1 on both splits; all nine ranks unchanged |
| V2 Gate D failure | `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_gate_d_decision.json` | ACCEPTED | V2R all six gates PASS; all observed drops 0.0 |
| V0 timing mismatch | `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md` | CLOSED; TIMING_ALIGNED_RERUN_PASS | Use only V0/V2R/V3R formal timing-aligned results |
| V4 false-overlap claim | `docs/paper/phase0_5/PAPER_CORE_VALIDITY_AUDIT_v1.0.md` | CLOSED; PARTIAL_BUFFER_ROTATION_NOT_TRUE_OVERLAP | Exclude formal performance/Pareto/core use; retain limitation history |
| Raw evidence external retention | `docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/manifest.json`; archive manifest | CLOSED_WITH_RETENTION_RECORD | 112 files, 12746622 bytes, 112/112 SHA256 verification PASS |

## 3. Dataset Split Disclosure

The historical split had one train/validation image-content duplicate. Split
v2 is `1260 train / 359 validation / 180 test`; the test entries are unchanged.
Matched split-v1 and split-v2 checkpoint-only evaluation was completed. No
retraining, checkpoint re-freeze, ONNX export, Engine rebuild, calibration
rerun, or split-driven downstream rerun is required. Historical validation
absolute metrics remain contemporaneous records because byte-identical
reproduction was not established.

## 4. Stage R Evidence Gaps Closed by Timing-Aligned Rerun

The common external boundary starts before source pull/frame acquisition and
ends after preprocessing, inference, postprocess, and frame-result
construction, before JSON serialization/write. It includes decode/staging,
H2D, CUDA preprocessing, TensorRT, synchronization, D2H, postprocess, and
frame construction; it excludes serialization, file I/O, digest finalization,
and summary persistence.

The formal contract is 60 warmup frames, 1080 measured frames, six measured
cycles, five independent processes per variant, 15/15 valid runs, zero drops,
and EOS PASS. The formal objects are V0, V2R, and V3R only.

## 5. Non-Gaps and Stop Conditions

No additional variant, V4 overlap implementation, Pipeline extension, INT8
optimization, GPU preprocessing redesign, or new code optimization is
authorized by this reconciliation. Do not convert presentation work into a
new experiment. Do not fabricate missing figures, tables, or measurements;
until rendered, they remain paper-production tasks.

## 6. Historical Retention

The v1.0 gap register, old Attempt 2 evidence, V4 records, failed Gate D
record, timing-mismatch record, and raw archive are retained. They are audit
trail and remediation history, not current final-paper numerical authority.
