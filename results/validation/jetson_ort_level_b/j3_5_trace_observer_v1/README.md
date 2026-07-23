# J3.5 Trace observer and recorder

Result: PASS.

The optional `IFrameTraceObserver` covers source, preprocess, inference,
postprocess and sink stage boundaries. `TraceRecorder` emits deterministic
JSON Lines records with cycle id, stage, monotonic start/end timestamps and
duration. It retains only one active stage and flushes each completed record
by default; an explicit `flush()` is also available.

No ROS2, camera, TensorRT, CUDA, inference or benchmark operation was performed.
