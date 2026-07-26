# J4.2 Level B under D048

The original Stage J Plan §18.2 strict Gate failed and remains explicitly recorded as `strict_plan_gate_pass=false`. D048 acceptance passed for the frozen Jetson Orin Nano Super aarch64 / ORT 1.23.2 CPU-only combination. The final status is `COMPLETE_WITH_ACCEPTED_CROSS_ARCH_NUMERICAL_LIMITATION`, not an unqualified strict PASS.

The two Jetson raw outputs are deterministic and use the canonical AArch64 SHA recorded in `raw_output_identity.json`. The D048 envelope does not relax J4.3: Level C retains its own strict matching, confidence, bbox and byte-identity requirements. J4.3 was not executed.
