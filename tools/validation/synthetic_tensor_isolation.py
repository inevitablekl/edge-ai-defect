#!/usr/bin/env python3
"""Stage K synthetic raw-tensor isolation diagnostic.

The tool generates continuous NCHW FP32 tensors without image processing,
runs the frozen ONNX model through Python ORT when available (otherwise the
existing C++ ORT CPU control is used and recorded explicitly), runs the
existing TensorRT raw runner, and reports numeric differences.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np


INPUT_SHAPE = (1, 3, 640, 640)
OUTPUT_SHAPE = (1, 10, 8400)
INPUT_COUNT = math.prod(INPUT_SHAPE)
OUTPUT_COUNT = math.prod(OUTPUT_SHAPE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_input(case_dir: Path, case_name: str) -> tuple[Path, dict[str, Any]]:
    if case_name == "ones":
        values = np.ones(INPUT_SHAPE, dtype="<f4")
        generator = {"kind": "all_ones", "value": 1.0}
    elif case_name == "random_seed_42":
        values = np.random.RandomState(42).random_sample(INPUT_SHAPE).astype("<f4")
        generator = {"kind": "numpy_random_sample", "seed": 42, "dtype": "float32"}
    else:
        raise ValueError(f"unsupported case: {case_name}")
    values = np.ascontiguousarray(values, dtype="<f4")
    path = case_dir / "input.f32le"
    values.tofile(path)
    manifest = {
        "schema_version": 1,
        "artifact_kind": "stage_k_synthetic_tensor_input",
        "case": case_name,
        "generator": generator,
        "shape": list(INPUT_SHAPE),
        "dtype": "float32",
        "byte_order": "little_endian",
        "layout": "NCHW",
        "element_count": INPUT_COUNT,
        "byte_size": path.stat().st_size,
        "sha256": sha256(path),
        "continuous": bool(values.flags["C_CONTIGUOUS"]),
    }
    write_json(case_dir / "input_manifest.json", manifest)
    return path, manifest


def write_runner_manifest(case_dir: Path, input_path: Path, input_sha: str, case_name: str) -> Path:
    manifest = {
        "schema_version": 1,
        "artifact_kind": "stage_k_raw_tensor_input_manifest",
        "dtype": "float32",
        "byte_order": "little_endian",
        "layout": "NCHW",
        "shape": list(INPUT_SHAPE),
        "element_count": INPUT_COUNT,
        "byte_size": input_path.stat().st_size,
        "entries": [{
            "image_id": case_name,
            "input_tensor_path": input_path.name,
            "input_tensor_sha256": input_sha,
            "dtype": "float32",
            "byte_order": "little_endian",
            "layout": "NCHW",
            "shape": list(INPUT_SHAPE),
            "element_count": INPUT_COUNT,
            "byte_size": input_path.stat().st_size,
        }],
    }
    path = case_dir / "runner_input_manifest.json"
    write_json(path, manifest)
    return path


def run_command(command: list[str], stdout_path: Path, stderr_path: Path) -> None:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    (stdout_path.parent / (stdout_path.stem + ".exit_code.txt")).write_text(
        f"{completed.returncode}\n", encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}")


def run_ort_python(input_path: Path, output_path: Path, model_path: Path) -> dict[str, Any]:
    import onnxruntime as ort  # type: ignore[import-not-found]

    session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    values = np.fromfile(input_path, dtype="<f4").reshape(INPUT_SHAPE)
    output = np.asarray(session.run(["output0"], {input_name: values})[0], dtype="<f4")
    if tuple(output.shape) != OUTPUT_SHAPE:
        raise RuntimeError(f"Python ORT output shape mismatch: {output.shape}")
    np.ascontiguousarray(output).tofile(output_path)
    return {"backend": "python_onnxruntime", "version": ort.__version__, "provider": "CPUExecutionProvider"}


def run_ort_cpp(input_path: Path, output_path: Path, case_dir: Path, ort_runner: Path,
                ort_config: Path) -> dict[str, Any]:
    control_dir = case_dir / "ort_control"
    runtime_record = case_dir / "ort_runtime_record.json"
    command = [str(ort_runner), "--config", str(ort_config), "--input", str(input_path),
               "--raw-output", str(output_path), "--runtime-record", str(runtime_record),
               "--control-directory", str(control_dir)]
    run_command(command, case_dir / "ort.stdout.txt", case_dir / "ort.stderr.txt")
    return {"backend": "cpp_onnxruntime_fallback", "version": "1.23.2", "provider": "CPUExecutionProvider",
            "reason": "Python onnxruntime package is unavailable in this Jetson environment",
            "command": command}


def metric(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    delta = np.abs(reference.astype(np.float64) - candidate.astype(np.float64))
    denominator = float(np.linalg.norm(reference) * np.linalg.norm(candidate))
    cosine = float(np.clip(np.dot(reference.astype(np.float64), candidate.astype(np.float64)) /
                           denominator, -1.0, 1.0))
    return {"mae": float(np.mean(delta)), "max_abs": float(np.max(delta)), "cosine_similarity": cosine}


def compare(reference: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    if reference.shape != OUTPUT_SHAPE or candidate.shape != OUTPUT_SHAPE:
        raise RuntimeError(f"output shape mismatch: {reference.shape} vs {candidate.shape}")
    if not np.isfinite(reference).all() or not np.isfinite(candidate).all():
        raise RuntimeError("non-finite output")
    return {
        "overall": metric(reference.reshape(-1), candidate.reshape(-1)),
        "bbox_channels_0_3": metric(reference[:, 0:4, :].reshape(-1), candidate[:, 0:4, :].reshape(-1)),
        "score_channels_4_9": metric(reference[:, 4:10, :].reshape(-1), candidate[:, 4:10, :].reshape(-1)),
        "shape": list(OUTPUT_SHAPE),
        "finite": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--trt-runner", type=Path, required=True)
    parser.add_argument("--trt-config", type=Path, required=True)
    parser.add_argument("--ort-runner", type=Path, required=True)
    parser.add_argument("--ort-config", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()

    if args.output_root.exists():
        raise RuntimeError(f"output root already exists: {args.output_root}")
    args.output_root.mkdir(parents=True)
    try:
        import onnxruntime as ort  # type: ignore[import-not-found]
        python_ort = {"available": True, "version": ort.__version__}
    except ModuleNotFoundError as exc:
        python_ort = {"available": False, "error": str(exc)}

    report: dict[str, Any] = {
        "schema_version": 1,
        "artifact_kind": "stage_k_synthetic_tensor_isolation_report",
        "source_commit": args.source_commit,
        "model": str(args.model),
        "model_sha256": sha256(args.model),
        "python_environment": {"python": "3.10.12", "onnxruntime_requested": "1.23.2", **python_ort},
        "cases": [],
        "limitations": [],
    }
    if not python_ort["available"]:
        report["limitations"].append("Python onnxruntime package unavailable; C++ ORT 1.23.2 CPU control used explicitly.")

    for case_name in ("ones", "random_seed_42"):
        case_dir = args.output_root / case_name
        case_dir.mkdir()
        input_path, input_manifest = write_input(case_dir, case_name)
        runner_manifest = write_runner_manifest(case_dir, input_path, input_manifest["sha256"], case_name)
        ort_output = case_dir / "Y_ort.f32le"
        trt_output_dir = case_dir / "trt_raw"
        trt_command = [str(args.trt_runner), "--config", str(args.trt_config), "--input-manifest",
                       str(runner_manifest), "--output-dir", str(trt_output_dir), "--run-id",
                       f"synthetic_{case_name}_trt", "--source-commit", args.source_commit]
        if python_ort["available"]:
            ort_meta = run_ort_python(input_path, ort_output, args.model)
        else:
            ort_meta = run_ort_cpp(input_path, ort_output, case_dir, args.ort_runner, args.ort_config)
        run_command(trt_command, case_dir / "trt.stdout.txt", case_dir / "trt.stderr.txt")
        trt_manifest = json.loads((trt_output_dir / "output_manifest.json").read_text())
        trt_output = trt_output_dir / trt_manifest["entries"][0]["output_filename"]
        ort_values = np.fromfile(ort_output, dtype="<f4").reshape(OUTPUT_SHAPE)
        trt_values = np.fromfile(trt_output, dtype="<f4").reshape(OUTPUT_SHAPE)
        case_report = {
            "case": case_name,
            "input": input_manifest,
            "ort_output_sha256": sha256(ort_output),
            "trt_output_sha256": sha256(trt_output),
            "ort": ort_meta,
            "trt": {"engine_sha256": trt_manifest.get("engine_sha256"), "output_manifest": str(trt_output_dir / "output_manifest.json")},
            "metrics": compare(ort_values, trt_values),
        }
        write_json(case_dir / "case_report.json", case_report)
        report["cases"].append(case_report)

    max_abs = max(case["metrics"]["overall"]["max_abs"] for case in report["cases"])
    min_cosine = min(case["metrics"]["overall"]["cosine_similarity"] for case in report["cases"])
    if max_abs < 1.0e-3 and min_cosine > 0.999:
        report["diagnosis"] = "DIAGNOSIS_PREPROCESS_PATH"
    else:
        report["diagnosis"] = "DIAGNOSIS_TENSORRT_GRAPH_OR_BINDING_PATH"
    report["diagnostic_rule_observed"] = {"max_abs": max_abs, "min_cosine_similarity": min_cosine}
    write_json(args.output_root / "synthetic_tensor_isolation_report.json", report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
