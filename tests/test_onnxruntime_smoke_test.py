from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_smoke_module():
    module_path = REPO_ROOT / "tools" / "validation" / "onnxruntime_smoke_test.py"
    spec = importlib.util.spec_from_file_location("onnxruntime_smoke_test", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


smoke_test = load_smoke_module()


class FakeValueInfo:
    def __init__(self, name, shape, dtype="tensor(float)"):
        self.name = name
        self.shape = shape
        self.type = dtype


class FakeSession:
    output = np.ones((1, 10, 8400), dtype=np.float32)

    def __init__(self, model_path, providers):
        self.model_path = model_path
        self.providers = providers

    def get_inputs(self):
        return [FakeValueInfo("images", [1, 3, 640, 640])]

    def get_outputs(self):
        return [FakeValueInfo("output0", [1, 10, 8400])]

    def run(self, output_names, feeds):
        assert output_names is None
        assert feeds["images"].shape == (1, 3, 640, 640)
        assert feeds["images"].dtype == np.float32
        return [self.output]


class FakeOrt:
    __version__ = "test-version"
    InferenceSession = FakeSession


class OnnxRuntimeSmokeTest(unittest.TestCase):
    def test_successful_inference_writes_evidence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model_path = root / "model.onnx"
            output_path = root / "evidence.json"
            model_path.write_bytes(b"onnx")

            evidence = smoke_test.run_smoke_test(model_path, output_path, FakeOrt)
            saved = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertTrue(evidence["inference_success"])
            self.assertEqual(saved["input_metadata"][0]["shape"], [1, 3, 640, 640])
            self.assertEqual(saved["output_metadata"][0]["runtime_shape"], [1, 10, 8400])
            self.assertTrue(saved["output_statistics"]["all_outputs_non_empty"])
            self.assertFalse(saved["output_statistics"]["contains_nan"])
            self.assertFalse(saved["output_statistics"]["contains_inf"])

    def test_nan_output_fails_but_writes_evidence(self):
        class NanSession(FakeSession):
            output = np.full((1, 10, 8400), np.nan, dtype=np.float32)

        class NanOrt(FakeOrt):
            InferenceSession = NanSession

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model_path = root / "model.onnx"
            output_path = root / "evidence.json"
            model_path.write_bytes(b"onnx")

            with self.assertRaisesRegex(smoke_test.SmokeTestError, "Output validation failed"):
                smoke_test.run_smoke_test(model_path, output_path, NanOrt)
            saved = json.loads(output_path.read_text(encoding="utf-8"))

            self.assertFalse(saved["inference_success"])
            self.assertTrue(saved["output_statistics"]["contains_nan"])

    def test_dynamic_input_shape_is_rejected(self):
        input_info = FakeValueInfo("images", ["batch", 3, 640, 640])

        with self.assertRaisesRegex(smoke_test.SmokeTestError, "concrete positive shape"):
            smoke_test.create_dummy_input(input_info)


if __name__ == "__main__":
    unittest.main()
