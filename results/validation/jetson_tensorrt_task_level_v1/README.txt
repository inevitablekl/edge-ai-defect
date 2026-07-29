Stage K5.4 Task-Level Validation
TensorRT FP32 noTF32 Reference vs TensorRT FP16 Deployment

Verdict
-------

TASK_LEVEL_VALIDATION_INCOMPLETE_REAL_ANNOTATIONS_REQUIRED

The frozen 16-image corpus contains no validation bounding-box annotations.
Therefore Precision, Recall, mAP50, and mAP50-95 are reported as TBD and no
Case A/B/C classification is claimed. This is an evidence limitation, not a
fabricated accuracy result. The final Stage K decision must remain open until
the real NEU-DET validation annotations are supplied.

Detection-level comparison
--------------------------

The same 16 images, application preprocessing, inference contract, and
postprocessing configuration were run through both frozen engines.

  image count:                  16
  FP32 detections:              54
  FP16 detections:              54
  matched detections:           54
  class mismatch count:          0
  class-consistent images:      16/16
  mean IoU:                     0.994954508
  minimum IoU:                  0.879173286
  IoU < 0.5:                    0
  confidence-difference MAE:    0.002402265

The comparison is final-detection comparison only. It does not claim raw
tensor equivalence. See results_fp32.json, results_fp16.json, and
detection_comparison.json in this directory.

Dataset-level evaluation
------------------------

  Backend             Precision       Recall          mAP50           mAP50-95
  TRT FP32 noTF32     TBD              TBD             TBD             TBD
  TRT FP16            TBD              TBD             TBD             TBD

Absolute mAP drop and recall drop: TBD. The independent evaluator supports
standard YOLO labels through --labels-dir, but no NEU-DET validation labels
were present in the frozen/local corpus. See dataset_metrics.json.

Performance evaluation
----------------------

Environment: NVIDIA Jetson Orin Nano Engineering Reference Developer Kit
Super, MAXN_SUPER, L4T R36.5.0, aarch64, TensorRT 10.3.0.30, CUDA 12.6.68,
OpenCV threads=1. jetson_clocks was not verified because it requires root.

The same ordered 550-frame hard-link corpus was used for both engines; the
first 50 frames were warmup and the next 500 were measured.

  Backend             TRT mean ms   TRT P95 ms   E2E mean ms   E2E P95 ms
  TRT FP32 noTF32     16.549833     18.185525     22.465320     24.471018
  TRT FP16            12.379175     12.556807     18.303997     19.127403

  mean TRT speedup FP32/FP16: 1.336909x
  mean E2E speedup FP32/FP16: 1.227345x

Performance improvement is measured, but it cannot by itself satisfy the
task-level accuracy decision rule without dataset metrics.

Engines and reproducibility
---------------------------

  Git commit: b819993185e4a48c7af87b53787c08bb39194627
  FP32 engine SHA256: aaa37030ca1d24838e75ad6fd1a16bdeb74072d87302c1b2cef62faa3856d74f
  FP16 engine SHA256: 6c3d12dcbd8a568d28e038f192eecfd6a3f917d06a52876de49d4e7d7750d9bc
  Level B input manifest SHA256: d81d6bb57346231f3ea4cd2dcf0f5285b5993b4b16953641c45f85359b9d0fbf
  Source corpus manifest SHA256: 687682f37d1affbe8813a9e7287b42dc28a9a8b9ea8d67f8b85175960f3e2dcd

Build commands are retained in the two engine manifests. No engine was
modified or rebuilt for this task. The FP32 engine is strict FP32/noTF32;
the FP16 engine is the original Stage K FP16 engine, whose original build
command did not record a --noTF32 flag.

Preprocessing: BGR input, aspect-preserving LetterBox to 640x640,
INTER_LINEAR, padding value 114, RGB NCHW FP32 tensor, uint8/255.0.
Postprocessing: confidence 0.25, IoU 0.45, max_nms 30000, max_det 300,
max_wh 7680.0, agnostic=false, multi_label=false.

Artifacts
---------

  evaluation_manifest.json
  results_fp32.json
  results_fp16.json
  detection_comparison.json
  dataset_metrics.json
  performance_results.json
  tools/validation/task_level_detection_compare.py
  tools/validation/task_level_dataset_metrics.py
  tools/validation/task_level_performance_analyze.py
  tools/validation/task_level_profile_runner.cpp

The raw application result and profile JSON files remain in
/home/orin/edge-ai-local-evidence/stage_k/task_level_v1/ and are referenced
with SHA256 values in evaluation_manifest.json. The repository report does
not include generated engine binaries.

No K5 official gate, production runtime, ModelContract, ONNX, engine, NMS
parameters, or comparator tolerance was changed. No Level C, benchmark,
K6, stability, push, merge, or tag operation was performed.
