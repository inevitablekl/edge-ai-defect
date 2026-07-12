from __future__ import annotations

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_train_module():
    module_path = REPO_ROOT / "scripts" / "train_yolo.py"
    spec = importlib.util.spec_from_file_location("train_yolo", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


train_yolo = load_train_module()


class BuildTrainCommandTest(unittest.TestCase):
    def test_allowlisted_false_and_zero_values_are_forwarded(self):
        config = {
            "task": "detect",
            "mode": "train",
            "model": "model.pt",
            "dataset_yaml": "dataset.yaml",
            "imgsz": 640,
            "epochs": 100,
            "batch": 16,
            "device": 0,
            "deterministic": False,
            "mosaic": 0.0,
            "close_mosaic": 0,
            "warmup_epochs": 0,
            "cos_lr": False,
            "lr0": 0.001,
            "unused_training_field": "must-not-leak",
        }

        command = train_yolo.build_train_command(config, Path("experiment"))

        for expected in (
            "deterministic=False",
            "mosaic=0.0",
            "close_mosaic=0",
            "warmup_epochs=0",
            "cos_lr=False",
            "lr0=0.001",
        ):
            self.assertIn(expected, command)
        self.assertFalse(any(item.startswith("unused_training_field=") for item in command))

    def test_none_and_missing_values_are_not_forwarded(self):
        config = {
            "task": "detect",
            "mode": "train",
            "model": "model.pt",
            "dataset_yaml": "dataset.yaml",
            "imgsz": 640,
            "epochs": 100,
            "batch": 16,
            "device": 0,
            "mosaic": None,
        }

        command = train_yolo.build_train_command(config, Path("experiment"))

        self.assertFalse(any(item.startswith("mosaic=") for item in command))
        self.assertFalse(any(item.startswith("deterministic=") for item in command))

    def test_repository_configs_have_no_unhandled_training_keys(self):
        launcher_keys = {
            "experiment_name",
            "dataset_yaml",
            "model",
            "task",
            "mode",
            "imgsz",
            "epochs",
            "batch",
            "device",
            "experiment_root",
            *train_yolo.TRAIN_OPTION_KEYS,
        }
        for config_path in sorted((REPO_ROOT / "configs" / "train").glob("*.yaml")):
            with self.subTest(config=config_path.name):
                config = train_yolo.load_config(config_path)
                self.assertEqual(set(config) - launcher_keys, set())


class MetricsSummaryTest(unittest.TestCase):
    def test_last_and_best_recorded_metrics_are_distinct(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            results_path = run_dir / "train" / "results.csv"
            results_path.parent.mkdir(parents=True)
            with results_path.open("w", newline="", encoding="utf-8") as output:
                writer = csv.DictWriter(
                    output,
                    fieldnames=["epoch", "metrics/mAP50(B)", "metrics/mAP50-95(B)"],
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {"epoch": 1, "metrics/mAP50(B)": 0.7, "metrics/mAP50-95(B)": 0.4},
                        {"epoch": 2, "metrics/mAP50(B)": 0.6, "metrics/mAP50-95(B)": 0.3},
                    ]
                )

            summary = train_yolo.read_metrics_summary(run_dir, configured_epochs=100)

        self.assertIsNotNone(summary)
        assert summary is not None
        self.assertEqual(summary["configured_epochs"], 100)
        self.assertEqual(summary["completed_epochs"], 2)
        self.assertEqual(summary["last_epoch"], 2)
        self.assertEqual(summary["best_epoch_by_map50_95"], 1)
        self.assertEqual(summary["last_epoch_metrics"]["metrics/mAP50-95(B)"], 0.3)
        self.assertEqual(summary["best_recorded_metrics"]["metrics/mAP50-95(B)"], 0.4)


if __name__ == "__main__":
    unittest.main()
