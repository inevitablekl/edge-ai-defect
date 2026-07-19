#!/usr/bin/env python3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "benchmark"))
import run_m5_ort_cpu_baseline as runner
import m5_ort_cpu_common as common


class Result:
    def __init__(self, code=0, stdout="", stderr=""):
        self.returncode = code
        self.stdout = stdout
        self.stderr = stderr
        self.pid = id(self)


class RunnerTests(unittest.TestCase):
    def test_runtime_config_preserves_application_schema_and_timing(self):
        config = runner.build_runtime_config(Path("contract.yaml"), Path("model.onnx"), Path("workload"), Path("raw.json"))
        self.assertTrue(config["timing"]["enabled"])
        self.assertFalse(config["output"]["console"])
        self.assertTrue(config["output"]["overwrite"])
        self.assertEqual(config["postprocess"]["max_det"], 300)

    def test_six_independent_invocations_and_exactly_four_waits(self):
        calls = []
        waits = []
        def invoke(command, **kwargs):
            calls.append((command, kwargs))
            return Result()
        commands = [["app", "--config", str(index)] for index in range(6)]
        records = runner.execute_formal_runs(commands, invoke=invoke, sleep_fn=waits.append, cwd=Path("."))
        self.assertEqual(len(records), 6)
        self.assertEqual(len(calls), 6)
        self.assertEqual(waits, [30, 30, 30, 30])
        self.assertEqual([record.phase for record in records], ["pilot", "formal_run_1", "formal_run_2", "formal_run_3", "formal_run_4", "formal_run_5"])

    def test_failure_stops_and_does_not_sleep_or_continue(self):
        calls = []
        waits = []
        def invoke(command, **kwargs):
            calls.append(command)
            return Result(4 if len(calls) == 3 else 0)
        with self.assertRaises(common.BenchmarkError):
            runner.execute_formal_runs([["app", str(i)] for i in range(6)], invoke=invoke, sleep_fn=waits.append)
        self.assertEqual(len(calls), 3)
        self.assertEqual(waits, [30])

    def test_staging_is_atomic_and_existing_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = runner.stage_evidence(root, "20260719_aaaaaaa", {"README.txt": "NON-FORMAL DEVELOPMENT SMOKE\n"})
            self.assertTrue((target / "README.txt").is_file())
            with self.assertRaises(common.EvidenceError):
                runner.stage_evidence(root, "20260719_aaaaaaa", {"x": "y"})

    def test_development_smoke_never_targets_formal_results(self):
        parser = runner._parser()
        args = parser.parse_args(["--dataset-root", ".", "--cpp-executable", "app", "--build-dir", ".", "--output-root", "results/benchmark/ort_cpu", "--development-smoke"])
        self.assertTrue(args.development_smoke)


if __name__ == "__main__":
    unittest.main()
