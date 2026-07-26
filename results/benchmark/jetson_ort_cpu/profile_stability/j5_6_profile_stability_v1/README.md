# J5.6 Tuned Profile Stability

Status: COMPLETE

Only the D051-frozen Tuned profile k5 was executed. No profile comparison or profile reselection was performed.

The run lasted 1,800,546 ms (30.009 minutes) and completed 771 repeated 20-image inference cycles. Every cycle exited successfully, used CPU affinity 1-5, matched the frozen k5 semantic output SHA, and passed the finite-value check. No images, model files, or raw large telemetry logs are included in this published evidence.

Thermal-throttle counters were not exposed by the available sysfs paths during the run; tegrastats showed no explicit throttle event field. This is recorded as unavailable, not as a fabricated PASS.
