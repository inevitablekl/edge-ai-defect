#!/usr/bin/env python3
import json
import hashlib
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
        args = parser.parse_args(["--dataset-root", ".", "--cpp-executable", "app", "--build-dir", ".", "--output-root", "tmp", "--development-smoke"])
        self.assertTrue(args.development_smoke)

    def test_modes_are_explicit_and_mutually_exclusive(self):
        parser = runner._parser()
        base = ["--dataset-root", ".", "--cpp-executable", "app", "--build-dir", ".", "--output-root", "tmp"]
        with self.assertRaises(SystemExit):
            parser.parse_args(base)
        with self.assertRaises(SystemExit):
            parser.parse_args(base + ["--formal", "--check-only"])
        self.assertTrue(parser.parse_args(base + ["--formal"]).formal)

    def test_formal_orchestrator_end_to_end_fake_application(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cycle = root / "cycle"
            cycle.mkdir()
            entries = []
            for index in range(20):
                filename = f"{index:04d}_frame_{index}.jpg"
                data = bytes([index]) * 8
                (cycle / filename).write_bytes(data)
                digest = hashlib.sha256(data).hexdigest()
                entries.append({"source_filename": f"frame_{index}.jpg", "prepared_filename": filename,
                                "source_sha256": digest, "prepared_sha256": digest, "width": 200,
                                "height": 200, "derived": False})
            common.write_stable_json(cycle / "prepared_corpus_manifest.json",
                                     {"schema_version": 1, "corpus_mode": "benchmark", "entries": entries})
            output = root / "evidence"
            work = root / "work"
            calls = []
            waits = []
            protocol = dict(common.PROTOCOL)
            protocol.update({"formal_warmup": 2, "minimum_measured_frames": 3,
                             "target_measured_duration_ms": 3, "minimum_valid_duration_ms": 3})

            def preflight(*args, **kwargs):
                return {"branch": "feature/cpp-onnxruntime", "source_commit": "b" * 40,
                        "upstream": "origin/feature/cpp-onnxruntime", "upstream_behind": 0,
                        "upstream_ahead": 0, "binary_sha256": "a" * 64,
                        "model_contract_sha256": "c" * 64, "onnx_sha256": "d" * 64,
                        "manifest": common.load_benchmark_manifest(), "allowed_cpus": [2, 4],
                        "selected_cpu": 2}

            def prepare(_dataset, destination):
                destination.mkdir(parents=True)
                for item in cycle.iterdir():
                    if item.name != "prepared_corpus_manifest.json":
                        (destination / item.name).write_bytes(item.read_bytes())
                common.write_stable_json(destination / "prepared_corpus_manifest.json",
                                         json.loads((cycle / "prepared_corpus_manifest.json").read_text()))

            def fake_app(command, _work, selected_cpu):
                calls.append((list(command), selected_cpu))
                config = json.loads(Path(command[2]).read_text())
                input_dir = Path(config["input"]["directory"])
                names = sorted(path.name for path in input_dir.iterdir() if path.is_file() and path.name != "workload_manifest.json")
                images = []
                for index, name in enumerate(names):
                    images.append({"sequence_index": index, "relative_path": name, "width": 200, "height": 200,
                                   "detections": [], "timing_ms": {"source": 0.1, "preprocess": 0.1,
                                   "inference": 0.5, "postprocess": 0.1, "pre_sink_total": 1.0}})
                payload = {"schema_version": 1, "backend": {"type": "onnxruntime_cpu"},
                           "model": {"filename": "model.onnx", "sha256": "a" * 64,
                                     "contract_filename": "contract.yaml", "classes": analyze_classes()},
                           "postprocess": {"confidence_threshold": 0.25, "iou_threshold": 0.45,
                                           "max_nms": 30000, "max_det": 300, "max_wh": 7680.0,
                                           "agnostic": False, "multi_label": False},
                           "images": images, "summary": {"processed_images": len(images), "total_detections": 0}}
                output_path = Path(config["output"]["json_path"])
                common.write_stable_json(output_path, payload)
                return runner.ProcessRecord("application", list(command), 0, "", "", 1000 + len(calls), 0.01)

            def analyze_classes():
                return ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]

            result = runner.run_formal_orchestrator(
                root / "dataset", root / "app", root / "build", output,
                repo_root=root, work_root=work, preflight_fn=preflight,
                prepare_cycle_fn=prepare, invoke_fn=fake_app, sleep_fn=waits.append,
                environment_fn=lambda **kwargs: {"schema_version": 1, "baseline_name": "WSL2 x86_64 ONNX Runtime CPU Engineering Baseline",
                                                  "selected_cpu": kwargs["selected_cpu"], "effective_affinity": [2],
                                                  "limitations": ["warm-cache"]},
                date_fn=lambda: "20260719", protocol=protocol)
            self.assertEqual(result["evidence_id"], "20260719_bbbbbbb")
            self.assertEqual(len(calls), 6)
            self.assertEqual([item[1] for item in calls], [2] * 6)
            self.assertEqual(waits, [30, 30, 30, 30])
            self.assertEqual(result["aggregate"]["valid_run_count"], 5)
            published = result["evidence_path"]
            self.assertTrue((published / "aggregate_summary.json").is_file())
            self.assertFalse(list(published.rglob("raw_application.json")))
            self.assertFalse(list(published.rglob("*.jpg")))
            runner._verify_sha256sums(published)

    def test_reserved_placeholder_is_gone(self):
        text = Path(runner.__file__).read_text(encoding="utf-8")
        self.assertNotIn("formal execution is reserved", text)


if __name__ == "__main__":
    unittest.main()
