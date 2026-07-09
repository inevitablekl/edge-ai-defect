#!/usr/bin/env python3
"""Skeleton for converting NEU-DET annotations into YOLO dataset layout.

This script intentionally does not assume the dataset is present. It validates
input paths, prepares the target directory structure, and leaves the actual
NEU-DET annotation parsing as an explicit implementation step.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


DEFAULT_OUTPUT_DIR = Path("data/yolo/neu_det")
DEFAULT_SPLIT = (0.7, 0.2, 0.1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a NEU-DET to YOLO conversion run without assuming data exists."
    )
    parser.add_argument(
        "--raw-root",
        type=Path,
        required=True,
        help="Path to the manually provided NEU-DET raw dataset root.",
    )
    parser.add_argument(
        "--output-dir",
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
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible splitting.",
    )
    parser.add_argument(
        "--class-names",
        type=str,
        nargs="+",
        required=True,
        help="Class names in the order used by YOLO labels.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and print planned outputs without writing files.",
    )
    return parser.parse_args()


def validate_split(split: Sequence[float]) -> None:
    if len(split) != 3:
        raise ValueError("Split must contain train, val, and test ratios.")
    if any(value <= 0 for value in split):
        raise ValueError(f"Split ratios must be positive: {split}")
    if abs(sum(split) - 1.0) > 1e-6:
        raise ValueError(f"Split ratios must sum to 1.0: {split}")


def validate_raw_root(raw_root: Path) -> None:
    if not raw_root.exists():
        raise FileNotFoundError(
            f"NEU-DET raw dataset root not found: {raw_root}. "
            "Provide the dataset manually; this script does not download data."
        )
    if not raw_root.is_dir():
        raise NotADirectoryError(f"NEU-DET raw root is not a directory: {raw_root}")


def planned_yolo_layout(output_dir: Path) -> list[Path]:
    return [
        output_dir / "images" / "train",
        output_dir / "images" / "val",
        output_dir / "images" / "test",
        output_dir / "labels" / "train",
        output_dir / "labels" / "val",
        output_dir / "labels" / "test",
    ]


def write_dataset_yaml(output_dir: Path, class_names: Sequence[str]) -> None:
    yaml_path = output_dir / "dataset.yaml"
    names = "\n".join(f"  {idx}: {name}" for idx, name in enumerate(class_names))
    yaml_path.write_text(
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


def write_conversion_manifest(args: argparse.Namespace) -> None:
    manifest_path = args.output_dir / "conversion_manifest.json"
    manifest = {
        "source_dataset": "NEU-DET / NEU Surface Defect Database",
        "raw_root": str(args.raw_root),
        "output_dir": str(args.output_dir),
        "split": list(args.split),
        "seed": args.seed,
        "class_names": list(args.class_names),
        "status": "skeleton_prepared",
        "note": "Annotation parsing and label conversion are not implemented yet.",
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    validate_split(args.split)
    validate_raw_root(args.raw_root)

    layout = planned_yolo_layout(args.output_dir)
    print("Planned YOLO output layout:")
    for path in layout:
        print(f"  {path}")

    if args.dry_run:
        print("Dry run complete. No files were written.")
        return 0

    for path in layout:
        path.mkdir(parents=True, exist_ok=True)
    write_dataset_yaml(args.output_dir, args.class_names)
    write_conversion_manifest(args)

    raise NotImplementedError(
        "NEU-DET annotation parsing is not implemented yet. "
        "Add parsing after confirming the raw dataset directory layout."
    )


if __name__ == "__main__":
    raise SystemExit(main())
