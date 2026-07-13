#!/usr/bin/env python3
"""Export a YOLO checkpoint to ONNX from a validated YAML configuration."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CONFIG_KEYS = (
    "source_model",
    "onnx_path",
    "metadata_path",
    "imgsz",
    "opset",
    "dynamic",
    "simplify",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export a YOLO model to ONNX using a YAML configuration."
    )
    parser.add_argument(
        "--config", type=Path, required=True, help="ONNX export YAML config path."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the config and source model, then print the export plan without writing files.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.is_file():
        raise FileNotFoundError(f"Export config not found: {config_path}")
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required; install the project requirements first.") from exc

    loaded = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"Export config must be a YAML mapping: {config_path}")
    return loaded


def resolve_repo_path(value: Any) -> Path:
    path = Path(str(value)).expanduser()
    return path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()


def validate_config(config: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    if missing:
        raise ValueError(f"Missing required export config fields: {missing}")

    source_model = resolve_repo_path(config["source_model"])
    onnx_path = resolve_repo_path(config["onnx_path"])
    metadata_path = resolve_repo_path(config["metadata_path"])
    if not source_model.is_file():
        raise FileNotFoundError(f"Source model not found: {source_model}")
    if source_model.suffix.lower() != ".pt":
        raise ValueError(f"source_model must be a .pt file: {source_model}")
    if onnx_path.suffix.lower() != ".onnx":
        raise ValueError(f"onnx_path must be a .onnx file: {onnx_path}")
    if metadata_path.suffix.lower() != ".json":
        raise ValueError(f"metadata_path must be a .json file: {metadata_path}")
    if source_model == onnx_path:
        raise ValueError("source_model and onnx_path must be different files")

    for key in ("imgsz", "opset"):
        value = config[key]
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"Config field '{key}' must be a positive integer: {value!r}")
    for key in ("dynamic", "simplify"):
        if not isinstance(config[key], bool):
            raise ValueError(f"Config field '{key}' must be a boolean: {config[key]!r}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def export_plan(config: dict[str, Any]) -> dict[str, Any]:
    source_model = resolve_repo_path(config["source_model"])
    return {
        "source_model_path": display_path(source_model),
        "source_model_sha256": sha256_file(source_model),
        "onnx_path": display_path(resolve_repo_path(config["onnx_path"])),
        "metadata_path": display_path(resolve_repo_path(config["metadata_path"])),
        "imgsz": config["imgsz"],
        "opset": config["opset"],
        "dynamic": config["dynamic"],
        "simplify": config["simplify"],
    }


def load_export_dependencies() -> tuple[Any, Any, Any, Any]:
    try:
        import onnx
        import torch
        import ultralytics
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            f"Missing ONNX export dependency '{exc.name}'. Install the project requirements first."
        ) from exc
    return YOLO, onnx, ultralytics, torch


def export_model(config: dict[str, Any], yolo_class: Any) -> Path:
    source_model = resolve_repo_path(config["source_model"])
    onnx_path = resolve_repo_path(config["onnx_path"])
    onnx_path.parent.mkdir(parents=True, exist_ok=True)

    # Export from a temporary checkpoint copy so Ultralytics does not create an
    # intermediate ONNX file beside the frozen source model.
    with tempfile.TemporaryDirectory(prefix=".onnx-export-", dir=onnx_path.parent) as temp_dir:
        temp_model = Path(temp_dir) / source_model.name
        shutil.copy2(source_model, temp_model)
        exported = Path(
            yolo_class(str(temp_model)).export(
                format="onnx",
                imgsz=config["imgsz"],
                opset=config["opset"],
                dynamic=config["dynamic"],
                simplify=config["simplify"],
            )
        )
        if not exported.is_file():
            raise FileNotFoundError(
                f"Ultralytics reported an export, but no ONNX file exists: {exported}"
            )
        os.replace(exported, onnx_path)
    return onnx_path


def tensor_description(value_info: Any, onnx_module: Any) -> str:
    tensor_type = value_info.type.tensor_type
    dtype = onnx_module.TensorProto.DataType.Name(tensor_type.elem_type)
    dimensions: list[str] = []
    for dimension in tensor_type.shape.dim:
        if dimension.HasField("dim_value"):
            dimensions.append(str(dimension.dim_value))
        elif dimension.HasField("dim_param"):
            dimensions.append(dimension.dim_param)
        else:
            dimensions.append("?")
    return f"name={value_info.name}, dtype={dtype}, shape=[{', '.join(dimensions)}]"


def check_and_print_onnx(onnx_path: Path, onnx_module: Any) -> None:
    if not onnx_path.is_file():
        raise FileNotFoundError(f"Exported ONNX file not found: {onnx_path}")
    model = onnx_module.load(str(onnx_path))
    onnx_module.checker.check_model(model)
    print(f"ONNX checker: PASS ({display_path(onnx_path)})")
    print("Inputs:")
    for value_info in model.graph.input:
        print(f"  - {tensor_description(value_info, onnx_module)}")
    print("Outputs:")
    for value_info in model.graph.output:
        print(f"  - {tensor_description(value_info, onnx_module)}")


def timestamp() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_metadata(
    config: dict[str, Any],
    onnx_path: Path,
    ultralytics_version: str,
    torch_version: str,
) -> Path:
    source_model = resolve_repo_path(config["source_model"])
    metadata_path = resolve_repo_path(config["metadata_path"])
    metadata = {
        "source_model_path": display_path(source_model),
        "source_model_sha256": sha256_file(source_model),
        "onnx_path": display_path(onnx_path),
        "onnx_sha256": sha256_file(onnx_path),
        "imgsz": config["imgsz"],
        "opset": config["opset"],
        "dynamic": config["dynamic"],
        "simplify": config["simplify"],
        "ultralytics_version": ultralytics_version,
        "torch_version": torch_version,
        "timestamp": timestamp(),
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = metadata_path.with_suffix(metadata_path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary_path, metadata_path)
    return metadata_path


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
        validate_config(config)
        if args.dry_run:
            print("Dry run: ONNX export configuration is valid; no files were written.")
            print(json.dumps(export_plan(config), ensure_ascii=False, indent=2))
            return 0

        yolo_class, onnx_module, ultralytics_module, torch_module = load_export_dependencies()
        onnx_path = export_model(config, yolo_class)
        check_and_print_onnx(onnx_path, onnx_module)
        metadata_path = write_metadata(
            config,
            onnx_path,
            ultralytics_module.__version__,
            torch_module.__version__,
        )
        print(f"Metadata: {display_path(metadata_path)}")
        return 0
    except (FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
