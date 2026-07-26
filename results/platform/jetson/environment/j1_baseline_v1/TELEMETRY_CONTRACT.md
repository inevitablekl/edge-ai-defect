# Telemetry and Throttling Contract

Decision authority: `D042 Accepted`.

## Thermal

Readable relevant set:

- `cpu-thermal`
- `gpu-thermal`
- `soc0-thermal`
- `soc1-thermal`
- `soc2-thermal`
- `tj-thermal`

Excluded inventory set: `cv0-thermal`, `cv1-thermal`, `cv2-thermal`; their
temperature reads returned stable `EAGAIN`. They are not converted to zero or
included in the numeric maximum. Raw unit is milli-degree Celsius. Formal
`T_idle_ref` uses five minutes idle followed by 60 one-second relevant-set
maximum samples and their median; J1.4 did not establish a reference.

## Frequency and EMC

- CPU sources: policy0/policy4 `scaling_cur_freq`, target `1728000 kHz`
- GPU source: discovered devfreq `cur_freq`, target `1020000000 Hz`
- EMC cap source: `/sys/kernel/nvpmodel_clk_cap/emc`, target `3199000000 Hz`
- EMC start/end authority: `jetson_clocks --show` current/max and
  `FreqOverride=1`
- Independent ordinary-user 1Hz EMC runtime source: unavailable
- EMC is not part of the per-second sustained-frequency sequence

## tegrastats and rails

- Executable: `/usr/bin/tegrastats`
- Package: `nvidia-l4t-tools 36.5.0-20260115194252`
- Interval: `1000 ms`
- Rail set: `VDD_IN`, `VDD_CPU_GPU_CV`, `VDD_SOC`
- Rail pair: `current/sample power / device-emitted average power`, mW
- First value is used for formal statistics; second value is diagnostic only
- This is onboard rail telemetry, not wall power or precision energy measurement

## OC/UV and alarms

- OC1: Under Voltage; cumulative counter delta `>0` is hard failure
- OC2: Average Overcurrent; cumulative counter delta `>0` is hard failure
- OC3: Instantaneous Overcurrent; cumulative counter delta `>0` is hard failure
- Current counters: `0`, `0`, `0`
- Current throttle-enable values: `1`, `1`, `1`
- INA3221 required alarm values: all `0`; any non-zero per-sample alarm is hard failure
- Counters are recorded at attempt start/end and are not reset in-run

## Sustained throttling v1

Sample every one second using monotonic timestamps. Monitor CPU policy0,
policy4 and GPU runtime frequency. Three consecutive valid samples below target
for one source are a hard sustained-throttling failure. One or two samples are
warnings unless paired with an OC/UV counter delta or alarm. Gaps over 2500 ms,
coverage below 0.90 or required-source failures invalidate the run. Thermal and
frequency gates remain independent. With all allowed CPUs, telemetry CPU0
overlap is recorded as an interference limitation.

## Environment drift

Hard-match fields include kernel/L4T/package/config hashes, mode and CPU sets,
frequency paths and targets, EMC state, fan state, thermal paths, tegrastats,
rail set, OC/UV fields, enable values and wrapper hashes. Boot ID is per-attempt;
reboot invalidates the resolved reference.

J1.4 result: `COMPLETE`.
