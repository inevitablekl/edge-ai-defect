#!/usr/bin/env python3
"""Minimal Stage K Level B raw-output comparator.

This tool compares the raw-output manifests emitted by
``stage_k_raw_tensor_runner``.  It intentionally owns only tensor identity,
numeric comparison, policy gates, and ORT repeatability checks; it does not
implement Level C or threshold-boundary diagnostics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


SHAPE = [1, 10, 8400]
COUNT = 84000
BYTE_SIZE = COUNT * 4
DTYPE = "float32"
BYTE_ORDER = "little_endian"
LAYOUT = "BCN"

POLICIES: dict[str, dict[str, float]] = {
    "ort_strict": {
        "overall_mae": 1e-6,
        "overall_max_abs": 1e-4,
    },
    "ort_cross_arch": {
        "overall_mae": 1e-5,
        "overall_max_abs": 0.01,
        "bbox_max_abs": 0.01,
        "score_max_abs": 1e-4,
    },
    "tensorrt_fp16": {
        "score_mae": 2e-3,
        "score_p99": 5e-3,
        "score_max_abs": 2e-2,
        "bbox_mae": 0.5,
        "bbox_p99": 1.5,
        "bbox_max_abs": 4.0,
    },
}


class CompareError(ValueError):
    """Malformed or numerically invalid comparison input."""


def _duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise CompareError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise CompareError(f"non-finite JSON constant: {value}")


def read_strict_json(path: Path) -> Any:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise CompareError(f"cannot read JSON {path}: {exc}") from exc
    if not raw.endswith("\n") or raw.endswith("\n\n"):
        raise CompareError(f"JSON must end with exactly one LF: {path}")
    try:
        return json.loads(raw, object_pairs_hook=_duplicate_pairs,
                          parse_constant=_reject_constant)
    except (json.JSONDecodeError, CompareError) as exc:
        raise CompareError(f"invalid strict JSON {path}: {exc}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    except OSError as exc:
        raise CompareError(f"cannot read raw output {path}: {exc}") from exc
    return digest.hexdigest()


def type7_p99(values: np.ndarray) -> float:
    """Hyndman--Fan Type 7 quantile, aligned with the frozen M5 helper."""
    flat = np.asarray(values, dtype=np.float64).reshape(-1)
    if flat.size == 0 or not np.isfinite(flat).all():
        raise CompareError("Type-7 requires finite, non-empty values")
    ordered = np.sort(flat)
    h = (ordered.size - 1) * 0.99
    lower = int(math.floor(h))
    upper = int(math.ceil(h))
    return float(ordered[lower] + (h - lower) * (ordered[upper] - ordered[lower]))


def _require_mapping(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CompareError(f"{where} must be an object")
    return value


def _require_string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value:
        raise CompareError(f"{where} must be a non-empty string")
    return value


def _require_int(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise CompareError(f"{where} must be a non-negative integer")
    return value


def _validate_tensor_entry(entry: Any, manifest_path: Path, index: int) -> dict[str, Any]:
    value = _require_mapping(entry, f"{manifest_path}: entries[{index}]")
    image_id = _require_string(value.get("image_id"), f"entries[{index}].image_id")
    output_name = _require_string(value.get("output_filename"),
                                  f"entries[{index}].output_filename")
    output_sha = _require_string(value.get("output_sha256"),
                                 f"entries[{index}].output_sha256")
    if len(output_sha) != 64 or any(c not in "0123456789abcdef" for c in output_sha):
        raise CompareError(f"entries[{index}].output_sha256 is not lowercase SHA256")
    input_sha = _require_string(value.get("input_sha256"), f"entries[{index}].input_sha256")
    if len(input_sha) != 64 or any(c not in "0123456789abcdef" for c in input_sha):
        raise CompareError(f"entries[{index}].input_sha256 is not lowercase SHA256")
    if value.get("dtype") != DTYPE or value.get("byte_order") != BYTE_ORDER or value.get("layout") != LAYOUT:
        raise CompareError(f"entries[{index}] tensor contract mismatch")
    if value.get("shape") != SHAPE or _require_int(value.get("element_count"), f"entries[{index}].element_count") != COUNT:
        raise CompareError(f"entries[{index}] shape/element_count mismatch")
    if _require_int(value.get("output_byte_size"), f"entries[{index}].output_byte_size") != BYTE_SIZE:
        raise CompareError(f"entries[{index}] output byte size mismatch")
    if _require_int(value.get("finite_count"), f"entries[{index}].finite_count") != COUNT:
        raise CompareError(f"entries[{index}] finite_count is not exact")
    if value.get("status") != "success":
        raise CompareError(f"entries[{index}] status is not success")
    path = (manifest_path.parent / output_name).resolve()
    if path.is_symlink() or not path.is_file():
        raise CompareError(f"output is not a regular file: {path}")
    if path.stat().st_size != BYTE_SIZE:
        raise CompareError(f"output byte size differs on disk: {path}")
    actual_sha = sha256_file(path)
    if actual_sha != output_sha:
        raise CompareError(f"output SHA256 mismatch for {image_id}")
    raw = path.read_bytes()
    values = np.frombuffer(raw, dtype="<f4")
    if values.size != COUNT or not np.isfinite(values).all():
        raise CompareError(f"output is not finite float32 BCN: {image_id}")
    result = dict(value)
    result["_path"] = path
    result["_values"] = values
    return result


def load_manifest(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    root = _require_mapping(read_strict_json(path), str(path))
    if root.get("schema_version") != 1 or root.get("artifact_kind") != "stage_k_raw_tensor_output_manifest":
        raise CompareError(f"unsupported raw output manifest: {path}")
    entries_value = root.get("entries")
    if not isinstance(entries_value, list) or not entries_value:
        raise CompareError(f"manifest entries must be a non-empty array: {path}")
    entries = [_validate_tensor_entry(entry, path, index)
               for index, entry in enumerate(entries_value)]
    entries.sort(key=lambda item: item["image_id"])
    ids = [item["image_id"] for item in entries]
    if len(ids) != len(set(ids)):
        raise CompareError(f"duplicate image_id in manifest: {path}")
    return root, entries


def _identity(entry: dict[str, Any]) -> tuple[str, str, str, str, list[int]]:
    return (entry["image_id"], entry["input_filename"], entry["input_sha256"],
            entry["dtype"], entry["shape"])


def _metric(reference: np.ndarray, candidate: np.ndarray) -> dict[str, float | int]:
    error = np.abs(reference.astype(np.float64) - candidate.astype(np.float64))
    return {
        "element_count": int(error.size),
        "mae": float(np.mean(error)),
        "max_abs": float(np.max(error)),
        "type7_p99": type7_p99(error),
    }


def _gate(metric: dict[str, float | int], limits: dict[str, float], prefix: str) -> bool:
    return all(float(metric[key]) <= limit for key, limit in limits.items()
               if key.startswith(prefix))


def compare_tensors(reference: np.ndarray, candidate: np.ndarray, policy: str) -> dict[str, Any]:
    overall = _metric(reference, candidate)
    bbox = _metric(reference[: 4 * 8400], candidate[: 4 * 8400])
    score = _metric(reference[4 * 8400 :], candidate[4 * 8400 :])
    limits = POLICIES[policy]
    checks: dict[str, bool] = {}
    if policy == "ort_strict":
        checks = {
            "overall_mae": overall["mae"] <= limits["overall_mae"],
            "overall_max_abs": overall["max_abs"] <= limits["overall_max_abs"],
        }
    elif policy == "ort_cross_arch":
        checks = {
            "overall_mae": overall["mae"] <= limits["overall_mae"],
            "overall_max_abs": overall["max_abs"] <= limits["overall_max_abs"],
            "bbox_max_abs": bbox["max_abs"] <= limits["bbox_max_abs"],
            "score_max_abs": score["max_abs"] <= limits["score_max_abs"],
        }
    else:
        checks = {
            "score_mae": score["mae"] <= limits["score_mae"],
            "score_p99": score["type7_p99"] <= limits["score_p99"],
            "score_max_abs": score["max_abs"] <= limits["score_max_abs"],
            "bbox_mae": bbox["mae"] <= limits["bbox_mae"],
            "bbox_p99": bbox["type7_p99"] <= limits["bbox_p99"],
            "bbox_max_abs": bbox["max_abs"] <= limits["bbox_max_abs"],
        }
    return {"overall": overall, "bbox": bbox, "score": score,
            "gate_checks": checks, "pass": all(checks.values())}


def compare_manifests(reference_path: Path, candidate_path: Path, policy: str) -> dict[str, Any]:
    reference_root, reference_entries = load_manifest(reference_path)
    candidate_root, candidate_entries = load_manifest(candidate_path)
    if [item["image_id"] for item in reference_entries] != [item["image_id"] for item in candidate_entries]:
        raise CompareError("manifest entry identity mismatch: missing or extra entry")
    results = []
    for reference, candidate in zip(reference_entries, candidate_entries):
        if _identity(reference) != _identity(candidate):
            raise CompareError(f"manifest entry identity mismatch: {reference['image_id']}")
        result = compare_tensors(reference["_values"], candidate["_values"], policy)
        results.append({"image_id": reference["image_id"], **result})
    return {
        "schema_version": 1,
        "artifact_kind": "stage_k_level_b_comparison_report",
        "policy": policy,
        "reference_manifest": str(reference_path),
        "candidate_manifest": str(candidate_path),
        "entry_count": len(results),
        "entries": results,
        "overall_status": "PASS" if all(item["pass"] for item in results) else "FAIL",
        "limitations": ["non-formal tooling comparator; no Level C or boundary disposition"],
        "reference_run_id": reference_root.get("run_id"),
        "candidate_run_id": candidate_root.get("run_id"),
    }


def compare_repeatability(first_path: Path, second_path: Path) -> dict[str, Any]:
    _, first = load_manifest(first_path)
    _, second = load_manifest(second_path)
    if [item["image_id"] for item in first] != [item["image_id"] for item in second]:
        raise CompareError("repeatability entry identity mismatch")
    entries = []
    for left, right in zip(first, second):
        same = left["output_sha256"] == right["output_sha256"]
        entries.append({"image_id": left["image_id"], "first_sha256": left["output_sha256"],
                        "second_sha256": right["output_sha256"], "byte_identical": same})
    return {"schema_version": 1, "artifact_kind": "stage_k_ort_repeatability_report",
            "entry_count": len(entries), "entries": entries,
            "overall_status": "PASS" if all(item["byte_identical"] for item in entries) else "FAIL",
            "canonical_sha256_list": [item["first_sha256"] for item in entries]}


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(json.dumps(value, ensure_ascii=True, indent=2,
                                    separators=(",", ": "), allow_nan=False) + "\n",
                         encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Stage K raw tensor outputs.")
    parser.add_argument("--reference-manifest")
    parser.add_argument("--candidate-manifest")
    parser.add_argument("--policy", choices=sorted(POLICIES), default="tensorrt_fp16")
    parser.add_argument("--report", required=True)
    parser.add_argument("--repeatability-manifest-a")
    parser.add_argument("--repeatability-manifest-b")
    args = parser.parse_args()
    try:
        if bool(args.reference_manifest) != bool(args.candidate_manifest):
            raise CompareError("reference and candidate manifests must be provided together")
        if bool(args.repeatability_manifest_a) != bool(args.repeatability_manifest_b):
            raise CompareError("repeatability manifests must be provided together")
        reports = []
        if args.reference_manifest:
            reports.append(compare_manifests(Path(args.reference_manifest).resolve(),
                                             Path(args.candidate_manifest).resolve(), args.policy))
        if args.repeatability_manifest_a:
            reports.append(compare_repeatability(Path(args.repeatability_manifest_a).resolve(),
                                                 Path(args.repeatability_manifest_b).resolve()))
        if not reports:
            raise CompareError("a manifest comparison or repeatability comparison is required")
        report: dict[str, Any] = reports[0] if len(reports) == 1 else {
            "schema_version": 1,
            "artifact_kind": "stage_k_level_b_comparison_bundle",
            "comparisons": reports,
            "overall_status": "PASS" if all(item["overall_status"] == "PASS" for item in reports) else "FAIL",
        }
        write_json(Path(args.report).resolve(), report)
        return 0 if report["overall_status"] == "PASS" else 1
    except (CompareError, OSError, ValueError) as exc:
        print(f"stage_k_level_b_compare: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
