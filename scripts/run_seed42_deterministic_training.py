#!/usr/bin/env python3
"""Run YOLOv8n deterministic seed=42 training via Python API.

This avoids shell-level process management issues.
Equivalent to: yolo detect train ... deterministic=true seed=42
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from ultralytics import YOLO

# Project root
PROJECT_ROOT = Path("/root/wklproject/edge-ai-defect")

# Config
MODEL_PATH = PROJECT_ROOT / "models/pretrained/yolov8n.pt"
DATA_YAML = PROJECT_ROOT / "data/yolo/neu_det/dataset.yaml"
RUN_ROOT = PROJECT_ROOT / "experiments/training"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_NAME = f"yolov8n_neudet_baseline_seed42_deterministic_{TIMESTAMP}"
RUN_DIR = RUN_ROOT / RUN_NAME

os.environ["YOLO_OFFLINE"] = "true"

def main():
    # Create run directory
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    # Write records
    import subprocess
    git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True, cwd=PROJECT_ROOT).strip()

    (RUN_DIR / "git_commit.txt").write_text(git_commit + "\n")
    (RUN_DIR / "start_time.txt").write_text(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

    import shutil
    shutil.copy2(
        PROJECT_ROOT / "configs/train/yolov8n_neudet_baseline_seed42_deterministic.yaml",
        RUN_DIR / "config.yaml",
    )

    command = (
        "yolo detect train model=models/pretrained/yolov8n.pt "
        "data=data/yolo/neu_det/dataset.yaml imgsz=640 epochs=100 batch=16 "
        "device=0 workers=4 patience=30 seed=42 deterministic=true "
        f"optimizer=auto amp=False mosaic=1.0 project={RUN_DIR} name=train exist_ok=False"
    )
    (RUN_DIR / "command.txt").write_text(command + "\n")

    print(f"Run directory: {RUN_DIR}")
    print(f"Starting training at {datetime.now()}")
    t0 = time.time()

    # Load model and train
    model = YOLO(str(MODEL_PATH))

    results = model.train(
        data=str(DATA_YAML),
        imgsz=640,
        epochs=100,
        batch=16,
        device=0,
        workers=4,
        patience=30,
        seed=42,
        deterministic=True,
        optimizer="auto",
        amp=False,
        mosaic=1.0,
        project=str(RUN_DIR),
        name="train",
        exist_ok=False,
        verbose=True,
    )

    elapsed = time.time() - t0
    print(f"Training completed in {elapsed:.1f}s at {datetime.now()}")
    (RUN_DIR / "end_time.txt").write_text(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

    # Write summary
    results_csv = RUN_DIR / "train" / "results.csv"
    if results_csv.exists():
        import csv
        with open(results_csv) as f:
            rows = list(csv.DictReader(f))
        if rows:
            best = max(rows, key=lambda r: float(r.get('metrics/mAP50-95(B)', '0')))
            summary = {
                "status": "completed",
                "return_code": 0,
                "start_time": (RUN_DIR / "start_time.txt").read_text().strip(),
                "end_time": (RUN_DIR / "end_time.txt").read_text().strip(),
                "config_path": str(PROJECT_ROOT / "configs/train/yolov8n_neudet_baseline_seed42_deterministic.yaml"),
                "run_dir": str(RUN_DIR),
                "dataset_yaml": str(DATA_YAML),
                "command": command.split(),
                "metrics": {
                    "source": str(results_csv),
                    "best_epoch": {k: v for k, v in best.items()},
                },
                "note": "Trained via Python API with deterministic=True, seed=42.",
            }
            (RUN_DIR / "summary.json").write_text(
                json.dumps(summary, indent=2, ensure_ascii=False) + "\n"
            )
            print(f"Best epoch: {best.get('epoch')} | "
                  f"mAP50: {best.get('metrics/mAP50(B)')} | "
                  f"mAP50-95: {best.get('metrics/mAP50-95(B)')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
