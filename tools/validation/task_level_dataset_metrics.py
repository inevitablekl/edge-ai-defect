#!/usr/bin/env python3
"""Evaluate postprocessed detections against standard YOLO validation labels.

The script deliberately refuses to invent dataset metrics when labels are not
provided.  It accepts the normalized result files emitted by the task-level
detection comparator.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    iw = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    ih = max(0.0, min(ay2, by2) - max(ay1, by1))
    inter = iw * ih
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0.0 else 0.0


def load_labels(labels_dir: Path, result: dict[str, Any]) -> list[dict[str, Any]]:
    relative_path = Path(str(result["relative_path"]))
    label_path = labels_dir / (relative_path.stem + ".txt")
    if not label_path.is_file():
        raise FileNotFoundError(str(label_path))
    width = float(result["width"])
    height = float(result["height"])
    labels = []
    for line_number, line in enumerate(label_path.read_text().splitlines(), 1):
        fields = line.split()
        if len(fields) != 5:
            raise ValueError(f"{label_path}:{line_number}: expected 5 YOLO fields")
        class_id, cx, cy, box_width, box_height = int(fields[0]), *map(float, fields[1:])
        labels.append({
            "class_id": class_id,
            "bbox_xyxy": [
                (cx - box_width / 2.0) * width,
                (cy - box_height / 2.0) * height,
                (cx + box_width / 2.0) * width,
                (cy + box_height / 2.0) * height,
            ],
        })
    return labels


def ap_at_iou(result: dict[str, Any], labels_by_image: dict[str, list[dict[str, Any]]], threshold: float) -> tuple[float, int, int, int]:
    predictions = []
    total_ground_truth = 0
    for image in result["images"]:
        image_id = str(image["image_id"])
        ground_truth = labels_by_image[image_id]
        total_ground_truth += len(ground_truth)
        for prediction in image["detections"]:
            predictions.append((float(prediction["confidence"]), image_id, prediction))
    predictions.sort(key=lambda item: (-item[0], item[1], int(item[2]["class_id"])))
    used: dict[str, set[int]] = {key: set() for key in labels_by_image}
    tp: list[int] = []
    fp: list[int] = []
    for _, image_id, prediction in predictions:
        candidates = [
            (index, target)
            for index, target in enumerate(labels_by_image[image_id])
            if index not in used[image_id]
            and int(target["class_id"]) == int(prediction["class_id"])
        ]
        best = max(candidates, key=lambda item: iou(prediction["bbox_xyxy"], item[1]["bbox_xyxy"]), default=None)
        if best is not None and iou(prediction["bbox_xyxy"], best[1]["bbox_xyxy"]) >= threshold:
            used[image_id].add(best[0])
            tp.append(1)
            fp.append(0)
        else:
            tp.append(0)
            fp.append(1)
    cumulative_tp = 0
    cumulative_fp = 0
    precisions = []
    recalls = []
    for true_positive, false_positive in zip(tp, fp):
        cumulative_tp += true_positive
        cumulative_fp += false_positive
        precisions.append(cumulative_tp / (cumulative_tp + cumulative_fp))
        recalls.append(cumulative_tp / total_ground_truth if total_ground_truth else 0.0)
    precision_envelope = []
    for index in range(len(precisions)):
        precision_envelope.append(max(precisions[index:]))
    recall_points = [index / 100.0 for index in range(101)]
    precision_at_recall = []
    for recall_point in recall_points:
        candidates = [precision_envelope[index] for index, recall in enumerate(recalls) if recall >= recall_point]
        precision_at_recall.append(max(candidates, default=0.0))
    average_precision = sum(precision_at_recall) / len(recall_points)
    return average_precision, cumulative_tp, cumulative_fp, total_ground_truth


def evaluate(result: dict[str, Any], labels_dir: Path) -> dict[str, Any]:
    labels_by_image = {}
    for image in result["images"]:
        labels_by_image[str(image["image_id"])] = load_labels(labels_dir, image)
    ap50, tp, fp, gt_count = ap_at_iou(result, labels_by_image, 0.5)
    aps = [ap_at_iou(result, labels_by_image, threshold)[0] for threshold in [0.5 + 0.05 * index for index in range(10)]]
    return {
        "status": "MEASURED",
        "image_count": len(result["images"]),
        "ground_truth_count": gt_count,
        "true_positive_count_iou50": tp,
        "false_positive_count_iou50": fp,
        "false_negative_count_iou50": gt_count - tp,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / gt_count if gt_count else 0.0,
        "mAP50": ap50,
        "mAP50_95": sum(aps) / len(aps),
        "iou_thresholds": [round(0.5 + 0.05 * index, 2) for index in range(10)],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fp32-result", required=True, type=Path)
    parser.add_argument("--fp16-result", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--labels-dir", type=Path)
    args = parser.parse_args()
    output: dict[str, Any] = {
        "schema_version": 1,
        "artifact_kind": "stage_k5_4_dataset_metrics",
        "label_format": "YOLO normalized class cx cy width height",
    }
    if args.labels_dir is None or not args.labels_dir.is_dir():
        reason = "NEU-DET validation bounding-box annotations were not available in the frozen/local corpus"
        output.update({
            "status": "TBD_REAL_ANNOTATIONS_REQUIRED",
            "reason": reason,
            "precision": "TBD: real experiment data required",
            "recall": "TBD: real experiment data required",
            "mAP50": "TBD: real experiment data required",
            "mAP50_95": "TBD: real experiment data required",
            "backends": {"TRT FP32 noTF32": None, "TRT FP16": None},
        })
    else:
        fp32 = evaluate(json.loads(args.fp32_result.read_text()), args.labels_dir)
        fp16 = evaluate(json.loads(args.fp16_result.read_text()), args.labels_dir)
        output["status"] = "MEASURED"
        output["backends"] = {"TRT FP32 noTF32": fp32, "TRT FP16": fp16}
        output["absolute_mAP50_drop"] = fp32["mAP50"] - fp16["mAP50"]
        output["absolute_mAP50_95_drop"] = fp32["mAP50_95"] - fp16["mAP50_95"]
        output["absolute_recall_drop"] = fp32["recall"] - fp16["recall"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
