#!/usr/bin/env python3
"""Validate and summarize the frozen Q6 5100-frame Serial experiment."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

EXPECTED_FRAMES = 5100
WARMUP = 100
MEASURED = 5000
CYCLE = 180


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def load_backend(name: str, result_path: Path, trace_path: Path, hashes_path: Path,
                 expected_hash_path: Path, manifest_path: Path) -> dict:
    result = json.loads(result_path.read_text())
    images = result.get("images", [])
    if len(images) != EXPECTED_FRAMES:
        raise ValueError(f"{name}: result has {len(images)} frames, expected {EXPECTED_FRAMES}")
    manifest = json.loads(manifest_path.read_text())["entries"]
    expected_paths = [entry["image_path"] for _ in range(29) for entry in manifest]
    expected_paths = expected_paths[:EXPECTED_FRAMES]
    if [item.get("relative_path") for item in images] != expected_paths:
        raise ValueError(f"{name}: result path/order is not manifest replay order")
    timings = [item.get("timing_ms", {}) for item in images]
    fields = ("inference", "pre_sink_total")
    for index, timing in enumerate(timings):
        for field in fields:
            value = float(timing[field])
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name}: invalid {field} timing at frame {index}")

    hashes = json.loads(hashes_path.read_text())
    cycle_hashes = hashes.get("cycle_sha256", [])
    if len(cycle_hashes) != 29:
        raise ValueError(f"{name}: expected 29 cycle digests")
    expected = json.loads(expected_hash_path.read_text())
    expected_cycle = expected["expected_cycle_sha"]
    for item in cycle_hashes[:28]:
        if item["frame_count"] != CYCLE or item["sha256"] != expected_cycle:
            raise ValueError(f"{name}: complete cycle SHA mismatch at cycle {item['cycle_id']}")
    partial = cycle_hashes[28]
    if partial["frame_count"] != 60 or not partial["sha256"]:
        raise ValueError(f"{name}: invalid 60-frame partial cycle digest")

    records = [json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()]
    by_key = {(record["cycle_id"], record["stage"]): record for record in records}
    measured = images[WARMUP:]
    source_begin = by_key[(WARMUP, "source")]["start_ns"]
    post_end = by_key[(EXPECTED_FRAMES - 1, "postprocess")]["end_ns"]
    window_seconds = (post_end - source_begin) / 1e9
    inference = [float(item["timing_ms"]["inference"]) for item in measured]
    latency = [float(item["timing_ms"]["pre_sink_total"]) for item in measured]
    summary = {
        "backend": name,
        "result_sha256": sha256(result_path),
        "trace_sha256": sha256(trace_path),
        "hashes_sha256": sha256(hashes_path),
        "accepted_frames": EXPECTED_FRAMES,
        "warmup_frames": WARMUP,
        "measured_frames": MEASURED,
        "complete_cycles": 28,
        "partial_cycle_frames": 60,
        "expected_cycle_sha256": expected_cycle,
        "partial_cycle_sha256": partial["sha256"],
        "inference_service_ms": {"mean": statistics.fmean(inference)},
        "pre_sink_throughput_fps": MEASURED / window_seconds,
        "end_to_end_latency_ms": {
            "mean": statistics.fmean(latency),
            "p50": percentile(latency, .50),
            "p95": percentile(latency, .95),
            "p99": percentile(latency, .99),
        },
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--fp16-result", type=Path, required=True)
    parser.add_argument("--fp16-trace", type=Path, required=True)
    parser.add_argument("--fp16-hashes", type=Path, required=True)
    parser.add_argument("--fp16-expected", type=Path, required=True)
    parser.add_argument("--int8-result", type=Path, required=True)
    parser.add_argument("--int8-trace", type=Path, required=True)
    parser.add_argument("--int8-hashes", type=Path, required=True)
    parser.add_argument("--int8-expected", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    backends = {
        "tensorrt_fp16": load_backend("tensorrt_fp16", args.fp16_result, args.fp16_trace,
                                      args.fp16_hashes, args.fp16_expected, args.manifest),
        "tensorrt_int8": load_backend("tensorrt_int8", args.int8_result, args.int8_trace,
                                      args.int8_hashes, args.int8_expected, args.manifest),
    }
    fp16, int8 = backends["tensorrt_fp16"], backends["tensorrt_int8"]
    inference_ratio = fp16["inference_service_ms"]["mean"] / int8["inference_service_ms"]["mean"]
    throughput_ratio = int8["pre_sink_throughput_fps"] / fp16["pre_sink_throughput_fps"]
    mean_latency_ratio = int8["end_to_end_latency_ms"]["mean"] / fp16["end_to_end_latency_ms"]["mean"]
    p95_latency_ratio = int8["end_to_end_latency_ms"]["p95"] / fp16["end_to_end_latency_ms"]["p95"]
    if inference_ratio >= 1.10: gain = "MATERIAL_INT8_INFERENCE_GAIN"
    elif inference_ratio >= 1.03: gain = "SMALL_INT8_INFERENCE_GAIN"
    elif inference_ratio >= .97: gain = "NO_MATERIAL_INT8_GAIN"
    else: gain = "INT8_INFERENCE_REGRESSION"
    e2e = ("NO_MATERIAL_END_TO_END_REGRESSION"
           if throughput_ratio >= .97 and mean_latency_ratio <= 1.03 and p95_latency_ratio <= 1.05
           else "MATERIAL_END_TO_END_REGRESSION")
    output = {
        "schema_version": 1, "artifact_kind": "q6_serial_performance_evaluation",
        "protocol": {"warmup_frames": WARMUP, "measured_frames": MEASURED,
                     "accepted_frames": EXPECTED_FRAMES, "cycle_length": CYCLE,
                     "complete_cycles": 28, "partial_cycle_frames": 60,
                     "percentile": "Hyndman-Fan Type 7"},
        "backends": backends,
        "paired_ratios": {"inference_speedup": inference_ratio,
                           "throughput_int8_over_fp16": throughput_ratio,
                           "mean_latency_int8_over_fp16": mean_latency_ratio,
                           "p95_latency_int8_over_fp16": p95_latency_ratio},
        "classification": {"inference_gain": gain, "end_to_end_regression": e2e},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print("Q6_SERIAL_PERFORMANCE_EVIDENCE_VALID")
    print(gain)
    print(e2e)


if __name__ == "__main__":
    main()
