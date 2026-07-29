#!/usr/bin/env python3
"""Evaluate three Stage K detection artifacts against converted NEU-DET GT.

This intentionally reports itself as a project-local evaluator.  It follows
the frozen task contract and uses class-aware one-to-one matching plus a
101-point interpolated precision-envelope AP calculation.  It does not claim
bitwise identity with Ultralytics or any other external evaluator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]
IOU_THRESHOLDS = [round(0.50 + 0.05 * index, 2) for index in range(10)]
MAX_DET = 300


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def iou(left: list[float], right: list[float]) -> float:
    x1 = max(left[0], right[0])
    y1 = max(left[1], right[1])
    x2 = min(left[2], right[2])
    y2 = min(left[3], right[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    left_area = max(0.0, left[2] - left[0]) * max(0.0, left[3] - left[1])
    right_area = max(0.0, right[2] - right[0]) * max(0.0, right[3] - right[1])
    union = left_area + right_area - intersection
    return intersection / union if union > 0.0 else 0.0


def load_ground_truth(path: Path) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    artifact = json.loads(path.read_text())
    if artifact.get("split") != "test" or artifact.get("image_count") != 180:
        raise ValueError("ground truth is not the frozen 180-image test split")
    if artifact.get("class_names") != CLASS_NAMES:
        raise ValueError("ground-truth class mapping is not frozen NEU-DET order")
    by_image: dict[str, list[dict[str, Any]]] = {}
    for image in artifact["images"]:
        image_id = str(image["image_id"])
        if image_id in by_image:
            raise ValueError(f"duplicate GT image_id: {image_id}")
        objects = []
        for obj in image.get("objects", []):
            bbox = [float(value) for value in obj["bbox_xyxy"]]
            if len(bbox) != 4 or not all(finite(value) for value in bbox):
                raise ValueError(f"invalid GT bbox in {image_id}")
            if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                raise ValueError(f"non-positive GT bbox in {image_id}")
            class_id = int(obj["class_id"])
            if class_id < 0 or class_id >= len(CLASS_NAMES):
                raise ValueError(f"invalid GT class in {image_id}")
            objects.append({"class_id": class_id, "bbox_xyxy": bbox})
        by_image[image_id] = objects
    if len(by_image) != 180:
        raise ValueError("ground truth image container count is not 180")
    return artifact, by_image


def load_predictions(path: Path, gt_artifact: dict[str, Any]) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    artifact = json.loads(path.read_text())
    if artifact.get("image_count") != 180 or artifact.get("split") != "test":
        raise ValueError(f"prediction artifact is not a 180-image test result: {path}")
    expected = {str(image["image_id"]): image for image in gt_artifact["images"]}
    predictions: dict[str, list[dict[str, Any]]] = {}
    for image in artifact["images"]:
        image_id = str(image["image_id"])
        if image_id not in expected or image_id in predictions:
            raise ValueError(f"prediction image identity mismatch: {image_id}")
        if image.get("image_sha256") != expected[image_id].get("image_sha256"):
            raise ValueError(f"prediction image SHA mismatch: {image_id}")
        detections = []
        if len(image.get("detections", [])) > MAX_DET:
            raise ValueError(f"max_det exceeded in {image_id}")
        for detection in image.get("detections", []):
            confidence = float(detection["confidence"])
            bbox = [float(value) for value in detection["bbox_xyxy"]]
            class_id = int(detection["class_id"])
            if not finite(confidence) or len(bbox) != 4 or not all(finite(value) for value in bbox):
                raise ValueError(f"NaN/Inf in prediction artifact: {image_id}")
            if class_id < 0 or class_id >= len(CLASS_NAMES):
                raise ValueError(f"invalid prediction class in {image_id}")
            if bbox[2] <= bbox[0] or bbox[3] <= bbox[1]:
                raise ValueError(f"non-positive prediction bbox in {image_id}")
            detections.append({
                "class_id": class_id,
                "confidence": confidence,
                "bbox_xyxy": bbox,
            })
        predictions[image_id] = detections
    if set(predictions) != set(expected):
        raise ValueError(f"prediction image set mismatch: {path}")
    return artifact, predictions


def prediction_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    bbox = item["prediction"]["bbox_xyxy"]
    return (
        -float(item["prediction"]["confidence"]),
        str(item["image_id"]),
        int(item["prediction"]["class_id"]),
        *bbox,
    )


def evaluate_predictions(
    predictions_by_image: dict[str, list[dict[str, Any]]],
    gt_by_image: dict[str, list[dict[str, Any]]],
    iou_threshold: float,
    class_id: int | None = None,
) -> dict[str, Any]:
    all_gt = [
        (image_id, index, target)
        for image_id, targets in gt_by_image.items()
        for index, target in enumerate(targets)
        if class_id is None or target["class_id"] == class_id
    ]
    gt_count = len(all_gt)
    predictions = [
        {"image_id": image_id, "prediction": prediction}
        for image_id, detections in predictions_by_image.items()
        for prediction in detections
        if class_id is None or prediction["class_id"] == class_id
    ]
    predictions.sort(key=prediction_sort_key)
    used: dict[str, set[int]] = {image_id: set() for image_id in gt_by_image}
    tp_flags: list[int] = []
    fp_flags: list[int] = []
    matched_iou: list[float] = []
    for item in predictions:
        image_id = item["image_id"]
        prediction = item["prediction"]
        candidates = []
        for index, target in enumerate(gt_by_image[image_id]):
            if index in used[image_id]:
                continue
            if class_id is not None and target["class_id"] != class_id:
                continue
            if class_id is None and target["class_id"] != prediction["class_id"]:
                continue
            overlap = iou(prediction["bbox_xyxy"], target["bbox_xyxy"])
            candidates.append((overlap, index, target))
        best = max(candidates, key=lambda value: (value[0], -value[1]), default=None)
        if best is not None and best[0] >= iou_threshold:
            used[image_id].add(best[1])
            tp_flags.append(1)
            fp_flags.append(0)
            matched_iou.append(best[0])
        else:
            tp_flags.append(0)
            fp_flags.append(1)

    tp = sum(tp_flags)
    fp = sum(fp_flags)
    fn = gt_count - tp
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / gt_count if gt_count else 0.0
    cumulative_tp = 0
    cumulative_fp = 0
    precisions = []
    recalls = []
    for true_positive, false_positive in zip(tp_flags, fp_flags):
        cumulative_tp += true_positive
        cumulative_fp += false_positive
        precisions.append(cumulative_tp / (cumulative_tp + cumulative_fp))
        recalls.append(cumulative_tp / gt_count if gt_count else 0.0)
    envelope = [
        max(precisions[index:]) for index in range(len(precisions))
    ]
    ap_samples = []
    for recall_point in [index / 100.0 for index in range(101)]:
        candidates = [
            envelope[index]
            for index, observed_recall in enumerate(recalls)
            if observed_recall >= recall_point
        ]
        ap_samples.append(max(candidates, default=0.0))
    return {
        "precision": precision,
        "recall": recall,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "prediction_count": len(predictions),
        "gt_count": gt_count,
        "ap": sum(ap_samples) / len(ap_samples),
        "matched_iou_count": len(matched_iou),
    }


def evaluate_backend(
    predictions_by_image: dict[str, list[dict[str, Any]]],
    gt_by_image: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    overall_by_threshold = {
        threshold: evaluate_predictions(predictions_by_image, gt_by_image, threshold)
        for threshold in IOU_THRESHOLDS
    }
    class_by_threshold = {
        class_name: {
            threshold: evaluate_predictions(
                predictions_by_image, gt_by_image, threshold, class_id
            )
            for threshold in IOU_THRESHOLDS
        }
        for class_id, class_name in enumerate(CLASS_NAMES)
    }
    at50 = overall_by_threshold[0.5]
    backend_metrics = {
        "precision": at50["precision"],
        "recall": at50["recall"],
        "mAP50": sum(class_by_threshold[name][0.5]["ap"] for name in CLASS_NAMES) / len(CLASS_NAMES),
        "mAP50_95": sum(
            class_by_threshold[name][threshold]["ap"]
            for name in CLASS_NAMES
            for threshold in IOU_THRESHOLDS
        ) / (len(CLASS_NAMES) * len(IOU_THRESHOLDS)),
        "tp": at50["tp"],
        "fp": at50["fp"],
        "fn": at50["fn"],
        "prediction_count": at50["prediction_count"],
        "gt_count": at50["gt_count"],
        "iou50": {key: value for key, value in at50.items() if key != "ap"},
        "iou_thresholds": IOU_THRESHOLDS,
    }
    classwise = {}
    for class_name in CLASS_NAMES:
        class50 = class_by_threshold[class_name][0.5]
        classwise[class_name] = {
            "AP50": class50["ap"],
            "AP50_95": sum(
                class_by_threshold[class_name][threshold]["ap"]
                for threshold in IOU_THRESHOLDS
            ) / len(IOU_THRESHOLDS),
            "precision": class50["precision"],
            "recall": class50["recall"],
            "tp": class50["tp"],
            "fp": class50["fp"],
            "fn": class50["fn"],
            "prediction_count": class50["prediction_count"],
            "gt_count": class50["gt_count"],
        }
    return backend_metrics, classwise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", required=True, type=Path)
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--fp32-detections", required=True, type=Path)
    parser.add_argument("--original-fp16-detections", required=True, type=Path)
    parser.add_argument("--m3-detections", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    gt_artifact, gt_by_image = load_ground_truth(args.ground_truth)
    detection_paths = {
        "TRT FP32 noTF32": args.fp32_detections,
        "TRT FP16 Original Stage K": args.original_fp16_detections,
        "TRT M3 diagnostic control": args.m3_detections,
    }
    backend_metrics = {}
    classwise_metrics = {}
    prediction_artifacts = {}
    for label, path in detection_paths.items():
        prediction_artifact, predictions = load_predictions(path, gt_artifact)
        prediction_artifacts[label] = {
            "path": str(path),
            "sha256": sha256(path),
            "backend": prediction_artifact.get("backend"),
        }
        metrics, classwise = evaluate_backend(predictions, gt_by_image)
        backend_metrics[label] = metrics
        classwise_metrics[label] = classwise

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "backend_metrics.json").write_text(json.dumps({
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_backend_metrics",
        "ground_truth_sha256": sha256(args.ground_truth),
        "backends": backend_metrics,
    }, indent=2) + "\n")
    (args.output_dir / "classwise_metrics.json").write_text(json.dumps({
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_classwise_metrics",
        "ground_truth_sha256": sha256(args.ground_truth),
        "class_names": CLASS_NAMES,
        "backends": classwise_metrics,
    }, indent=2) + "\n")
    provenance = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_evaluator_provenance",
        "evaluator_kind": "project-local evaluator",
        "evaluator_path": str(Path(__file__).resolve()),
        "evaluator_sha256": sha256(Path(__file__).resolve()),
        "ground_truth_path": str(args.ground_truth),
        "ground_truth_sha256": sha256(args.ground_truth),
        "contract_path": str(args.contract),
        "contract_sha256": sha256(args.contract),
        "prediction_artifacts": prediction_artifacts,
        "ap_calculation": {
            "method": "101-point interpolated precision envelope",
            "recall_points": 101,
            "integration": "mean of maximum precision at recall >= each recall point",
        },
        "matching": {
            "class_aware": True,
            "one_to_one": True,
            "priority": "highest IoU eligible ground truth after confidence sorting",
            "confidence_sort": "descending confidence; deterministic image/class/geometry tie-break",
        },
        "iou": {
            "thresholds": IOU_THRESHOLDS,
            "coordinate_semantics": "exclusive width/height",
        },
        "max_det": MAX_DET,
        "confidence_handling": "detections are already filtered by frozen confidence threshold 0.25; no additional filtering",
        "ultralytics_equivalence": "not claimed; this is project-local evaluator output",
    }
    (args.output_dir / "evaluator_provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps(backend_metrics, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"ERROR: {error}") from error
