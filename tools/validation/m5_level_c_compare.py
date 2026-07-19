#!/usr/bin/env python3
"""Deterministic semantic comparator for Python and C++ Level C results."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from m5_level_c_common import ContractError, InitError, atomic_write


CONF_TOL = 1e-4
BBOX_TOL = 0.01
REF_TOP = ["schema_version", "reference", "model", "postprocess", "images", "summary"]
CPP_TOP = ["schema_version", "backend", "model", "postprocess", "images", "summary"]
IMAGE_KEYS = ["sequence_index", "relative_path", "width", "height", "detections"]
DETECTION_KEYS = ["x1", "y1", "x2", "y2", "confidence", "class_id", "candidate_index"]


class SchemaError(ValueError):
    pass


def _dup(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SchemaError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
        if not raw.endswith("\n") or raw.endswith("\n\n"):
            raise SchemaError("JSON must end with exactly one LF")
        return json.loads(raw, object_pairs_hook=_dup)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SchemaError(f"cannot read JSON {path}: {exc}") from exc


def _keys(value: Any, expected: list[str], where: str) -> None:
    if not isinstance(value, dict) or list(value) != expected:
        raise SchemaError(f"{where} fields/order mismatch")


def _finite(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise SchemaError(f"{where} must be finite")
    return float(value)


def _int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise SchemaError(f"{where} must be integer")
    return value


def _normalize_image(image: dict[str, Any], where: str) -> dict[str, Any]:
    _keys(image, IMAGE_KEYS, where)
    sequence = _int(image["sequence_index"], f"{where}.sequence_index")
    width, height = _int(image["width"], f"{where}.width"), _int(image["height"], f"{where}.height")
    if sequence < 0 or width <= 0 or height <= 0 or not isinstance(image["relative_path"], str) or not image["relative_path"] or Path(image["relative_path"]).is_absolute():
        raise SchemaError(f"{where} identity is invalid")
    detections = image["detections"]
    if not isinstance(detections, list):
        raise SchemaError(f"{where}.detections must be a list")
    normalized = []
    for index, detection in enumerate(detections):
        _keys(detection, DETECTION_KEYS, f"{where}.detections[{index}]")
        values = {key: _finite(detection[key], f"{where}.detections[{index}].{key}") for key in ("x1", "y1", "x2", "y2", "confidence")}
        class_id, candidate_index = _int(detection["class_id"], "class_id"), _int(detection["candidate_index"], "candidate_index")
        if not 0 <= class_id < 6 or not 0 <= candidate_index < 8400:
            raise SchemaError(f"{where}.detections[{index}] identifiers are invalid")
        values.update({"class_id": class_id, "candidate_index": candidate_index})
        normalized.append(values)
    return {"sequence_index": sequence, "relative_path": image["relative_path"], "width": width, "height": height, "detections": normalized}


def _normalize_reference(data: Any) -> dict[str, Any]:
    _keys(data, REF_TOP, "reference result")
    if data["schema_version"] != 1 or data["reference"] != {"type": "python_onnxruntime_explicit", "preprocess": "letterbox_bgr_rgb_nchw_float32"}:
        raise SchemaError("reference identity mismatch")
    model = data["model"]
    expected_model = ["contract_path", "model_path", "model_sha256", "input_name", "input_shape", "input_dtype", "output_name", "output_shape", "output_dtype", "class_names"]
    _keys(model, expected_model, "reference model")
    if model["class_names"] != ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]:
        raise SchemaError("reference class contract mismatch")
    postprocess = _normalize_postprocess(data["postprocess"])
    images = data["images"]
    if not isinstance(images, list):
        raise SchemaError("reference images must be a list")
    normalized = [_normalize_image(image, f"reference images[{index}]") for index, image in enumerate(images)]
    summary = data["summary"]
    _keys(summary, ["image_count", "detection_count", "per_class_counts"], "reference summary")
    result = _check_summary(normalized, summary, model["class_names"])
    result["postprocess"] = postprocess
    return result


def _normalize_postprocess(value: Any) -> dict:
    expected = ["confidence_threshold", "iou_threshold", "max_nms", "max_det", "max_wh", "agnostic", "multi_label"]
    _keys(value, expected, "postprocess")
    if value["agnostic"] is not False or value["multi_label"] is not False:
        raise SchemaError("postprocess flags mismatch")
    return value


def _normalize_cpp(data: Any) -> dict[str, Any]:
    _keys(data, CPP_TOP, "C++ result")
    if data["schema_version"] != 1 or data["backend"] != {"type": "onnxruntime_cpu"}:
        raise SchemaError("C++ identity mismatch")
    model = data["model"]
    _keys(model, ["filename", "sha256", "contract_filename", "classes"], "C++ model")
    if model["classes"] != ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]:
        raise SchemaError("C++ class contract mismatch")
    postprocess = _normalize_postprocess(data["postprocess"])
    images = data["images"]
    if not isinstance(images, list):
        raise SchemaError("C++ images must be a list")
    normalized = [_normalize_image(image, f"C++ images[{index}]") for index, image in enumerate(images)]
    summary = data["summary"]
    _keys(summary, ["processed_images", "total_detections"], "C++ summary")
    result = _check_summary(normalized, {"image_count": summary["processed_images"], "detection_count": summary["total_detections"], "per_class_counts": _class_counts(normalized)}, model["classes"])
    result["postprocess"] = postprocess
    return result


def _class_counts(images: list[dict[str, Any]]) -> list[int]:
    counts = [0] * 6
    for image in images:
        for detection in image["detections"]:
            counts[detection["class_id"]] += 1
    return counts


def _check_summary(images: list[dict[str, Any]], summary: dict[str, Any], class_names: list[str]) -> dict[str, Any]:
    if summary["image_count"] != len(images) or summary["detection_count"] != sum(len(image["detections"]) for image in images) or summary["per_class_counts"] != _class_counts(images):
        raise SchemaError("summary mismatch")
    return {"images": images, "class_names": class_names}


def compatible(python: dict[str, Any], cpp: dict[str, Any]) -> bool:
    return abs(python["confidence"] - cpp["confidence"]) <= CONF_TOL and max(abs(python[key] - cpp[key]) for key in ("x1", "y1", "x2", "y2")) <= BBOX_TOL


def maximum_matching(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[tuple[int, int]]:
    adjacency = [[j for j, candidate in enumerate(right) if compatible(item, candidate)] for item in left]
    matched_right: list[int | None] = [None] * len(right)

    def augment(left_index: int, visited: set[int]) -> bool:
        for right_index in adjacency[left_index]:
            if right_index in visited:
                continue
            visited.add(right_index)
            previous = matched_right[right_index]
            if previous is None or augment(previous, visited):
                matched_right[right_index] = left_index
                return True
        return False

    for left_index in range(len(left)):
        if not augment(left_index, set()):
            return []
    pairs = [(left_index, right_index) for right_index, left_index in enumerate(matched_right) if left_index is not None]
    return sorted(pairs)


def compare(python_path: Path, cpp_path: Path) -> tuple[dict[str, Any], bool]:
    python = _normalize_reference(read_json(python_path))
    cpp = _normalize_cpp(read_json(cpp_path))
    failures: list[dict[str, Any]] = []
    if not _postprocess_equal(python["postprocess"], cpp["postprocess"]):
        failures.append({"category": "schema_error", "detail": "postprocess contracts differ"})
    if len(python["images"]) != len(cpp["images"]):
        failures.append({"category": "image_count_mismatch", "detail": "image counts differ"})
    if python["class_names"] != cpp["class_names"]:
        failures.append({"category": "class_contract_mismatch", "detail": "class names differ"})
    image_results = []
    for index in range(min(len(python["images"]), len(cpp["images"]))):
        lhs, rhs = python["images"][index], cpp["images"][index]
        result = {"sequence_index": lhs["sequence_index"], "relative_path": lhs["relative_path"], "status": "PASS", "detection_count": len(lhs["detections"]), "class_results": [], "max_confidence_abs_error": 0.0, "max_bbox_coordinate_abs_error": 0.0, "matched_pairs": []}
        if (lhs["sequence_index"], lhs["relative_path"]) != (rhs["sequence_index"], rhs["relative_path"]):
            result["status"] = "FAIL"
            failures.append({"category": "image_identity_mismatch", "sequence_index": lhs["sequence_index"], "detail": "image identity differs"})
            image_results.append(result)
            continue
        if (lhs["width"], lhs["height"]) != (rhs["width"], rhs["height"]):
            result["status"] = "FAIL"
            failures.append({"category": "shape_mismatch", "sequence_index": lhs["sequence_index"], "detail": "image dimensions differ"})
            image_results.append(result)
            continue
        if len(lhs["detections"]) != len(rhs["detections"]):
            result["status"] = "FAIL"
            failures.append({"category": "detection_count_mismatch", "sequence_index": lhs["sequence_index"], "detail": "detection counts differ"})
        for class_id in range(6):
            left = [item for item in lhs["detections"] if item["class_id"] == class_id]
            right = [item for item in rhs["detections"] if item["class_id"] == class_id]
            class_result = {"class_id": class_id, "python_count": len(left), "cpp_count": len(right), "status": "PASS"}
            if len(left) != len(right):
                class_result["status"] = "FAIL"
                result["status"] = "FAIL"
                failures.append({"category": "per_class_count_mismatch", "sequence_index": lhs["sequence_index"], "class_id": class_id, "detail": "class counts differ"})
            pairs = maximum_matching(left, right) if len(left) == len(right) else []
            if len(pairs) != len(left):
                class_result["status"] = "FAIL"
                result["status"] = "FAIL"
                has_edge = any(compatible(item, candidate) for item in left for candidate in right)
                failures.append({"category": "no_compatible_edge" if not has_edge and left and right else "no_complete_matching", "sequence_index": lhs["sequence_index"], "class_id": class_id, "detail": "no complete maximum matching"})
            result["class_results"].append(class_result)
            for left_index, right_index in pairs:
                py_detection, cpp_detection = left[left_index], right[right_index]
                conf_error = abs(py_detection["confidence"] - cpp_detection["confidence"])
                bbox_error = max(abs(py_detection[key] - cpp_detection[key]) for key in ("x1", "y1", "x2", "y2"))
                result["max_confidence_abs_error"] = max(result["max_confidence_abs_error"], conf_error)
                result["max_bbox_coordinate_abs_error"] = max(result["max_bbox_coordinate_abs_error"], bbox_error)
                result["matched_pairs"].append({"python_detection_index": lhs["detections"].index(py_detection), "cpp_detection_index": rhs["detections"].index(cpp_detection), "class_id": class_id, "python_candidate_index": py_detection["candidate_index"], "cpp_candidate_index": cpp_detection["candidate_index"], "confidence_abs_error": conf_error, "bbox_max_abs_error": bbox_error})
        image_results.append(result)
    report = {"schema_version": 1, "status": "PASS" if not failures else "FAIL", "tolerances": {"confidence_abs": CONF_TOL, "bbox_coordinate_abs": BBOX_TOL}, "inputs": {"python_reference": python_path.name, "cpp_result": cpp_path.name}, "image_results": image_results, "aggregate": {"image_count": len(image_results), "passed_images": sum(item["status"] == "PASS" for item in image_results), "failed_images": sum(item["status"] == "FAIL" for item in image_results)}, "failures": failures}
    return report, not failures


def _postprocess_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    for key in ("confidence_threshold", "iou_threshold", "max_wh"):
        if abs(float(left[key]) - float(right[key])) > 1e-6:
            return False
    return all(left[key] == right[key] for key in ("max_nms", "max_det", "agnostic", "multi_label"))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare Python and C++ Level C results using maximum matching.")
    parser.add_argument("--python-reference", required=True, type=Path)
    parser.add_argument("--cpp-result", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        report, passed = compare(args.python_reference, args.cpp_result)
        atomic_write(args.output, report)
        print(f"comparison {report['status']}: {report['aggregate']['passed_images']}/{report['aggregate']['image_count']} images")
        return 0 if passed else 4
    except SystemExit as exc:
        return int(exc.code)
    except (SchemaError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
