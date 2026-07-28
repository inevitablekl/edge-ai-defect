Stage K Selective Precision Investigation M3
============================================

Candidate: M3_Backbone_Neck_Detect_FP32

Conclusion: M3_FAIL_SELECTIVE_FP16_NOT_RECOVERED
Inspection classification: M3_DEGENERATED_TO_FP32

M3 constrained the frozen graph's Backbone (/model.0-/model.9), Neck
(/model.10-/model.21), and Detect Head (/model.22). The existing M2 Detect
mapping was reused exactly. The generated mapping contains 235 requested
FP32 nodes: Backbone 97, Neck 68, Detect 70. Twenty-two Constant nodes were
excluded because they have no execution precision. Four Neck Split nodes are
recorded with the same fused/elided parser-identity rule used by M2.

M2 versus M3
------------

M2: global --fp16 --noTF32 --precisionConstraints=obey; complete Detect Head
FP32 island; actual FP16 tactics existed outside Detect Head; Level B 0/16
PASS; bbox max_abs 27.280731201171875.

M3: same global builder policy; Backbone, Neck, and Detect Head requested
FP32; actual FP16 tactics 0; Level B 16/16 PASS; bbox maximum across the
16 samples max_abs 0.025054931640625, MAE 0.0003009629959151858, P99
0.002594146728515656; score max_abs 1.8984079360961914e-05.

The M3 Level B result is numerically within the frozen gate, but inspection
found no actual FP16 execution. Therefore this experiment does not isolate
Backbone/Neck drift from a full FP32 execution path and is not evidence for
an effective selective-FP16 recovery.

Build command
-------------

Tool: /usr/src/tensorrt/bin/trtexec
Help verification: /home/orin/edge-ai-local-evidence/stage_k/selective_fp16_notf32_m3/m3/trtexec_help.txt

The build used the frozen ONNX and the generated exact layer policies:

  --fp16 --noTF32 --precisionConstraints=obey
  --layerPrecisions=<m3 layer spec>:fp32
  --layerOutputTypes=<m3 layer spec>:fp32
  --memPoolSize=workspace:4096M
  --inputIOFormats=fp32:chw --outputIOFormats=fp32:chw
  --profilingVerbosity=detailed --skipInference

The fully expanded command is recorded at:
/home/orin/edge-ai-local-evidence/stage_k/selective_fp16_notf32_m3/m3/build_command.sh

Engine:
/home/orin/edge-ai-local-models/stage_k/selective_fp16_notf32_m3/yolov8n_neudet_trt10.3_fp16_notf32_backbone_neck_detect_fp32.engine
SHA256: 83e7100b01b9bb0c04dd4c41e52d6d5f61ee61d07cef82dffee173a1c692266b

Layer mapping
-------------

Mapping JSON:
results/build/tensorrt/selective_fp16_notf32_m3/m3_precision_mapping.json

Every mapping entry records ONNX node, TensorRT layer identity, semantic role,
requested FP32 precision, requested FP32 output type, and mapping evidence.
The M2 mapping and TensorRT 10.3 M2 detailed layer dump are the source facts;
layer names were not re-guessed.

Inspection
----------

Inspection summary:
results/build/tensorrt/selective_fp16_notf32_m3/engine_inspection.json

Load smoke and detailed inspection both exited 0. Build logs accepted 235
precision requests and 235 output-type requests. Input/output are FP32 with
shapes [1,3,640,640] and [1,10,8400]. The engine is static, noTF32, no INT8,
no DLA, and has no custom plugin dependency. Detailed inspection reported 64
tactic execution layers, all non-FP16, with observed output datatypes FP32.

Level B
-------

Reference: frozen Python ORT Reference Bundle
Report: results/validation/jetson_tensorrt_selective_fp16_notf32_m3/level_b_report.json
Gate: unchanged BBox MAE <=0.5, P99 <=1.5, max_abs <=4.0; Score MAE <=2e-3,
P99 <=5e-3, max_abs <=2e-2.

Result: 16/16 PASS. No Level C, benchmark, K6, or stability work was run.

Repeatability
-------------

Because Level B passed, two independent raw inference runs were executed.
The frozen comparator reports 16/16 byte-identical output SHA pairs.
Raw evidence remains local-only under:
/home/orin/edge-ai-local-evidence/stage_k/selective_fp16_notf32_m3/m3/

Final disposition
-----------------

M3_DEGENERATED_TO_FP32
M3_FAIL_SELECTIVE_FP16_NOT_RECOVERED

No production runtime, K5 gate, official Engine manifest, or RuntimeConfig was
modified. No push, merge, or tag was performed.
