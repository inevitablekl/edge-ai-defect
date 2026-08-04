# Paper Evidence Authority Map v1.1

Previous version: `docs/paper/phase0/PAPER_EVIDENCE_AUTHORITY_MAP_v1.0.md`

Supersedes: Paper Phase 0 evidence authority map v1.0.

Supersession reason: Final reconciliation after Paper Phase 0.5 validity remediation, including split sensitivity closure, V2R Gate D acceptance, V3R identity evidence, and the timing-aligned V0/V2R/V3R rerun.

Effective authority date: `2026-08-04`.

Basis: Paper Phase 0.5 validity remediation. This document is a governance
record, not paper正文 and not a replacement for the machine-readable evidence.

## 1. Final Authority Verdict

```text
Paper Phase 0.5 technical remediation: COMPLETE
Dataset split: CLOSED_WITH_DISCLOSURE
Checkpoint sensitivity: SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL
V2R correctness: ACCEPTED
V3R correctness inheritance: ACCEPTED_WITH_IDENTITY_EVIDENCE
Timing-aligned rerun: PASS
Further experiment: NOT REQUIRED
New code optimization: NOT AUTHORIZED
```
The v1.0 documents remain historical baselines. The v1.1 documents in this
directory are the current paper-governance authority.

## 2. Authority Inputs

The reconciliation used the six Phase 0 v1.0 files, the Phase 0.5 core audit,
the Phase 0.5B matched-control report and evidence, the Phase 0.5C V2R
correctness evidence, the Phase 0.5D harness/rerun reports, and the compact
machine-readable manifests and hash records. No benchmark, training,
inference, or repository-wide rescan was performed for this draft.

Primary Phase 0.5 sources:

- `docs/paper/phase0_5/PAPER_CORE_VALIDITY_AUDIT_v1.0.md`
- `docs/paper/phase0_5/PAPER_DATASET_SPLIT_SENSITIVITY_FINAL_v1.0.md`
- `docs/paper/phase0_5/PAPER_V2R_GATE_D_DISPOSITION_v1.0.md`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_G_EXECUTION_REPORT.md`
- `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md`

## 3. Dataset and Model-Selection Authority

The historical train/validation split contained one image-content duplicate:
train `IMAGES/patches_101.jpg` and validation `IMAGES/patches_105.jpg`, with
image SHA-256
`4d2de82731b86cdbc7a66f2a9bfb01074bb4cb65e47bccf06b66470d53857071`.
The test set remained unchanged at 180 entries.

The deduplicated split v2 is `1260 train / 359 validation / 180 test`. Matched
split-v1 control and split-v2 sensitivity evaluation covered the same nine
existing checkpoints. Seed 7 ranked first on both splits and all nine ranks
were unchanged. The accepted status is
`SEED7_SELECTION_CONFIRMED_MATCHED_CONTROL` and
`DATASET_SPLIT_REMEDIATION_COMPLETE`.

The evidence does not byte-identically reproduce all historical validation
numbers. Historical metrics remain contemporaneous records. This limitation
must be disclosed, but it does not require retraining, checkpoint re-freeze,
ONNX re-export, Engine rebuild, calibration rerun, or downstream rerun.

## 4. Stage R Formal Authority

Only `V0`, `V2R`, and `V3R` are formal Stage R objects.

| Variant | Definition | Formal authority |
|---|---|---|
| V0 | CPU/OpenCV preprocessing correctness baseline | `docs/paper/phase0_5/PAPER_PHASE0_5D_I2_FORMAL_EXECUTION_REPORT.md` |
| V2R | pageable raw staging plus correctness-aligned CUDA preprocessing | same formal report; Gate D: `docs/paper/phase0_5/PAPER_V2R_GATE_D_DISPOSITION_v1.0.md` |
| V3R | pinned raw staging plus the same correctness-aligned CUDA preprocessing as V2R | same formal report; identity evidence: `docs/paper/phase0_5/evidence/v2r_gate_d_v1/v3r_identity_check.json` |

### 4.1 Formal performance numbers

| Variant | FPS mean | FPS SD | Mean latency | P95 | P99 |
|---|---:|---:|---:|---:|---:|
| V0 | 54.600 | 0.223 | 18.273 ms | 18.854 ms | 19.068 ms |
| V2R | 122.122 | 0.492 | 8.140 ms | 9.827 ms | 11.529 ms |
| V3R | 127.097 | 1.279 | 7.812 ms | 9.842 ms | 11.515 ms |

V2R relative to V0: FPS ratio `2.2367x`, FPS increase `123.67%`, mean latency
reduction `55.45%`, P95 reduction `47.88%`, and P99 reduction `39.54%`.

V3R relative to V0: FPS ratio `2.3278x`, FPS increase `132.78%`, mean latency
reduction `57.25%`, P95 reduction `47.80%`, and P99 reduction `39.61%`.

V3R relative to V2R: FPS increase `4.07%`, mean latency reduction `4.03%`,
P95 slightly worse by approximately `0.15%`, and P99 approximately unchanged
with an improvement of approximately `0.12%`.

The allowed V3R conclusion is limited additional benefit in average FPS and
mean latency. It is a marginal optimization, not a new order-of-magnitude
gain, and it does not establish P95/P99 tail-latency improvement. Pinned raw
staging is therefore an average-performance optimization in this tested path,
not a universal memory conclusion.

### 4.2 Correctness authority

V2R task metrics are precision `0.6912751678`, recall `0.6990950226`, mAP50
`0.6476254638`, and mAP50-95 `0.3523443910`; all deltas against V0 are `0.0`
and Gate D is `PASS`. The machine result is
`docs/paper/phase0_5/evidence/v2r_gate_d_v1/v2r_task_metrics.json`.

V3R has the same tensor digest
`da2b2bba8d71a25b9bafce988ee838e184666369bbd94bcecc73c6a513d6abb6` and the
same detection digest
`12bdb792840316e5569ba1a7f8a7d56221b47a6c064ff2be01ce4ceb69513de2` as V2R,
with frame order, paths, geometry, count, zero-drop, EOS, worker join, and
result contract passing. This is accepted identity evidence, not an
independent Gate D parameter-selection run.

## 5. Common Timing Boundary and Formal Contract

The external timing interval starts before source pull/frame acquisition and
ends after preprocessing, inference, postprocess, and frame-result
construction, before JSON serialization/write.

Included: source pull/decode, raw staging, H2D, CUDA preprocessing, TensorRT
inference, synchronization, D2H, postprocess, and frame-object construction.

Excluded: JSON serialization, file I/O, digest finalization, and summary
persistence. All variants use `timing.enabled=false`, `profiling.mode=off`,
60 warmup frames, 1080 measured frames, six measured cycles, five independent
processes per variant, 15/15 valid runs, zero drops, and EOS PASS.

The compact formal evidence is
`docs/paper/phase0_5/evidence/timing_aligned_v0_v2r_v3r_v1/manifest.json` and
its hash record. Its execution commit is
`6885dc5c8d1099c34f1cd8d10c4b30426df61daf`; the compact manifest SHA-256 is
`74b77515020d4924060dd7f4c7bd773229684fb18d0bd5a6e004cfe41f5309c0` and the
formal report SHA-256 is
`3d9ea96fc430a94b090bcd2f9241313df81d5cd82bc7f7bcb7b05f47c95a85ec`.

## 6. V4 and Historical Attempt 2 Disposition

V4 is classified as `PARTIAL_BUFFER_ROTATION_NOT_TRUE_OVERLAP`. It implemented
two fixed resource slots with serial reuse and explicit synchronization, not
true double buffering or cross-frame overlap. It is excluded from the formal
performance table, formal ablation, Pareto, and core contribution. The
implementation/anomaly record is retained as supplemental engineering
limitation evidence: a severe tail and one recorded OOM event occurred, but
the evidence does not prove that double buffering caused the OOM.

The historical Attempt 2 V0/V2/V3/V4 table, its derived comparison, old V2/V3
correctness boundary, and old Pareto are
`SUPERSEDED_FOR_FINAL_PAPER_USE`. They remain available for remediation
motivation, audit trail, historical process evidence, and timing-mismatch /
correctness-remediation background only. They must not enter the final paper
performance table, figures, abstract, or conclusions.

## 7. Current Claim Boundary

The paper may claim, within the frozen Jetson, model, Engine, workload, and
timing contract, that CUDA preprocessing is the main observed performance
source; V2R is correctness-accepted; and V3R supplies limited average
performance benefit without clear tail-latency improvement. It may not claim
universal CUDA, pinned-memory, double-buffer, bottleneck-migration, or
cross-platform conclusions.

## 8. Reconciliation Status

```text
Evidence authority: REFROZEN
Contribution scope: REFROZEN
Open Must gaps: NONE
Open Should experimental gaps: NONE
Further experiment: NOT REQUIRED
New code optimization: NOT AUTHORIZED
```
