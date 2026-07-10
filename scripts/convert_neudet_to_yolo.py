#!/usr/bin/env python3
"""Convert NEU-DET Pascal VOC annotations to YOLO detection format.

Expected NEU-DET raw layout:

    <raw-root>/
    ├── IMAGES/
    │   ├── *.jpg
    │   └── ...
    └── ANNOTATIONS/
        ├── *.xml
        └── ...

The script does not download data and does not invent missing labels. It fails
with explicit errors when the raw dataset path, image files, annotation files,
classes, or bounding boxes are invalid.
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


DEFAULT_OUTPUT_DIR = Path("data/yolo/neu_det")
DEFAULT_SPLIT = (0.7, 0.2, 0.1)
DEFAULT_CLASS_NAMES = (
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
)
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")


@dataclass(frozen=True)
class BoundingBox:
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
    boxes: tuple[BoundingBox, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert manually provided NEU-DET data to YOLO format."
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        required=True,
        help="Path to the manually provided NEU-DET raw dataset root.",
    )
    parser.add_argument(
        "--images-dir",
        type=Path,
        default=None,
        help="Optional image directory. Defaults to <raw-root>/IMAGES.",
    )
    parser.add_argument(
        "--annotations-dir",
        type=Path,
        default=None,
        help="Optional annotation directory. Defaults to <raw-root>/ANNOTATIONS.",
    )
    parser.add_argument(
        "--output-root",
        "--output-dir",
        dest="output_dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output YOLO dataset directory. Default: {DEFAULT_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--split",
        type=float,
        nargs=3,
        metavar=("TRAIN", "VAL", "TEST"),
        default=DEFAULT_SPLIT,
        help="Train/val/test split ratio. Default: 0.7 0.2 0.1",
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=None,
        help="Train split ratio. Use with --val-ratio and --test-ratio.",
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=None,
        help="Validation split ratio. Use with --train-ratio and --test-ratio.",
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=None,
        help="Test split ratio. Use with --train-ratio and --val-ratio.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible splitting.",
    )
    parser.add_argument(
        "--class-names",
        type=str,
        nargs="+",
        default=DEFAULT_CLASS_NAMES,
        help=(
            "Class names in YOLO id order. Defaults to the six NEU-DET classes: "
            + ", ".join(DEFAULT_CLASS_NAMES)
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read annotations and print statistics without writing files.",
    )
    return parser.parse_args()


def resolve_split(args: argparse.Namespace) -> tuple[float, float, float]:
    ratio_values = (args.train_ratio, args.val_ratio, args.test_ratio)
    if any(value is not None for value in ratio_values):
        if any(value is None for value in ratio_values):
            raise ValueError(
                "--train-ratio, --val-ratio, and --test-ratio must be provided together."
            )
        return (args.train_ratio, args.val_ratio, args.test_ratio)
    return tuple(args.split)


def validate_split(split: Sequence[float]) -> None:
    if len(split) != 3:
        raise ValueError("Split must contain train, val, and test ratios.")
    if any(value <= 0 for value in split):
        raise ValueError(f"Split ratios must be positive: {split}")
    if abs(sum(split) - 1.0) > 1e-6:
        raise ValueError(f"Split ratios must sum to 1.0: {split}")


def validate_directory(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{description} not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"{description} is not a directory: {path}")


def resolve_neudet_dirs(args: argparse.Namespace) -> tuple[Path, Path]:
    validate_directory(args.raw_root, "NEU-DET raw dataset root")

    images_dir = args.images_dir or find_existing_child(
        args.raw_root, ("IMAGES", "images", "JPEGImages")
    )
    annotations_dir = args.annotations_dir or find_existing_child(
        args.raw_root, ("ANNOTATIONS", "annotations", "Annotations")
    )

    validate_directory(images_dir, "NEU-DET image directory")
    validate_directory(annotations_dir, "NEU-DET annotation directory")
    return images_dir, annotations_dir


def find_existing_child(root: Path, names: Sequence[str]) -> Path:
    for name in names:
        candidate = root / name
        if candidate.is_dir():
            return candidate
    expected = ", ".join(str(root / name) for name in names)
    raise FileNotFoundError(f"Expected one of these directories: {expected}")


def build_image_index(images_dir: Path) -> dict[str, Path]:
    image_paths = [
        path
        for ext in IMAGE_EXTENSIONS
        for path in images_dir.rglob(f"*{ext}")
    ]
    image_paths.extend(
        path
        for ext in IMAGE_EXTENSIONS
        for path in images_dir.rglob(f"*{ext.upper()}")
    )
    if not image_paths:
        raise FileNotFoundError(f"No images found under: {images_dir}")

    index: dict[str, Path] = {}
    duplicates: list[str] = []
    for image_path in sorted(image_paths):
        key = image_path.stem
        if key in index:
            duplicates.append(key)
        index[key] = image_path
    if duplicates:
        raise ValueError(f"Duplicate image stems found: {sorted(set(duplicates))[:10]}")
    return index


def collect_samples(
    images_dir: Path,
    annotations_dir: Path,
    class_to_id: dict[str, int],
) -> list[Sample]:
    image_index = build_image_index(images_dir)
    annotation_paths = sorted(annotations_dir.rglob("*.xml"))
    if not annotation_paths:
        raise FileNotFoundError(f"No XML annotations found under: {annotations_dir}")

    samples: list[Sample] = []
    missing_images: list[str] = []
    matched_image_stems: set[str] = set()
    for annotation_path in annotation_paths:
        image_path = image_index.get(annotation_path.stem)
        if image_path is None:
            missing_images.append(annotation_path.name)
            continue
        matched_image_stems.add(image_path.stem)
        samples.append(parse_annotation(annotation_path, image_path, class_to_id))

    if missing_images:
        preview = ", ".join(missing_images[:10])
        raise FileNotFoundError(
            f"{len(missing_images)} annotations have no matching image. "
            f"Examples: {preview}"
        )
    images_without_annotations = sorted(set(image_index) - matched_image_stems)
    if images_without_annotations:
        preview = ", ".join(images_without_annotations[:10])
        raise FileNotFoundError(
            f"{len(images_without_annotations)} images have no matching XML annotation. "
            f"Examples: {preview}"
        )
    if not samples:
        raise ValueError("No valid samples found after matching images and annotations.")
    return samples


def parse_annotation(
    annotation_path: Path,
    image_path: Path,
    class_to_id: dict[str, int],
) -> Sample:
    root = ET.parse(annotation_path).getroot()
    width, height = parse_image_size(root, annotation_path)
    boxes: list[BoundingBox] = []

    for obj in root.findall("object"):
        class_name = read_required_text(obj, "name", annotation_path)
        if class_name not in class_to_id:
            raise ValueError(
                f"Unknown class '{class_name}' in {annotation_path}. "
                f"Known classes: {sorted(class_to_id)}"
            )

        bndbox = obj.find("bndbox")
        if bndbox is None:
            raise ValueError(f"Missing bndbox in {annotation_path}")

        box = BoundingBox(
            class_name=class_name,
            xmin=parse_float(bndbox, "xmin", annotation_path),
            ymin=parse_float(bndbox, "ymin", annotation_path),
            xmax=parse_float(bndbox, "xmax", annotation_path),
            ymax=parse_float(bndbox, "ymax", annotation_path),
        )
        validate_box(box, width, height, annotation_path)
        boxes.append(box)

    if not boxes:
        raise ValueError(f"No objects found in annotation: {annotation_path}")
    return Sample(
        image_path=image_path,
        annotation_path=annotation_path,
        width=width,
        height=height,
        boxes=tuple(boxes),
    )


def parse_image_size(root: ET.Element, annotation_path: Path) -> tuple[int, int]:
    size = root.find("size")
    if size is None:
        raise ValueError(f"Missing size field in annotation: {annotation_path}")

    width_text = read_required_text(size, "width", annotation_path)
    height_text = read_required_text(size, "height", annotation_path)
    width = int(float(width_text))
    height = int(float(height_text))
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid image size in {annotation_path}: {width}x{height}")
    return width, height


def read_required_text(node: ET.Element, tag: str, annotation_path: Path) -> str:
    child = node.find(tag)
    if child is None or child.text is None or not child.text.strip():
        raise ValueError(f"Missing required tag '{tag}' in {annotation_path}")
    return child.text.strip()


def parse_float(node: ET.Element, tag: str, annotation_path: Path) -> float:
    value = read_required_text(node, tag, annotation_path)
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(
            f"Invalid numeric value for {tag} in {annotation_path}: {value}"
        ) from exc


def validate_box(box: BoundingBox, width: int, height: int, annotation_path: Path) -> None:
    if box.xmax <= box.xmin or box.ymax <= box.ymin:
        raise ValueError(f"Invalid bbox with non-positive area in {annotation_path}: {box}")
    if box.xmin < 0 or box.ymin < 0 or box.xmax > width or box.ymax > height:
        raise ValueError(
            f"Bbox out of image bounds in {annotation_path}: {box}, image={width}x{height}"
        )


def split_samples(
    samples: Sequence[Sample],
    split: Sequence[float],
    seed: int,
) -> dict[str, list[Sample]]:
    shuffled = list(samples)
    random.Random(seed).shuffle(shuffled)

    total = len(shuffled)
    train_count = int(total * split[0])
    val_count = int(total * split[1])
    test_count = total - train_count - val_count

    return {
        "train": shuffled[:train_count],
        "val": shuffled[train_count:train_count + val_count],
        "test": shuffled[train_count + val_count:train_count + val_count + test_count],
    }


def yolo_lines(sample: Sample, class_to_id: dict[str, int]) -> list[str]:
    lines = []
    for box in sample.boxes:
        class_id = class_to_id[box.class_name]
        x_center = ((box.xmin + box.xmax) / 2.0) / sample.width
        y_center = ((box.ymin + box.ymax) / 2.0) / sample.height
        box_width = (box.xmax - box.xmin) / sample.width
        box_height = (box.ymax - box.ymin) / sample.height
        normalized = (x_center, y_center, box_width, box_height)
        if any(value < 0.0 or value > 1.0 for value in normalized):
            raise ValueError(f"Normalized bbox out of range for {sample.annotation_path}: {normalized}")
        lines.append(
            f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"
        )
    return lines


def write_dataset(
    split_map: dict[str, list[Sample]],
    output_dir: Path,
    class_names: Sequence[str],
) -> None:
    class_to_id = class_index(class_names)
    for split_name, samples in split_map.items():
        image_dir = output_dir / "images" / split_name
        label_dir = output_dir / "labels" / split_name
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)
        for sample in samples:
            shutil.copy2(sample.image_path, image_dir / sample.image_path.name)
            label_path = label_dir / f"{sample.image_path.stem}.txt"
            label_path.write_text(
                "\n".join(yolo_lines(sample, class_to_id)) + "\n",
                encoding="utf-8",
            )
    write_dataset_yaml(output_dir, class_names)


def class_index(class_names: Sequence[str]) -> dict[str, int]:
    return {class_name: idx for idx, class_name in enumerate(class_names)}


def write_dataset_yaml(output_dir: Path, class_names: Sequence[str]) -> None:
    names = "\n".join(f"  {idx}: {name}" for idx, name in enumerate(class_names))
    (output_dir / "dataset.yaml").write_text(
        "\n".join(
            [
                f"path: {output_dir.as_posix()}",
                "train: images/train",
                "val: images/val",
                "test: images/test",
                "names:",
                names,
                "",
            ]
        ),
        encoding="utf-8",
    )


def class_counts(samples: Sequence[Sample]) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for sample in samples:
        counter.update(box.class_name for box in sample.boxes)
    return dict(sorted(counter.items()))


def build_manifest(
    args: argparse.Namespace,
    images_dir: Path,
    annotations_dir: Path,
    samples: Sequence[Sample],
    split_map: dict[str, list[Sample]],
) -> dict[str, object]:
    split_counts = {split_name: len(items) for split_name, items in split_map.items()}
    split_class_counts = {
        split_name: class_counts(items) for split_name, items in split_map.items()
    }
    return {
        "source_dataset": "NEU-DET / NEU Surface Defect Database",
        "raw_root": str(args.raw_root),
        "images_dir": str(images_dir),
        "annotations_dir": str(annotations_dir),
        "output_dir": str(args.output_dir),
        "image_count": len(samples),
        "annotation_count": len(samples),
        "bbox_count": sum(len(sample.boxes) for sample in samples),
        "class_count": len(args.class_names),
        "class_names": list(args.class_names),
        "class_counts": class_counts(samples),
        "split_ratio": list(args.split),
        "split_seed": args.seed,
        "split_counts": split_counts,
        "split_class_counts": split_class_counts,
        "abnormal_sample_count": 0,
        "abnormal_samples": {
            "missing_images": [],
            "images_without_annotations": [],
            "unknown_classes": [],
            "invalid_bboxes": [],
            "empty_annotations": [],
        },
        "dry_run": args.dry_run,
    }


def write_manifest(output_dir: Path, manifest: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "conversion_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def print_summary(manifest: dict[str, object]) -> None:
    print("NEU-DET conversion summary")
    print(f"  raw_root: {manifest['raw_root']}")
    print(f"  images_dir: {manifest['images_dir']}")
    print(f"  annotations_dir: {manifest['annotations_dir']}")
    print(f"  output_dir: {manifest['output_dir']}")
    print(f"  image_count: {manifest['image_count']}")
    print(f"  bbox_count: {manifest['bbox_count']}")
    print(f"  class_count: {manifest['class_count']}")
    print(f"  split_seed: {manifest['split_seed']}")
    print(f"  split_counts: {manifest['split_counts']}")
    print(f"  class_counts: {manifest['class_counts']}")


def main() -> int:
    try:
        args = parse_args()
        args.class_names = tuple(args.class_names)
        args.split = resolve_split(args)
        validate_split(args.split)
        images_dir, annotations_dir = resolve_neudet_dirs(args)
        class_to_id = class_index(args.class_names)
        samples = collect_samples(images_dir, annotations_dir, class_to_id)
        split_map = split_samples(samples, args.split, args.seed)
        manifest = build_manifest(args, images_dir, annotations_dir, samples, split_map)
        print_summary(manifest)

        if args.dry_run:
            print("Dry run complete. No files were written.")
            return 0

        write_dataset(split_map, args.output_dir, args.class_names)
        write_manifest(args.output_dir, manifest)
        print(f"Conversion complete: {args.output_dir}")
        return 0
    except (FileNotFoundError, NotADirectoryError, ValueError, ET.ParseError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
