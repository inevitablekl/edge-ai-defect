#!/usr/bin/env python3
"""Compare final detections from the frozen FP32 and Original FP16 runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100.0
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def load(path: Path) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]]]:
    artifact = json.loads(path.read_text())
    by_image = {}
    for image in artifact["images"]:
        image_id = str(image["image_id"])
        if image_id in by_image:
            raise ValueError(f"duplicate image_id: {image_id}")
        by_image[image_id] = image["detections"]
    if len(by_image) != 180:
        raise ValueError(f"expected 180 images in {path}")
    return artifact, by_image


def detection_key(item: dict[str, Any], side: str) -> tuple[Any, ...]:
    box = item[side]["bbox_xyxy"]
    return (
        int(item[side]["class_id"]),
        *[float(value) for value in box],
        float(item[side]["confidence"]),
    )


def detection_record(item: dict[str, Any], side: str) -> dict[str, Any]:
    detection = item[side]
    return {
        "class_id": int(detection["class_id"]),
        "confidence": float(detection["confidence"]),
        "bbox_xyxy": [float(value) for value in detection["bbox_xyxy"]],
    }


def compare_image(
    image_id: str,
    left: list[dict[str, Any]],
    right: list[dict[str, Any]],
) -> dict[str, Any]:
    candidate_pairs = []
    for left_index, left_detection in enumerate(left):
        for right_index, right_detection in enumerate(right):
            if int(left_detection["class_id"]) != int(right_detection["class_id"]):
                continue
            overlap = iou(left_detection["bbox_xyxy"], right_detection["bbox_xyxy"])
            candidate_pairs.append({
                "left_index": left_index,
                "right_index": right_index,
                "iou": overlap,
                "left": left_detection,
                "right": right_detection,
            })
    candidate_pairs.sort(
        key=lambda item: (
            -item["iou"],
            detection_key(item, "left"),
            detection_key(item, "right"),
        )
    )
    used_left: set[int] = set()
    used_right: set[int] = set()
    matched = []
    for item in candidate_pairs:
        if item["left_index"] in used_left or item["right_index"] in used_right:
            continue
        used_left.add(item["left_index"])
        used_right.add(item["right_index"])
        left_detection = item["left"]
        right_detection = item["right"]
        left_box = left_detection["bbox_xyxy"]
        right_box = right_detection["bbox_xyxy"]
        matched.append({
            "left_index": item["left_index"],
            "right_index": item["right_index"],
            "class_id": int(left_detection["class_id"]),
            "iou": item["iou"],
            "confidence_difference": abs(
                float(left_detection["confidence"]) - float(right_detection["confidence"])
            ),
            "bbox_coordinate_abs_error": [
                abs(float(left_box[index]) - float(right_box[index]))
                for index in range(4)
            ],
            "fp32": detection_record({"left": left_detection}, "left"),
            "original_fp16": detection_record({"right": right_detection}, "right"),
        })
    matched.sort(key=lambda item: item["left_index"])

    left_only = [
        detection_record({"left": detection}, "left")
        for index, detection in enumerate(left)
        if index not in used_left
    ]
    right_only = [
        detection_record({"right": detection}, "right")
        for index, detection in enumerate(right)
        if index not in used_right
    ]

    # Cross-class pairs are a diagnostic only.  They are not counted as
    # matches, and they use IoU>=0.5 solely to identify likely class flips.
    mismatch_candidates = []
    for left_index, left_detection in enumerate(left):
        if left_index in used_left:
            continue
        for right_index, right_detection in enumerate(right):
            if right_index in used_right:
                continue
            if int(left_detection["class_id"]) == int(right_detection["class_id"]):
                continue
            overlap = iou(left_detection["bbox_xyxy"], right_detection["bbox_xyxy"])
            if overlap >= 0.5:
                mismatch_candidates.append({
                    "left_index": left_index,
                    "right_index": right_index,
                    "iou": overlap,
                    "fp32_class_id": int(left_detection["class_id"]),
                    "original_fp16_class_id": int(right_detection["class_id"]),
                })
    mismatch_candidates.sort(key=lambda item: (-item["iou"], item["left_index"], item["right_index"]))
    mismatch_left: set[int] = set()
    mismatch_right: set[int] = set()
    mismatches = []
    for item in mismatch_candidates:
        if item["left_index"] in mismatch_left or item["right_index"] in mismatch_right:
            continue
        mismatch_left.add(item["left_index"])
        mismatch_right.add(item["right_index"])
        mismatches.append(item)

    ious = [item["iou"] for item in matched]
    confidence_errors = [item["confidence_difference"] for item in matched]
    bbox_errors = [error for item in matched for error in item["bbox_coordinate_abs_error"]]
    return {
        "image_id": image_id,
        "fp32_detection_count": len(left),
        "original_fp16_detection_count": len(right),
        "detection_count_difference": len(right) - len(left),
        "matched_detection_count": len(matched),
        "fp32_only_count": len(left_only),
        "original_fp16_only_count": len(right_only),
        "class_mismatch_count": len(mismatches),
        "matched": matched,
        "fp32_only": left_only,
        "original_fp16_only": right_only,
        "class_mismatches": mismatches,
        "mean_iou": sum(ious) / len(ious) if ious else None,
        "minimum_iou": min(ious) if ious else None,
        "iou_p5": percentile(ious, 5),
        "iou_p50": percentile(ious, 50),
        "iou_p95": percentile(ious, 95),
        "confidence_mae": sum(confidence_errors) / len(confidence_errors) if confidence_errors else None,
        "bbox_coordinate_mae": sum(bbox_errors) / len(bbox_errors) if bbox_errors else None,
        "bbox_coordinate_max_abs": max(bbox_errors) if bbox_errors else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fp32-detections", required=True, type=Path)
    parser.add_argument("--original-fp16-detections", required=True, type=Path)
    parser.add_argument("--test-manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    left_artifact, left = load(args.fp32_detections)
    right_artifact, right = load(args.original_fp16_detections)
    if left_artifact.get("split_manifest_sha256") != right_artifact.get("split_manifest_sha256"):
        raise ValueError("prediction split identity mismatch")
    split_sha = sha256(args.test_manifest)
    if left_artifact.get("split_manifest_sha256") != split_sha:
        raise ValueError("prediction split SHA does not match supplied test manifest")
    if set(left) != set(right):
        raise ValueError("prediction image sets differ")

    per_image = [compare_image(image_id, left[image_id], right[image_id]) for image_id in sorted(left)]
    matched = [item for image in per_image for item in image["matched"]]
    ious = [item["iou"] for item in matched]
    confidence_errors = [item["confidence_difference"] for item in matched]
    bbox_errors = [error for item in matched for error in item["bbox_coordinate_abs_error"]]
    output = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_fp32_vs_original_fp16",
        "test_manifest_sha256": split_sha,
        "fp32_detections_sha256": sha256(args.fp32_detections),
        "original_fp16_detections_sha256": sha256(args.original_fp16_detections),
        "matching": {
            "class_exact_for_matches": True,
            "per_class_one_to_one": True,
            "priority": "descending IoU within exact class; geometry/class tie-break, not candidate order",
            "cross_class_diagnostic_threshold": 0.5,
            "cross_class_pairs_are_not_matches": True,
        },
        "image_count": len(per_image),
        "fp32_detection_count": sum(len(value) for value in left.values()),
        "original_fp16_detection_count": sum(len(value) for value in right.values()),
        "matched_detection_count": len(matched),
        "fp32_only_detection_count": sum(item["fp32_only_count"] for item in per_image),
        "original_fp16_only_detection_count": sum(item["original_fp16_only_count"] for item in per_image),
        "class_mismatch_count": sum(item["class_mismatch_count"] for item in per_image),
        "mean_iou": sum(ious) / len(ious) if ious else None,
        "minimum_iou": min(ious) if ious else None,
        "iou_p5": percentile(ious, 5),
        "iou_p50": percentile(ious, 50),
        "iou_p95": percentile(ious, 95),
        "confidence_mae": sum(confidence_errors) / len(confidence_errors) if confidence_errors else None,
        "bbox_coordinate_mae": sum(bbox_errors) / len(bbox_errors) if bbox_errors else None,
        "bbox_coordinate_max_abs": max(bbox_errors) if bbox_errors else None,
        "per_image_detection_count_difference": [
            {
                "image_id": image["image_id"],
                "fp32_count": image["fp32_detection_count"],
                "original_fp16_count": image["original_fp16_detection_count"],
                "difference": image["detection_count_difference"],
            }
            for image in per_image
        ],
        "per_image": per_image,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({key: output[key] for key in (
        "image_count", "fp32_detection_count", "original_fp16_detection_count",
        "matched_detection_count", "fp32_only_detection_count",
        "original_fp16_only_detection_count", "class_mismatch_count",
        "mean_iou", "minimum_iou", "iou_p5", "iou_p50", "iou_p95",
        "confidence_mae", "bbox_coordinate_mae", "bbox_coordinate_max_abs")}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit(f"ERROR: {error}") from error
