# J3.9 Jetson ASan/UBSan validation

Verdict: **FAIL / STOP**

The independent native aarch64 C++17 sanitizer build configured and built
successfully. With LeakSanitizer enabled, `runtime_config` failed on a
792-byte leak in 3 allocations. The allocation stack is in system TBB reached
through OpenCV `cv::setNumThreads(1)` from
`PortableControlSession::start`. `serial_runner` passed.

Per protocol, no code was modified and no further test, application, model,
inference or benchmark operation was started. J4 and subsequent tasks were
not entered.
