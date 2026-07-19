#!/usr/bin/env python3
"""Strict M4 FrameTimings parser and offline M5.3 statistics analyzer."""

from __future__ import annotations

import argparse
import copy
import math
import sys
from pathlib import Path
from typing import Any, Mapping

from m5_ort_cpu_common import (
    PROTOCOL,
    TIMING_COLUMNS,
    TIMING_FIELDS,
    BenchmarkError,
    TimingError,
    finite_nonnegative,
    gzip_file_deterministic,
    read_strict_json,
    sha256_file,
    stable_json_bytes,
    summarize_values,
    type7_quantile,
    write_stable_json,
)


APP_TOP = ["schema_version", "backend", "model", "postprocess", "images", "summary"]
IMAGE_KEYS_NO_TIMING = ["sequence_index", "relative_path", "width", "height", "detections"]
IMAGE_KEYS_TIMING = ["sequence_index", "relative_path", "width", "height", "detections", "timing_ms"]
TIMING_KEYS = ["source", "preprocess", "inference", "postprocess", "pre_sink_total"]


def _keys(value: Any, expected: list[str], where: str) -> None:
    if not isinstance(value, dict) or list(value) != expected:
        raise TimingError(f"{where} fields/order mismatch")


def _validate_detection_list(value: Any, where: str) -> None:
    if not isinstance(value, list):
        raise TimingError(f"{where} must be a list")
    expected = ["x1", "y1", "x2", "y2", "confidence", "class_id", "candidate_index"]
    for index, detection in enumerate(value):
        _keys(detection, expected, f"{where}[{index}]")
        for key in expected[:4]:
            value = detection[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
                raise TimingError(f"{where}[{index}].{key} must be finite")
        finite_nonnegative(detection["confidence"], f"{where}[{index}].confidence")
        if isinstance(detection["class_id"], bool) or not isinstance(detection["class_id"], int) or not 0 <= detection["class_id"] < 6:
            raise TimingError("detection class_id is invalid")
        if isinstance(detection["candidate_index"], bool) or not isinstance(detection["candidate_index"], int) or not 0 <= detection["candidate_index"] < 8400:
            raise TimingError("detection candidate_index is invalid")


def _validate_timing(value: Any, where: str) -> dict[str, float]:
    _keys(value, TIMING_KEYS, where)
    return {key: finite_nonnegative(value[key], f"{where}.{key}") for key in TIMING_KEYS}


def parse_application_json(path: Path, workload_manifest: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Parse schema-version-1 application JSON and return normalized timing records."""
    data = read_strict_json(path)
    _keys(data, APP_TOP, "application result")
    if isinstance(data["schema_version"], bool) or data["schema_version"] != 1 or data["backend"] != {"type": "onnxruntime_cpu"}:
        raise TimingError("application identity mismatch")
    _keys(data["model"], ["filename", "sha256", "contract_filename", "classes"], "model")
    if any(not isinstance(data["model"][key], str) or not data["model"][key] for key in ["filename", "sha256", "contract_filename"]):
        raise TimingError("model identity fields are invalid")
    if data["model"]["classes"] != ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]:
        raise TimingError("application class contract mismatch")
    _keys(data["postprocess"], ["confidence_threshold", "iou_threshold", "max_nms", "max_det", "max_wh", "agnostic", "multi_label"], "postprocess")
    if any(isinstance(data["postprocess"][key], bool) or not isinstance(data["postprocess"][key], (int, float)) or not math.isfinite(float(data["postprocess"][key]))
           for key in ["confidence_threshold", "iou_threshold", "max_wh"]):
        raise TimingError("postprocess numeric fields are invalid")
    if any(isinstance(data["postprocess"][key], bool) or not isinstance(data["postprocess"][key], int)
           or data["postprocess"][key] < 0 for key in ["max_nms", "max_det"]):
        raise TimingError("postprocess count fields are invalid")
    if any(not isinstance(data["postprocess"][key], bool) for key in ["agnostic", "multi_label"]):
        raise TimingError("postprocess boolean fields are invalid")
    images = data["images"]
    if not isinstance(images, list):
        raise TimingError("images must be a list")
    expected_paths = None
    if workload_manifest is not None:
        expected_paths = [entry["workload_filename"] for entry in workload_manifest["entries"]]
        if len(images) != len(expected_paths):
            raise TimingError("image count differs from workload")
    records: list[dict[str, Any]] = []
    for index, image in enumerate(images):
        _keys(image, IMAGE_KEYS_TIMING, f"image {index}")
        sequence = image["sequence_index"]
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence != index:
            raise TimingError("sequence_index must be contiguous")
        path_value = image["relative_path"]
        if not isinstance(path_value, str) or not path_value or path_value.startswith("/") or "\\" in path_value or ".." in Path(path_value).parts:
            raise TimingError("relative_path must be relative")
        if expected_paths is not None and path_value != expected_paths[index]:
            raise TimingError("relative_path order differs from workload")
        if isinstance(image["width"], bool) or not isinstance(image["width"], int) or image["width"] <= 0:
            raise TimingError("image width is invalid")
        if isinstance(image["height"], bool) or not isinstance(image["height"], int) or image["height"] <= 0:
            raise TimingError("image height is invalid")
        _validate_detection_list(image["detections"], f"image {index}.detections")
        timing = _validate_timing(image["timing_ms"], f"image {index}.timing_ms")
        records.append({"sequence_index": sequence, "relative_path": path_value,
                        **{f"{key}_ms": timing[key] for key in TIMING_FIELDS}})
    summary = data["summary"]
    _keys(summary, ["processed_images", "total_detections"], "summary")
    total_detections = sum(len(image["detections"]) for image in images)
    if (isinstance(summary["processed_images"], bool) or not isinstance(summary["processed_images"], int)
            or isinstance(summary["total_detections"], bool) or not isinstance(summary["total_detections"], int)
            or summary["processed_images"] < 0 or summary["total_detections"] < 0
            or summary["processed_images"] != len(images) or summary["total_detections"] != total_detections):
        raise TimingError("summary does not match images")
    return {"data": data, "records": records, "raw_sha256": sha256_file(path)}


def validate_formal_records(records: list[dict[str, Any]], protocol: Mapping[str, int] = PROTOCOL) -> list[dict[str, Any]]:
    if len(records) < protocol["formal_warmup"]:
        raise BenchmarkError("formal run has fewer than 50 warmup frames")
    measured = records[protocol["formal_warmup"]:]
    if len(measured) < protocol["minimum_measured_frames"]:
        raise BenchmarkError("formal run has fewer than 500 measured frames")
    duration = sum(record["pre_sink_total_ms"] for record in measured)
    if not math.isfinite(duration) or duration < protocol["minimum_valid_duration_ms"]:
        raise BenchmarkError("formal measured duration is below 30000 ms")
    return measured


def write_timings_tsv(records: list[dict[str, Any]], path: Path) -> bytes:
    lines = ["sequence_index\trelative_path\t" + "\t".join(TIMING_COLUMNS)]
    for record in records:
        values = [str(record["sequence_index"]), record["relative_path"]]
        values.extend(format(float(record[key]), ".17g") for key in TIMING_COLUMNS)
        lines.append("\t".join(values))
    content = ("\n".join(lines) + "\n").encode("utf-8")
    path.write_bytes(content)
    return content


def timing_statistics(records: list[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    return {column: summarize_values([record[column] for record in records]) for column in TIMING_COLUMNS}


def _throughput(count: int, total_ms: float, where: str) -> float:
    if total_ms <= 0 or not math.isfinite(total_ms):
        raise BenchmarkError(f"{where} denominator must be finite and positive")
    return count * 1000.0 / total_ms


def analyze_run(raw_path: Path, *, workload_manifest: Mapping[str, Any] | None = None,
                run_index: int = 1, formal: bool = False, output_dir: Path | None = None,
                protocol: Mapping[str, int] = PROTOCOL, process_exit_code: int = 0,
                process_wall_clock_seconds: float = 0.0) -> dict[str, Any]:
    parsed = parse_application_json(raw_path, workload_manifest)
    records = parsed["records"]
    measured = validate_formal_records(records, protocol) if formal else records
    stats = timing_statistics(measured)
    duration = sum(record["pre_sink_total_ms"] for record in measured)
    backend_duration = sum(record["inference_ms"] for record in measured)
    summary: dict[str, Any] = {
        "schema_version": 1, "run_index": run_index, "status": "PASS", "raw_frame_count": len(records),
        "warmup_frame_count": min(protocol["formal_warmup"], len(records)), "measured_frame_count": len(measured),
        "measured_pre_sink_duration_ms": duration, "protocol": dict(protocol), "timing_statistics": stats,
        "pre_sink_fps": _throughput(len(measured), duration, "pre_sink_fps"),
        "backend_fps_equivalent": _throughput(len(measured), backend_duration, "backend_fps_equivalent"),
        "process_wall_clock_seconds": float(process_wall_clock_seconds), "process_exit_code": process_exit_code,
        "raw_application_uncompressed_sha256": parsed["raw_sha256"], "raw_application_compressed_sha256": None,
        "timings_tsv_sha256": None, "command": None,
        "validity_checks": {"timing_schema": True, "all_timing_finite_nonnegative": True,
                            "measured_count_minimum": len(measured) >= protocol["minimum_measured_frames"],
                            "duration_minimum": duration >= protocol["minimum_valid_duration_ms"]},
        "warnings": [], "outlier_policy": "keep_all_measured_samples",
    }
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        tsv_path = output_dir / "timings.tsv"
        tsv_bytes = write_timings_tsv(measured, tsv_path)
        summary["timings_tsv_sha256"] = sha256_file(tsv_path)
        raw_gz = output_dir / "raw_application.json.gz"
        _, summary["raw_application_compressed_sha256"] = gzip_file_deterministic(raw_path, raw_gz)
        write_stable_json(output_dir / "summary.json", summary)
    return summary


def aggregate_summaries(summaries: list[Mapping[str, Any]], *, source_commit: str,
                        protocol: Mapping[str, int] = PROTOCOL) -> dict[str, Any]:
    if len(summaries) != protocol["formal_run_count"] or any(item.get("status") != "PASS" for item in summaries):
        raise BenchmarkError("aggregate requires exactly five PASS run summaries")
    metric_groups = {column: [item["timing_statistics"][column]["mean"] for item in summaries]
                     for column in TIMING_COLUMNS}
    p95_groups = {column: [item["timing_statistics"][column]["P95"] for item in summaries] for column in TIMING_COLUMNS}
    fps_pre = [item["pre_sink_fps"] for item in summaries]
    fps_backend = [item["backend_fps_equivalent"] for item in summaries]

    def range_summary(values: list[float]) -> dict[str, float]:
        return {"median": type7_quantile(values, 0.5), "minimum": min(values), "maximum": max(values)}

    across = {"timing_mean": {column: range_summary(values) for column, values in metric_groups.items()},
              "timing_P95": {column: range_summary(values) for column, values in p95_groups.items()},
              "pre_sink_fps": range_summary(fps_pre), "backend_fps_equivalent": range_summary(fps_backend)}
    return {"schema_version": 1, "baseline_name": "WSL2 x86_64 ONNX Runtime CPU Engineering Baseline",
            "source_commit": source_commit, "run_count": 5, "valid_run_count": 5,
            "protocol": dict(protocol), "run_summaries": [copy.deepcopy(dict(x)) for x in summaries],
            "across_run_summary": across,
            "auxiliary_pooled_statistics": {"description": "pooled values are auxiliary and do not replace per-run summaries"},
            "limitations": ["WSL2", "not a Jetson result", "not used for TensorRT speedup"]}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze M4 FrameTimings JSON offline.")
    parser.add_argument("--raw-json", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--run-index", required=True, type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        analyze_run(args.raw_json, run_index=args.run_index, formal=False, output_dir=args.output_dir)
        print(f"analyzer PASS: run {args.run_index}")
        return 0
    except SystemExit as exc:
        return int(exc.code)
    except (BenchmarkError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
