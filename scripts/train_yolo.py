#!/usr/bin/env python3
"""Skeleton for launching and recording YOLOv8n training experiments.

Default behavior is dry-run: it creates an experiment directory and records the
planned command, environment snapshot, git commit, and config snapshot without
starting training. Use --execute later when the dataset and training environment
are ready.
"""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_EXPERIMENT_ROOT = Path("experiments/training")
DEFAULT_MODEL_OUTPUT_DIR = Path("models/pytorch")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare or run a YOLO training experiment with reproducibility records."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Training YAML config path. The file must be provided manually.",
    )
    parser.add_argument(
        "--dataset-yaml",
        type=Path,
        required=True,
        help="YOLO dataset.yaml path generated after dataset conversion.",
    )
    parser.add_argument(
        "--experiment-root",
        type=Path,
        default=DEFAULT_EXPERIMENT_ROOT,
        help=f"Root directory for training experiment records. Default: {DEFAULT_EXPERIMENT_ROOT}",
    )
    parser.add_argument(
        "--model-output-dir",
        type=Path,
        default=DEFAULT_MODEL_OUTPUT_DIR,
        help=f"Directory reserved for PyTorch weights. Default: {DEFAULT_MODEL_OUTPUT_DIR}",
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        choices=(320, 416, 640),
        default=640,
        help="YOLO input size.",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=100,
        help="Training epochs to include in the planned command.",
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Training batch size to include in the planned command.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="0",
        help="Training device identifier for ultralytics.",
    )
    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Optional run name. Defaults to timestamped name.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute the training command. Default is dry-run.",
    )
    return parser.parse_args()


def run_command(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Not available"


def current_git_commit() -> str:
    return run_command(["git", "rev-parse", "HEAD"])


def current_git_status() -> str:
    return run_command(["git", "status", "--short"])


def collect_environment() -> dict[str, str]:
    return {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "Not available",
        "git_commit": current_git_commit(),
        "git_status_short": current_git_status(),
        "ultralytics_version": run_command(
            [sys.executable, "-c", "import ultralytics; print(ultralytics.__version__)"]
        ),
        "torch_version": run_command(
            [sys.executable, "-c", "import torch; print(torch.__version__)"]
        ),
    }


def validate_inputs(args: argparse.Namespace) -> None:
    if not args.config.exists():
        raise FileNotFoundError(
            f"Training config not found: {args.config}. "
            "Create it manually under configs/train/ before running training."
        )
    if not args.dataset_yaml.exists():
        raise FileNotFoundError(
            f"Dataset YAML not found: {args.dataset_yaml}. "
            "Run dataset conversion after manually providing NEU-DET data."
        )


def build_train_command(args: argparse.Namespace, run_dir: Path) -> list[str]:
    return [
        "yolo",
        "detect",
        "train",
        "model=yolov8n.pt",
        f"data={args.dataset_yaml}",
        f"imgsz={args.imgsz}",
        f"epochs={args.epochs}",
        f"batch={args.batch}",
        f"device={args.device}",
        f"project={run_dir.parent}",
        f"name={run_dir.name}",
    ]


def create_run_dir(args: argparse.Namespace) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = args.run_name or f"yolov8n_neudet_{args.imgsz}_{timestamp}"
    run_dir = args.experiment_root / run_name
    run_dir.mkdir(parents=True, exist_ok=False)
    args.model_output_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_records(args: argparse.Namespace, run_dir: Path, command: list[str]) -> None:
    shutil.copy2(args.config, run_dir / "train_config.yaml")
    shutil.copy2(args.dataset_yaml, run_dir / "dataset_snapshot.yaml")
    (run_dir / "train_command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")
    (run_dir / "environment_snapshot.json").write_text(
        json.dumps(collect_environment(), indent=2),
        encoding="utf-8",
    )
    manifest = {
        "run_dir": str(run_dir),
        "config": str(args.config),
        "dataset_yaml": str(args.dataset_yaml),
        "model_output_dir": str(args.model_output_dir),
        "imgsz": args.imgsz,
        "epochs": args.epochs,
        "batch": args.batch,
        "device": args.device,
        "execute": args.execute,
        "status": "prepared" if not args.execute else "execution_requested",
        "note": "No metrics are recorded here until real training completes.",
    }
    (run_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    args = parse_args()
    validate_inputs(args)
    run_dir = create_run_dir(args)
    command = build_train_command(args, run_dir)
    write_records(args, run_dir, command)

    print(f"Training experiment directory prepared: {run_dir}")
    print(f"Recorded command: {' '.join(command)}")

    if not args.execute:
        print("Dry run complete. Training was not started. Use --execute when ready.")
        return 0

    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
