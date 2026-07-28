#!/usr/bin/env python3
"""Run the frozen Stage K test split through two TensorRT engines.

This is an orchestration/evidence script.  It reuses the existing independent
task_level_profile_runner and never copies or edits the source dataset.  The
runner accepts a directory, while the frozen split is a manifest, so temporary
hard links are used to present exactly the manifest image set to the runner.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPLIT_MANIFEST = (
    REPO_ROOT / "results/validation/stage_k_task_eval_v2/split/test_manifest.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "results/validation/stage_k_task_eval_v2/inference"
DEFAULT_RUNNER = Path(
    "/home/orin/edge-ai-local-build/k5_correctness_v1/c54020c_release/"
    "task_level_profile_runner"
)
MODEL_CONTRACT = REPO_ROOT / "configs/model_contracts/yolov8n_neudet_frozen.yaml"

EXPECTED_SPLIT_SHA256 = (
    "fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8"
)
CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]
POSTPROCESS = {
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45,
    "max_nms": 30000,
    "max_det": 300,
    "max_wh": 7680.0,
    "agnostic": False,
    "multi_label": False,
}

BACKENDS = {
    "fp32_notf32": {
        "label": "TRT FP32 noTF32",
        "engine_path": Path(
            "/home/orin/edge-ai-local-models/stage_k/strict_fp32_notf32_v1/"
            "yolov8n_neudet_trt10.3_strict_fp32_notf32_b1_640.engine"
        ),
        "manifest_path": Path(
            "/home/orin/edge-ai-local-evidence/stage_k/strict_fp32_notf32_v1/"
            "strict_fp32_notf32_runtime_descriptor.json"
        ),
        "precision": "strict FP32, TF32 disabled",
    },
    "fp16_selective": {
        "label": "TRT FP16 selective M3",
        "engine_path": Path(
            "/home/orin/edge-ai-local-models/stage_k/selective_fp16_notf32_m3/"
            "yolov8n_neudet_trt10.3_fp16_notf32_backbone_neck_detect_fp32.engine"
        ),
        "manifest_path": Path(
            "/home/orin/edge-ai-local-evidence/stage_k/selective_fp16_notf32_m3/"
            "m3/engine.manifest.json"
        ),
        "precision": (
            "FP16 builder enabled, TF32 disabled; M3 Backbone/Neck/Detect "
            "requested FP32"
        ),
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def json_dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n")


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def yaml_config(
    engine: dict[str, Any], input_dir: Path, output_json: Path
) -> str:
    # Values are fixed by the Stage K task protocol.  Paths are absolute so
    # this temporary config cannot change meaning with the subprocess cwd.
    return f"""schema_version: 3
backend:
  type: tensorrt_fp16
tensorrt:
  engine_path: {engine['engine_path']}
  engine_manifest_path: {engine['manifest_path']}
  device_id: 0
runtime:
  opencv_num_threads: 1
model:
  contract_path: {MODEL_CONTRACT}
input:
  type: directory
  directory: {input_dir}
output:
  json_path: {output_json}
  console: false
  overwrite: true
postprocess:
  conf_threshold: 0.25
  iou_threshold: 0.45
  max_nms: 30000
  max_det: 300
  max_wh: 7680.0
  agnostic: false
"""


def load_split(path: Path) -> tuple[dict[str, Any], str]:
    actual_sha = sha256_file(path)
    if actual_sha != EXPECTED_SPLIT_SHA256:
        raise RuntimeError(
            f"frozen test manifest SHA mismatch: expected {EXPECTED_SPLIT_SHA256}, "
            f"got {actual_sha}"
        )
    manifest = json.loads(path.read_text())
    entries = manifest.get("entries")
    if manifest.get("split") != "test" or not isinstance(entries, list):
        raise RuntimeError("test manifest has invalid split or entries")
    if len(entries) != 180:
        raise RuntimeError(f"expected 180 test entries, got {len(entries)}")
    paths = [entry.get("image_path") for entry in entries]
    if any(not isinstance(value, str) or not value for value in paths):
        raise RuntimeError("test manifest contains an invalid image_path")
    if len(set(paths)) != len(paths):
        raise RuntimeError("test manifest contains duplicate image paths")
    return manifest, actual_sha


def validate_engines() -> dict[str, dict[str, Any]]:
    identities: dict[str, dict[str, Any]] = {}
    for key, definition in BACKENDS.items():
        engine_path = definition["engine_path"]
        manifest_path = definition["manifest_path"]
        if not engine_path.is_file():
            raise RuntimeError(f"engine is unavailable: {engine_path}")
        if not manifest_path.is_file():
            raise RuntimeError(f"engine manifest is unavailable: {manifest_path}")
        engine_manifest = json.loads(manifest_path.read_text())
        engine_sha = sha256_file(engine_path)
        declared_sha = engine_manifest.get("engine_sha256")
        if declared_sha != engine_sha:
            raise RuntimeError(f"engine SHA mismatch for {key}")
        identities[key] = {
            **definition,
            "engine_sha256": engine_sha,
            "manifest_sha256": sha256_file(manifest_path),
            "tensorrt_version": engine_manifest.get("tensorrt_version"),
            "manifest_engine_id": engine_manifest.get("engine_id"),
            "source_onnx_sha256": engine_manifest.get("source_onnx_sha256"),
            "model_contract_sha256": engine_manifest.get("model_contract_sha256"),
        }
        if identities[key]["tensorrt_version"] != "10.3.0.30":
            raise RuntimeError(f"unexpected TensorRT version for {key}")
    return identities


def prepare_input_dir(root: Path, dataset_root: Path, entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    root.mkdir(parents=True, exist_ok=True)
    by_filename: dict[str, dict[str, Any]] = {}
    for entry in entries:
        relative = Path(entry["image_path"])
        source = dataset_root / relative
        if not source.is_file():
            raise RuntimeError(f"split image is unavailable: {source}")
        actual_sha = sha256_file(source)
        if actual_sha != entry["image_sha256"]:
            raise RuntimeError(f"image SHA mismatch: {relative}")
        destination = root / relative.name
        if destination.name in by_filename:
            raise RuntimeError(f"duplicate input basename: {destination.name}")
        os.link(source, destination)
        by_filename[destination.name] = entry
    if len(by_filename) != 180:
        raise RuntimeError(f"prepared input count is {len(by_filename)}, not 180")
    return by_filename


def run_backend(
    key: str,
    identity: dict[str, Any],
    input_dir: Path,
    output_dir: Path,
    entries_by_filename: dict[str, dict[str, Any]],
    split_sha256: str,
    runner: Path,
) -> dict[str, Any]:
    backend_dir = output_dir / key
    backend_dir.mkdir(parents=True, exist_ok=True)
    raw_result = backend_dir / "_application_result.json"
    config_path = backend_dir / "_runtime.yaml"
    config_path.write_text(yaml_config(identity, input_dir, raw_result))
    command = [str(runner), "--config", str(config_path)]
    started_at = utc_now()
    wall_start = time.monotonic()
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    wall_elapsed_ms = (time.monotonic() - wall_start) * 1000.0
    completed_at = utc_now()
    (backend_dir / "runner.stdout.txt").write_text(completed.stdout)
    (backend_dir / "runner.stderr.txt").write_text(completed.stderr)
    if completed.returncode != 0:
        raise RuntimeError(
            f"{key} runner failed with exit {completed.returncode}; see "
            f"{backend_dir / 'runner.stderr.txt'}"
        )
    if not raw_result.is_file():
        raise RuntimeError(f"{key} did not produce application output")

    raw = json.loads(raw_result.read_text())
    images = raw.get("images")
    if not isinstance(images, list) or len(images) != 180:
        raise RuntimeError(f"{key} output does not contain 180 images")
    raw_by_name = {Path(item["relative_path"]).name: item for item in images}
    if set(raw_by_name) != set(entries_by_filename):
        raise RuntimeError(f"{key} output image set does not match test manifest")

    detections_images = []
    latency_images = []
    detection_schema: tuple[str, ...] | None = None
    for filename in sorted(entries_by_filename):
        entry = entries_by_filename[filename]
        item = raw_by_name[filename]
        if item.get("relative_path") != filename:
            raise RuntimeError(f"unexpected runner relative path for {filename}")
        detections = []
        for detection in item.get("detections", []):
            values = [
                detection.get("x1"), detection.get("y1"),
                detection.get("x2"), detection.get("y2"),
                detection.get("confidence"), detection.get("class_id"),
            ]
            if not all(finite(value) for value in values[:5]):
                raise RuntimeError(f"NaN/Inf in {key} detection for {filename}")
            if not isinstance(values[5], int) or values[5] < 0:
                raise RuntimeError(f"invalid class_id in {key} output for {filename}")
            normalized = {
                "class_id": values[5],
                "confidence": float(values[4]),
                "bbox_xyxy": [float(value) for value in values[:4]],
            }
            detections.append(normalized)
            schema = tuple(normalized.keys())
            if detection_schema is None:
                detection_schema = schema
            elif schema != detection_schema:
                raise RuntimeError(f"inconsistent detection schema in {key}")
        timing = item.get("timing_ms")
        required_timing = {
            "source", "preprocess", "inference", "postprocess", "pre_sink_total"
        }
        if not isinstance(timing, dict) or not required_timing.issubset(timing):
            raise RuntimeError(f"missing timing fields in {key} output for {filename}")
        if not all(finite(timing[name]) for name in required_timing):
            raise RuntimeError(f"NaN/Inf in {key} timing for {filename}")
        image_sha = entry["image_sha256"]
        detections_images.append({
            "image_id": Path(filename).stem,
            "image_path": entry["image_path"],
            "image_sha256": image_sha,
            "backend": identity["label"],
            # The existing independent runner exposes monotonic stage timing,
            # not wall-clock timestamps.  This is the real batch start marker;
            # exact stage durations are retained in latency.json.
            "inference_timestamp_utc": started_at,
            "detections": detections,
        })
        latency_images.append({
            "image_id": Path(filename).stem,
            "image_path": entry["image_path"],
            "image_sha256": image_sha,
            "backend": identity["label"],
            "inference_timestamp_utc": started_at,
            "preprocessing_latency_ms": float(timing["preprocess"]),
            "tensorrt_inference_latency_ms": float(timing["inference"]),
            "postprocess_latency_ms": float(timing["postprocess"]),
            "e2e_latency_ms": float(timing["pre_sink_total"]),
            "source_latency_ms": float(timing["source"]),
        })

    detections_artifact = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_level_inference_detections",
        "backend": identity["label"],
        "backend_key": key,
        "split": "test",
        "split_manifest_sha256": split_sha256,
        "class_names": CLASS_NAMES,
        "postprocess": POSTPROCESS,
        "image_count": len(detections_images),
        "images": detections_images,
    }
    latency_values = [item["tensorrt_inference_latency_ms"] for item in latency_images]
    e2e_values = [item["e2e_latency_ms"] for item in latency_images]
    latency_artifact = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_level_inference_latency",
        "backend": identity["label"],
        "backend_key": key,
        "split": "test",
        "split_manifest_sha256": split_sha256,
        "image_count": len(latency_images),
        "summary_ms": {
            "inference_mean": sum(latency_values) / len(latency_values),
            "inference_min": min(latency_values),
            "inference_max": max(latency_values),
            "e2e_mean": sum(e2e_values) / len(e2e_values),
            "e2e_min": min(e2e_values),
            "e2e_max": max(e2e_values),
        },
        "images": latency_images,
    }
    json_dump(backend_dir / "detections.json", detections_artifact)
    json_dump(backend_dir / "latency.json", latency_artifact)
    inference_manifest = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_level_inference_manifest",
        "backend": identity["label"],
        "backend_key": key,
        "precision_configuration": identity["precision"],
        "engine_path": str(identity["engine_path"]),
        "engine_sha256": identity["engine_sha256"],
        "engine_manifest_path": str(identity["manifest_path"]),
        "engine_manifest_sha256": identity["manifest_sha256"],
        "engine_id": identity["manifest_engine_id"],
        "tensorrt_version": identity["tensorrt_version"],
        "source_onnx_sha256": identity["source_onnx_sha256"],
        "model_contract_sha256": identity["model_contract_sha256"],
        "dataset_split": "test",
        "split_manifest_sha256": split_sha256,
        "image_count": len(images),
        "success_count": len(images),
        "failure_count": 0,
        "runner": str(runner),
        "runner_sha256": sha256_file(runner),
        "command": command,
        "started_at_utc": started_at,
        "completed_at_utc": completed_at,
        "subprocess_wall_elapsed_ms": wall_elapsed_ms,
        "preprocessing": {
            "implementation": "existing application Preprocessor/LetterBox",
            "source_color": "BGR",
            "resize": "aspect-preserving LetterBox to 640x640",
            "interpolation": "INTER_LINEAR",
            "padding_value": 114,
            "tensor_color_order": "RGB",
            "tensor_layout": "NCHW",
            "normalization": "uint8 / 255.0",
        },
        "postprocess": POSTPROCESS,
        "artifacts": {
            "detections": "detections.json",
            "latency": "latency.json",
            "runner_stdout": "runner.stdout.txt",
            "runner_stderr": "runner.stderr.txt",
        },
        "limitations": [
            "The existing independent runner exposes per-image monotonic stage durations but not per-image wall-clock timestamps; inference_timestamp_utc is the backend batch start marker.",
            "No ground-truth metrics are computed in this phase.",
        ],
    }
    json_dump(backend_dir / "inference_manifest.json", inference_manifest)
    raw_result.unlink()
    config_path.unlink()
    return {
        "backend": identity["label"],
        "backend_key": key,
        "image_count": len(images),
        "success_count": len(images),
        "failure_count": 0,
        "inference_mean_ms": latency_artifact["summary_ms"]["inference_mean"],
        "e2e_mean_ms": latency_artifact["summary_ms"]["e2e_mean"],
        "engine_sha256": identity["engine_sha256"],
        "engine_manifest_sha256": identity["manifest_sha256"],
        "tensorrt_version": identity["tensorrt_version"],
    }


def validate_pair(output_dir: Path) -> dict[str, Any]:
    artifacts = {}
    image_sets = {}
    for key in BACKENDS:
        detections = json.loads((output_dir / key / "detections.json").read_text())
        latency = json.loads((output_dir / key / "latency.json").read_text())
        manifest = json.loads((output_dir / key / "inference_manifest.json").read_text())
        if detections["image_count"] != 180 or latency["image_count"] != 180:
            raise RuntimeError(f"{key} artifact count validation failed")
        image_sets[key] = [item["image_id"] for item in detections["images"]]
        if image_sets[key] != [item["image_id"] for item in latency["images"]]:
            raise RuntimeError(f"{key} detection/latency identity mismatch")
        artifacts[key] = {
            "detections_sha256": sha256_file(output_dir / key / "detections.json"),
            "latency_sha256": sha256_file(output_dir / key / "latency.json"),
            "inference_manifest_sha256": sha256_file(
                output_dir / key / "inference_manifest.json"
            ),
            "success_count": manifest["success_count"],
            "failure_count": manifest["failure_count"],
            "inference_mean_ms": latency["summary_ms"]["inference_mean"],
            "e2e_mean_ms": latency["summary_ms"]["e2e_mean"],
        }
    if image_sets["fp32_notf32"] != image_sets["fp16_selective"]:
        raise RuntimeError("FP32 and FP16 output image schemas are not identical")
    return {
        "output_schema_identical": True,
        "nan_inf_validation": "PASS",
        "backend_artifacts": artifacts,
    }


def write_readme(
    output_dir: Path, split_sha256: str, summaries: dict[str, Any], pair: dict[str, Any]
) -> None:
    fp32 = summaries["fp32_notf32"]
    fp16 = summaries["fp16_selective"]
    readme = f"""Stage K Full Task-Level Evaluation v1 — inference phase
============================================================

Verdict
-------

READY_FOR_TASK_METRIC_EVALUATION

This phase generated final detections and per-image latency artifacts only.
No ground-truth metric was calculated.

Dataset split
-------------

  split: test
  image count: 180
  test manifest SHA256: {split_sha256}

Backend identity
----------------

  Backend                         Engine SHA256                                      TRT
  TRT FP32 noTF32                {fp32['engine_sha256']}  10.3.0.30
  TRT FP16 selective M3           {fp16['engine_sha256']}  10.3.0.30

  FP32 engine manifest SHA256: {fp32['engine_manifest_sha256']}
  FP16 engine manifest SHA256: {fp16['engine_manifest_sha256']}

Execution validation
--------------------

  FP32 success: {fp32['success_count']}/180 ({100.0 * fp32['success_count'] / 180:.2f}%)
  FP16 success: {fp16['success_count']}/180 ({100.0 * fp16['success_count'] / 180:.2f}%)
  output schema identical: {pair['output_schema_identical']}
  NaN/Inf validation: {pair['nan_inf_validation']}

Latency summary (application per-image timing)
-----------------------------------------------

  Backend                         mean TRT inference ms   mean E2E ms
  TRT FP32 noTF32                {fp32['inference_mean_ms']:.6f}              {fp32['e2e_mean_ms']:.6f}
  TRT FP16 selective M3           {fp16['inference_mean_ms']:.6f}              {fp16['e2e_mean_ms']:.6f}

Artifacts
---------

  fp32_notf32/detections.json
  fp32_notf32/latency.json
  fp32_notf32/inference_manifest.json
  fp16_selective/detections.json
  fp16_selective/latency.json
  fp16_selective/inference_manifest.json

The raw TensorRT Engine files, dataset images, and XML annotations were not
copied into the repository output.  The task runner used temporary hard links
to the frozen test images and removed them after completion.

The selective M3 identity is preserved exactly as built.  Its existing
inspection evidence classified actual execution as M3_DEGENERATED_TO_FP32;
this report does not reinterpret that engine identity.
"""
    (output_dir / "README.txt").write_text(readme)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-manifest", type=Path, default=DEFAULT_SPLIT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    split_manifest_path = args.test_manifest.resolve()
    output_dir = args.output_dir.resolve()
    runner = args.runner.resolve()
    if not runner.is_file() or not os.access(runner, os.X_OK):
        raise SystemExit(f"task-level runner is unavailable or not executable: {runner}")
    if not MODEL_CONTRACT.is_file():
        raise SystemExit(f"ModelContract is unavailable: {MODEL_CONTRACT}")
    if output_dir.exists() and any(output_dir.iterdir()) and not args.overwrite:
        raise SystemExit(
            f"output directory is non-empty: {output_dir}; use --overwrite only "
            "after resolving the exact existing target"
        )
    if args.overwrite and output_dir.exists():
        for child in output_dir.iterdir():
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest, split_sha256 = load_split(split_manifest_path)
    dataset_root = Path(manifest["dataset_root"])
    if not dataset_root.is_absolute():
        dataset_root = REPO_ROOT / dataset_root
    identities = validate_engines()
    entries = manifest["entries"]
    summaries: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="stage_k_task_eval_v2_") as temp_root_text:
        temp_root = Path(temp_root_text)
        input_dirs = {}
        entries_by_filename = None
        for key in BACKENDS:
            input_dirs[key] = temp_root / key / "inputs"
            current = prepare_input_dir(input_dirs[key], dataset_root, entries)
            if entries_by_filename is None:
                entries_by_filename = current
            elif set(current) != set(entries_by_filename):
                raise RuntimeError("backend temporary input sets differ")
        assert entries_by_filename is not None
        for key in BACKENDS:
            summaries[key] = run_backend(
                key,
                identities[key],
                input_dirs[key],
                output_dir,
                entries_by_filename,
                split_sha256,
                runner,
            )

    pair = validate_pair(output_dir)
    summary = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_level_inference_summary",
        "split_manifest": str(split_manifest_path),
        "split_manifest_sha256": split_sha256,
        "expected_image_count": 180,
        "backends": summaries,
        "validation": pair,
        "ready_for_task_metric_evaluation": all(
            item["success_count"] == 180 and item["failure_count"] == 0
            for item in summaries.values()
        ) and pair["output_schema_identical"] and pair["nan_inf_validation"] == "PASS",
    }
    json_dump(output_dir / "inference_summary.json", summary)
    write_readme(output_dir, split_sha256, summaries, pair)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"ERROR: {error}") from error
