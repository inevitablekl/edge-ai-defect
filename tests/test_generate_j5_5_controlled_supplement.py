#!/usr/bin/env python3

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/benchmark"))

from m5_ort_cpu_common import BenchmarkError, stable_json_bytes, type7_quantile
from generate_j5_5_controlled_supplement import build_supplement


def runs(count=5):
    return [{
        "process_wall_ms": 100.0 + index,
        "fps": 10.0 - index * 0.1,
        "processed_frames": 560,
        "semantic_pass": True,
        "expected_cycle_sha256": "cycle",
        "payload_sha256": f"payload-{index}",
        "max_VmRSS_kB": 1000 + index,
    } for index in range(count)]


class ControlledSupplementTests(unittest.TestCase):
    def test_five_value_sample_standard_deviation(self):
        report = build_supplement(runs())
        self.assertEqual(report["whole_process_wall_time_ms"]["sample_count"], 5)
        self.assertAlmostEqual(
            report["whole_process_wall_time_ms"]["sample_standard_deviation"],
            1.5811388300841898)

    def test_type_7(self):
        self.assertEqual(type7_quantile([1, 2, 3, 4, 5], 0.5), 3.0)
        self.assertEqual(type7_quantile([1, 2, 3, 4, 5], 0.95), 4.8)

    def test_fewer_than_five_runs_fails(self):
        with self.assertRaises(BenchmarkError):
            build_supplement(runs(4))

    def test_missing_value_is_not_fabricated(self):
        value = runs()
        del value[2]["process_wall_ms"]
        with self.assertRaises(BenchmarkError):
            build_supplement(value)

    def test_deterministic_output(self):
        self.assertEqual(stable_json_bytes(build_supplement(runs())),
                         stable_json_bytes(build_supplement(runs())))


if __name__ == "__main__":
    unittest.main()
