#!/usr/bin/env python3
"""Launch YOLOv8n training from a YAML config with reproducibility records.

The script never downloads datasets and never fabricates metrics. It validates
that the configured dataset.yaml exists before a dry-run or real run.
"""

from __future__ import annotations

import argparse
import json
import platform
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REQUIRED_CONFIG_KEYS = (
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
)
SMOKE_OVERRIDES = {
    "epochs": 1,
    "imgsz": 320,
    "batch": 2,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run or dry-run a YOLO training experiment from YAML config."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Training YAML config path, for example configs/train/yolov8n_neudet_640.yaml.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and print the planned command without creating experiment files.",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Override epochs=1, imgsz=320, and batch=2 for a quick chain check.",
    )
    return parser.parse_args()


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Training config not found: {config_path}")
    text = config_path.read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore
    except ImportError:
        return parse_simple_yaml(text, config_path)

    loaded = yaml.safe_load(text)
    if not isinstance(loaded, dict):
        raise ValueError(f"Training config must be a YAML mapping: {config_path}")
    return loaded


def parse_simple_yaml(text: str, config_path: Path) -> dict[str, Any]:
    config: dict[str, Any] = {}
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError(
                f"Unsupported YAML syntax in {config_path}:{line_number}. "
                "Install PyYAML for complex YAML."
            )
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ValueError(f"Empty YAML key in {config_path}:{line_number}")
        config[key] = parse_scalar(value)
    return config


def parse_scalar(value: str) -> Any:
    if value == "":
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        return value


def validate_config(config: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_CONFIG_KEYS if key not in config]
    if missing:
        raise ValueError(f"Missing required training config fields: {missing}")

    dataset_yaml = Path(str(config["dataset_yaml"]))
    if not dataset_yaml.exists():
        raise FileNotFoundError(
            f"Dataset YAML not found: {dataset_yaml}. "
            "Run dataset conversion after manually providing NEU-DET data; "
            "do not create a fake dataset.yaml."
        )

    for int_key in ("imgsz", "epochs", "batch"):
        value = config[int_key]
        if not isinstance(value, int) or value <= 0:
            raise ValueError(f"Config field '{int_key}' must be a positive integer: {value}")


def apply_smoke_overrides(config: dict[str, Any]) -> dict[str, Any]:
    updated = dict(config)
    updated.update(SMOKE_OVERRIDES)
    updated["experiment_name"] = f"{config['experiment_name']}_smoke"
    return updated


def run_command(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Not available"


def collect_environment_text() -> str:
    lines = [
        f"python: {sys.version.replace(chr(10), ' ')}",
        f"platform: {platform.platform()}",
        f"machine: {platform.machine()}",
        f"processor: {platform.processor() or 'Not available'}",
        f"git_commit: {current_git_commit()}",
        f"git_status_short: {current_git_status()}",
        "ultralytics_version: "
        + run_command([sys.executable, "-c", "import ultralytics; print(ultralytics.__version__)"]),
        "torch_version: "
        + run_command([sys.executable, "-c", "import torch; print(torch.__version__)"]),
    ]
    return "\n".join(lines) + "\n"


def current_git_commit() -> str:
    return run_command(["git", "rev-parse", "HEAD"])


def current_git_status() -> str:
    return run_command(["git", "status", "--short"])


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timestamp_for_path() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_run_dir(config: dict[str, Any]) -> Path:
    experiment_root = Path(str(config["experiment_root"]))
    run_name = f"{config['experiment_name']}_{timestamp_for_path()}"
    return experiment_root / run_name


def build_train_command(config: dict[str, Any], run_dir: Path) -> list[str]:
    command = [
        "yolo",
        str(config["task"]),
        str(config["mode"]),
        f"model={config['model']}",
        f"data={config['dataset_yaml']}",
        f"imgsz={config['imgsz']}",
        f"epochs={config['epochs']}",
        f"batch={config['batch']}",
        f"device={config['device']}",
        f"project={run_dir}",
        "name=train",
        "exist_ok=False",
    ]
    optional_keys = ("workers", "patience", "seed", "optimizer")
    for key in optional_keys:
        if key in config and config[key] is not None:
            command.append(f"{key}={config[key]}")
    return command


def write_run_records(
    run_dir: Path,
    config_path: Path,
    config: dict[str, Any],
    command: list[str],
    start_time: str,
    end_time: str | None,
    status: str,
    return_code: int | None,
) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_path, run_dir / "config.yaml")
    (run_dir / "command.txt").write_text(shlex.join(command) + "\n", encoding="utf-8")
    (run_dir / "git_commit.txt").write_text(current_git_commit() + "\n", encoding="utf-8")
    (run_dir / "environment.txt").write_text(collect_environment_text(), encoding="utf-8")
    (run_dir / "start_time.txt").write_text(start_time + "\n", encoding="utf-8")
    if end_time is not None:
        (run_dir / "end_time.txt").write_text(end_time + "\n", encoding="utf-8")
    summary = {
        "status": status,
        "return_code": return_code,
        "start_time": start_time,
        "end_time": end_time,
        "config_path": str(config_path),
        "run_dir": str(run_dir),
        "dataset_yaml": str(config["dataset_yaml"]),
        "command": command,
        "note": "No metrics are written by this launcher. Use real training logs only.",
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def print_plan(config_path: Path, config: dict[str, Any], run_dir: Path, command: list[str]) -> None:
    print("YOLO training plan")
    print(f"  config: {config_path}")
    print(f"  dataset_yaml: {config['dataset_yaml']}")
    print(f"  experiment_dir: {run_dir}")
    print(f"  command: {shlex.join(command)}")


def main() -> int:
    try:
        args = parse_args()
        config = load_config(args.config)
        if args.smoke:
            config = apply_smoke_overrides(config)
        validate_config(config)
        run_dir = build_run_dir(config)
        command = build_train_command(config, run_dir)
        print_plan(args.config, config, run_dir, command)

        if args.dry_run:
            print("Dry run complete. Training was not started and no experiment files were written.")
            return 0

        start = timestamp()
        write_run_records(
            run_dir=run_dir,
            config_path=args.config,
            config=config,
            command=command,
            start_time=start,
            end_time=None,
            status="running",
            return_code=None,
        )
        try:
            completed = subprocess.run(command, check=False)
            return_code = completed.returncode
        except FileNotFoundError as exc:
            print(f"ERROR: training command not found: {command[0]}", file=sys.stderr)
            print(f"ERROR: {exc}", file=sys.stderr)
            return_code = 1
        end = timestamp()
        status = "completed" if return_code == 0 else "failed"
        write_run_records(
            run_dir=run_dir,
            config_path=args.config,
            config=config,
            command=command,
            start_time=start,
            end_time=end,
            status=status,
            return_code=return_code,
        )
        return return_code
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
