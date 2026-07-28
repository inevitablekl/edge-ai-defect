#!/usr/bin/env python3
"""Generate the frozen Stage K task-evaluation train/val/test manifests.

The split semantics intentionally match scripts/convert_neudet_to_yolo.py:
sorted annotation paths, exact duplicate YOLO bbox-row removal, then
random.Random(seed).shuffle and 70/20/10 slicing. This script only reads the
raw dataset and writes metadata/manifests under the requested output root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_RAW_ROOT = Path("data/raw/NEU-DET")
DEFAULT_OUTPUT_ROOT = Path("results/validation/stage_k_task_eval_v2/split")
DEFAULT_SEED = 42
SPLIT_RATIOS = (0.7, 0.2, 0.1)
CLASS_NAMES = (
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
)
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


@dataclass(frozen=True)
class Box:
    class_name: str
    xmin: float
    ymin: float
    xmax: float
    ymax: float


@dataclass(frozen=True)
class Sample:
    image_path: Path
    annotation_path: Path
    width: int
    height: int
    boxes: tuple[Box, ...]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(node: ET.Element, tag: str, path: Path) -> str:
    child = node.find(tag)
    if child is None or child.text is None or not child.text.strip():
        raise ValueError(f"Missing required '{tag}' in {path}")
    return child.text.strip()


def parse_float(node: ET.Element, tag: str, path: Path) -> float:
    try:
        return float(read_text(node, tag, path))
    except ValueError as exc:
        raise ValueError(f"Invalid '{tag}' in {path}") from exc


def parse_sample(image_path: Path, annotation_path: Path) -> Sample:
    root = ET.parse(annotation_path).getroot()
    if root.tag != "annotation":
        raise ValueError(f"Unexpected XML root in {annotation_path}: {root.tag}")
    size = root.find("size")
    if size is None:
        raise ValueError(f"Missing size in {annotation_path}")
    width = int(float(read_text(size, "width", annotation_path)))
    height = int(float(read_text(size, "height", annotation_path)))
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image size in {annotation_path}")

    boxes: list[Box] = []
    for object_node in root.findall("object"):
        class_name = read_text(object_node, "name", annotation_path)
        if class_name not in CLASS_NAMES:
            raise ValueError(f"Unknown class '{class_name}' in {annotation_path}")
        bndbox = object_node.find("bndbox")
        if bndbox is None:
            raise ValueError(f"Missing bndbox in {annotation_path}")
        box = Box(
            class_name=class_name,
            xmin=parse_float(bndbox, "xmin", annotation_path),
            ymin=parse_float(bndbox, "ymin", annotation_path),
            xmax=parse_float(bndbox, "xmax", annotation_path),
            ymax=parse_float(bndbox, "ymax", annotation_path),
        )
        if box.xmax <= box.xmin or box.ymax <= box.ymin:
            raise ValueError(f"Non-positive bbox in {annotation_path}")
        if box.xmin < 0 or box.ymin < 0 or box.xmax > width or box.ymax > height:
            raise ValueError(f"Out-of-bounds bbox in {annotation_path}")
        boxes.append(box)
    if not boxes:
        raise ValueError(f"No objects in {annotation_path}")
    return Sample(image_path, annotation_path, width, height, tuple(boxes))


def yolo_row(sample: Sample, box: Box) -> str:
    class_id = CLASS_NAMES.index(box.class_name)
    x_center = ((box.xmin + box.xmax) / 2.0) / sample.width
    y_center = ((box.ymin + box.ymax) / 2.0) / sample.height
    box_width = (box.xmax - box.xmin) / sample.width
    box_height = (box.ymax - box.ymin) / sample.height
    return f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"


def deduplicate(sample: Sample) -> tuple[Sample, int]:
    seen: set[str] = set()
    unique: list[Box] = []
    removed = 0
    for box in sample.boxes:
        row = yolo_row(sample, box)
        if row in seen:
            removed += 1
            continue
        seen.add(row)
        unique.append(box)
    return Sample(sample.image_path, sample.annotation_path, sample.width, sample.height, tuple(unique)), removed


def collect_samples(raw_root: Path) -> tuple[list[Sample], dict[str, int]]:
    images_dir = raw_root / "IMAGES"
    annotations_dir = raw_root / "ANNOTATIONS"
    if not images_dir.is_dir() or not annotations_dir.is_dir():
        raise FileNotFoundError(f"Expected IMAGES and ANNOTATIONS under {raw_root}")

    image_paths = sorted(
        path
        for extension in IMAGE_EXTENSIONS
        for path in images_dir.rglob(f"*{extension}")
    )
    image_index: dict[str, Path] = {}
    for image_path in image_paths:
        if image_path.stem in image_index:
            raise ValueError(f"Duplicate image stem: {image_path.stem}")
        image_index[image_path.stem] = image_path

    annotation_paths = sorted(annotations_dir.rglob("*.xml"))
    samples: list[Sample] = []
    for annotation_path in annotation_paths:
        image_path = image_index.get(annotation_path.stem)
        if image_path is None:
            raise ValueError(f"Annotation without image: {annotation_path}")
        samples.append(parse_sample(image_path, annotation_path))
    annotation_stems = {path.stem for path in annotation_paths}
    missing_annotations = sorted(set(image_index) - annotation_stems)
    if missing_annotations:
        raise ValueError(f"Images without annotations: {missing_annotations[:10]}")
    if len(samples) != 1800:
        raise ValueError(f"Expected 1800 matched samples, found {len(samples)}")

    raw_bbox_count = sum(len(sample.boxes) for sample in samples)
    deduplicated: list[Sample] = []
    duplicate_count = 0
    for sample in samples:
        clean_sample, removed = deduplicate(sample)
        deduplicated.append(clean_sample)
        duplicate_count += removed
    return deduplicated, {
        "raw_bbox_count": raw_bbox_count,
        "duplicate_bbox_count_removed": duplicate_count,
        "deduplicated_bbox_count": sum(len(sample.boxes) for sample in deduplicated),
    }


def split_samples(samples: list[Sample], seed: int) -> dict[str, list[Sample]]:
    shuffled = list(samples)
    random.Random(seed).shuffle(shuffled)
    train_count = int(len(shuffled) * SPLIT_RATIOS[0])
    val_count = int(len(shuffled) * SPLIT_RATIOS[1])
    return {
        "train": shuffled[:train_count],
        "val": shuffled[train_count:train_count + val_count],
        "test": shuffled[train_count + val_count:],
    }


def entry(sample: Sample, raw_root: Path) -> dict[str, object]:
    return {
        "image_path": sample.image_path.relative_to(raw_root).as_posix(),
        "image_sha256": sha256(sample.image_path),
        "annotation_path": sample.annotation_path.relative_to(raw_root).as_posix(),
        "annotation_sha256": sha256(sample.annotation_path),
        "class_list": [name for name in CLASS_NAMES if any(box.class_name == name for box in sample.boxes)],
        "bbox_count": len(sample.boxes),
    }


def manifest_payload(split_name: str, samples: list[Sample], raw_root: Path, seed: int, dedup_stats: dict[str, int]) -> dict[str, object]:
    entries = [entry(sample, raw_root) for sample in samples]
    class_image_counter = Counter(
        name for item in entries for name in item["class_list"]
    )
    class_bbox_counter = Counter(
        box.class_name for sample in samples for box in sample.boxes
    )
    return {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_split_manifest",
        "split": split_name,
        "dataset_root": str(raw_root),
        "split_ratio": list(SPLIT_RATIOS),
        "random_seed": seed,
        "ordering": "sorted XML paths then random.Random(seed).shuffle",
        "duplicate_bbox_policy": "remove exact duplicate YOLO rows before splitting",
        "class_names": list(CLASS_NAMES),
        "deduplication": dedup_stats,
        "entry_count": len(entries),
        "bbox_count": sum(int(item["bbox_count"]) for item in entries),
        "class_image_distribution": dict(sorted(class_image_counter.items())),
        "class_bbox_distribution": dict(sorted(class_bbox_counter.items())),
        "entries": entries,
    }


def canonical_json(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False) + "\n").encode("utf-8")


def write_json(path: Path, payload: dict[str, object]) -> str:
    content = canonical_json(payload)
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = parser.parse_args()

    samples, dedup_stats = collect_samples(args.raw_root)
    split_map = split_samples(samples, args.seed)
    repeat_map = split_samples(samples, args.seed)
    if [[sample.image_path for sample in split_map[name]] for name in ("train", "val", "test")] != [[sample.image_path for sample in repeat_map[name]] for name in ("train", "val", "test")]:
        raise AssertionError("Same-seed split reproducibility check failed")

    manifests = {
        name: manifest_payload(name, split_map[name], args.raw_root, args.seed, dedup_stats)
        for name in ("train", "val", "test")
    }
    repeat_manifests = {
        name: manifest_payload(name, repeat_map[name], args.raw_root, args.seed, dedup_stats)
        for name in ("train", "val", "test")
    }
    output_root = args.output_root
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_hashes = {}
    repeat_hashes = {}
    for name, payload in manifests.items():
        manifest_hashes[name] = write_json(output_root / f"{name}_manifest.json", payload)
        repeat_hashes[name] = hashlib.sha256(canonical_json(repeat_manifests[name])).hexdigest()

    split_sets = {name: {item["image_path"] for item in payload["entries"]} for name, payload in manifests.items()}
    overlap_pairs = {}
    names = ("train", "val", "test")
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            overlap_pairs[f"{left}_vs_{right}"] = sorted(split_sets[left] & split_sets[right])
    metadata = {
        "schema_version": 1,
        "artifact_kind": "stage_k_task_eval_v2_split_metadata",
        "dataset_root": str(args.raw_root),
        "random_seed": args.seed,
        "split_ratio": list(SPLIT_RATIOS),
        "class_names": list(CLASS_NAMES),
        "counts": {name: len(payload["entries"]) for name, payload in manifests.items()},
        "bbox_counts": {name: payload["bbox_count"] for name, payload in manifests.items()},
        "class_image_distributions": {name: payload["class_image_distribution"] for name, payload in manifests.items()},
        "class_bbox_distributions": {name: payload["class_bbox_distribution"] for name, payload in manifests.items()},
        "deduplication": dedup_stats,
        "manifest_sha256": manifest_hashes,
        "reproducibility_check": {
            "same_seed": args.seed,
            "repeat_manifest_sha256": repeat_hashes,
            "all_manifest_hashes_match": manifest_hashes == repeat_hashes,
        },
        "overlap_check": {
            "pairs": overlap_pairs,
            "no_overlap": all(not values for values in overlap_pairs.values()),
        },
    }
    write_json(output_root / "split_metadata.json", metadata)
    print(json.dumps({
        "output_root": str(output_root),
        "counts": metadata["counts"],
        "bbox_counts": metadata["bbox_counts"],
        "manifest_sha256": manifest_hashes,
        "reproducibility": metadata["reproducibility_check"],
        "no_overlap": metadata["overlap_check"]["no_overlap"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
