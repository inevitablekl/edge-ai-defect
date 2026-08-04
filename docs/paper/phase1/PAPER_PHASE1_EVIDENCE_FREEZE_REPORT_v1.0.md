# Paper Phase 1 Evidence Freeze Report v1.0

## 1. Status

**Status: `PHASE_1_COMPLETE`**

**Independent review verdict: `PASS`**

**Freeze authorization: `AUTHORIZED`**

**Next phase: `Paper Phase 2 Writing Preparation`**

**New experiment required: NO**

This is the final Phase 1 evidence freeze. It is based on the frozen Phase 0 v1.1 and Phase 0.5 authority set, the Step 1 input-completeness report, the independent review, and a read-only audit of present repository evidence plus the user-provided verified external PT fact. Independent review record: `docs/paper/phase1/PAPER_PHASE1_INDEPENDENT_REVIEW_v1.0.md`.

## 2. Authority basis

The evidence authority order used in this amendment is:

1. Phase 0 v1.1 governance and frozen scope.
2. Phase 0.5 formal/compact/raw authority, including the verified Stage R archive.
3. Formal machine evidence from Training, ONNX, J, K, Q, P, and R.
4. Formal execution, final, and closeout reports.
5. Deterministically derived statistics.
6. Historical, superseded, or excluded evidence.

`AGENTS.md` is a repository operational constraint for this audit; it is not ranked above the Phase 0 v1.1 evidence authority.

The Step 1 input-completeness report and inventory were used as audit-control inputs.

The frozen PT is recorded as `VERIFIED_EXTERNAL_ASSET`, not as a Git-tracked repository artifact. No repository file was changed.

## 3. Experiment inclusion decisions

The experiment matrix contains 16 frozen rows:

- `INCLUDE`: 2 — `R_V0`, `R_V2R`.
- `INCLUDE_WITH_LIMITATION`: 2 — `R_V3R`, `K_TRT_FP16`.
- `SUPPORTING_ONLY`: 9 — training freeze, PT/ONNX consistency, J ORT CPU baseline, K FP32 baseline, Q accuracy, Q serial, Q pipeline, P serial/pipeline, and correctness/stability support.
- `EXCLUDE`: 3 — old R Attempt 2, V4 formal/partial-slot evidence, and the V4 overlap claim.
- `REMEDIATION_REQUIRED`: 0.

The core paper frozen is therefore the timing-aligned Stage R V0/V2R/V3R comparison. K, Q, P, J, training, and ONNX evidence remain supporting or boundary evidence, not a single cross-stage benchmark.

## 4. Metric provenance verification

The formal metric provenance file contains 87 rows. These counts are generated with Python `csv.DictReader` from the final CSV, not copied from an earlier draft:

- `VERIFIED`: 43.
- `DERIVED_VERIFIED`: 40.
- `SUMMARY_ONLY`: 1.
- `MISSING`: 2.
- `EXCLUDED`: 1.
- `CONFLICTED`: 0.

Experiment-ID row counts are: `TRAINING_FREEZE` 7, `PT_ONNX_CONSISTENCY` 4, `J_ORT_CPU_BASELINE` 6, `K_TRT_FP32_BASELINE` 5, `K_TRT_FP16` 10, `Q_TRT_INT8_ACCURACY` 13, `Q_TRT_INT8_SERIAL` 4, `Q_TRT_INT8_PIPELINE` 1, `P_SERIAL_PIPELINE` 2, `R_V0` 6, `R_V2R` 14, `R_V3R` 14, and `R_V4_FORMAL` 1.

Reproducibility flags are 83 `yes` and 4 `no`; the four non-reproducible/present-evidence exceptions are the missing training archive, summary-only sensitivity values, missing J5.5 per-frame latency, and excluded V4 metric.

The Stage R aggregate values were independently recomputed from the verified archive. The principal derived results are:

| comparison | FPS result | mean latency result | tail result |
|---|---:|---:|---:|
| V2R vs V0 | 2.236671x; +123.6671% | 55.4519% reduction | P95 -47.8780%; P99 -39.5385% |
| V3R vs V0 | 2.327790x; +132.7790% | 57.2493% reduction | P95 -47.7991%; P99 -39.6101% |
| V3R vs V2R | +4.0738% | 4.0349% reduction | P95 +0.1513864517% latency change; P99 -0.1183944591% latency change |

These are Stage R timing-boundary results, not total deployment acceleration factors.

## 5. Comparability decisions

Direct comparisons are permitted only within a shared protocol:

- Stage R: V0, V2R, and V3R are directly comparable under the common timing boundary, same workload, five runs per variant, and matched run protocol.
- Stage K K7: strict FP32 and original FP16 are directly comparable within K7 only.
- Stage Q Q5/Q6: INT8 and FP16 are directly comparable within the stated Q accuracy and serial-performance protocols.
- Stage Q Q7 and Stage P: paired pipeline/throughput comparisons are valid only within their own experiment protocol.

J ORT CPU, K TensorRT, Q TensorRT, P pipeline, and Stage R results must not be merged into one multiplicative speedup. Different backends, timing boundaries, runtime modes, workloads, and stages make cross-family arithmetic invalid.

## 6. Claim–evidence coverage

The claim map marks C1–C3 as the core contribution frozen: a bounded common-path ablation, V2R correctness-preserving speed improvement, and the limited incremental V3R effect including its tail-metric trade-off. C4–C8 are supporting or limitation-aware claims. C9 prevents excluded historical evidence and invalid total-speedup language from entering the paper.

Every allowed numeric claim in the map has a source authority, metric provenance row, timing boundary, and limitation. The seed-7 rank, split-v1/split-v2 counts, Stage R ratios, and Stage R tail changes each have independent metric IDs. No paper claim is supported by fabricated or unmeasured data.

Numeric crosswalk: V2R/V0 `2.236671x` → `M_R_V2R_V0_FPS_RATIO`; V2R/V0 `55.4519%` → `M_R_V2R_V0_LAT_REDUCTION`; V3R/V2R `4.0738%` → `M_R_V3R_V2R_FPS_INCREASE`; V3R/V2R `4.0349%` → `M_R_V3R_V2R_LAT_REDUCTION`; P95 `+0.1513864517%` → `M_R_V3R_V2R_P95_CHANGE`; P99 `-0.1183944591%` → `M_R_V3R_V2R_P99_CHANGE`; V2R/V0 `+123.6671%` → `M_R_V2R_V0_FPS_INCREASE`; V3R/V0 `+132.7790%` → `M_R_V3R_V0_FPS_INCREASE`; seed-7 rank 1 → `M_TRAIN_SEED7_RANK`; split-v1 `1260/360/180` → `M_TRAIN_SPLIT_V1_COUNTS`; split-v2 `1260/359/180` → `M_TRAIN_SPLIT_V2_COUNTS`.

## 7. Excluded evidence

The following remain visible in the audit trail but cannot support formal paper conclusions:

- failed/preserved Stage R implementation attempt;
- historical R Attempt 2 materials with incomplete/stale provenance;
- V4 partial-slot rotation evidence and its proposed overlap/double-buffer interpretation;
- positive raw tensor-equivalence and bitwise-equivalence claims;
- any cross-stage product of J/K/Q/P/R ratios.

The verified Stage K Raw Level B `FAIL` is retained as limitation evidence
supporting C6. It is not excluded evidence; the excluded items are the
unsupported positive raw tensor-equivalence, bitwise-equivalence, and
raw-output-equality-passed claims.

## 8. Remaining gaps

The gap register identifies nine accepted limitations or scope exclusions and no remediation blocker. The most important are external-only PT/archive access, incomplete historical compact logs, the absence of a dedicated Stage K final report, missing J5.5 per-frame latency, K raw Level B failure, and incomplete thermal/resource telemetry. These gaps require explicit paper wording, not new experiments under the current freeze boundary.

## 9. Accepted limitations

The paper must disclose split-v1 as 1260/360/180 and split-v2 as 1260/359/180. The seed-7 selection is rank 1 under an engineering selection rule, not a cherry-pick claim. The Stage R archive is externally located but hash-verified. Pipeline evidence supports throughput only, not single-frame latency or real-camera performance. J5.5 whole-process FPS and J5.6 pre-sink FPS must not be conflated.

## 10. Prohibited paper statements

Do not state that:

- V2R or V3R provides a universal or total-system acceleration;
- independent J/K/Q/P/R speedups can be multiplied;
- K raw tensor equivalence or bitwise FP16 identity passed;
- Pipeline mode reduces single-frame end-to-end latency;
- V4 proves true double-buffer overlap or establishes an OOM cause;
- INT8 is lossless or universally faster without accuracy trade-off;
- historical absolute matched-control values are fully reproducible from the present compact package;
- Stage R proves thermal, power, endurance, or real-camera industrial reliability.
- V3R has uniform tail-latency improvement; its measured tail result is mixed: P95 slightly worse and P99 slightly better.

## 11. Phase 2 readiness assessment

The frozen evidence set is sufficiently organized for Phase 2 writing preparation after independent review. No new experiment is required for the bounded core claim set, and no Stage K production implementation, Pipeline implementation, or other out-of-scope work is authorized by this audit.

## 12. Finalization

Independent review verdict: `PASS`.

Freeze authorization: `AUTHORIZED`.

The five formal Phase 1 evidence files, this report, and the Final Freeze record are the authoritative Phase 1 freeze set. The next phase is `Paper Phase 2 Writing Preparation`. No new experiment is required.
