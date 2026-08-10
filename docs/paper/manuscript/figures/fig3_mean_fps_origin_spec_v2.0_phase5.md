# Target Figure 3 Origin Specification v2.0

Status: `PHASE5_PREPARATION_ONLY`; final production owner: `USER_MANUAL_ORIGIN`.

## Data authority

Import `fig2_mean_fps_origin_data.csv` without recalculation or retyping:

| Variant | Mean FPS | Sample SD FPS |
|---|---:|---:|
| V0 | 54.600 | 0.223 |
| V2R | 122.122 | 0.492 |
| V3R | 127.097 | 1.279 |

The error bars are sample standard deviations of FPS across five independent process-level runs. They are not confidence intervals, standard errors, population standard deviations, or significance intervals.

## Origin construction

1. Set `Variant` as categorical X in V0, V2R, V3R order.
2. Plot `Mean_FPS` as three vertical bars from a zero baseline.
3. Add symmetric Y error bars from `Sample_SD_FPS`.
4. Y title: `平均帧率/(frame·s⁻¹)`; no broken axis.
5. Apply the shared variant identity: V0 white/no hatch; V2R white/diagonal hatch; V3R white/cross-hatch; all use equal black outlines and equal apparent luminance.
6. Optional data labels use exactly `54.600`, `122.122`, and `127.097`; do not label derived ratios in the plot.
7. Use no p-values, brackets, asterisks, CI language, gradient, 3D, shadow, or decorative background.

Target caption: `图3　V0、V2R和V3R平均帧率比较。误差棒表示5次独立进程级运行FPS的样本标准差。`

Target outputs: `fig3_mean_fps_phase5_final.opju`, `.pdf`, `.svg`, and a print-review `.png`. The OPJU and exports remain candidates until later acceptance/integration.
