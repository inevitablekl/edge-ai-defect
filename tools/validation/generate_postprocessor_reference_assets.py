#!/usr/bin/env python3
"""Generate deterministic synthetic assets for M3.5 PostProcessor-only Validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
SHAPE = (1, 10, 8400)
CHANNEL_COUNT = 10
CANDIDATE_COUNT = 8400
CONFIG = {
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45,
    "max_nms": 30000,
    "max_det": 300,
    "max_wh": 7680.0,
    "agnostic": False,
    "multi_label": False,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate fixed BCN assets without ORT or Ultralytics."
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "tests/data/postprocessor_reference",
    )
    return parser.parse_args()


def set_candidate(
    raw: np.ndarray,
    candidate_index: int,
    cx: float,
    cy: float,
    width: float,
    height: float,
    class_scores: dict[int, float],
) -> None:
    raw[0 * CANDIDATE_COUNT + candidate_index] = np.float32(cx)
    raw[1 * CANDIDATE_COUNT + candidate_index] = np.float32(cy)
    raw[2 * CANDIDATE_COUNT + candidate_index] = np.float32(width)
    raw[3 * CANDIDATE_COUNT + candidate_index] = np.float32(height)
    for class_id, score in class_scores.items():
        raw[(4 + class_id) * CANDIDATE_COUNT + candidate_index] = np.float32(score)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_case(
    root: Path,
    name: str,
    metadata: dict[str, object],
    candidates: list[dict[str, object]],
) -> None:
    case_dir = root / name
    case_dir.mkdir(parents=True, exist_ok=True)
    raw = np.zeros(CHANNEL_COUNT * CANDIDATE_COUNT, dtype=np.dtype("<f4"))
    for candidate in candidates:
        set_candidate(
            raw,
            int(candidate["candidate_index"]),
            float(candidate["cx"]),
            float(candidate["cy"]),
            float(candidate["width"]),
            float(candidate["height"]),
            {int(key): float(value) for key, value in candidate["class_scores"].items()},
        )
    raw.tofile(case_dir / "raw_output.f32le")
    write_json(case_dir / "metadata.json", metadata)
    write_json(case_dir / "config.json", CONFIG)
    write_json(
        case_dir / "asset_description.json",
        {"case": name, "shape": list(SHAPE), "candidates": candidates},
    )


def main() -> int:
    args = parse_args()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    write_case(
        output_root,
        "case_no_padding",
        {
            "original_width": 640,
            "original_height": 640,
            "target_width": 640,
            "target_height": 640,
            "resized_width": 640,
            "resized_height": 640,
            "gain": 1.0,
            "pad_left": 0,
            "pad_right": 0,
            "pad_top": 0,
            "pad_bottom": 0,
        },
        [
            {"candidate_index": 100, "cx": 200.0, "cy": 200.0, "width": 100.0, "height": 100.0, "class_scores": {"0": 0.95}},
            {"candidate_index": 101, "cx": 205.0, "cy": 205.0, "width": 100.0, "height": 100.0, "class_scores": {"0": 0.90}},
            {"candidate_index": 102, "cx": 200.0, "cy": 200.0, "width": 100.0, "height": 100.0, "class_scores": {"1": 0.90}},
            {"candidate_index": 103, "cx": 300.0, "cy": 100.0, "width": 20.0, "height": 20.0, "class_scores": {"2": 0.25}},
            {"candidate_index": 104, "cx": 350.0, "cy": 100.0, "width": 20.0, "height": 20.0, "class_scores": {"2": float(np.nextafter(np.float32(0.25), np.float32(np.inf)))}},
            {"candidate_index": 105, "cx": 400.0, "cy": 100.0, "width": 20.0, "height": 20.0, "class_scores": {"3": 0.80, "4": 0.80}},
            {"candidate_index": 106, "cx": 450.0, "cy": 100.0, "width": 20.0, "height": 20.0, "class_scores": {"5": 0.70}},
            {"candidate_index": 107, "cx": 500.0, "cy": 100.0, "width": 20.0, "height": 20.0, "class_scores": {"5": 0.70}},
            {"candidate_index": 108, "cx": 550.0, "cy": 100.0, "width": 20.0, "height": 20.0, "class_scores": {"0": 0.60}},
        ],
    )

    write_case(
        output_root,
        "case_odd_padding",
        {
            "original_width": 480,
            "original_height": 641,
            "target_width": 640,
            "target_height": 640,
            "resized_width": 479,
            "resized_height": 640,
            "gain": 640.0 / 641.0,
            "pad_left": 80,
            "pad_right": 81,
            "pad_top": 0,
            "pad_bottom": 0,
        },
        [
            {"candidate_index": 200, "cx": 150.0, "cy": 150.0, "width": 100.0, "height": 100.0, "class_scores": {"0": 0.95}},
            {"candidate_index": 201, "cx": 90.0, "cy": 10.0, "width": 60.0, "height": 60.0, "class_scores": {"1": 0.90}},
            {"candidate_index": 202, "cx": 600.0, "cy": 650.0, "width": 200.0, "height": 200.0, "class_scores": {"2": 0.85}},
            {"candidate_index": 203, "cx": -75.0, "cy": 125.0, "width": 50.0, "height": 50.0, "class_scores": {"3": 0.80}},
            {"candidate_index": 204, "cx": 125.0, "cy": 725.0, "width": 50.0, "height": 50.0, "class_scores": {"4": 0.75}},
        ],
    )

    write_case(
        output_root,
        "case_odd_vertical_padding",
        {
            "original_width": 641,
            "original_height": 480,
            "target_width": 640,
            "target_height": 640,
            "resized_width": 640,
            "resized_height": 479,
            "gain": 640.0 / 641.0,
            "pad_left": 0,
            "pad_right": 0,
            "pad_top": 80,
            "pad_bottom": 81,
        },
        [
            {"candidate_index": 300, "cx": 150.0, "cy": 150.0, "width": 100.0, "height": 100.0, "class_scores": {"0": 0.95}},
            {"candidate_index": 301, "cx": 10.0, "cy": 90.0, "width": 60.0, "height": 60.0, "class_scores": {"1": 0.90}},
            {"candidate_index": 302, "cx": 650.0, "cy": 600.0, "width": 200.0, "height": 200.0, "class_scores": {"2": 0.85}},
            {"candidate_index": 303, "cx": 125.0, "cy": -75.0, "width": 50.0, "height": 50.0, "class_scores": {"3": 0.80}},
            {"candidate_index": 304, "cx": 725.0, "cy": 125.0, "width": 50.0, "height": 50.0, "class_scores": {"4": 0.75}},
        ],
    )

    (output_root / "README.txt").write_text(
        "M3.5 PostProcessor-only Validation assets.\n"
        "raw_output.f32le is headerless little-endian float32 BCN [1,10,8400].\n"
        "Run postprocessor_reference.py after this generator to write golden TSV and manifests.\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Generated PostProcessor reference assets: {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
