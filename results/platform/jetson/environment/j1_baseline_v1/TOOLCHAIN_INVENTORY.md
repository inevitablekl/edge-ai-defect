# Platform and Toolchain Inventory

Status: `PASS_WITH_CARRIED_GAPS`

## Observed software platform

- Ubuntu: `22.04.5 LTS`
- Kernel: `5.15.185-tegra`
- L4T: `R36.5.0`
- Installed `nvidia-l4t-core`: `36.5.0-20260115194252`
- JetPack exact installed version: not independently verified
- `nvidia-jetpack` candidate: `6.2.2+b24`
- glibc: `2.35`
- Architecture: `aarch64`

## Native tools

- GCC/G++: `11.4.0`
- Make: `4.3`
- pkg-config: `0.29.2`
- CMake/CTest: missing; remediation required before J2 build work
- Ninja: missing; optional unless selected later
- patchelf: missing; assess before packaging

## Python and libraries

- Python: `3.10.12`
- NumPy: `1.21.5`
- PyYAML: `5.4.1`
- Python `cv2`: unavailable; non-blocking for the C++ Stage J path
- OpenCV C++: runtime and headers present, pkg-config/CMake metadata missing;
  remediation required before J3 configure/build
- yaml-cpp: missing; blocks J3 configure/build
- ONNX Runtime: absent before J2; official `1.23.2` build is pending J2
- CUDA/cuDNN/TensorRT: recorded-only pre-existing facts; not used by J1

J1.2 result: `COMPLETE`.
