#!/usr/bin/env python3
"""Extract per-class validation metrics from all experiment best.pt files.

Runs ultralytics val mode on each best.pt with val split, imgsz=640, batch=16.
Saves per-class results to a JSON file for later use.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from ultralytics import YOLO

EXPERIMENTS = {
    "V1_baseline_seed42": {
        "model": "experiments/training/yolov8n_neudet_baseline_20260712_122943/train/weights/best.pt",
        "deterministic": False,
        "seed": 42,
        "variant": "V1 baseline",
    },
    "baseline_seed7": {
        "model": "experiments/training/yolov8n_neudet_baseline_seed7_20260712_140145/train/weights/best.pt",
        "deterministic": True,
        "seed": 7,
        "variant": "baseline seed=7",
    },
    "baseline_seed123": {
        "model": "experiments/training/yolov8n_neudet_baseline_seed123_20260712_141510/train/weights/best.pt",
        "deterministic": True,
        "seed": 123,
        "variant": "baseline seed=123",
    },
    "V2_extended_epochs": {
        "model": "experiments/training/yolov8n_neudet_v2_20260712_125029/train/weights/best.pt",
        "deterministic": False,
        "seed": 42,
        "variant": "V2 extended epochs",
    },
    "V3_no_mosaic": {
        "model": "experiments/training/yolov8n_neudet_v3_no_mosaic_20260712_133730/train/weights/best.pt",
        "deterministic": False,
        "seed": 42,
        "variant": "V3 no mosaic",
    },
    "V4_AdamW": {
        "model": "experiments/training/yolov8n_neudet_v4_adamw_20260712_142809/train/weights/best.pt",
        "deterministic": True,
        "seed": 42,
        "variant": "V4 AdamW",
    },
    "V5_cosLR": {
        "model": "experiments/training/yolov8n_neudet_v5_coslr_20260712_144107/train/weights/best.pt",
        "deterministic": True,
        "seed": 42,
        "variant": "V5 cosine LR",
    },
    "V6_no_warmup": {
        "model": "experiments/training/yolov8n_neudet_v6_no_warmup_20260712_145401/train/weights/best.pt",
        "deterministic": True,
        "seed": 42,
        "variant": "V6 no warmup",
    },
}

CLASS_NAMES = [
    "crazing",
    "inclusion",
    "patches",
    "pitted_surface",
    "rolled-in_scale",
    "scratches",
]

DATA_YAML = "data/yolo/neu_det/dataset.yaml"


def main():
    results = {}
    for exp_key, exp_info in EXPERIMENTS.items():
        model_path = Path(exp_info["model"])
        if not model_path.is_file():
            print(f"SKIP {exp_key}: model not found at {model_path}", file=sys.stderr)
            results[exp_key] = {"error": f"model not found: {model_path}"}
            continue

        print(f"\n{'='*60}")
        print(f"Validating: {exp_key} ({exp_info['variant']})")
        print(f"Model: {model_path}")
        print(f"{'='*60}")

        model = YOLO(str(model_path))

        val_results = model.val(
            data=DATA_YAML,
            split="val",
            imgsz=640,
            batch=16,
            device=0,
            verbose=True,
            plots=False,
        )

        # Extract per-class metrics
        per_class = {}
        ap50_dict = val_results.ap_class_index if hasattr(val_results, 'ap_class_index') else {}
        maps = val_results.maps if hasattr(val_results, 'maps') else []
        ap50_all = val_results.box.ap50 if hasattr(val_results.box, 'ap50') else []

        # box.ap50 is per-class AP50
        ap50_per_class = []
        if hasattr(val_results.box, 'ap50') and val_results.box.ap50 is not None:
            ap50_per_class = val_results.box.ap50.tolist() if hasattr(val_results.box.ap50, 'tolist') else list(val_results.box.ap50)

        # box.ap is per-class AP50-95
        ap_per_class = []
        if hasattr(val_results.box, 'ap') and val_results.box.ap is not None:
            ap_per_class = val_results.box.ap.tolist() if hasattr(val_results.box.ap, 'tolist') else list(val_results.box.ap)

        # Per-class precision and recall are harder to get directly
        # Use box.all_ap to compute from confusion matrix
        # For now capture what's available
        p_per_class = []
        r_per_class = []
        if hasattr(val_results.box, 'p') and val_results.box.p is not None:
            p_per_class = val_results.box.p.tolist() if hasattr(val_results.box.p, 'tolist') else list(val_results.box.p)
        if hasattr(val_results.box, 'r') and val_results.box.r is not None:
            r_per_class = val_results.box.r.tolist() if hasattr(val_results.box.r, 'tolist') else list(val_results.box.r)

        # Build per-class dict
        for i, name in enumerate(CLASS_NAMES):
            per_class[name] = {
                "ap50": round(ap50_per_class[i], 6) if i < len(ap50_per_class) else None,
                "ap50_95": round(ap_per_class[i], 6) if i < len(ap_per_class) else None,
                "precision": round(p_per_class[i], 6) if i < len(p_per_class) else None,
                "recall": round(r_per_class[i], 6) if i < len(r_per_class) else None,
            }

        overall = {
            "mAP50": round(float(val_results.box.map50), 6),
            "mAP50_95": round(float(val_results.box.map), 6),
            "precision": round(float(val_results.box.mp), 6) if hasattr(val_results.box, 'mp') else None,
            "recall": round(float(val_results.box.mr), 6) if hasattr(val_results.box, 'mr') else None,
        }

        results[exp_key] = {
            "variant": exp_info["variant"],
            "deterministic": exp_info["deterministic"],
            "seed": exp_info["seed"],
            "model_path": str(model_path),
            "overall": overall,
            "per_class": per_class,
        }

        print(f"  Overall mAP50: {overall['mAP50']}, mAP50-95: {overall['mAP50_95']}")
        for name, metrics in per_class.items():
            print(f"  {name}: AP50={metrics['ap50']}, AP50-95={metrics['ap50_95']}")

    output_path = Path("experiments/validation_per_class_metrics.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
