#!/usr/bin/env python3
"""Compare frozen PyTorch and ONNX models on deterministic validation images."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PT_MODEL = Path("models/pytorch/yolov8n_neudet_frozen.pt")
DEFAULT_ONNX_MODEL = Path("models/onnx/yolov8n_neudet_frozen.onnx")
DEFAULT_IMAGES_DIR = Path("data/yolo/neu_det/images/val")
DEFAULT_OUTPUT_PATH = Path("results/onnx_export/pt_onnx_compare.json")
IMAGE_SUFFIXES = {".bmp", ".jpeg", ".jpg", ".png"}

IMAGE_COUNT = 10
IMAGE_SIZE = 640
CONFIDENCE_THRESHOLD = 0.25
IOU_THRESHOLD = 0.45
RAW_MAE_TOLERANCE = 1e-4
RAW_MAX_ABS_ERROR_TOLERANCE = 1e-2
BBOX_MAX_ABS_ERROR_TOLERANCE = 1e-2
CONFIDENCE_MAX_ABS_ERROR_TOLERANCE = 1e-4


class ComparisonError(RuntimeError):
    """Raised when comparison setup or execution cannot be completed."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare frozen PyTorch and ONNX Runtime outputs on validation images."
    )
    parser.add_argument("--pt-model", type=Path, default=DEFAULT_PT_MODEL)
    parser.add_argument("--onnx-model", type=Path, default=DEFAULT_ONNX_MODEL)
    parser.add_argument("--images-dir", type=Path, default=DEFAULT_IMAGES_DIR)
    parser.add_argument("--image-count", type=int, default=IMAGE_COUNT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
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


def select_images(images_dir: Path, count: int) -> list[Path]:
    if count <= 0:
        raise ValueError(f"image-count must be positive, got {count}")
    candidates = sorted(
        path
        for path in images_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if len(candidates) < count:
        raise ComparisonError(
            f"Need {count} validation images, found {len(candidates)} in {images_dir}"
        )
    if count == 1:
        return [candidates[0]]
    indices = [round(index * (len(candidates) - 1) / (count - 1)) for index in range(count)]
    return [candidates[index] for index in indices]


def preprocess_image(image: np.ndarray[Any, Any], letterbox: Any) -> np.ndarray[Any, Any]:
    letterboxed = letterbox(image=image)
    rgb_chw = letterboxed[:, :, ::-1].transpose(2, 0, 1)
    batch = np.ascontiguousarray(rgb_chw[None], dtype=np.float32) / 255.0
    expected_shape = (1, 3, IMAGE_SIZE, IMAGE_SIZE)
    if batch.shape != expected_shape:
        raise ComparisonError(
            f"Preprocessed input shape is {batch.shape}, expected {expected_shape}"
        )
    return batch


def extract_pt_output(result: Any, torch_module: Any) -> np.ndarray[Any, Any]:
    output = result[0] if isinstance(result, (tuple, list)) else result
    if not isinstance(output, torch_module.Tensor):
        raise ComparisonError(f"Unexpected PyTorch output type: {type(output).__name__}")
    return output.detach().cpu().numpy()


def raw_output_comparison(
    pytorch_output: np.ndarray[Any, Any], onnx_output: np.ndarray[Any, Any]
) -> dict[str, Any]:
    if pytorch_output.shape != onnx_output.shape:
        raise ComparisonError(
            f"Raw output shape mismatch: PyTorch {pytorch_output.shape}, ONNX {onnx_output.shape}"
        )
    difference = np.abs(
        pytorch_output.astype(np.float64) - onnx_output.astype(np.float64)
    )
    return {
        "pytorch": {
            "shape": list(pytorch_output.shape),
            "mean": float(pytorch_output.mean()),
            "max": float(pytorch_output.max()),
        },
        "onnx": {
            "shape": list(onnx_output.shape),
            "mean": float(onnx_output.mean()),
            "max": float(onnx_output.max()),
        },
        "mae": float(difference.mean()),
        "max_absolute_error": float(difference.max()),
        "element_count": int(difference.size),
        "absolute_error_sum": float(difference.sum()),
    }


def class_names(model_names: Any) -> dict[int, str]:
    if isinstance(model_names, dict):
        return {int(class_id): str(name) for class_id, name in model_names.items()}
    return {class_id: str(name) for class_id, name in enumerate(model_names)}


def detection_records(
    raw_output: np.ndarray[Any, Any],
    original_shape: tuple[int, int],
    names: dict[int, str],
    torch_module: Any,
    non_max_suppression: Any,
    scale_boxes: Any,
) -> list[dict[str, Any]]:
    prediction = torch_module.from_numpy(np.ascontiguousarray(raw_output))
    detections = non_max_suppression(
        prediction,
        conf_thres=CONFIDENCE_THRESHOLD,
        iou_thres=IOU_THRESHOLD,
        max_det=300,
        nc=len(names),
        max_time_img=10.0,
    )[0]
    if detections.numel() == 0:
        return []
    detections = detections.detach().cpu().clone()
    detections[:, :4] = scale_boxes(
        (IMAGE_SIZE, IMAGE_SIZE), detections[:, :4], original_shape
    )
    records = []
    for row in detections:
        class_id = int(row[5].item())
        records.append(
            {
                "class_id": class_id,
                "class_name": names.get(class_id, f"class_{class_id}"),
                "confidence": float(row[4].item()),
                "bbox_xyxy": [float(value) for value in row[:4].tolist()],
            }
        )
    records.sort(key=lambda record: (-record["confidence"], record["class_id"]))
    return records


def compare_detections(
    pytorch_detections: list[dict[str, Any]],
    onnx_detections: list[dict[str, Any]],
) -> dict[str, Any]:
    counts_equal = len(pytorch_detections) == len(onnx_detections)
    pytorch_classes = Counter(record["class_id"] for record in pytorch_detections)
    onnx_classes = Counter(record["class_id"] for record in onnx_detections)
    classes_equal = pytorch_classes == onnx_classes
    unmatched_onnx = list(onnx_detections)
    matched_errors = []

    if counts_equal and classes_equal:
        for pytorch_detection in pytorch_detections:
            candidates = [
                (index, detection)
                for index, detection in enumerate(unmatched_onnx)
                if detection["class_id"] == pytorch_detection["class_id"]
            ]
            match_index, match = min(
                candidates,
                key=lambda item: max(
                    abs(left - right)
                    for left, right in zip(
                        pytorch_detection["bbox_xyxy"], item[1]["bbox_xyxy"], strict=True
                    )
                ),
            )
            unmatched_onnx.pop(match_index)
            matched_errors.append(
                {
                    "class_id": pytorch_detection["class_id"],
                    "confidence_absolute_error": abs(
                        pytorch_detection["confidence"] - match["confidence"]
                    ),
                    "bbox_max_absolute_error": max(
                        abs(left - right)
                        for left, right in zip(
                            pytorch_detection["bbox_xyxy"], match["bbox_xyxy"], strict=True
                        )
                    ),
                }
            )

    max_confidence_error = max(
        (match["confidence_absolute_error"] for match in matched_errors), default=0.0
    )
    max_bbox_error = max(
        (match["bbox_max_absolute_error"] for match in matched_errors), default=0.0
    )
    comparison_pass = (
        counts_equal
        and classes_equal
        and max_confidence_error <= CONFIDENCE_MAX_ABS_ERROR_TOLERANCE
        and max_bbox_error <= BBOX_MAX_ABS_ERROR_TOLERANCE
    )
    return {
        "counts_equal": counts_equal,
        "classes_equal": classes_equal,
        "max_confidence_absolute_error": max_confidence_error,
        "max_bbox_absolute_error": max_bbox_error,
        "comparison_pass": comparison_pass,
        "matched_errors": matched_errors,
    }


def write_json(path: Path, evidence: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    os.replace(temporary_path, path)


def validate_file(path: Path, description: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"{description} not found: {path}")
    if path.stat().st_size == 0:
        raise ComparisonError(f"{description} is empty: {path}")


def run_comparison(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import cv2
        import onnxruntime as ort
        import torch
        import ultralytics
        from ultralytics import YOLO
        from ultralytics.data.augment import LetterBox
        from ultralytics.utils.nms import non_max_suppression
        from ultralytics.utils.ops import scale_boxes
    except ImportError as exc:
        raise ComparisonError(
            f"Missing comparison dependency '{exc.name}'. Install project requirements first."
        ) from exc

    pt_model_path = resolve_repo_path(args.pt_model)
    onnx_model_path = resolve_repo_path(args.onnx_model)
    images_dir = resolve_repo_path(args.images_dir)
    output_path = resolve_repo_path(args.output)
    validate_file(pt_model_path, "PyTorch model")
    validate_file(onnx_model_path, "ONNX model")
    if not images_dir.is_dir():
        raise FileNotFoundError(f"Validation images directory not found: {images_dir}")
    selected_images = select_images(images_dir, args.image_count)

    yolo = YOLO(str(pt_model_path))
    pytorch_model = yolo.model.to("cpu").float().eval()
    names = class_names(yolo.names)
    session = ort.InferenceSession(
        str(onnx_model_path), providers=["CPUExecutionProvider"]
    )
    onnx_inputs = session.get_inputs()
    onnx_outputs = session.get_outputs()
    if len(onnx_inputs) != 1 or len(onnx_outputs) != 1:
        raise ComparisonError(
            f"Expected one ONNX input and output, got {len(onnx_inputs)} and {len(onnx_outputs)}"
        )
    input_info = onnx_inputs[0]
    if input_info.shape != [1, 3, IMAGE_SIZE, IMAGE_SIZE] or input_info.type != "tensor(float)":
        raise ComparisonError(
            f"Expected ONNX input float32 [1, 3, {IMAGE_SIZE}, {IMAGE_SIZE}], "
            f"got {input_info.type} {input_info.shape}"
        )

    letterbox = LetterBox(new_shape=(IMAGE_SIZE, IMAGE_SIZE), auto=False, stride=32)
    image_results = []
    total_absolute_error = 0.0
    total_elements = 0
    overall_raw_max_error = 0.0
    overall_bbox_max_error = 0.0
    overall_confidence_max_error = 0.0

    for image_path in selected_images:
        image = cv2.imread(str(image_path))
        if image is None:
            raise ComparisonError(f"Failed to read validation image: {image_path}")
        batch = preprocess_image(image, letterbox)
        with torch.no_grad():
            pytorch_result = pytorch_model(torch.from_numpy(batch))
        pytorch_output = extract_pt_output(pytorch_result, torch)
        onnx_output = session.run(None, {input_info.name: batch})[0]
        raw_comparison = raw_output_comparison(pytorch_output, onnx_output)

        pytorch_detections = detection_records(
            pytorch_output,
            image.shape[:2],
            names,
            torch,
            non_max_suppression,
            scale_boxes,
        )
        onnx_detections = detection_records(
            onnx_output,
            image.shape[:2],
            names,
            torch,
            non_max_suppression,
            scale_boxes,
        )
        detection_comparison = compare_detections(pytorch_detections, onnx_detections)
        raw_pass = (
            raw_comparison["mae"] <= RAW_MAE_TOLERANCE
            and raw_comparison["max_absolute_error"] <= RAW_MAX_ABS_ERROR_TOLERANCE
        )
        image_pass = raw_pass and detection_comparison["comparison_pass"]
        image_results.append(
            {
                "image_path": display_path(image_path),
                "original_shape": list(image.shape),
                "raw_output": raw_comparison,
                "detections": {
                    "pytorch": {
                        "count": len(pytorch_detections),
                        "items": pytorch_detections,
                    },
                    "onnx": {
                        "count": len(onnx_detections),
                        "items": onnx_detections,
                    },
                    "comparison": detection_comparison,
                },
                "raw_output_pass": raw_pass,
                "image_pass": image_pass,
            }
        )
        total_absolute_error += raw_comparison["absolute_error_sum"]
        total_elements += raw_comparison["element_count"]
        overall_raw_max_error = max(
            overall_raw_max_error, raw_comparison["max_absolute_error"]
        )
        overall_bbox_max_error = max(
            overall_bbox_max_error,
            detection_comparison["max_bbox_absolute_error"],
        )
        overall_confidence_max_error = max(
            overall_confidence_max_error,
            detection_comparison["max_confidence_absolute_error"],
        )

    overall_raw_mae = total_absolute_error / total_elements
    raw_output_pass = (
        overall_raw_mae <= RAW_MAE_TOLERANCE
        and overall_raw_max_error <= RAW_MAX_ABS_ERROR_TOLERANCE
    )
    detection_pass = all(
        result["detections"]["comparison"]["comparison_pass"]
        for result in image_results
    )
    consistency_pass = raw_output_pass and detection_pass
    evidence = {
        "timestamp": timestamp(),
        "pytorch_model_path": display_path(pt_model_path),
        "pytorch_model_sha256": sha256_file(pt_model_path),
        "onnx_model_path": display_path(onnx_model_path),
        "onnx_model_sha256": sha256_file(onnx_model_path),
        "versions": {
            "torch": torch.__version__,
            "ultralytics": ultralytics.__version__,
            "onnxruntime": ort.__version__,
        },
        "preprocess": {
            "shared_input": True,
            "image_size": [IMAGE_SIZE, IMAGE_SIZE],
            "letterbox_auto": False,
            "letterbox_stride": 32,
            "color_conversion": "BGR to RGB",
            "layout_conversion": "HWC to CHW",
            "dtype": "float32",
            "normalization": "divide by 255.0",
        },
        "postprocess": {
            "shared_nms": True,
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "iou_threshold": IOU_THRESHOLD,
            "bbox_format": "xyxy in original image coordinates",
        },
        "selection": {
            "strategy": "evenly spaced over sorted validation image paths",
            "available_image_count": len(
                [
                    path
                    for path in images_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
                ]
            ),
            "selected_image_count": len(selected_images),
            "images": [display_path(path) for path in selected_images],
        },
        "tolerances": {
            "raw_mae": RAW_MAE_TOLERANCE,
            "raw_max_absolute_error": RAW_MAX_ABS_ERROR_TOLERANCE,
            "bbox_max_absolute_error": BBOX_MAX_ABS_ERROR_TOLERANCE,
            "confidence_max_absolute_error": CONFIDENCE_MAX_ABS_ERROR_TOLERANCE,
            "detection_counts_must_match": True,
            "detection_classes_must_match": True,
        },
        "summary": {
            "raw_output_mae": overall_raw_mae,
            "raw_output_max_absolute_error": overall_raw_max_error,
            "detection_max_bbox_absolute_error": overall_bbox_max_error,
            "detection_max_confidence_absolute_error": overall_confidence_max_error,
            "all_detection_counts_equal": all(
                result["detections"]["comparison"]["counts_equal"]
                for result in image_results
            ),
            "all_detection_classes_equal": all(
                result["detections"]["comparison"]["classes_equal"]
                for result in image_results
            ),
            "raw_output_pass": raw_output_pass,
            "detection_pass": detection_pass,
            "consistency_pass": consistency_pass,
        },
        "images": image_results,
    }
    write_json(output_path, evidence)
    print(f"Compared images: {len(selected_images)}")
    print(f"Raw output MAE: {overall_raw_mae:.10g}")
    print(f"Raw output max absolute error: {overall_raw_max_error:.10g}")
    print(f"Detection max bbox absolute error: {overall_bbox_max_error:.10g}")
    print(f"Detection max confidence absolute error: {overall_confidence_max_error:.10g}")
    print(f"Consistency: {'PASS' if consistency_pass else 'FAIL'}")
    print(f"Evidence: {display_path(output_path)}")
    return evidence


def main() -> int:
    args = parse_args()
    try:
        evidence = run_comparison(args)
        return 0 if evidence["summary"]["consistency_pass"] else 1
    except (ComparisonError, FileNotFoundError, OSError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
