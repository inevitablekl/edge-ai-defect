#!/usr/bin/env python3
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "validation"))
spec = importlib.util.spec_from_file_location("run_m5_level_c", ROOT / "tools/validation/run_m5_level_c.py")
assert spec and spec.loader
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def payload(kind):
    detection = {"x1": 0.0, "y1": 0.0, "x2": 1.0, "y2": 1.0, "confidence": 0.9, "class_id": 0, "candidate_index": 1}
    if kind == "python":
        return {"schema_version": 1, "reference": {"type": "python_onnxruntime_explicit", "preprocess": "letterbox_bgr_rgb_nchw_float32"}, "model": {"contract_path": "contract.yaml", "model_path": "model.onnx", "model_sha256": "a" * 64, "input_name": "images", "input_shape": [1, 3, 640, 640], "input_dtype": "float32", "output_name": "output0", "output_shape": [1, 10, 8400], "output_dtype": "float32", "class_names": ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]}, "postprocess": {"confidence_threshold": 0.25, "iou_threshold": 0.45, "max_nms": 30000, "max_det": 300, "max_wh": 7680.0, "agnostic": False, "multi_label": False}, "images": [{"sequence_index": 0, "relative_path": "x.bmp", "width": 1, "height": 1, "detections": [detection]}], "summary": {"image_count": 1, "detection_count": 1, "per_class_counts": [1, 0, 0, 0, 0, 0]}}
    return {"schema_version": 1, "backend": {"type": "onnxruntime_cpu"}, "model": {"filename": "model.onnx", "sha256": "a" * 64, "contract_filename": "contract.yaml", "classes": ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]}, "postprocess": {"confidence_threshold": 0.25, "iou_threshold": 0.449999988, "max_nms": 30000, "max_det": 300, "max_wh": 7680, "agnostic": False, "multi_label": False}, "images": [{"sequence_index": 0, "relative_path": "x.bmp", "width": 1, "height": 1, "detections": [detection]}], "summary": {"processed_images": 1, "total_detections": 1}}


class RunnerTests(unittest.TestCase):
    def test_workdir_preflight_rejects_nonempty_and_cleans_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.yaml"
            config.write_text(yaml.safe_dump({"schema_version": 1}), encoding="utf-8")
            input_dir = root / "input"
            input_dir.mkdir()
            executable = root / "fake"
            executable.write_text("fake", encoding="utf-8")
            work = root / "work"
            work.mkdir()
            (work / "existing").write_text("x", encoding="utf-8")
            with self.assertRaises(runner.InitError):
                runner.run_dry(config, input_dir, executable, work)

    def test_determinism_failure_stops_and_cleans_workdir(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / "config.yaml"
            config.write_text(yaml.safe_dump({"schema_version": 1}), encoding="utf-8")
            input_dir = root / "input"
            input_dir.mkdir()
            executable = root / "fake"
            executable.write_text("fake", encoding="utf-8")
            work = root / "work"
            counter = {"value": 0}
            def fake_reference(_config, _input, output):
                counter["value"] += 1
                value = payload("python")
                if counter["value"] == 2:
                    value["summary"]["detection_count"] = 0
                output.write_bytes(runner.__dict__["atomic_write"].__globals__["stable_json_bytes"](value))
            with mock.patch.object(runner, "run_reference", side_effect=fake_reference):
                with self.assertRaises(runner.RunnerError):
                    runner.run_dry(config, input_dir, executable, work)
            self.assertFalse(work.exists())


if __name__ == "__main__":
    unittest.main()
