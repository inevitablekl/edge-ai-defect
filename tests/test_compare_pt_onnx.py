from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_compare_module():
    module_path = REPO_ROOT / "tools" / "validation" / "compare_pt_onnx.py"
    spec = importlib.util.spec_from_file_location("compare_pt_onnx", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


compare = load_compare_module()


class ComparePtOnnxTest(unittest.TestCase):
    def test_image_selection_is_deterministic_and_spans_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index in range(20):
                (root / f"image_{index:02d}.jpg").write_bytes(b"image")

            selected = compare.select_images(root, 4)

            self.assertEqual(
                [path.name for path in selected],
                ["image_00.jpg", "image_06.jpg", "image_13.jpg", "image_19.jpg"],
            )

    def test_raw_output_comparison_records_expected_errors(self):
        pytorch_output = np.array([[[1.0, 2.0]]], dtype=np.float32)
        onnx_output = np.array([[[1.0, 2.002]]], dtype=np.float32)

        result = compare.raw_output_comparison(pytorch_output, onnx_output)

        self.assertEqual(result["pytorch"]["shape"], [1, 1, 2])
        self.assertAlmostEqual(result["mae"], 0.001, places=6)
        self.assertAlmostEqual(result["max_absolute_error"], 0.002, places=6)

    def test_detection_matching_handles_different_order(self):
        pytorch = [
            {"class_id": 1, "confidence": 0.9, "bbox_xyxy": [1.0, 2.0, 3.0, 4.0]},
            {"class_id": 2, "confidence": 0.8, "bbox_xyxy": [5.0, 6.0, 7.0, 8.0]},
        ]
        onnx = [
            {"class_id": 2, "confidence": 0.8, "bbox_xyxy": [5.0, 6.0, 7.0, 8.0]},
            {"class_id": 1, "confidence": 0.9, "bbox_xyxy": [1.0, 2.0, 3.0, 4.0]},
        ]

        result = compare.compare_detections(pytorch, onnx)

        self.assertTrue(result["counts_equal"])
        self.assertTrue(result["classes_equal"])
        self.assertTrue(result["comparison_pass"])


if __name__ == "__main__":
    unittest.main()
