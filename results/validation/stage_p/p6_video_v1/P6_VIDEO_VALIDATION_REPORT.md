# P6 Video Validation Report

## 1 Verdict

`P6_VIDEO_SOURCE_PASS`

The frozen MJPG video passed codec preflight, production CLI Serial/Pipeline
smoke, and StagePExperimentRunner Serial ×1 / Pipeline ×1 validation.

## 2 Environment

- Platform: Jetson aarch64; Linux 5.15.185-tegra.
- JetPack/L4T runtime: R36.5.0, as reported by `/etc/nv_tegra_release`.
- CUDA runtime: 12.6.68.
- TensorRT runtime library: 10.3.0.
- OpenCV: 4.5.4.
- CMake: 3.22.1.
- TensorRT-OFF and TensorRT-ON builds both completed successfully.
- P5 frozen pipeline configuration: `queue_capacity=1`, `drop_policy=block`.

Detailed environment output is retained in `attempt_002/environment.txt`.

## 3 Video Asset

- Local asset: `attempt_001/assets/frozen_test_video.avi`.
- SHA-256: `8c1967dc0de607a72ef40525d91dbcddec05ebd7ada094188204fd2942c7cf69`.
- Requested codec: `MJPG`.
- Observed FourCC: `MJPG`.
- Resolution: `32×24`.
- Nominal FPS: `15`.
- Generated frames: `16`.
- Decoded frames: `16`.
- `CAP_PROP_FRAME_COUNT`: `16`.
- Identity: `frozen_test_video.avi/frame_000000` through
  `frozen_test_video.avi/frame_000015`.

The AVI is local evidence only and is not committed to the repository.

## 4 Codec Preflight

`VideoWriter` opened the requested MJPG codec, wrote and closed the fixed
asset, then `VideoCapture` reopened it and decoded the complete file. The
preflight passed with exact generated/decoded counts. Evidence:
`attempt_001/preflight/codec_preflight.json`.

## 5 Serial Validation

- Production CLI smoke: exit code `0`; Result JSON schema v3; `video_file` input;
  16 source/processed frames; zero drops; continuous identity; finite timing.
- StagePExperimentRunner formal run: exit code `0`; 16 processed frames;
  zero detections were observed for this synthetic asset, with no fabricated
  accuracy claim.
- Normal EOS completed; the extra source-only EOS probe is not counted as a
  frame.

## 6 Pipeline Validation

- Production CLI smoke: exit code `0`; Result JSON schema v3; `video_file` input;
  `queue_capacity=1`; `drop_policy=block`; 16 source/processed frames; zero
  drops; finite timing.
- StagePExperimentRunner formal run: exit code `0`; 16 processed frames;
  queue high-water marks were `1,1,1`, all within the selected capacity.
- Normal EOS completed, queues drained/closed, and workers joined before the
  runner returned successfully.

## 7 Hash Verification

- Serial RUN SHA-256:
  `932853ac5a5c8a8e210a689b6b83d3751b8b0b6f261849b18dfbbd781a04207b`
- Pipeline RUN SHA-256:
  `932853ac5a5c8a8e210a689b6b83d3751b8b0b6f261849b18dfbbd781a04207b`
- Result: identical.
- Both runs used the same frozen video SHA, TensorRT engine SHA, model
  contract SHA, and executable SHA.

The full machine-readable gate is retained in
`attempt_002/validation/gate_checks.json`.

## 8 Known Limitations

- This validation uses a short deterministic synthetic MJPG AVI. It does not
  compare directory pixels or detections with video pixels or detections.
- Nominal FPS is descriptive metadata only; it is not a pacing or timing
  authority and is not added to Result JSON v3.
- No camera, RTSP, GStreamer, ROS2, queue-policy, preprocessing,
  postprocessing, model, ONNX export, or TensorRT engine change was made.
- No P5 benchmark was rerun.
- The formal run records normal lifecycle completion and queue high-water marks;
  it is not a long-duration stability or performance benchmark.

## 9 Next Authorization

P6 is complete. P7 may be considered after project-owner review; no P7 work was
executed by this task.
