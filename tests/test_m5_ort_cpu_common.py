#!/usr/bin/env python3
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "benchmark"))
import m5_ort_cpu_common as common


def cycle_manifest(root: Path, count: int = 20):
    entries = []
    for index in range(count):
        name = f"{index:04d}_frame_{index}.jpg"
        data = bytes([index]) * 8
        (root / name).write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        entries.append({"source_filename": f"frame_{index}.jpg", "prepared_filename": name,
                        "source_sha256": digest, "prepared_sha256": digest,
                        "width": 200, "height": 200, "derived": False})
    manifest = {"schema_version": 1, "corpus_mode": "benchmark",
                "manifest_path": "tests/data/m5/manifests/benchmark_corpus.json", "entries": entries}
    common.write_stable_json(root / "prepared_corpus_manifest.json", manifest)
    return manifest


class CommonTests(unittest.TestCase):
    def test_manifest_is_frozen_and_valid(self):
        manifest = common.load_benchmark_manifest()
        self.assertEqual(len(manifest["entries"]), 20)
        self.assertEqual([entry["sequence_index"] for entry in manifest["entries"]], list(range(20)))
        self.assertEqual(manifest["entries"][:12][0]["source_filename"], "crazing_51.jpg")

    def test_manifest_rejects_wrong_count(self):
        manifest = common.load_benchmark_manifest()
        with self.assertRaises(common.BenchmarkError):
            common.validate_benchmark_manifest({**manifest, "entries": manifest["entries"][:-1]})

    def test_workload_repeats_cycle_with_stable_mapping_and_regular_copies(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cycle = root / "cycle"
            cycle.mkdir()
            cycle_manifest(cycle)
            output = root / "workload"
            first = common.build_workload(cycle, output, 100)
            self.assertEqual(len(first["entries"]), 100)
            self.assertEqual(first["entries"][0]["cycle_index"], 0)
            self.assertEqual(first["entries"][20]["cycle_index"], 1)
            self.assertEqual(first["entries"][20]["source_sequence_index"], 0)
            self.assertEqual([entry["workload_filename"] for entry in first["entries"][:2]],
                             ["000000_frame_0.jpg", "000001_frame_1.jpg"])
            self.assertTrue(all((output / entry["workload_filename"]).stat().st_nlink == 1 for entry in first["entries"]))
            self.assertEqual(common.sha256_file(output / "workload_manifest.json"), common.sha256_file(output / "workload_manifest.json"))
            with self.assertRaises(common.BenchmarkError):
                common.build_workload(cycle, root / "invalid", 21)
            with self.assertRaises(common.BenchmarkError):
                common.build_workload(cycle, output, 100)

    def test_pilot_frame_math_and_invalid_cases(self):
        samples = [10.0] * 100
        result = common.compute_formal_frame_counts(samples)
        self.assertEqual(result["pilot_discard_count"], 20)
        self.assertEqual(result["pilot_analyzed_count"], 80)
        self.assertEqual(result["target_measured_frames"], 3300)
        self.assertEqual(result["formal_total_frames"], 3360)
        self.assertEqual(result["formal_measured_frames"], 3310)
        with self.assertRaises(common.BenchmarkError):
            common.compute_formal_frame_counts([10.0] * 99)
        with self.assertRaises(common.BenchmarkError):
            common.compute_formal_frame_counts([0.0] * 100)
        with self.assertRaises(common.BenchmarkError):
            common.compute_formal_frame_counts([float("nan")] + [10.0] * 99)

    def test_type7_sample_stddev_and_outlier_are_not_removed(self):
        values = [1.0, 1.0, 1.0, 1000.0]
        self.assertEqual(common.type7_quantile([1, 2, 3, 4], 0.5), 2.5)
        self.assertAlmostEqual(common.type7_quantile([1, 2, 3, 4], 0.95), 3.85)
        summary = common.summarize_values(values)
        self.assertEqual(summary["sample_count"], 4)
        self.assertEqual(summary["maximum"], 1000.0)
        self.assertGreater(summary["mean"], 1.0)
        self.assertGreater(summary["sample_standard_deviation"], 0.0)
        with self.assertRaises(common.BenchmarkError):
            common.sample_stddev([1.0])

    def test_deterministic_gzip_and_affinity_selection(self):
        raw = b'{"schema_version":1}\n'
        first = common.deterministic_gzip(raw)
        second = common.deterministic_gzip(raw)
        self.assertEqual(first, second)
        self.assertEqual(__import__("gzip").decompress(first), raw)
        self.assertEqual(common.select_lowest_cpu({2, 4, 5}), 2)
        with self.assertRaises(common.BenchmarkError):
            common.select_lowest_cpu(set())


if __name__ == "__main__":
    unittest.main()
