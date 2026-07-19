#!/usr/bin/env python3
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "validation"))
spec = importlib.util.spec_from_file_location("m5_level_c_compare", ROOT / "tools/validation/m5_level_c_compare.py")
assert spec and spec.loader
compare_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare_module)
from m5_level_c_common import stable_json_bytes


def detection(x1=0.0, y1=0.0, x2=10.0, y2=10.0, confidence=0.9, class_id=0, candidate_index=1):
    return {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "confidence": confidence, "class_id": class_id, "candidate_index": candidate_index}


def reference(detections):
    return {"schema_version": 1, "reference": {"type": "python_onnxruntime_explicit", "preprocess": "letterbox_bgr_rgb_nchw_float32"}, "model": {"contract_path": "contract.yaml", "model_path": "model.onnx", "model_sha256": "a" * 64, "input_name": "images", "input_shape": [1, 3, 640, 640], "input_dtype": "float32", "output_name": "output0", "output_shape": [1, 10, 8400], "output_dtype": "float32", "class_names": ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]}, "postprocess": {"confidence_threshold": 0.25, "iou_threshold": 0.45, "max_nms": 30000, "max_det": 300, "max_wh": 7680.0, "agnostic": False, "multi_label": False}, "images": [{"sequence_index": 0, "relative_path": "0000.bmp", "width": 200, "height": 200, "detections": detections}], "summary": {"image_count": 1, "detection_count": len(detections), "per_class_counts": [sum(item["class_id"] == value for item in detections) for value in range(6)]}}


def cpp(detections):
    return {"schema_version": 1, "backend": {"type": "onnxruntime_cpu"}, "model": {"filename": "model.onnx", "sha256": "a" * 64, "contract_filename": "contract.yaml", "classes": ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]}, "postprocess": {"confidence_threshold": 0.25, "iou_threshold": 0.449999988, "max_nms": 30000, "max_det": 300, "max_wh": 7680, "agnostic": False, "multi_label": False}, "images": [{"sequence_index": 0, "relative_path": "0000.bmp", "width": 200, "height": 200, "detections": detections}], "summary": {"processed_images": 1, "total_detections": len(detections)}}


class ComparatorTests(unittest.TestCase):
    def test_greedy_counterexample_is_solved_by_maximum_matching(self):
        left = [
            detection(x1=0.005, confidence=0.9, candidate_index=0),
            detection(x1=0.000, confidence=0.9, candidate_index=1),
        ]
        right = [
            detection(x1=0.000, confidence=0.9, candidate_index=2),
            detection(x1=0.015, confidence=0.9, candidate_index=3),
        ]
        adjacency = [
            [right_index for right_index, candidate in enumerate(right) if compare_module.compatible(item, candidate)]
            for item in left
        ]
        self.assertEqual(adjacency, [[0, 1], [0]])

        greedy_pairs = []
        used_right = set()
        for left_index, candidates in enumerate(adjacency):
            first = next((right_index for right_index in candidates if right_index not in used_right), None)
            if first is None:
                break
            used_right.add(first)
            greedy_pairs.append((left_index, first))
        self.assertEqual(greedy_pairs, [(0, 0)])
        self.assertEqual(len(greedy_pairs), 1)

        pairs = compare_module.maximum_matching(left, right)
        self.assertEqual(pairs, [(0, 1), (1, 0)])
        self.assertEqual(len(pairs), 2)
        report, passed = self._compare(left, right)
        self.assertTrue(passed)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(
            {(pair["python_detection_index"], pair["cpp_detection_index"]) for pair in report["image_results"][0]["matched_pairs"]},
            {(0, 1), (1, 0)},
        )

    def test_confidence_tolerance_boundaries_both_directions(self):
        left = [detection(confidence=0.9, candidate_index=10)]
        for delta, expected_pass in ((0.0001, True), (-0.0001, True), (0.0001001, False), (-0.0001001, False)):
            with self.subTest(delta=delta):
                right = [detection(confidence=left[0]["confidence"] + delta, candidate_index=99)]
                report, passed = self._compare(left, right)
                self.assertEqual(passed, expected_pass)
                self.assertEqual(report["status"], "PASS" if expected_pass else "FAIL")
                if expected_pass:
                    self.assertLessEqual(report["image_results"][0]["max_confidence_abs_error"], compare_module.CONF_TOL)
                else:
                    self.assertEqual(report["failures"][0]["category"], "no_compatible_edge")

    def test_bbox_tolerance_boundaries_both_directions(self):
        left = [detection(candidate_index=10)]
        for delta, expected_pass in ((0.01, True), (-0.01, True), (0.010001, False), (-0.010001, False)):
            with self.subTest(delta=delta):
                right = [detection(x1=left[0]["x1"] + delta, candidate_index=99)]
                report, passed = self._compare(left, right)
                self.assertEqual(passed, expected_pass)
                self.assertEqual(report["status"], "PASS" if expected_pass else "FAIL")
                if expected_pass:
                    self.assertLessEqual(report["image_results"][0]["max_bbox_coordinate_abs_error"], compare_module.BBOX_TOL)
                else:
                    self.assertEqual(report["failures"][0]["category"], "no_compatible_edge")

    def test_detection_order_is_irrelevant_and_candidate_index_is_diagnostic(self):
        left = [
            detection(x1=0, x2=10, confidence=0.8, candidate_index=10),
            detection(x1=20, x2=30, confidence=0.7, candidate_index=11),
        ]
        right = [
            detection(x1=20, x2=30, confidence=0.7, candidate_index=99),
            detection(x1=0, x2=10, confidence=0.8, candidate_index=98),
        ]
        self.assertEqual(compare_module.maximum_matching(left, right), [(0, 1), (1, 0)])
        report, passed = self._compare(left, right)
        self.assertTrue(passed)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["image_results"][0]["matched_pairs"]), 2)
        self.assertEqual(
            {(pair["python_detection_index"], pair["cpp_detection_index"]) for pair in report["image_results"][0]["matched_pairs"]},
            {(0, 1), (1, 0)},
        )
        self.assertEqual(
            {(pair["python_candidate_index"], pair["cpp_candidate_index"]) for pair in report["image_results"][0]["matched_pairs"]},
            {(10, 98), (11, 99)},
        )

    def test_non_finite_json_values_are_rejected_before_comparison(self):
        for field, value in (("confidence", "NaN"), ("confidence", "Infinity"), ("confidence", "-Infinity"), ("x1", "NaN"), ("x1", "Infinity"), ("x1", "-Infinity")):
            with self.subTest(field=field, value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                py = root / "py.json"
                cpp_path = root / "cpp.json"
                out = root / "report.json"
                py.write_text(json.dumps(reference([detection()]), indent=2) + "\n", encoding="utf-8")
                raw_cpp = json.dumps(cpp([detection()]), indent=2) + "\n"
                raw_cpp = raw_cpp.replace(f'"{field}": 0.9' if field == "confidence" else f'"{field}": 0.0', f'"{field}": {value}', 1)
                cpp_path.write_text(raw_cpp, encoding="utf-8")
                with self.assertRaises(compare_module.SchemaError):
                    compare_module.compare(py, cpp_path)
                self.assertFalse(out.exists())

    def test_genuine_semantic_failure_and_stable_report(self):
        left, right = [detection()], [detection(x1=1.0)]
        report, passed = self._compare(left, right)
        self.assertFalse(passed)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["failures"][0]["category"], "no_compatible_edge")

    def _compare(self, left, right):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            py, cc, out = root / "py.json", root / "cpp.json", root / "report.json"
            py.write_text(json.dumps(reference(left), indent=2) + "\n", encoding="utf-8")
            cc.write_text(json.dumps(cpp(right), indent=2) + "\n", encoding="utf-8")
            report, passed = compare_module.compare(py, cc)
            compare_module.atomic_write(out, report)
            self.assertEqual(out.read_bytes(), stable_json_bytes(report))
            return report, passed


if __name__ == "__main__":
    unittest.main()
