# J3.4 OpenCV thread policy

Result: PASS.

RuntimeConfig v2 `runtime.opencv_num_threads` is applied explicitly through
`cv::setNumThreads(N)` immediately after configuration load and before model,
source or runtime initialization. The policy reads back the applied value and
creates a stable record containing requested/applied threads, OpenCV version
and activation status.

No inference, benchmark, camera, TensorRT, CUDA or ROS2 operation was performed.
