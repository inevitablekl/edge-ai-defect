#!/usr/bin/env python3
"""Convert the frozen NEU-DET test XML annotations into evaluator GT.

The conversion is provenance-preserving: source XML and image bytes are
read-only, source hashes are carried into every image/object record, and the
duplicate-row rule is the exact six-decimal YOLO-row rule used by the frozen
Stage K split generator.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPLIT = REPO_ROOT / "results/validation/stage_k_task_eval_v2/split/test_manifest.json"
DEFAULT_OUTPUT = REPO_ROOT / "results/validation/stage_k_task_eval_v2/ground_truth"
DATASET_MANIFEST = REPO_ROOT / "results/validation/stage_k_task_eval_v2/ground_truth_audit/dataset_manifest.json"
EXPECTED_TEST_SHA = "fd978beae99d8d88b72bcf2da082ed4caddccc502d882106e0e91e27a61797b8"
EXPECTED_SOURCE_TREE_SHA = "5e0f688fb5400406533e7c8d0406bfd29d2674011a657210de18740fe161b283"
CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]
CLASS_TO_ID = {name: index for index, name in enumerate(CLASS_NAMES)}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> str:
    content = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    path.write_text(content)
    return hashlib.sha256(content.encode()).hexdigest()


def text(root: ET.Element, path: str, source: Path) -> str:
    node = root.find(path)
    if node is None or node.text is None or not node.text.strip():
        raise ValueError(f"missing {path} in {source}")
    return node.text.strip()


def number(root: ET.Element, path: str, source: Path) -> float:
    try:
        value = float(text(root, path, source))
    except ValueError as error:
        raise ValueError(f"invalid {path} in {source}") from error
    if not math.isfinite(value):
        raise ValueError(f"non-finite {path} in {source}")
    return value


def yolo_row(width: int, height: int, box: dict[str, Any]) -> str:
    x1, y1, x2, y2 = [float(box[key]) for key in ("xmin", "ymin", "xmax", "ymax")]
    class_id = CLASS_TO_ID[box["class_name"]]
    cx = ((x1 + x2) / 2.0) / width
    cy = ((y1 + y2) / 2.0) / height
    bw = (x2 - x1) / width
    bh = (y2 - y1) / height
    return f"{class_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}"


def parse_xml(path: Path) -> tuple[int, int, list[dict[str, Any]], int]:
    root = ET.parse(path).getroot()
    if root.tag != "annotation":
        raise ValueError(f"unexpected XML root in {path}: {root.tag}")
    width = int(number(root, "size/width", path))
    height = int(number(root, "size/height", path))
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid image dimensions in {path}")
    boxes = []
    for object_node in root.findall("object"):
        class_name = text(object_node, "name", path)
        if class_name not in CLASS_TO_ID:
            raise ValueError(f"unknown class {class_name!r} in {path}")
        box = {
            "class_name": class_name,
            "xmin": number(object_node, "bndbox/xmin", path),
            "ymin": number(object_node, "bndbox/ymin", path),
            "xmax": number(object_node, "bndbox/xmax", path),
            "ymax": number(object_node, "bndbox/ymax", path),
        }
        if box["xmax"] <= box["xmin"] or box["ymax"] <= box["ymin"]:
            raise ValueError(f"non-positive bbox in {path}")
        if (
            box["xmin"] < 0 or box["ymin"] < 0
            or box["xmax"] > width or box["ymax"] > height
        ):
            raise ValueError(f"out-of-bounds bbox in {path}")
        boxes.append(box)
    unique = []
    seen = set()
    removed = 0
    for box in boxes:
        row = yolo_row(width, height, box)
        if row in seen:
            removed += 1
            continue
        seen.add(row)
        unique.append(box)
    return width, height, unique, removed


def validate_full_dataset(dataset_root: Path) -> dict[str, Any]:
    recorded = json.loads(DATASET_MANIFEST.read_text())
    if recorded["source_tree_sha256"] != EXPECTED_SOURCE_TREE_SHA:
        raise RuntimeError("recorded dataset source-tree SHA does not match frozen SHA")
    errors = []
    for entry in recorded["entries"]:
        path = dataset_root / entry["relative_path"]
        if not path.is_file():
            errors.append({"kind": "missing", "path": entry["relative_path"]})
            continue
        if path.stat().st_size != entry["size"]:
            errors.append({"kind": "size", "path": entry["relative_path"]})
        actual = sha256(path)
        if actual != entry["sha256"]:
            errors.append({"kind": "sha256", "path": entry["relative_path"]})
    if errors:
        raise RuntimeError(f"dataset source-tree integrity failed: {errors[:3]}")
    return {
        "manifest_path": str(DATASET_MANIFEST),
        "manifest_sha256": sha256(DATASET_MANIFEST),
        "entry_count": len(recorded["entries"]),
        "source_tree_sha256": recorded["source_tree_sha256"],
        "all_entries_verified": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-manifest", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    split_path = args.test_manifest.resolve()
    output_dir = args.output_dir.resolve()
    split_sha = sha256(split_path)
    if split_sha != EXPECTED_TEST_SHA:
        raise SystemExit(f"STOP: test manifest SHA mismatch: {split_sha}")
    split = json.loads(split_path.read_text())
    entries = split.get("entries", [])
    if split.get("split") != "test" or len(entries) != 180:
        raise SystemExit("STOP: frozen test manifest is not 180-entry test split")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise SystemExit(f"STOP: ground-truth output directory is non-empty: {output_dir}")

    dataset_root = Path(split["dataset_root"])
    if not dataset_root.is_absolute():
        dataset_root = REPO_ROOT / dataset_root
    full_dataset = validate_full_dataset(dataset_root)

    train = json.loads((split_path.parent / "train_manifest.json").read_text())
    val = json.loads((split_path.parent / "val_manifest.json").read_text())
    test_paths = {entry["image_path"] for entry in entries}
    if test_paths & ({item["image_path"] for item in train["entries"]} | {item["image_path"] for item in val["entries"]}):
        raise SystemExit("STOP: test split overlaps train/val")

    images = []
    class_counts = {name: 0 for name in CLASS_NAMES}
    raw_bbox_count = 0
    removed_duplicate_count = 0
    for entry in entries:
        image_path = dataset_root / entry["image_path"]
        xml_path = dataset_root / entry["annotation_path"]
        if not image_path.is_file() or not xml_path.is_file():
            raise SystemExit(f"STOP: missing split source: {entry['image_path']}")
        image_sha = sha256(image_path)
        xml_sha = sha256(xml_path)
        if image_sha != entry["image_sha256"] or xml_sha != entry["annotation_sha256"]:
            raise SystemExit(f"STOP: split source SHA mismatch: {entry['image_path']}")
        width, height, boxes, removed = parse_xml(xml_path)
        raw_bbox_count += len(ET.parse(xml_path).getroot().findall("object"))
        removed_duplicate_count += removed
        if len(boxes) != entry["bbox_count"]:
            raise SystemExit(f"STOP: bbox count mismatch: {entry['image_path']}")
        objects = []
        for index, box in enumerate(boxes):
            class_name = box["class_name"]
            class_counts[class_name] += 1
            objects.append({
                "object_index": index,
                "class_id": CLASS_TO_ID[class_name],
                "class_name": class_name,
                "bbox_xyxy": [
                    float(box["xmin"]), float(box["ymin"]),
                    float(box["xmax"]), float(box["ymax"]),
                ],
                "source_xml_sha256": xml_sha,
                "source_image_sha256": image_sha,
            })
        images.append({
            "image_id": Path(entry["image_path"]).stem,
            "image_path": entry["image_path"],
            "image_sha256": image_sha,
            "annotation_path": entry["annotation_path"],
            "annotation_sha256": xml_sha,
            "width": width,
            "height": height,
            "objects": objects,
        })

    ground_truth = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_test_ground_truth",
        "split": "test",
        "split_manifest_sha256": split_sha,
        "dataset_root": str(dataset_root.relative_to(REPO_ROOT)),
        "annotation_format": "Pascal VOC XML",
        "class_names": CLASS_NAMES,
        "class_mapping": CLASS_TO_ID,
        "duplicate_bbox_policy": "remove exact duplicate six-decimal YOLO rows, matching frozen split generator",
        "bbox_semantics": "source Pascal VOC xyxy values; evaluator IoU uses exclusive widths/heights",
        "image_count": len(images),
        "total_bbox_count": sum(len(image["objects"]) for image in images),
        "images": images,
    }
    report = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_ground_truth_conversion_report",
        "verdict": "GROUND_TRUTH_CONVERSION_PASS",
        "split_manifest_sha256": split_sha,
        "image_count": len(images),
        "image_records_complete": len(images) == 180,
        "images_with_zero_objects": sum(not image["objects"] for image in images),
        "raw_bbox_count": raw_bbox_count,
        "duplicate_bbox_count_removed": removed_duplicate_count,
        "deduplicated_bbox_count": sum(len(image["objects"]) for image in images),
        "class_bbox_distribution": class_counts,
        "class_mapping": CLASS_TO_ID,
        "cross_split_overlap": False,
        "source_tree_verification": full_dataset,
        "source_xml_and_images_modified": False,
        "pseudo_labels_generated": False,
    }
    manifest_entries = []
    for image in images:
        manifest_entries.append({
            "image_path": image["image_path"],
            "image_size": (dataset_root / image["image_path"]).stat().st_size,
            "image_sha256": image["image_sha256"],
            "annotation_path": image["annotation_path"],
            "annotation_size": (dataset_root / image["annotation_path"]).stat().st_size,
            "annotation_sha256": image["annotation_sha256"],
        })
    gt_manifest = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_ground_truth_manifest",
        "split": "test",
        "split_manifest_sha256": split_sha,
        "dataset_source_tree_sha256": EXPECTED_SOURCE_TREE_SHA,
        "image_count": len(manifest_entries),
        "entries": manifest_entries,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    write_json(output_dir / "test_ground_truth.json", ground_truth)
    write_json(output_dir / "ground_truth_conversion_report.json", report)
    write_json(output_dir / "ground_truth_manifest.json", gt_manifest)
    print(json.dumps({
        "verdict": report["verdict"],
        "image_count": report["image_count"],
        "raw_bbox_count": report["raw_bbox_count"],
        "duplicate_bbox_count_removed": report["duplicate_bbox_count_removed"],
        "deduplicated_bbox_count": report["deduplicated_bbox_count"],
        "class_bbox_distribution": report["class_bbox_distribution"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, ET.ParseError, json.JSONDecodeError) as error:
        raise SystemExit(f"ERROR: {error}") from error
