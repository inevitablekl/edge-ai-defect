# Stage J J5.7 Evidence Gate Report

## A. Verdict

`BLOCKED`

J5.7 does not grant the J6 dependency gate. J6, J7, J8 and J9 were not
executed.

## B. Scope and authority

This is a read-only gate over the existing J5.1–J5.6 Evidence directories.
No J5 Evidence, benchmark data, frozen protocol, model, contract, corpus or
reference was modified. No benchmark was rerun.

Starting source commit:

`0558d46fa02ca8f280d054c88962ac8b54f84dc4`

Checked Evidence:

| Task | Evidence |
|---|---|
| J5.1 | `python_reference/j5_1_python_reference_v1` |
| J5.2 | `profile_precheck/j5_2_candidate_semantic_precheck_v2` |
| J5.3 | `profile_sizing/j5_3_candidate_sizing_v1` |
| J5.4 | `profile_selection/j5_4_profile_selection_v1` |
| J5.5 | `profile_baseline/j5_5_profile_baseline_v1` |
| J5.6 | `tuned/j5_6_tuned_formal_baseline_v3` |

## C. SHA256 manifest verification

All six existing `sha256sums.txt` files passed `sha256sum -c`. Existing
Evidence was not rewritten. The manifest hashes are recorded in
`evidence_manifest.json`.

## D. Frozen asset verification

The current frozen assets match the required values:

| Asset | SHA256 |
|---|---|
| Model | `c88ac014bb6110cf14394d8bf2dfc7be05676d1b9a6ab73014f0542490245944` |
| ModelContract | `9dd74f8420d832d6fdad77057a2ae282c260e0be9b4be80b16bbf00bc6ddd190` |
| Corpus manifest | `235b062cb82166709e2ff800ec71bf92396d5348508281f822ef116d5f0962ab` |
| Python Reference | `1c31cfd41b4377c989baf35d57352280bb84f26b1942a8e26ac60076e61392a7` |
| Expected cycle | `dff5686b46de48416d9038ccc40b573eb1c59830ba9e96eac5becbdb6bb0746f` |

## E. Provenance chain

J5.1–J5.6 provenance files exist and their hashes are included in the gate
manifest. J5.2, J5.3, J5.4 and J5.6 explicitly report PASS. J5.5 records the
frozen k1 execution and its upstream J5.1–J5.4 references. The J5.6 source
commit is `480876aff91edecd800758407f6618d78295cbcc`.

## F. Profile consistency

The selected and executed roles are consistent with D051:

| Role | Profile | CPU set | ORT intra/inter |
|---|---|---|---|
| Controlled | k1 | 5 | 1 / 1 |
| Tuned | k5 | 1-5 | 5 / 1 |

J5.5 benchmark report confirms only k1 was executed. J5.6 verification
confirms five k5 formal runs.

## G. Formal statistics and telemetry review

### J5.5

The published J5.5 Evidence confirms five independent k1 processes, 560
processed frames per run, process-wall latency aggregation, FPS, VmRSS,
CPU/temperature/VDD_IN/RAM resource summaries, semantic correctness and
determinism SHA results.

However, it does not satisfy the complete §22.4 formal statistics contract as
published:

1. The five per-run summary files do not contain the required latency
   statistics set.
2. `benchmark_report.json` contains aggregate process-wall min/max/median/P95/
   P99/mean, but no sample standard deviation.
3. `README.md` states that raw JSON and telemetry were retained outside the
   published Evidence, so the published directory does not provide the full
   per-run telemetry/raw-statistics chain for independent gate reconstruction.

These are missing published Evidence, not invented values. They cannot be
repaired by this read-only gate.

### J5.6

The v3 Evidence confirms five PASS independent k5 runs, 500 measured frames and
25 cycles per run, with the required latency statistics, pre-sink FPS, wall
FPS, backend FPS equivalent, payload/trace/report SHA references, semantic
comparison, expected cycle SHA and telemetry index. Its own `sha256sums.txt`
passes.

## H. Historical failed attempts

Both historical failed attempts remain present and are not treated as v3
Evidence:

- `/home/orin/edge-ai-local-evidence/stage_j/j5_attempts/j5_6_tuned_formal_baseline_v1`
- `/home/orin/edge-ai-local-evidence/stage_j/j5_attempts/j5_6_tuned_formal_baseline_v2`

Their failure records are retained. They do not invalidate the J5.6 v3
formal data; the J5.7 blocker is the independent J5.5 published-statistics
gap.

## I. Final decision

`J5.7 BLOCKED — J5.5 published formal statistics/telemetry evidence is incomplete.`

No J6 authorization is implied or granted. Remediation requires a separately
authorized Evidence/documentation decision; this gate does not rerun or patch
J5.5.
