#!/usr/bin/env python3
"""Independent NumPy reference for frozen M3 PostProcessor semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[2]
CANDIDATE_COUNT = 8400
CHANNEL_COUNT = 10
ELEMENT_COUNT = CANDIDATE_COUNT * CHANNEL_COUNT
CLASS_COUNT = 6


@dataclass(frozen=True)
class Config:
    confidence_threshold: np.float32
    iou_threshold: np.float32
    max_nms: int
    max_det: int
    max_wh: np.float32
    agnostic: bool
    multi_label: bool


@dataclass(frozen=True)
class Metadata:
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


@dataclass(frozen=True)
class Candidate:
    x1: np.float32
    y1: np.float32
    x2: np.float32
    y2: np.float32
    confidence: np.float32
    class_id: int
    candidate_index: int


def f32(value: float | np.float32) -> np.float32:
    return np.float32(value)


def fadd(left: np.float32, right: np.float32) -> np.float32:
    return f32(left + right)


def fsub(left: np.float32, right: np.float32) -> np.float32:
    return f32(left - right)


def fmul(left: np.float32, right: np.float32) -> np.float32:
    return f32(left * right)


def fdiv(left: np.float32, right: np.float32) -> np.float32:
    return f32(left / right)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_relative(path: Path) -> str:
    resolved_path = path.resolve()
    try:
        return resolved_path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved_path.as_posix()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate independent M3.5 Python Detection goldens."
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=REPO_ROOT / "tests/data/postprocessor_reference",
    )
    return parser.parse_args()


def load_config(path: Path) -> Config:
    source = json.loads(path.read_text(encoding="utf-8"))
    config = Config(
        confidence_threshold=f32(source["confidence_threshold"]),
        iou_threshold=f32(source["iou_threshold"]),
        max_nms=int(source["max_nms"]),
        max_det=int(source["max_det"]),
        max_wh=f32(source["max_wh"]),
        agnostic=bool(source["agnostic"]),
        multi_label=bool(source["multi_label"]),
    )
    if not np.isfinite(config.confidence_threshold) or not 0.0 <= config.confidence_threshold <= 1.0:
        raise ValueError("invalid confidence threshold")
    if not np.isfinite(config.iou_threshold) or not 0.0 <= config.iou_threshold <= 1.0:
        raise ValueError("invalid IoU threshold")
    if config.max_det <= 0 or config.max_nms <= 0 or config.max_nms < config.max_det:
        raise ValueError("invalid NMS limits")
    if not np.isfinite(config.max_wh) or config.max_wh <= 0.0:
        raise ValueError("invalid max_wh")
    if config.agnostic or config.multi_label:
        raise ValueError("M3 reference requires agnostic=false and multi_label=false")
    return config


def load_metadata(path: Path) -> Metadata:
    source = json.loads(path.read_text(encoding="utf-8"))
    metadata = Metadata(**source)
    if metadata.original_width <= 0 or metadata.original_height <= 0:
        raise ValueError("original dimensions must be positive")
    if metadata.target_width != 640 or metadata.target_height != 640:
        raise ValueError("target dimensions must be frozen 640 by 640")
    if metadata.resized_width <= 0 or metadata.resized_height <= 0:
        raise ValueError("resized dimensions must be positive")
    if not np.isfinite(metadata.gain) or metadata.gain <= 0.0:
        raise ValueError("gain must be finite and positive")
    if min(metadata.pad_left, metadata.pad_right, metadata.pad_top, metadata.pad_bottom) < 0:
        raise ValueError("padding must be nonnegative")
    if metadata.resized_width + metadata.pad_left + metadata.pad_right != metadata.target_width:
        raise ValueError("horizontal padding is inconsistent")
    if metadata.resized_height + metadata.pad_top + metadata.pad_bottom != metadata.target_height:
        raise ValueError("vertical padding is inconsistent")
    return metadata


def load_raw(path: Path) -> np.ndarray:
    if path.stat().st_size != ELEMENT_COUNT * np.dtype("<f4").itemsize:
        raise ValueError("raw tensor byte size mismatch")
    raw = np.fromfile(path, dtype=np.dtype("<f4"))
    if raw.size != ELEMENT_COUNT or not np.isfinite(raw).all():
        raise ValueError("raw tensor must be finite BCN [1,10,8400]")
    return raw


def decode(raw: np.ndarray, config: Config) -> list[Candidate]:
    decoded: list[Candidate] = []
    for candidate_index in range(CANDIDATE_COUNT):
        cx = f32(raw[candidate_index])
        cy = f32(raw[CANDIDATE_COUNT + candidate_index])
        width = f32(raw[2 * CANDIDATE_COUNT + candidate_index])
        height = f32(raw[3 * CANDIDATE_COUNT + candidate_index])
        if width <= f32(0.0) or height <= f32(0.0):
            continue
        class_id = 0
        confidence = f32(raw[4 * CANDIDATE_COUNT + candidate_index])
        for class_index in range(1, CLASS_COUNT):
            score = f32(raw[(4 + class_index) * CANDIDATE_COUNT + candidate_index])
            if score > confidence:
                confidence = score
                class_id = class_index
        if confidence <= config.confidence_threshold:
            continue
        half_width = fdiv(width, f32(2.0))
        half_height = fdiv(height, f32(2.0))
        candidate = Candidate(
            fsub(cx, half_width),
            fsub(cy, half_height),
            fadd(cx, half_width),
            fadd(cy, half_height),
            confidence,
            class_id,
            candidate_index,
        )
        if not all(np.isfinite(value) for value in (candidate.x1, candidate.y1, candidate.x2, candidate.y2)):
            continue
        decoded.append(candidate)
    return sorted(decoded, key=lambda value: (-float(value.confidence), value.class_id, value.candidate_index))[: config.max_nms]


def continuous_iou(lhs: Candidate, rhs: Candidate, lhs_offset: np.float32, rhs_offset: np.float32) -> np.float32:
    lhs_x1, lhs_y1 = fadd(lhs.x1, lhs_offset), fadd(lhs.y1, lhs_offset)
    lhs_x2, lhs_y2 = fadd(lhs.x2, lhs_offset), fadd(lhs.y2, lhs_offset)
    rhs_x1, rhs_y1 = fadd(rhs.x1, rhs_offset), fadd(rhs.y1, rhs_offset)
    rhs_x2, rhs_y2 = fadd(rhs.x2, rhs_offset), fadd(rhs.y2, rhs_offset)
    values = (lhs_x1, lhs_y1, lhs_x2, lhs_y2, rhs_x1, rhs_y1, rhs_x2, rhs_y2)
    if not all(np.isfinite(value) for value in values):
        return f32(0.0)
    intersection_width = max(f32(0.0), fsub(min(lhs_x2, rhs_x2), max(lhs_x1, rhs_x1)))
    intersection_height = max(f32(0.0), fsub(min(lhs_y2, rhs_y2), max(lhs_y1, rhs_y1)))
    lhs_width = max(f32(0.0), fsub(lhs_x2, lhs_x1))
    lhs_height = max(f32(0.0), fsub(lhs_y2, lhs_y1))
    rhs_width = max(f32(0.0), fsub(rhs_x2, rhs_x1))
    rhs_height = max(f32(0.0), fsub(rhs_y2, rhs_y1))
    intersection_area = fmul(intersection_width, intersection_height)
    lhs_area = fmul(lhs_width, lhs_height)
    rhs_area = fmul(rhs_width, rhs_height)
    union_area = fsub(fadd(lhs_area, rhs_area), intersection_area)
    if not all(np.isfinite(value) for value in (intersection_area, lhs_area, rhs_area, union_area)) or union_area <= f32(0.0):
        return f32(0.0)
    iou = fdiv(intersection_area, union_area)
    return iou if np.isfinite(iou) else f32(0.0)


def nms(sorted_candidates: list[Candidate], config: Config) -> list[Candidate]:
    suppressed = [False] * min(len(sorted_candidates), config.max_nms)
    retained: list[Candidate] = []
    for current_index, current in enumerate(sorted_candidates[: config.max_nms]):
        if suppressed[current_index]:
            continue
        retained.append(current)
        if len(retained) == config.max_det:
            break
        current_offset = fmul(f32(current.class_id), config.max_wh)
        for later_index in range(current_index + 1, len(suppressed)):
            if suppressed[later_index]:
                continue
            later = sorted_candidates[later_index]
            later_offset = fmul(f32(later.class_id), config.max_wh)
            if continuous_iou(current, later, current_offset, later_offset) > config.iou_threshold:
                suppressed[later_index] = True
    return retained


def transform(candidates: list[Candidate], metadata: Metadata) -> list[Candidate]:
    transformed: list[Candidate] = []
    for candidate in candidates:
        def restore(value: np.float32, padding: int, extent: int) -> np.float32:
            restored = (float(value) - float(padding)) / metadata.gain
            if not np.isfinite(restored):
                raise ValueError("inverse transform produced non-finite coordinate")
            return f32(min(max(restored, 0.0), float(extent)))

        transformed.append(
            Candidate(
                restore(candidate.x1, metadata.pad_left, metadata.original_width),
                restore(candidate.y1, metadata.pad_top, metadata.original_height),
                restore(candidate.x2, metadata.pad_left, metadata.original_width),
                restore(candidate.y2, metadata.pad_top, metadata.original_height),
                candidate.confidence,
                candidate.class_id,
                candidate.candidate_index,
            )
        )
    return transformed


def format_float32(value: np.float32) -> str:
    return format(float(value), ".9g")


def write_tsv(path: Path, detections: list[Candidate]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as output:
        output.write("x1\ty1\tx2\ty2\tconfidence\tclass_id\tcandidate_index\n")
        for detection in detections:
            output.write(
                "\t".join(
                    [
                        format_float32(detection.x1),
                        format_float32(detection.y1),
                        format_float32(detection.x2),
                        format_float32(detection.y2),
                        format_float32(detection.confidence),
                        str(detection.class_id),
                        str(detection.candidate_index),
                    ]
                )
                + "\n"
            )


def write_manifest(case_dir: Path, detections: list[Candidate]) -> None:
    raw_path = case_dir / "raw_output.f32le"
    metadata_path = case_dir / "metadata.json"
    config_path = case_dir / "config.json"
    golden_path = case_dir / "python_golden_detections.tsv"
    reference_path = Path(__file__).resolve()
    generator_path = reference_path.with_name("generate_postprocessor_reference_assets.py")
    manifest = {
        "schema_version": 1,
        "evidence_id": "postprocessor_only",
        "case": case_dir.name,
        "command": "./.venv/bin/python tools/validation/postprocessor_reference.py --data-root tests/data/postprocessor_reference",
        "environment": {"python_version": platform.python_version(), "numpy_version": np.__version__},
        "raw_output": {"path": repo_relative(raw_path), "sha256": sha256_file(raw_path), "dtype": "float32", "byte_order": "little_endian", "layout": "BCN", "shape": [1, 10, 8400], "element_count": ELEMENT_COUNT},
        "metadata": {"path": repo_relative(metadata_path), "sha256": sha256_file(metadata_path)},
        "config": {"path": repo_relative(config_path), "sha256": sha256_file(config_path)},
        "python_golden_detections": {"path": repo_relative(golden_path), "sha256": sha256_file(golden_path), "format": "tsv_utf8_lf", "detection_count": len(detections)},
        "scripts": {"python_reference": {"path": repo_relative(reference_path), "sha256": sha256_file(reference_path)}, "asset_generator": {"path": repo_relative(generator_path), "sha256": sha256_file(generator_path)}},
    }
    (case_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    data_root = args.data_root.resolve()
    case_dirs = sorted(path for path in data_root.iterdir() if path.is_dir() and path.name.startswith("case_"))
    if not case_dirs:
        raise ValueError("No postprocessor reference cases found")
    for case_dir in case_dirs:
        config = load_config(case_dir / "config.json")
        metadata = load_metadata(case_dir / "metadata.json")
        raw = load_raw(case_dir / "raw_output.f32le")
        detections = transform(nms(decode(raw, config), config), metadata)
        if not all(np.isfinite(value) for detection in detections for value in (detection.x1, detection.y1, detection.x2, detection.y2, detection.confidence)):
            raise ValueError("reference generated a non-finite Detection")
        write_tsv(case_dir / "python_golden_detections.tsv", detections)
        write_manifest(case_dir, detections)
        print(f"Python Detection golden: {case_dir / 'python_golden_detections.tsv'} ({len(detections)} detections)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
