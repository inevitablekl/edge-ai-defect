#!/usr/bin/env python3
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "validation"))
spec = importlib.util.spec_from_file_location("m5_level_c_common", ROOT / "tools/validation/m5_level_c_common.py")
assert spec and spec.loader
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)


class ReferenceHelperTests(unittest.TestCase):
    def test_enumeration_is_nonrecursive_sorted_and_skips_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "z.JPG").write_bytes(b"not-an-image")
            (root / "a.bmp").write_bytes(b"not-an-image")
            (root / "nested").mkdir()
            (root / "nested" / "inside.jpg").write_bytes(b"not-an-image")
            (root / "notes.json").write_text("{}", encoding="utf-8")
            try:
                (root / "link.png").symlink_to(root / "a.bmp")
            except OSError:
                pass
            paths = common.enumerate_images(root)
            self.assertEqual([path.name for path in paths], ["a.bmp", "z.JPG"])

    def test_letterbox_geometry_and_rgb_chw_float32(self):
        image = np.zeros((201, 319, 3), dtype=np.uint8)
        image[0, 0] = [1, 2, 3]
        tensor, metadata = common.preprocess(image)
        self.assertEqual(tensor.shape, (1, 3, 640, 640))
        self.assertEqual(tensor.dtype, np.float32)
        self.assertTrue(tensor.flags.c_contiguous)
        self.assertAlmostEqual(metadata["gain"], 640 / 319)
        self.assertEqual((metadata["pad_left"], metadata["pad_top"]), (0, 118))
        self.assertAlmostEqual(float(tensor[0, 0, metadata["pad_top"], 0]), 3 / 255, places=6)

    def test_ties_to_even_and_nonfinite_rejection(self):
        self.assertEqual(common.python_round(2.5), 2)
        self.assertEqual(common.python_round(3.5), 4)
        raw = np.zeros((1, 10, 8400), dtype=np.float32)
        raw[0, 2, 7] = 2
        raw[0, 3, 7] = 2
        raw[0, 4, 7] = 0.25
        self.assertEqual(common.postprocess(raw, {"original_width": 200, "original_height": 200, "gain": 1, "pad_left": 0, "pad_top": 0}, {"confidence_threshold": 0.25, "iou_threshold": 0.45, "max_nms": 30000, "max_det": 300, "max_wh": 7680.0, "agnostic": False, "multi_label": False}), [])
        raw[0, 4, 7] = 0.9
        detections = common.postprocess(raw, {"original_width": 200, "original_height": 200, "gain": 1, "pad_left": 0, "pad_top": 0}, {"confidence_threshold": 0.25, "iou_threshold": 0.45, "max_nms": 30000, "max_det": 300, "max_wh": 7680.0, "agnostic": False, "multi_label": False})
        self.assertEqual(detections[0]["candidate_index"], 7)
        raw[0, 0, 9] = np.nan
        with self.assertRaises(common.FrameError):
            common.postprocess(raw, {"original_width": 200, "original_height": 200, "gain": 1, "pad_left": 0, "pad_top": 0}, {"confidence_threshold": 0.25, "iou_threshold": 0.45, "max_nms": 30000, "max_det": 300, "max_wh": 7680.0, "agnostic": False, "multi_label": False})

    def test_strict_yaml_duplicate_and_unknown_field(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.yaml"
            path.write_text("a: 1\na: 2\n", encoding="utf-8")
            with self.assertRaises(common.ContractError):
                common.read_yaml(path)

    def test_atomic_json_refuses_existing_and_normalizes_negative_zero(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "result.json"
            common.atomic_write(path, {"value": -0.0})
            self.assertEqual(path.read_text(encoding="utf-8"), '{\n  "value": 0.0\n}\n')
            with self.assertRaises(common.InitError):
                common.atomic_write(path, {"value": 1})


if __name__ == "__main__":
    unittest.main()
