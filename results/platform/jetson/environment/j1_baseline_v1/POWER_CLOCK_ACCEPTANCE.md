# Power and Clock Acceptance

Status: `PASS`

## Transition

- Pre-state: `15W` / mode ID `0`
- Accepted state: `MAXN_SUPER` / mode ID `2`
- Reboot required: `false`
- Silent fallback: not observed

## Controlled state

- CPU online set: `0-5`
- CPU locked target: `1728000 kHz`
- GPU locked target: `1020000000 Hz`
- EMC observed target: `3199000000 Hz`
- `jetson_clocks` apply: accepted in J1.3
- `jetson_clocks --fan` apply: accepted in J1.3
- Fan PWM: `255`
- Dynamic fan speed control: disabled
- `nvfancontrol`: inactive after fan-control apply
- Reboot since J1.3 acceptance: `false`

J1.3 result: `COMPLETE`.
