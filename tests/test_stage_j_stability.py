#!/usr/bin/env python3

from pathlib import Path
import json
import tempfile
import unittest
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/benchmark"))

from run_stage_j_stability import (
    canonical_cycle_hash,
    _read_optional_int,
    parse_duration_minutes,
    record_failure,
    unavailable,
)


class StageJStabilityTests(unittest.TestCase):
    def test_duration_parser(self):
        self.assertEqual(parse_duration_minutes("30"), 30.0)
        self.assertAlmostEqual(parse_duration_minutes("0.5"), 0.5)
        with self.assertRaises(Exception):
            parse_duration_minutes("0")
        with self.assertRaises(Exception):
            parse_duration_minutes("nan")

    def test_hash_is_deterministic(self):
        cycle = {"cycle_id": 1, "frame_count": 20, "success": True}
        self.assertEqual(canonical_cycle_hash(cycle), canonical_cycle_hash(cycle))
        self.assertNotEqual(canonical_cycle_hash(cycle), canonical_cycle_hash({**cycle, "cycle_id": 2}))

    def test_telemetry_unavailable_is_explicit(self):
        value = unavailable("/sys/example", "missing")
        self.assertEqual(value["status"], "unavailable")
        self.assertEqual(value["error"], "missing")

    def test_missing_telemetry_source_is_explicit(self):
        value = _read_optional_int(Path("/sys/example/stage_j6_missing"))
        self.assertEqual(value["status"], "unavailable")
        self.assertIn("path", value)

    def test_failure_recording(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "failure.json"
            record_failure(path, cycle=7, exception=RuntimeError("boom"))
            value = json.loads(path.read_text())
            self.assertEqual(value["status"], "FAIL")
            self.assertEqual(value["cycle"], 7)
            self.assertIn("RuntimeError", value["exception"])


if __name__ == "__main__":
    unittest.main()
