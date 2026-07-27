#!/usr/bin/env python3
"""Stage K TensorRT Level C comparator and targeted boundary classifier.

The normal matching path reuses the frozen Stage J JSON normalizers and
maximum-matching implementation.  TensorRT v2 metadata is normalized to the
same image/detection representation, while ``candidate_index`` is retained
only in diagnostics and matching reports.
"""

from __future__ import annotations

import argparse
import importlib
import math
import sys
import types
from pathlib import Path
from typing import Any

import numpy as np


def _load_stage_j_helpers() -> Any:
    """Load Stage J's pure comparator helpers without requiring Python cv2."""
    try:
        return importlib.import_module("m5_level_c_compare")
    except ModuleNotFoundError as exc:
        if exc.name != "cv2":
            raise
        # m5_level_c_common imports cv2 for the reference runner, but the
        # comparator helpers used here do not execute any cv2 operation.
        sys.modules.setdefault("cv2", types.ModuleType("cv2"))
        return importlib.import_module("m5_level_c_compare")


STAGE_J = _load_stage_j_helpers()
from stage_k_level_b_compare import load_manifest as load_raw_manifest  # noqa: E402


CONF_TOL = 1e-2
BBOX_TOL = 1.0
THRESHOLD = 0.25
BOUNDARY_LOW = 0.245
BOUNDARY_HIGH = 0.255
MAX_BOUNDARY_CASES = 2
MAX_BOUNDARY_CASES_PER_IMAGE = 1
RAW_CHANNELS = 10
RAW_CANDIDATES = 8400
RAW_VALUES = RAW_CHANNELS * RAW_CANDIDATES
CLASS_NAMES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
POSTPROCESS = {
    "confidence_threshold": THRESHOLD,
    "iou_threshold": 0.45,
    "max_nms": 30000,
    "max_det": 300,
    "max_wh": 7680.0,
    "agnostic": False,
    "multi_label": False,
}


class SchemaError(ValueError):
    """Malformed result/reference/raw identity."""


class InvestigationRequired(RuntimeError):
    """A normal unmatched case needs targeted raw-tensor investigation."""


def _keys(value: Any, expected: list[str], where: str) -> None:
    if not isinstance(value, dict) or list(value) != expected:
        raise SchemaError(f"{where} fields/order mismatch")


def _sha(value: Any, where: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise SchemaError(f"{where} must be a lowercase SHA256")
    return value


def _normalize_tensortrt(data: Any) -> dict[str, Any]:
    _keys(data, ["schema_version", "backend", "model", "postprocess", "images", "summary"], "TensorRT result")
    if data["schema_version"] != 2 or data["backend"] != {"type": "tensorrt_fp16"}:
        raise SchemaError("TensorRT Result JSON v2 identity mismatch")
    model = data["model"]
    _keys(model, ["artifact_kind", "filename", "sha256", "source_onnx_sha256", "engine_manifest_filename", "contract_filename", "classes"], "TensorRT model")
    if model["artifact_kind"] != "tensorrt_engine" or not isinstance(model["filename"], str) or not model["filename"]:
        raise SchemaError("TensorRT model artifact identity mismatch")
    _sha(model["sha256"], "TensorRT model.sha256")
    _sha(model["source_onnx_sha256"], "TensorRT model.source_onnx_sha256")
    if not isinstance(model["engine_manifest_filename"], str) or not model["engine_manifest_filename"]:
        raise SchemaError("TensorRT engine manifest filename is invalid")
    if not isinstance(model["contract_filename"], str) or not model["contract_filename"]:
        raise SchemaError("TensorRT contract filename is invalid")
    if model["classes"] != CLASS_NAMES:
        raise SchemaError("TensorRT class contract mismatch")
    try:
        postprocess = STAGE_J._normalize_postprocess(data["postprocess"])
    except STAGE_J.SchemaError as exc:
        raise SchemaError(str(exc)) from exc
    if postprocess != POSTPROCESS:
        raise SchemaError("TensorRT postprocess contract mismatch")
    images = data["images"]
    if not isinstance(images, list):
        raise SchemaError("TensorRT images must be a list")
    try:
        normalized = [STAGE_J._normalize_image(image, f"TensorRT images[{index}]") for index, image in enumerate(images)]
    except STAGE_J.SchemaError as exc:
        raise SchemaError(str(exc)) from exc
    summary = data["summary"]
    _keys(summary, ["processed_images", "total_detections"], "TensorRT summary")
    if summary["processed_images"] != len(normalized) or summary["total_detections"] != sum(len(image["detections"]) for image in normalized):
        raise SchemaError("TensorRT summary mismatch")
    return {"images": normalized, "class_names": CLASS_NAMES, "postprocess": postprocess, "model": model}


def _normalize_python(path: Path) -> dict[str, Any]:
    try:
        normalized = STAGE_J._normalize_reference(STAGE_J.read_json(path))
    except STAGE_J.SchemaError as exc:
        raise SchemaError(str(exc)) from exc
    if normalized["postprocess"] != POSTPROCESS:
        raise SchemaError("Python reference postprocess contract mismatch")
    return normalized


def _scaled_for_stage_j(detection: dict[str, Any]) -> dict[str, Any]:
    """Map K tolerances to Stage J's fixed helper tolerances.

    Stage J uses confidence <= 1e-4 and coordinates <= .01. Scaling both
    numeric groups by a factor just below .01 makes its unchanged helper
    implement K's confidence <= 1e-2 and coordinate <= 1.0 edge without
    turning a decimal equality into a binary floating-point false negative.
    """
    value = dict(detection)
    for key in ("x1", "y1", "x2", "y2", "confidence"):
        value[key] = round(value[key] * 0.00999999, 12)
    return value


def maximum_matching(left: list[dict[str, Any]], right: list[dict[str, Any]]) -> list[tuple[int, int]]:
    return STAGE_J.maximum_matching([_scaled_for_stage_j(item) for item in left], [_scaled_for_stage_j(item) for item in right])


def _bbox_errors(left: dict[str, Any], right: dict[str, Any]) -> dict[str, float]:
    return {key: abs(float(left[key]) - float(right[key])) for key in ("x1", "y1", "x2", "y2")}


def _iou(left: dict[str, Any], right: dict[str, Any]) -> float:
    lx1, ly1, lx2, ly2 = (float(left[key]) for key in ("x1", "y1", "x2", "y2"))
    rx1, ry1, rx2, ry2 = (float(right[key]) for key in ("x1", "y1", "x2", "y2"))
    intersection = max(0.0, min(lx2, rx2) - max(lx1, rx1)) * max(0.0, min(ly2, ry2) - max(ly1, ry1))
    union = max(0.0, lx2 - lx1) * max(0.0, ly2 - ly1) + max(0.0, rx2 - rx1) * max(0.0, ry2 - ry1) - intersection
    return intersection / union if union > 0.0 else 0.0


def _matching_report(python: dict[str, Any], tensorrt: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    if len(python["images"]) != len(tensorrt["images"]):
        failures.append({"category": "image_count_mismatch"})
    image_results: list[dict[str, Any]] = []
    for index in range(min(len(python["images"]), len(tensorrt["images"]))):
        lhs, rhs = python["images"][index], tensorrt["images"][index]
        result: dict[str, Any] = {
            "sequence_index": lhs["sequence_index"], "relative_path": lhs["relative_path"],
            "status": "PASS", "python_detection_count": len(lhs["detections"]),
            "tensorrt_detection_count": len(rhs["detections"]), "matched_count": 0,
            "unmatched_python": [], "unmatched_tensorrt": [], "matched_detections": [],
            "max_confidence_abs_error": 0.0, "max_bbox_coordinate_abs_error": 0.0,
        }
        if (lhs["sequence_index"], lhs["relative_path"], lhs["width"], lhs["height"]) != (rhs["sequence_index"], rhs["relative_path"], rhs["width"], rhs["height"]):
            result["status"] = "FAIL"
            failures.append({"category": "image_identity_mismatch", "sequence_index": lhs["sequence_index"]})
            image_results.append(result)
            continue
        for class_id in range(6):
            left = [item for item in lhs["detections"] if item["class_id"] == class_id]
            right = [item for item in rhs["detections"] if item["class_id"] == class_id]
            pairs = maximum_matching(left, right)
            left_matched, right_matched = set(), set()
            for left_index, right_index in pairs:
                left_matched.add(left_index); right_matched.add(right_index)
                py, trt = left[left_index], right[right_index]
                bbox = _bbox_errors(py, trt)
                confidence_error = abs(float(py["confidence"]) - float(trt["confidence"]))
                result["matched_detections"].append({
                    "image_id": lhs["relative_path"], "python_candidate_index": py["candidate_index"],
                    "tensorrt_candidate_index": trt["candidate_index"], "class_id": class_id,
                    "confidence_abs_error": confidence_error, "bbox_coordinate_abs_error": bbox,
                    "iou": _iou(py, trt), "pass": confidence_error <= CONF_TOL and max(bbox.values()) <= BBOX_TOL,
                })
                result["max_confidence_abs_error"] = max(result["max_confidence_abs_error"], confidence_error)
                result["max_bbox_coordinate_abs_error"] = max(result["max_bbox_coordinate_abs_error"], max(bbox.values()))
            for item_index, item in enumerate(left):
                if item_index not in left_matched: result["unmatched_python"].append(item)
            for item_index, item in enumerate(right):
                if item_index not in right_matched: result["unmatched_tensorrt"].append(item)
        result["matched_count"] = len(result["matched_detections"])
        if result["unmatched_python"] or result["unmatched_tensorrt"]:
            result["status"] = "INVESTIGATION_REQUIRED"
            failures.append({"category": "unmatched_detection", "sequence_index": lhs["sequence_index"]})
        image_results.append(result)
    unmatched = sum(len(item["unmatched_python"]) + len(item["unmatched_tensorrt"]) for item in image_results)
    return {
        "schema_version": 1, "status": "INVESTIGATION_REQUIRED" if unmatched else ("FAIL" if failures else "PASS"),
        "tolerances": {"confidence_abs": CONF_TOL, "bbox_coordinate_abs": BBOX_TOL},
        "inputs": {"python_reference": "", "tensorrt_result": ""}, "image_results": image_results,
        "aggregate": {"image_count": len(image_results), "python_detections": sum(len(i["detections"]) for i in python["images"]), "tensorrt_detections": sum(len(i["detections"]) for i in tensorrt["images"]), "matched": sum(i["matched_count"] for i in image_results), "unmatched": unmatched},
        "failures": failures,
    }


def _raw_candidate(entry: dict[str, Any], candidate_index: int) -> dict[str, Any]:
    values = entry["_values"]
    if values.size != RAW_VALUES or not np.isfinite(values).all() or not 0 <= candidate_index < RAW_CANDIDATES:
        raise SchemaError("raw candidate tensor contract failure")
    components = [float(values[channel * RAW_CANDIDATES + candidate_index]) for channel in range(4)]
    scores = [float(values[(4 + class_id) * RAW_CANDIDATES + candidate_index]) for class_id in range(6)]
    class_id = max(range(6), key=lambda item: (scores[item], -item))
    return {"cx": components[0], "cy": components[1], "w": components[2], "h": components[3], "class_scores": scores, "argmax_class": class_id, "confidence": scores[class_id], "candidate_index": candidate_index}


def _python_round(value: float) -> int:
    lower = math.floor(value)
    fraction = value - lower
    return int(lower + (1 if fraction > 0.5 or (fraction == 0.5 and lower % 2 != 0) else 0))


def _letterbox_geometry(width: int, height: int) -> tuple[float, int, int]:
    gain = min(640.0 / width, 640.0 / height)
    resized_width = _python_round(width * gain)
    resized_height = _python_round(height * gain)
    return gain, _python_round((640 - resized_width) / 2.0 - 0.1), _python_round((640 - resized_height) / 2.0 - 0.1)


def _restore(raw: dict[str, Any], width: int, height: int) -> dict[str, float]:
    gain, pad_left, pad_top = _letterbox_geometry(width, height)
    values = {"x1": raw["cx"] - raw["w"] / 2.0, "y1": raw["cy"] - raw["h"] / 2.0, "x2": raw["cx"] + raw["w"] / 2.0, "y2": raw["cy"] + raw["h"] / 2.0}
    return {key: min(max((value - (pad_left if key in ("x1", "x2") else pad_top)) / gain, 0.0), float(width if key in ("x1", "x2") else height)) for key, value in values.items()}


def _unclipped_restore(raw: dict[str, Any], width: int, height: int) -> dict[str, float]:
    gain, pad_left, pad_top = _letterbox_geometry(width, height)
    return {
        "x1": (raw["cx"] - raw["w"] / 2.0 - pad_left) / gain,
        "y1": (raw["cy"] - raw["h"] / 2.0 - pad_top) / gain,
        "x2": (raw["cx"] + raw["w"] / 2.0 - pad_left) / gain,
        "y2": (raw["cy"] + raw["h"] / 2.0 - pad_top) / gain,
    }


def _find_raw(entries: list[dict[str, Any]], image_id: str) -> dict[str, Any]:
    for entry in entries:
        if entry["image_id"] == image_id:
            return entry
    raise SchemaError(f"raw manifest has no image_id: {image_id}")


def _boundary_case(image: dict[str, Any], tensorrt_image: dict[str, Any], raw_python: dict[str, Any], raw_tensorrt: dict[str, Any], unmatched: dict[str, Any], side: str) -> tuple[dict[str, Any] | None, str]:
    candidate_index = unmatched["candidate_index"]
    py = _raw_candidate(raw_python, candidate_index)
    trt = _raw_candidate(raw_tensorrt, candidate_index)
    py_box, trt_box = _restore(py, image["width"], image["height"]), _restore(trt, image["width"], image["height"])
    py_unclipped, trt_unclipped = _unclipped_restore(py, image["width"], image["height"]), _unclipped_restore(trt, image["width"], image["height"])
    reasons: list[str] = []
    python_presence = [item for item in image["detections"] if item["candidate_index"] == candidate_index]
    tensorrt_presence = [item for item in tensorrt_image["detections"] if item["candidate_index"] == candidate_index]
    if (side == "python") != bool(python_presence) or (side == "tensorrt") != bool(tensorrt_presence):
        reasons.append("final_presence_identity")
    other_presence = tensorrt_presence if side == "python" else python_presence
    if other_presence:
        reasons.append("same_candidate_present_on_both_sides")
    if py["argmax_class"] != trt["argmax_class"]: reasons.append("class_change")
    if not (BOUNDARY_LOW <= py["confidence"] <= BOUNDARY_HIGH and BOUNDARY_LOW <= trt["confidence"] <= BOUNDARY_HIGH): reasons.append("outside_boundary_band")
    if not ((py["confidence"] > THRESHOLD) != (trt["confidence"] > THRESHOLD)): reasons.append("threshold_decision_not_crossed")
    if abs(py["confidence"] - trt["confidence"]) > CONF_TOL: reasons.append("confidence_error")
    if any(abs(py[key] - trt[key]) > 1.0 for key in ("cx", "cy", "w", "h")): reasons.append("raw_bbox_error")
    if any(abs(py_box[key] - trt_box[key]) > BBOX_TOL for key in py_box): reasons.append("restored_bbox_error")
    if any(value < 0.0 or value > float(limit) for box, limit in ((py_unclipped, image["width"]), (trt_unclipped, image["width"])) for key, value in box.items() if key in ("x1", "x2")) or any(value < 0.0 or value > float(limit) for box, limit in ((py_unclipped, image["height"]), (trt_unclipped, image["height"])) for key, value in box.items() if key in ("y1", "y2")):
        reasons.append("clipping_induced_disappearance")
    if py["w"] <= 0 or py["h"] <= 0 or trt["w"] <= 0 or trt["h"] <= 0: reasons.append("invalid_bbox")
    present = python_presence[0] if side == "python" and python_presence else tensorrt_presence[0] if side == "tensorrt" and tensorrt_presence else None
    if present is not None:
        if present["class_id"] != py["argmax_class"] if side == "python" else present["class_id"] != trt["argmax_class"]:
            reasons.append("final_class_identity")
        present_raw = py if side == "python" else trt
        present_box = py_box if side == "python" else trt_box
        if abs(float(present["confidence"]) - present_raw["confidence"]) > CONF_TOL or any(abs(float(present[key]) - present_box[key]) > BBOX_TOL for key in ("x1", "y1", "x2", "y2")):
            reasons.append("final_raw_identity")
    if reasons: return None, ";".join(reasons)
    return {
        "image_id": image["relative_path"], "candidate_index": candidate_index,
        "python_raw_cx_cy_w_h": [py[key] for key in ("cx", "cy", "w", "h")],
        "tensorrt_raw_cx_cy_w_h": [trt[key] for key in ("cx", "cy", "w", "h")],
        "python_class_scores": py["class_scores"], "tensorrt_class_scores": trt["class_scores"],
        "python_argmax_class": py["argmax_class"], "tensorrt_argmax_class": trt["argmax_class"],
        "python_confidence": py["confidence"], "tensorrt_confidence": trt["confidence"],
        "threshold_decision": {"python_pass": py["confidence"] > THRESHOLD, "tensorrt_pass": trt["confidence"] > THRESHOLD},
        "python_restored_bbox": py_box, "tensorrt_restored_bbox": trt_box,
        "final_presence": {"python": side == "python", "tensorrt": side == "tensorrt"},
        "classification_reason": "threshold_boundary_variation",
    }, ""


def classify_boundaries(python: dict[str, Any], tensorrt: dict[str, Any], report: dict[str, Any], python_manifest: Path, tensorrt_manifest: Path) -> dict[str, Any]:
    _, python_raw = load_raw_manifest(python_manifest)
    _, tensorrt_raw = load_raw_manifest(tensorrt_manifest)
    expected_ids = [image["relative_path"].split(".", 1)[0] for image in python["images"]]
    python_ids, tensorrt_ids = [entry["image_id"] for entry in python_raw], [entry["image_id"] for entry in tensorrt_raw]
    if python_ids != expected_ids or tensorrt_ids != expected_ids or python_ids != tensorrt_ids:
        raise SchemaError("raw manifest image identity/order mismatch")
    if [entry["input_filename"] for entry in python_raw] != [entry["input_filename"] for entry in tensorrt_raw] or [entry["input_sha256"] for entry in python_raw] != [entry["input_sha256"] for entry in tensorrt_raw]:
        raise SchemaError("raw manifest input identity mismatch")
    cases: list[dict[str, Any]] = []
    failures: list[str] = []
    for result, image in zip(report["image_results"], python["images"]):
        py_unmatched, trt_unmatched = result["unmatched_python"], result["unmatched_tensorrt"]
        if not py_unmatched and not trt_unmatched: continue
        if len(py_unmatched) == 0 or len(trt_unmatched) != 0 or len(py_unmatched) != 1:
            # The symmetric case is allowed below; replacements remain failures.
            if len(trt_unmatched) != 1 or len(py_unmatched) != 0:
                failures.append(f"{image['relative_path']}: candidate replacement or count divergence")
                continue
            unmatched, side = trt_unmatched[0], "tensorrt"
        else:
            unmatched, side = py_unmatched[0], "python"
        tensorrt_image = next(item for item in tensorrt["images"] if item["sequence_index"] == image["sequence_index"])
        py_raw = _find_raw(python_raw, image["relative_path"].split(".", 1)[0])
        trt_raw = _find_raw(tensorrt_raw, image["relative_path"].split(".", 1)[0])
        candidate, reason = _boundary_case(image, tensorrt_image, py_raw, trt_raw, unmatched, side)
        if candidate is None:
            failures.append(f"{image['relative_path']}: {reason}")
        else:
            cases.append(candidate)
    by_image: dict[str, int] = {}
    for case in cases: by_image[case["image_id"]] = by_image.get(case["image_id"], 0) + 1
    if len(cases) > MAX_BOUNDARY_CASES: failures.append("corpus boundary case limit exceeded")
    if any(count > MAX_BOUNDARY_CASES_PER_IMAGE for count in by_image.values()): failures.append("per-image boundary case limit exceeded")
    if len(cases) != report["aggregate"]["unmatched"]: failures.append("detection-count difference does not equal boundary case count")
    return {"status": "PASS_WITH_REPORTED_NUMERICAL_BOUNDARY_VARIATION" if cases and not failures else ("PASS" if not cases and not failures else "FAIL"), "boundary_case_count": len(cases), "per_image_case_count": by_image, "cases": cases, "unexplained_divergence_count": len(failures), "failures": failures}


def compare(python_path: Path, tensorrt_path: Path, python_manifest: Path | None = None, tensorrt_manifest: Path | None = None) -> tuple[dict[str, Any], bool]:
    python = _normalize_python(python_path)
    tensorrt = _normalize_tensortrt(STAGE_J.read_json(tensorrt_path))
    report = _matching_report(python, tensorrt)
    report["inputs"] = {"python_reference": python_path.name, "tensorrt_result": tensorrt_path.name}
    if report["status"] == "PASS":
        report["boundary"] = {"status": "NOT_TRIGGERED", "boundary_case_count": 0, "unexplained_divergence_count": 0}
        return report, True
    if report["status"] != "INVESTIGATION_REQUIRED":
        return report, False
    if python_manifest is None or tensorrt_manifest is None:
        report["boundary"] = {"status": "INVESTIGATION_REQUIRED", "boundary_case_count": 0, "unexplained_divergence_count": report["aggregate"]["unmatched"]}
        return report, False
    boundary = classify_boundaries(python, tensorrt, report, python_manifest, tensorrt_manifest)
    report["boundary"] = boundary
    report["status"] = boundary["status"]
    return report, report["status"] in {"PASS", "PASS_WITH_REPORTED_NUMERICAL_BOUNDARY_VARIATION"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare Python ORT final detections with TensorRT Result JSON v2.")
    parser.add_argument("--python-reference", required=True, type=Path)
    parser.add_argument("--tensorrt-result", required=True, type=Path)
    parser.add_argument("--python-raw-manifest", type=Path)
    parser.add_argument("--tensorrt-raw-manifest", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        report, passed = compare(args.python_reference, args.tensorrt_result, args.python_raw_manifest, args.tensorrt_raw_manifest)
        STAGE_J.atomic_write(args.output, report)
        print(f"stage_k_level_c_compare: {report['status']}")
        return 0 if passed else 4
    except (SchemaError, STAGE_J.SchemaError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
