#!/usr/bin/env python3
"""Normalize and compare final detections from two frozen TensorRT engines."""

import argparse
import json
import math
from pathlib import Path


def box_xyxy(detection: dict) -> list[float]:
    if "bbox_xyxy" in detection:
        values = detection["bbox_xyxy"]
    else:
        values = [detection[key] for key in ("x1", "y1", "x2", "y2")]
    if len(values) != 4 or not all(math.isfinite(float(value)) for value in values):
        raise ValueError("detection bbox must contain four finite values")
    return [float(value) for value in values]


def normalize(source: Path, output: Path, backend: str) -> dict:
    raw = json.loads(source.read_text())
    images = []
    for image in raw.get("images", []):
        detections = []
        for detection in image.get("detections", []):
            detections.append({
                "class_id": int(detection["class_id"]),
                "confidence": float(detection["confidence"]),
                "bbox_xyxy": box_xyxy(detection),
            })
        images.append({
            "image_id": Path(image["relative_path"]).stem,
            "relative_path": image["relative_path"],
            "width": int(image["width"]),
            "height": int(image["height"]),
            "detections": detections,
        })
    result = {
        "schema_version": 1,
        "artifact_kind": "stage_k5_4_task_level_detection_results",
        "backend": backend,
        "source_application_result": str(source),
        "postprocess": raw.get("postprocess"),
        "images": images,
    }
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


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


def pair_metrics(left: dict, right: dict) -> dict:
    left_box = left["bbox_xyxy"]
    right_box = right["bbox_xyxy"]
    left_cx = (left_box[0] + left_box[2]) / 2.0
    left_cy = (left_box[1] + left_box[3]) / 2.0
    right_cx = (right_box[0] + right_box[2]) / 2.0
    right_cy = (right_box[1] + right_box[3]) / 2.0
    left_width = left_box[2] - left_box[0]
    left_height = left_box[3] - left_box[1]
    right_width = right_box[2] - right_box[0]
    right_height = right_box[3] - right_box[1]
    return {
        "fp32_class_id": left["class_id"],
        "fp16_class_id": right["class_id"],
        "class_match": left["class_id"] == right["class_id"],
        "iou": iou(left_box, right_box),
        "center_distance": math.hypot(left_cx - right_cx, left_cy - right_cy),
        "width_difference": abs(left_width - right_width),
        "height_difference": abs(left_height - right_height),
        "confidence_difference": abs(left["confidence"] - right["confidence"]),
        "fp32_confidence": left["confidence"],
        "fp16_confidence": right["confidence"],
        "fp32_bbox_xyxy": left_box,
        "fp16_bbox_xyxy": right_box,
    }


def compare_image(left: dict, right: dict) -> dict:
    if left["image_id"] != right["image_id"]:
        raise ValueError(f"image identity mismatch: {left['image_id']} vs {right['image_id']}")
    left_detections = left["detections"]
    right_detections = right["detections"]
    pairs = []
    for left_index, left_detection in enumerate(left_detections):
        for right_index, right_detection in enumerate(right_detections):
            pairs.append((
                left_detection["class_id"] == right_detection["class_id"],
                iou(left_detection["bbox_xyxy"], right_detection["bbox_xyxy"]),
                -left_index,
                -right_index,
                left_index,
                right_index,
            ))
    pairs.sort(reverse=True)
    used_left, used_right, matches = set(), set(), []
    for _, _, _, _, left_index, right_index in pairs:
        if left_index in used_left or right_index in used_right:
            continue
        used_left.add(left_index)
        used_right.add(right_index)
        metric = pair_metrics(left_detections[left_index], right_detections[right_index])
        metric.update({"fp32_index": left_index, "fp16_index": right_index})
        matches.append(metric)
    matches.sort(key=lambda item: item["fp32_index"])
    ious = [item["iou"] for item in matches]
    confidence_differences = [item["confidence_difference"] for item in matches]
    class_mismatches = sum(not item["class_match"] for item in matches)
    return {
        "image_id": left["image_id"],
        "relative_path": left["relative_path"],
        "fp32_detection_count": len(left_detections),
        "fp16_detection_count": len(right_detections),
        "detection_count_difference": len(right_detections) - len(left_detections),
        "matched_detection_count": len(matches),
        "unmatched_fp32_count": len(left_detections) - len(matches),
        "unmatched_fp16_count": len(right_detections) - len(matches),
        "class_mismatch_count": class_mismatches,
        "class_consistent": class_mismatches == 0 and len(left_detections) == len(right_detections),
        "mean_iou": sum(ious) / len(ious) if ious else None,
        "minimum_iou": min(ious) if ious else None,
        "iou_below_0_5_count": sum(value < 0.5 for value in ious),
        "confidence_difference_mae": sum(confidence_differences) / len(confidence_differences) if confidence_differences else None,
        "matches": matches,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fp32-app-result", type=Path, required=True)
    parser.add_argument("--fp16-app-result", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fp32 = normalize(args.fp32_app_result, args.output_dir / "results_fp32.json", "tensorrt_strict_fp32_notf32")
    fp16 = normalize(args.fp16_app_result, args.output_dir / "results_fp16.json", "tensorrt_fp16")
    if [image["image_id"] for image in fp32["images"]] != [image["image_id"] for image in fp16["images"]]:
        raise SystemExit("FP32 and FP16 image identities are not identical")
    per_image = [compare_image(left, right) for left, right in zip(fp32["images"], fp16["images"])]
    all_matches = [match for image in per_image for match in image["matches"]]
    ious = [match["iou"] for match in all_matches]
    confidence_differences = [match["confidence_difference"] for match in all_matches]
    comparison = {
        "schema_version": 1,
        "artifact_kind": "stage_k5_4_detection_level_comparison",
        "matching": {
            "algorithm": "deterministic greedy one-to-one matching",
            "priority": "same class first, then descending IoU",
            "cross_class_pairs_retained_for_class_mismatch_reporting": True,
        },
        "image_count": len(per_image),
        "fp32_total_detection_count": sum(image["fp32_detection_count"] for image in per_image),
        "fp16_total_detection_count": sum(image["fp16_detection_count"] for image in per_image),
        "matched_detection_count": len(all_matches),
        "class_mismatch_count": sum(image["class_mismatch_count"] for image in per_image),
        "class_consistent_image_count": sum(image["class_consistent"] for image in per_image),
        "mean_iou": sum(ious) / len(ious) if ious else None,
        "minimum_iou": min(ious) if ious else None,
        "iou_below_0_5_count": sum(value < 0.5 for value in ious),
        "confidence_difference_mae": sum(confidence_differences) / len(confidence_differences) if confidence_differences else None,
        "per_image": per_image,
    }
    (args.output_dir / "detection_comparison.json").write_text(json.dumps(comparison, indent=2) + "\n")
    print(json.dumps({key: comparison[key] for key in (
        "image_count", "fp32_total_detection_count", "fp16_total_detection_count",
        "matched_detection_count", "class_mismatch_count", "mean_iou",
        "minimum_iou", "iou_below_0_5_count", "confidence_difference_mae")}, indent=2))


if __name__ == "__main__":
    main()
