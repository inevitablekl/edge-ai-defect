#!/usr/bin/env python3
"""Run one ONNX Runtime inference and record lightweight validation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_PATH = Path("results/onnx_export/onnxruntime_smoke_test.json")
ORT_TO_NUMPY_DTYPE = {
    "tensor(float)": np.dtype(np.float32),
    "tensor(double)": np.dtype(np.float64),
    "tensor(float16)": np.dtype(np.float16),
    "tensor(int64)": np.dtype(np.int64),
    "tensor(int32)": np.dtype(np.int32),
    "tensor(uint8)": np.dtype(np.uint8),
}


class SmokeTestError(RuntimeError):
    """Raised when the model cannot complete a valid smoke inference."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load an ONNX model and run one ONNX Runtime dummy inference."
    )
    parser.add_argument("--model", type=Path, required=True, help="Path to the ONNX model.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=f"JSON evidence path (default: {DEFAULT_OUTPUT_PATH}).",
    )
    return parser.parse_args()


def resolve_repo_path(path: Path) -> Path:
    path = path.expanduser()
    return path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_shape(shape: list[Any]) -> list[int | str | None]:
    return [dimension if isinstance(dimension, (int, str)) else None for dimension in shape]


def numpy_dtype(ort_dtype: str) -> np.dtype[Any]:
    try:
        return ORT_TO_NUMPY_DTYPE[ort_dtype]
    except KeyError as exc:
        raise SmokeTestError(f"Unsupported ONNX Runtime tensor dtype: {ort_dtype}") from exc


def create_dummy_input(input_info: Any) -> np.ndarray[Any, Any]:
    shape = normalized_shape(input_info.shape)
    if not shape or any(not isinstance(dimension, int) or dimension <= 0 for dimension in shape):
        raise SmokeTestError(
            f"Input '{input_info.name}' must have a concrete positive shape, got {shape}"
        )
    dtype = numpy_dtype(input_info.type)
    if dtype != np.dtype(np.float32):
        raise SmokeTestError(
            f"Input '{input_info.name}' must be float32 for this smoke test, got {dtype.name}"
        )
    return np.zeros(tuple(shape), dtype=dtype)


def tensor_metadata(value_info: Any) -> dict[str, Any]:
    return {
        "name": value_info.name,
        "shape": normalized_shape(value_info.shape),
        "dtype": numpy_dtype(value_info.type).name,
    }


def output_statistics(name: str, output: Any) -> dict[str, Any]:
    array = np.asarray(output)
    is_floating = np.issubdtype(array.dtype, np.floating)
    has_nan = bool(np.isnan(array).any()) if is_floating else False
    has_inf = bool(np.isinf(array).any()) if is_floating else False
    if is_floating:
        finite_values = array[np.isfinite(array)]
    else:
        finite_values = array.reshape(-1)
    return {
        "name": name,
        "shape": list(array.shape),
        "dtype": array.dtype.name,
        "size": int(array.size),
        "min": float(finite_values.min()) if finite_values.size else None,
        "max": float(finite_values.max()) if finite_values.size else None,
        "mean": float(finite_values.mean()) if finite_values.size else None,
        "has_nan": has_nan,
        "has_inf": has_inf,
    }


def write_json(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary_path, path)


def run_smoke_test(model_path: Path, output_path: Path, ort_module: Any) -> dict[str, Any]:
    model_path = resolve_repo_path(model_path)
    output_path = resolve_repo_path(output_path)
    if not model_path.is_file():
        raise FileNotFoundError(f"ONNX model not found: {model_path}")
    if model_path.stat().st_size == 0:
        raise SmokeTestError(f"ONNX model is empty: {model_path}")

    evidence: dict[str, Any] = {
        "timestamp": timestamp(),
        "model_path": display_path(model_path),
        "model_sha256": sha256_file(model_path),
        "onnxruntime_version": ort_module.__version__,
        "input_metadata": [],
        "output_metadata": [],
        "inference_success": False,
        "output_statistics": {
            "all_outputs_non_empty": False,
            "contains_nan": False,
            "contains_inf": False,
            "outputs": [],
        },
    }

    try:
        session = ort_module.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        input_infos = session.get_inputs()
        output_infos = session.get_outputs()
        if not input_infos:
            raise SmokeTestError("The ONNX model has no inputs")
        if not output_infos:
            raise SmokeTestError("The ONNX model has no outputs")

        evidence["input_metadata"] = [tensor_metadata(info) for info in input_infos]
        feeds = {info.name: create_dummy_input(info) for info in input_infos}
        outputs = session.run(None, feeds)
        if len(outputs) != len(output_infos):
            raise SmokeTestError(
                f"Runtime returned {len(outputs)} outputs; model declares {len(output_infos)}"
            )

        statistics = [
            output_statistics(info.name, output)
            for info, output in zip(output_infos, outputs, strict=True)
        ]
        output_metadata = []
        for info, stats in zip(output_infos, statistics, strict=True):
            metadata = tensor_metadata(info)
            metadata["runtime_shape"] = stats["shape"]
            metadata["runtime_dtype"] = stats["dtype"]
            output_metadata.append(metadata)
        evidence["output_metadata"] = output_metadata

        all_non_empty = all(stats["size"] > 0 for stats in statistics)
        contains_nan = any(stats["has_nan"] for stats in statistics)
        contains_inf = any(stats["has_inf"] for stats in statistics)
        success = all_non_empty and not contains_nan and not contains_inf
        evidence["output_statistics"] = {
            "all_outputs_non_empty": all_non_empty,
            "contains_nan": contains_nan,
            "contains_inf": contains_inf,
            "outputs": statistics,
        }
        evidence["inference_success"] = success
    except Exception as exc:
        evidence["error"] = f"{type(exc).__name__}: {exc}"
        write_json(output_path, evidence)
        if isinstance(exc, SmokeTestError):
            raise
        raise SmokeTestError(str(exc)) from exc

    write_json(output_path, evidence)
    print(f"ONNX Runtime version: {ort_module.__version__}")
    for metadata in evidence["input_metadata"]:
        print(
            f"Input: name={metadata['name']}, shape={metadata['shape']}, "
            f"dtype={metadata['dtype']}"
        )
    for metadata in evidence["output_metadata"]:
        print(
            f"Output: name={metadata['name']}, shape={metadata['runtime_shape']}, "
            f"dtype={metadata['runtime_dtype']}"
        )
    print(f"Inference: {'PASS' if evidence['inference_success'] else 'FAIL'}")
    print(f"Evidence: {display_path(output_path)}")
    if not evidence["inference_success"]:
        raise SmokeTestError("Output validation failed: empty tensor, NaN, or Inf detected")
    return evidence


def load_onnxruntime() -> Any:
    try:
        import onnxruntime
    except ImportError as exc:
        raise RuntimeError(
            "onnxruntime is required; install the project requirements first."
        ) from exc
    return onnxruntime


def main() -> int:
    args = parse_args()
    try:
        run_smoke_test(args.model, args.output, load_onnxruntime())
        return 0
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
