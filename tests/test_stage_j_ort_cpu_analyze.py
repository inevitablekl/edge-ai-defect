#!/usr/bin/env python3

import copy
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/benchmark"))

from m5_ort_cpu_common import BenchmarkError, TimingError, sample_stddev, stable_json_bytes, type7_quantile
from stage_j_ort_cpu_analyze import (
    PROTOCOL,
    aggregate_formal_runs,
    analyze_formal_run,
    formal_frames_from_pilot,
    parse_benchmark_result,
    parse_trace_jsonl,
    round_up_to_multiple_of_20,
)


def timing(value=60.0):
    return {
        "source": 1.0, "preprocess": 2.0, "inference": 50.0,
        "postprocess": 3.0, "pre_sink_total": value,
    }


def application(frame_count, value=60.0):
    images = []
    for index in range(frame_count):
        images.append({
            "sequence_index": index,
            "relative_path": f"c{index // 20:06d}_f{index % 20:02d}_{index % 20:04d}_image.jpg",
            "width": 200,
            "height": 200,
            "detections": [],
            "timing_ms": timing(value),
        })
    return {
        "schema_version": 1,
        "backend": {"type": "onnxruntime_cpu"},
        "model": {
            "filename": "model.onnx", "sha256": "a" * 64,
            "contract_filename": "contract.yaml",
            "classes": ["crazing", "inclusion", "patches", "pitted_surface",
                        "rolled-in_scale", "scratches"],
        },
        "postprocess": {
            "confidence_threshold": 0.25, "iou_threshold": 0.45,
            "max_nms": 30000, "max_det": 300, "max_wh": 7680,
            "agnostic": False, "multi_label": False,
        },
        "images": images,
        "summary": {"processed_images": frame_count, "total_detections": 0},
    }


def trace_records(frame_count, eof=True):
    records = []
    now = 0
    for frame in range(frame_count):
        for stage in ("source", "preprocess", "inference", "postprocess", "sink"):
            records.append({
                "cycle_id": frame, "stage": stage, "start_ns": now,
                "end_ns": now + 1, "duration_ns": 1,
            })
            now += 1
    if eof:
        records.append({
            "cycle_id": frame_count, "stage": "source", "start_ns": now,
            "end_ns": now + 1, "duration_ns": 1,
        })
    return records


class StageJAnalyzerTests(unittest.TestCase):
    def test_round_up(self):
        self.assertEqual(round_up_to_multiple_of_20(500), 500)
        self.assertEqual(round_up_to_multiple_of_20(501), 520)

    def test_pilot_calculation_and_short_rejection(self):
        records = [{"pre_sink_total_ms": 60.0}] * 260
        result = formal_frames_from_pilot(records)
        self.assertEqual(result["pilot_measured_frame_count"], 200)
        self.assertEqual(result["formal_measured_frames"], 560)
        with self.assertRaises(BenchmarkError):
            formal_frames_from_pilot(records[:-20])

    def test_statistics_definitions_reused(self):
        self.assertAlmostEqual(type7_quantile([1, 2, 3, 4], 0.95), 3.85)
        self.assertAlmostEqual(sample_stddev([1, 2, 3]), 1.0)

    def test_formal_window_and_protocol_failures(self):
        parsed = {"records": [
            {"source_ms": 1.0, "preprocess_ms": 2.0, "inference_ms": 50.0,
             "postprocess_ms": 3.0, "pre_sink_total_ms": 60.0}
            for _ in range(620)
        ]}
        summary = analyze_formal_run(
            parsed, 560, run_index=1, process_wall_seconds=40.0)
        self.assertEqual(summary["measured_frame_count"], 560)
        self.assertEqual(summary["measured_cycle_count"], 28)
        self.assertEqual(summary["timing_statistics"]["source_ms"]["sample_count"], 560)
        with self.assertRaises(BenchmarkError):
            analyze_formal_run(parsed, 480, run_index=1, process_wall_seconds=40.0)
        with self.assertRaises(BenchmarkError):
            analyze_formal_run(parsed, 501, run_index=1, process_wall_seconds=40.0)
        short_duration = copy.deepcopy(parsed)
        for item in short_duration["records"]:
            item["pre_sink_total_ms"] = 1.0
        with self.assertRaises(BenchmarkError):
            analyze_formal_run(
                short_duration, 560, run_index=1, process_wall_seconds=40.0)

    def test_trace_validation_and_eof(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.jsonl"
            path.write_text("".join(
                json.dumps(item, separators=(",", ":")) + "\n"
                for item in trace_records(2)), encoding="utf-8")
            self.assertEqual(len(parse_trace_jsonl(path, 2)), 10)

            missing = trace_records(2)
            del missing[2]
            path.write_text("".join(json.dumps(item) + "\n" for item in missing),
                            encoding="utf-8")
            with self.assertRaises(TimingError):
                parse_trace_jsonl(path, 2)

            wrong = trace_records(2)
            wrong[1]["stage"] = "inference"
            path.write_text("".join(json.dumps(item) + "\n" for item in wrong),
                            encoding="utf-8")
            with self.assertRaises(TimingError):
                parse_trace_jsonl(path, 2)

            backwards = trace_records(2)
            backwards[1]["start_ns"] = 0
            backwards[1]["end_ns"] = 1
            path.write_text("".join(json.dumps(item) + "\n" for item in backwards),
                            encoding="utf-8")
            with self.assertRaises(TimingError):
                parse_trace_jsonl(path, 2)

    def test_strict_result_and_trace_parse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = root / "result.json"
            result.write_bytes(stable_json_bytes(application(20)))
            trace = root / "trace.jsonl"
            trace.write_text("".join(
                json.dumps(item, separators=(",", ":")) + "\n"
                for item in trace_records(20)), encoding="utf-8")
            parsed = parse_benchmark_result(result, trace)
            self.assertEqual(len(parsed["records"]), 20)
            self.assertTrue(all(math.isfinite(
                item["pre_sink_total_ms"]) for item in parsed["records"]))

    def test_aggregate_requires_five_pass_and_is_deterministic(self):
        base = {
            "status": "PASS",
            "timing_statistics": {
                column: {"mean": 1.0} for column in
                ("source_ms", "preprocess_ms", "inference_ms",
                 "postprocess_ms", "pre_sink_total_ms")
            },
            "pre_sink_fps": 1.0,
            "backend_fps_equivalent": 2.0,
            "process_wall_fps": 3.0,
        }
        with self.assertRaises(BenchmarkError):
            aggregate_formal_runs([base] * 4)
        aggregate = aggregate_formal_runs([copy.deepcopy(base) for _ in range(5)])
        self.assertEqual(stable_json_bytes(aggregate), stable_json_bytes(aggregate))


if __name__ == "__main__":
    unittest.main()
