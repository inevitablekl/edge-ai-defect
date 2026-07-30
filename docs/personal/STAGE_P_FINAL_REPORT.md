# Stage P Final Report

## 1. Objective

Stage P delivered and validated a bounded TensorRT pipeline runtime for the
accepted TensorRT FP16 deployment candidate. The scope covered exact
correctness, queue-capacity selection, Serial/Pipeline benchmarking, video
input, and long-running stability. No new feature or next-stage development is
authorized by this closeout.

## 2. Architecture

The production Pipeline topology is fixed as four workers and three bounded
SPSC queues:

```text
Source
  → bounded Q1 → Preprocess
  → bounded Q2 → Inference
  → bounded Q3 → Postprocess + Sink
```

There is one inference worker and at most one concurrent `engine.run()`.
Offline DirectorySource and VideoFileSource use bounded blocking semantics;
the selected queue capacity is `1`.

## 3. Correctness

P4, P5, and P7 preserve the frozen detection identity through the RUN/CYCLE
hash chain:

- P4: `P4_PIPELINE_CORRECTNESS_PASS`; Serial and Pipeline matched the frozen
  180-frame RUN and CYCLE hashes.
- P5: the corrected P5R contract requires same-window formal RUN hashes to
  match and every complete CYCLE hash to match the P4 expected CYCLE hash.
- P7: all 2281 complete cycles matched the expected P4 CYCLE SHA during the
  1800-second stability run.

The inherited raw TensorRT Level B limitation remains unchanged and is not
reinterpreted as raw numerical equality.

## 4. Benchmark

P5 selected queue capacity `1` as the smallest eligible capacity from the
1/2/4 pilot. The formal Serial/Pipeline benchmark recorded a paired ratio mean
of `4.165718` and sample SD `0.007915`; the corrected classification is
`MATERIAL_MEASURED_THROUGHPUT_INCREASE`. These are measured results under the
frozen protocol. Pipeline throughput improvement does not imply lower
single-frame end-to-end latency.

P5 final verdict:
`P5_PASS_WITH_THERMAL_STATUS_UNAVAILABLE`.

## 5. Video Support

`VideoFileSource` passed the frozen short MJPG validation asset. Serial and
Pipeline each processed 16 frames with zero drops and identical RUN SHA.
Video identity, codec, and asset SHA are retained in the P6 Evidence.

## 6. Stability

P7 completed a single bounded Pipeline lifecycle with a source-active interval
of `1800.006143093 s`. It processed `410691` frames, completed `2281` full
cycles, retained a 111-frame partial tail separately, and ended with all three
queues closed and drained and all four workers joined.

## 7. Limitations

- Thermal throttle status was unavailable; no no-throttling claim is made.
- The raw Level B TensorRT numerical limitation inherited from Stage K remains
  documented and unchanged.
- No industrial certification claim is made. The stability result is an
  engineering bounded-memory observation, not industrial leak certification.
- Raw traces, telemetry, generated video, and other large runtime artifacts are
  local-only Evidence and are not committed here.

## 8. Final Recommendation

Close Stage P as complete and retain the TensorRT FP16 Pipeline runtime as the
bounded throughput path, with queue capacity `1` frozen for the recorded
offline workload. Keep Serial as the reference runtime, preserve the explicit
thermal and raw Level B limitations, and base any future claims only on new
real measurements under separately authorized work.

Final verdict: `STAGE_P_COMPLETE_PIPELINE_RECOMMENDED`.
