# Stage J J4 Entry Brief

状态：`CURRENT`

This brief records the single J4 entry state after D047 and J3.10 v2. It is
not a second Stage J Plan and does not copy Level A/B/C thresholds. The
thresholds and execution protocol remain exclusively in
[`STAGE_J_EXECUTION_PLAN.md`](STAGE_J_EXECUTION_PLAN.md) §18。

## 1. Authority hierarchy

1. Stage J Plan v0.3；
2. Accepted Decisions D041–D047；
3. Frozen Task Cards, interpreted by accepted Decisions；
4. Published Evidence；
5. The latest live-status section at the end of `TASKS.md`；
6. Summary documents。

Task Card `PENDING` values define cards; they do not override live status。

## 2. Entry point and J3 status

- Branch：`feature/jetson-onnxruntime`。
- Current HEAD：`f20b3b125f723562b8601e1f20519729d5d7d683`。
- J3 final status：`COMPLETE_WITH_ACCEPTED_THIRD_PARTY_LIMITATION`。
- J3.9 strict failure remains retained; D046 accepts the third-party
  OpenCV/TBB LeakSanitizer limitation as classification B。
- D047 reconciles the invalid J3.5 recorded SHA with the correct source
  commit `9b146317922561c55d91ad7126dbde4164b0c800`。
- Final J3 gate：`j3_10_j3_evidence_gate_v2`。
- J3.10 v1 remains retained and is superseded only for final provenance
  authority。

## 3. J4 mapping

- J4.1 — Level A correctness：Plan §18.1，`READY`。
- J4.2 — Level B runtime/integration：Plan §18.2，`PENDING`。
- J4.3 — Level C robustness：Plan §18.3，`PENDING`。
- J4.4 — Cross-level Evidence gate：Plan §18 and §26，`PENDING`。

The frozen Task Card §28 references are formally classified by D047 as
`FROZEN_CROSS_REFERENCE_DEFECT`; Plan §28 is J7 Consolidation. The J4.3
J3.9 entry dependency is satisfied by D046 and J3.10 v2. J4.3 does not start
a new sanitizer campaign。

## 4. Unified J4 validation profile

Every J4 level uses the common controlled profile defined by the frozen Plan:

- Controlled 1-Core；
- OpenCV threads `1`；
- ORT intra `1`；
- ORT inter `1`；
- sequential；
- spinning enabled；
- `MAXN_SUPER`；
- `jetson_clocks --fan`。

This brief intentionally does not duplicate the Level A/B/C thresholds。

## 5. Boundary

J4 has not started. J4.1 has not been executed. The next authorized task is
`J4.1 — Level A correctness`。Stage T and Stage P remain not started。
