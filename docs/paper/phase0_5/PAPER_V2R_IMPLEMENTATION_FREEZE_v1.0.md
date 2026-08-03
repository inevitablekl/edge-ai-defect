# Paper V2R Implementation Freeze v1.0

## 1. Verdict

`I1_READY_FOR_GATE_D`

## 2. Frozen Implementation Identity

- Remediation ID: `opencv_4_5_4_aligned_fixed_contract_cuda_resize_v1`
- `V2R`: pageable raw staging plus the fixed OpenCV C++ 4.5.4-aligned CUDA
  resize semantic.
- `V3R`: pinned raw staging plus the identical resize semantic.
- Parent identities: `V2` and `V3`; historical configurations and evidence
  remain unchanged.
- Applicability is limited to the current Jetson/OpenCV 4.5.4 environment,
  `CV_8UC3` BGR, the existing 640x640 letterbox geometry, uint8 resize-result
  semantics, and RGB NCHW FP32 `/255` output.

## 3. Authorized Scope Compliance

Only the bounded CUDA resize semantic, explicit V2R/V3R runtime identity and
dispatch, focused validators/tests, independent configs, and compact evidence
were changed. TensorRT Engine code/binary, CPU letterbox authority,
postprocess, NMS, model, calibration, Pipeline/V4, ROS2, UI, and formal
benchmark protocol were not changed.

The implementation follows the narrow OpenCV 4.5.4 `CV_8U INTER_LINEAR`
fixed-point coefficient and aarch64 vector accumulation order. No OpenCV
source was copied into the repository and no runtime coefficient or rounding
search was added.

## 4. Source Changes

The implementation files are `backend_tensorrt/cuda_preprocessor.{hpp,cu}`;
runtime parser/dispatch changes are in `include/edge_ai_defect/runtime/runtime_config.hpp`,
`src/runtime_config.cpp`, `src/application_runner.cpp`,
`stage_r/{pageable_runner,pinned_runner}.{hpp,cpp}`, and the necessary CMake
registration. Focused tests and validation tools are recorded in the source
identity evidence.

## 5. Gate C0 Results

PASS. Independent CUDA-enabled TensorRT build passed. Focused CTest passed
4/4: pageable staging, pinned staging, runtime parser, and CUDA preprocessing.
The CUDA test covered historical V2 behavior, V2R fixed semantic, V2R/V3R
same-semantic identity, non-square geometry, padded output, row-stride input,
BGR-to-RGB/NCHW/normalization, finite values, and CUDA launch/copy status.

## 6. Gate C1 Results

PASS on the frozen 16-case preprocessing corpus.

| Variant | MAE | P99 absolute error | Max absolute error | Non-finite |
|---|---:|---:|---:|---:|
| Historical V2 | 0.00041558645672675235 | 0.003921627998352051 | 0.003921627998352051 | 0 |
| V2R | 0.000000013098467330034206 | 0.00000005960464477539063 | 0.00000005960464477539063 | 0 |
| V3R | same semantic as V2R | same | same | 0 |

Relative V2R minus historical V2 deltas are MAE `-0.0004155733582594223`,
P99 `-0.003921568393707275`, and max `-0.003921568393707275`.
Geometry and padding-region checks passed; V2R/V3R tensor digest is
`8b7a07b28c10e360cb75ab55a377c3e254937d88e49181503cfa3c275eaa8f75`.

## 7. Gate C2 Results

PASS. Using the unchanged frozen INT8 Engine, focused 16-case integration
processed 16/16 frames for each variant. TensorRT output was finite, output
shape was `[1,10,8400]`, geometry and CUDA status passed, and both variants
produced 44 detections. Tensor digest and detection SHA were identical:

`1a65a16a25335dde4524dccae2579035f54ac7425e12086cced81e2af01c6dcb`

## 8. Historical V2 Preservation

Historical V2/V3 configs were not modified. The default preprocessor semantic
remains historical, and the historical CUDA path remains selectable by V2/V3.
No historical result directory was overwritten.

## 9. V2R/V3R Identity

V2R and V3R use the same resize semantic and differ only in raw staging memory
type. They have matching tensor and detection digests in C1/C2.

## 10. Test-Set Separation Confirmation

Formal Gate D: `NOT RUN`.

Task P/R/mAP metrics: `NOT GENERATED`.

The 180-image accuracy harness and Phase 0.5D benchmark were not run or
inspected.

## 11. Remaining Risks

The frozen semantic is version- and platform-bounded, not a universal OpenCV
bit-exact or generic CUDA resize claim. Formal task-level acceptance remains a
later one-time Gate D responsibility under the frozen implementation commit.

## 12. Gate D Authorization State

I1 has completed its implementation and pre-test gates. Gate D is eligible
only after Paper Project Manager review and is not authorized by this file to
run automatically.

## 13. Recommended Next Actor

`Paper Project Manager`

Phase 0.5C-I2: `NOT AUTHORIZED BY THIS FILE`
