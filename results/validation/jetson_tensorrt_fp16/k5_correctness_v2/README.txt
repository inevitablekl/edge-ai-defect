Stage K K5.2 ORT Control Re-evaluation after D063

Attempt: k5_correctness_v2
Source commit: 838e2bfbfc84cb378ea629f9ff316828ed86fe09
Reference Bundle: stage_k_level_b_reference_v1
Reference Bundle SHA256: fed5755ce630d0902449f3052fcbb915592245583df19bf924ec867d1c1e1e29

This Evidence records a new immutable ORT control re-evaluation. The prior
K5 failure Evidence at k5_correctness_v1 remains unchanged.

ORT Level B:
- 16/16 Jetson C++ ORT inferences succeeded.
- Strict Gate: FAIL, 0/16, with the original MAE <= 1e-6 and max_abs <= 1e-4.
- Jetson repeatability: PASS, 16/16 byte-identical.
- D063 inherited cross-architecture evaluation: PASS_WITH_INHERITED_LIMITATION.
  The drift remains bbox-dominated, score channels are bounded, and input
  identity, exact output shape, and finite output checks pass.

ORT Level C:
- Original-image semantic comparison: PASS, 16/16.
- Confidence maximum absolute error: 2.65265835569517e-06.
- Bbox maximum coordinate absolute error: 0.0003051264160163214.
- Original strict Level C limits were retained: confidence <= 1e-4 and
  bbox coordinate <= 0.01.

Final ORT Control disposition:
INHERITED_CROSS_ARCH_LIMITATION

This is not TensorRT correctness Evidence and does not authorize TensorRT
Level B/C, benchmark, stability, Pipeline, or K6.
