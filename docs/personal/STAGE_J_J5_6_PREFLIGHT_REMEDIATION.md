# Stage J J5.6 Formal Preflight Remediation

## Scope

This document records a manual platform verification supplied for the J5.6
formal preflight Gate. It does not modify Stage J Plan v0.3, the J5.6 protocol,
D051, D052, the model, ModelContract, corpus or reference SHA values.

The verification is evidence for preflight only. No benchmark, formal run or
Evidence publication was performed while recording it.

## Manual platform verification

Source: owner-provided root-session output from:

```text
sudo jetson_clocks --show
sudo nvpmodel -q
```

Recorded facts:

```text
manual platform verification
SOC family: tegra234
Machine: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super
L4T: R36.5

CPU:
0-5 online
CPU frequency locked 1728000 MHz

GPU:
1020 MHz locked

EMC:
3199000000 MHz

FAN:
FAN Dynamic Speed Control=disabled
hwmon0_pwm1=255

Power:
MAXN_SUPER

sudo nvpmodel -q:

NV Power Mode: MAXN_SUPER
2
```

The accepted fan verification source is `jetson_clocks --show` output showing
`FAN Dynamic Speed Control=disabled` and `hwmon*_pwm1=255`. The preflight does
not read or require `fan1_input`; absence of that non-authoritative hwmon node
is not a failure.

## Build artifact provenance

The frozen protocol requires a native Jetson aarch64 Release artifact; it does
not require a repository-local directory named `build/`. The accepted external
Release artifact is recorded explicitly, including its path difference:

```text
stage_j_profile_runner:
/home/orin/edge-ai-local-build/r2-stage-j-tooling-on/stage_j_profile_runner
SHA256: e5a69f3be8f64ed0ac086148998040e8380f4eb2610ae1959829ca215829c725

edge_ai_defect:
/home/orin/edge-ai-local-build/r2-stage-j-tooling-on/edge_ai_defect
SHA256: bd02668f345dd0c232a0a84f64309d0b04017b177c33cbd29e32fcf45f114014
```

The repository-local `build/` directory remains absent. This is not treated as
a failure because the frozen build contract and the existing Stage J build
provenance use external native Release build roots. The path distinction is
retained and is reported by the tooling.

## Gate result

The complete preflight was executed with the explicit manual verification file
and external Release artifact paths: `PASS`. The formal execution
authorization remains separate and requires an explicit
`--execute-formal --profile k5 --evidence-id <new-id>` invocation. No formal
benchmark was started by this remediation.
