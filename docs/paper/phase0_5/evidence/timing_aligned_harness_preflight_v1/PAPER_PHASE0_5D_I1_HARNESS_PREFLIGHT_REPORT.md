# Paper Phase 0.5D-I1 Harness Preflight Report

Decision: `HARNESS_READY_FOR_FORMAL_RUN`

This compact report records only protocol validation. The formal 15-run
benchmark was `NOT RUN`; all preflight metrics are `NOT FORMAL PERFORMANCE
EVIDENCE`.

| Variant | Warmup | Measured | Return code | Processed | Drops | EOS | Internal timing | Detection identity |
|---|---:|---:|---:|---:|---:|---|---|---|
| V0 | 3 | 16 | 0 | 16 | 0 | PASS | false | PASS |
| V2R | 3 | 16 | 0 | 16 | 0 | PASS | false | PASS |
| V3R | 3 | 16 | 0 | 16 | 0 | PASS | false | PASS |

The three Result v4 outputs have equal top-level and per-frame field sets and
contain no timing field. The V2R/V3R production dispatches use the accepted
OpenCV 4.5.4-aligned remediation identity. The formal schedule is frozen but
was not executed. Phase 0.5D-I2 is not authorized by this report.
