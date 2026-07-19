#!/usr/bin/env python3
"""Small, auditable helpers shared by the M5 Level C tools."""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CLASS_NAMES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
POSTPROCESS_KEYS = ["confidence_threshold", "iou_threshold", "max_nms", "max_det", "max_wh", "agnostic", "multi_label"]


class ContractError(ValueError):
    pass


class InitError(RuntimeError):
    pass


class FrameError(RuntimeError):
    pass


class _StrictLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: _StrictLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise ContractError("YAML mapping keys must be strings")
        if key in mapping:
            raise ContractError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


def read_yaml(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = yaml.load(handle, Loader=_StrictLoader)
    except (OSError, yaml.YAMLError, UnicodeError) as exc:
        raise ContractError(f"cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"YAML root must be a mapping: {path}")
    return value


def exact_keys(value: Any, expected: list[str], where: str) -> None:
    if not isinstance(value, dict) or list(value) != expected:
        raise ContractError(f"{where} fields/order mismatch")


def nonempty_string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{where} must be a non-empty string")
    return value


def integer(value: Any, where: str, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ContractError(f"{where} must be an integer")
    if minimum is not None and value < minimum:
        raise ContractError(f"{where} must be >= {minimum}")
    return value


def finite_number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ContractError(f"{where} must be finite")
    return float(value)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise ContractError(f"path is outside repository: {path}") from exc


def _resolved_path(value: Any, config_dir: Path, where: str) -> Path:
    raw = nonempty_string(value, where)
    return (Path(raw) if Path(raw).is_absolute() else config_dir / raw).resolve()


def load_runtime_config(path: Path) -> dict[str, Any]:
    source = read_yaml(path)
    exact_keys(source, ["schema_version", "backend", "model", "input", "output", "postprocess", "timing"], "runtime config")
    if source["schema_version"] != 1 or isinstance(source["schema_version"], bool):
        raise ContractError("schema_version must be 1")
    exact_keys(source["backend"], ["type"], "backend")
    if source["backend"]["type"] != "onnxruntime_cpu":
        raise ContractError("backend.type must be onnxruntime_cpu")
    exact_keys(source["model"], ["contract_path", "model_path"], "model")
    exact_keys(source["input"], ["type", "directory"], "input")
    if source["input"]["type"] != "directory":
        raise ContractError("input.type must be directory")
    exact_keys(source["output"], ["json_path", "console", "overwrite"], "output")
    if not isinstance(source["output"]["console"], bool) or not isinstance(source["output"]["overwrite"], bool):
        raise ContractError("output console/overwrite must be bool")
    exact_keys(source["postprocess"], POSTPROCESS_KEYS, "postprocess")
    confidence = finite_number(source["postprocess"]["confidence_threshold"], "confidence_threshold")
    iou = finite_number(source["postprocess"]["iou_threshold"], "iou_threshold")
    max_nms = integer(source["postprocess"]["max_nms"], "max_nms", 1)
    max_det = integer(source["postprocess"]["max_det"], "max_det", 1)
    max_wh = finite_number(source["postprocess"]["max_wh"], "max_wh")
    if not 0 <= confidence <= 1 or not 0 <= iou <= 1 or max_nms < max_det or max_wh <= 0:
        raise ContractError("invalid postprocess ranges")
    if source["postprocess"]["agnostic"] is not False or source["postprocess"]["multi_label"] is not False:
        raise ContractError("agnostic and multi_label must be false")
    exact_keys(source["timing"], ["enabled"], "timing")
    if source["timing"]["enabled"] is not False:
        raise ContractError("Level C reference requires timing.enabled=false")
    config_dir = path.resolve().parent
    return {
        "path": path.resolve(),
        "contract_path": _resolved_path(source["model"]["contract_path"], config_dir, "model.contract_path"),
        "model_path": _resolved_path(source["model"]["model_path"], config_dir, "model.model_path"),
        "input_directory": _resolved_path(source["input"]["directory"], config_dir, "input.directory"),
        "postprocess": {key: source["postprocess"][key] for key in POSTPROCESS_KEYS},
    }


def load_model_contract(path: Path, model_path: Path) -> dict[str, Any]:
    source = read_yaml(path)
    exact_keys(source, ["schema_version", "model", "input", "output", "classes"], "model contract")
    if source["schema_version"] != 1 or isinstance(source["schema_version"], bool):
        raise ContractError("model contract schema_version must be 1")
    exact_keys(source["model"], ["id", "format", "sha256", "size_bytes"], "contract.model")
    if source["model"]["format"] != "onnx":
        raise ContractError("contract model.format must be onnx")
    expected_sha = nonempty_string(source["model"]["sha256"], "contract model.sha256")
    if len(expected_sha) != 64 or any(c not in "0123456789abcdef" for c in expected_sha):
        raise ContractError("contract model.sha256 is invalid")
    if not model_path.is_file() or model_path.is_symlink():
        raise InitError(f"model is not a regular file: {model_path}")
    if sha256_file(model_path) != expected_sha:
        raise InitError("model SHA256 does not match contract")
    if model_path.stat().st_size != integer(source["model"]["size_bytes"], "contract model.size_bytes", 1):
        raise InitError("model size does not match contract")
    for section, expected in (("input", ["name", "dtype", "layout", "shape"]), ("output", ["name", "dtype", "layout", "shape"])):
        exact_keys(source[section], expected, f"contract.{section}")
        if source[section]["dtype"] != "float32":
            raise ContractError(f"contract.{section}.dtype must be float32")
        expected_layout = "NCHW" if section == "input" else "BCN"
        if source[section]["layout"] != expected_layout:
            raise ContractError(f"contract.{section}.layout must be {expected_layout}")
        if not isinstance(source[section]["shape"], list) or any(isinstance(v, bool) or not isinstance(v, int) or v <= 0 for v in source[section]["shape"]):
            raise ContractError(f"contract.{section}.shape is invalid")
    exact_keys(source["classes"], ["count", "names"], "contract.classes")
    if source["classes"]["count"] != 6 or source["classes"]["names"] != CLASS_NAMES:
        raise ContractError("contract class names mismatch")
    if source["input"]["shape"] != [1, 3, 640, 640] or source["output"]["shape"] != [1, 10, 8400]:
        raise ContractError("contract tensor shapes are not the frozen Level C shapes")
    return {"path": path.resolve(), "model_path": model_path.resolve(), "source": source}


def enumerate_images(input_dir: Path) -> list[Path]:
    if not input_dir.is_dir() or input_dir.is_symlink():
        raise InitError(f"input directory is not a real directory: {input_dir}")
    paths = []
    for path in input_dir.iterdir():
        if path.is_symlink() or not path.is_file() or path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".bmp"}:
            continue
        paths.append(path)
    paths.sort(key=lambda path: path.name)
    if not paths:
        raise InitError("input directory contains no supported image files")
    return paths


def python_round(value: float) -> int:
    lower = math.floor(value)
    fraction = value - lower
    return int(lower + (1 if fraction > 0.5 or (fraction == 0.5 and lower % 2 != 0) else 0))


def preprocess(image_bgr: np.ndarray, target_width: int = 640, target_height: int = 640) -> tuple[np.ndarray, dict[str, Any]]:
    if image_bgr is None or image_bgr.ndim != 3 or image_bgr.dtype != np.uint8 or image_bgr.shape[2] != 3:
        raise FrameError("input image must be uint8 BGR three-channel")
    height, width = image_bgr.shape[:2]
    gain = min(target_width / width, target_height / height)
    resized_width = python_round(width * gain)
    resized_height = python_round(height * gain)
    pad_left = python_round((target_width - resized_width) / 2.0 - 0.1)
    pad_right = python_round((target_width - resized_width) / 2.0 + 0.1)
    pad_top = python_round((target_height - resized_height) / 2.0 - 0.1)
    pad_bottom = python_round((target_height - resized_height) / 2.0 + 0.1)
    resized = cv2.resize(image_bgr, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
    letterboxed = cv2.copyMakeBorder(resized, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
    rgb = cv2.cvtColor(letterboxed, cv2.COLOR_BGR2RGB)
    tensor = np.ascontiguousarray(np.transpose(rgb, (2, 0, 1))[None, ...], dtype=np.float32) / np.float32(255.0)
    if tensor.shape != (1, 3, 640, 640) or not tensor.flags.c_contiguous or not np.isfinite(tensor).all():
        raise FrameError("preprocessed tensor contract failure")
    return tensor, {"original_width": width, "original_height": height, "gain": gain, "pad_left": pad_left, "pad_top": pad_top}


def _f32(value: Any) -> np.float32:
    return np.float32(value)


def postprocess(raw: np.ndarray, transform: dict[str, Any], config: dict[str, Any]) -> list[dict[str, Any]]:
    raw = np.ascontiguousarray(raw, dtype=np.float32)
    if raw.shape != (1, 10, 8400) or not np.isfinite(raw).all():
        raise FrameError("raw output must be finite float32 [1,10,8400]")
    threshold = _f32(config["confidence_threshold"])
    candidates: list[dict[str, Any]] = []
    for index in range(8400):
        cx, cy, width, height = (_f32(raw[0, channel, index]) for channel in range(4))
        if width <= 0 or height <= 0:
            continue
        class_id = 0
        confidence = _f32(raw[0, 4, index])
        for class_index in range(1, 6):
            score = _f32(raw[0, 4 + class_index, index])
            if score > confidence:
                confidence, class_id = score, class_index
        if confidence <= threshold:
            continue
        half_width, half_height = width / _f32(2), height / _f32(2)
        values = [cx - half_width, cy - half_height, cx + half_width, cy + half_height]
        if not all(np.isfinite(v) for v in values):
            continue
        candidates.append({"x1": _f32(values[0]), "y1": _f32(values[1]), "x2": _f32(values[2]), "y2": _f32(values[3]), "confidence": confidence, "class_id": class_id, "candidate_index": index})
    candidates.sort(key=lambda item: (-float(item["confidence"]), item["class_id"], item["candidate_index"]))
    candidates = candidates[: int(config["max_nms"])]
    retained: list[dict[str, Any]] = []
    suppressed = [False] * len(candidates)
    max_wh = _f32(config["max_wh"])
    iou_threshold = _f32(config["iou_threshold"])
    for current_index, current in enumerate(candidates):
        if suppressed[current_index]:
            continue
        retained.append(current)
        if len(retained) == int(config["max_det"]):
            break
        current_offset = _f32(current["class_id"]) * max_wh
        for later_index in range(current_index + 1, len(candidates)):
            if suppressed[later_index]:
                continue
            later = candidates[later_index]
            later_offset = _f32(later["class_id"]) * max_wh
            lx1, ly1, lx2, ly2 = [_f32(current[k]) + current_offset for k in ("x1", "y1", "x2", "y2")]
            rx1, ry1, rx2, ry2 = [_f32(later[k]) + later_offset for k in ("x1", "y1", "x2", "y2")]
            iw, ih = max(_f32(0), min(lx2, rx2) - max(lx1, rx1)), max(_f32(0), min(ly2, ry2) - max(ly1, ry1))
            ia = iw * ih
            la = max(_f32(0), lx2 - lx1) * max(_f32(0), ly2 - ly1)
            ra = max(_f32(0), rx2 - rx1) * max(_f32(0), ry2 - ry1)
            union = la + ra - ia
            iou = ia / union if union > 0 else _f32(0)
            if np.isfinite(iou) and iou > iou_threshold:
                suppressed[later_index] = True
    output: list[dict[str, Any]] = []
    for candidate in retained:
        def restore(value: np.float32, padding: int, extent: int) -> float:
            restored = (float(value) - padding) / transform["gain"]
            return float(min(max(restored, 0.0), float(extent)))
        output.append({"x1": restore(candidate["x1"], transform["pad_left"], transform["original_width"]), "y1": restore(candidate["y1"], transform["pad_top"], transform["original_height"]), "x2": restore(candidate["x2"], transform["pad_left"], transform["original_width"]), "y2": restore(candidate["y2"], transform["pad_top"], transform["original_height"]), "confidence": float(candidate["confidence"]), "class_id": candidate["class_id"], "candidate_index": candidate["candidate_index"]})
    return output


def clean_json(value: Any) -> Any:
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractError("JSON value is not finite")
        return 0.0 if value == 0.0 else value
    if isinstance(value, np.floating):
        return clean_json(float(value))
    if isinstance(value, dict):
        return {key: clean_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [clean_json(item) for item in value]
    return value


def stable_json_bytes(value: Any) -> bytes:
    return (json.dumps(clean_json(value), ensure_ascii=False, indent=2, allow_nan=False, separators=(",", ": ")) + "\n").encode("utf-8")


def atomic_write(path: Path, value: Any, *, refuse_existing: bool = True) -> None:
    if refuse_existing and path.exists():
        raise InitError(f"output already exists: {path}")
    if not path.parent.is_dir():
        raise InitError(f"output parent directory does not exist: {path.parent}")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(stable_json_bytes(value))
        if refuse_existing and path.exists():
            raise InitError(f"output already exists: {path}")
        os.replace(temporary, path)
    except Exception:
        try:
            Path(temporary).unlink(missing_ok=True)
        except OSError:
            pass
        raise
