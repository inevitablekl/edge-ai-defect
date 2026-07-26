# J4.2 Cross-Architecture Numerical Investigation

Status: `CLOSED_BY_D048`

## Scope

This record reconciles the original strict J4.2 Level B failure and documents
the accepted D048 policy. It does not modify the original `j4.2_level_b_v1`
formal result, frozen assets, production code or ORT SDK.

## Original strict result

The Jetson aarch64 two-process result was deterministic:

- overall MAE: `6.972924584434146e-06`;
- overall max_abs: `0.001068115234375`;
- bbox MAE: `1.7397602399190266e-05`;
- bbox max_abs: `0.001068115234375`;
- score MAE: `2.3139374596732005e-08`;
- score max_abs: `4.76837158203125e-07`;
- maximum error: channel 3, candidate 6803, flat index 32003；
- finite/NaN/+Inf/-Inf: `84000/0/0/0`；
- both raw outputs SHA256:
  `a64a1028c3ce0c3b6cf2263122fe555338a75dd38bd9cbb6b0f62495359af358`；
- raw outputs and reports were byte-identical across the two processes。

The original Plan §18.2 strict result is therefore permanently recorded as
`strict_plan_gate_pass=false`.

## Reference and diagnostic evidence

The WSL2 x86_64 Python reference used Python 3.10.12, NumPy 1.26.4, ORT
1.23.2, CPUExecutionProvider, ORT sequential mode, ORT_ENABLE_ALL and
intra/inter-op threads 1. Its two-process output was deterministic and had
SHA256 `c3b17b6072147afb126c9ce812184703e4f75966db07a9433f50f829d892f254`.
The historical x86 C++ Level B result exactly matched that Python golden.

On Jetson, the controlled direct-ORT diagnostics were:

| Scenario | Graph optimization | Intra/inter | MAE | max_abs |
|---|---|---:|---:|---:|
| A current | ORT_ENABLE_ALL | 1/1 | 6.97292e-06 | 0.00106812 |
| B diagnostic | ORT_DISABLE_ALL | 1/1 | 6.97292e-06 | 0.00106812 |
| C diagnostic | ORT_ENABLE_ALL | 1/1 | 6.97292e-06 | 0.00106812 |

The result did not change with graph optimization or the tested thread
configuration. The mismatch is concentrated in bbox channel 3; score error
is far smaller and all values are finite.

## Conclusion boundary

The supported engineering attribution is
`SUPPORTED_CROSS_ARCH_ORT_CPU_NUMERICAL_DRIFT`. The evidence does not prove a
single MLAS, convolution or other kernel root cause. No production code
change and no ORT rebuild is required by this investigation.

## D048 policy

D048 accepts only the frozen Jetson/aarch64/ORT 1.23.2 CPU-only combination
and its deterministic canonical raw SHA under the numerical envelope recorded
in `docs/personal/DECISIONS.md`. The strict Gate remains visible and failed;
D048 acceptance is a separate result. J4.3's own Level C Gate remains
unchanged.

## Attempt integrity

The original 19-file formal attempt is preserved. Three later forensic files
are retained as append-only historical diagnostic artifacts and are not
treated as original formal runner output. No original raw output, report,
runtime record, model, input or golden was overwritten.
