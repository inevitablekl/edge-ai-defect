# P5R Protocol Amendment

Date: 2026-07-31

## Scope

This amendment corrects the P5 validity interpretation only. It does not
change runtime implementation, benchmark data, queue selection rule, measured
window, trace semantics, percentile definition, or any P4/P5 raw Evidence.

The historical P5 protocol and the original invalid-state report remain
unchanged and are retained under `attempt_001/`.

## Corrected hash contract

The former interpretation incorrectly required:

```text
P5 RUN SHA == P4 RUN SHA
```

P4 is a 180-frame single-cycle reference, while P5 pilot and formal runs are
extended windows of 1100 and 5100 accepted frames. Their RUN-domain input
lengths therefore differ. The P4 RUN SHA remains a single-cycle reference and
is not an expected hash for an extended P5 run.

For P5, RUN SHA is defined as:

```text
hash(all accepted frames in this run)
```

The six formal runs are valid when all six P5 RUN SHA values are identical.
P5 CYCLE SHA continues to inherit the P4 contract: every complete 180-frame
cycle must equal:

```text
6faee435cb3705c94406b5b295d8d053f49e5621b6f8aa6f7ada52c22f4531b3
```

Partial cycles are retained as descriptive digests and do not participate in
the complete-cycle PASS.

## Corrected thermal contract

`thermal_throttle_status=unavailable` is a known limitation, not an invalid
attempt. A run is invalid only when throttling is actually detected:

```text
RUN_INVALID_THERMAL_THROTTLING
```

Unavailable interfaces must remain explicitly recorded. They must not be
reported as a no-throttling PASS.

## Reclassification authority

This amendment is applied by
`P5_FINAL_RECLASSIFICATION_REPORT.md` to the already completed
`attempt_001` Evidence. No benchmark was rerun and no raw Evidence was
regenerated.
