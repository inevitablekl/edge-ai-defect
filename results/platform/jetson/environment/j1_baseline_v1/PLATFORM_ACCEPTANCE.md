# J1 Platform Acceptance Summary

Status: `PASS`

## Device

- Observed platform: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit Super
- Architecture: `aarch64`
- SoC family: `Tegra234`
- Observed MemTotal: `7976910848` bytes
- Nominal SKU: `8GB`; observed memory is consistent with the nominal SKU

## Storage and boot

- NVMe model label: `PUSKILL`
- NVMe capacity: `256060514304` bytes
- Root filesystem: NVMe, ext4, read-write
- Boot slots: A/B accepted
- SMART critical warning: `0`
- SMART media/data integrity errors: `0`
- Historical unsafe shutdown counter: `11`; no increase during J1 acceptance

## User-confirmed conditions

- Active fan and heatsink: `USER_CONFIRMED`
- Stable original power adapter: `USER_CONFIRMED`
- Device exclusivity: `USER_CONFIRMED`
- Known random reboot, power loss or NVMe drop: none reported

J1.1 result: `COMPLETE`.
