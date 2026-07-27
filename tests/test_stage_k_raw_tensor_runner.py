#!/usr/bin/env python3
"""Focused subprocess tests for the Stage K raw tensor runner."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config_text(mode: str, repo: Path) -> str:
    if mode == "ort":
        return f'''schema_version: 2
backend:
  type: onnxruntime_cpu
onnxruntime:
  execution_mode: sequential
  graph_optimization_level: all
  intra_op_threads: 1
  inter_op_threads: 1
  intra_op_allow_spinning: true
  inter_op_allow_spinning: true
  cpu_arena_enabled: true
  memory_pattern_enabled: true
runtime:
  opencv_num_threads: 1
model:
  path: {repo / "models/onnx/yolov8n_neudet_frozen.onnx"}
  contract_path: {repo / "configs/model_contracts/yolov8n_neudet_frozen.yaml"}
input:
  type: directory
  directory: /tmp
output:
  json_path: /tmp/stage-k-unused.json
  console: false
  overwrite: false
postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680
  agnostic: false
'''
    return f'''schema_version: 3
backend:
  type: tensorrt_fp16
tensorrt:
  engine_path: /home/orin/edge-ai-local-models/stage_k/yolov8n_neudet_trt10.3_fp16_b1_640.engine
  engine_manifest_path: {repo / "models/tensorrt/yolov8n_neudet_trt10.3_fp16_b1_640.manifest.json"}
  device_id: 0
runtime:
  opencv_num_threads: 1
model:
  contract_path: {repo / "configs/model_contracts/yolov8n_neudet_frozen.yaml"}
input:
  type: directory
  directory: /tmp
output:
  json_path: /tmp/stage-k-unused.json
  console: false
  overwrite: false
postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680
  agnostic: false
'''


def manifest(path: Path, *, image_id: str = "image", tensor_path: Path | None = None,
             sha: str | None = None, byte_size: int = 4915200,
             shape: list[int] | None = None) -> dict:
    tensor_path = tensor_path or path
    return {
        "schema_version": 1,
        "artifact_kind": "stage_k_raw_tensor_input_manifest",
        "dtype": "float32",
        "byte_order": "little_endian",
        "layout": "NCHW",
        "shape": shape or [1, 3, 640, 640],
        "element_count": 1228800,
        "byte_size": 4915200,
        "entries": [{
            "image_id": image_id,
            "input_tensor_path": str(tensor_path),
            "input_sha256": sha or sha256(tensor_path),
            "dtype": "float32",
            "byte_order": "little_endian",
            "layout": "NCHW",
            "shape": shape or [1, 3, 640, 640],
            "element_count": 1228800,
            "byte_size": byte_size,
        }],
    }


def run(runner: Path, config: Path, input_manifest: Path, output: Path,
        run_id: str, expect_success: bool) -> subprocess.CompletedProcess[str]:
    manifest_path = output / "output_manifest.json"
    original_manifest = manifest_path.read_bytes() if manifest_path.is_file() else None
    result = subprocess.run([
        str(runner), "--config", str(config), "--input-manifest", str(input_manifest),
        "--output-dir", str(output), "--run-id", run_id,
    ], capture_output=True, text=True)
    if (result.returncode == 0) != expect_success:
        raise AssertionError(f"unexpected runner result: {result.returncode}\n{result.stdout}\n{result.stderr}")
    if expect_success and not manifest_path.is_file():
        raise AssertionError("successful run did not publish output manifest")
    if not expect_success and original_manifest is None and manifest_path.exists():
        raise AssertionError("failed run published a success manifest")
    if not expect_success and original_manifest is not None and manifest_path.read_bytes() != original_manifest:
        raise AssertionError("overwrite rejection changed the existing manifest")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runner", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--mode", choices=["ort", "trt"], required=True)
    parser.add_argument("--temp-dir", required=True, type=Path)
    args = parser.parse_args()
    args.temp_dir.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix=f"raw_runner_{args.mode}_", dir=args.temp_dir))
    source = args.repo_root / "tests/data/preprocess_level_a/golden/frozen_640_checkerboard.f32le"
    config = root / "runtime.yaml"
    config.write_text(config_text(args.mode, args.repo_root), encoding="utf-8")

    malformed = root / "malformed.json"
    malformed.write_text('{"entries":\n', encoding="utf-8")
    run(args.runner, config, malformed, root / "malformed-output", "malformed", False)

    invalid_config = root / "invalid-runtime.yaml"
    invalid_config.write_text(config.read_text(encoding="utf-8").replace(
        "type: onnxruntime_cpu", "type: invalid_backend").replace(
        "type: tensorrt_fp16", "type: invalid_backend"), encoding="utf-8")
    valid_manifest = root / "valid.json"
    valid_manifest.write_text(json.dumps(manifest(source), indent=2) + "\n", encoding="utf-8")
    run(args.runner, invalid_config, valid_manifest, root / "invalid-config-output", "invalid-config", False)

    wrong_sha = manifest(source, sha="0" * 64)
    wrong_sha_path = root / "wrong-sha.json"
    wrong_sha_path.write_text(json.dumps(wrong_sha) + "\n", encoding="utf-8")
    run(args.runner, config, wrong_sha_path, root / "wrong-sha-output", "wrong-sha", False)

    wrong_size = manifest(source, byte_size=4915196)
    wrong_size_path = root / "wrong-size.json"
    wrong_size_path.write_text(json.dumps(wrong_size) + "\n", encoding="utf-8")
    run(args.runner, config, wrong_size_path, root / "wrong-size-output", "wrong-size", False)

    wrong_shape = manifest(source, shape=[1, 3, 320, 320])
    wrong_shape_path = root / "wrong-shape.json"
    wrong_shape_path.write_text(json.dumps(wrong_shape) + "\n", encoding="utf-8")
    run(args.runner, config, wrong_shape_path, root / "wrong-shape-output", "wrong-shape", False)

    nonfinite = root / "nonfinite.f32le"
    data = bytearray(source.read_bytes())
    data[:4] = struct.pack("<I", 0x7FC00000)
    nonfinite.write_bytes(data)
    nonfinite_manifest = root / "nonfinite.json"
    nonfinite_manifest.write_text(json.dumps(manifest(nonfinite)) + "\n", encoding="utf-8")
    run(args.runner, config, nonfinite_manifest, root / "nonfinite-output", "nonfinite", False)

    ordered = root / "ordered.json"
    ordered_value = manifest(source, image_id="z-image")
    ordered_value["entries"].append({**ordered_value["entries"][0], "image_id": "a-image"})
    ordered.write_text(json.dumps(ordered_value, indent=2) + "\n", encoding="utf-8")
    valid_output = root / "valid-output"
    run(args.runner, config, ordered, valid_output, "valid", True)
    output_manifest = json.loads((valid_output / "output_manifest.json").read_text(encoding="utf-8"))
    entries = output_manifest["entries"]
    if [entry["image_id"] for entry in entries] != ["a-image", "z-image"]:
        raise AssertionError("output manifest ordering is not deterministic")
    for entry in entries:
        raw = valid_output / entry["output_filename"]
        if raw.stat().st_size != 336000 or entry["finite_count"] != 84000:
            raise AssertionError("output raw tensor contract is invalid")
        values = struct.unpack("<84000f", raw.read_bytes())
        if not all(math.isfinite(value) for value in values):
            raise AssertionError("output raw tensor contains a non-finite value")
    run(args.runner, config, valid_manifest, valid_output, "overwrite", False)
    if not (valid_output / "output_manifest.json").is_file():
        raise AssertionError("overwrite rejection removed the existing manifest")
    shutil.rmtree(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
