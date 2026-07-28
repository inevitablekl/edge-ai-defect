#!/usr/bin/env python3
"""Analyze independent application timing results for Stage K5.4."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


FIELDS = ("preprocess", "inference", "postprocess", "pre_sink_total")


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def summarize(images: list[dict[str, Any]], warmup: int) -> dict[str, Any]:
    measured = images[warmup:]
    result: dict[str, Any] = {"measured_frame_count": len(measured)}
    for field in FIELDS:
        values = [float(image["timing_ms"][field]) for image in measured]
        result[field + "_ms"] = {
            "mean": statistics.fmean(values),
            "median": statistics.median(values),
            "p50": percentile(values, 0.50),
            "p95": percentile(values, 0.95),
            "p99": percentile(values, 0.99),
            "min": min(values),
            "max": max(values),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fp32-result", required=True, type=Path)
    parser.add_argument("--fp16-result", required=True, type=Path)
    parser.add_argument("--warmup", type=int, default=50)
    parser.add_argument("--min-measured", type=int, default=500)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    loaded = {
        "TRT FP32 noTF32": json.loads(args.fp32_result.read_text()),
        "TRT FP16": json.loads(args.fp16_result.read_text()),
    }
    summaries: dict[str, Any] = {}
    for backend, result in loaded.items():
        images = result.get("images", [])
        if len(images) < args.warmup + args.min_measured:
            raise SystemExit(f"{backend}: only {len(images)} frames; need {args.warmup + args.min_measured}")
        for image in images:
            if any(field not in image.get("timing_ms", {}) for field in FIELDS):
                raise SystemExit(f"{backend}: missing timing field")
        summaries[backend] = summarize(images, args.warmup)

    fp32 = summaries["TRT FP32 noTF32"]
    fp16 = summaries["TRT FP16"]
    output = {
        "schema_version": 1,
        "artifact_kind": "stage_k5_4_performance_results",
        "environment": {
            "warmup_frames": args.warmup,
            "minimum_measured_frames": args.min_measured,
            "input_frame_count_each_backend": len(loaded["TRT FP32 noTF32"]["images"]),
            "measured_frame_count": fp32["measured_frame_count"],
        },
        "backends": summaries,
        "speedup_ratio": {
            "trt_latency_mean_fp32_div_fp16": fp32["inference_ms"]["mean"] / fp16["inference_ms"]["mean"],
            "e2e_latency_mean_fp32_div_fp16": fp32["pre_sink_total_ms"]["mean"] / fp16["pre_sink_total_ms"]["mean"],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")


if __name__ == "__main__":
    main()
