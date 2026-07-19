#!/usr/bin/env python3
"""Explicit Python ONNX Runtime Level C reference (M5.2A)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort

from m5_level_c_common import (
    CLASS_NAMES,
    ContractError,
    FrameError,
    InitError,
    atomic_write,
    enumerate_images,
    load_model_contract,
    load_runtime_config,
    postprocess,
    preprocess,
    sha256_file,
)


def _metadata_path(path: Path) -> str:
    try:
        from m5_level_c_common import repo_relative
        return repo_relative(path)
    except ContractError:
        return path.name


def _shape(value: object) -> list[int]:
    if not isinstance(value, (list, tuple)) or any(not isinstance(item, int) for item in value):
        raise InitError("ORT tensor shape must be concrete integers")
    return list(value)


def create_session(config: dict, contract: dict) -> tuple[ort.InferenceSession, dict]:
    source = contract["source"]
    input_meta = source["input"]
    output_meta = source["output"]
    try:
        options = ort.SessionOptions()
        options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        options.intra_op_num_threads = 1
        options.inter_op_num_threads = 1
        session = ort.InferenceSession(str(config["model_path"]), sess_options=options, providers=["CPUExecutionProvider"])
    except Exception as exc:
        raise InitError(f"ORT session initialization failed: {exc}") from exc
    providers = session.get_providers()
    if providers != ["CPUExecutionProvider"]:
        raise InitError(f"ORT providers are not CPU-only: {providers}")
    inputs, outputs = session.get_inputs(), session.get_outputs()
    if len(inputs) != 1 or len(outputs) != 1:
        raise InitError("ORT model must have one input and one output")
    actual_input, actual_output = inputs[0], outputs[0]
    if actual_input.name != input_meta["name"] or actual_output.name != output_meta["name"]:
        raise InitError("ORT input/output name does not match ModelContract")
    if _shape(actual_input.shape) != input_meta["shape"] or _shape(actual_output.shape) != output_meta["shape"]:
        raise InitError("ORT input/output shape does not match ModelContract")
    if actual_input.type != "tensor(float)" or actual_output.type != "tensor(float)":
        raise InitError("ORT input/output dtype is not float32")
    return session, {"input": actual_input, "output": actual_output}


def run_reference(config_path: Path, input_dir: Path, output_path: Path) -> dict:
    config = load_runtime_config(config_path)
    if input_dir != config["input_directory"]:
        # The CLI input override is intentionally limited to the prepared corpus path.
        config["input_directory"] = input_dir.resolve()
    contract = load_model_contract(config["contract_path"], config["model_path"])
    session, meta = create_session(config, contract)
    paths = enumerate_images(config["input_directory"])
    images = []
    per_class = [0] * len(CLASS_NAMES)
    for sequence_index, path in enumerate(paths):
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None or image.ndim != 3 or image.dtype != np.uint8 or image.shape[2] != 3:
            raise FrameError(f"cannot decode image: {path.name}")
        tensor, transform = preprocess(image)
        try:
            raw_values = session.run([meta["output"].name], {meta["input"].name: tensor})[0]
        except Exception as exc:
            raise FrameError(f"ORT inference failed for {path.name}: {exc}") from exc
        detections = postprocess(raw_values, transform, config["postprocess"])
        for detection in detections:
            per_class[detection["class_id"]] += 1
        images.append({"sequence_index": sequence_index, "relative_path": path.name, "width": int(image.shape[1]), "height": int(image.shape[0]), "detections": detections})
    output = {
        "schema_version": 1,
        "reference": {"type": "python_onnxruntime_explicit", "preprocess": "letterbox_bgr_rgb_nchw_float32"},
        "model": {"contract_path": _metadata_path(contract["path"]), "model_path": _metadata_path(contract["model_path"]), "model_sha256": sha256_file(contract["model_path"]), "input_name": contract["source"]["input"]["name"], "input_shape": contract["source"]["input"]["shape"], "input_dtype": contract["source"]["input"]["dtype"], "output_name": contract["source"]["output"]["name"], "output_shape": contract["source"]["output"]["shape"], "output_dtype": contract["source"]["output"]["dtype"], "class_names": CLASS_NAMES},
        "postprocess": config["postprocess"],
        "images": images,
        "summary": {"image_count": len(images), "detection_count": sum(per_class), "per_class_counts": per_class},
    }
    atomic_write(output_path, output)
    return output


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the explicit Python ONNX Runtime Level C reference.")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        run_reference(args.config, args.input_dir, args.output)
        print(f"reference wrote {args.output}")
        return 0
    except SystemExit as exc:
        return int(exc.code)
    except ContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except InitError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    except FrameError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
