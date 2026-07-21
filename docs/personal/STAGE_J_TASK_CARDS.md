# Stage J Milestone Task Cards v0.1 — FROZEN

- Document status: `FROZEN`
- Version: `v0.1`
- Parent protocol: `Stage J Plan v0.3 — FROZEN`
- Stage J status: `PENDING`
- J0 status: `IN PROGRESS`
- J0.5 status: `IN_PROGRESS`
- Implementation branch: `not created` (J0.6 pending)
- Production implementation: `not started`
- Device-dependent facts: pending J1; Jetson/JetPack/MAXN_SUPER/ORT aarch64 values below are planned contracts, not observations.

## Frozen starting facts

- Repository `edge-ai-defect`; branch `main`; task-card source commit `6e1c46ac4f9d09ef2e620f316723957144a66cf0`.
- Frozen plan SHA256: `a723ae1ffae70366c7435313869f5a2ec1318c47ed43398ffdfcf40e8ba6a9bd`; D041 is `Accepted`.
- M0–M5 are `CLOSED`; baseline tag `m5-onnxruntime-baseline-v1`; CMake target `edge_ai_infer`; executable `edge_ai_defect`.
- Inventory `configs/stage_j/test_inventory.yaml`, source commit `2da4d2cae6c5075e516c7edcfbd28e52f5301299`, has Model Smoke OFF `31`, ON `39`, and JTEST-001–JTEST-011; all future JTEST cards remain `not_implemented` with no CTest name.
- Device identity, JetPack/L4T, MAXN_SUPER, thermal/rail/OCUV and target ORT aarch64 facts are unavailable until J1; product pages cannot substitute for observed Evidence.

## Card contract

Allowed statuses are only `PENDING`, `READY`, `BLOCKED`, `IN_PROGRESS`, `COMPLETE`, `FAILED`, `SUPERSEDED`, `NOT_APPLICABLE`. Every card has the complete frozen field set below. J1 is device-blocked; J2–J9 are not executed and none is COMPLETE. Device-dependent work remains blocked by the unexecuted J1/J0.6 gates even where its frozen card status is `PENDING`.

## J1.1 — Device Identity, Storage and Flash Acceptance

- Milestone: J1
- Status: BLOCKED
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §5, §8
- Dependencies: J0.6; device access
- Blocking conditions: J0.6 and reachable target device are required; this card is BLOCKED.
- Objective: Freeze and execute the J1.1 contract for Device Identity, Storage and Flash Acceptance.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: When the device is available, collect direct observations and preserve raw command output; do not infer values.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Identity, version, telemetry, command, timestamp and provenance output.
- Published Evidence destination: results/platform/jetson/environment/<evidence_id>/
- PASS criteria: All required facts are directly observed, complete and internally consistent.
- FAIL / BLOCKED criteria: Device unavailable, unsafe, contradictory or unverifiable observation => remain BLOCKED.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J1.1 Device Identity, Storage and Flash Acceptance`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Provide target access and review observed facts.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J1.2 — JetPack/L4T/toolchain inventory

- Milestone: J1
- Status: BLOCKED
- Task type: evidence
- Parent protocol sections: Stage J Plan v0.3 §5, §8
- Dependencies: J1.1; device access
- Blocking conditions: J0.6 and reachable target device are required; this card is BLOCKED.
- Objective: Freeze and execute the J1.2 contract for JetPack/L4T/toolchain inventory.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: When the device is available, collect direct observations and preserve raw command output; do not infer values.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Identity, version, telemetry, command, timestamp and provenance output.
- Published Evidence destination: results/platform/jetson/environment/<evidence_id>/
- PASS criteria: All required facts are directly observed, complete and internally consistent.
- FAIL / BLOCKED criteria: Device unavailable, unsafe, contradictory or unverifiable observation => remain BLOCKED.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J1.2 JetPack/L4T/toolchain inventory`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Provide target access and review observed facts.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J1.3 — MAXN_SUPER and clocks

- Milestone: J1
- Status: BLOCKED
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §5, §8
- Dependencies: J1.1; device access
- Blocking conditions: J0.6 and reachable target device are required; this card is BLOCKED.
- Objective: Freeze and execute the J1.3 contract for MAXN_SUPER and clocks.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: When the device is available, collect direct observations and preserve raw command output; do not infer values.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Identity, version, telemetry, command, timestamp and provenance output.
- Published Evidence destination: results/platform/jetson/environment/<evidence_id>/
- PASS criteria: All required facts are directly observed, complete and internally consistent.
- FAIL / BLOCKED criteria: Device unavailable, unsafe, contradictory or unverifiable observation => remain BLOCKED.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J1.3 MAXN_SUPER and clocks`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Provide target access and review observed facts.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J1.4 — Thermal, frequency, rail and OCUV discovery

- Milestone: J1
- Status: BLOCKED
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §5, §8
- Dependencies: J1.1; J1.3; device access
- Blocking conditions: J0.6 and reachable target device are required; this card is BLOCKED.
- Objective: Freeze and execute the J1.4 contract for Thermal, frequency, rail and OCUV discovery.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: When the device is available, collect direct observations and preserve raw command output; do not infer values.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Identity, version, telemetry, command, timestamp and provenance output.
- Published Evidence destination: results/platform/jetson/environment/<evidence_id>/
- PASS criteria: All required facts are directly observed, complete and internally consistent.
- FAIL / BLOCKED criteria: Device unavailable, unsafe, contradictory or unverifiable observation => remain BLOCKED.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J1.4 Thermal, frequency, rail and OCUV discovery`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Provide target access and review observed facts.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J1.5 — Platform Evidence gate

- Milestone: J1
- Status: BLOCKED
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §5, §8
- Dependencies: J1.1–J1.4
- Blocking conditions: J0.6 and reachable target device are required; this card is BLOCKED.
- Objective: Freeze and execute the J1.5 contract for Platform Evidence gate.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: When the device is available, collect direct observations and preserve raw command output; do not infer values.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Identity, version, telemetry, command, timestamp and provenance output.
- Published Evidence destination: results/platform/jetson/environment/<evidence_id>/
- PASS criteria: All required facts are directly observed, complete and internally consistent.
- FAIL / BLOCKED criteria: Device unavailable, unsafe, contradictory or unverifiable observation => remain BLOCKED.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J1.5 Platform Evidence gate`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Provide target access and review observed facts.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J2.0 — Build interface discovery

- Milestone: J2
- Status: PENDING
- Task type: planning
- Parent protocol sections: Stage J Plan v0.3 §24.2–§24.5
- Dependencies: J0.6; J1 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J2.0 contract for Build interface discovery.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/build/onnxruntime_aarch64/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J2.0 Build interface discovery`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J2.1 — Development feasibility probe

- Milestone: J2
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §24.2–§24.5
- Dependencies: J2.0; J1 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J2.1 contract for Development feasibility probe.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/build/onnxruntime_aarch64/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J2.1 Development feasibility probe`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J2.2 — Formal clean build

- Milestone: J2
- Status: PENDING
- Task type: build
- Parent protocol sections: Stage J Plan v0.3 §24.2–§24.5
- Dependencies: J2.0; J2.1; J1 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J2.2 contract for Formal clean build.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/build/onnxruntime_aarch64/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J2.2 Formal clean build`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J2.3 — SDK packaging and manifest

- Milestone: J2
- Status: PENDING
- Task type: evidence
- Parent protocol sections: Stage J Plan v0.3 §24.2–§24.5
- Dependencies: J2.2
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J2.3 contract for SDK packaging and manifest.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/build/onnxruntime_aarch64/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J2.3 SDK packaging and manifest`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J2.4 — RPATH smoke

- Milestone: J2
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §24.2–§24.5
- Dependencies: J2.3
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J2.4 contract for RPATH smoke.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/build/onnxruntime_aarch64/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J2.4 RPATH smoke`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J2.5 — J2 Evidence gate

- Milestone: J2
- Status: PENDING
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §24.2–§24.5
- Dependencies: J2.2–J2.4
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J2.5 contract for J2 Evidence gate.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/build/onnxruntime_aarch64/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J2.5 J2 Evidence gate`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J3.1 — aarch64 build and CMake portability

- Milestone: J3
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J2.5 PASS; J0.6
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.1 contract for aarch64 build and CMake portability.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J3.1 aarch64 build and CMake portability`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.2 — RuntimeConfig v2

- Milestone: J3
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.1
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.2 contract for RuntimeConfig v2.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J3.2 RuntimeConfig v2`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.3 — Immutable ORT options record

- Milestone: J3
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.2
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.3 contract for Immutable ORT options record.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J3.3 Immutable ORT options record`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.4 — OpenCV thread policy

- Milestone: J3
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.2
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.4 contract for OpenCV thread policy.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J3.4 OpenCV thread policy`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.5 — Trace observer and recorder

- Milestone: J3
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.2; J3.3
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.5 contract for Trace observer and recorder.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J3.5 Trace observer and recorder`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.6 — Portable control utilities

- Milestone: J3
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.1; J3.5
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.6 contract for Portable control utilities.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J3.6 Portable control utilities`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.7 — Historical v1 regression

- Milestone: J3
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.1–J3.6
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.7 contract for Historical v1 regression.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J3.7 Historical v1 regression`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.8 — Jetson regression

- Milestone: J3
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J2 SDK; J3.1–J3.7
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.8 contract for Jetson regression.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J3.8 Jetson regression`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J3.9 — Jetson ASan/UBSan

- Milestone: J3
- Status: PENDING
- Task type: stability
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.8; J3 production/inventory
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.9 contract for Jetson ASan/UBSan.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J3.9 Jetson ASan/UBSan`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J3.10 — J3 Evidence gate

- Milestone: J3
- Status: PENDING
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §25
- Dependencies: J3.7–J3.9
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J3.10 contract for J3 Evidence gate.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_b/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J3.10 J3 Evidence gate`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J4.1 — Level A correctness

- Milestone: J4
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §28
- Dependencies: J3.10 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J4.1 contract for Level A correctness.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_c/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J4.1 Level A correctness`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J4.2 — Level B runtime/integration

- Milestone: J4
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §28
- Dependencies: J4.1 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J4.2 contract for Level B runtime/integration.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_c/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J4.2 Level B runtime/integration`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J4.3 — Level C robustness/sanitizer

- Milestone: J4
- Status: PENDING
- Task type: stability
- Parent protocol sections: Stage J Plan v0.3 §28
- Dependencies: J4.2 PASS; J3.9 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J4.3 contract for Level C robustness/sanitizer.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_c/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J4.3 Level C robustness/sanitizer`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J4.4 — Cross-level Evidence gate

- Milestone: J4
- Status: PENDING
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §28
- Dependencies: J4.1–J4.3
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J4.4 contract for Cross-level Evidence gate.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/validation/jetson_ort_level_c/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J4.4 Cross-level Evidence gate`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J5.1 — Benchmark launcher and protocol

- Milestone: J5
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J4.4 PASS; J3.6
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.1 contract for Benchmark launcher and protocol.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J5.1 Benchmark launcher and protocol`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J5.1a — Launcher and provenance contract

- Milestone: J5
- Status: PENDING
- Task type: documentation
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.1
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.1a contract for Launcher and provenance contract.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.1a Launcher and provenance contract`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J5.1b — Python reference

- Milestone: J5
- Status: PENDING
- Task type: implementation
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.1; J5.1a
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.1b contract for Python reference.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: Only the exact production/runtime paths named in the execution report (for example the applicable CMakeLists.txt, src/, include/ or tools/ file); no unlisted path.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: One independent source commit; formal Evidence is a separate commit.
- Suggested commit subject: `feat: execute J5.1b Python reference`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J5.1c — Smoke and evidence budget

- Milestone: J5
- Status: PENDING
- Task type: planning
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.1; J5.1b
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.1c contract for Smoke and evidence budget.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.1c Smoke and evidence budget`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J5.2 — Candidate semantic precheck

- Milestone: J5
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.1b; J5.1c
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.2 contract for Candidate semantic precheck.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.2 Candidate semantic precheck`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J5.3 — Candidate sizing

- Milestone: J5
- Status: PENDING
- Task type: benchmark
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.2 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.3 contract for Candidate sizing.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.3 Candidate sizing`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J5.4 — Profile selection campaign

- Milestone: J5
- Status: PENDING
- Task type: benchmark
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: all candidate J5.2/J5.3
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.4 contract for Profile selection campaign.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.4 Profile selection campaign`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J5.5 — Controlled 1-Core formal baseline

- Milestone: J5
- Status: PENDING
- Task type: benchmark
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.4 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.5 contract for Controlled 1-Core formal baseline.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.5 Controlled 1-Core formal baseline`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J5.6 — Tuned k-Core formal baseline

- Milestone: J5
- Status: PENDING
- Task type: benchmark
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.4 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.6 contract for Tuned k-Core formal baseline.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.6 Tuned k-Core formal baseline`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J5.7 — J5 Evidence gate

- Milestone: J5
- Status: PENDING
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §24.6–§24.8, §26–§28
- Dependencies: J5.1–J5.6
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J5.7 contract for J5 Evidence gate.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/benchmark/jetson_ort_cpu/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J5.7 J5 Evidence gate`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J6.1 — Stability components and canonical parity

- Milestone: J6
- Status: PENDING
- Task type: stability
- Parent protocol sections: Stage J Plan v0.3 §24.9, §28
- Dependencies: J5.7 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J6.1 contract for Stability components and canonical parity.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/stability/jetson_ort_cpu/tuned_30min/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J6.1 Stability components and canonical parity`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J6.2 — Precheck and target cycle

- Milestone: J6
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §24.9, §28
- Dependencies: J6.1
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J6.2 contract for Precheck and target cycle.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/stability/jetson_ort_cpu/tuned_30min/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J6.2 Precheck and target cycle`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J6.3 — Formal 30-minute stability

- Milestone: J6
- Status: PENDING
- Task type: stability
- Parent protocol sections: Stage J Plan v0.3 §24.9, §28
- Dependencies: J6.2 PASS; J5.7 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J6.3 contract for Formal 30-minute stability.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/stability/jetson_ort_cpu/tuned_30min/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J6.3 Formal 30-minute stability`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J6.4 — Stability analysis and gate

- Milestone: J6
- Status: PENDING
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §24.9, §28
- Dependencies: J6.3
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J6.4 contract for Stability analysis and gate.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/stability/jetson_ort_cpu/tuned_30min/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J6.4 Stability analysis and gate`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J7.1 — Consolidation generation

- Milestone: J7
- Status: PENDING
- Task type: evidence
- Parent protocol sections: Stage J Plan v0.3 §27–§28
- Dependencies: J1.5; J2.5; J3.10; J4.4; J5.7; J6.4
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J7.1 contract for Consolidation generation.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/consolidation/stage_j/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J7.1 Consolidation generation`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J7.2 — Consolidation self-validation

- Milestone: J7
- Status: PENDING
- Task type: validation
- Parent protocol sections: Stage J Plan v0.3 §27–§28
- Dependencies: J7.1
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J7.2 contract for Consolidation self-validation.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/consolidation/stage_j/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J7.2 Consolidation self-validation`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J8.1 — Independent reconstruction audit

- Milestone: J8
- Status: PENDING
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §29
- Dependencies: J7.2
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J8.1 contract for Independent reconstruction audit.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/audit/stage_j_deep_gate/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J8.1 Independent reconstruction audit`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J8.2 — Deep gate decision

- Milestone: J8
- Status: PENDING
- Task type: audit
- Parent protocol sections: Stage J Plan v0.3 §29
- Dependencies: J8.1
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J8.2 contract for Deep gate decision.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: results/audit/stage_j_deep_gate/<evidence_id>/
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J8.2 Deep gate decision`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Sol
- Suggested reasoning level: High

## J9.1 — Documentation closeout

- Milestone: J9
- Status: PENDING
- Task type: documentation
- Parent protocol sections: Stage J Plan v0.3 §30
- Dependencies: J8.2 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J9.1 contract for Documentation closeout.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: None; documentation or handoff only
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J9.1 Documentation closeout`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## J9.2 — User merge, tag and backup handoff

- Milestone: J9
- Status: PENDING
- Task type: documentation
- Parent protocol sections: Stage J Plan v0.3 §30
- Dependencies: J9.1; J8.2 PASS
- Blocking conditions: All dependencies and preceding PASS gates are required; no gate may be skipped.
- Objective: Freeze and execute the J9.2 contract for User merge, tag and backup handoff.
- Inputs and frozen contracts: D041 Accepted; frozen Stage J Plan v0.3; J0.4 inventory (31/39, JTEST-001–011); upstream accepted outputs listed in Dependencies.
- Allowed repository changes: No repository change during the attempt, except the exact manifest/index/report path declared for this card.
- Prohibited changes: No unlisted source, CMake, test-name, inventory, build-metadata, frozen-plan or historical-Evidence changes; no Stage T/P/R work.
- Required implementation or execution steps: Execute one atomic protocol using frozen inputs, preserve raw attempts, and record source/evidence commit relations.
- Required validation: Verify exact scope, dependency PASS, provenance, hashes and the card-specific PASS/FAIL gate before proceeding.
- Required raw attempt outputs: Commands, return codes, logs, hashes, environment provenance and rejection details.
- Published Evidence destination: None; documentation or handoff only
- PASS criteria: All protocol assertions pass with reproducible raw outputs and complete provenance.
- FAIL / BLOCKED criteria: Any failed assertion, missing raw output, wrong scope or dependency gate => FAILED/BLOCKED and stop.
- Invalidation and rerun scope: Invalidate only the affected attempt and rerun the complete card protocol after any remediation; publish a new Evidence ID.
- Commit boundary: No source commit for a pure attempt; any remediation uses a new source commit.
- Suggested commit subject: `docs: execute J9.2 User merge, tag and backup handoff`
- Agent stop conditions: Stop at the first failed hard gate, unsafe device condition, scope drift or missing provenance; do not start the next card.
- User actions required: Review the Execution Report/gate and authorize the next card; user performs merge/tag/backup/push.
- Suggested model: GPT-5.6 Terra
- Suggested reasoning level: Medium

## Dependency graph

```text
J0.6 ↓ J1 ↓ J2 ↓ J3 ↓ J4 ↓ J5 ↓ J6 ↓ J7 ↓ J8 ↓ J9
```

Internal dependencies: `J2.2 ← J2.0/J2.1`; `J3.8 ← J2 SDK`; `J3.9 ← J3 production/inventory`; `J4 ← J3 PASS`; `J5.2 ← J5.1b`; `J5.4 ← all candidate J5.2/J5.3`; `J5.5/J5.6 ← J5.4`; `J6 ← J5.6/J5.7`; `J7 ← J1–J6 published Evidence`; `J8 ← J7`; `J9 ← J8 PASS`.

## Unified execution, Evidence and commit strategy

- One card/atomic subcard at a time from a clean committed HEAD; every attempt has an Execution Report. A failed gate stops the next card; no hard gate is skipped.
- Exact test-name inventory is authoritative, not counts. Smoke is not formal Evidence; one run cannot replace a required five-run role; campaigns cannot be spliced; WSL↔Jetson speedup is never a Stage J claim.
- Each implementation subtask has an independent source commit. Production/source and formal Evidence are never the same commit. Evidence IDs use the actual source commit; unknown future SHAs are never prefilled. Failed local attempts are task records, not published Evidence. Remediation uses a new source commit and Evidence ID.
- J7 creates a new consolidation directory; J8 creates a new audit directory and never edits J1–J7 Evidence; J9 is documentation/handoff only. The agent does not push or perform user merge/tag/backup actions.

## Scope exclusions

These cards do not redefine the frozen plan, D041, J0.4 inventory, CMake registration or M0–M5 Evidence. Stage T/P/R implementation is out of scope. Future JTEST-001–JTEST-011 remain `not_implemented` with `ctest_name: null` and do not enter the current baseline.
