#!/usr/bin/env python3
"""Evaluate the two same-invocation Q5 Result JSON artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import pathlib
import xml.etree.ElementTree as ET

CLASSES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]
THRESHOLDS = [round(0.50 + 0.05 * i, 2) for i in range(10)]


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def parse_gt(xml_path: pathlib.Path) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    result = []
    for obj in root.findall("object"):
        name = obj.findtext("name")
        if name not in CLASSES:
            raise ValueError(f"unknown class in {xml_path}")
        box = obj.find("bndbox")
        values = [float(box.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax")]
        if not all(math.isfinite(v) for v in values) or values[2] <= values[0] or values[3] <= values[1]:
            raise ValueError(f"invalid ground truth box in {xml_path}")
        result.append({"class_id": CLASSES.index(name), "bbox": values})
    return result


def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    return inter / (area_a + area_b - inter) if area_a + area_b - inter > 0 else 0.0


def evaluate(preds, gts, threshold, class_id=None):
    gt_count = sum(sum(1 for x in boxes if class_id is None or x["class_id"] == class_id) for boxes in gts.values())
    items = [(image, p) for image, boxes in preds.items() for p in boxes if class_id is None or p["class_id"] == class_id]
    items.sort(key=lambda x: (-x[1]["confidence"], x[0], x[1]["class_id"], *x[1]["bbox"]))
    used = {image: set() for image in gts}
    tp, fp, precisions, recalls = [], [], [], []
    cumulative_tp = cumulative_fp = 0
    for image, prediction in items:
        candidates = [(iou(prediction["bbox"], gt["bbox"]), index, gt) for index, gt in enumerate(gts[image])
                      if index not in used[image] and (class_id is None and gt["class_id"] == prediction["class_id"] or class_id is not None and gt["class_id"] == class_id)]
        best = max(candidates, default=None, key=lambda x: (x[0], -x[1]))
        hit = best is not None and best[0] >= threshold
        tp.append(1 if hit else 0); fp.append(0 if hit else 1)
        if hit: used[image].add(best[1])
        cumulative_tp += tp[-1]; cumulative_fp += fp[-1]
        precisions.append(cumulative_tp / (cumulative_tp + cumulative_fp))
        recalls.append(cumulative_tp / gt_count if gt_count else 0.0)
    envelope = [max(precisions[i:], default=0.0) for i in range(len(precisions))]
    ap = sum(max((envelope[i] for i, r in enumerate(recalls) if r >= point), default=0.0)
             for point in (i / 100 for i in range(101))) / 101
    true_positive = sum(tp)
    false_positive = sum(fp)
    return {"precision": true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0,
            "recall": true_positive / gt_count if gt_count else 0.0, "ap": ap,
            "tp": true_positive, "fp": false_positive, "fn": gt_count - true_positive,
            "prediction_count": len(items), "gt_count": gt_count}


def backend_metrics(preds, gts):
    class_metrics = {}
    for index, name in enumerate(CLASSES):
        at50 = evaluate(preds, gts, 0.50, index)
        class_metrics[name] = {"AP50": at50["ap"], "Recall": at50["recall"]}
    at50 = evaluate(preds, gts, 0.50)
    return {"Precision": at50["precision"], "Recall": at50["recall"],
            "mAP50": sum(x["AP50"] for x in class_metrics.values()) / len(CLASSES),
            "mAP50-95": sum(evaluate(preds, gts, t, c)["ap"] for c in range(len(CLASSES)) for t in THRESHOLDS) / (len(CLASSES) * len(THRESHOLDS)),
            "detection_count": sum(len(x) for x in preds.values()), "tp": at50["tp"], "fp": at50["fp"], "fn": at50["fn"],
            "per_class": class_metrics}


def load_result(path, manifest_entries, backend):
    data = json.loads(path.read_text())
    if data.get("schema_version") != (4 if backend == "int8" else 3) or data.get("backend", {}).get("type") != ("tensorrt_int8" if backend == "int8" else "tensorrt_fp16"):
        raise ValueError(f"result schema/backend mismatch: {path}")
    images = data.get("images", [])
    if len(images) != 180:
        raise ValueError(f"result image count is not 180: {path}")
    expected = [x["image_path"] for x in manifest_entries]
    if [x.get("relative_path") for x in images] != expected:
        raise ValueError(f"result order/path mismatch: {path}")
    predictions = {}
    failures = non_finite = 0
    for image in images:
        boxes = []
        for item in image.get("detections", []):
            values = [float(item[k]) for k in ("x1", "y1", "x2", "y2", "confidence")]
            if not all(math.isfinite(v) for v in values): non_finite += 1; continue
            boxes.append({"class_id": int(item["class_id"]), "confidence": values[4], "bbox": values[:4]})
        predictions[image["relative_path"]] = boxes
    return data, predictions, failures, non_finite


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--dataset-root", type=pathlib.Path, required=True)
    parser.add_argument("--fp16-result", type=pathlib.Path, required=True)
    parser.add_argument("--int8-result", type=pathlib.Path, required=True)
    parser.add_argument("--fp16-hash", type=pathlib.Path, required=True)
    parser.add_argument("--int8-hash", type=pathlib.Path, required=True)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    args = parser.parse_args()
    entries = json.loads(args.manifest.read_text())["entries"]
    if len(entries) != 180 or json.loads(args.manifest.read_text()).get("split") != "test": raise ValueError("test manifest authority invalid")
    gts = {}
    for entry in entries:
        image = args.dataset_root / entry["image_path"]
        annotation = args.dataset_root / entry["annotation_path"]
        if sha256(image) != entry["image_sha256"] or sha256(annotation) != entry["annotation_sha256"]: raise ValueError(f"source SHA mismatch: {image}")
        gts[entry["image_path"]] = parse_gt(annotation)
    fp16, fp16_preds, fp16_fail, fp16_nf = load_result(args.fp16_result, entries, "fp16")
    int8, int8_preds, int8_fail, int8_nf = load_result(args.int8_result, entries, "int8")
    if fp16_nf + int8_nf:
        raise ValueError(f"non-finite detection values found: {fp16_nf + int8_nf}")
    for hash_path, backend in ((args.fp16_hash, "fp16"), (args.int8_hash, "int8")):
        authority = json.loads(hash_path.read_text())
        if authority.get("backend") != backend or authority.get("accepted_frames") != 180 or authority.get("cycles") != 1: raise ValueError(f"hash authority invalid: {hash_path}")
    metrics = {"fp16": backend_metrics(fp16_preds, gts), "int8": backend_metrics(int8_preds, gts)}
    drops = {"mAP50-95": metrics["fp16"]["mAP50-95"] - metrics["int8"]["mAP50-95"], "mAP50": metrics["fp16"]["mAP50"] - metrics["int8"]["mAP50"], "Precision": metrics["fp16"]["Precision"] - metrics["int8"]["Precision"], "Recall": metrics["fp16"]["Recall"] - metrics["int8"]["Recall"], "max_class_AP50": max(metrics["fp16"]["per_class"][c]["AP50"] - metrics["int8"]["per_class"][c]["AP50"] for c in CLASSES), "max_class_Recall": max(metrics["fp16"]["per_class"][c]["Recall"] - metrics["int8"]["per_class"][c]["Recall"] for c in CLASSES)}
    acceptable = drops["mAP50-95"] <= .020 and drops["mAP50"] <= .020 and drops["Precision"] <= .030 and drops["Recall"] <= .030 and drops["max_class_AP50"] <= .050 and drops["max_class_Recall"] <= .100
    tradeoff = drops["mAP50-95"] <= .040 and drops["mAP50"] <= .040 and drops["Precision"] <= .060 and drops["Recall"] <= .060 and drops["max_class_AP50"] <= .100 and drops["max_class_Recall"] <= .200
    classification = "ACCEPTABLE" if acceptable else "TRADEOFF" if tradeoff else "UNACCEPTABLE"
    out = args.output_dir; out.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": 1, "test_manifest_sha256": sha256(args.manifest), "evaluated_images": 180, "ground_truth_boxes": sum(len(x) for x in gts.values()), "image_failures": fp16_fail + int8_fail, "non_finite_values": fp16_nf + int8_nf, "metrics": metrics, "drops": drops, "classification": classification, "fp16_result_sha256": sha256(args.fp16_result), "int8_result_sha256": sha256(args.int8_result)}
    (out / "metrics_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    (out / "classification_report.json").write_text(json.dumps({"classification": classification, "thresholds": {"acceptable": {"mAP50-95": .020, "mAP50": .020, "Precision": .030, "Recall": .030, "class_AP50": .050, "class_Recall": .100}, "tradeoff": {"mAP50-95": .040, "mAP50": .040, "Precision": .060, "Recall": .060, "class_AP50": .100, "class_Recall": .200}}, "drops": drops}, indent=2) + "\n")
    (out / "evaluator_config.json").write_text(json.dumps({"evaluator": "tools/validation/evaluate_stage_q5_accuracy.py", "iou_thresholds": THRESHOLDS, "postprocess": {"confidence_threshold": .25, "iou_threshold": .45, "max_nms": 30000, "max_det": 300, "max_wh": 7680.0, "agnostic": False}, "evaluator_source_sha256": sha256(pathlib.Path(__file__))}, indent=2) + "\n")
    print("Q5_ACCURACY_EVIDENCE_VALID")
    print(classification)


if __name__ == "__main__":
    main()
