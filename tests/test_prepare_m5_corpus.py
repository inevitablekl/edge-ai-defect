#!/usr/bin/env python3
"""Unit tests for the M5 corpus contract and preparation tool."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("prepare_m5_corpus", ROOT / "tools/validation/prepare_m5_corpus.py")
assert SPEC and SPEC.loader
tool = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tool)


class M5CorpusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original, self.derived, self.benchmark = tool.load_manifests()

    def test_frozen_manifests_validate(self) -> None:
        self.assertEqual([len(x["entries"]) for x in (self.original, self.derived, self.benchmark)], [12, 4, 20])

    def test_unknown_missing_duplicate_and_wrong_types_fail(self) -> None:
        unknown = copy.deepcopy(self.original)
        unknown["unknown"] = 1
        with self.assertRaises(tool.ManifestError):
            tool.validate_original(unknown)
        missing = copy.deepcopy(self.original)
        del missing["entries"][0]["roles"]
        with self.assertRaises(tool.ManifestError):
            tool.validate_original(missing)
        wrong = copy.deepcopy(self.original)
        wrong["entries"][0]["sequence_index"] = True
        with self.assertRaises(tool.ManifestError):
            tool.validate_original(wrong)
        duplicate = '{"schema_version":1,"schema_version":1}\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text(duplicate, encoding="utf-8")
            with self.assertRaises(tool.ManifestError):
                tool._read_json(path)

    def test_path_sha_order_and_coverage_fail(self) -> None:
        for field, value in (("source_filename", "/absolute.jpg"), ("prepared_filename", "../escape.jpg"), ("expected_sha256", "z" * 64)):
            candidate = copy.deepcopy(self.original)
            candidate["entries"][0][field] = value
            with self.assertRaises(tool.ManifestError):
                tool.validate_original(candidate)
        candidate = copy.deepcopy(self.original)
        candidate["entries"][1]["sequence_index"] = 4
        with self.assertRaises(tool.ManifestError):
            tool.validate_original(candidate)
        candidate = copy.deepcopy(self.original)
        candidate["entries"][0]["gt_classes"] = []
        with self.assertRaises(tool.ManifestError):
            tool.validate_original(candidate)

    def test_derived_contract_failures(self) -> None:
        candidate = copy.deepcopy(self.derived)
        candidate["entries"][0]["source_expected_sha256"] = "0" * 64
        with self.assertRaises(tool.ManifestError):
            tool.validate_derived(candidate, self.original)
        candidate = copy.deepcopy(self.derived)
        candidate["entries"][0]["right"] = 60
        with self.assertRaises(tool.ManifestError):
            tool.validate_derived(candidate, self.original)
        candidate = copy.deepcopy(self.derived)
        candidate["entries"][0]["prepared_filename"] = "0013_wrong.bmp"
        with self.assertRaises(tool.ManifestError):
            tool.validate_derived(candidate, self.original)

    def test_benchmark_contract_failures(self) -> None:
        candidate = copy.deepcopy(self.benchmark)
        candidate["entries"] = candidate["entries"][:-1]
        with self.assertRaises(tool.ManifestError):
            tool.validate_benchmark(candidate)
        candidate = copy.deepcopy(self.benchmark)
        candidate["split"] = "train"
        with self.assertRaises(tool.ManifestError):
            tool.validate_benchmark(candidate)

    def test_preparation_uses_regular_copies_and_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "images"
            root.mkdir()
            original = copy.deepcopy(self.original)
            benchmark = copy.deepcopy(self.benchmark)
            for index, name in enumerate(dict.fromkeys(e["source_filename"] for e in benchmark["entries"])):
                image = np.full((200, 200, 3), index * 7 % 255, dtype=np.uint8)
                path = root / name
                self.assertTrue(cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, 100]))
                digest = hashlib.sha256(path.read_bytes()).hexdigest()
                for entry in original["entries"]:
                    if entry["source_filename"] == name:
                        entry["expected_sha256"] = digest
                for entry in benchmark["entries"]:
                    if entry["source_filename"] == name:
                        entry["expected_sha256"] = digest
            derived = copy.deepcopy(self.derived)
            for entry in derived["entries"]:
                source = next(e for e in original["entries"] if e["source_filename"] == entry["source_filename"])
                entry["source_expected_sha256"] = source["expected_sha256"]
                image = cv2.imread(str(root / entry["source_filename"]), cv2.IMREAD_COLOR)
                resized = cv2.resize(image, (entry["resized_width"], entry["resized_height"]), interpolation=cv2.INTER_LINEAR)
                output = cv2.copyMakeBorder(resized, entry["top"], entry["bottom"], entry["left"], entry["right"], cv2.BORDER_CONSTANT, value=(114, 114, 114))
                temp = Path(directory) / (entry["prepared_filename"] + ".bmp")
                cv2.imwrite(str(temp), output)
                entry["expected_output_sha256"] = hashlib.sha256(temp.read_bytes()).hexdigest()
            old = (tool.ORIGINAL_MANIFEST, tool.DERIVED_MANIFEST, tool.BENCHMARK_MANIFEST)
            try:
                manifest_paths = tuple(Path(directory) / name for name in ("original.json", "derived.json", "benchmark.json"))
                tool.ORIGINAL_MANIFEST, tool.DERIVED_MANIFEST, tool.BENCHMARK_MANIFEST = manifest_paths
                for path, value in zip(manifest_paths, (original, derived, benchmark)):
                    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
                first = Path(directory) / "first"
                second = Path(directory) / "second"
                tool.prepare("level-c", root, first)
                tool.prepare("level-c", root, second)
                first_bytes = sorted(p.read_bytes() for p in first.glob("*.bmp"))
                second_bytes = sorted(p.read_bytes() for p in second.glob("*.bmp"))
                self.assertEqual(first_bytes, second_bytes)
                self.assertEqual(len(list(first.glob("*.jpg"))), 12)
                self.assertTrue(all(p.is_file() and not p.is_symlink() for p in first.iterdir()))
                with self.assertRaises(tool.PreparationError):
                    tool.prepare("level-c", root, first)
            finally:
                tool.ORIGINAL_MANIFEST, tool.DERIVED_MANIFEST, tool.BENCHMARK_MANIFEST = old


if __name__ == "__main__":
    unittest.main()
