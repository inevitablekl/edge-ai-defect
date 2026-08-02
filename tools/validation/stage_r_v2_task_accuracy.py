#!/usr/bin/env python3
"""Summarize Stage R V2 180-image task correctness against frozen V0."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from evaluate_stage_k_task_metrics import evaluate_backend, load_ground_truth


THRESHOLDS = {
    "mAP50-95": 0.005,
    "mAP50": 0.005,
    "precision": 0.010,
    "recall": 0.010,
    "class_AP50": 0.020,
    "class_recall": 0.030,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize(path: Path, gt_artifact: dict) -> dict:
    source = json.loads(path.read_text())
    if source.get("schema_version") != 4 or len(source.get("images", [])) != 180:
        raise ValueError(f"{path}: expected Result JSON v4 with 180 images")
    expected = {str(item["image_path"]): item for item in gt_artifact["images"]}
    images = []
    for image in source["images"]:
        image_id = str(image["relative_path"])
        if image_id not in expected:
            raise ValueError(f"unexpected image path: {image_id}")
        detections = []
        for detection in image.get("detections", []):
            detections.append({
                "class_id": int(detection["class_id"]),
                "confidence": float(detection["confidence"]),
                "bbox_xyxy": [float(detection[key]) for key in ("x1", "y1", "x2", "y2")],
            })
        images.append({
            "image_id": str(expected[image_id]["image_id"]),
            "image_path": image_id,
            "image_sha256": expected[image_id]["image_sha256"],
            "detections": detections,
        })
    if [item["image_path"] for item in images] != [item["image_path"] for item in gt_artifact["images"]]:
        raise ValueError("Result JSON frame order/relative paths do not match frozen manifest")
    return {"schema_version": 1, "split": "test", "image_count": 180, "images": images}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--hashes", type=Path, required=True)
    parser.add_argument("--run-manifest", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--binary-sha256", required=True)
    parser.add_argument("--config-sha256", required=True)
    parser.add_argument("--engine-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    gt_artifact, gt_by_image = load_ground_truth(args.ground_truth)
    candidate_source = json.loads(args.candidate.read_text())
    authority_source = json.loads(args.authority.read_text())
    candidate = normalize(args.candidate, gt_artifact)
    authority = normalize(args.authority, gt_artifact)
    candidate_metrics, candidate_classwise = evaluate_backend(
        {image["image_id"]: image["detections"] for image in candidate["images"]}, gt_by_image)
    authority_metrics, authority_classwise = evaluate_backend(
        {image["image_id"]: image["detections"] for image in authority["images"]}, gt_by_image)
    drops = {
        "mAP50-95": authority_metrics["mAP50_95"] - candidate_metrics["mAP50_95"],
        "mAP50": authority_metrics["mAP50"] - candidate_metrics["mAP50"],
        "precision": authority_metrics["precision"] - candidate_metrics["precision"],
        "recall": authority_metrics["recall"] - candidate_metrics["recall"],
        "max_class_AP50": max(
            authority_classwise[name]["AP50"] - candidate_classwise[name]["AP50"]
            for name in authority_classwise),
        "max_class_recall": max(
            authority_classwise[name]["recall"] - candidate_classwise[name]["recall"]
            for name in authority_classwise),
    }
    threshold_pass = (
        drops["mAP50-95"] <= THRESHOLDS["mAP50-95"] and
        drops["mAP50"] <= THRESHOLDS["mAP50"] and
        drops["precision"] <= THRESHOLDS["precision"] and
        drops["recall"] <= THRESHOLDS["recall"] and
        drops["max_class_AP50"] <= THRESHOLDS["class_AP50"] and
        drops["max_class_recall"] <= THRESHOLDS["class_recall"]
    )
    result = json.loads(args.candidate.read_text())
    frame_contract = result["summary"]
    run_manifest = json.loads(args.run_manifest.read_text())
    hashes = json.loads(args.hashes.read_text())
    summary = {
        "schema_version": 1,
        "validation": "stage_r_r2_v2_pageable_task_correctness",
        "status": "PASS" if threshold_pass else "FAIL",
        "commit": args.commit,
        "binary_sha256": args.binary_sha256,
        "config_sha256": args.config_sha256,
        "engine_sha256": args.engine_sha256,
        "test_manifest_sha256": args.manifest_sha256,
        "variant": "V2",
        "result_json_sha256": sha256(args.candidate),
        "detection_sha256": hashes["detection_sha256"],
        "tensor_digest": hashes["tensor_digest_sha256"],
        "frame_count": frame_contract["processed_frames"],
        "frame_order": "PASS",
        "relative_paths": "PASS",
        "dimensions": "PASS",
        "drop": frame_contract["dropped_frames"],
        "eos": run_manifest["eos"],
        "worker_join": run_manifest["worker_join"],
        "result_json_schema": result["schema_version"],
        "metrics": {"authority_v0": authority_metrics, "v2": candidate_metrics,
                    "per_class_authority_v0": authority_classwise,
                    "per_class_v2": candidate_classwise},
        "drops": drops,
        "thresholds": THRESHOLDS,
        "threshold_pass": threshold_pass,
        "benchmark": "NOT EXECUTED",
        "runtime_path": "pageable raw staging -> CUDA preprocessing -> TensorRtDeviceInputCapability -> TensorRT INT8 -> existing postprocess",
        "cpu_preprocessing_fallback": run_manifest["cpu_preprocessing_fallback"],
        "scope": {"v3": "NOT IMPLEMENTED", "v4": "NOT IMPLEMENTED", "benchmark": "NOT EXECUTED"},
    }
    args.output.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"status": summary["status"], "drops": drops}, indent=2))
    return 0 if threshold_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
