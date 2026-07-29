#!/usr/bin/env bash
set -o pipefail
TRTEXEC=/usr/src/tensorrt/bin/trtexec
ONNX=models/onnx/yolov8n_neudet_frozen.onnx
ENGINE=/home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine
"$TRTEXEC" \
  --onnx="$ONNX" \
  --fp16 \
  --memPoolSize=workspace:4096M \
  --inputIOFormats=fp32:chw \
  --outputIOFormats=fp32:chw \
  --saveEngine="$ENGINE" \
  --skipInference \
  > results/build/tensorrt/k2_fp16_engine_v1/build_stdout.log \
  2> results/build/tensorrt/k2_fp16_engine_v1/build_stderr.log
RC=$?
cat results/build/tensorrt/k2_fp16_engine_v1/build_stdout.log \
    results/build/tensorrt/k2_fp16_engine_v1/build_stderr.log \
  > results/build/tensorrt/k2_fp16_engine_v1/build_complete.log
printf '%s\n' "$RC" > results/build/tensorrt/k2_fp16_engine_v1/build_exit_code.txt
exit "$RC"
