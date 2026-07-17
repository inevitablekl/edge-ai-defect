#!/usr/bin/env python3
"""Generate deterministic raw-BGR preprocessing Level A validation assets."""

from __future__ import annotations

import argparse
import hashlib
import platform
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


EXPECTED_OPENCV_VERSION = "4.10.0"
EXACT_MAE_LIMIT = 1.0e-7
EXACT_MAX_ABS_LIMIT = 1.0e-7
RESIZE_MAE_LIMIT = 5.0e-4
RESIZE_MAX_ABS_LIMIT = 2.0 / 255.0 + 1.0e-6


@dataclass(frozen=True)
class CaseDefinition:
    case_id: str
    width: int
    height: int
    target_width: int
    target_height: int
    pattern: str
    tolerance_profile: str


@dataclass(frozen=True)
class TransformMetadata:
    original_width: int
    original_height: int
    target_width: int
    target_height: int
    resized_width: int
    resized_height: int
    gain: float
    pad_left: int
    pad_right: int
    pad_top: int
    pad_bottom: int


CASES = (
    CaseDefinition("no_transform_gradient", 4, 4, 4, 4, "gradient", "exact"),
    CaseDefinition("vertical_padding", 8, 4, 8, 8, "gradient", "exact"),
    CaseDefinition("horizontal_padding", 4, 8, 8, 8, "gradient", "exact"),
    CaseDefinition("odd_horizontal_padding", 5, 8, 8, 8, "gradient", "exact"),
    CaseDefinition("non_integer_resize", 7, 5, 11, 11, "edges", "resize"),
    CaseDefinition("small_upscale", 3, 2, 16, 16, "small_colors", "resize"),
    CaseDefinition("rgb_color_blocks", 2, 2, 2, 2, "rgb_blocks", "exact"),
    CaseDefinition("frozen_640_checkerboard", 37, 53, 640, 640, "checker", "resize"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate deterministic preprocessing Level A assets."
    )
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as input_file:
        for chunk in iter(lambda: input_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def gradient_pattern(width: int, height: int) -> np.ndarray:
    y, x = np.indices((height, width), dtype=np.uint32)
    image = np.empty((height, width, 3), dtype=np.uint8)
    image[:, :, 0] = ((17 * x + 29 * y + 3 * x * y + 11) % 256).astype(np.uint8)
    image[:, :, 1] = ((53 * x + 7 * y + 5 * x * y + 23) % 256).astype(np.uint8)
    image[:, :, 2] = ((11 * x + 47 * y + 9 * x * y + 101) % 256).astype(np.uint8)
    return image


def edge_pattern(width: int, height: int) -> np.ndarray:
    image = gradient_pattern(width, height)
    y, x = np.indices((height, width), dtype=np.uint32)
    boundary = ((x >= width // 2) ^ (y >= height // 2)).astype(np.uint8)
    image[:, :, 0] = (image[:, :, 0].astype(np.uint16) + 97 * boundary) % 256
    image[:, :, 1] = (image[:, :, 1].astype(np.uint16) + 43 * (1 - boundary)) % 256
    image[:, :, 2] = (image[:, :, 2].astype(np.uint16) + 151 * boundary) % 256
    return image.astype(np.uint8)


def small_color_pattern() -> np.ndarray:
    return np.array(
        [
            [[0, 0, 255], [0, 255, 0], [255, 0, 0]],
            [[255, 255, 255], [0, 0, 0], [0, 255, 255]],
        ],
        dtype=np.uint8,
    )


def rgb_block_pattern() -> np.ndarray:
    return np.array(
        [
            [[0, 0, 255], [0, 255, 0]],
            [[255, 0, 0], [255, 255, 255]],
        ],
        dtype=np.uint8,
    )


def checker_pattern(width: int, height: int) -> np.ndarray:
    y, x = np.indices((height, width), dtype=np.uint32)
    checker = ((x // 2 + y // 3) % 2).astype(np.uint32)
    image = np.empty((height, width, 3), dtype=np.uint8)
    image[:, :, 0] = ((13 * x + 7 * y + 173 * checker + 19) % 256).astype(np.uint8)
    image[:, :, 1] = ((5 * x + 29 * y + 91 * (1 - checker) + 37) % 256).astype(np.uint8)
    image[:, :, 2] = ((31 * x + 11 * y + 127 * checker + 61) % 256).astype(np.uint8)
    return image


def make_input(case: CaseDefinition) -> np.ndarray:
    if case.pattern == "gradient":
        image = gradient_pattern(case.width, case.height)
    elif case.pattern == "edges":
        image = edge_pattern(case.width, case.height)
    elif case.pattern == "small_colors":
        image = small_color_pattern()
    elif case.pattern == "rgb_blocks":
        image = rgb_block_pattern()
    elif case.pattern == "checker":
        image = checker_pattern(case.width, case.height)
    else:
        raise ValueError(f"Unknown pattern: {case.pattern}")
    expected_shape = (case.height, case.width, 3)
    if image.shape != expected_shape or image.dtype != np.uint8:
        raise RuntimeError(
            f"{case.case_id}: input is {image.shape}/{image.dtype}, expected {expected_shape}/uint8"
        )
    return np.ascontiguousarray(image)


def preprocess_reference(
    input_bgr: np.ndarray, case: CaseDefinition
) -> tuple[np.ndarray, TransformMetadata]:
    gain = min(
        case.target_height / case.height,
        case.target_width / case.width,
    )
    resized_width = round(case.width * gain)
    resized_height = round(case.height * gain)
    horizontal_padding = case.target_width - resized_width
    vertical_padding = case.target_height - resized_height
    half_width_padding = horizontal_padding / 2.0
    half_height_padding = vertical_padding / 2.0
    pad_left = round(half_width_padding - 0.1)
    pad_right = round(half_width_padding + 0.1)
    pad_top = round(half_height_padding - 0.1)
    pad_bottom = round(half_height_padding + 0.1)

    if resized_width == case.width and resized_height == case.height:
        resized_bgr = input_bgr.copy()
    else:
        resized_bgr = cv2.resize(
            input_bgr,
            (resized_width, resized_height),
            interpolation=cv2.INTER_LINEAR,
        )
    letterboxed_bgr = cv2.copyMakeBorder(
        resized_bgr,
        pad_top,
        pad_bottom,
        pad_left,
        pad_right,
        cv2.BORDER_CONSTANT,
        value=(114, 114, 114),
    )
    expected_image_shape = (case.target_height, case.target_width, 3)
    if letterboxed_bgr.shape != expected_image_shape:
        raise RuntimeError(
            f"{case.case_id}: LetterBox is {letterboxed_bgr.shape}, expected {expected_image_shape}"
        )

    rgb_chw = letterboxed_bgr[:, :, ::-1].transpose(2, 0, 1)
    tensor = np.ascontiguousarray(rgb_chw[None], dtype=np.float32) / 255.0
    tensor = np.ascontiguousarray(tensor, dtype=np.dtype("<f4"))
    metadata = TransformMetadata(
        original_width=case.width,
        original_height=case.height,
        target_width=case.target_width,
        target_height=case.target_height,
        resized_width=resized_width,
        resized_height=resized_height,
        gain=gain,
        pad_left=pad_left,
        pad_right=pad_right,
        pad_top=pad_top,
        pad_bottom=pad_bottom,
    )
    return tensor, metadata


def render_readme() -> str:
    return """# Preprocess Level A Assets

These deterministic assets validate the production C++ `Preprocessor` against
a Python OpenCV 4.10.0 reference without image decoding. Inputs are headerless
uint8 HWC BGR bytes. Golden tensors are headerless little-endian float32 NCHW.

Regenerate from the repository root:

```bash
.venv/bin/python tools/validation/generate_preprocess_level_a.py \\
  --output-root tests/data/preprocess_level_a
```

Verify tracked asset hashes from this directory with `sha256sum -c SHA256SUMS`.
"""


def render_manifest(records: list[dict[str, object]]) -> str:
    lines = [
        "schema_version: 1",
        "reference:",
        "  implementation: tools/validation/generate_preprocess_level_a.py",
        f"  python_version: {platform.python_version()}",
        f"  numpy_version: {np.__version__}",
        f"  opencv_version: {cv2.__version__}",
        "  input_color_order: BGR",
        "  output_color_order: RGB",
        "  interpolation: INTER_LINEAR",
        "  padding_value: 114",
        "  rounding: python_ties_to_even",
        "  center: true",
        "  auto: false",
        "  scale_fill: false",
        "  scaleup: true",
        "  stride: 32",
        "tensor_format:",
        "  dtype: float32",
        "  byte_order: little_endian",
        "  layout: NCHW",
        "tolerance_profiles:",
        "  exact:",
        "    mae_limit: 1.0e-7",
        "    max_abs_limit: 1.0e-7",
        "  resize:",
        "    mae_limit: 5.0e-4",
        "    max_abs_limit: 0.00784413725490196",
        "cases:",
    ]
    metadata_fields = (
        "original_width",
        "original_height",
        "target_width",
        "target_height",
        "resized_width",
        "resized_height",
        "gain",
        "pad_left",
        "pad_right",
        "pad_top",
        "pad_bottom",
    )
    for record in records:
        metadata = record["metadata"]
        if not isinstance(metadata, TransformMetadata):
            raise TypeError("metadata record must contain TransformMetadata")
        target_shape = record["target_shape"]
        lines.extend(
            [
                f"  - id: {record['id']}",
                f"    input: {record['input']}",
                f"    input_sha256: {record['input_sha256']}",
                f"    width: {record['width']}",
                f"    height: {record['height']}",
                "    channels: 3",
                "    target_shape: [" + ", ".join(str(value) for value in target_shape) + "]",
                f"    golden_tensor: {record['golden_tensor']}",
                f"    golden_sha256: {record['golden_sha256']}",
                f"    golden_element_count: {record['golden_element_count']}",
                "    expected_metadata:",
            ]
        )
        for field in metadata_fields:
            value = getattr(metadata, field)
            rendered_value = format(value, ".17g") if isinstance(value, float) else str(value)
            lines.append(f"      {field}: {rendered_value}")
        lines.append(f"    tolerance_profile: {record['tolerance_profile']}")
    return "\n".join(lines) + "\n"


def generate(output_root: Path) -> None:
    if cv2.__version__ != EXPECTED_OPENCV_VERSION:
        raise RuntimeError(
            f"Python OpenCV must be {EXPECTED_OPENCV_VERSION}, got {cv2.__version__}"
        )
    inputs_dir = output_root / "inputs"
    golden_dir = output_root / "golden"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    golden_dir.mkdir(parents=True, exist_ok=True)

    records: list[dict[str, object]] = []
    for case in CASES:
        input_bgr = make_input(case)
        tensor, metadata = preprocess_reference(input_bgr, case)
        input_relative = Path("inputs") / f"{case.case_id}.bgr"
        golden_relative = Path("golden") / f"{case.case_id}.f32le"
        input_path = output_root / input_relative
        golden_path = output_root / golden_relative
        input_path.write_bytes(input_bgr.tobytes(order="C"))
        golden_path.write_bytes(tensor.tobytes(order="C"))
        records.append(
            {
                "id": case.case_id,
                "input": input_relative.as_posix(),
                "input_sha256": sha256_file(input_path),
                "width": case.width,
                "height": case.height,
                "target_shape": [1, 3, case.target_height, case.target_width],
                "golden_tensor": golden_relative.as_posix(),
                "golden_sha256": sha256_file(golden_path),
                "golden_element_count": int(tensor.size),
                "metadata": metadata,
                "tolerance_profile": case.tolerance_profile,
            }
        )

    readme_path = output_root / "README.md"
    manifest_path = output_root / "manifest.yaml"
    readme_path.write_text(render_readme(), encoding="utf-8")
    manifest_path.write_text(render_manifest(records), encoding="utf-8")

    checksum_paths = [readme_path, manifest_path]
    checksum_paths.extend(sorted(inputs_dir.glob("*.bgr")))
    checksum_paths.extend(sorted(golden_dir.glob("*.f32le")))
    checksum_lines = [
        f"{sha256_file(path)}  {path.relative_to(output_root).as_posix()}"
        for path in sorted(checksum_paths, key=lambda value: value.relative_to(output_root).as_posix())
    ]
    (output_root / "SHA256SUMS").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )


def main() -> int:
    args = parse_args()
    generate(args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
