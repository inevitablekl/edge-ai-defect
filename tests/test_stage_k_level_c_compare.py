#!/usr/bin/env python3
import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / "tools" / "validation"))
spec = importlib.util.spec_from_file_location("stage_k_level_c_compare", ROOT / "tools/validation/stage_k_level_c_compare.py")
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


CLASSES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]


def detection(x1=0.0, y1=0.0, x2=10.0, y2=10.0, confidence=0.9, class_id=0, candidate_index=1):
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "confidence": confidence, "class_id": class_id, "candidate_index": candidate_index}


def reference(detections):
    return {"schema_version": 1, "reference": {"type": "python_onnxruntime_explicit", "preprocess": "letterbox_bgr_rgb_nchw_float32"}, "model": {"contract_path": "contract.yaml", "model_path": "model.onnx", "model_sha256": "a" * 64, "input_name": "images", "input_shape": [1, 3, 640, 640], "input_dtype": "float32", "output_name": "output0", "output_shape": [1, 10, 8400], "output_dtype": "float32", "class_names": CLASSES}, "postprocess": module.POSTPROCESS, "images": [{"sequence_index": 0, "relative_path": "0000.bmp", "width": 200, "height": 200, "detections": detections}], "summary": {"image_count": 1, "detection_count": len(detections), "per_class_counts": [sum(item["class_id"] == value for item in detections) for value in range(6)]}}


def tensorrt(detections, schema_version=2, backend_type="tensorrt_fp16"):
    return {"schema_version": schema_version, "backend": {"type": backend_type}, "model": {"artifact_kind": "tensorrt_engine", "filename": "model.engine", "sha256": "b" * 64, "source_onnx_sha256": "a" * 64, "engine_manifest_filename": "engine.manifest.json", "contract_filename": "contract.yaml", "classes": CLASSES}, "postprocess": module.POSTPROCESS, "images": [{"sequence_index": 0, "relative_path": "0000.bmp", "width": 200, "height": 200, "detections": detections}], "summary": {"processed_images": 1, "total_detections": len(detections)}}


def raw_values(candidate_index, confidence, *, cx=320.0, cy=320.0, width=100.0, height=100.0, class_id=0, fill=0.0):
    values = np.full(module.RAW_VALUES, fill, dtype="<f4")
    values[candidate_index] = cx
    values[module.RAW_CANDIDATES + candidate_index] = cy
    values[2 * module.RAW_CANDIDATES + candidate_index] = width
    values[3 * module.RAW_CANDIDATES + candidate_index] = height
    values[(4 + class_id) * module.RAW_CANDIDATES + candidate_index] = confidence
    return values


class StageKLevelCComparatorTests(unittest.TestCase):
    def compare(self, py_detections, trt_detections):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            py_path, trt_path = root / "reference.json", root / "tensorrt.json"
            py_path.write_text(json.dumps(reference(py_detections), indent=2) + "\n")
            trt_path.write_text(json.dumps(tensorrt(trt_detections), indent=2) + "\n")
            return module.compare(py_path, trt_path)

    def test_exact_and_tolerance_boundary_pass(self):
        left = [detection(candidate_index=10)]
        for delta, expected in ((0.01, True), (-0.01, True), (0.010001, False), (-0.010001, False)):
            report, passed = self.compare(left, [detection(confidence=0.9 + delta, candidate_index=99)])
            self.assertEqual(passed, expected)
            self.assertEqual(report["status"], "PASS" if expected else "INVESTIGATION_REQUIRED")
        for delta, expected in ((1.0, True), (-1.0, True), (1.0001, False), (-1.0001, False)):
            report, passed = self.compare(left, [detection(x1=delta, candidate_index=99)])
            self.assertEqual(passed, expected)

    def test_class_change_and_schema_rejection(self):
        report, passed = self.compare([detection()], [detection(class_id=1)])
        self.assertFalse(passed)
        self.assertEqual(report["status"], "INVESTIGATION_REQUIRED")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); py = root / "py.json"; trt = root / "trt.json"
            py.write_text(json.dumps(reference([detection()])) + "\n")
            trt.write_text(json.dumps(tensorrt([detection()], schema_version=1, backend_type="onnxruntime_cpu")) + "\n")
            with self.assertRaises(module.SchemaError): module.compare(py, trt)

    def test_maximum_matching_is_deterministic_and_ignores_candidate_index(self):
        left = [detection(x1=0.005, candidate_index=0), detection(x1=0.0, candidate_index=1)]
        right = [detection(x1=0.0, candidate_index=2), detection(x1=0.015, candidate_index=3)]
        self.assertEqual(module.maximum_matching(left, right), [(0, 1), (1, 0)])
        report, passed = self.compare(left, right)
        self.assertTrue(passed); self.assertEqual(report["aggregate"]["matched"], 2)

    def test_boundary_classifier_accepts_only_single_threshold_crossing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            py_path, trt_path = root / "reference.json", root / "tensorrt.json"
            py_manifest, trt_manifest = root / "py_manifest.json", root / "trt_manifest.json"
            py_path.write_text(json.dumps(reference([detection(x1=84.375, y1=84.375, x2=115.625, y2=115.625, confidence=0.2501, candidate_index=7)]), indent=2) + "\n")
            trt_path.write_text(json.dumps(tensorrt([]), indent=2) + "\n")
            py_values = raw_values(7, 0.2501); trt_values = raw_values(7, 0.2499)
            py_raw, trt_raw = root / "py.f32le", root / "trt.f32le"; py_values.tofile(py_raw); trt_values.tofile(trt_raw)
            def manifest(raw_path, image_id, values, backend):
                digest = __import__("hashlib").sha256(raw_path.read_bytes()).hexdigest()
                return {"schema_version": 1, "artifact_kind": "stage_k_raw_tensor_output_manifest", "entries": [{"image_id": image_id, "input_filename": "input.f32le", "input_sha256": "a" * 64, "output_filename": raw_path.name, "output_sha256": digest, "output_byte_size": module.RAW_VALUES * 4, "dtype": "float32", "byte_order": "little_endian", "layout": "BCN", "shape": [1, 10, 8400], "element_count": module.RAW_VALUES, "finite_count": module.RAW_VALUES, "status": "success"}]}
            py_manifest.write_text(json.dumps(manifest(py_raw, "0000", py_values, "python_onnxruntime_cpu")) + "\n")
            trt_manifest.write_text(json.dumps(manifest(trt_raw, "0000", trt_values, "tensorrt_fp16")) + "\n")
            # The normalizer uses the image basename as image_id, matching the actual runner contract.
            py_data = json.loads(py_path.read_text()); py_data["images"][0]["relative_path"] = "0000.bmp"; py_path.write_text(json.dumps(py_data, indent=2) + "\n")
            report, passed = module.compare(py_path, trt_path, py_manifest, trt_manifest)
            self.assertTrue(passed); self.assertEqual(report["status"], "PASS_WITH_REPORTED_NUMERICAL_BOUNDARY_VARIATION")
            self.assertEqual(report["boundary"]["boundary_case_count"], 1)

    def test_boundary_policy_rejects_both_sides_passing_and_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); py_path, trt_path = root / "reference.json", root / "tensorrt.json"
            py_path.write_text(json.dumps(reference([detection(confidence=0.26, candidate_index=7)]), indent=2) + "\n")
            trt_path.write_text(json.dumps(tensorrt([]), indent=2) + "\n")
            py_values = raw_values(7, 0.26); trt_values = raw_values(7, 0.26)
            py_raw, trt_raw = root / "py.f32le", root / "trt.f32le"; py_values.tofile(py_raw); trt_values.tofile(trt_raw)
            def write_manifest(path, raw):
                digest = __import__("hashlib").sha256(raw.read_bytes()).hexdigest()
                path.write_text(json.dumps({"schema_version": 1, "artifact_kind": "stage_k_raw_tensor_output_manifest", "entries": [{"image_id": "0000", "input_filename": "input", "input_sha256": "a" * 64, "output_filename": raw.name, "output_sha256": digest, "output_byte_size": module.RAW_VALUES * 4, "dtype": "float32", "byte_order": "little_endian", "layout": "BCN", "shape": [1, 10, 8400], "element_count": module.RAW_VALUES, "finite_count": module.RAW_VALUES, "status": "success"}]} ) + "\n")
            pm, tm = root / "pm.json", root / "tm.json"; write_manifest(pm, py_raw); write_manifest(tm, trt_raw)
            report, passed = module.compare(py_path, trt_path, pm, tm)
            self.assertFalse(passed); self.assertEqual(report["status"], "FAIL")

    def test_nonfinite_and_ort_v1_are_not_accepted_as_trt_v2(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); py = root / "py.json"; trt = root / "trt.json"
            py.write_text(json.dumps(reference([detection()]), indent=2) + "\n")
            bad = tensorrt([detection()]); bad["images"][0]["detections"][0]["confidence"] = float("nan")
            trt.write_text(json.dumps(bad, allow_nan=True, indent=2) + "\n")
            with self.assertRaises(module.SchemaError): module.compare(py, trt)


if __name__ == "__main__":
    unittest.main()
