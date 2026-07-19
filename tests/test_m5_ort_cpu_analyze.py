#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "benchmark"))
import m5_ort_cpu_analyze as analyze
import m5_ort_cpu_common as common


def app_payload(count=2, timing=True, *, duplicate=False, pre_sink=10.0):
    images = []
    for index in range(count):
        image = {"sequence_index": index, "relative_path": f"{index:06d}_frame.jpg", "width": 200, "height": 200,
                 "detections": []}
        if timing:
            image["timing_ms"] = {"source": 1.0, "preprocess": 2.0, "inference": 3.0,
                                  "postprocess": 4.0, "pre_sink_total": pre_sink}
        images.append(image)
    payload = {"schema_version": 1, "backend": {"type": "onnxruntime_cpu"},
               "model": {"filename": "model.onnx", "sha256": "a" * 64, "contract_filename": "contract.yaml",
                         "classes": ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]},
               "postprocess": {"confidence_threshold": 0.25, "iou_threshold": 0.45, "max_nms": 30000,
                               "max_det": 300, "max_wh": 7680, "agnostic": False, "multi_label": False},
               "images": images, "summary": {"processed_images": count, "total_detections": 0}}
    if duplicate:
        return '{"schema_version":1,"schema_version":1}\n'
    return payload


class AnalyzeTests(unittest.TestCase):
    def write(self, path, payload):
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            common.write_stable_json(path, payload)

    def test_valid_timing_json_and_stable_tsv(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "raw.json"
            self.write(raw, app_payload())
            parsed = analyze.parse_application_json(raw)
            self.assertEqual(len(parsed["records"]), 2)
            out = root / "run"
            summary = analyze.analyze_run(raw, run_index=1, output_dir=out)
            self.assertEqual(summary["status"], "PASS")
            self.assertEqual(summary["measured_frame_count"], 2)
            self.assertEqual((out / "timings.tsv").read_text().splitlines()[0],
                             "sequence_index\trelative_path\tsource_ms\tpreprocess_ms\tinference_ms\tpostprocess_ms\tpre_sink_total_ms")
            first = (out / "timings.tsv").read_bytes()
            analyze.write_timings_tsv(parsed["records"], out / "timings2.tsv")
            self.assertEqual(first, (out / "timings2.tsv").read_bytes())

    def test_schema_missing_duplicate_nonfinite_and_negative_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            duplicate = root / "duplicate.json"
            self.write(duplicate, app_payload(duplicate=True))
            with self.assertRaises(common.TimingError):
                analyze.parse_application_json(duplicate)
            missing = root / "missing.json"
            self.write(missing, app_payload(timing=False))
            with self.assertRaises(common.TimingError):
                analyze.parse_application_json(missing)
            nonfinite = root / "nan.json"
            text = json.dumps(app_payload(), indent=2).replace("1.0", "NaN", 1) + "\n"
            nonfinite.write_text(text, encoding="utf-8")
            with self.assertRaises(common.TimingError):
                analyze.parse_application_json(nonfinite)

    def test_formal_warmup_and_validity_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = root / "formal.json"
            self.write(raw, app_payload(550, pre_sink=60.0))
            summary = analyze.analyze_run(raw, run_index=1, formal=True)
            self.assertEqual(summary["raw_frame_count"], 550)
            self.assertEqual(summary["warmup_frame_count"], 50)
            self.assertEqual(summary["measured_frame_count"], 500)
            self.assertEqual(summary["measured_pre_sink_duration_ms"], 30000.0)
            self.assertEqual(summary["status"], "PASS")
            self.assertAlmostEqual(summary["pre_sink_fps"], 500.0 / 30.0)
            with self.assertRaises(common.BenchmarkError):
                analyze.analyze_run(raw, run_index=1, formal=True, protocol={**common.PROTOCOL, "minimum_valid_duration_ms": 40000})

    def test_aggregate_requires_five_pass_runs_and_has_across_run_ranges(self):
        base = {"status": "PASS", "timing_statistics": {column: {"mean": 1.0, "P95": 2.0} for column in analyze.TIMING_COLUMNS},
                "pre_sink_fps": 10.0, "backend_fps_equivalent": 20.0}
        aggregate = analyze.aggregate_summaries([base.copy() for _ in range(5)], source_commit="a" * 40)
        self.assertEqual(aggregate["run_count"], 5)
        self.assertEqual(aggregate["valid_run_count"], 5)
        self.assertEqual(aggregate["across_run_summary"]["pre_sink_fps"]["median"], 10.0)
        with self.assertRaises(common.BenchmarkError):
            analyze.aggregate_summaries([base.copy() for _ in range(4)], source_commit="a" * 40)


if __name__ == "__main__":
    unittest.main()
