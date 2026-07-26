# J3.10 v2 — J3 Evidence Gate and J4 Entry Reconciliation

Verdict: **PASS**.

This v2 Evidence is the final J3 provenance authority under D047. It
reconciles the invalid J3.5 source-commit record using direct ancestry and an
Evidence-only successor commit. The original J3.5 Evidence and J3.10 v1 are
retained unchanged; v1 is superseded only for final provenance authority.

J3 final status is `COMPLETE_WITH_ACCEPTED_THIRD_PARTY_LIMITATION`. The J3.9
strict LeakSanitizer failure remains retained, with D046 accepting the
documented third-party OpenCV/TBB initialization limitation. J4 is not
started; J4.1 is READY.

This is a documentation and provenance gate. No technical J3 rerun, model
loading, inference, benchmark, sanitizer campaign, ORT rebuild, TensorRT,
CUDA EP, ROS2, camera operation, or J4.1 execution was performed.
