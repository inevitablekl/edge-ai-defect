#!/usr/bin/env python3
"""Focused, synthetic tests for the Stage K Level B comparator."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "validation"))
import stage_k_level_b_compare as compare  # noqa: E402


class StageKLevelBCompareTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _manifest(self, name: str, values: np.ndarray, image_ids: list[str] | None = None) -> Path:
        output_dir = self.root / name
        output_dir.mkdir()
        image_ids = image_ids or ["image-01"]
        entries = []
        for index, image_id in enumerate(image_ids):
            raw = np.asarray(values[index], dtype="<f4").tobytes()
            filename = f"output_{index}.f32le"
            (output_dir / filename).write_bytes(raw)
            entries.append({
                "image_id": image_id,
                "input_filename": f"{image_id}.f32le",
                "input_sha256": "a" * 64,
                "output_filename": filename,
                "output_sha256": hashlib.sha256(raw).hexdigest(),
                "output_byte_size": compare.BYTE_SIZE,
                "dtype": compare.DTYPE,
                "byte_order": compare.BYTE_ORDER,
                "layout": compare.LAYOUT,
                "shape": compare.SHAPE,
                "element_count": compare.COUNT,
                "finite_count": compare.COUNT,
                "backend_type": "onnxruntime_cpu",
                "status": "success",
            })
        manifest = {
            "schema_version": 1,
            "artifact_kind": "stage_k_raw_tensor_output_manifest",
            "run_id": name,
            "entries": entries,
        }
        path = output_dir / "output_manifest.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        return path

    def _base(self) -> np.ndarray:
        return np.zeros(compare.COUNT, dtype="<f4")

    def test_type7_known_vector(self) -> None:
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertAlmostEqual(compare.type7_p99(values), 4.96)

    def test_exact_equality_pass(self) -> None:
        values = self._base()
        reference = self._manifest("reference", np.array([values]))
        candidate = self._manifest("candidate", np.array([values]))
        result = compare.compare_manifests(reference, candidate, "tensorrt_fp16")
        self.assertEqual(result["overall_status"], "PASS")

    def test_shape_mismatch_fails(self) -> None:
        values = self._base()
        reference = self._manifest("reference", np.array([values]))
        candidate = self._manifest("candidate", np.array([values]))
        raw = json.loads(candidate.read_text())
        raw["entries"][0]["shape"] = [1, 10, 8399]
        candidate.write_text(json.dumps(raw) + "\n")
        with self.assertRaises(compare.CompareError):
            compare.compare_manifests(reference, candidate, "ort_strict")

    def test_missing_entry_fails(self) -> None:
        values = self._base()
        reference = self._manifest("reference", np.array([values, values]), ["a", "b"])
        candidate = self._manifest("candidate", np.array([values]), ["a"])
        with self.assertRaises(compare.CompareError):
            compare.compare_manifests(reference, candidate, "ort_strict")

    def test_non_finite_fails(self) -> None:
        values = self._base()
        reference = self._manifest("reference", np.array([values]))
        candidate_values = values.copy()
        candidate_values[0] = np.nan
        candidate = self._manifest("candidate", np.array([candidate_values]))
        with self.assertRaises(compare.CompareError):
            compare.compare_manifests(reference, candidate, "ort_strict")

    def test_bbox_and_score_policy_boundaries(self) -> None:
        reference_values = self._base()
        candidate_values = reference_values.copy()
        candidate_values[0] = 4.0
        candidate_values[4 * 8400] = 0.02
        reference = self._manifest("reference", np.array([reference_values]))
        candidate = self._manifest("candidate", np.array([candidate_values]))
        result = compare.compare_manifests(reference, candidate, "tensorrt_fp16")
        self.assertEqual(result["overall_status"], "PASS")
        candidate_values[4 * 8400] = 0.020001
        candidate = self._manifest("candidate_fail", np.array([candidate_values]))
        result = compare.compare_manifests(reference, candidate, "tensorrt_fp16")
        self.assertEqual(result["overall_status"], "FAIL")

    def test_mae_and_max_abs_failure(self) -> None:
        reference_values = self._base()
        candidate_values = np.full(compare.COUNT, 0.000002, dtype="<f4")
        reference = self._manifest("reference", np.array([reference_values]))
        candidate = self._manifest("candidate", np.array([candidate_values]))
        result = compare.compare_manifests(reference, candidate, "ort_strict")
        self.assertEqual(result["overall_status"], "FAIL")

    def test_one_tensor_failure_fails_aggregate(self) -> None:
        reference_values = np.zeros((2, compare.COUNT), dtype="<f4")
        candidate_values = reference_values.copy()
        candidate_values[1, 0] = 0.1
        reference = self._manifest("reference", reference_values, ["a", "b"])
        candidate = self._manifest("candidate", candidate_values, ["a", "b"])
        result = compare.compare_manifests(reference, candidate, "ort_strict")
        self.assertEqual(result["entry_count"], 2)
        self.assertEqual(result["overall_status"], "FAIL")
        self.assertTrue(result["entries"][0]["pass"])
        self.assertFalse(result["entries"][1]["pass"])

    def test_repeatability_sha_match_and_mismatch(self) -> None:
        values = self._base()
        first = self._manifest("first", np.array([values]))
        second = self._manifest("second", np.array([values]))
        result = compare.compare_repeatability(first, second)
        self.assertEqual(result["overall_status"], "PASS")
        changed = values.copy()
        changed[0] = 1.0
        third = self._manifest("third", np.array([changed]))
        result = compare.compare_repeatability(first, third)
        self.assertEqual(result["overall_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
