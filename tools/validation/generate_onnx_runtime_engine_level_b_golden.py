#!/usr/bin/env python3
"""Generate a Python ONNX Runtime golden output for M2 Level B."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort


REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_ORT_VERSION = "1.23.2"
INPUT_SHAPE = (1, 3, 640, 640)
OUTPUT_SHAPE = (1, 10, 8400)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Python ONNX Runtime Level B raw-output golden data."
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=REPO_ROOT / "models/onnx/yolov8n_neudet_frozen.onnx",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=(
            REPO_ROOT
            / "tests/data/preprocess_level_a/golden/frozen_640_checkerboard.f32le"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "results/validation/onnx_runtime_engine_level_b",
    )
    return parser.parse_args()


def load_input(path: Path) -> np.ndarray:
    expected_count = int(np.prod(INPUT_SHAPE))
    expected_size = expected_count * np.dtype("<f4").itemsize
    if not path.is_file():
        raise ValueError(f"Input tensor is not a regular file: {path}")
    if path.stat().st_size != expected_size:
        raise ValueError(
            f"Input tensor byte size mismatch: expected {expected_size}, "
            f"actual {path.stat().st_size}"
        )
    tensor = np.fromfile(path, dtype="<f4")
    if tensor.size != expected_count or not np.isfinite(tensor).all():
        raise ValueError("Input tensor must contain exactly finite float32 values")
    return np.ascontiguousarray(tensor.reshape(INPUT_SHAPE))


def main() -> int:
    args = parse_args()
    model_path = args.model.resolve()
    input_path = args.input.resolve()
    output_dir = args.output_dir.resolve()
    if ort.__version__ != EXPECTED_ORT_VERSION:
        raise RuntimeError(
            f"Expected onnxruntime {EXPECTED_ORT_VERSION}, got {ort.__version__}"
        )
    if not model_path.is_file():
        raise ValueError(f"Model is not a regular file: {model_path}")

    input_tensor = load_input(input_path)
    session_options = ort.SessionOptions()
    session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        str(model_path), sess_options=session_options, providers=["CPUExecutionProvider"]
    )
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    if len(inputs) != 1 or len(outputs) != 1:
        raise ValueError("Expected exactly one model input and one model output")
    if inputs[0].name != "images" or outputs[0].name != "output0":
        raise ValueError("Unexpected frozen model input/output names")

    output_tensor = session.run([outputs[0].name], {inputs[0].name: input_tensor})[0]
    if output_tensor.dtype != np.float32 or tuple(output_tensor.shape) != OUTPUT_SHAPE:
        raise ValueError("Python ORT output contract mismatch")
    if not np.isfinite(output_tensor).all():
        raise ValueError("Python ORT output contains non-finite values")

    output_dir.mkdir(parents=True, exist_ok=True)
    golden_path = output_dir / "python_golden_output.f32le"
    manifest_path = output_dir / "input_manifest.json"
    np.ascontiguousarray(output_tensor.astype("<f4", copy=False)).tofile(golden_path)

    command = " ".join(
        [
            "./.venv/bin/python",
            "tools/validation/generate_onnx_runtime_engine_level_b_golden.py",
            "--model",
            repo_relative(model_path),
            "--input",
            repo_relative(input_path),
            "--output-dir",
            repo_relative(output_dir),
        ]
    )
    manifest = {
        "schema_version": 1,
        "evidence_id": "onnx_runtime_engine_level_b",
        "command": command,
        "environment": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "onnxruntime_version": ort.__version__,
            "providers": session.get_providers(),
        },
        "model": {
            "path": repo_relative(model_path),
            "size_bytes": model_path.stat().st_size,
            "sha256": sha256_file(model_path),
        },
        "input": {
            "path": repo_relative(input_path),
            "sha256": sha256_file(input_path),
            "dtype": "float32",
            "byte_order": "little_endian",
            "layout": "NCHW",
            "shape": list(INPUT_SHAPE),
            "element_count": int(input_tensor.size),
        },
        "python_golden_output": {
            "path": repo_relative(golden_path),
            "sha256": sha256_file(golden_path),
            "dtype": "float32",
            "byte_order": "little_endian",
            "layout": "BCN",
            "shape": list(OUTPUT_SHAPE),
            "element_count": int(output_tensor.size),
            "finite_count": int(np.isfinite(output_tensor).sum()),
        },
        "invocation": {"python_executable": sys.executable},
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Level B Python golden: {golden_path}")
    print(f"Level B input manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
