from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "generate_evidence_patch.py"


def load_generator_module():
    spec = importlib.util.spec_from_file_location("generate_evidence_patch", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load_generator_module()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EvidenceGeneratorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        experiment = self.root / "experiments" / "run"
        train = experiment / "train"
        (train / "weights").mkdir(parents=True)
        (self.root / "configs").mkdir()
        (self.root / "evidence").mkdir()
        (self.root / "models").mkdir()
        (self.root / "test_eval" / "test").mkdir(parents=True)

        (train / "args.yaml").write_text(
            "model: models/pretrained.pt\n"
            "data: data/dataset.yaml\n"
            "epochs: 2\n"
            "imgsz: 640\n"
            "batch: 2\n"
            "seed: 42\n"
            "deterministic: true\n",
            encoding="utf-8",
        )
        (train / "results.csv").write_text(
            "epoch,metrics/mAP50-95(B)\n1,0.4\n2,0.3\n",
            encoding="utf-8",
        )
        checkpoint = b"test checkpoint"
        (train / "weights" / "best.pt").write_bytes(checkpoint)
        (self.root / "models" / "frozen.pt").write_bytes(checkpoint)
        (experiment / "git_commit.txt").write_text("abc123\n", encoding="utf-8")
        (self.root / "configs" / "train.yaml").write_text("epochs: 2\n", encoding="utf-8")
        (self.root / "test_eval" / "test" / "predictions.json").write_text("[]\n", encoding="utf-8")
        (self.root / "test_eval" / "test_summary.json").write_text("{}\n", encoding="utf-8")

        for name in (
            "validation.json",
            "test.json",
        ):
            (self.root / "evidence" / name).write_text("{}\n", encoding="utf-8")
        for name in (
            "validation.csv",
            "test.csv",
        ):
            (self.root / "evidence" / name).write_text("value\n1\n", encoding="utf-8")
        (self.root / "evidence" / "test_command.txt").write_text("existing test command\n", encoding="utf-8")
        (self.root / "evidence" / "validation_command.txt").write_text("existing validation command\n", encoding="utf-8")
        (self.root / "evidence" / "test_environment.txt").write_text("python: test\n", encoding="utf-8")

        manifest = {
            "frozen_source_experiment": "baseline",
            "validation_metrics_json": "evidence/validation.json",
            "validation_metrics_csv": "evidence/validation.csv",
            "validation_command": "evidence/validation_command.txt",
            "test_metrics_json": "evidence/test.json",
            "test_metrics_csv": "evidence/test.csv",
            "test_command": "evidence/test_command.txt",
            "test_environment": "evidence/test_environment.txt",
            "experiments": [
                {
                    "experiment_name": "baseline",
                    "slug": "baseline",
                    "directory": "experiments/run",
                    "config_path": "configs/train.yaml",
                }
            ],
        }
        self.manifest_path = self.root / "manifest.json"
        self.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def generate(self, output: Path):
        return generator.generate_evidence_package(
            project_root=self.root,
            output_dir=output,
            experiment_manifest=self.manifest_path,
            frozen_model=Path("models/frozen.pt"),
            test_evaluation_dir=Path("test_eval"),
        )

    def test_source_has_no_hardcoded_server_root_or_gpu_dependency(self):
        source = MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("/root/wklproject", source)
        self.assertNotIn("from ultralytics", source)
        self.assertNotIn("import torch", source)

    def test_missing_required_file_fails_before_output_creation(self):
        (self.root / "experiments" / "run" / "train" / "args.yaml").unlink()
        output = self.root / "output"

        with self.assertRaises(FileNotFoundError):
            self.generate(output)

        self.assertFalse(output.exists())

    def test_default_does_not_overwrite(self):
        output = self.root / "output"
        self.generate(output)

        with self.assertRaises(FileExistsError):
            self.generate(output)

    def test_manifest_hashes_and_archive_checksum_are_correct(self):
        output = self.root / "output"
        archive, checksum = self.generate(output)

        manifest_lines = (output / "MANIFEST.txt").read_text(encoding="utf-8").splitlines()
        entries = [
            re.match(r"^([0-9a-f]{64})  (\d+)  \./(.+)$", line)
            for line in manifest_lines
        ]
        entries = [match for match in entries if match is not None]
        self.assertGreater(len(entries), 0)
        for match in entries:
            expected_hash, expected_size, relative = match.groups()
            path = output / relative
            self.assertEqual(sha256(path), expected_hash)
            self.assertEqual(path.stat().st_size, int(expected_size))

        recorded_hash = checksum.read_text(encoding="utf-8").split()[0]
        self.assertEqual(recorded_hash, sha256(archive))
        self.assertTrue((output / "frozen_test_artifacts" / "test_summary.json").is_file())

    def test_explicit_overwrite_rebuilds_identical_archive(self):
        output = self.root / "output"
        archive, _ = self.generate(output)
        first_hash = sha256(archive)

        rebuilt, _ = generator.generate_evidence_package(
            project_root=self.root,
            output_dir=output,
            experiment_manifest=self.manifest_path,
            frozen_model=Path("models/frozen.pt"),
            test_evaluation_dir=Path("test_eval"),
            overwrite=True,
        )

        self.assertEqual(first_hash, sha256(rebuilt))


if __name__ == "__main__":
    unittest.main()
