#!/usr/bin/env python3
"""Strict Stage J v2 ONNX Runtime CPU benchmark analyzer."""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping

from m5_ort_cpu_analyze import parse_application_json
from m5_ort_cpu_common import (
    BenchmarkError,
    TimingError,
    sample_stddev,
    sha256_file,
    summarize_values,
    type7_quantile,
    write_stable_json,
)


PROTOCOL = {
    "cycle_frames": 20,
    "pilot_warmup_frames": 60,
    "pilot_minimum_measured_frames": 200,
    "formal_warmup_frames": 60,
    "formal_minimum_measured_frames": 500,
    "formal_target_duration_ms": 33000,
    "formal_minimum_valid_duration_ms": 30000,
    "formal_run_count": 5,
}
TIMING_COLUMNS = [
    "source_ms",
    "preprocess_ms",
    "inference_ms",
    "postprocess_ms",
    "pre_sink_total_ms",
]
TRACE_STAGES = ["source", "preprocess", "inference", "postprocess", "sink"]
TRACE_KEYS = ["cycle_id", "stage", "start_ns", "end_ns", "duration_ns"]
STAGED_NAME = re.compile(r"^c([0-9]{6})_f([0-9]{2})_(.+)$")


def round_up_to_multiple_of_20(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise BenchmarkError("frame count must be a positive integer")
    return ((value + 19) // 20) * 20


def formal_frames_from_pilot(
    records: list[Mapping[str, Any]],
    protocol: Mapping[str, int] = PROTOCOL,
) -> dict[str, float | int]:
    warmup = protocol["pilot_warmup_frames"]
    measured = records[warmup:]
    if len(measured) < protocol["pilot_minimum_measured_frames"]:
        raise BenchmarkError("pilot has fewer than 200 measured frames")
    if len(records) % protocol["cycle_frames"] != 0:
        raise BenchmarkError("pilot frame count is not a multiple of 20")
    total_ms = sum(float(record["pre_sink_total_ms"]) for record in measured)
    wall_ms_per_frame = total_ms / len(measured)
    if not math.isfinite(wall_ms_per_frame) or wall_ms_per_frame <= 0.0:
        raise BenchmarkError("pilot wall ms/frame must be finite and positive")
    target = max(
        protocol["formal_minimum_measured_frames"],
        math.ceil(protocol["formal_target_duration_ms"] / wall_ms_per_frame),
    )
    formal_measured = round_up_to_multiple_of_20(target)
    return {
        "pilot_measured_frame_count": len(measured),
        "pilot_wall_ms_per_frame": wall_ms_per_frame,
        "formal_measured_frames": formal_measured,
        "formal_total_frames": protocol["formal_warmup_frames"] + formal_measured,
    }


def _duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TimingError(f"duplicate trace JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> Any:
    raise TimingError(f"non-finite trace JSON constant: {value}")


def parse_trace_jsonl(path: Path, real_frame_count: int) -> list[dict[str, Any]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TimingError(f"cannot read trace JSONL: {exc}") from exc
    if not raw or not raw.endswith("\n") or raw.endswith("\n\n"):
        raise TimingError("trace JSONL must end with exactly one LF")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        try:
            record = json.loads(
                line,
                object_pairs_hook=_duplicate_pairs,
                parse_constant=_reject_constant,
            )
        except (json.JSONDecodeError, TimingError) as exc:
            raise TimingError(f"invalid trace line {line_number}: {exc}") from exc
        if not isinstance(record, dict) or list(record) != TRACE_KEYS:
            raise TimingError(f"trace line {line_number} fields/order mismatch")
        for key in ("cycle_id", "start_ns", "end_ns", "duration_ns"):
            value = record[key]
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise TimingError(f"trace line {line_number} {key} is invalid")
        if record["stage"] not in TRACE_STAGES:
            raise TimingError(f"trace line {line_number} stage is invalid")
        if (record["end_ns"] < record["start_ns"] or
                record["duration_ns"] != record["end_ns"] - record["start_ns"]):
            raise TimingError(f"trace line {line_number} duration is invalid")
        if records and record["start_ns"] < records[-1]["end_ns"]:
            raise TimingError("trace timestamp is not monotonic")
        records.append(record)

    expected_count = real_frame_count * len(TRACE_STAGES)
    has_eof_probe = len(records) == expected_count + 1
    if len(records) not in {expected_count, expected_count + 1}:
        raise TimingError("trace record count does not match Result JSON")
    for frame_index in range(real_frame_count):
        frame = records[frame_index * 5:(frame_index + 1) * 5]
        if [item["cycle_id"] for item in frame] != [frame_index] * 5:
            raise TimingError("trace cycle/frame ids are not contiguous")
        if [item["stage"] for item in frame] != TRACE_STAGES:
            raise TimingError("trace stage order is invalid")
    if has_eof_probe:
        eof = records[-1]
        if eof["cycle_id"] != real_frame_count or eof["stage"] != "source":
            raise TimingError("invalid EOF source probe")
    return records[:-1] if has_eof_probe else records


def parse_benchmark_result(
    result_json: Path,
    trace_jsonl: Path,
    workload_manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    parsed = parse_application_json(result_json, workload_manifest)
    trace = parse_trace_jsonl(trace_jsonl, len(parsed["records"]))
    return {
        "data": parsed["data"],
        "records": parsed["records"],
        "trace_records": trace,
        "raw_sha256": parsed["raw_sha256"],
    }


def _statistics(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        column: summarize_values(float(record[column]) for record in records)
        for column in TIMING_COLUMNS
    }


def analyze_formal_run(
    parsed: Mapping[str, Any],
    formal_measured_frames: int,
    *,
    run_index: int,
    process_wall_seconds: float,
    protocol: Mapping[str, int] = PROTOCOL,
) -> dict[str, Any]:
    if formal_measured_frames < protocol["formal_minimum_measured_frames"]:
        raise BenchmarkError("formal run has fewer than 500 measured frames")
    if formal_measured_frames % protocol["cycle_frames"] != 0:
        raise BenchmarkError("formal measured frames are not a multiple of 20")
    records = list(parsed["records"])
    expected = protocol["formal_warmup_frames"] + formal_measured_frames
    if len(records) != expected or len(records) % protocol["cycle_frames"] != 0:
        raise BenchmarkError("formal run frame count does not match protocol")
    measured = records[
        protocol["formal_warmup_frames"]:
        protocol["formal_warmup_frames"] + formal_measured_frames
    ]
    duration = sum(float(item["pre_sink_total_ms"]) for item in measured)
    if not math.isfinite(duration) or duration < protocol["formal_minimum_valid_duration_ms"]:
        raise BenchmarkError("formal measured duration is below 30000 ms")
    backend_duration = sum(float(item["inference_ms"]) for item in measured)
    if process_wall_seconds <= 0.0 or backend_duration <= 0.0:
        raise BenchmarkError("throughput duration must be positive")
    return {
        "schema_version": 1,
        "run_index": run_index,
        "status": "PASS",
        "measured_frame_count": len(measured),
        "measured_cycle_count": len(measured) // protocol["cycle_frames"],
        "measured_pre_sink_duration_ms": duration,
        "process_wall_seconds": process_wall_seconds,
        "timing_statistics": _statistics(measured),
        "pre_sink_fps": len(measured) * 1000.0 / duration,
        "backend_fps_equivalent": len(measured) * 1000.0 / backend_duration,
        "process_wall_fps": len(records) / process_wall_seconds,
        "outlier_policy": "keep_all_measured_samples",
    }


def _across(values: Iterable[float]) -> dict[str, float]:
    samples = [float(value) for value in values]
    if len(samples) != 5:
        raise BenchmarkError("aggregate metric requires five values")
    return {
        "mean": sum(samples) / len(samples),
        "sample_standard_deviation": sample_stddev(samples),
        "median": type7_quantile(samples, 0.5),
        "minimum": min(samples),
        "maximum": max(samples),
    }


def aggregate_formal_runs(summaries: list[Mapping[str, Any]]) -> dict[str, Any]:
    if len(summaries) != PROTOCOL["formal_run_count"] or any(
            item.get("status") != "PASS" for item in summaries):
        raise BenchmarkError("aggregate requires exactly five PASS run summaries")
    return {
        "schema_version": 1,
        "run_count": 5,
        "timing_mean_across_runs": {
            column: _across(
                item["timing_statistics"][column]["mean"] for item in summaries
            )
            for column in TIMING_COLUMNS
        },
        "throughput_across_runs": {
            name: _across(item[name] for item in summaries)
            for name in (
                "pre_sink_fps",
                "backend_fps_equivalent",
                "process_wall_fps",
            )
        },
        "runs": [copy.deepcopy(dict(item)) for item in summaries],
        "outlier_policy": "keep_all_measured_samples",
    }


def decode_staged_filename(value: str) -> tuple[int, int, str]:
    match = STAGED_NAME.fullmatch(value)
    if match is None:
        raise BenchmarkError(f"invalid staged workload filename: {value}")
    return int(match.group(1)), int(match.group(2)), match.group(3)


def verify_cycle_correctness(
    result_data: Mapping[str, Any],
    expected_cycle_json: Path,
    expected_sha256: str,
) -> list[str]:
    if sha256_file(expected_cycle_json) != expected_sha256:
        raise BenchmarkError("expected cycle JSON SHA drift")
    from m5_ort_cpu_common import read_strict_json
    golden = read_strict_json(expected_cycle_json)
    golden_images = golden.get("images")
    images = result_data.get("images")
    if not isinstance(golden_images, list) or len(golden_images) != 20:
        raise BenchmarkError("expected cycle JSON is not a 20-frame result")
    if not isinstance(images, list) or not images or len(images) % 20:
        raise BenchmarkError("result does not contain complete 20-frame cycles")
    verified: list[str] = []
    for cycle_index in range(len(images) // 20):
        normalized = copy.deepcopy(dict(result_data))
        normalized_images = []
        for within, image in enumerate(images[cycle_index * 20:(cycle_index + 1) * 20]):
            encoded_cycle, encoded_within, original = decode_staged_filename(
                image["relative_path"])
            if encoded_cycle != cycle_index or encoded_within != within:
                raise BenchmarkError("staged filename cycle indices are inconsistent")
            if original != golden_images[within]["relative_path"]:
                raise BenchmarkError("staged filename does not recover frozen path")
            item = copy.deepcopy(image)
            item["sequence_index"] = within
            item["relative_path"] = original
            item.pop("timing_ms", None)
            normalized_images.append(item)
        normalized["images"] = normalized_images
        normalized["summary"] = {
            "processed_images": 20,
            "total_detections": sum(len(item["detections"]) for item in normalized_images),
        }
        if normalized != golden:
            raise BenchmarkError(f"cycle {cycle_index} differs from canonical J5.2 result")
        verified.append(expected_sha256)
    return verified


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze a Stage J benchmark run.")
    parser.add_argument("--result-json", required=True, type=Path)
    parser.add_argument("--trace-jsonl", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
        parsed = parse_benchmark_result(args.result_json, args.trace_jsonl)
        write_stable_json(args.output_json, {
            "schema_version": 1,
            "status": "PASS",
            "frame_count": len(parsed["records"]),
            "trace_real_frame_count": len(parsed["trace_records"]) // 5,
        })
        return 0
    except SystemExit as exc:
        return int(exc.code)
    except (BenchmarkError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
