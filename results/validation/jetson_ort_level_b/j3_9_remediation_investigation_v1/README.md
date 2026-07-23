# J3.9 remediation investigation

Classification: **B — third-party OpenCV/TBB initialization leak**

Scenario A reproduced the original LeakSanitizer result in an independent
diagnostic build. Scenario B used a diagnostic-only dynamic shim to bypass
OpenCV thread-policy activation while preserving the expected thread-count
readback; the same test then passed with leak detection enabled. Scenario C
kept current code, disabled only leak detection, and passed with no non-leak
ASan/UBSan diagnostic.

No production source, test logic, CMake sanitizer flag, Release build, ORT SDK,
model asset or frozen asset was modified. The original J3.9 failure evidence
was verified intact and not changed.
